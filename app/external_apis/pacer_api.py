# File: lexforge-backend/app/external_apis/pacer_api.py
# This file defines functions for interacting with the PACER API.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_pacer_data(query: str):
    """Retrieve data from PACER API using the provided query."""
    base_url = "https://pacer.uscourts.gov/api/search"
    params = {"q": query}
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"PACER API failed for query '{query}': {str(e)}")
        raise