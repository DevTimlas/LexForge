# File: lexforge-backend/app/utils/security.py
# This file defines utility functions for security-related operations.

import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_id() -> str:
    """Generate a unique identifier."""
    try:
        return str(uuid.uuid4())
    except Exception as e:
        logger.error(f"Failed to generate ID: {str(e)}")
        raise