# File: lexforge-backend/app/data/loaders.py
# This file defines the DataLoader for loading data from legal APIs.
import logging
from typing import List, Dict, Any
from app.external_apis.courtlistener_api import CourtListenerAPI
from app.external_apis.legislation_api import (
    get_legislation_work, get_legislation_expression, get_legislation_manifestation,
    search_legislation_id, search_legislation, list_legislation,
    get_case_law_feed, get_case_law_deprecated_feed, get_case_law_document, get_case_law_document_format
)

# Configure logging
logger = logging.getLogger(__name__)

class DataLoader:
    """Class for loading data from legal APIs, handling XML and JSON responses."""
    def __init__(self):
        self.courtlistener_api = CourtListenerAPI()

    async def load_legislation(self, query: str) -> List[Dict[str, Any]]:
        """Load UK legislation data from Legislation.gov.uk API."""
        try:
            results = await search_legislation(title=query)
            return results  # Already a list of dicts from legislation_api
        except Exception as e:
            logger.error(f"Legislation load failed for query '{query}': {str(e)}")
            raise

    async def load_case_law(self, query: str) -> List[Dict[str, Any]]:
        """Load UK case law data from National Archives API."""
        try:
            results = await get_case_law_feed(query=query)
            return results  # Already a list of dicts from legislation_api
        except Exception as e:
            logger.error(f"Case law load failed for query '{query}': {str(e)}")
            raise

    async def load_us_case_law(self, query: str) -> List[Dict[str, Any]]:
        """Load US case law data from CourtListener API."""
        try:
            results = await self.courtlistener_api.search_courtlistener(query=query)
            return results
        except Exception as e:
            logger.error(f"US case law load failed for query '{query}': {str(e)}")
            raise

    async def load_us_case_by_id(self, case_id: str) -> Dict[str, Any]:
        """Load a specific US case by ID from CourtListener API."""
        try:
            result = await self.courtlistener_api.courtlistener_request(case_id=case_id)
            return result
        except Exception as e:
            logger.error(f"US case load failed for case_id '{case_id}': {str(e)}")
            raise

    async def load_clusters(self, cluster_id: str = None) -> List[Dict[str, Any]]:
        """Load case clusters from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_clusters(cluster_id=cluster_id)
            return result
        except Exception as e:
            logger.error(f"Clusters load failed for cluster_id '{cluster_id}': {str(e)}")
            raise

    async def load_opinions(self, opinion_id: str = None) -> List[Dict[str, Any]]:
        """Load opinions from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_opinions(opinion_id=opinion_id)
            return result
        except Exception as e:
            logger.error(f"Opinions load failed for opinion_id '{opinion_id}': {str(e)}")
            raise

    async def load_dockets(self, docket_id: str = None) -> List[Dict[str, Any]]:
        """Load dockets from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_dockets(docket_id=docket_id)
            return result
        except Exception as e:
            logger.error(f"Dockets load failed for docket_id '{docket_id}': {str(e)}")
            raise

    async def load_docket_entries(self, entry_id: str = None) -> List[Dict[str, Any]]:
        """Load docket entries from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_docket_entries(entry_id=entry_id)
            return result
        except Exception as e:
            logger.error(f"Docket entries load failed for entry_id '{entry_id}': {str(e)}")
            raise

    async def load_recap_documents(self, document_id: str = None) -> List[Dict[str, Any]]:
        """Load RECAP documents from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_recap_documents(document_id=document_id)
            return result
        except Exception as e:
            logger.error(f"RECAP documents load failed for document_id '{document_id}': {str(e)}")
            raise

    async def load_courts(self, court_id: str = None) -> List[Dict[str, Any]]:
        """Load court information from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_courts(court_id=court_id)
            return result
        except Exception as e:
            logger.error(f"Courts load failed for court_id '{court_id}': {str(e)}")
            raise

    async def load_audio(self, audio_id: str = None) -> List[Dict[str, Any]]:
        """Load audio files from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_audio(audio_id=audio_id)
            return result
        except Exception as e:
            logger.error(f"Audio load failed for audio_id '{audio_id}': {str(e)}")
            raise

    async def load_people(self, person_id: str = None) -> List[Dict[str, Any]]:
        """Load people (e.g., judges) information from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_people(person_id=person_id)
            return result
        except Exception as e:
            logger.error(f"People load failed for person_id '{person_id}': {str(e)}")
            raise

    async def load_positions(self, position_id: str = None) -> List[Dict[str, Any]]:
        """Load judicial positions from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_positions(position_id=position_id)
            return result
        except Exception as e:
            logger.error(f"Positions load failed for position_id '{position_id}': {str(e)}")
            raise

    async def load_educations(self, education_id: str = None) -> List[Dict[str, Any]]:
        """Load education records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_educations(education_id=education_id)
            return result
        except Exception as e:
            logger.error(f"Educations load failed for education_id '{education_id}': {str(e)}")
            raise

    async def load_schools(self, school_id: str = None) -> List[Dict[str, Any]]:
        """Load school information from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_schools(school_id=school_id)
            return result
        except Exception as e:
            logger.error(f"Schools load failed for school_id '{school_id}': {str(e)}")
            raise

    async def load_political_affiliations(self, affiliation_id: str = None) -> List[Dict[str, Any]]:
        """Load political affiliations from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_political_affiliations(affiliation_id=affiliation_id)
            return result
        except Exception as e:
            logger.error(f"Political affiliations load failed for affiliation_id '{affiliation_id}': {str(e)}")
            raise

    async def load_aba_ratings(self, rating_id: str = None) -> List[Dict[str, Any]]:
        """Load ABA ratings from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_aba_ratings(rating_id=rating_id)
            return result
        except Exception as e:
            logger.error(f"ABA ratings load failed for rating_id '{rating_id}': {str(e)}")
            raise

    async def load_parties(self, party_id: str = None) -> List[Dict[str, Any]]:
        """Load parties involved in cases from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_parties(party_id=party_id)
            return result
        except Exception as e:
            logger.error(f"Parties load failed for party_id '{party_id}': {str(e)}")
            raise

    async def load_attorneys(self, attorney_id: str = None) -> List[Dict[str, Any]]:
        """Load attorney information from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_attorneys(attorney_id=attorney_id)
            return result
        except Exception as e:
            logger.error(f"Attorneys load failed for attorney_id '{attorney_id}': {str(e)}")
            raise

    async def load_financial_disclosures(self, disclosure_id: str = None) -> List[Dict[str, Any]]:
        """Load financial disclosures from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_financial_disclosures(disclosure_id=disclosure_id)
            return result
        except Exception as e:
            logger.error(f"Financial disclosures load failed for disclosure_id '{disclosure_id}': {str(e)}")
            raise

    async def load_investments(self, investment_id: str = None) -> List[Dict[str, Any]]:
        """Load investment records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_investments(investment_id=investment_id)
            return result
        except Exception as e:
            logger.error(f"Investments load failed for investment_id '{investment_id}': {str(e)}")
            raise

    async def load_gifts(self, gift_id: str = None) -> List[Dict[str, Any]]:
        """Load gift records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_gifts(gift_id=gift_id)
            return result
        except Exception as e:
            logger.error(f"Gifts load failed for gift_id '{gift_id}': {str(e)}")
            raise

    async def load_reimbursements(self, reimbursement_id: str = None) -> List[Dict[str, Any]]:
        """Load reimbursement records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_reimbursements(reimbursement_id=reimbursement_id)
            return result
        except Exception as e:
            logger.error(f"Reimbursements load failed for reimbursement_id '{reimbursement_id}': {str(e)}")
            raise

    async def load_non_investment_incomes(self, income_id: str = None) -> List[Dict[str, Any]]:
        """Load non-investment income records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_non_investment_incomes(income_id=income_id)
            return result
        except Exception as e:
            logger.error(f"Non-investment incomes load failed for income_id '{income_id}': {str(e)}")
            raise

    async def load_debts(self, debt_id: str = None) -> List[Dict[str, Any]]:
        """Load debt records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_debts(debt_id=debt_id)
            return result
        except Exception as e:
            logger.error(f"Debts load failed for debt_id '{debt_id}': {str(e)}")
            raise

    async def load_agreements(self, agreement_id: str = None) -> List[Dict[str, Any]]:
        """Load agreement records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_agreements(agreement_id=agreement_id)
            return result
        except Exception as e:
            logger.error(f"Agreements load failed for agreement_id '{agreement_id}': {str(e)}")
            raise

    async def load_disclosure_positions(self, position_id: str = None) -> List[Dict[str, Any]]:
        """Load disclosure position records from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_disclosure_positions(position_id=position_id)
            return result
        except Exception as e:
            logger.error(f"Disclosure positions load failed for position_id '{position_id}': {str(e)}")
            raise

    async def load_tags(self, tag_id: str = None) -> List[Dict[str, Any]]:
        """Load tags from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_tags(tag_id=tag_id)
            return result
        except Exception as e:
            logger.error(f"Tags load failed for tag_id '{tag_id}': {str(e)}")
            raise

    async def load_visualizations(self, visualization_id: str = None) -> List[Dict[str, Any]]:
        """Load visualizations from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_visualizations(visualization_id=visualization_id)
            return result
        except Exception as e:
            logger.error(f"Visualizations load failed for visualization_id '{visualization_id}': {str(e)}")
            raise

    async def load_visualizations_json(self, visualization_id: str = None) -> List[Dict[str, Any]]:
        """Load visualizations in JSON format from CourtListener API."""
        try:
            result = await self.courtlistener_api.get_visualizations_json(visualization_id=visualization_id)
            return result
        except Exception as e:
            logger.error(f"Visualizations JSON load failed for visualization_id '{visualization_id}': {str(e)}")
            raise