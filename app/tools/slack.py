from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


class SlackTool:
    def __init__(
        self,
        webhook_url: str | None = SLACK_WEBHOOK_URL,
    ) -> None:
        self.webhook_url = webhook_url
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=10.0,
            )

        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "SlackTool":
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.close()

    def _validate_webhook(self) -> None:
        if not self.webhook_url:
            raise ValueError(
                "SLACK_WEBHOOK_URL is not configured."
            )

    async def send_message(
        self,
        message: str,
    ) -> dict[str, Any]:
        """
        Send a message to Slack using an Incoming Webhook.
        """

        self._validate_webhook()

        response = await self._get_client().post(
            self.webhook_url,
            json={
                "text": message,
            },
        )

        response.raise_for_status()

        return {
            "status": "sent",
        }


slack_tool = SlackTool()
