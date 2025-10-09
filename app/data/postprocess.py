# File: lexforge-backend/app/data/postprocess.py
# This file defines the DataPostprocessor for post-processing API responses.

import logging

# Configure logging
logger = logging.getLogger(__name__)

class DataPostprocessor:
    """Class for post-processing data from legal APIs, including summarization."""
    def summarize(self, data: list, max_length: int = 200):
        """Summarize legal data from API responses, truncating long titles or descriptions."""
        try:
            summaries = []
            for item in data[:5]:  # Limit to 5 items for performance
                title = item.get("title", "")
                summary = title[:max_length] + ("..." if len(title) > max_length else "")
                summaries.append({"id": item.get("id"), "summary": summary})
            return summaries
        except Exception as e:
            logger.error(f"Postprocessing summary failed: {str(e)}")
            raise