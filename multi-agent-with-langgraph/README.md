# Multi-Agent RAG with LangGraph

This project implements a hierarchical multi-agent system using LangGraph for complex research and document generation tasks. The system demonstrates how multiple specialized agents can collaborate under supervisor coordination to accomplish sophisticated workflows that would be challenging for a single agent.

## Overview

The implementation follows the hierarchical agent team pattern from the AutoGen research paper, creating a three-level architecture: specialized agent teams, team supervisors, and a meta-supervisor. The system can research topics using multiple information sources, then generate structured documents through a collaborative writing process involving planning, writing, and editing agents.

## Architecture

### Hierarchical Agent Structure

The system implements a three-tier hierarchy:

1. **Meta-Supervisor**: Coordinates between high-level teams (Research and Response)
2. **Team Supervisors**: Manage specialized agent teams within each domain
3. **Specialized Agents**: Execute specific tasks using dedicated tools

### Research Team

The Research Team consists of two specialized agents supervised by a Research Supervisor:

- **Search Agent**: Uses Tavily search to find current, up-to-date information from the web
- **RAG Agent**: Retrieves specific information from a pre-indexed knowledge base about AI usage patterns
- **Research Supervisor**: Routes queries to the appropriate research agent based on task requirements

This team handles information gathering and research tasks, with the supervisor determining whether web search or knowledge base retrieval is more appropriate.

### Document Writing Team

The Document Writing Team includes three specialized agents supervised by an Authoring Supervisor:

- **NoteTaker**: Creates outlines and takes notes, referencing previous cohort responses for context
- **DocWriter**: Writes and edits document content based on outlines and research
- **CopyEditor**: Reviews and improves grammar, spelling, and tone
- **Authoring Supervisor**: Coordinates the writing workflow, ensuring proper sequencing of planning, writing, and editing

The team maintains a working directory where documents are created, edited, and managed throughout the writing process.

### Graph Composition

LangGraph enables composition of subgraphs as nodes in parent graphs. The Research Team and Document Writing Team are each implemented as separate LangGraph instances, which are then composed as nodes in the meta-supervisor graph. This hierarchical composition allows for:

- **Modularity**: Each team can be developed and tested independently
- **Reusability**: Teams can be reused in different contexts
- **Scalability**: New teams can be added without modifying existing graphs

## Key Techniques

### State Management

Each graph level maintains its own state:
- **ResearchTeamState**: Tracks messages, team members, and next agent to act
- **DocWritingState**: Extends research state with current files tracking
- **Meta State**: Simplifies to messages and next team, with message extraction/joining for subgraph communication

### Tool Integration

Agents are equipped with specialized tools:
- **Research Tools**: Tavily search, RAG retrieval chains
- **Writing Tools**: File creation, reading, editing, outline generation, previous response reference
- **Tool Wrapping**: LCEL chains (like RAG pipelines) can be wrapped as tools for agent use

### Supervisor Pattern

Supervisors use LLM-based routing with function calling:
- Define available agents/teams as routing options
- Use structured prompts to guide routing decisions
- Return structured JSON indicating next agent to activate
- Handle termination conditions (FINISH)

### Helper Functions

The implementation includes reusable helper functions:
- **create_agent()**: Standardizes agent creation with system prompts and tool binding
- **create_team_supervisor()**: Generates supervisor routing logic with function calling
- **agent_node()**: Wraps agents as LangGraph nodes with proper state handling

## Key Learnings

1. **Hierarchical Composition**: LangGraph's ability to compose graphs as nodes enables building complex multi-agent systems from simpler components. This pattern scales well and maintains clear separation of concerns.

2. **Supervisor Routing**: LLM-based supervisors provide flexible routing that adapts to task requirements. The function calling API enables structured decision-making while maintaining the benefits of LLM reasoning.

3. **State Abstraction**: Different graph levels require different state representations. Message extraction and joining functions enable clean communication between parent and child graphs.

4. **Tool Design**: Well-designed tools with clear docstrings enable agents to autonomously select appropriate tools. Wrapping complex chains (like RAG) as tools allows agents to leverage sophisticated pipelines.

5. **Workflow Coordination**: Multi-agent workflows require careful coordination to ensure proper sequencing. Supervisors must understand task dependencies and agent capabilities to route effectively.

## Evaluation

### Strengths

- **Modular Architecture**: Clear separation between research and writing teams enables independent development and testing
- **Specialized Agents**: Each agent has focused responsibilities, improving task quality and reducing confusion
- **Flexible Routing**: Supervisor-based routing adapts to different task requirements without hard-coded workflows
- **Composable Design**: Subgraphs can be reused and composed in different contexts

### Limitations

- **Cost**: Multiple LLM calls (agents + supervisors) increase operational costs
- **Latency**: Sequential agent execution and supervisor routing add significant latency
- **Error Propagation**: Errors in one agent can cascade through the workflow
- **State Complexity**: Managing state across multiple graph levels requires careful design

### Performance Characteristics

- **Research Phase**: 5-15 seconds depending on number of research iterations
- **Writing Phase**: 10-30 seconds depending on document complexity and editing cycles
- **Total Workflow**: 20-60 seconds for complete research and document generation
- **Token Usage**: 2000-8000 tokens per complete workflow (varies with task complexity)

## Tech Stack

- **LangGraph**: Graph-based workflow orchestration for multi-agent systems
- **LangChain**: LLM application framework, agent creation, and tool integration
- **OpenAI API**: GPT-4o-mini for agent reasoning and supervisor routing
- **OpenAI Embeddings**: text-embedding-3-small for vector search
- **Qdrant**: Vector database for RAG retrieval
- **Tavily API**: Real-time web search capabilities
- **PyMuPDF**: PDF document processing
- **Python 3.13** with **uv** for dependency management

## Project Structure

```
multi-agent-with-langgraph/
├── Multi_Agent_RAG_LangGraph.ipynb    # Main implementation notebook
├── data/                               # Knowledge base documents
│   ├── AIE7_Projects_with_Domains.csv
│   └── howpeopleuseai.pdf
├── content/                            # Generated documents
│   └── data/                          # Working directories for writing team
├── img/                               # Graph visualizations
└── pyproject.toml                     # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.13
- API Keys:
  - OpenAI API key
  - Tavily API key (for web search)

### Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-key"
   export TAVILY_API_KEY="your-key"
   ```

3. Execute the notebook:
   - Follow the notebook sequentially to build each team
   - Test individual teams before composing the full system
   - Experiment with different research and writing tasks

## Implementation Highlights

### Research Team Graph

The Research Team demonstrates how multiple information sources can be coordinated:
- Supervisor routes between web search and knowledge base retrieval
- Agents work autonomously with specialized tools
- Results are synthesized through supervisor coordination

### Document Writing Team Graph

The Document Writing Team shows collaborative document creation:
- File-based workflow with persistent working directory
- Sequential coordination: outline → writing → editing
- Context awareness through file tracking and previous response reference

### Meta-Supervisor Graph

The meta-supervisor demonstrates hierarchical composition:
- Research and Writing teams are composed as nodes
- Message extraction/joining enables clean communication
- Supervisor coordinates high-level workflow between teams

## Conclusion

This project demonstrates how LangGraph enables building sophisticated multi-agent systems through hierarchical composition. The supervisor pattern provides flexible coordination while maintaining agent autonomy. The modular architecture allows for independent development and testing of agent teams, making complex multi-agent workflows more manageable and maintainable.

The patterns demonstrated—hierarchical composition, supervisor routing, state management across graph levels, and tool integration—form the foundation for production-grade multi-agent systems that can handle complex, multi-step tasks requiring diverse capabilities.
