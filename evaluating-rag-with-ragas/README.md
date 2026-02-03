# Evaluating RAG and Agents with RAGAS

This project demonstrates comprehensive evaluation of RAG systems and agentic applications using RAGAS (Retrieval-Augmented Generation Assessment). The implementation covers synthetic data generation, multi-metric evaluation, and systematic performance analysis to enable data-driven improvements in retrieval and generation quality.

## Overview

The project implements a complete evaluation workflow for both traditional RAG pipelines and agentic systems. Using RAGAS's framework-agnostic evaluation framework, the system generates synthetic test data, evaluates multiple quality dimensions, and provides comparative analysis to guide iterative improvements. The implementation demonstrates how systematic evaluation reveals which components drive performance gains and which optimizations may not justify their costs.

## Architecture

### RAG Evaluation Workflow

The RAG evaluation process follows a systematic approach:

1. **Synthetic Data Generation**: RAGAS knowledge graph-based generation creates diverse test questions with reference answers and contexts
2. **Baseline Evaluation**: Initial RAG system is evaluated across multiple metrics
3. **Iterative Improvement**: Components are modified (chunking, retrieval, reranking)
4. **Comparative Analysis**: Performance changes are measured and attributed to specific modifications

### Agent Evaluation Workflow

Agent evaluation extends RAG evaluation with agent-specific metrics:

1. **Agent Construction**: ReAct agent with tool-calling capabilities
2. **Message Conversion**: LangGraph messages are converted to RAGAS format
3. **Multi-Metric Evaluation**: Agent-specific metrics assess tool usage, goal achievement, and topic adherence
4. **Performance Analysis**: Metrics reveal agent behavior patterns and failure modes

## Key Techniques

### RAGAS Metrics for RAG Systems

The project evaluates RAG systems using six core metrics:

- **LLMContextRecall**: Measures how much of the relevant context from the knowledge base is retrieved and used
- **Faithfulness**: Assesses whether the answer is grounded in the provided context (no hallucination)
- **FactualCorrectness**: Evaluates factual accuracy of responses against reference answers
- **ResponseRelevancy**: Measures how relevant the answer is to the question asked
- **ContextEntityRecall**: Evaluates whether all relevant entities from the context are included in the answer
- **NoiseSensitivity**: Tests robustness by measuring performance degradation when noise is added to context

### RAGAS Metrics for Agents

Agent evaluation uses specialized metrics:

- **ToolCallAccuracy**: Measures correctness of tool selection and parameter usage
- **AgentGoalAccuracy**: Binary metric assessing whether the agent achieved the user's goal (with or without reference)
- **TopicAdherence**: Evaluates whether agent responses stay within the intended topic domain

### Synthetic Data Generation

RAGAS generates test data using knowledge graph-based synthesis:
- Documents are transformed into graph nodes with relationships
- Query synthesizers generate questions of varying complexity
- Generated data includes questions, reference answers, and ground truth contexts

### Message Format Conversion

For agent evaluation, LangGraph messages must be converted to RAGAS format:
- LangChain message objects (HumanMessage, AIMessage, ToolMessage) are converted
- RAGAS trace format preserves conversation flow and tool calls
- Conversion enables framework-agnostic evaluation

## Key Learnings

1. **Metric Selection**: Different metrics reveal different aspects of system performance. Context Recall identifies retrieval issues, while Faithfulness catches hallucination. A comprehensive evaluation requires multiple metrics.

2. **Component Isolation**: Changing multiple components simultaneously makes it impossible to attribute improvements. Systematic single-variable testing reveals which changes drive performance gains and which add cost without proportional benefit.

3. **Cost-Benefit Analysis**: Advanced techniques (e.g., reranking) may provide minimal improvements (0-7%) while significantly increasing cost (10-50x) and latency (2-4x). Evaluation enables informed trade-off decisions.

4. **Chunking Impact**: Increasing chunk size from 50 to 500 characters with overlap dramatically improves most metrics (200-800% improvements). This simple change often provides more value than complex retrieval enhancements.

5. **Reranking Trade-offs**: In this use case, reranking provided minimal additional benefit over improved chunking alone. The technique may be more valuable for multi-hop queries or larger document collections, but evaluation is necessary to validate assumptions.

6. **Agent Evaluation Complexity**: Agent evaluation requires different metrics than RAG evaluation. Tool call accuracy, goal achievement, and topic adherence reveal agent-specific behaviors that standard RAG metrics miss.

7. **Synthetic Data Quality**: Knowledge graph-based generation produces diverse, realistic test cases that enable early evaluation before production deployment.

