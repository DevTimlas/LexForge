# File: lexforge-backend/app/external_apis/echr_api.py
# This file defines functions for interacting with the ECHR API.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def search_echr(query: str):
    """Search ECHR for case law using the provided query."""
    base_url = "https://hudoc.echr.coe.int/app/conversion/docx?library=echreng&q=" + query
    try:
        response = await make_api_request(base_url)
        return response
    except Exception as e:
        logger.error(f"ECHR search failed for query '{query}': {str(e)}")
        raise