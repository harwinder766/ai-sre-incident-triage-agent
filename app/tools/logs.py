import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


PAYMENT_API_CONTAINER = os.getenv(
    "PAYMENT_API_CONTAINER",
    "ai-sre-payment-api",
)

LOKI_URL = os.getenv(
    "LOKI_URL",
    "http://localhost:3100",
)


class LogsTool:
    """
    Tool for querying application logs from Loki.
    """

    def __init__(
        self,
        base_url: str = LOKI_URL,
    ):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=10.0
            )

        return self._client

    async def close(self) -> None:
        """Close the shared HTTP client."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "LogsTool":
        return self

    async def __aexit__(
        self,
        *_args: object,
    ) -> None:
        await self.close()

    async def query(
        self,
        log_query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Execute a LogQL query against Loki.

        Example:
            {container="ai-sre-payment-api"}
        """

        response = await self._get_client().get(
            f"{self.base_url}/loki/api/v1/query_range",
            params={
                "query": log_query,
                "limit": limit,
                "direction": "backward",
            },
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"Loki query failed: {data}"
            )

        return data["data"]["result"]

    async def get_service_logs(
        self,
        container_name: str = PAYMENT_API_CONTAINER,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get recent logs for a specific Docker container.
        """

        query = (
            f'{{container="{container_name}"}}'
        )

        return await self.query(
            query,
            limit=limit,
        )

    async def get_error_logs(
        self,
        container_name: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get recent error logs for a service.

        Since our payment-api emits JSON logs,
        we search for ERROR-level messages.
        """

        query = (
            f'{{container="{container_name}"}}'
            f' |= "ERROR"'
        )

        return await self.query(
            query,
            limit=limit,
        )


logs_tool = LogsTool()