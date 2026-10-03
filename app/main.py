import asyncio
import sys
from contextlib import asynccontextmanager

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI  # type: ignore[import-not-found]
from langgraph.checkpoint.postgres.aio import (
    AsyncConnectionPool,
    AsyncPostgresSaver,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from psycopg.rows import dict_row
from sqlalchemy.engine import make_url

from app.api.routes_incidents import router as incidents_router
from app.api.routes_alerts import router as alerts_router
from app.analysis.schema import RemediationPlan
from app.db.database import DATABASE_URL
from app.graph.graph import compile_graph
from app.adapters.simulator import register_simulator_adapters

from app.rag.factory import create_rag_tool

rag_tool = create_rag_tool()

checkpoint_database_url = make_url(DATABASE_URL).set(
    drivername="postgresql"
).render_as_string(hide_password=False)

checkpoint_serde = JsonPlusSerializer(
    allowed_msgpack_modules=(RemediationPlan,),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncConnectionPool(
        checkpoint_database_url,
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row,
        },
        min_size=1,
        max_size=10,
    ) as pool:
        checkpointer = AsyncPostgresSaver(
            conn=pool,
            serde=checkpoint_serde,
        )
        await checkpointer.setup()
        register_simulator_adapters()
        app.state.checkpointer = checkpointer
        app.state.graph = compile_graph(checkpointer)
        yield
        app.state.graph = None
        app.state.checkpointer = None


app = FastAPI(
    title="AI-SRE Incident Triage Agent",
    description="Agentic AI system for incident investigation and controlled response.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(incidents_router)
app.include_router(alerts_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
