import pytest

from app.tools.logs import LogsTool


@pytest.mark.asyncio
async def test_loki_query():

    tool = LogsTool()

    results = await tool.query(
        '{container=~".+"}',
        limit=10,
    )

    assert isinstance(results, list)

    await tool.close()


@pytest.mark.asyncio
async def test_get_service_logs():

    tool = LogsTool()

    results = await tool.get_service_logs(
        "ai-sre-payment-api",
        limit=10,
    )

    assert isinstance(results, list)

    await tool.close()