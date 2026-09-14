import asyncio
from typing import Any

from app.tools.prometheus import prometheus_tool
from app.tools.logs import logs_tool
from app.tools.github import github_tool


class IncidentInvestigator:
    """
    Collect evidence from multiple external systems concurrently.
    """

    async def investigate(
        self,
        service: str,
        container_name: str,
        log_limit: int = 50,
        commit_limit: int = 10,
    ) -> dict[str, Any]:

        metrics_task = prometheus_tool.get_service_metrics(
            service
        )

        logs_task = logs_tool.get_service_logs(
            container_name,
            limit=log_limit,
        )

        commits_task = github_tool.get_recent_commits(
            limit=commit_limit,
        )


        results = await asyncio.gather(
            metrics_task,
            logs_task,
            commits_task,
            return_exceptions=True
        )
        metrics, logs, commits = results

        if isinstance(metrics, Exception):
            metrics = {
                'status': 'unavailable',
                'error': str(metrics),
            }

        if isinstance(logs, Exception):
            logs = {
                'status': 'unavailable',
                'error': str(logs),
            }

        if isinstance(commits, Exception):
            commits = {
                'status': 'unavailable',
                'error': str(commits),
            }
            
        return {
            "metrics": metrics,
            "logs": logs,
            "recent_commits": commits,
        }


incident_investigator = IncidentInvestigator()