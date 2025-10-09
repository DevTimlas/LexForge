# File: lexforge-backend/app/external_apis/__init__.py
# This file initializes the external_apis package, importing all API modules.
from .bailii_api import search_bailii_cases
from .courtlistener_api import CourtListenerAPI
from .echr_api import search_echr
from .eur_lex_api import search_eur_lex
from .google_search import google_search
from .icj_api import get_icj_judgments
from .int_caselaw_api import search_int_caselaw
from .legislation_api import (
    get_legislation_work, get_legislation_expression, get_legislation_manifestation,
    search_legislation_id, search_legislation, list_legislation,
    get_case_law_feed, get_case_law_deprecated_feed, get_case_law_document, get_case_law_document_format
)
from .pacer_api import get_pacer_data
from .regulatory_feeds import get_regulatory_updates
from .un_api import search_un_documents, search_pdf_attachment
from .wto_api import get_wto_cases