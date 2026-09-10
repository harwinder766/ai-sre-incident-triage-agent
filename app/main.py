from fastapi import FastAPI

from app.api.routes_incidents import router as incidents_router


app = FastAPI(
    title="AI-SRE Incident Triage Agent",
    description="Agentic AI system for incident investigation and controlled response.",
    version="0.1.0",
)


app.include_router(incidents_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
