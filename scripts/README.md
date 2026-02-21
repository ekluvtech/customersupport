# MCP Server Startup Scripts

This directory contains scripts to start the unified MCP integration server.

## Overview

The unified MCP server combines all integrations (Zendesk, Slack, Database) into a single HTTP server, providing:
- Single endpoint for all tools
- Simplified deployment
- Centralized management
- All integrations in one process

## Starting the Unified Server

### Option 1: Using Startup Scripts (Recommended)

**Using Bash script:**
```bash
./scripts/start_mcp_servers.sh
```

**Using Python script:**
```bash
python scripts/start_mcp_servers.py
```

### Option 2: Direct Command

```bash
python -m mcp_integrations.unified_server --http --port 8000
```

## Server URL

The unified server runs on:
- **Unified MCP Server**: http://localhost:8000

This single server provides all tools from:
- **Zendesk**: get_ticket, update_ticket, create_ticket
- **Slack**: search_messages, get_channel_history
- **Database**: query_orders, get_order_details

## Configuration

Update `config/config.yaml` to set the unified server URL:

```yaml
mcp:
  servers:
    - name: unified_mcp
      url: http://localhost:8000
```

## API Endpoints

The unified server provides:

- `POST /` - JSON-RPC 2.0 endpoint for tool execution
- `GET /health` - Health check endpoint
- `GET /tools` - List all available tools from all integrations

## Testing

Test the server is running:
```bash
curl http://localhost:8000/health
```

List all available tools:
```bash
curl http://localhost:8000/tools
```

## Stopping the Server

**Stop the unified server:**
```bash
pkill -f 'mcp_integrations.unified_server'
```

**Or find the PID and kill it:**
```bash
ps aux | grep unified_server
kill <PID>
```

## Environment Variables

Make sure to set required environment variables before starting servers:

```bash
export ZENDESK_SUBDOMAIN="your_subdomain"
export ZENDESK_EMAIL="your_email@example.com"
export ZENDESK_API_KEY="your_api_key"
export SLACK_TOKEN="xoxb-your-token"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

