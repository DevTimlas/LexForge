# app/agents/evidence_vault_agent.py
# This file defines the EvidenceVaultAgent for storing and managing legal evidence from APIs.

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.security.blockchain_audit import BlockchainAudit
from app.models.evidence import Evidence
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
import logging
import uuid
from datetime import datetime
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class EvidenceVaultAgent(BaseAgent):
    """Agent for managing evidence vault, storing legal documents securely with blockchain auditing."""
    def __init__(self, upload_dir: str = "uploads"):
        super().__init__(upload_dir=upload_dir)
        self.logger = logging.getLogger(__name__)
        self.blockchain_audit = BlockchainAudit()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def store_evidence(self, data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Store evidence with blockchain audit."""
        try:
            description = data.get("description", "")
            evidence_type = data.get("evidence_type", "")
            associated_case = data.get("associated_case", "")
            file = data.get("file")
            content = description
            filename = "text_evidence.txt"
            if file:
                content = await file.read()
                filename = file.filename
            # Create evidence record
            evidence = Evidence(
                id=str(uuid.uuid4()),
                filename=filename,
                evidence_type=evidence_type,
                upload_date=datetime.utcnow(),
                chain_of_custody=json.dumps([{"action": "uploaded", "timestamp": datetime.utcnow().isoformat(), "user": "system"}]),
                status="secure",
                associated_case=associated_case,
                content=content.decode() if isinstance(content, bytes) else content
            )
            db.add(evidence)
            await db.commit()
            await db.refresh(evidence)
            await self.blockchain_audit.log_action(evidence_id=evidence.id, action=f"stored evidence file {evidence.filename}")
            return evidence.__dict__
        except Exception as e:
            self.logger.error(f"Failed to store evidence: {str(e)}")
            raise

    async def get_inventory(self, associated_case: str = None, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """Get evidence inventory."""
        stmt = select(Evidence)
        if associated_case:
            stmt = stmt.where(Evidence.associated_case == associated_case)
        result = await db.execute(stmt)
        evidences = result.scalars().all()
        return [evidence.__dict__ for evidence in evidences]

    async def get_summary(self, evidence_id: str, db: AsyncSession = None) -> Dict[str, Any]:
        """Get AI-generated summary."""
        stmt = select(Evidence).where(Evidence.id == evidence_id)
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")
        prompt = f"Summarize the following evidence content: {evidence.content[:2000]}"  # Limit to avoid token limits
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content
        return {"summary": summary, "evidence_id": evidence_id}

    async def get_chain_of_custody(self, evidence_id: str, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """Get chain of custody log."""
        stmt = select(Evidence.chain_of_custody).where(Evidence.id == evidence_id)
        result = await db.execute(stmt)
        coc = result.scalar()
        return json.loads(coc) if coc else []

    async def handle(self, request: Dict[str, Any], db: AsyncSession = None) -> Dict[str, Any]:
        """Handle evidence vault requests."""
        result = await self.store_evidence(request, db)
        provenance = await self._create_provenance(
            sources=["user_upload"],
            method="evidence_storage",
            confidence=0.95
        )
        final_result = {
            "data": result,
            "provenance": [provenance]
        }
        return final_result