# File: lexforge-backend/app/external_apis/wto_api.py
# This file defines functions for interacting with the WTO API.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_wto_cases(year: int = None):
    """Retrieve WTO case law using the provided year filter if specified."""
    base_url = "https://www.wto.org/api/disputes"
    params = {"year": year} if year else {}
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"WTO API failed for year {year}: {str(e)}")
        raise