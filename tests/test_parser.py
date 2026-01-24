"""
Tests for the Parser module.
"""

import pytest
from pathlib import Path

from holon.parser import Parser
from holon.models import AgentConfig, AgentDefinition


def test_parse_echo_agent():
    """Test parsing the echo agent sample."""
    agent = Parser.parse_file("test/samples/01_echo/echo.md")
    
    assert agent.config.id == "echo"
    assert agent.config.type == "agent"
    assert agent.config.model == "gpt-4o-mini"
    assert "Echo Bot" in agent.prompt
    assert agent.source_file is not None


def test_parse_researcher_agent():
    """Test parsing the researcher agent with tools."""
    agent = Parser.parse_file("test/samples/02_collaborators/researcher.md")
    
    assert agent.config.id == "researcher"
    assert agent.config.model == "perplexity-sonar-reasoning"
    assert agent.config.tools == ["web_search"]
    assert "Research Assistant" in agent.prompt


def test_parse_manager_agent():
    """Test parsing the manager agent."""
    agent = Parser.parse_file("test/samples/03_complex_network/manager.md")
    
    assert agent.config.id == "manager"
    assert agent.config.model == "o1-preview"
    assert "Engineering Manager" in agent.prompt


def test_parse_string():
    """Test parsing from string content."""
    content = """---
id: test-agent
type: agent
model: gpt-4o
---

# Test Agent

This is a test agent.
"""
    
    agent = Parser.parse_string(content)
    
    assert agent.config.id == "test-agent"
    assert agent.config.model == "gpt-4o"
    assert "Test Agent" in agent.prompt


def test_parse_missing_file():
    """Test that parsing a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        Parser.parse_file("nonexistent.md")


def test_parse_invalid_frontmatter():
    """Test that invalid frontmatter raises ValueError."""
    content = """---
type: agent
---

# Test Agent

Missing required 'id' and 'model' fields.
"""
    
    with pytest.raises(ValueError):
        Parser.parse_string(content)


def test_parse_empty_prompt():
    """Test that empty prompt body raises ValueError."""
    content = """---
id: test-agent
type: agent
model: gpt-4o
---

"""
    
    with pytest.raises(ValueError):
        Parser.parse_string(content)
