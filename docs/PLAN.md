# Holon POC Implementation Plan

## Done
(No items yet)

## To Do

### Phase 1: Foundation & CLI
- [ ] Initialize Python project structure (`pyproject.toml`, `src/`).
- [ ] Create basic `holon` CLI entry point using `Typer` or `Click`.
- [ ] Implement `holon test` command to compile local markdown files and launch interactive chat interface.
- [ ] Implement `holon deploy <file>` command structure.
- [ ] Implement `Parser` module to extract YAML frontmatter and Markdown body from `.md` files.

### Phase 2: The Agent Runtime (Python)
- [ ] Create `Agent` class to represent the parsed configuration and prompt.
- [ ] Implement a basic `Runtime` engine that can:
    - [ ] Load the `Agent` definition.
    - [ ] Handle the `trigger` (e.g., run immediately or simplified cron).
    - [ ] Construct the full prompt (System prompt from Markdown + Context).
    - [ ] Call an LLM or Higher-Order Agent (using `litellm` to support reasoning/thinking models like Grok, O1).
- [ ] Implement an interactive REPL / Chat Loop using stdin/stdout for direct agent communication.
- [ ] Implement a basic Tool interface (Support for both Holon-side tools and Model-side internal tools).

### Phase 3: Containerization
- [ ] Design the `Dockerfile.template` for the runtime environment.
- [ ] Implement logic in CLI to:
    - [ ] Generate a directory context for the build.
    - [ ] dynamicall create a `Dockerfile` that includes the parsed plan.
    - [ ] Execute `docker build`.
    - [ ] Execute `docker run`.

### Phase 4: Verification & Examples
- [ ] Create 3 sample Holon definitions to validate syntax and capability:
    - [ ] `test/samples/01_echo/echo.md`: Trivial single agent (The "Hello World" of Holon).
    - [ ] `test/samples/02_collaborators/`: Two-agent setup (e.g., Researcher -> Writer) to test chaining.
    - [ ] `test/samples/03_complex_network/`: Multi-agent/High-Order network (testing delegation and reasoning capabilities).
- [ ] Verify `holon test` works with all examples.
- [ ] Verify `holon deploy` functionality locally with `test/samples/01_echo/echo.md`.
