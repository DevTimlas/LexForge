# File: lexforge-backend/app/data_sources/icj_caselaw.py
# This file defines functions for loading ICJ case law.

from app.external_apis.icj_api import get_icj_judgments
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_icj_caselaw(year: int = None):
    """Load ICJ case law from the provided ICJ API."""
    try:
        return await get_icj_judgments(year)
    except Exception as e:
        logger.error(f"ICJ load failed for year {year}: {str(e)}")
        raise