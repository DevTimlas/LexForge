from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    priority = Column(String, default="low")
    status = Column(String, default="unread")