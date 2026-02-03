"""Policy management API routes."""

import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.models.schemas import (
    PolicyUploadResponse,
    QuestionRequest,
    AnswerResponse,
    PolicyOverview,
    QuestionType
)
from app.services import PolicyService
from app.core.exceptions import (
    NoRelevantChunksError,
    AnswerGenerationFailedError,
    PolicyProcessingError
)
from app.core.config import settings
from app.core.dependencies import get_policy_service
from fastapi import Depends

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/policies", tags=["policies"])

@router.post("/upload", response_model=PolicyUploadResponse)
async def upload_policy(
    file: UploadFile = File(...),
    strategy: str = Query(
        "semantic",
        description="Chunking strategy to use: 'semantic' (fixed-size) or 'paragraph' (natural boundaries)",
        regex="^(semantic|paragraph)$"
    ),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Upload and process a PDF policy document.

    Args:
        file: PDF file to upload and process
        strategy: Chunking strategy ("semantic" or "paragraph")
        policy_service: PolicyService instance

    Returns:
        PolicyUploadResponse with policy_id and processing status
    """
    from pathlib import Path

    # Sanitize filename to prevent path traversal attacks
    safe_filename = Path(file.filename).name if file.filename else "unknown"

    try:
        logger.info(f"Processing policy upload: {safe_filename}, strategy={strategy}")
        result = await policy_service.process_policy_upload(file, strategy)
        logger.info(f"Successfully uploaded policy {result.policy_id}: {result.total_chunks} chunks created from {result.total_pages} pages")
        return result
    except ValueError as e:
        logger.warning(f"Invalid upload request for {safe_filename}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to process policy upload: {safe_filename}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "upload_failed",
                "message": str(e) if settings.debug else "Upload failed"
            }
        )


@router.post("/{policy_id}/ask", response_model=AnswerResponse)
async def ask_question(
    policy_id: str,
    request: QuestionRequest,
    retrieval_strategy: str = Query(
        "rerank",
        description="Retrieval strategy: 'semantic' (vector only), 'hybrid' (BM25+vector), or 'rerank' (Cohere reranking)",
        regex="^(semantic|hybrid|rerank)$"
    ),
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Ask a question about a specific policy.

    Args:
        policy_id: ID of the policy to query
        request: Question request with question text
        retrieval_strategy: Strategy for document retrieval
        policy_service: PolicyService instance
    Returns:
        AnswerResponse with answer and citations
    """
    try:
        logger.info(f"Processing question for policy {policy_id} with strategy {retrieval_strategy}")
        result = await policy_service.answer_question(policy_id, request, retrieval_strategy)

        # Extract question type and web sources from metadata
        question_type_str = result.metadata.get("question_type", "policy_specific")
        question_type = QuestionType.GENERAL_INSURANCE if question_type_str == "general" else QuestionType.POLICY_SPECIFIC
        web_sources = result.metadata.get("web_sources", [])

        logger.info(f"Successfully answered question for policy {policy_id}, type={question_type}, confidence={result.confidence:.2f}")

        # Convert AnswerResult to AnswerResponse for API
        return AnswerResponse(
            answer=result.answer,
            question_type=question_type,
            citations=result.citations,
            web_sources=web_sources,
            confidence=result.confidence
        )

    except ValueError as e:
        # Guardrail rejected the question
        logger.warning(f"Question rejected by guardrail for policy {policy_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except NoRelevantChunksError as e:
        # Log query length instead of full query for privacy
        logger.info(f"No relevant chunks found for policy {policy_id}, query length: {len(e.query)}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "no_relevant_chunks_found",
                "message": "No relevant information found in the policy document for this question."
            }
        )
    except AnswerGenerationFailedError as e:
        logger.error(f"Answer generation failed for policy {policy_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "answer_generation_failed",
                "message": str(e.original_error) if settings.debug else "Failed to generate answer."
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error processing question for policy {policy_id}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": str(e) if settings.debug else "An unexpected error occurred."
            }
        )


@router.get("/", response_model=List[PolicyOverview])
async def list_policies(
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    List all uploaded policies.

    Returns:
        List of policy overviews
    """
    try:
        logger.info("Listing all policies")
        policies = policy_service.list_policies()
        logger.info(f"Successfully retrieved {len(policies)} policies")
        return policies
    except Exception as e:
        logger.exception("Failed to list policies")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": str(e) if settings.debug else "Failed to list policies"
            }
        )


@router.get("/{policy_id}/overview", response_model=PolicyOverview)
async def get_policy_overview(
    policy_id: str,
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Get overview of a specific policy.

    Args:
        policy_id: ID of the policy
        policy_service: PolicyService instance
    Returns:
        PolicyOverview with policy details
    """
    try:
        logger.info(f"Retrieving overview for policy {policy_id}")
        overview = policy_service.get_policy_overview(policy_id)
        logger.info(f"Successfully retrieved overview for policy {policy_id}")
        return overview
    except ValueError as e:
        logger.warning(f"Policy overview not found for policy {policy_id}: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "policy_not_found",
                "message": "Policy not found"
            }
        )
    except Exception as e:
        logger.exception(f"Failed to get policy overview for policy {policy_id}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": str(e) if settings.debug else "Failed to get policy overview"
            }
        )


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: str,
    policy_service: PolicyService = Depends(get_policy_service)
):
    """
    Delete a policy and its data.

    Args:
        policy_id: ID of the policy to delete
        policy_service: PolicyService instance
    Returns:
        Success message
    """
    try:
        logger.info(f"Deleting policy: {policy_id}")
        result = policy_service.delete_policy(policy_id)
        logger.info(f"Successfully deleted policy: {policy_id}")
        return result
    except ValueError as e:
        logger.warning(f"Policy not found for deletion: {policy_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to delete policy {policy_id}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": str(e) if settings.debug else "Failed to delete policy"
            }
        )
