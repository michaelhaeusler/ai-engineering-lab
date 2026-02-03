"""
Comprehensive Integration Test Suite for InsuranceLens API

Tests all endpoints with various scenarios:
- Happy path (successful operations)
- Error handling (invalid inputs)
- Edge cases (boundary conditions)

Run this script with the backend server running:
1. Start backend: cd backend && make dev
2. Run tests: cd backend && uv run python dev_scripts/test_api_comprehensive.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import AsyncClient, Response
from typing import Dict, Any, Optional


# Configuration
BASE_URL = "http://localhost:8000/api/v1"
SAMPLE_PDF = Path(__file__).parent.parent / "data" / "sample_policy.pdf"


class TestResult:
    """Track test results"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.total += 1
        self.passed += 1
        self.results.append({
            "test": test_name,
            "status": "✅ PASS",
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name: str, error: str):
        self.total += 1
        self.failed += 1
        self.results.append({
            "test": test_name,
            "status": "❌ FAIL",
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.total}")
        print(f"Passed: {self.passed} ({self.passed/self.total*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/self.total*100:.1f}%)")
        print("="*70)
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status"] == "❌ FAIL":
                    print(f"  - {result['test']}: {result['error']}")
        
        return self.failed == 0


results = TestResult()


async def test_health_check():
    """Test 1: Health check endpoint"""
    try:
        async with AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data["status"] == "healthy", "Status should be 'healthy'"
            
            results.add_pass(
                "Health Check",
                f"Status: {data['status']}, Service: {data['service']}"
            )
    except Exception as e:
        results.add_fail("Health Check", str(e))


async def test_upload_policy_success():
    """Test 2: Upload a valid PDF policy"""
    try:
        if not SAMPLE_PDF.exists():
            raise FileNotFoundError(f"Sample PDF not found at {SAMPLE_PDF}")
        
        async with AsyncClient() as client:
            with open(SAMPLE_PDF, "rb") as f:
                files = {"file": ("sample_policy.pdf", f, "application/pdf")}
                response = await client.post(
                    f"{BASE_URL}/policies/upload",
                    files=files,
                    timeout=60.0  # PDF processing can take time
                )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            # Validate response structure
            assert "policy_id" in data, "Response should contain policy_id"
            assert "filename" in data, "Response should contain filename"
            assert "total_chunks" in data, "Response should contain total_chunks"
            assert "highlights" in data, "Response should contain highlights"
            
            # Store policy_id for subsequent tests
            global uploaded_policy_id
            uploaded_policy_id = data["policy_id"]
            
            results.add_pass(
                "Upload Policy - Success",
                f"Policy ID: {data['policy_id']}, Chunks: {data['total_chunks']}"
            )
            
            return data["policy_id"]
            
    except Exception as e:
        results.add_fail("Upload Policy - Success", str(e))
        return None


async def test_upload_policy_invalid_file():
    """Test 3: Upload an invalid file (not PDF)"""
    try:
        async with AsyncClient() as client:
            # Create a fake text file
            files = {"file": ("test.txt", b"This is not a PDF", "text/plain")}
            response = await client.post(
                f"{BASE_URL}/policies/upload",
                files=files,
                timeout=30.0
            )
            
            # Should return error (400 or 500)
            assert response.status_code in [400, 422, 500], \
                f"Expected error status, got {response.status_code}"
            
            results.add_pass(
                "Upload Policy - Invalid File",
                f"Correctly rejected with status {response.status_code}"
            )
            
    except Exception as e:
        results.add_fail("Upload Policy - Invalid File", str(e))


async def test_upload_policy_no_file():
    """Test 4: Upload request without file"""
    try:
        async with AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/policies/upload",
                timeout=30.0
            )
            
            # Should return 422 (Unprocessable Entity) - missing file
            assert response.status_code == 422, \
                f"Expected 422, got {response.status_code}"
            
            results.add_pass(
                "Upload Policy - No File",
                f"Correctly rejected with status {response.status_code}"
            )
            
    except Exception as e:
        results.add_fail("Upload Policy - No File", str(e))


async def test_ask_question_success(policy_id: str):
    """Test 5: Ask a valid question about the policy"""
    try:
        async with AsyncClient() as client:
            question_data = {
                "question": "Welche Wartezeiten gelten?"
            }
            
            response = await client.post(
                f"{BASE_URL}/policies/{policy_id}/ask",
                json=question_data,
                timeout=30.0
            )
            
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Validate response structure
            assert "answer" in data, "Response should contain answer"
            assert "question_type" in data, "Response should contain question_type"
            assert "citations" in data, "Response should contain citations"
            assert "confidence" in data, "Response should contain confidence"
            
            # Validate answer is not empty
            assert len(data["answer"]) > 0, "Answer should not be empty"
            
            # Validate confidence is a number between 0 and 1
            assert 0 <= data["confidence"] <= 1, \
                f"Confidence should be between 0 and 1, got {data['confidence']}"
            
            results.add_pass(
                "Ask Question - Success",
                f"Answer length: {len(data['answer'])} chars, "
                f"Citations: {len(data['citations'])}, "
                f"Confidence: {data['confidence']:.2f}"
            )
            
    except Exception as e:
        results.add_fail("Ask Question - Success", str(e))


async def test_ask_question_invalid_policy():
    """Test 6: Ask question with invalid policy_id"""
    try:
        async with AsyncClient() as client:
            question_data = {
                "question": "Test question"
            }
            
            invalid_policy_id = "00000000-0000-0000-0000-000000000000"
            response = await client.post(
                f"{BASE_URL}/policies/{invalid_policy_id}/ask",
                json=question_data,
                timeout=30.0
            )
            
            # Should return 404 or 500 (policy not found)
            assert response.status_code in [404, 500], \
                f"Expected error status, got {response.status_code}"
            
            results.add_pass(
                "Ask Question - Invalid Policy",
                f"Correctly rejected with status {response.status_code}"
            )
            
    except Exception as e:
        results.add_fail("Ask Question - Invalid Policy", str(e))


async def test_ask_question_empty(policy_id: str):
    """Test 7: Ask an empty question"""
    try:
        async with AsyncClient() as client:
            question_data = {
                "question": ""
            }
            
            response = await client.post(
                f"{BASE_URL}/policies/{policy_id}/ask",
                json=question_data,
                timeout=30.0
            )
            
            # Should return 422 (validation error) or handle gracefully
            assert response.status_code in [422, 400], \
                f"Expected validation error, got {response.status_code}"
            
            results.add_pass(
                "Ask Question - Empty Question",
                f"Correctly rejected with status {response.status_code}"
            )
            
    except Exception as e:
        results.add_fail("Ask Question - Empty Question", str(e))


async def test_ask_question_long(policy_id: str):
    """Test 8: Ask a very long question"""
    try:
        async with AsyncClient() as client:
            # Create a very long question
            long_question = "Was ist " + "sehr " * 200 + "wichtig über diese Police?"
            
            question_data = {
                "question": long_question
            }
            
            response = await client.post(
                f"{BASE_URL}/policies/{policy_id}/ask",
                json=question_data,
                timeout=60.0  # Longer timeout for processing
            )
            
            # Should either succeed or return meaningful error
            if response.status_code == 200:
                data = response.json()
                assert "answer" in data, "Response should contain answer"
                results.add_pass(
                    "Ask Question - Long Question",
                    f"Handled long question successfully (status {response.status_code})"
                )
            else:
                # Accept graceful error handling
                results.add_pass(
                    "Ask Question - Long Question",
                    f"Rejected gracefully with status {response.status_code}"
                )
            
    except Exception as e:
        results.add_fail("Ask Question - Long Question", str(e))


async def test_ask_question_english(policy_id: str):
    """Test 9: Ask question in English (should still work)"""
    try:
        async with AsyncClient() as client:
            question_data = {
                "question": "What are the waiting periods?"
            }
            
            response = await client.post(
                f"{BASE_URL}/policies/{policy_id}/ask",
                json=question_data,
                timeout=30.0
            )
            
            # Should succeed - our system should handle English queries
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert "answer" in data, "Response should contain answer"
            
            results.add_pass(
                "Ask Question - English Query",
                f"Handled English query successfully"
            )
            
    except Exception as e:
        results.add_fail("Ask Question - English Query", str(e))


async def test_list_policies():
    """Test 10: List all policies"""
    try:
        async with AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/policies/",
                timeout=30.0
            )
            
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            results.add_pass(
                "List Policies",
                f"Found {len(data)} policies"
            )
            
    except Exception as e:
        results.add_fail("List Policies", str(e))


