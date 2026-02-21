"""MCP Client for connecting to MCP servers"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json
import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with MCP servers via HTTP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.connected = False
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def connect(self):
        """Connect to all configured MCP servers via HTTP"""
        logger.info("Connecting to MCP servers...")
        
        for server_config in self.config.get("servers", []):
            server_name = server_config["name"]
            server_url = server_config.get("url") or server_config.get("base_url")
            
            if not server_url:
                logger.warning(f"No URL configured for server {server_name}, skipping...")
                continue
            
            try:
                logger.info(f"Connecting to {server_name} at {server_url}...")
                
                # Test connection with health check
                try:
                    health_url = f"{server_url.rstrip('/')}/health"
                    response = await self.http_client.get(health_url)
                    if response.status_code == 200:
                        logger.info(f"✓ Connected to {server_name}")
                    else:
                        logger.warning(f"Health check failed for {server_name}: {response.status_code}")
                except Exception as e:
                    logger.warning(f"Health check failed for {server_name}: {e}")
                
                # Store server connection
                self.servers[server_name] = {
                    "config": server_config,
                    "url": server_url,
                    "connected": True
                }
                
                # Discover tools from this server
                await self._discover_tools(server_name)
                
            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
        
        self.connected = True
        logger.info(f"Connected to {len(self.servers)} MCP server(s)")
    
    async def _discover_tools(self, server_name: str):
        """Discover available tools from an MCP server via HTTP"""
        server_info = self.servers.get(server_name)
        if not server_info:
            logger.error(f"Server {server_name} not found")
            return
        
        server_url = server_info.get("url")
        if not server_url:
            logger.error(f"No URL for server {server_name}")
            return
        
        try:
            # Try to get tools via HTTP
            tools_url = f"{server_url.rstrip('/')}/tools"
            response = await self.http_client.get(tools_url)
            
            if response.status_code == 200:
                tools_data = response.json()
                tools_list = tools_data.get("tools", [])
                
                for tool in tools_list:
                    tool_name = tool.get("name")
                    if tool_name:
                        # Convert inputSchema to parameters format for compatibility
                        tool_info = {
                            "name": tool_name,
                            "description": tool.get("description", ""),
                            "server": server_name
                        }
                        
                        # Convert inputSchema to parameters
                        input_schema = tool.get("inputSchema", {})
                        if input_schema:
                            tool_info["parameters"] = {
                                "type": input_schema.get("type", "object"),
                                "properties": input_schema.get("properties", {}),
                                "required": input_schema.get("required", [])
                            }
                        else:
                            tool_info["parameters"] = tool.get("parameters", {})
                        
                        self.tools[tool_name] = tool_info
                
                logger.info(f"Discovered {len(tools_list)} tools from {server_name}")
                return
        
        except Exception as e:
            logger.warning(f"Failed to discover tools from {server_name} via HTTP: {e}")
            logger.info(f"Falling back to hardcoded tool definitions for {server_name}")
        
        # Fallback to hardcoded tool definitions if HTTP discovery fails
        # For unified server, include all tools
        if "unified" in server_name.lower():
            # All tools are in the unified server
            self._add_unified_tools(server_name)
        elif "zendesk" in server_name:
            self.tools.update({
                "get_ticket": {
                    "name": "get_ticket",
                    "description": "Get ticket details from Zendesk by ticket ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "Zendesk ticket ID (required)"
                            }
                        },
                        "required": ["ticket_id"]
                    },
                    "server": server_name
                },
                "update_ticket": {
                    "name": "update_ticket",
                    "description": "Update a Zendesk ticket with comment and/or status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "Zendesk ticket ID (required)"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Optional comment to add to the ticket"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["open", "pending", "solved", "closed"],
                                "description": "Optional ticket status"
                            }
                        },
                        "required": ["ticket_id"]
                    },
                    "server": server_name
                },
                "create_ticket": {
                    "name": "create_ticket",
                    "description": "Create a new Zendesk ticket",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject": {
                                "type": "string",
                                "description": "Ticket subject (required)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Ticket description/body (required)"
                            },
                            "requester_email": {
                                "type": "string",
                                "description": "Email of the ticket requester (required)"
                            },
                            "requester_name": {
                                "type": "string",
                                "description": "Optional name of the requester (defaults to email username)"
                            }
                        },
                        "required": ["subject", "description", "requester_email"]
                    },
                    "server": server_name
                }
            })
        
        if "slack" in server_name:
            self.tools.update({
                "search_messages": {
                    "name": "search_messages",
                    "description": "Search Slack message history by query string",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string (required)"
                            },
                            "channel": {
                                "type": "string",
                                "description": "Optional channel name or ID to limit search"
                            }
                        },
                        "required": ["query"]
                    },
                    "server": server_name
                },
                "get_channel_history": {
                    "name": "get_channel_history",
                    "description": "Get channel message history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel": {
                                "type": "string",
                                "description": "Channel name or ID (required)"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of messages to retrieve (default: 100)"
                            }
                        },
                        "required": ["channel"]
                    },
                    "server": server_name
                }
            })
        
        if "database" in server_name:
            self.tools.update({
                "query_orders": {
                    "name": "query_orders",
                    "description": "Query order database by order_id, customer_email, or status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "Optional order ID to filter by"
                            },
                            "customer_email": {
                                "type": "string",
                                "description": "Optional customer email to filter by"
                            },
                            "status": {
                                "type": "string",
                                "description": "Optional order status to filter by (e.g., 'processing', 'delivered', 'cancelled')"
                            }
                        }
                    },
                    "server": server_name
                },
                "get_order_details": {
                    "name": "get_order_details",
                    "description": "Get detailed information for a specific order. Requires order_id parameter.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID to get details for (required)"
                            }
                        },
                        "required": ["order_id"]
                    },
                    "server": server_name
                }
            })
    
    def _add_unified_tools(self, server_name: str):
        """Add all tools for unified server (fallback if HTTP discovery fails)"""
        # Zendesk tools
        self.tools.update({
            "get_ticket": {
                "name": "get_ticket",
                "description": "Get ticket details from Zendesk by ticket ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string", "description": "Zendesk ticket ID (required)"}
                    },
                    "required": ["ticket_id"]
                },
                "server": server_name
            },
            "update_ticket": {
                "name": "update_ticket",
                "description": "Update a Zendesk ticket with comment and/or status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string", "description": "Zendesk ticket ID (required)"},
                        "comment": {"type": "string", "description": "Optional comment"},
                        "status": {"type": "string", "enum": ["open", "pending", "solved", "closed"]}
                    },
                    "required": ["ticket_id"]
                },
                "server": server_name
            },
            "create_ticket": {
                "name": "create_ticket",
                "description": "Create a new Zendesk ticket",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string", "description": "Ticket subject (required)"},
                        "description": {"type": "string", "description": "Ticket description (required)"},
                        "requester_email": {"type": "string", "description": "Requester email (required)"}
                    },
                    "required": ["subject", "description", "requester_email"]
                },
                "server": server_name
            }
        })
        
        # Slack tools
        self.tools.update({
            "search_messages": {
                "name": "search_messages",
                "description": "Search Slack message history by query string",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (required)"},
                        "channel": {"type": "string", "description": "Optional channel name"}
                    },
                    "required": ["query"]
                },
                "server": server_name
            },
            "get_channel_history": {
                "name": "get_channel_history",
                "description": "Get channel message history",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "description": "Channel name or ID (required)"},
                        "limit": {"type": "number", "description": "Max messages (default: 100)"}
                    },
                    "required": ["channel"]
                },
                "server": server_name
            }
        })
        
        # Database tools
        self.tools.update({
            "query_orders": {
                "name": "query_orders",
                "description": "Query order database by order_id, customer_email, or status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "Optional order ID"},
                        "customer_email": {"type": "string", "description": "Optional customer email"},
                        "status": {"type": "string", "description": "Optional order status"}
                    }
                },
                "server": server_name
            },
            "get_order_details": {
                "name": "get_order_details",
                "description": "Get detailed information for a specific order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "Order ID (required)"}
                    },
                    "required": ["order_id"]
                },
                "server": server_name
            }
        })
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call an MCP tool via HTTP"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        server_name = tool["server"]
        
        server_info = self.servers.get(server_name)
        if not server_info:
            raise ValueError(f"Server {server_name} not connected")
        
        server_url = server_info.get("url")
        if not server_url:
            raise ValueError(f"No URL configured for server {server_name}")
        
        logger.info(f"Calling tool {tool_name} on server {server_name} at {server_url} with params {parameters}")
        
        try:
            # Make JSON-RPC 2.0 request
            request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                },
                "id": 1
            }
            
            response = await self.http_client.post(
                f"{server_url.rstrip('/')}/",
                json=request
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"result: {result}")
            # Handle JSON-RPC 2.0 response
            if "error" in result and result["error"] is not None:
                error = result["error"]
                raise ValueError(f"MCP server error: {error.get('message', 'Unknown error')} - {error.get('data', '')}")
            
            if "result" in result:
                result_data = result["result"]
                # Extract content from MCP response format
                if isinstance(result_data, dict) and "content" in result_data:
                    content = result_data["content"]
                    if isinstance(content, list) and len(content) > 0:
                        # Parse JSON text response
                        text_content = content[0].get("text", "")
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            return text_content
                return result_data
            
            raise ValueError(f"Unexpected response format: {result}")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            raise ValueError(f"Failed to call tool {tool_name}: HTTP {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            raise
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return list(self.tools.values())
    
    def get_tools_description(self) -> str:
        """Get human-readable description of available tools"""
        descriptions = []
        for tool_name, tool_info in self.tools.items():
            desc = f"- {tool_name}: {tool_info.get('description', 'No description')}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    async def disconnect(self):
        """Disconnect from all MCP servers"""
        logger.info("Disconnecting from MCP servers...")
        self.servers.clear()
        self.tools.clear()
        self.connected = False
        if self.http_client:
            await self.http_client.aclose()
        logger.info("Disconnected from all MCP servers")

