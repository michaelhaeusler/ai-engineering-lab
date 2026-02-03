"""
Factory function for creating LLM instances.

Centralizes LLM initialization to ensure consistency across all services
and provide a single point of configuration.
"""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from app.core.config import settings
from app.core.constants import DEFAULT_MAX_TOKENS


def create_llm(
    temperature: float | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> BaseChatModel:
    """
    Create a configured LLM instance.

    Args:
        temperature: Override the default temperature from settings.
                    If None, uses settings.llm_temperature
        max_tokens: Maximum tokens for the response (default: DEFAULT_MAX_TOKENS)
        
    Returns:
        Configured LLM instance
        
    Example:
        # Use default settings
        llm = create_llm()
        
        # Override temperature for classification (deterministic)
        classifier_llm = create_llm(temperature=0.0)
        
        # Override for creative tasks
        creative_llm = create_llm(temperature=0.7, max_tokens=3000)
    """
    return init_chat_model(
        model=settings.llm_model,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        api_key=settings.openai_api_key,
        max_tokens=max_tokens
    )

