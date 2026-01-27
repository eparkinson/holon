"""
Tests for the HTTP API server.
"""

import pytest
from pathlib import Path

# Try to import FastAPI dependencies
try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    from holon.server import create_server


# Get the repository root (two levels up from this file)
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "tests" / "samples"


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_server_initialization():
    """Test server initialization with sample definitions."""
    server = create_server(str(SAMPLES_DIR))
    
    # Check that agents were loaded
    assert len(server.agents) > 0
    
    # Check that at least one network was loaded
    assert len(server.networks) >= 1


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_health_endpoint():
    """Test health check endpoint."""
    server = create_server(str(SAMPLES_DIR))
    client = TestClient(server.app)
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "agents" in data
    assert "networks" in data
    assert isinstance(data["agents"], list)
    assert isinstance(data["networks"], list)


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_list_agents_endpoint():
    """Test list agents endpoint."""
    server = create_server(str(SAMPLES_DIR))
    client = TestClient(server.app)
    
    response = client.get("/agents")
    assert response.status_code == 200
    
    data = response.json()
    assert "agents" in data
    assert isinstance(data["agents"], list)
    
    # Check that each agent has required fields
    for agent in data["agents"]:
        assert "id" in agent
        assert "model" in agent
        assert "tools" in agent


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_list_networks_endpoint():
    """Test list networks endpoint."""
    server = create_server(str(SAMPLES_DIR))
    client = TestClient(server.app)
    
    response = client.get("/networks")
    assert response.status_code == 200
    
    data = response.json()
    assert "networks" in data
    assert isinstance(data["networks"], list)
    
    # Check that each network has required fields
    for network in data["networks"]:
        assert "id" in network
        assert "execution_mode" in network
        assert "agents" in network


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_chat_endpoint_not_found():
    """Test chat endpoint with non-existent agent."""
    server = create_server(str(SAMPLES_DIR))
    client = TestClient(server.app)
    
    response = client.post(
        "/agents/nonexistent/chat",
        json={"message": "Hello"}
    )
    assert response.status_code == 404


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_network_endpoint_not_found():
    """Test network execution endpoint with non-existent network."""
    server = create_server(str(SAMPLES_DIR))
    client = TestClient(server.app)
    
    response = client.post(
        "/networks/nonexistent/execute",
        json={"input": "Test input"}
    )
    assert response.status_code == 404


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_webhook_endpoint_not_found():
    """Test webhook endpoint with non-existent agent."""
    server = create_server(str(SAMPLES_DIR))
    client = TestClient(server.app)
    
    response = client.post(
        "/webhook/nonexistent",
        json={"message": "Webhook test"}
    )
    assert response.status_code == 404
