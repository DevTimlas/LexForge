# File: app/api/v1/calendar.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.calendar import EventCreate, EventResponse  # We'll define these schemas
from app.models.calendar import Event  # We'll define this model
from app.crud.calendar import create_event, get_events  # We'll define these CRUD functions

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/events", response_model=list[EventResponse])
async def fetch_events(db: AsyncSession = Depends(get_db)):
    """Fetch all calendar events"""
    events = await get_events(db)
    return events

@router.post("/events", response_model=EventResponse)
async def add_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    """Add a new calendar event"""
    new_event = await create_event(db, event)
    if not new_event:
        raise HTTPException(status_code=400, detail="Failed to create event")
    return new_event