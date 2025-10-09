# File: lexforge-backend/app/embeddings/models.py
# This file defines configuration models for embeddings.

from pydantic import BaseModel

class EmbeddingConfig(BaseModel):
    """Configuration for embedding models."""
    model_name: str = "all-MiniLM-L6-v2"
    max_length: int = 512