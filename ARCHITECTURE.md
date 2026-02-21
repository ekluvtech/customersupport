# Architecture Overview

## System Architecture

The Customer Support Agent is built with a modular architecture that separates concerns and allows for easy extension:

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Interface                        │
│  (Interactive Chat / REST API / Programmatic)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      SupportAgent (core.py)                  │
│  - Orchestrates all components                              │
│  - Handles message processing                               │
│  - Manages conversation flow                                │
└─────────┬──────────┬───────────┬─────────────┬─────────────┘
          │          │           │             │
          ▼          ▼           ▼             ▼
    ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐
    │ Ollama  │ │   MCP    │ │ Memory  │ │  Identity    │
    │ Client  │ │  Client  │ │ Manager │ │  Verifier    │
    └─────────┘ └────┬─────┘ └─────────┘ └──────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   MCP Integrations   │
          │  - Zendesk Server    │
          │  - Slack Server      │
          │  - Database Server   │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   External Systems   │
          │  - Zendesk API       │
          │  - Slack API         │
          │  - Order Database    │
          │  - CRMs              │
          └──────────────────────┘
```

## Component Details

### 1. SupportAgent (`agent/core.py`)

The main orchestration class that:
- Initializes all components
- Processes customer messages
- Coordinates between LLM, MCP, and memory systems
- Manages conversation context

**Key Methods:**
- `start()`: Initialize all components
- `process_message()`: Main message processing pipeline
- `stop()`: Cleanup and shutdown

### 2. OllamaClient (`agent/llm_client.py`)

Handles communication with the local Ollama LLM service:
- Sends prompts to Ollama
- Receives and processes responses
- Manages HTTP connections
- Supports tool calling (with proper implementation)

**Configuration:**
- Model selection (llama2, mistral, etc.)
- Temperature and token limits
- Timeout settings

### 3. MCPClient (`agent/mcp_client.py`)

Manages connections to MCP (Model Context Protocol) servers:
- Discovers available tools from MCP servers
- Routes tool calls to appropriate integrations
- Maintains connections to multiple MCP servers

**MCP Servers:**
- Zendesk MCP Server: Ticket operations
- Slack MCP Server: Message search and history
- Database MCP Server: Order queries

### 4. MemoryManager (`agent/memory.py`)

Handles conversation context and persistence:
- Stores conversation history
- Retrieves relevant context for conversations
- Supports multiple backends (ChromaDB, in-memory, etc.)
- Maintains context across sessions

**Features:**
- User/channel-specific contexts
- Configurable history limits
- Persistent storage options

### 5. IdentityVerifier (`agent/identity.py`)

Verifies customer identity before accessing sensitive data:
- Validates order numbers, emails, ticket IDs
- Configurable verification methods
- Security-first approach

### 6. Integration Modules (`integrations/`)

Direct integrations with external systems:

**ZendeskIntegration:**
- Get ticket details
- Update tickets (status, comments)
- Create new tickets

**SlackIntegration:**
- Search message history
- Get channel conversations
- Access archived threads

**DatabaseIntegration:**
- Query orders by various criteria
- Get detailed order information
- Supports multiple database types

## Data Flow

### Message Processing Flow

1. **Receive Message**: Customer sends message via any interface
2. **Identity Verification**: Verify customer if required
3. **Context Retrieval**: Load relevant conversation history
4. **Tool Discovery**: Get available MCP tools
5. **LLM Generation**: Send message to Ollama with context and tools
6. **Tool Execution**: Execute any required tool calls
7. **Response Generation**: Generate final response
8. **Storage**: Store interaction in memory

### MCP Tool Execution Flow

1. **Tool Discovery**: MCP client discovers tools from servers
2. **Tool Call**: Agent requests tool execution
3. **Routing**: MCP client routes to appropriate integration
4. **API Call**: Integration makes external API call
5. **Response**: Result returned to agent
6. **LLM Processing**: LLM incorporates result into response

## Configuration

Configuration is managed through YAML files with environment variable support:

- **Ollama Settings**: Model, URL, parameters
- **MCP Servers**: Server definitions and credentials
- **Integrations**: API keys, connection strings
- **Agent Settings**: Prompts, verification, context limits
- **Security**: Encryption, data retention

## Extension Points

### Adding New Integrations

1. Create integration module in `integrations/`
2. Implement tool execution methods
3. Register with MCP client
4. Update configuration

### Adding New MCP Servers

1. Create MCP server module in `mcp_integrations/`
2. Implement MCP protocol handlers
3. Define available tools
4. Add server configuration

### Custom Memory Backends

1. Implement backend interface in `agent/memory.py`
2. Add configuration option
3. Update MemoryManager initialization

## Security Considerations

- **Local Processing**: All LLM processing happens locally with Ollama
- **Credential Management**: Environment variables for sensitive data
- **Identity Verification**: Required before accessing customer data
- **Data Encryption**: Configurable encryption for stored data
- **Access Control**: Integration-level authentication

## Performance Considerations

- **Async Operations**: All I/O operations are asynchronous
- **Connection Pooling**: Database connections use pools
- **Context Limits**: Configurable history limits prevent memory issues
- **Caching**: Consider adding caching for frequently accessed data
- **Rate Limiting**: Consider rate limiting for external APIs

## Deployment Options

1. **Local Development**: Direct Python execution
2. **API Server**: FastAPI/uvicorn server
3. **Docker Container**: Containerized deployment (future)
4. **Kubernetes**: Scalable deployment (future)

