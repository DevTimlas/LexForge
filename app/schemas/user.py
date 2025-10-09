# File: lexforge-backend/app/schemas/user.py
# This file defines Pydantic schemas for user operations.

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    email: EmailStr
    password: str
    full_name: str
    subscription_tier: str = "basic"

class UserResponse(BaseModel):
    """Schema for user response data."""
    id: str
    username: str
    email: EmailStr
    full_name: str
    subscription_tier: str