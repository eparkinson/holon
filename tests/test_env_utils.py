"""
Tests for environment utilities.
"""

import os
import tempfile
from pathlib import Path

import pytest

from holon.env_utils import (
    apply_env_overrides,
    get_required_api_key_for_model,
    load_env_from_yaml,
    validate_api_key,
)


class TestGetRequiredApiKey:
    """Tests for get_required_api_key_for_model function."""
    
    def test_openai_model(self):
        """Test that OpenAI models require OPENAI_API_KEY."""
        assert get_required_api_key_for_model("gpt-4o-mini") == "OPENAI_API_KEY"
        assert get_required_api_key_for_model("gpt-4o") == "OPENAI_API_KEY"
        assert get_required_api_key_for_model("gpt-3.5-turbo") == "OPENAI_API_KEY"
    
    def test_anthropic_model(self):
        """Test that Anthropic models require ANTHROPIC_API_KEY."""
        assert get_required_api_key_for_model("claude-3-5-sonnet-20241022") == "ANTHROPIC_API_KEY"
    
    def test_gemini_model(self):
        """Test that Gemini models require GOOGLE_API_KEY."""
        assert get_required_api_key_for_model("gemini/gemini-1.5-pro") == "GOOGLE_API_KEY"
    
    def test_perplexity_model(self):
        """Test that Perplexity models require PERPLEXITY_API_KEY."""
        assert get_required_api_key_for_model("perplexity/llama-3.1-sonar-small-128k-online") == "PERPLEXITY_API_KEY"


class TestLoadEnvFromYaml:
    """Tests for load_env_from_yaml function."""
    
    def test_load_valid_yaml(self):
        """Test loading a valid YAML file with environment variables."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("OPENAI_API_KEY: sk-test123\n")
            f.write("ANTHROPIC_API_KEY: sk-ant-test456\n")
            f.flush()
            temp_file = f.name
        
        try:
            result = load_env_from_yaml(temp_file)
            assert result == {
                "OPENAI_API_KEY": "sk-test123",
                "ANTHROPIC_API_KEY": "sk-ant-test456"
            }
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_env_from_yaml("nonexistent.yaml")
    
    def test_load_invalid_yaml(self):
        """Test that loading invalid YAML raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: syntax:\n")
            f.flush()
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid YAML"):
                load_env_from_yaml(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_non_dict_yaml(self):
        """Test that loading YAML that's not a dict raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- item1\n- item2\n")
            f.flush()
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain a YAML dictionary"):
                load_env_from_yaml(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_converts_values_to_strings(self):
        """Test that all values are converted to strings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("NUMBER: 123\n")
            f.write("BOOLEAN: true\n")
            f.flush()
            temp_file = f.name
        
        try:
            result = load_env_from_yaml(temp_file)
            assert result == {
                "NUMBER": "123",
                "BOOLEAN": "True"
            }
        finally:
            os.unlink(temp_file)


class TestApplyEnvOverrides:
    """Tests for apply_env_overrides function."""
    
    def test_apply_overrides(self):
        """Test that overrides are applied to environment."""
        # Save original values
        original_test_key = os.environ.get("TEST_KEY_12345")
        
        try:
            # Apply overrides
            apply_env_overrides({"TEST_KEY_12345": "test_value"})
            
            # Verify it's set
            assert os.environ.get("TEST_KEY_12345") == "test_value"
        finally:
            # Restore original value
            if original_test_key is None:
                os.environ.pop("TEST_KEY_12345", None)
            else:
                os.environ["TEST_KEY_12345"] = original_test_key
    
    def test_overrides_existing_values(self):
        """Test that overrides replace existing environment values."""
        # Save original value
        original_test_key = os.environ.get("TEST_KEY_67890")
        
        try:
            # Set an initial value
            os.environ["TEST_KEY_67890"] = "old_value"
            
            # Apply override
            apply_env_overrides({"TEST_KEY_67890": "new_value"})
            
            # Verify it's updated
            assert os.environ.get("TEST_KEY_67890") == "new_value"
        finally:
            # Restore original value
            if original_test_key is None:
                os.environ.pop("TEST_KEY_67890", None)
            else:
                os.environ["TEST_KEY_67890"] = original_test_key


class TestValidateApiKey:
    """Tests for validate_api_key function."""
    
    def test_valid_key_in_environment(self):
        """Test that validation passes when key is in environment."""
        # Save original value
        original_key = os.environ.get("OPENAI_API_KEY")
        
        try:
            os.environ["OPENAI_API_KEY"] = "sk-test123"
            result = validate_api_key("gpt-4o-mini")
            assert result is None
        finally:
            # Restore original value
            if original_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = original_key
    
    def test_valid_key_in_overrides(self):
        """Test that validation passes when key is in overrides."""
        # Save original value
        original_key = os.environ.get("OPENAI_API_KEY")
        
        try:
            # Make sure it's not in environment
            os.environ.pop("OPENAI_API_KEY", None)
            
            # But provide it in overrides
            result = validate_api_key("gpt-4o-mini", {"OPENAI_API_KEY": "sk-test123"})
            assert result is None
        finally:
            # Restore original value
            if original_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = original_key
    
    def test_missing_key(self):
        """Test that validation fails when key is missing."""
        # Save original value
        original_key = os.environ.get("OPENAI_API_KEY")
        
        try:
            # Make sure it's not in environment
            os.environ.pop("OPENAI_API_KEY", None)
            
            result = validate_api_key("gpt-4o-mini")
            assert result is not None
            assert "OPENAI_API_KEY" in result
            assert "Missing required API key" in result
        finally:
            # Restore original value
            if original_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = original_key
    
    def test_unknown_model(self):
        """Test that validation passes for unknown models."""
        # For models we can't determine the provider for, we shouldn't fail
        result = validate_api_key("unknown-model-12345")
        assert result is None
    
    def test_override_takes_precedence(self):
        """Test that overrides take precedence over environment."""
        # Save original value
        original_key = os.environ.get("OPENAI_API_KEY")
        
        try:
            # Set environment to empty
            os.environ["OPENAI_API_KEY"] = ""
            
            # But provide it in overrides
            result = validate_api_key("gpt-4o-mini", {"OPENAI_API_KEY": "sk-test123"})
            assert result is None
        finally:
            # Restore original value
            if original_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = original_key
