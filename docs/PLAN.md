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

## To Do

### Phase 3: Containerization
- [ ] Design the `Dockerfile.template` for the runtime environment.
- [ ] Implement logic in CLI to:
    - [ ] Generate a directory context for the build.
    - [ ] Dynamically create a `Dockerfile` that includes the parsed plan.
    - [ ] Execute `docker build`.
    - [ ] Execute `docker run`.

### Phase 4: Verification & Examples
- [x] Create 3 sample Holon definitions to validate syntax and capability:
    - [x] `tests/samples/01_echo/echo.md`: Trivial single agent (The "Hello World" of Holon).
    - [x] `tests/samples/02_collaborators/`: Two-agent setup (e.g., Researcher -> Writer) to test chaining.
    - [x] `tests/samples/03_complex_network/`: Multi-agent/High-Order network (testing delegation and reasoning capabilities).
- [x] Verify `holon test` works with all examples (requires API keys).
- [ ] Verify `holon deploy` functionality locally with `tests/samples/01_echo/echo.md` (Phase 3 pending).
