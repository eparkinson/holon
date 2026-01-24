"""
Runtime engine for executing Holon agents.
"""

import sys
from typing import Optional

from litellm import completion
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .models import AgentDefinition


class Runtime:
    """Runtime engine for executing Holon agents."""
    
    def __init__(self, agent: AgentDefinition):
        """
        Initialize the runtime with an agent definition.
        
        Args:
            agent: AgentDefinition to execute
        """
        self.agent = agent
        self.console = Console()
        self.conversation_history = []
        
    def run_interactive(self):
        """
        Run an interactive REPL chat session with the agent.
        Continues until the user types 'exit' or 'quit'.
        """
        self.console.print(Panel(
            f"[bold cyan]Holon Agent: {self.agent.config.id}[/bold cyan]\n"
            f"Model: {self.agent.config.model}\n"
            f"Type 'exit' or 'quit' to end the session.",
            title="[bold]Welcome to Holon[/bold]",
            border_style="cyan"
        ))
        
        # Initialize conversation with system prompt
        self.conversation_history = [
            {"role": "system", "content": self.agent.prompt}
        ]
        
        while True:
            try:
                # Get user input
                user_input = self.console.input("\n[bold green]You:[/bold green] ")
                
                # Check for exit commands
                if user_input.strip().lower() in ['exit', 'quit']:
                    self.console.print("\n[yellow]Goodbye![/yellow]")
                    break
                
                # Skip empty inputs
                if not user_input.strip():
                    continue
                
                # Add user message to history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Get response from LLM
                response = self._get_llm_response()
                
                # Display response
                self.console.print(f"\n[bold blue]{self.agent.config.id}:[/bold blue]")
                self.console.print(Markdown(response))
                
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                # Continue the loop instead of crashing
    
    def _get_llm_response(self) -> str:
        """
        Get a response from the LLM using litellm.
        
        Returns:
            The assistant's response text
        """
        try:
            response = completion(
                model=self.agent.config.model,
                messages=self.conversation_history
            )
            return response.choices[0].message.content
        except Exception as e:
            # Provide a more helpful error message
            raise Exception(
                f"Failed to get response from model '{self.agent.config.model}': {e}\n"
                f"Make sure you have the appropriate API key set (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY)"
            )
