"""
Integration tests for X Search capability in xchat agent.

These tests verify that:
1. The agent can access real X Search via the xAI agentic API
2. Tool calls are actually being made (not hallucinated)
3. X search results are being integrated into responses
"""

import pytest
import yaml
from pathlib import Path

from src.holon.parser import Parser
from src.holon.runtime import Runtime
from src.holon.agent_apis import GrokAgentAPI


@pytest.fixture
def api_key():
    """Load API key from secrets if available."""
    secrets_path = Path("secrets.yaml")
    if secrets_path.exists():
        with open(secrets_path) as f:
            secrets = yaml.safe_load(f)
            if "GROK_API_KEY" in secrets or "XAI_API_KEY" in secrets:
                return True
    return False


@pytest.fixture
def xchat_agent():
    """Load the xchat agent definition."""
    agent = Parser.parse_file("tests/samples/04_xchat/xchat.md")
    assert agent.config.model == "xai/grok-4-1-fast"
    assert "x_search" in agent.config.tools
    return agent


class TestGrokXSearchCapability:
    """Tests for real X Search functionality."""

    def test_grok_api_initialized(self, api_key):
        """Test that GrokAgentAPI can be initialized."""
        if not api_key:
            pytest.skip("GROK_API_KEY not available")
        
        grok = GrokAgentAPI()
        assert grok.model == "grok-4-1-fast"
        assert grok.get_model_name() == "grok-4-1-fast"

    def test_agent_has_tools_configured(self, xchat_agent):
        """Test that agent has tools properly configured."""
        assert xchat_agent.config.tools is not None
        assert len(xchat_agent.config.tools) > 0
        assert "x_search" in xchat_agent.config.tools

    def test_runtime_loads_tool_definitions(self, xchat_agent):
        """Test that Runtime properly loads tool definitions."""
        runtime = Runtime(xchat_agent)
        
        # Should have tool definitions from global registry
        assert len(runtime.tool_definitions) > 0
        
        # Should include x_search
        tool_names = [t["function"]["name"] for t in runtime.tool_definitions]
        assert "x_search" in tool_names

    def test_x_search_requires_recent_data(self, api_key, xchat_agent):
        """
        Test that X Search query requires real-time data.
        
        This test asks for something that MUST come from X Search
        (a very recent event that couldn't be in training data).
        """
        if not api_key:
            pytest.skip("GROK_API_KEY not available")
        
        runtime = Runtime(xchat_agent)
        
        # Ask for something that must involve real X data
        # Using a query that would be impossible to answer from training data
        query = (
            "What date is today according to the most recent X posts you can see? "
            "Tell me the exact date from a recent post you can access right now."
        )
        
        runtime.conversation_history = [
            {"role": "user", "content": query}
        ]
        
        response = runtime._get_grok_response()
        
        # Response should mention January 2026 (the actual date)
        # or contain specific recent dates, not October 2024
        assert "January" in response or "2026" in response or \
               "january" in response.lower(), \
               f"Response doesn't show current date, got: {response[:200]}"

    def test_tool_calls_are_tracked(self, api_key, xchat_agent):
        """
        Test that tool calls are actually tracked in the response.
        
        When tools are used, we should see them in usage stats.
        """
        if not api_key:
            pytest.skip("GROK_API_KEY not available")
        
        grok = GrokAgentAPI()
        
        # Request with explicit mention to search
        response = grok.chat(
            messages=[
                {
                    "role": "user",
                    "content": "Search X right now for '#AI' and tell me what you find."
                }
            ],
            system_prompt="You are Grok with access to real-time X search.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "x_search",
                        "description": "Search X for posts"
                    }
                }
            ]
        )
        
        # Check usage includes tool information
        assert "usage" in response.__dict__
        assert response.usage is not None
        
        # Should have tool call info
        # Either server_side_tool_usage or tool_calls
        has_tool_info = (
            "server_side_tool_usage" in response.usage or
            "tool_calls" in response.usage
        )
        
        assert has_tool_info, \
            f"No tool information in response. Usage: {response.usage}"

    def test_x_search_vs_hallucination_difference(self, api_key, xchat_agent):
        """
        Test the difference between real X search and hallucination.
        
        Old model (grok-3) would hallucinate fake post URLs.
        New model (grok-4-1-fast) should return real post URLs from X search.
        """
        if not api_key:
            pytest.skip("GROK_API_KEY not available")
        
        runtime = Runtime(xchat_agent)
        
        query = "Find a real recent post from @elonmusk on X and give me the post URL."
        
        runtime.conversation_history = [
            {"role": "user", "content": query}
        ]
        
        response = runtime._get_grok_response()
        
        # Real X post URLs have the format: https://x.com/username/status/ID
        # Not fake placeholder URLs
        assert "x.com/" in response.lower(), \
            f"No valid X URL found in response: {response[:300]}"
        
        # Should not contain placeholder text
        assert "placeholder" not in response.lower(), \
            f"Response contains placeholder text (hallucination): {response[:300]}"


class TestAgenticToolOrchestration:
    """Tests specific to agentic tool calling orchestration."""

    def test_server_orchestrates_tool_calls(self, api_key):
        """
        Test that the server (xAI) orchestrates tool calls, not the client.
        
        With agentic tool calling, the server makes all decisions about
        which tools to use and how to use them.
        """
        if not api_key:
            pytest.skip("GROK_API_KEY not available")
        
        grok = GrokAgentAPI()
        
        # Make a request with tools enabled
        response = grok.chat(
            messages=[
                {
                    "role": "user",
                    "content": "What is trending on X right now?"
                }
            ],
            system_prompt="Use X search to find current trends.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "x_search",
                        "description": "Search X for trending content"
                    }
                }
            ]
        )
        
        # Server should return a response with tool usage info
        assert response.content, "Response should have content"
        
        # Check that tools were potentially used
        # (response.usage might have server_side_tool_usage dict)
        tool_info = response.usage.get("server_side_tool_usage")
        
        # If tool was used, we should have evidence
        if tool_info and tool_info.get("SERVER_SIDE_TOOL_X_SEARCH"):
            # Tool was used, response should be rich with X data
            assert len(response.content) > 100, \
                "Response with X search should be substantial"


@pytest.mark.skipif(
    not Path("secrets.yaml").exists(),
    reason="Requires API key in secrets.yaml"
)
class TestEndToEndXSearch:
    """End-to-end tests requiring real API credentials."""

    def test_complete_x_search_workflow(self, xchat_agent):
        """
        Complete workflow: Load agent -> Configure tools -> Query -> Verify X search.
        """
        runtime = Runtime(xchat_agent)
        
        # Verify tools are loaded
        assert len(runtime.tool_definitions) > 0
        
        # Ask for something requiring real X data
        runtime.conversation_history = [
            {
                "role": "user",
                "content": (
                    "Search X for recent posts about 'Grok' and 'AI'. "
                    "Show me 2 real posts with their X.com URLs and brief descriptions."
                )
            }
        ]
        
        # Execute
        response = runtime._get_grok_response()
        
        # Verify response
        assert response, "Should get a response"
        assert "x.com" in response.lower(), "Should contain real X URLs"
        assert len(response) > 200, "Response should be substantive"

