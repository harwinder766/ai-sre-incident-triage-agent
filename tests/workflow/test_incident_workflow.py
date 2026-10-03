import pytest

from langgraph.types import Command

from app.main import app


@pytest.mark.asyncio
async def test_incident_workflow():

    initial_state = {
        "incident_id": "INC-001",
        "service": "payment",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    config = {
        "configurable": {
            "thread_id": "test-incident-workflow-001",
        }
    }

    async with app.router.lifespan_context(app):
        graph = app.state.graph

        await graph.ainvoke(
            initial_state,
            config=config,
        )

        result = await graph.ainvoke(
            Command(
                resume={
                    "decision": "approve",
                    "reason": "Approved for workflow testing.",
                }
            ),
            config=config,
        )

    assert result["category"] == "database"

    assert result["severity"] == "SEV-2"

    assert "investigation" in result

    assert result["investigation"] != ""

    assert "relevant_metrics" in result

    assert "relevant_logs" in result

    assert "recent_commits" in result

    assert "final_response" in result

    assert result["final_response"] != ""