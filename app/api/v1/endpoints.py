# File: lexforge-backend/app/api/v1/endpoints.py
# This file defines API endpoints for the LexForge platform, handling retrieval, generation, classification, analytics, orchestration, and document uploads.
# It integrates with agents for processing requests and uses database sessions for persistence.
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from app.db.session import get_db
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.generation_agent import GenerationAgent
from app.agents.classification_agent import ClassificationAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.external_apis.courtlistener_api import CourtListenerAPI
from app.data.loaders import DataLoader
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

# Initialize FastAPI router for grouping endpoints
router = APIRouter()

# Initialize agents with upload directory for file handling
retrieval_agent = RetrievalAgent(upload_dir="uploads")
generation_agent = GenerationAgent(upload_dir="uploads")
classification_agent = ClassificationAgent(upload_dir="uploads")
analytics_agent = AnalyticsAgent(upload_dir="uploads")
orchestrator_agent = OrchestratorAgent(upload_dir="uploads")
data_loader = DataLoader()
courtlistener_api = CourtListenerAPI()

@router.post("/retrieval")
async def retrieval(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle document retrieval requests using the RetrievalAgent."""
    try:
        result = await retrieval_agent.handle(request | {"db": db})
        return result
    except ValueError as ve:
        logger.error(f"Retrieval error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/generation")
async def generation(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle text generation requests using the GenerationAgent."""
    try:
        result = await generation_agent.handle(request | {"db": db})
        return result
    except ValueError as ve:
        logger.error(f"Generation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/classification")
async def classification(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle document classification requests using the ClassificationAgent."""
    try:
        result = await classification_agent.handle(request | {"db": db})
        return result
    except ValueError as ve:
        logger.error(f"Classification error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected classification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/analytics")
async def analytics(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle analytics requests using the AnalyticsAgent."""
    try:
        result = await analytics_agent.handle(request | {"db": db})
        return result
    except ValueError as ve:
        logger.error(f"Analytics error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/orchestration")
async def orchestration(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Handle orchestrated workflows using the OrchestratorAgent."""
    try:
        result = await orchestrator_agent.handle(request | {"db": db})
        return result
    except ValueError as ve:
        logger.error(f"Orchestration error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected orchestration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "user_123",
    session_id: str = "session_123",
    db: AsyncSession = Depends(get_db)
):
    """Handle document uploads using the OrchestratorAgent and save metadata to the database."""
    try:
        result = await orchestrator_agent.process_upload(file, user_id, session_id)
        async with db as session:
            await session.commit()
        return result
    except ValueError as ve:
        logger.error(f"Upload error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/legal/search/uk")
async def search_uk_legal_data(
    query: str,
    type_: str = None,
    start_year: int = None,
    end_year: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Search UK legislation and case law using Legislation.gov.uk and National Archives APIs."""
    try:
        legislation_results = await data_loader.load_legislation(query=query)
        case_law_results = await data_loader.load_case_law(query=query)
        return {
            "legislation": legislation_results,
            "case_law": case_law_results
        }
    except Exception as e:
        logger.error(f"Error in UK legal search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/legal/search/us")
async def search_us_legal_data(
    query: str,
    court: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Search US case law via CourtListener API."""
    try:
        results = await courtlistener_api.search_courtlistener(query=query, court=court)
        return results
    except Exception as e:
        logger.error(f"Error in US legal search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))