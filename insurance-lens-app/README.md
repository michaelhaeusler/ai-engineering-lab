#InsuranceLens 🔍

**AI-powered German Health Insurance Assistant**

### The problem

Everyone has to handle with insurances (health, liability, household contents, etc.) which are often huge documents, mostly written in 
### **1. Write a succinct 1-sentence description of the problem**

German insurance policies are complex and difficult to understand, making it hard for people to know what coverage they actually have and how their policy differs from standard industry norms.

### **2. Why is this a problem?**

For people with German health insurance, understanding their policy documents is a real challenge. These contracts are written in complex legal language with technical insurance terms, making it hard to know what is actually covered. Most people don't have time to read through 40+ pages of dense text, and even if they do, they might miss important clauses about waiting periods, exclusions, or deductibles that could affect them when filing claims.

Additionally, people have no easy way to compare their policy against industry standards. They might be paying for a policy with unusual restrictions or longer waiting periods than normal without knowing it. When they have questions about their coverage, they either have to call their insurance company or search through documents manually. There is no tool that lets them quickly ask questions about their own policy or understand how it differs from what is typical in the market.

### **3. Solution**

**InsuranceLens** is an AI-powered assistant that helps users understand their German health insurance policies. Users upload their policy PDF, and the system automatically analyzes it to identify clauses that differ from typical industry standards. The application can answer specific questions about the uploaded policy with exact citations from the document, and it can also answer general insurance questions using web search when needed.

The core features include:
- Automatic clause analysis that highlights unusual clauses compared to German health insurance norms
- Policy-specific Q&A with citations showing exactly where in the document the information comes from
- General insurance Q&A using web search for questions not related to the specific policy
- Intelligent routing that determines whether to search the user's policy or the web based on the question

The system understands the difference between questions about a user's specific policy and general insurance questions, routing them appropriately to provide accurate and relevant answers. All policy data is processed privately and the user maintains full control over their documents.

### **4. Tools used**

**Backend:**
- FastAPI - Industry standard for building Python APIs with automatic documentation and excellent async support needed for handling LLM calls efficiently
- LangChain/LangGraph - Most popular framework for building production-ready agentic systems, with good abstractions for multi-agent workflows
- OpenAI GPT-4o-mini - Widely used language model that offers a good balance between cost and quality for RAG applications
- Qdrant - Open-source vector database that is easy to set up locally and provides good performance for semantic search
- Cohere Rerank - Popular Reranking model that significantly improves retrieval precision compared to pure vector search
- Tavily - Specialized web search API designed for AI applications with good filtering options for German sources

**Frontend:**
- Next.js - Most popular React framework in 2025 with built-in routing and easy deployment on Vercel
- TypeScript - Industry standard for large JavaScript applications to catch errors early and improve code quality
- Tailwind CSS - Very popular utility-first CSS framework that allows fast UI development with a professional look

**Evaluation:**
- RAGAS - Framework for RAG evaluation with established metrics like faithfulness and context precision that help measure system quality

### **5. Agents and Agentic Reasoning**

I use a multi-agent system built with LangGraph to handle different types of questions. The main agentic reasoning happens in three areas:

**Question Classification and Routing:**
The first agent analyzes each question to determine its intent - whether it's about the user's specific policy or general insurance knowledge. This is more complex than keyword matching because questions like "What are my waiting periods?" and "What are waiting periods?" look similar but need different handling. The agent also acts as a guardrail to reject unrelated questions.

**Policy-Specific Agent:**
When a question is about the user's policy, this agent retrieves relevant chunks from the vector database using semantic search with reranking, and generates an answer with citations showing exactly where in the document the information comes from.

**General Insurance Agent:**
For general questions, this agent uses web search to find current information from trusted German sources and synthesizes the findings into a coherent answer with web source links.

The system uses conditional routing based on the classification result. I specifically did not use ReAct or tools-in-a-loop approaches because they are not needed for this use case. Each question type has a clear, deterministic path - either search the policy or search the web. There is no need for the agent to iteratively decide which tools to use or reason through multiple steps. A simple router pattern is the right solution here, keeping the system fast, predictable, and cost-effective while still providing the agentic flexibility to handle different question types appropriately.


