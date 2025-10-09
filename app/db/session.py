# File: lexforge-backend/app/db/session.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
from app.models.base import Base
from app.models.user import User
from app.models.document import Document
from app.models.alert import Alert
from app.models.user_metrics import UserMetrics
from app.models.feedback import Feedback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://mac@localhost:5432/lexforge"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,         # Enable SQL logging for debugging
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for dependency injection."""
    session: AsyncSession = AsyncSessionLocal()
    try:
        logger.debug("Opening database session")
        yield session
        await session.commit()
        logger.debug("Database session committed")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        await session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await session.rollback()
        raise
    finally:
        await session.close()
        logger.debug("Database session closed")

async def init_db():
    """Initialize the database (development only)."""
    logger.info(f"Initializing database with URL: {DATABASE_URL}")
    if os.getenv("ENV", "development") == "development":
        try:
            async with engine.begin() as conn:
                # Only create tables if they don't exist
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables ensured: users, documents, alerts, user_metrics, feedback")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {str(e)}")
            raise
    else:
        logger.info("Skipping direct table creation; use Alembic for migrations in production")
