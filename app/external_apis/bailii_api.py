# File: lexforge-backend/app/external_apis/bailii_api.py
# This file defines functions for interacting with the BAILII API for UK case law.

import xml.etree.ElementTree as ET
from .utils import make_api_request
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def search_bailii_cases(query: str, court: str = None):
    """Search BAILII for UK case law using the provided query and optional court filter.
    This function fetches XML data from BAILII and parses it into a list of results.
    """
    base_url = "https://www.bailii.org/cgi-bin/lucy_search_1.cgi"
    params = {"query": query}
    if court:
        params["court"] = court
    try:
        response_text = await make_api_request(base_url, params=params)
        root = ET.fromstring(response_text)
        results = [
            {"title": elem.find("title").text, "link": elem.find("link").text}
            for elem in root.findall(".//item")
        ]
        return results
    except Exception as e:
        logger.error(f"BAILII search failed for query '{query}': {str(e)}")
        raise