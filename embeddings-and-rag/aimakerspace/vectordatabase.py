import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio
import logging
import time


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the cosine similarity between two vectors.

    What it does: Measures the cosine of the angle between two vectors (direction similarity, ignoring magnitude)
    Formula: cos(θ) = (a · b) / (||a|| × ||b||)

        Where:
            a · b = dot product of vectors a and b
            ||a|| = magnitude (length) of vector a
            ||b|| = magnitude (length) of vector b
            θ = angle between the vectors

        Args:
            vector_a: The first vector
            vector_b: The second vector

        Returns:
            The cosine similarity between the two vectors
    """
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


def euclidean_distance(vector_a: np.array, vector_b: np.array) -> float:
    """
    Computes the Euclidean distance between two vectors.

    What it does: Measures straight-line distance between two points in space
    Formula: √(Σ(aᵢ - bᵢ)²)

    Args:
        vector_a: The first vector
        vector_b: The second vector

    Returns:
        The Euclidean distance between the two vectors
    """
    # Calculate the difference between vectors
    diff = vector_a - vector_b

    # Square each difference
    squared_diff = diff**2

    # Sum all squared differences
    sum_squared = np.sum(squared_diff)

    # Take square root
    distance = np.sqrt(sum_squared)

    return distance


def manhattan_distance(vector_a: np.array, vector_b: np.array) -> float:
    """
    Computes the Manhattan distance between two vectors.

    What it does: Measures distance along a grid, like the streets of a city
    Formula: Σ|aᵢ - bᵢ|

    Args:
        vector_a: The first vector
        vector_b: The second vector

    Returns:
        The Manhattan distance between the two vectors
    """
    # Calculate the difference between vectors
    diff = vector_a - vector_b

    # Take absolute value of each difference
    abs_diff = np.abs(diff)

    # Sum all absolute differences
    distance = np.sum(abs_diff)

    return distance


def dot_product_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """
    Computes the dot product similarity between two vectors.

    What it does: Measures how aligned two vectors are
    Formula: Σ(aᵢ * bᵢ)

    Args:
        vector_a: The first vector
        vector_b: The second vector

    Returns:
        The dot product similarity between the two vectors
    """
    # Element-wise multiplication
    multiplied = vector_a * vector_b

    # Sum all products
    similarity = np.sum(multiplied)

    return similarity


class VectorDatabase:
    def __init__(
        self, embedding_model: EmbeddingModel = None, enable_logging: bool = True
    ):
        """
        Initialize VectorDatabase with optional logging.

        Args:
            embedding_model: EmbeddingModel instance for creating embeddings
        """
        self.vectors = defaultdict(np.array)

        # Create embedding model with matching logging preference
        self.embedding_model = embedding_model or EmbeddingModel(
            enable_logging=enable_logging
        )
        self.enable_logging = enable_logging

        # Set up logging using the same pattern as EmbeddingModel
        if self.enable_logging:
            # Create logger with hierarchical name
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

            # Don't create handlers - let the root logger handle it
            self.logger.propagate = True

    def insert(self, key: str, vector: np.array) -> None:
        self.vectors[key] = vector

    def search(
        self,
        query_vector: np.array,
        k: int,
        distance_measure: Callable = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        """
        Search for the k most similar vectors using the specified distance measure.

        Args:
            query_vector: The query vector to search for
            k: Number of top results to return
            distance_measure: Function to calculate similarity (default: cosine_similarity)

        Returns:
            List of tuples (text, similarity_score) sorted by similarity (highest first)
        """
        # Log search initiation with key parameters
        if self.enable_logging:
            self.logger.info(
                f"Searching for top {k} similar vectors from {len(self.vectors)} total vectors"
            )

        # Start timing the search operation
        start_time = time.time()

        # Calculate scores for all vectors
        scores = [
            (key, distance_measure(query_vector, vector))
            for key, vector in self.vectors.items()
        ]

        # Sort based on metric type
        if distance_measure in [euclidean_distance, manhattan_distance]:
            # Distance metrics: lower is better
            results = sorted(scores, key=lambda x: x[1], reverse=False)[:k]
        else:
            # Similarity metrics: higher is better
            results = sorted(scores, key=lambda x: x[1], reverse=True)[:k]

        # Log search completion and performance metrics
        if self.enable_logging:
            elapsed = time.time() - start_time
            self.logger.info(f"Search completed in {elapsed:.3f}s")

        # Log search quality metrics
        if results:
            self.logger.info(f"Top similarity score: {results[0][1]:.3f}")
            if len(results) > 1:
                self.logger.debug(
                    f"Score range: {results[0][1]:.3f} to {results[-1][1]:.3f}"
                )
        else:
            self.logger.warning("No results found in search")

        return results

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
    ) -> List[Tuple[str, float]]:
        """
        Search for similar vectors using text query.

        Args:
            query_text: Text to search for
            k: Number of top results to return
            distance_measure: Function to calculate similarity
            return_as_text: If True, return only text without scores

        Returns:
            List of tuples (text, similarity_score) or just texts if return_as_text=True
        """
        # Log the search query (truncate long queries for readability)
        if self.enable_logging:
            query_preview = (
                query_text[:50] + "..." if len(query_text) > 50 else query_text
            )
            self.logger.info(f"Searching by text: '{query_preview}'")

        # Start timing the entire text search operation
        start_time = time.time()

        # Create embedding for the query text (this calls the embedding API)
        query_vector = self.embedding_model.get_embedding(query_text)

        # Log embedding creation time
        if self.enable_logging:
            embedding_time = time.time() - start_time
            self.logger.info(f"Query embedding created in {embedding_time:.3f}s")

        # Perform vector search using the embedded query
        results = self.search(query_vector, k, distance_measure)

        # Log total operation time
        if self.enable_logging:
            total_time = time.time() - start_time
            self.logger.info(f"Total text search completed in {total_time:.3f}s")

        # Return results in requested format
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> np.array:
        return self.vectors.get(key, None)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        """
        Build vector database from a list of texts with comprehensive logging.

        Args:
            list_of_text: List of text strings to create embeddings for

        Returns:
            Self (for method chaining)
        """
        # Log the database building operation start
        if self.enable_logging:
            self.logger.info(f"Building vector database from {len(list_of_text)} texts")

        # Start timing the entire database building process
        start_time = time.time()

        # Get embeddings (this will show progress bar if enabled in EmbeddingModel)
        # The EmbeddingModel will handle its own logging and progress tracking
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)

        # Log the transition from embedding creation to database insertion
        if self.enable_logging:
            self.logger.info("Inserting embeddings into vector database...")

        # Insert all embeddings into the database
        insertion_start = time.time()
        for text, embedding in zip(list_of_text, embeddings):
            # Convert to numpy array and store
            self.insert(text, np.array(embedding))

        # Calculate and log final statistics
        total_time = time.time() - start_time
        insertion_time = time.time() - insertion_start

        if self.enable_logging:
            self.logger.info(f"Vector database built successfully in {total_time:.2f}s")
            self.logger.info(
                f"  - Embedding creation: {total_time - insertion_time:.2f}s"
            )
            self.logger.info(f"  - Database insertion: {insertion_time:.3f}s")
            self.logger.info(f"Total vectors stored: {len(self.vectors)}")

            # Log memory/storage insights
            if embeddings:
                embedding_dim = len(embeddings[0])
                total_values = len(self.vectors) * embedding_dim

                # Calculate theoretical memory usage (just the data)
                bytes_per_float = 8  # float64
                theoretical_bytes = total_values * bytes_per_float
                theoretical_mb = theoretical_bytes / (1024 * 1024)

                # Calculate actual memory usage (including Python overhead)
                import sys

                actual_memory = sys.getsizeof(self.vectors)
                for key, vector in self.vectors.items():
                    actual_memory += sys.getsizeof(key) + sys.getsizeof(vector)
                actual_mb = actual_memory / (1024 * 1024)

                # Calculate overhead percentage
                overhead_percent = (
                    (actual_memory - theoretical_bytes) / theoretical_bytes
                ) * 100

                self.logger.info(f"Vector dimensions: {embedding_dim}")
                self.logger.info(
                    f"Storage size: {len(self.vectors)} × {embedding_dim} = {total_values:,} values"
                )
                self.logger.info(
                    f"Theoretical memory: {theoretical_bytes:,} bytes ({theoretical_mb:.2f} MB)"
                )
                self.logger.info(
                    f"Actual memory: {actual_memory:,} bytes ({actual_mb:.2f} MB)"
                )
                self.logger.info(f"Memory overhead: {overhead_percent:.1f}%")

        return self

    def compare_metrics(
        self, query_text: str, k: int = 3, return_as_text: bool = False
    ) -> dict:
        """
        Compare all distance metrics on the same query with intelligent score evaluation.

        Args:
            query_text: The text query to search for
            k: Number of top results to return
            return_as_text: Whether to return text or keys

        Returns:
            Dictionary with results and evaluations for each metric
        """
        if self.enable_logging:
            self.logger.info(
                f" Comparing all distance metrics for query: '{query_text[:50]}...'"
            )

        # Create query embedding once (shared by all metrics)
        start_time = time.time()
        query_embedding = self.embedding_model.get_embedding(query_text)
        embedding_time = time.time() - start_time

        if self.enable_logging:
            self.logger.info(f"📊 Query embedding created in {embedding_time:.3f}s")

        # Define all metrics to test with their evaluation functions
        metrics = {
            "cosine_similarity": {
                "function": cosine_similarity,
                "evaluate": self._evaluate_cosine_score,
                "range": "0.0 to 1.0",
            },
            "euclidean_distance": {
                "function": euclidean_distance,
                "evaluate": self._evaluate_euclidean_score,
                "range": "0.0 to ∞",
            },
            "manhattan_distance": {
                "function": manhattan_distance,
                "evaluate": self._evaluate_manhattan_score,
                "range": "0.0 to ∞",
            },
            "dot_product_similarity": {
                "function": dot_product_similarity,
                "evaluate": self._evaluate_dot_product_score,
                "range": "-∞ to +∞",
            },
        }

        results = {}

        # Test each metric
        for metric_name, metric_info in metrics.items():
            if self.enable_logging:
                self.logger.info(f"🧮 Testing {metric_name}...")

            # Time the search operation
            search_start = time.time()
            search_results = self.search(query_embedding, k, metric_info["function"])
            search_time = time.time() - search_start

            # Evaluate the top score
            top_score = search_results[0][1] if search_results else 0
            evaluation = metric_info["evaluate"](top_score)

            # Convert to text if requested
            if return_as_text:
                text_results = [
                    self.retrieve_from_key(key) for key, _ in search_results
                ]
                results[metric_name] = {
                    "results": text_results,
                    "scores": [score for _, score in search_results],
                    "search_time": search_time,
                    "total_time": embedding_time + search_time,
                    "top_score": top_score,
                    "evaluation": evaluation,
                    "range": metric_info["range"],
                }
            else:
                results[metric_name] = {
                    "results": search_results,
                    "search_time": search_time,
                    "total_time": embedding_time + search_time,
                    "top_score": top_score,
                    "evaluation": evaluation,
                    "range": metric_info["range"],
                }

            if self.enable_logging:
                self.logger.info(
                    f"   ⚡ {metric_name}: {search_time:.3f}s, top score: {top_score:.3f} ({evaluation})"
                )

        # Log performance summary
        if self.enable_logging:
            self.logger.info("📈 Performance Summary:")
            for metric_name, data in results.items():
                self.logger.info(
                    f"   {metric_name}: {data['search_time']:.3f}s - {data['evaluation']}"
                )

        return results

    def _evaluate_cosine_score(self, score: float) -> str:
        """Evaluate cosine similarity score quality."""
        if score >= 0.9:
            return "[EXCELLENT] Perfect match"
        elif score >= 0.8:
            return "[VERY GOOD] Very good match"
        elif score >= 0.7:
            return "[GOOD] Good match"
        elif score >= 0.6:
            return "[MODERATE] Moderate match"
        elif score >= 0.5:
            return "[POOR] Poor match"
        else:
            return "[VERY POOR] Very poor match"

    def _evaluate_euclidean_score(self, score: float) -> str:
        """Evaluate Euclidean distance score quality for 1536-dimensional embeddings."""
        if score <= 0.05:
            return "[EXCELLENT] Perfect match"
        elif score <= 0.15:
            return "[VERY GOOD] Very good match"
        elif score <= 0.25:
            return "[GOOD] Good match"
        elif score <= 0.4:
            return "[MODERATE] Moderate match"
        elif score <= 0.7:
            return "[POOR] Poor match"
        else:
            return "[VERY POOR] Very poor match"

    def _evaluate_manhattan_score(self, score: float) -> str:
        """Evaluate Manhattan distance score quality for 1536-dimensional embeddings."""
        if score <= 0.1:
            return "[EXCELLENT] Perfect match"
        elif score <= 0.3:
            return "[VERY GOOD] Very good match"
        elif score <= 0.5:
            return "[GOOD] Good match"
        elif score <= 0.8:
            return "[MODERATE] Moderate match"
        elif score <= 1.5:
            return "[POOR] Poor match"
        else:
            return "[VERY POOR] Very poor match"

    def _evaluate_dot_product_score(self, score: float) -> str:
        """Evaluate dot product score quality for normalized embeddings (same as cosine)."""
        # For normalized vectors, dot product = cosine similarity
        if score >= 0.9:
            return "[EXCELLENT] Perfect match"
        elif score >= 0.8:
            return "[VERY GOOD] Very good match"
        elif score >= 0.7:
            return "[GOOD] Good match"
        elif score >= 0.6:
            return "[MODERATE] Moderate match"
        elif score >= 0.5:
            return "[POOR] Poor match"
        else:
            return "[VERY POOR] Very poor match"

    if __name__ == "__main__":
        list_of_text = [
            "I like to eat broccoli and bananas.",
            "I ate a banana and spinach smoothie for breakfast.",
            "Chinchillas and kittens are cute.",
            "My sister adopted a kitten yesterday.",
            "Look at this cute hamster munching on a piece of broccoli.",
        ]

        vector_db = VectorDatabase()
        vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
        k = 2

        searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
        print(f"Closest {k} vector(s):", searched_vector)

        retrieved_vector = vector_db.retrieve_from_key(
            "I like to eat broccoli and bananas."
        )
        print("Retrieved vector:", retrieved_vector)

        relevant_texts = vector_db.search_by_text(
            "I think fruit is awesome!", k=k, return_as_text=True
        )
        print(f"Closest {k} text(s):", relevant_texts)
