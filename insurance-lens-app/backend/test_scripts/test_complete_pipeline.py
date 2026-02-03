#!/usr/bin/env python3
"""Test the complete PDF processing and vector storage pipeline."""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore


def test_complete_pipeline():
    """Test the complete pipeline: PDF → chunks → storage → search."""
    print("🧪 Testing Complete InsuranceLens Pipeline...")
    print("=" * 60)
    
    # Initialize services with configuration
    print("1️⃣ Initializing services...")
    pdf_processor = PDFProcessor(settings.pdf_processing)
    vector_store = VectorStore(settings.vector_store)
    print(f"   ✅ PDFProcessor: {settings.pdf_processing.chunk_size} tokens, {settings.pdf_processing.overlap_size} overlap")
    print(f"   ✅ VectorStore: {settings.vector_store.embedding_model}, threshold: {settings.vector_store.similarity_threshold}")
    
    # Test PDF processing
    print("\n2️⃣ Processing PDF...")
    sample_pdf = "data/sample_policy.pdf"
    
    if not Path(sample_pdf).exists():
        print(f"❌ Sample PDF not found at {sample_pdf}")
        print("   Please place a sample_policy.pdf in the data/ folder")
        return
    
    try:
        # Process PDF
        result = pdf_processor.process_pdf(sample_pdf, "sample_policy.pdf")
        print(f"   ✅ PDF processed successfully!")
        print(f"   📄 Pages: {result['total_pages']}")
        print(f"   📦 Chunks: {result['total_chunks']}")
        print(f"   📁 Filename: {result['filename']}")
        
        # Show chunk statistics
        if result['chunks']:
            token_counts = [chunk['token_count'] for chunk in result['chunks']]
            print(f"   📊 Token stats: min={min(token_counts)}, max={max(token_counts)}, avg={sum(token_counts)/len(token_counts):.1f}")
            
            # Show first chunk preview
            first_chunk = result['chunks'][0]
            print(f"\n   📝 First chunk preview:")
            print(f"      ID: {first_chunk['chunk_id']}")
            print(f"      Page: {first_chunk['page']}")
            print(f"      Tokens: {first_chunk['token_count']}")
            print(f"      Text: {first_chunk['text'][:100]}...")
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return
    
    # Test vector storage
    print("\n3️⃣ Storing chunks in Qdrant...")
    policy_id = "test_policy_123"
    
    try:
        storage_result = vector_store.store_chunks(policy_id, result['chunks'])
        print(f"   ✅ Chunks stored successfully!")
        print(f"   🗄️ Collection: {storage_result['collection_name']}")
        print(f"   📦 Points stored: {storage_result['points_stored']}")
        print(f"   🆔 Policy ID: {storage_result['policy_id']}")
        
    except Exception as e:
        print(f"❌ Error storing chunks: {e}")
        print("   💡 Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
        return
    
    # Test similarity search
    print("\n4️⃣ Testing similarity search...")
    test_queries = [
        "Wartezeiten",
        "Selbstbeteiligung", 
        "Ausschlüsse",
        "Kündigung",
        "Psychotherapie"
    ]
    
    for query in test_queries:
        try:
            similar_chunks = vector_store.search_similar_chunks(policy_id, query, limit=3)
            print(f"   🔍 Query: '{query}'")
            print(f"      Found {len(similar_chunks)} similar chunks")
            
            if similar_chunks:
                best_match = similar_chunks[0]
                print(f"      🎯 Best match (score: {best_match['score']:.3f}):")
                print(f"         Page {best_match['page']}: {best_match['text'][:80]}...")
            else:
                print(f"      ⚠️ No similar chunks found (threshold: {settings.vector_store.similarity_threshold})")
                
        except Exception as e:
            print(f"      ❌ Error searching for '{query}': {e}")
    
    # Test cleanup
    print("\n5️⃣ Testing cleanup...")
    try:
        deleted = vector_store.delete_policy(policy_id)
        if deleted:
            print(f"   ✅ Policy {policy_id} deleted successfully")
        else:
            print(f"   ⚠️ Policy {policy_id} not found for deletion")
    except Exception as e:
        print(f"   ❌ Error deleting policy: {e}")
    
    print("\n🎉 Complete pipeline test finished!")
    print("=" * 60)


if __name__ == "__main__":
    test_complete_pipeline()
