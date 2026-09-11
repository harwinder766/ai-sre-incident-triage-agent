import hashlib
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import IncidentRepository
from app.graph.graph import graph


router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Alerts"],
)


def generate_incident_id(alert: dict[str, Any]) -> str:
    """
    Generate a stable incident ID from the Alertmanager fingerprint.

    Alertmanager provides the same fingerprint for the same alert
    identity, which allows us to detect duplicate alerts.
    """

    fingerprint = alert.get("fingerprint")

    if fingerprint:
        return f"INC-{fingerprint}"

    # Fallback if fingerprint is unavailable.
    labels = alert.get("labels", {})

    identity = "|".join(
        f"{key}={labels[key]}"
        for key in sorted(labels)
    )

    digest = hashlib.sha256(identity.encode()).hexdigest()[:12]

    return f"INC-{digest}"

def map_alert_severity(alert_severity: str | None) -> str:
    """
    Convert Alertmanager severity into our internal SEV level.
    """

    severity_mapping = {
        "critical": "SEV-1",
        "high": "SEV-1",
        "warning": "SEV-2",
        "medium": "SEV-2",
        "low": "SEV-3",
        "info": "SEV-4",
    }

    return severity_mapping.get(
        (alert_severity or "").lower(),
        "SEV-3",
    )


@router.post("/")
def receive_alert(
    payload: dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    Receive an alert from Prometheus Alertmanager,
    convert it into an incident, process it through
    LangGraph, and persist it in PostgreSQL.
    """

    print("🚨 Alert received from Alertmanager")

    alert_status = payload.get("status", "unknown")
    alerts = payload.get("alerts", [])

    repository = IncidentRepository(db)

    processed_incidents = []

    for alert in alerts:

        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        alert_name = labels.get(
            "alertname",
            "UnknownAlert",
        )

        service = labels.get(
            "service",
            "unknown-service",
        )

        alert_severity = labels.get(
            "severity",
            "warning",
        )

        summary = annotations.get(
            "summary",
            alert_name,
        )

        description = annotations.get(
            "description",
            summary,
        )

        incident_id = generate_incident_id(alert)

        print(
            f"Processing alert: {alert_name} | "
            f"service={service} | "
            f"severity={alert_severity} | "
            f"incident_id={incident_id}"
        )

        # --------------------------------------------------
        # Handle resolved alerts
        # --------------------------------------------------

        if alert_status == "resolved":

            existing_incident = repository.get_incident(
                incident_id
            )

            if existing_incident:

                repository.update_incident(
                    incident_id,
                    {
                        "status": "resolved",
                    },
                )

                processed_incidents.append(
                    {
                        "incident_id": incident_id,
                        "status": "resolved",
                    }
                )

            continue

        # --------------------------------------------------
        # Handle firing alerts
        # --------------------------------------------------

        existing_incident = repository.get_incident(
            incident_id
        )

        if existing_incident:

            print(
                f"Incident {incident_id} already exists. "
                "Updating existing incident."
            )

            repository.update_incident(
                incident_id,
                {
                    "status": "open",
                },
            )

            processed_incidents.append(
                {
                    "incident_id": incident_id,
                    "status": "already_exists",
                }
            )

            continue

        # Create new incident state

        initial_state = {
            "incident_id": incident_id,
            "service": service,
            "message": (
                f"{summary}. "
                f"{description}"
            ),
            "error_rate": 0.0,
        }

        # Process through LangGraph
        result = graph.invoke(initial_state)

        # Alertmanager is the source of the alert severity,
        # so preserve that severity instead of relying only
        # on the current temporary classifier.
        result["severity"] = map_alert_severity(
            alert_severity
        )

        # Store the incident
        repository.create_incident(result)

        processed_incidents.append(
            {
                "incident_id": incident_id,
                "status": "created",
                "service": service,
                "severity": result["severity"],
            }
        )

        print(
            f"✅ Incident created: {incident_id}"
        )

    return {
        "status": "processed",
        "alert_status": alert_status,
        "alerts_received": len(alerts),
        "incidents": processed_incidents,
    }
