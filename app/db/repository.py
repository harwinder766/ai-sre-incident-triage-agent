import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis.schema import RemediationPlan

from .models import Incident


class IncidentRepository:

    def __init__(self, session: Session):
        self.session = session

    def create_incident(self, incident_data: dict) -> Incident:
        """
        Create a new incident in the database.
        """

        remediation = incident_data.get("remediation")
        if isinstance(remediation, RemediationPlan):
            remediation = remediation.model_dump_json()

        incident = Incident(
            incident_id=incident_data["incident_id"],
            service=incident_data["service"],
            message=incident_data["message"],
            error_rate=incident_data.get("error_rate", 0.0),
            category=incident_data.get("category"),
            severity=incident_data.get("severity"),
            investigation=incident_data.get("investigation"),
            root_cause=incident_data.get("root_cause"),
            confidence=incident_data.get("confidence"),
            reasoning=incident_data.get("reasoning"),
            supporting_evidence=json.dumps(
                incident_data.get("supporting_evidence", [])
            ),
            expected_impact=incident_data.get("expected_impact"),
            risks=json.dumps(
                incident_data.get("risks", [])
            ),
            remediation=remediation,
            thread_id=incident_data.get("thread_id"),
            approval_status=incident_data.get(
                "approval_status",
                "pending",
            ),
            approval_reason=incident_data.get("approval_reason"),
            status=incident_data.get("status", "open"),
        )

        self.session.add(incident)
        self.session.commit()
        self.session.refresh(incident)

        return incident

    def get_incident(self, incident_id: str) -> Incident | None:
        """
        Get a single incident using its incident_id.
        """

        statement = select(Incident).where(
            Incident.incident_id == incident_id
        )

        return self.session.scalar(statement)

    def update_incident(
        self,
        incident_id: str,
        updates: dict,
    ) -> Incident | None:
        """
        Update an existing incident.
        """

        incident = self.get_incident(incident_id)

        if incident is None:
            return None

        for field, value in updates.items():

            if hasattr(incident, field):
                setattr(incident, field, value)

        self.session.commit()
        self.session.refresh(incident)

        return incident

    def list_incidents(self) -> list[Incident]:
        """
        Return all incidents.
        """
        
        statement = select(Incident).order_by(
            Incident.created_at.desc()
        )

        return list(self.session.scalars(statement).all())