# API routes use a lazy-initialised global orchestrator rather than dependency
# injection. This is a tradeoff worth explaining:
#
# True DI (passing orchestrator via FastAPI Depends):
# + Cleaner testability — inject mock orchestrator in tests
# + Explicit dependencies visible in function signatures
# - Requires FastAPI's dependency resolution — couples routes to FastAPI
# - Overkill for a single-instance orchestrator that has no external state
#
# Global lazy init:
# + No DI framework ceremony for a portfolio project
# + Orchestra created on first use, not at import time (avoids import-time side effects)
# + Simple to understand — functions are just functions
# - Cannot swap orchestrator per-request
# - Global state makes parallel request handling theoretically unsafe
#
# For a portfolio project demonstrating data engineering patterns, the global
# init is appropriate. The orchestrator is stateless between pipeline runs
# (each run creates its own PipelineRun object), so there's no shared state
# risk. If this were a production multi-tenant service, we'd use DI.
#
# DataResponse and RunResponse are Pydantic models (not raw dicts) because:
# 1. FastAPI generates OpenAPI schema from Pydantic models automatically
# 2. Response validation — if a field is missing, you get an error at
#    serialisation time, not at the client's JSON parse time
# 3. Self-documenting — the model IS the API contract
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from pipeline.config import Settings
from pipeline.run import PipelineOrchestrator

router = APIRouter()
_orchestrator: PipelineOrchestrator | None = None


def get_orchestrator() -> PipelineOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PipelineOrchestrator()
    return _orchestrator


class RunResponse(BaseModel):
    run_id: str
    status: str
    rows_read: int
    rows_written: int
    error_log: list[str]


class DataResponse(BaseModel):
    table: str
    rows: list[dict]
    count: int


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/pipeline/run")
def run_pipeline(source_path: str = Query("data/sample")):
    orchestrator = get_orchestrator()
    result = orchestrator.run_csv_pipeline(source_path=source_path)
    return RunResponse(
        run_id=result.run_id,
        status=result.status.value,
        rows_read=result.rows_read,
        rows_written=result.rows_written,
        error_log=result.error_log,
    )


@router.get("/pipeline/runs")
def list_runs():
    orchestrator = get_orchestrator()
    return [RunResponse(
        run_id=r.run_id,
        status=r.status.value,
        rows_read=r.rows_read,
        rows_written=r.rows_written,
        error_log=r.error_log,
    ) for r in orchestrator.get_runs()]


@router.get("/data/{table_name}")
def get_data(table_name: str):
    # Direct SQLite access rather than going through the orchestrator.
    # The orchestrator orchestrates pipeline runs; it's not a data access layer.
    # Mixing those responsibilities would violate single responsibility principle.
    # When the API needs to read data, it reads it directly.
    settings = Settings()
    db_path = settings.db_url.replace("sqlite:///", "")
    if not Path(db_path).exists():
        raise HTTPException(status_code=404, detail="Database not found")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    conn.close()
    return DataResponse(table=table_name, rows=rows, count=len(rows))
