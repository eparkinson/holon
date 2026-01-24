"""
Tests for CLI commands.
"""

from pathlib import Path
from typer.testing import CliRunner

from holon.cli import app

runner = CliRunner()

# Get the repository root (two levels up from this file)
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "test" / "samples"


def test_version_command():
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Holon version" in result.stdout


def test_deploy_command_with_valid_file():
    """Test deploy command with a valid agent file."""
    test_file = str(SAMPLES_DIR / "01_echo" / "echo.md")
    result = runner.invoke(app, ["deploy", test_file])
    assert result.exit_code == 0
    assert "Deploying agent from:" in result.stdout
    assert "✓ Parsed agent: echo" in result.stdout


def test_deploy_command_with_invalid_file():
    """Test deploy command with a non-existent file."""
    result = runner.invoke(app, ["deploy", "nonexistent.md"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout


def test_test_command_with_folder_single_file():
    """Test test command with a folder containing a single markdown file."""
    test_dir = str(SAMPLES_DIR / "01_echo")
    # Use input="exit\n" to immediately exit the interactive session
    result = runner.invoke(app, ["test", test_dir], input="exit\n")
    assert result.exit_code == 0
    assert "Using:" in result.stdout
    assert "echo.md" in result.stdout


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
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, ["test", tmpdir])
        assert result.exit_code == 1
        assert "No markdown files found in directory" in result.stdout
