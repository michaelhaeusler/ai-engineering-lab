# Agentic RAG with LangGraph

This project implements an agentic Retrieval-Augmented Generation system using LangGraph for orchestration. The system extends traditional RAG by introducing autonomous tool usage, cyclic workflows, and self-evaluation capabilities, creating an agent that can research topics, evaluate its responses, and iteratively improve answers.

## Overview

The project demonstrates a research agent that autonomously uses external tools (web search, academic papers) to gather information and synthesize responses. Through LangGraph's graph-based architecture, the agent implements cyclic behavior where it can iteratively refine answers based on helpfulness evaluation, representing an advancement from traditional linear RAG pipelines.

## Architecture and Techniques

### Cyclic Workflows

The implementation leverages LangGraph's support for cyclic graphs, enabling:
- **Iterative Refinement**: Agent loops back to improve responses based on self-evaluation
- **Tool Orchestration**: Seamless integration of multiple tools (Tavily search, Arxiv) into the workflow
- **Conditional Routing**: Dynamic determination of next steps based on agent output

### State Management

Message-based state pattern tracks the entire conversation history, preserving context across tool calls and agent responses. The `AgentState` TypedDict with `add_messages` reducer ensures state consistency across graph nodes.

### Tool Integration

The agent uses OpenAI's function calling API to dynamically select and invoke tools:
- **Tavily Search**: Real-time web search for current information
- **Arxiv Query**: Academic paper retrieval for research-backed responses

Tools are bound to the model, enabling autonomous tool selection and parameter formatting.

### Self-Evaluation

A key feature is the integration of helpfulness checking:
- Secondary LLM evaluates whether responses adequately address the original query
- Loop limits prevent infinite iterations (>10 messages)
- Agent automatically refines responses when deemed insufficient

### Evaluation Framework

Comprehensive evaluation using LangSmith and OpenEvals:
- Structured evaluation datasets with custom and LLM-as-judge evaluators
- Concurrent execution for efficient testing
- Systematic comparison of agent configurations

## Key Learnings

1. **Cyclic vs. Linear Architectures**: Cyclic graphs enable adaptive behavior and quality control through self-evaluation, providing more natural decision-making flows than sequential chains.

2. **Tool Orchestration**: Effective tool usage requires clear schemas and proper output formatting. The `ToolNode` prebuilt component efficiently handles parallel tool execution.

3. **State Management**: Message-based state aligns with LLM conversational context, naturally integrating tool calls and enabling streaming support.

4. **Evaluation Strategies**: Production agents require multiple metrics (correctness, completeness, domain-specific checks) and automated evaluation for scalable quality assessment.

5. **Loop Control**: Cyclic systems need both hard limits (message counts) and soft limits (helpfulness checks) to prevent infinite loops while maintaining intelligent termination.

## Evaluation

### Strengths

- Autonomous operation with independent tool selection
- Built-in quality assurance through helpfulness checking
- Extensible graph architecture for additional tools or evaluation steps
- Full LangSmith integration for observability and debugging
- Production-ready patterns applicable to real-world deployments

### Limitations

- Evaluation model selection significantly impacts scores; requires experimentation
- Limited error handling for tool failures
- Multiple LLM calls increase costs; caching strategies needed
- No explicit context window management for long conversations

### Performance

- Tool latency: 1-3 seconds per tool call
- Evaluation overhead: ~1-2 seconds per iteration
- Total latency: 5-15 seconds depending on tool usage and iterations
- Token usage: 500-2000 tokens per query (varies with complexity)

## Tech Stack

- **LangGraph**: Graph-based workflow orchestration
- **LangChain**: LLM application framework and tool integration
- **OpenAI API**: GPT-4.1-nano (agent) and GPT-4.1-mini (evaluation)
- **Tavily Search API**: Real-time web search
- **Arxiv API**: Academic paper retrieval
- **LangSmith**: Tracing, monitoring, and evaluation
- **OpenEvals**: LLM-as-judge evaluation framework
- **Python 3.13** with **uv** for dependency management

## Getting Started

### Prerequisites

- Python 3.13
- API Keys: OpenAI, Tavily, LangSmith

### Setup

1. Install dependencies: `uv sync`
2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-key"
   export TAVILY_API_KEY="your-key"
   export LANGCHAIN_TRACING_V2="true"
   export LANGCHAIN_API_KEY="your-key"
   export LANGCHAIN_PROJECT="Agent-with-LangGraph"
   ```
3. Execute the notebook sequentially to build and evaluate the agent

## Project Structure

```
agent-with-langgraph/
├── Introduction_to_LangGraph_for_Agents_Assignment_Version.ipynb
├── pyproject.toml
└── README.md
```

## Conclusion

This project demonstrates the transition from static RAG systems to dynamic, agentic applications capable of autonomous research, self-evaluation, and iterative improvement. The LangGraph framework provides abstractions for complex agent workflows while maintaining clarity and debuggability. The patterns demonstrated—cyclic workflows, tool orchestration, self-evaluation, and comprehensive evaluation—form the foundation for production-grade agentic systems.
