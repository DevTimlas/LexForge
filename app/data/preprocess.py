# File: lexforge-backend/app/data/preprocess.py
# This file defines the DataPreprocessor for preprocessing legal documents.

import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Class for preprocessing data from legal APIs, including text cleaning."""
    def clean_text(self, text: str):
        """Clean legal document text by removing XML tags and extra whitespace."""
        try:
            # Remove XML tags and normalize whitespace
            text = re.sub(r"<[^>]+>", "", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        except Exception as e:
            logger.error(f"Preprocessing clean text failed: {str(e)}")
            raise