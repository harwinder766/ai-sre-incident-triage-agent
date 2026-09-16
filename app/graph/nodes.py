from .state import IncidentState
from app.investigation.investigator import incident_investigator
from app.analysis.analyzer import incident_analyzer

import asyncio

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


async def investigate_incident(
    state: IncidentState,
) -> IncidentState:

    print("🔹 Investigating incident...")

    service = state["service"]

    # For now we derive the container name from the service.
    # Later this can come from configuration.
    container_name = "ai-sre-payment-api"

    result = await incident_investigator.investigate(
        service=service,
        container_name=container_name,
        incident_message=state["message"]
    )

    metrics = result.get("metrics", {})
    logs = result.get("logs", [])
    recent_commits = result.get(
        "recent_commits",
        [],
    )
    rag_evidence = result.get(
        "rag_evidence",
        []
    )

    investigation = (
        f"Incident {state['incident_id']} "
        f"is affecting the {service} service.\n"
        f"Category: {state.get('category', 'unknown')}\n"
        f"Severity: {state.get('severity', 'unknown')}\n\n"
        f"Current metrics: {metrics}\n"
        f"Relevant logs: {logs}\n"
        f"RAG evidence: {rag_evidence}\n"
        f"Recent commits: {recent_commits}"
    )

    return {
        **state,
        "investigation": investigation,
        "relevant_metrics": metrics,
        "relevant_logs": logs,
        "recent_commits": recent_commits,
        "rag_evidence": rag_evidence,
    }

async def analyze_incident(
    state: IncidentState,
) -> IncidentState:

    print("🔹 Analyzing incident...")

    analysis = await incident_analyzer.analyze(
        service=state["service"],
        message=state["message"],
        category=state.get("category", "unknown"),
        severity=state.get("severity", "unknown"),
        metrics=state.get("relevant_metrics", {}),
        logs=state.get("relevant_logs", []),
        recent_commits=state.get("recent_commits", []),
        rag_evidence=state.get("rag_evidence", []),
    )

    return {
        **state,
        "root_cause": analysis.root_cause,
        "confidence": analysis.confidence,
        "reasoning": analysis.reasoning,
        "supporting_evidence": analysis.supporting_evidence,
    }

def generate_final_response(
    state: IncidentState,
) -> IncidentState:

    print("🔹 Generating final response...")

    final_response = (
        f"Incident {state['incident_id']} "
        f"processed successfully.\n\n"

        f"Service: {state['service']}\n"
        f"Category: {state['category']}\n"
        f"Severity: {state['severity']}\n\n"

        f"Root Cause:\n"
        f"{state.get('root_cause', 'Unknown')}\n\n"

        f"Confidence:\n"
        f"{state.get('confidence', 0.0):.2f}\n\n"

        f"Reasoning:\n"
        f"{state.get('reasoning', 'Not available')}\n\n"

        f"Supporting Evidence:\n"
        f"{state.get('supporting_evidence', [])}\n\n"

        f"Investigation:\n"
        f"{state.get('investigation', 'Not available')}"
    )

    return {
        **state,
        "final_response": final_response,
    }

