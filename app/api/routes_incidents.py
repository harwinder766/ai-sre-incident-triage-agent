from fastapi import APIRouter
from pydantic import BaseModel

from app.graph.graph import graph


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
def create_incident(incident: IncidentRequest):
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
    result = graph.invoke(initial_state)

    # Return the workflow result as JSON
    return result

