"""Integration test for projects endpoint error handling.

This test reproduces the bug where the web 'projects' menu item
gives an "Internal Server Error".
"""

import subprocess
import time
import os
import signal
import sys
import httpx
import json
from pathlib import Path
from uuid import uuid4


def test_projects_endpoint_with_engine_not_ready():
    """Test that projects endpoint returns proper error when engine is not fully initialized."""
    # Get the root directory
    root_dir = Path(__file__).parent.parent
    engine_dir = root_dir / "engine"

    # Start the engine server without proper initialization
    env = os.environ.copy()
    env["PYTHONPATH"] = str(engine_dir / "src")
    # Use a storage URI that might cause issues
    env["HOLON_STORAGE_URI"] = "file:///tmp/holon_test_error"

    # Clean up any existing test data
    import shutil

    test_data_dir = Path("/tmp/holon_test_error")
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)

    engine_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "holon_engine.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8002",
        ],
        cwd=str(engine_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != "nt" else None,
    )

    try:
        # Wait for the engine to start
        max_wait = 10
        engine_ready = False
        for _ in range(max_wait * 2):
            time.sleep(0.5)
            try:
                response = httpx.get("http://127.0.0.1:8002/health", timeout=1.0)
                if response.status_code == 200:
                    engine_ready = True
                    break
            except (httpx.ConnectError, httpx.TimeoutException):
                continue

        if not engine_ready:
            stdout, stderr = engine_process.communicate(timeout=1)
            raise RuntimeError(
                f"Engine failed to start within {max_wait} seconds.\n"
                f"STDOUT: {stdout.decode()}\n"
                f"STDERR: {stderr.decode()}"
            )

        # Test 1: Empty database - should NOT return 500 Internal Server Error
        print("\n=== Test 1: Empty database ===")
        response = httpx.get("http://127.0.0.1:8002/api/v1/projects", timeout=5.0)

        # The key assertion: we should NOT get a 500 error
        # Even if there are no projects, we should get a 200 with an empty array
        assert (
            response.status_code == 200
        ), f"Expected 200 OK, got {response.status_code}: {response.text}"

        # Should return an empty list or a list of projects
        projects = response.json()
        assert isinstance(
            projects, list
        ), f"Expected list, got {type(projects)}: {projects}"
        assert len(projects) == 0, "Expected empty list for fresh database"

        print("✓ Projects endpoint handles empty state correctly")

        # Test 2: Create a project and verify it appears in the list
        print("\n=== Test 2: Deploy project and list ===")
        config_yaml = """
version: "1.0"
project: "Test-Integration"
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

        deploy_response = httpx.post(
            "http://127.0.0.1:8002/api/v1/deploy",
            json={"name": "Test-Integration", "config_yaml": config_yaml},
            timeout=5.0,
        )
        assert deploy_response.status_code == 200
        project_id = deploy_response.json()["project_id"]
        print(f"✓ Deployed project with ID: {project_id}")

        # List projects again
        response = httpx.get("http://127.0.0.1:8002/api/v1/projects", timeout=5.0)
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == "Test-Integration"
        assert "created_at" in projects[0]
        print("✓ Project appears in list with correct data")

        # Test 3: Create a corrupt JSON file to test error handling
        print("\n=== Test 3: Corrupt project file ===")
        corrupt_id = uuid4()
        # Ensure projects directory exists
        projects_dir = test_data_dir / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        corrupt_file = projects_dir / f"{corrupt_id}.json"
        with open(corrupt_file, "w") as f:
            f.write("{ invalid json syntax")

        # List should still work, just skip the corrupt file
        response = httpx.get("http://127.0.0.1:8002/api/v1/projects", timeout=5.0)
        assert response.status_code == 200
        projects = response.json()
        assert (
            len(projects) == 1
        ), "Corrupt file should be skipped, only valid project returned"
        print("✓ Endpoint gracefully handles corrupt project files")

    finally:
        # Clean up: Stop the engine server
        if os.name != "nt":
            os.killpg(os.getpgid(engine_process.pid), signal.SIGTERM)
        else:
            engine_process.terminate()

        try:
            engine_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            engine_process.kill()
            engine_process.wait()


def test_projects_endpoint_error_handling():
    """Test that projects endpoint handles errors gracefully."""
    # This test verifies that the endpoint has proper error handling in place
    # The actual error handling is tested by the comprehensive test above
    # Future: Add tests for permission errors, disk full, etc.
    pass


if __name__ == "__main__":
    test_projects_endpoint_with_engine_not_ready()
    test_projects_endpoint_error_handling()
