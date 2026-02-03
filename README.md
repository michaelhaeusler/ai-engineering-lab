# AI Engineering Lab

A learning portfolio and lab for AI engineering: course work from the **[AI Makerspace AI Engineering Bootcamp](https://aimakerspace.io)** program and original projects, plus a place for future experiments in RAG, agents, and LLM applications.

Most folders contain **course assignments**—notebooks and code provided by AI Makerspace, with tasks and extensions completed by me. Two projects are **original builds**: [fullstack-rag-pdf-chat-app](#original-projects) and [insurance-lens-app](#original-projects). This repo is also the home for **future AI experiments** beyond the course.

## Repo structure

| Folder | Type | Description |
|--------|------|-------------|
| [fullstack-rag-pdf-chat-app](./fullstack-rag-pdf-chat-app) | Original project | Full-stack RAG application: upload PDFs, chat over documents with streaming and vector search. |
| [insurance-lens-app](./insurance-lens-app) | Original project | InsuranceLens: AI assistant for German health insurance policies; clause analysis, policy Q&A with citations, general insurance Q&A via web search. |
| [embeddings-and-rag](./embeddings-and-rag) | Course assignment | Embeddings and RAG from first principles: vector embeddings, semantic search, end-to-end RAG pipeline. |
| [evaluating-rag-with-ragas](./evaluating-rag-with-ragas) | Course assignment | RAG and agent evaluation with RAGAS: synthetic data, multi-metric evaluation, comparative analysis. |
| [production-rag](./production-rag) | Course assignment | Production RAG with LCEL and LangGraph: PDF ingestion, embeddings, vector store, stateful graph orchestration. |
| [agent-with-langgraph](./agent-with-langgraph) | Course assignment | Agentic RAG with LangGraph: tool use, cyclic workflows, self-evaluation and refinement. |
| [advanced-retrieval](./advanced-retrieval) | Course assignment | Advanced retrieval with LangChain and Qdrant: BM25, compression, multi-query, parent-document, ensemble, semantic chunking; RAGAS/LangSmith evaluation. |
| [synthetic-data-generation-and-langsmith](./synthetic-data-generation-and-langsmith) | Course assignment | Synthetic test data with RAGAS and RAG evaluation with LangSmith. |
| [multi-agent-with-langgraph](./multi-agent-with-langgraph) | Course assignment | Hierarchical multi-agent system with LangGraph: meta-supervisor, research and document-writing teams. |
| [open-deep-research](./open-deep-research) | Course assignment | Deep research agent with LangGraph: clarification, research brief, supervisor–researcher delegation, parallel research, final report. |
| [openai-agents-sdk](./openai-agents-sdk) | Course assignment | Multi-agent research workflow with OpenAI Agents SDK: Planner, Search, Writer; structured handoffs and hosted tools. |
| [production-rag-and-guardrails](./production-rag-and-guardrails) | Course assignment | Production RAG with LangGraph and Guardrails AI: input/output validation, PII redaction, topic/jailbreak/profanity checks, caching. |
| [a2a-langgraph](./a2a-langgraph) | Course assignment | A2A (Agent-to-Agent) protocol with LangGraph: server exposes an agent over HTTP; client invokes it as a tool. |
| [langgraph-platform](./langgraph-platform) | Course assignment | LangGraph Platform: build and serve agent graphs via `langgraph.json`, LangGraph Studio, MCP tools. |
| [mcp](./mcp) | Course assignment | OpenAI Responses API: File Search (vector stores, citations) and MCP/connectors. |

## Topics and tech

Across the repo: **RAG** (embeddings, retrieval strategies, reranking, evaluation), **agents** (LangGraph, tool use, multi-agent, supervisor patterns), **evaluation** (RAGAS, LangSmith, synthetic data), **production concerns** (guardrails, caching, LCEL). Tech includes Python, LangChain, LangGraph, OpenAI, Qdrant, Guardrails AI, Next.js/React, FastAPI. Each folder has its own README and dependency setup (e.g. `uv`, `.env`).

## Original projects

**Full-stack RAG PDF chat app** ([fullstack-rag-pdf-chat-app](./fullstack-rag-pdf-chat-app))  
A full-stack application for question-answering over uploaded PDFs. Backend (FastAPI) handles PDF processing, embeddings, and vector search; frontend (Next.js) provides a chat UI with streaming. Built with a custom RAG library, OpenAI embeddings, and in-memory vector search. See the project README for architecture and setup.

**InsuranceLens** ([insurance-lens-app](./insurance-lens-app))  
An AI assistant for German health insurance policies. It analyzes uploaded policy PDFs for clauses that differ from typical norms, answers policy-specific questions with citations, and handles general insurance questions via web search. Implemented with LangGraph (routing, policy RAG, and general Q&A agents), FastAPI, Next.js, Qdrant, Cohere rerank, Tavily, and RAGAS for evaluation. See the project README for details.

## Using this repo

Clone the repo and open the folder you care about. Each project has its own README with setup (dependencies, environment variables, how to run notebooks or apps). Many use `uv` for Python; some need API keys (OpenAI, Tavily, Guardrails, etc.)—see the project README or `.env.example` where present.

## Attribution

Course materials and assignments are by the **[AI Makerspace](https://aimakerspace.io)** AI Engineering Bootcamp that I attended. Solutions, extensions, and notebook completions in the course-assignment folders are my work. The two original projects—fullstack-rag-pdf-chat-app and insurance-lens-app—are my own builds. This repo will also host future AI experiments unrelated to the course.
