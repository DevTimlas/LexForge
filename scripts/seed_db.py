# File: lexforge-backend/scripts/seed_db.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.user_metrics import UserMetrics
from datetime import datetime

async def seed_db():
    async with AsyncSessionLocal() as session:
        user = User(
            id="user_123",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User",
            subscription_tier="basic",
            created_at=datetime.utcnow()
        )
        metrics = UserMetrics(
            id="metric_1",
            user_id="user_123",
            active_cases=10,
            win_rate=94.2
        )
        session.add_all([user, metrics])
        await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_db())