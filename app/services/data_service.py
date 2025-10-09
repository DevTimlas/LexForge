# File: lexforge-backend/app/services/data_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.document import Document
from app.embeddings.embedding_manager import EmbeddingManager
from app.external_apis.courtlistener_api import CourtListenerAPI
import logging
from typing import List, Dict, Optional
from fastapi import UploadFile
import uuid
from datetime import datetime
import aiofiles

logger = logging.getLogger(__name__)

class DataService:
    """Service for handling legal document storage and retrieval."""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_manager = EmbeddingManager()
        self.courtlistener_api = CourtListenerAPI()

    async def store_document(self, filename: str, content: bytes, jurisdiction: str, classification: str, user_id: str, case_id: Optional[str] = None, tags: List[str] = []) -> Document:
        """Store document with metadata and embeddings in the database."""
        try:
            content_str = content.decode('utf-8', errors='ignore')
            embedding = await self.embedding_manager.generate_embedding(content_str)
            document = Document(
                id=str(uuid.uuid4()),
                filename=filename,
                file_path=f"uploads/{filename}",
                user_id=user_id,
                case_id=case_id,
                tags=tags,
                jurisdiction=jurisdiction,
                classification=classification,
                content=content_str,
                embedding=embedding,
                size=len(content),
                upload_date=datetime.utcnow()
            )
            self.db.add(document)
            await self.db.commit()
            return document
        except Exception as e:
            logger.error(f"Document storage failed: {str(e)}")
            raise

    async def get_user_documents(self, user_id: str, case_id: Optional[str] = None, classification: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Fetch user's documents from the database."""
        try:
            stmt = select(Document).where(Document.user_id == user_id)
            if case_id:
                stmt = stmt.where(Document.case_id == case_id)
            if classification:
                stmt = stmt.where(Document.classification == classification)
            stmt = stmt.offset(offset).limit(limit)
            result = await self.db.execute(stmt)
            return [{
                "id": d.id,
                "filename": d.filename,
                "file_type": d.classification,
                "size": d.size,
                "upload_date": d.upload_date,
                "classification": d.classification,
                "privilege_status": d.privilege_status,
                "processed": d.status == "processed"
            } for d in result.scalars().all()]
        except Exception as e:
            logger.error(f"Document fetch failed: {str(e)}")
            raise

    async def search_user_documents(self, user_id: str, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search user documents using semantic or keyword search."""
        try:
            query_embedding = await self.embedding_manager.generate_embedding(query)
            stmt = select(Document).where(Document.user_id == user_id)
            if filters.get("jurisdiction"):
                stmt = stmt.where(Document.jurisdiction == filters["jurisdiction"])
            if filters.get("case_id"):
                stmt = stmt.where(Document.case_id == filters["case_id"])
            if filters.get("document_type"):
                stmt = stmt.where(Document.classification == filters["document_type"])
            result = await self.db.execute(stmt)
            docs = result.scalars().all()
            results = []
            for doc in docs:
                if doc.embedding:
                    similarity = await self.embedding_manager.compare_embeddings(query_embedding, doc.embedding)
                    results.append({
                        "id": doc.id,
                        "title": doc.title or doc.filename,
                        "snippet": doc.content[:200] if doc.content else "",
                        "citation": doc.citation or "N/A",
                        "relevance": similarity,
                        "source": "local_database"
                    })
            return sorted(results, key=lambda x: x["relevance"], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Document search failed: {str(e)}")
            raise

    async def save_uploaded_file(self, file: UploadFile, doc_id: str, user_id: str) -> str:
        """Save uploaded file to disk."""
        file_path = f"uploads/{doc_id}_{file.filename}"
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())
        return file_path

    async def create_document_record(self, doc_id: str, filename: str, file_path: str, user_id: str, case_id: Optional[str], tags: List[str], jurisdiction: Optional[str]) -> Dict:
        """Create document record in the database."""
        try:
            content = await self.extract_document_content(file_path)
            embedding = await self.embedding_manager.generate_embedding(content)
            document = Document(
                id=doc_id,
                filename=filename,
                file_path=file_path,
                user_id=user_id,
                case_id=case_id,
                tags=tags,
                jurisdiction=jurisdiction,
                content=content,
                embedding=embedding,
                size=len(content.encode('utf-8')),
                upload_date=datetime.utcnow()
            )
            self.db.add(document)
            await self.db.commit()
            return {
                "id": document.id,
                "filename": document.filename,
                "file_type": document.classification or "unknown",
                "size": document.size,
                "upload_date": document.upload_date,
                "classification": document.classification or "pending",
                "privilege_status": document.privilege_status or "pending",
                "processed": document.status == "processed"
            }
        except Exception as e:
            logger.error(f"Document record creation failed: {str(e)}")
            raise

    async def extract_document_content(self, file_path: str) -> str:
        """Extract text content from a file."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Content extraction failed for {file_path}: {str(e)}")
            raise

    async def update_document_processing_results(self, doc_id: str, classification: str, privilege_analysis: str, content: str):
        """Update document with processing results."""
        try:
            result = await self.db.execute(select(Document).where(Document.id == doc_id))
            document = result.scalars().first()
            if not document:
                raise ValueError("Document not found")
            document.classification = classification
            document.privilege_status = privilege_analysis
            document.content = content
            document.status = "processed"
            await self.db.commit()
        except Exception as e:
            logger.error(f"Update document processing failed: {str(e)}")
            raise

    async def generate_document_embeddings(self, doc_id: str, content: str):
        """Generate and store embeddings for a document."""
        try:
            embedding = await self.embedding_manager.generate_embedding(content)
            result = await self.db.execute(select(Document).where(Document.id == doc_id))
            document = result.scalars().first()
            if not document:
                raise ValueError("Document not found")
            document.embedding = embedding
            await self.db.commit()
        except Exception as e:
            logger.error(f"Embedding generation failed for {doc_id}: {str(e)}")
            raise

    async def get_document_details(self, document_id: str, user_id: str) -> Dict:
        """Get detailed document information."""
        try:
            result = await self.db.execute(select(Document).where(Document.id == document_id, Document.user_id == user_id))
            document = result.scalars().first()
            if not document:
                raise ValueError("Document not found")
            return {
                "id": document.id,
                "filename": document.filename,
                "file_type": document.classification,
                "size": document.size,
                "upload_date": document.upload_date,
                "classification": document.classification,
                "privilege_status": document.privilege_status,
                "processed": document.status == "processed",
                "content": document.content,
                "jurisdiction": document.jurisdiction,
                "citation": document.citation
            }
        except Exception as e:
            logger.error(f"Document details fetch failed: {str(e)}")
            raise

    async def get_document_file_info(self, document_id: str, user_id: str) -> Dict:
        """Get file info for downloading a document."""
        try:
            result = await self.db.execute(select(Document).where(Document.id == document_id, Document.user_id == user_id))
            document = result.scalars().first()
            if not document:
                raise ValueError("Document not found")
            return {"file_path": document.file_path, "filename": document.filename}
        except Exception as e:
            logger.error(f"Document file info fetch failed: {str(e)}")
            raise

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and associated data."""
        try:
            result = await self.db.execute(select(Document).where(Document.id == document_id, Document.user_id == user_id))
            document = result.scalars().first()
            if not document:
                return False
            await self.db.delete(document)
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Document deletion failed: {str(e)}")
            raise

    async def update_document_error(self, doc_id: str, error: str):
        """Update document status with error."""
        try:
            result = await self.db.execute(select(Document).where(Document.id == doc_id))
            document = result.scalars().first()
            if not document:
                raise ValueError("Document not found")
            document.status = f"error: {error}"
            await self.db.commit()
        except Exception as e:
            logger.error(f"Update document error failed: {str(e)}")
            raise