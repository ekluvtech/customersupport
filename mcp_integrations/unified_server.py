"""Unified MCP Server combining all integrations"""

import logging
import sys
from typing import Dict, Any, List, Optional

from mcp_integrations.base_server import MCPServer
from integrations.zendesk import ZendeskIntegration
from integrations.slack import SlackIntegration
from integrations.database import DatabaseIntegration

logger = logging.getLogger(__name__)


class UnifiedMCPServer(MCPServer):
    """Unified MCP Server that combines all integrations"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize all integrations
        self.zendesk_integration = ZendeskIntegration()
        self.slack_integration = SlackIntegration()
        self.database_integration = DatabaseIntegration()
        
        # Map tool names to their integrations
        self.tool_integrations: Dict[str, Any] = {}
        
        # Define all available tools from all integrations
        self._define_tools()
    
    def _define_tools(self):
        """Define all tools from all integrations"""
        
        # Zendesk tools
        zendesk_tools = {
            "get_ticket": {
                "name": "get_ticket",
                "description": "Get ticket details from Zendesk by ticket ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The Zendesk ticket ID (required)"
                        }
                    },
                    "required": ["ticket_id"]
                }
            },
            "update_ticket": {
                "name": "update_ticket",
                "description": "Update a Zendesk ticket (status, add comment, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The Zendesk ticket ID (required)"
                        },
                        "comment": {
                            "type": "string",
                            "description": "Optional comment to add to the ticket"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["open", "pending", "solved", "closed"],
                            "description": "Optional status to set for the ticket"
                        }
                    },
                    "required": ["ticket_id"]
                }
            },
            "create_ticket": {
                "name": "create_ticket",
                "description": "Create a new Zendesk ticket",
                "inputSchema": {
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
                }
            }
        }
        
        # Slack tools
        slack_tools = {
            "search_messages": {
                "name": "search_messages",
                "description": "Search Slack message history by query string",
                "inputSchema": {
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
                }
            },
            "get_channel_history": {
                "name": "get_channel_history",
                "description": "Get channel message history from Slack",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel name or ID (required)"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of messages to retrieve (default: 100)",
                            "default": 100
                        }
                    },
                    "required": ["channel"]
                }
            }
        }
        
        # Database tools
        database_tools = {
            "query_orders": {
                "name": "query_orders",
                "description": "Query orders from the database by order_id, customer_email, or status",
                "inputSchema": {
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
                }
            },
            "get_order_details": {
                "name": "get_order_details",
                "description": "Get detailed information for a specific order",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order ID (required)"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        }
        
        # Combine all tools
        self.tools.update(zendesk_tools)
        self.tools.update(slack_tools)
        self.tools.update(database_tools)
        
        # Map tools to their integrations
        for tool_name in zendesk_tools.keys():
            self.tool_integrations[tool_name] = self.zendesk_integration
        for tool_name in slack_tools.keys():
            self.tool_integrations[tool_name] = self.slack_integration
        for tool_name in database_tools.keys():
            self.tool_integrations[tool_name] = self.database_integration
        
        logger.info(f"Unified MCP Server initialized with {len(self.tools)} tools")
        logger.info(f"  - Zendesk tools: {len(zendesk_tools)}")
        logger.info(f"  - Slack tools: {len(slack_tools)}")
        logger.info(f"  - Database tools: {len(database_tools)}")
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the unified MCP server"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "unified-mcp-server",
                "version": "1.0.0"
            }
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of all available tools"""
        return list(self.tools.values())
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by routing to the appropriate integration"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        integration = self.tool_integrations.get(tool_name)
        if not integration:
            raise ValueError(f"No integration found for tool {tool_name}")
        
        if not hasattr(integration, "execute_tool"):
            raise ValueError(f"Integration {type(integration).__name__} does not support execute_tool")
        
        logger.info(f"Executing tool {tool_name} via {type(integration).__name__} with args: {arguments}")
        return await integration.execute_tool(tool_name, arguments)


def main():
    """Main entry point for running the unified MCP server"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Unified MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run as stdio server (MCP protocol)")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port (default: 8000)")
    
    args = parser.parse_args()
    
    server = UnifiedMCPServer()
    
    if args.stdio:
        server.run_stdio()
    elif args.http:
        from mcp_integrations.http_server import MCPHTTPServer
        http_server = MCPHTTPServer(server, host=args.host, port=args.port)
        http_server.run()
    else:
        # Default to HTTP mode
        from mcp_integrations.http_server import MCPHTTPServer
        http_server = MCPHTTPServer(server, host=args.host, port=args.port)
        http_server.run()


if __name__ == "__main__":
    main()

