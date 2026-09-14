import asyncio
import time
from app.tools.prometheus import prometheus_tool


async def main():
    print("Testing async Prometheus tool...\n")

    print("Request rate:")
    print(
        await prometheus_tool.get_request_rate(
            "payment"
        )
    )

    print("\nError rate:")
    print(
        await prometheus_tool.get_error_rate(
            "payment"
        )
    )

    print("\nAverage latency:")
    print(
        await prometheus_tool.get_average_latency(
            "payment"
        )
    )

    print("\nAll metrics:")
    print(
        await prometheus_tool.get_service_metrics(
            "payment"
        )
    )

    # Close the shared AsyncClient
    await prometheus_tool.close()


if __name__ == "__main__":
    x = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - x
    print(f"\nPrometheus tool test completed in {elapsed:.3f} seconds.")