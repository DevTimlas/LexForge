# File: lexforge-backend/app/agents/orchestrator_agent.py
# This file defines the OrchestratorAgent for coordinating tasks across multiple agents.

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.classification_agent import ClassificationAgent
from app.agents.generation_agent import GenerationAgent
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    """Agent for orchestrating tasks across multiple agents.
    This agent coordinates retrieval, classification, and generation for legal queries.
    """
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.logger = logging.getLogger(__name__)
        self.retrieval_agent = RetrievalAgent(upload_dir=upload_dir)
        self.classification_agent = ClassificationAgent(upload_dir=upload_dir)
        self.generation_agent = GenerationAgent(upload_dir=upload_dir)

    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle orchestrated workflows for legal queries."""
        start_time = time.time()
        try:
            query = request.get("query", "")
            jurisdiction = request.get("jurisdiction", "US_FEDERAL")
            if not query:
                return {"error": "Query is required for orchestration"}
            # Step 1: Retrieve data from APIs
            retrieval_result = await self.retrieval_agent.handle(request)
            if "error" in retrieval_result:
                raise ValueError(f"Retrieval failed: {retrieval_result['error']}")
            documents = retrieval_result["data"].get("documents", [])

            # Step 2: Classify retrieved documents
            classification_results = []
            for doc in documents[:5]:  # Limit to 5 documents for performance
                classification_result = await self.classification_agent.handle({
                    "content": doc.get("content", ""),
                    "classification_type": "document",
                    "jurisdiction": jurisdiction
                })
                if "error" not in classification_result:
                    classification_results.append(classification_result["data"])

            # Step 3: Generate response based on retrieved and classified data
            generation_result = await self.generation_agent.handle({
                "query": query,
                "generation_type": "legal_memo",
                "jurisdiction": jurisdiction,
                "retrieved_documents": documents,
                "context": {"classifications": classification_results}
            })
            if "error" in generation_result:
                raise ValueError(f"Generation failed: {generation_result['error']}")

            # Aggregate results
            final_result = {
                "retrieved_documents": documents,
                "classifications": classification_results,
                "generated_memo": generation_result["data"],
                "confidence": min(
                    retrieval_result["data"].get("confidence", 0.95),
                    generation_result["data"].get("confidence", 0.95)
                ),
                "sources": (
                    retrieval_result["data"].get("sources", []) +
                    generation_result["data"].get("sources", [])
                )
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