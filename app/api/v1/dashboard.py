# File: lexforge-backend/app/api/v1/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio
import uuid

from app.services.agent_service import AgentService
from app.services.user_service import UserService
from app.services.data_service import DataService
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.simulation_agent import SimulationAgent
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Pydantic Models
class AnalysisRequest(BaseModel):
    jurisdiction: str
    analysis_type: str
    case_description: Optional[str] = None
    documents: Optional[List[str]] = None

class AIQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    session_id: Optional[str] = None

class MetricsResponse(BaseModel):
    active_cases: int
    win_rate: float
    revenue_generated: float
    ai_queries_today: int
    accuracy_rate: float
    time_saved_per_case: float
    citation_verification_rate: float

class AlertItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime
    priority: str
    status: str

class DashboardStats(BaseModel):
    metrics: MetricsResponse
    alerts: List[AlertItem]
    recent_activity: List[Dict[str, Any]]

# Dashboard endpoints
@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(UserService.get_current_user)
):
    """Get comprehensive dashboard statistics"""
    try:
        analytics_agent = AnalyticsAgent()
        
        # Get user-specific metrics
        metrics = await analytics_agent.get_user_metrics(current_user.id)
        
        # Get alerts
        alerts = await analytics_agent.get_user_alerts(current_user.id)
        
        # Get recent activity
        activity = await analytics_agent.get_recent_activity(current_user.id)
        
        return DashboardStats(
            metrics=metrics,
            alerts=alerts,
            recent_activity=activity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")

@router.post("/analysis/start")
async def start_case_analysis(
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    files: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(UserService.get_current_user)
):
    """Start comprehensive case analysis with document processing"""
    try:
        # Generate analysis session ID
        session_id = str(uuid.uuid4())
        
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Process uploaded files if any
        processed_files = []
        if files:
            data_service = DataService()
            for file in files:
                processed_file = await data_service.process_upload(
                    file, current_user.id, session_id
                )
                processed_files.append(processed_file)
        
        # Start analysis in background
        background_tasks.add_task(
            orchestrator.start_analysis,
            session_id,
            analysis_request,
            processed_files,
            current_user.id
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "message": "Analysis initiated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@router.get("/analysis/{session_id}/status")
async def get_analysis_status(
    session_id: str,
    current_user: User = Depends(UserService.get_current_user)
):
    """Get real-time analysis status"""
    try:
        orchestrator = OrchestratorAgent()
        status = await orchestrator.get_analysis_status(session_id, current_user.id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Analysis session not found: {str(e)}")

@router.get("/analysis/{session_id}/stream")
async def stream_analysis_results(
    session_id: str,
    current_user: User = Depends(UserService.get_current_user)
):
    """Stream real-time analysis results"""
    async def generate_stream():
        orchestrator = OrchestratorAgent()
        async for chunk in orchestrator.stream_analysis_results(session_id, current_user.id):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/ai/query")
async def handle_ai_query(
    query_request: AIQueryRequest,
    current_user: User = Depends(UserService.get_current_user)
):
    """Handle AI assistant queries with context awareness"""
    try:
        orchestrator = OrchestratorAgent()
        
        response = await orchestrator.process_ai_query(
            query_request.query,
            current_user.id,
            context=query_request.context,
            session_id=query_request.session_id
        )
        
        return {
            "response": response,
            "session_id": query_request.session_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

@router.get("/ai/suggestions")
async def get_ai_suggestions(
    context: Optional[str] = None,
    current_user: User = Depends(UserService.get_current_user)
):
    """Get contextual AI suggestions"""
    try:
        orchestrator = OrchestratorAgent()
        suggestions = await orchestrator.get_contextual_suggestions(
            current_user.id, context
        )
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.post("/simulation/start")
async def start_case_simulation(
    case_facts: str = Form(...),
    jurisdiction: str = Form(...),
    opposing_strategy: Optional[str] = Form(None),
    current_user: User = Depends(UserService.get_current_user)
):
    """Start adversarial case simulation"""
    try:
        simulation_agent = SimulationAgent()
        
        simulation_id = str(uuid.uuid4())
        
        simulation_result = await simulation_agent.start_simulation(
            simulation_id,
            case_facts,
            jurisdiction,
            opposing_strategy,
            current_user.id
        )
        
        return {
            "simulation_id": simulation_id,
            "initial_analysis": simulation_result,
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.get("/simulation/{simulation_id}/results")
async def get_simulation_results(
    simulation_id: str,
    current_user: User = Depends(UserService.get_current_user)
):
    """Get detailed simulation results"""
    try:
        simulation_agent = SimulationAgent()
        results = await simulation_agent.get_simulation_results(
            simulation_id, current_user.id
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Simulation not found: {str(e)}")

@router.get("/jurisdictions")
async def get_available_jurisdictions():
    """Get list of supported jurisdictions"""
    jurisdictions = [
        {"code": "US_FEDERAL", "name": "Federal Courts (US)", "description": "US Federal Court System"},
        {"code": "US_NY", "name": "New York State", "description": "New York State Courts"},
        {"code": "US_CA", "name": "California State", "description": "California State Courts"},
        {"code": "UK_HC", "name": "UK High Court", "description": "England & Wales High Court"},
        {"code": "EU_CJEU", "name": "EU Court of Justice", "description": "Court of Justice of the European Union"},
        {"code": "UK_SC", "name": "UK Supreme Court", "description": "Supreme Court of the United Kingdom"},
        {"code": "CA_SCC", "name": "Supreme Court of Canada", "description": "Canada Supreme Court"},
        {"code": "AU_HCA", "name": "High Court of Australia", "description": "Australia High Court"},
    ]
    return {"jurisdictions": jurisdictions}

@router.get("/alerts")
async def get_user_alerts(
    limit: int = 10,
    current_user: User = Depends(UserService.get_current_user)
):
    """Get user-specific alerts and notifications"""
    try:
        analytics_agent = AnalyticsAgent()
        alerts = await analytics_agent.get_user_alerts(current_user.id, limit=limit)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    current_user: User = Depends(UserService.get_current_user)
):
    """Dismiss a specific alert"""
    try:
        analytics_agent = AnalyticsAgent()
        success = await analytics_agent.dismiss_alert(alert_id, current_user.id)
        if success:
            return {"status": "dismissed"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to dismiss alert: {str(e)}")

@router.get("/performance/metrics")
async def get_performance_metrics(
    period: str = "30d",
    current_user: User = Depends(UserService.get_current_user)
):
    """Get detailed performance metrics"""
    try:
        analytics_agent = AnalyticsAgent()
        metrics = await analytics_agent.get_performance_metrics(
            current_user.id, period
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    feedback_type: str = Form(...),
    rating: int = Form(...),
    comments: str = Form(...),
    feature: Optional[str] = Form(None),
    current_user: User = Depends(UserService.get_current_user)
):
    """Submit user feedback"""
    try:
        analytics_agent = AnalyticsAgent()
        feedback_id = await analytics_agent.submit_feedback(
            current_user.id,
            feedback_type,
            rating,
            comments,
            feature
        )
        return {"feedback_id": feedback_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")
