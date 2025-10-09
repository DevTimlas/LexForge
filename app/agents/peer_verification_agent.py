# File: lexforge-backend/app/agents/peer_verification_agent.py
# This file defines the PeerVerificationAgent for verifying legal citations using X search.

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.utils.x_user_search import search_x_users
import logging

# Configure logging
logger = logging.getLogger(__name__)

class PeerVerificationAgent(BaseAgent):
    """Agent for peer verification of legal citations using X search."""
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.logger = logging.getLogger(__name__)

    async def verify_citation(self, citation: str):
        """Verify legal citation using X search for peer discussions."""
        try:
            x_results = await search_x_users(citation)
            return {"verified": len(x_results) > 0, "sources": x_results}
        except Exception as e:
            self.logger.error(f"Citation verification failed: {str(e)}")
            raise

    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle peer verification requests."""
        citation = request.get("citation")
        if not citation:
            return {"error": "Citation is required for verification"}
        result = await self.verify_citation(citation)
        provenance = await self._create_provenance(
            sources=["x_search"],
            method="peer_verification",
            confidence=0.85
        )
        final_result = {
            "data": result,
            "provenance": [provenance]
        }
        return final_result