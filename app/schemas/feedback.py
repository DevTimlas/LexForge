# File: lexforge-backend/app/schemas/feedback.py
# This file defines Pydantic schemas for feedback operations.

from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    """Schema for submitting user feedback."""
    user_id: str
    feedback_type: str
    content: str