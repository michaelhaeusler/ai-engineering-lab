# LangGraph Platform: Build and Serve Agentic Graphs

This project demonstrates how to build, serve, and operate LangGraph agent graphs using the **LangGraph Platform** (LangGraph API and CLI). It includes two graphs: a simple tool-calling agent and an agent with a helpfulness-evaluation loop, both exposed as **assistants** via `langgraph.json` and callable over HTTP or from **LangGraph Studio**.

## Overview

The repo runs a local LangGraph server (`langgraph dev`) that serves two compiled graphs. Each graph uses the same tool belt (Tavily, Arxiv, RAG, and optional MCP tools from a FastMCP server). The difference is control flow: the simple agent only branches on tool calls, while the helpfulness agent adds a post-response check that can loop back to the agent or terminate. The server can be driven by the LangGraph SDK, curl, or LangGraph Studio for visualization and streaming.

## Architecture

### Graphs

1. **simple_agent** (`app.graphs.simple_agent`)
   - **Nodes:** `agent` (model + tools), `action` (ToolNode).
   - **Flow:** Entry → `agent`. If the last message has tool calls → `action` → back to `agent`; else END.
   - **State:** `AgentState` with `messages` (add_messages reducer).

2. **agent_with_helpfulness** (`app.graphs.agent_with_helpfulness`)
   - **Nodes:** `agent`, `action`, `helpfulness`.
   - **Flow:** Entry → `agent`. If tool calls → `action` → `agent`. If no tool calls → `helpfulness`. Helpfulness node runs a small LLM chain (initial query vs final response, Y/N). If "Y" or message count > 10 → END; else → back to `agent`.
   - **Purpose:** Quality gate so the agent only finishes when the answer is deemed helpful or a loop limit is hit.

### Assistants (langgraph.json)

- **agent** → graph `simple_agent`, name "Simple Agent".
- **agent_helpful** → graph `agent_with_helpfulness`, name "Agent with Helpfulness Check".

Assistants are the top-level handle used by the API and Studio; each points at a graph and optional metadata.

### Tool Belt (app/tools.py)

- **TavilySearch** (web search).
- **ArxivQueryRun** (paper search).
- **retrieve_information** (RAG over project data).
- **MCP tools** (from `mcp_server.py` via `app/mcp_client.py`), e.g. `text_and_token_length`. The MCP server is run separately (e.g. FastMCP stdio); the client loads tools and adds them to the belt. If MCP is unavailable, the rest of the tools still work.

### MCP Server (mcp_server.py)

A small **FastMCP** server that exposes a `text_and_token_length` tool (character count and rough token estimate). Used to show how LangGraph agents can consume tools from an MCP server; the app’s MCP client connects to it and merges those tools into the graph’s tool list.

## Key Techniques

### LangGraph Platform and langgraph.json

- **graphs:** Map graph IDs to import paths (`app.graphs.simple_agent:graph`, etc.).
- **assistants:** Map assistant IDs to a graph_id, name, and description for the UI and API.
- **env:** Points to `.env` for secrets (OpenAI, Tavily, etc.).

### Serving and calling

