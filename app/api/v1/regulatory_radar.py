# regulatory_radar.py
# -------------------
# Handles regulatory radar endpoints for LexForge backend.
# TODO: Extend with real-time monitoring, deadline computation, and visual timelines.

from fastapi import APIRouter, Request
from app.agents.regulatory_radar_agent import RegulatoryRadarAgent

router = APIRouter()

regulatory_agent = RegulatoryRadarAgent()

@router.post("/monitor-regulation")
async def monitor_regulation(request: Request):
    """
    Monitors regulatory changes and computes deadlines.
    TODO: Add jurisdiction mapping and visual timelines.
    """
    data = await request.json()
    result = regulatory_agent.handle(data)
    return {"regulatory_update": result}
