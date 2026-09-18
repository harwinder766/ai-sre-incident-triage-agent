import asyncio

from langgraph.types import Command

from app.graph.graph import graph


async def main() -> None:
    initial_state = {
        "incident_id": "INC-001",
        "service": "payment-api",
        "message": "Database connection pool exhausted",
        "error_rate": 0.63,
    }

    config = {
        "configurable": {
            "thread_id": "INC-001",
        }
    }

    print("\n========== STARTING INCIDENT ==========\n")

    result = await graph.ainvoke(
        initial_state,
        config=config,
    )

    print("\n========== GRAPH PAUSED ==========\n")

    print(result)

    print("\n========== APPROVAL REQUEST ==========\n")

    print("Root Cause:")
    print(result.get("root_cause"))

    print("\nConfidence:")
    print(result.get("confidence"))

    print("\nRemediation:")
    print(result.get("remediation"))

    print("\nExpected Impact:")
    print(result.get("expected_impact"))

    print("\nRisks:")
    print(result.get("risks"))

    print("\n======================================")
    print("The graph is now waiting for approval.")
    print("======================================\n")

    approval = input(
        "Approve remediation? (yes/no): "
    ).strip().lower()

    if approval == "yes":
        decision = "approve"
        reason = "Approved by human."
    elif approval == "no":
        decision = "reject"
        reason = "Rejected by human."
    else:
        print("Invalid input. Use yes or no.")
        return

    print("\n========== RESUMING GRAPH ==========\n")

    result = await graph.ainvoke(
        Command(
            resume={
                "decision": decision,
                "reason": reason,
            }
        ),
        config=config,
    )

    print("\n========== FINAL RESULT ==========\n")

    print(result)


if __name__ == "__main__":
    asyncio.run(main())