"""FastAPI application for the Holon Engine API."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    DeployRequest,
    DeployResponse,
    ProjectSummary,
    ProcessSummary,
    TriggerRunRequest,
    TriggerRunResponse,
    RunDetail,
    VersionResponse,
    Project,
    Run,
    RunStatus,
    TraceEvent,
)
from .persistence import get_persistence, PersistenceService
from .engine import WorkflowEngine
from . import __version__


# Set up logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize persistence on startup."""
    # Ensure persistence layer is ready (e.g. create folders)
    get_persistence()
    yield


# Create FastAPI app
app = FastAPI(
    title="Holon Engine API",
    description="The control plane API for the Holon Agent Orchestration Engine.",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}


@app.get("/version", response_model=VersionResponse)
async def get_version():
    """Get the version of the Holon Engine."""
    return VersionResponse(version=__version__)


@app.post("/api/v1/deploy", response_model=DeployResponse)
async def deploy_project(request: DeployRequest):
    """Deploy a HolonDSL configuration."""
    store = get_persistence()

    project_id = uuid4()
    project = Project(
        id=project_id,
        name=request.name,
        config_yaml=request.config_yaml,
        env_vars=request.env_vars,
        created_at=datetime.utcnow(),
    )

    try:
        store.save_project(project)
        logger.info(f"Deployed project {project.name} ({project_id})")
        return DeployResponse(project_id=project_id, status="deployed")
    except Exception as e:
        logger.error(f"Failed to deploy project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/projects", response_model=List[ProjectSummary])
async def list_projects():
    """List all deployed projects."""
    store = get_persistence()
    projects = store.list_projects()

    return [
        ProjectSummary(id=p.id, name=p.name, created_at=p.created_at) for p in projects
    ]


@app.get("/api/v1/processes", response_model=List[ProcessSummary])
async def list_processes():
    """List all deployed processes (for CLI list command)."""
    store = get_persistence()
    projects = store.list_projects()

    # Convert to ProcessSummary with additional fields for the CLI
    processes = []
    for p in projects:
        # Calculate uptime (time since created)
        uptime = None
        if p.created_at:
            delta = datetime.utcnow() - p.created_at
            hours = int(delta.total_seconds() / 3600)
            if hours < 24:
                uptime = f"{hours}h"
            else:
                days = hours // 24
                uptime = f"{days}d"

        # Extract trigger type from config if available
        trigger_type = None
        try:
            import yaml

            config = yaml.safe_load(p.config_yaml)
            if config and "trigger" in config:
                trigger_type = config["trigger"].get("type", "N/A")
        except Exception:
            pass

        processes.append(
            ProcessSummary(
                id=str(p.id),
                name=p.name,
                status="deployed",
                uptime=uptime,
                triggers=trigger_type,
            )
        )

    return processes


@app.post(
    "/api/v1/projects/{project_id}/run",
    response_model=TriggerRunResponse,
    status_code=202,
)
async def trigger_run(
    project_id: UUID, request: TriggerRunRequest, background_tasks: BackgroundTasks
):
    """Trigger a new run for a project."""
    store = get_persistence()
    project = store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    run_id = uuid4()
    run = Run(
        id=run_id,
        project_id=project_id,
        status=RunStatus.PENDING,
        input_context=request.input_context,
        started_at=None,
        ended_at=None,
    )

    store.save_run(run)

    # Initialize engine and run in background
    engine_instance = WorkflowEngine(store)
    background_tasks.add_task(engine_instance.execute_run, run_id, project.config_yaml)

    return TriggerRunResponse(run_id=run_id, status=RunStatus.PENDING)


@app.get("/api/v1/runs/{run_id}", response_model=RunDetail)
async def get_run(run_id: UUID):
    """Get details of a specific run."""
    store = get_persistence()
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunDetail(
        id=run.id,
        project_id=run.project_id,
        status=run.status,
        context=run.context,
        started_at=run.started_at,
        ended_at=run.ended_at,
    )


@app.get("/api/v1/runs/{run_id}/logs", response_model=List[TraceEvent])
async def get_run_logs(run_id: UUID):
    """Get the trace logs for a run."""
    store = get_persistence()
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return run.trace_events


@app.get("/api/v1/processes/{process_id}/logs", response_model=List[TraceEvent])
async def get_process_logs(process_id: UUID):
    """Get the trace logs for the most recent run of a process/project."""
    store = get_persistence()
    project = store.get_project(process_id)
    if not project:
        raise HTTPException(status_code=404, detail="Process not found")

    # Find the most recent run for this project
    # For now, we'll try to find runs by checking the runs directory
    import os

    runs_dir = store._path("runs")
    if not store.fs.exists(runs_dir):
        return []

    run_files = store.fs.glob(f"{runs_dir}/*.json")
    latest_run = None
    latest_time = None

    for run_file in run_files:
        try:
            with store.fs.open(run_file, "r") as f:
                import json

                run_data = json.load(f)
                if run_data.get("project_id") == str(project_id):
                    started_at = run_data.get("started_at")
                    if started_at and (latest_time is None or started_at > latest_time):
                        latest_time = started_at
                        latest_run = Run(**run_data)
        except Exception:
            continue

    if latest_run:
        return latest_run.trace_events
    return []
