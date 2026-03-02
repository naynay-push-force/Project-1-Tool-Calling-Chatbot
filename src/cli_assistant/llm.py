import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import Config
from .tools.registry import registry

class LLMClient:
    def __init__(self, config: Config):
        self.config = config
        self.conversation_history: List[Dict[str, Any]] = []

        # Mock mode: lets the CLT run without any API access
        self.mock_mode = (self.config.model_name or "").lower() == "mock"

        if not self.mock_mode:
            self.client = AsyncOpenAI(api_key=config.openai_api_key)
        else:
            self.client = None
    
    async def chat(self, message: str) -> str:
        """Send a message and get a response, handling function calls"""

        if self.mock_mode:
            return await self._mock_chat(message)
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Get available tools
        available_tools = registry.get_openai_functions()
        
        # Call OpenAI
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=self.conversation_history,
            tools=available_tools if available_tools else None,
            tool_choice="auto" if available_tools else None,
            temperature=self.config.temperature
        )
        
        assistant_message = response.choices[0].message
        
        # Add assistant message to history
        self.conversation_history.append(assistant_message.model_dump())
        
        # Handle function calls
        if assistant_message.tool_calls:
            await self._handle_tool_calls(assistant_message.tool_calls)
            
            # Get final response after function calls
            final_response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self.conversation_history,
                temperature=self.config.temperature
            )
            
            final_message = final_response.choices[0].message
            self.conversation_history.append(final_message.model_dump())
            return final_message.content
        
        return assistant_message.content
    
    async def _handle_tool_calls(self, tool_calls) -> None:
        """Execute tool calls and add results to conversation"""
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            try:
                tool = registry.get_tool(tool_name)
                result = await tool.execute(**arguments)
                
                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result.model_dump())
                })
                
            except Exception as e:
                # Add error to conversation
                self.conversation_history.append({
                    "role": "tool", 
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps({"error": str(e)})
                })

    async def _mock_chat(self, message: str) -> str:
        """
        Offline mode (no OpenAI). Supports manual tool execution:
        /tool <tool_name> <json_args>

        Example:
        /tool calculator {"expression": "2+2"}
        """
        self.conversation_history.append({"role": "user", "content": message})

        # Manual tool execution
        if message.strip().startswith("/tool "):
            parts = message.strip().split(" ", 2)
            if len(parts) < 2:
                return "Usage: /tool <tool_name> <json_args>"

            tool_name = parts[1]
            raw_args = parts[2] if len(parts) == 3 else "{}"

            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError as e:
                return f"Invalid JSON args. Example: /tool {tool_name} {{\"x\": 1}}. Error: {e}"

            try:
                tool = registry.get_tool(tool_name)
                result = await tool.execute(**args)
                return f"[MOCK] Tool '{tool_name}' executed.\nResult: {result.model_dump()}"
            except Exception as e:
                return f"[MOCK] Tool '{tool_name}' failed: {e}"

        # Normal chat fallback in mock mode
        tools = registry.list_tools()
        tool_list = ", ".join(tools) if tools else "(no tools registered)"
        return (
            "[MOCK MODE]\n"
            f"Tools available: {tool_list}\n"
            "To run one: /tool <tool_name> <json_args>\n"
            'Example: /tool calculate {"expression":"2+2"}'
        )