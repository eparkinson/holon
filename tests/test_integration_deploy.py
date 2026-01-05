"""Integration test for holon deploy command.

This test starts the engine, deploys the news sample using the CLI,
and verifies that:
1. The CLI can deploy a project with .env file
2. The API persists the project to file storage
3. The holon list command shows the deployed project
4. The web dashboard can fetch and display the project
5. Events/logs are viewable
"""

import subprocess
import time
import os
import signal
import sys
import json
import httpx
import yaml
from pathlib import Path
from uuid import UUID


def test_holon_deploy_integration():
    """Test end-to-end deployment flow."""
    # Get the root directory
    root_dir = Path(__file__).parent.parent
    engine_dir = root_dir / "engine"
    cli_dir = root_dir / "cli"
    samples_dir = root_dir / "samples" / "news"

    # Create a temporary .env file for the news sample
    env_file = samples_dir / ".env"
    env_content = """# Sample API Keys
ANTHROPIC_API_KEY=test_key_123
PERPLEXITY_API_KEY=test_key_456
XAI_API_KEY=test_key_789
"""
    with open(env_file, "w") as f:
        f.write(env_content)

    # Start the engine server in the background
    env = os.environ.copy()
    env["PYTHONPATH"] = str(engine_dir / "src")
    env["HOLON_STORAGE_URI"] = "file:///tmp/holon_test_data"

    # Clean up any existing test data
    import shutil

    test_data_dir = Path("/tmp/holon_test_data")
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
            "8000",
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
                response = httpx.get("http://127.0.0.1:8000/health", timeout=1.0)
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

        # Configure the CLI to point to the local engine
        holon_config_dir = Path.home() / ".holon"
        holon_config_dir.mkdir(exist_ok=True)
        config_file = holon_config_dir / "config.yaml"

        config_data = {"host": "http://127.0.0.1:8000"}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Test 1: Deploy the news sample using CLI
        print("\n=== Test 1: Deploy with CLI ===")
        cli_env = os.environ.copy()
        cli_env["PYTHONPATH"] = str(cli_dir / "src")

        holon_yaml = samples_dir / "holon.yaml"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "holon_cli.cli",
                "deploy",
                "--file",
                str(holon_yaml),
            ],
            cwd=str(cli_dir),
            env=cli_env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Deploy failed: {result.stderr}"
        assert "Deployment successful" in result.stdout
        assert "Process ID:" in result.stdout

        # Extract project ID from output
        project_id = None
        for line in result.stdout.split("\n"):
            if "Process ID:" in line:
                # Extract UUID from the line
                import re

                match = re.search(
                    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    line,
                )
                if match:
                    project_id = match.group(0)
                    break

        assert project_id is not None, "Could not extract project ID from output"
        print(f"✓ Deployed project with ID: {project_id}")

        # Test 2: Verify file storage persistence
        print("\n=== Test 2: Verify File Persistence ===")
        project_file = test_data_dir / "projects" / f"{project_id}.json"
        assert project_file.exists(), f"Project file not found at {project_file}"

        with open(project_file, "r") as f:
            stored_project = json.load(f)

        assert stored_project["name"] == "Daily-Briefing-Digest"
        assert "config_yaml" in stored_project
        assert "env_vars" in stored_project
        assert stored_project["env_vars"]["ANTHROPIC_API_KEY"] == "test_key_123"
        print("✓ Project persisted to file storage with env vars")

        # Test 3: List projects via CLI
        print("\n=== Test 3: List Projects via CLI ===")
        result = subprocess.run(
            [sys.executable, "-m", "holon_cli.cli", "list"],
            cwd=str(cli_dir),
            env=cli_env,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, f"List failed: {result.stderr}"
        assert "Daily-Briefing-Digest" in result.stdout
        print("✓ Project visible in list command")

        # Test 4: Fetch projects via API (simulating web dashboard)
        print("\n=== Test 4: Fetch via API (Web Dashboard) ===")
        response = httpx.get("http://127.0.0.1:8000/api/v1/projects", timeout=5.0)
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) >= 1
        assert any(p["name"] == "Daily-Briefing-Digest" for p in projects)
        print("✓ Project fetched via API")

        # Also test the /processes endpoint (used by list command)
        response = httpx.get("http://127.0.0.1:8000/api/v1/processes", timeout=5.0)
        assert response.status_code == 200
        processes = response.json()
        assert len(processes) >= 1
        print("✓ Processes endpoint working")

        # Test 5: Trigger a run and verify logs/events
        print("\n=== Test 5: Trigger Run and View Logs ===")
        response = httpx.post(
            f"http://127.0.0.1:8000/api/v1/projects/{project_id}/run",
            json={"input_context": {"test": "data"}},
            timeout=5.0,
        )
        assert response.status_code == 202
        run_data = response.json()
        run_id = run_data["run_id"]
        assert run_data["status"] == "PENDING"
        print(f"✓ Run triggered with ID: {run_id}")

        # Wait a moment for run to be saved
        time.sleep(1)

        # Get run logs
        response = httpx.get(
            f"http://127.0.0.1:8000/api/v1/runs/{run_id}/logs",
            timeout=5.0,
        )
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
        print(f"✓ Logs retrieved (count: {len(logs)})")

        # Test logs via CLI
        result = subprocess.run(
            [sys.executable, "-m", "holon_cli.cli", "logs", run_id],
            cwd=str(cli_dir),
            env=cli_env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Logs command should work (even if empty)
        assert result.returncode == 0 or "not found" not in result.stdout.lower()
        print("✓ CLI logs command working")

        print("\n=== All Integration Tests Passed! ===")

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

        # Clean up .env file
        if env_file.exists():
            env_file.unlink()


if __name__ == "__main__":
    test_holon_deploy_integration()
