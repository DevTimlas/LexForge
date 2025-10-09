# File: lexforge-backend/app/api/v1/cases.py
# This file defines case-related API endpoints for the LexForge platform.
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.user_service import UserService
from app.db.session import get_db
import logging
import os
from datetime import datetime
from app.utils.security import generate_id
from pydantic import BaseModel
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(tags=["cases"])

@router.post("/create")
async def create_case(
    case_data: dict,
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new case with a generated ID."""
    try:
        case_id = generate_id()
        logger.info(f"Case created: {case_id} for user {current_user.username}")
        return {"case_id": case_id, "message": "Case created successfully"}
    except Exception as e:
        logger.error(f"Case creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Case creation failed: {str(e)}")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(UserService.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document and save to the uploads directory."""
    try:
        file_id = generate_id()
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Document uploaded: {file.filename} by user {current_user.username}")
        return {"file_id": file_id, "filename": file.filename, "message": "Document uploaded successfully"}
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")