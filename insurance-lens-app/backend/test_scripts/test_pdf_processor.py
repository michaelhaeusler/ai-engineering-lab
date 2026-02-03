#!/usr/bin/env python3
"""Simple test script for PDFProcessor."""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import PDFProcessingConfig
from app.services.pdf_processor import PDFProcessor


def test_pdf_processor():
    """Test the PDFProcessor with a sample PDF."""
    print("🧪 Testing PDFProcessor...")
    
    # Initialize with default config
    config = PDFProcessingConfig()
    processor = PDFProcessor(config)
    
    print(f"✅ PDFProcessor initialized")
    print(f"   - Chunk size: {config.chunk_size} tokens")
    print(f"   - Overlap: {config.overlap_size} tokens")
    print(f"   - Encoding: {config.encoding_type}")
    
    # Test with a sample PDF (if available)
    sample_pdf = "data/sample_policy.pdf"  # You can add a test PDF here
    
    if Path(sample_pdf).exists():
        print(f"\n📄 Testing with sample PDF: {sample_pdf}")
        try:
            result = processor.process_pdf(sample_pdf, "sample_policy.pdf")
            print(f"✅ PDF processed successfully!")
            print(f"   - Total pages: {result['total_pages']}")
            print(f"   - Total chunks: {result['total_chunks']}")
            print(f"   - Filename: {result['filename']}")
            
            # Show first chunk as example
            if result['chunks']:
                first_chunk = result['chunks'][0]
                print(f"\n📝 First chunk preview:")
                print(f"   - Chunk ID: {first_chunk['chunk_id']}")
                print(f"   - Page: {first_chunk['page']}")
                print(f"   - Tokens: {first_chunk['token_count']}")
                print(f"   - Text preview: {first_chunk['text'][:100]}...")
                
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
    else:
        print(f"\n⚠️  No sample PDF found at {sample_pdf}")
        print("   PDFProcessor is ready to use when you have a PDF to test!")
    
    print("\n🎯 PDFProcessor test completed!")


if __name__ == "__main__":
    test_pdf_processor()
