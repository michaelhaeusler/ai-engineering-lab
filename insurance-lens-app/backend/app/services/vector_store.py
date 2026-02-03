"""Vector storage service for policy chunks and embeddings."""

import uuid
from typing import Dict, List, Optional

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
from rank_bm25 import BM25Okapi
from langchain_cohere import CohereRerank
from langchain_core.documents import Document

from app.core.config import VectorStoreConfig, settings
from app.core.constants import OPENAI_EMBEDDING_DIMENSIONS, VECTOR_SCROLL_BATCH_SIZE
from app.models.internal import TextChunk, SearchResult


class VectorStore:
    """Handles vector storage and retrieval for policy chunks."""
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize vector store with configuration."""
        self.config = config
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )
        # Initialize Cohere reranker for advanced retrieval
        self.reranker = CohereRerank(
            model="rerank-v3.5",
            cohere_api_key=settings.cohere_api_key
        )
    
    def create_policy_collection(self, policy_id: str) -> str:
        """
        Create a new Qdrant collection for a specific policy.
        
        Args:
            policy_id: Unique identifier for the policy
            
        Returns:
            Collection name
        """
        collection_name = f"{self.config.collection_prefix}{policy_id}"
        
        # Check if collection exists, delete if it does
        if self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.delete_collection(collection_name)
        
        # Create new collection
        # Get embedding dimension based on configured model
        dimension = OPENAI_EMBEDDING_DIMENSIONS[self.config.embedding_model]

        self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=Distance.COSINE
            )
        )
        
        return collection_name
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        response = self.openai_client.embeddings.create(
            model=self.config.embedding_model,
            input=text
        )
        return response.data[0].embedding
    
    def store_chunks(self, policy_id: str, chunks: List[TextChunk]) -> Dict:
        """
        Store policy chunks in Qdrant with embeddings.
        
        Args:
            policy_id: Unique identifier for the policy
            chunks: List of TextChunk Pydantic models from PDFProcessor
            
        Returns:
            Dictionary with storage results
        """
        collection_name = self.create_policy_collection(policy_id)
        points = []
        
        for chunk in chunks:
            # Generate embedding for chunk text (now chunk.text, not chunk["text"])
            embedding = self.embed_text(chunk.text)
            
            # Create point for Qdrant
            # Use chunk.to_dict() to get all fields as a dictionary for payload
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    **chunk.to_dict(),  # Include all chunk fields
                    "policy_id": policy_id  # Add policy_id
                }
            )
            points.append(point)
        
        # Store all points in Qdrant
        self.qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        return {
            "collection_name": collection_name,
            "points_stored": len(points),
            "policy_id": policy_id
        }
    
    def search_similar_chunks(self, policy_id: str, query: str, limit: Optional[int] = None) -> List[SearchResult]:
        """
        Search for similar chunks in a policy collection using semantic similarity.
        
        Args:
            policy_id: Policy to search in
            query: Search query text
            limit: Maximum number of results (uses config default if None)
            
        Returns:
            List of SearchResult Pydantic models with TextChunk and scores
        """
        collection_name = f"{self.config.collection_prefix}{policy_id}"
        
        if not self.qdrant_client.collection_exists(collection_name):
            return []
        
        # Generate embedding for query
        query_embedding = self.embed_text(query)
        
        # Search in Qdrant
        results = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit or self.config.max_results,
            score_threshold=self.config.similarity_threshold
        )
        
        # Convert Qdrant results to SearchResult Pydantic models
        search_results = []
        for result in results:
            # Reconstruct TextChunk from payload
            chunk = TextChunk(
                id=result.payload["id"],
                text=result.payload["text"],
                page=result.payload["page"],
                chunk_index=result.payload["chunk_index"],
                token_count=result.payload["token_count"],
                start_char=result.payload.get("start_char"),
                end_char=result.payload.get("end_char")
            )
            
            # Create SearchResult with chunk and score
            search_results.append(SearchResult(
                chunk=chunk,
                score=result.score,
                distance=None  # Qdrant doesn't return distance separately
            ))
        
        return search_results
    
    def _get_all_chunks(self, policy_id: str) -> List[TextChunk]:
        """
        Retrieve all chunks for a policy from Qdrant.
        
        Args:
            policy_id: Policy to retrieve chunks from
            
        Returns:
            List of TextChunk objects
        """
        collection_name = f"{self.config.collection_prefix}{policy_id}"
        
        if not self.qdrant_client.collection_exists(collection_name):
            return []
        
        # Scroll through all points in the collection
        chunks = []
        offset = None
        
        while True:
            results = self.qdrant_client.scroll(
                collection_name=collection_name,
                limit=VECTOR_SCROLL_BATCH_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            points, next_offset = results
            
            if not points:
                break
            
            for point in points:
                chunk = TextChunk(
                    id=point.payload["id"],
                    text=point.payload["text"],
                    page=point.payload["page"],
                    chunk_index=point.payload["chunk_index"],
                    token_count=point.payload["token_count"],
                    start_char=point.payload.get("start_char"),
                    end_char=point.payload.get("end_char")
                )
                chunks.append(chunk)
            
            if next_offset is None:
                break
            
            offset = next_offset
        
        return chunks
    
    def search_hybrid(
        self,
        policy_id: str,
        query: str,
        limit: Optional[int] = None,
        bm25_weight: float = 0.5
    ) -> List[SearchResult]:
        """
        Hybrid search combining BM25 (keyword) and semantic similarity.
        
        This method combines:
        - BM25: Keyword-based search for exact term matching
        - Semantic: Vector similarity for conceptual matching
        
        Args:
            policy_id: Policy to search in
            query: Search query text
            limit: Maximum number of results (uses config default if None)
            bm25_weight: Weight for BM25 scores (0-1), semantic gets (1 - bm25_weight)
            
        Returns:
            List of SearchResult objects ranked by combined score
        """
        from rank_bm25 import BM25Okapi
        
        max_results = limit or self.config.max_results
        
        # Get all chunks for this policy
        all_chunks = self._get_all_chunks(policy_id)
        
        if not all_chunks:
            return []
        
        # Get semantic search results
        semantic_results = self.search_similar_chunks(policy_id, query, limit=max_results * 2)
        
        # Create BM25 index
        tokenized_corpus = [chunk.text.lower().split() for chunk in all_chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Get BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # Normalize BM25 scores to 0-1 range
        if max(bm25_scores) > 0:
            bm25_scores_norm = [score / max(bm25_scores) for score in bm25_scores]
        else:
            bm25_scores_norm = bm25_scores
        
        # Create a dictionary mapping chunk ID to BM25 score
        bm25_score_dict = {chunk.id: bm25_scores_norm[i] for i, chunk in enumerate(all_chunks)}
        
        # Create a dictionary mapping chunk ID to semantic score
        semantic_score_dict = {result.chunk.id: result.score for result in semantic_results}
        
        # Combine scores for all chunks
        combined_results = {}
        for chunk in all_chunks:
            bm25_score = bm25_score_dict.get(chunk.id, 0.0)
            semantic_score = semantic_score_dict.get(chunk.id, 0.0)
            
            # Calculate weighted combined score
            combined_score = (bm25_weight * bm25_score) + ((1 - bm25_weight) * semantic_score)
            
            combined_results[chunk.id] = SearchResult(
                chunk=chunk,
                score=combined_score,
                distance=None
            )
        
        # Sort by combined score and return top results
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x.score,
            reverse=True
        )
        
        # Filter by similarity threshold and limit
        filtered_results = [
            result for result in sorted_results
            if result.score >= self.config.similarity_threshold
        ][:max_results]
        
        return filtered_results
    
    def search_with_rerank(
        self,
        policy_id: str,
        query: str,
        limit: Optional[int] = None,
        rerank_top_k: int = 10
    ) -> List[SearchResult]:
        """
        Semantic search with Cohere reranking for improved relevance.
        
        This method combines:
        - Semantic search: Vector similarity for initial candidate retrieval
        - Cohere Rerank: Advanced reranking model for query-specific relevance
        
        Args:
            policy_id: Policy to search in
            query: Search query text
            limit: Maximum number of final results (uses config default if None)
            rerank_top_k: Number of candidates to retrieve before reranking (more = better quality, slower)
            
        Returns:
            List of SearchResult objects ranked by Cohere relevance scores
        """
        max_results = limit or self.config.max_results
        
        # Step 1: Get top candidates using semantic search (more than final limit)
        semantic_candidates = self.search_similar_chunks(
            policy_id=policy_id,
            query=query,
            limit=rerank_top_k
        )
        
        if not semantic_candidates:
            return []
        
        # Step 2: Prepare documents for reranking (must be LangChain Document objects)
        documents = [
            Document(page_content=result.chunk.text)
            for result in semantic_candidates
        ]
        
        # Step 3: Rerank using Cohere
        reranked = self.reranker.compress_documents(
            documents=documents,
            query=query
        )
        
        # Step 4: Map reranked results back to SearchResult objects
        # Cohere returns documents in reranked order with relevance scores
        reranked_results = []
        for doc in reranked[:max_results]:
            # Find the original chunk that matches this document
            for candidate in semantic_candidates:
                if candidate.chunk.text == doc.page_content:
                    # Create new SearchResult with Cohere relevance score
                    reranked_results.append(SearchResult(
                        chunk=candidate.chunk,
                        score=doc.metadata.get("relevance_score", 0.0),
                        distance=None  # Distance not meaningful after reranking
                    ))
                    break
        
        return reranked_results
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        Delete all chunks for a specific policy.

        Args:
            policy_id: Policy to delete

        Returns:
            True if collection was deleted, False if collection didn't exist
        """
        collection_name = f"{self.config.collection_prefix}{policy_id}"

        if self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.delete_collection(collection_name)
            return True

        return False  # Explicitly return False if collection doesn't exist
