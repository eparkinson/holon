"""Main CLI application for Holon."""

import json
from pathlib import Path
from typing import Optional

import httpx
import typer
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from holon_cli import __version__
from holon_cli.config import load_config, set_config_value, get_config_value
from holon_cli.models import HolonConfig

app = typer.Typer(
    name="holon",
    help="Holon CLI - Command-line interface for the Holon Agent Orchestration Engine",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """Display version and exit."""
    if value:
        # Display CLI version
        rprint(f"[bold blue]Holon CLI[/bold blue] version [green]{__version__}[/green]")

        # Try to get engine version from API
        try:
            cli_config = load_config()
            response = httpx.get(
                f"{cli_config.host}/api/v1/version",
                headers=(
                    {"Authorization": f"Bearer {cli_config.api_key}"} if cli_config.api_key else {}
                ),
                timeout=5.0,
            )
            response.raise_for_status()
            engine_version = response.json().get("version", "unknown")
            rprint(f"[bold blue]Holon Engine[/bold blue] version [green]{engine_version}[/green]")
        except (httpx.ConnectError, httpx.HTTPStatusError, httpx.TimeoutException):
            rprint("[dim]Holon Engine[/dim] [yellow](not reachable)[/yellow]")

        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Holon CLI - Orchestrate Higher-Order AI Agents."""
    pass


@app.command()
def init(
    name: str = typer.Option(
        ..., "--name", "-n", prompt="Project name", help="Name of the project"
    ),
    path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Path where to create the project"),
):
    """
    Initialize a new Holon project with a template holon.yaml.

    Creates a basic holon.yaml configuration file and .env.example.
    """
    console.print(f"[bold green]Initializing new Holon project:[/bold green] {name}")

    # Create holon.yaml template
    holon_file = path / "holon.yaml"
    if holon_file.exists():
        if not typer.confirm(f"{holon_file} already exists. Overwrite?"):
            raise typer.Abort()

    template = {
        "version": "1.0",
        "project": name,
        "trigger": {"type": "webhook", "route": "/api/v1/trigger"},
        "resources": [{"id": "assistant", "provider": "anthropic", "model": "claude-3-5-sonnet"}],
        "workflow": {
            "type": "sequential",
            "steps": [
                {
                    "id": "process_request",
                    "agent": "assistant",
                    "instruction": "Process the incoming request: {trigger.input}",
                }
            ],
        },
    }

    with open(holon_file, "w") as f:
        yaml.dump(template, f, default_flow_style=False, sort_keys=False)

    # Create .env.example
    env_file = path / ".env.example"
    with open(env_file, "w") as f:
        f.write("# API Keys for Agent Providers\n")
        f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
        f.write("OPENAI_API_KEY=your_api_key_here\n")
        f.write("PERPLEXITY_API_KEY=your_api_key_here\n")

    console.print(f"[green]✓[/green] Created {holon_file}")
    console.print(f"[green]✓[/green] Created {env_file}")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit holon.yaml to define your workflow")
    console.print("  2. Copy .env.example to .env and add your API keys")
    console.print("  3. Deploy with: [cyan]holon deploy[/cyan]")


@app.command()
def deploy(
    file: Optional[Path] = typer.Option(
        None, "--file", help="Path to holon.yaml configuration file"
    ),
    name: Optional[str] = typer.Option(None, "--name", help="Override project name from YAML"),
    env_file: Optional[Path] = typer.Option(None, "--env", help="Path to .env file for secrets"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate without deploying"),
):
    """
    Deploy a Holon workflow to the engine.

    Validates the holon.yaml configuration and registers it with the Holon Engine.
    By default, deploys holon.yaml from the current directory.
    """
    # Default to holon.yaml in current directory if not specified
    if file is None:
        file = Path.cwd() / "holon.yaml"

    # Check if file exists
    if not file.exists():
        console.print(f"[red]✗ Configuration file not found:[/red] {file}")
        console.print("  Use [cyan]--file[/cyan] to specify a different configuration file")
        raise typer.Exit(code=1)

    console.print(f"[bold]Deploying workflow from:[/bold] {file}")

    # Load and validate YAML
    try:
        with open(file, "r") as f:
            config_data = yaml.safe_load(f)

        # Validate with Pydantic
        config = HolonConfig(**config_data)

        # Override name if provided
        if name:
            config.project = name

        # Load environment variables from .env file
        env_vars = {}
        if env_file:
            if not env_file.exists():
                console.print(f"[yellow]Warning:[/yellow] .env file not found at {env_file}")
            else:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                env_vars[key.strip()] = value.strip()
                console.print(
                    f"[green]✓[/green] Loaded {len(env_vars)} environment variables from {env_file}"
                )
        else:
            # Try to find .env in the same directory as holon.yaml
            default_env = file.parent / ".env"
            if default_env.exists():
                with open(default_env, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                env_vars[key.strip()] = value.strip()
                console.print(
                    f"[green]✓[/green] Loaded {len(env_vars)} environment variables from {default_env}"
                )

        console.print("[green]✓[/green] Configuration validated successfully")
        console.print(f"  Project: [cyan]{config.project}[/cyan]")
        console.print(f"  Resources: {len(config.resources)}")
        console.print(f"  Workflow steps: {len(config.workflow.steps)}")

        if dry_run:
            console.print("[yellow]Dry run - not deploying to engine[/yellow]")
            return

        # Deploy to engine
        cli_config = load_config()

        try:
            # Read the raw YAML content
            with open(file, "r") as f:
                config_yaml = f.read()

            deploy_data = {
                "name": config.project,
                "config_yaml": config_yaml,
            }
            if env_vars:
                deploy_data["env_vars"] = env_vars

            with console.status("[bold blue]Deploying to engine..."):
                response = httpx.post(
                    f"{cli_config.host}/api/v1/deploy",
                    json=deploy_data,
                    headers=(
                        {"Authorization": f"Bearer {cli_config.api_key}"}
                        if cli_config.api_key
                        else {}
                    ),
                    timeout=30.0,
                )
                response.raise_for_status()

            result = response.json()
            console.print("[bold green]✓ Deployment successful![/bold green]")
            console.print(f"  Process ID: [cyan]{result.get('project_id', 'N/A')}[/cyan]")
            console.print(f"  Status: {result.get('status', 'N/A')}")

        except httpx.ConnectError:
            console.print(f"[red]✗ Could not connect to Holon Engine at {cli_config.host}[/red]")
            console.print("  Is the engine running? Check with: [cyan]holon config get host[/cyan]")
        except httpx.HTTPStatusError as e:
            console.print(f"[red]✗ Deployment failed:[/red] {e.response.status_code}")
            console.print(f"  {e.response.text}")

    except ValidationError as e:
        console.print("[red]✗ Configuration validation failed:[/red]")
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            console.print(f"  [red]•[/red] {field}: {error['msg']}")
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        console.print(f"[red]✗ Invalid YAML:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def list(
    show_all: bool = typer.Option(False, "--all", help="Show all processes including stopped"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)"),
):
    """
    List all deployed Holon processes.

    Shows running workflows and their current status.
    """
    cli_config = load_config()

    try:
        with console.status("[bold blue]Fetching processes..."):
            response = httpx.get(
                f"{cli_config.host}/api/v1/processes",
                params={"all": show_all},
                headers=(
                    {"Authorization": f"Bearer {cli_config.api_key}"} if cli_config.api_key else {}
                ),
                timeout=10.0,
            )
            response.raise_for_status()

        processes = response.json()

        if format == "json":
            console.print_json(data=processes)
            return

        # Display as table
        if not processes:
            console.print("[yellow]No processes found[/yellow]")
            return

        table = Table(title="Holon Processes")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Uptime")
        table.add_column("Triggers")

        for process in processes:
            table.add_row(
                process.get("id", "N/A"),
                process.get("name", "N/A"),
                process.get("status", "N/A"),
                process.get("uptime", "N/A"),
                process.get("triggers", "N/A"),
            )

        console.print(table)

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Holon Engine at {cli_config.host}[/red]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Request failed:[/red] {e.response.status_code}")


@app.command()
def logs(
    process_id: str = typer.Argument(..., help="Process ID or name"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Stream logs in real-time"),
    tail: Optional[int] = typer.Option(None, "--tail", help="Show last N lines"),
):
    """
    View logs for a Holon process.

    Display execution history and output from workflow steps.
    """
    cli_config = load_config()

    try:
        params = {}
        if tail:
            params["tail"] = tail

        response = httpx.get(
            f"{cli_config.host}/api/v1/processes/{process_id}/logs",
            params=params,
            headers={"Authorization": f"Bearer {cli_config.api_key}"} if cli_config.api_key else {},
            timeout=30.0,
        )
        response.raise_for_status()

        logs = response.json()

        if follow:
            console.print("[yellow]Note: Streaming mode not yet implemented[/yellow]")

        for log_entry in logs:
            timestamp = log_entry.get("timestamp", "")
            level = log_entry.get("level", "INFO")
            message = log_entry.get("message", "")

            color = {
                "ERROR": "red",
                "WARNING": "yellow",
                "INFO": "blue",
                "DEBUG": "dim",
            }.get(level, "white")

            console.print(f"[dim]{timestamp}[/dim] [{color}]{level}[/{color}] {message}")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Holon Engine at {cli_config.host}[/red]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Request failed:[/red] {e.response.status_code}")
        if e.response.status_code == 404:
            console.print(f"  Process '{process_id}' not found")


@app.command()
def event(
    process: str = typer.Option(..., "--process", "-p", help="Process ID or name"),
    event_name: str = typer.Option(..., "--event", "-e", help="Event name to trigger"),
    data: Optional[str] = typer.Option(None, "--data", help="JSON data payload"),
    file: Optional[Path] = typer.Option(None, "--file", help="JSON file with payload"),
):
    """
    Trigger an event in a running Holon process.

    Manually invoke a workflow step or trigger.
    """
    cli_config = load_config()

    # Prepare payload
    payload = {"event": event_name}

    if data:
        try:
            payload["data"] = json.loads(data)
        except json.JSONDecodeError as e:
            console.print(f"[red]✗ Invalid JSON in --data:[/red] {e}")
            raise typer.Exit(code=1)
    elif file:
        try:
            with open(file, "r") as f:
                payload["data"] = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            console.print(f"[red]✗ Could not read JSON file:[/red] {e}")
            raise typer.Exit(code=1)

    try:
        with console.status(f"[bold blue]Triggering event '{event_name}'..."):
            response = httpx.post(
                f"{cli_config.host}/api/v1/processes/{process}/events",
                json=payload,
                headers=(
                    {"Authorization": f"Bearer {cli_config.api_key}"} if cli_config.api_key else {}
                ),
                timeout=30.0,
            )
            response.raise_for_status()

        result = response.json()
        console.print("[green]✓ Event triggered successfully[/green]")
        console.print(f"  Status: {result.get('status', 'N/A')}")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Holon Engine at {cli_config.host}[/red]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Request failed:[/red] {e.response.status_code}")


@app.command()
def stop(
    process_id: str = typer.Argument(..., help="Process ID to stop"),
):
    """
    Stop a running Holon process.

    Pauses execution but keeps state.
    """
    cli_config = load_config()

    try:
        with console.status(f"[bold blue]Stopping process {process_id}..."):
            response = httpx.post(
                f"{cli_config.host}/api/v1/processes/{process_id}/stop",
                headers=(
                    {"Authorization": f"Bearer {cli_config.api_key}"} if cli_config.api_key else {}
                ),
                timeout=30.0,
            )
            response.raise_for_status()

        console.print(f"[green]✓ Process {process_id} stopped[/green]")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Holon Engine at {cli_config.host}[/red]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Request failed:[/red] {e.response.status_code}")


@app.command()
def delete(
    process_id: str = typer.Argument(..., help="Process ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """
    Delete a Holon process.

    Removes the process and its configuration permanently.
    """
    if not force:
        if not typer.confirm(f"Are you sure you want to delete process '{process_id}'?"):
            raise typer.Abort()

    cli_config = load_config()

    try:
        with console.status(f"[bold blue]Deleting process {process_id}..."):
            response = httpx.delete(
                f"{cli_config.host}/api/v1/processes/{process_id}",
                headers=(
                    {"Authorization": f"Bearer {cli_config.api_key}"} if cli_config.api_key else {}
                ),
                timeout=30.0,
            )
            response.raise_for_status()

        console.print(f"[green]✓ Process {process_id} deleted[/green]")

    except httpx.ConnectError:
        console.print(f"[red]✗ Could not connect to Holon Engine at {cli_config.host}[/red]")
    except httpx.HTTPStatusError as e:
        console.print(f"[red]✗ Request failed:[/red] {e.response.status_code}")


# Config command group
config_app = typer.Typer(help="Manage CLI configuration")
app.add_typer(config_app, name="config")


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Configuration key to retrieve"),
):
    """Get a configuration value."""
    try:
        value = get_config_value(key)
        console.print(f"{key}: [cyan]{value}[/cyan]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(code=1)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set a configuration value."""
    try:
        set_config_value(key, value)
        console.print(f"[green]✓[/green] Set {key} = [cyan]{value}[/cyan]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(code=1)


@config_app.command("show")
def config_show():
    """Show all configuration values."""
    config = load_config()

    table = Table(title="Holon CLI Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config.model_dump(exclude_none=True).items():
        table.add_row(key, str(value))

    console.print(table)


if __name__ == "__main__":
    app()
