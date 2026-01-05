# Holon Engine

The core orchestration service for the Holon Agent Framework.

## Quick Start

### Installation

```bash
cd engine
pip install -e ".[dev]"
```

### Running Locally

```bash
cd src
python -m holon_engine.main
```

The API server will start on `http://localhost:8000`.

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
pytest
```

## Architecture

The engine consists of:

1. **API Layer** (`api.py`) - FastAPI endpoints matching the OpenAPI spec
2. **Data Models** (`models.py`) - Pydantic schemas for validation
3. **Database** (`database.py`) - SQLAlchemy models and SQLite persistence
4. **Workflow Engine** (`engine.py`) - Execution engine for HolonDSL workflows

## Current Limitations (Prototype)

This is a skeleton/prototype implementation with the following limitations:

- **No Real Agents**: Steps are simulated and return mock data
- **Sequential Only**: Only sequential workflows are implemented
- **No MCP Integration**: MCP servers are not yet connected
- **No Security**: No authentication or authorization
- **Basic Error Handling**: Minimal error recovery

These will be addressed in future iterations.
