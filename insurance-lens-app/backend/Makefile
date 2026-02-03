# Makefile for InsuranceLens Backend
# Usage: make <target>

.PHONY: help install check format test mypy lint all clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make check      - Run all checks (mypy, ruff)"
	@echo "  make mypy       - Run type checking with mypy"
	@echo "  make lint       - Run linting with ruff"
	@echo "  make format     - Format code with ruff"
	@echo "  make test       - Run tests with pytest"
	@echo "  make all        - Run format + check + test"
	@echo "  make clean      - Remove cache files"
	@echo "  make dev        - Start development server"

# Run type checking with mypy
mypy:
	@echo "🔍 Running mypy type checker..."
	uv run mypy app/

# Run linting with ruff
lint:
	@echo "🔍 Running ruff linter..."
	uv run ruff check app/

# Format code with ruff
format:
	@echo "✨ Formatting code with ruff..."
	uv run ruff format app/
	uv run ruff check --fix app/

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest

# Run all checks
check: mypy lint
	@echo "✅ All checks passed!"

# Run format + check
all: format check test
	@echo "🎉 All tasks completed!"

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned!"

# Start development server
dev:
	@echo "🚀 Starting development server..."
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

