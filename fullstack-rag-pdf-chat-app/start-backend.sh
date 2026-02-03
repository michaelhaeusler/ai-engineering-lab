#!/bin/bash

# Start only the backend server using uv
echo "🚀 Starting RAG PDF Chat Backend with uv..."

# Check if we're in the right directory
if [ ! -f "api/app.py" ]; then
    echo "❌ Error: api/app.py not found. Please run this script from the project root."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Clear any conflicting virtual environment variables
unset VIRTUAL_ENV

# Install dependencies if needed
echo "📦 Ensuring dependencies are installed..."
uv sync
uv pip install -e .

# Use uv to run the Python app
echo "🎵 Starting FastAPI server on http://localhost:8000..."
echo "💡 To start both frontend and backend, use: ./start-dev.sh"
echo ""
uv run --python-preference only-managed python api/app.py
