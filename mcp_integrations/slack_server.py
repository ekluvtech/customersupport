"""Slack MCP Server"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List

from mcp_integrations.base_server import SimpleMCPServer
from integrations.slack import SlackIntegration

logger = logging.getLogger(__name__)


class SlackMCPServer(SimpleMCPServer):
    """MCP Server for Slack integration"""
    
    def __init__(self):
        integration = SlackIntegration()
        super().__init__(integration)
        
        # Define available tools
        self.tools = {
            "search_messages": {
                "name": "search_messages",
                "description": "Search Slack message history",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string"
                        },
                        "channel": {
                            "type": "string",
                            "description": "Optional channel name to limit search"
                        }
                    },
                    "required": ["query"]
                }
            },
            "get_channel_history": {
                "name": "get_channel_history",
                "description": "Get message history from a Slack channel",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel name or ID"
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
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the Slack MCP server"""
        info = super().initialize()
        info["serverInfo"]["name"] = "slack-mcp-server"
        return info
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a Slack tool"""
        logger.info(f"Executing Slack tool: {tool_name} with args: {arguments}")
        return await super().execute_tool(tool_name, arguments)


def main():
    """Main entry point for running as a standalone server"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Slack MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run as stdio server (MCP protocol)")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8002, help="HTTP server port (default: 8002)")
    
    args = parser.parse_args()
    
    server = SlackMCPServer()
    
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

