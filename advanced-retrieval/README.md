# Advanced Retrieval with LangChain

This project implements and compares multiple retrieval strategies for RAG using LangChain and Qdrant. It covers dense and sparse retrieval, reranking, query expansion, parent-document retrieval, ensemble methods, and semantic chunking, with evaluation via RAGAS and LangSmith.

## Overview

The notebook builds a shared RAG chain and swaps in different retrievers to compare behavior and performance. Data is structured project/domain CSV with rich metadata. Each strategy is run on the same prompts and evaluated for correctness, must-mention coverage, latency, and cost.

## Retrieval Strategies

### Naive (Dense) Retrieval

- Single embedding-based retriever over documents.
- Cosine similarity, top-k (e.g. k=10).
- Baseline for comparison.

### BM25 (Sparse Retrieval)

- Bag-of-words, term-frequency based (BM25).
- Complements dense retrieval: strong on exact/keyword match, can avoid false positives when embeddings over-generalize.

### Contextual Compression (Reranking)

- Retrieve more candidates (e.g. 10), then rerank with Cohere to keep top N (e.g. 5).
- Reduces irrelevant context and token usage at the cost of extra API calls and latency.

### Multi-Query Retrieval

- LLM generates multiple query variants from the user question.
- Each variant is run against the same retriever; results are deduplicated and merged.
- Improves recall for underspecified or ambiguous questions.

### Parent Document Retriever

- Small chunks (e.g. for retrieval) are linked to larger “parent” documents.
- Retrieve by small chunks, return parent content for generation.
- Balances precise retrieval with enough context for the LLM.

### Ensemble Retriever

- Combines several retrievers (e.g. BM25, naive, parent-document, compression, multi-query) with rank fusion and configurable weights.
- Can improve robustness and recall at the cost of latency and complexity.

### Semantic Chunking

- Not a retriever but a chunking strategy: split by semantic similarity (e.g. embedding distance, percentile threshold).
- Chunks respect topic boundaries; same retriever (e.g. naive) is used on semantic chunks.
- Compared in the notebook as “semantic chunking on” vs “off” with regular chunking.

## Evaluation

- **RAGAS**: Retriever-specific metrics (e.g. faithfulness, context precision/recall, answer relevancy) on synthetic or fixed Q&A sets.
- **LangSmith**: Runs each retriever on a shared dataset, compares correctness, must-mention, latency, and cost; results are summarized in `data/langsmith-results.md` and `images/langsmith-bar-charts.png`.

## Key Learnings

1. **Dense vs sparse**: Embeddings excel at semantic match; BM25 excels at keyword/precision. Choice depends on query and corpus (e.g. BM25 can reduce false positives on security/domain-style questions).
2. **Reranking trade-offs**: Reranking (contextual compression) improves relevance and can reduce tokens but adds latency and cost; impact varies by corpus and k.
3. **Ensemble cost**: Combining many retrievers increases tokens and latency; gains should be validated with evaluation.
4. **Chunking matters**: Semantic chunking can improve retrieval quality when documents have clear thematic breaks; it is complementary to retriever choice.
5. **Evaluate per strategy**: Subjective “feel” is unreliable; RAGAS and LangSmith give comparable, reproducible signals across strategies.

## Tech Stack

- **LangChain / LangChain Community**: RAG chains, retrievers, document loaders, text splitters.
- **LangChain OpenAI**: Chat and embeddings (e.g. GPT-4, text-embedding-3-small).
- **LangChain Cohere**: Reranker for contextual compression.
- **LangChain Experimental**: SemanticChunker.
- **Qdrant**: Vector store (in-memory for the assignment).
- **rank-bm25**: BM25Retriever.
- **RAGAS**: Evaluation metrics and runs.
- **LangSmith**: Evaluation runs and comparison (optional).
- **Python 3.13**, **uv** for dependencies.

## Project Structure

```
advanced-retrieval/
├── Advanced_Retrieval_with_LangChain_Assignment.ipynb
├── data/
│   ├── howpeopleuseai.pdf
│   ├── langsmith-results.md      # Summary of LangSmith eval results
│   └── Projects_with_Domains.csv
├── images/
│   └── langsmith-bar-charts.png
├── pyproject.toml
└── README.md
```

## Getting Started

1. Install dependencies: `uv sync`
2. Set environment variables:
   - `OPENAI_API_KEY`
   - `COHERE_API_KEY` (for contextual compression/reranking)
   - LangSmith env vars if running LangSmith evaluation
3. Run the notebook top to bottom: data load, Qdrant setup, then each retrieval strategy and finally RAGAS/LangSmith evaluation.

## Conclusion

This project provides a single RAG pipeline and a consistent evaluation setup to compare advanced retrieval methods. It shows how dense and sparse retrieval, reranking, multi-query, parent-document, and ensemble strategies affect correctness, coverage, latency, and cost, and how semantic chunking can be evaluated alongside them. The workflow is suitable for choosing and tuning retrieval and chunking in production RAG systems.
