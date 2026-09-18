from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import IncidentState
from .nodes import(
    ingest_incident,
    classify_incident,
    investigate_incident,
    generate_final_response,
    analyze_incident,
    request_approval,
    route_after_approval,
)

builder = StateGraph(IncidentState)

builder.add_node('ingest_incident', ingest_incident)
builder.add_node('classify_incident', classify_incident)
builder.add_node('investigate_incident', investigate_incident)
builder.add_node('analyze_incident', analyze_incident)
builder.add_node('request_approval', request_approval)
builder.add_node('generate_final_response', generate_final_response)

checkpointer = InMemorySaver()

builder.add_edge(START, 'ingest_incident')
builder.add_edge('ingest_incident', 'classify_incident')
builder.add_edge('classify_incident', 'investigate_incident')
builder.add_edge('investigate_incident', 'analyze_incident')
builder.add_edge('analyze_incident', 'request_approval')
builder.add_conditional_edges(
    "request_approval",
    route_after_approval,
    {
        "approved": "generate_final_response",
        "rejected": "generate_final_response",
    },
)
builder.add_edge(
    "generate_final_response",
    END,
)

graph = builder.compile(checkpointer=checkpointer)
