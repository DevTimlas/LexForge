# File: lexforge-backend/app/agents/regulatory_radar_agent.py
# This file defines the RegulatoryRadarAgent for monitoring regulatory changes.

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.external_apis.regulatory_feeds import get_regulatory_updates
import logging

# Configure logging
logger = logging.getLogger(__name__)

class RegulatoryRadarAgent(BaseAgent):
    """Agent for monitoring regulatory changes from legal APIs."""
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.logger = logging.getLogger(__name__)

    async def monitor_regulations(self, jurisdiction: str):
        """Monitor regulatory changes from legal APIs."""
        try:
            updates = await get_regulatory_updates(jurisdiction)
            return updates
        except Exception as e:
            self.logger.error(f"Regulation monitoring failed: {str(e)}")
            raise

    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regulatory radar requests."""
        jurisdiction = request.get("jurisdiction")
        if not jurisdiction:
            return {"error": "Jurisdiction is required for regulation monitoring"}
        result = await self.monitor_regulations(jurisdiction)
        provenance = await self._create_provenance(
            sources=["regulatory_apis"],
            method="regulatory_monitoring",
            confidence=0.95
        )
        final_result = {
            "data": result,
            "provenance": [provenance]
        }
        return final_result