### **6. Used Data Sources and APIs**

**Policy Documents (User Upload):**
Users upload their German health insurance policy PDFs. These documents are the primary data source for policy-specific questions. The system extracts text, chunks it into semantic pieces, converts them to embeddings, and stores them in the vector database for retrieval. This allows users to get answers about their specific coverage with exact citations.

**German Health Insurance Norms Database:**
A curated JSON file containing around 30-40 reference snippets about typical German health insurance standards. This includes statutory requirements from the VVG (German Insurance Contract Act), industry model conditions (GDV Musterbedingungen), and consumer guidance from sources like Verbraucherzentrale. The system uses this to compare user policies against what is normal in the industry and identify unusual clauses.

**OpenAI API:**
Used for generating embeddings (text-embedding-3-small model) to convert text chunks into vector representations for semantic search. Also used for language model calls (GPT-4.1-nano) to classify questions, generate answers, and analyze policy clauses.

**Cohere API:**
Used for reranking search results. After the initial vector search retrieves potentially relevant chunks, Cohere's rerank model (v3.5) re-scores them based on actual relevance to the query, which significantly improves answer quality.

**Tavily API:**
Web search API used for general insurance questions. When users ask about general topics like "What does PKV mean?" instead of questions about their specific policy, Tavily searches trusted German health insurance websites to find current information.

### **7. Chunking Strategy**

I use semantic chunking with RecursiveCharacterTextSplitter as the default strategy. The system chunks policy documents into 512-token pieces with a 50-token overlap between chunks to preserve context across boundaries.

I tested two different chunking strategies during development because German insurance policies have a specific document structure with paragraphs that contain complete clauses:

**Semantic Chunking (fixed-size):**
Creates consistent 512-token chunks regardless of document structure. This is simpler and more predictable.

**Paragraph-Aware Chunking:**
Tries to respect paragraph boundaries to keep complete clauses together. The idea was that insurance policies are structured with one clause per paragraph, so keeping them intact might improve retrieval.

Based on RAGAS evaluation with 10 test questions, I chose semantic chunking as the default because:
- Context precision was significantly better (0.73 vs 0.47) - semantic chunking retrieved more relevant chunks
- Context recall was also better (0.47 vs 0.30) - it found more of the needed information
- The fixed size makes the system more predictable and easier to optimize

While paragraph chunking had slightly better answer relevancy, it struggled with precision and recall, meaning it often retrieved less relevant chunks or missed important information. For a RAG system, having good retrieval is more important than potentially keeping clauses perfectly intact.

*For more information and a graphical comparison see the "insurancelens_evaluation" notebook.*

With more time, it would definitely be possible to develop a better chunking strategy specifically for insurance documents. This could use manual regex split rules to identify section headers, numbered clauses (like §1, §2, etc.), and labeled sections to keep complete legal clauses intact. However, for an MVP with limited time, semantic chunking provides good enough results and is much simpler to implement and maintain.


### **8. Specific Data**

The clause analysis feature requires specific reference data to work properly.

**German Health Insurance Norms Database:**
To identify unusual clauses in user policies, the system needs a reference dataset of what is considered "normal" in the German health insurance market. I created a curated JSON file with around 30-40 reference snippets covering typical standards in different categories:

- **Statutory requirements:** Sections from the VVG (Versicherungsvertragsgesetz) - the German Insurance Contract Act - which defines legal minimums and maximums (like maximum waiting periods)
- **Industry model conditions:** GDV Musterbedingungen MB/KK 2009 - standard templates that most insurers follow
- **Consumer guidance:** Snippets from trusted sources like Verbraucherzentrale, BaFin, and Finanztest explaining what is typical

Each norm entry includes the text, source, category (waiting_period, exclusion, deductible, etc.), and a URL reference. The clause analyzer uses this data to compare the user's policy against these standards and identify clauses that are unusual, like longer waiting periods than allowed, uncommon exclusions, or higher deductibles than typical.

