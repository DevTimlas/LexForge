# compliance.py
# -------------
# Handles compliance check endpoints for LexForge backend.
# TODO: Extend with jurisdiction selection, batch checks, and reporting.

from fastapi import APIRouter, Request
from app.compliance.gdpr import GDPRCompliance
from app.compliance.ccpa import CCPACompliance

router = APIRouter()

gdpr = GDPRCompliance()
ccpa = CCPACompliance()

@router.post("/check-compliance")
async def check_compliance(request: Request):
    """
    Runs GDPR and CCPA compliance checks on provided data.
    TODO: Add jurisdiction selection and batch processing.
    """
    data = await request.json()
    gdpr_result = gdpr.check(data)
    ccpa_result = ccpa.check(data)
    return {"gdpr": gdpr_result, "ccpa": ccpa_result}
