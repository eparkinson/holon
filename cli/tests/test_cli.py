"""Tests for the Holon CLI commands."""

from pathlib import Path
from typer.testing import CliRunner

from holon_cli.cli import app

runner = CliRunner()


def test_version_command():
    """Test that --version flag works."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Holon CLI" in result.stdout
    assert "0.1.0" in result.stdout


def test_help_command():
    """Test that help is displayed."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Holon CLI" in result.stdout
    assert "init" in result.stdout
    assert "deploy" in result.stdout
    assert "list" in result.stdout


def test_init_command_creates_files(tmp_path, monkeypatch):
    """Test that init command creates holon.yaml and .env.example."""
    # Change to tmp directory
    monkeypatch.chdir(tmp_path)
    
    result = runner.invoke(app, ["init", "--name", "test-project", "--path", str(tmp_path)])
    
    # Check command succeeded
    assert result.exit_code == 0
    
    # Check files were created
    holon_file = tmp_path / "holon.yaml"
    env_file = tmp_path / ".env.example"
    
    assert holon_file.exists()
    assert env_file.exists()
    
    # Check holon.yaml content
    content = holon_file.read_text()
    assert "test-project" in content
    assert "version: '1.0'" in content or 'version: "1.0"' in content


def test_deploy_command_validation_success(tmp_path):
    """Test that deploy command validates a correct config."""
    # Create a valid holon.yaml
    holon_file = tmp_path / "holon.yaml"
    holon_file.write_text("""
version: "1.0"
project: "test-project"
resources:
  - id: agent1
    provider: anthropic
    model: claude-3-5-sonnet
workflow:
  type: sequential
  steps:
    - id: step1
      agent: agent1
      instruction: "Do something"
""")
    
    # Run deploy with --dry-run (won't connect to engine)
    result = runner.invoke(app, ["deploy", str(holon_file), "--dry-run"])
    
    assert result.exit_code == 0
    assert "Configuration validated successfully" in result.stdout
    assert "test-project" in result.stdout


def test_deploy_command_validation_failure(tmp_path):
    """Test that deploy command catches invalid config."""
    # Create an invalid holon.yaml (missing required fields)
    holon_file = tmp_path / "holon.yaml"
    holon_file.write_text("""
version: "1.0"
# Missing project, resources, workflow
""")
    
    # Run deploy with --dry-run
    result = runner.invoke(app, ["deploy", str(holon_file), "--dry-run"])
    
    assert result.exit_code == 1
    assert "validation failed" in result.stdout.lower()


def test_config_show_command():
    """Test that config show command works."""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Configuration" in result.stdout


def test_config_set_get_commands(tmp_path, monkeypatch):
    """Test setting and getting config values."""
    # Mock config directory
    def mock_get_config_dir():
        config_dir = tmp_path / ".holon"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    import holon_cli.config
    monkeypatch.setattr(holon_cli.config, "get_config_dir", mock_get_config_dir)
    
    # Set a value
    result = runner.invoke(app, ["config", "set", "host", "http://test.example.com"])
    assert result.exit_code == 0
    assert "http://test.example.com" in result.stdout
    
    # Get the value back
    result = runner.invoke(app, ["config", "get", "host"])
    assert result.exit_code == 0
    assert "http://test.example.com" in result.stdout


def test_config_set_invalid_key(tmp_path, monkeypatch):
    """Test that setting an invalid config key fails."""
    # Mock config directory
    def mock_get_config_dir():
        config_dir = tmp_path / ".holon"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    import holon_cli.config
    monkeypatch.setattr(holon_cli.config, "get_config_dir", mock_get_config_dir)
    
    result = runner.invoke(app, ["config", "set", "invalid_key", "value"])
    assert result.exit_code == 1
    assert "Unknown configuration key" in result.stdout


def test_list_command_no_engine():
    """Test list command when engine is not available."""
    # This will fail to connect, but should handle gracefully
    result = runner.invoke(app, ["list"])
    # Should not crash, but show connection error
    assert "Could not connect" in result.stdout or result.exit_code == 0


def test_logs_command_no_engine():
    """Test logs command when engine is not available."""
    result = runner.invoke(app, ["logs", "test-process-id"])
    # Should handle connection error gracefully
    assert "Could not connect" in result.stdout or result.exit_code == 0


def test_event_command_validation():
    """Test event command requires process and event options."""
    result = runner.invoke(app, ["event"])
    assert result.exit_code != 0  # Should fail without required options


def test_stop_command():
    """Test stop command (will fail to connect but shouldn't crash)."""
    result = runner.invoke(app, ["stop", "test-process"])
    # Should handle connection error gracefully
    assert "Could not connect" in result.stdout or result.exit_code == 0


def test_delete_command_with_force():
    """Test delete command with force flag."""
    result = runner.invoke(app, ["delete", "test-process", "--force"])
    # Should handle connection error gracefully
    assert "Could not connect" in result.stdout or result.exit_code == 0
