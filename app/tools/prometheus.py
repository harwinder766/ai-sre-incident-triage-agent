import os
from typing import Any

import requests
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

    def query(
        self,
        promql: str,
    ) -> list[dict[str, Any]]:
        """
        Execute a PromQL instant query.
        """

        response = requests.get(
            f"{self.base_url}/api/v1/query",
            params={"query": promql},
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"Prometheus query failed: {data}"
            )

        return data["data"]["result"]

    def get_request_rate(
        self,
        service: str,
    ) -> float:
        """
        Get requests per second for a service.
        """

        query = (
            f'rate({service}_requests_total[1m])'
        )

        results = self.query(query)

        if not results:
            return 0.0

        return float(results[0]["value"][1])

    def get_error_rate(
        self,
        service: str,
    ) -> float:
        """
        Calculate the current error rate for a service.

        error rate = errors / requests
        """

        error_query = (
            f'rate({service}_errors_total[1m])'
        )

        request_query = (
            f'rate({service}_requests_total[1m])'
        )

        error_results = self.query(error_query)
        request_results = self.query(request_query)

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

    def get_average_latency(
        self,
        service: str,
    ) -> float:
        """
        Calculate average request latency.

        For a Prometheus histogram:

        average latency =
            rate(_sum) / rate(_count)
        """

        sum_query = (
            f'rate({service}_request_duration_seconds_sum[1m])'
        )

        count_query = (
            f'rate({service}_request_duration_seconds_count[1m])'
        )

        sum_results = self.query(sum_query)
        count_results = self.query(count_query)

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

    def get_service_metrics(
        self,
        service: str,
    ) -> dict[str, float]:
        """
        Collect the main metrics needed during
        incident investigation.
        """

        return {
            "request_rate": self.get_request_rate(
                service
            ),
            "error_rate": self.get_error_rate(
                service
            ),
            "average_latency": self.get_average_latency(
                service
            ),
        }


prometheus_tool = PrometheusTool()
