from app.graph.graph import graph


def test_incident_workflow():
    # Sample incident
    initial_state = {
        "incident_id": "INC-001",
        "service": "payment-api",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    # Run the LangGraph workflow
    result = graph.invoke(initial_state)

    # Check classification
    assert result["category"] == "database"
    assert result["severity"] == "SEV-2"

    # Check investigation
    assert "investigation" in result
    assert result["investigation"] != ""

    # Check final response
    assert "final_response" in result
    assert result["final_response"] != ""
