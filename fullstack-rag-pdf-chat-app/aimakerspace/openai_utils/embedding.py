import asyncio
import os
from typing import Iterable, List

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI


class EmbeddingModel:
    """
    Helper for generating embeddings via the OpenAI API.

    This is the HEART of RAG systems! Embeddings are numerical representations
    of text that capture semantic meaning. Similar texts have similar embeddings.

    Key RAG Concepts:
    - Embeddings: Converting text into high-dimensional vectors (lists of numbers)
    - Semantic Similarity: Texts with similar meaning have similar embeddings
    - Vector Space: Embeddings exist in a mathematical space where distance = similarity
    - Dense Representations: Each dimension captures some aspect of meaning

    How it works:
    1. Text goes in: "The cat sat on the mat"
    2. Embedding comes out: [0.1, -0.3, 0.7, ..., 0.2] (1536 numbers for text-embedding-3-small)
    3. Similar texts get similar number patterns

    This enables semantic search: find documents that mean similar things,
    not just documents that use the same words.
    """

    def __init__(
        self, embeddings_model_name: str = "text-embedding-3-small", api_key: str = None
    ):
        """
        Initialize the embedding model.

        Args:
            embeddings_model_name (str): OpenAI embedding model to use
                - "text-embedding-3-small": Cheaper, faster, good quality
                - "text-embedding-3-large": More expensive, slower, higher quality
            api_key (str): OpenAI API key. If not provided, will try to get from environment variable.

        Python Concepts:
        - Environment variables: API keys stored securely outside code
        - Client initialization: Setting up both sync and async clients
        - Error handling: Validates API key is present
        """
        load_dotenv()  # Load environment variables from .env file

        # Use provided API key or fall back to environment variable
        self.openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key is None:
            raise ValueError(
                "OpenAI API key is required. Please provide it as a parameter or set the OPENAI_API_KEY environment variable."
            )

        self.embeddings_model_name = embeddings_model_name
        self.async_client = AsyncOpenAI(
            api_key=self.openai_api_key
        )  # For async operations (faster when processing many texts)
        self.client = OpenAI(
            api_key=self.openai_api_key
        )  # For synchronous operations (simpler to use)

    async def async_get_embeddings(
        self, list_of_text: Iterable[str]
    ) -> List[List[float]]:
        """
        Return embeddings for multiple texts using the async client.

        Args:
            list_of_text (Iterable[str]): Multiple text strings to embed

        Returns:
            List[List[float]]: List of embeddings, one for each input text

        This is the BATCH version - more efficient when processing many texts
        because it sends them all in one API request instead of many separate requests.

        Python Concepts:
        - async/await: Non-blocking operations that can run concurrently
        - List comprehension: Extracting embeddings from API response
        - Type hints: List[List[float]] means "list of lists of floats"

        RAG Concepts:
        - Batch processing: More efficient for large document collections
        - API efficiency: Fewer requests = lower cost and faster processing
        """
        embedding_response = await self.async_client.embeddings.create(
            input=list(list_of_text), model=self.embeddings_model_name
        )

        return [item.embedding for item in embedding_response.data]

    async def async_get_embedding(self, text: str) -> List[float]:
        """
        Return an embedding for a single text using the async client.

        Args:
            text (str): Single text string to embed

        Returns:
            List[float]: Embedding vector for the input text

        Use this for single texts or when you need async behavior.
        For multiple texts, prefer async_get_embeddings() for efficiency.
        """
        embedding = await self.async_client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        return embedding.data[0].embedding

    def get_embeddings(self, list_of_text: Iterable[str]) -> List[List[float]]:
        """
        Return embeddings for multiple texts using the synchronous client.

        Args:
            list_of_text (Iterable[str]): Multiple text strings to embed

        Returns:
            List[List[float]]: List of embeddings, one for each input text

        Synchronous version - easier to use but blocks execution until complete.
        Use this when you don't need async behavior or are learning.

        Python Concepts:
        - Synchronous execution: Code waits for API call to complete
        - Simpler error handling: No async/await complexity
        """
        embedding_response = self.client.embeddings.create(
            input=list(list_of_text), model=self.embeddings_model_name
        )

        return [item.embedding for item in embedding_response.data]

    def get_embedding(self, text: str) -> List[float]:
        """
        Return an embedding for a single text using the synchronous client.

        Args:
            text (str): Single text string to embed

        Returns:
            List[float]: Embedding vector for the input text

        Simplest method to use - just pass in text and get back the embedding vector.
        Perfect for testing, learning, or simple use cases.

        Example:
            embedding_model = EmbeddingModel()
            vector = embedding_model.get_embedding("Hello world")
            print(len(vector))  # Will print 1536 for text-embedding-3-small
        """
        embedding = self.client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        return embedding.data[0].embedding


if __name__ == "__main__":
    """
    Example usage demonstrating embedding generation.
    
    This shows how to:
    1. Create an embedding model
    2. Generate embedding for a single text
    3. Generate embeddings for multiple texts
    
    The output will be lists of floating-point numbers representing
    the semantic meaning of the input texts.
    """
    embedding_model = EmbeddingModel()

    # Generate embedding for a single text
    single_embedding = asyncio.run(embedding_model.async_get_embedding("Hello, world!"))
    print(f"Single embedding length: {len(single_embedding)}")
    print(f"First few values: {single_embedding[:5]}")  # Show first 5 numbers

    # Generate embeddings for multiple texts
    multiple_embeddings = asyncio.run(
        embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
    )
    print(f"Generated {len(multiple_embeddings)} embeddings")
    print(f"Each embedding has {len(multiple_embeddings[0])} dimensions")
