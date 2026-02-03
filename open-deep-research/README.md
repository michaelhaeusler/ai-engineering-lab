# Open Deep Research with LangGraph

This project implements a deep research agent using LangGraph's supervisor–researcher delegation pattern. Given a user question, the system can optionally clarify scope, produce a structured research brief, delegate parallel research tasks to sub-agents, synthesize findings, and generate a final report.

## Overview

The implementation is based on [Open Deep Research](https://github.com/langchain-ai/open_deep_research). It uses a hierarchical graph: a top-level agent drives clarification and report writing; a supervisor subgraph plans and delegates; and researcher subgraphs run in parallel to conduct focused research (search, reflection, compression) and return summarized results.

## Architecture

### Workflow Stages

1. **Clarify with user** (optional): Analyzes the request and either asks a clarifying question or proceeds with a short verification message.
2. **Write research brief**: Turns the conversation into a structured research brief used by the supervisor.
3. **Research supervisor**: Lead researcher that can use `think_tool` (reflection), delegate via `ConductResearch`, or finish via `ResearchComplete`. Runs in a loop until completion or iteration limit.
4. **Researchers** (parallel): Each delegated task runs in a researcher subgraph that searches (e.g. Tavily), reflects, and compresses its findings before returning to the supervisor.
5. **Final report generation**: Aggregates notes and brief into a single report using the configured report model.

### State Hierarchy

- **AgentState**: Top-level messages, research brief, accumulated notes, final report.
- **SupervisorState**: Supervisor messages, research brief, notes, raw notes, iteration count.
- **ResearcherState**: Per-researcher messages, topic, tool iterations, compressed research, raw notes.

Structured outputs (e.g. `ClarifyWithUser`, `ResearchQuestion`, `ConductResearch`, `ResearchComplete`) drive routing and tool calls instead of a single monolithic state.

### Subgraphs

- **Supervisor subgraph**: `supervisor` → `supervisor_tools` (execute think_tool, ConductResearch, ResearchComplete); researchers are invoked inside `supervisor_tools` via `researcher_subgraph.ainvoke`; loop back to `supervisor` or end.
- **Researcher subgraph**: `researcher` → `researcher_tools` (search, think) → loop or `compress_research` → END.
- **Main graph**: `clarify_with_user` → `write_research_brief` → `research_supervisor` (supervisor subgraph) → `final_report_generation` → END.

## Key Techniques

### Delegation and Parallel Research

The supervisor binds tools (`ConductResearch`, `ResearchComplete`, `think_tool`). When it calls `ConductResearch` with a topic, the main process invokes the researcher subgraph with that topic; multiple calls can be run in parallel (up to `max_concurrent_research_units`). Results are returned as tool messages and the supervisor continues or signals completion.

### Search and Reflection

Researchers use search tools (e.g. Tavily, or Anthropic/OpenAI native search when configured) and a `think_tool` for planning and reflection (ReAct-style). Token limits and retries are handled so that long runs degrade gracefully.

### Compression and Report Generation

Each researcher run ends with a compression step that turns the conversation and tool outputs into a short `compressed_research` and `raw_notes`. The final report node takes the supervisor’s notes and brief and generates one coherent report with the configured writer model.

### Configuration

`Configuration` (and optional `config_schema` on the graph) controls: clarification on/off, research and report models, search API (Tavily, Anthropic, OpenAI, etc.), max concurrent research units, max researcher/supervisor iterations, and MCP if used.

## Key Learnings

1. **Hierarchical state**: Separate agent, supervisor, and researcher states keep concerns clear and allow parallel researcher runs without shared mutable state.
2. **Structured outputs for control flow**: Using Pydantic tools (`ConductResearch`, `ResearchComplete`, `ClarifyWithUser`, `ResearchQuestion`) makes routing and delegation explicit and easier to debug.
3. **Subgraphs as tools**: The supervisor “calls” research by invoking the researcher subgraph and passing results back as tool results; the same pattern could extend to other subgraphs.
4. **Concurrency limits**: Capping concurrent research units avoids rate limits and cost spikes while still allowing parallel work.
5. **Clarification vs. brevity**: Optional clarification improves scope but adds a turn; configuration lets you skip it for faster, single-shot runs.

## Evaluation

### Strengths

- Clear separation between planning (supervisor), execution (researchers), and synthesis (report).
- Parallel research and configurable concurrency.
- Pluggable search backends and models via configuration.
- Optional clarification and retry/compression logic for robustness.

### Limitations

- Latency and cost scale with number of research tasks and search calls.
- Quality depends heavily on prompt design and model choice for brief, research, and report.
- No built-in persistence; state is in-memory per run.

## Tech Stack

- **LangGraph**: StateGraph, Command-based routing, subgraphs.
- **LangChain**: Chat models (init_chat_model), tools, messages, structured output.
- **LangChain Community / Tavily / etc.**: Search and tool integrations.
- **Pydantic**: Configuration and structured tool outputs.
- **Anthropic / OpenAI / etc.**: LLM and optional native search.
- **Python 3.10+**, **uv** for install; optional **LangSmith** for tracing.

## Project Structure

```
open-deep-research/
├── open-deep-research.ipynb     # Walkthrough and usage
├── open_deep_library/           # Package (mapped as open_deep_research)
│   ├── configuration.py        # Configuration and search/model settings
│   ├── deep_researcher.py      # Graph and node definitions
│   ├── prompts.py              # System and user prompts
│   ├── state.py                # Agent, Supervisor, Researcher states and Pydantic tools
│   └── utils.py                # Tools (e.g. Tavily), think_tool, helpers
├── data/                        # Optional sample data
├── images/                      # Architecture diagrams
├── pyproject.toml
└── README.md
```

## Getting Started

1. Install dependencies: `uv sync`
2. Set environment variables, e.g.:
   - `ANTHROPIC_API_KEY`
   - `TAVILY_API_KEY`
3. Run the notebook: it uses the library to build the graph and demonstrates clarification, brief writing, supervisor/researcher flow, and report generation. Adjust `Configuration` (or config passed at runtime) for models, search API, and concurrency.

## Conclusion

This project illustrates a production-style deep research agent: hierarchical state, supervisor–researcher delegation, parallel subgraph execution, and configurable search and models. The patterns (structured tools, subgraphs as tools, compression before aggregation) are reusable for other multi-agent and research workflows.
