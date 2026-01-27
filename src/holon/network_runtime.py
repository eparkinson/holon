"""
Network runtime for orchestrating multiple Holon agents.

This module provides the NetworkRuntime class that coordinates execution
of multiple agents according to a network definition.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from .models import AgentDefinition, AgentMessage, ExecutionMode, NetworkDefinition
from .parser import Parser
from .runtime import Runtime


class NetworkRuntime:
    """Runtime for executing multi-agent networks."""

    def __init__(self, network: NetworkDefinition, base_path: Optional[Path] = None):
        """
        Initialize the network runtime.

        Args:
            network: NetworkDefinition to execute
            base_path: Base path for resolving relative agent paths
        """
        self.network = network
        self.console = Console()
        self.base_path = base_path or Path.cwd()
        self.agents: Dict[str, AgentDefinition] = {}
        self.runtimes: Dict[str, Runtime] = {}
        self.message_queue: List[AgentMessage] = []
        self.agent_outputs: Dict[str, str] = {}

        # Load all agents in the network
        self._load_agents()

    def _load_agents(self):
        """Load all agent definitions specified in the network."""
        for agent_ref in self.network.config.agents:
            # Check if it's a file path or agent ID
            if agent_ref.endswith('.md'):
                # It's a file path
                agent_path = self.base_path / agent_ref
                agent = Parser.parse_file(agent_path)
            else:
                # Assume it's a path relative to base_path
                # Try to find the agent file
                possible_paths = [
                    self.base_path / f"{agent_ref}.md",
                    self.base_path / agent_ref / f"{agent_ref}.md",
                ]
                
                agent = None
                for path in possible_paths:
                    if path.exists():
                        agent = Parser.parse_file(path)
                        break
                
                if agent is None:
                    raise FileNotFoundError(
                        f"Could not find agent definition for '{agent_ref}'. "
                        f"Tried: {', '.join(str(p) for p in possible_paths)}"
                    )
            
            self.agents[agent.config.id] = agent
            self.runtimes[agent.config.id] = Runtime(agent)

    def execute(self, input_data: str) -> Dict[str, Any]:
        """
        Execute the network with the given input.

        Args:
            input_data: Input to the network

        Returns:
            Dict containing network execution results
        """
        mode = self.network.config.execution_mode

        if mode == ExecutionMode.SEQUENTIAL:
            return self._execute_sequential(input_data)
        elif mode == ExecutionMode.PARALLEL:
            return self._execute_parallel(input_data)
        elif mode == ExecutionMode.CONDITIONAL:
            return self._execute_conditional(input_data)
        else:
            raise ValueError(f"Unsupported execution mode: {mode}")

    def _execute_sequential(self, input_data: str) -> Dict[str, Any]:
        """
        Execute agents sequentially based on upstream/downstream relationships.

        Args:
            input_data: Input to the first agent

        Returns:
            Dict with outputs from all agents
        """
        # Build execution order based on upstream/downstream relationships
        execution_order = self._build_execution_order()
        
        current_input = input_data
        
        for agent_id in execution_order:
            agent = self.agents[agent_id]
            runtime = self.runtimes[agent_id]
            
            self.console.print(f"\n[cyan]Executing agent:[/cyan] {agent_id}")
            
            # Execute the agent with current input
            output = self._execute_single_agent(runtime, current_input)
            
            # Store the output
            self.agent_outputs[agent_id] = output
            
            # Pass output to next agent
            current_input = output
        
        return {
            "mode": "sequential",
            "outputs": self.agent_outputs,
            "final_output": current_input
        }

    def _execute_parallel(self, input_data: str) -> Dict[str, Any]:
        """
        Execute all agents in parallel.

        Args:
            input_data: Input to all agents

        Returns:
            Dict with outputs from all agents
        """
        self.console.print(f"\n[cyan]Executing {len(self.agents)} agents in parallel...[/cyan]")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # Submit all agent executions
            futures = {
                executor.submit(
                    self._execute_single_agent,
                    self.runtimes[agent_id],
                    input_data
                ): agent_id
                for agent_id in self.agents.keys()
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                agent_id = futures[future]
                try:
                    output = future.result()
                    self.agent_outputs[agent_id] = output
                    self.console.print(f"[green]✓[/green] {agent_id} completed")
                except Exception as e:
                    self.console.print(f"[red]✗[/red] {agent_id} failed: {e}")
                    self.agent_outputs[agent_id] = f"Error: {e}"
        
        # Synthesize final output (could be customized)
        final_output = self._synthesize_outputs(self.agent_outputs)
        
        return {
            "mode": "parallel",
            "outputs": self.agent_outputs,
            "final_output": final_output
        }

    def _execute_conditional(self, input_data: str) -> Dict[str, Any]:
        """
        Execute agents based on conditional logic.
        
        This is a placeholder for more sophisticated conditional execution.
        Currently defaults to sequential execution.

        Args:
            input_data: Input to the network

        Returns:
            Dict with outputs from executed agents
        """
        # For now, use sequential execution
        # Future: Add support for conditional branching based on agent outputs
        return self._execute_sequential(input_data)

    def _execute_single_agent(self, runtime: Runtime, input_data: str) -> str:
        """
        Execute a single agent and return its output.

        Args:
            runtime: Runtime instance for the agent
            input_data: Input to the agent

        Returns:
            Agent's output
        """
        # Add user message to conversation history
        runtime.conversation_history = [
            {"role": "system", "content": runtime.agent.prompt},
            {"role": "user", "content": input_data}
        ]
        
        # Get response from the agent
        response = runtime._get_llm_response()
        
        return response

    def _build_execution_order(self) -> List[str]:
        """
        Build execution order based on upstream/downstream relationships.
        Uses topological sort to determine the order.

        Returns:
            List of agent IDs in execution order
        """
        # Simple topological sort
        # Start with agents that have no upstream dependencies
        
        in_degree = {agent_id: 0 for agent_id in self.agents.keys()}
        
        # Calculate in-degrees
        for agent_id, agent in self.agents.items():
            if agent.config.downstream:
                for downstream_id in agent.config.downstream:
                    if downstream_id in in_degree:
                        in_degree[downstream_id] += 1
        
        # Find agents with no dependencies
        queue = [agent_id for agent_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            # Process agent with no remaining dependencies
            agent_id = queue.pop(0)
            execution_order.append(agent_id)
            
            # Reduce in-degree for downstream agents
            agent = self.agents[agent_id]
            if agent.config.downstream:
                for downstream_id in agent.config.downstream:
                    if downstream_id in in_degree:
                        in_degree[downstream_id] -= 1
                        if in_degree[downstream_id] == 0:
                            queue.append(downstream_id)
        
        # If not all agents are in execution order, there might be a cycle
        # or disconnected agents - just add remaining agents
        for agent_id in self.agents.keys():
            if agent_id not in execution_order:
                execution_order.append(agent_id)
        
        return execution_order

    def _synthesize_outputs(self, outputs: Dict[str, str]) -> str:
        """
        Synthesize multiple agent outputs into a single output.

        Args:
            outputs: Dict of agent_id -> output

        Returns:
            Synthesized output
        """
        # Simple concatenation with headers
        result = []
        for agent_id, output in outputs.items():
            result.append(f"## {agent_id}\n{output}\n")
        
        return "\n".join(result)

    def run_interactive(self):
        """
        Run the network in interactive mode.
        This allows users to provide input and see the network execute.
        """
        from rich.markdown import Markdown
        from rich.panel import Panel
        
        self.console.print(
            Panel(
                f"[bold cyan]Holon Network: {self.network.config.id}[/bold cyan]\n"
                f"Execution Mode: {self.network.config.execution_mode.value}\n"
                f"Agents: {', '.join(self.agents.keys())}\n"
                f"Type 'exit' or 'quit' to end the session.",
                title="[bold]Welcome to Holon Network[/bold]",
                border_style="cyan",
            )
        )

        while True:
            try:
                # Get user input
                user_input = self.console.input("\n[bold green]Input:[/bold green] ")

                # Check for exit commands
                if user_input.strip().lower() in ["exit", "quit"]:
                    self.console.print("\n[yellow]Goodbye![/yellow]")
                    break

                # Skip empty inputs
                if not user_input.strip():
                    continue

                # Execute the network
                result = self.execute(user_input)

                # Display results
                self.console.print(f"\n[bold blue]Network Output:[/bold blue]")
                self.console.print(Markdown(result["final_output"]))

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")
                # Continue the loop instead of crashing
