import asyncio
from typing import Any

from app.tools.prometheus import prometheus_tool
from app.tools.logs import logs_tool
from app.tools.github import github_tool
from app.dependencies import rag_tool   

class IncidentInvestigator:
    """
    Collect evidence from multiple external systems concurrently.
    """

    async def investigate(
        self,
        service: str,
        container_name: str,
        incident_message: str,
        log_limit: int = 50,
        commit_limit: int = 10,
    ) -> dict[str, Any]:

        rag_query = (
            f"Service: {service}\n"
            f"Incident: {incident_message}"
        )

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

        rag_task = asyncio.to_thread(
            rag_tool.search,
            rag_query
        )


        results = await asyncio.gather(
            metrics_task,
            logs_task,
            commits_task,
            rag_task,
            return_exceptions=True
        )
        metrics, logs, commits, rag_evidence = results

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

        if isinstance(rag_evidence, Exception):
            rag_evidence = {
                'status': 'unavailable',
                'error': str(rag_evidence),
            }
        
            
        return {
            "metrics": metrics,
            "logs": logs,
            "recent_commits": commits,
        }


incident_investigator = IncidentInvestigator()