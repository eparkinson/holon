# Holon CLI

The Holon CLI is a command-line interface for the Holon Agent Orchestration Engine. It provides a developer-friendly way to create, deploy, and manage agentic workflows.

## Installation

### From Source (Development)

```bash
cd cli
pip install -e ".[dev]"
```

This installs the CLI in editable mode with development dependencies.

### Verify Installation

```bash
holon --version
```

## Quick Start

### 1. Initialize a New Project

```bash
holon init --name my-agent-project
```

This creates:
- `holon.yaml` - Your workflow configuration
- `.env.example` - Template for API keys

### 2. Configure Your Agents

Edit `holon.yaml` to define your workflow:

```yaml
version: "1.0"
project: "my-agent-project"

resources:
  - id: assistant
    provider: anthropic
    model: claude-3-5-sonnet

workflow:
  type: sequential
  steps:
    - id: process_request
      agent: assistant
      instruction: "Process the incoming request: {trigger.input}"
```

### 3. Set Up API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 4. Deploy Your Workflow

```bash
# Validate configuration without deploying (from current directory)
holon deploy --dry-run

# Deploy to the engine (uses holon.yaml in current directory)
holon deploy

# Deploy a specific file
holon deploy --file samples/news/holon.yaml
```

## Commands

### `holon init`

Initialize a new Holon project with a template configuration.

```bash
holon init --name my-project
```

Options:
- `--name, -n`: Project name (required)
- `--path, -p`: Path where to create the project (default: current directory)

### `holon deploy`

Deploy a workflow to the Holon Engine. By default, deploys `holon.yaml` from the current directory.

```bash
# Deploy holon.yaml from current directory
holon deploy

# Deploy a specific file
holon deploy --file samples/news/holon.yaml
```

Options:
- `--file`: Path to holon.yaml configuration file (default: ./holon.yaml)
- `--name`: Override project name from YAML
- `--env`: Path to .env file for secrets (default: .env in same directory as holon.yaml)
- `--dry-run`: Validate without deploying

### `holon list`

List all deployed processes.

```bash
holon list
```

Options:
- `--all`: Show all processes including stopped
- `--format`: Output format (table, json)

### `holon logs`

View logs for a process.

```bash
holon logs <process-id>
```

Options:
- `--follow, -f`: Stream logs in real-time
- `--tail`: Show last N lines

### `holon event`

Trigger an event in a running process.

```bash
holon event --process my-process --event trigger_name
```

Options:
- `--process, -p`: Process ID or name
- `--event, -e`: Event name to trigger
- `--data`: JSON data payload
- `--file`: JSON file with payload

### `holon stop`

Stop a running process.

```bash
holon stop <process-id>
```

### `holon delete`

Delete a process permanently.

```bash
holon delete <process-id>
```

Options:
- `--force, -f`: Skip confirmation

### `holon config`

Manage CLI configuration.

```bash
# Show all configuration
holon config show

# Get a value
holon config get host

# Set a value
holon config set host http://localhost:8000
holon config set api_key sk_...
```

## Configuration

The CLI stores its configuration in `~/.holon/config.yaml`.

Available settings:
- `host`: Holon Engine URL (default: `http://localhost:8000`)
- `api_key`: API key for authentication
- `default_project`: Default project name

## Development

### Run Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=holon_cli
```

### Format Code

```bash
black src/ tests/
```

### Lint Code

```bash
ruff check src/ tests/
```

## Architecture

The CLI is a thin client that:
1. Validates `holon.yaml` configurations locally using Pydantic
2. Communicates with the Holon Engine via REST API
3. Provides rich terminal output using Rich library

It does not execute agent logic locally - all orchestration happens in the Engine.

## Examples

See the [samples](../samples) directory for example configurations:
- `samples/news/holon.yaml` - Daily news briefing workflow
- `samples/assistant/holon.yaml` - Personal chief of staff

## License

MIT
