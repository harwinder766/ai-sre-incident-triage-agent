# from __future__ import annotations

# from typing import Any

# from langchain_ollama import ChatOllama

# from app.analysis.schema import IncidentAnalysis


# class IncidentAnalyzer:
#     """
#     Uses an LLM to analyze evidence collected
#     during incident investigation.
#     """

#     def __init__(
#         self,
#         model: str = "llama3.2:3b",
#         temperature: float = 0.0,
#     ) -> None:

#         self.llm = ChatOllama(
#             model=model,
#             temperature=temperature,
#         )

#         self.structured_llm = (
#             self.llm.with_structured_output(
#                 IncidentAnalysis
#             )
#         )

#     async def analyze(
#         self,
#         service: str,
#         message: str,
#         category: str,
#         severity: str,
#         metrics: dict[str, Any],
#         logs: Any,
#         recent_commits: Any,
#         rag_evidence: Any,
#     ) -> IncidentAnalysis:

#         prompt = f"""
# You are an SRE incident analysis system.

# Analyze the incident using ONLY the evidence provided below.

# Your task is to:
# 1. Identify the most likely root cause.
# 2. Estimate your confidence between 0 and 1.
# 3. Explain your reasoning.
# 4. List the strongest supporting evidence.

# Important rules:

# - Do not invent evidence.
# - Do not assume that historical RAG evidence describes
#   the current incident.
# - Give higher importance to current metrics and logs
#   when determining the current system state.
# - Use recent commits as supporting evidence when relevant.
# - Use RAG evidence as historical/runbook context.
# - If the evidence is insufficient or conflicting,
#   lower the confidence.
# - Do not recommend remediation yet.
# - Do not claim certainty unless the evidence strongly
#   supports the conclusion.

# INCIDENT
# --------
# Service: {service}
# Message: {message}
# Category: {category}
# Severity: {severity}

# CURRENT METRICS
# ---------------
# {metrics}

# CURRENT LOGS
# ------------
# {logs}

# RECENT COMMITS
# --------------
# {recent_commits}

# HISTORICAL / RUNBOOK EVIDENCE
# -----------------------------
# {rag_evidence}
# """

#         result = await self.structured_llm.ainvoke(
#             prompt
#         )

#         return result


# incident_analyzer = IncidentAnalyzer()

import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.analysis.schema import IncidentAnalysis


load_dotenv()


NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

NVIDIA_BASE_URL = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1",
)

NVIDIA_MODEL = os.getenv(
    "NVIDIA_MODEL",
    "deepseek-ai/deepseek-v4-flash-0731",
)


if not NVIDIA_API_KEY:
    raise ValueError(
        "NVIDIA_API_KEY is not configured."
    )


class IncidentAnalyzer:

    def __init__(
        self,
        model: str = NVIDIA_MODEL,
        temperature: float = 0.0,
    ) -> None:

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=NVIDIA_API_KEY,
            base_url=NVIDIA_BASE_URL,
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
- The remediation is only a recommendation that must be reviewed
  and approved by a human before execution.

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