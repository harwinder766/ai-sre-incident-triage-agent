from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.analysis.schema import RemediationPlan
from app.tools.remediation import remediation_tool


async def execute_remediation(
    remediation: RemediationPlan | Mapping[str, Any],
) -> dict[str, Any]:

    if not remediation:
        raise ValueError("No remediation plan provided.")

    remediation_values = (
        remediation.model_dump()
        if isinstance(remediation, RemediationPlan)
        else remediation
    )

    action = remediation_values.get("action")

    if not action:
        raise ValueError("Remediation action is required.")

    parameters = remediation_values.get("parameters", {})

    if not isinstance(parameters, dict):
        raise ValueError(
            "Remediation parameters must be a dictionary."
        )

    return await remediation_tool.execute(
        action=action,
        parameters=parameters,
    )