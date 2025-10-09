# File: lexforge-backend/app/external_apis/un_api.py
# This file defines functions for interacting with the UN API.

from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def search_un_documents(query: str, year: int = None):
    """Search UN documents using the provided query and optional year filter."""
    base_url = "https://documents.un.org/api/search"
    params = {"q": query}
    if year:
        params["year"] = year
    try:
        response = await make_api_request(base_url, params=params)
        return response
    except Exception as e:
        logger.error(f"UN API failed for query '{query}': {str(e)}")
        raise

async def search_pdf_attachment(url: str):
    """Retrieve PDF attachment from UN document URL."""
    try:
        response = await make_api_request(url, method="GET")
        return response  # Binary content
    except Exception as e:
        logger.error(f"UN PDF fetch failed for URL '{url}': {str(e)}")
        raise