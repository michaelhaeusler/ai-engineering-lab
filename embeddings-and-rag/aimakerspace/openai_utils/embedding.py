import os
import asyncio
import logging
import time
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from tqdm.asyncio import tqdm
import numpy as np
from typing import List


class EmbeddingModel:
    def __init__(
        self,
        embeddings_model_name: str = "text-embedding-3-small",
        batch_size: int = 1024,
        enable_logging: bool = True,
        enable_progress: bool = True,
    ):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.async_client = AsyncOpenAI()
        self.client = OpenAI()

        if self.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. Please set it to your OpenAI API key."
            )
        self.embeddings_model_name = embeddings_model_name
        self.batch_size = batch_size
        self.enable_logging = enable_logging
        self.enable_progress = enable_progress

        # Set up logging
        if self.enable_logging:
            # Create logger with hierarchical name
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

            # Don't create handlers - let the root logger handle it
            self.logger.propagate = True

    async def async_get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts with logging and progress tracking.

        Args:
            list_of_text: List of text strings to embed

        Returns:
            List of embedding vectors (each as List[float])
        """

        # Start timing the entire operation
        start_time = time.time()
        total_texts = len(list_of_text)

        # Log the operation start with key parameters
        if self.enable_logging:
            self.logger.info(f"Starting embedding creation for {total_texts} texts")
            self.logger.info(f"Using model: {self.embeddings_model_name}")
            self.logger.info(f"Batch size: {self.batch_size}")

        # Create batches for API efficiency
        # Split the list into batches
        batches = [
            list_of_text[i : i + self.batch_size]
            for i in range(0, len(list_of_text), self.batch_size)
        ]
        total_batches = len(batches)

        if self.enable_logging:
            self.logger.info(f"Created {total_batches} batches for processing")

        async def process_batch(batch_idx: int, batch: List[str]) -> List[List[float]]:
            """Process a single batch with timing and error handling"""
            batch_start = time.time()

            try:
                if self.enable_logging:
                    self.logger.debug(
                        f"Processing batch {batch_idx + 1}/{total_batches} with {len(batch)} texts"
                    )

                # Make the actual API call
                embedding_response = await self.async_client.embeddings.create(
                    input=batch, model=self.embeddings_model_name
                )

                # Log batch completion time
                batch_time = time.time() - batch_start
                if self.enable_logging:
                    self.logger.debug(
                        f"Batch {batch_idx + 1} completed in {batch_time:.2f}s"
                    )

                # Extract embeddings from response and return them
                return [embeddings.embedding for embeddings in embedding_response.data]

            except Exception as e:
                if self.enable_logging:
                    self.logger.error(
                        f"Error processing batch {batch_idx + 1}: {str(e)}"
                    )
                raise

        # Process batches with optional progress tracking
        if self.enable_progress:
            # Create progress bar for batches
            batch_tasks = [process_batch(i, batch) for i, batch in enumerate(batches)]
            results = []

            # Use tqdm for progress tracking with async tasks
            with tqdm(
                total=total_batches, desc="Creating embeddings", unit="batch"
            ) as pbar:
                for task in asyncio.as_completed(batch_tasks):
                    result = await task
                    results.append(result)
                    pbar.update(1)  # Update progress bar
        else:
            # Process without progress bar (faster for small datasets)
            # Use asyncio.gather to process all batches concurrently
            results = await asyncio.gather(
                *[process_batch(i, batch) for i, batch in enumerate(batches)]
            )

        # Flatten the results from all batches
        all_embeddings = []
        for batch_result in results:
            all_embeddings.extend(batch_result)

        # Same as above but using a list comprehension
        # return [embedding for batch_result in results for embedding in batch_result]

        # Convert to numpy arrays for better performance
        embeddings_array = np.array(all_embeddings)

        # Log final statistics
        total_time = time.time() - start_time
        if self.enable_logging:
            self.logger.info(f"Embedding creation completed in {total_time:.2f}s")
            self.logger.info(f"Average time per text: {total_time / total_texts:.3f}s")
            self.logger.info(f"Embedding shape: {embeddings_array.shape}")

        # Return as list of lists for compatibility with existing code
        return embeddings_array.tolist()

    async def async_get_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text with logging"""

        # Log input details at debug level (won't show unless DEBUG enabled)
        if self.enable_logging:
            self.logger.debug(f"Creating embedding for text of length {len(text)}")

        # Time the API call
        start_time = time.time()

        embedding = await self.async_client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        # Log completion time
        if self.enable_logging:
            elapsed = time.time() - start_time
            self.logger.debug(f"Single embedding created in {elapsed:.3f}s")

        return embedding.data[0].embedding

    def get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        embedding_response = self.client.embeddings.create(
            input=list_of_text, model=self.embeddings_model_name
        )

        return [embeddings.embedding for embeddings in embedding_response.data]

    def get_embedding(self, text: str) -> List[float]:
        embedding = self.client.embeddings.create(
            input=text, model=self.embeddings_model_name
        )

        return embedding.data[0].embedding


if __name__ == "__main__":
    embedding_model = EmbeddingModel()
    print(asyncio.run(embedding_model.async_get_embedding("Hello, world!")))
    print(
        asyncio.run(
            embedding_model.async_get_embeddings(["Hello, world!", "Goodbye, world!"])
        )
    )
