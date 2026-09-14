from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio

from app.graph.graph import graph
from app.db.database import get_db
from app.db.repository import IncidentRepository


# Create an API router
router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)


class IncidentRequest(BaseModel):
    incident_id: str
    service: str
    message: str
    error_rate: float = 0.0
    

@router.post("/")
async def create_incident(incident: IncidentRequest, db: Session =Depends(get_db)):
    """
    Receive an incident and send it to the LangGraph workflow.
    """
    # Convert the API request into the state expected by LangGraph
    initial_state = {
        "incident_id": incident.incident_id,
        "service": incident.service,
        "message": incident.message,
        "error_rate": incident.error_rate,
    }

    # Run the LangGraph workflow
    result = await graph.ainvoke(initial_state)

    repository = IncidentRepository(db)

    repository.create_incident(result)

    # Return the workflow result as JSON
    return result

@router.get("/{incident_id}")
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve an incident from PostgreSQL.
    """

    repository = IncidentRepository(db)

    incident = repository.get_incident(incident_id)

    if incident is None:
        return {"error": "Incident not found"}

    return {
        "incident_id": incident.incident_id,
        "service": incident.service,
        "message": incident.message,
        "error_rate": incident.error_rate,
        "category": incident.category,
        "severity": incident.severity,
        "investigation": incident.investigation,
        "root_cause": incident.root_cause,
        "confidence": incident.confidence,
        "remediation": incident.remediation,
        "status": incident.status,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
    }

