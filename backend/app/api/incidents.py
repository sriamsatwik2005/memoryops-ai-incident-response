from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentOut, InvestigationOut
from app.agent.incident_agent import IncidentAgent

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

@router.get("", response_model=list[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()

@router.get("/{external_id}", response_model=IncidentOut)
def get_incident(external_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.external_id == external_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    return incident

@router.post("", response_model=IncidentOut)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.post("/{external_id}/investigate", response_model=InvestigationOut)
def investigate(external_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.external_id == external_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    agent = IncidentAgent()
    result = agent.investigate({
        "external_id": incident.external_id,
        "service": incident.service,
        "severity": incident.severity,
        "summary": incident.summary,
        "logs": incident.logs,
        "metrics": incident.metrics,
        "deployment": incident.deployment,
    })
    incident.root_cause = result["root_cause"]
    db.commit()
    return result

@router.post("/{external_id}/resolve", response_model=IncidentOut)
def resolve(external_id: str, resolution: str = "Approved recommended remediation", db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.external_id == external_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    incident.status = "RESOLVED"
    incident.resolution = resolution
    db.commit()
    db.refresh(incident)
    IncidentAgent().retain_resolution({
        "external_id": incident.external_id,
        "service": incident.service,
        "summary": incident.summary,
        "logs": incident.logs,
        "metrics": incident.metrics,
        "deployment": incident.deployment,
        "root_cause": incident.root_cause,
        "resolution": incident.resolution,
    })
    return incident
