# Quick Start Guide - Holon Engine

This guide will help you get the Holon Engine running locally in minutes.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation

1. **Navigate to the engine directory:**
   ```bash
   cd engine
   ```

2. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

## Running the Engine

1. **Start the server:**
   ```bash
   cd src
   python -m holon_engine.main
   ```

2. **Verify it's running:**
   Open your browser and visit:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Example: Deploy and Run a Workflow

### 1. Deploy a Project

```bash
curl -X POST http://localhost:8000/api/v1/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research-Agent",
    "config_yaml": "version: \"1.0\"\nproject: \"Research-Agent\"\n\nresources:\n  - id: researcher\n    provider: perplexity\n    model: sonar-reasoning\n\nworkflow:\n  type: sequential\n  steps:\n    - id: research\n      agent: researcher\n      instruction: \"Research ${trigger.input.topic}\""
  }'
```

This will return a `project_id`.

### 2. List Projects

```bash
curl http://localhost:8000/api/v1/projects
```

### 3. Trigger a Run

Replace `<project_id>` with the ID from step 1:

```bash
curl -X POST http://localhost:8000/api/v1/projects/<project_id>/run \
  -H "Content-Type: application/json" \
  -d '{"input_context": {"topic": "Quantum Computing"}}'
```

This will return a `run_id`.

### 4. Check Run Status

Replace `<run_id>` with the ID from step 3:

```bash
curl http://localhost:8000/api/v1/runs/<run_id>
```

### 5. View Run Logs

```bash
curl http://localhost:8000/api/v1/runs/<run_id>/logs
```

## Running Tests

```bash
cd engine
pytest
```

All tests should pass (14 tests).

## Interactive API Documentation

The engine provides interactive API documentation via Swagger UI:

http://localhost:8000/docs

You can explore and test all endpoints directly from your browser.

## What's Working (Prototype)

- ✅ Deploy projects with HolonDSL (holon.yaml) configurations
- ✅ List all deployed projects
- ✅ Trigger workflow runs with custom input context
- ✅ Track run status (PENDING → RUNNING → COMPLETED/FAILED)
- ✅ View detailed execution logs and trace events
- ✅ Template variable resolution (e.g., `${trigger.input.topic}`)
- ✅ SQLite persistence for projects and runs

## Known Limitations (Prototype)

This is a skeleton/prototype implementation:

- ⚠️ **No Real Agents**: Agent steps are simulated and return mock data
- ⚠️ **Sequential Only**: Only sequential workflows are implemented (no scatter-gather yet)
- ⚠️ **No MCP Integration**: MCP servers defined in configs are not yet connected
- ⚠️ **No Security**: No authentication or authorization
- ⚠️ **Basic Error Handling**: Minimal error recovery and validation

These will be addressed in future iterations.

## Troubleshooting

### Port 8000 Already in Use

If you see `Address already in use`, another process is using port 8000. Find and stop it:

```bash
lsof -ti :8000 | xargs kill
```

### Database Issues

If you encounter database errors, remove the database file and restart:

```bash
rm holon.db
python -m holon_engine.main
```

## Next Steps

- Explore the sample configurations in `/samples`
- Check out the API documentation at `/docs`
- Read the design specification in `/docs/DESIGN.md`
