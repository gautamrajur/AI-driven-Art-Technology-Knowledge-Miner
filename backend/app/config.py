"""
Configuration settings for the Art & Technology Knowledge Miner API.
"""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    api_title: str = "Art & Technology Knowledge Miner API"
    api_version: str = "0.1.0"
    api_description: str = "API for mining and exploring art-technology intersections"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database settings
    chroma_persist_directory: str = "./chroma_db"
    collection_name: str = "art_tech_knowledge"
    
    # Pipeline settings
    pipeline_config_path: str = "pipeline/config/terms.yaml"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    summarization_model: str = "facebook/bart-large-cnn"
    
    # Background task settings
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # CORS settings
    cors_origins: list = ["*"]  # Configure appropriately for production
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # OpenAI settings (optional)
    openai_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
