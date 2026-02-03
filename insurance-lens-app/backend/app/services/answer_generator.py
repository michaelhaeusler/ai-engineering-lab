"""Answer generation service using LangChain for intelligent responses."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core.config import settings
from app.core.llm_factory import create_llm
from app.core.exceptions import NoRelevantChunksError, AnswerGenerationFailedError
from app.core.results import AnswerResult, ResultStatus
from app.models.schemas import Citation, HighlightedClause
from app.models.internal import SearchResult

logger = logging.getLogger(__name__)


@dataclass
class AnswerContext:
    """Context for answer generation."""
    question: str
    search_results: List[SearchResult]  # Changed from chunks: List[Dict]
    policy_id: str
    use_expansion: bool = True


class AnswerGenerator:
    """Service for generating intelligent answers using LangChain."""
    
    def __init__(self):
        """Initialize the answer generator with LangChain components."""
        self.model = create_llm(max_tokens=2000)
        self.prompt_template = self._create_prompt_template()
        self.chain = self._create_chain()
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for answer generation."""
        return ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", self._get_human_prompt_template())
        ])
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for insurance policy Q&A."""
        # Build language instruction if output language is specified
        language_instruction = ""
        if settings.llm_output_language and settings.llm_output_language.lower() != "english":
            language_instruction = f"- Always respond in {settings.llm_output_language}\n"
        
        return f"""You are an expert in health insurance policies. 
Your task is to provide precise and helpful answers based STRICTLY on the provided document excerpts.

CRITICAL RULES (DO NOT VIOLATE):
{language_instruction}- Answer ONLY using information from the provided document excerpts
- NEVER add information from your general knowledge
- NEVER make assumptions or inferences beyond what's explicitly stated
- If the answer is not in the provided excerpts, say: "Diese Information ist in den bereitgestellten Dokumentenauszügen nicht enthalten."
- Quote or paraphrase DIRECTLY from the provided text

QUALITY REQUIREMENTS:
- Provide precise page references [Page X]
- Explain technical terms if they appear in the document
- Use **bold** for important terms
- Use bullet points for structured information
- Be concise but complete"""
    
    def _get_human_prompt_template(self) -> str:
        """Get the human prompt template."""
        return """QUESTION: {question}

DOCUMENT INFORMATION:
{context}

Answer based on the above information. Use precise citations and page references."""
    
    def _create_chain(self) -> Any:
        """Create the LangChain processing chain.
        
        Returns:
            LangChain runnable chain for answer generation
        """
        return (
            {"context": self._format_context, "question": lambda x: x["question"]}
            | self.prompt_template
            | self.model
            | StrOutputParser()
        )
    
    def _format_context(self, input_data: Dict[str, Any]) -> str:
        """Format the context from retrieved search results."""
        search_results = input_data.get("search_results", [])
        if not search_results:
            raise NoRelevantChunksError("No search results provided for context formatting")
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            # Now we have proper SearchResult objects with TextChunk
            page = result.chunk.page
            text = result.chunk.text
            score = result.score
            
            context_parts.append(
                f"[Source {i} - Page {page} - Relevance: {score:.2f}]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    async def generate_answer(self, context: AnswerContext) -> AnswerResult:
        """
        Generate an intelligent answer using LangChain.
        
        Args:
            context: Answer context with question and retrieved search results
            
        Returns:
            AnswerResult with generated answer and citations
            
        Raises:
            NoRelevantChunksError: If no relevant search results are provided
            AnswerGenerationFailedError: If answer generation fails
        """
        if not context.search_results:
            raise NoRelevantChunksError(context.question)
        
        try:
            # Prepare input for the chain
            chain_input = {
                "question": context.question,
                "search_results": context.search_results  # Changed from chunks
            }
            
            # Generate answer using LangChain
            answer = await self.chain.ainvoke(chain_input)
            
            # Create citations from search results (using helper method)
            # Check if the answer indicates "not found" - if so, don't show citations
            not_found_phrases = [
                "nicht enthalten",
                "keine information",
                "nicht gefunden",
                "kann ich nicht",
                "steht nicht"
            ]
            answer_lower = answer.lower()
            has_info = not any(phrase in answer_lower for phrase in not_found_phrases)
            
            # Only create citations if the answer actually contains information
            citations = self._create_citations(context.search_results) if has_info else []
            
            # Create highlighted clauses
            highlighted_clauses = self._create_highlighted_clauses(context.search_results)
            
            # Calculate confidence based on search result scores
            confidence = self._calculate_confidence(context.search_results)
            
            return AnswerResult.success(
                answer=answer,
                citations=citations,
                highlighted_clauses=highlighted_clauses,
                confidence=confidence,
                metadata={
                    "policy_id": context.policy_id,
                    "use_expansion": context.use_expansion,
                    "result_count": len(context.search_results)
                }
            )
            
        except NoRelevantChunksError:
            # Re-raise this specific exception
            raise
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise AnswerGenerationFailedError(
                message=str(e),
                original_error=e
            )
    
    def _create_citations(self, search_results: List[SearchResult]) -> List[Citation]:
        """Create citations from search results using the helper method."""
        citations = []
        for result in search_results:
            # Use the to_citation_dict() helper method from SearchResult
            citation_dict = result.to_citation_dict()
            citations.append(Citation(**citation_dict))
        return citations
    
    def _create_highlighted_clauses(self, search_results: List[SearchResult]) -> List[HighlightedClause]:
        """Create highlighted clauses from search results."""
        # Simplified implementation - in a real system, this would use NLP
        # to identify and highlight specific insurance clauses
        # For now, return empty list as this is a complex feature
        # TODO: Implement proper clause highlighting with NLP
        return []
    
    def _calculate_confidence(self, search_results: List[SearchResult]) -> float:
        """Calculate confidence score based on search result relevance."""
        if not search_results:
            return 0.0
        
        # Return the actual average similarity score from vector store
        # This represents the true relevance of retrieved results
        scores = [result.score for result in search_results]
        return sum(scores) / len(scores)
    
    async def generate_simple_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Generate a simple answer without full response structure.
        
        Args:
            question: User question
            chunks: Retrieved document chunks
            
        Returns:
            Simple answer string
            
        Raises:
            NoRelevantChunksError: If no relevant chunks are provided
            AnswerGenerationFailedError: If answer generation fails
        """
        if not chunks:
            raise NoRelevantChunksError(question)
        
        context = AnswerContext(
            question=question,
            chunks=chunks,
            policy_id="",
            use_expansion=True
        )
        
        result = await self.generate_answer(context)
        return result.answer
