"""Tests for the Holon Engine API."""

import tempfile
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from holon_engine.api import app
from holon_engine.persistence import PersistenceService


@pytest.fixture
def test_storage():
    """Create a temporary storage directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(test_storage, monkeypatch):
    """Create a test client with isolated storage."""

    # Mock the persistence service to use test storage
    def mock_get_persistence():
        return PersistenceService(f"file://{test_storage}")

    import holon_engine.api as api_module

    monkeypatch.setattr(api_module, "get_persistence", mock_get_persistence)

    with TestClient(app) as client:
        yield client


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_version_endpoint(client):
    """Test the version endpoint."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_deploy_project(client):
    """Test deploying a project."""
    config_yaml = """
version: "1.0"
project: "Test-Project"

resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet

workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Test instruction"
"""

    response = client.post(
        "/api/v1/deploy",
        json={
            "name": "Test-Project",
            "config_yaml": config_yaml,
            "env_vars": {"API_KEY": "test123"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert data["status"] == "deployed"


def test_list_projects(client):
    """Test listing projects."""
    # Deploy a project first
    config_yaml = """
version: "1.0"
project: "Test-List-Project"
resources:
  - id: agent1
    provider: anthropic
    model: claude-3-5-sonnet
workflow:
  type: sequential
  steps:
    - id: step1
      agent: agent1
      instruction: "Test"
"""

    deploy_response = client.post(
        "/api/v1/deploy",
        json={"name": "Test-List-Project", "config_yaml": config_yaml},
    )
    assert deploy_response.status_code == 200

    # List projects
    list_response = client.get("/api/v1/projects")
    assert list_response.status_code == 200
    projects = list_response.json()
    assert len(projects) >= 1
    assert any(p["name"] == "Test-List-Project" for p in projects)


def test_list_processes(client):
    """Test listing processes."""
    # Deploy a project first
    config_yaml = """
version: "1.0"
project: "Test-Process"
trigger:
  type: schedule
  cron: "0 7 * * *"
resources:
  - id: agent1
    provider: anthropic
    model: claude-3-5-sonnet
workflow:
  type: sequential
  steps:
    - id: step1
      agent: agent1
      instruction: "Test"
"""

    deploy_response = client.post(
        "/api/v1/deploy",
        json={"name": "Test-Process", "config_yaml": config_yaml},
    )
    assert deploy_response.status_code == 200

    # List processes
    response = client.get("/api/v1/processes")
    assert response.status_code == 200
    processes = response.json()
    assert len(processes) >= 1
    assert any(p["name"] == "Test-Process" for p in processes)


def test_trigger_run(client):
    """Test triggering a workflow run."""
    config_yaml = """
version: "1.0"
project: "Test-Run-Project"
resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet
workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Process ${trigger.input.topic}"
"""

    # Deploy a project
    deploy_response = client.post(
        "/api/v1/deploy", json={"name": "Test-Run-Project", "config_yaml": config_yaml}
    )
    project_id = deploy_response.json()["project_id"]

    # Trigger a run
    run_response = client.post(
        f"/api/v1/projects/{project_id}/run", json={"input_context": {"topic": "Rust"}}
    )

    assert run_response.status_code == 202
    data = run_response.json()
    assert "run_id" in data
    assert data["status"] == "PENDING"


def test_get_run_status(client):
    """Test getting run status."""
    config_yaml = """
version: "1.0"
project: "Test-Status-Project"
resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet
workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Test"
"""

    # Deploy and trigger
    deploy_response = client.post(
        "/api/v1/deploy",
        json={"name": "Test-Status-Project", "config_yaml": config_yaml},
    )
    project_id = deploy_response.json()["project_id"]

    run_response = client.post(f"/api/v1/projects/{project_id}/run", json={})
    run_id = run_response.json()["run_id"]

    # Get run status
    status_response = client.get(f"/api/v1/runs/{run_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["id"] == run_id
    assert data["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]


def test_get_run_logs(client):
    """Test getting run logs."""
    config_yaml = """
version: "1.0"
project: "Test-Logs-Project"
resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet
workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Test"
"""

    # Deploy and trigger
    deploy_response = client.post(
        "/api/v1/deploy", json={"name": "Test-Logs-Project", "config_yaml": config_yaml}
    )
    project_id = deploy_response.json()["project_id"]

    run_response = client.post(f"/api/v1/projects/{project_id}/run", json={})
    run_id = run_response.json()["run_id"]

    # Get logs
    logs_response = client.get(f"/api/v1/runs/{run_id}/logs")
    assert logs_response.status_code == 200
    assert isinstance(logs_response.json(), list)
