"""
Simple LangGraph for A2A Agent

A basic graph that allows an LLM to use the A2A tool to query
the A2A server agent.
"""

from typing import Literal

from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode

from simple_agent.a2a_tool import query_a2a_agent


def create_simple_graph(llm):
    """
    Create a simple LangGraph that uses the A2A tool.

    The graph has two nodes:
    1. agent: The LLM that decides whether to use the A2A tool
    2. tools: Executes the A2A tool if requested

    Args:
        llm: The language model to use

    Returns:
        Compiled LangGraph
    """

    # Bind the A2A tool to the LLM
    llm_with_tools = llm.bind_tools([query_a2a_agent])

    # Define the agent node
    def agent_node(state: MessagesState):
        """The main agent that can use the A2A tool."""
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    # Define routing logic
    def should_continue(state: MessagesState) -> Literal["tools", "end"]:
        """Determine if we should use tools or end."""
        last_message = state["messages"][-1]

        # If there are tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Otherwise, we're done
        return "end"

    # Create the graph
    graph = StateGraph(MessagesState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode([query_a2a_agent]))

    # Set entry point
    graph.set_entry_point("agent")

    # Add conditional edges
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )

    # After tools, go back to agent
    graph.add_edge("tools", "agent")

    # Compile and return
    return graph.compile()
