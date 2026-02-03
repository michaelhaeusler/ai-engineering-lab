"""LangGraph agent integration with production features."""

from typing import Dict, Any, List, Optional
import os
import re

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_core.tools import tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

from .models import get_openai_model
from .rag import ProductionRAGChain


class AgentState(TypedDict):
    """State schema for agent graphs."""
    messages: Annotated[List[BaseMessage], add_messages]


class HelpfulnessAgentState(TypedDict):
    """Enhanced state schema for helpfulness agent with evaluation tracking."""
    messages: Annotated[List[BaseMessage], add_messages]
    helpfulness_score: Optional[float]
    needs_refinement: bool
    refinement_count: int


class GuardrailsAgentState(TypedDict):
    """State schema for guardrails-enabled agent with validation tracking."""
    messages: Annotated[List[BaseMessage], add_messages]
    input_validation_passed: bool
    output_validation_passed: bool
    validation_error: Optional[str]


def create_rag_tool(rag_chain: ProductionRAGChain):
    """Create a RAG tool from a ProductionRAGChain."""
    
    @tool
    def retrieve_information(query: str) -> str:
        """Use Retrieval Augmented Generation to retrieve information from the student loan documents."""
        try:
            result = rag_chain.invoke(query)
            return result.content if hasattr(result, 'content') else str(result)
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
    
    return retrieve_information


def get_default_tools(rag_chain: Optional[ProductionRAGChain] = None) -> List:
    """Get default tools for the agent.
    
    Args:
        rag_chain: Optional RAG chain to include as a tool
        
    Returns:
        List of tools
    """
    tools = []
    
    # Add Tavily search if API key is available
    if os.getenv("TAVILY_API_KEY"):
        tools.append(TavilySearchResults(max_results=5))
    
    # Add Arxiv tool
    tools.append(ArxivQueryRun())
    
    # Add RAG tool if provided
    if rag_chain:
        tools.append(create_rag_tool(rag_chain))
    
    return tools


