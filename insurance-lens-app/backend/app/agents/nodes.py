"""Node functions for the LangGraph multi-agent orchestrator."""

import logging
from typing import Dict, Any

from app.agents.state import AgentState
from app.services.answer_generator import AnswerContext
from app.models.schemas import QuestionType
from app.core.config import settings
from app.core.exceptions import NoRelevantChunksError

# Import factory functions instead of creating instances
from app.core.dependencies import (
    get_question_classifier,
    get_web_search_agent,
    get_vector_store,
    get_answer_generator
)


logger = logging.getLogger(__name__)

async def classify_node(state: AgentState) -> Dict[str, Any]:
    """
    Classify the question to determine routing.
    Also validates that the question is insurance-related.

    Args:
        state: Current agent state

    Returns:
        Updated state with question_type set

    Raises:
        ValueError: If question is not insurance-related
    """
    question = state["question"]
    logger.info(f"Classifying question: {question}")

    classifier = get_question_classifier()

    # Guardrail: Check if question is insurance-related
    is_valid, reason = classifier.is_insurance_related(question)

    if not is_valid:
        logger.warning(f"Question rejected by guardrail: {question} - Reason: {reason}")
        raise ValueError(f"Diese Frage ist nicht versicherungsbezogen: {reason}")

    # Classify question type
    question_type = classifier.classify(
        question=question,
        policy_id=state.get("policy_id")
    )

    logger.info(f"Classification result: {question_type}")

    return {"question_type": question_type}


async def policy_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Answer policy-specific questions using RAG.

    Args:
        state: Current agent state

    Returns:
        Updated state with answer_result set
    """
    logger.info(f"Policy agent handling: {state['question']}")

    policy_id = state["policy_id"]
    question = state["question"]
    retrieval_strategy = state.get("retrieval_strategy", "semantic")

    vector_store = get_vector_store()
    answer_generator = get_answer_generator()

    logger.debug(f"Using retrieval strategy: {retrieval_strategy}")

    # Search vector store for relevant chunks using configured strategy
    if retrieval_strategy == "hybrid":
        logger.info("Using hybrid BM25+semantic retrieval")
        search_results = vector_store.search_hybrid(
            policy_id=policy_id,
            query=question
        )
    elif retrieval_strategy == "rerank":
        logger.info("Using semantic search with Cohere reranking")
        search_results = vector_store.search_with_rerank(
            policy_id=policy_id,
            query=question
        )
    else:
        logger.info("Using semantic retrieval")
        search_results = vector_store.search_similar_chunks(
            policy_id=policy_id,
            query=question
        )

    context = AnswerContext(
        question=question,
        search_results=search_results,
        policy_id=policy_id
    )

    answer_result = await answer_generator.generate_answer(context)

    logger.info(f"Policy agent answer confidence: {answer_result.confidence}")

    return {"answer_result": answer_result}


async def web_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Answer general insurance questions using web search.

    Args:
        state: Current agent state

    Returns:
        Updated state with answer_result set
    """
    logger.info(f"Web agent handling: {state['question']}")

    web_agent = get_web_search_agent()
    answer_result = await web_agent.answer(state["question"])

    logger.info(f"Web agent answer status: {answer_result.status}")

    return {"answer_result": answer_result}


def route_question(state: AgentState) -> str:
    """
    Route to the appropriate agent based on question classification.

    Args:
        state: Current agent state with question_type set

    Returns:
        Name of the next node to execute
    """
    question_type = state.get("question_type")

    if question_type == QuestionType.POLICY_SPECIFIC:
        logger.info("Routing to policy_agent")
        return "policy_agent"
    else:
        logger.info("Routing to web_agent")
        return "web_agent"

