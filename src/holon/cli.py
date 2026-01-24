"""
Holon CLI - Command-line interface for the Holon agent orchestration engine.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .deployer import Deployer
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
        help="Path to agent markdown file or directory. If not provided, looks for agent definition in current directory.",
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
            console.print(
                "Please specify a file path or run from a directory containing an agent definition."
            )
            raise typer.Exit(code=1)
        elif len(md_files) == 1:
            file_path = str(md_files[0])
            console.print(f"[cyan]Using:[/cyan] {file_path}")
        else:
            console.print(
                "[red]Error:[/red] Multiple markdown files found. Please specify which one to use:"
            )
            for f in md_files:
                console.print(f"  - {f}")
            raise typer.Exit(code=1)
    else:
        # Check if the provided path is a directory
        path_obj = Path(file_path)
        if path_obj.is_dir():
            # Look for .md files in the specified directory
            md_files = list(path_obj.glob("*.md"))
            if not md_files:
                console.print(
                    f"[red]Error:[/red] No markdown files found in directory: {file_path}"
                )
                raise typer.Exit(code=1)
            elif len(md_files) == 1:
                file_path = str(md_files[0])
                console.print(f"[cyan]Using:[/cyan] {file_path}")
            else:
                console.print(
                    "[red]Error:[/red] Multiple markdown files found. Please specify which one to use:"
                )
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
def deploy(file_path: str = typer.Argument(..., help="Path to agent markdown file to deploy")):
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

    # Check if Docker is available
    import shutil
    if not shutil.which("docker"):
        console.print("\n[red]Error:[/red] Docker is not installed or not in PATH.")
        console.print("Please install Docker to use the deploy command.")
        console.print("For now, you can use 'holon test' to run agents locally.")
        raise typer.Exit(code=1)

    # Deploy the agent
    try:
        console.print("\n[cyan]Building Docker image...[/cyan]")
        deployer = Deployer(agent, Path(file_path))
        deployer.deploy(interactive=True)
    except Exception as e:
        console.print(f"\n[red]Deployment failed:[/red] {e}")
        raise typer.Exit(code=1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
