# app/models/evidence.py

from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from .base import Base
import uuid
import json

class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    evidence_type = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    chain_of_custody = Column(Text, default='[]')  # JSON string of list of dicts
    status = Column(String, default="secure")
    associated_case = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # For text-based evidence