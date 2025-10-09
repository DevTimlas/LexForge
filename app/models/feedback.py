from sqlalchemy import Column, String, Integer, ForeignKey
from .base import Base
from datetime import datetime
from sqlalchemy import Column, DateTime

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    comments = Column(String, nullable=True)
    feature = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)