from __future__ import annotations

from typing import Any

from app.tools.remediation import remediation_tool


async def execute_remediation(
    remediation: dict[str, Any],
) -> dict[str, Any]:

    if not remediation:
        raise ValueError("No remediation plan provided.")

    action = remediation.get("action")

    if not action:
        raise ValueError("Remediation action is required.")

    parameters = remediation.get("parameters", {})

    if not isinstance(parameters, dict):
        raise ValueError(
            "Remediation parameters must be a dictionary."
        )

    return await remediation_tool.execute(
        action=action,
        parameters=parameters,
    )