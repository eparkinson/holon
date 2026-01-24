"""
Utility functions for environment variable and API key management.
"""

import os
from pathlib import Path
from typing import Dict, Optional

import litellm
import yaml

# Mapping of provider names to environment variable names
PROVIDER_TO_ENV_VAR = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}


def get_required_api_key_for_model(model: str) -> Optional[str]:
    """
    Determine which API key environment variable is required for a given model.

    Args:
        model: The model name (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet-20241022')

    Returns:
        The name of the required environment variable (e.g., 'OPENAI_API_KEY') or None if unknown
    """
    try:
        # Use litellm to determine the provider
        _, provider, _, _ = litellm.get_llm_provider(model)

        # Map provider to environment variable
        return PROVIDER_TO_ENV_VAR.get(provider)
    except Exception:
        # If we can't determine the provider, return None
        return None


def load_env_from_yaml(env_file: str) -> Dict[str, str]:
    """
    Load environment variables from a YAML file.

    Args:
        env_file: Path to the YAML file containing environment variables

    Returns:
        Dictionary of environment variable names to values

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not valid YAML or doesn't contain a dictionary
    """
    file_path = Path(env_file)

    if not file_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_file}")

    with open(file_path, "r") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in environment file: {e}")

    if not isinstance(data, dict):
        raise ValueError("Environment file must contain a YAML dictionary")

    # Convert all values to strings
    return {k: str(v) for k, v in data.items()}


def apply_env_overrides(env_overrides: Dict[str, str]) -> None:
    """
    Apply environment variable overrides to the current process environment.
    Values from env_overrides take precedence over existing environment variables.

    Args:
        env_overrides: Dictionary of environment variable names to values
    """
    for key, value in env_overrides.items():
        os.environ[key] = value


def validate_api_key(model: str, env_overrides: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Validate that the required API key for a model is available.

    Args:
        model: The model name
        env_overrides: Optional dictionary of environment variable overrides

    Returns:
        None if the API key is available, or an error message if missing
    """
    required_key = get_required_api_key_for_model(model)

    # If we can't determine the required key, assume it's okay
    if required_key is None:
        return None

    # Check in overrides first, then in environment
    if env_overrides and required_key in env_overrides:
        return None

    if required_key in os.environ and os.environ[required_key]:
        return None

    # API key is missing
    return (
        f"Missing required API key: {required_key}\n"
        f"The model '{model}' requires the {required_key} environment variable to be set.\n"
        f"You can either:\n"
        f"  1. Set it as an environment variable: export {required_key}=your-api-key\n"
        f"  2. Use the --env option: holon test --env secrets.yaml"
    )
