# File: lexforge-backend/app/data_sources/wto_caselaw.py
# This file defines functions for loading WTO case law.

from app.external_apis.wto_api import get_wto_cases
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_wto_caselaw(year: int = None):
    """Load WTO case law from the provided WTO API."""
    try:
        return await get_wto_cases(year)
    except Exception as e:
        logger.error(f"WTO case law load failed for year {year}: {str(e)}")
        raise