Without this reference data, the system could still answer questions about the user's policy, but it couldn't tell them whether their policy is normal or has unusual terms compared to the market standard.


### **9. Future Improvements / Enhancements**

There are a lot of things I plan to make several improvements to make InsuranceLens more production-ready:

**Production Infrastructure:**
- Add proper user authentication and authorization so multiple users can securely use the system
- Implement a real database (PostgreSQL) to store user accounts, uploaded policies, and question history instead of only using in-memory storage
- Set up proper logging and monitoring to track errors, performance, and usage patterns
- Deploy the application to a cloud platform (likely Vercel for frontend and a cloud provider for backend)
- Add rate limiting and API security to prevent abuse
- Implement proper error handling and user-friendly error messages throughout the application

**UX Improvements:**
The current interface is functional but could be much better. I would add:
- Better loading states that show what the system is actually doing (uploading, analyzing, searching)
- Show the user's question immediately in the history instead of waiting for the answer
- Improve the highlights display with better visualization of why clauses are unusual
- Add the ability to save favorite questions or bookmark important answers
- Make it possible to download a report summarizing the policy analysis
- Make the UI multilingual

**Data Quality:**
- Expand the norms database from 30-40 entries to a more comprehensive collection covering more edge cases and policy types
- Add more specific norms for different types of health insurance (private vs. public, supplementary insurance, etc.)
- Validate and update norms regularly to reflect current legal requirements
- Extend it to more insurance types

**Chunking Strategy:**
- Develop a custom chunking strategy specifically for German insurance documents using regex patterns to identify section headers, numbered clauses, and labeled sections
- Test whether keeping complete legal clauses intact actually improves retrieval quality in practice
- Potentially implement adaptive chunking that adjusts chunk size based on document structure

**Evaluation and Quality:**
- Expand the RAGAS test set beyond 10 questions to get more reliable evaluation metrics
- Set up continuous evaluation to monitor system performance over time
- Add quality checks to alert when answer quality drops below acceptable thresholds


### Loom Video URL:
https://www.loom.com/share/c59ccfd1c3144519bc592ec5748483d8

