# File: lexforge-backend/app/api/v1/ai.py
# Enhanced AI-related API endpoints with autonomous agent decision-making
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.agents.retrieval_agent import RetrievalAgent
from openai import OpenAI
import logging
import os
import json
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing import TypedDict
import asyncio
from io import BytesIO

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai"])
class AIQueryRequest(BaseModel):
    prompt: str
    jurisdiction: str = None
    session_id: str = None
    user_context: Dict[str, Any] = {} # Additional user context
class AgentState(TypedDict):
    prompt: str
    user_context: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    analysis: Dict[str, Any] # LLM's analysis of the query
    search_strategy: Dict[str, Any] # LLM-determined search approach
    db: AsyncSession
    case_results: List[Dict]
    final_response: str
class AutonomousLegalAgent:
    """Fully autonomous agent that uses LLM for all decision-making."""
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OpenAI API key is missing")
        self.graph = self._build_graph()
    def _build_graph(self) -> CompiledStateGraph:
        """Build a flexible workflow where LLM makes all routing decisions."""
        graph = StateGraph(AgentState)
        graph.add_node("analyze_query", self._analyze_query)
        graph.add_node("determine_search_strategy", self._determine_search_strategy)
        graph.add_node("execute_search", self._execute_search)
        graph.add_node("generate_response", self._generate_response)
        graph.add_node("handle_simple_query", self._handle_simple_query)
        # LLM decides the flow based on analysis
        graph.add_conditional_edges(
            "analyze_query",
            self._route_based_on_analysis,
            {
                "search_required": "determine_search_strategy",
                "simple_response": "handle_simple_query"
            }
        )
        graph.add_edge("determine_search_strategy", "execute_search")
        graph.add_edge("execute_search", "generate_response")
        graph.add_edge("handle_simple_query", END)
        graph.add_edge("generate_response", END)
        graph.set_entry_point("analyze_query")
        return graph.compile()
    async def _analyze_query(self, state: AgentState) -> AgentState:
        """Let LLM analyze the query and determine its characteristics."""
        analysis_prompt = f"""
        Analyze the following user query for a legal research platform. Provide a JSON response with your analysis:
        User Query: "{state['prompt']}"
        User Context: {json.dumps(state.get('user_context', {}), indent=2)}
        Conversation History: {json.dumps(state.get('conversation_history', [])[-3:], indent=2)}
        Analyze and respond in JSON format:
{{
            "query_type": "greeting|legal_research|case_search|legal_advice|clarification|other",
            "complexity": "simple|moderate|complex",
            "requires_case_search": true|false,
            "emotional_tone": "casual|formal|urgent|frustrated|curious",
            "user_intent": "detailed description of what user is trying to achieve",
            "jurisdiction_hints": ["any jurisdiction clues from the query"],
            "key_legal_concepts": ["list of legal concepts mentioned"],
            "search_terms": ["optimized terms for legal search if needed"],
            "response_style": "conversational|formal|educational|step_by_step",
            "confidence_level": 0.0-1.0,
            "requires_followup_questions": true|false,
            "reasoning": "explanation of your analysis"
}}
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4.1-nano", # Using more capable model for analysis
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1 # Low temperature for consistent analysis
            )
            analysis_text = response.choices[0].message.content.strip()
            logger.debug(f"Raw analysis response: {analysis_text[:500]}...")
            # Extract JSON from response
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            elif "```" in analysis_text:
                # Handle cases where JSON is in code blocks without language specification
                parts = analysis_text.split("```")
                if len(parts) >= 3:
                    analysis_text = parts[1]
            # Clean up the JSON text
            analysis_text = analysis_text.strip()
            analysis = json.loads(analysis_text)
            logger.info(f"Query analysis successful: {analysis.get('query_type')} - {analysis.get('user_intent')}")
            return {**state, "analysis": analysis}
        except Exception as e:
            logger.error(f"Query analysis failed: {str(e)}")
            logger.debug(f"Failed analysis text: {analysis_text if 'analysis_text' in locals() else 'No response received'}")
            # Fallback analysis
            fallback_analysis = {
                "query_type": "legal_research",
                "complexity": "moderate",
                "requires_case_search": True,
                "emotional_tone": "formal",
                "user_intent": "General legal research",
                "search_terms": [state['prompt'][:100]], # Limit length
                "response_style": "conversational",
                "confidence_level": 0.3
            }
            return {**state, "analysis": fallback_analysis}
    def _route_based_on_analysis(self, state: AgentState) -> str:
        """Route based on LLM analysis."""
        analysis = state.get("analysis", {})
        # Simple queries that don't need search
        if (analysis.get("query_type") == "greeting" or
            not analysis.get("requires_case_search", True) or
            analysis.get("complexity") == "simple" and analysis.get("query_type") in ["clarification", "other"]):
            return "simple_response"
        return "search_required"
    async def _determine_search_strategy(self, state: AgentState) -> AgentState:
        """Let LLM determine the optimal search strategy."""
        analysis = state.get("analysis", {})
        strategy_prompt = f"""
        Based on the query analysis, determine the optimal search strategy for a legal database.
        Query: "{state['prompt']}"
        Analysis: {json.dumps(analysis, indent=2)}
        Determine the search strategy in JSON format:
{{
            "jurisdiction": "best jurisdiction to search (scotus|ca|ny|tx|federal|state|null)",
            "jurisdiction_reasoning": "why this jurisdiction",
            "search_queries": ["list of 1-3 optimized search queries"],
            "search_filters": {{
                "date_range": "recent|last_5_years|last_10_years|all|null",
                "case_type": "civil|criminal|constitutional|all|null",
                "court_level": "supreme|appellate|trial|all|null"
}},
            "expected_result_count": "number of results needed (5|10|20)",
            "search_priority": "precision|recall|balanced",
            "fallback_searches": ["alternative search terms if primary fails"]
}}
        Jurisdiction Guidance:
        - Use 'scotus' specifically for U.S. Supreme Court cases, especially if the query mentions 'Supreme Court' or 'SCOTUS'.
        - Use 'federal' only for general U.S. federal court cases that are not specifically Supreme Court.
        - Use state codes like 'ca', 'ny', 'tx' for state-specific queries.
        - If no clear jurisdiction or if broad search is needed, use 'null' to search without jurisdiction filter.
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": strategy_prompt}],
                temperature=0.1
            )
            strategy_text = response.choices[0].message.content.strip()
            logger.debug(f"Raw strategy response: {strategy_text[:500]}...")
            if "```json" in strategy_text:
                strategy_text = strategy_text.split("```json")[1].split("```")[0]
            elif "```" in strategy_text:
                parts = strategy_text.split("```")
                if len(parts) >= 3:
                    strategy_text = parts[1]
            strategy_text = strategy_text.strip()
            search_strategy = json.loads(strategy_text)
            logger.info(f"Search strategy determined: {search_strategy.get('jurisdiction')} - {len(search_strategy.get('search_queries', []))} queries")
            return {**state, "search_strategy": search_strategy}
        except Exception as e:
            logger.error(f"Search strategy determination failed: {str(e)}")
            logger.debug(f"Failed strategy text: {strategy_text if 'strategy_text' in locals() else 'No response received'}")
            # Fallback strategy
            fallback_strategy = {
                "jurisdiction": "scotus",
                "search_queries": [state['prompt'][:100]], # Limit length
                "expected_result_count": "10",
                "search_priority": "balanced"
            }
            return {**state, "search_strategy": fallback_strategy}
    async def _execute_search(self, state: AgentState) -> AgentState:
        """Execute search using LLM-determined strategy."""
        search_strategy = state.get("search_strategy", {})
        db = state.get("db")
        if not db:
            logger.error("Database session is None")
            return {**state, "case_results": []}
        retrieval_agent = RetrievalAgent()
        all_results = []
        jurisdiction = search_strategy.get("jurisdiction")
        # Post-LLM jurisdiction mapping for robustness
        if jurisdiction == "federal" and "supreme court" in state['prompt'].lower():
            jurisdiction = "scotus"
            logger.info(f"Mapped jurisdiction from 'federal' to 'scotus' based on query content")
        elif jurisdiction == "state":
            jurisdiction = None  # Broad search if generic state
        search_queries = search_strategy.get("search_queries", [state['prompt']])
        # Primary searches
        for query in search_queries:
            try:
                request = {
                    "query": query,
                    "jurisdiction": jurisdiction,
                    "db": db,
                    "filters": search_strategy.get("search_filters", {}),
                    "limit": int(search_strategy.get("expected_result_count", "10"))
                }
                # If jurisdiction is None, assume RetrievalAgent handles it by omitting filter
                agent_response = await retrieval_agent.handle(request)
                results = agent_response.get("data", {}).get("documents", [])
                all_results.extend(results)
                logger.info(f"Search query '{query[:100]}' in jurisdiction '{jurisdiction}' returned {len(results)} results")
                if len(all_results) >= 5:
                    break
            except Exception as e:
                logger.warning(f"Search query '{query[:100]}' failed: {str(e)}")
                continue
        # Fallback searches if few results
        if len(all_results) < 3:
            fallback_jurisdictions = ["scotus", None] if jurisdiction else [None]
            for fallback_jur in fallback_jurisdictions:
                if len(all_results) >= 3:
                    break
                for fallback_query in search_strategy.get("fallback_searches", []) or search_queries:
                    try:
                        request = {
                            "query": fallback_query,
                            "jurisdiction": fallback_jur,
                            "db": db,
                            "filters": {},
                            "limit": 10
                        }
                        agent_response = await retrieval_agent.handle(request)
                        results = agent_response.get("data", {}).get("documents", [])
                        all_results.extend(results)
                        logger.info(f"Fallback search '{fallback_query[:100]}' in jurisdiction '{fallback_jur}' returned {len(results)} results")
                    except Exception as e:
                        logger.warning(f"Fallback search failed: {str(e)}")
        # Remove duplicates and limit results
        seen_ids = set()
        unique_results = []
        for result in all_results:
            result_id = result.get('id') or result.get('citation', str(result))
            if result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)
        return {**state, "case_results": unique_results[:15]}
    async def _handle_simple_query(self, state: AgentState) -> AgentState:
        """Handle simple queries that don't require case search."""
        analysis = state.get("analysis", {})
        conversation_history = state.get("conversation_history", [])
        # Build context from conversation history
        context_str = ""
        if conversation_history:
            recent_context = conversation_history[-2:] # Last 2 exchanges
            context_str = "\n".join([f"Previous: {item['prompt']} -> {item['response'][:200]}..."
                                     for item in recent_context])
        simple_prompt = f"""
        You are a helpful legal research assistant. Respond to this query appropriately:
        Query: "{state['prompt']}"
        Query Type: {analysis.get('query_type', 'unknown')}
        User Intent: {analysis.get('user_intent', 'unknown')}
        Preferred Style: {analysis.get('response_style', 'conversational')}
        Emotional Tone Detected: {analysis.get('emotional_tone', 'neutral')}
        Recent Conversation Context:
{context_str}
        Provide a helpful, appropriate response. If this is a greeting, be welcoming and explain how you can help with legal research. If it's a simple question, answer directly and offer to help with more complex legal research if needed.
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": simple_prompt}],
                temperature=0.3
            )
            final_response = response.choices[0].message.content
            logger.info(f"Simple query handled: {analysis.get('query_type')}")
            return {**state, "final_response": final_response}
        except Exception as e:
            logger.error(f"Simple query handling failed: {str(e)}")
            return {**state, "final_response": "I'm here to help with your legal research. How can I assist you today?"}
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate comprehensive response using all available context."""
        analysis = state.get("analysis", {})
        search_strategy = state.get("search_strategy", {})
        case_results = state.get("case_results", [])
        conversation_history = state.get("conversation_history", [])
        # Build comprehensive context
        case_context = ""
        if case_results:
            case_context = "\n\nRelevant Legal Cases:\n" + "\n".join([
                f"• {case.get('title', 'Unknown Title')} ({case.get('citation', 'No Citation')})\n"
                f" Summary: {case.get('snippet', case.get('content', 'No summary available')[:300])}\n"
                for case in case_results[:5]
            ])
        else:
            case_context = "\n\nNo relevant cases found in initial search. Providing general guidance based on known legal principles."
        conversation_context = ""
        if conversation_history:
            recent_exchanges = conversation_history[-2:]
            conversation_context = "\n\nRecent Conversation:\n" + "\n".join([
                f"User: {exchange['prompt']}\nAssistant: {exchange['response'][:200]}..."
                for exchange in recent_exchanges
            ])
        response_prompt = f"""
        You are an expert legal research assistant. Provide a comprehensive response to the user's query.
        Original Query: "{state['prompt']}"
        Analysis Results:
        - Query Type: {analysis.get('query_type')}
        - User Intent: {analysis.get('user_intent')}
        - Complexity: {analysis.get('complexity')}
        - Preferred Response Style: {analysis.get('response_style', 'conversational')}
        - Key Legal Concepts: {', '.join(analysis.get('key_legal_concepts', []))}
        Search Information:
        - Jurisdiction Searched: {search_strategy.get('jurisdiction', 'multiple')}
        - Cases Found: {len(case_results)}
{case_context}
{conversation_context}
        Instructions:
        1. Address the user's query directly and comprehensively
        2. Use the case law context where relevant, citing specific cases
        3. Match the preferred response style ({analysis.get('response_style', 'conversational')})
        4. If the query is complex, break down your response into clear sections
        5. Include practical implications where appropriate
        6. If case results are limited or not relevant, acknowledge this and provide general legal guidance
        7. Always maintain accuracy and note when information might need verification by a legal professional
        Provide a complete, helpful response (never start the response with "As an AI language model"). or Certainly, here is a detailed response. or Similar phrases. and don't end with "If you have any more questions, feel free to ask.", or "Let me know if you need further assistance." If it's a report.:
        """
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": response_prompt}],
                temperature=0.2,
                max_tokens=1500
            )
            final_response = response.choices[0].message.content
            logger.info(f"Generated comprehensive response ({len(final_response)} chars)")
            return {**state, "final_response": final_response}
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            fallback_response = f"I understand you're asking about {analysis.get('user_intent', 'a legal matter')}. While I encountered an issue generating a detailed response, I can help you with legal research. Please try rephrasing your question or ask for specific aspects you'd like to explore."
            return {**state, "final_response": fallback_response}
    async def process_query(self, prompt: str, db: AsyncSession, jurisdiction: str = None,
                            user_context: Dict = None, session_id: str = None) -> Dict[str, Any]:
        """Process query with full autonomy."""
        state = {
            "prompt": prompt,
            "user_context": user_context or {},
            "conversation_history": [], # Could load from session_id/database
            "analysis": {},
            "search_strategy": {},
            "db": db, # Pass database session through state
            "case_results": [],
            "final_response": ""
        }
        # Execute the workflow
        result = await self.graph.ainvoke(state)
        return {
            "result": result.get("final_response", "I apologize, but I couldn't process your request properly."),
            "response": result.get("final_response", "I apologize, but I couldn't process your request properly."), # Fallback for frontend compatibility
            "analysis": result.get("analysis", {}),
            "search_strategy": result.get("search_strategy", {}),
            "cases": result.get("case_results", [])[:5], # Top 5 cases
            "total_cases_found": len(result.get("case_results", [])),
            "session_id": session_id,
            "tone": result.get("analysis", {}).get("emotional_tone", "neutral"),
            "intent": result.get("analysis", {}).get("user_intent", "unknown")
        }
