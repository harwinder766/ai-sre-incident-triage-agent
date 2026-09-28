from __future__ import annotations

from typing import Any

import httpx


class PaymentAPIAdapter:
    """
    Adapter used only for the local payment-api simulator.

    The core remediation system does not depend on this class.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def execute(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:

        pool_size = parameters.get("pool_size")

        if not isinstance(pool_size, int):
            raise ValueError(
                "pool_size must be an integer."
            )

        if pool_size <= 0:
            raise ValueError(
                "pool_size must be greater than zero."
            )

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.post(
                f"{self.base_url}/admin/remediation/database-pool",
                json={
                    "pool_size": pool_size,
                },
            )

            response.raise_for_status()

            return response.json()