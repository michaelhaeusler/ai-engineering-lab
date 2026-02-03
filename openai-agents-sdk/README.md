# OpenAI Agents SDK – Research Bot

This project implements a multi-agent research workflow using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) (package: `openai-agents`). It is a notebook adaptation of the SDK’s [Research Bot](https://github.com/openai/openai-agents-python/tree/main/examples/research_bot): a Planner agent produces a search plan, a Search agent runs web searches, and a Writer agent synthesizes a report with follow-up questions.

## Overview

The pipeline is linear and hand-off based: no single “supervisor” graph. A **ResearchManager** orchestrates three agents in sequence—plan → search → write—using structured outputs for handoffs and the SDK’s **Runner** for execution. Web search uses the Responses API **WebSearchTool** (hosted). Progress is shown in the console via Rich, and runs can be inspected with OpenAI platform traces.

## Architecture

### Agents

1. **Planner Agent**
   - **Role:** Turn the user query into a list of 5–20 web search queries.
   - **Model:** e.g. `gpt-4.1`.
   - **Output:** `WebSearchPlan` (Pydantic): list of `WebSearchItem` (reason, query).
   - **Why structured output:** Ensures a fixed schema for the next step (handoff to Search).

2. **Search Agent**
   - **Role:** For each search term, call web search and return a short summary (2–3 paragraphs, &lt;300 words).
   - **Tools:** `WebSearchTool()` (Responses API hosted tool).
   - **Model settings:** `tool_choice="required"` so the agent always uses search.
   - **Output:** Plain-text summaries consumed by the Writer.

3. **Writer Agent**
   - **Role:** Take the original query and all search summaries, then produce an outline, a long markdown report (e.g. 5–10 pages), and exactly five follow-up questions.
   - **Model:** e.g. `o3-mini` (reasoning model for structure and synthesis).
   - **Output:** `ReportData` (Pydantic): `short_summary`, `markdown_report`, `follow_up_questions`.

### Orchestration (ResearchManager)

- **Plan:** `Runner.run(planner_agent, query)` → parse `final_output_as(WebSearchPlan)`.
- **Search:** For each `WebSearchItem`, `Runner.run(search_agent, input)`; batches of up to 5 concurrent searches to respect rate limits and latency.
- **Write:** `Runner.run_streamed(writer_agent, input)`; progress messages updated periodically while consuming `stream_events()`; final result via `final_output_as(ReportData)`.

No graph engine: flow is explicit in Python (async/await and `ResearchManager` methods).

### Observability and UX

- **Traces:** `trace()`, `custom_span()`, `gen_trace_id()` from the SDK; link to `https://platform.openai.com/traces/trace?trace_id=...`.
- **Progress:** A **Printer** class (Rich Live + spinners) shows “Planning…”, “Searching… 3/12”, “Writing…”, etc.

## Key Techniques

### Structured outputs for handoffs

Planner and Writer use Pydantic `output_type`. That gives predictable shapes (`WebSearchPlan`, `ReportData`) and avoids parsing free-form text between agents.

### Hosted tools (Responses API)

`WebSearchTool` is a hosted tool from the Responses API; no custom server. The SDK supports other hosted capabilities (e.g. code interpreter, file search, MCP) via the same pattern.

### Tool choice

`ModelSettings(tool_choice="required")` on the Search agent forces tool use so every request results in a web search call.

### Runner and streaming

- `Runner.run(agent, input)` for one-shot runs; `result.final_output` / `result.final_output_as(MyModel)` for the parsed result.
- `Runner.run_streamed(agent, input)` for streaming; `stream_events()` and `final_output_as(ReportData)` for progress and final report.

### Concurrency

Searches are run in batches (e.g. 5 at a time) with `asyncio.create_task` and `asyncio.as_completed` to balance throughput and rate limits.

## Key Learnings

1. **Structured outputs** simplify multi-agent handoffs and make the pipeline easier to debug and extend.
2. **Hosted tools** reduce integration work; the trade-off is dependency on the Responses API and its tool set.
3. **Explicit orchestration** (ResearchManager) is clear and testable; for more dynamic routing or cycles, a graph (e.g. LangGraph) would be a better fit.
4. **Reasoning models** (e.g. o3-mini) help for the Writer’s planning and synthesis; simpler models can suffice for Planner and Search.
5. **Batching and streaming** improve perceived performance (parallel search, live writing updates) and align with API limits.

## Evaluation

### Strengths

- Clear separation of roles (plan, search, write) and clean handoffs via Pydantic.
- Minimal setup: SDK + API key + optional `nest_asyncio` for Jupyter.
- Observability via SDK trace/span and platform traces.
- Progress UX and streaming for long-running writes.

### Limitations

- Linear flow only; no conditional branching or multi-step reasoning loops in the SDK layer.
- Hosted tools only (e.g. WebSearch); custom tools require the SDK’s tool interface.
- Cost and latency scale with number of searches and writer length; no built-in caching.

## Tech Stack

- **openai-agents** (OpenAI Agents SDK): `Agent`, `Runner`, `WebSearchTool`, `trace` / `custom_span` / `gen_trace_id`, `ModelSettings`.
- **OpenAI Responses API**: Hosted web search (and other tools as needed).
- **Pydantic**: `WebSearchPlan`, `WebSearchItem`, `ReportData`.
- **Rich**: Console progress (Live, Spinner).
- **Python 3.13+**, **uv** for install; **Jupyter** for the notebook.

## Project Structure

```
openai-agents-sdk/
├── OpenAI_Agents_SDK.ipynb   # Research bot: agents, ResearchManager, run example
├── pyproject.toml            # openai-agents, logfire, jupyter
└── README.md
```

## Getting Started

1. Install: `uv sync`
2. Set `OPENAI_API_KEY` (e.g. in env or via getpass in the notebook).
3. Run the notebook top to bottom: it defines the three agents and `ResearchManager`, then runs a sample query and prints the report and follow-up questions.
4. Optional: use `nest_asyncio.apply()` if running async `Runner` calls inside Jupyter.

## Conclusion

This project shows how to build a multi-agent research pipeline with the OpenAI Agents SDK: structured outputs for handoffs, hosted WebSearchTool, Runner-based execution with optional streaming, and a small orchestrator with batched search and progress display. The pattern is reusable for other linear, multi-agent workflows (e.g. summarization, Q&A over search) and can be extended with more agents or tools as the SDK and Responses API evolve.
