"""
Holon CLI - Command-line interface for the Holon agent orchestration engine.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .parser import Parser
from .runtime import Runtime

app = typer.Typer(
    name="holon",
    help="Holon: An agent orchestration engine for higher-order AI agents",
    add_completion=False,
)

console = Console()


@app.command()
def version():
    """Show the version of Holon."""
    console.print(f"Holon version {__version__}")


@app.command()
def test(
    file_path: Optional[str] = typer.Argument(
        None,
        help="Path to agent markdown file. If not provided, looks for agent definition in current directory."
    )
):
    """
    Test an agent by running it in an interactive chat interface.
    
    This command compiles the markdown file and launches a local REPL
    where you can chat with the agent. No Docker required.
    """
    # Determine the file to use
    if file_path is None:
        # Look for .md files in current directory
        md_files = list(Path.cwd().glob("*.md"))
        if not md_files:
            console.print("[red]Error:[/red] No markdown files found in current directory.")
            console.print("Please specify a file path or run from a directory containing an agent definition.")
            raise typer.Exit(code=1)
        elif len(md_files) == 1:
            file_path = str(md_files[0])
            console.print(f"[cyan]Using:[/cyan] {file_path}")
        else:
            console.print("[red]Error:[/red] Multiple markdown files found. Please specify which one to use:")
            for f in md_files:
                console.print(f"  - {f}")
            raise typer.Exit(code=1)
    
    # Parse the agent definition
    try:
        agent = Parser.parse_file(file_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    
    # Run the interactive runtime
    runtime = Runtime(agent)
    runtime.run_interactive()


@app.command()
def deploy(
    file_path: str = typer.Argument(
        ...,
        help="Path to agent markdown file to deploy"
    )
):
    """
    Deploy an agent by building a Docker container.
    
    This command compiles the agent definition and creates a containerized
    deployment that can run anywhere.
    """
    console.print(f"[yellow]Deploying agent from:[/yellow] {file_path}")
    
    # Parse the agent definition to validate it
    try:
        agent = Parser.parse_file(file_path)
        console.print(f"[green]✓[/green] Parsed agent: {agent.config.id}")
        console.print(f"[green]✓[/green] Model: {agent.config.model}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    
    # Placeholder for actual deployment logic (Phase 3)
    console.print("\n[yellow]Note:[/yellow] Docker deployment is planned for Phase 3.")
    console.print("For now, use 'holon test' to run agents locally.")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
