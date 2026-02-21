"""Base MCP Server Implementation"""

import json
import logging
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def _json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    from datetime import datetime, date
    from decimal import Decimal
    
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


class MCPServer(ABC):
    """Base class for MCP servers following JSON-RPC 2.0 protocol"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
    
    @abstractmethod
    def initialize(self) -> Dict[str, Any]:
        """Initialize the server and return server info"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool and return the result"""
        pass
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC 2.0 request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self.initialize()
                self.initialized = True
                return self._create_response(request_id, result)
            
            elif method == "tools/list":
                tools = self.get_tools()
                return self._create_response(request_id, {"tools": tools})
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                # Handle async tool execution
                import asyncio
                try:
                    # Check if execute_tool is async
                    if asyncio.iscoroutinefunction(self.execute_tool):
                        # Try to get running event loop, create new if none exists
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # If loop is running, we need to handle differently
                                # This shouldn't happen in handle_request, but handle it
                                import concurrent.futures
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(asyncio.run, self.execute_tool(tool_name, arguments))
                                    result = future.result()
                            else:
                                result = loop.run_until_complete(self.execute_tool(tool_name, arguments))
                        except RuntimeError:
                            # No event loop, create new one
                            result = asyncio.run(self.execute_tool(tool_name, arguments))
                    else:
                        result = self.execute_tool(tool_name, arguments)
                    
                    # Serialize result to JSON string using module-level serializer
                    result_text = json.dumps(result, default=_json_serializer, ensure_ascii=False)
                    return self._create_response(request_id, {"content": [{"type": "text", "text": result_text}]})
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                    return self._create_error_response(request_id, -32603, "Internal error", str(e))
            
            else:
                return self._create_error_response(request_id, -32601, "Method not found", method)
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return self._create_error_response(request_id, -32603, "Internal error", str(e))
    
    def _create_response(self, request_id: Optional[Any], result: Any) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def _create_error_response(
        self,
        request_id: Optional[Any],
        code: int,
        message: str,
        data: Any = None
    ) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 error response"""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }
    
    def run_stdio(self):
        """Run server using stdio (for MCP protocol)"""
        logger.info("Starting MCP server on stdio...")
        
        # Read requests from stdin
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = self._create_error_response(None, -32700, "Parse error")
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)


class SimpleMCPServer(MCPServer):
    """Simplified MCP server that can work with direct function calls"""
    
    def __init__(self, integration):
        super().__init__()
        self.integration = integration
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the server"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.__class__.__name__,
                "version": "0.1.0"
            }
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return list(self.tools.values())
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool using the integration"""
        if not hasattr(self.integration, "execute_tool"):
            raise ValueError(f"Integration {self.integration} does not support execute_tool")
        return await self.integration.execute_tool(tool_name, arguments)

