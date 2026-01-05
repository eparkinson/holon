# Holon Creation Workflow

This guide details the developer process for creating, deploying, monitoring, and using a new Holon network (Agentic Workflow). We will use the **Daily Briefing Digest** (`samples/news/holon.yaml`) as our primary example.

---

## 1. Prerequisites (Environment Setup)

Before creating a new Holon, ensure your local environment is running.

1.  **Start the Local Platform**
    Use the provided script to spin up the Engine, database, and Web Dashboard.

    ```bash
    ./scripts/start_local.sh
    ```

    *   **Engine API:** `http://localhost:8000`
    *   **Dashboard:** `http://localhost:3000`

2.  **Verify CLI Connectivity**
    Ensure the CLI is installed and can talk to the engine.

    ```bash
    holon list
    # Should return an empty list if fresh, or existing projects.
    ```

---

## 2. Define the Network (`holon.yaml`)

The core of any Holon application is the `holon.yaml` file. This defines the **Trigger** (how it starts), the **Resources** (which agents involved), and the **Workflow** (the logic).

### Example Scenario: Daily News Digest

We want a bot that wakes up at 7 AM, researches specific topics using Perplexity and X.com (Grok), and uses Claude to synthesize a report.

### Structure of `holon.yaml`

Create a file named `holon.yaml` in your project folder (e.g., `samples/news/holon.yaml`).

#### A. Triggers
Define how the workflow begins. This could be a schedule (Cron), a webhook, or a manual prompt.

```yaml
version: "1.0"
project: "Daily-Briefing-Digest"

# 1. TRIGGER: Run every morning at 7 AM
trigger:
  type: schedule
  cron: "0 7 * * *"
  # Context variables available to the workflow
  context:
    topics:
      - "Rust Programming Language updates"
      - "AI Agent Frameworks"
      - "SpaceX Starship progress"
    preferred_sources:
      - "Hacker News"
      - "ArXiv"
      - "TechCrunch"
```

#### B. Resources (Agents)
Define the "Team" you need. Each resource is an Agent or an MCP Server.

```yaml
# 2. RESOURCES: The Agents
resources:
  - id: news_hunter
    provider: perplexity
    model: sonar-reasoning

  - id: x_hunter
    provider: grok
    model: grok-beta
  
  - id: editor
    provider: claude
    model: 3-5-sonnet
    # Example: Mount a filesystem tool to save the report directly
    tools: [filesystem_mcp]

  - id: filesystem_mcp
    type: mcp-server
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./briefings"]
```

#### C. Workflow
Define the execution steps. Holon supports sequential steps, parallel execution (`scatter-gather`), and more.

```yaml
# 3. WORKFLOW
workflow:
  type: sequential
  steps:
    # Step 1: Research all topics in parallel (Web + Social)
    - id: fetch_intelligence
      type: scatter-gather
      parallel_tasks:
        # Sub-task A: Perplexity for Web News
        - id: fetch_web_news
          type: map
          # ... (full mapping logic to news_hunter)
```

---

## 3. Configuration (Secrets)

Most agents require API keys (e.g., `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`). You do not put these in the YAML.

1.  **Create a `.env` file** in your project directory.
    ```bash
    ANTHROPIC_API_KEY=sk-...
    PERPLEXITY_API_KEY=pplx-...
    XAI_API_KEY=...
    ```

---

## 4. Deploy the Holon

Once defined, push the configuration to the Holon Engine.

By default, `holon deploy` looks for `holon.yaml` and `.env` in the current directory.

```bash
# Deploy a specific file
holon deploy --file samples/news/holon.yaml
```

**Success Output:**
```text
✓ Deployed 'Daily-Briefing-Digest'
  ├── ID: digest-8f7a2
  ├── Status: Active
  └── Next Run: Tomorrow at 07:00 AM
```

---

## 5. Manual Execution & Testing

You don't have to wait for the schedule (7 AM) to test if it works. Use the `event` command to force a run.

### Triggering the Default Entry Point
```bash
holon event --process "Daily-Briefing-Digest" --event trigger
```

### Triggering with Custom Data
You can override the context variables defined in the YAML for a single run.

```bash
# Test with a different topic
holon event --process "Daily-Briefing-Digest" --event trigger \
  --data '{"topics": ["New Holon Version Release"]}'
```

---

## 6. Monitoring & Debugging

### CLI Monitoring
Check the status of your deployed Holons.

```bash
holon list
```

### Web Dashboard
Open **http://localhost:3000** to see:
1.  **Service Directory**: All deployed Holons.
2.  **Run History**: Logs of previous executions.
3.  **Live Trace**: Watch each step of the workflow execute in real-time (e.g., watching Perplexity fetch results, then Claude writing the file).

### Logs
To see raw logs from the backend:

```bash
docker-compose logs -f engine
```

---

## 7. Stopping / Removing

To stop a running workflow or change its schedule, simply deploy an updated YAML. The engine handles versioning and updates the existing reference if the `project` name matches.

To shut down the entire local environment:

```bash
./scripts/stop_local.sh
```
