import asyncio
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import numpy as np

from aimakerspace.openai_utils.embedding import EmbeddingModel


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Return the cosine similarity between two vectors.

    This is THE mathematical function that makes RAG work! It measures how
    similar two embedding vectors are by calculating the cosine of the angle
    between them.

    Args:
        vector_a (np.ndarray): First embedding vector
        vector_b (np.ndarray): Second embedding vector

    Returns:
        float: Similarity score between -1 and 1
            - 1.0: Vectors point in exactly the same direction (very similar)
            - 0.0: Vectors are perpendicular (unrelated)
            - -1.0: Vectors point in opposite directions (opposite meaning)

    Key RAG Concepts:
    - Cosine Similarity: Measures angle between vectors, not distance
    - Why cosine?: It's normalized - vector length doesn't matter, only direction
    - Semantic Similarity: Similar meanings = similar vectors = high cosine similarity

    Python Concepts:
    - numpy arrays: Efficient mathematical operations on large vectors
    - Linear algebra: Using dot products and norms for similarity
    - Edge case handling: Returns 0.0 if either vector is all zeros

    Mathematical Formula:
    cosine_similarity = (A · B) / (||A|| * ||B||)
    Where A · B is dot product, ||A|| is the norm (length) of vector A
    """
    norm_a = np.linalg.norm(vector_a)  # Calculate length/magnitude of vector A
    norm_b = np.linalg.norm(vector_b)  # Calculate length/magnitude of vector B
    if norm_a == 0 or norm_b == 0:
        return 0.0  # Avoid division by zero

    dot_product = np.dot(vector_a, vector_b)  # Calculate dot product
    return float(dot_product / (norm_a * norm_b))  # Return cosine similarity


class VectorDatabase:
    """
    Minimal in-memory vector store backed by numpy arrays.

    This is the STORAGE and SEARCH engine of RAG! It stores document chunks
    as embedding vectors and enables fast semantic search.

    Key RAG Concepts:
    - Vector Database: Stores embeddings with their associated text
    - Semantic Search: Find similar vectors = find similar meaning
    - In-memory: Fast but limited by RAM (for production, use persistent DBs)
    - Key-Value Store: Maps text chunks to their embedding vectors

    How RAG Search Works:
    1. Store: Document chunks → embeddings → stored in database
    2. Query: User question → embedding → search similar embeddings
    3. Retrieve: Most similar embeddings → their original text chunks
    4. Generate: Pass retrieved chunks to LLM for answer generation

    This is a simple implementation. Production systems use specialized
    vector databases like Pinecone, Weaviate, or Chroma.
    """

    def __init__(self, embedding_model: Optional[EmbeddingModel] = None):
        """
        Initialize the vector database.

        Args:
            embedding_model (Optional[EmbeddingModel]): Model for generating embeddings
                If None, creates a default EmbeddingModel instance

        Python Concepts:
        - Optional type: Can be None or EmbeddingModel
        - Default parameter: Creates EmbeddingModel() if none provided
        - Dictionary typing: Dict[str, np.ndarray] means keys are strings, values are numpy arrays
        """
        self.vectors: Dict[str, np.ndarray] = {}  # Maps text chunks to their embeddings
        self.embedding_model = (
            embedding_model or EmbeddingModel()
        )  # Create default if none provided

    def insert(self, key: str, vector: Iterable[float]) -> None:
        """
        Store a vector so that it can be retrieved with key later on.

        Args:
            key (str): The text chunk that this vector represents
            vector (Iterable[float]): The embedding vector for this text

        This is how we populate the database with document chunks and their embeddings.
        The key is usually the original text chunk, and the vector is its embedding.

        Python Concepts:
        - np.asarray(): Converts list of floats to numpy array for efficient math
        - dtype=float: Ensures all numbers are floating-point for consistency
        - Dictionary storage: self.vectors[key] = value stores the mapping

        RAG Concepts:
        - Vector Storage: Keeping embeddings accessible for later search
        - Text-to-Vector Mapping: Connecting original text to its numerical representation
        """
        self.vectors[key] = np.asarray(vector, dtype=float)

    def search(
        self,
        query_vector: Iterable[float],
        k: int,
        distance_measure: Callable[[np.ndarray, np.ndarray], float] = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        """
        Return the k vectors most similar to query_vector.

        This is the CORE of RAG search! Given a query embedding, find the most
        similar document chunk embeddings.

        Args:
            query_vector (Iterable[float]): Embedding of the user's question
            k (int): Number of most similar chunks to return
            distance_measure (Callable): Function to measure similarity (default: cosine_similarity)

        Returns:
            List[Tuple[str, float]]: List of (text_chunk, similarity_score) pairs
                Sorted by similarity score (highest first)

        How it works:
        1. Convert query to numpy array for efficient computation
        2. Calculate similarity between query and every stored vector
        3. Sort by similarity score (highest = most similar)
        4. Return top k results

        Python Concepts:
        - List comprehension: Creates list of (key, score) tuples efficiently
        - Lambda function: key=lambda item: item[1] sorts by similarity score
        - Tuple unpacking: (key, vector) extracts both from dictionary items
        - Slicing: scores[:k] gets first k items

        RAG Concepts:
        - Similarity Search: Finding semantically similar content
        - Top-k Retrieval: Getting the most relevant chunks, not all of them
        - Ranking: Ordering results by relevance/similarity
        """
        if k <= 0:
            raise ValueError("k must be a positive integer")

        query = np.asarray(query_vector, dtype=float)
        scores = [
            (key, distance_measure(query, vector))
            for key, vector in self.vectors.items()
        ]
        scores.sort(
            key=lambda item: item[1], reverse=True
        )  # Sort by similarity (highest first)
        return scores[:k]  # Return top k results

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable[[np.ndarray, np.ndarray], float] = cosine_similarity,
        return_as_text: bool = False,
    ) -> Union[List[Tuple[str, float]], List[str]]:
        """
        Vector search using an embedding generated from query_text.

        This is the HIGH-LEVEL interface for RAG search! Just pass in a text query
        and get back the most relevant document chunks.

        Args:
            query_text (str): The user's question in plain text
            k (int): Number of most similar chunks to return
            distance_measure (Callable): Function to measure similarity
            return_as_text (bool): If True, return only text chunks; if False, include scores

        Returns:
            Union[List[Tuple[str, float]], List[str]]:
                If return_as_text=False: List of (text_chunk, similarity_score) pairs
                If return_as_text=True: List of just the text chunks

        How it works:
        1. Convert user's text question to an embedding vector
        2. Search for similar vectors in the database
        3. Return results in requested format

        This is what you'll use most often in RAG applications:

        Example:
            db = VectorDatabase()
            # ... populate database with document chunks ...
            relevant_chunks = db.search_by_text("What is machine learning?", k=3)

        RAG Concepts:
        - End-to-end Search: Text in, relevant text out
        - Automatic Embedding: Handles the embedding generation internally
        - Flexible Output: Can return scores or just text depending on needs
        """
        query_vector = self.embedding_model.get_embedding(
            query_text
        )  # Convert text to embedding
        results = self.search(
            query_vector, k, distance_measure
        )  # Search for similar vectors
        if return_as_text:
            return [result[0] for result in results]  # Return just the text chunks
        return results  # Return (text, score) pairs

    def retrieve_from_key(self, key: str) -> Optional[np.ndarray]:
        """
        Return the stored vector for key if present.

        Args:
            key (str): The text chunk to look up

        Returns:
            Optional[np.ndarray]: The embedding vector, or None if key not found

        This is useful for debugging or when you need the actual embedding vector
        for a specific text chunk.
        """
        return self.vectors.get(key)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        """
        Populate the vector store asynchronously from raw text snippets.

        This is the BULK LOADING method for RAG! Give it a list of text chunks
        and it will generate embeddings for all of them and store them.

        Args:
            list_of_text (List[str]): List of text chunks to embed and store

        Returns:
            VectorDatabase: Returns self for method chaining

        How it works:
        1. Generate embeddings for all texts in one batch (efficient!)
        2. Store each text chunk with its corresponding embedding
        3. Return self so you can chain method calls

        Python Concepts:
        - async/await: Non-blocking operation for better performance
        - zip(): Pairs each text with its corresponding embedding
        - Method chaining: Returning self allows db.abuild_from_list().search_by_text()
        - Type hint "VectorDatabase": Quotes needed for forward reference

        RAG Concepts:
        - Bulk Loading: Efficient way to populate the database with many documents
        - Batch Embedding: Generate many embeddings at once (faster, cheaper)
        - Database Population: Converting document collection to searchable format

        Example:
            chunks = ["Machine learning is...", "Neural networks are...", ...]
            db = await VectorDatabase().abuild_from_list(chunks)
        """
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, embedding)
        return self


if __name__ == "__main__":
    """
    Example usage demonstrating the complete RAG vector database workflow.
    
    This shows how to:
    1. Create a vector database
    2. Populate it with text chunks
    3. Perform semantic searches
    4. Retrieve specific vectors
    
    The example demonstrates semantic similarity: "I think fruit is awesome!"
    should match texts about bananas and broccoli, even though it doesn't
    use the exact same words.
    """
    # Sample text chunks with different topics
    list_of_text = [
        "I like to eat broccoli and bananas.",  # Food/fruit topic
        "I ate a banana and spinach smoothie for breakfast.",  # Food/fruit topic
        "Chinchillas and kittens are cute.",  # Animals topic
        "My sister adopted a kitten yesterday.",  # Animals topic
        "Look at this cute hamster munching on a piece of broccoli.",  # Animals + food
    ]

    # Create and populate the vector database
    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2  # Get top 2 most similar results

    # Search for texts similar to "I think fruit is awesome!"
    # This should match the food-related texts even though the words are different
    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    # Retrieve the specific vector for a known text
    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print(
        "Retrieved vector shape:",
        retrieved_vector.shape if retrieved_vector is not None else "None",
    )

    # Get just the text results without similarity scores
    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
