from pathlib import Path
from typing import Iterable, List

import PyPDF2


class TextFileLoader:
    """
    Load plain-text documents from a single file or an entire directory.

    This class is the first step in the RAG (Retrieval-Augmented Generation) pipeline.
    It handles reading text files (.txt) from the filesystem and preparing them
    for further processing like chunking and embedding.

    Key RAG Concepts:
    - Document Loading: Getting raw text from files into memory
    - Text Preprocessing: Converting files into strings for processing
    """

    def __init__(self, path: str, encoding: str = "utf-8"):
        """
        Initialize the TextFileLoader.

        Args:
            path (str): File path or directory path to load documents from
            encoding (str): Text encoding to use when reading files (default: utf-8)

        Python Concepts:
        - Path: Using pathlib for cross-platform file path handling
        - Type hints: List[str] means "a list containing strings"
        - Default parameters: encoding defaults to "utf-8" if not specified
        """
        self.path = Path(
            path
        )  # Convert string path to Path object for easier manipulation
        self.encoding = encoding  # Store encoding for file reading
        self.documents: List[
            str
        ] = []  # Initialize empty list to store loaded documents

    def load(self) -> None:
        """
        Populate self.documents from the configured path.

        This method automatically detects whether the path is a file or directory
        and loads accordingly. It's the main entry point for loading documents.

        Python Concepts:
        - None return type: This method modifies the object but doesn't return anything
        - Private method calls: Uses _iter_documents() (private method indicated by _)
        """
        self.documents = list(self._iter_documents())

    def load_file(self) -> None:
        """
        Load a single file specified by self.path.

        Use this when you know you're loading exactly one text file.
        """
        self.documents = [self._read_text_file(self.path)]

    def load_directory(self) -> None:
        """
        Load all text files contained within self.path.

        Use this when you want to load all .txt files from a directory.
        Files are loaded recursively (including subdirectories).
        """
        self.documents = list(self._iter_directory(self.path))

    def load_documents(self) -> List[str]:
        """
        Convenience wrapper that loads and returns the documents in one call.

        Returns:
            List[str]: List of document contents as strings

        This is useful when you want to load documents and get them back immediately
        without having to call load() and then access self.documents separately.
        """
        self.load()
        return self.documents

    def _iter_documents(self) -> Iterable[str]:
        """
        Private method that determines how to load documents based on path type.

        Python Concepts:
        - Private method: Leading underscore indicates this is for internal use
        - Iterable[str]: Returns an iterator that yields strings
        - yield: Makes this a generator function (memory efficient)
        - yield from: Delegates to another generator

        RAG Concepts:
        - Path detection: Automatically handles files vs directories
        - Error handling: Validates input before processing
        """
        if self.path.is_dir():
            # If it's a directory, load all .txt files from it
            yield from self._iter_directory(self.path)
        elif self.path.is_file() and self.path.suffix.lower() == ".txt":
            # If it's a single .txt file, load just that file
            yield self._read_text_file(self.path)
        else:
            # If it's neither a directory nor a .txt file, raise an error
            raise ValueError(
                f"Provided path must be a directory or a .txt file: {self.path}"
            )

    def _iter_directory(self, directory: Path) -> Iterable[str]:
        """
        Private method to recursively find and load all .txt files in a directory.

        Args:
            directory (Path): Directory path to search

        Yields:
            str: Content of each text file found

        Python Concepts:
        - rglob: Recursive glob - searches subdirectories too
        - sorted(): Ensures consistent ordering of files
        - Generator: Uses yield for memory-efficient iteration
        """
        for entry in sorted(directory.rglob("*.txt")):
            if entry.is_file():
                yield self._read_text_file(entry)

    def _read_text_file(self, file_path: Path) -> str:
        """
        Private method to read the contents of a single text file.

        Args:
            file_path (Path): Path to the text file to read

        Returns:
            str: Complete contents of the file

        Python Concepts:
        - Context manager: 'with' statement ensures file is properly closed
        - File encoding: Uses the encoding specified in __init__
        - Exception handling: Any file reading errors will bubble up
        """
        with file_path.open("r", encoding=self.encoding) as file_handle:
            return file_handle.read()


