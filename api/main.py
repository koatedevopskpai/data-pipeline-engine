# FastAPI application factory. Why a factory pattern instead of a module-level app?
#
# 1. Test isolation: each test can call create_app() and get a fresh application
#    with no shared state, no cached middleware, no test-to-test contamination.
# 2. Configuration flexibility: create_app() could accept a Settings object in
#    the future, letting tests inject test configuration without env vars.
# 3. Multiple instances: unlikely needed here, but the factory pattern doesn't
#    prevent it — you could spin up two API instances with different middleware.
#
# The lifespan context manager is currently a no-op but exists as a hook for:
#   - Initialising the database connection pool on startup
#   - Loading the orchestrator with historical runs from persistent storage
#   - Registering health check callbacks
# Starting with the hook in place (even if empty) is cheaper than retrofitting it.
#
# CORS is wide-open (*) because this is a portfolio project. The dashboard
# (Streamlit on port 8501) needs to call the API (port 8000). In production,
# you'd restrict this to specific origins.
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Data Pipeline Engine API",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
