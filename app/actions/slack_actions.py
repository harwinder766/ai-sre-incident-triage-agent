from __future__ import annotations

from typing import Any

from app.tools.slack import slack_tool


async def notify_incident(
    *,
    incident_id: str,
    service: str,
    severity: str,
    root_cause: str,
    confidence: float,
    remediation: str,
    approval_status: str,
    github_issue_url: str | None = None,
) -> dict[str, Any]:
    """
    Send an incident notification to Slack.
    """

    github_section = ""

    if github_issue_url:
        github_section = (
            f"\nGitHub Issue: {github_issue_url}"
        )

    message = f"""
🚨 SRE Incident Update

Incident: {incident_id}
Service: {service}
Severity: {severity}

Root Cause:
{root_cause}

Confidence:
{confidence:.2f}

Recommended Remediation:
{remediation}

Approval Status:
{approval_status}
{github_section}
"""

    return await slack_tool.send_message(message)