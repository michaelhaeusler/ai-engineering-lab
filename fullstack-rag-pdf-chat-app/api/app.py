# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Import Pydantic for data validation and settings management
from pydantic import BaseModel

# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
from typing import Optional
import tempfile
from pathlib import Path

# Import RAG components from aimakerspace
from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.vectordatabase import VectorDatabase

"""
Backend API for the AI Chat Application

This FastAPI application provides endpoints for:
1. Chat completions with streaming responses
2. Health checks for monitoring

Key Technologies:
- FastAPI: Modern, fast web framework for building APIs
- OpenAI API: For LLM chat completions
- Pydantic: Data validation and serialization
- CORS: Cross-Origin Resource Sharing for frontend access
- Streaming: Real-time response delivery

This is currently a simple chat API, but it's designed to be extended
with RAG functionality using the aimakerspace package.
"""

# Initialize FastAPI application with a title
app = FastAPI(
    title="OpenAI Chat API",
    description="A FastAPI backend for AI chat applications with streaming support",
    version="1.0.0",
)

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
# CRITICAL for frontend-backend communication!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows requests from any origin (use specific domains in production)
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Global RAG components - initialized when first PDF is uploaded
vector_database = None
embedding_model = None


# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated and typed
class ChatRequest(BaseModel):
    """
    Data model for chat completion requests.

    Pydantic automatically validates that incoming JSON matches this structure
    and converts it to a Python object with proper types.

    Python Concepts:
    - Pydantic BaseModel: Automatic validation and serialization
    - Type hints: Explicit types for each field
    - Optional fields: Can be omitted in requests
    - Default values: Fallback values if not provided
    """

    developer_message: str  # System/developer instructions (maps to "system" role)
    user_message: str  # User's question or input (maps to "user" role)
    model: Optional[str] = (
        "gpt-4o-mini"  # OpenAI model to use (corrected from gpt-4.1-mini)
    )
    api_key: str  # OpenAI API key for authentication

    class Config:
        """Pydantic configuration for the model."""

        # Example of what a valid request looks like (updated for Pydantic V2)
        json_schema_extra = {
            "example": {
                "developer_message": "You are a helpful AI assistant.",
                "user_message": "What is machine learning?",
                "model": "gpt-4o-mini",
                "api_key": "sk-...",
            }
        }


# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
@app.post("/backend/chat")
async def chat(request: ChatRequest):
    """
    Main chat completion endpoint with streaming support.

    This endpoint:
    1. Accepts a chat request with system and user messages
    2. Validates the request data using Pydantic
    3. Creates an OpenAI client with the provided API key
    4. Streams the response back in real-time

    Args:
        request (ChatRequest): Validated request data from the client

    Returns:
        StreamingResponse: Real-time streaming text response

    HTTP Details:
        - Method: POST
        - Path: /api/chat
        - Content-Type: application/json (input)
        - Content-Type: text/plain (output, streaming)

    Future RAG Enhancement:
        This endpoint can be extended to:
        1. Extract relevant documents based on user_message
        2. Include retrieved documents in developer_message
        3. Generate context-aware responses
    """
    try:
        # Initialize OpenAI client with the provided API key
        # Each request uses its own API key for security
        client = OpenAI(api_key=request.api_key)

        # Perform RAG retrieval if vector database is available
        enhanced_developer_message = request.developer_message
        global vector_database, embedding_model

        if vector_database is not None and embedding_model is not None:
            # Get embedding for user's question
            query_embedding = await embedding_model.async_get_embedding(
                request.user_message
            )

            # Retrieve relevant chunks from vector database
            relevant_chunks = vector_database.search(query_embedding, k=3)

            # Create context from retrieved chunks
            if relevant_chunks:
                context = "\n\n".join(
                    [chunk[0] for chunk in relevant_chunks]
                )  # chunk[0] is the text, chunk[1] is the score
                enhanced_developer_message = f"""{request.developer_message}

CONTEXT FROM UPLOADED DOCUMENT:
{context}

Please answer the user's question based ONLY on the information provided in the context above. If the answer is not in the context, please say "I don't have that information in the uploaded document."
"""

        # Create an async generator function for streaming responses
        async def generate():
            """
            Inner generator function that yields response chunks.

            This function handles the streaming logic:
            1. Creates a streaming chat completion request
            2. Processes each chunk as it arrives
            3. Yields content to the client in real-time

            Python Concepts:
            - Nested function: Function defined inside another function
            - Generator: Uses yield to produce values incrementally
            - Streaming: Processes data as it arrives, not all at once
            """
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    # System message: Instructions for how the AI should behave (enhanced with RAG context)
                    {"role": "system", "content": enhanced_developer_message},
                    # User message: The actual question or input
                    {"role": "user", "content": request.user_message},
                ],
                stream=True,  # Enable streaming response (chunks arrive incrementally)
            )

            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                # Check if this chunk contains actual content (not just metadata)
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        # This allows the frontend to display text as it's generated
        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        # Handle any errors that occur during processing
        # This could be API key issues, network problems, etc.
        raise HTTPException(status_code=500, detail=str(e))


