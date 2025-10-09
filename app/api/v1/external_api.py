# external_api.py
# ---------------
# Handles external API access endpoints for LexForge backend.
# TODO: Extend with authentication, rate limiting, and error handling.

from fastapi import APIRouter, Request
from app.external_apis.google_search import GoogleSearchAPI
from app.external_apis.courtlistener_api import CourtListenerAPI

router = APIRouter()

google_api = GoogleSearchAPI(api_key="YOUR_KEY", cx="YOUR_CX")
courtlistener_api = CourtListenerAPI()

@router.post("/google-search")
async def google_search(request: Request):
    """
    Performs a Google Custom Search using provided query.
    TODO: Add pagination and error handling.
    """
    data = await request.json()
    result = google_api.search(data.get("query", ""))
    return {"results": result}

@router.post("/courtlistener-search")
async def courtlistener_search(request: Request):
    """
    Searches CourtListener for legal opinions using provided query.
    TODO: Add pagination and error handling.
    """
    data = await request.json()
    result = courtlistener_api.search_cases(data.get("query", ""))
    return {"results": result}
