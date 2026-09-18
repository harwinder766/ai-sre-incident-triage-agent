from __future__ import annotations

from typing import Any

from app.tools.github import github_tool


async def create_incident_issue(
    *,
    incident_id: str,
    service: str,
    severity: str,
    root_cause: str,
    confidence: float,
    reasoning: str,
    supporting_evidence: list[str],
    remediation: str,
    expected_impact: str,
    risks: list[str],
) -> dict[str, Any]:
    """
    Create a GitHub issue containing the incident analysis.
    """

    title = (
        f"[SRE Incident] "
        f"{incident_id} - "
        f"{service} - "
        f"{severity}"
    )

    evidence_text = "\n".join(
        f"- {evidence}"
        for evidence in supporting_evidence
    )

    risks_text = "\n".join(
        f"- {risk}"
        for risk in risks
    )

    body = f"""
# SRE Incident Report

## Incident

**Incident ID:** {incident_id}

**Service:** {service}

**Severity:** {severity}

---

## Root Cause

{root_cause}

**Model Confidence:** {confidence:.2f}

---

## Reasoning

{reasoning}

---

## Supporting Evidence

{evidence_text}

---

## Recommended Remediation

{remediation}

### Expected Impact

{expected_impact}

### Risks

{risks_text}

---

## Approval

This remediation was reviewed and approved through the
SRE incident triage workflow.
"""

    return await github_tool.create_issue(
        title=title,
        body=body,
        labels=["incident", severity.lower()],
    )
