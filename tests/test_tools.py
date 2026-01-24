"""
Tests for the Tool interface and registry.
"""

import pytest

from holon.tools import Tool, ToolRegistry


class MockCalculatorTool(Tool):
    """Mock calculator tool for testing."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic arithmetic operations"
        )
    
    def get_function_definition(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First operand"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second operand"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    
    def execute(self, operation: str, a: float, b: float) -> float:
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")


def test_tool_registration():
    """Test registering a tool in the registry."""
    registry = ToolRegistry()
    tool = MockCalculatorTool()
    
    registry.register(tool)
    
    assert registry.get("calculator") is not None
    assert registry.get("calculator").name == "calculator"


def test_tool_execution():
    """Test executing a tool through the registry."""
    registry = ToolRegistry()
    tool = MockCalculatorTool()
    registry.register(tool)
    
    result = registry.execute("calculator", operation="add", a=5, b=3)
    assert result == 8
    
    result = registry.execute("calculator", operation="multiply", a=4, b=2)
    assert result == 8


def test_tool_not_found():
    """Test that executing a non-existent tool raises ValueError."""
    registry = ToolRegistry()
    
    with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
        registry.execute("nonexistent", foo="bar")


def test_get_function_definitions():
    """Test getting function definitions for tools."""
    registry = ToolRegistry()
    tool = MockCalculatorTool()
    registry.register(tool)
    
    # Get definitions for specific tools
    definitions = registry.get_function_definitions(["calculator"])
    
    assert len(definitions) == 1
    assert definitions[0]["type"] == "function"
    assert definitions[0]["function"]["name"] == "calculator"
    assert definitions[0]["function"]["description"] == "Perform basic arithmetic operations"
    assert "parameters" in definitions[0]["function"]


def test_get_all_function_definitions():
    """Test getting function definitions for all registered tools."""
    registry = ToolRegistry()
    
    tool1 = MockCalculatorTool()
    registry.register(tool1)
    
    # Register another mock tool
    class MockWeatherTool(Tool):
        def __init__(self):
            super().__init__("weather", "Get weather information")
        
        def get_function_definition(self):
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        
        def execute(self, location: str):
            return f"Weather in {location}: Sunny"
    
    tool2 = MockWeatherTool()
    registry.register(tool2)
    
    # Get all definitions
    definitions = registry.get_function_definitions()
    
    assert len(definitions) == 2
    tool_names = {d["function"]["name"] for d in definitions}
    assert "calculator" in tool_names
    assert "weather" in tool_names


def test_builtin_web_search_tool():
    """Test the built-in web search tool."""
    from holon.builtin_tools import WebSearchTool
    
    tool = WebSearchTool()
    
    assert tool.name == "web_search"
    assert tool.description == "Search the web for information"
    
    # Test function definition
    definition = tool.get_function_definition()
    assert definition["name"] == "web_search"
    assert "query" in definition["parameters"]["properties"]
    
    # Test execution (placeholder)
    result = tool.execute(query="test query")
    assert "test query" in result
    assert "Placeholder" in result
