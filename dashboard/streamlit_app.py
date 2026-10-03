import json
from typing import Any

import httpx
import streamlit as st


API_BASE_URL = "http://localhost:8000"


def display_value(value: Any, fallback: str = "Not available") -> Any:
    return value if value not in (None, "") else fallback


def status_label(status: str | None, labels: dict[str, str]) -> str:
    if not status:
        return "Not available"
    return labels.get(status, status.replace("_", " ").title())


def render_incident_overview(incident: dict[str, Any]) -> None:
    st.header(f"Incident: {incident['incident_id']}")

    overview_columns = st.columns(4)
    overview_columns[0].metric(
        "Service",
        display_value(incident.get("service")),
    )
    overview_columns[1].metric(
        "Category",
        display_value(incident.get("category")),
    )
    overview_columns[2].metric(
        "Severity",
        display_value(incident.get("severity")),
    )
    overview_columns[3].metric(
        "Status",
        display_value(incident.get("status")),
    )

    with st.container(border=True):
        st.caption("Incident message")
        st.write(display_value(incident.get("message")))


def render_investigation(incident: dict[str, Any]) -> None:
    st.subheader("Investigation & AI Analysis")

    investigation_tab, analysis_tab = st.tabs(
        ["Investigation", "AI Analysis"]
    )

    with investigation_tab:
        st.markdown("#### Current Metrics")
        metric_columns = st.columns(3)
        metrics = incident.get("relevant_metrics")
        if not isinstance(metrics, dict):
            metrics = {}

        request_rate = metrics.get("request_rate")
        error_rate = metrics.get(
            "error_rate",
            incident.get("error_rate"),
        )
        average_latency = metrics.get("average_latency")

        metric_columns[0].metric(
            "Request Rate",
            display_value(request_rate),
        )
        metric_columns[1].metric(
            "Error Rate",
            display_value(error_rate),
        )
        metric_columns[2].metric(
            "Average Latency",
            display_value(average_latency),
        )

        with st.expander("Logs"):
            logs = incident.get("relevant_logs")
            if isinstance(logs, list) and logs:
                for log in logs:
                    st.write(log)
            else:
                st.info("No logs available.")

        with st.expander("Recent Commits"):
            commits = incident.get("recent_commits")
            if isinstance(commits, list) and commits:
                for commit in commits:
                    st.write(commit)
            else:
                st.info("No recent commits available.")

        with st.expander("Investigation Details"):
            st.write(
                display_value(
                    incident.get("investigation"),
                    "Investigation not available.",
                )
            )

    with analysis_tab:
        st.markdown("#### Root Cause")
        st.write(display_value(incident.get("root_cause")))

        st.markdown("#### AI Reasoning")
        st.write(display_value(incident.get("reasoning")))

        st.markdown("#### Supporting Evidence")
        evidence = incident.get("supporting_evidence") or []
        if evidence:
            for item in evidence:
                st.write(f"- {item}")
        else:
            st.info("No supporting evidence available.")

        st.markdown("#### Expected Impact")
        st.write(display_value(incident.get("expected_impact")))

        st.markdown("#### Risks")
        risks = incident.get("risks") or []
        if risks:
            for risk in risks:
                st.write(f"- {risk}")
        else:
            st.info("No risks reported.")


def get_remediation(incident: dict[str, Any]) -> dict[str, Any] | None:
    value = incident.get("remediation")

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None

    return None


def render_remediation(incident: dict[str, Any]) -> None:
    st.subheader("Recommended Remediation")
    remediation = get_remediation(incident)

    if not remediation:
        st.info("No remediation recommendation available.")
        return

    st.markdown(
        f"**Action:** {display_value(remediation.get('action'))}"
    )
    st.markdown(
        f"**Description:** "
        f"{display_value(remediation.get('description'))}"
    )

    st.markdown("**Parameters**")
    parameters = remediation.get("parameters") or {}
    if parameters:
        for name, value in parameters.items():
            st.write(f"- {name.replace('_', ' ').title()}: {value}")
    else:
        st.caption("No parameters provided.")

    st.markdown(
        f"**Expected Impact:** "
        f"{display_value(remediation.get('expected_impact'))}"
    )

    st.markdown("**Risks**")
    risks = remediation.get("risks") or []
    if risks:
        for risk in risks:
            st.write(f"- {risk}")
    else:
        st.caption("No risks reported.")


def render_approval(
    incident: dict[str, Any],
    incident_id: str,
) -> None:
    approval_status = incident.get("approval_status") or "unknown"
    approval_reason = incident.get("approval_reason")

    if approval_status == "pending":
        st.warning("Human approval required.")
        approval_columns = st.columns(2)

        if approval_columns[0].button("Approve Remediation"):
            try:
                response = httpx.post(
                    f"{API_BASE_URL}/api/v1/incidents/"
                    f"{incident_id}/approval",
                    json={
                        "decision": "approve",
                        "reason": "Approved from dashboard.",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                st.session_state["approval_message"] = (
                    "Remediation approval submitted."
                )
                st.rerun()
            except httpx.HTTPError as exc:
                st.error(f"Could not approve remediation: {exc}")

        if approval_columns[1].button("Reject Remediation"):
            try:
                response = httpx.post(
                    f"{API_BASE_URL}/api/v1/incidents/"
                    f"{incident_id}/approval",
                    json={
                        "decision": "reject",
                        "reason": "Rejected from dashboard.",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                st.session_state["approval_message"] = (
                    "Remediation rejection submitted."
                )
                st.rerun()
            except httpx.HTTPError as exc:
                st.error(f"Could not reject remediation: {exc}")
    elif approval_status == "approved":
        st.success("Remediation approved.")
    elif approval_status == "rejected":
        st.error("Remediation rejected.")
        st.write(
            f"**Reason:** {display_value(approval_reason)}"
        )
    else:
        st.info(
            f"Approval status: "
            f"{status_label(approval_status, {})}"
        )


def render_workflow_status(incident: dict[str, Any]) -> None:
    st.subheader("Workflow Status")
    approval_status = incident.get("approval_status")
    execution_status = incident.get("execution_status")
    verification_status = incident.get("verification_status")

    status_columns = st.columns(3)
    status_columns[0].metric(
        "Approval",
        status_label(
            approval_status,
            {
                "approved": "Approved",
                "rejected": "Rejected",
                "pending": "Pending",
            },
        ),
    )
    status_columns[1].metric(
        "Execution",
        status_label(
            execution_status,
            {
                "completed": "Completed",
                "failed": "Failed",
                "skipped": "Not executed",
            },
        ),
    )
    status_columns[2].metric(
        "Verification",
        status_label(
            verification_status,
            {
                "passed": "Passed",
                "failed": "Failed",
                "skipped": "Skipped",
            },
        ),
    )


def render_execution_result(incident: dict[str, Any]) -> None:
    result = incident.get("execution_result") or {}
    if not result:
        st.info("Remediation has not been executed.")
        return

    st.markdown("#### Remediation Execution")
    st.write(
        f"**Action:** {display_value(result.get('action'))}"
    )

    if result.get("status") == "success":
        st.success("Result: Successful")
    elif result.get("error") or result.get("reason"):
        st.error(
            f"Result: {display_value(result.get('error') or result.get('reason'))}"
        )
    else:
        st.write(
            f"**Result:** {display_value(result.get('status'))}"
        )

    with st.expander("View raw execution details"):
        st.json(result)


def render_verification_result(incident: dict[str, Any]) -> None:
    result = incident.get("verification_result") or {}
    if not result:
        st.info("Verification has not run.")
        return

    st.markdown("#### Remediation Verification")
    verification_status = incident.get("verification_status")
    if verification_status == "passed":
        st.success("Status: Passed")
    elif verification_status == "failed":
        st.error("Status: Failed")
    elif verification_status == "skipped":
        st.warning(
            f"Status: Skipped — "
            f"{display_value(result.get('reason'))}"
        )
    else:
        st.info(
            f"Status: {status_label(verification_status, {})}"
        )

    before = result.get("before") or {}
    after = result.get("after") or {}
    if before or after:
        before_column, after_column = st.columns(2)
        with before_column:
            st.markdown("**Before**")
            st.write(
                f"Error Rate: "
                f"{display_value(before.get('error_rate'))}"
            )
            st.write(
                f"Average Latency: "
                f"{display_value(before.get('average_latency'))}"
            )
        with after_column:
            st.markdown("**After**")
            st.write(
                f"Error Rate: "
                f"{display_value(after.get('error_rate'))}"
            )
            st.write(
                f"Average Latency: "
                f"{display_value(after.get('average_latency'))}"
            )

    message = result.get("message")
    if message:
        st.write(f"**Message:** {message}")

    with st.expander("View raw verification details"):
        st.json(result)


def render_technical_details(incident: dict[str, Any]) -> None:
    st.subheader("Technical Details")
    with st.expander("Raw Incident Data"):
        st.json(incident)
    with st.expander("Raw Execution Result"):
        st.json(incident.get("execution_result") or {})
    with st.expander("Raw Verification Result"):
        st.json(incident.get("verification_result") or {})
    with st.expander("Workflow / Debug Information"):
        st.write(
            {
                "thread_id": incident.get("thread_id"),
                "updated_at": incident.get("updated_at"),
            }
        )


st.set_page_config(
    page_title="AI-SRE Incident Dashboard",
    page_icon="AI",
    layout="wide",
)

st.title("AI-SRE Incident Dashboard")
st.caption("AI-powered incident investigation, remediation and verification")

try:
    health_response = httpx.get(
        f"{API_BASE_URL}/health",
        timeout=10,
    )
    health_response.raise_for_status()
    health = health_response.json()

    if health.get("status") == "ok":
        st.success("Backend connected.")
    else:
        st.warning(
            f"FastAPI returned an unexpected health response: {health}"
        )
except httpx.HTTPError as exc:
    st.error(f"Could not connect to the FastAPI backend: {exc}")


with st.sidebar:
    st.header("AI-SRE")
    st.caption("Incident Operations")
    st.divider()
    st.markdown("**Backend**")
    st.caption("Connected" if "health" in locals() else "Unavailable")

    incidents: list[dict[str, Any]] = []
    try:
        response = httpx.get(
            f"{API_BASE_URL}/api/v1/incidents/",
            timeout=10,
        )
        response.raise_for_status()
        incidents = response.json()
    except httpx.HTTPError as exc:
        st.error(f"Could not load incident history: {exc}")

    if st.button("Refresh incidents", use_container_width=True):
        st.rerun()

    selected_incident_id = None
    if incidents:
        selected_incident_id = st.selectbox(
            "Select Incident",
            [incident["incident_id"] for incident in incidents],
        )
        selected_summary = next(
            incident
            for incident in incidents
            if incident["incident_id"] == selected_incident_id
        )
        st.divider()
        st.caption("Selected incident")
        st.write(f"**ID:** {selected_summary['incident_id']}")
        st.write(f"**Service:** {selected_summary.get('service')}")
        st.write(f"**Severity:** {selected_summary.get('severity')}")
        st.write(f"**Status:** {selected_summary.get('status')}")


if not selected_incident_id:
    st.info("Select an incident from the sidebar to view its details.")
else:
    detail_url = (
        f"{API_BASE_URL}/api/v1/incidents/"
        f"{selected_incident_id}"
    )
    try:
        detail_response = httpx.get(
            detail_url,
            timeout=10,
        )
        detail_response.raise_for_status()
        selected_incident = detail_response.json()

        approval_message = st.session_state.pop(
            "approval_message",
            None,
        )
        if approval_message:
            st.success(approval_message)

        render_incident_overview(selected_incident)
        st.divider()
        render_investigation(selected_incident)
        st.divider()
        render_remediation(selected_incident)
        render_approval(selected_incident, selected_incident_id)
        st.divider()
        render_workflow_status(selected_incident)
        render_execution_result(selected_incident)
        render_verification_result(selected_incident)
        st.divider()
        render_technical_details(selected_incident)
    except httpx.HTTPError as exc:
        st.error(f"Could not load incident details: {exc}")
