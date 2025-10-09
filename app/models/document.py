# File: lexforge-backend/app/models/document.py
from sqlalchemy import Column, String, DateTime, Integer, ARRAY, Float, ForeignKey
from datetime import datetime
from .base import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    case_id = Column(String, nullable=True)
    tags = Column(ARRAY(String), default=[])
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="uploaded")
    size = Column(Integer, default=0)
    classification = Column(String, nullable=True)
    privilege_status = Column(String, nullable=True)
    content = Column(String, nullable=True)
    jurisdiction = Column(String, nullable=True)
    citation = Column(String, nullable=True)
    embedding = Column(ARRAY(Float), nullable=True)