# Global agent instance
autonomous_agent = AutonomousLegalAgent()
@router.post("/ai-query")
async def ai_query(
    query: AIQueryRequest,
    db_session=Depends(get_db)
):
    """Process an AI query with fully autonomous decision-making."""
    async with db_session as db:
        try:
            response = await autonomous_agent.process_query(
                prompt=query.prompt,
                db=db, # Pass database session directly
                jurisdiction=query.jurisdiction,
                user_context=query.user_context,
                session_id=query.session_id
            )
            logger.info(f"Autonomous AI query processed successfully: {query.prompt[:100]}... "
                        f"Analysis: {response['analysis'].get('query_type', 'unknown')}, "
                        f"Response length: {len(response.get('result', ''))}")
            return response
        except Exception as e:
            logger.error(f"AI query failed: {str(e)}", exc_info=True)
            # Return a properly formatted error response for frontend compatibility
            return {
                "result": f"I encountered an issue processing your request: {str(e)}. Please try rephrasing your question.",
                "response": f"I encountered an issue processing your request: {str(e)}. Please try rephrasing your question.",
                "analysis": {"query_type": "error", "user_intent": "unknown"},
                "search_strategy": {},
                "cases": [],
                "total_cases_found": 0,
                "session_id": query.session_id,
                "tone": "neutral",
                "intent": "error"
            }

