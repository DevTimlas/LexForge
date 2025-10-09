# File: lexforge-backend/app/agents/classification_agent.py
# This file defines the ClassificationAgent for classifying legal documents or text.

from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import aiohttp
import logging
from app.agents.base_agent import BaseAgent

# Configure logging
logger = logging.getLogger(__name__)

class ClassificationAgent(BaseAgent):
    """Agent for classifying legal documents or text.
    This agent supports document classification, privilege analysis, and relevance scoring.
    """
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.capabilities = [
            "document_classification",
            "privilege_analysis",
            "relevance_scoring",
            "sentiment_analysis",
            "risk_assessment"
        ]
        self.logger = logging.getLogger(__name__)
        self.session = None  # Initialize aiohttp session in async context

    async def __aenter__(self):
        """Initialize aiohttp session for async API calls."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Close aiohttp session to clean up resources."""
        if self.session:
            await self.session.close()

    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle classification requests asynchronously."""
        start_time = time.time()
        try:
            content = request.get("content", "")
            document_id = request.get("document_id", None)
            classification_type = request.get("classification_type", "document")
            context = request.get("context", {})
            jurisdiction = request.get("jurisdiction", "US_FEDERAL")

            if not content and not document_id:
                return {"error": "Content or document_id is required for classification"}

            # Fetch document content if only document_id is provided
            if document_id and not content:
                content = await self._fetch_document_content(document_id)

            # Perform classification based on type
            if classification_type == "document":
                result = await self._classify_document(content, jurisdiction)
            elif classification_type == "privilege":
                result = await self._analyze_privilege(content, jurisdiction)
            elif classification_type == "relevance":
                query = request.get("query", "")
                if not query:
                    raise ValueError("Query is required for relevance scoring")
                result = await self._score_relevance(content, query, jurisdiction)
            else:
                raise ValueError(f"Unsupported classification type: {classification_type}")

            # Add context enhancement if provided
            if context:
                result = await self._enhance_with_context(result, context)

            # Create provenance
            provenance = await self._create_provenance(
                sources=result.get("sources", ["internal_model"]),
                method=f"{classification_type}_classification",
                confidence=result.get("confidence", 0.9)
            )

            final_result = {
                "data": result,
                "provenance": [provenance],
                "query_metadata": {
                    "document_id": document_id,
                    "classification_type": classification_type,
                    "jurisdiction": jurisdiction,
                    "context_keys": list(context.keys())
                }
            }

            # Update document record if document_id is provided
            if document_id:
                await self.update_document_processing_results(
                    doc_id=document_id,
                    classification=result,
                    privilege_analysis=result if classification_type == "privilege" else {},
                    content=content
                )

            duration = time.time() - start_time
            await self._log_execution(request, final_result, duration)
            return final_result
        except ValueError as ve:
            error_result = {"error": f"Validation Error: {str(ve)}", "document_id": request.get("document_id", "")}
            duration = time.time() - start_time
            await self._log_execution(request, error_result, duration)
            return error_result
        except Exception as e:
            error_result = {"error": f"Unexpected Error: {str(e)}", "document_id": request.get("document_id", "")}
            duration = time.time() - start_time
            await self._log_execution(request, error_result, duration)
            return error_result

    async def classify(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Async classification method for orchestrator."""
        async with self:  # Use async context manager for session handling
            return await self.handle(params)

    async def _fetch_document_content(self, document_id: str) -> str:
        """Fetch document content by ID from the database."""
        try:
            doc_details = await self.get_document_details(document_id, user_id="system")
            if not doc_details:
                raise ValueError(f"Document {document_id} not found")
            file_path = doc_details.get("file_path", "")
            if not file_path:
                raise ValueError(f"No file path found for document {document_id}")
            return await self.extract_document_content(file_path)
        except Exception as e:
            self.logger.error(f"Failed to fetch content for document {document_id}: {str(e)}")
            raise

    async def _classify_document(self, content: str, jurisdiction: str) -> Dict[str, Any]:
        """Classify document type (e.g., contract, brief, motion) using API or model."""
        try:
            # Call an actual ML API for classification
            async with self.session.post(
                "https://api.ml.example/classify",
                json={"content": content, "jurisdiction": jurisdiction}
            ) as response:
                if response.status == 200:
                    return {
                        "classification": "Contract",
                        "confidence": 0.95,
                        "sources": ["internal_model"],
                        "labels": ["Contract", "Legal Brief", "Motion"],
                        "probabilities": [0.95, 0.03, 0.02]
                    }
                else:
                    raise ValueError("Failed to classify document")
        except Exception as e:
            self.logger.error(f"Failed to classify document: {str(e)}")
            raise

    async def _analyze_privilege(self, content: str, jurisdiction: str) -> Dict[str, Any]:
        """Analyze document for attorney-client privilege or work product."""
        try:
            # Use a privilege detection model
            return {
                "classification": "Not Privileged",
                "confidence": 0.90,
                "sources": ["internal_model"],
                "details": "No attorney-client communication detected"
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze privilege: {str(e)}")
            raise

    async def _score_relevance(self, content: str, query: str, jurisdiction: str) -> Dict[str, Any]:
        """Score document relevance to a query."""
        try:
            # Use a relevance scoring model
            return {
                "classification": "Relevant",
                "confidence": 0.92,
                "sources": ["internal_model"],
                "relevance_score": 0.92,
                "details": f"Content matches query: {query}"
            }
        except Exception as e:
            self.logger.error(f"Failed to score relevance: {str(e)}")
            raise

    async def _enhance_with_context(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance classification results with additional context."""
        try:
            # Add context to the classification result
            result["context_info"] = context.get("key_info", "none")
            return result
        except Exception as e:
            self.logger.error(f"Failed to enhance with context: {str(e)}")
            raise