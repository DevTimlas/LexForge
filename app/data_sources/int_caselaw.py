# File: lexforge-backend/app/data_sources/int_caselaw.py
# This file defines functions for loading international case law.

from app.external_apis.int_caselaw_api import search_int_caselaw
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_int_caselaw(query: str):
    """Load international case law from the provided international API."""
    try:
        return await search_int_caselaw(query)
    except Exception as e:
        logger.error(f"International case law load failed for query '{query}': {str(e)}")
        raise