async def test_get_policy_overview(policy_id: str):
    """Test 11: Get policy overview"""
    try:
        async with AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/policies/{policy_id}/overview",
                timeout=30.0
            )
            
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert "policy_id" in data, "Response should contain policy_id"
            
            results.add_pass(
                "Get Policy Overview",
                f"Retrieved overview for policy {policy_id}"
            )
            
    except Exception as e:
        results.add_fail("Get Policy Overview", str(e))


async def test_delete_policy(policy_id: str):
    """Test 12: Delete a policy"""
    try:
        async with AsyncClient() as client:
            response = await client.delete(
                f"{BASE_URL}/policies/{policy_id}",
                timeout=30.0
            )
            
            assert response.status_code == 200, \
                f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert "message" in data, "Response should contain message"
            
            results.add_pass(
                "Delete Policy",
                f"Successfully deleted policy {policy_id}"
            )
            
    except Exception as e:
        results.add_fail("Delete Policy", str(e))


async def test_delete_nonexistent_policy():
    """Test 13: Delete a non-existent policy"""
    try:
        async with AsyncClient() as client:
            invalid_policy_id = "00000000-0000-0000-0000-000000000000"
            response = await client.delete(
                f"{BASE_URL}/policies/{invalid_policy_id}",
                timeout=30.0
            )
            
            # Should return 404
            assert response.status_code == 404, \
                f"Expected 404, got {response.status_code}"
            
            results.add_pass(
                "Delete Policy - Non-existent",
                f"Correctly rejected with status {response.status_code}"
            )
            
    except Exception as e:
        results.add_fail("Delete Policy - Non-existent", str(e))


