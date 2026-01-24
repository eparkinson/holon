"""
Tool interface for Holon agents.

Supports both:
- Holon-side tools: Executed by the runtime on behalf of the agent
- Model-side internal tools: Native tools provided by the LLM provider
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Tool(ABC):
    """
    Base class for Holon tools.
    
    Tools can be executed locally by the runtime or passed to the LLM
    as function definitions for native tool calling.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a tool.
        
        Args:
            name: Unique identifier for the tool
            description: Human-readable description of what the tool does
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_function_definition(self) -> Dict[str, Any]:
        """
        Get the OpenAI-compatible function definition for this tool.
        
        Returns:
            Dict containing the function definition with name, description, and parameters
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the given arguments.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Result of tool execution
        """
        pass


class ToolRegistry:
    """
    Registry for managing available tools.
    
    The registry maps tool names to tool instances and provides
    methods for looking up and executing tools.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            Tool instance if found, None otherwise
        """
        return self._tools.get(name)
    
    def get_function_definitions(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get function definitions for specified tools or all registered tools.
        
        Args:
            tool_names: Optional list of tool names to get definitions for.
                       If None, returns definitions for all registered tools.
        
        Returns:
            List of function definitions compatible with LiteLLM's tools parameter
        """
        if tool_names is None:
            tool_names = list(self._tools.keys())
        
        definitions = []
        for name in tool_names:
            tool = self._tools.get(name)
            if tool:
                definitions.append({
                    "type": "function",
                    "function": tool.get_function_definition()
                })
        
        return definitions
    
    def execute(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name.
        
        Args:
            name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of tool execution
            
        Raises:
            ValueError: If the tool is not found
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        return tool.execute(**kwargs)


# Global tool registry instance
_global_registry = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.
    
    Returns:
        Global ToolRegistry instance
    """
    return _global_registry
