# File: lexforge-backend/app/external_apis/int_caselaw_api.py
# This file defines functions for international case law API.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def search_int_caselaw(query: str):
    """Search international case law using the provided query."""
    base_url = "https://example.com/int_caselaw/search"
    params = {"q": query}
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"International case law search failed for query '{query}': {str(e)}")
        raise