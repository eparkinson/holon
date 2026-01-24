#!/usr/bin/env python3
"""
Runtime entrypoint for containerized Holon agents.

This script is copied into the Docker container and serves as the
entry point for running the agent.
"""

import sys
from pathlib import Path

# Import holon modules
from holon.parser import Parser
from holon.runtime import Runtime
from holon.builtin_tools import WebSearchTool
from holon.tools import ToolRegistry


def main():
    """Main entry point for containerized agent execution."""
    # Get agent file path from command line arguments
    if len(sys.argv) < 2:
        print("Error: Agent definition file path required")
        sys.exit(1)
    
    agent_file = sys.argv[1]
    
    # Parse the agent definition
    try:
        agent = Parser.parse_file(agent_file)
        print(f"Loaded agent: {agent.config.id}")
        print(f"Model: {agent.config.model}")
        if agent.config.tools:
            print(f"Tools: {', '.join(agent.config.tools)}")
    except Exception as e:
        print(f"Error loading agent: {e}")
        sys.exit(1)
    
    # Set up tool registry with built-in tools
    tool_registry = ToolRegistry()
    
    # Register built-in tools
    if agent.config.tools:
        if "web_search" in agent.config.tools:
            tool_registry.register(WebSearchTool())
    
    # Create and run the runtime
    runtime = Runtime(agent, tool_registry)
    
    # Determine execution mode based on trigger
    if agent.config.trigger:
        # For now, we only support immediate execution
        # Future: implement cron scheduling, HTTP endpoints, etc.
        print(f"Trigger type: {agent.config.trigger.type}")
        print("Note: Only immediate execution is currently supported")
    
    # Run interactive mode
    print("\nStarting interactive mode...")
    runtime.run_interactive()


if __name__ == "__main__":
    main()
