# File: lexforge-backend/app/data_sources/eu_directives.py
# This file defines functions for loading EU directives.

from app.external_apis.eur_lex_api import search_eur_lex
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_eu_directives(query: str):
    """Load EU directives from the provided EUR-Lex API."""
    try:
        return await search_eur_lex(query)
    except Exception as e:
        logger.error(f"EU directives load failed for query '{query}': {str(e)}")
        raise