"""Database MCP Server"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List

from mcp_integrations.base_server import SimpleMCPServer
from integrations.database import DatabaseIntegration

logger = logging.getLogger(__name__)


class DatabaseMCPServer(SimpleMCPServer):
    """MCP Server for Database integration"""
    
    def __init__(self):
        integration = DatabaseIntegration()
        super().__init__(integration)
        
        # Define available tools
        self.tools = {
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
                            "description": "The order ID"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        }
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the Database MCP server"""
        info = super().initialize()
        info["serverInfo"]["name"] = "database-mcp-server"
        return info
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a Database tool"""
        logger.info(f"Executing Database tool: {tool_name} with args: {arguments}")
        return await super().execute_tool(tool_name, arguments)


def main():
    """Main entry point for running as a standalone server"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Database MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run as stdio server (MCP protocol)")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8003, help="HTTP server port (default: 8003)")
    
    args = parser.parse_args()
    
    server = DatabaseMCPServer()
    
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

