# File: lexforge-backend/app/data_sources/uk_legislation.py
# This file defines functions for loading UK legislation.

from app.external_apis import search_legislation
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_uk_legislation(query: str):
    """Load UK legislation from Legislation.gov.uk API."""
    try:
        return await search_legislation(title=query)
    except Exception as e:
        logger.error(f"UK legislation load failed for query '{query}': {str(e)}")
        raise