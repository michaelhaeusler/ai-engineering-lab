"""Custom exceptions for the InsuranceLens application."""

from typing import Optional


class InsuranceLensError(Exception):
    """Base exception for all InsuranceLens errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PolicyError(InsuranceLensError):
    """Base exception for policy-related errors."""
    pass


class PolicyNotFoundError(PolicyError):
    """Raised when a policy is not found."""
    
    def __init__(self, policy_id: str):
        super().__init__(
            message=f"Policy {policy_id} not found",
            error_code="policy_not_found"
        )
        self.policy_id = policy_id


class PolicyProcessingError(PolicyError):
    """Raised when policy processing fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Policy processing failed: {message}",
            error_code="policy_processing_failed"
        )
        self.original_error = original_error


class AnswerGenerationError(InsuranceLensError):
    """Base exception for answer generation errors."""
    pass


class NoRelevantChunksError(AnswerGenerationError):
    """Raised when no relevant chunks are found for a query."""
    
    def __init__(self, query: str):
        super().__init__(
            message=f"No relevant chunks found for query: {query}",
            error_code="no_relevant_chunks"
        )
        self.query = query


class AnswerGenerationFailedError(AnswerGenerationError):
    """Raised when answer generation fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Answer generation failed: {message}",
            error_code="answer_generation_failed"
        )
        self.original_error = original_error


class VectorStoreError(InsuranceLensError):
    """Base exception for vector store errors."""
    pass


class CollectionNotFoundError(VectorStoreError):
    """Raised when a vector collection is not found."""
    
    def __init__(self, collection_name: str):
        super().__init__(
            message=f"Collection {collection_name} not found",
            error_code="collection_not_found"
        )
        self.collection_name = collection_name


class PDFProcessingError(InsuranceLensError):
    """Raised when PDF processing fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"PDF processing failed: {message}",
            error_code="pdf_processing_failed"
        )
        self.original_error = original_error
