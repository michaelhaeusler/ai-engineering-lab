# Production RAG with LangChain and LangGraph

This project demonstrates the implementation of a production-ready Retrieval-Augmented Generation (RAG) system using LangChain's LCEL (LangChain Expression Language) and LangGraph for orchestration. The system processes PDF documents, creates semantic embeddings, and provides context-aware responses using local open-source language models.

## Overview

The project consists of three Jupyter notebooks that progressively build understanding and implementation of modern RAG architectures:

1. **Ollama_Setup_and_Testing.ipynb** - Infrastructure setup and validation
2. **LangChain_LangGraph_Practice.ipynb** - Core RAG implementation practice
3. **Assignment_Introduction_to_LCEL_and_LangGraph_LangChain_Powered_RAG.ipynb** - Complete production RAG system with advanced concepts

## Architecture and Techniques

### LangChain Expression Language (LCEL)

LCEL provides a declarative, composable approach to building LLM applications. The system leverages LCEL's pipe operator (`|`) to create chains that seamlessly connect components:

- **Runnables**: Standardized interfaces for all LangChain components (models, prompts, parsers, retrievers)
- **Composition**: Chains are constructed by composing Runnables using the pipe operator
- **Streaming**: Built-in support for streaming responses for real-time applications
- **Parallelization**: Batch processing capabilities for handling multiple inputs efficiently

### LangGraph State Management

The system implements a stateful graph architecture where application state flows through nodes:

```python
class State(TypedDict):
    question: str
    context: list[Document]
    response: str
```

This state object serves as the single source of truth, enabling:
- **Traceability**: Complete visibility into data flow through the pipeline
- **Modularity**: Nodes operate independently while sharing state
- **Extensibility**: Easy addition of new nodes (fact-checking, human-in-the-loop, etc.)

### Vector Search Pipeline

The RAG pipeline implements a complete document processing workflow:

1. **Document Ingestion**: PDF documents are loaded using PyMuPDFLoader with async support
2. **Text Chunking**: RecursiveCharacterTextSplitter with token-aware splitting (750 tokens per chunk, using tiktoken for accurate tokenization)
3. **Embedding Generation**: Local embeddings using Ollama's `embeddinggemma` model (768-dimensional vectors)
4. **Vector Storage**: Qdrant vector database with cosine similarity for semantic search
5. **Retrieval**: Top-k retrieval (k=5) of most relevant document chunks based on query similarity

### Graph-Based Orchestration

The system uses LangGraph to construct a directed acyclic graph (DAG) with two primary nodes:

- **Retrieve Node**: Executes semantic search against the vector store and populates context
- **Generate Node**: Formats context and query into a RAG prompt, invokes the LLM, and parses the response

The graph architecture enables natural extension to more complex flows, including conditional routing, loops, and multi-agent coordination.

## Key Learnings

### 1. Composable Architecture

LCEL's composable design allows for rapid prototyping and iteration. Components can be easily swapped (e.g., changing embedding models or LLMs) without restructuring the entire pipeline.

### 2. State Management Patterns

The TypedDict-based state pattern provides type safety and clear contracts between nodes. This approach scales well to complex multi-step workflows where intermediate results need to be preserved and passed between stages.

### 3. Local Model Deployment

Using Ollama for local model deployment provides:
- **Cost Efficiency**: No API costs for inference or embeddings
- **Privacy**: Data never leaves the local environment
- **Performance Control**: Direct control over model selection and resource allocation
- **Offline Capability**: Full functionality without internet connectivity

### 4. Production Considerations

The implementation highlights several production-readiness considerations:
- **Chunking Strategy**: Token-aware splitting ensures proper handling of model context windows
- **Embedding Dimensions**: Understanding model-specific embedding dimensions (768 for embeddinggemma) is critical for vector database configuration
- **Error Handling**: The system demonstrates handling edge cases (e.g., queries with no relevant context)
- **Monitoring**: Optional LangSmith integration provides observability for debugging and optimization

