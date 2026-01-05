# Holon CLI Specification

The Holon CLI (`holon`) is the primary interface for developers to interact with the Holon Service. It allows users to deploy workflows, manage running processes, trigger events, and interact with agents directly.

## 1. Overview

The CLI acts as a client to the Holon Control Plane (Service). It communicates via REST/gRPC to manage the lifecycle of Holon Agents and Workflows.

**Usage Syntax:**
```bash
holon <command> [subcommand] [flags]
```

---

## 2. Core Commands

### 2.1 Deploy
Deploys a HolonDSL configuration file (`.yaml`) to the backend service. This registers the workflow, initializes the agents, and sets up any defined triggers (cron, webhooks, etc.).

**Syntax:**
```bash
holon deploy [flags]
```

**Flags:**
- `--file <path>`: Path to the HolonDSL configuration file (default: `holon.yaml`).
- `--name <string>`: Override the project name defined in the YAML.
- `--env <path>`: Path to a `.env` file for secrets (default: `.env`).
- `--dry-run`: Validate the YAML syntax and agent availability without deploying.

**Example:**
```bash
# Deploy default holon.yaml
holon deploy

# Deploy specific example
holon deploy --file samples/news/holon.yaml
# Output: Deployed 'Daily-Briefing-Digest' (ID: digest-8f7a2)
```

### 2.2 List
Lists all currently deployed processes and their status.

**Syntax:**
```bash
holon list [flags]
```

**Flags:**
- `--all`: Show stopped/archived processes as well.
- `--format <json|table>`: Output format (default: table).

**Example:**
```bash
holon list
# Output:
# ID              NAME                    STATUS    UPTIME    TRIGGERS
# digest-8f7a2    Daily-Briefing-Digest   Running   2d 4h     Schedule (0 7 * * *)
# pr-bot-99a1b    Crisis-Comms-Room       Idle      5h        Watcher (Twitter)
```

### 2.3 Event
Manually triggers a specific event or entry point in a running process. This is useful for testing webhooks or forcing a schedule to run immediately.

**Syntax:**
```bash
holon event --process <process_id> --event <event_name> [flags]
```

**Flags:**
- `--process, -p <id>`: The ID or Name of the target process.
- `--event, -e <name>`: The name of the trigger or step to invoke (e.g., `trigger`, `get_news`).
- `--data <json>`: JSON string payload to pass to the event.
- `--file <path>`: Path to a JSON file containing the payload.

**Example:**
```bash
# Trigger the news fetch immediately
holon event --process Daily-Briefing-Digest --event trigger

# Trigger with custom context
holon event -p digest-8f7a2 -e fetch_news --data '{"topic": "Quantum Computing"}'
```

### 2.4 Prompt
Sends a direct prompt or instruction file to a specific process. This is used for "Prompt Mode" interactions where the workflow expects dynamic input (like the `prompt` trigger type).

**Syntax:**
```bash
holon prompt --process <process_id> [flags]
```

**Flags:**
- `--process, -p <id>`: The ID or Name of the target process.
- `--message, -m <string>`: Inline text prompt.
- `--file, -f <path>`: Path to a file (Markdown, Text, Code) to send as context/instruction.

**Example:**
```bash
# Send a quick instruction
holon prompt -p research-bot -m "Find the latest stock price for AAPL"

# Send a detailed instruction file
holon prompt -p code-refactor-bot -f ./specs/new_auth_module.md
```

### 2.5 Logs
Stream or view logs for a specific process.

**Syntax:**
```bash
holon logs <process_id> [flags]
```

**Flags:**
- `--follow, -f`: Stream logs in real-time.
- `--tail <n>`: Show only the last N lines.

**Example:**
```bash
holon logs digest-8f7a2 -f
```

### 2.6 Stop / Delete
Manage the lifecycle of a deployed process.

**Syntax:**
```bash
holon stop <process_id>   # Pauses execution (keeps state)
holon delete <process_id> # Removes the process and configuration
```

---

## 3. Configuration

The CLI can be configured via a global config file (`~/.holon/config.yaml`) or environment variables.

- `HOLON_HOST`: The URL of the Holon Service (default: `localhost:8080`).
- `HOLON_API_KEY`: Authentication key for the service.

**Command:**
```bash
holon config set host https://api.holon.ai
holon config set key sk_live_...
```
