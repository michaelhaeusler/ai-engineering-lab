"""LangGraph graph definition and compilation."""

import logging
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes import (
    classify_node,
    policy_agent_node,
    web_agent_node,
    route_question
)

logger = logging.getLogger(__name__)


def create_agent_graph():
    """
    Create and compile the multi-agent LangGraph.
    
    Returns:
        Compiled graph ready for execution
    """
    # Initialize the StateGraph with our AgentState
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("classify", classify_node)
    graph.add_node("policy_agent", policy_agent_node)
    graph.add_node("web_agent", web_agent_node)
    
    # Set entry point
    graph.set_entry_point("classify")
    
    # Add conditional routing from classify to agents
    graph.add_conditional_edges(
        "classify",
        route_question,
        {
            "policy_agent": "policy_agent",
            "web_agent": "web_agent"
        }
    )
    
    # Both agents go to END when done
    graph.add_edge("policy_agent", END)
    graph.add_edge("web_agent", END)
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    logger.info("Agent graph compiled successfully")
    
    return compiled_graph


# Create a single compiled graph instance (reused across requests)
agent_graph = create_agent_graph()

