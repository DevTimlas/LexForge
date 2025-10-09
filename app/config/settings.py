# File: lexforge-backend/app/config/settings.py
# This file defines application settings.

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secure-secret-key-here"  # Replace with a secure key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://mac:password@localhost:5432/lexforge"  # Update with your DB credentials

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()