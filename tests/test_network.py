"""
Tests for network runtime and multi-agent orchestration.
"""

import pytest
from pathlib import Path

from holon.models import ExecutionMode, NetworkDefinition
from holon.network_runtime import NetworkRuntime
from holon.parser import Parser


# Get the repository root (two levels up from this file)
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "tests" / "samples"


def test_parse_network_definition():
    """Test parsing a network definition."""
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition file not found")
    
    definition = Parser.parse_file(network_path)
    
    assert isinstance(definition, NetworkDefinition)
    assert definition.config.id == "research-writer-network"
    assert definition.config.type == "network"
    assert definition.config.execution_mode == ExecutionMode.SEQUENTIAL
    assert len(definition.config.agents) == 2
    assert "researcher" in definition.config.agents
    assert "writer" in definition.config.agents


def test_network_runtime_initialization():
    """Test NetworkRuntime initialization."""
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition file not found")
    
    definition = Parser.parse_file(network_path)
    assert isinstance(definition, NetworkDefinition)
    
    # Initialize network runtime
    runtime = NetworkRuntime(definition, base_path=network_path.parent)
    
    # Check that agents were loaded
    assert len(runtime.agents) == 2
    assert "researcher" in runtime.agents
    assert "writer" in runtime.agents
    
    # Check that runtimes were created
    assert len(runtime.runtimes) == 2
    assert "researcher" in runtime.runtimes
    assert "writer" in runtime.runtimes


def test_execution_order_building():
    """Test building execution order from upstream/downstream relationships."""
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition file not found")
    
    definition = Parser.parse_file(network_path)
    assert isinstance(definition, NetworkDefinition)
    
    runtime = NetworkRuntime(definition, base_path=network_path.parent)
    
    # Build execution order
    order = runtime._build_execution_order()
    
    # Check that we have the right number of agents
    assert len(order) == 2
    
    # Researcher should come before writer based on downstream relationship
    researcher_idx = order.index("researcher")
    writer_idx = order.index("writer")
    assert researcher_idx < writer_idx


def test_network_string_parsing():
    """Test parsing a network from string content."""
    content = """---
id: test-network
type: network
execution_mode: parallel
agents:
  - agent1
  - agent2
---

# Test Network

A simple test network for validation.
"""
    
    definition = Parser.parse_string(content)
    
    assert isinstance(definition, NetworkDefinition)
    assert definition.config.id == "test-network"
    assert definition.config.execution_mode == ExecutionMode.PARALLEL
    assert len(definition.config.agents) == 2
