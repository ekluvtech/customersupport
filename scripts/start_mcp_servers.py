#!/usr/bin/env python3
"""Python script to start the unified MCP server"""

import subprocess
import sys
import signal

server = None

def signal_handler(sig, frame):
    """Handle shutdown signal"""
    print("\nShutting down Unified MCP Server...")
    if server and server.poll() is None:  # Process is still running
        server.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("Starting Unified MCP Server...\n")
    
    # Start unified server
    print("Starting Unified MCP Server on port 8000...")
    server = subprocess.Popen(
        [sys.executable, "-m", "mcp_integrations.unified_server", "--http", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print(f"  Unified MCP Server started with PID: {server.pid}")
    
    print("\n" + "="*60)
    print("Unified MCP Server started!")
    print("="*60)
    print("Server URL: http://localhost:8000")
    print("\nAvailable integrations:")
    print("  - Zendesk: get_ticket, update_ticket, create_ticket")
    print("  - Slack: search_messages, get_channel_history")
    print("  - Database: query_orders, get_order_details")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Wait for process
    try:
        server.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

