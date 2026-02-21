"""LLM Client Factory - Supports Ollama, OpenAI, and Vertex AI (Gemini)"""

import logging
from typing import Dict, Any, Optional, Callable, Awaitable, List
from agent.llm_client import OllamaClient
from agent.openai_client import OpenAIClient
from agent.vertexai_client import VertexAIClient

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified interface for LLM clients (Ollama, OpenAI, or Vertex AI)"""
    
    def __init__(self, client):
        self._client = client
    
    async def verify_connection(self):
        """Verify LLM connection"""
        await self._client.verify_connection()
    
    async def generate(
        self,
        message: str,
        system_prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executor: Optional[Callable[[str, Dict[str, Any]], Awaitable[Any]]] = None
    ) -> str:
        """Generate a response"""
        return await self._client.generate(
            message=message,
            system_prompt=system_prompt,
            context=context,
            tools=tools,
            tool_executor=tool_executor
        )
    
    async def close(self):
        """Close the client"""
        await self._client.close()


def create_llm_client(config: Dict[str, Any], provider: Optional[str] = None) -> LLMClient:
    """
    Create an LLM client based on provider configuration
    
    Args:
        config: Configuration dictionary
        provider: Optional provider override ('ollama', 'openai', or 'vertexai')
                  If not provided, uses 'llm.provider' from config
    
    Returns:
        LLMClient instance
    """
    # Determine provider
    if provider:
        selected_provider = provider
    else:
        # Check for provider in config
        llm_config = config.get("llm", {})
        selected_provider = llm_config.get("provider", "ollama").lower()
    
    logger.info(f"Creating LLM client with provider: {selected_provider}")
    
    if selected_provider == "openai":
        # Get OpenAI config
        openai_config = config.get("openai", {})
        if not openai_config:
            raise ValueError(
                "OpenAI provider selected but 'openai' config not found. "
                "Please add 'openai' section to your config.yaml"
            )
        client = OpenAIClient(openai_config)
    elif selected_provider == "ollama":
        # Get Ollama config
        ollama_config = config.get("ollama", {})
        if not ollama_config:
            raise ValueError(
                "Ollama provider selected but 'ollama' config not found. "
                "Please add 'ollama' section to your config.yaml"
            )
        client = OllamaClient(ollama_config)
    elif selected_provider in ["vertexai", "vertex", "gemini"]:
        # Get Vertex AI config
        vertexai_config = config.get("vertexai", {})
        if not vertexai_config:
            raise ValueError(
                "Vertex AI provider selected but 'vertexai' config not found. "
                "Please add 'vertexai' section to your config.yaml"
            )
        client = VertexAIClient(vertexai_config)
    else:
        raise ValueError(
            f"Unknown LLM provider: {selected_provider}. "
            "Supported providers: 'ollama', 'openai', 'vertexai' (or 'gemini')"
        )
    
    return LLMClient(client)