@router.post("/voice-agent")
async def voice_agent(
    audio: UploadFile = File(...),
    db_session=Depends(get_db)
):
    """Process voice input: transcribe and then query the AI."""
    async with db_session as db:
        try:
            content = await audio.read()
            file = BytesIO(content)
            # Transcribe audio using Whisper
            transcription_response = await asyncio.to_thread(
                autonomous_agent.client.audio.transcriptions.create,
                model="whisper-1",
                file=file
            )
            transcript = transcription_response.text
            # Process the transcript as AI query
            response = await autonomous_agent.process_query(
                prompt=transcript,
                db=db,
                jurisdiction=None,
                user_context={},
                session_id=None
            )
            logger.info(f"Voice agent processed: Transcript '{transcript[:100]}...'")
            return {**response, "transcript": transcript}
        except Exception as e:
            logger.error(f"Voice agent failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to process voice input: {str(e)}")

@router.post("/ai-feedback")
async def ai_feedback(
    session_id: str,
    feedback: Dict[str, Any]
):
    """Collect feedback to improve agent performance."""
    try:
        # Store feedback for agent improvement
        logger.info(f"Feedback received for session {session_id}: {feedback}")
        return {"status": "feedback_received", "message": "Thank you for your feedback!"}
    except Exception as e:
        logger.error(f"Feedback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process feedback")