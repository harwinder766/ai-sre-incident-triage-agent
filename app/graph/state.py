from typing import Any, TypedDict


class IncidentState(TypedDict, total=False):
    incident_id: str
    service: str
    message: str
    error_rate: float

    category: str
    severity: str

    investigation: str

    relevant_logs: list[str]
    relevant_metrics: dict[str, Any]
    recent_commits: list[dict[str, Any]]

    root_cause: str
    confidence: float
    reasoning: str
    supporting_evidence: list[str]
    
    remediation: str
    expected_impact: str
    risks: list[str]
    
    approval_status: str
    approval_reason: str

    github_issue: dict[str, Any]
    slack_notification: dict[str, Any]

    final_response: str