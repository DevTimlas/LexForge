# File: lexforge-backend/app/agents/retrieval_agent.py
from typing import Dict, Any, List, Optional
import time
import asyncio
import re
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.agents.base_agent import BaseAgent
from app.models.document import Document
from app.embeddings.embedding_manager import EmbeddingManager
from app.external_apis.courtlistener_api import CourtListenerAPI
import logging
from numpy import dot
from numpy.linalg import norm
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class RetrievalAgent(BaseAgent):
    """Enhanced legal document and case law retrieval agent for the LexForge platform."""
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.embedding_manager = EmbeddingManager()
        self.courtlistener_api = CourtListenerAPI()
        self.capabilities = [
            "legal_document_search",
            "case_law_retrieval",
            "semantic_search",
            "citation_verification",
            "jurisdiction_filtering"
        ]
        self.knowledge_sources = [
            "case_law_database",
            "statutory_database",
            "legal_journals"
        ]
        self.logger = logger

    @lru_cache(maxsize=1000)
    def _is_citation_query(self, query: str) -> bool:
        """Detect if query is a legal citation (cached for performance)."""
        citation_patterns = [
            r'\d+\s+[A-Z][a-z]*\.?\s*\d*d?\s+\d+',  # Federal reporter
            r'\d+\s+U\.S\.?\s+\d+',  # Supreme Court
            r'\d+\s+S\.?\s*Ct\.?\s+\d+',  # Supreme Court
            r'\d+\s+[A-Z][a-z]*\.?\s*App\.?\s+\d+'  # State appellate
        ]
        return any(re.search(pattern, query) for pattern in citation_patterns)

    async def _is_semantic_query(self, query: str) -> bool:
        """Detect if query requires semantic search (based on length or complexity)."""
        try:
            return len(query.split()) > 5 or any(keyword in query.lower() for keyword in ["issue", "ruling", "precedent"])
        except Exception as e:
            self.logger.error(f"Failed to detect semantic query: {str(e)}")
            raise

    async def _retrieve_by_citation(self, citation: str, jurisdiction: str, db: AsyncSession) -> List[Dict]:
        """Retrieve documents by citation from database or CourtListener API."""
        try:
            # Check local database
            result = await db.execute(select(Document).where(Document.citation == citation, Document.jurisdiction == jurisdiction))
            doc = result.scalars().first()
            if doc:
                return [{
                    "id": doc.id,
                    "title": doc.title or doc.filename,
                    "snippet": doc.content[:200] if doc.content else "",
                    "citation": doc.citation,
                    "relevance": 0.9,
                    "source": "local_database"
                }]
            # Fallback to CourtListener API
            api_results = await self.courtlistener_api.search_courtlistener(citation, jurisdiction)
            return api_results
        except Exception as e:
            self.logger.error(f"Failed to retrieve by citation {citation}: {str(e)}")
            raise

    async def _semantic_retrieval(self, query: str, jurisdiction: str, filters: Dict, db: AsyncSession) -> List[Dict]:
        """Perform semantic retrieval using embeddings."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_manager.generate_embedding(query)
            # Query local documents
            local_results = await self._search_local(query_embedding, jurisdiction, filters, db)
            # Query CourtListener API with fallback
            external_results = []
            try:
                external_results = await self.courtlistener_api.search_courtlistener(query, jurisdiction)
            except Exception as e:
                self.logger.warning(f"CourtListener API failed for query '{query[:100]}...': {str(e)}. Falling back to local results.")
            # Combine and rank results
            combined_results = local_results + external_results
            return self._rank_results(combined_results, query_embedding)
        except Exception as e:
            self.logger.error(f"Failed to perform semantic retrieval for {query[:100]}...: {str(e)}")
            raise

    async def _keyword_retrieval(self, query: str, jurisdiction: str, filters: Dict, db: AsyncSession) -> List[Dict]:
        """Perform keyword-based retrieval."""
        try:
            # Query local database
            query_str = f"%{query}%"
            stmt = select(Document).where(Document.content.ilike(query_str))
            if jurisdiction:
                stmt = stmt.where(Document.jurisdiction == jurisdiction)
            if filters.get("case_id"):
                stmt = stmt.where(Document.case_id == filters["case_id"])
            if filters.get("document_type"):
                stmt = stmt.where(Document.classification == filters["document_type"])
            result = await db.execute(stmt)
            docs = result.scalars().all()
            local_results = [{
                "id": doc.id,
                "title": doc.title or doc.filename,
                "snippet": doc.content[:200] if doc.content else "",
                "citation": doc.citation or "N/A",
                "relevance": 0.8,
                "source": "local_database"
            } for doc in docs]
            # Query CourtListener API with fallback
            external_results = []
            try:
                external_results = await self.courtlistener_api.search_courtlistener(query, jurisdiction)
            except Exception as e:
                self.logger.warning(f"CourtListener API failed for query '{query[:100]}...': {str(e)}. Falling back to local results.")
            return local_results + external_results
        except Exception as e:
            self.logger.error(f"Failed to perform keyword retrieval for {query[:100]}...: {str(e)}")
            raise

    async def _search_local(self, query_embedding: List[float], jurisdiction: str, filters: Dict, db: AsyncSession) -> List[Dict]:
        """Search local documents using vector similarity."""
        try:
            stmt = select(Document)
            if jurisdiction:
                stmt = stmt.where(Document.jurisdiction == jurisdiction)
            if filters.get("case_id"):
                stmt = stmt.where(Document.case_id == filters["case_id"])
            if filters.get("document_type"):
                stmt = stmt.where(Document.classification == filters["document_type"])
            result = await db.execute(stmt)
            docs = result.scalars().all()
            results = []
            for doc in docs:
                if doc.embedding:
                    similarity = await self.embedding_manager.compare_embeddings(query_embedding, doc.embedding)
                    results.append({
                        "id": doc.id,
                        "title": doc.title or doc.filename,
                        "snippet": doc.content[:200] if doc.content else "",
                        "citation": doc.citation or "N/A",
                        "relevance": similarity,
                        "source": "local_database"
                    })
            return sorted(results, key=lambda x: x["relevance"], reverse=True)[:filters.get("limit", 20)]
        except Exception as e:
            self.logger.error(f"Failed to search local documents: {str(e)}")
            raise

    def _rank_results(self, results: List[Dict], query_embedding: List[float]) -> List[Dict]:
        """Rank combined results based on relevance."""
        for result in results:
            if "embedding" in result and query_embedding:
                similarity = dot(query_embedding, result["embedding"]) / (norm(query_embedding) * norm(result["embedding"]))
                result["relevance"] = max(result.get("relevance", 0), similarity)
        return sorted(results, key=lambda x: x.get("relevance", 0), reverse=True)

    async def search(self, query: str, jurisdiction: Optional[str], db: AsyncSession, filters: Dict = {}, limit: int = 20) -> List[Dict]:
        """Main search method for the Legal Research tab."""
        start_time = time.time()
        try:
            filters["limit"] = limit
            if self._is_citation_query(query):
                results = await self._retrieve_by_citation(query, jurisdiction, db)
            elif await self._is_semantic_query(query):
                results = await self._semantic_retrieval(query, jurisdiction, filters, db)
            else:
                results = await self._keyword_retrieval(query, jurisdiction, filters, db)
            duration = time.time() - start_time
            self.logger.info(f"Search completed in {duration:.2f} seconds for query: {query[:100]}...")
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise

    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy handle method for compatibility."""
        query = request.get("query", "")
        jurisdiction = request.get("jurisdiction", None)
        filters = request.get("filters", {})
        limit = request.get("limit", 20)
        db = request.get("db")
        results = await self.search(query, jurisdiction, db, filters, limit)
        provenance = await self._create_provenance(
            sources=[r["source"] for r in results],
            method="legal_retrieval",
            confidence=max(r.get("relevance", 0) for r in results) if results else 0.8
        )
        return {
            "data": {"documents": results},
            "provenance": [provenance],
            "query_metadata": {
                "original_query": query,
                "jurisdiction": jurisdiction,
                "results_count": len(results)
            }
        }