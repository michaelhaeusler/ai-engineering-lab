import os
from typing import Any, AsyncIterator, Iterable, List, MutableMapping

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv()

# Type alias for chat messages - makes code more readable
ChatMessage = MutableMapping[str, Any]


class ChatOpenAI:
    """
    Thin wrapper around the OpenAI chat completion APIs.

    This is the GENERATION component of RAG! After retrieving relevant
    documents, we use this class to generate responses from the LLM.

    Key RAG Concepts:
    - Generation: The "G" in RAG - using LLMs to create responses
    - Context Integration: Combining retrieved documents with user queries
    - Streaming: Real-time response generation for better user experience
    - Chat Format: Structured conversations with roles (system/user/assistant)

    This wrapper simplifies OpenAI API usage and provides both synchronous
    and asynchronous interfaces for different use cases.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the chat model wrapper.

        Args:
            model_name (str): OpenAI model to use for chat completions
                - "gpt-4o-mini": Cheaper, faster, good for most tasks
                - "gpt-4o": More expensive, higher quality reasoning
                - "gpt-3.5-turbo": Older, cheaper option

        Python Concepts:
        - Environment variables: Secure API key storage
        - Client initialization: Setting up both sync and async clients
        - Error handling: Validates API key is present
        """
        self.model_name = model_name
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY is not set")

        self._client = OpenAI()  # Synchronous client
        self._async_client = AsyncOpenAI()  # Asynchronous client

    def run(
        self,
        messages: Iterable[ChatMessage],
        text_only: bool = True,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a chat completion request.

        This is the SYNCHRONOUS method for getting LLM responses. Perfect for
        simple use cases where you don't need streaming.

        Args:
            messages (Iterable[ChatMessage]): List of chat messages
                Each message should be: {"role": "user/system/assistant", "content": "text"}
            text_only (bool): If True, return just the response text; if False, return full response object
            **kwargs: Additional parameters for OpenAI API (temperature, max_tokens, etc.)

        Returns:
            Any: Either the response text (if text_only=True) or full response object

        In RAG systems, this is where the magic happens:
        1. System message contains instructions + retrieved documents
        2. User message contains the question
        3. LLM generates response based on both

        Example RAG usage:
            messages = [
                {"role": "system", "content": "Use these docs: " + retrieved_chunks},
                {"role": "user", "content": "What is machine learning?"}
            ]
            response = chat_model.run(messages)

        Python Concepts:
        - **kwargs: Pass additional parameters to OpenAI API
        - Conditional return: Different return types based on text_only flag
        - Method chaining: Uses helper method _coerce_messages
        """
        message_list = self._coerce_messages(messages)
        response = self._client.chat.completions.create(
            model=self.model_name, messages=message_list, **kwargs
        )

        if text_only:
            return response.choices[0].message.content  # Just the text response

        return response  # Full response object with metadata

    async def astream(
        self, messages: Iterable[ChatMessage], **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        Yield streaming completion chunks as they arrive from the API.

        This is the STREAMING method - perfect for real-time chat interfaces!
        Instead of waiting for the complete response, you get chunks as they're generated.

        Args:
            messages (Iterable[ChatMessage]): List of chat messages (same format as run())
            **kwargs: Additional parameters for OpenAI API

        Yields:
            str: Text chunks as they arrive from the API

        This creates a much better user experience because:
        - Users see responses appearing in real-time
        - No waiting for the complete response
        - Feels more conversational and responsive

        Python Concepts:
        - async def: Asynchronous function that can be awaited
        - AsyncIterator: Returns an async generator that yields values
        - yield: Produces values one at a time (like a generator)
        - async for: Iterates over async iterators

        Example usage:
            async for chunk in chat_model.astream(messages):
                print(chunk, end="", flush=True)  # Print each chunk immediately

        RAG Concepts:
        - Streaming Generation: Real-time response generation
        - User Experience: Better perceived performance
        - Incremental Display: Show partial responses as they're generated
        """
        message_list = self._coerce_messages(messages)
        stream = await self._async_client.chat.completions.create(
            model=self.model_name, messages=message_list, stream=True, **kwargs
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content  # Yield each chunk of text as it arrives

    def _coerce_messages(self, messages: Iterable[ChatMessage]) -> List[ChatMessage]:
        """
        Convert messages to a list format if they aren't already.

        Args:
            messages (Iterable[ChatMessage]): Messages in any iterable format

        Returns:
            List[ChatMessage]: Messages as a list

        This is a helper method that ensures we always have a list of messages
        to send to the OpenAI API, regardless of what format was passed in.

        Python Concepts:
        - Type checking: isinstance() checks if object is of specific type
        - Type conversion: list() converts any iterable to a list
        - Defensive programming: Handle different input types gracefully
        """
        if isinstance(messages, list):
            return messages  # Already a list, return as-is
        return list(messages)  # Convert to list
