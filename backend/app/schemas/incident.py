from datetime import datetime
from pydantic import BaseModel

class IncidentCreate(BaseModel):
    external_id: str
    service: str
    severity: str = "HIGH"
    summary: str
    logs: str = ""
    metrics: str = ""
    deployment: str = ""

class IncidentOut(IncidentCreate):
    id: int
    status: str
    root_cause: str | None = None
    resolution: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}

class InvestigationOut(BaseModel):
    incident_id: str
    root_cause: str
    confidence: float
    recommendation: list[str]
    reasoning: str
    memories: list[dict]
