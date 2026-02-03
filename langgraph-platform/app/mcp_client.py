"""MCP client for loading tools into LangGraph."""

from __future__ import annotations

import asyncio
from typing import List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def get_mcp_tools_async(server_script_path: str) -> List[BaseTool]:
    """Connect to MCP server and load available tools.

    Args:
        server_script_path: Path to the MCP server Python script

    Returns:
        List of LangChain-compatible tools
    """
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await load_mcp_tools(session)


def get_mcp_tools(server_script_path: str = "mcp_server.py") -> List[BaseTool]:
    """Get MCP tools synchronously.

    Args:
        server_script_path: Path to MCP server script

    Returns:
        List of LangChain tools
    """
    return asyncio.run(get_mcp_tools_async(server_script_path))
