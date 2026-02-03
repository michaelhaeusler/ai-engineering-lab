"""
Application-wide constants.

This module defines named constants to replace magic numbers throughout
the codebase, improving readability and maintainability.
"""

# ============================================================================
# OpenAI Model Configuration
# ============================================================================

OPENAI_EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}
"""
Embedding dimensions for OpenAI models.

Usage:
    dimension = OPENAI_EMBEDDING_DIMENSIONS[settings.embedding_model]
"""


# ============================================================================
# LLM Generation Settings
# ============================================================================

DEFAULT_MAX_TOKENS = 2000
"""Default maximum tokens for LLM responses."""

CLASSIFICATION_MAX_TOKENS = 50
"""Maximum tokens for classification tasks (short outputs)."""

ANALYSIS_TEMPERATURE = 0.3
"""Temperature for analysis tasks requiring consistency."""


# ============================================================================
# Vector Store Settings
# ============================================================================

VECTOR_SCROLL_BATCH_SIZE = 100
"""Batch size when scrolling through vector store results."""


# ============================================================================
# Text Processing
# ============================================================================

LOG_PREVIEW_LENGTH = 500
"""Maximum length for log message previews."""
