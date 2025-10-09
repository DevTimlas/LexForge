# File: lexforge-backend/app/data_sources/us_caselaw.py
# This file defines functions for loading US case law.
from app.external_apis.courtlistener_api import CourtListenerAPI
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_us_caselaw(query: str, court: str = None):
    """Load US case law from CourtListener API."""
    try:
        api = CourtListenerAPI()
        results = await api.search_courtlistener(query, court=court)
        return results
    except Exception as e:
        logger.error(f"US case law load failed for query '{query}': {str(e)}")
        raise