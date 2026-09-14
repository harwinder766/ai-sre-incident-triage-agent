from langgraph.graph import StateGraph, START, END
from .state import IncidentState
from .nodes import(
    ingest_incident,
    classify_incident,
    investigate_incident,
    generate_final_response
)

builder = StateGraph(IncidentState)

builder.add_node('ingest_incident', ingest_incident)
builder.add_node('classify_incident', classify_incident)
builder.add_node('investigate_incident', investigate_incident)
builder.add_node('generate_final_response', generate_final_response)

builder.add_edge(START, 'ingest_incident')
builder.add_edge('ingest_incident', 'classify_incident')
builder.add_edge('classify_incident', 'investigate_incident')
builder.add_edge('investigate_incident', 'generate_final_response')
builder.add_edge('generate_final_response', END)

graph = builder.compile()

