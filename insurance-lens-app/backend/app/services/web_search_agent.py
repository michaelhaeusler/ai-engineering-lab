"""Web search agent for general insurance questions using Tavily API."""

import logging
from typing import List, Dict, Any
from tavily import TavilyClient

from app.core.config import settings
from app.core.llm_factory import create_llm
from app.core.results import AnswerResult, ResultStatus
from app.core.exceptions import AnswerGenerationFailedError

logger = logging.getLogger(__name__)


class WebSearchAgent:
    """Agent for answering general insurance questions using web search."""
    
    def __init__(self):
        """Initialize the web search agent with Tavily and LLM."""
        self.tavily = TavilyClient(api_key=settings.tavily_api_key)
        self.llm = create_llm(max_tokens=2000)
    
    async def answer(self, question: str) -> AnswerResult:
        """
        Answer a general insurance question using web search.
        
        Searches the web for relevant information and synthesizes an answer.
        
        Args:
            question: The user's question about insurance
            
        Returns:
            AnswerResult with answer and web sources
            
        Raises:
            AnswerGenerationFailedError: If search or answer generation fails
        """
        try:
            # Search the web
            logger.info(f"Searching web for: {question}")
            search_results = self._search_web(question)
            
            if not search_results:
                # No search results found - return fail status
                return AnswerResult.fail(
                    answer="",  # Frontend will handle the message
                    confidence=0.0,
                    metadata={
                        "question_type": "general",
                        "search_results_count": 0,
                        "error_code": "no_web_results_found"
                    }
                )
            
            # Generate answer from search results
            answer = await self._generate_answer_from_results(question, search_results)
            
            # Extract web sources
            web_sources = [result.get("url", "") for result in search_results if result.get("url")]
            
            return AnswerResult.success(
                answer=answer,
                citations=[],  # No policy citations for web search
                highlighted_clauses=[],
                confidence=0.8,  # Web search confidence
                metadata={
                    "question_type": "general",
                    "search_results_count": len(search_results),
                    "web_sources": web_sources
                }
            )
            
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            raise AnswerGenerationFailedError(
                message=f"Web search failed: {str(e)}",
                original_error=e
            )
    
    def _search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the web using Tavily API.
        
        Args:
            query: Search query
            
        Returns:
            List of search results with content and URLs
        """
        try:
            # Tavily search with German health insurance focus
            response = self.tavily.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_domains=[
                    "gesundheit.de",
                    "krankenkassen.de",
                    "bundesgesundheitsministerium.de",
                    "verbraucherzentrale.de",
                    "test.de"
                ],
                exclude_domains=[
                    "facebook.com",
                    "twitter.com",
                    "instagram.com"
                ]
            )
            
            # Extract results
            results = response.get("results", [])
            logger.info(f"Tavily found {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    async def _generate_answer_from_results(
        self, 
        question: str, 
        search_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate an answer from search results using LLM.
        
        Args:
            question: Original question
            search_results: List of search results from Tavily
            
        Returns:
            Generated answer
        """
        # Format search results into context
        context_parts = []
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")
            
            context_parts.append(
                f"[Source {i}: {title}]\n{content}\nURL: {url}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Generate answer using LLM
        # Build language instruction if output language is specified
        language_instruction = ""
        if settings.llm_output_language and settings.llm_output_language.lower() != "english":
            language_instruction = f"- Always respond in {settings.llm_output_language}\n"
        
        prompt = f"""You are an expert on health insurance.

Answer the following question based on the web search results.

IMPORTANT RULES:
{language_instruction}- Be precise and helpful
- Explain complex terms clearly
- Structure your answer well (use paragraphs, bullet points)
- Only mention sources if relevant

WEB SEARCH RESULTS:
{context}

QUESTION: {question}

ANSWER:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer from search results: {str(e)}")
            # Re-raise to be caught by the outer try-catch
            raise AnswerGenerationFailedError(
                message=f"Failed to generate answer from web results: {str(e)}",
                original_error=e
            )

