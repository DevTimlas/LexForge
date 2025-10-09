# File: lexforge-backend/app/models/user.py
# This file defines SQLAlchemy and Pydantic models for user-related data.

from sqlalchemy import Column, String, Boolean, DateTime, ARRAY
from datetime import datetime
from .base import Base
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import relationship
from .cases import Case

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Store hashed password
    full_name = Column(String, nullable=False)
    firm_name = Column(String, nullable=True)
    jurisdiction = Column(String, nullable=True)
    bar_number = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String, default="basic")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    permissions = Column(ARRAY(String), default=[])
    cases = relationship("Case", back_populates="user")

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    firm_name: Optional[str]
    jurisdiction: Optional[str]
    bar_number: Optional[str]
    is_verified: bool
    is_active: bool
    subscription_tier: str
    created_at: str
    last_login: Optional[str]
    permissions: List[str]

    class Config:
        from_attributes = True  # Enable conversion from SQLAlchemy ORM objects