# A2A Protocol with LangGraph

This project implements the **A2A (Agent-to-Agent) Protocol** using LangGraph: a **server** exposes a LangGraph agent (with tool use and a helpfulness-evaluation loop) over HTTP via the A2A SDK, and a **client** is a separate LangGraph agent that invokes the server as a tool. The server advertises an **AgentCard** (name, description, URL, skills) and handles streaming and task lifecycle; the client uses the A2A client to send messages and consume streaming artifact updates.

## Overview

The repo has two main parts. The **app** package runs the A2A server: a LangGraph agent (Tavily, Arxiv, RAG, plus a helpfulness loop) is wrapped by an **AgentExecutor** that maps graph stream events to A2A task states and artifacts. The **simple_agent** package is a client-side LangGraph that has a single tool, **query_a2a_agent**, which calls the server via the A2A protocol and returns the collected response text. Together they show how one agent can use another as a tool over a standardized protocol.

## Architecture

### Server (app)

1. **LangGraph** (`agent_graph_with_helpfulness`): Agent node (LLM + tools) → if tool calls, action node (Tavily, Arxiv, RAG) → back to agent; if no tool calls, helpfulness node (Y/N + loop limit 10) → end or back to agent.
2. **Agent** (`agent.py`): Wraps the graph, exposes `stream(query, context_id)`. Consumes graph stream and yields items with `is_task_complete`, `require_user_input`, `content`. Final response is read from graph state (e.g. structured_response).
3. **GeneralAgentExecutor** (`agent_executor.py`): Implements A2A `AgentExecutor`. In `execute()`, calls `agent.stream()`, maps stream items to A2A task updates (working, input_required, completed) and artifacts via `TaskUpdater`.
4. **A2A server** (`__main__.py`): Builds `AgentCard` (name, description, url, version, capabilities, skills), `DefaultRequestHandler` with the executor and task store, and `A2AStarletteApplication`. Runs with uvicorn (default `localhost:10000`).

### Client (simple_agent)

1. **query_a2a_agent** (`a2a_tool.py`): LangChain tool that uses `a2a.client.A2AClient` to send a user message to `A2A_SERVER_URL`, streams the response, collects text from `artifact-update` events, and returns the concatenated text.
2. **Graph** (`graph.py`): Two-node LangGraph: agent (LLM bound to `query_a2a_agent`) and tools (ToolNode). Agent can call the A2A server once or multiple times; tool result is the server’s reply.
3. **run** (`run.py`): Entry point to run the client graph (e.g. invoke with a question and print the result).

### A2A Concepts

- **AgentCard**: Describes the agent (name, description, url, version, capabilities such as streaming, skills list). Returned by the server and used by clients to discover and call the agent.
- **AgentSkill**: Describes a capability (id, name, description, tags, examples). Used for discovery and prompts.
- **Task lifecycle**: Server creates a task, streams updates (working, artifact-update), and can signal input_required or completed. Client sends messages and consumes the stream.

## Key Techniques

### A2A server wiring

- **a2a-sdk**: `AgentExecutor`, `RequestContext`, `EventQueue`, `TaskUpdater`, `AgentCard`, `AgentSkill`, `A2AStarletteApplication`, `DefaultRequestHandler`. The executor’s `execute()` runs the LangGraph stream and pushes A2A events.
- **Stream mapping**: Graph stream items (e.g. “Searching…”, “Processing…”, final content) are mapped to `updater.update_status()` (working / input_required) or `updater.add_artifact()` + `updater.complete()`.

### Client A2A tool

- **A2AClient**: `SendStreamingMessageRequest` with `MessageSendParams` (role, parts, message_id). `send_message_streaming()` returns an async iterator of chunks.
- **Parsing**: Filter chunks by `kind == 'artifact-update'`, then extract text from `artifact.parts[].root.text` and concatenate for the tool result.

### Helpfulness loop (server graph)

- Same pattern as in other LangGraph projects: after the agent responds without tool calls, a helpfulness node runs a small LLM chain (initial query vs final response, Y/N). If Y or message count > 10, end; else route back to the agent.
- Ensures the server agent does not terminate with an unhelpful answer when used by the client.

