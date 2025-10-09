# File: lexforge-backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
import logging
from app.config import settings
from app.db.session import init_db
from app.api.v1 import endpoints
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.auth import router as auth_router
from app.api.v1.document import router as documents_router
from app.api.v1 import (
    analytics, simulation, evidence_vault,
    privilege_firewall, regulatory_radar,
    peer_verification, compliance, audit
)
from app.api.v1.metrics import router as metrics_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.cases import router as cases_router
from app.api.v1.ai import router as ai_router  # Added new AI router
from app.api.v1.calendar import router as calendar_router  # Add this

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LexForge - Legal Intelligence Platform",
    description="AI-powered legal research and case analysis platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting LexForge application")
    await init_db()
    logger.info("Database initialization completed")

# Include routers with explicit prefixes
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(metrics_router, prefix="/api/v1/metrics")
app.include_router(alerts_router, prefix="/api/v1/alerts")
app.include_router(dashboard_router, prefix="/api/v1/dashboard")
app.include_router(documents_router, prefix="/api/v1/documents")
app.include_router(endpoints.router, prefix="/api/v1/endpoints")
app.include_router(analytics.router, prefix="/api/v1/analytics")
app.include_router(simulation.router, prefix="/api/v1/simulation")
app.include_router(evidence_vault.router, prefix="/api/v1/evidence-vault")
app.include_router(privilege_firewall.router, prefix="/api/v1/privilege-firewall")
app.include_router(regulatory_radar.router, prefix="/api/v1/regulatory-radar")
app.include_router(peer_verification.router, prefix="/api/v1/peer-verification")
app.include_router(compliance.router, prefix="/api/v1/compliance")
app.include_router(audit.router, prefix="/api/v1/audit")
app.include_router(cases_router, prefix="/api/v1/cases")
app.include_router(ai_router, prefix="/api/v1/ai")  # Added new AI router
app.include_router(calendar_router, prefix="/api/v1")

# Serve frontend static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Frontend route
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend application"""
    frontend_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head><title>LexForge API</title></head>
            <body>
                <h1>LexForge Legal Intelligence Platform API</h1>
                <p>API Documentation: <a href="/api/docs">/api/docs</a></p>
            </body>
            </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "lexforge-api", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENV == "development" else False,
        log_level="info"
    )