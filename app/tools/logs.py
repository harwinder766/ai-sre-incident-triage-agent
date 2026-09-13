import os
from typing import Any

import requests
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

    def query(
        self,
        log_query: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Execute a LogQL query against Loki.

        Example:
            {container="ai-sre-payment-api"}
        """

        response = requests.get(
            f"{self.base_url}/loki/api/v1/query_range",
            params={
                "query": log_query,
                "limit": limit,
                "direction": "backward",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"Loki query failed: {data}"
            )

        return data["data"]["result"]

    def get_service_logs(
        self,
        container_name: str=PAYMENT_API_CONTAINER,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get recent logs for a specific Docker container.
        """

        query = (
            f'{{container="{container_name}"}}'
        )

        return self.query(
            query,
            limit=limit,
        )

    def get_error_logs(
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

        return self.query(
            query,
            limit=limit,
        )


logs_tool = LogsTool()