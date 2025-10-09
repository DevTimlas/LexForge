# File: app/crud/calendar.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.calendar import Event
from app.schemas.calendar import EventCreate

async def get_events(db: AsyncSession):
    result = await db.execute(select(Event))
    return result.scalars().all()

async def create_event(db: AsyncSession, event: EventCreate):
    db_event = Event(**event.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event