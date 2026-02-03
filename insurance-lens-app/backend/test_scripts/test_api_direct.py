"""Test the API route logic directly to isolate the issue."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api.routes.policies import ask_question
from app.models.schemas import QuestionRequest


async def main():
    """Test the API route function directly."""
    
    policy_id = "b2426222-10b9-418d-bcd0-d1e90657463b"
    question = "Welche Wartezeiten gelten?"
    
    print(f"Testing API route directly...")
    print(f"Policy ID: {policy_id}")
    print(f"Question: {question}\n")
    
    try:
        request = QuestionRequest(question=question)
        response = await ask_question(policy_id, request)
        
        print("\n=== SUCCESS ===")
        print(f"Answer preview: {response.answer[:200]}...")
        print(f"Confidence: {response.confidence}")
        print(f"Citations: {len(response.citations)}")
            
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

