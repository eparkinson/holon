"""
Agent API abstraction layer for integrating direct agent APIs.

This module provides a pluggable interface for integrating AI agents through their
native APIs, enabling agents to retain their built-in capabilities (like Grok's X Search)
rather than relying on generic LLM abstractions.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AgentResponse:
    """Standardized response from an agent API."""
    content: str
    model: str
    usage: Dict[str, Any]
    raw_response: Any


class AgentAPI(ABC):
    """Abstract base class for agent API integrations."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name handled by this API."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        Send a chat request to the agent.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt for the agent
            **kwargs: Additional parameters (tools, temperature, etc)

        Returns:
            AgentResponse with the agent's response
        """
        pass


class GrokAgentAPI(AgentAPI):
    """
    Grok agent API using xAI SDK with agentic tool calling.
    
    This integration uses grok-4-1-fast with server-side tool orchestration,
    enabling real-time access to X Search and Web Search capabilities.
    """

    def __init__(self):
        """Initialize Grok API client using xAI SDK."""
        # Try GROK_API_KEY first, then fall back to XAI_API_KEY
        self.api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROK_API_KEY or XAI_API_KEY environment variable not set"
            )
        self.model = "grok-4-1-fast"
        
        # Import xAI SDK
        try:
            from xai_sdk import Client
            from xai_sdk.tools import web_search, x_search
            
            self.Client = Client
            self.web_search = web_search
            self.x_search = x_search
        except ImportError:
            raise ImportError(
                "xai-sdk is required for Grok integration. "
                "Install with: pip install xai-sdk>=1.3.1"
            )

    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        Send a chat request to Grok with agentic tool calling.
        
        The xAI server orchestrates the tool calling loop autonomously.
        Tools are executed on the server side and results are integrated
        into the final response.

        Args:
            messages: Conversation history
            system_prompt: System instructions for Grok
            **kwargs: Additional parameters (tools, temperature, etc)

        Returns:
            AgentResponse with Grok's response and tool usage info

        Raises:
            Exception: If the API call fails
        """
        try:
            # Initialize client
            client = self.Client(api_key=self.api_key)
            
            # Build tools list
            tools = []
            if "tools" in kwargs and kwargs["tools"]:
                # Support both tool names and tool definitions
                tool_configs = kwargs["tools"]
                for tool_config in tool_configs:
                    # Handle both string names and full definitions
                    if isinstance(tool_config, str):
                        tool_name = tool_config
                    elif isinstance(tool_config, dict) and "function" in tool_config:
                        tool_name = tool_config["function"]["name"]
                    else:
                        continue
                    
                    # Add appropriate tool
                    if tool_name == "x_search":
                        tools.append(self.x_search())
                    elif tool_name == "web_search":
                        tools.append(self.web_search())
            
            # Create chat with tools
            chat = client.chat.create(
                model=self.model,
                tools=tools if tools else [],
                store_messages=False,
            )
            
            # Add system prompt if provided
            if system_prompt:
                from xai_sdk.chat import system
                chat.append(system(system_prompt))
            
            # Add conversation history
            from xai_sdk.chat import user, assistant
            for msg in messages:
                if msg["role"] == "user":
                    chat.append(user(msg["content"]))
                elif msg["role"] == "assistant":
                    chat.append(assistant(msg["content"]))
            
            # Get response with streaming to capture tool calls
            response_content = ""
            tool_calls_made = []
            
            for response, chunk in chat.stream():
                # Accumulate content
                if chunk.content:
                    response_content += chunk.content
                
                # Track tool calls for testing/observability
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    tool_calls_made.extend(chunk.tool_calls)
            
            # Prepare usage stats
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            # Add tool usage info if available
            if hasattr(response, 'server_side_tool_usage'):
                usage["server_side_tool_usage"] = dict(response.server_side_tool_usage)
            if hasattr(response, 'tool_calls') and response.tool_calls:
                usage["tool_calls"] = [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in response.tool_calls
                ]
            
            return AgentResponse(
                content=response_content,
                model=self.model,
                usage=usage,
                raw_response=response,
            )
            
        except Exception as e:
            raise Exception(f"Failed to get response from Grok API: {e}")


