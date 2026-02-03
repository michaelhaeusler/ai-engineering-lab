# Setup Guide

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Start LangGraph server
uv run langgraph dev
```

The server will start on `http://localhost:2024`

## What You Get

Your LangGraph agents now have access to:

1. **Tavily Search** - Web search capability
2. **Arxiv** - Research paper lookup
3. **RAG** - Document retrieval
4. **text_and_token_length** - Your MCP tool for text analysis

## Architecture

```
LangGraph Server (localhost:2024)
  └── Agents (simple_agent, agent_with_helpfulness)
      └── Tools (app/tools.py)
          ├── Tavily, Arxiv, RAG
          └── MCP Tools
              └── MCP Server (mcp_server.py - auto-started)
```

## Testing Your MCP Tool

### Via LangGraph API

```bash
# Test the agent with MCP tool
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "simple_agent",
    "input": {
      "messages": [{
        "role": "user",
        "content": "How many tokens is this phrase: Hello World"
      }]
    }
  }'
```

### Via LangGraph Studio

1. Open: https://smith.langchain.com/studio/?baseUrl=http://localhost:2024
2. Select an assistant
3. Ask: "Calculate token count for 'Hello World'"
4. Watch the agent use your MCP tool!

## File Structure

```
14_LangGraph_Platform/
├── mcp_server.py          # MCP server with tools
├── app/
│   ├── mcp_client.py      # MCP client integration
│   └── tools.py           # Tool belt (includes MCP tools)
└── langgraph.json         # LangGraph configuration
```

## Adding More MCP Tools

Edit `mcp_server.py`:

```python
@mcp.tool()
def your_new_tool(input: str) -> str:
    """Description of what your tool does."""
    # Your implementation
    return result
```

Restart the server - that's it! The tool will be automatically discovered.

