# src/cli_assistant/tools/weather.py
import aiohttp
from typing import Any, Dict
from .base import BaseTool, ToolResult

class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_weather"
    
    @property
    def description(self) -> str:
        return "Get current weather for a location"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string", 
                    "description": "City and state/country, e.g. 'San Francisco, CA'"
                }
            },
            "required": ["location"]
        }
    
    async def execute(self, location: str) -> ToolResult:
        # Mock implementation - in reality, call a weather API
        return ToolResult(
            success=True,
            result={
                "location": location,
                "temperature": 22,
                "condition": "Sunny",
                "humidity": 65
            }
        )