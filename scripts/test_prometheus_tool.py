from app.tools.prometheus import prometheus_tool


def main():

    print("Testing Prometheus tool...\n")

    print("Request rate:")
    print(
        prometheus_tool.get_request_rate(
            "payment"
        )
    )

    print("\nError rate:")
    print(
        prometheus_tool.get_error_rate(
            "payment"
        )
    )

    print("\nAverage latency:")
    print(
        prometheus_tool.get_average_latency(
            "payment"
        )
    )

    print("\nAll metrics:")
    print(
        prometheus_tool.get_service_metrics(
            "payment"
        )
    )


if __name__ == "__main__":
    main()