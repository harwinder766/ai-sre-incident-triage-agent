from __future__ import annotations

from typing import Any


class RemediationTool:
    """
    Generic interface for executing an approved remediation.

    This layer does not know how a particular remediation is performed.
    Environment-specific implementations should be handled by adapters.
    """

    def __init__(self, adapters: dict[str, Any] | None = None):
        self.adapters = adapters or {}

    def register_adapter(
        self,
        action: str,
        adapter: Any,
    ) -> None:
        """
        Register an implementation for a remediation action.
        """
        self.adapters[action] = adapter

    async def execute(
        self,
        action: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        if not action:
            raise ValueError("Remediation action is required.")

        parameters = parameters or {}

        adapter = self.adapters.get(action)

        if adapter is None:
            raise ValueError(
                f"No remediation adapter registered for action: {action}"
            )

        result = await adapter.execute(parameters)

        return {
            "action": action,
            "parameters": parameters,
            "result": result,
        }


remediation_tool = RemediationTool()