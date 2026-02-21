"""Configuration Loader"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OllamaConfig(BaseModel):
    base_url: str
    model: str
    timeout: int = 300
    temperature: float = 0.7
    max_tokens: int = 2048


class OpenAIConfig(BaseModel):
    api_key: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 300


class VertexAIConfig(BaseModel):
    credentials_path: Optional[str] = None  # Path to service account JSON file
    project_id: Optional[str] = None
    location: str = "us-central1"
    model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 300


class LLMConfig(BaseModel):
    provider: str = "ollama"  # "ollama", "openai", or "vertexai"


class IdentityVerificationConfig(BaseModel):
    required: bool = True
    methods: list = ["order_number", "email", "ticket_id"]


class ContextConfig(BaseModel):
    max_history: int = 50
    persist_across_sessions: bool = True
    memory_backend: str = "postgres"


class AgentConfig(BaseModel):
    name: str
    system_prompt: str
    identity_verification: IdentityVerificationConfig
    context: ContextConfig


class Config(BaseModel):
    ollama: Optional[OllamaConfig] = None
    openai: Optional[OpenAIConfig] = None
    vertexai: Optional[VertexAIConfig] = None
    llm: Optional[LLMConfig] = None
    mcp: Dict[str, Any]
    integrations: Dict[str, Any]
    agent: AgentConfig
    security: Dict[str, Any] = {}
    logging: Dict[str, Any] = {}


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file (defaults to config/config.yaml)
    
    Returns:
        Config object
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please copy config/config.example.yaml to config/config.yaml and configure it."
        )
    
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    
    # Replace environment variables
    config_dict = _replace_env_vars(config_dict)
    
    # Validate and create Config object
    try:
        config = Config(**config_dict)
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def _replace_env_vars(obj: Any) -> Any:
    """Recursively replace ${VAR} with environment variables"""
    if isinstance(obj, dict):
        return {k: _replace_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        var_name = obj[2:-1]
        return os.getenv(var_name, obj)
    return obj

