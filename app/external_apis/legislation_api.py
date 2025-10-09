# File: lexforge-backend/app/external_apis/legislation_api.py
# This file defines functions for interacting with the UK Legislation API (Legislation.gov.uk).

from .utils import make_api_request
import xml.etree.ElementTree as ET
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def get_legislation_work(type_: str = "ukpga", year: int = 2000, number: int = 1, format_: str = "xml"):
    """Retrieve a specific UK legislation work from Legislation.gov.uk."""
    base_url = f"https://www.legislation.gov.uk/{type_}/{year}/{number}"
    params = {"format": format_} if format_ else {}
    try:
        response_text = await make_api_request(base_url, params=params)
        if format_ == "xml":
            root = ET.fromstring(response_text)
            return {
                "id": root.find(".//id").text,
                "title": root.find(".//title").text,
                "content": response_text
            }
        return response_text
    except Exception as e:
        logger.error(f"Legislation work fetch failed for {type_}/{year}/{number}: {str(e)}")
        raise

async def get_legislation_expression(type_: str, year: int, number: int, format_: str = "xml"):
    """Retrieve a specific UK legislation expression from Legislation.gov.uk."""
    base_url = f"https://www.legislation.gov.uk/{type_}/{year}/{number}/expression"
    params = {"format": format_}
    try:
        response_text = await make_api_request(base_url, params=params)
        if format_ == "xml":
            root = ET.fromstring(response_text)
            return {
                "id": root.find(".//id").text,
                "title": root.find(".//title").text,
                "content": response_text
            }
        return response_text
    except Exception as e:
        logger.error(f"Legislation expression fetch failed for {type_}/{year}/{number}: {str(e)}")
        raise

async def get_legislation_manifestation(type_: str, year: int, number: int, format_: str = "xml"):
    """Retrieve a specific UK legislation manifestation from Legislation.gov.uk."""
    base_url = f"https://www.legislation.gov.uk/{type_}/{year}/{number}/manifestation"
    params = {"format": format_}
    try:
        response_text = await make_api_request(base_url, params=params)
        if format_ == "xml":
            root = ET.fromstring(response_text)
            return {
                "id": root.find(".//id").text,
                "title": root.find(".//title").text,
                "content": response_text
            }
        return response_text
    except Exception as e:
        logger.error(f"Legislation manifestation fetch failed for {type_}/{year}/{number}: {str(e)}")
        raise

async def search_legislation_id(identifier: str, format_: str = "xml"):
    """Search UK legislation by identifier."""
    base_url = f"https://www.legislation.gov.uk/id/{identifier}"
    params = {"format": format_}
    try:
        response_text = await make_api_request(base_url, params=params)
        if format_ == "xml":
            root = ET.fromstring(response_text)
            return {
                "id": root.find(".//id").text,
                "title": root.find(".//title").text,
                "content": response_text
            }
        return response_text
    except Exception as e:
        logger.error(f"Legislation ID search failed for {identifier}: {str(e)}")
        raise

async def search_legislation(title: str, type_: str = None, start_year: int = None, end_year: int = None):
    """Search UK legislation by title with optional filters."""
    base_url = "https://www.legislation.gov.uk/search"
    params = {"title": title}
    if type_:
        params["type"] = type_
    if start_year:
        params["start_year"] = start_year
    if end_year:
        params["end_year"] = end_year
    try:
        response_text = await make_api_request(base_url, params=params)
        root = ET.fromstring(response_text)
        return [
            {"id": elem.find("id").text, "title": elem.find("title").text}
            for elem in root.findall(".//item")
        ]
    except Exception as e:
        logger.error(f"Legislation search failed for title '{title}': {str(e)}")
        raise

async def list_legislation(type_: str = None, year: int = None):
    """List UK legislation with optional type and year filters."""
    base_url = "https://www.legislation.gov.uk/all"
    params = {}
    if type_:
        params["type"] = type_
    if year:
        params["year"] = year
    try:
        response_text = await make_api_request(base_url, params=params)
        root = ET.fromstring(response_text)
        return [
            {"id": elem.find("id").text, "title": elem.find("title").text}
            for elem in root.findall(".//item")
        ]
    except Exception as e:
        logger.error(f"Legislation list failed for type '{type_}', year {year}: {str(e)}")
        raise

async def get_case_law_feed(query: str):
    """Retrieve UK case law feed from National Archives."""
    base_url = "https://www.nationalarchives.gov.uk/case-law/feed"
    params = {"q": query}
    try:
        response_text = await make_api_request(base_url, params=params)
        root = ET.fromstring(response_text)
        return [
            {"title": elem.find("title").text, "link": elem.find("link").text}
            for elem in root.findall(".//item")
        ]
    except Exception as e:
        logger.error(f"Case law feed fetch failed for query '{query}': {str(e)}")
        raise

async def get_case_law_deprecated_feed(query: str):
    """Retrieve deprecated UK case law feed from National Archives."""
    base_url = "https://www.nationalarchives.gov.uk/case-law/deprecated/feed"
    params = {"q": query}
    try:
        response_text = await make_api_request(base_url, params=params)
        root = ET.fromstring(response_text)
        return [
            {"title": elem.find("title").text, "link": elem.find("link").text}
            for elem in root.findall(".//item")
        ]
    except Exception as e:
        logger.error(f"Deprecated case law feed fetch failed for query '{query}': {str(e)}")
        raise

async def get_case_law_document(case_id: str, format_: str = "xml"):
    """Retrieve a specific UK case law document by ID."""
    base_url = f"https://www.nationalarchives.gov.uk/case-law/{case_id}"
    params = {"format": format_}
    try:
        response_text = await make_api_request(base_url, params=params)
        if format_ == "xml":
            root = ET.fromstring(response_text)
            return {
                "id": root.find(".//id").text,
                "title": root.find(".//title").text,
                "content": response_text
            }
        return response_text
    except Exception as e:
        logger.error(f"Case law document fetch failed for case_id '{case_id}': {str(e)}")
        raise

async def get_case_law_document_format(case_id: str, format_: str):
    """Retrieve a UK case law document in a specific format."""
    base_url = f"https://www.nationalarchives.gov.uk/case-law/{case_id}/{format_}"
    try:
        response_text = await make_api_request(base_url)
        return response_text
    except Exception as e:
        logger.error(f"Case law document format fetch failed for case_id '{case_id}', format '{format_}': {str(e)}")
        raise