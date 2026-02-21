# MCP Integrations

This directory contains MCP (Model Context Protocol) server implementations for various integrations.

## Overview

MCP servers expose integrations as standardized tools that can be discovered and called by MCP clients. Each server follows the JSON-RPC 2.0 protocol and can be run as standalone processes or integrated directly.

## Available Servers

### Zendesk MCP Server (`zendesk_server.py`)

Exposes Zendesk ticket operations as MCP tools:

- `get_ticket`: Get ticket details by ID
- `update_ticket`: Update ticket status or add comments
- `create_ticket`: Create new tickets

**Usage:**
```bash
# Run as standalone server (stdio mode)
python -m mcp_integrations.zendesk_server --stdio

# Or import and use programmatically
from mcp_integrations import ZendeskMCPServer
server = ZendeskMCPServer()
```

### Slack MCP Server (`slack_server.py`)

Exposes Slack message operations as MCP tools:

- `search_messages`: Search message history
- `get_channel_history`: Get channel message history

**Usage:**
```bash
python -m mcp_integrations.slack_server --stdio
```

### Database MCP Server (`database_server.py`)

Exposes database query operations as MCP tools:

- `query_orders`: Query orders by various criteria
- `get_order_details`: Get detailed order information

**Usage:**
```bash
python -m mcp_integrations.database_server --stdio
```

## Architecture

### Base Server (`base_server.py`)

The `MCPServer` base class provides:
- JSON-RPC 2.0 request handling
- Tool discovery and execution
- Error handling and response formatting
- stdio communication mode

The `SimpleMCPServer` class simplifies server creation by wrapping existing integration classes.

## Protocol

MCP servers communicate using JSON-RPC 2.0 over stdio. Key methods:

- `initialize`: Initialize the server
- `tools/list`: List available tools
- `tools/call`: Execute a tool

## Configuration

Servers are configured via environment variables:

- **Zendesk**: `ZENDESK_SUBDOMAIN`, `ZENDESK_EMAIL`, `ZENDESK_API_KEY`
- **Slack**: `SLACK_TOKEN`
- **Database**: `DATABASE_URL`

## Integration with MCP Client

The MCP client (`agent/mcp_client.py`) can connect to these servers either:

1. **As standalone processes**: Via stdio using the MCP protocol
2. **Directly**: By importing and using the server classes programmatically

For direct integration (current implementation), the MCP client routes tool calls directly to integration modules, but the server implementations are available for full MCP protocol compliance.

## Testing

Test servers individually:

```python
from mcp_integrations import ZendeskMCPServer

server = ZendeskMCPServer()
tools = server.get_tools()
print(f"Available tools: {[t['name'] for t in tools]}")
```

## Future Enhancements

- Full async/await support for tool execution
- Resource discovery (beyond tools)
- Prompts and templates
- Streaming responses
- Authentication and authorization

