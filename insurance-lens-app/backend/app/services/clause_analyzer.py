"""
Clause Analyzer Service

Compares policy clauses against German health insurance norms
to identify unusual or non-standard clauses.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm_factory import init_chat_model
from app.core.config import settings
from app.models.internal import TextChunk

logger = logging.getLogger(__name__)


class ClauseAnalyzer:
    """Analyzes policy clauses against health insurance norms."""
    
    def __init__(self):
        """Initialize the clause analyzer."""
        self.llm = init_chat_model(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        self.norms = self._load_norms()
        logger.info("ClauseAnalyzer initialized")
    
    def _load_norms(self) -> List[Dict[str, Any]]:
        """Load German health insurance norms from JSON file."""
        norms_path = Path(__file__).parent.parent.parent / "data" / "norms" / "norms_health_de_v1.json"
        
        if not norms_path.exists():
            logger.error(f"Norms file not found at {norms_path}")
            return []
        
        try:
            with open(norms_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                norms = data.get('norms', [])
                logger.info(f"Loaded {len(norms)} norms from {norms_path}")
                return norms
        except Exception as e:
            logger.error(f"Error loading norms: {str(e)}")
            return []
    
    def _create_norms_context(self) -> str:
        """Create a concise summary of norms for the LLM prompt."""
        if not self.norms:
            return "No norms available."
        
        # Group norms by category for better context
        categories = {}
        for norm in self.norms:
            category = norm.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(norm)
        
        context_parts = ["DEUTSCHE KRANKENVERSICHERUNGSNORMEN:\n"]
        
        for category, norms in categories.items():
            context_parts.append(f"\n{category.upper()}:")
            for norm in norms[:3]:  # Limit to 3 per category to keep context short
                context_parts.append(f"- {norm.get('title', '')}: {norm.get('text', '')[:150]}...")
        
        return "\n".join(context_parts)
    
    async def analyze_policy(
        self,
        chunks: List[TextChunk],
        policy_id: str,
        max_highlights: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Analyze policy chunks to find unusual clauses compared to norms.
        
        Args:
            chunks: List of text chunks from the policy
            policy_id: Unique identifier for the policy
            max_highlights: Maximum number of highlights to return (default: 5)
            
        Returns:
            List of highlighted clauses with reasons
        """
        if not chunks:
            logger.warning(f"No chunks provided for policy {policy_id}")
            return []
        
        if not self.norms:
            logger.warning("No norms loaded, cannot analyze policy")
            return []
        
        logger.info(f"Analyzing policy {policy_id} with {len(chunks)} chunks")
        
        # Select most relevant chunks (prefer longer chunks with keywords)
        keywords = ['wartezeit', 'ausschluss', 'selbstbeteiligung', 'leistung', 'bedingung']
        scored_chunks = []
        
        for chunk in chunks:
            score = len(chunk.text)  # Base score on length
            # Boost score if contains keywords
            for keyword in keywords:
                if keyword in chunk.text.lower():
                    score += 500
            scored_chunks.append((score, chunk))
        
        # Take top 10 chunks for analysis
        top_chunks = sorted(scored_chunks, key=lambda x: x[0], reverse=True)[:10]
        selected_chunks = [chunk for _, chunk in top_chunks]
        
        # Combine chunks into policy context
        policy_text = "\n\n".join([
            f"Abschnitt {i+1} (Seite {chunk.page}):\n{chunk.text}"
            for i, chunk in enumerate(selected_chunks)
        ])
        
        # Create analysis prompt
        norms_context = self._create_norms_context()
        
        system_prompt = f"""Du bist ein Experte für deutsche Krankenversicherungen.

Deine Aufgabe: Vergleiche die folgende Police mit den üblichen Branchennormen und identifiziere 3-5 Klauseln, die UNGEWÖHNLICH oder ABWEICHEND sind.

{norms_context}

WICHTIG:
- Nur ECHTE Abweichungen markieren (z.B. längere Wartezeiten, ungewöhnliche Ausschlüsse, hohe Selbstbeteiligung)
- Wenn die Police normal ist, gib eine LEERE Liste zurück
- Sei kritisch aber fair
- Zitiere den genauen Text aus der Police

Antworte NUR mit einem JSON-Array in diesem Format (keine Markdown-Formatierung):
[
  {{
    "clause_text": "Der genaue Text aus der Police",
    "page": Seitenzahl,
    "reason": "Kurze Erklärung warum ungewöhnlich (1-2 Sätze)",
    "severity": "low|medium|high",
    "category": "waiting_period|exclusion|deductible|coverage_scope|claim_process|other"
  }}
]

Falls KEINE ungewöhnlichen Klauseln gefunden: []"""

        user_prompt = f"""Analysiere diese Police:

{policy_text}

Finde 3-5 ungewöhnliche Klauseln oder gib [] zurück falls die Police den Normen entspricht."""

        try:
            # Call LLM for analysis
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            # Parse JSON response
            highlights = json.loads(content)
            
            if not isinstance(highlights, list):
                logger.error(f"Expected list, got {type(highlights)}")
                return []
            
            # Limit to max_highlights
            highlights = highlights[:max_highlights]
            
            logger.info(f"Found {len(highlights)} unusual clauses for policy {policy_id}")
            return highlights
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"LLM response was: {content[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error analyzing policy: {str(e)}")
            return []

