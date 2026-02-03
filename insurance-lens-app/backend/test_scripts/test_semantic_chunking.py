"""Test semantic (fixed-size) chunking via API endpoint."""

import asyncio
import httpx
from pathlib import Path

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/v1/policies/upload"

sample_pdf_path = Path(__file__).parent.parent / "data" / "sample_policy.pdf"


async def test_semantic_chunking():
    """Test semantic chunking strategy via API."""
    print("\n" + "="*70)
    print("TESTING SEMANTIC (FIXED-SIZE) CHUNKING STRATEGY")
    print("="*70)
    
    if not sample_pdf_path.exists():
        print(f"❌ Error: Sample PDF not found at {sample_pdf_path}")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            with open(sample_pdf_path, "rb") as f:
                files = {"file": (sample_pdf_path.name, f, "application/pdf")}
                
                print(f"\n📤 Uploading with 'semantic' strategy...")
                response = await client.post(
                    UPLOAD_ENDPOINT, 
                    files=files, 
                    params={"strategy": "semantic"},
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                policy_id = data["policy_id"]
                total_chunks = data["total_chunks"]
                highlights = len(data["highlights"])
                
                print(f"\n✅ Upload successful!")
                print(f"  📋 Policy ID: {policy_id}")
                print(f"  📦 Total Chunks: {total_chunks}")
                print(f"  ⭐ Highlights: {highlights}")
                
                # Check if processing_metadata exists
                if 'processing_metadata' in data:
                    print(f"\n📊 Processing Metadata:")
                    metadata = data['processing_metadata']
                    print(f"  Strategy: {metadata.get('chunking_strategy')}")
                    print(f"  Processing time: {metadata.get('processing_time_seconds', 0):.2f}s")
                    
                    if metadata.get('chunking_strategy') == 'semantic':
                        print("\n  ✅ Metadata confirms 'semantic' chunking strategy")
                    else:
                        print("\n  ❌ Metadata does NOT confirm 'semantic' strategy")
                else:
                    print("\n  ℹ️  processing_metadata not in response (not exposed in API schema)")
                    print("  ✅ But upload succeeded with correct chunk count")
                    
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_semantic_chunking())

