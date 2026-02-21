"""HTTP Server for MCP integrations"""

import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from mcp_integrations.base_server import _json_serializer

logger = logging.getLogger(__name__)


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = {}
    id: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response model"""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPHTTPServer:
    """HTTP server wrapper for MCP servers"""
    
    def __init__(self, mcp_server, host: str = "0.0.0.0", port: int = 8000):
        self.mcp_server = mcp_server
        self.host = host
        self.port = port
        self.app = FastAPI(title=f"{mcp_server.__class__.__name__} HTTP Server")
        self._setup_cors()
        self._setup_routes()
    
    def _setup_cors(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins for MCP server
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],  # Explicitly include OPTIONS
            allow_headers=["*"],
            expose_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        # Add explicit OPTIONS handler for CORS preflight
        @self.app.options("/{full_path:path}")
        async def options_handler(full_path: str):
            """Handle OPTIONS requests for CORS preflight"""
            return {"status": "ok"}
        
        @self.app.post("/")
        async def handle_jsonrpc(request: JSONRPCRequest):
            """Handle JSON-RPC 2.0 requests"""
            try:
                request_dict = request.dict()
                
                # Run handle_request in executor since it may block or use asyncio.run
                import asyncio
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    self.mcp_server.handle_request, 
                    request_dict
                )
                
                return JSONRPCResponse(**response)
            except Exception as e:
                logger.error(f"Error handling request: {e}", exc_info=True)
                return JSONRPCResponse(
                    jsonrpc="2.0",
                    id=getattr(request, 'id', None),
                    error={
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "server": self.mcp_server.__class__.__name__}
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools"""
            try:
                tools = self.mcp_server.get_tools()
                return {"tools": tools}
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def run(self):
        """Run the HTTP server"""
        logger.info(f"Starting {self.mcp_server.__class__.__name__} HTTP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")

