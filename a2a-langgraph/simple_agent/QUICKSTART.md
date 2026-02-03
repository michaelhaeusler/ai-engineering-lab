# Quick Start - Simple A2A Agent

Get the simple agent running in 2 minutes!

## Step 1: Start the A2A Server

Terminal 1:
```bash
cd 15_A2A_LangGraph
uv run python -m app
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:10000
```

## Step 2: Run the Simple Agent

Terminal 2:
```bash
cd 15_A2A_LangGraph
uv run python simple_agent/run.py "What are the latest AI developments?"
```

## That's It!

The agent will:
1. Use LangGraph to process your question
2. Call the A2A server via A2A protocol
3. Return the response

## Interactive Mode

```bash
uv run python simple_agent/run.py
```

Then type your questions!

## File Overview

```
simple_agent/
├── a2a_tool.py    - A2A protocol tool (74 lines)
├── graph.py       - LangGraph definition (73 lines)
├── agent.py       - Simple agent class (90 lines)
├── run.py         - Test script (104 lines)
└── __init__.py    - Package file (10 lines)
```

**Total: 351 lines** - Simple and clear!

## See Also

- Full documentation: `SIMPLE_AGENT_README.md`
- Server agent: `app/` directory
