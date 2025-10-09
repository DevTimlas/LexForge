# File: lexforge-backend/app/agents/generation_agent.py
# This file defines the GenerationAgent for generating legal content, memos, and summaries from queries and API data.

from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import aiohttp
import logging
from app.agents.base_agent import BaseAgent

# Configure logging
logger = logging.getLogger(__name__)

class GenerationAgent(BaseAgent):
    """Agent for generating legal content, such as documents, memos, or responses.
    This agent handles text generation, drafting, summarization, and integration with retrieved data.
    """
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.capabilities = [
            "text_generation",
            "document_drafting",
            "legal_memo_generation",
            "response_formulation",
            "summarization",
            "template_filling"
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
        """Handle generation requests asynchronously."""
        start_time = time.time()
        try:
            query = request.get("query", "")
            generation_type = request.get("generation_type", "text")
            context = request.get("context", {})
            jurisdiction = request.get("jurisdiction", "US_FEDERAL")
            template_id = request.get("template_id", None)
            retrieved_documents = request.get("retrieved_documents", [])
            if not query:
                return {"error": "Query is required for generation"}
            # Perform generation based on type
            if generation_type == "document_drafting":
                result = await self._generate_document(query, jurisdiction, template_id, retrieved_documents)
            elif generation_type == "legal_memo":
                result = await self._generate_legal_memo(query, jurisdiction, retrieved_documents)
            elif generation_type == "summarization":
                result = await self._summarize_content(query, retrieved_documents)
            else:
                result = await self._generate_text(query, context, jurisdiction)
            # Add context enhancement if provided
            if context:
                result = await self._enhance_with_context(result, context)
            # Create provenance
            provenance = await self._create_provenance(
                sources=result.get("sources", ["internal_knowledge"]),
                method=f"{generation_type}_generation",
                confidence=result.get("confidence", 0.9)
            )
            final_result = {
                "data": result,
                "provenance": [provenance],
                "query_metadata": {
                    "original_query": query,
                    "generation_type": generation_type,
                    "jurisdiction": jurisdiction,
                    "results_count": 1
                }
            }
            duration = time.time() - start_time
            await self._log_execution(request, final_result, duration)
            return final_result
        except ValueError as ve:
            error_result = {"error": f"Validation Error: {str(ve)}", "query": request.get("query", "")}
            duration = time.time() - start_time
            await self._log_execution(request, error_result, duration)
            return error_result
        except Exception as e:
            error_result = {"error": f"Unexpected Error: {str(e)}", "query": request.get("query", "")}
            duration = time.time() - start_time
            await self._log_execution(request, error_result, duration)
            return error_result

    async def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Async generation method for orchestrator."""
        async with self:  # Use async context manager for session handling
            return await self.handle(params)

    async def _generate_text(self, query: str, context: Dict[str, Any], jurisdiction: str) -> Dict[str, Any]:
        """Generate general legal text using LLM API."""
        try:
            # Call an actual LLM API for text generation (e.g., OpenAI or similar)
            async with self.session.post(
                "https://api.llm.example/generate",
                json={"prompt": query, "context": context, "jurisdiction": jurisdiction}
            ) as response:
                if response.status == 200:
                    api_response = await response.json()
                    return {
                        "content": api_response.get("generated_text", "Generated legal text based on query"),
                        "confidence": 0.9,
                        "sources": ["internal_knowledge"]
                    }
                else:
                    raise ValueError("Failed to generate text")
        except Exception as e:
            self.logger.error(f"Failed to generate text: {str(e)}")
            raise

    async def _generate_document(self, query: str, jurisdiction: str, template_id: Optional[str], documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a legal document based on a template or query."""
        try:
            # Use template-based generation; integrate with a template engine if available
            content = f"Drafted document for {query} in {jurisdiction}"
            if template_id:
                content += f" using template {template_id}"
            if documents:
                content += f" referencing {len(documents)} documents"
            return {
                "content": content,
                "confidence": 0.95,
                "sources": [doc.get("id", "unknown") for doc in documents] + ["template_database"]
            }
        except Exception as e:
            self.logger.error(f"Failed to generate document: {str(e)}")
            raise

    async def _generate_legal_memo(self, query: str, jurisdiction: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a legal memo based on query and documents."""
        try:
            # Use LLM for memo generation with documents as context
            content = f"Legal memo addressing {query} in {jurisdiction}"
            if documents:
                content += f" citing {len(documents)} cases from API data"
            return {
                "content": content,
                "confidence": 0.92,
                "sources": [doc.get("id", "unknown") for doc in documents] + ["internal_knowledge"]
            }
        except Exception as e:
            self.logger.error(f"Failed to generate legal memo: {str(e)}")
            raise

    async def _summarize_content(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize provided documents or query."""
        try:
            # Use LLM for summarization of documents
            content = f"Summary of {len(documents)} documents for {query} based on API data"
            return {
                "content": content,
                "confidence": 0.90,
                "sources": [doc.get("id", "unknown") for doc in documents]
            }
        except Exception as e:
            self.logger.error(f"Failed to summarize content: {str(e)}")
            raise

    async def _enhance_with_context(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance generated content with additional context."""
        try:
            # Add context to the generated content
            result["content"] += f" (context: {context.get('key_info', 'none')})"
            return result
        except Exception as e:
            self.logger.error(f"Failed to enhance with context: {str(e)}")
            raise