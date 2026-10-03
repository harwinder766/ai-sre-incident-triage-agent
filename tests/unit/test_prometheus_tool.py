from app.tools.prometheus import PrometheusTool
import pytest


def test_metric_prefix_uses_payment_api_mapping():
    assert PrometheusTool._metric_prefix("payment-api") == "payment"


def test_metric_prefix_uses_generic_fallback():
    assert PrometheusTool._metric_prefix("checkout-api") == "checkout_api"


@pytest.mark.asyncio
async def test_prometheus_query():
    tool = PrometheusTool()

    results = await tool.query(
        "payment_requests_total"
    )

    assert isinstance(results, list)

    await tool.close()


@pytest.mark.asyncio
async def test_payment_api_metric_queries_use_simulator_prefix(monkeypatch):
    tool = PrometheusTool()
    queries = []

    async def fake_query(promql):
        queries.append(promql)
        if "request_duration_seconds_sum" in promql:
            return [{"value": [0, "2.0"]}]
        if "request_duration_seconds_count" in promql:
            return [{"value": [0, "4.0"]}]
        return [{"value": [0, "10.0"]}]

    monkeypatch.setattr(tool, "query", fake_query)

    metrics = await tool.get_service_metrics(
        "payment-api"
    )

    assert metrics == {
        "request_rate": 10.0,
        "error_rate": 1.0,
        "average_latency": 0.5,
    }
    assert "rate(payment_requests_total[1m])" in queries
    assert "rate(payment_errors_total[1m])" in queries
    assert (
        "rate(payment_request_duration_seconds_sum[1m])"
        in queries
    )
    assert (
        "rate(payment_request_duration_seconds_count[1m])"
        in queries
    )
    assert all("payment_api_" not in query for query in queries)

    assert "request_rate" in metrics
    assert "error_rate" in metrics
    assert "average_latency" in metrics

    assert metrics["request_rate"] >= 0
    assert metrics["error_rate"] >= 0
    assert metrics["average_latency"] >= 0

    await tool.close()
    