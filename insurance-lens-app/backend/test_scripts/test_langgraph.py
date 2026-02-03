"""Test script for LangGraph multi-agent orchestration."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.agents import agent_graph, AgentState
from app.models.schemas import QuestionType


async def test_general_question():
    """Test a general insurance question (should route to web agent)."""
    print("\n" + "="*80)
    print("TEST 1: General Insurance Question")
    print("="*80)
    
    initial_state: AgentState = {
        "question": "What is the difference between statutory and private health insurance in Germany?",
        "policy_id": None,
        "question_type": None,
        "answer_result": None
    }
    
    print(f"\n📝 Question: {initial_state['question']}")
    print(f"📋 Policy ID: {initial_state['policy_id']}")
    print("\n🔄 Executing LangGraph...")
    
    final_state = await agent_graph.ainvoke(initial_state)
    
    print(f"\n✅ Classification: {final_state['question_type'].value}")
    print(f"✅ Answer Status: {final_state['answer_result'].status}")
    print(f"✅ Confidence: {final_state['answer_result'].confidence:.2f}")
    print(f"\n💬 Answer:\n{final_state['answer_result'].answer[:300]}...")
    
    if final_state['answer_result'].citations:
        print(f"\n📚 Citations ({len(final_state['answer_result'].citations)}):")
        for i, citation in enumerate(final_state['answer_result'].citations[:3], 1):
            print(f"  {i}. {citation.text[:60]}...")
    
    return final_state


async def test_policy_question_without_policy():
    """Test a policy-specific question without a policy (should fail gracefully)."""
    print("\n" + "="*80)
    print("TEST 2: Policy Question WITHOUT Policy ID")
    print("="*80)
    
    initial_state: AgentState = {
        "question": "What is covered under my dental insurance?",
        "policy_id": None,  # No policy provided!
        "question_type": None,
        "answer_result": None
    }
    
    print(f"\n📝 Question: {initial_state['question']}")
    print(f"📋 Policy ID: {initial_state['policy_id']}")
    print("\n🔄 Executing LangGraph...")
    
    final_state = await agent_graph.ainvoke(initial_state)
    
    print(f"\n✅ Classification: {final_state['question_type'].value}")
    print(f"✅ Answer Status: {final_state['answer_result'].status}")
    print(f"✅ Confidence: {final_state['answer_result'].confidence:.2f}")
    
    if final_state['answer_result'].status == "failed":
        print(f"\n⚠️  Expected failure (no policy provided)")
        print(f"📋 Error code: {final_state['answer_result'].metadata.get('error_code', 'N/A')}")
    
    return final_state


async def main():
    """Run all tests."""
    print("\n🚀 LangGraph Multi-Agent Orchestrator Test Suite")
    print("=" * 80)
    
    try:
        # Test 1: General question
        await test_general_question()
        
        # Test 2: Policy question without policy
        await test_policy_question_without_policy()
        
        print("\n" + "="*80)
        print("✅ All tests completed!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

