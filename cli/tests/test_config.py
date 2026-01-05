"""Tests for Holon CLI configuration management."""

import tempfile
from pathlib import Path

import pytest

from holon_cli.config import (
    get_config_dir,
    load_config,
    save_config,
    set_config_value,
    get_config_value,
)
from holon_cli.models import CLIConfig


def test_default_config():
    """Test that default config is returned when no config file exists."""
    config = CLIConfig()
    assert config.host == "http://localhost:8000"
    assert config.api_key is None
    assert config.default_project is None


def test_config_validation():
    """Test that config validation works."""
    # Valid config
    config = CLIConfig(host="http://example.com", api_key="test_key")
    assert config.host == "http://example.com"
    assert config.api_key == "test_key"


def test_save_and_load_config(tmp_path, monkeypatch):
    """Test saving and loading configuration."""
    # Mock config directory to use tmp_path
    def mock_get_config_dir():
        config_dir = tmp_path / ".holon"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    monkeypatch.setattr("holon_cli.config.get_config_dir", mock_get_config_dir)
    
    # Create and save config
    config = CLIConfig(
        host="http://test.example.com",
        api_key="test_api_key",
        default_project="test_project"
    )
    save_config(config)
    
    # Load and verify
    loaded_config = load_config()
    assert loaded_config.host == "http://test.example.com"
    assert loaded_config.api_key == "test_api_key"
    assert loaded_config.default_project == "test_project"


def test_set_and_get_config_value(tmp_path, monkeypatch):
    """Test setting and getting individual config values."""
    # Mock config directory to use tmp_path
    def mock_get_config_dir():
        config_dir = tmp_path / ".holon"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    monkeypatch.setattr("holon_cli.config.get_config_dir", mock_get_config_dir)
    
    # Set value
    set_config_value("host", "http://new-host.com")
    
    # Get value
    value = get_config_value("host")
    assert value == "http://new-host.com"


def test_set_invalid_config_key(tmp_path, monkeypatch):
    """Test that setting an invalid config key raises an error."""
    # Mock config directory to use tmp_path
    def mock_get_config_dir():
        config_dir = tmp_path / ".holon"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    monkeypatch.setattr("holon_cli.config.get_config_dir", mock_get_config_dir)
    
    with pytest.raises(ValueError, match="Unknown configuration key"):
        set_config_value("invalid_key", "value")


def test_get_invalid_config_key(tmp_path, monkeypatch):
    """Test that getting an invalid config key raises an error."""
    # Mock config directory to use tmp_path
    def mock_get_config_dir():
        config_dir = tmp_path / ".holon"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    monkeypatch.setattr("holon_cli.config.get_config_dir", mock_get_config_dir)
    
    with pytest.raises(ValueError, match="Unknown configuration key"):
        get_config_value("invalid_key")
