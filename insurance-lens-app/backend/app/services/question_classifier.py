"""Question classification service for routing to appropriate agents."""

import logging
from typing import Optional

from app.models.schemas import QuestionType
from app.core.llm_factory import create_llm
from app.core.constants import CLASSIFICATION_MAX_TOKENS

logger = logging.getLogger(__name__)


class QuestionClassifier:
    """
    Classifies questions using AI to route them to the appropriate agent.
    
    Uses pure LLM classification without keyword matching for intelligent,
    context-aware routing between policy-specific and general insurance questions.
    """
    
    def __init__(self):
        """Initialize the question classifier with an LLM."""
        self.llm = create_llm(
            temperature=0.0,  # Deterministic for classification
            max_tokens=CLASSIFICATION_MAX_TOKENS
        )
    
    def is_insurance_related(self, question: str) -> tuple[bool, str]:
        """
        Check if a question is related to health insurance.
        
        Args:
            question: The user's question
            
        Returns:
            Tuple of (is_valid, reason) where reason explains why if invalid
        """
        prompt = f"""You are a guardrail for a German health insurance AI assistant.

Determine if this question is related to health insurance, healthcare, or medical topics.

VALID topics:
- Health insurance coverage, policies, contracts
- Medical treatments, doctors, hospitals
- Insurance terms (deductible, waiting period, premium, etc.)
- Healthcare system, insurance types
- Claims, reimbursement

INVALID topics:
- Completely unrelated (sports, cooking, programming, etc.)
- Other insurance types (car, home, life insurance)
- General chitchat or greetings

Question: {question}

Respond in this EXACT format:
VALID: yes/no
REASON: brief explanation (one sentence, in German)

Response:"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Parse response
            lines = content.split('\n')
            valid_line = next((l for l in lines if l.startswith('VALID:')), '')
            reason_line = next((l for l in lines if l.startswith('REASON:')), '')
            
            is_valid = 'yes' in valid_line.lower() or 'ja' in valid_line.lower()
            reason = reason_line.replace('REASON:', '').strip() if reason_line else "Diese Frage ist nicht versicherungsbezogen."
            
            logger.info(f"Guardrail check for '{question}': valid={is_valid}, reason={reason}")
            return (is_valid, reason)
            
        except Exception as e:
            logger.error(f"Error in guardrail check: {str(e)}")
            # Fail open: allow question if guardrail fails
            return (True, "")
    
    def classify(self, question: str, policy_id: Optional[str]) -> QuestionType:
        """
        Classify a question as policy-specific or general using AI.
        
        Args:
            question: The user's question
            policy_id: Optional policy ID if a policy is uploaded
            
        Returns:
            QuestionType.POLICY_SPECIFIC or QuestionType.GENERAL_INSURANCE
        """
        # Fast path: No policy uploaded → must be general
        if not policy_id:
            logger.info(f"No policy uploaded → GENERAL_INSURANCE")
            return QuestionType.GENERAL_INSURANCE
        
        # Use LLM for intelligent classification
        return self._llm_classify(question, has_policy=True)
    
    def _llm_classify(self, question: str, has_policy: bool) -> QuestionType:
        """
        Use LLM to intelligently classify the question intent.
        
        Args:
            question: The user's question
            has_policy: Whether a policy is uploaded
            
        Returns:
            QuestionType.POLICY_SPECIFIC or QuestionType.GENERAL_INSURANCE
        """
        prompt = f"""You are an expert at understanding user intent for health insurance questions.

Classify this question into ONE category:

1. "policy_specific": User asks about THEIR specific uploaded policy document
   Examples: 
   - "What is MY deductible?"
   - "What does MY contract say?"
   - "What benefits do I have?"
   - "What waiting periods apply?" (asking about their specific policy)

2. "general_insurance": User asks for general insurance knowledge, definitions, or explanations
   Examples:
   - "What is a deductible?"
   - "How does private health insurance work?"
   - "What does waiting period mean?"
   - "Explain the difference between..."
   - "Was bedeutet PKV?" (asking for definition/explanation)
   - "What does [abbreviation/term] mean?"

Important: Look at the INTENT, not just keywords!
- "What waiting periods apply?" → policy_specific (asking about their specific policy)
- "What are waiting periods?" → general_insurance (asking for definition)
- "Was bedeutet [term]?" → general_insurance (asking for explanation)

Question: {question}
User has uploaded a policy: {has_policy}

Respond with ONLY the category name: "policy_specific" or "general_insurance"

Classification:"""

        try:
            response = self.llm.invoke(prompt)
            classification = response.content.strip().lower()
            
            if "policy" in classification or "policy_specific" in classification:
                logger.info(f"LLM classified '{question}' as POLICY_SPECIFIC")
                return QuestionType.POLICY_SPECIFIC
            else:
                logger.info(f"LLM classified '{question}' as GENERAL_INSURANCE")
                return QuestionType.GENERAL_INSURANCE
                
        except Exception as e:
            logger.error(f"Error in LLM classification: {str(e)}")
            # Safe default: if has policy, assume policy-specific
            return QuestionType.POLICY_SPECIFIC if has_policy else QuestionType.GENERAL_INSURANCE