### 5. Extensibility Patterns

The graph-based architecture naturally supports extensions such as:
- Conditional edges for handling different query types
- Additional nodes for fact-checking or validation
- Human-in-the-loop workflows for sensitive applications
- Multi-retrieval strategies (hybrid search, re-ranking)

## Evaluation

### Strengths

- **Modularity**: Clear separation of concerns between retrieval and generation
- **Type Safety**: TypedDict state provides compile-time guarantees
- **Local Deployment**: Complete privacy and cost control with local models
- **Observability**: LangSmith integration enables comprehensive tracing
- **Scalability**: Architecture supports extension to complex multi-agent systems

### Limitations and Future Improvements

- **In-Memory Storage**: Current Qdrant implementation uses in-memory storage, requiring persistence layer for production
- **Naive Chunking**: RecursiveCharacterTextSplitter doesn't respect document structure (headers, sections); semantic chunking would improve retrieval quality
- **Single Retrieval Strategy**: No hybrid search (dense + sparse) or re-ranking for improved relevance
- **No Query Understanding**: Missing query expansion or rewriting for better retrieval
- **Limited Context Handling**: Fixed context window without dynamic chunk selection based on query complexity

### Performance Characteristics

- **Embedding Generation**: ~768-dimensional vectors with embeddinggemma
- **Inference Speed**: ~27-28 tokens/second with gpt-oss:20b on CPU
- **Retrieval Latency**: Sub-millisecond for in-memory vector search
- **End-to-End Latency**: ~15-20 seconds per query (dominated by LLM inference)

## Tech Stack

### Core Frameworks
- **LangChain**: LLM application framework and orchestration
- **LangGraph**: Graph-based workflow orchestration for stateful applications
- **LCEL**: LangChain Expression Language for composable chain construction

### Vector Database
- **Qdrant**: Vector database for semantic search (in-memory for development)

### Local LLM Infrastructure
- **Ollama**: Local model serving infrastructure
- **gpt-oss:20b**: Open-source chat model for text generation
- **embeddinggemma**: Open-source embedding model (768 dimensions)

### Document Processing
- **PyMuPDF**: PDF document loading and parsing
- **tiktoken**: Tokenization for accurate chunk sizing

### Observability
- **LangSmith**: Tracing, monitoring, and debugging platform

### Development Environment
- **Jupyter**: Interactive development and experimentation
- **Python 3.12**: Runtime environment
- **uv**: Fast Python package manager and dependency resolver

## Project Structure

```
04_Production_RAG/
├── Ollama_Setup_and_Testing.ipynb          # Infrastructure setup and validation
├── LangChain_LangGraph_Practice.ipynb      # Core RAG implementation practice
├── Assignment_Introduction_to_LCEL_and_LangGraph_LangChain_Powered_RAG.ipynb  # Complete production system
├── data/
│   └── howpeopleuseai.pdf                  # Knowledge base document
├── pyproject.toml                           # Project dependencies
└── README.md                                # This file
```

## Getting Started

### Prerequisites

1. Python 3.12
2. Ollama installed and running
3. Required models pulled:
   ```bash
   ollama pull gpt-oss:20b
   ollama pull embeddinggemma:latest
   ```

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Verify Ollama setup by running `Ollama_Setup_and_Testing.ipynb`

3. Execute notebooks in sequence:
   - Start with the setup notebook to validate infrastructure
   - Practice with the LangChain/LangGraph notebook
   - Complete the full assignment notebook

4. (Optional) Configure LangSmith for tracing:
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_API_KEY="your-api-key"
   export LANGCHAIN_PROJECT="RAG-Assignment"
   ```

## Conclusion

This project demonstrates the practical implementation of production-grade RAG systems using modern orchestration frameworks. The combination of LCEL's composability and LangGraph's state management provides a robust foundation for building complex, multi-step AI applications. The local deployment approach showcases how open-source models can deliver production-quality results while maintaining privacy and cost efficiency.
