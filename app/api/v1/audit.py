from fastapi import APIRouter, Depends
from app.agents.orchestrator_agent import OrchestratorAgent
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

router = APIRouter()
orchestrator = OrchestratorAgent()

@router.post("/audit")
async def handle_audit_request(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    return await orchestrator.handle(request)