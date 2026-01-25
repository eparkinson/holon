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
from .tools import ToolRegistry


class Runtime:
    """Runtime engine for executing Holon agents."""

    def __init__(self, agent: AgentDefinition, tool_registry: Optional[ToolRegistry] = None):
        """
        Initialize the runtime with an agent definition.

        Args:
            agent: AgentDefinition to execute
            tool_registry: Optional ToolRegistry for agent tools
        """
        self.agent = agent
        self.console = Console()
        self.conversation_history = []
        self.tool_registry = tool_registry or ToolRegistry()

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
