# File: lexforge-backend/app/api/v1/documents.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import aiofiles
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.data_service import DataService
from app.services.user_service import UserService
from app.agents.classification_agent import ClassificationAgent
from app.agents.privilege_firewall_agent import PrivilegeFirewallAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_type: str
    size: int
    upload_date: datetime
    classification: str
    privilege_status: str
    processed: bool

class DocumentAnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str
    options: Optional[Dict[str, Any]] = None

class SearchQuery(BaseModel):
    query: str
    jurisdiction: Optional[str] = None
    case_id: Optional[str] = None
    document_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 20

@router.post("/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    case_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    jurisdiction: Optional[str] = Form(None),
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process legal documents."""
    try:
        data_service = DataService(db)
        uploaded_docs = []
        for file in files:
            # Validate file type
            if not data_service.is_valid_file_type(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not supported: {file.filename}"
                )
            # Generate document ID
            doc_id = str(uuid.uuid4())
            # Save file
            file_path = await data_service.save_uploaded_file(
                file, doc_id, current_user.id
            )
            # Create document record
            doc_metadata = await data_service.create_document_record(
                doc_id,
                file.filename,
                file_path,
                current_user.id,
                case_id,
                tags.split(",") if tags else [],
                jurisdiction
            )
            uploaded_docs.append(doc_metadata)
            # Schedule background processing
            background_tasks.add_task(
                process_document_pipeline,
                doc_id,
                file_path,
                current_user.id,
                db
            )
        return {
            "uploaded_documents": uploaded_docs,
            "message": f"Successfully uploaded {len(files)} documents"
        }
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_document_pipeline(doc_id: str, file_path: str, user_id: str, db: AsyncSession):
    """Background task for document processing pipeline."""
    try:
        data_service = DataService(db)
        classification_agent = ClassificationAgent()
        privilege_agent = PrivilegeFirewallAgent()
        # Extract text and metadata
        content = await data_service.extract_document_content(file_path)
        # Classify document
        classification = await classification_agent.classify_document(content, doc_id)
        # Check for privileged content
        privilege_analysis = await privilege_agent.scan_document(content, doc_id)
        # Update document record
        await data_service.update_document_processing_results(
            doc_id,
            classification,
            privilege_analysis,
            content
        )
        # Generate embeddings for search
        await data_service.generate_document_embeddings(doc_id, content)
    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {str(e)}")
        await data_service.update_document_error(doc_id, str(e))

@router.get("/list")
async def list_user_documents(
    case_id: Optional[str] = None,
    classification: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of user documents with filtering."""
    try:
        data_service = DataService(db)
        documents = await data_service.get_user_documents(
            current_user.id,
            case_id=case_id,
            classification=classification,
            limit=limit,
            offset=offset
        )
        return {
            "documents": documents,
            "total": len(documents),
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/{document_id}")
async def get_document_details(
    document_id: str,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed document information."""
    try:
        data_service = DataService(db)
        document = await data_service.get_document_details(document_id, current_user.id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: str,
    analysis_request: DocumentAnalysisRequest,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform specific analysis on document."""
    try:
        data_service = DataService(db)
        document = await data_service.get_document_details(document_id, current_user.id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        analysis_result = await data_service.analyze_document(
            document_id,
            analysis_request.analysis_type,
            analysis_request.options or {}
        )
        return {
            "document_id": document_id,
            "analysis_type": analysis_request.analysis_type,
            "results": analysis_result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download original document."""
    try:
        data_service = DataService(db)
        file_info = await data_service.get_document_file_info(document_id, current_user.id)
        if not file_info:
            raise HTTPException(status_code=404, detail="Document not found")
        async def file_stream():
            async with aiofiles.open(file_info["file_path"], "rb") as f:
                while chunk := await f.read(8192):
                    yield chunk
        return StreamingResponse(
            file_stream(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_info['filename']}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete document and associated data."""
    try:
        data_service = DataService(db)
        success = await data_service.delete_document(document_id, current_user.id)
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.post("/search")
async def search_documents(
    search_query: SearchQuery,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search through user documents and external legal databases using semantic search."""
    try:
        data_service = DataService(db)
        retrieval_agent = RetrievalAgent()
        # Perform semantic search across local and external documents
        search_results = await retrieval_agent.search(
            query=search_query.query,
            jurisdiction=search_query.jurisdiction,
            db=db,
            filters={
                "user_id": current_user.id,
                "case_id": search_query.case_id,
                "document_type": search_query.document_type,
                "date_from": search_query.date_from,
                "date_to": search_query.date_to
            },
            limit=search_query.limit
        )
        return {
            "query": search_query.query,
            "results": search_results,
            "total_found": len(search_results)
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")