"""Core Support Agent Implementation"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from agent.llm_factory import create_llm_client
from agent.memory import MemoryManager
from agent.mcp_client import MCPClient
from agent.identity import IdentityVerifier
from config.loader import Config

logger = logging.getLogger(__name__)


class SupportAgent:
    """Main Customer Support Agent powered by MCP and Ollama"""
    
    def __init__(self, config: Config):
        self.config = config
        # Create LLM client using factory (supports both Ollama and OpenAI)
        config_dict = config.model_dump()
        self.llm_client = create_llm_client(config_dict)
        self.memory_manager = MemoryManager(config.agent.context.model_dump())
        self.mcp_client = MCPClient(config.mcp)
        self.identity_verifier = IdentityVerifier(config.agent.identity_verification.model_dump())
        self.conversation_history: List[Dict[str, Any]] = []
        self.running = False
        
    async def start(self):
        """Initialize and start the agent"""
        logger.info("Starting Customer Support Agent...")
        
        # Initialize MCP connections
        await self.mcp_client.connect()
        logger.info("MCP connections established")
        
        # Initialize memory
        await self.memory_manager.initialize()
        logger.info("Memory manager initialized")
        
        # Verify LLM connection
        await self.llm_client.verify_connection()
        logger.info("LLM connection verified")
        
        self.running = True
        logger.info("Agent started successfully")
    
    async def run(self):
        """Main agent loop"""
        logger.info("Agent is running. Use process_message() to interact.")
        # Keep the agent running
        while self.running:
            await asyncio.sleep(1)
    
    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a customer message and return a response
        
        Args:
            message: Customer message
            user_id: Optional user identifier
            channel: Optional channel identifier (e.g., 'slack', 'web', 'email')
            metadata: Optional metadata (e.g., order_number, email, ticket_id)
        
        Returns:
            Agent response
        """
        try:
            # Verify identity if required
            if self.config.agent.identity_verification.required and metadata:
                verification_result = await self.identity_verifier.verify(metadata)
                if not verification_result["verified"]:
                    return "I need to verify your identity before accessing your information. Please provide your order number, email, or ticket ID."
            
            # Retrieve context from memory
            context = await self.memory_manager.get_context(
                user_id=user_id,
                channel=channel,
                limit=self.config.agent.context.max_history
            )
            
            # Build system prompt with available MCP tools
            system_prompt = self._build_system_prompt()
            
            # Get response from LLM with MCP tool access
            response = await self.llm_client.generate(
                message=message,
                system_prompt=system_prompt,
                context=context,
                tools=self.mcp_client.get_available_tools(),
                tool_executor=self._execute_tool
            )
            
            # Store conversation in memory
            await self.memory_manager.store_interaction(
                user_id=user_id,
                channel=channel,
                message=message,
                response=response,
                metadata=metadata
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "channel": channel,
                "message": message,
                "response": response,
                "metadata": metadata
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I apologize, but I encountered an error processing your request. Please try again or contact support."
    
    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute an MCP tool"""
        try:
            result = await self.mcp_client.call_tool(tool_name, parameters)
            logger.debug(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with available tools"""
        base_prompt = self.config.agent.system_prompt
        
        # Add available tools information
        tools_info = self.mcp_client.get_tools_description()
        if tools_info:
            base_prompt += f"\n\nAvailable tools:\n{tools_info}"
        
        return base_prompt
    
    async def stop(self):
        """Stop the agent"""
        logger.info("Stopping agent...")
        self.running = False
        await self.mcp_client.disconnect()
        await self.memory_manager.close()
        logger.info("Agent stopped")

