"""Pydantic models for HolonDSL configuration and API schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ============================================================================
# HolonDSL Configuration Models (for parsing holon.yaml)
# ============================================================================


class TriggerType(str, Enum):
    """Types of triggers that can initiate a workflow."""

    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    ADAPTER = "adapter"
    WEBSOCKET = "websocket"
    WATCHER = "watcher"


class Trigger(BaseModel):
    """Trigger configuration."""

    type: TriggerType

    # Additional fields would be validated based on type
    # For now, accept any additional fields
    class Config:
        extra = "allow"


class ResourceType(str, Enum):
    """Types of resources in Holon."""

    AGENT = "agent"
    MCP_SERVER = "mcp-server"


class Resource(BaseModel):
    """A resource definition (agent or MCP server)."""

    id: str
    provider: Optional[str] = None  # e.g., "perplexity", "anthropic"
    model: Optional[str] = None  # e.g., "sonar-reasoning", "claude-3-5-sonnet"
    type: Optional[ResourceType] = None  # Only required for MCP servers
    command: Optional[str] = None  # For MCP servers
    args: Optional[List[str]] = None  # For MCP servers
    tools: Optional[List[str]] = None  # List of tool IDs (for agents)
    env: Optional[Dict[str, str]] = None  # Environment variables

    class Config:
        extra = "allow"


class WorkflowType(str, Enum):
    """Types of workflow execution patterns."""

    SEQUENTIAL = "sequential"
    SCATTER_GATHER = "scatter-gather"
    PARALLEL = "parallel"


class WorkflowStep(BaseModel):
    """A single step in a workflow."""

    id: str
    type: Optional[str] = None  # e.g., "scatter-gather", "agent"
    agent: Optional[str] = None  # Agent ID to use
    instruction: Optional[str] = None  # Instruction template for the agent
    inputs: Optional[List[str]] = None  # Input references from previous steps
    parallel_tasks: Optional[List[Dict[str, Any]]] = None  # For scatter-gather

    class Config:
        extra = "allow"


class Workflow(BaseModel):
    """Workflow definition."""

    type: WorkflowType
    steps: List[WorkflowStep]


class HolonConfig(BaseModel):
    """Complete HolonDSL configuration."""

    version: str
    project: str
    trigger: Optional[Trigger] = None
    resources: List[Resource]
    workflow: Workflow


# ============================================================================
# API Request/Response Models (matching swagger.yaml)
# ============================================================================


class DeployRequest(BaseModel):
    """Request body for POST /deploy."""

    name: str = Field(..., example="Daily-Briefing")
    config_yaml: str = Field(..., description="The raw YAML content of holon.yaml")
    env_vars: Optional[Dict[str, str]] = Field(None, description="Environment variables from .env file")


class DeployResponse(BaseModel):
    """Response for POST /deploy."""

    project_id: UUID
    status: str = Field(default="deployed")


class ProjectSummary(BaseModel):
    """Summary information about a project."""

    id: UUID
    name: str
    created_at: datetime


class RunStatus(str, Enum):
    """Status of a workflow run."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TriggerRunRequest(BaseModel):
    """Request body for POST /projects/{project_id}/run."""

    input_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional JSON payload to inject into ${trigger.input}",
        example={"topic": "Rust"},
    )


class TriggerRunResponse(BaseModel):
    """Response for POST /projects/{project_id}/run."""

    run_id: UUID
    status: RunStatus = Field(default=RunStatus.PENDING)


class RunDetail(BaseModel):
    """Detailed information about a run."""

    id: UUID
    project_id: UUID
    status: RunStatus
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="The final blackboard state"
    )
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class TraceEventStatus(str, Enum):
    """Status of a trace event."""

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TraceEventMetrics(BaseModel):
    """Metrics for a trace event."""

    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None


class TraceEvent(BaseModel):
    """A single trace event in a run's execution."""

    step_id: str
    status: TraceEventStatus
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    metrics: Optional[TraceEventMetrics] = None
    timestamp: datetime


class Project(BaseModel):
    """Storage model for a deployed project."""

    id: UUID
    name: str
    config_yaml: str
    env_vars: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    created_at: datetime


class Run(BaseModel):
    """Storage model for a workflow run."""

    id: UUID
    project_id: UUID
    status: RunStatus
    context: Optional[Dict[str, Any]] = Field(default=None)  # Blackboard state
    input_context: Optional[Dict[str, Any]] = Field(default=None)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    trace_events: List[TraceEvent] = Field(default_factory=list)


class VersionResponse(BaseModel):
    """Response for GET /version."""

    version: str = Field(..., description="Version of the Holon Engine")
