# RAG PDF Chat Application

A full-stack Retrieval-Augmented Generation application that enables interactive question-answering over PDF documents. The system processes uploaded PDFs, extracts text, generates semantic embeddings, and provides context-aware responses using vector similarity search and large language models.

## Overview

This application implements a production-ready RAG system with a modern web interface. Users can upload PDF documents, which are processed and indexed into a vector database. The system then uses semantic search to retrieve relevant document chunks and generates accurate answers based solely on the uploaded content.

## Architecture

### RAG Pipeline

The system follows a standard RAG workflow:

1. **Document Processing**: PDF text extraction using PyPDF2, followed by intelligent chunking with configurable size and overlap
2. **Embedding Generation**: Text chunks are converted to high-dimensional vectors using OpenAI's text-embedding-3-small model
3. **Vector Storage**: In-memory vector database with cosine similarity search for efficient semantic retrieval
4. **Query Processing**: User questions are embedded and matched against stored vectors to find relevant context
5. **Response Generation**: Retrieved context is injected into prompts, and GPT-4o-mini generates streaming responses

### System Components

**Backend (FastAPI)**
- RESTful API with streaming support for real-time responses
- PDF upload and processing endpoints
- Vector database management
- CORS middleware for frontend integration

**Frontend (Next.js)**
- React-based chat interface with streaming response display
- Drag-and-drop PDF upload with progress indicators
- Markdown rendering for formatted AI responses
- Responsive design with Tailwind CSS

**RAG Library (aimakerspace)**
- Custom vector database implementation with cosine similarity
- Text processing utilities for PDF loading and chunking
- OpenAI integration for embeddings and chat completions
- Modular design for easy extension

## Key Features

- **Semantic Search**: Vector-based similarity search finds relevant content even with different wording
- **Streaming Responses**: Real-time text generation for improved user experience
- **Document Management**: Upload, process, and clear documents through the interface
- **Context-Aware Answers**: Responses are grounded in uploaded document content
- **Error Handling**: Graceful handling when information isn't available in the document

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **OpenAI API**: GPT-4o-mini for chat completions, text-embedding-3-small for embeddings
- **PyPDF2**: PDF text extraction and processing
- **NumPy**: Efficient vector operations for semantic search
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **Next.js 15**: React framework with App Router and TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Accessible component library
- **React Dropzone**: File upload with drag-and-drop support
- **React Markdown**: Markdown rendering for AI responses

### Development Tools
- **uv**: Fast Python package manager
- **TypeScript**: Type-safe frontend development
- **Playwright**: End-to-end testing framework

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-pdf-chat-app
```

2. Start the development environment:
```bash
./start-dev.sh
```

This script:
- Installs Python dependencies using uv
- Installs frontend dependencies
- Starts the backend server (port 8000)
- Starts the frontend development server (port 3000)

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

**Backend:**
```bash
cd api
uv sync
uv run python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. **Configure API Key**: Enter your OpenAI API key in the application settings
2. **Upload PDF**: Drag and drop or select a PDF file to upload
3. **Wait for Processing**: The system extracts text, creates chunks, and generates embeddings
4. **Ask Questions**: Query the document using natural language
5. **Receive Answers**: Get context-aware responses based on the uploaded document content

## Project Structure

```
rag-pdf-chat-app/
├── aimakerspace/              # Custom RAG library
│   ├── text_utils.py         # PDF loading and text chunking
│   ├── vectordatabase.py     # Vector storage and semantic search
│   └── openai_utils/         # OpenAI API integrations
│       ├── embedding.py      # Text embedding generation
│       ├── chatmodel.py      # Chat completion handling
│       └── prompts.py         # Prompt engineering utilities
├── api/                      # FastAPI backend
│   ├── app.py                # Main FastAPI application
│   └── requirements.txt      # Backend dependencies
├── frontend/                 # Next.js frontend
│   ├── src/app/              # App Router pages and layouts
│   ├── src/components/       # React components
│   └── package.json          # Frontend dependencies
├── start-dev.sh              # Development environment startup
├── stop-dev.sh               # Stop development servers
└── pyproject.toml            # Python project configuration
```

## Development Commands

```bash
./start-dev.sh      # Start both frontend and backend
./stop-dev.sh       # Stop all development servers
./start-backend.sh  # Start only the backend server
./status-dev.sh     # Check server status
```

## Key Learnings

1. **Vector Similarity Search**: Cosine similarity enables semantic matching between queries and document chunks, allowing retrieval based on meaning rather than exact keyword matching.

2. **Streaming Architecture**: Server-sent events and async generators enable real-time response delivery, improving perceived performance and user experience.

3. **Chunking Strategy**: Optimal chunk size and overlap balance context preservation with retrieval precision. Too large chunks include irrelevant information; too small chunks lose context.

4. **Context Injection**: Retrieved chunks must be properly formatted and injected into prompts to ensure the LLM generates grounded responses.

5. **Error Handling**: Robust error handling for edge cases (empty documents, API failures, missing context) ensures reliable operation.

## Evaluation

### Strengths

- **Modular Architecture**: Separation of concerns between frontend, backend, and RAG library enables independent development and testing
- **Streaming Support**: Real-time response generation improves user experience
- **Semantic Search**: Vector-based retrieval finds relevant content even with different terminology
- **Production-Ready**: FastAPI and Next.js provide scalable foundations for deployment

### Limitations

- **In-Memory Storage**: Vector database is stored in memory, requiring re-indexing on server restart
- **Single Document**: Currently supports one document at a time; multi-document support would require document management
- **No Persistence**: Uploaded documents and embeddings are not persisted across sessions
- **Chunking Strategy**: Fixed chunk size may not be optimal for all document types

### Performance Characteristics

- **PDF Processing**: ~1-3 seconds for typical documents (depends on size)
- **Embedding Generation**: ~0.5-1 second per chunk (batch processing available)
- **Query Latency**: ~2-5 seconds including embedding, search, and generation
- **Streaming Latency**: First token appears within ~1-2 seconds

## Conclusion

This project demonstrates a complete RAG implementation from document processing to user interface. The modular architecture, streaming support, and semantic search capabilities provide a solid foundation for document Q&A applications. The system effectively grounds LLM responses in document content, ensuring accuracy and relevance while maintaining a responsive user experience.