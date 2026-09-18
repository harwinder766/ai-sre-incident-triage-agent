import asyncio

from app.analysis.analyzer import incident_analyzer


async def main() -> None:

    result = await incident_analyzer.analyze(
        service="payment",
        message=(
            "Payment API database connection "
            "pool exhausted"
        ),
        category="database",
        severity="SEV-1",
        metrics={
            "request_rate": 12.4,
            "error_rate": 0.63,
            "average_latency": 2.8,
        },
        logs=[
            "ERROR database connection pool exhausted",
            "ERROR failed to acquire database connection",
        ],
        recent_commits=[
            {
                "sha": "abc123",
                "message": (
                    "Reduce database connection pool size"
                ),
            }
        ],
        rag_evidence=[
            {
                "content": (
                    "Previous incident caused by "
                    "database connection pool exhaustion."
                ),
                "source": "database_runbook.md",
                "rrf_score": 0.0325,
            }
        ],
    )

    print("\n========== ANALYSIS ==========\n")

    print(
        "Root cause:",
        result.root_cause,
    )

    print(
        "Confidence:",
        result.confidence,
    )

    print(
        "Reasoning:",
        result.reasoning,
    )

    print(
        "Supporting evidence:",
        result.supporting_evidence,
    )

    print(
        "Remediation:",
        result.remediation,
    )

    print(
        "Expected impact:",
        result.expected_impact,
    )

    print(
        "Risks:",
        result.risks,
    )


if __name__ == "__main__":
    asyncio.run(main())