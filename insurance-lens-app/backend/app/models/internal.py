"""Internal Pydantic models for service layer.

These models are used internally between services and are NOT exposed in the API.
They provide type safety and validation for data passed between components.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """A chunk of text from a document with metadata.
    
    This model represents a processed chunk of text that has been:
    1. Extracted from a PDF document
    2. Split based on token count
    3. Enriched with metadata (page number, position, etc.)
    
    Used internally by PDFProcessor, VectorStore, and AnswerGenerator.
    """
    
    id: str = Field(..., description="Unique identifier for this chunk")
    text: str = Field(..., description="The actual text content")
    page: int = Field(..., description="Page number in the original document")
    chunk_index: int = Field(..., description="Position of this chunk in the document (0-based)")
    token_count: int = Field(..., description="Number of tokens in this chunk")
    start_char: Optional[int] = Field(None, description="Starting character position in the document")
    end_char: Optional[int] = Field(None, description="Ending character position in the document")
    
    class Config:
        """Pydantic configuration."""
        frozen = False  # Allow modification after creation
        extra = "forbid"  # Reject unknown fields
        
    def to_dict(self) -> dict:
        """Convert to dictionary for storage in vector database.
        
        Returns:
            Dictionary representation suitable for Qdrant payload
        """
        return self.model_dump()


class SearchResult(BaseModel):
    """A search result from the vector store.
    
    Represents a chunk that was retrieved from vector search,
    along with its relevance score and original metadata.
    """
    
    chunk: TextChunk = Field(..., description="The retrieved text chunk")
    score: float = Field(..., description="Similarity/relevance score (0.0 to 1.0)")
    distance: Optional[float] = Field(None, description="Vector distance (lower = more similar)")
    
    class Config:
        """Pydantic configuration."""
        frozen = False
        extra = "forbid"
        
    def to_citation_dict(self) -> dict:
        """Convert to dictionary format for creating Citation objects.
        
        Returns:
            Dictionary with fields matching the Citation schema
        """
        return {
            "chunk_id": self.chunk.id,
            "page_number": self.chunk.page,
            "text_snippet": self.chunk.text[:200] + "..." if len(self.chunk.text) > 200 else self.chunk.text,
            "relevance_score": self.score
        }


class ProcessedDocument(BaseModel):
    """Result of processing a PDF document.
    
    Contains all chunks extracted from a document along with
    metadata about the processing operation.
    """
    
    policy_id: str = Field(..., description="Unique identifier for the policy")
    filename: str = Field(..., description="Original filename")
    total_pages: int = Field(..., description="Number of pages in the document")
    chunks: list[TextChunk] = Field(..., description="All text chunks extracted")
    total_chunks: int = Field(..., description="Total number of chunks created")
    processing_metadata: dict = Field(default_factory=dict, description="Additional processing information")
    
    class Config:
        """Pydantic configuration."""
        frozen = False
        extra = "allow"  # Allow additional metadata fields
        
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens across all chunks."""
        return sum(chunk.token_count for chunk in self.chunks)

