# File: lexforge-backend/app/external_apis/utils.py
# This file defines common utilities for external API requests, including async request handling.

import aiohttp
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def make_api_request(url, method="GET", headers=None, params=None, json=None):
    """Utility function for async API requests with error handling.
    This function handles GET and POST requests to external APIs, raising exceptions on failure.
    """
    async with aiohttp.ClientSession() as session:
        try:
            if method == "GET":
                async with session.get(url, headers=headers, params=params) as response:
                    response.raise_for_status()
                    return await response.text()
            elif method == "POST":
                async with session.post(url, headers=headers, json=json) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {url}, error: {str(e)}")
            raise ValueError(f"API request failed: {str(e)}")