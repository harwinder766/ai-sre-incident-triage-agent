from app.adapters.simulator.payment_api import PaymentAPIAdapter
from app.tools.remediation import remediation_tool


def register_simulator_adapters() -> None:
    remediation_tool.register_adapter(
        action="increase_database_pool",
        adapter=PaymentAPIAdapter(
            base_url="http://localhost:8001"
        ),
    )