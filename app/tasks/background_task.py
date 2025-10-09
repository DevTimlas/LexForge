# File: lexforge-backend/app/tasks/background_tasks.py
# This file defines background tasks using Celery for long-running operations like simulations.

from celery import Celery
from app.agents.simulation_agent import SimulationAgent
from app.db.session import AsyncSessionLocal
import logging

# Configure logging
logger = logging.getLogger(__name__)
celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
async def run_simulation_task(user_id: str, case_id: str):
    """Run legal case simulation in background using Celery."""
    async with AsyncSessionLocal() as db:
        try:
            agent = SimulationAgent(db)
            result = await agent.simulate_case(case_id)
            logger.info(f"Simulation completed for user {user_id}, case {case_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Simulation task failed: {str(e)}")
            raise