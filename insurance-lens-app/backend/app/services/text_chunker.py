"""Simple text chunking using LangChain's RecursiveCharacterTextSplitter."""

from typing import List, Dict

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.models.internal import TextChunk


# Chunking strategy configurations
CHUNKING_STRATEGIES = {
    "semantic": {
        "chunk_size": 512,
        "chunk_overlap": 50,
        "separators": ["\n\n", "\n", ". ", " ", ""],
        "description": "Fixed-size chunks with standard separators"
    },
    "paragraph": {
        "chunk_size": 1000,
        "chunk_overlap": 100,
        "separators": ["\n\n\n", "\n\n", ".\n", "\n", ". ", " "],
        "description": "Larger chunks respecting paragraph boundaries"
    }
}


def chunk_text(
    text_data: List[Dict], 
    filename: str, 
    strategy: str = "semantic"
) -> List[TextChunk]:
    """
    Split text into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        text_data: List of page dictionaries with text and page numbers
        filename: Original filename for metadata
        strategy: Chunking strategy name ("semantic" or "paragraph")
        
    Returns:
        List of TextChunk objects with metadata
        
    Raises:
        ValueError: If strategy is unknown
    """
    if strategy not in CHUNKING_STRATEGIES:
        available = ", ".join(CHUNKING_STRATEGIES.keys())
        raise ValueError(f"Unknown strategy '{strategy}'. Available: {available}")
    
    config = CHUNKING_STRATEGIES[strategy]
    tokenizer = tiktoken.get_encoding(settings.pdf_processing.encoding_type)
    
    # Create text splitter with strategy configuration
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        length_function=lambda text: len(tokenizer.encode(text)),
        separators=config["separators"]
    )
    
    # Combine all text
    all_text = "\n\n".join([page["text"] for page in text_data])
    
    # Split into chunks
    langchain_chunks = text_splitter.create_documents([all_text])
    
    # Convert to TextChunk objects with page mapping
    chunks = []
    for i, lc_chunk in enumerate(langchain_chunks):
        chunk_start = all_text.find(lc_chunk.page_content)
        page_num = _find_page_number(text_data, chunk_start)
        
        chunks.append(TextChunk(
            id=f"{filename}_{strategy}_{i}",
            text=lc_chunk.page_content,
            page=page_num,
            chunk_index=i,
            token_count=len(tokenizer.encode(lc_chunk.page_content)),
            start_char=None,
            end_char=None
        ))
    
    return chunks


def _find_page_number(text_data: List[Dict], char_offset: int) -> int:
    """Find page number for a character offset in combined text."""
    current_char_count = 0
    for page_data in text_data:
        page_len = len(page_data["text"])
        if char_offset >= current_char_count and char_offset < current_char_count + page_len:
            return page_data["page"]
        current_char_count += page_len + 2  # +2 for "\n\n" separator
    
    return text_data[0]["page"] if text_data else 1

