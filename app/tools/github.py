import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

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
    ):
        self.token = token
        self.owner = owner
        self.repo = repo

        self.base_url = "https://api.github.com"

        self.headers = {
            "Accept": "application/vnd.github+json",
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _validate_repository(self) -> None:
        if not self.owner:
            raise ValueError("GITHUB_OWNER is not configured")

        if not self.repo:
            raise ValueError("GITHUB_REPO is not configured")

    def get_recent_commits(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        self._validate_repository()

        response = requests.get(
            f"{self.base_url}/repos/"
            f"{self.owner}/{self.repo}/commits",
            headers=self.headers,
            params={"per_page": limit},
            timeout=10,
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

    def search_issues(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        self._validate_repository()

        search_query = (
            f"repo:{self.owner}/{self.repo} "
            f"{query}"
        )

        response = requests.get(
            f"{self.base_url}/search/issues",
            headers=self.headers,
            params={
                "q": search_query,
                "per_page": limit,
            },
            timeout=10,
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

    def get_issue(
        self,
        issue_number: int,
    ) -> dict[str, Any]:
        self._validate_repository()

        response = requests.get(
            f"{self.base_url}/repos/"
            f"{self.owner}/{self.repo}/issues/{issue_number}",
            headers=self.headers,
            timeout=10,
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