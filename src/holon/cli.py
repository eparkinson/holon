"""
Holon CLI - Command-line interface for the Holon agent orchestration engine.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__

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
    ),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        help="Path to YAML file containing environment variables (e.g., API keys). Values from this file take precedence over environment variables.",
    ),
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

    # Defer imports to improve startup time
    from .env_utils import apply_env_overrides, load_env_from_yaml, validate_api_key
    from .models import AgentDefinition, NetworkDefinition
    from .parser import Parser
    from .runtime import Runtime

    # Load environment variables from file if provided
    env_overrides = {}
    if env:
        try:
            env_overrides = load_env_from_yaml(env)
            console.print(f"[cyan]Loaded environment variables from:[/cyan] {env}")
            # Apply the overrides to the environment
            apply_env_overrides(env_overrides)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=1)

    # Parse the definition (agent or network)
    try:
        definition = Parser.parse_file(file_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    # Check if it's a network or agent
    if isinstance(definition, NetworkDefinition):
        # Run as network
        from .network_runtime import NetworkRuntime
        
        console.print(f"[cyan]Running network:[/cyan] {definition.config.id}")
        network_runtime = NetworkRuntime(definition, base_path=Path(file_path).parent)
        network_runtime.run_interactive()
    else:
        # Run as agent
        # Validate that required API keys are available
        error_message = validate_api_key(definition.config.model, env_overrides)
        if error_message:
            console.print(f"[red]Error:[/red] {error_message}")
            raise typer.Exit(code=1)

        # Run the interactive runtime
        runtime = Runtime(definition)
        runtime.run_interactive()


@app.command()
def deploy(file_path: str = typer.Argument(..., help="Path to agent markdown file to deploy")):
    """
    Deploy an agent by building a Docker container.

    This command compiles the agent definition and creates a containerized
    deployment that can run anywhere.
    """
    console.print(f"[yellow]Deploying agent from:[/yellow] {file_path}")

    # Defer imports to improve startup time
    from .deployer import Deployer
    from .parser import Parser

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


@app.command()
def serve(
    definitions_path: Optional[str] = typer.Argument(
        None,
        help="Path to directory containing agent/network definitions. Defaults to current directory.",
    ),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        help="Host to bind the server to"
    ),
    port: int = typer.Option(
        8000,
        "--port",
        help="Port to bind the server to"
    ),
):
    """
    Start an HTTP API server for agents and networks.

    This command starts a production-ready FastAPI server that exposes
    REST endpoints for interacting with agents and networks.
    """
    # Check if FastAPI and uvicorn are available
    try:
        import fastapi
        import uvicorn
    except ImportError:
        console.print("[red]Error:[/red] FastAPI and uvicorn are required for the serve command.")
        console.print("Install with: pip install 'holon[server]' or pip install fastapi uvicorn")
        raise typer.Exit(code=1)

    # Defer imports
    from .server import create_server

    # Determine the path to use
    path = definitions_path or "."
    
    console.print(f"[cyan]Starting Holon server...[/cyan]")
    console.print(f"[cyan]Loading definitions from:[/cyan] {path}")
    console.print(f"[cyan]Server will be available at:[/cyan] http://{host}:{port}")
    console.print(f"[cyan]API docs available at:[/cyan] http://{host}:{port}/docs")
    
    # Create and run server
    try:
        server = create_server(path)
        server.run(host=host, port=port)
    except Exception as e:
        console.print(f"\n[red]Server failed to start:[/red] {e}")
        raise typer.Exit(code=1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
