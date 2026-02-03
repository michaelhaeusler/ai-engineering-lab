"""Test clause analysis with a real policy upload."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.clause_analyzer import ClauseAnalyzer
from app.services.pdf_processor import PDFProcessor
from app.core.config import settings


async def test_clause_analysis():
    """Test clause analysis on a sample policy."""
    
    # Find a sample policy
    data_dir = Path(__file__).parent.parent / "data"
    policy_files = list(data_dir.glob("*.pdf"))
    
    if not policy_files:
        print("❌ No PDF files found in data/ directory")
        return
    
    policy_path = policy_files[0]
    print(f"📄 Testing with: {policy_path.name}")
    
    # Process PDF
    print("\n1️⃣ Processing PDF...")
    pdf_processor = PDFProcessor(settings.pdf_processing, "semantic")
    processed_doc = pdf_processor.process_pdf(str(policy_path), policy_path.name, "test-001")
    print(f"   ✓ Extracted {processed_doc.total_chunks} chunks from {processed_doc.total_pages} pages")
    
    # Analyze clauses
    print("\n2️⃣ Analyzing clauses against norms...")
    analyzer = ClauseAnalyzer()
    highlights = await analyzer.analyze_policy(
        chunks=processed_doc.chunks,
        policy_id="test-001",
        max_highlights=5
    )
    
    # Display results
    print(f"\n✅ Analysis complete!")
    print(f"\n{'='*80}")
    print(f"Found {len(highlights)} unusual clauses:\n")
    
    if not highlights:
        print("🟢 No unusual clauses found - policy follows standard norms")
    else:
        for i, highlight in enumerate(highlights, 1):
            severity_emoji = {
                "low": "🟡",
                "medium": "🟠",
                "high": "🔴"
            }.get(highlight.get("severity", "low"), "⚪")
            
            print(f"{severity_emoji} Clause {i} ({highlight.get('category', 'other')})")
            print(f"   Page: {highlight.get('page', 'N/A')}")
            print(f"   Severity: {highlight.get('severity', 'unknown').upper()}")
            print(f"   \n   Text: {highlight.get('clause_text', '')[:200]}...")
            print(f"   \n   Reason: {highlight.get('reason', '')}")
            print()
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(test_clause_analysis())

