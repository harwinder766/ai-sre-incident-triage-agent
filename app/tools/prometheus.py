import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://localhost:9090",
)


class PrometheusTool:
    """
    Tool for querying current metrics from Prometheus.
    """

    def __init__(
        self,
        base_url: str = PROMETHEUS_URL,
    ):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._client_loop: asyncio.AbstractEventLoop | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        loop = asyncio.get_running_loop()

        if self._client_loop is not loop:
            if self._client is not None and self._client_loop is not None:
                if self._client_loop.is_closed():
                    self._client = None
                else:
                    await self._client.aclose()
                self._client_loop = None
            self._client_loop = loop

        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)

        return self._client

    @staticmethod
    def _metric_prefix(service: str) -> str:
        return service.replace("-", "_")

    async def close(self) -> None:
        """Close the shared HTTP client."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._client_loop = None

    async def __aenter__(self) -> "PrometheusTool":
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.close()

    async def query(
        self,
        promql: str,
    ) -> list[dict[str, Any]]:
        """
        Execute a PromQL instant query.
        """

        response = await (await self._get_client()).get(
            f"{self.base_url}/api/v1/query",
            params={"query": promql},
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"Prometheus query failed: {data}"
            )

        return data["data"]["result"]

    async def get_request_rate(
        self,
        service: str,
    ) -> float:
        """
        Get requests per second for a service.
        """

        metric_prefix = self._metric_prefix(service)
        query = (
            f'rate({metric_prefix}_requests_total[1m])'
        )

        results = await self.query(query)

        if not results:
            return 0.0

        return float(results[0]["value"][1])

    async def get_error_rate(
        self,
        service: str,
    ) -> float:
        """
        Calculate the current error rate for a service.

        error rate = errors / requests
        """

        metric_prefix = self._metric_prefix(service)

        error_query = (
            f'rate({metric_prefix}_errors_total[1m])'
        )

        request_query = (
            f'rate({metric_prefix}_requests_total[1m])'
        )

        error_results, request_results = await asyncio.gather(
            self.query(error_query),
            self.query(request_query),
        )

        if not request_results:
            return 0.0

        if not error_results:
            return 0.0

        errors = float(
            error_results[0]["value"][1]
        )

        requests_per_second = float(
            request_results[0]["value"][1]
        )

        if requests_per_second == 0:
            return 0.0

        return errors / requests_per_second

    async def get_average_latency(
        self,
        service: str,
    ) -> float:
        """
        Calculate average request latency.

        For a Prometheus histogram:

        average latency =
            rate(_sum) / rate(_count)
        """

        metric_prefix = self._metric_prefix(service)

        sum_query = (
            f'rate({metric_prefix}_request_duration_seconds_sum[1m])'
        )

        count_query = (
            f'rate({metric_prefix}_request_duration_seconds_count[1m])'
        )

        sum_results, count_results = await asyncio.gather(
            self.query(sum_query),
            self.query(count_query),
        )

        if not sum_results or not count_results:
            return 0.0

        total_duration = float(
            sum_results[0]["value"][1]
        )

        request_count = float(
            count_results[0]["value"][1]
        )

        if request_count == 0:
            return 0.0

        return total_duration / request_count

    async def get_service_metrics(
        self,
        service: str,
    ) -> dict[str, float]:
        """
        Collect the main metrics needed during
        incident investigation.
        """

        request_rate, error_rate, average_latency = await asyncio.gather(
            self.get_request_rate(service),
            self.get_error_rate(service),
            self.get_average_latency(service),
        )

        return {
            "request_rate": request_rate,
            "error_rate": error_rate,
            "average_latency": average_latency,
        }


prometheus_tool = PrometheusTool()
