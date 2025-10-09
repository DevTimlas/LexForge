# File: lexforge-backend/app/api/v1/metrics.py
# This file defines API endpoints for metrics.

from fastapi import APIRouter
import random

router = APIRouter(tags=["metrics"])

@router.get("")
@router.get("/")
async def get_metrics():
    """Fetch performance metrics."""
    return {
        "activeCases": random.randint(100, 150),
        "winRate": random.randint(90, 98),
        "revenue": random.randint(2000000, 3000000),
        "queriesToday": random.randint(100, 200),
        "queryAccuracy": round(random.uniform(95, 98), 1),
        "timeSaved": round(random.uniform(10, 15), 1),
        "citationRate": round(random.uniform(98, 99.5), 1)
    }
