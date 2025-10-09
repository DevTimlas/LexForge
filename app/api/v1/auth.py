# File: lexforge-backend/app/api/v1/auth.py
# This file handles authentication endpoints for user registration, login, logout, profile, bar verification, and password reset.

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.models.user import User, UserResponse
from app.db.session import get_db
from app.config import settings
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserCreate(BaseModel):
    """Schema for creating a new user with legal professional details."""
    email: str
    username: str
    password: str
    full_name: str
    bar_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    firm_name: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login credentials."""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Schema for token response with user info."""
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with legal professional verification."""
    user_service = UserService()
    try:
        # Check if user already exists
        existing_user = await user_service.get_user_by_username(user_data.username, db)
        if existing_user:
            logger.warning(f"Registration failed: Username {user_data.username} already exists")
            raise HTTPException(status_code=400, detail="Username already registered")
        existing_email = await user_service.get_user_by_email(user_data.email, db)
        if existing_email:
            logger.warning(f"Registration failed: Email {user_data.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_data_dict = user_data.dict()
        user_data_dict["password"] = user_service.get_password_hash(user_data.password)
        new_user = await user_service.create_user(user_data_dict, db)
        logger.info(f"User registered: {new_user.username}")
        return UserResponse.from_orm(new_user)
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user_service = UserService()
    try:
        user = await user_service.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            logger.warning(f"Authentication failed for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = user_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        await user_service.update_last_login(user.id, db)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "firm_name": user.firm_name,
                "jurisdiction": user.jurisdiction,
                "is_verified": user.is_verified,
                "subscription_tier": user.subscription_tier,
            }
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/logout")
async def logout_user(current_user: User = Depends(UserService.get_current_user)):
    """Logout current user and invalidate token."""
    try:
        # In production, add token blacklisting (e.g., store in Redis)
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(UserService.get_current_user)):
    """Get current user information."""
    return UserResponse.from_orm(current_user)

@router.post("/verify-bar")
async def verify_bar_credentials(
    bar_number: str = Form(...),
    jurisdiction: str = Form(...),
    current_user: User = Depends(UserService.get_current_user),
    db: Session = Depends(get_db)
):
    """Verify legal professional bar credentials."""
    user_service = UserService()
    try:
        verification_result = await user_service.verify_bar_credentials(
            current_user.id, bar_number, jurisdiction, db
        )
        return {
            "verified": verification_result,
            "message": "Bar credentials verified" if verification_result else "Verification failed"
        }
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.post("/reset-password")
async def reset_password_request(email: str = Form(...), db: Session = Depends(get_db)):
    """Request password reset."""
    user_service = UserService()
    try:
        user = await user_service.get_user_by_email(email, db)
        if not user:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            raise HTTPException(status_code=404, detail="User not found")
        reset_token = await user_service.create_password_reset_token(email, db)
        # In production, send email with reset link
        logger.info(f"Password reset token generated for email: {email}")
        return {"message": "Password reset instructions sent to email", "reset_token": reset_token}
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@router.post("/reset-password-confirm")
async def reset_password_confirm(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """Confirm password reset with token."""
    user_service = UserService()
    try:
        success = await user_service.reset_password_with_token(token, new_password, db)
        if not success:
            logger.warning(f"Password reset failed for token: {token}")
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        logger.info("Password reset successful")
        return {"message": "Password reset successfully"}
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@router.get("/courtlistener-key")
async def get_courtlistener_key(db: Session = Depends(get_db)):
    """Retrieve CourtListener API key from environment or user profile."""
    api_key = os.getenv("COURTLISTENER_API_KEY")
    if not api_key:
        logger.error("CourtListener API key not configured")
        raise HTTPException(status_code=400, detail="CourtListener API key not configured")
    return {"api_key": api_key}