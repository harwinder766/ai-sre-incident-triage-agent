from app.tools.logs import logs_tool
import asyncio
import time

CONTAINER_NAME = "ai-sre-payment-api"


async def main():

    print("Testing Logs Tool...\n")

    print("Recent service logs:")
    logs = await logs_tool.get_service_logs(
        CONTAINER_NAME,
        limit=10,
    )

    print(logs)

    print("\nRecent error logs:")
    errors = await logs_tool.get_error_logs(
        CONTAINER_NAME,
        limit=10,
    )

    print(errors)


if __name__ == "__main__":
    x = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - x
    print(f"\nLogs tool test completed in {elapsed:.3f} seconds.")