class CharacterTextSplitter:
    """
    Naively split long strings into overlapping character chunks.

    This is a critical component in RAG systems. Large documents need to be split
    into smaller chunks because:
    1. LLMs have token limits (can't process infinite text)
    2. Embeddings work better on focused, coherent text segments
    3. Retrieval is more precise with smaller, relevant chunks

    Key RAG Concepts:
    - Chunking: Breaking documents into smaller, manageable pieces
    - Overlap: Preserving context between adjacent chunks
    - Character-based: Simple but effective splitting strategy
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the text splitter with chunking parameters.

        Args:
            chunk_size (int): Maximum number of characters per chunk
            chunk_overlap (int): Number of characters to overlap between chunks

        The overlap is important because it ensures that concepts or sentences
        that span chunk boundaries aren't lost. For example, if a sentence
        is split across two chunks, the overlap ensures both chunks contain
        the complete sentence.

        Python Concepts:
        - Input validation: Checks that parameters make sense
        - Default parameters: Reasonable defaults for most use cases
        """
        if chunk_size <= chunk_overlap:
            raise ValueError("Chunk size must be greater than chunk overlap")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        """
        Split text into chunks preserving the configured overlap.

        Args:
            text (str): The text to split into chunks

        Returns:
            List[str]: List of text chunks with overlap

        How it works:
        - If chunk_size=1000 and chunk_overlap=200, then step=800
        - First chunk: characters 0-1000
        - Second chunk: characters 800-1800 (overlaps with first chunk by 200 chars)
        - Third chunk: characters 1600-2600, etc.

        Python Concepts:
        - List comprehension: Compact way to create a list
        - String slicing: text[i:i+chunk_size] extracts a substring
        - range(start, stop, step): Creates sequence of positions
        """
        step = self.chunk_size - self.chunk_overlap
        return [text[i : i + self.chunk_size] for i in range(0, len(text), step)]

    def split_texts(self, texts: List[str]) -> List[str]:
        """
        Split multiple texts and flatten the resulting chunks.

        Args:
            texts (List[str]): List of documents to split

        Returns:
            List[str]: Flattened list of all chunks from all documents

        This is useful when you have multiple documents and want to process
        them all into chunks for embedding and storage in a vector database.

        Python Concepts:
        - List.extend(): Adds all items from another list
        - Type hints: Explicit input and output types for clarity
        """
        chunks: List[str] = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


class PDFLoader:
    """
    Extract text from PDF files stored at a path.

    This class handles PDF document loading for RAG systems. PDFs are a common
    format for documents, reports, and research papers that need to be processed
    for question-answering systems.

    Key RAG Concepts:
    - PDF Processing: Converting PDF format to plain text
    - Text Extraction: Getting readable content from formatted documents
    - Document Ingestion: Preparing PDFs for embedding and retrieval

    Technical Note:
    Uses PyPDF2 library for PDF parsing. Some PDFs (especially scanned images)
    may not extract well and might need OCR (Optical Character Recognition).
    """

    def __init__(self, path: str):
        """
        Initialize the PDF loader.

        Args:
            path (str): File path or directory path containing PDF files

        Python Concepts:
        - Similar structure to TextFileLoader for consistency
        - Path handling for cross-platform compatibility
        """
        self.path = Path(path)
        self.documents: List[str] = []

    def load(self) -> None:
        """
        Populate self.documents from the configured path.

        Identical interface to TextFileLoader for consistency.
        """
        self.documents = list(self._iter_documents())

    def load_file(self) -> None:
        """
        Load a single PDF specified by self.path.
        """
        self.documents = [self._read_pdf(self.path)]

    def load_directory(self) -> None:
        """
        Load all PDF files contained within self.path.

        Recursively searches for .pdf files in the directory.
        """
        self.documents = list(self._iter_directory(self.path))

    def load_documents(self) -> List[str]:
        """
        Convenience wrapper returning the loaded documents.

        Returns:
            List[str]: List of extracted PDF contents as strings
        """
        self.load()
        return self.documents

    def _iter_documents(self) -> Iterable[str]:
        """
        Private method to determine how to load PDFs based on path type.

        Similar logic to TextFileLoader but for .pdf files instead of .txt files.
        """
        if self.path.is_dir():
            yield from self._iter_directory(self.path)
        elif self.path.is_file() and self.path.suffix.lower() == ".pdf":
            yield self._read_pdf(self.path)
        else:
            raise ValueError(
                f"Provided path must be a directory or a .pdf file: {self.path}"
            )

    def _iter_directory(self, directory: Path) -> Iterable[str]:
        """
        Private method to recursively find and load all PDF files in a directory.

        Args:
            directory (Path): Directory path to search

        Yields:
            str: Extracted text content from each PDF found
        """
        for entry in sorted(directory.rglob("*.pdf")):
            if entry.is_file():
                yield self._read_pdf(entry)

    def _read_pdf(self, file_path: Path) -> str:
        """
        Private method to extract text from a single PDF file.

        Args:
            file_path (Path): Path to the PDF file to read

        Returns:
            str: Complete text content extracted from the PDF

        Python Concepts:
        - Binary file reading: PDFs are binary files, so we use "rb" mode
        - List comprehension with fallback: Uses "" if page.extract_text() returns None
        - String joining: Combines all pages with newlines between them

        RAG Concepts:
        - Text extraction: Converting structured PDF to plain text
        - Page handling: Processes each page separately then combines
        - Error resilience: Handles pages that might not extract properly
        """
        with file_path.open("rb") as file_handle:
            pdf_reader = PyPDF2.PdfReader(file_handle)
            extracted_pages = [page.extract_text() or "" for page in pdf_reader.pages]
        return "\n".join(extracted_pages)


if __name__ == "__main__":
    """
    Example usage demonstrating the complete text processing pipeline.
    
    This shows how to:
    1. Load a text file
    2. Split it into chunks
    3. Examine the results
    
    Python Concepts:
    - __name__ == "__main__": Code that only runs when script is executed directly
    - This is a common Python pattern for example/test code
    """
    # Step 1: Load a text document
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()

    # Step 2: Split the loaded documents into chunks
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)

    # Step 3: Display information about the chunks
    print(len(chunks))  # Total number of chunks created
    print(chunks[0])  # First chunk
    print("--------")
    print(chunks[1])  # Second chunk (should overlap with first)
    print("--------")
    print(chunks[-2])  # Second-to-last chunk
    print("--------")
    print(chunks[-1])  # Last chunk
