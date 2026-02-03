"""
Test script for Cohere Rerank retrieval strategy.

This script tests the new "rerank" retrieval strategy which combines:
1. Semantic search to get top 10 candidates
2. Cohere Rerank API to rerank by relevance
3. Returns top 3 results

Usage:
    uv run python dev_scripts/test_rerank_retrieval.py
"""

import asyncio
import httpx
from pathlib import Path


BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/v1/policies/upload"
ASK_ENDPOINT = f"{BASE_URL}/api/v1/policies"

# Path to sample PDF
sample_pdf_path = Path(__file__).parent.parent / "data" / "sample_policy.pdf"


async def test_rerank_retrieval():
    """Test the rerank retrieval strategy end-to-end."""
    print("=" * 70)
    print("TESTING COHERE RERANK RETRIEVAL STRATEGY")
    print("=" * 70)
    
    if not sample_pdf_path.exists():
        print(f"❌ Error: Sample PDF not found at {sample_pdf_path}")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Upload policy
            print("\n📤 Step 1: Uploading policy with semantic chunking...")
            with open(sample_pdf_path, "rb") as f:
                files = {"file": (sample_pdf_path.name, f, "application/pdf")}
                
                response = await client.post(
                    UPLOAD_ENDPOINT,
                    files=files,
                    params={"strategy": "semantic"},
                    timeout=60.0
                )
                response.raise_for_status()
                
                policy_data = response.json()
                policy_id = policy_data["policy_id"]
                total_chunks = policy_data["total_chunks"]
                
                print(f"✅ Upload successful!")
                print(f"   Policy ID: {policy_id}")
                print(f"   Total Chunks: {total_chunks}")
            
            # Step 2: Test question with RERANK strategy
            print(f"\n📤 Step 2: Asking question with RERANK retrieval...")
            test_question = "Welche Wartezeiten gelten für diese Versicherung?"
            print(f"   Question: {test_question}")
            
            response = await client.post(
                f"{ASK_ENDPOINT}/{policy_id}/ask",
                json={"question": test_question},
                params={"retrieval_strategy": "rerank"},
                timeout=60.0
            )
            response.raise_for_status()
            
            answer_data = response.json()
            
            print(f"\n✅ Rerank retrieval successful!")
            print(f"\n📊 Results:")
            print(f"   Answer length: {len(answer_data['answer'])} chars")
            print(f"   Citations: {len(answer_data['citations'])}")
            print(f"   Confidence: {answer_data.get('confidence', 'N/A')}")
            
            print(f"\n📝 Answer preview:")
            print(f"   {answer_data['answer'][:200]}...")
            
            if answer_data['citations']:
                print(f"\n📚 Citations:")
                for i, citation in enumerate(answer_data['citations'][:3], 1):
                    print(f"   {i}. Page {citation.get('page', 'N/A')}")
                    print(f"      Score: {citation.get('score', 'N/A')}")
                    print(f"      Text: {citation.get('text_snippet', '')[:80]}...")
            
            # Step 3: Compare with semantic retrieval
            print(f"\n📤 Step 3: Comparing with SEMANTIC retrieval (baseline)...")
            
            response = await client.post(
                f"{ASK_ENDPOINT}/{policy_id}/ask",
                json={"question": test_question},
                params={"retrieval_strategy": "semantic"},
                timeout=60.0
            )
            response.raise_for_status()
            
            semantic_data = response.json()
            
            print(f"\n✅ Semantic retrieval successful!")
            print(f"\n📊 Comparison:")
            print(f"   {'Strategy':<15} {'Answer Length':<15} {'Citations':<12}")
            print(f"   {'-'*42}")
            print(f"   {'Rerank':<15} {len(answer_data['answer']):<15} {len(answer_data['citations']):<12}")
            print(f"   {'Semantic':<15} {len(semantic_data['answer']):<15} {len(semantic_data['citations']):<12}")
            
            print(f"\n" + "=" * 70)
            print("✅ ALL TESTS PASSED - Rerank retrieval is working!")
            print("=" * 70)
            
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except httpx.RequestError as e:
        print(f"\n❌ Request error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_rerank_retrieval())