def create_langgraph_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None,
    with_input_guardrails: bool = False,
    with_output_guardrails: bool = False,
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None
):
    """Create a simple LangGraph agent with optional guardrails.

    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        with_input_guardrails: Enable input validation (jailbreak, topic, PII)
        with_output_guardrails: Enable output validation (PII, profanity)
        valid_topics: List of valid topics (only if with_input_guardrails=True)
        invalid_topics: List of invalid topics (only if with_input_guardrails=True)

    Returns:
        Compiled LangGraph agent
    """
    if tools is None:
        tools = get_default_tools(rag_chain)

    # Get model and bind tools
    model = get_openai_model(model_name=model_name, temperature=temperature)
    model_with_tools = model.bind_tools(tools)

    # Choose state schema based on guardrails
    state_schema = GuardrailsAgentState if (with_input_guardrails or with_output_guardrails) else AgentState

    def call_model(state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: Dict[str, Any]):
        """Route to tools if the last message has tool calls."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        # If we have output guardrails, route to validation
        if with_output_guardrails:
            return "validate_output"
        return END

    def route_after_input_validation(state: Dict[str, Any]):
        """Route after input validation: proceed to agent or end with error."""
        if state.get("input_validation_passed", False):
            return "agent"
        else:
            return "input_error"

    def create_input_error_message(state: Dict[str, Any]) -> Dict[str, Any]:
        """Create an error message for input validation failure."""
        error_msg = state.get("validation_error", "Your request could not be processed")
        return {"messages": [AIMessage(content=error_msg)]}

    # Build graph
    graph = StateGraph(state_schema)
    tool_node = ToolNode(tools)

    # Add validation nodes if needed
    if with_input_guardrails:
        from .guardrails import create_input_validation_node, create_default_input_guards
        pii_guard, content_guard = create_default_input_guards(valid_topics, invalid_topics)
        input_validation_node = create_input_validation_node(content_guard, pii_guard)
        graph.add_node("validate_input", input_validation_node)
        graph.add_node("input_error", create_input_error_message)

    if with_output_guardrails:
        from .guardrails import create_output_validation_node, create_default_output_guard
        output_guard = create_default_output_guard()
        output_validation_node = create_output_validation_node(output_guard)
        graph.add_node("validate_output", output_validation_node)

    # Add core nodes
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)

    # Set entry point and routing
    if with_input_guardrails:
        graph.set_entry_point("validate_input")
        graph.add_conditional_edges(
            "validate_input",
            route_after_input_validation,
            {"agent": "agent", "input_error": "input_error"}
        )
        graph.add_edge("input_error", END)
    else:
        graph.set_entry_point("agent")

    graph.add_conditional_edges("agent", should_continue, {
        "action": "action",
        "validate_output": "validate_output" if with_output_guardrails else END,
        END: END
    })
    graph.add_edge("action", "agent")

    if with_output_guardrails:
        graph.add_edge("validate_output", END)

    return graph.compile()


def parse_helpfulness_score(response_text: str) -> float:
    """Parse helpfulness score from LLM response.

    Args:
        response_text: LLM response containing a score

    Returns:
        Float score between 0 and 1, defaults to 0.5 if parsing fails
    """
    try:
        # Look for patterns like "0.8", "0.75", "Score: 0.9", etc.
        match = re.search(r'(\d+\.?\d*)', response_text)
        if match:
            score = float(match.group(1))
            # Normalize if score is out of range
            if score > 1.0:
                score = score / 10.0 if score <= 10.0 else 0.5
            return max(0.0, min(1.0, score))
    except (ValueError, AttributeError):
        pass
    return 0.5  # Default to middle score if parsing fails


class HelpfulnessGuardrailsAgentState(TypedDict):
    """Enhanced state schema combining helpfulness tracking with guardrails."""
    messages: Annotated[List[BaseMessage], add_messages]
    helpfulness_score: Optional[float]
    needs_refinement: bool
    refinement_count: int
    input_validation_passed: bool
    output_validation_passed: bool
    validation_error: Optional[str]


def create_helpfulness_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.1,
    tools: Optional[List] = None,
    rag_chain: Optional[ProductionRAGChain] = None,
    helpfulness_threshold: float = 0.7,
    max_refinements: int = 2,
    with_input_guardrails: bool = False,
    with_output_guardrails: bool = False,
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None
):
    """Create a helpfulness-aware LangGraph agent with optional guardrails.

    This agent extends the simple agent by adding:
    - Response helpfulness evaluation after generating answers
    - Automatic refinement loops if responses don't meet threshold
    - Tracking of refinement attempts to prevent infinite loops
    - Optional input/output guardrails validation

    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        tools: List of tools to bind to the model
        rag_chain: Optional RAG chain to include as a tool
        helpfulness_threshold: Minimum score (0-1) for acceptable responses (default: 0.7)
        max_refinements: Maximum number of refinement attempts (default: 2)
        with_input_guardrails: Enable input validation (jailbreak, topic, PII)
        with_output_guardrails: Enable output validation (PII, profanity)
        valid_topics: List of valid topics (only if with_input_guardrails=True)
        invalid_topics: List of invalid topics (only if with_input_guardrails=True)

    Returns:
        Compiled LangGraph agent with helpfulness evaluation and optional guardrails
    """
    if tools is None:
        tools = get_default_tools(rag_chain)

    # Get models
    model = get_openai_model(model_name=model_name, temperature=temperature)
    eval_model = get_openai_model(model_name="gpt-4o-mini", temperature=0.0)  # Fast, cheap eval
    model_with_tools = model.bind_tools(tools)

    # Choose state schema based on guardrails
    state_schema = HelpfulnessGuardrailsAgentState if (with_input_guardrails or with_output_guardrails) else HelpfulnessAgentState

    def call_model(state: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the model with messages."""
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    def evaluate_helpfulness(state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if the response is helpful enough."""
        last_message = state["messages"][-1]

        # Find the original user query (first human message)
        original_query = None
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                original_query = msg.content
                break

        # Create evaluation prompt
        eval_prompt = f"""Evaluate the helpfulness of this response on a scale of 0 to 1.

User Query: {original_query}

Response: {last_message.content}

Consider:
- Does it directly answer the question?
- Is it detailed and informative?
- Is it accurate and relevant?

Provide ONLY a number between 0 and 1 (e.g., 0.8)."""

        # Get evaluation
        try:
            result = eval_model.invoke(eval_prompt)
            score = parse_helpfulness_score(result.content)
        except Exception:
            score = 0.5  # Default to middle score on error

        current_count = state.get("refinement_count", 0)
        needs_refinement = score < helpfulness_threshold and current_count < max_refinements

        return {
            "helpfulness_score": score,
            "needs_refinement": needs_refinement
        }

    def refine_response(state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a refinement prompt to improve the response."""
        # Find original query
        original_query = None
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                original_query = msg.content
                break

        previous_response = state["messages"][-1].content
        current_score = state.get("helpfulness_score", 0.0)

        refinement_prompt = f"""Your previous response was not helpful enough (score: {current_score:.2f}).

Original Query: {original_query}

Previous Response: {previous_response}

Please provide a MORE helpful, detailed, and comprehensive response that better addresses the user's question. Focus on:
- Providing more specific details
- Being more direct and clear
- Adding relevant context or examples"""

        new_count = state.get("refinement_count", 0) + 1

        return {
            "messages": [HumanMessage(content=refinement_prompt)],
            "refinement_count": new_count
        }

    def should_evaluate(state: Dict[str, Any]):
        """Route to evaluation if response complete, otherwise to tools."""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "action"
        # If we have output guardrails, validate before evaluating
        if with_output_guardrails:
            return "validate_output"
        return "evaluate"

    def should_refine(state: Dict[str, Any]):
        """Route to refinement or end based on evaluation."""
        if state.get("needs_refinement", False):
            return "refine"
        return END

    def route_after_input_validation(state: Dict[str, Any]):
        """Route after input validation."""
        if state.get("input_validation_passed", False):
            return "agent"
        else:
            return "input_error"

    def route_after_output_validation(state: Dict[str, Any]):
        """Route after output validation to evaluation."""
        # Output validated, now evaluate helpfulness
        return "evaluate"

    def create_input_error_message(state: Dict[str, Any]) -> Dict[str, Any]:
        """Create an error message for input validation failure."""
        error_msg = state.get("validation_error", "Your request could not be processed")
        return {"messages": [AIMessage(content=error_msg)]}

    # Build graph
    graph = StateGraph(state_schema)
    tool_node = ToolNode(tools)

    # Add validation nodes if needed
    if with_input_guardrails:
        from .guardrails import create_input_validation_node, create_default_input_guards
        pii_guard, content_guard = create_default_input_guards(valid_topics, invalid_topics)
        input_validation_node = create_input_validation_node(content_guard, pii_guard)
        graph.add_node("validate_input", input_validation_node)
        graph.add_node("input_error", create_input_error_message)

    if with_output_guardrails:
        from .guardrails import create_output_validation_node, create_default_output_guard
        output_guard = create_default_output_guard()
        output_validation_node = create_output_validation_node(output_guard)
        graph.add_node("validate_output", output_validation_node)

    # Add core nodes
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    graph.add_node("evaluate", evaluate_helpfulness)
    graph.add_node("refine", refine_response)

    # Set entry point and routing
    if with_input_guardrails:
        graph.set_entry_point("validate_input")
        graph.add_conditional_edges(
            "validate_input",
            route_after_input_validation,
            {"agent": "agent", "input_error": "input_error"}
        )
        graph.add_edge("input_error", END)
    else:
        graph.set_entry_point("agent")

    # Add edges
    graph.add_conditional_edges(
        "agent",
        should_evaluate,
        {
            "action": "action",
            "validate_output": "validate_output" if with_output_guardrails else "evaluate",
            "evaluate": "evaluate"
        }
    )
    graph.add_edge("action", "agent")  # After tools, back to agent

    if with_output_guardrails:
        graph.add_conditional_edges(
            "validate_output",
            route_after_output_validation,
            {"evaluate": "evaluate"}
        )

    graph.add_conditional_edges(
        "evaluate",
        should_refine,
        {"refine": "refine", END: END}
    )
    graph.add_edge("refine", "agent")  # After refinement, back to agent

    return graph.compile()


