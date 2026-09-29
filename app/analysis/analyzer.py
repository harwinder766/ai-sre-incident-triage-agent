import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.analysis.schema import IncidentAnalysis


load_dotenv(override=True)


XKIRO_API_KEY = os.getenv("XKIRO_API_KEY")

XKIRO_BASE_URL = os.getenv(
    "XKIRO_BASE_URL",
    "https://api.xkiro.com/v1",
)

XKIRO_MODEL = os.getenv(
    "XKIRO_MODEL",
    "qwen/qwen3.8-omni-flash:free",
)


if not XKIRO_API_KEY:
    raise ValueError(
        "XKIRO_API_KEY is not configured."
    )
class IncidentAnalyzer:

    def __init__(
        self,
        model: str = XKIRO_MODEL,
        temperature: float = 0.0,
    ) -> None:

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=XKIRO_API_KEY,
            base_url=XKIRO_BASE_URL,
            timeout=120,
            max_retries=2,
        )

        self.structured_llm = (
            self.llm.with_structured_output(
                IncidentAnalysis
            )
        )


    async def analyze(
        self,
        service: str,
        message: str,
        category: str,
        severity: str,
        metrics: dict[str, Any],
        logs: Any,
        recent_commits: Any,
        rag_evidence: Any,
    ) -> IncidentAnalysis:

        prompt = f"""
You are an SRE incident analysis system.

Analyze the incident using ONLY the evidence provided below.

Your task is to:

1. Identify the most likely root cause.
2. Estimate confidence.
3. Explain your reasoning.
4. List the strongest supporting evidence.
5. Explain how the incident could be remediated.
6. Explain the expected impact of the remediation.
7. Identify potential risks.

Important rules:

- Do not invent evidence.
- Do not assume historical RAG evidence describes the current incident.
- Give higher importance to current metrics and logs.
- Use recent commits as supporting evidence when relevant.
- Use RAG as historical/runbook context.
- If evidence is insufficient or conflicting, lower confidence.
- Do not claim certainty without sufficient evidence.
- Do not execute anything.
- Do not generate shell commands.
- The remediation plan is only a recommendation that must be reviewed
  and approved by a human before execution.
- For a database connection pool exhaustion incident, use the simulator's
  supported remediation action `increase_database_pool` with an integer
  `pool_size` parameter.

INCIDENT
--------
Service: {service}
Message: {message}
Category: {category}
Severity: {severity}

CURRENT METRICS
---------------
{metrics}

CURRENT LOGS
------------
{logs}

RECENT COMMITS
--------------
{recent_commits}

HISTORICAL / RUNBOOK EVIDENCE
-----------------------------
{rag_evidence}
"""

        result = await self.structured_llm.ainvoke(prompt)

        return result


incident_analyzer = IncidentAnalyzer()