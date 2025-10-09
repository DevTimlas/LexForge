# File: lexforge-backend/run_server.py (Convenience script)
#!/usr/bin/env python3
"""
LexForge Development Server Runner
"""
import uvicorn
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
