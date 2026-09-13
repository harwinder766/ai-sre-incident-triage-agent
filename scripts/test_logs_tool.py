from app.tools.logs import logs_tool


CONTAINER_NAME = "ai-sre-payment-api"


def main():

    print("Testing Logs Tool...\n")

    print("Recent service logs:")
    logs = logs_tool.get_service_logs(
        CONTAINER_NAME,
        limit=10,
    )

    print(logs)

    print("\nRecent error logs:")
    errors = logs_tool.get_error_logs(
        CONTAINER_NAME,
        limit=10,
    )

    print(errors)


if __name__ == "__main__":
    main()