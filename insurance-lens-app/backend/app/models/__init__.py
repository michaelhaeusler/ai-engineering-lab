"""Data models and schemas."""

# API schemas (external, exposed in API)
from .schemas import (
    QuestionType,
    PolicyUploadResponse,
    QuestionRequest,
    Citation,
    AnswerResponse,
    HighlightedClause,
    PolicyOverview,
    ErrorResponse,
)

# Internal models (for service layer)
from .internal import (
    TextChunk,
    SearchResult,
    ProcessedDocument,
)

__all__ = [
    # API schemas
    "QuestionType",
    "PolicyUploadResponse", 
    "QuestionRequest",
    "Citation",
    "AnswerResponse",
    "HighlightedClause",
    "PolicyOverview",
    "ErrorResponse",
    # Internal models
    "TextChunk",
    "SearchResult",
    "ProcessedDocument",
]
