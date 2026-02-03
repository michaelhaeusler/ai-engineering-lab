"""Toolbelt assembly for agents."""

from __future__ import annotations

import logging
from typing import List

from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_tavily import TavilySearch

from app.mcp_client import get_mcp_tools
from app.rag import retrieve_information

logger = logging.getLogger(__name__)


def get_tool_belt() -> List:
    """Return all available tools for agents.

    Includes Tavily search, Arxiv, RAG, and MCP tools.
    """
    tools = [
        TavilySearch(max_results=5),
        ArxivQueryRun(),
        retrieve_information,
    ]

    try:
        mcp_tools = get_mcp_tools("mcp_server.py")
        tools.extend(mcp_tools)
        logger.info(f"Loaded {len(mcp_tools)} MCP tool(s)")
    except Exception as e:
        logger.warning(f"Could not load MCP tools: {e}")

    return tools
