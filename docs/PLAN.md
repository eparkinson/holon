# Holon POC Implementation Plan

## Done

### Phase 1: Foundation & CLI ✅
- [x] Initialize Python project structure (`pyproject.toml`, `src/`).
- [x] Create basic `holon` CLI entry point using `Typer` or `Click`.
- [x] Implement `holon test` command to compile local markdown files and launch interactive chat interface.
- [x] Implement `holon deploy <file>` command structure.
- [x] Implement `Parser` module to extract YAML frontmatter and Markdown body from `.md` files.

### Phase 2: The Agent Runtime (Python) ✅
- [x] Create `Agent` class to represent the parsed configuration and prompt.
- [x] Implement a basic `Runtime` engine that can:
    - [x] Load the `Agent` definition.
    - [x] Handle the `trigger` (e.g., run immediately or simplified cron).
    - [x] Construct the full prompt (System prompt from Markdown + Context).
    - [x] Call an LLM or Higher-Order Agent (using `litellm` to support reasoning/thinking models like Grok, O1).
- [x] Implement an interactive REPL / Chat Loop using stdin/stdout for direct agent communication.
- [x] Implement a basic Tool interface (Support for both Holon-side tools and Model-side internal tools).

### Phase 3: Containerization ✅
- [x] Design the `Dockerfile.template` for the runtime environment.
- [x] Implement logic in CLI to:
    - [x] Generate a directory context for the build.
    - [x] Dynamically create a `Dockerfile` that includes the parsed plan.
    - [x] Execute `docker build`.
    - [x] Execute `docker run`.

### Phase 4: Verification & Examples ✅
- [x] Create 3 sample Holon definitions to validate syntax and capability:
    - [x] `tests/samples/01_echo/echo.md`: Trivial single agent (The "Hello World" of Holon).
    - [x] `tests/samples/02_collaborators/`: Two-agent setup (e.g., Researcher -> Writer) to test chaining.
    - [x] `tests/samples/03_complex_network/`: Multi-agent/High-Order network (testing delegation and reasoning capabilities).
- [x] Verify `holon test` works with all examples (requires API keys).
- [x] Verify `holon deploy` functionality locally with `tests/samples/01_echo/echo.md` (requires Docker).

## To Do

### Phase 5: Agent Network Orchestration (Multi-Agent Intelligence)

A phase focused on enabling complex, coordinated workflows where multiple higher-order agents work together autonomously. This realizes Holon's core vision: **treating agents as intelligent microservices that collaborate without human intervention**.

- [ ] **Agent-to-Agent Communication**
  - [ ] Define `upstream`/`downstream` relationships in agent YAML
  - [ ] Implement message passing protocol between agents
  - [ ] Create `AgentMessage` dataclass with sender, receiver, content, context
  - [ ] Update Runtime to route messages between agents
  - [ ] Add `@agent_receive` hook in agent prompts
  - **Success**: 2-agent pipeline (researcher → writer) working end-to-end

- [ ] **Multi-Agent Network Orchestration**
  - [ ] Define agent `type: network` with execution topology
  - [ ] Support execution modes: sequential, parallel, conditional
  - [ ] Implement network executor for state and dependency management
  - [ ] Add input/output mapping between agents
  - **Success**: 3-agent parallel research network + synthesizer working faster than sequential

- [ ] **Agent Deployment & Containerization (Production-Ready)**
  - [ ] Create HTTP API server for agent invocation (REST endpoints)
  - [ ] Add webhook support for external triggers
  - [ ] Implement environment variable injection for secrets
  - [ ] Add health checks and monitoring hooks
  - [ ] Package multi-agent network as single Docker container
  - **Success**: `docker run holon-agents` starts server; POST to `/agents/{id}` returns responses

  ## Deferred

  - [ ] **Tool Registry & Custom Tool Integration**
  - [ ] Extend global tool registry to support custom Python functions
  - [ ] Add external service integrations (databases, APIs, webhooks)
  - [ ] Implement tool validation and error handling
  - [ ] Create tool calling loop in Runtime (agent requests tool, you execute)
  - **Success**: Agent calling custom Python function and using results

- [ ] **Agent State Management** _(Deferred - evaluate need after network orchestration)_
  - [ ] Leverage existing conversation history in Runtime (already in-memory)
  - [ ] If needed: Add network-wide shared state for multi-agent coordination
  - [ ] If needed: Simple persistence (JSON files or SQLite) for cross-session continuity
  - **Note**: Higher-order agents typically have built-in context/memory. Only implement external storage if agents need to coordinate across separate invocations or exceed token limits.
  - **Success**: Multi-agent network shares state within a single session; optional persistence added only when proven necessary

