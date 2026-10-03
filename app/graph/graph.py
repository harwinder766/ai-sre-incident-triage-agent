from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph, START, END
from .state import IncidentState
from .nodes import(
    ingest_incident,
    classify_incident,
    investigate_incident,
    generate_final_response,
    analyze_incident,
    request_approval,
    execute_external_actions,
    execute_remediation_action,
    verify_remediation,
)


def compile_graph(checkpointer: BaseCheckpointSaver):
    builder = StateGraph(IncidentState)

    builder.add_node("ingest_incident", ingest_incident)
    builder.add_node("classify_incident", classify_incident)
    builder.add_node("investigate_incident", investigate_incident)
    builder.add_node("analyze_incident", analyze_incident)
    builder.add_node("request_approval", request_approval)
    builder.add_node("execute_external_actions", execute_external_actions)
    builder.add_node("execute_remediation_action", execute_remediation_action)
    builder.add_node("verify_remediation", verify_remediation)
    builder.add_node("generate_final_response", generate_final_response)

    builder.add_edge(START, "ingest_incident")
    builder.add_edge("ingest_incident", "classify_incident")
    builder.add_edge("classify_incident", "investigate_incident")
    builder.add_edge("investigate_incident", "analyze_incident")
    builder.add_edge("analyze_incident", "request_approval")

    def route_after_approval(state: IncidentState) -> str:
        approval_status = state.get("approval_status")

        if approval_status == "approved":
            return "approved"

        if approval_status == "rejected":
            return "rejected"

        raise ValueError(
            f"Unexpected approval status: {approval_status}"
        )

    builder.add_conditional_edges(
        "request_approval",
        route_after_approval,
        {
            "approved": "execute_external_actions",
            "rejected": "generate_final_response",
        },
    )
    builder.add_edge("execute_external_actions", "execute_remediation_action")
    builder.add_edge("execute_remediation_action", "verify_remediation")
    builder.add_edge("verify_remediation", "generate_final_response")
    builder.add_edge("generate_final_response", END)

    return builder.compile(checkpointer=checkpointer)
