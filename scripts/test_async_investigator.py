import asyncio
import time

from app.investigation.investigator import incident_investigator


async def main():

    print("Starting async investigation...\n")

    start = time.perf_counter()

    result = await incident_investigator.investigate(
        service="payment",
        container_name="ai-sre-payment-api",
    )

    elapsed = time.perf_counter() - start

    print("=== Metrics ===")
    print(result["metrics"])

    print("\n=== Error Logs ===")
    for log in result["logs"][:5]:
        print(log)

    print("\n=== Recent Commits ===")
    for commit in result["recent_commits"][:5]:
        print(
            f"{commit['sha'][:7]} | "
            f"{commit['message'].splitlines()[0]}"
        )

    print(f"\nInvestigation completed in {elapsed:.3f} seconds.")


if __name__ == "__main__":
    asyncio.run(main())