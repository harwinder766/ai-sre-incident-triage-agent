import pytest

from app.graph.graph import graph


@pytest.mark.asyncio
async def test_incident_workflow():

    initial_state = {
        "incident_id": "INC-001",
        "service": "payment",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    result = await graph.ainvoke(
        initial_state
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