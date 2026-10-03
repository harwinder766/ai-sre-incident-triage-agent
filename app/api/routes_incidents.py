import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio
from uuid import uuid4

from app.db.database import get_db
from app.db.repository import IncidentRepository
from app.db.models import Incident
from langgraph.types import Command


def serialize_incident(
    incident: Incident,
    workflow_state: dict | None = None,
) -> dict:
    serialized = {
        "incident_id": incident.incident_id,
        "service": incident.service,
        "message": incident.message,
        "error_rate": incident.error_rate,
        "category": incident.category,
        "severity": incident.severity,
        "investigation": incident.investigation,
        "root_cause": incident.root_cause,
        "confidence": incident.confidence,
        "reasoning": incident.reasoning,
        "supporting_evidence": json.loads(
            incident.supporting_evidence
        ) if incident.supporting_evidence else [],
        "expected_impact": incident.expected_impact,
        "risks": json.loads(
            incident.risks
        ) if incident.risks else [],
        "remediation": incident.remediation,
        "thread_id": incident.thread_id,
        "approval_status": incident.approval_status,
        "approval_reason": incident.approval_reason,
        "status": incident.status,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
    }

    serialized["relevant_metrics"] = (
        workflow_state.get("relevant_metrics", {})
        if workflow_state is not None
        else {}
    )
    serialized["relevant_logs"] = (
        workflow_state.get("relevant_logs", [])
        if workflow_state is not None
        else []
    )
    serialized["recent_commits"] = (
        workflow_state.get("recent_commits", [])
        if workflow_state is not None
        else []
    )

    for field in (
        "execution_status",
        "execution_result",
        "verification_status",
        "verification_result",
    ):
        serialized[field] = (
            workflow_state.get(field)
            if workflow_state is not None
            else None
        )

    return serialized

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


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str | None = None
    

@router.post("/")
async def create_incident(
    incident: IncidentRequest,
    request: Request,
    db: Session = Depends(get_db),
):
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
    thread_id = f"incident-{incident.incident_id}-{uuid4().hex}"
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = await request.app.state.graph.ainvoke(
        initial_state,
        config=config,
    )
    result["thread_id"] = thread_id
    result["approval_status"] = "pending"
    result["approval_reason"] = None

    repository = IncidentRepository(db)

    repository.create_incident(result)

    # Return the workflow result as JSON
    return result


@router.post("/{incident_id}/approval")
async def approve_incident(
    incident_id: str,
    approval: ApprovalRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Resume a paused incident workflow with an approval decision.
    """

    repository = IncidentRepository(db)
    incident_record = repository.get_incident(incident_id)

    if incident_record is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    if incident_record.approval_status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Incident is not pending approval",
        )

    if not incident_record.thread_id:
        raise HTTPException(
            status_code=409,
            detail="Incident has no workflow thread ID",
        )

    config = {
        "configurable": {
            "thread_id": incident_record.thread_id,
        }
    }

    result = await request.app.state.graph.ainvoke(
        Command(
            resume={
                "decision": approval.decision,
                "reason": approval.reason or "",
            }
        ),
        config=config,
    )

    repository.update_incident(
        incident_id,
        {
            "approval_status": result.get(
                "approval_status",
                "approved"
                if approval.decision == "approve"
                else "rejected",
            ),
            "approval_reason": result.get(
                "approval_reason",
                approval.reason,
            ),
        },
    )

    updated_incident = repository.get_incident(incident_id)

    if updated_incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found after approval",
        )

    return serialize_incident(
        updated_incident,
        workflow_state=result,
    )

@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Retrieve an incident from PostgreSQL.
    """

    repository = IncidentRepository(db)

    incident = repository.get_incident(incident_id)

    if incident is None:
        return {"error": "Incident not found"}

    workflow_state = None
    if incident.thread_id:
        state_snapshot = await request.app.state.graph.aget_state(
            {
                "configurable": {
                    "thread_id": incident.thread_id,
                }
            }
        )
        workflow_state = state_snapshot.values

    return serialize_incident(
        incident,
        workflow_state=workflow_state,
    )

@router.get('/')
def list_incidents(
    db: Session = Depends(get_db),
):
    """
    List all incidents from PostgreSQL.
    """

    repository = IncidentRepository(db)

    incidents = repository.list_incidents()

    return [
        serialize_incident(incident)
        for incident in incidents
    ]