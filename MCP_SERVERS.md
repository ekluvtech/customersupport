# MCP Servers Architecture

## Overview

The MCP (Model Context Protocol) integrations are combined into a single unified HTTP server, providing all tools from Zendesk, Slack, and Database in one endpoint.

## Architecture

```
┌─────────────────┐
│  Support Agent  │
│   (Main App)    │
└────────┬────────┘
         │ HTTP Calls
         │
    ┌────┴────┐
    │ MCP     │
    │ Client  │
    └────┬────┘
         │
    ┌────┴──────────────┐
    │                   │
┌───▼───────────────────▼──┐
│   Unified MCP Server     │
│   http://localhost:8000  │
│                          │
│  ┌──────────┐           │
│  │ Zendesk  │           │
│  │ Tools    │           │
│  └──────────┘           │
│  ┌──────────┐           │
│  │  Slack   │           │
│  │  Tools   │           │
│  └──────────┘           │
│  ┌──────────┐           │
│  │ Database │           │
│  │  Tools   │           │
│  └──────────┘           │
└──────────────────────────┘
```

## Quick Start

### 1. Start the Unified MCP Server

```bash
# Option 1: Using bash script
./scripts/start_mcp_servers.sh

# Option 2: Using Python script
python scripts/start_mcp_servers.py

# Option 3: Direct command
python -m mcp_integrations.unified_server --http --port 8000
```

### 2. Verify Server is Running

```bash
# Check health
curl http://localhost:8000/health

# List all available tools
curl http://localhost:8000/tools
```

## Configuration

Update `config/config.yaml`:

```yaml
mcp:
  servers:
    - name: unified_mcp
      url: http://localhost:8000
```

## Server Endpoints

Each MCP server provides:

- **POST /** - JSON-RPC 2.0 endpoint for tool execution
- **GET /health** - Health check
- **GET /tools** - List available tools

## Available Tools

The unified server exposes all tools from all integrations:

### Zendesk Tools
- `get_ticket` - Get ticket details by ID
- `update_ticket` - Update ticket status or add comments
- `create_ticket` - Create a new ticket

### Slack Tools
- `search_messages` - Search Slack message history
- `get_channel_history` - Get messages from a channel

### Database Tools
- `query_orders` - Query orders by various criteria
- `get_order_details` - Get detailed order information

## Benefits

1. **Simplicity**: Single server to manage and deploy
2. **Centralized**: All tools accessible from one endpoint
3. **Efficiency**: Reduced overhead from multiple processes
4. **Easier Configuration**: One URL to configure
5. **Unified Logging**: All integration logs in one place

## Migration from Separate Servers

If you were using separate servers, simply:
1. Stop the individual servers
2. Start the unified server
3. Update config to point to `http://localhost:8000`
4. The MCP client will automatically discover all tools

## Troubleshooting

### Server Won't Start

1. Check if port is already in use:
   ```bash
   lsof -i :8000
   ```

2. Check environment variables are set:
   ```bash
   echo $ZENDESK_SUBDOMAIN
   echo $SLACK_TOKEN
   echo $DATABASE_URL
   ```

### Connection Errors

1. Verify servers are running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check firewall/network settings

3. Verify URLs in config match server ports

## Development

To run in stdio mode (for MCP protocol):
```bash
python -m mcp_integrations.zendesk_server --stdio
```

To run in HTTP mode (default):
```bash
python -m mcp_integrations.zendesk_server --http --port 8000
```

