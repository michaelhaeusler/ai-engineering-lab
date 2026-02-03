"""PDF processing service for extracting and chunking text from German insurance policies."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import tiktoken
import pypdf
import pymupdf as fitz
from app.core.config import PDFProcessingConfig
from app.models.internal import TextChunk, ProcessedDocument
from app.services.text_chunker import chunk_text


class PDFProcessor:
    """Handles PDF text extraction and chunking for German insurance policies."""
    
    def __init__(self, config: PDFProcessingConfig, chunking_strategy: str = "semantic"):
        """
        Initialize PDF processor with configuration and chunking strategy.
        
        Args:
            config: PDF processing configuration
            chunking_strategy: Name of chunking strategy to use ("semantic" or "paragraph")
        """
        self.config = config
        self.tokenizer = tiktoken.get_encoding(config.encoding_type)
        self.chunking_strategy = chunking_strategy
    
    def extract_text(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF with page information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries with page number and text content
        """
        text_data = []
        
        try:
            # Try pymupdf first (better for complex PDFs)
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():  # Only add non-empty pages
                    text_data.append({
                        "page": page_num + 1,
                        "text": text.strip()
                    })
            doc.close()
            
        except Exception:
            # Fallback to pypdf if pymupdf fails
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():  # Only add non-empty pages
                        text_data.append({
                            "page": page_num + 1,
                            "text": text.strip()
                        })
        
        return text_data
    
    def chunk_text_method(self, text_data: List[Dict], filename: str) -> List[TextChunk]:
        """
        Split text into chunks using the configured chunking strategy.
        
        Args:
            text_data: List of page dictionaries with text
            filename: Original filename for metadata
            
        Returns:
            List of TextChunk Pydantic models with full metadata
        """
        return chunk_text(text_data, filename, self.chunking_strategy)
    
    def process_pdf(self, pdf_path: str, filename: str, policy_id: str) -> ProcessedDocument:
        """
        Main method: extract text and chunk a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            filename: Original filename
            policy_id: Unique identifier for the policy
            
        Returns:
            ProcessedDocument Pydantic model with all chunks and metadata
        """
        # Extract text with page information
        text_data = self.extract_text(pdf_path)
        
        if not text_data:
            raise ValueError("No text could be extracted from the PDF")
        
        # Chunk the text (returns List[TextChunk])
        chunks = self.chunk_text_method(text_data, filename)
        
        # Create and return ProcessedDocument
        return ProcessedDocument(
            policy_id=policy_id,
            filename=filename,
            total_pages=len(text_data),
            chunks=chunks,
            total_chunks=len(chunks),
            processing_metadata={
                "processing_date": datetime.now().isoformat(),
                "encoding_type": self.config.encoding_type,
                "chunking_strategy": self.chunking_strategy,
                "chunk_size": self.config.chunk_size,
                "overlap_size": self.config.overlap_size
            }
        )
