import aiohttp
import logging
from typing import List, Dict, Optional
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class CourtListenerAPI:
    """Interface for interacting with the CourtListener API for US case law and related data."""
    BASE_URL = "https://www.courtlistener.com/api/rest/v4"

    def __init__(self):
        self.api_key = settings.COURTLISTENER_API_KEY
        if not self.api_key:
            raise ValueError("CourtListener API key required")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(aiohttp.ClientResponseError),
        before_sleep=lambda retry_state: logger.info(f"Retrying CourtListener API request (attempt {retry_state.attempt_number})...")
    )
    async def search_courtlistener(self, query: str, court: Optional[str] = None) -> List[Dict]:
        """Search CourtListener for US case law using the provided query and optional court filter."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            params = {"type": "o", "q": query[:500], "highlight": "on"}  # Truncate query to 500 chars
            if court:
                params["court"] = court.lower().replace(" ", "_")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/search/", headers=headers, params=params) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(f"CourtListener API error: status {response.status}, response: {response_text}")
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = []
                    for item in data.get("results", []):
                        opinions = item.get("opinions", [])
                        snippet = opinions[0].get("snippet", opinions[0].get("plain_text", "")[:200]) if opinions else ""
                        result = {
                            "id": item["cluster_id"],
                            "title": item["caseName"],
                            "snippet": snippet,
                            "citation": ', '.join(item.get("citation", [])) or "N/A",
                            "relevance": item.get("meta", {}).get("score", {}).get("bm25", 0.8),
                            "source": "courtlistener"
                        }
                        results.append(result)
                    return results
        except Exception as e:
            logger.error(f"CourtListener search failed for query '{query[:100]}...': {str(e)}")
            raise

    async def courtlistener_request(self, case_id: str) -> Dict:
        """Retrieve a specific US case law document by ID from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}/opinions/{case_id}/", headers=headers) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    citation = data.get("citation", "N/A")
                    if isinstance(citation, list):
                        citation = ', '.join(citation)
                    return {
                        "id": data["id"],
                        "title": data.get("type", "Untitled Opinion"),
                        "snippet": data.get("plain_text", "")[:200],
                        "citation": citation,
                        "relevance": 0.9,
                        "source": "courtlistener"
                    }
        except Exception as e:
            logger.error(f"CourtListener request failed for case_id '{case_id}': {str(e)}")
            raise

    async def get_clusters(self, cluster_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve case clusters from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/clusters/" + (f"{cluster_id}/" if cluster_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if cluster_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("caseName", "Untitled Cluster"),
                        "snippet": item.get("syllabus", "")[:200],
                        "citation": ', '.join(item.get("citation", [])) or "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener clusters fetch failed for cluster_id '{cluster_id}': {str(e)}")
            raise

    async def get_opinions(self, opinion_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve opinions from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/opinions/" + (f"{opinion_id}/" if opinion_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if opinion_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("type", "Untitled Opinion"),
                        "snippet": item.get("plain_text", "")[:200],
                        "citation": ', '.join(item.get("citation", [])) or "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener opinions fetch failed for opinion_id '{opinion_id}': {str(e)}")
            raise

    async def get_dockets(self, docket_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve dockets from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/dockets/" + (f"{docket_id}/" if docket_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if docket_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("case_name", "Untitled Docket"),
                        "snippet": item.get("docket_number", "")[:200],
                        "citation": item.get("docket_number", "N/A"),
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener dockets fetch failed for docket_id '{docket_id}': {str(e)}")
            raise

    async def get_docket_entries(self, entry_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve docket entries from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/docket-entries/" + (f"{entry_id}/" if entry_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if entry_id else [])
                    return [{
                        "id": item["id"],
                        "title": f"Docket Entry {item.get('entry_number', 'N/A')}",
                        "snippet": item.get("description", "")[:200],
                        "citation": item.get("entry_number", "N/A"),
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener docket entries fetch failed for entry_id '{entry_id}': {str(e)}")
            raise

    async def get_recap_documents(self, document_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve RECAP documents from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/recap-documents/" + (f"{document_id}/" if document_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if document_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("document_type", "Untitled RECAP Document"),
                        "snippet": item.get("plain_text", "")[:200],
                        "citation": item.get("document_number", "N/A"),
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener RECAP documents fetch failed for document_id '{document_id}': {str(e)}")
            raise

    async def get_courts(self, court_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve court information from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/courts/" + (f"{court_id}/" if court_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if court_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("full_name", "Untitled Court"),
                        "snippet": item.get("short_name", "")[:200],
                        "citation": item.get("court_code", "N/A"),
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener courts fetch failed for court_id '{court_id}': {str(e)}")
            raise

    async def get_audio(self, audio_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve audio files from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/audio/" + (f"{audio_id}/" if audio_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if audio_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("case_name", "Untitled Audio"),
                        "snippet": item.get("description", "")[:200],
                        "citation": item.get("docket_number", "N/A"),
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener audio fetch failed for audio_id '{audio_id}': {str(e)}")
            raise

    async def get_people(self, person_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve people (e.g., judges) information from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/people/" + (f"{person_id}/" if person_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if person_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("name", "Unknown Person"),
                        "snippet": item.get("summary", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener people fetch failed for person_id '{person_id}': {str(e)}")
            raise

    async def get_positions(self, position_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve judicial positions from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/positions/" + (f"{position_id}/" if position_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if position_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("position_type", "Unknown Position"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener positions fetch failed for position_id '{position_id}': {str(e)}")
            raise

    async def get_educations(self, education_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve education records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/educations/" + (f"{education_id}/" if education_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if education_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("school_name", "Unknown Education"),
                        "snippet": item.get("degree_detail", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener educations fetch failed for education_id '{education_id}': {str(e)}")
            raise

    async def get_schools(self, school_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve school information from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/schools/" + (f"{school_id}/" if school_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if school_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("name", "Unknown School"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener schools fetch failed for school_id '{school_id}': {str(e)}")
            raise

    async def get_political_affiliations(self, affiliation_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve political affiliations from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/political-affiliations/" + (f"{affiliation_id}/" if affiliation_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if affiliation_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("affiliation_type", "Unknown Affiliation"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener political affiliations fetch failed for affiliation_id '{affiliation_id}': {str(e)}")
            raise

    async def get_aba_ratings(self, rating_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve ABA ratings from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/aba-ratings/" + (f"{rating_id}/" if rating_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if rating_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("rating", "Unknown Rating"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener ABA ratings fetch failed for rating_id '{rating_id}': {str(e)}")
            raise

    async def get_parties(self, party_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve parties involved in cases from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/parties/" + (f"{party_id}/" if party_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if party_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("name", "Unknown Party"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener parties fetch failed for party_id '{party_id}': {str(e)}")
            raise

    async def get_attorneys(self, attorney_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve attorney information from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/attorneys/" + (f"{attorney_id}/" if attorney_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if attorney_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("name", "Unknown Attorney"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener attorneys fetch failed for attorney_id '{attorney_id}': {str(e)}")
            raise

    async def get_financial_disclosures(self, disclosure_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve financial disclosures from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/financial-disclosures/" + (f"{disclosure_id}/" if disclosure_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if disclosure_id else [])
                    return [{
                        "id": item["id"],
                        "title": f"Disclosure {item.get('year', 'N/A')}",
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener financial disclosures fetch failed for disclosure_id '{disclosure_id}': {str(e)}")
            raise

    async def get_investments(self, investment_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve investment records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/investments/" + (f"{investment_id}/" if investment_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if investment_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("description", "Unknown Investment"),
                        "snippet": item.get("details", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener investments fetch failed for investment_id '{investment_id}': {str(e)}")
            raise

    async def get_gifts(self, gift_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve gift records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/gifts/" + (f"{gift_id}/" if gift_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if gift_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("description", "Unknown Gift"),
                        "snippet": item.get("details", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener gifts fetch failed for gift_id '{gift_id}': {str(e)}")
            raise

    async def get_reimbursements(self, reimbursement_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve reimbursement records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/reimbursements/" + (f"{reimbursement_id}/" if reimbursement_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if reimbursement_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("description", "Unknown Reimbursement"),
                        "snippet": item.get("details", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener reimbursements fetch failed for reimbursement_id '{reimbursement_id}': {str(e)}")
            raise

    async def get_non_investment_incomes(self, income_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve non-investment income records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/non-investment-incomes/" + (f"{income_id}/" if income_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if income_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("description", "Unknown Income"),
                        "snippet": item.get("details", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener non-investment incomes fetch failed for income_id '{income_id}': {str(e)}")
            raise

    async def get_debts(self, debt_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve debt records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/debts/" + (f"{debt_id}/" if debt_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if debt_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("description", "Unknown Debt"),
                        "snippet": item.get("details", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener debts fetch failed for debt_id '{debt_id}': {str(e)}")
            raise

    async def get_agreements(self, agreement_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve agreement records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/agreements/" + (f"{agreement_id}/" if agreement_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if agreement_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("description", "Unknown Agreement"),
                        "snippet": item.get("details", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener agreements fetch failed for agreement_id '{agreement_id}': {str(e)}")
            raise

    async def get_disclosure_positions(self, position_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve disclosure position records from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/disclosure-positions/" + (f"{position_id}/" if position_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if position_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("position", "Unknown Position"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener disclosure positions fetch failed for position_id '{position_id}': {str(e)}")
            raise

    async def get_tags(self, tag_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve tags from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/tags/" + (f"{tag_id}/" if tag_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if tag_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("name", "Unknown Tag"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener tags fetch failed for tag_id '{tag_id}': {str(e)}")
            raise

    async def get_visualizations(self, visualization_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve visualizations from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/visualizations/" + (f"{visualization_id}/" if visualization_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if visualization_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("title", "Unknown Visualization"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener visualizations fetch failed for visualization_id '{visualization_id}': {str(e)}")
            raise

    async def get_visualizations_json(self, visualization_id: str = None, params: Optional[Dict] = None) -> List[Dict]:
        """Retrieve visualizations in JSON format from CourtListener."""
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = f"{self.BASE_URL}/visualizations-json/" + (f"{visualization_id}/" if visualization_id else "")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"CourtListener API returned status {response.status}")
                    data = await response.json()
                    results = data.get("results", [data] if visualization_id else [])
                    return [{
                        "id": item["id"],
                        "title": item.get("title", "Unknown Visualization JSON"),
                        "snippet": item.get("description", "")[:200],
                        "citation": "N/A",
                        "relevance": 0.85,
                        "source": "courtlistener"
                    } for item in results]
        except Exception as e:
            logger.error(f"CourtListener visualizations JSON fetch failed for visualization_id '{visualization_id}': {str(e)}")
            raise