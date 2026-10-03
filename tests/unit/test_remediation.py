import pytest

from app.adapters.simulator import register_simulator_adapters
from app.graph.nodes import execute_remediation_action, verify_remediation
from app.tools.remediation import remediation_tool


class SuccessfulPaymentAdapter:
    async def execute(self, parameters):
        return {
            "status": "success",
            "parameters": parameters,
        }


@pytest.mark.asyncio
async def test_registered_remediation_action_executes(monkeypatch):
    register_simulator_adapters()

    adapter = remediation_tool.adapters["increase_database_pool"]
    monkeypatch.setattr(
        adapter,
        "execute",
        SuccessfulPaymentAdapter().execute,
    )

    state = await execute_remediation_action(
        {
            "approval_status": "approved",
            "remediation": {
                "action": "increase_database_pool",
                "parameters": {"pool_size": 20},
            },
        }
    )

    assert state["execution_status"] == "completed"
    assert state["execution_result"]["action"] == "increase_database_pool"


@pytest.mark.asyncio
async def test_unsupported_remediation_skips_verification():
    state = await execute_remediation_action(
        {
            "approval_status": "approved",
            "remediation": {
                "action": "unsupported_action",
                "parameters": {},
            },
        }
    )

    assert state["execution_status"] == "failed"

    verified_state = await verify_remediation(state)

    assert verified_state["verification_status"] == "skipped"