## Evaluation

### Strengths

- **Comprehensive Metrics**: Multiple metrics provide holistic performance assessment across different quality dimensions
- **Framework Agnostic**: RAGAS works with any RAG or agent implementation, not just LangChain
- **Comparative Analysis**: Side-by-side evaluation enables clear understanding of improvement sources
- **Cost Awareness**: Evaluation reveals when optimizations don't justify their costs
- **Early Signal**: Synthetic data enables evaluation before production deployment

### Limitations

- **Metric Interpretation**: RAGAS scores are directional—absolute values aren't comparable across systems
- **Synthetic vs. Real**: Generated test cases may not perfectly match real user queries
- **Evaluation Cost**: Multiple LLM calls for evaluation increase operational costs
- **Single Variable Testing**: Requires discipline to test one change at a time
- **Metric Selection**: Choosing appropriate metrics requires domain knowledge

### Performance Characteristics

**RAG Evaluation:**
- Synthetic data generation: ~2-5 minutes for 10 test cases
- Evaluation latency: ~5-10 seconds per test case
- Total evaluation time: ~2-5 minutes for 10 test cases

**Agent Evaluation:**
- Message conversion: <1 second
- Metric calculation: ~2-5 seconds per metric per test case
- Tool call accuracy: Direct comparison (fast)
- Goal accuracy: LLM-based evaluation (~2-3 seconds)
- Topic adherence: LLM-based evaluation (~2-3 seconds)

## Tech Stack

- **RAGAS**: Evaluation framework for RAG and agent systems
- **LangChain**: RAG pipeline construction
- **LangGraph**: Agent workflow orchestration
- **OpenAI API**: 
  - GPT-4.1 for synthetic data generation
  - GPT-4.1-mini for RAG generation and evaluation
  - GPT-4o-mini for agent evaluation
  - text-embedding-3-small for embeddings
- **Cohere API**: Rerank-v3.5 for contextual compression
- **Qdrant**: Vector database for RAG retrieval
- **PyMuPDF**: PDF document processing
- **metals.dev API**: External API for agent tool demonstration
- **Python 3.13** with **uv** for dependency management

## Project Structure

```
evaluating-rag-with-ragas/
├── Evaluating_RAG_with_Ragas.ipynb        # RAG system evaluation
├── Evaluating_Agents_with_Ragas.ipynb     # Agent system evaluation
├── data/                                   # Source documents
│   ├── AIE7_Projects_with_Domains.csv
│   └── howpeopleuseai.pdf
└── pyproject.toml                          # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.13
- API Keys:
  - OpenAI API key
  - Cohere API key (for reranking evaluation)
  - metals.dev API key (for agent evaluation)

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-key"
   export COHERE_API_KEY="your-key"  # For reranking
   export METAL_API_KEY="your-key"    # For agent evaluation
   ```

3. Execute notebooks:
   - **Evaluating_RAG_with_Ragas.ipynb**: RAG system evaluation workflow
   - **Evaluating_Agents_with_Ragas.ipynb**: Agent system evaluation workflow

## Implementation Highlights

### RAG Evaluation

The RAG evaluation notebook demonstrates:
- Synthetic data generation with RAGAS
- Baseline RAG system construction with LangGraph
- Multi-metric evaluation (6 metrics)
- Iterative improvement with chunking and reranking
- Comparative analysis showing component impact

### Agent Evaluation

The agent evaluation notebook demonstrates:
- ReAct agent construction with tool calling
- Message format conversion from LangGraph to RAGAS
- Agent-specific metrics (tool accuracy, goal accuracy, topic adherence)
- Evaluation of agent behavior patterns

### Key Findings

The evaluation revealed:
- Chunk size increase (50→500) provided 200-800% improvements across metrics
- Reranking added only 0-7% improvement over improved chunking alone
- Reranking increased cost 10-50x and latency 2-4x
- Simple solutions can outperform complex ones when properly evaluated

## Conclusion

This project demonstrates how systematic evaluation with RAGAS enables data-driven RAG and agent development. The comprehensive metric suite reveals performance across multiple dimensions, while comparative analysis identifies which components drive improvements. The findings highlight the importance of measuring each change independently and making cost-benefit trade-offs based on quantitative evidence rather than assumptions.

The patterns demonstrated—synthetic data generation, multi-metric evaluation, component isolation testing, and cost-benefit analysis—form essential practices for building reliable, efficient RAG and agent systems that deliver value while managing operational costs.
