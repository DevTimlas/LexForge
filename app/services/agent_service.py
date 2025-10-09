# File: lexforge-backend/app/services/agent_service.py
# This file defines the AgentService for managing agents and workflows.

from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.retrieval_agent import RetrievalAgent
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AgentService:
    """Service for managing agents and running workflows."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_legal_workflow(self, query: str):
        """Run legal search and analysis workflow using agents."""
        try:
            orchestrator = OrchestratorAgent(self.db)
            retrieval = RetrievalAgent(self.db)
            data = await retrieval.search_legal_data(query)
            result = await orchestrator.handle({"query": query, "data": data})
            return result
        except Exception as e:
            logger.error(f"Agent workflow failed: {str(e)}")
            raise