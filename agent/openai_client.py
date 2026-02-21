"""OpenAI LLM Client"""

import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self, config: Dict[str, Any]):
        import os
        # Try to get API key from config, then environment variable
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        print(f"API Key: {api_key}")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set 'api_key' in config.yaml under 'openai' section, "
                "or set OPENAI_API_KEY environment variable."
            )
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
        self.timeout = config.get("timeout", 300)
    
    async def verify_connection(self):
        """Verify OpenAI API is accessible"""
        try:
            # Test connection by listing models
            models = await self.client.models.list()
            logger.info(f"Connected to OpenAI API. Using model: {self.model}")
        except Exception as e:
            error_msg = f"Cannot connect to OpenAI API: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
    
    async def generate(
        self,
        message: str,
        system_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Awaitable[Any]]] = None
    ) -> str:
        """
        Generate a response using OpenAI
        
        Args:
            message: User message
            system_prompt: System prompt
            context: Conversation history
            tools: Available MCP tools (converted to OpenAI function format)
            tool_executor: Function to execute tools
        
        Returns:
            Generated response
        """
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add context
        if context:
            messages.extend(context)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Convert MCP tools to OpenAI function format if available
        functions = None
        if tools:
            functions = self._convert_tools_to_openai_format(tools)
        
        try:
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            
            if functions:
                request_params["tools"] = functions
                request_params["tool_choice"] = "auto"
            
            # Make API call
            response = await self.client.chat.completions.create(**request_params)
            
            assistant_message = response.choices[0].message
            
            # Handle tool calls if present
            if assistant_message.tool_calls and tool_executor:
                return await self._handle_tool_calls(
                    assistant_message, messages, functions, tool_executor
                )
            
            return assistant_message.content or ""
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            raise
    
    def _convert_tools_to_openai_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function calling format"""
        functions = []
        for tool in tools:
            # Extract tool information
            name = tool.get("name", "")
            description = tool.get("description", "")
            parameters = tool.get("parameters", {})
            
            functions.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            })
        
        return functions
    
    async def _handle_tool_calls(
        self,
        assistant_message,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        tool_executor: Callable[[str, Dict[str, Any]], Awaitable[Any]]
    ) -> str:
        """Handle tool calls from OpenAI response"""
        # Add assistant message with tool calls to conversation
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })
        
        # Execute tool calls
        import json
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            try:
                result = await tool_executor(function_name, function_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })
            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {e}")
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": f"Error: {str(e)}"
                })
        
        # Add tool results to messages
        messages.extend(tool_results)
        
        # Get final response from OpenAI
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content or ""
    
    async def close(self):
        """Close the OpenAI client"""
        # OpenAI client doesn't need explicit closing, but we keep this for consistency
        pass

