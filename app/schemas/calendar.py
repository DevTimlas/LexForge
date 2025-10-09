# File: app/schemas/calendar.py

from pydantic import BaseModel
from datetime import datetime

class EventCreate(BaseModel):
    title: str
    start: datetime
    end: datetime | None = None
    description: str | None = None
    case_id: int | None = None  # Link to cases if needed

class EventResponse(EventCreate):
    id: int