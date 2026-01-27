"""
Parser module to extract YAML frontmatter and Markdown body from .md files.
"""

import frontmatter
from pathlib import Path
from typing import Union

from .models import AgentConfig, AgentDefinition, NetworkConfig, NetworkDefinition


class Parser:
    """Parser for Holon agent and network markdown definitions."""
    
    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Union[AgentDefinition, NetworkDefinition]:
        """
        Parse a markdown file containing agent or network definition.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            AgentDefinition or NetworkDefinition object depending on the type
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the frontmatter is invalid or missing required fields
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Definition file not found: {file_path}")
        
        # Parse the frontmatter
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Check if it's a network or agent
        definition_type = post.metadata.get('type', 'agent')
        
        if definition_type == 'network':
            # Parse as network
            try:
                config = NetworkConfig(**post.metadata)
            except Exception as e:
                raise ValueError(f"Invalid network configuration in {file_path}: {e}")
            
            # Extract markdown body as the network description
            description = post.content.strip()
            
            if not description:
                raise ValueError(f"Network definition must contain a description in {file_path}")
            
            return NetworkDefinition(
                config=config,
                description=description,
                source_file=str(file_path.absolute())
            )
        else:
            # Parse as agent
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
    def parse_string(content: str) -> Union[AgentDefinition, NetworkDefinition]:
        """
        Parse a markdown string containing agent or network definition.
        
        Args:
            content: Markdown content with YAML frontmatter
            
        Returns:
            AgentDefinition or NetworkDefinition object depending on the type
            
        Raises:
            ValueError: If the frontmatter is invalid or missing required fields
        """
        post = frontmatter.loads(content)
        
        # Check if it's a network or agent
        definition_type = post.metadata.get('type', 'agent')
        
        if definition_type == 'network':
            # Parse as network
            try:
                config = NetworkConfig(**post.metadata)
            except Exception as e:
                raise ValueError(f"Invalid network configuration: {e}")
            
            description = post.content.strip()
            
            if not description:
                raise ValueError("Network definition must contain a description")
            
            return NetworkDefinition(
                config=config,
                description=description
            )
        else:
            # Parse as agent
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
