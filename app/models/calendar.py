# File: app/models/calendar.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    start = Column(DateTime)
    end = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)  # Assuming you have a 'cases' table