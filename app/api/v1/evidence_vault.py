# app/api/v1/evidence_vault.py
# -----------------
# Handles evidence vault endpoints for LexForge backend.
# Extended with blockchain integration, chain-of-custody, and secure sharing.

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.agents.evidence_vault_agent import EvidenceVaultAgent
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

evidence_agent = EvidenceVaultAgent()

@router.post("/store-evidence")
async def store_evidence(
    description: str = Form(None),
    evidence_type: str = Form(None),
    associated_case: str = Form(None),
    files: List[UploadFile] = File(None),  # Optional
    db: AsyncSession = Depends(get_db)
):
    try:
        data = {
            "description": description,
            "evidence_type": evidence_type,
            "associated_case": associated_case,
            "files": files,
        }
        result = await evidence_agent.handle(data, db)
        return {"evidence_result": result}
    except Exception as e:
        logger.error(f"Evidence storage failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory")
async def get_evidence_inventory(
    associated_case: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieves evidence inventory, optionally filtered by case.
    """
    try:
        inventory = await evidence_agent.get_inventory(associated_case, db)
        # Assuming inventory is list of dicts, adjust keys accordingly
        inventory_dicts = [
            {
                "id": e["id"],
                "filename": e["filename"],
                "evidence_type": e["evidence_type"],
                "upload_date": e["upload_date"].isoformat() if isinstance(e["upload_date"], datetime) else e["upload_date"],
                "chain_of_custody": e["chain_of_custody"],
                "status": e["status"],
                "associated_case": e["associated_case"],
                "content": e["content"],
            }
            for e in inventory
        ]
        return inventory_dicts
    except Exception as e:
        logger.error(f"Failed to retrieve inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{evidence_id}")
async def get_evidence_summary(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generates AI-powered summary of evidence item.
    """
    try:
        summary = await evidence_agent.get_summary(evidence_id, db)
        return summary
    except Exception as e:
        logger.error(f"Failed to generate summary for {evidence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chain-of-custody/{evidence_id}")
async def get_chain_of_custody(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Retrieves chain-of-custody log for evidence item.
    """
    try:
        log = await evidence_agent.get_chain_of_custody(evidence_id, db)
        return log
    except Exception as e:
        logger.error(f"Failed to retrieve chain-of-custody for {evidence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))