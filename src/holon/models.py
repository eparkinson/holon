"""
Pydantic models for agent configuration validation.
"""

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
