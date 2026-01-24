# Agents.md - Guide for AI Coding Agents

This document provides essential context for AI coding agents working on the Holon codebase. It's designed to help you quickly understand the project structure, make effective changes, and maintain code quality.

## Project Overview

**Holon** is an open-source Agent Orchestration Engine for Higher-Order AI Agents. It allows developers to define AI agent networks using Markdown files with YAML frontmatter, treating AI agents as microservices.

### Core Philosophy
- **Markdown + YAML**: Agent definitions are human-readable Markdown files with YAML metadata
- **Declarative over Imperative**: Define what agents should do, not how to do it
- **Federated Architecture**: Agents are treated as autonomous microservices
- **Portable**: Single Docker container deployment (planned for Phase 3)

### Key Features
1. **Agent Definition**: Define agents in `.md` files with YAML frontmatter
2. **Interactive Testing**: Test agents locally via CLI REPL interface
3. **Model Agnostic**: Support for multiple LLM providers via `litellm`
4. **Extensible**: Support for tools and multi-agent collaboration

## Project Structure

```
holon/
├── src/holon/           # Main package source code
│   ├── __init__.py      # Package initialization, version info
│   ├── cli.py           # Command-line interface (Typer-based)
│   ├── parser.py        # Markdown/YAML frontmatter parser
│   ├── models.py        # Pydantic models for validation
│   └── runtime.py       # Agent execution engine
├── test/samples/        # Example agent definitions
│   ├── 01_echo/         # Simple echo bot example
│   ├── 02_collaborators/# Multi-agent collaboration
│   └── 03_complex_network/ # Complex agent network
├── tests/               # pytest test suite
│   ├── test_parser.py   # Parser unit tests
│   └── test_cli.py      # CLI tests
├── docs/                # Documentation
│   ├── DESIGN.md        # Architecture and design spec
│   ├── PLAN.md          # Implementation roadmap
│   └── PHASE1_SUMMARY.md # Phase 1 completion summary
├── scripts/             # Utility scripts
├── pyproject.toml       # Project metadata and dependencies
└── README.md            # User-facing documentation
```

## Development Setup

### Prerequisites
- Python 3.9 or higher
- pip for package management

### Installation

```bash
# Clone the repository
git clone https://github.com/eparkinson/holon.git
cd holon

# Install in editable mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py -v

# Run with coverage
pytest tests/ --cov=holon --cov-report=html
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Both tools are configured in pyproject.toml
```

## Core Components

### 1. CLI (`src/holon/cli.py`)
- Built with `Typer`
- Commands:
  - `holon version`: Display version
  - `holon test [file]`: Test agent interactively
  - `holon deploy <file>`: Deploy agent (Phase 3 - not yet implemented)
- Uses `rich` for beautiful console output

### 2. Parser (`src/holon/parser.py`)
- Extracts YAML frontmatter and Markdown body
- Uses `python-frontmatter` library
- Methods:
  - `parse_file(file_path)`: Parse from file
  - `parse_string(content)`: Parse from string
- Returns `AgentDefinition` objects

### 3. Models (`src/holon/models.py`)
- Pydantic models for validation
- Key models:
  - `AgentConfig`: YAML frontmatter configuration
  - `TriggerConfig`: Trigger configuration (schedule, http, cli)
  - `AgentDefinition`: Complete agent (config + prompt)
- Uses Pydantic v2 with `ConfigDict(extra="allow")` for extensibility

### 4. Runtime (`src/holon/runtime.py`)
- Executes agents interactively
- Uses `litellm` for LLM API calls
- Manages conversation history
- Provides REPL interface with `rich` formatting
- Key methods:
  - `run_interactive()`: Start chat session
  - `_get_llm_response()`: Get LLM response

## Agent Definition Format

Agents are defined in Markdown files with YAML frontmatter:

```markdown
---
id: my-agent                    # Required: unique identifier
type: agent                     # Required: "agent" or "network"
model: gpt-4o-mini              # Required: LLM model name
trigger:                        # Optional: trigger configuration
  type: schedule
  cron: "0 9 * * *"
tools:                          # Optional: list of available tools
  - web_search
  - postgres_mcp
upstream:                       # Optional: upstream agent IDs
  - researcher
downstream:                     # Optional: downstream agent IDs
  - writer
---

# Agent Name

Your system prompt goes here. This is the instruction text that will be
sent to the LLM to define the agent's behavior, personality, and goals.

You can use full Markdown formatting including:
- Lists
- **Bold** and *italic*
- Code blocks
- Links and more
```

### Required Fields
- `id`: Unique identifier (string)
- `model`: LLM model to use (e.g., "gpt-4o-mini", "claude-3-5-sonnet", "o1-preview")

### Optional Fields
- `type`: "agent" (default) or "network"
- `trigger`: Trigger configuration object
- `tools`: List of tool names
- `upstream`: List of upstream agent IDs
- `downstream`: List of downstream agent IDs

