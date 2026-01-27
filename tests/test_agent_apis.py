"""Tests for agent API abstraction layer with xAI SDK."""

import pytest
from holon.agent_apis import (
    AgentAPI,
    AgentResponse,
    GrokAgentAPI,
    AgentAPIRegistry,
    get_global_registry,
)


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_create_response(self):
        """Test creating an agent response."""
        response = AgentResponse(
            content="Hello",
            model="test-model",
            usage={"tokens": 10},
            raw_response=None,
        )
        assert response.content == "Hello"
        assert response.model == "test-model"
        assert response.usage == {"tokens": 10}

    def test_response_with_full_data(self):
        """Test response with all data."""
        usage = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }
        response = AgentResponse(
            content="Hello world",
            model="grok-4-1-fast",
            usage=usage,
            raw_response={"id": "test"},
        )
        assert response.usage["prompt_tokens"] == 100
        assert response.model == "grok-4-1-fast"


class TestAgentAPIRegistry:
    """Tests for agent API registry."""

    def test_create_registry(self):
        """Test creating a registry."""
        registry = AgentAPIRegistry()
        assert len(registry.list_agents()) == 0

    def test_registry_list_agents(self):
        """Test listing registered agents."""
        registry = AgentAPIRegistry()
        assert isinstance(registry.list_agents(), list)


class TestGrokAgentAPI:
    """Tests for Grok agent API."""

    def test_grok_api_model_name(self):
        """Test that Grok API has correct model name."""
        import os
        # Skip if no API key
        api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
        if not api_key:
            pytest.skip("No API key available")
        
        grok = GrokAgentAPI()
        assert grok.get_model_name() == "grok-4-1-fast"

    def test_grok_api_model_property(self):
        """Test Grok model property."""
        import os
        api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
        if not api_key:
            pytest.skip("No API key available")
        
        grok = GrokAgentAPI()
        assert grok.model == "grok-4-1-fast"


class TestGlobalRegistry:
    """Tests for global registry instance."""

    def test_get_global_registry(self):
        """Test getting the global registry."""
        registry = get_global_registry()
        assert isinstance(registry, AgentAPIRegistry)

    def test_registry_is_singleton(self):
        """Test that registry is the same instance."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        assert registry1 is registry2
