"""Pydantic models for Holon configuration validation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TriggerConfig(BaseModel):
    """Configuration for workflow triggers."""

    type: str = Field(
        ..., description="Trigger type (schedule, webhook, adapter, websocket, watcher)"
    )
    cron: Optional[str] = Field(None, description="Cron expression for schedule triggers")
    route: Optional[str] = Field(None, description="API route for webhook triggers")
    platform: Optional[str] = Field(None, description="Platform for adapter triggers")
    channel: Optional[str] = Field(None, description="Channel for adapter triggers")
    mode: Optional[str] = Field(None, description="Mode for adapter triggers")
    context: Optional[Dict[str, Any]] = Field(None, description="Context variables")


class ResourceConfig(BaseModel):
    """Configuration for agents and MCP servers."""

    id: str = Field(..., description="Unique identifier for the resource")
    provider: Optional[str] = Field(
        None, description="Provider (anthropic, openai, perplexity, etc.)"
    )
    model: Optional[str] = Field(None, description="Model name")
    type: Optional[str] = Field(None, description="Resource type (mcp-server, etc.)")
    command: Optional[str] = Field(None, description="Command for MCP servers")
    args: Optional[List[str]] = Field(None, description="Arguments for MCP servers")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    tools: Optional[List[str]] = Field(None, description="List of tool IDs available to the agent")


class WorkflowTask(BaseModel):
    """Configuration for a workflow task."""

    id: Optional[str] = Field(None, description="Task identifier")
    agent: Optional[str] = Field(None, description="Agent ID to execute the task")
    instruction: Optional[str] = Field(None, description="Instruction for the agent")
    type: Optional[str] = Field(None, description="Task type (map, scatter-gather, action)")
    items: Optional[str] = Field(None, description="Items to iterate over for map tasks")
    task: Optional["WorkflowTask"] = Field(None, description="Nested task for map operations")
    parallel_tasks: Optional[List["WorkflowTask"]] = Field(
        None, description="Parallel tasks for scatter-gather"
    )
    inputs: Optional[List[str]] = Field(None, description="Input references")
    action: Optional[str] = Field(None, description="Action name for action tasks")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for action tasks")


class WorkflowConfig(BaseModel):
    """Configuration for the workflow."""

    type: str = Field(..., description="Workflow type (sequential, parallel, etc.)")
    steps: List[WorkflowTask] = Field(..., description="List of workflow steps")


class HolonConfig(BaseModel):
    """Complete Holon configuration schema."""

    version: str = Field(..., description="Configuration version")
    project: str = Field(..., description="Project name")
    trigger: Optional[TriggerConfig] = Field(None, description="Trigger configuration")
    resources: List[ResourceConfig] = Field(..., description="List of resources (agents and tools)")
    workflow: WorkflowConfig = Field(..., description="Workflow definition")


class CLIConfig(BaseModel):
    """CLI global configuration stored in ~/.holon/config.yaml."""

    host: str = Field(default="http://localhost:8000", description="Holon Engine host URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    default_project: Optional[str] = Field(None, description="Default project name")
