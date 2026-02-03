"""Policy management service for business logic."""

import uuid
import os
from typing import List, Optional, Dict, Any
from fastapi import UploadFile

from app.models.schemas import (
    PolicyUploadResponse,
    QuestionRequest,
    AnswerResponse,
    PolicyOverview,
    Citation
)
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore
from app.services.answer_generator import AnswerGenerator
from app.services.clause_analyzer import ClauseAnalyzer
from app.core.config import settings
from app.core.exceptions import (
    PolicyProcessingError,
    NoRelevantChunksError,
    AnswerGenerationFailedError,
    PDFProcessingError
)
from app.core.results import AnswerResult, PolicyUploadResult
from app.core.dependencies import (get_vector_store, get_answer_generator)


class PolicyService:
    """Service for managing policy operations."""

    def __init__(self):
        """Initialize the policy service with required components."""
        self.vector_store = get_vector_store()  # No arguments - uses settings internally
        self.answer_generator = get_answer_generator()
        self.clause_analyzer = ClauseAnalyzer()
        self.uploads_dir = settings.upload_folder_path

    async def process_policy_upload(
        self,
        file: UploadFile,
        chunking_strategy: str = "semantic"
    ) -> PolicyUploadResponse:
        """
        Process a PDF policy upload.

        Args:
            file: Uploaded PDF file
            chunking_strategy: Chunking strategy to use ("semantic" or "paragraph")

        Returns:
            PolicyUploadResponse with processing results

        Raises:
            ValueError: If file processing fails
        """
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are allowed")

        # Generate unique policy ID
        policy_id = str(uuid.uuid4())

        try:
            # Save uploaded file
            file_path = os.path.join(self.uploads_dir, f"{policy_id}.pdf")
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Create PDF processor with specified chunking strategy
            pdf_processor = PDFProcessor(settings.pdf_processing, chunking_strategy)

            # Process PDF (now returns ProcessedDocument)
            processed_doc = pdf_processor.process_pdf(file_path, file.filename, policy_id)

            # Create vector collection
            collection_name = self.vector_store.create_policy_collection(policy_id)

            # Store chunks in vector database (processed_doc.chunks is List[TextChunk])
            storage_result = self.vector_store.store_chunks(policy_id, processed_doc.chunks)

            # Analyze policy for unusual clauses
            highlights = await self.clause_analyzer.analyze_policy(
                chunks=processed_doc.chunks,
                policy_id=policy_id,
                max_highlights=5
            )

            return PolicyUploadResponse(
                policy_id=policy_id,
                filename=file.filename,
                total_pages=processed_doc.total_pages,
                total_chunks=processed_doc.total_chunks,
                highlights=highlights
            )

        except Exception as e:
            # Clean up on failure
            file_path = os.path.join(self.uploads_dir, f"{policy_id}.pdf")
            if os.path.exists(file_path):
                os.remove(file_path)

            raise ValueError(f"Failed to process PDF: {str(e)}")

    async def answer_question(
        self,
        policy_id: str,
        request: QuestionRequest,
        retrieval_strategy: str = "semantic"
    ) -> AnswerResult:
        """
        Answer a question using LangGraph multi-agent orchestration.

        The graph will:
        1. Classify the question (policy-specific vs general insurance)
        2. Route to appropriate agent (policy RAG or web search)
        3. Return the answer

        Args:
            policy_id: ID of the policy to query (optional for general questions)
            request: Question request
            retrieval_strategy: Strategy for retrieval ("semantic" or "hybrid")

        Returns:
            AnswerResult with answer and citations

        Raises:
            AnswerGenerationFailedError: If answer generation fails
        """
        # Lazy import to avoid circular dependency
        from app.agents import agent_graph, AgentState

        # Create initial state for the graph
        initial_state: AgentState = {
            "question": request.question,
            "policy_id": policy_id,  # Can be None for general questions
            "question_type": None,  # Will be set by classify_node
            "answer_result": None,  # Will be set by agent nodes
            "retrieval_strategy": retrieval_strategy  # Configure retrieval strategy
        }

        # Execute the graph
        final_state = await agent_graph.ainvoke(initial_state)

        # Extract the answer from the final state
        answer_result = final_state.get("answer_result")

        if not answer_result:
            # This shouldn't happen, but handle it gracefully
            raise AnswerGenerationFailedError(
                message="Graph execution completed but no answer was generated",
                original_error=None
            )

        return answer_result

    def list_policies(self) -> List[PolicyOverview]:
        """
        List all uploaded policies.

        Returns:
            List of policy overviews
        """
        # TODO: Implement policy listing from database
        # For now, return empty list
        return []

    def get_policy_overview(self, policy_id: str) -> PolicyOverview:
        """
        Get overview of a specific policy.

        Args:
            policy_id: ID of the policy

        Returns:
            PolicyOverview with policy details

        Raises:
            ValueError: If policy not found
        """
        # TODO: Implement policy overview retrieval
        raise ValueError("Not implemented yet")

    def delete_policy(self, policy_id: str) -> Dict[str, str]:
        """
        Delete a policy and its data.

        Args:
            policy_id: ID of the policy to delete

        Returns:
            Success message

        Raises:
            ValueError: If policy not found or deletion fails
        """
        try:
            # Delete from vector store
            success = self.vector_store.delete_policy(policy_id)

            # Delete PDF file
            file_path = os.path.join(self.uploads_dir, f"{policy_id}.pdf")
            if os.path.exists(file_path):
                os.remove(file_path)

            if success:
                return {"message": f"Policy {policy_id} deleted successfully"}
            else:
                raise ValueError("Policy not found")

        except Exception as e:
            raise ValueError(f"Failed to delete policy: {str(e)}")

    def get_policy_file_path(self, policy_id: str) -> Optional[str]:
        """
        Get the file path for a policy PDF.

        Args:
            policy_id: ID of the policy

        Returns:
            File path if exists, None otherwise
        """
        file_path = os.path.join(self.uploads_dir, f"{policy_id}.pdf")
        return file_path if os.path.exists(file_path) else None
