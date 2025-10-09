# File: lexforge-backend/app/external_apis/eur_lex_api.py
# This file defines functions for interacting with the EUR-Lex API for EU legislation.

import xml.etree.ElementTree as ET
from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def search_eur_lex(query: str, year: int = None):
    """Search EUR-Lex for EU legislation using the provided query and optional year filter."""
    base_url = "https://eur-lex.europa.eu/api/search"
    params = {"q": query}
    if year:
        params["year"] = year
    try:
        response_text = await make_api_request(base_url, params=params)
        root = ET.fromstring(response_text)
        return [
            {"id": elem.find("id").text, "title": elem.find("title").text}
            for elem in root.findall(".//document")
        ]
    except Exception as e:
        logger.error(f"EUR-Lex search failed for query '{query}': {str(e)}")
        raise