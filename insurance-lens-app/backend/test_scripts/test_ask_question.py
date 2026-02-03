"""Test the question-answering functionality."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services import PolicyService
from app.models.schemas import QuestionRequest


async def main():
    """Test asking a question about the uploaded policy."""
    
    policy_id = "b2426222-10b9-418d-bcd0-d1e90657463b"
    question = "Welche Wartezeiten gelten für diese Versicherung?"
    
    print(f"Testing question: {question}")
    print(f"Policy ID: {policy_id}\n")
    
    try:
        # Initialize service
        service = PolicyService()
        
        # Create request
        request = QuestionRequest(question=question)
        
        # Ask question
        print("Calling answer_question...")
        result = await service.answer_question(policy_id, request)
        
        print("\n=== SUCCESS ===")
        print(f"Answer: {result.answer}")
        print(f"\nConfidence: {result.confidence}")
        print(f"\nNumber of citations: {len(result.citations)}")
        
        for i, citation in enumerate(result.citations, 1):
            print(f"\nCitation {i}:")
            print(f"  Page: {citation.page_number}")
            print(f"  Score: {citation.relevance_score}")
            print(f"  Text: {citation.text_snippet[:100]}...")
            
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

