"""Tests for Holon configuration models."""

import pytest
from pydantic import ValidationError

from holon_cli.models import (
    HolonConfig,
    ResourceConfig,
    WorkflowConfig,
    WorkflowTask,
    TriggerConfig,
    CLIConfig,
)


def test_minimal_holon_config():
    """Test minimal valid Holon configuration."""
    config = HolonConfig(
        version="1.0",
        project="test-project",
        resources=[ResourceConfig(id="agent1", provider="anthropic", model="claude-3-5-sonnet")],
        workflow=WorkflowConfig(
            type="sequential",
            steps=[WorkflowTask(id="step1", agent="agent1", instruction="Do something")],
        ),
    )

    assert config.version == "1.0"
    assert config.project == "test-project"
    assert len(config.resources) == 1
    assert len(config.workflow.steps) == 1


def test_complex_holon_config():
    """Test more complex Holon configuration with multiple resources and steps."""
    config = HolonConfig(
        version="1.0",
        project="complex-project",
        trigger=TriggerConfig(type="schedule", cron="0 7 * * *"),
        resources=[
            ResourceConfig(id="researcher", provider="perplexity", model="sonar-reasoning"),
            ResourceConfig(
                id="analyst", provider="anthropic", model="claude-3-5-sonnet", tools=["mcp_server"]
            ),
            ResourceConfig(
                id="mcp_server",
                type="mcp-server",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"],
            ),
        ],
        workflow=WorkflowConfig(
            type="sequential",
            steps=[
                WorkflowTask(id="research", agent="researcher", instruction="Research topic"),
                WorkflowTask(
                    id="analyze",
                    agent="analyst",
                    instruction="Analyze results",
                    inputs=["research.output"],
                ),
            ],
        ),
    )

    assert len(config.resources) == 3
    assert config.trigger.type == "schedule"
    assert config.trigger.cron == "0 7 * * *"


def test_resource_validation():
    """Test resource configuration validation."""
    # Valid agent resource
    resource = ResourceConfig(id="agent1", provider="anthropic", model="claude-3-5-sonnet")
    assert resource.id == "agent1"

    # Valid MCP server resource
    mcp = ResourceConfig(id="mcp1", type="mcp-server", command="npx", args=["server"])
    assert mcp.type == "mcp-server"


def test_workflow_task_validation():
    """Test workflow task validation."""
    # Simple task
    task = WorkflowTask(id="task1", agent="agent1", instruction="Do something")
    assert task.id == "task1"

    # Task with type
    map_task = WorkflowTask(
        id="map1",
        type="map",
        items="${items}",
        task=WorkflowTask(
            id="nested_task", agent="agent1", instruction="Process {item}"  # Add ID for consistency
        ),
    )
    assert map_task.type == "map"
    assert map_task.task is not None


def test_holon_config_missing_required_fields():
    """Test that missing required fields raise validation errors."""
    with pytest.raises(ValidationError):
        HolonConfig(
            version="1.0"
            # Missing project, resources, workflow
        )


def test_cli_config_defaults():
    """Test CLI configuration defaults."""
    config = CLIConfig()
    assert config.host == "http://localhost:8000"
    assert config.api_key is None
    assert config.default_project is None


def test_cli_config_custom():
    """Test CLI configuration with custom values."""
    config = CLIConfig(
        host="https://api.holon.ai", api_key="sk_test_123", default_project="my-project"
    )
    assert config.host == "https://api.holon.ai"
    assert config.api_key == "sk_test_123"
    assert config.default_project == "my-project"


def test_trigger_config_types():
    """Test different trigger configuration types."""
    # Schedule trigger
    schedule = TriggerConfig(type="schedule", cron="0 * * * *")
    assert schedule.type == "schedule"

    # Webhook trigger
    webhook = TriggerConfig(type="webhook", route="/api/trigger")
    assert webhook.type == "webhook"

    # Adapter trigger
    adapter = TriggerConfig(type="adapter", platform="slack", channel="#general", mode="mention")
    assert adapter.platform == "slack"
