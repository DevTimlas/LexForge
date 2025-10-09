# File: lexforge-backend/app/data_sources/echr_caselaw.py
# This file defines functions for loading ECHR case law.

from app.external_apis.echr_api import search_echr
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_echr_caselaw(query: str):
    """Load ECHR case law from the provided ECHR API."""
    try:
        return await search_echr(query)
    except Exception as e:
        logger.error(f"ECHR load failed for query '{query}': {str(e)}")
        raise