----

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for Qdrant vector database)
- OpenAI API key
- Tavily API key (for web search)
- Cohere API key (for reranking)
- `uv` package manager (recommended) - [Install here](https://github.com/astral-sh/uv)

### Backend Setup

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Install dependencies** (creates `.venv` automatically):
   ```bash
   # Recommended: Modern uv approach (fast & reliable)
   uv sync
   
   # Alternative: Traditional pip (slower)
   pip install --upgrade pip
   pip install -e .
   ```

3. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - OPENAI_API_KEY
   # - TAVILY_API_KEY
   # - COHERE_API_KEY
   ```

4. **Start Qdrant (Docker)**:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

5. **Run the backend** (auto-runs in virtual environment):
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # OR run the main module
   uv run python -m app.main
   ```

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Environment setup**:
   ```bash
   cp .env.local.example .env.local
   # Edit if you changed the backend URL
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

5. **Open in browser**:
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
├── backend/                    # Python FastAPI backend
│   ├── .venv/                 # Virtual environment (auto-created by uv)
│   ├── app/
│   │   ├── core/              # Configuration and settings
│   │   ├── models/            # Pydantic schemas
│   │   ├── api/               # API routes
│   │   ├── services/          # Business logic
│   │   └── agents/            # LangGraph agents
│   ├── tests/                 # Backend tests
│   ├── pyproject.toml         # Modern Python project config
│   └── uv.lock               # Exact dependency versions
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # React components
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # Utility functions
│   └── package.json          # Frontend dependencies
├── data/                     # Seed data and norms
│   └── norms_health_de_v1.json
└── README.md
```

## 🔧 Environment Variables

### Backend (.env)
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# Optional - Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_URL=http://localhost:6333

# Optional - App Configuration
LLM_MODEL=gpt-4.2-nano              # LLM for answer generation
LLM_TEMPERATURE=0.3                 # Lower = more deterministic
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Optional - LangSmith (for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=insurancelens
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```


## 🧪 Development

### Backend Development
```bash
cd backend

# Run tests (in virtual environment)
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=html

# Code formatting
uv run ruff format .

# Linting
uv run ruff check .

# Type checking
uv run mypy app/

# Add new dependencies
uv add package-name

# Add development dependencies  
uv add --dev package-name

# Test specific retrieval strategy
uv run python dev_scripts/test_rerank_retrieval.py
```

### Running RAGAS Evaluation
```bash
cd notebooks

uv run python -m ipykernel install --user --name=insurancelens --display-name="Python (InsuranceLens)"

# Open the evaluation notebook
jupyter notebook insurancelens_evaluation.ipynb

# The notebook will:
# 1. Upload a policy to the backend
# 2. Generate synthetic test questions
# 3. Run questions through all retrieval strategies
# 4. Evaluate with RAGAS metrics
# 5. Compare results and generate insights
```

### Frontend Development
```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build

# Lint
npm run lint
```

## 📚 API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔍 Key Endpoints

### Policy Management
- `POST /api/v1/policies/upload?strategy={semantic|paragraph}` - Upload policy PDF with chunking strategy
- `GET /api/v1/policies/{id}/overview` - Get policy overview and highlights

### Question Answering
- `POST /api/v1/policies/{id}/ask?retrieval_strategy={semantic|hybrid|rerank}` - Ask policy questions with configurable retrieval
  - **Query Parameters**:
    - `retrieval_strategy`: `rerank` (default), `hybrid`, or `semantic`
  - **Request Body**:
    ```json
    {
      "question": "Welche Wartezeiten gelten?"
    }
    ```
  - **Response**:
    ```json
    {
      "answer": "Laut Ihrem Vertrag...",
      "citations": [
        {
          "text_snippet": "...",
          "page": 5,
          "score": 0.89
        }
      ],
      "confidence": 0.87
    }
    ```

### Health & Info
- `GET /api/v1/health` - Health check


### Configuration Choices
- **LLM Model**: `gpt-4o` (better instruction-following than `gpt-4o-mini`)
- **Chunk Size**: 512 tokens (optimal for insurance documents)
- **Max Results**: 3 chunks (prevents "lost in the middle" problem)
- **Similarity Threshold**: 0.6 (filters out noise)
- **Temperature**: 0.3 (deterministic, fact-based answers)

## 🎓 Lessons Learned & Best Practices

### What Worked Well
1. **Semantic Chunking** with LangChain's `RecursiveCharacterTextSplitter` provided the best baseline
3. **RAGAS Evaluation** with synthetic questions caught quality issues early
4. **LangGraph** simplified complex agent orchestration with clear state management
5. **Three Retrieval Options** gave flexibility for different query types

### What Has Been Optimized
1. **Initial Prompt Too Strict** → Rewrote to balance helpfulness with faithfulness
2. **Query Expansion** → Removed (added noise, hurt precision)
3. **Chunk Count** → Settled on 3 (more isn't always better - "lost in the middle")
4. **Model Choice** → `gpt-4.1-nano` over `gpt-4o-mini` for better instruction-following


### Key Takeaways for Production RAG
1. **Measure faithfulness** - it's the hardest metric to get right
2. **Fewer, better chunks** beats more, noisier chunks
4. **Iterative evaluation** with RAGAS saves debugging time
5. **Test with real user questions** not just synthetic data

## 📄 License

This project is created for educational purposes as part of the AI Makerspace bootcamp.

## 🔗 Links

- [AI Makerspace](https://aimakerspace.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [RAGAS Documentation](https://docs.ragas.io/)
- [Cohere Rerank](https://docs.cohere.com/docs/reranking)

---

**Built with ❤️ for German health insurance clarity**

*"The best RAG system is the one that admits when it doesn't know." - InsuranceLens Team*
