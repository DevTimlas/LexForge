# File: lexforge-backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "LexForge"
    ENV: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database & Cache
    DATABASE_URL: str = "postgresql+asyncpg://mac:password@localhost:5432/lexforge"  # "postgresql://mac:password@localhost:5432/lexforge"
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CX: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None

    # Legal APIs
    WESTLAW_API_KEY: Optional[str] = None
    LEXIS_API_KEY: Optional[str] = None
    COURTLISTENER_API_KEY: Optional[str] = None
    PACER_API_KEY: Optional[str] = None
    BAILII_API_KEY: Optional[str] = None
    EURLEx_API_KEY: Optional[str] = None
    ICJ_API_KEY: Optional[str] = None
    ECHR_API_KEY: Optional[str] = None
    WTO_API_KEY: Optional[str] = None
    UN_API_KEY: Optional[str] = None

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        ".pdf", ".doc", ".docx", ".txt", ".rtf",
        ".mp3", ".mp4", ".wav", ".avi", ".mov",
        ".jpg", ".jpeg", ".png", ".zip",
    ]

    # AI Models
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo-preview"

    # Blockchain / Security
    ETHEREUM_RPC_URL: Optional[str] = None
    PRIVATE_KEY: Optional[str] = None
    BLOCKCHAIN_SECRET: Optional[str] = None
    ZERO_KNOWLEDGE_SECRET: Optional[str] = None
    JWT_SECRET: Optional[str] = None
    MEM0_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