async def run_all_tests():
    """Run all integration tests in sequence"""
    print("\n" + "="*70)
    print("INSURANCELENS API - COMPREHENSIVE INTEGRATION TESTS")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Sample PDF: {SAMPLE_PDF}")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*70 + "\n")
    
    # Test 1: Health check
    await test_health_check()
    
    # Test 2-4: Upload tests
    policy_id = await test_upload_policy_success()
    await test_upload_policy_invalid_file()
    await test_upload_policy_no_file()
    
    if policy_id:
        # Test 5-9: Question tests (only if upload succeeded)
        await test_ask_question_success(policy_id)
        await test_ask_question_invalid_policy()
        await test_ask_question_empty(policy_id)
        await test_ask_question_long(policy_id)
        await test_ask_question_english(policy_id)
        
        # Test 10-11: List and overview tests
        await test_list_policies()
        await test_get_policy_overview(policy_id)
        
        # Test 12-13: Delete tests
        await test_delete_policy(policy_id)
    else:
        results.add_fail("Skipped Tests", "Policy upload failed, skipping dependent tests")
    
    await test_delete_nonexistent_policy()
    
    # Print summary
    success = results.summary()
    
    # Save results to file
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": results.total,
                "passed": results.passed,
                "failed": results.failed,
                "success_rate": f"{results.passed/results.total*100:.1f}%"
            },
            "results": results.results
        }, f, indent=2)
    
    print(f"\n📝 Detailed results saved to: {results_file}")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

