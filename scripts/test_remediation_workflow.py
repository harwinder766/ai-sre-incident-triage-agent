import asyncio

from langgraph.types import Command

from app.main import app
from app.adapters.simulator import register_simulator_adapters
from app.tools.remediation import remediation_tool


async def run_remediation_workflow():
    """
    End-to-end test for the remediation workflow.

    Flow:

    ingest
        ↓
    classify
        ↓
    investigate
        ↓
    analyze
        ↓
    human approval
        ↓
    external actions
        ↓
    remediation
        ↓
    verification
        ↓
    final response
    """

    # ---------------------------------------------------------
    # 1. Register simulator remediation adapter
    # ---------------------------------------------------------

    register_simulator_adapters()

    # ---------------------------------------------------------
    # 2. Incident input
    # ---------------------------------------------------------

    incident = {
        "incident_id": "TEST-REMEDIATION-001",
        "service": "payment-api",
        "message": "Database connection pool exhausted",
        "error_rate": 0.65,
    }

    # ---------------------------------------------------------
    # 3. LangGraph configuration
    # ---------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": "test-remediation-workflow-001"
        }
    }

    # ---------------------------------------------------------
    # 4. Start workflow
    # ---------------------------------------------------------

    print("\n🔹 Starting remediation workflow...")

    async with app.router.lifespan_context(app):
        graph = app.state.graph

        await graph.ainvoke(
            incident,
            config=config,
        )

        # ---------------------------------------------------------
        # 5. Check that workflow stopped at approval
        # ---------------------------------------------------------

        state = await graph.aget_state(config)

        assert state is not None

        print("\n🔹 Workflow reached approval step.")

        print("Next node:", state.next)

        assert state.next == ("request_approval",)

        # ---------------------------------------------------------
        # 6. Read approval request
        # ---------------------------------------------------------

        approval_request = state.tasks[0].interrupts[0].value

        print("\n🔹 Approval request:")
        print(approval_request)

        assert approval_request["incident_id"] == "TEST-REMEDIATION-001"
        assert approval_request["service"] == "payment-api"

        assert "root_cause" in approval_request
        assert "remediation" in approval_request

        # ---------------------------------------------------------
        # 7. Approve remediation
        # ---------------------------------------------------------

        print("\n🔹 Approving remediation...")

        await graph.ainvoke(
            Command(
                resume={
                    "decision": "approve",
                    "reason": "Approved for workflow testing.",
                }
            ),
            config=config,
        )

        # ---------------------------------------------------------
        # 8. Get final state
        # ---------------------------------------------------------

        final_state = await graph.aget_state(config)

    assert final_state is not None
    
    print("\n🔍 Final state:")
    print("Next:", final_state.next)
    print("State keys:", list(final_state.values.keys()))
    
    values = final_state.values

    # ---------------------------------------------------------
    # 9. Check approval
    # ---------------------------------------------------------

    print("\n🔹 Checking approval...")

    assert values["approval_status"] == "approved"

    print("✅ Approval:", values["approval_status"])

    # ---------------------------------------------------------
    # 10. Check remediation execution
    # ---------------------------------------------------------

    print("\n🔹 Checking remediation execution...")

    print("Execution status:", values.get("execution_status"))

    assert values["execution_status"] == "completed"

    execution_result = values.get("execution_result")

    assert execution_result is not None

    print("Execution result:")
    print(execution_result)

    assert execution_result["action"] is not None

    # ---------------------------------------------------------
    # 11. Check verification
    # ---------------------------------------------------------

    print("\n🔹 Checking remediation verification...")

    verification_status = values.get("verification_status")

    print("Verification status:", verification_status)

    assert verification_status in {
        "passed",
        "failed",
    }

    verification_result = values.get("verification_result")

    assert verification_result is not None

    print("Verification result:")
    print(verification_result)

    # ---------------------------------------------------------
    # 12. Check final response
    # ---------------------------------------------------------

    print("\n🔹 Checking final response...")

    final_response = values.get("final_response")

    assert final_response

    print("\nFinal response:")
    print(final_response)

    print("\n" + "=" * 60)
    print("✅ REMEDIATION WORKFLOW TEST PASSED")
    print("=" * 60)


def test_remediation_workflow():
    """
    Pytest entry point.

    Runs the async workflow using asyncio.
    """

    asyncio.run(run_remediation_workflow())