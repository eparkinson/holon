"""
Deployment module for building and running containerized Holon agents.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from .models import AgentDefinition


class Deployer:
    """
    Handles building and running containerized Holon agents.
    """
    
    def __init__(self, agent: AgentDefinition, source_file: Path):
        """
        Initialize the deployer.
        
        Args:
            agent: AgentDefinition to deploy
            source_file: Path to the source markdown file
        """
        self.agent = agent
        self.source_file = source_file
    
    def build_context(self, build_dir: Path) -> None:
        """
        Create the Docker build context with all necessary files.
        
        Args:
            build_dir: Directory where build context will be created
        """
        # Create build directory if it doesn't exist
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy agent definition
        shutil.copy(self.source_file, build_dir / "agent.md")
        
        # Get the templates directory
        templates_dir = Path(__file__).parent / "templates"
        
        # Copy runtime entrypoint
        shutil.copy(
            templates_dir / "runtime_entrypoint.py",
            build_dir / "runtime_entrypoint.py"
        )
        
        # Copy holon package source
        holon_src = Path(__file__).parent
        holon_dest = build_dir / "holon"
        shutil.copytree(
            holon_src,
            holon_dest,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'templates')
        )
        
        # Create requirements.txt
        self._create_requirements_file(build_dir / "requirements.txt")
        
        # Create Dockerfile from template
        self._create_dockerfile(build_dir / "Dockerfile")
    
    def _create_requirements_file(self, output_path: Path) -> None:
        """
        Create requirements.txt with necessary dependencies.
        
        Args:
            output_path: Path where requirements.txt will be created
        """
        requirements = [
            "typer>=0.9.0",
            "python-frontmatter>=1.0.0",
            "pydantic>=2.0.0",
            "litellm>=1.0.0",
            "rich>=13.0.0",
        ]
        
        # Add tool-specific requirements based on agent config
        if self.agent.config.tools:
            # Add any tool-specific dependencies here in the future
            pass
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(requirements))
            f.write('\n')
    
    def _create_dockerfile(self, output_path: Path) -> None:
        """
        Create Dockerfile from template.
        
        Args:
            output_path: Path where Dockerfile will be created
        """
        templates_dir = Path(__file__).parent / "templates"
        template_path = templates_dir / "Dockerfile.template"
        
        # For now, just copy the template as-is
        # In the future, we could add template variable substitution
        shutil.copy(template_path, output_path)
    
    def build_image(self, build_dir: Path, tag: Optional[str] = None) -> str:
        """
        Build the Docker image.
        
        Args:
            build_dir: Directory containing the build context
            tag: Optional tag for the Docker image. If None, uses agent ID.
            
        Returns:
            The tag of the built image
            
        Raises:
            RuntimeError: If docker build fails
        """
        if tag is None:
            tag = f"holon-{self.agent.config.id}:latest"
        
        # Build the Docker image
        cmd = [
            "docker", "build",
            "-t", tag,
            str(build_dir)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Docker build failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
        
        return tag
    
    def run_container(
        self,
        image_tag: str,
        interactive: bool = True,
        env_vars: Optional[dict] = None
    ) -> subprocess.CompletedProcess:
        """
        Run the Docker container.
        
        Args:
            image_tag: Tag of the Docker image to run
            interactive: Whether to run in interactive mode
            env_vars: Optional environment variables to pass to container
            
        Returns:
            CompletedProcess object from subprocess.run
            
        Raises:
            RuntimeError: If docker run fails
        """
        cmd = ["docker", "run", "--rm"]
        
        # Add interactive flags if needed
        if interactive:
            cmd.extend(["-it"])
        
        # Add environment variables
        if env_vars:
            for key, value in env_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        # Pass through API keys from host environment
        api_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "PERPLEXITY_API_KEY",
            "GOOGLE_API_KEY",
        ]
        
        for key in api_keys:
            value = os.environ.get(key)
            if value:
                cmd.extend(["-e", f"{key}={value}"])
        
        # Add the image tag
        cmd.append(image_tag)
        
        # Run the container
        result = subprocess.run(cmd)
        
        return result
    
    def deploy(
        self,
        interactive: bool = True,
        cleanup: bool = True
    ) -> None:
        """
        Full deployment process: build and run the container.
        
        Args:
            interactive: Whether to run in interactive mode
            cleanup: Whether to clean up build directory after deployment
            
        Raises:
            RuntimeError: If deployment fails
        """
        # Create temporary build directory
        build_dir = Path(tempfile.mkdtemp(prefix="holon-build-"))
        
        try:
            # Build context
            self.build_context(build_dir)
            
            # Build image
            image_tag = self.build_image(build_dir)
            
            # Run container
            self.run_container(image_tag, interactive=interactive)
            
        finally:
            # Clean up build directory if requested
            if cleanup and build_dir.exists():
                shutil.rmtree(build_dir)
