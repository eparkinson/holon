# Phase 1 Implementation & Testing Guide

This document provides a comprehensive overview of what was implemented in Phase 1 and detailed instructions for testing all features.

## Table of Contents
1. [What Was Implemented](#what-was-implemented)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Testing Guide](#testing-guide)
5. [Troubleshooting](#troubleshooting)

---

## What Was Implemented

### 1. Project Structure
Phase 1 establishes the foundational Python package structure:

- **`pyproject.toml`**: Project metadata, dependencies, and build configuration
- **`src/holon/`**: Main package directory with all core modules
- **`tests/`**: Comprehensive test suite
- **Python 3.9+ compatibility**

### 2. Core Modules

#### Parser Module (`src/holon/parser.py`)
Extracts and validates agent definitions from Markdown files:
- Parses YAML frontmatter for agent configuration
- Extracts Markdown body as the system prompt
- Validates configuration using Pydantic models
- Supports both file-based and string-based parsing

#### Data Models (`src/holon/models.py`)
Pydantic models for type safety and validation:
- **`AgentConfig`**: Validates agent configuration (id, model, tools, triggers, etc.)
- **`TriggerConfig`**: Validates trigger configuration (schedule, http, cli)
- **`AgentDefinition`**: Complete agent representation (config + prompt)

#### Runtime Engine (`src/holon/runtime.py`)
Interactive chat runtime for agents:
- REPL-style interface using Rich for beautiful terminal output
- Integration with `litellm` for multi-provider LLM support
- Conversation history management
- Graceful error handling with helpful messages

#### CLI (`src/holon/cli.py`)
Command-line interface built with Typer:
- **`holon version`**: Display version information
- **`holon test [file]`**: Launch interactive chat with an agent
- **`holon deploy <file>`**: Validate agent definition (containerization in Phase 3)

### 3. Test Suite
Comprehensive automated tests (`tests/`):
- 10 tests covering parser validation, CLI commands, and error cases
- Tests for edge cases (missing files, invalid frontmatter, empty prompts)
- 100% passing rate

### 4. Sample Agents
Three example agent configurations demonstrating different capabilities:
- **`test/samples/01_echo/`**: Simple echo bot (single agent)
- **`test/samples/02_collaborators/`**: Two-agent collaboration (researcher + writer)
- **`test/samples/03_complex_network/`**: Multi-agent network (manager + architect + po)

---

## Prerequisites

Before testing, ensure you have:
- **Python 3.9 or higher** installed
- **pip** package manager
- (Optional) API keys for LLM providers if you want to test interactive chat:
  - `OPENAI_API_KEY` for OpenAI models (gpt-4o, gpt-4o-mini)
  - `ANTHROPIC_API_KEY` for Anthropic models (claude-3-5-sonnet)
  - `PERPLEXITY_API_KEY` for Perplexity models (perplexity-sonar-reasoning)

---

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/eparkinson/holon.git
cd holon
```

### Step 2: Install in Development Mode
```bash
pip install -e .
```

This installs the package in editable mode, making the `holon` command available system-wide.

### Step 3: Verify Installation
```bash
holon --help
```

Expected output:
```
Usage: holon [OPTIONS] COMMAND [ARGS]...

 Holon: An agent orchestration engine for higher-order AI agents

╭─ Options ────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                              │
╰──────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────╮
│ version   Show the version of Holon.                                     │
│ test      Test an agent by running it in an interactive chat interface.  │
│ deploy    Deploy an agent by building a Docker container.                │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## Testing Guide

### Test 1: Version Command
**Purpose**: Verify the CLI is working and displays version information.

```bash
holon version
```

**Expected Output**:
```
Holon version 0.1.0
```

✅ **Pass Criteria**: Version number is displayed.

---

### Test 2: Deploy Command (Validation)
**Purpose**: Verify that the parser can read and validate agent definitions.

```bash
holon deploy test/samples/01_echo/echo.md
```

**Expected Output**:
```
Deploying agent from: test/samples/01_echo/echo.md
✓ Parsed agent: echo
✓ Model: gpt-4o-mini

Note: Docker deployment is planned for Phase 3.
For now, use 'holon test' to run agents locally.
```

✅ **Pass Criteria**: Agent is successfully parsed and validated.

**Test with all sample agents**:
```bash
holon deploy test/samples/01_echo/echo.md
holon deploy test/samples/02_collaborators/researcher.md
holon deploy test/samples/02_collaborators/writer.md
holon deploy test/samples/03_complex_network/manager.md
holon deploy test/samples/03_complex_network/architect.md
holon deploy test/samples/03_complex_network/po.md
```

All should parse successfully.

---

### Test 3: Deploy Command (Error Handling)
**Purpose**: Verify proper error handling for invalid files.

```bash
holon deploy nonexistent.md
```

**Expected Output**:
```
Error: Agent definition file not found: nonexistent.md
```

✅ **Pass Criteria**: Clear error message is displayed (exit code 1).

---

### Test 4: Parser Module (Python API)
**Purpose**: Test the parser programmatically.

Create a test script or run in Python:
```python
from holon.parser import Parser

# Test parsing a valid agent
agent = Parser.parse_file('test/samples/01_echo/echo.md')
print(f"Agent ID: {agent.config.id}")
print(f"Model: {agent.config.model}")
print(f"Type: {agent.config.type}")
print(f"Prompt length: {len(agent.prompt)} characters")
```

**Expected Output**:
```
Agent ID: echo
Model: gpt-4o-mini
Type: agent
Prompt length: 146 characters
```

✅ **Pass Criteria**: Agent is parsed correctly with all fields populated.

---

### Test 5: Parser with All Sample Agents
**Purpose**: Verify parser works with all agent types (simple, collaborative, complex).

```bash
python3 -c "
from holon.parser import Parser

samples = [
    'test/samples/01_echo/echo.md',
    'test/samples/02_collaborators/researcher.md',
    'test/samples/02_collaborators/writer.md',
    'test/samples/03_complex_network/manager.md',
    'test/samples/03_complex_network/architect.md',
    'test/samples/03_complex_network/po.md'
]

for sample in samples:
    agent = Parser.parse_file(sample)
    print(f'✓ {sample} → ID: {agent.config.id}, Model: {agent.config.model}')
"
```

**Expected Output**:
```
✓ test/samples/01_echo/echo.md → ID: echo, Model: gpt-4o-mini
✓ test/samples/02_collaborators/researcher.md → ID: researcher, Model: perplexity-sonar-reasoning
✓ test/samples/02_collaborators/writer.md → ID: writer, Model: claude-3-5-sonnet
✓ test/samples/03_complex_network/manager.md → ID: manager, Model: o1-preview
✓ test/samples/03_complex_network/architect.md → ID: architect, Model: claude-3-5-sonnet
✓ test/samples/03_complex_network/po.md → ID: po, Model: gpt-4o
```

✅ **Pass Criteria**: All agents parse successfully.

---

### Test 6: Automated Test Suite
**Purpose**: Run the comprehensive automated test suite.

#### Install pytest (if not already installed):
```bash
pip install pytest
```

#### Run all tests:
```bash
pytest tests/ -v
```

**Expected Output**:
```
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /path/to/holon
configfile: pyproject.toml
collected 10 items

tests/test_cli.py::test_version_command PASSED                                                               [ 10%]
tests/test_cli.py::test_deploy_command_with_valid_file PASSED                                                [ 20%]
tests/test_cli.py::test_deploy_command_with_invalid_file PASSED                                              [ 30%]
tests/test_parser.py::test_parse_echo_agent PASSED                                                           [ 40%]
tests/test_parser.py::test_parse_researcher_agent PASSED                                                     [ 50%]
tests/test_parser.py::test_parse_manager_agent PASSED                                                        [ 60%]
tests/test_parser.py::test_parse_string PASSED                                                               [ 70%]
tests/test_parser.py::test_parse_missing_file PASSED                                                         [ 80%]
tests/test_parser.py::test_parse_invalid_frontmatter PASSED                                                  [ 90%]
tests/test_parser.py::test_parse_empty_prompt PASSED                                                         [100%]

================================================== 10 passed in 1.82s ==================================================
```

✅ **Pass Criteria**: All 10 tests pass.

---

### Test 7: Interactive Chat (Optional - Requires API Key)
**Purpose**: Test the interactive runtime with a live LLM.

⚠️ **Note**: This test requires a valid API key for the model being used.

#### Set your API key:
```bash
export OPENAI_API_KEY="your-key-here"
```

#### Run the echo agent interactively:
```bash
holon test test/samples/01_echo/echo.md
```

**Expected Output**:
```
╭─────────────────────── Welcome to Holon ───────────────────────╮
│ Holon Agent: echo                                               │
│ Model: gpt-4o-mini                                              │
│ Type 'exit' or 'quit' to end the session.                      │
╰─────────────────────────────────────────────────────────────────╯

You: Hello
```

The agent should respond with your input formatted as a quote block:
```
echo:
> Hello
```

Type `exit` to end the session.

✅ **Pass Criteria**: 
- Agent starts successfully
- Agent responds to user input
- Responses match the agent's prompt instructions
- Session can be exited cleanly

---

### Test 8: Test Command Without File Argument
**Purpose**: Verify auto-detection of markdown files.

```bash
cd test/samples/01_echo
echo "exit" | holon test
```

**Expected Output**:
```
Using: /path/to/test/samples/01_echo/echo.md
╭────────────────────────────── Welcome to Holon ──────────────────────────────╮
│ Holon Agent: echo                                                            │
│ Model: gpt-4o-mini                                                           │
│ Type 'exit' or 'quit' to end the session.                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

You: 
Goodbye!
```

**If multiple `.md` files exist**:
```
Error: Multiple markdown files found. Please specify which one to use:
  - file1.md
  - file2.md
```

✅ **Pass Criteria**: 
- Single `.md` file is auto-detected
- Multiple files show an error with list
- No files shows an appropriate error message

---

### Test 9: Parser Error Handling
**Purpose**: Verify parser handles invalid configurations gracefully.

Create a test file with invalid frontmatter:
```bash
cat > /tmp/invalid_agent.md << 'EOF'
---
type: agent
---

# Test Agent

Missing required 'id' and 'model' fields.
EOF
```

Test parsing:
```bash
holon deploy /tmp/invalid_agent.md
```

**Expected Output**:
```
Error: Invalid agent configuration in /tmp/invalid_agent.md: ...
```

✅ **Pass Criteria**: Clear error message indicating what's wrong.

---

### Test 10: Parser with Empty Prompt
**Purpose**: Verify parser rejects agents with no prompt body.

Create a test file:
```bash
cat > /tmp/empty_prompt.md << 'EOF'
---
id: test-agent
type: agent
model: gpt-4o
---

EOF
```

Test parsing:
```bash
holon deploy /tmp/empty_prompt.md
```

**Expected Output**:
```
Error: Agent definition must contain a prompt body in /tmp/empty_prompt.md
```

✅ **Pass Criteria**: Error message about missing prompt.

---

## Troubleshooting

### Issue: `holon: command not found`
**Solution**: Reinstall the package:
```bash
pip install -e .
```

Or use the full path to Python:
```bash
python3 -m holon.cli --help
```

### Issue: `ModuleNotFoundError: No module named 'holon'`
**Solution**: Ensure you're in the correct directory and the package is installed:
```bash
cd /path/to/holon
pip install -e .
```

### Issue: API key errors when testing interactive chat
**Example Error**:
```
Failed to get response from model 'gpt-4o-mini': ...
Make sure you have the appropriate API key set
```

**Solution**: Export the correct API key:
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export PERPLEXITY_API_KEY="your-key"
```

### Issue: Tests fail with import errors
**Solution**: Ensure pytest and dependencies are installed:
```bash
pip install -e .
pip install pytest
```

### Issue: Rich output looks broken in terminal
**Solution**: Ensure your terminal supports ANSI colors and Unicode. Most modern terminals do.

---

## Summary

### What Works ✅
- CLI with `version`, `test`, and `deploy` commands
- Markdown parser with YAML frontmatter validation
- Pydantic models for type safety
- Interactive chat runtime (with API keys)
- Comprehensive test suite (10/10 passing)
- Error handling for invalid configurations

### What's Coming Next 🚧
- **Phase 2**: Tool interfaces and multi-agent orchestration
- **Phase 3**: Docker containerization and deployment
- **Phase 4**: Production examples and advanced features

---

## Quick Validation Checklist

Use this checklist to quickly validate the Phase 1 implementation:

- [ ] `holon --help` displays commands
- [ ] `holon version` shows version 0.1.0
- [ ] `holon deploy test/samples/01_echo/echo.md` validates successfully
- [ ] All 6 sample agents parse without errors
- [ ] `pytest tests/ -v` shows 10/10 passing
- [ ] Parser rejects invalid configurations with clear errors
- [ ] (Optional) Interactive chat works with API key

### Automated Validation Script

For convenience, run the automated validation script:

```bash
bash scripts/validate_phase1.sh
```

This script runs all the essential tests and provides a summary report.

If all checks pass, Phase 1 is working correctly! ✅
