"""Guardrails integration for production-safe LangGraph agents.

This module provides utilities for integrating Guardrails AI validation
into LangGraph agent workflows, including input and output validation.
"""

import logging
from typing import Dict, Any, Optional, List
from typing_extensions import TypedDict, Annotated

from guardrails.hub import (
    RestrictToTopic,
    DetectJailbreak,
    CompetitorCheck,
    LlmRagEvaluator,
    HallucinationPrompt,
    ProfanityFree,
    GuardrailsPII
)
from guardrails import Guard
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

# Set up logging
logger = logging.getLogger(__name__)


class GuardrailsState(TypedDict):
    """State schema for guardrails-enabled agent graphs.
    
    Attributes:
        messages: List of messages in the conversation history.
        validation_results: Optional validation results from guardrails.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    validation_results: Optional[Dict[str, Any]]


def create_guardrails_guard(
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None,
    enable_jailbreak_detection: bool = True,
    enable_pii_protection: bool = True,
    enable_profanity_check: bool = True,
    enable_competitor_check: bool = False,
    pii_entities: Optional[List[str]] = None
) -> Guard:
    """Create a Guardrails guard with common production safety checks.
    
    Args:
        valid_topics: List of valid topics to allow. None disables topic restriction.
        invalid_topics: List of invalid topics to block. None disables topic restriction.
        enable_jailbreak_detection: Whether to enable jailbreak detection. Default: True.
        enable_pii_protection: Whether to enable PII detection and redaction. Default: True.
        enable_profanity_check: Whether to enable profanity filtering. Default: True.
        enable_competitor_check: Whether to enable competitor mention detection. Default: False.
        pii_entities: List of PII entity types to detect. Default: Common PII types.
        
    Returns:
        Configured Guard instance.
        
    Raises:
        RuntimeError: If guard configuration fails.
    """
    guard = Guard()
    
    try:
        # Topic restriction
        if valid_topics or invalid_topics:
            guard = guard.use(
                RestrictToTopic(
                    valid_topics=valid_topics or [],
                    invalid_topics=invalid_topics or [],
                    disable_classifier=True,
                    disable_llm=False,
                    on_fail="exception"
                )
            )
            logger.debug("Topic restriction guard configured")
        
        # Jailbreak detection
        if enable_jailbreak_detection:
            guard = guard.use(DetectJailbreak())
            logger.debug("Jailbreak detection guard configured")
        
        # PII protection
        if enable_pii_protection:
            default_entities = ["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"]
            entities = pii_entities or default_entities
            guard = guard.use(
                GuardrailsPII(
                    entities=entities,
                    on_fail="fix"
                )
            )
            logger.debug(f"PII protection guard configured for entities: {entities}")
        
        # Profanity check
        if enable_profanity_check:
            guard = guard.use(
                ProfanityFree(
                    threshold=0.8,
                    validation_method="sentence",
                    on_fail="exception"
                )
            )
            logger.debug("Profanity check guard configured")
        
        # Competitor check (optional)
        if enable_competitor_check:
            guard = guard.use(CompetitorCheck())
            logger.debug("Competitor check guard configured")
        
        logger.info("Guardrails guard configured successfully")
        return guard
        
    except Exception as e:
        logger.error(f"Failed to configure guardrails: {e}", exc_info=True)
        raise RuntimeError(f"Failed to configure guardrails: {e}") from e


def create_factuality_guard(
    eval_model: str = "gpt-4.1-mini",
    on_prompt: bool = True
) -> Guard:
    """Create a factuality guard for RAG responses.
    
    Args:
        eval_model: Model to use for factuality evaluation. Default: "gpt-4.1-mini".
        on_prompt: Whether to validate at prompt stage or response stage. Default: True.
        
    Returns:
        Configured Guard instance for factuality checking.
        
    Raises:
        RuntimeError: If guard configuration fails.
    """
    try:
        guard = Guard().use(
            LlmRagEvaluator(
                eval_llm_prompt_generator=HallucinationPrompt(prompt_name="hallucination_judge_llm"),
                llm_evaluator_fail_response="hallucinated",
                llm_evaluator_pass_response="factual",
                llm_callable=eval_model,
                on_fail="exception",
                on="prompt" if on_prompt else "response"
            )
        )
        logger.info(f"Factuality guard configured with model: {eval_model}")
        return guard
    except Exception as e:
        logger.error(f"Failed to configure factuality guard: {e}", exc_info=True)
        raise RuntimeError(f"Failed to configure factuality guard: {e}") from e


def validate_input(
    guard: Guard,
    user_input: str,
    raise_on_failure: bool = True
) -> Dict[str, Any]:
    """Validate user input using a Guardrails guard.
    
    Args:
        guard: The Guard instance to use for validation.
        user_input: The user input to validate.
        raise_on_failure: Whether to raise an exception on validation failure.
            If False, returns validation result. Default: True.
        
    Returns:
        Dictionary with validation results including:
        - validation_passed: Boolean indicating if validation passed
        - validated_output: The validated (and potentially modified) output
        - error: Error message if validation failed
        
    Raises:
        RuntimeError: If validation fails and raise_on_failure is True.
    """
    try:
        result = guard.validate(user_input)
        
        validation_result = {
            "validation_passed": result.validation_passed,
            "validated_output": result.validated_output if hasattr(result, 'validated_output') else user_input,
            "error": None
        }
        
        if not result.validation_passed and raise_on_failure:
            error_msg = f"Input validation failed: {getattr(result, 'error', 'Unknown error')}"
            logger.warning(f"Input validation failed: {user_input[:100]}...")
            raise RuntimeError(error_msg)
        
        return validation_result
        
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Input validation error: {e}", exc_info=True)
        if raise_on_failure:
            raise RuntimeError(f"Input validation failed: {e}") from e
        return {
            "validation_passed": False,
            "validated_output": user_input,
            "error": str(e)
        }


def validate_output(
    guard: Guard,
    agent_response: str,
    context: Optional[str] = None,
    raise_on_failure: bool = True
) -> Dict[str, Any]:
    """Validate agent output using a Guardrails guard.
    
    Args:
        guard: The Guard instance to use for validation.
        agent_response: The agent's response to validate.
        context: Optional context for factuality checking.
        raise_on_failure: Whether to raise an exception on validation failure.
            If False, returns validation result. Default: True.
        
    Returns:
        Dictionary with validation results.
        
    Raises:
        RuntimeError: If validation fails and raise_on_failure is True.
    """
    try:
        # For factuality guards, include context if provided
        if context:
            result = guard.validate(agent_response, metadata={"context": context})
        else:
            result = guard.validate(agent_response)
        
        validation_result = {
            "validation_passed": result.validation_passed,
            "validated_output": result.validated_output if hasattr(result, 'validated_output') else agent_response,
            "error": None
        }
        
        if not result.validation_passed and raise_on_failure:
            error_msg = f"Output validation failed: {getattr(result, 'error', 'Unknown error')}"
            logger.warning(f"Output validation failed: {agent_response[:100]}...")
            raise RuntimeError(error_msg)
        
        return validation_result
        
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Output validation error: {e}", exc_info=True)
        if raise_on_failure:
            raise RuntimeError(f"Output validation failed: {e}") from e
        return {
            "validation_passed": False,
            "validated_output": agent_response,
            "error": str(e)
        }


def create_input_validation_node(
    content_guard: Guard,
    pii_guard: Optional[Guard] = None
):
    """Create a LangGraph node that validates user input before agent processing.

    This node performs two-stage validation:
    1. PII redaction (optional, never fails - just redacts)
    2. Content validation (topic, jailbreak, profanity, etc.)

    Args:
        content_guard: Guard for content validation (topic, jailbreak, profanity)
        pii_guard: Optional Guard for PII redaction. If provided, runs first with on_fail="fix"

    Returns:
        A function that can be used as a LangGraph node for input validation.
    """
    def input_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user input before processing.

        Args:
            state: Current agent state with messages.

        Returns:
            Updated state with validation results.
        """
        messages = state.get("messages", [])
        if not messages:
            logger.debug("No messages to validate")
            return {
                "input_validation_passed": True,
                "validation_error": None
            }

        last_message = messages[-1]

        # Only validate HumanMessages
        if not isinstance(last_message, HumanMessage):
            logger.debug("Last message is not a HumanMessage, skipping input validation")
            return {
                "input_validation_passed": True,
                "validation_error": None
            }

        try:
            content = last_message.content
            logger.info(f"Starting input validation for message: {content[:100]}...")

            # Stage 1: PII Redaction (optional, never fails)
            pii_redacted = False
            if pii_guard:
                logger.info("Stage 1: Applying PII redaction to user input")
                pii_result = validate_input(pii_guard, content, raise_on_failure=False)
                redacted_content = pii_result.get("validated_output", content)
                if redacted_content != content:
                    pii_redacted = True
                    logger.warning(f"PII detected and redacted from input")
                    content = redacted_content
                else:
                    logger.info("No PII detected in input")

            # Stage 2: Content validation
            logger.info("Stage 2: Validating user input content (topic, jailbreak, profanity)")
            content_result = validate_input(content_guard, content, raise_on_failure=False)

            if content_result["validation_passed"]:
                logger.info("✓ Input validation PASSED")
                # Update message if PII was redacted
                if pii_redacted:
                    new_messages = messages[:-1] + [HumanMessage(content=content)]
                    logger.info("Updating message history with redacted content")
                    return {
                        "input_validation_passed": True,
                        "validation_error": None,
                        "messages": new_messages
                    }

                return {
                    "input_validation_passed": True,
                    "validation_error": None
                }
            else:
                error_msg = content_result.get("error", "Input validation failed")
                logger.error(f"✗ Input validation FAILED: {error_msg}")
                return {
                    "input_validation_passed": False,
                    "validation_error": f"Your request could not be processed: {error_msg}"
                }

        except Exception as e:
            logger.error(f"✗ Input validation ERROR: {e}", exc_info=True)
            return {
                "input_validation_passed": False,
                "validation_error": f"Validation error: {str(e)}"
            }

    return input_validation_node


