# Production RAG and Guardrails

Production-ready RAG pipeline with a LangGraph agent and Guardrails AI for input/output validation and safety. Implements caching for embeddings and optional LLM caching, topic restriction, jailbreak detection, PII redaction, and output checks.

## Architecture

- **RAG pipeline** (`langgraph_agent_lib/rag.py`): PDF load → chunking → cache-backed embeddings (OpenAI + `LocalFileStore`) → in-memory Qdrant → MMR retriever → prompt + LLM. Exposed to the agent as a RAG tool.
- **LangGraph agent** (`langgraph_agent_lib/agents.py`): Reusable graph with optional input/output guardrail nodes. Tools: Tavily, Arxiv, and the RAG chain. Optional variant adds helpfulness evaluation and refinement loops.
- **Guardrails** (`langgraph_agent_lib/guardrails.py`): Composable guards (Guardrails AI Hub). Input: two-stage validation — PII redaction (`on_fail="fix"`) then content checks (topic, jailbreak, profanity). Output: PII/profanity (and optional factuality) before response is returned. Validation implemented as LangGraph nodes; failed input routes to an error node, failed output can be replaced with a safe message or marked for refinement.
- **Caching** (`langgraph_agent_lib/caching.py`): Cache-backed embeddings via `LocalFileStore`; LLM cache configurable as in-memory or SQLite.

## Key techniques

- **Input guardrails**: Separate PII guard (redact) and content guard (reject). Topic allow/block lists, jailbreak detection, profanity filter.
- **Output guardrails**: Same PII/profanity stack on model output; optional RAG factuality guard using an eval model.
- **Graph routing**: Entry → `validate_input` → agent or `input_error`; after agent → tools or `validate_output` → end. Conditional edges drive validation and error paths.
- **State**: `GuardrailsAgentState` (or extended variants) carries `messages`, `input_validation_passed`, `output_validation_passed`, `validation_error` for guardrail-aware flows.

## Evaluation

- **Strengths**: Modular guard composition, clear split between input (redact then validate) and output checks, optional guardrails so the same agent can run with or without safety layers. Caching reduces embedding and optionally LLM cost.
- **Limitations**: In-memory Qdrant and file-based embedding cache are for single-process/prototyping; production would typically use persistent vector DB and shared cache (e.g. Redis). Current LLM cache is exact-match only; semantic or E2E caching would improve hit rates.

## Tech stack

Python 3.11, LangChain (core, community, OpenAI), LangGraph, Guardrails AI, Qdrant (in-memory), PyMuPDF, Tenacity, Tavily, Arxiv. Optional: LangSmith.

## Getting started

1. **Dependencies**

   ```bash
   uv sync
   ```

2. **Guardrails API**  
   The `guardrails configure` CLI can be unreliable in 0.5.14; use the script instead:

   ```bash
   uv run python configure_guardrails.py
   # or: uv run python configure_guardrails.py YOUR_API_KEY
   # or: export GUARDRAILS_API_KEY=... && uv run python configure_guardrails.py
   ```

   API key: [Guardrails AI Hub](https://hub.guardrailsai.com/keys).

3. **Install guards**

   ```bash
   uv run guardrails hub install hub://tryolabs/restricttotopic
   uv run guardrails hub install hub://guardrails/detect_jailbreak
   uv run guardrails hub install hub://guardrails/competitor_check
   uv run guardrails hub install hub://arize-ai/llm_rag_evaluator
   uv run guardrails hub install hub://guardrails/profanity_free
   uv run guardrails hub install hub://guardrails/guardrails_pii
   ```

4. Run the assignment notebook `Prototyping_LangChain_Application_with_Production_Minded_Changes_Assignment.ipynb` for end-to-end RAG, agent, and guardrail setup.

For a deeper walkthrough of guard creation and graph integration, see `GUARDRAILS_EXPLAINED.md`.
