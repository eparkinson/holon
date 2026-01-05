# Holon Engine Technical Specification

## 1. Overview
The Holon Engine is the server-side execution plane. It acts as a dynamic runtime interpreter that ingests HolonDSL configurations (`holon.yaml`), manages the lifecycle of agentic workflows, and persists state. It exposes a REST API for the CLI and Dashboard.

## 2. Technology Stack
*   **Language:** Python 3.10+
*   **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async-capable, but running sync endpoints for MVP simplicity).
*   **Database:** [SQLite](https://www.sqlite.org/index.html) (via SQLAlchemy or raw SQL) for zero-config persistence.
*   **Validation:** [Pydantic](https://docs.pydantic.dev/) for request/response schemas and YAML parsing.
*   **Concurrency:** `concurrent.futures.ThreadPoolExecutor` for parallel agent execution (Scatter-Gather).
*   **MCP Support:** `subprocess` module to manage Model Context Protocol servers.

## 3. Architecture

```mermaid
graph TD
    API[FastAPI Layer] --> Controller[Workflow Controller]
    Controller --> DB[(SQLite)]
    Controller --> Interpreter[Runtime Interpreter]
    Interpreter -->|Execute Step| AgentMgr[Agent Manager]
    AgentMgr -->|LLM Call| Provider[LLM Provider (OpenAI/Anthropic)]
    AgentMgr -->|Tool Call| MCP[MCP Client]
    MCP -->|Stdio| MCPServer[External MCP Server]
```

## 4. Data Models (SQLite Schema)

### `projects`
*   `id`: UUID
*   `name`: String
*   `config_yaml`: Text (The raw YAML definition)
*   `created_at`: Timestamp

### `runs`
*   `id`: UUID
*   `project_id`: UUID (FK)
*   `status`: Enum (PENDING, RUNNING, COMPLETED, FAILED)
*   `context`: JSON (The final state/blackboard)
*   `started_at`: Timestamp
*   `ended_at`: Timestamp

### `trace_events`
*   `id`: UUID
*   `run_id`: UUID (FK)
*   `step_id`: String
*   `input`: JSON
*   `output`: JSON
*   `metrics`: JSON (latency, cost, tokens)
*   `timestamp`: Timestamp

## 5. Core Components

### 5.1 API Layer
Exposes REST endpoints:
*   `POST /deploy`: Accepts YAML, validates, saves to `projects`.
*   `POST /projects/{id}/run`: Triggers a new execution.
*   `GET /runs/{id}`: Gets status and current context.
*   `GET /runs/{id}/logs`: Streams trace events.

### 5.2 Runtime Interpreter
The "Virtual Machine" that executes the workflow.
*   **State Machine:** Tracks current step.
*   **Variable Resolver:** Replaces `${trigger.input}` with actual values.
*   **Router:** Evaluates logic (via Python hooks or simple conditionals) to determine the next step.

### 5.3 Agent Manager & MCP Client
*   **Agent Manager:** Standardizes inputs for different providers (OpenAI, Anthropic, Perplexity).
*   **MCP Client:** Manages long-running subprocesses for MCP servers. Handles the JSON-RPC communication over Stdio.

## 6. Execution Flow (MVP)
1.  **Trigger:** API receives a run request.
2.  **Load:** Engine fetches YAML from DB and initializes the `Context`.
3.  **Step Loop:**
    *   Identify next step.
    *   Resolve inputs.
    *   **If Sequential:** Execute in main thread.
    *   **If Scatter-Gather:** Submit tasks to `ThreadPoolExecutor`. Wait for all to complete.
    *   Update `Context` with results.
    *   Save `trace_event` to DB.
4.  **Completion:** Update `runs` status to COMPLETED.

## 7. Future Scope
*   **Asyncio Migration:** Move to full async for higher concurrency.
*   **Distributed Workers:** Use Celery/Redis for scaling beyond a single node.
*   **Sandboxing:** Run Python hooks in a secure sandbox (e.g., Docker/WASM).
