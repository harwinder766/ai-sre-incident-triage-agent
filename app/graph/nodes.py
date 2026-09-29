from .state import IncidentState
from app.investigation.investigator import incident_investigator
from app.analysis.analyzer import incident_analyzer
from app.actions.github_action import create_incident_issue
from app.actions.slack_actions import notify_incident   
from app.actions.remediation_actions import execute_remediation
from app.tools.prometheus import prometheus_tool

from langgraph.types import interrupt
import asyncio
from langgraph.types import interrupt


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
        incident_message=state["message"],
        incident_error_rate=state.get("error_rate", 0.0),
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
        "remediation": analysis.remediation,
        "expected_impact": analysis.expected_impact,
        "risks": analysis.risks,
    }

def request_approval(state: IncidentState) -> IncidentState:
    print("🔹 Waiting for human approval...")

    approval_request = {
        "incident_id": state["incident_id"],
        "service": state["service"],
        "severity": state.get("severity", "unknown"),
        "root_cause": state.get("root_cause", "Unknown"),
        "confidence": state.get("confidence", 0.0),
        "reasoning": state.get("reasoning", ""),
        "supporting_evidence": state.get(
            "supporting_evidence",
            [],
        ),
        "remediation": state.get(
            "remediation",
            "No remediation proposed.",
        ),
        "expected_impact": state.get(
            "expected_impact",
            "Unknown.",
        ),
        "risks": state.get(
            "risks",
            [],
        ),
    }

    human_response = interrupt(approval_request)

    if not isinstance(human_response, dict):
        raise ValueError(
            "Human approval response must be a dictionary."
        )

    decision = human_response.get("decision")

    if decision not in {"approve", "reject"}:
        raise ValueError(
            "Approval decision must be either 'approve' or 'reject'."
        )

    if decision == "approve":
        return {
            **state,
            "approval_status": "approved",
            "approval_reason": human_response.get(
                "reason",
                "Approved by human.",
            ),
        }

    return {
        **state,
        "approval_status": "rejected",
        "approval_reason": human_response.get(
            "reason",
            "Rejected by human.",
        ),
    }

async def execute_external_actions(
    state: IncidentState,
) -> IncidentState:
    print("🔹 Executing external actions...")

    if state.get("approval_status") != "approved":
        print("   Skipping external actions: remediation not approved.")

        return {
            **state,
            "github_issue": {
                "status": "skipped",
                "reason": "Remediation was not approved.",
            },
            "slack_notification": {
                "status": "skipped",
                "reason": "Remediation was not approved.",
            },
        }

    github_task = create_incident_issue(
        incident_id=state["incident_id"],
        service=state["service"],
        severity=state.get("severity", "unknown"),
        root_cause=state.get("root_cause", "Unknown"),
        confidence=state.get("confidence", 0.0),
        reasoning=state.get("reasoning", ""),
        supporting_evidence=state.get(
            "supporting_evidence",
            [],
        ),
        remediation=state.get(
            "remediation",
            "Not available",
        ),
        expected_impact=state.get(
            "expected_impact",
            "Not available",
        ),
        risks=state.get(
            "risks",
            [],
        ),
    )

    github_result = None

    try:
        github_result = await github_task

    except Exception as exc:
        github_result = {
            "status": "failed",
            "error": str(exc),
        }

    github_url = None

    if github_result.get("status") != "failed":
        github_url = github_result.get("url")

    try:
        slack_result = await notify_incident(
            incident_id=state["incident_id"],
            service=state["service"],
            severity=state.get("severity", "unknown"),
            root_cause=state.get("root_cause", "Unknown"),
            confidence=state.get("confidence", 0.0),
            remediation=state.get(
                "remediation",
                "Not available",
            ),
            approval_status=state.get(
                "approval_status",
                "unknown",
            ),
            github_issue_url=github_url,
        )

    except Exception as exc:
        slack_result = {
            "status": "failed",
            "error": str(exc),
        }

    return {
        **state,
        "github_issue": github_result,
        "slack_notification": slack_result,
    }

async def execute_remediation_action(state: IncidentState) -> IncidentState:
    print('🔹 Executing remediation action...')
    if state.get("approval_status") != "approved":
        return {
            **state,
            "execution_status": "skipped",
            "execution_result": {
                "status": "failed",
                "reason": "Remediation was not approved by human.",
            },
        }

    if state.get("remediation") is None:
        return {
            **state,
            "execution_status": "skipped",
            "execution_result": {
                "status": "failed",
                "reason": "No remediation plan provided.",
            },
        }

    remediation = state["remediation"]

    try:
        result = await execute_remediation(remediation)
        return {
            **state,
            "execution_status": "completed",
            "execution_result": result,
        }
    # except Exception as exc:
    #     return {
    #         **state,
    #         "execution_status": "failed",
    #         "execution_result": {
    #             "status": "failed",
    #             "error": str(exc),
    #         }
    #     }

    except Exception as exc:
        print("\n❌ Remediation execution failed")
        print("Remediation:", remediation)
        print("Exception type:", type(exc).__name__)
        print("Exception:", exc)
    
        return {
            **state,
            "execution_status": "failed",
            "execution_result": {
                "status": "failed",
                "error": str(exc),
            },
        }

