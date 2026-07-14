"""Configuration management for the RAG application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # API
    API_VERSION: str = "v1"
    API_TITLE: str = "Exam RAG Portal API"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://rag_user:rag_password_dev@localhost:5432/rag_db"
    )
    DATABASE_ECHO: bool = DEBUG

    # Vector Database
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY", None)

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY", None)
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY", None)

    # Embeddings
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDINGS_DIMENSION: int = 384
    BATCH_SIZE_EMBEDDINGS: int = 32

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_UPLOAD_EXTENSIONS: list = ["pdf", "docx", "txt", "pptx", "xlsx"]
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "./uploads")

    # Chunking
    CHUNK_SIZE: int = 500  # tokens
    CHUNK_OVERLAP: int = 50  # tokens

    # Retrieval
    TOP_K_RETRIEVAL: int = 5
    MIN_SIMILARITY_SCORE: float = 0.3

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    if ENVIRONMENT == "production":
        ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

    class Config:
        case_sensitive = True


settings = Settings()
