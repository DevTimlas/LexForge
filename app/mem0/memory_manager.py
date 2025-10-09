# File: lexforge-backend/app/mem0/memory_manager.py
# This file defines the MemoryManager for caching legal query history.

import redis
import json
from datetime import timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MemoryManager:
    """Manager for caching legal query results using Redis."""
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379, db=0)

    async def store(self, key: str, value: dict):
        """Store query results in Redis with expiration."""
        try:
            self.redis.setex(key, timedelta(hours=1), json.dumps(value))  # Expire in 1 hour
        except Exception as e:
            logger.error(f"Memory store failed: {str(e)}")
            raise

    async def get(self, key: str):
        """Retrieve query results from Redis."""
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Memory retrieval failed: {str(e)}")
            raise