
import subprocess
import time
import os
import sys
import json
import httpx
import pytest
import websockets
import shutil
import asyncio
import signal
from pathlib import Path

# Skip if websockets is not installed
try:
    import websockets
except ImportError:
    pytest.skip("websockets not installed", allow_module_level=True)

@pytest.mark.asyncio
async def test_ollama_integration():
    """Test end-to-end Ollama chat flow via Websockets."""
    # Get the root directory
    root_dir = Path(__file__).parent.parent
    engine_dir = root_dir / "engine"
    holon_yaml_path = root_dir / "tests" / "holon-yaml" / "ollama.yaml"

    # Start the engine server in the background
    env = os.environ.copy()
    env["PYTHONPATH"] = str(engine_dir / "src")
    env["HOLON_STORAGE_URI"] = "file:///tmp/holon_test_ollama_data"

    # Clean up any existing test data
    test_data_dir = Path("/tmp/holon_test_ollama_data")
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)

    # Start Engine
    engine_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "holon_engine.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",  # Use a different port to avoid conflicts
        ],
        cwd=str(engine_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != "nt" else None,
    )

    try:
        # Wait for the engine to start
        base_url = "http://127.0.0.1:8001"
        ws_url = "ws://127.0.0.1:8001"
        
        max_wait = 10
        engine_ready = False
        for _ in range(max_wait * 2):
            await asyncio.sleep(0.5)
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{base_url}/health", timeout=1.0)
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

        # 1. Deploy the project
        async with httpx.AsyncClient() as client:
            with open(holon_yaml_path, "r") as f:
                config_yaml = f.read()
            
            deploy_response = await client.post(
                f"{base_url}/api/v1/deploy",
                json={
                    "name": "Integration-Test-Ollama",
                    "config_yaml": config_yaml,
                },
                timeout=10.0
            )
            assert deploy_response.status_code == 200
            project_id = deploy_response.json()["project_id"]
            print(f"Deployed Project ID: {project_id}")

        # 2. Connect via Websocket
        # Note: The path is an assumption based on typical conventions, as it's not implemented yet
        ws_endpoint = f"{ws_url}/api/v1/projects/{project_id}/chat"
        
        print(f"Connecting to {ws_endpoint}...")
        async with websockets.connect(ws_endpoint) as websocket:
            # 3. Send a message
            message = {"message": "Why is the sky blue?"}
            await websocket.send(json.dumps(message))
            
            # 4. Receive response
            response = await websocket.recv()
            response_data = json.loads(response)
            
            print(f"Received: {response_data}")
            
            # Assertions
            assert "response" in response_data
            assert response_data["role"] == "assistant"
            # We don't verify the actual content heavily as it depends on the LLM
            assert len(response_data["response"]) > 0

    finally:
        # Teardown
        if engine_process:
            if os.name != "nt":
                os.killpg(os.getpgid(engine_process.pid), signal.SIGTERM)
            else:
                engine_process.terminate()
            engine_process.wait()
        
        if test_data_dir.exists():
            shutil.rmtree(test_data_dir)
