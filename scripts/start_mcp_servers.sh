#!/bin/bash
# Script to start the unified MCP server

echo "Starting Unified MCP Server..."

# Start Unified MCP Server (combines Zendesk, Slack, and Database)
echo "Starting Unified MCP Server on port 8000..."
python -m mcp_integrations.unified_server --http --port 8000 &
SERVER_PID=$!
echo "Unified MCP Server started with PID: $SERVER_PID"

echo ""
echo "Unified MCP Server started!"
echo "Server URL: http://localhost:8000"
echo "PID: $SERVER_PID"
echo ""
echo "Available integrations:"
echo "  - Zendesk (get_ticket, update_ticket, create_ticket)"
echo "  - Slack (search_messages, get_channel_history)"
echo "  - Database (query_orders, get_order_details)"
echo ""
echo "To stop the server, run: kill $SERVER_PID"
echo "Or use: pkill -f 'mcp_integrations.unified_server'"

# Wait for the process
wait

