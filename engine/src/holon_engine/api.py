"""FastAPI application for the Holon Engine API."""

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
    TriggerRunRequest,
    TriggerRunResponse,
    RunDetail,
    TraceEvent,
    RunStatus,
)
from .database import init_db, get_session_maker, Project, Run
from .engine import WorkflowEngine


# Global database session maker
SessionMaker = None
engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    global SessionMaker, engine
    engine = init_db()
    SessionMaker = get_session_maker(engine)
    yield
    # Cleanup on shutdown (if needed)


# Create FastAPI app
app = FastAPI(
    title="Holon Engine API",
    description="The control plane API for the Holon Agent Orchestration Engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/api/v1/deploy", response_model=DeployResponse, status_code=200)
async def deploy_project(request: DeployRequest):
    """
    Deploy a Project.
    
    Validates and registers a new HolonDSL configuration.
    """
    session = SessionMaker()
    try:
        # Validate the YAML by parsing it
        workflow_engine = WorkflowEngine(session)
        try:
            config = workflow_engine.parse_config(request.config_yaml)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML Configuration: {str(e)}")
        
        # Create and store the project
        project = Project(
            id=str(uuid4()),
            name=request.name,
            config_yaml=request.config_yaml,
            created_at=datetime.utcnow()
        )
        session.add(project)
        session.commit()
        
        return DeployResponse(
            project_id=UUID(project.id),
            status="deployed"
        )
    finally:
        session.close()


@app.get("/api/v1/projects", response_model=List[ProjectSummary])
async def list_projects():
    """
    List Projects.
    
    Returns a list of all deployed projects.
    """
    session = SessionMaker()
    try:
        projects = session.query(Project).order_by(Project.created_at.desc()).all()
        return [
            ProjectSummary(
                id=UUID(p.id),
                name=p.name,
                created_at=p.created_at
            )
            for p in projects
        ]
    finally:
        session.close()


@app.post("/api/v1/projects/{project_id}/run", response_model=TriggerRunResponse, status_code=202)
async def trigger_run(project_id: UUID, request: TriggerRunRequest, background_tasks: BackgroundTasks):
    """
    Trigger a Run.
    
    Manually triggers a workflow execution for a specific project.
    """
    session = SessionMaker()
    try:
        # Find the project
        project = session.query(Project).filter(Project.id == str(project_id)).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create a new run
        run = Run(
            id=str(uuid4()),
            project_id=project.id,
            status=RunStatus.PENDING,
            input_context=request.input_context,
            started_at=None,
            ended_at=None
        )
        session.add(run)
        session.commit()
        
        # Execute the run in the background
        background_tasks.add_task(execute_run_task, str(run.id), project.config_yaml)
        
        return TriggerRunResponse(
            run_id=UUID(run.id),
            status=RunStatus.PENDING
        )
    finally:
        session.close()


@app.get("/api/v1/runs/{run_id}", response_model=RunDetail)
async def get_run_status(run_id: UUID):
    """
    Get Run Status.
    
    Retrieve the current status and context of a specific run.
    """
    session = SessionMaker()
    try:
        run = session.query(Run).filter(Run.id == str(run_id)).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        
        return RunDetail(
            id=UUID(run.id),
            project_id=UUID(run.project_id),
            status=run.status,
            context=run.context,
            started_at=run.started_at,
            ended_at=run.ended_at
        )
    finally:
        session.close()


@app.get("/api/v1/runs/{run_id}/logs", response_model=List[TraceEvent])
async def get_run_logs(run_id: UUID):
    """
    Get Run Logs (Trace).
    
    Retrieve the list of trace events (steps executed) for a run.
    """
    session = SessionMaker()
    try:
        run = session.query(Run).filter(Run.id == str(run_id)).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        
        # Get trace events ordered by timestamp
        trace_events = session.query(
            # Import TraceEvent from database to avoid name collision
            __import__('holon_engine.database', fromlist=['TraceEvent']).TraceEvent
        ).filter_by(run_id=run.id).order_by(
            __import__('holon_engine.database', fromlist=['TraceEvent']).TraceEvent.timestamp
        ).all()
        
        return [
            TraceEvent(
                step_id=te.step_id,
                status=te.status,
                input=te.input,
                output=te.output,
                metrics=te.metrics,
                timestamp=te.timestamp
            )
            for te in trace_events
        ]
    finally:
        session.close()


# ============================================================================
# Background Tasks
# ============================================================================

def execute_run_task(run_id: str, config_yaml: str):
    """
    Background task to execute a workflow run.
    
    This runs asynchronously so the API can return immediately.
    """
    session = SessionMaker()
    try:
        run = session.query(Run).filter(Run.id == run_id).first()
        if not run:
            return
        
        workflow_engine = WorkflowEngine(session)
        workflow_engine.execute_run(run, config_yaml)
    except Exception as e:
        # Error handling is done within execute_run
        print(f"Error executing run {run_id}: {e}")
    finally:
        session.close()


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
