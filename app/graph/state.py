from typing import TypedDict

class IncidentState(TypedDict, total=False):
    # Incident input
    incident_id: str
    service: str
    message: str
    error_rate: float

    # Incident classification
    category: str
    severity: str

    # Investigation
    investigation: str
    relevant_logs: list[str]
    relevant_metrics: dict[str,float]

    # Root cause analysis
    root_cause: str
    confidence: float

    # Remediation
    remediation: str

    # Final output
    final_response: str