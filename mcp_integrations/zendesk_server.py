"""Zendesk MCP Server"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List

from mcp_integrations.base_server import SimpleMCPServer
from integrations.zendesk import ZendeskIntegration

logger = logging.getLogger(__name__)


class ZendeskMCPServer(SimpleMCPServer):
    """MCP Server for Zendesk integration"""
    
    def __init__(self):
        integration = ZendeskIntegration()
        super().__init__(integration)
        
        # Define available tools
        self.tools = {
            "get_ticket": {
                "name": "get_ticket",
                "description": "Get ticket details from Zendesk by ticket ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The Zendesk ticket ID"
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
                            "description": "The Zendesk ticket ID"
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
                            "description": "Ticket subject"
                        },
                        "description": {
                            "type": "string",
                            "description": "Ticket description/body"
                        },
                        "requester_email": {
                            "type": "string",
                            "description": "Email of the ticket requester"
                        }
                    },
                    "required": ["subject", "description", "requester_email"]
                }
            }
        }
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the Zendesk MCP server"""
        info = super().initialize()
        info["serverInfo"]["name"] = "zendesk-mcp-server"
        return info
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a Zendesk tool"""
        logger.info(f"Executing Zendesk tool: {tool_name} with args: {arguments}")
        return await super().execute_tool(tool_name, arguments)


def main():
    """Main entry point for running as a standalone server"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Zendesk MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run as stdio server (MCP protocol)")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="HTTP server port (default: 8001)")
    
    args = parser.parse_args()
    
    server = ZendeskMCPServer()
    
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

