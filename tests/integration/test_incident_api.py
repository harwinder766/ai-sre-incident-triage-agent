import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from uuid import uuid4

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client


@pytest.mark.asyncio
async def test_create_incident(client):

    incident = {
        "incident_id": "TEST-INC-001",
        "service": "payment-api",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    response = await client.post(
        "/api/v1/incidents/",
        json=incident,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["incident_id"] == "TEST-INC-001"
    assert result["service"] == "payment-api"
    assert result["category"] == "database"
    assert result["severity"] == "SEV-2"


@pytest.mark.asyncio
async def test_get_incident_from_database(client):

    incident = {
        "incident_id": "TEST-INC-002",
        "service": "user-api",
        "message": "High memory usage",
        "error_rate": 0.20,
    }

    create_response = await client.post(
        "/api/v1/incidents/",
        json=incident,
    )

    assert create_response.status_code == 200

    get_response = await client.get(
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
    assert isinstance(result["relevant_metrics"], dict)
    assert "request_rate" in result["relevant_metrics"]
    assert "error_rate" in result["relevant_metrics"]
    assert "average_latency" in result["relevant_metrics"]
    assert isinstance(result["relevant_logs"], list)
    assert isinstance(result["recent_commits"], list)
    assert isinstance(result["reasoning"], str)
    assert result["reasoning"]
    assert isinstance(result["supporting_evidence"], list)
    assert result["supporting_evidence"]
    assert isinstance(result["expected_impact"], str)
    assert result["expected_impact"]
    assert isinstance(result["risks"], list)
    assert result["risks"]


@pytest.mark.asyncio
async def test_list_incidents(client):

    incident_id = f"TEST-LIST-{uuid4().hex}"
    incident = {
        "incident_id": incident_id,
        "service": "payment-api",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    create_response = await client.post(
        "/api/v1/incidents/",
        json=incident,
    )

    assert create_response.status_code == 200

    list_response = await client.get(
        "/api/v1/incidents/",
    )

    assert list_response.status_code == 200

    incidents = list_response.json()
    listed_incident = next(
        item
        for item in incidents
        if item["incident_id"] == incident_id
    )

    assert listed_incident["service"] == "payment-api"
    assert listed_incident["message"] == "DB connection pool exhausted"
    assert listed_incident["error_rate"] == 0.18
    assert listed_incident["category"] == "database"
    assert listed_incident["severity"] == "SEV-2"
    assert listed_incident["status"] == "open"
    assert isinstance(listed_incident["reasoning"], str)
    assert listed_incident["reasoning"]
    assert isinstance(listed_incident["supporting_evidence"], list)
    assert listed_incident["supporting_evidence"]
    assert isinstance(listed_incident["expected_impact"], str)
    assert listed_incident["expected_impact"]
    assert isinstance(listed_incident["risks"], list)
    assert listed_incident["risks"]


@pytest.mark.asyncio
async def test_reject_incident_approval(client):

    incident_id = f"TEST-APPROVAL-{uuid4().hex}"
    incident = {
        "incident_id": incident_id,
        "service": "payment-api",
        "message": "DB connection pool exhausted",
        "error_rate": 0.18,
    }

    create_response = await client.post(
        "/api/v1/incidents/",
        json=incident,
    )

    assert create_response.status_code == 200
    created_incident = create_response.json()

    approval_response = await client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "reject",
            "reason": "Rejected during API testing.",
        },
    )

    assert approval_response.status_code == 200

    result = approval_response.json()

    assert result["incident_id"] == incident_id
    assert result["thread_id"] == created_incident["thread_id"]
    assert result["approval_status"] == "rejected"
    assert result["approval_reason"] == "Rejected during API testing."


@pytest.mark.asyncio
async def test_alert_incident_persists_thread_and_can_resume(client):
    fingerprint = f"TEST-ALERT-{uuid4().hex}"
    incident_id = f"INC-{fingerprint}"

    alert_payload = {
        "status": "firing",
        "alerts": [
            {
                "fingerprint": fingerprint,
                "labels": {
                    "alertname": "HighPaymentErrorRate",
                    "service": "payment-api",
                    "severity": "critical",
                },
                "annotations": {
                    "summary": "High payment API error rate",
                    "description": "Test alert for thread persistence.",
                },
            }
        ],
    }

    alert_response = await client.post(
        "/api/v1/alerts/",
        json=alert_payload,
    )

    assert alert_response.status_code == 200
    assert alert_response.json()["incidents"][0]["status"] == "created"

    detail_response = await client.get(
        f"/api/v1/incidents/{incident_id}"
    )

    assert detail_response.status_code == 200
    created_incident = detail_response.json()
    assert created_incident["thread_id"] == incident_id
    assert created_incident["approval_status"] == "pending"

    approval_response = await client.post(
        f"/api/v1/incidents/{incident_id}/approval",
        json={
            "decision": "reject",
            "reason": "Rejected during alert workflow testing.",
        },
    )

    assert approval_response.status_code == 200
    resumed_incident = approval_response.json()
    assert resumed_incident["thread_id"] == incident_id
    assert resumed_incident["approval_status"] == "rejected"
    assert resumed_incident["approval_reason"] == (
        "Rejected during alert workflow testing."
    )