# File: lexforge-backend/app/api/v1/alerts.py
# This file defines API endpoints for alerts.

from fastapi import APIRouter
import random

router = APIRouter(tags=["alerts"])

@router.get("")
@router.get("/")
async def get_alerts():
    """Fetch recent alerts."""
    alerts = [
        {
            "title": "Case Law Update",
            "description": "Johnson v. State overruled - affects 3 active cases",
            "time": "2 hours ago",
            "type": "danger",
            "action": "Review"
        },
        {
            "title": "Deadline Reminder",
            "description": "Motion due for Wilson v. Corp in 2 days",
            "time": "5 hours ago",
            "type": "warning",
            "action": "Schedule"
        },
        {
            "title": "Analysis Complete",
            "description": "Contract risk assessment for MegaCorp deal",
            "time": "1 day ago",
            "type": "success",
            "action": "View"
        }
    ]
    return random.sample(alerts, k=min(len(alerts), 3))