# Define a health check endpoint to verify API status
@app.get("/api/health")
@app.get("/backend/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    This simple endpoint allows external services to verify that:
    1. The API server is running
    2. The application is responsive
    3. Basic functionality is working

    Returns:
        dict: Simple status response

    HTTP Details:
        - Method: GET
        - Path: /api/health
        - Response: {"status": "ok"}

    Usage:
        - Monitoring systems can ping this endpoint
        - Load balancers can use it for health checks
        - Deployment systems can verify successful deploys
    """
    return {"status": "ok", "message": "Chat API is running"}


@app.post("/api/clear-document")
@app.post("/backend/clear-document")
async def clear_document():
    """
    Clear the uploaded document and return to normal chat mode.

    This endpoint:
    1. Clears the global vector database
    2. Clears the embedding model
    3. Returns the app to normal chat mode

    Returns:
        dict: Status response confirming document was cleared
    """
    global vector_database, embedding_model

    vector_database = None
    embedding_model = None

    print("🗑️ Document cleared - returning to normal chat mode")

    return {
        "status": "success",
        "message": "Document cleared successfully. App is now in normal chat mode.",
    }


@app.post("/api/upload-pdf")
@app.post("/backend/upload-pdf")
async def upload_pdf(file: UploadFile, api_key: str = Form(None)):
    """
    Process uploaded PDF files for RAG functionality.

    This endpoint:
    1. Validates the uploaded file is a PDF
    2. Temporarily saves the file to disk
    3. Uses PDFLoader to extract text content
    4. Uses CharacterTextSplitter to create chunks
    5. Returns processing results

    Args:
        file (UploadFile): The uploaded PDF file from the frontend
        api_key (str): OpenAI API key for embedding generation

    Returns:
        dict: Processing results with chunks and metadata
    """
    import time

    # Validate API key
    if not api_key or len(api_key.strip()) == 0:
        raise HTTPException(status_code=400, detail="API key is required")

    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        start_time = time.time()
        print(f"🚀 Starting PDF processing: {file.filename}")
        print(
            f"🔑 API Key received: {'✅ Present' if api_key else '❌ Missing'} (length: {len(api_key) if api_key else 0})"
        )
        if api_key:
            print(f"🔑 API Key starts with: {api_key[:10]}... (showing first 10 chars)")
        # Create a temporary file to save the uploaded PDF
        file_start = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Read and save the uploaded file content
            content = await file.read()

            # Server-side size check (align with client 4.5MB limit)
            size_bytes = len(content)
            print(f"📦 Uploaded file size: {size_bytes / (1024 * 1024):.2f} MB")
            import os

            max_mb = float(os.getenv("MAX_PDF_MB", "4.5"))
            max_bytes = int(max_mb * 1024 * 1024)
            if size_bytes > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File is too large. Please upload a PDF smaller than {max_mb}MB (got {size_bytes / (1024 * 1024):.2f}MB).",
                )

            temp_file.write(content)
            temp_file_path = temp_file.name
        file_end = time.time()
        print(f"📁 File saved in {(file_end - file_start) * 1000:.1f}ms")

        # Process the PDF using our RAG components
        pdf_start = time.time()
        pdf_loader = PDFLoader(temp_file_path)
        documents = pdf_loader.load_documents()
        pdf_end = time.time()
        print(
            f"📖 PDF text extraction completed in {(pdf_end - pdf_start) * 1000:.1f}ms - {len(documents)} documents"
        )

        # Split the document into chunks for RAG
        split_start = time.time()
        text_splitter = CharacterTextSplitter()
        raw_chunks = text_splitter.split_texts(documents)

        # Clean chunks to handle Unicode issues
        chunks = []
        for chunk in raw_chunks:
            try:
                # Remove or replace problematic Unicode characters
                cleaned_chunk = chunk.encode("utf-8", errors="ignore").decode("utf-8")
                # Remove surrogate pairs and other problematic characters
                cleaned_chunk = "".join(
                    char for char in cleaned_chunk if ord(char) < 65536
                )
                if cleaned_chunk.strip():  # Only keep non-empty chunks
                    chunks.append(cleaned_chunk)
            except Exception as e:
                print(f"⚠️ Skipping problematic chunk: {str(e)[:100]}...")
                continue

        split_end = time.time()
        print(
            f"✂️ Text splitting and cleaning completed in {(split_end - split_start) * 1000:.1f}ms - {len(chunks)} chunks (cleaned from {len(raw_chunks)})"
        )

        # Clean up the temporary file
        Path(temp_file_path).unlink()

        # Initialize RAG components if not already done
        global vector_database, embedding_model
        embedding_start = time.time()
        if embedding_model is None:
            print("🤖 Initializing embedding model...")
            try:
                embedding_model = EmbeddingModel(api_key=api_key)
            except Exception as e:
                print(f"❌ Error initializing embedding model: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error initializing embedding model: {str(e)}",
                )

        # Create embeddings for all chunks (batch processing for efficiency)
        print(
            f"🔄 Creating embeddings for {len(chunks)} chunks using batch processing..."
        )
        batch_start = time.time()

        # Use batch processing for better performance with error handling
        try:
            embeddings = await embedding_model.async_get_embeddings(chunks)
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error creating embeddings: {error_msg}")

            # Check for specific OpenAI errors
            if "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="OpenAI rate limit exceeded. Please wait a moment and try again.",
                )
            elif "quota" in error_msg.lower():
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI quota exceeded. Please check your OpenAI account billing.",
                )
            elif "invalid" in error_msg.lower() and "api" in error_msg.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Invalid OpenAI API key. Please check your API key.",
                )
            else:
                raise HTTPException(
                    status_code=500, detail=f"Error creating embeddings: {error_msg}"
                )

        batch_end = time.time()
        print(
            f"📊 Batch embedding creation: {(batch_end - batch_start) * 1000:.1f}ms for {len(chunks)} chunks"
        )
        print(
            f"📈 Average per chunk: {((batch_end - batch_start) * 1000) / len(chunks):.1f}ms"
        )

        embedding_end = time.time()
        print(
            f"✅ Embedding creation completed in {(embedding_end - embedding_start) * 1000:.1f}ms"
        )

        # Initialize or reset vector database with new document
        db_start = time.time()
        vector_database = VectorDatabase(embedding_model=embedding_model)

        # Add all chunks and embeddings to vector database
        for chunk, embedding in zip(chunks, embeddings):
            vector_database.insert(chunk, embedding)
        db_end = time.time()
        print(f"💾 Vector database populated in {(db_end - db_start) * 1000:.1f}ms")

        total_time = time.time() - start_time
        print(
            f"🎉 Total processing time: {total_time * 1000:.1f}ms ({total_time:.1f}s)"
        )

        return {
            "status": "success",
            "filename": file.filename,
            "num_documents": len(documents),
            "num_chunks": len(chunks),
            "num_embeddings": len(embeddings),
            "message": f"Successfully processed {file.filename} and created RAG database",
            "processing_time_ms": int(total_time * 1000),
        }

    except Exception as e:
        # Clean up temp file if it exists
        if "temp_file_path" in locals():
            Path(temp_file_path).unlink(missing_ok=True)

        print(f"❌ Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/summarize-document")
@app.post("/backend/summarize-document")
async def summarize_document(request: ChatRequest):
    """
    Generate a summary and main topics for the uploaded document.

    This endpoint:
    1. Uses the existing vector database to get document content
    2. Generates a comprehensive summary using the LLM
    3. Extracts main topics and chapters
    4. Returns structured summary information

    Args:
        request (ChatRequest): Request containing API key and model selection

    Returns:
        dict: Document summary with main topics and overview
    """
    try:
        import time

        summary_start_time = time.time()
        print("🤖 Starting document summarization...")

        # Initialize OpenAI client
        client = OpenAI(api_key=request.api_key)

        # Check if we have a document loaded
        global vector_database
        if vector_database is None:
            raise HTTPException(
                status_code=400,
                detail="No document uploaded. Please upload a PDF first.",
            )

        # Smart content extraction: Look for key document sections first
        all_chunks = list(vector_database.vectors.keys())

        # Define key sections to search for (case-insensitive)
        key_sections = [
            # Table of Contents variations
            "table of contents",
            "contents",
            "toc",
            "index",
            # Abstract/Summary variations
            "abstract",
            "executive summary",
            "summary",
            "overview",
            # Introduction variations
            "introduction",
            "preface",
            "foreword",
            "about this book",
            # Book-specific sections
            "what's in this book",
            "what is in this book",
            "book overview",
            "chapter overview",
            "structure of this book",
        ]

        print("🔍 Searching for key document sections...")

        # Find chunks that contain key sections
        priority_chunks = []
        regular_chunks = []

        for chunk in all_chunks:
            chunk_lower = chunk.lower()
            is_priority = False

            # Check if chunk contains any key section indicators
            for section in key_sections:
                if section in chunk_lower:
                    priority_chunks.append(chunk)
                    is_priority = True
                    print(f"📋 Found key section: '{section}' in chunk")
                    break

            if not is_priority:
                regular_chunks.append(chunk)

        # Build final sample with intelligent selection
        sample_chunks = []
        max_chunks = 25  # Increased limit for better coverage

        # 1. Always include priority chunks (TOC, abstract, etc.)
        if priority_chunks:
            sample_chunks.extend(priority_chunks[:15])  # Up to 15 priority chunks
            print(
                f"✅ Using {len(priority_chunks[:15])} priority chunks with key sections"
            )

        # 2. Fill remaining slots with early chunks (likely intro/setup)
        remaining_slots = max_chunks - len(sample_chunks)
        if remaining_slots > 0:
            # Take early chunks that weren't already selected as priority
            early_chunks = [
                chunk
                for chunk in regular_chunks[: remaining_slots * 2]
                if chunk not in sample_chunks
            ]
            sample_chunks.extend(early_chunks[:remaining_slots])
            print(
                f"📖 Added {len(early_chunks[:remaining_slots])} early document chunks"
            )

        # If we still don't have enough content, this is likely a very short document
        if len(sample_chunks) < 5:
            sample_chunks = all_chunks[:max_chunks]
            print(f"📄 Short document: using first {len(sample_chunks)} chunks")

        # Combine sample chunks for summarization
        document_content = "\n\n".join(sample_chunks)
        print(
            f"📊 Final selection: {len(sample_chunks)} chunks out of {len(all_chunks)} total"
        )
        print(
            f"🎯 Priority sections found: {len(priority_chunks)} chunks with key structural content"
        )

        # Create an intelligent prompt that leverages structural content
        summary_prompt = f"""Analyze this document content to create a summary like you'd find on the back of a book.

IMPORTANT: The content below includes key structural sections like Table of Contents, Abstract, Introduction, or "What's in this book" sections. Pay special attention to these as they contain the document's structure and main themes.

Document Content:
{document_content}

Create a book-back-cover style summary in the following JSON format:
{{
    "summary": "A compelling 2-3 sentence description of what this document covers, like a book's back cover",
    "main_topics": [
        "Specific topic from TOC/chapters",
        "Another concrete topic covered", 
        "Third main area discussed"
    ],
    "key_sections": [
        "Chapter/Section name: What it covers",
        "Another section: Its focus",
        "Third section: Its content"
    ],
    "document_type": "Book/Manual/Guide/Research Paper/etc.",
    "suggested_questions": [
        "Specific question about topic X mentioned in the content",
        "Question about concept Y that appears in the text",
        "Question about method/process Z discussed in the document"
    ]
}}

INSTRUCTIONS:
1. Look for Table of Contents, chapter listings, or section headings to identify main_topics and key_sections
2. If you find "What's in this book" or similar sections, use that for the summary
3. Extract actual chapter/section names when available, don't make up generic ones
4. Make suggested questions specific to content actually mentioned in the text
5. Write the summary as if you're convincing someone to read this document

Be specific and concrete - use actual topics, names, and concepts from the text."""

        # Generate the summary using the LLM with error handling
        try:
            response = client.chat.completions.create(
                model=request.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analyst. Provide accurate, helpful summaries in the requested JSON format.",
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual summaries
            )
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error generating summary: {error_msg}")

            # Check for specific OpenAI errors
            if "rate limit" in error_msg.lower():
                raise HTTPException(
                    status_code=429,
                    detail="OpenAI rate limit exceeded. Please wait a moment and try again.",
                )
            elif "quota" in error_msg.lower():
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI quota exceeded. Please check your OpenAI account billing.",
                )
            elif "invalid" in error_msg.lower() and "api" in error_msg.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Invalid OpenAI API key. Please check your API key.",
                )
            else:
                raise HTTPException(
                    status_code=500, detail=f"Error generating summary: {error_msg}"
                )

        # Parse the response
        summary_content = response.choices[0].message.content

        # Try to parse as JSON, fallback to plain text if parsing fails
        try:
            import json

            summary_data = json.loads(summary_content)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a structured response from the text
            summary_data = {
                "summary": summary_content,
                "main_topics": ["Document analysis completed"],
                "key_sections": ["Content processed"],
                "document_type": "PDF Document",
                "suggested_questions": [
                    "What is this document about?",
                    "What are the main topics covered?",
                    "Can you explain the key concepts?",
                ],
            }

        summary_end_time = time.time()
        total_summary_time = summary_end_time - summary_start_time
        print(
            f"✅ Document summarization completed in {total_summary_time * 1000:.1f}ms ({total_summary_time:.1f}s)"
        )

        return {
            "status": "success",
            "summary": summary_data,
            "message": "Document summary generated successfully",
            "summary_time_ms": int(total_summary_time * 1000),
        }

    except Exception as e:
        print(f"❌ Error generating summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating summary: {str(e)}"
        )


# Entry point for running the application directly
if __name__ == "__main__":
    """
    Development server startup.
    
    This block only runs when the script is executed directly
    (not when imported as a module).
    
    Python Concepts:
    - __name__ == "__main__": Checks if script is run directly
    - Uvicorn: ASGI server for running FastAPI applications
    - Host binding: 0.0.0.0 allows connections from any IP
    - Port configuration: 8000 is the default development port
    
    For production, use a proper ASGI server like:
    - uvicorn api.app:app --host 0.0.0.0 --port 8000
    - gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.app:app
    """
    import uvicorn

    # Start the development server
    # Note: reload=False to avoid the import string warning when running directly
    uvicorn.run(
        app,
        host="0.0.0.0",  # Accept connections from any IP address
        port=8000,  # Listen on port 8000
        reload=False,  # Disabled when running directly to avoid warnings
    )
