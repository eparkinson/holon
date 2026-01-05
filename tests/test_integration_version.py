"""Integration test for holon --version command.

This test starts the engine and invokes the holon --version command line
to verify that the version information is correctly displayed for both
CLI and engine components.
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


def test_holon_version_integration():
    """Test that holon --version displays both CLI and engine versions."""
    # Get the root directory
    root_dir = Path(__file__).parent.parent
    engine_dir = root_dir / "engine"
    cli_dir = root_dir / "cli"

    # Start the engine server in the background
    env = os.environ.copy()
    env["PYTHONPATH"] = str(engine_dir / "src")

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
        # Wait for the engine to start (give it up to 10 seconds)
        max_wait = 10
        for _ in range(max_wait * 2):  # Check every 0.5 seconds
            time.sleep(0.5)
            try:
                response = httpx.get("http://127.0.0.1:8000/health", timeout=1.0)
                if response.status_code == 200:
                    break
            except (httpx.ConnectError, httpx.TimeoutException):
                continue
        else:
            # Engine didn't start in time
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

        # Run the holon --version command
        env = os.environ.copy()
        env["PYTHONPATH"] = str(cli_dir / "src")

        result = subprocess.run(
            [sys.executable, "-m", "holon_cli.cli", "--version"],
            cwd=str(cli_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Verify the output
        assert (
            result.returncode == 0
        ), f"Command failed with code {result.returncode}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

        output = result.stdout

        # Check that both versions are displayed
        assert "Holon CLI" in output, f"CLI version not in output: {output}"
        assert "0.1.0" in output, f"Version 0.1.0 not in output: {output}"
        assert "Holon Engine" in output, f"Engine version not in output: {output}"

        # The output should contain two version lines
        lines = [line for line in output.split("\n") if line.strip()]
        assert (
            len(lines) >= 2
        ), f"Expected at least 2 lines in output, got {len(lines)}: {output}"

        print(f"✓ Integration test passed!")
        print(f"Output:\n{output}")

    finally:
        # Clean up: Stop the engine server
        if os.name != "nt":
            # On Unix, kill the entire process group
            os.killpg(os.getpgid(engine_process.pid), signal.SIGTERM)
        else:
            # On Windows, just terminate the process
            engine_process.terminate()

        try:
            engine_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            engine_process.kill()
            engine_process.wait()


if __name__ == "__main__":
    test_holon_version_integration()
