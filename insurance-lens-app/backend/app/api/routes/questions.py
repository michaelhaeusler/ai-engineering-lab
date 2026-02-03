"""Question answering API routes."""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models.schemas import QuestionRequest, AnswerResponse, ErrorResponse

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a policy or general insurance topic.
    
    The system will:
    1. Classify the question type (policy-specific vs general)
    2. Route to appropriate handler:
       - Policy questions: RAG with citations from uploaded document
       - General questions: Web search via Tavily + summarization
    3. Return answer with sources
    """
    try:
        # TODO: Implement question classification
        # TODO: Implement RAG for policy-specific questions
        # TODO: Implement web search for general questions
        # TODO: Implement LangGraph orchestration
        
        # Placeholder response
        raise HTTPException(
            status_code=501,
            detail="Question answering not yet implemented"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/history/{policy_id}")
async def get_question_history(policy_id: str):
    """Get question/answer history for a specific policy."""
    # TODO: Implement question history
    return []
