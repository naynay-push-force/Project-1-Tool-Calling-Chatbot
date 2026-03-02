from typing import Dict, Type, List, Any
from .base import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool instance"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name"""
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found")
        return self._tools[name]
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get all tools formatted for OpenAI API"""
        return [tool.to_openai_function() for tool in self._tools.values()]

# Global registry instance (singleton)
registry = ToolRegistry()