# File: lexforge-backend/app/services/embedding_service.py
# This file defines the EmbeddingService for generating embeddings.

from app.embeddings.embedding_manager import EmbeddingManager
import logging

# Configure logging
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings for legal documents."""
    def __init__(self):
        self.embedding_manager = EmbeddingManager()

    async def generate_document_embedding(self, text: str):
        """Generate embedding for legal document using the manager."""
        try:
            return await self.embedding_manager.generate_embedding(text)
        except Exception as e:
            logger.error(f"Embedding service failed: {str(e)}")
            raise