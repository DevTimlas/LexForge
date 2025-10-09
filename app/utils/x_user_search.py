# File: lexforge-backend/app/utils/x_user_search.py
# This file defines utilities for searching X users.

import aiohttp
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def search_x_users(query: str):
    """Search X for user posts related to legal citations."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.x.com/search?q={query}") as response:
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        logger.error(f"X search failed for query '{query}': {str(e)}")
        raise