class GeminiAgentAPI(AgentAPI):
    """
    Gemini agent API using Google AI SDK with built-in tools.
    
    This integration uses Gemini models with server-side tool execution,
    enabling access to Google Search, Google Maps, Code Execution, and more.
    """

    def __init__(self):
        """Initialize Gemini API client using Google AI SDK."""
        # Try GEMINI_API_KEY first, then fall back to GOOGLE_API_KEY
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set. "
                "Get your key from https://aistudio.google.com/apikey"
            )
        self.model = "gemini-3-pro-preview"
        
        # Import Google AI SDK
        try:
            from google import genai
            self.genai = genai
            self.Client = genai.Client
        except ImportError:
            raise ImportError(
                "google-genai is required for Gemini integration. "
                "Install with: pip install google-genai"
            )

    def get_model_name(self) -> str:
        """Get the model name."""
        return self.model

    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AgentResponse:
        """
        Send a chat request to Gemini with built-in tools.
        
        Google's servers execute tools like Google Search and Maps automatically.
        Results are integrated into the response.

        Args:
            messages: Conversation history
            system_prompt: System instructions for Gemini
            **kwargs: Additional parameters (tools, temperature, etc)

        Returns:
            AgentResponse with Gemini's response and tool usage info

        Raises:
            Exception: If the API call fails
        """
        try:
            # Initialize client
            client = self.Client(api_key=self.api_key)
            
            # Build tools list for Gemini
            tools = []
            if "tools" in kwargs and kwargs["tools"]:
                tool_configs = kwargs["tools"]
                for tool_config in tool_configs:
                    # Handle both string names and full definitions
                    if isinstance(tool_config, str):
                        tool_name = tool_config
                    elif isinstance(tool_config, dict) and "function" in tool_config:
                        tool_name = tool_config["function"]["name"]
                    else:
                        continue
                    
                    # Map tool names to Gemini tools
                    if tool_name == "google_search":
                        tools.append({"google_search": {}})
                    elif tool_name == "google_maps":
                        # Gemini uses google_maps (not google_maps_grounding)
                        tools.append({"google_maps": {}})
                    elif tool_name == "code_execution":
                        tools.append({"code_execution": {}})
            
            # Build request config
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            if tools:
                config["tools"] = tools
            
            # Format messages for Gemini
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Generate content
            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.genai.types.GenerateContentConfig(**config) if config else None
            )
            
            # Extract response text
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    response_text = "".join(
                        part.text for part in candidate.content.parts if hasattr(part, 'text')
                    )
            
            # Build usage stats
            usage = {}
            if hasattr(response, 'usage_metadata'):
                metadata = response.usage_metadata
                usage = {
                    "prompt_tokens": getattr(metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(metadata, 'total_token_count', 0),
                }
            
            # Track grounding metadata if available
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    usage["grounding_metadata"] = True
                    # Gemini includes search queries and grounding support
                    if hasattr(candidate.grounding_metadata, 'search_entry_point'):
                        usage["search_queries_made"] = True
            
            return AgentResponse(
                content=response_text,
                model=self.model,
                usage=usage,
                raw_response=response,
            )
            
        except Exception as e:
            raise Exception(f"Failed to get response from Gemini API: {e}")


class AgentAPIRegistry:
    """Registry for managing multiple agent API integrations."""

    def __init__(self):
        """Initialize an empty registry."""
        self._apis: Dict[str, AgentAPI] = {}

    def register(self, agent_api: AgentAPI) -> None:
        """
        Register an agent API.

        Args:
            agent_api: AgentAPI instance to register
        """
        model_name = agent_api.get_model_name()
        self._apis[model_name] = agent_api

    def get(self, model_name: str) -> Optional[AgentAPI]:
        """
        Get an agent API by model name.

        Args:
            model_name: Name of the model

        Returns:
            AgentAPI instance if found, None otherwise
        """
        return self._apis.get(model_name)

    def get_by_model(self, model_pattern: str) -> Optional[AgentAPI]:
        """
        Get an agent API by model pattern (e.g., "xai/grok-*").

        Args:
            model_pattern: Pattern to match (e.g., "xai/grok-4-1-fast")

        Returns:
            AgentAPI instance if found, None otherwise
        """
        for model_name, api in self._apis.items():
            if model_name == model_pattern:
                return api
        return None

    def list_agents(self) -> List[str]:
        """
        Get list of all registered agent models.

        Returns:
            List of registered model names
        """
        return list(self._apis.keys())


# Global registry
_global_registry = AgentAPIRegistry()


def get_global_registry() -> AgentAPIRegistry:
    """
    Get the global agent API registry.

    Returns:
        Global AgentAPIRegistry instance
    """
    return _global_registry
