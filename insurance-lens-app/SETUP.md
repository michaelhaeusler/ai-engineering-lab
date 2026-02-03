# InsuranceLens Setup Guide

## Quick Start Commands

### 1. Backend Setup (Modern uv + .venv)
```bash
cd backend

# Install Python dependencies (creates .venv automatically)
uv sync

# Start Qdrant database  
docker run -p 6333:6333 qdrant/qdrant

# Copy environment file
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY=your_key_here
# - TAVILY_API_KEY=your_key_here

# Start backend (runs in virtual environment automatically)
uv run uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install Node.js dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start frontend
npm run dev
```

### 3. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Required API Keys

1. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
2. **Tavily API Key**: Get from https://tavily.com/

## Development Workflow

1. Upload a German health insurance PDF
2. System analyzes and creates highlights
3. Ask questions in German about your policy
4. Get AI-powered answers with citations

## Next Steps for Implementation

The basic structure is set up. To complete the MVP, implement:

### Day 1 - Backend Core
- [ ] PDF text extraction service
- [ ] Qdrant vector storage setup
- [ ] Basic RAG pipeline

### Day 2 - AI Agent
- [ ] LangGraph agent for question routing
- [ ] Policy Q&A with citations
- [ ] Tavily web search integration
- [ ] Clause highlighting logic

### Day 3 - Frontend Polish
- [ ] Connect all API endpoints
- [ ] Add question history
- [ ] Polish UI/UX
- [ ] Error handling and loading states
