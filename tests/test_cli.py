"""
Tests for CLI commands.
"""

import tempfile
from pathlib import Path
from typer.testing import CliRunner

from holon.cli import app

runner = CliRunner()

# Get the repository root (two levels up from this file)
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "tests" / "samples"


def test_version_command():
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Holon version" in result.stdout


def test_deploy_command_with_valid_file():
    """Test deploy command with a valid agent file."""
    import shutil

    test_file = str(SAMPLES_DIR / "01_echo" / "echo.md")
    result = runner.invoke(app, ["deploy", test_file])

    # The command should parse the agent successfully
    assert "Deploying agent from:" in result.stdout
    assert "✓ Parsed agent: echo" in result.stdout

    # If Docker is not available, it should exit with code 1 and show an error
    # If Docker is available, it should attempt to build (exit code 0 or 1 depending on build success)
    if not shutil.which("docker"):
        assert result.exit_code == 1
        assert "Docker is not installed" in result.stdout
    # If Docker is available, we don't test the actual build here (would require Docker daemon)


def test_deploy_command_with_invalid_file():
    """Test deploy command with a non-existent file."""
    result = runner.invoke(app, ["deploy", "nonexistent.md"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout


def test_test_command_with_folder_single_file():
    """Test test command with a folder containing a single markdown file."""
    import os

    # Save original API key
    original_key = os.environ.get("OPENAI_API_KEY")

    try:
        # Set a dummy API key for testing
        os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"

        test_dir = str(SAMPLES_DIR / "01_echo")
        # Use input="exit\n" to immediately exit the interactive session
        result = runner.invoke(app, ["test", test_dir], input="exit\n")
        assert result.exit_code == 0
        assert "Using:" in result.stdout
        assert "echo.md" in result.stdout
    finally:
        # Restore original API key
        if original_key is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = original_key


def test_test_command_with_folder_multiple_files():
    """Test test command with a folder containing multiple markdown files."""
    test_dir = str(SAMPLES_DIR / "02_collaborators")
    result = runner.invoke(app, ["test", test_dir])
    assert result.exit_code == 1
    assert "Multiple markdown files found" in result.stdout
    assert "writer.md" in result.stdout or "researcher.md" in result.stdout


def test_test_command_with_folder_no_files():
    """Test test command with a folder containing no markdown files."""
    # Create a temporary directory with no .md files
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["test", tmpdir])
        assert result.exit_code == 1
        assert "No markdown files found in directory" in result.stdout


def test_test_command_with_env_file():
    """Test test command with --env parameter."""
    import os

    # Save original API key
    original_key = os.environ.get("OPENAI_API_KEY")

    try:
        # Remove API key from environment
        os.environ.pop("OPENAI_API_KEY", None)

        # Create a temporary env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as env_file:
            env_file.write("OPENAI_API_KEY: sk-test-key-123\n")
            env_file.flush()
            env_file_path = env_file.name

        try:
            test_dir = str(SAMPLES_DIR / "01_echo")
            result = runner.invoke(app, ["test", test_dir, "--env", env_file_path], input="exit\n")

            # Should succeed with the env file
            assert result.exit_code == 0
            assert "Loaded environment variables from:" in result.stdout
        finally:
            os.unlink(env_file_path)
    finally:
        # Restore original API key
        if original_key is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = original_key


def test_test_command_missing_api_key():
    """Test test command fails when required API key is missing."""
    import os

    # Save original API key
    original_key = os.environ.get("OPENAI_API_KEY")

    try:
        # Remove API key from environment
        os.environ.pop("OPENAI_API_KEY", None)

        test_dir = str(SAMPLES_DIR / "01_echo")
        result = runner.invoke(app, ["test", test_dir])

        # Should fail due to missing API key
        assert result.exit_code == 1
        assert "Missing required API key" in result.stdout
        assert "OPENAI_API_KEY" in result.stdout
    finally:
        # Restore original API key
        if original_key is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = original_key


def test_test_command_with_invalid_env_file():
    """Test test command with invalid --env file."""
    test_dir = str(SAMPLES_DIR / "01_echo")
    result = runner.invoke(app, ["test", test_dir, "--env", "nonexistent.yaml"])

    # Should fail due to missing env file
    assert result.exit_code == 1
    assert "Error:" in result.stdout
