"""
Simple A2A Tool - Query the A2A server agent with streaming support

This tool enables a LangGraph agent to communicate with the A2A server
using the A2A protocol with streaming responses.
"""

import os
from uuid import uuid4

import httpx
from langchain_core.tools import tool
from a2a.client import A2AClient
from a2a.types import SendStreamingMessageRequest, MessageSendParams


# A2A Server configuration
A2A_SERVER_URL = os.getenv('A2A_SERVER_URL', 'http://localhost:10000')
REQUEST_TIMEOUT = 60  # seconds


@tool
async def query_a2a_agent(question: str) -> str:
    """
    Send a question to the A2A server agent and get the response.

    The A2A agent can:
    - Search the web for current information
    - Find academic papers on arXiv
    - Retrieve information from documents

    Args:
        question: The question to ask the A2A agent

    Returns:
        str: The response from the A2A agent
    """
    try:
        # Create async HTTP client with timeout
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as httpx_client:
            # Initialize A2A client
            client = A2AClient(httpx_client=httpx_client, url=A2A_SERVER_URL)

            # Create streaming request
            request = SendStreamingMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(
                    message={
                        'role': 'user',
                        'parts': [{'kind': 'text', 'text': question}],
                        'message_id': uuid4().hex,
                    }
                )
            )

            # Stream responses from A2A server
            stream_response = client.send_message_streaming(request)

            collected_text = []

            async for chunk in stream_response:
                try:
                    result = chunk.root.result

                    # Only process artifact-update events
                    if getattr(result, 'kind', None) != 'artifact-update':
                        continue

                    # Extract text from artifact parts
                    artifact = getattr(result, 'artifact', None)
                    if not artifact:
                        continue

                    parts = getattr(artifact, 'parts', [])
                    for part in parts:
                        # Extract text from the part's root
                        part_root = getattr(part, 'root', None)
                        if part_root:
                            text = getattr(part_root, 'text', None)
                            if text:
                                collected_text.append(text)

                except (AttributeError, TypeError):
                    # Skip malformed chunks
                    continue

            # Return the collected response
            if collected_text:
                return '\n'.join(collected_text)
            else:
                return 'The A2A agent responded but no content was returned.'

    except httpx.ConnectError:
        return (
            f'Cannot connect to A2A server at {A2A_SERVER_URL}. '
            'Make sure the server is running with: uv run python -m app'
        )
    except httpx.TimeoutException:
        return f'Request to A2A server timed out after {REQUEST_TIMEOUT} seconds.'
    except Exception as e:
        return f'Error communicating with A2A agent: {str(e)}'
