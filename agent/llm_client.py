"""Ollama LLM Client"""

import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
import httpx

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama locally"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.2")
        self.timeout = config.get("timeout", 300)
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def verify_connection(self):
        """Verify Ollama is accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            logger.info(f"Connected to Ollama at {self.base_url}")
        except httpx.ConnectError as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please ensure Ollama is running. You can start it with: ollama serve"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            raise
    
    async def generate(
        self,
        message: str,
        system_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Awaitable[Any]]] = None
    ) -> str:
        """
        Generate a response using Ollama
        
        Args:
            message: User message
            system_prompt: System prompt
            context: Conversation history
            tools: Available MCP tools
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
        
        # Prepare request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            }
        }
        
        try:
            # Try /api/chat endpoint first (newer Ollama versions)
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "")
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Fallback to /api/generate for older Ollama versions
                    logger.warning(f"/api/chat not found (404), trying /api/generate fallback")
                    assistant_message = await self._generate_legacy(payload)
                else:
                    raise
            except httpx.ConnectError as e:
                error_msg = (
                    f"Cannot connect to Ollama at {self.base_url}. "
                    f"Please ensure Ollama is running. Error: {e}"
                )
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e
            
            # If tools are available, check if the model wants to use them
            # This is a simplified version - in practice, you'd parse tool calls from the response
            if tools and tool_executor:
                assistant_message = await self._handle_tool_calls(
                    assistant_message, tools, tool_executor
                )
            
            return assistant_message
            
        except (ConnectionError, httpx.HTTPStatusError) as e:
            # Re-raise connection and HTTP errors as-is
            raise
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def _generate_legacy(self, payload: Dict[str, Any]) -> str:
        """
        Fallback method for older Ollama versions that use /api/generate
        Converts chat-style messages to a single prompt
        """
        # Convert messages to a single prompt for legacy API
        prompt_parts = []
        for msg in payload.get("messages", []):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n".join(prompt_parts)
        
        # Prepare legacy payload
        legacy_payload = {
            "model": payload["model"],
            "prompt": prompt,
            "stream": False,
            "options": payload.get("options", {})
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json=legacy_payload
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    async def _handle_tool_calls(
        self,
        response: str,
        tools: List[Dict[str, Any]],
        tool_executor: Callable[[str, Dict[str, Any]], Awaitable[Any]]
    ) -> str:
        """
        Handle tool calls in the response
        This is a simplified implementation - in practice, you'd use structured outputs
        """
        # In a real implementation, you'd parse tool calls from the LLM response
        # For now, this is a placeholder that would be enhanced with function calling
        return response
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

