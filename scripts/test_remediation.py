import asyncio

from app.actions.remediation_actions import execute_remediation
from app.adapters.simulator.payment_api import PaymentAPIAdapter
from app.tools.remediation import remediation_tool


def register_simulator_adapters():
    """
    Register adapters available in the local simulator.
    """

    payment_api_adapter = PaymentAPIAdapter(
        base_url="http://localhost:8001"
    )

    remediation_tool.register_adapter(
        action="increase_database_pool",
        adapter=payment_api_adapter,
    )


async def main():

    register_simulator_adapters()

    remediation = {
        "description": "Increase database connection pool",
        "action": "increase_database_pool",
        "parameters": {
            "pool_size": 20,
        },
        "expected_impact": (
            "Reduce database connection pool exhaustion."
        ),
        "risks": [
            "Higher database connection usage."
        ],
    }

    print("\n🔹 Testing remediation execution...\n")

    try:

        result = await execute_remediation(
            remediation
        )

        print("✅ Remediation executed successfully.")

        print("\nResult:")
        print(result)

    except Exception as exc:

        print("❌ Remediation execution failed.")
        print(f"Error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())