async def verify_remediation(
    state: IncidentState,
) -> IncidentState:

    print("🔹 Verifying remediation...")

    if state.get("execution_status") != "completed":

        return {
            **state,
            "verification_status": "skipped",
            "verification_result": {
                "status": "skipped",
                "reason": "Remediation was not completed.",
            },
        }

    await asyncio.sleep(5)

    try:

        metrics = await prometheus_tool.get_service_metrics(
            service=state["service"]
        )

        before_metrics = state.get(
            "relevant_metrics",
            {},
        )

        before_error_rate = float(
            before_metrics.get(
                "error_rate",
                0.0,
            )
        )

        before_latency = float(
            before_metrics.get(
                "average_latency",
                0.0,
            )
        )

        after_error_rate = float(
            metrics.get(
                "error_rate",
                0.0,
            )
        )

        after_latency = float(
            metrics.get(
                "average_latency",
                0.0,
            )
        )

        error_rate_recovered = after_error_rate < 0.10

        latency_recovered = (
            after_latency < 2.0
            if after_latency > 0
            else True
        )

        error_rate_improved = (
            after_error_rate < before_error_rate
        )

        latency_improved = (
            after_latency < before_latency
            if before_latency > 0
            else True
        )

        passed = (
            error_rate_recovered
            and latency_recovered
            and error_rate_improved
        )

        if passed:

            verification_status = "passed"

            verification_result = {
                "status": "passed",
                "message": (
                    "System metrics indicate that the "
                    "incident has recovered after remediation."
                ),
                "before": {
                    "error_rate": before_error_rate,
                    "average_latency": before_latency,
                },
                "after": {
                    "error_rate": after_error_rate,
                    "average_latency": after_latency,
                },
            }

        else:

            verification_status = "failed"

            verification_result = {
                "status": "failed",
                "message": (
                    "The remediation executed successfully, "
                    "but the system has not recovered sufficiently."
                ),
                "before": {
                    "error_rate": before_error_rate,
                    "average_latency": before_latency,
                },
                "after": {
                    "error_rate": after_error_rate,
                    "average_latency": after_latency,
                },
                "checks": {
                    "error_rate_recovered": error_rate_recovered,
                    "latency_recovered": latency_recovered,
                    "error_rate_improved": error_rate_improved,
                    "latency_improved": latency_improved,
                },
            }

        return {
            **state,
            "verification_status": verification_status,
            "verification_result": verification_result,
            "post_remediation_metrics": metrics,
        }

    except Exception as exc:

        return {
            **state,
            "verification_status": "failed",
            "verification_result": {
                "status": "failed",
                "reason": "Unable to verify remediation.",
                "error": str(exc),
            },
        }

def generate_final_response(
    state: IncidentState,
) -> IncidentState:

    verification_status = state.get(
        "verification_status",
        "not_started",
    )

    verification_result = state.get(
        "verification_result",
        {},
    )

    final_response = (
        f"Incident {state['incident_id']} processed.\n\n"

        f"Service: {state['service']}\n"
        f"Category: {state.get('category', 'unknown')}\n"
        f"Severity: {state.get('severity', 'unknown')}\n\n"

        f"========== ROOT CAUSE ==========\n"
        f"{state.get('root_cause', 'Unknown')}\n\n"

        f"Confidence:\n"
        f"{state.get('confidence', 0.0):.2f}\n\n"

        f"========== REMEDIATION ==========\n"
        f"{state.get('remediation', {})}\n\n"

        f"Expected Impact:\n"
        f"{state.get('expected_impact', 'Unknown')}\n\n"

        f"Risks:\n"
        f"{state.get('risks', [])}\n\n"

        f"========== APPROVAL ==========\n"
        f"Status: {state.get('approval_status', 'unknown')}\n"
        f"Reason: {state.get('approval_reason', 'Unknown')}\n\n"

        f"========== EXECUTION ==========\n"
        f"Status: {state.get('execution_status', 'not_started')}\n"
        f"Result: {state.get('execution_result', {})}\n\n"

        f"========== VERIFICATION ==========\n"
        f"Status: {verification_status}\n"
        f"Result: {verification_result}\n"
    )

    return {
        **state,
        "final_response": final_response,
    }