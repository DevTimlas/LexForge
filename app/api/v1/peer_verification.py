# peer_verification.py
# --------------------
# Handles peer verification endpoints for LexForge backend.
# TODO: Extend with bar API integration, reputation scoring, and gamified rewards.

from fastapi import APIRouter, Request
from app.agents.peer_verification_agent import PeerVerificationAgent

router = APIRouter()

peer_agent = PeerVerificationAgent()

@router.post("/verify-peer")
async def verify_peer(request: Request):
    """
    Verifies peer contributions and manages reputation.
    TODO: Add bar API integration and rewards.
    """
    data = await request.json()
    result = peer_agent.handle(data)
    return {"peer_verification": result}
