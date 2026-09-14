from app.tools.prometheus import PrometheusTool
import pytest

@pytest.mark.asyncio
async def test_prometheus_query():
    tool = PrometheusTool()

    results = await tool.query(
        "payment_requests_total"
    )

    assert isinstance(results, list)

    await tool.close()

@pytest.mark.asyncio
async def test_get_service_metrics():
    tool = PrometheusTool()

    metrics = await tool.get_service_metrics(
        "payment"
    )

    assert "request_rate" in metrics
    assert "error_rate" in metrics
    assert "average_latency" in metrics

    assert metrics["request_rate"] >= 0
    assert metrics["error_rate"] >= 0
    assert metrics["average_latency"] >= 0

    await tool.close()
    