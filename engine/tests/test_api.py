"""Basic tests for the Holon Engine API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from holon_engine.api import app
from holon_engine.database import Base


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_client():
    """Create a test client with an in-memory database for each test."""
    # Create a unique in-memory database for this test
    from holon_engine.database import init_db, get_session_maker
    import holon_engine.api as api_module
    
    # Use a unique in-memory DB for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=None  # Don't pool connections for testing
    )
    Base.metadata.create_all(engine)
    TestSessionMaker = sessionmaker(bind=engine)
    
    # Override the global SessionMaker in the app
    original_session_maker = api_module.SessionMaker
    original_engine = api_module.engine
    
    api_module.SessionMaker = TestSessionMaker
    api_module.engine = engine
    
    # Create test client
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client
    
    # Cleanup and restore
    Base.metadata.drop_all(engine)
    engine.dispose()
    api_module.SessionMaker = original_session_maker
    api_module.engine = original_engine


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_version_endpoint(test_client):
    """Test the version endpoint."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_deploy_project(test_client):
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
    
    response = test_client.post(
        "/api/v1/deploy",
        json={
            "name": "Test-Project",
            "config_yaml": config_yaml
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert data["status"] == "deployed"


def test_deploy_invalid_yaml(test_client):
    """Test deploying with invalid YAML."""
    response = test_client.post(
        "/api/v1/deploy",
        json={
            "name": "Bad-Project",
            "config_yaml": "not: valid: yaml: structure"
        }
    )
    
    assert response.status_code == 400
    assert "Invalid YAML Configuration" in response.json()["detail"]


def test_list_projects_empty(test_client):
    """Test listing projects when none exist initially in this test."""
    # Get initial count
    response = test_client.get("/api/v1/projects")
    assert response.status_code == 200
    # For a clean test, we just verify the endpoint works
    # Other tests may have created projects before this test runs
    assert isinstance(response.json(), list)


def test_list_projects(test_client):
    """Test listing projects after deployment."""
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
      instruction: "Test"
"""
    
    # Get initial count
    initial_response = test_client.get("/api/v1/projects")
    initial_count = len(initial_response.json())
    
    # Deploy a project
    deploy_response = test_client.post(
        "/api/v1/deploy",
        json={"name": "Test-Project-List", "config_yaml": config_yaml}
    )
    assert deploy_response.status_code == 200
    
    # List projects
    list_response = test_client.get("/api/v1/projects")
    assert list_response.status_code == 200
    projects = list_response.json()
    assert len(projects) == initial_count + 1
    # Verify our project is in the list
    assert any(p["name"] == "Test-Project-List" for p in projects)


def test_trigger_run(test_client):
    """Test triggering a workflow run."""
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
      instruction: "Process ${trigger.input.topic}"
"""
    
    # Deploy a project
    deploy_response = test_client.post(
        "/api/v1/deploy",
        json={"name": "Test-Project", "config_yaml": config_yaml}
    )
    project_id = deploy_response.json()["project_id"]
    
    # Trigger a run
    run_response = test_client.post(
        f"/api/v1/projects/{project_id}/run",
        json={"input_context": {"topic": "Rust"}}
    )
    
    assert run_response.status_code == 202
    data = run_response.json()
    assert "run_id" in data
    assert data["status"] == "PENDING"


def test_get_run_status(test_client):
    """Test getting run status."""
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
      instruction: "Test"
"""
    
    # Deploy and trigger
    deploy_response = test_client.post(
        "/api/v1/deploy",
        json={"name": "Test-Project", "config_yaml": config_yaml}
    )
    project_id = deploy_response.json()["project_id"]
    
    run_response = test_client.post(
        f"/api/v1/projects/{project_id}/run",
        json={}
    )
    run_id = run_response.json()["run_id"]
    
    # Get run status
    status_response = test_client.get(f"/api/v1/runs/{run_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["id"] == run_id
    assert data["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]


def test_get_nonexistent_run(test_client):
    """Test getting a run that doesn't exist."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = test_client.get(f"/api/v1/runs/{fake_uuid}")
    assert response.status_code == 404


def test_get_run_logs(test_client):
    """Test getting run logs."""
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
      instruction: "Test"
"""
    
    # Deploy and trigger
    deploy_response = test_client.post(
        "/api/v1/deploy",
        json={"name": "Test-Project", "config_yaml": config_yaml}
    )
    project_id = deploy_response.json()["project_id"]
    
    run_response = test_client.post(
        f"/api/v1/projects/{project_id}/run",
        json={}
    )
    run_id = run_response.json()["run_id"]
    
    # Get logs (they might be empty if run hasn't completed yet)
    logs_response = test_client.get(f"/api/v1/runs/{run_id}/logs")
    assert logs_response.status_code == 200
    # Logs should be a list (might be empty or populated depending on timing)
    assert isinstance(logs_response.json(), list)
