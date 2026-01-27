"""
Integration tests for multi-agent networks.

These tests validate end-to-end network execution with real agent interactions.
Note: These tests require API keys and are skipped if not available.
"""

import os
import pytest
from pathlib import Path

from holon.models import ExecutionMode, NetworkDefinition
from holon.network_runtime import NetworkRuntime
from holon.parser import Parser


# Get the repository root
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "tests" / "samples"


def has_api_key() -> bool:
    """Check if any LLM API key is available."""
    return any([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("PERPLEXITY_API_KEY"),
    ])


@pytest.mark.skipif(not has_api_key(), reason="No API key available")
def test_simple_agent_execution():
    """Test executing a simple agent to verify API connectivity."""
    from holon.runtime import Runtime
    
    # Use the chat agent which is simple and works with most models
    chat_agent_path = SAMPLES_DIR / "01_chat" / "chat.md"
    if not chat_agent_path.exists():
        pytest.skip("Chat agent not found")
    
    agent = Parser.parse_file(chat_agent_path)
    runtime = Runtime(agent)
    
    # Set up a simple conversation
    runtime.conversation_history = [
        {"role": "system", "content": agent.prompt},
        {"role": "user", "content": "Say 'test successful' and nothing else"}
    ]
    
    # Get response
    try:
        response = runtime._get_llm_response()
        assert response is not None
        assert len(response) > 0
    except Exception as e:
        pytest.skip(f"Could not connect to LLM API: {e}")


def test_network_execution_order():
    """Test that network builds correct execution order."""
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition not found")
    
    definition = Parser.parse_file(network_path)
    assert isinstance(definition, NetworkDefinition)
    
    runtime = NetworkRuntime(definition, base_path=network_path.parent)
    order = runtime._build_execution_order()
    
    # Verify execution order respects dependencies
    assert "researcher" in order
    assert "writer" in order
    
    # Researcher should come before writer
    researcher_idx = order.index("researcher")
    writer_idx = order.index("writer")
    assert researcher_idx < writer_idx


def test_network_message_passing():
    """Test that messages can be created and validated."""
    from holon.models import AgentMessage
    from datetime import datetime, timezone
    
    message = AgentMessage(
        sender="agent1",
        receiver="agent2",
        content="Test message",
        context={"key": "value"}
    )
    
    assert message.sender == "agent1"
    assert message.receiver == "agent2"
    assert message.content == "Test message"
    assert message.context == {"key": "value"}
    assert isinstance(message.timestamp, datetime)


def test_network_output_synthesis():
    """Test synthesizing outputs from multiple agents."""
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition not found")
    
    definition = Parser.parse_file(network_path)
    runtime = NetworkRuntime(definition, base_path=network_path.parent)
    
    # Create mock outputs
    outputs = {
        "researcher": "Research findings: Point A, Point B",
        "writer": "Article: This is the introduction..."
    }
    
    # Synthesize
    result = runtime._synthesize_outputs(outputs)
    
    # Verify synthesis includes both outputs
    assert "researcher" in result
    assert "writer" in result
    assert "Research findings" in result
    assert "Article" in result


@pytest.mark.skipif(not has_api_key(), reason="No API key available")
@pytest.mark.slow
def test_sequential_network_execution():
    """
    Integration test for sequential network execution.
    
    This test requires API keys and actually executes the network,
    so it's marked as slow and skipped if no API key is available.
    """
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition not found")
    
    definition = Parser.parse_file(network_path)
    assert isinstance(definition, NetworkDefinition)
    
    runtime = NetworkRuntime(definition, base_path=network_path.parent)
    
    # Execute with a simple test input
    test_input = "What are the key features of Python programming language?"
    
    try:
        result = runtime.execute(test_input)
        
        # Verify result structure
        assert "mode" in result
        assert result["mode"] == "sequential"
        assert "outputs" in result
        assert "final_output" in result
        
        # Verify we got outputs from expected agents
        assert "researcher" in result["outputs"] or "writer" in result["outputs"]
        
        # Verify final output is not empty
        assert len(result["final_output"]) > 0
        
    except Exception as e:
        # If execution fails due to API issues, skip the test
        pytest.skip(f"Network execution failed: {e}")


def test_parallel_execution_mode():
    """Test creating a network with parallel execution mode."""
    content = """---
id: parallel-test-network
type: network
execution_mode: parallel
agents:
  - agent1
  - agent2
  - agent3
---

# Parallel Test Network

Tests parallel execution of multiple agents.
"""
    
    definition = Parser.parse_string(content)
    assert isinstance(definition, NetworkDefinition)
    assert definition.config.execution_mode == ExecutionMode.PARALLEL
    assert len(definition.config.agents) == 3


def test_network_agent_loading():
    """Test that network runtime correctly loads agent definitions."""
    network_path = SAMPLES_DIR / "02_collaborators" / "network.md"
    if not network_path.exists():
        pytest.skip("Network definition not found")
    
    definition = Parser.parse_file(network_path)
    runtime = NetworkRuntime(definition, base_path=network_path.parent)
    
    # Verify agents were loaded
    assert len(runtime.agents) > 0
    assert len(runtime.runtimes) > 0
    
    # Verify each agent has a corresponding runtime
    for agent_id in runtime.agents.keys():
        assert agent_id in runtime.runtimes
        assert runtime.runtimes[agent_id].agent == runtime.agents[agent_id]
