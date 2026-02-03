"""
Dependency injection container for services.

This module provides factory functions that create service instances.
Each function ensures services are created fresh or returns cached instances.
"""

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from app.services.question_classifier import QuestionClassifier
from app.services.web_search_agent import WebSearchAgent
from app.services.vector_store import VectorStore
from app.services.answer_generator import AnswerGenerator
from app.core.config import settings

# Import PolicyService only for type checking to avoid circular import
if TYPE_CHECKING:
    from app.services.policy_service import PolicyService

logger = logging.getLogger(__name__)


# Service instances cache
# We use @lru_cache to create singletons that are still testable
# because we can clear the cache in tests


@lru_cache(maxsize=1)
def get_question_classifier() -> QuestionClassifier:
    """
    Get the question classifier service instance.

    Uses caching to return the same instance across calls (singleton pattern),
    but can be cleared for testing or reinitialization.

    Returns:
        QuestionClassifier instance

    Example:
        >>> classifier = get_question_classifier()
        >>> result = classifier.classify("What is my deductible?", "policy-123")
    """
    logger.debug("Creating QuestionClassifier instance")
    return QuestionClassifier()


@lru_cache(maxsize=1)
def get_web_search_agent() -> WebSearchAgent:
    """
    Get the web search agent service instance.

    Returns:
        WebSearchAgent instance
    """
    logger.debug("Creating WebSearchAgent instance")
    return WebSearchAgent()


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """
    Get the vector store service instance.

    Returns:
        VectorStore instance configured from settings
    """
    logger.debug("Creating VectorStore instance")
    return VectorStore(config=settings.vector_store)


@lru_cache(maxsize=1)
def get_answer_generator() -> AnswerGenerator:
    """
    Get the answer generator service instance.

    Returns:
        AnswerGenerator instance
    """
    logger.debug("Creating AnswerGenerator instance")
    return AnswerGenerator()

@lru_cache(maxsize=1)
def get_policy_service() -> "PolicyService":
    """
    Get the policy service instance.

    Returns:
        PolicyService instance
    """
    # Import here to avoid circular import
    from app.services.policy_service import PolicyService

    logger.debug("Creating PolicyService instance")
    return PolicyService()


def clear_service_cache() -> None:
    """
    Clear all cached service instances.

    Use this in tests or when you need to reinitialize services.

    Example:
        >>> # In your test
        >>> clear_service_cache()
        >>> # Now get_question_classifier() will create a new instance
    """
    get_question_classifier.cache_clear()
    get_web_search_agent.cache_clear()
    get_vector_store.cache_clear()
    get_answer_generator.cache_clear()
    get_policy_service.cache_clear()
    logger.info("Service cache cleared")
