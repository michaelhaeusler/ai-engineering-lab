# InsuranceLens Backend

Modern Python FastAPI backend using uv for dependency management.

## Quick Start

```bash
# One-time setup: Install dependencies
cd backend/
uv sync

# Start the development server
make dev

# Visit http://localhost:8000/docs for API documentation
```

## Development Commands

```bash
# Code Quality
make mypy        # Type checking
make lint        # Linting
make format      # Auto-format code
make check       # Run all checks (mypy + lint)
make test        # Run tests
make all         # Format + check + test

# Development
make dev         # Start dev server
make clean       # Clean cache files
make help        # Show all available commands

# Manual commands (if you prefer)
uv run mypy app/
uv run ruff check app/
uv run ruff format app/
uv run pytest
```

## Automated Type Checking

This project uses **mypy** for type checking. Run checks via:
- ✅ **VS Code integration** (real-time feedback as you type)
- ✅ **Makefile commands** (run before committing)

📚 **See [MYPY_SETUP.md](../docs/MYPY_SETUP.md) for setup guide**

## Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

## For pip Users

If you don't have `uv` installed, you can still use pip:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install from pyproject.toml
pip install -e .

# Or install dependencies manually
pip install fastapi "uvicorn[standard]" openai langchain langchain-openai langgraph langsmith qdrant-client tiktoken pypdf pymupdf tavily-python python-multipart python-dotenv pydantic httpx tenacity pytest pytest-asyncio black isort mypy
```

## Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI application
├── core/
│   ├── __init__.py
│   └── config.py        # Settings and configuration
├── models/
│   ├── __init__.py
│   └── schemas.py       # Pydantic models
├── api/
│   ├── __init__.py
│   └── routes/          # API endpoints
│       ├── __init__.py
│       ├── health.py    # Health checks
│       ├── policies.py  # Policy management
│       └── questions.py # Q&A endpoints
├── services/            # Business logic (to be implemented)
└── agents/              # LangGraph agents (to be implemented)
```