- **CLI:** `uv run langgraph dev` starts the server (default http://localhost:2024).
- **SDK:** `langgraph_sdk.get_sync_client(url="http://localhost:2024")` then `client.runs.stream(..., assistant_id="agent", input={...}, stream_mode="updates")`.
- **Studio:** Open `https://smith.langchain.com/studio?baseUrl=http://localhost:2024` to select an assistant, send messages, and see node-by-node updates (and set interrupts if needed).

### Helpfulness loop

- After the agent responds without tool calls, control goes to a dedicated node that calls a second model with a fixed prompt (helpful Y/N).
- The result is pushed into state as a synthetic message (`HELPFULNESS:Y` / `HELPFULNESS:N` / `HELPFULNESS:END`); a conditional edge reads it to either END or route back to `agent`.
- Loop limit: if `len(messages) > 10`, the helpfulness node returns `HELPFULNESS:END` so the graph always terminates.

### Interrupts (Studio)

- **Before:** Pause before a node runs; inspect or modify inputs.
- **After:** Pause after a node runs; inspect or modify outputs before the next step.

## Key Learnings

1. **Assistants vs graphs:** The platform exposes *assistants* to users; each assistant is backed by a *graph*. This keeps a stable API surface while you swap or version graphs.
2. **Single tool belt, multiple graphs:** The same tools (and MCP integration) are reused across graphs; only the graph topology (e.g. helpfulness loop) changes.
3. **MCP integration:** Tools from an external MCP server can be loaded into LangChain/LangGraph like any other tool list; the agent doesn’t care whether a tool is local or from MCP.
4. **Studio for debugging:** Streaming and interrupts in Studio make it easier to see where a run is and to test “what if” by changing state at interrupt points.

## Evaluation

### Strengths

- Clear split between graph definition, tool belt, and platform config (`langgraph.json`).
- Two graphs illustrate minimal vs quality-gated flows without duplicating tool code.
- Local dev story is simple: `uv sync`, `langgraph dev`, then SDK or Studio.
- MCP example is minimal and shows the pattern for adding more tools via FastMCP.

### Limitations

- Helpfulness is a simple Y/N prompt; production might want structured output or extra checks.
- MCP server must be running and reachable for MCP tools to load; failure is non-fatal but tools are missing.
- Default in-memory persistence; for production you’d configure a proper checkpoint store.

## Tech Stack

- **LangGraph** / **langgraph-cli**: Graph definition and `langgraph dev` server.
- **langgraph-sdk**: Sync (and async) client for runs and streaming.
- **LangChain**: Chat model, tools (Tavily, Arxiv), prompts, ToolNode.
- **FastMCP**: MCP server and `text_and_token_length` tool.
- **langchain-mcp** / **langchain-mcp-adapters**: Loading MCP tools into the agent.
- **Python 3.13+**, **uv**; **python-dotenv** for `.env`.

## Project Structure

```
langgraph-platform/
├── langgraph.json           # Platform config: graphs, assistants, env
├── mcp_server.py            # FastMCP server (e.g. text_and_token_length)
├── app/
│   ├── graphs/
│   │   ├── simple_agent.py           # Tool-calling agent graph
│   │   └── agent_with_helpfulness.py # Agent + helpfulness loop
│   ├── mcp_client.py        # Load MCP tools for the belt
│   ├── tools.py             # Tool belt (Tavily, Arxiv, RAG, MCP)
│   ├── state.py             # AgentState
│   ├── models.py            # Chat model factory
│   └── rag.py               # RAG retrieval tool
├── data/                    # Documents for RAG
├── test_served_graph.py    # Example SDK call to local server
├── setup_guide.md           # Quick start and testing
└── pyproject.toml
```

## Getting Started

1. **Install:** `uv sync`
2. **Configure:** Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `TAVILY_API_KEY`; optionally LangSmith.
3. **Serve:** `uv run langgraph dev` (server at http://localhost:2024).
4. **Call:** From another terminal, `uv run test_served_graph.py` (uses SDK to stream from `simple_agent`), or use curl/Postman against the runs API.
5. **Studio:** Open https://smith.langchain.com/studio?baseUrl=http://localhost:2024, pick an assistant, and run a conversation with streaming and optional interrupts.

To try MCP tools, start the MCP server (e.g. run `mcp_server.py` with the transport your client expects) and ensure `app/mcp_client.py` can connect; then the tool belt will include the MCP tools.

## Conclusion

This project shows how to run LangGraph agents behind the LangGraph Platform: define graphs and assistants in `langgraph.json`, serve with `langgraph dev`, and consume via the SDK or LangGraph Studio. The helpfulness graph illustrates a small quality loop and termination guard; the MCP integration shows how to extend the tool set with external servers. Together this is a template for building and serving production-style agent APIs with minimal boilerplate.
