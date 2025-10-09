# File: app/api/v1/analytics.py

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.agents.analytics_agent import AnalyticsAgent

router = APIRouter(tags=["analytics"])

analytics_agent = AnalyticsAgent()


@router.get("/usage")
async def get_usage(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Query("demo_user")
):
    try:
        return await analytics_agent.handle({
            "action": "user_metrics",
            "user_id": user_id
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Query("demo_user"),
    limit: int = Query(10)
):
    try:
        return await analytics_agent.handle({
            "action": "user_alerts",
            "user_id": user_id,
            "limit": limit
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Query("demo_user"),
    period: str = Query("week")
):
    try:
        return await analytics_agent.handle({
            "action": "performance_metrics",
            "user_id": user_id,
            "period": period
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Query("demo_user"),
    feedback_type: str = Query(...),
    rating: int = Query(...),
    comments: Optional[str] = Query(None),
    feature: Optional[str] = Query(None)
):
    try:
        return await analytics_agent.handle({
            "action": "submit_feedback",
            "user_id": user_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "comments": comments,
            "feature": feature
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
