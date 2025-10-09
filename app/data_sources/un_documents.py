# File: lexforge-backend/app/data_sources/un_documents.py
# This file defines functions for loading UN documents.

from app.external_apis.un_api import search_un_documents
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def load_un_documents(query: str):
    """Load UN documents from the provided UN API."""
    try:
        return await search_un_documents(query)
    except Exception as e:
        logger.error(f"UN documents load failed for query '{query}': {str(e)}")
        raise