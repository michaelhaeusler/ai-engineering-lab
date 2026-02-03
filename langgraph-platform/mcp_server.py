"""MCP server providing text analysis tools."""

from __future__ import annotations

import math

from fastmcp import FastMCP

mcp = FastMCP("mcp-server")


@mcp.tool()
def text_and_token_length(query: str) -> str:
    """Calculate text length in characters and estimate token count.

    Assumes approximately 4 characters per token.
    """
    if not query:
        return "Empty query provided"

    text_length = len(query)
    token_length = math.ceil(text_length / 4)

    return (
        f"Text length: {text_length} characters, "
        f"estimated tokens: {token_length} (1 token ≈ 4 characters)"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
