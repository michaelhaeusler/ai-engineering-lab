"""Result classes for structured API responses."""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum

from app.models.schemas import Citation, HighlightedClause


class ResultStatus(Enum):
    """Status of a result."""
    SUCCESS = "success"
    ERROR = "error"
    NO_RESULTS = "no_results"


@dataclass
class AnswerResult:
    """Structured result for answer generation."""
    
    status: ResultStatus
    answer: Optional[str] = None
    citations: List[Citation] = field(default_factory=list)
    highlighted_clauses: List[HighlightedClause] = field(default_factory=list)
    confidence: float = 0.0
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(
        cls,
        answer: str,
        citations: List[Citation],
        highlighted_clauses: List[HighlightedClause],
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "AnswerResult":
        """Create a successful result."""
        return cls(
            status=ResultStatus.SUCCESS,
            answer=answer,
            citations=citations,
            highlighted_clauses=highlighted_clauses,
            confidence=confidence,
            metadata=metadata or {}
        )
    
    @classmethod
    def no_results(cls, error_code: str = "no_relevant_chunks") -> "AnswerResult":
        """Create a no results result."""
        return cls(
            status=ResultStatus.NO_RESULTS,
            error_code=error_code,
            error_message="No relevant information found"
        )
    
    @classmethod
    def error(
        cls,
        error_code: str,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "AnswerResult":
        """Create an error result."""
        return cls(
            status=ResultStatus.ERROR,
            error_code=error_code,
            error_message=error_message,
            metadata=metadata or {}
        )


@dataclass
class PolicyUploadResult:
    """Structured result for policy upload."""
    
    status: ResultStatus
    policy_id: Optional[str] = None
    filename: Optional[str] = None
    chunks_created: int = 0
    collection_name: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(
        cls,
        policy_id: str,
        filename: str,
        chunks_created: int,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "PolicyUploadResult":
        """Create a successful upload result."""
        return cls(
            status=ResultStatus.SUCCESS,
            policy_id=policy_id,
            filename=filename,
            chunks_created=chunks_created,
            collection_name=collection_name,
            metadata=metadata or {}
        )
    
    @classmethod
    def error(
        cls,
        error_code: str,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "PolicyUploadResult":
        """Create an error result."""
        return cls(
            status=ResultStatus.ERROR,
            error_code=error_code,
            error_message=error_message,
            metadata=metadata or {}
        )
