"""
Parser module to extract YAML frontmatter and Markdown body from .md files.
"""

import frontmatter
from pathlib import Path
from typing import Union

from .models import AgentConfig, AgentDefinition


class Parser:
    """Parser for Holon agent markdown definitions."""
    
    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> AgentDefinition:
        """
        Parse a markdown file containing agent definition.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            AgentDefinition object containing config and prompt
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the frontmatter is invalid or missing required fields
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Agent definition file not found: {file_path}")
        
        # Parse the frontmatter
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract metadata and validate
        try:
            config = AgentConfig(**post.metadata)
        except Exception as e:
            raise ValueError(f"Invalid agent configuration in {file_path}: {e}")
        
        # Extract markdown body as the system prompt
        prompt = post.content.strip()
        
        if not prompt:
            raise ValueError(f"Agent definition must contain a prompt body in {file_path}")
        
        return AgentDefinition(
            config=config,
            prompt=prompt,
            source_file=str(file_path.absolute())
        )
    
    @staticmethod
    def parse_string(content: str) -> AgentDefinition:
        """
        Parse a markdown string containing agent definition.
        
        Args:
            content: Markdown content with YAML frontmatter
            
        Returns:
            AgentDefinition object containing config and prompt
            
        Raises:
            ValueError: If the frontmatter is invalid or missing required fields
        """
        post = frontmatter.loads(content)
        
        try:
            config = AgentConfig(**post.metadata)
        except Exception as e:
            raise ValueError(f"Invalid agent configuration: {e}")
        
        prompt = post.content.strip()
        
        if not prompt:
            raise ValueError("Agent definition must contain a prompt body")
        
        return AgentDefinition(
            config=config,
            prompt=prompt
        )
