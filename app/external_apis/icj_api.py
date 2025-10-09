# File: lexforge-backend/app/external_apis/icj_api.py
# This file defines functions for interacting with the ICJ API.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_icj_judgments(year: int = None):
    """Retrieve ICJ judgments using the provided year filter if specified."""
    base_url = "https://www.icj-cij.org/api/judgments"
    params = {"year": year} if year else {}
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"ICJ API failed for year {year}: {str(e)}")
        raise