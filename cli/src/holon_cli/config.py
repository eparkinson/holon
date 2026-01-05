"""Configuration management for the Holon CLI."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from holon_cli.models import CLIConfig


def get_config_dir() -> Path:
    """Get the Holon configuration directory (~/.holon)."""
    config_dir = Path.home() / ".holon"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the CLI configuration file."""
    return get_config_dir() / "config.yaml"


def load_config() -> CLIConfig:
    """Load the CLI configuration from ~/.holon/config.yaml."""
    config_file = get_config_file()
    
    if not config_file.exists():
        # Return default configuration
        return CLIConfig()
    
    try:
        with open(config_file, "r") as f:
            data = yaml.safe_load(f) or {}
        return CLIConfig(**data)
    except (yaml.YAMLError, ValidationError) as e:
        # If config is invalid, return default and warn
        print(f"Warning: Invalid config file at {config_file}: {e}")
        return CLIConfig()


def save_config(config: CLIConfig) -> None:
    """Save the CLI configuration to ~/.holon/config.yaml."""
    config_file = get_config_file()
    
    with open(config_file, "w") as f:
        yaml.dump(config.model_dump(exclude_none=True), f, default_flow_style=False)


def set_config_value(key: str, value: str) -> None:
    """Set a configuration value."""
    config = load_config()
    
    if hasattr(config, key):
        setattr(config, key, value)
        save_config(config)
    else:
        raise ValueError(f"Unknown configuration key: {key}")


def get_config_value(key: str) -> Optional[str]:
    """Get a configuration value."""
    config = load_config()
    
    if hasattr(config, key):
        return getattr(config, key)
    else:
        raise ValueError(f"Unknown configuration key: {key}")