## Key Learnings

1. **AgentCard and skills**: The card and skills list are the public contract of the agent; clients use them to know what the agent can do and how to phrase requests.
2. **Executor bridges graph and protocol**: The A2A executor is the only place that knows about both the LangGraph stream and the A2A event model; keeping this in one class keeps the graph independent of the protocol.
3. **Streaming end-to-end**: Server streams graph updates; executor turns them into A2A task/artifact events; client tool consumes the stream and returns text. No need to buffer the full response on the server.
4. **One agent as another’s tool**: The client agent does not duplicate the server’s tools; it just has one “call the other agent” tool. Composition is at the agent level, not the tool level.
5. **Protocol over custom APIs**: A2A gives a standard way to expose and consume agents (URL, message format, streaming, tasks). Other frameworks can implement the same protocol and interoperate.

## Evaluation

### Strengths

- Clear separation: server graph, executor, and A2A app are distinct; client graph and A2A tool are minimal.
- Single protocol for both “human UI” and “agent client”: the same server URL and message format work for both.
- Helpfulness loop on the server improves quality when the agent is used as a tool by another agent.
- a2a-sdk handles transport and task lifecycle; you focus on executor logic and graph.

### Limitations

- Client tool is synchronous from the graph’s perspective (one blocking “call A2A” tool); for multi-turn or more complex client flows you’d extend the client graph or tool.
- Default in-memory task store and no auth; production would add persistence and security.
- AgentCard URL is fixed at startup (e.g. localhost:10000); deployment needs config or discovery.

## Tech Stack

- **LangGraph**: Server graph (agent + action + helpfulness), client graph (agent + tools).
- **LangChain**: Chat model, tools (Tavily, Arxiv, RAG), ToolNode.
- **a2a-sdk**: A2A client and server types, Starlette app, request handler, task store, event queue.
- **FastAPI/Starlette/Uvicorn**: HTTP server for A2A.
- **Python 3.12+**, **uv** for install; **python-dotenv** for `.env`.

## Project Structure

```
a2a-langgraph/
├── app/                          # A2A server
│   ├── __main__.py               # AgentCard, A2A app, uvicorn entry
│   ├── agent_executor.py         # GeneralAgentExecutor (graph → A2A events)
│   ├── agent.py                  # Agent class (wraps graph, stream)
│   ├── agent_graph_with_helpfulness.py  # LangGraph with helpfulness loop
│   ├── rag.py                    # RAG retrieval tool
│   ├── tools.py                  # Tool belt (Tavily, Arxiv, RAG)
│   ├── test_client.py            # Example client calling server
│   └── README.md                 # App-level docs
├── simple_agent/                 # Client agent (uses server as tool)
│   ├── a2a_tool.py               # query_a2a_agent (A2AClient, streaming)
│   ├── graph.py                  # LangGraph with A2A tool
│   ├── agent.py                  # LLM + graph wiring
│   ├── run.py                    # Run client graph
│   └── QUICKSTART.md
├── test_personas/                # Optional: persona-based client tests
├── data/                         # Documents for RAG
├── quickstart.sh                 # Setup and run helper
├── pyproject.toml
└── README.md
```

## Getting Started

1. **Install:** `uv sync`
2. **Configure:** Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `TAVILY_API_KEY` (and any RAG/Arxiv vars). For the client, set `A2A_SERVER_URL` (default `http://localhost:10000`).
3. **Run server:** `uv run python -m app` (or `./quickstart.sh` if it starts the server). Server listens on port 10000.
4. **Run client:** In another terminal, `uv run python simple_agent/run.py` (or use `test_client.py`). The client sends a message to the server and prints the reply.
5. **Optional:** Use `test_personas` to run the client with different personas/goals against the same server.

## Conclusion

This project shows how to expose a LangGraph agent over the A2A protocol and how to build a second agent that uses the first as a tool. The server combines a tool-using graph with a helpfulness loop and an A2A executor that maps the graph stream to protocol events; the client is a thin LangGraph plus an A2A tool that calls the server. The pattern is reusable for other A2A-compliant agents and clients.
