"""
Pydantic models for agent configuration validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TriggerConfig(BaseModel):
    """Configuration for agent triggers."""
    type: str = Field(..., description="Type of trigger (schedule, http, cli)")
    cron: Optional[str] = Field(None, description="Cron expression for scheduled triggers")


class AgentConfig(BaseModel):
    """Configuration parsed from agent markdown frontmatter."""
    model_config = ConfigDict(extra="allow")  # Allow extra fields for future extensibility
    
    id: str = Field(..., description="Unique identifier for the agent")
    type: str = Field(default="agent", description="Type of holon (agent, network)")
    model: str = Field(..., description="LLM model to use (e.g., gpt-4o-mini, claude-3-5-sonnet)")
    trigger: Optional[TriggerConfig] = Field(None, description="Trigger configuration")
    tools: Optional[List[str]] = Field(default=None, description="List of tools available to the agent")
    upstream: Optional[List[str]] = Field(default=None, description="List of upstream agent IDs")
    downstream: Optional[List[str]] = Field(default=None, description="List of downstream agent IDs")


class AgentDefinition(BaseModel):
    """Complete agent definition including config and prompt."""
    config: AgentConfig = Field(..., description="Agent configuration from frontmatter")
    prompt: str = Field(..., description="System prompt from markdown body")
    source_file: Optional[str] = Field(None, description="Path to source markdown file")


class AgentMessage(BaseModel):
    """Message passed between agents in a network."""
    sender: str = Field(..., description="ID of the sending agent")
    receiver: str = Field(..., description="ID of the receiving agent")
    content: str = Field(..., description="Message content")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )


class ExecutionMode(str, Enum):
    """Execution mode for multi-agent networks."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class NetworkConfig(BaseModel):
    """Configuration for network-type agent definitions."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(..., description="Unique identifier for the network")
    type: str = Field(default="network", description="Must be 'network'")
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.SEQUENTIAL,
        description="How agents in the network should execute"
    )
    agents: List[str] = Field(
        ..., description="List of agent IDs or paths to agent definitions in the network"
    )
    input_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="Map network inputs to specific agent inputs"
    )
    output_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="Map agent outputs to network outputs"
    )


class NetworkDefinition(BaseModel):
    """Complete network definition including config and description."""
    config: NetworkConfig = Field(..., description="Network configuration from frontmatter")
    description: str = Field(..., description="Network description from markdown body")
    source_file: Optional[str] = Field(None, description="Path to source markdown file")
