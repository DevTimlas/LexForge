# File: lexforge-backend/app/embeddings/embedding_manager.py
from sentence_transformers import SentenceTransformer
import logging
from typing import List
from numpy import dot
from numpy.linalg import norm

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manager for generating and comparing embeddings for legal documents."""
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for legal document text."""
        try:
            embedding = self.model.encode(text, convert_to_tensor=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    async def compare_embeddings(self, query_embedding: List[float], doc_embedding: List[float]) -> float:
        """Compare query and document embeddings using cosine similarity."""
        try:
            return dot(query_embedding, doc_embedding) / (norm(query_embedding) * norm(doc_embedding))
        except Exception as e:
            logger.error(f"Embedding comparison failed: {str(e)}")
            raise