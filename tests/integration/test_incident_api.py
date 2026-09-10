from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

def test_create_incident():
    incident = {
        "incident_id": "TEST-INC-001",
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

    assert result["incident_id"] == "TEST-INC-001"
    assert result["service"] == "payment-api"
    assert result["category"] == "database"
    assert result["severity"] == "SEV-2"

def test_get_incident_from_database():
    incident = {
        "incident_id": "TEST-INC-002",
        "service": "user-api",
        "message": "High memory usage",
        "error_rate": 0.20,
    }

    create_response = client.post(
        "/api/v1/incidents/",
        json=incident,
    )

    assert create_response.status_code == 200

    get_response = client.get(
        "/api/v1/incidents/TEST-INC-002"
    )

    assert get_response.status_code == 200

    result = get_response.json()

    assert result["incident_id"] == "TEST-INC-002"
    assert result["service"] == "user-api"
    assert result["message"] == "High memory usage"
    assert result["error_rate"] == 0.20
    assert result["category"] == "memory"
    assert result["severity"] == "SEV-2"
    assert result["status"] == "open"