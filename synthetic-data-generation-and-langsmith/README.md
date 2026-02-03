# Synthetic Data Generation and RAG Evaluation with LangSmith

This project demonstrates a complete workflow for generating synthetic test data using RAGAS and evaluating RAG systems with LangSmith. The implementation shows how knowledge graph-based synthetic data generation can create diverse, realistic test cases, and how systematic evaluation enables iterative improvement of RAG pipelines.

## Overview

The project implements a data-driven approach to RAG system development: generating synthetic test datasets from source documents, evaluating baseline RAG performance, iterating on system components, and measuring improvements through comparative evaluation. This workflow addresses the critical challenge of obtaining high-quality evaluation data early in the development process.

## Architecture

### Synthetic Data Generation with RAGAS

RAGAS uses a knowledge graph-based approach to generate synthetic test data:

1. **Knowledge Graph Construction**: Source documents are inserted as nodes in a knowledge graph
2. **Graph Transformation**: Default transformations create additional nodes:
   - Document summaries
   - Extracted headlines
   - Broad themes
3. **Relationship Building**: Cosine similarity and heuristics create edges between related nodes
4. **Query Generation**: Query synthesizers generate questions from personas and scenarios

### Query Synthesizers

The system uses three types of query synthesizers with different complexity levels:

- **SingleHopSpecificQuerySynthesizer**: Generates simple, factual questions answerable from a single source (50% distribution)
- **MultiHopAbstractQuerySynthesizer**: Creates abstract questions requiring reasoning across concepts (25% distribution)
- **MultiHopSpecificQuerySynthesizer**: Produces complex questions needing multiple specific facts (25% distribution)

This distribution ensures evaluation covers both simple retrieval and complex reasoning scenarios.

### RAG Pipeline

The baseline RAG system implements a standard pipeline:

1. **Document Processing**: PDF loading and text chunking with RecursiveCharacterTextSplitter
2. **Embedding Generation**: OpenAI text-embedding-3-small for vector representations
3. **Vector Storage**: Qdrant in-memory vector database
4. **Retrieval**: Top-k retrieval (k=10) based on query similarity
5. **Generation**: GPT-4.1-mini with context-aware prompting

### Evaluation Framework

LangSmith provides the evaluation infrastructure:

1. **Dataset Management**: Synthetic test data is loaded into LangSmith datasets
2. **Multiple Evaluators**: 
   - QA evaluator: Measures answer correctness and completeness
   - Labeled helpfulness evaluator: Assesses response utility to users
   - Custom criteria evaluator: Evaluates specific attributes (e.g., "dopeness")
3. **Comparative Analysis**: Side-by-side comparison of different pipeline versions
4. **Metadata Tracking**: Revision IDs enable tracking of changes across iterations

## Key Techniques

### Knowledge Graph-Based Generation

RAGAS's knowledge graph approach provides several advantages:
- **Structured Representation**: Documents and their relationships are explicitly modeled
- **Rich Context**: Transformations (summaries, themes) provide multiple perspectives
- **Relationship Discovery**: Graph edges capture semantic relationships between concepts
- **Query Diversity**: Different graph traversal patterns generate varied question types

### Iterative Improvement Workflow

The project demonstrates a systematic improvement process:

1. **Baseline Evaluation**: Establish performance metrics on synthetic dataset
2. **Hypothesis Formation**: Identify potential improvements (prompts, chunking, embeddings)
3. **Implementation**: Make targeted changes to specific components
4. **Re-evaluation**: Measure impact of changes on evaluation metrics
5. **Analysis**: Compare results to understand which changes drive improvements

### Evaluation Metrics

Multiple evaluators provide comprehensive performance assessment:
- **Correctness**: Factual accuracy of responses
- **Helpfulness**: Utility and relevance to users
- **Custom Criteria**: Domain-specific quality measures

## Key Learnings

1. **Synthetic Data Quality**: Knowledge graph-based generation produces more realistic and diverse test cases than simple template-based approaches. The combination of personas, scenarios, and graph relationships creates questions that mirror real-world usage patterns.

2. **Evaluation Importance**: Without systematic evaluation, it's difficult to measure the impact of changes. Synthetic datasets enable early iteration when real user data is unavailable.

3. **Component Interactions**: Changes to one component (e.g., embedding model) can affect multiple metrics. Better embeddings improve retrieval quality, which can increase both correctness and helpfulness, but may also lead to overconfidence when incorrect information is retrieved.

4. **Chunk Size Trade-offs**: Larger chunks preserve context and relationships but may include irrelevant information. The optimal size depends on query complexity—multi-hop questions may benefit from larger chunks, while single-hop questions may perform better with smaller, focused chunks.

