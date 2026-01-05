"""Holon CLI - Command-line interface for the Holon Agent Orchestration Engine."""

import yaml
from pathlib import Path

def _load_version():
    """Load version from conf.yaml."""
    conf_path = Path(__file__).parent.parent.parent / "conf.yaml"
    try:
        with open(conf_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("version", "0.1.0")
    except Exception:
        return "0.1.0"

__version__ = _load_version()
