"""LangGraph State definition for the multi-agent orchestrator."""

from typing import TypedDict, Optional
from app.models.schemas import QuestionType
from app.core.results import AnswerResult


class AgentState(TypedDict):
    """
    State passed between nodes in the LangGraph workflow.
    
    Attributes:
        question: The user's question
        policy_id: Optional policy ID if a policy was uploaded
        question_type: Classification result (set by classify_node)
        answer_result: Final answer (set by policy_agent or web_agent)
        retrieval_strategy: Optional strategy for retrieval ("semantic" or "hybrid")
    """
    question: str
    policy_id: Optional[str]
    question_type: Optional[QuestionType]
    answer_result: Optional[AnswerResult]
    retrieval_strategy: Optional[str]

