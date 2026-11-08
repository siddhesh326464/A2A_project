from pydantic import BaseModel
from typing import Optional


class FinancialRequest(BaseModel):
    """Payload received from the orchestrator."""
    question: str
    request_id: Optional[str] = ""


class FinancialResponse(BaseModel):
    """A2A-compliant payload returned to the orchestrator."""
    response: str
    agent: str = "financial"
    request_id: Optional[str] = ""

