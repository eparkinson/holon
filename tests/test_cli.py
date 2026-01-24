"""
Tests for CLI commands.
"""

import pytest
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
