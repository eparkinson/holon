"""
Tests for CLI commands.
"""

import pytest
from typer.testing import CliRunner

from holon.cli import app


runner = CliRunner()


def test_version_command():
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Holon version" in result.stdout


def test_deploy_command_with_valid_file():
    """Test deploy command with a valid agent file."""
    result = runner.invoke(app, ["deploy", "test/samples/01_echo/echo.md"])
    assert result.exit_code == 0
    assert "Deploying agent from:" in result.stdout
    assert "✓ Parsed agent: echo" in result.stdout


def test_deploy_command_with_invalid_file():
    """Test deploy command with a non-existent file."""
    result = runner.invoke(app, ["deploy", "nonexistent.md"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout
