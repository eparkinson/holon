"""
Runtime engine for executing Holon agents.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from litellm import completion
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .models import AgentDefinition
from .tools import ToolRegistry, get_global_registry
from .agent_apis import GrokAgentAPI


class Runtime:
    """Runtime engine for executing Holon agents."""

    def __init__(self, agent: AgentDefinition, tool_registry: Optional[ToolRegistry] = None):
        """
        Initialize the runtime with an agent definition.

        Args:
            agent: AgentDefinition to execute
            tool_registry: Optional ToolRegistry for agent tools (defaults to global registry)
        """
        self.agent = agent
        self.console = Console()
        self.conversation_history = []
        self.tool_registry = tool_registry or get_global_registry()

        # Pre-compute tool definitions
        self.tool_definitions = []
        if self.agent.config.tools:
            self.tool_definitions = self.tool_registry.get_function_definitions(
                self.agent.config.tools
            )

    def run_interactive(self):
        """
        Run an interactive REPL chat session with the agent.
        Continues until the user types 'exit' or 'quit'.
        """
        self.console.print(
            Panel(
                f"[bold cyan]Holon Agent: {self.agent.config.id}[/bold cyan]\n"
                f"Model: {self.agent.config.model}\n"
                f"Type 'exit' or 'quit' to end the session.",
                title="[bold]Welcome to Holon[/bold]",
                border_style="cyan",
            )
        )

        # Initialize conversation with system prompt
        self.conversation_history = [{"role": "system", "content": self.agent.prompt}]

        while True:
            try:
                # Get user input
                user_input = self.console.input("\n[bold green]You:[/bold green] ")

                # Check for exit commands
                if user_input.strip().lower() in ["exit", "quit"]:
                    self.console.print("\n[yellow]Goodbye![/yellow]")
                    break

                # Skip empty inputs
                if not user_input.strip():
                    continue

                # Add user message to history
                self.conversation_history.append({"role": "user", "content": user_input})

                # Get response from LLM
                response = self._get_llm_response()

                # Display response
                self.console.print(f"\n[bold blue]{self.agent.config.id}:[/bold blue]")
                self.console.print(Markdown(response))

                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": response})

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                # Continue the loop instead of crashing

    def _get_llm_response(self) -> str:
        """
        Get a response from the LLM using native agent APIs when available,
        otherwise fall back to litellm.
        Handles tool calls if the agent has tools configured.

        Returns:
            The assistant's response text
        """
        # Check if we should use a native agent API
        if self.agent.config.model.startswith("xai/grok"):
            return self._get_grok_response()
        elif self.agent.config.model.startswith("google/gemini"):
            return self._get_gemini_response()
        
        # Fall back to litellm for other models
        return self._get_litellm_response()
    
    def _get_grok_response(self) -> str:
        """
        Get a response from Grok using the native xAI API with agentic tool calling.
        
        Uses grok-4-1-fast with the xAI SDK for server-side tool orchestration.
        The agent autonomously decides which tools to use (x_search, web_search, etc).
        
        Returns:
            The assistant's response text
        """
        try:
            grok = GrokAgentAPI()
            
            # Build kwargs with tools if the agent has them configured
            kwargs = {}
            if self.tool_definitions:
                kwargs["tools"] = self.tool_definitions
            
            # Get response with tool calling
            response = grok.chat(
                messages=self.conversation_history,
                system_prompt=self.agent.prompt,
                **kwargs
            )
            
            # Log tool usage if available
            if "server_side_tool_usage" in response.usage:
                import sys
                tool_usage = response.usage.get("server_side_tool_usage", {})
                if tool_usage:
                    print(f"[DEBUG] Grok used tools: {tool_usage}", file=sys.stderr)
            
            return response.content
        except Exception as e:
            raise Exception(
                f"Failed to get response from Grok: {e}\n"
                f"Make sure GROK_API_KEY or XAI_API_KEY is set in your environment"
            )
    
    def _get_gemini_response(self) -> str:
        """
        Get a response from Gemini using the native Google AI API with built-in tools.
        
        Uses Gemini 3 Pro with server-side tool execution for Google Search,
        Google Maps, Code Execution, and more.
        
        Returns:
            The assistant's response text
        """
        try:
            from .agent_apis import GeminiAgentAPI
            gemini = GeminiAgentAPI()
            
            # Build kwargs with tools if the agent has them configured
            kwargs = {}
            if self.tool_definitions:
                kwargs["tools"] = self.tool_definitions
            
            # Get response with tool calling
            response = gemini.chat(
                messages=self.conversation_history,
                system_prompt=self.agent.prompt,
                **kwargs
            )
            
            # Log tool usage if available
            if "grounding_metadata" in response.usage:
                import sys
                print(f"[DEBUG] Gemini used grounding/tools", file=sys.stderr)
                if "search_queries_made" in response.usage:
                    print(f"[DEBUG] Google Search queries were made", file=sys.stderr)
            
            return response.content
        except Exception as e:
            raise Exception(
                f"Failed to get response from Gemini: {e}\n"
                f"Make sure GOOGLE_API_KEY or GEMINI_API_KEY is set in your environment. "
                f"Get your key from https://aistudio.google.com/apikey"
            )
    
    def _get_litellm_response(self) -> str:
        """
        Get a response from the LLM using litellm.
        Handles tool calls if the agent has tools configured.

        Returns:
            The assistant's response text
        """
        try:
            # Prepare completion parameters
            completion_params = {
                "model": self.agent.config.model,
                "messages": self.conversation_history,
            }

            # Add tools if agent has them configured
            if self.tool_definitions:
                completion_params["tools"] = self.tool_definitions

            response = completion(**completion_params)
            message = response.choices[0].message

            # Handle tool calls if present
            if hasattr(message, "tool_calls") and message.tool_calls:
                # Convert tool_calls to a serializable format
                tool_calls_dict = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ]

                # Add the assistant's response with tool calls to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": tool_calls_dict
                })
                
                # Helper function for executing a single tool
                def execute_single_tool(tool_call):
                    function_name = tool_call.function.name
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        result = self.tool_registry.execute(function_name, **function_args)
                        tool_response = str(result)
                    except Exception as e:
                        tool_response = f"Error executing tool: {e}"
                    
                    return {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_response
                    }

                # Execute tool calls in parallel
                with ThreadPoolExecutor() as executor:
                    # Use map to preserve the order of tool calls in the results
                    results = executor.map(execute_single_tool, message.tool_calls)

                    # Add all tool responses to conversation history
                    for result in results:
                        self.conversation_history.append(result)
                
                # Get final response after tool execution
                return self._get_llm_response()

            content = message.content

            # Handle None content (can happen with some models/settings)
            if content is None:
                return "(No response content received from model)"

            return content
        except Exception as e:
            # Provide a more helpful error message
            raise Exception(
                f"Failed to get response from model '{self.agent.config.model}': {e}\n"
                f"Make sure you have the appropriate API key set (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY)"
            )
