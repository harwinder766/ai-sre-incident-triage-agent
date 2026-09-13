from app.tools.logs import LogsTool


def test_loki_query():

    tool = LogsTool()

    results = tool.query(
        '{container=~".+"}',
        limit=10,
    )

    assert isinstance(results, list)


def test_get_service_logs():

    tool = LogsTool()

    results = tool.get_service_logs(
        "ai-sre-payment-api",
        limit=10,
    )

    assert isinstance(results, list)