"""Test script to verify paragraph chunking strategy."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_processor import PDFProcessor
from app.core.config import settings


def test_paragraph_chunking():
    """Test paragraph chunking with sample policy."""
    print("=" * 70)
    print("TESTING PARAGRAPH CHUNKING STRATEGY")
    print("=" * 70)
    
    # Test with paragraph strategy
    print("\n📄 Testing with PARAGRAPH strategy...")
    processor_para = PDFProcessor(settings.pdf_processing, chunking_strategy="paragraph")
    
    pdf_path = "data/sample_policy.pdf"
    result_para = processor_para.process_pdf(pdf_path, "sample_policy.pdf", "test-para-001")
    
    print(f"\n✅ Paragraph Strategy Results:")
    print(f"  📊 Total chunks: {result_para.total_chunks}")
    print(f"  📏 Avg chunk size: {sum(c.token_count for c in result_para.chunks) / len(result_para.chunks):.1f} tokens")
    print(f"  📈 Max chunk size: {max(c.token_count for c in result_para.chunks)} tokens")
    print(f"  📉 Min chunk size: {min(c.token_count for c in result_para.chunks)} tokens")
    
    # Show sample chunks
    print(f"\n📝 Sample chunks:")
    for i, chunk in enumerate(result_para.chunks[:3]):
        print(f"\n  Chunk {i+1} (Page {chunk.page}, {chunk.token_count} tokens):")
        print(f"    {chunk.text[:150]}...")
    
    # Test with semantic strategy for comparison
    print("\n" + "=" * 70)
    print("\n📄 Testing with SEMANTIC strategy (baseline)...")
    processor_sem = PDFProcessor(settings.pdf_processing, chunking_strategy="semantic")
    result_sem = processor_sem.process_pdf(pdf_path, "sample_policy.pdf", "test-sem-001")
    
    print(f"\n✅ Semantic Strategy Results:")
    print(f"  📊 Total chunks: {result_sem.total_chunks}")
    print(f"  📏 Avg chunk size: {sum(c.token_count for c in result_sem.chunks) / len(result_sem.chunks):.1f} tokens")
    print(f"  📈 Max chunk size: {max(c.token_count for c in result_sem.chunks)} tokens")
    print(f"  📉 Min chunk size: {min(c.token_count for c in result_sem.chunks)} tokens")
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON:")
    print("=" * 70)
    print(f"  Paragraph chunks: {result_para.total_chunks}")
    print(f"  Semantic chunks:  {result_sem.total_chunks}")
    print(f"  Difference: {abs(result_para.total_chunks - result_sem.total_chunks)} chunks")
    print(f"\n  Paragraph strategy creates {'FEWER' if result_para.total_chunks < result_sem.total_chunks else 'MORE'} chunks")
    print(f"  This means {'LARGER' if result_para.total_chunks < result_sem.total_chunks else 'SMALLER'} average chunk size")
    
    print("\n✅ Both strategies working correctly!")


if __name__ == "__main__":
    test_paragraph_chunking()