5. **Embedding Model Impact**: Upgrading from text-embedding-3-small to text-embedding-3-large significantly improves retrieval quality. Higher-dimensional embeddings capture semantic relationships more accurately, leading to better context selection.

6. **Prompt Engineering**: Explicit instructions in prompts (e.g., "make your answer rad") can influence output style without necessarily improving correctness. Style changes should be evaluated separately from functional improvements.

## Evaluation

### Strengths

- **Early Signal**: Synthetic data generation enables evaluation before production deployment
- **Diverse Test Cases**: Knowledge graph approach generates varied question types and complexity levels
- **Systematic Iteration**: Structured evaluation workflow enables data-driven improvements
- **Comparative Analysis**: LangSmith's comparison features make it easy to measure impact of changes
- **Multiple Metrics**: Different evaluators provide comprehensive performance assessment

### Limitations

- **Synthetic vs. Real**: Generated questions may not perfectly match real user queries
- **Cost**: Multiple LLM calls for generation and evaluation increase operational costs
- **Metric Interpretation**: RAGAS scores are directional—absolute values aren't comparable across systems
- **Overconfidence Risk**: Better retrieval may increase confidence even when answers are incorrect
- **Single Variable Testing**: Changing multiple components simultaneously makes it difficult to isolate individual impacts

### Performance Characteristics

- **Data Generation**: 10 test cases generated in ~2-5 minutes (depends on document size)
- **Evaluation Latency**: ~5-10 seconds per test case (includes retrieval, generation, and evaluation)
- **Total Evaluation Time**: ~2-5 minutes for 10 test cases
- **Token Usage**: ~500-1000 tokens per generated question, ~2000-3000 tokens per evaluation

## Tech Stack

- **RAGAS**: Synthetic test data generation and evaluation framework
- **LangSmith**: Evaluation platform with dataset management and comparative analysis
- **LangChain**: RAG pipeline construction and orchestration
- **OpenAI API**: 
  - GPT-4.1-nano for synthetic data generation
  - GPT-4.1-mini for RAG generation
  - GPT-4.1 for evaluation
  - text-embedding-3-small/large for embeddings
- **Qdrant**: Vector database for RAG retrieval
- **PyMuPDF**: PDF document processing
- **NLTK**: Natural language processing for data preparation
- **Python 3.13** with **uv** for dependency management

## Project Structure

```
synthetic-data-generation-and-langsmith/
├── Synthetic_Data_Generation_RAGAS_&_LangSmith_Assignment.ipynb
├── data/                                    # Source documents
│   ├── AIE7_Projects_with_Domains.csv
│   └── howpeopleuseai.pdf
├── img/                                     # Evaluation screenshots
│   ├── langsmith-eval-1.png
│   ├── langsmith-eval-2.png
│   └── langsmith-eval-3.png
├── usecase_data_kg.json                    # Saved knowledge graph
└── pyproject.toml                          # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.13
- API Keys:
  - OpenAI API key
  - LangSmith API key

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-key"
   export LANGCHAIN_API_KEY="your-langsmith-key"
   export LANGCHAIN_TRACING_V2="true"
   export LANGCHAIN_PROJECT="Synthetic-Data-Generation"
   ```

3. Download NLTK data (handled automatically in notebook):
   - punkt tokenizer
   - averaged_perceptron_tagger

4. Execute the notebook:
   - Generate synthetic test data using RAGAS
   - Load data into LangSmith dataset
   - Evaluate baseline RAG chain
   - Iterate on pipeline components
   - Compare evaluation results

## Implementation Highlights

### Synthetic Data Generation

The knowledge graph approach creates structured test data:
- Documents are transformed into graph nodes with relationships
- Query synthesizers generate questions from different complexity levels
- Generated data includes questions, reference answers, and context

### Evaluation Workflow

The evaluation process demonstrates:
- Dataset creation and management in LangSmith
- Multiple evaluator configuration (QA, helpfulness, custom criteria)
- Metadata tracking for version comparison
- Comparative analysis of different pipeline versions

### Iterative Improvement

The project shows systematic improvement:
- Baseline establishment with initial metrics
- Targeted changes to prompts, chunking, and embeddings
- Re-evaluation to measure impact
- Analysis of which changes drive improvements

## Conclusion

This project demonstrates how synthetic data generation and systematic evaluation enable data-driven RAG system development. The knowledge graph-based approach produces diverse, realistic test cases, while LangSmith provides the infrastructure for comparative evaluation. The iterative improvement workflow shows how targeted changes can be measured and validated, providing a foundation for production-grade RAG system development.

The patterns demonstrated—synthetic data generation, multi-metric evaluation, and iterative improvement—form essential practices for building reliable, high-quality RAG systems that can be systematically improved based on quantitative feedback.
