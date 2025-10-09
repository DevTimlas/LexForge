# File: lexforge-backend/app/external_apis/google_search.py
# This file defines functions for Google search integration.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def google_search(query: str):
    """Perform Google search for additional legal information."""
    base_url = "https://www.google.com/search"
    params = {"q": query}
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"Google search failed for query '{query}': {str(e)}")
        raise