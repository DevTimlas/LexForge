# File: lexforge-backend/scripts/update_embeddings.py
import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select

# Ensure project root is in sys.path for "app.*" imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.document import Document
from app.embeddings.embedding_manager import EmbeddingManager


async def update_embeddings():
    engine = create_async_engine("postgresql+asyncpg://mac@localhost:5432/lexforge")
    embedding_manager = EmbeddingManager()

    async with AsyncSession(engine) as db:
        result = await db.execute(select(Document).where(Document.embedding.is_(None)))
        docs = result.scalars().all()

        for doc in docs:
            if doc.content:
                doc.embedding = await embedding_manager.generate_embedding(doc.content)

        await db.commit()


if __name__ == "__main__":
    asyncio.run(update_embeddings())
