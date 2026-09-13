from app.tools.prometheus import PrometheusTool


def test_prometheus_query():
    tool = PrometheusTool()

    results = tool.query(
        "payment_requests_total"
    )

    assert isinstance(results, list)


def test_get_service_metrics():
    tool = PrometheusTool()

    metrics = tool.get_service_metrics(
        "payment"
    )

    assert "request_rate" in metrics
    assert "error_rate" in metrics
    assert "average_latency" in metrics

    assert metrics["request_rate"] >= 0
    assert metrics["error_rate"] >= 0
    assert metrics["average_latency"] >= 0