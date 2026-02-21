"""API Interface for the Customer Support Agent"""

import asyncio
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent.core import SupportAgent
from config.loader import load_config

logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Support Agent API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[SupportAgent] = None


class MessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    channel: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    response: str
    user_id: Optional[str] = None
    channel: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    try:
        config = load_config()
        agent = SupportAgent(config)
        await agent.start()
        logger.info("Agent initialized and started")
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent
    if agent:
        await agent.stop()
        logger.info("Agent stopped")


@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """
    Process a customer message and return a response
    
    Example:
        POST /chat
        {
            "message": "What's the status of my order #12345?",
            "user_id": "user_123",
            "channel": "web",
            "metadata": {"order_number": "12345", "email": "customer@example.com"}
        }
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        response = await agent.process_message(
            message=request.message,
            user_id=request.user_id,
            channel=request.channel,
            metadata=request.metadata
        )
        
        return MessageResponse(
            response=response,
            user_id=request.user_id,
            channel=request.channel
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if agent and agent.running else "unhealthy",
        "agent_running": agent.running if agent else False
    }


def run_api(host: str = "0.0.0.0", port: int = 8100):
    """Run the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()

