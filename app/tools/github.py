import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_API_URL = os.getenv(
    "GITHUB_API_URL",
    "https://api.github.com",
)


class GitHubTool:
    """
    Tool for retrieving repository changes and issues
    from GitHub.
    """

    def __init__(
        self,
        token: str | None = GITHUB_TOKEN,
        owner: str | None = GITHUB_OWNER,
        repo: str | None = GITHUB_REPO,
        base_url: str = GITHUB_API_URL,
    ):
        self.token = token
        self.owner = owner
        self.repo = repo

        self.base_url = base_url.rstrip("/")

        self.headers = {
            "Accept": "application/vnd.github+json",
        }

        if self.token:
            self.headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=10.0,
            )

        return self._client

    async def close(self) -> None:
        """Close the shared HTTP client."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "GitHubTool":
        return self

    async def __aexit__(
        self,
        *_args: object,
    ) -> None:
        await self.close()

    def _validate_repository(self) -> None:
        if not self.owner:
            raise ValueError(
                "GITHUB_OWNER is not configured"
            )

        if not self.repo:
            raise ValueError(
                "GITHUB_REPO is not configured"
            )

    async def get_recent_commits(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get recent commits from the repository.
        """

        self._validate_repository()

        client = self._get_client()

        response = await client.get(
            f"{self.base_url}/repos/"
            f"{self.owner}/{self.repo}/commits",
            params={
                "per_page": limit,
            },
        )

        response.raise_for_status()

        commits = response.json()

        return [
            {
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "url": commit["html_url"],
            }
            for commit in commits
        ]

    async def search_issues(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search issues in the repository.
        """

        self._validate_repository()

        search_query = (
            f"repo:{self.owner}/{self.repo} "
            f"{query}"
        )

        client = self._get_client()

        response = await client.get(
            f"{self.base_url}/search/issues",
            params={
                "q": search_query,
                "per_page": limit,
            },
        )

        response.raise_for_status()

        data = response.json()

        return [
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "url": issue["html_url"],
            }
            for issue in data.get("items", [])
        ]

    async def get_issue(
        self,
        issue_number: int,
    ) -> dict[str, Any]:
        """
        Get a specific issue from the repository.
        """

        self._validate_repository()

        client = self._get_client()

        response = await client.get(
            f"{self.base_url}/repos/"
            f"{self.owner}/{self.repo}/issues/"
            f"{issue_number}",
        )

        response.raise_for_status()

        issue = response.json()

        return {
            "number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "state": issue["state"],
            "url": issue["html_url"],
            "created_at": issue["created_at"],
            "updated_at": issue["updated_at"],
        }


github_tool = GitHubTool()