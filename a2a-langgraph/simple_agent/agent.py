"""
Simple Agent - Uses A2A protocol through LangGraph with Streaming

A straightforward agent that demonstrates using the A2A server
through a LangGraph graph with streaming support.
"""

import os
import asyncio
from typing import AsyncIterator

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from simple_agent.graph import create_simple_graph


class SimpleAgent:
    """
    A simple agent that can delegate tasks to the A2A server agent.

    This agent uses LangGraph to decide when to use the A2A tool
    to query the server agent for help with complex questions.
    """

    SYSTEM_PROMPT = """You are a helpful assistant with access to a specialized A2A agent.

You have access to the query_a2a_agent tool which connects to an A2A server that can:
- Search the web for current information
- Find academic papers on arXiv
- Retrieve information from documents

When you need up-to-date information, web search results, academic research, or access to
specific documents, use the query_a2a_agent tool to get help from the remote agent.

For simple questions that don't require external information, you can answer directly."""

    def __init__(self):
        """Initialize the simple agent with LLM and graph."""

        # Create the LLM
        self.llm = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-4o-mini'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('TOOL_LLM_URL', 'https://api.openai.com/v1'),
            temperature=0,
        )

        # Create the graph
        self.graph = create_simple_graph(self.llm)

    async def stream_async(self, query: str, thread_id: str = "default") -> AsyncIterator[str]:
        """
        Stream the agent's response (async version).

        Args:
            query: The question or task
            thread_id: Conversation thread ID for memory (default: "default")

        Yields:
            str: Status updates and final response
        """

        # Prepare inputs with system prompt
        inputs = {
            "messages": [
                SystemMessage(content=self.SYSTEM_PROMPT),
                ("user", query)
            ]
        }
        config = {"configurable": {"thread_id": thread_id}}

        consulting_shown = False

        # Show initial thinking indicator
        yield "Thinking...\n"

        # Stream the graph execution
        async for event in self.graph.astream(inputs, config, stream_mode="values"):
            # Extract messages from the event
            if "messages" in event:
                last_message = event["messages"][-1]

                # Show consulting indicator when tool is being called
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    if not consulting_shown:
                        yield "Consulting the remote A2A agent...\n\n"
                        consulting_shown = True

                # Check for message content
                elif hasattr(last_message, "content") and last_message.content:
                    message_type = getattr(last_message, "type", None)

                    # Yield AI messages (skip tool messages)
                    if message_type == "ai":
                        tool_calls = getattr(last_message, "tool_calls", [])
                        if not tool_calls:  # No tool calls means this is the final response
                            yield last_message.content

    async def run_async(self, query: str, thread_id: str = "default") -> str:
        """
        Run the agent with a query (async version).

        Args:
            query: The question or task
            thread_id: Conversation thread ID for memory (default: "default")

        Returns:
            str: The agent's response
        """

        # Collect all streamed chunks
        chunks = []
        async for chunk in self.stream_async(query, thread_id):
            chunks.append(chunk)

        return '\n'.join(chunks) if chunks else "No response generated."

    def stream(self, query: str, thread_id: str = "default"):
        """
        Stream the agent's response (sync wrapper).

        Args:
            query: The question or task
            thread_id: Conversation thread ID for memory (default: "default")

        Yields:
            str: Intermediate updates and response chunks
        """
        # Run async generator in sync context
        async_gen = self.stream_async(query, thread_id)

        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Yield results from async generator
        try:
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.run_until_complete(async_gen.aclose())

    def run(self, query: str, thread_id: str = "default") -> str:
        """
        Run the agent with a query (sync wrapper).

        Args:
            query: The question or task
            thread_id: Conversation thread ID for memory (default: "default")

        Returns:
            str: The agent's response
        """
        return asyncio.run(self.run_async(query, thread_id))