def create_output_validation_node(output_guard: Guard, enable_refinement: bool = False):
    """Create a LangGraph node that validates agent output before returning to user.

    Args:
        output_guard: Guard for output validation (PII, profanity, factuality, etc.)
        enable_refinement: If True, mark failed outputs for refinement instead of just erroring

    Returns:
        A function that can be used as a LangGraph node for output validation.
    """
    def output_validation_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent output before returning to user.

        Args:
            state: Current agent state with messages.

        Returns:
            Updated state with validation results.
        """
        messages = state.get("messages", [])
        if not messages:
            logger.debug("No messages to validate")
            return {
                "output_validation_passed": True,
                "validation_error": None
            }

        last_message = messages[-1]

        # Only validate AIMessages
        if not isinstance(last_message, AIMessage):
            logger.debug("Last message is not an AIMessage, skipping output validation")
            return {
                "output_validation_passed": True,
                "validation_error": None
            }

        try:
            logger.info(f"Starting output validation for message: {last_message.content[:100]}...")
            result = validate_output(output_guard, last_message.content, raise_on_failure=False)

            if result["validation_passed"]:
                logger.info("✓ Output validation PASSED")
                return {
                    "output_validation_passed": True,
                    "validation_error": None
                }
            else:
                error_msg = result.get("error", "Output validation failed")
                logger.error(f"✗ Output validation FAILED: {error_msg}")

                if enable_refinement:
                    # Mark for refinement rather than replacing with error
                    logger.info("Refinement enabled - marking output for refinement")
                    return {
                        "output_validation_passed": False,
                        "validation_error": error_msg,
                        "needs_output_refinement": True
                    }
                else:
                    # Replace the AI message with an error message
                    logger.info("Refinement disabled - replacing output with error message")
                    error_response = AIMessage(
                        content=f"I apologize, but I cannot provide that response due to content policy: {error_msg}"
                    )
                    return {
                        "output_validation_passed": False,
                        "validation_error": error_msg,
                        "messages": [error_response]
                    }

        except Exception as e:
            logger.error(f"✗ Output validation ERROR: {e}", exc_info=True)
            error_response = AIMessage(
                content=f"I apologize, but there was an error validating the response: {str(e)}"
            )
            return {
                "output_validation_passed": False,
                "validation_error": str(e),
                "messages": [error_response]
            }

    return output_validation_node


def create_default_input_guards(
    valid_topics: Optional[List[str]] = None,
    invalid_topics: Optional[List[str]] = None
) -> tuple[Guard, Guard]:
    """Create default input guards (PII + content validation).

    Args:
        valid_topics: List of valid topics to allow
        invalid_topics: List of invalid topics to block

    Returns:
        Tuple of (pii_guard, content_guard)
    """
    # PII guard for redaction
    pii_guard = Guard().use(
        GuardrailsPII(
            entities=["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"],
            on_fail="fix"  # Redact instead of failing
        )
    )

    # Content validation guard
    content_guard = create_guardrails_guard(
        valid_topics=valid_topics,
        invalid_topics=invalid_topics,
        enable_jailbreak_detection=True,
        enable_pii_protection=False,  # Handled by separate PII guard
        enable_profanity_check=True
    )

    return pii_guard, content_guard


def create_default_output_guard(
    enable_factuality: bool = False,
    factuality_model: str = "gpt-4o-mini"
) -> Guard:
    """Create default output guard (PII + profanity + optional factuality).

    Args:
        enable_factuality: Enable factuality checking for RAG responses
        factuality_model: Model to use for factuality evaluation

    Returns:
        Configured output Guard
    """
    if enable_factuality:
        logger.info(f"Creating output guard WITH factuality checking using {factuality_model}")
        return create_factuality_guard(eval_model=factuality_model, on_prompt=False)
    else:
        logger.info("Creating output guard WITHOUT factuality checking")
        return create_guardrails_guard(
            valid_topics=None,  # Don't restrict topics on output
            enable_jailbreak_detection=False,  # Only check input for jailbreaks
            enable_pii_protection=True,
            enable_profanity_check=True
        )

