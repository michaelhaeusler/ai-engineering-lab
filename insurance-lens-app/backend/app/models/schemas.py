"""Pydantic models for API request/response schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions the system can handle."""
    POLICY_SPECIFIC = "policy_specific"
    GENERAL_INSURANCE = "general_insurance"


class PolicyUploadResponse(BaseModel):
    """Response schema for policy upload."""
    policy_id: str = Field(..., description="Unique identifier for the uploaded policy")
    filename: str = Field(..., description="Original filename of the uploaded policy")
    total_pages: int = Field(..., description="Number of pages in the document")
    total_chunks: int = Field(..., description="Number of text chunks created")
    highlights: List[Dict[str, Any]] = Field(..., description="Highlighted unusual clauses")


class QuestionRequest(BaseModel):
    """Request schema for asking questions."""
    question: str = Field(..., description="User's question")


class Citation(BaseModel):
    """Citation information for answers."""
    chunk_id: str = Field(..., description="ID of the source chunk")
    page_number: Optional[int] = Field(None, description="Page number in original document")
    text_snippet: str = Field(..., description="Relevant text snippet")
    relevance_score: float = Field(..., description="Relevance score for this citation")


class AnswerResponse(BaseModel):
    """Response schema for question answers."""
    answer: str = Field(..., description="The AI-generated answer")
    question_type: QuestionType = Field(..., description="Type of question answered")
    citations: List[Citation] = Field(default=[], description="Source citations for policy questions")
    web_sources: List[str] = Field(default=[], description="Web sources for general questions")
    confidence: float = Field(..., description="Confidence score for the answer")


class HighlightedClause(BaseModel):
    """A policy clause that differs from typical norms."""
    clause_id: str = Field(..., description="Unique identifier for the clause")
    title: str = Field(..., description="Title or topic of the clause")
    text: str = Field(..., description="The actual clause text")
    reason: str = Field(..., description="Why this clause is highlighted (differs from norm)")
    norm_comparison: str = Field(..., description="How it compares to typical industry norms")
    category: str = Field(..., description="Category (waiting_period, exclusion, etc.)")
    page_number: Optional[int] = Field(None, description="Page number in original document")


class PolicyOverview(BaseModel):
    """Overview information about an uploaded policy."""
    policy_id: str = Field(..., description="Unique identifier for the policy")
    filename: str = Field(..., description="Original filename")
    upload_date: str = Field(..., description="Upload timestamp")
    total_pages: int = Field(..., description="Number of pages in the document")
    total_chunks: int = Field(..., description="Number of text chunks created")
    highlighted_clauses: List[HighlightedClause] = Field(..., description="Unusual clauses found")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
