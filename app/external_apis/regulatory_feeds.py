# File: lexforge-backend/app/external_apis/regulatory_feeds.py
# This file defines functions for regulatory feeds.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_regulatory_updates(jurisdiction: str):
    """Get regulatory updates for the provided jurisdiction."""
    base_url = "https://example.com/regulatory/feeds"
    params = {"jurisdiction": jurisdiction}
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"Regulatory feeds failed for jurisdiction '{jurisdiction}': {str(e)}")
        raise