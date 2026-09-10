from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_incident():
    incident = {
        "incident_id": "INC-001",
        "service": "payment-api",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    response = client.post(
        "/api/v1/incidents/",
        json=incident,
    )

    assert response.status_code == 200

    result = response.json()

    # Check that the original incident information is preserved
    assert result["incident_id"] == "INC-001"
    assert result["service"] == "payment-api"

    # Check LangGraph classification
    assert result["category"] == "database"
    assert result["severity"] == "SEV-2"

    # Check that the workflow produced its outputs
    assert "investigation" in result
    assert result["investigation"] != ""

    assert "final_response" in result
    assert result["final_response"] != ""