## Testing Agents

### Set API Keys
```bash
# For OpenAI models
export OPENAI_API_KEY="sk-..."

# For Anthropic models
export ANTHROPIC_API_KEY="sk-ant-..."

# For Perplexity models
export PERPLEXITY_API_KEY="..."
```

### Test Interactively
```bash
# Test a specific agent
holon test test/samples/01_echo/echo.md

# Test from current directory (auto-detects .md file)
cd test/samples/01_echo
holon test

# Exit the chat with 'exit' or 'quit'
```

## Common Development Tasks

### Adding a New CLI Command
1. Edit `src/holon/cli.py`
2. Add a new function decorated with `@app.command()`
3. Use `typer.Argument()` or `typer.Option()` for parameters
4. Use `console.print()` for output with `rich` formatting

### Adding a New Agent Configuration Field
1. Update `AgentConfig` in `src/holon/models.py`
2. Add the field with appropriate type and validation
3. Update parser tests in `tests/test_parser.py`
4. Update sample agents in `test/samples/` if needed

### Adding a New Parser Feature
1. Edit `src/holon/parser.py`
2. Modify `parse_file()` or `parse_string()` methods
3. Add corresponding tests in `tests/test_parser.py`
4. Ensure error handling with helpful messages

### Modifying Runtime Behavior
1. Edit `src/holon/runtime.py`
2. Update `run_interactive()` for chat loop changes
3. Update `_get_llm_response()` for LLM interaction changes
4. Test with sample agents to ensure compatibility

## Important Conventions

### Code Style
- **Formatting**: Black with 100-character line length
- **Linting**: Ruff (configured in `pyproject.toml`)
- **Python Version**: Target 3.9+ for compatibility
- **Type Hints**: Use type hints where practical
- **Docstrings**: Use Google-style docstrings

### Error Handling
- Use specific exceptions (`FileNotFoundError`, `ValueError`)
- Provide helpful error messages
- Use `rich` console for user-facing errors
- Don't crash the REPL - catch and display errors

### Testing
- Use pytest
- Test files mirror source structure (`tests/test_*.py`)
- Use fixtures for repeated setup
- Test both success and failure cases
- Sample agents in `test/samples/` serve as integration tests

## Dependencies

### Core Dependencies
- `typer>=0.9.0`: CLI framework
- `python-frontmatter>=1.0.0`: YAML/Markdown parsing
- `pydantic>=2.0.0`: Data validation
- `litellm>=1.0.0`: Unified LLM API interface
- `rich>=13.0.0`: Beautiful terminal output

### Development Dependencies
- `pytest>=7.0.0`: Testing framework
- `black>=23.0.0`: Code formatter
- `ruff>=0.1.0`: Fast Python linter

## Current Implementation Status

### ✅ Completed (Phase 1 & 2)
- CLI foundation with `test` and `deploy` commands
- Parser with YAML frontmatter extraction
- Pydantic models for validation
- Interactive runtime with litellm integration
- Sample agents demonstrating capabilities
- Basic test suite

### 🚧 Planned / Not Yet Implemented
- **Phase 2**: Tool interface implementation (support for Holon-side and model-side tools)
- **Phase 3**: Docker containerization and deployment
- **Phase 3**: Full deployment functionality
- **Phase 4**: Production examples and additional documentation

See `docs/PLAN.md` for detailed roadmap.

## Sample Agents

### Simple Echo Bot (`test/samples/01_echo/echo.md`)
- Minimal agent that echoes user input
- Good for testing basic functionality
- Uses `gpt-4o-mini` model

### Collaborators (`test/samples/02_collaborators/`)
- `researcher.md`: Uses Perplexity with web search
- `writer.md`: Creates content based on research
- Demonstrates multi-agent workflows

### Complex Network (`test/samples/03_complex_network/`)
- `manager.md`: Engineering manager using O1
- `architect.md`: Technical architect
- `po.md`: Product owner
- Demonstrates complex agent interactions

## Helpful Tips for Coding Agents

1. **Read the Design First**: Check `docs/DESIGN.md` for architecture
2. **Follow Existing Patterns**: Look at similar code before adding new features
3. **Test Incrementally**: Run tests after each change
4. **Use Sample Agents**: Test changes with `test/samples/` agents
5. **Minimal Changes**: Keep modifications focused and small
6. **Error Messages**: Make them helpful for end users
7. **Documentation**: Update README.md if user-facing changes
8. **API Keys**: Remember agents need API keys set in environment

## Getting Help

- **README.md**: User-facing documentation
- **docs/DESIGN.md**: Architecture and design decisions
- **docs/PLAN.md**: Implementation roadmap and status
- **test/samples/**: Working examples of agent definitions
- **tests/**: Examples of how to test components

## License

MIT License - See LICENSE file for details.
