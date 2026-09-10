from .state import IncidentState


def ingest_incident(state: IncidentState) -> IncidentState:
    """
    Validate and prepare the incoming incident data.
    """

    print("🔹 Ingesting incident...")

    if not state.get("incident_id"):
        raise ValueError("incident_id is required")

    if not state.get("service"):
        raise ValueError("service is required")

    if not state.get("message"):
        raise ValueError("message is required")

    return state


def classify_incident(state: IncidentState) -> IncidentState:
    """
    Classify the incident into a category and severity.

    This is intentionally rule-based for now.
    Later, this node can use an LLM.
    """

    print("🔹 Classifying incident...")

    message = state["message"].lower()
    error_rate = state.get("error_rate", 0.0)

    # -------------------------
    # Incident category
    # -------------------------

    if any(word in message for word in ["database", "db", "sql", "connection pool"]):
        category = "database"

    elif any(word in message for word in ["timeout", "latency", "slow"]):
        category = "performance"

    elif any(word in message for word in ["authentication", "login", "unauthorized"]):
        category = "authentication"

    elif any(word in message for word in ["memory", "oom", "out of memory"]):
        category = "memory"

    elif any(word in message for word in ["cpu", "high cpu"]):
        category = "resource"

    else:
        category = "unknown"

    # -------------------------
    # Incident severity
    # -------------------------

    if error_rate >= 0.50:
        severity = "SEV-1"

    elif error_rate >= 0.10:
        severity = "SEV-2"

    elif error_rate > 0:
        severity = "SEV-3"

    else:
        severity = "SEV-4"

    return {
        **state,
        "category": category,
        "severity": severity,
    }


def generate_initial_investigation(state: IncidentState) -> IncidentState:
    """
    Generate a basic investigation summary.

    This is a placeholder for now.
    Later this node will combine evidence from:
        - Prometheus
        - logs
        - RAG
        - GitHub
    """

    print("🔹 Generating initial investigation...")

    investigation = (
        f"Incident {state['incident_id']} affects the "
        f"{state['service']} service. "
        f"The incident is classified as {state['severity']} "
        f"and categorized as {state['category']}."
    )

    return {
        **state,
        "investigation": investigation,
    }


def generate_final_response(state: IncidentState) -> IncidentState:
    """
    Generate the final response returned by the workflow.
    """

    print("🔹 Generating final response...")

    final_response = (
        f"Incident {state['incident_id']} processed successfully.\n"
        f"Service: {state['service']}\n"
        f"Category: {state['category']}\n"
        f"Severity: {state['severity']}\n"
        f"Investigation: {state.get('investigation', 'Not available')}"
    )

    return {
        **state,
        "final_response": final_response,
    }
