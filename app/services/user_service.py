# File: lexforge-backend/app/services/user_service.py
# This file defines the UserService class for handling user-related operations.

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.db.session import get_db
from app.config import settings
import secrets

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """Service for user management and authentication"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, username: str, password: str, db: AsyncSession = Depends(get_db)) -> Optional[User]:
        """Authenticate user credentials"""
        try:
            user = await self.get_user_by_username(username, db)
            if not user or not self.verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed for username: {username}")
                return None
            return user
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {str(e)}")
            return None

    # async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    #     """Get current user from JWT token"""
    #     credentials_exception = HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Could not validate credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    #     try:
    #         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #         username: str = payload.get("sub")
    #         if username is None:
    #             raise credentials_exception
    #     except JWTError as e:
    #         logger.error(f"JWT decode failed: {str(e)}")
    #         raise credentials_exception

    #     user = await self.get_user_by_username(username, db)
    #     if user is None:
    #         raise credentials_exception
    #     return user

    async def get_current_user() -> User:
        """Return a mock user for testing, bypassing authentication."""
        try:
            # Mock user for testing purposes
            mock_user = User(
                id="mock_user_123",
                username="test_user",
                email="test@example.com"
            )
            logger.info("Returning mock user for testing")
            return mock_user
        except Exception as e:
            logger.error(f"Failed to get mock user: {str(e)}")
            raise

    async def create_user(self, user_data: dict, db: AsyncSession = Depends(get_db)) -> User:
        """Create new user"""
        try:
            # Check for existing user
            existing_user = await self.get_user_by_username(user_data["username"], db)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered",
                )
            existing_email = await self.get_user_by_email(user_data["email"], db)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Create new user with hashed password
            new_user = User(
                id=str(secrets.randbelow(10000)),
                username=user_data["username"],
                email=user_data["email"],
                password_hash=self.get_password_hash(user_data["password"]),  # Hash password
                full_name=user_data["full_name"],
                firm_name=user_data.get("firm_name", ""),
                jurisdiction=user_data.get("jurisdiction", "US_FEDERAL"),
                is_verified=False,
                subscription_tier="basic",
                created_at=datetime.utcnow(),
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            logger.info(f"User created: {new_user.username}")
            return new_user
        except Exception as e:
            await db.rollback()
            logger.error(f"User creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

    async def get_user_by_username(self, username: str, db: AsyncSession = Depends(get_db)) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_user_by_email(self, email: str, db: AsyncSession = Depends(get_db)) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def update_last_login(self, user_id: str, db: AsyncSession = Depends(get_db)):
        """Update user's last login timestamp"""
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if user:
                user.last_login = datetime.utcnow()
                await db.commit()
                logger.info(f"Updated last login for user_id: {user_id}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update last login for user_id {user_id}: {str(e)}")

    async def verify_bar_credentials(self, user_id: str, bar_number: str, jurisdiction: str, db: AsyncSession = Depends(get_db)) -> bool:
        """Verify legal professional credentials"""
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if user:
                user.bar_number = bar_number
                user.jurisdiction = jurisdiction
                user.is_verified = len(bar_number) > 5  # Mock verification
                await db.commit()
                logger.info(f"Bar credentials verified for user_id: {user_id}")
                return user.is_verified
            return False
        except Exception as e:
            await db.rollback()
            logger.error(f"Bar credentials verification failed for user_id {user_id}: {str(e)}")
            return False

    async def create_password_reset_token(self, email: str, db: AsyncSession = Depends(get_db)) -> str:
        """Create password reset token"""
        try:
            user = await self.get_user_by_email(email, db)
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return secrets.token_urlsafe(32)  # Return dummy token for security
            token = secrets.token_urlsafe(32)
            # In production, store token in DB with expiry
            logger.info(f"Password reset token created for email: {email}")
            return token
        except Exception as e:
            logger.error(f"Failed to create password reset token for email {email}: {str(e)}")
            return secrets.token_urlsafe(32)  # Return dummy token for security

    async def reset_password_with_token(self, token: str, new_password: str, db: AsyncSession = Depends(get_db)) -> bool:
        """Reset password using token"""
        try:
            # Mock implementation: In production, verify token against DB
            user = await db.execute(select(User).limit(1))
            user = user.scalars().first()
            if user:
                user.password_hash = self.get_password_hash(new_password)
                await db.commit()
                logger.info("Password reset successful")
                return True
            logger.warning("Password reset failed: No user found")
            return False
        except Exception as e:
            await db.rollback()
            logger.error(f"Password reset failed: {str(e)}")
            return False