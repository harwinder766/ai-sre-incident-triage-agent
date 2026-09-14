import pytest

from app.investigation.investigator import incident_investigator


@pytest.mark.asyncio
async def test_async_investigation():

    result = await incident_investigator.investigate(
        service="payment",
        container_name="ai-sre-payment-api",
    )

    assert isinstance(result, dict)

    assert "metrics" in result
    assert "logs" in result
    assert "recent_commits" in result

    assert isinstance(result["metrics"], dict)
    assert isinstance(result["logs"], list)
    assert isinstance(result["recent_commits"], list)