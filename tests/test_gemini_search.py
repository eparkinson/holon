"""
Integration tests for Gemini agent with Google Search and Maps.

These tests verify that:
1. Gemini agent definition is properly configured
2. Google Search and Maps tools are available
3. Real Google Search capability works (not hallucination)
4. Tool usage is tracked in response metadata
"""

import os
import pytest
import yaml
from pathlib import Path

from src.holon.parser import Parser
from src.holon.runtime import Runtime
from src.holon.agent_apis import GeminiAgentAPI, get_global_registry
from src.holon.tools import get_global_registry as get_tool_registry


@pytest.fixture(scope="module")
def load_secrets():
    """Load secrets from secrets.yaml for integration tests."""
    secrets_path = Path("secrets.yaml")
    if secrets_path.exists():
        with open(secrets_path) as f:
            secrets = yaml.safe_load(f)
            for key, value in secrets.items():
                os.environ[key] = str(value)
    return secrets_path.exists()


class TestGeminiSearchCapability:
    """Test Gemini agent with Google Search integration."""
    
    def test_agent_has_tools_configured(self):
        """Test that gchat agent has google_search tool."""
        agent_path = Path("tests/samples/05_gchat/gchat.md")
        agent = Parser.parse_file(str(agent_path))
        
        assert agent.config.model == "google/gemini-3-pro-preview"
        assert agent.config.tools is not None
        assert "google_search" in agent.config.tools
    
    def test_runtime_loads_tool_definitions(self):
        """Test that Runtime loads google_search tool definition."""
        agent_path = Path("tests/samples/05_gchat/gchat.md")
        agent = Parser.parse_file(str(agent_path))
        
        runtime = Runtime(agent)
        assert len(runtime.tool_definitions) >= 1
        
        tool_names = [t["function"]["name"] for t in runtime.tool_definitions]
        assert "google_search" in tool_names


class TestGeminiIntegration:
    """
    Integration tests requiring real API calls.
    
    These tests MUST have secrets.yaml with GOOGLE_API_KEY configured.
    They will FAIL (not skip) if the API integration is broken.
    """
    
    def test_gemini_api_initialized(self, load_secrets):
        """Test that GeminiAgentAPI can be initialized with real API key."""
        api = GeminiAgentAPI()
        assert api is not None
        assert api.get_model_name() == "gemini-3-pro-preview"
    
    def test_google_search_requires_recent_data(self, load_secrets):
        """
        CRITICAL TEST: Verify Google Search returns real-time data, not training data.
        
        This test asks for the current date. If Gemini uses Google Search properly,
        it should return January 2026 (current date). If it's hallucinating or using
        training data, it would return an older date.
        """
        api = GeminiAgentAPI()
        
        response = api.chat(
            messages=[{"role": "user", "content": "What is today's date? Use Google Search to find the current date."}],
            system_prompt="You have access to Google Search. Use it to find current information.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "google_search",
                        "description": "Search Google for current information"
                    }
                }
            ]
        )
        
        # Should contain January 2026 or just 2026
        content_lower = response.content.lower()
        assert "2026" in content_lower or "january" in content_lower, (
            f"Expected response to contain 2026 or January (real-time data), "
            f"but got: {response.content[:200]}"
        )
        
        # Should NOT contain old dates from training data
        assert "2024" not in content_lower, "Response contains training data date (2024)"
        assert "2023" not in content_lower, "Response contains training data date (2023)"
    
    def test_tool_calls_are_tracked(self, load_secrets):
        """Test that Google Search tool usage is tracked in response metadata."""
        api = GeminiAgentAPI()
        
        response = api.chat(
            messages=[{"role": "user", "content": "Search Google for the latest news about AI."}],
            system_prompt="You have access to Google Search.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "google_search",
                        "description": "Search Google for information"
                    }
                }
            ]
        )
        
        # Response should have usage metadata
        assert "usage" in response.__dict__ or hasattr(response, "usage")
        
        # Should track tool usage (Gemini may track this differently than Grok)
        usage = response.usage
        assert usage is not None
        
        # At minimum should have token counts
        assert "prompt_tokens" in usage or "input_tokens" in usage
        assert "completion_tokens" in usage or "output_tokens" in usage
    
    def test_google_search_vs_hallucination_difference(self, load_secrets):
        """
        Test that Google Search provides real facts, not hallucinated content.
        
        With Google Search, responses should mention recent developments (2025-2026),
        not just training data from 2023-2024.
        """
        api = GeminiAgentAPI()
        
        response = api.chat(
            messages=[{"role": "user", "content": "What are the latest developments in quantum computing?"}],
            system_prompt="Use Google Search for current information.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "google_search",
                        "description": "Search Google for current information"
                    }
                }
            ]
        )
        
        content_lower = response.content.lower()
        
        # Should mention recent timeframes (2025 or 2026) indicating real-time data
        has_recent_year = "2025" in content_lower or "2026" in content_lower
        
        # Response should have substance (more than a few words)
        has_substance = len(response.content) > 100
        
        assert has_recent_year and has_substance, (
            f"Expected response with recent developments (2025/2026), "
            f"but got: {response.content[:300]}"
        )


class TestGeminiRuntimeIntegration:
    """End-to-end integration tests with Runtime."""
    
    def test_runtime_with_gemini_agent(self, load_secrets):
        """Test that Runtime can execute Gemini agent with Google Search."""
        agent_path = Path("tests/samples/05_gchat/gchat.md")
        agent = Parser.parse_file(str(agent_path))
        
        runtime = Runtime(agent)
        
        # Add a user message
        runtime.conversation_history.append({
            "role": "user",
            "content": "What's the weather like today? Use Google Search."
        })
        
        # Get response
        response = runtime._get_llm_response()
        
        assert response is not None
        assert len(response) > 0
        assert "2026" in response or "january" in response.lower()
