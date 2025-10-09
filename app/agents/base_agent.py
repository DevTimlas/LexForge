from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import os
import aiofiles
from fastapi import UploadFile
import logging

class BaseAgent(ABC):
    """Enhanced base class for all LexForge agents"""
    def __init__(self, upload_dir: str = "uploads"):
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.capabilities: List[str] = []
        self.status = "active"
        self.execution_history: List[Dict[str, Any]] = []
        self.upload_dir = upload_dir
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle synchronous requests"""
        pass

    async def handle_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle asynchronous requests (default implementation)"""
        return self.handle(request)

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.capabilities

    def get_status(self) -> Dict[str, Any]:
        """Return agent status information"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
            "executions": len(self.execution_history)
        }

    async def _log_execution(self, request: Dict[str, Any], result: Dict[str, Any], duration: float):
        """Log execution for monitoring (async)"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request": request,
            "result_keys": list(result.keys()),
            "duration_seconds": duration,
            "status": "success" if "error" not in result else "error"
        }
        self.execution_history.append(log_entry)
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        # Async log to file
        try:
            async with aiofiles.open("agent_execution.log", "a") as f:
                await f.write(f"{log_entry}\n")
        except Exception as e:
            self.logger.error(f"Failed to log execution: {str(e)}")

    async def _create_provenance(self, sources: List[str], method: str, confidence: float = 1.0) -> Dict[str, Any]:
        """Create provenance information for results (async)"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "sources": sources,
            "method": method,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def save_uploaded_file(self, file: UploadFile, doc_id: str, user_id: str) -> str:
        """Save uploaded file to disk"""
        try:
            user_dir = os.path.join(self.upload_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            filename = f"{doc_id}_{file.filename}"
            file_path = os.path.join(user_dir, filename)
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to save file {file.filename}: {str(e)}")
            raise ValueError(f"Failed to save file: {str(e)}")

    async def create_document_record(
        self,
        doc_id: str,
        filename: str,
        file_path: str,
        user_id: str,
        case_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create document record in database"""
        # Mock implementation - replace with actual DB operations
        try:
            return {
                "id": doc_id,
                "filename": filename,
                "file_path": file_path,
                "user_id": user_id,
                "case_id": case_id,
                "tags": tags or [],
                "upload_date": datetime.utcnow(),
                "status": "uploaded",
                "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
        except Exception as e:
            self.logger.error(f"Failed to create document record: {str(e)}")
            raise

    async def process_upload(self, file: UploadFile, user_id: str, session_id: str) -> Dict[str, Any]:
        """Process uploaded file for analysis"""
        try:
            doc_id = str(uuid.uuid4())
            file_path = await self.save_uploaded_file(file, doc_id, user_id)
            return {
                "id": doc_id,
                "filename": file.filename,
                "path": file_path,
                "session_id": session_id,
                "processed_at": datetime.utcnow()
            }
        except Exception as e:
            self.logger.error(f"Failed to process upload: {str(e)}")
            raise ValueError(f"Upload processing failed: {str(e)}")

    async def extract_document_content(self, file_path: str) -> str:
        """Extract text content from document"""
        # Mock implementation - integrate with document processing libraries (e.g., PyPDF2, Tika)
        try:
            return "Extracted document content would appear here"
        except Exception as e:
            self.logger.error(f"Failed to extract content from {file_path}: {str(e)}")
            raise

    async def update_document_processing_results(
        self,
        doc_id: str,
        classification: Dict[str, Any],
        privilege_analysis: Dict[str, Any],
        content: str
    ):
        """Update document with processing results"""
        # Mock implementation - replace with actual DB update
        try:
            pass
        except Exception as e:
            self.logger.error(f"Failed to update document {doc_id}: {str(e)}")
            raise

    async def generate_document_embeddings(self, doc_id: str, content: str):
        """Generate embeddings for document search"""
        # Mock implementation - integrate with embedding service (e.g., HuggingFace, OpenAI)
        try:
            pass
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings for {doc_id}: {str(e)}")
            raise

    async def update_document_error(self, doc_id: str, error: str):
        """Update document with error status"""
        # Mock implementation - replace with actual DB update
        try:
            pass
        except Exception as e:
            self.logger.error(f"Failed to update error for {doc_id}: {str(e)}")
            raise

    async def get_user_documents(
        self,
        user_id: str,
        case_id: Optional[str] = None,
        classification: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user documents with filtering"""
        # Mock data - replace with actual DB query
        try:
            return [
                {
                    "id": "doc1",
                    "filename": "contract.pdf",
                    "classification": "Contract",
                    "upload_date": datetime.utcnow(),
                    "size": 1024000,
                    "processed": True
                }
            ]
        except Exception as e:
            self.logger.error(f"Failed to get user documents: {str(e)}")
            raise

    async def get_document_details(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed document information"""
        # Mock implementation
        try:
            return {
                "id": document_id,
                "filename": "sample.pdf",
                "user_id": user_id,
                "status": "processed",
                "classification": "Legal Brief",
                "privilege_status": "Not Privileged",
                "upload_date": datetime.utcnow()
            }
        except Exception as e:
            self.logger.error(f"Failed to get document details for {document_id}: {str(e)}")
            raise

    async def analyze_document(
        self,
        document_id: str,
        analysis_type: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform specific analysis on document"""
        try:
            return {
                "analysis_type": analysis_type,
                "results": f"Analysis results for {document_id}",
                "confidence": 0.95
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze document {document_id}: {str(e)}")
            raise

    async def get_document_file_info(self, document_id: str, user_id: str) -> Optional[Dict[str, str]]:
        """Get file information for download"""
        try:
            return {
                "filename": "sample.pdf",
                "file_path": "/path/to/file.pdf"
            }
        except Exception as e:
            self.logger.error(f"Failed to get file info for {document_id}: {str(e)}")
            raise

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document and cleanup"""
        try:
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise

    async def search_user_documents(
        self,
        user_id: str,
        query: str,
        filters: Dict[str, Any],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search documents with semantic search"""
        # Mock search results
        try:
            return [
                {
                    "id": "doc1",
                    "filename": "relevant_case.pdf",
                    "relevance_score": 0.92,
                    "snippet": "Relevant text snippet..."
                }
            ]
        except Exception as e:
            self.logger.error(f"Failed to search documents: {str(e)}")
            raise