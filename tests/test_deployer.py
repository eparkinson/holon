"""
Tests for the Deployer module.
"""

import tempfile
from pathlib import Path

import pytest

from holon.deployer import Deployer
from holon.parser import Parser


# Get the repository root (two levels up from this file)
REPO_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = REPO_ROOT / "tests" / "samples"


def test_build_context():
    """Test that build_context creates necessary files."""
    # Parse a test agent
    agent = Parser.parse_file(SAMPLES_DIR / "01_chat" / "chat.md")
    deployer = Deployer(agent, SAMPLES_DIR / "01_chat" / "chat.md")
    
    # Create a temporary build directory
    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir)
        
        # Build the context
        deployer.build_context(build_dir)
        
        # Check that all required files exist
        assert (build_dir / "agent.md").exists()
        assert (build_dir / "runtime_entrypoint.py").exists()
        assert (build_dir / "requirements.txt").exists()
        assert (build_dir / "Dockerfile").exists()
        assert (build_dir / "holon").exists()
        assert (build_dir / "holon").is_dir()


def test_requirements_file_content():
    """Test that requirements.txt contains necessary dependencies."""
    agent = Parser.parse_file(SAMPLES_DIR / "01_chat" / "chat.md")
    deployer = Deployer(agent, SAMPLES_DIR / "01_chat" / "chat.md")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir)
        deployer.build_context(build_dir)
        
        # Read requirements.txt
        requirements = (build_dir / "requirements.txt").read_text()
        
        # Check for essential dependencies
        assert "typer" in requirements
        assert "python-frontmatter" in requirements
        assert "pydantic" in requirements
        assert "litellm" in requirements
        assert "rich" in requirements


def test_dockerfile_exists():
    """Test that Dockerfile is created from template."""
    agent = Parser.parse_file(SAMPLES_DIR / "01_chat" / "chat.md")
    deployer = Deployer(agent, SAMPLES_DIR / "01_chat" / "chat.md")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir)
        deployer.build_context(build_dir)
        
        # Check Dockerfile exists and has content
        dockerfile = build_dir / "Dockerfile"
        assert dockerfile.exists()
        
        content = dockerfile.read_text()
        assert "FROM python:" in content
        assert "COPY agent.md" in content
        assert "CMD" in content


def test_holon_package_copied():
    """Test that holon package is copied to build context."""
    agent = Parser.parse_file(SAMPLES_DIR / "01_chat" / "chat.md")
    deployer = Deployer(agent, SAMPLES_DIR / "01_chat" / "chat.md")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir)
        deployer.build_context(build_dir)
        
        # Check that holon package is copied
        holon_dir = build_dir / "holon"
        assert holon_dir.exists()
        assert (holon_dir / "__init__.py").exists()
        assert (holon_dir / "parser.py").exists()
        assert (holon_dir / "runtime.py").exists()
        assert (holon_dir / "models.py").exists()
        assert (holon_dir / "tools.py").exists()
