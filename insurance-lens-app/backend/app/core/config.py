"""Application configuration settings."""

import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PDFProcessingConfig(BaseModel):
    """Configuration for PDF text extraction and chunking."""
    chunk_size: int = Field(default=500, ge=100, le=2000, description="Token size for text chunks")
    overlap_size: int = Field(default=50, ge=0, le=200, description="Token overlap between chunks")
    encoding_type: str = Field(default="cl100k_base", description="Tiktoken encoding type")
    max_file_size: int = Field(default=50_000_000, description="Max PDF file size in bytes")


class VectorStoreConfig(BaseModel):
    """Configuration for vector storage and retrieval."""
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    collection_prefix: str = Field(default="policy_", description="Qdrant collection name prefix")
    similarity_threshold: float = Field(default=0.4, ge=0.0, le=1.0, description="Minimum similarity for retrieval")
    max_results: int = Field(default=3, ge=1, le=20, description="Max results to return")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    debug: bool = Field(default=True, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4.1-nano", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.3, env="LLM_TEMPERATURE")
    llm_output_language: str = Field(default="German", env="LLM_OUTPUT_LANGUAGE")

    # Cohere Configuration
    cohere_api_key: str = Field(..., env="COHERE_API_KEY")

    # Tavily Web Search
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")

    # Qdrant Vector Database
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    qdrant_api_key: str = Field(default="", env="QDRANT_API_KEY")

    # LangSmith (Optional)
    langchain_tracing_v2: bool = Field(default=True, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field(default="", env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="insurancelens", env="LANGCHAIN_PROJECT")

    # File Upload Settings
    max_upload_size: int = Field(default=50000000, env="MAX_UPLOAD_SIZE")  # 50MB
    upload_folder: str = Field(default="data/uploads", env="UPLOAD_FOLDER")

    # Processing Configuration
    pdf_processing: PDFProcessingConfig = Field(default_factory=PDFProcessingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


    @property
    def upload_folder_path(self) -> Path:
        """
        Get upload folder as absolute Path object.

        Creates the directory if it doesn't exist.

        Returns:
            Path: Absolute path to the upload directory
        """
        # Make it relative to the backend directory
        base_dir = Path(__file__).parent.parent.parent  # Go up to backend/
        upload_path = base_dir / self.upload_folder

        # Create directory if it doesn't exist
        upload_path.mkdir(parents=True, exist_ok=True)

        return upload_path.resolve()  # Return absolute path

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
