# Setup Guide

## Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running locally
   ```bash
   # Install Ollama from https://ollama.ai
   # Then pull a model:
   ollama pull llama2
   # Or use other models like:
   # ollama pull mistral
   # ollama pull codellama
   ```

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install with optional dependencies:

```bash
# With API support
pip install -r requirements.txt
pip install fastapi uvicorn

# With database support
pip install psycopg2-binary  # PostgreSQL
pip install pymongo  # MongoDB

# With memory backend
pip install chromadb
```

### 2. Configure the Agent

Copy the example configuration file:

```bash
cp config/config.example.yaml config/config.yaml
```

Edit `config/config.yaml` and configure:

- **Ollama settings**: Model name, base URL
- **MCP servers**: Zendesk, Slack, Database connections
- **Integration credentials**: API keys, tokens, connection strings
- **Agent settings**: System prompt, identity verification, context settings

### 3. Set Environment Variables (Recommended)

For security, use environment variables for sensitive credentials:

```bash
export ZENDESK_API_KEY="your_api_key"
export ZENDESK_SUBDOMAIN="your_subdomain"
export ZENDESK_EMAIL="your_email@example.com"
export SLACK_TOKEN="xoxp-your-token"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

Or create a `.env` file:

```bash
ZENDESK_API_KEY=your_api_key
ZENDESK_SUBDOMAIN=your_subdomain
ZENDESK_EMAIL=your_email@example.com
SLACK_TOKEN=xoxp-your-token
DATABASE_URL=postgresql://user:pass@localhost/dbname
```


### 4. Verify Ollama is Running

```bash
ollama list
```

Should show your installed models.

### 5. Test the Installation

Run the interactive chat example:

```bash
python -m examples.interactive_chat
```

Or start the API server:

```bash
python -m agent.api
```

Then test with:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with my order",
    "user_id": "test_user",
    "metadata": {"email": "test@example.com"}
  }'
```

## Troubleshooting

### Configuration Errors

- Ensure `config/config.yaml` exists (copy from `config/config.example.yaml`)
- Check that all required fields are filled
- Verify environment variables are set if using `${VAR}` syntax

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use a virtual environment to avoid conflicts
- Check Python version: `python --version` (should be 3.9+)

### MCP Server Connection Issues

- Verify integration credentials are correct
- Check network connectivity to external services
- Review logs for specific error messages

## Next Steps

- Read the [README.md](README.md) for usage examples
- Customize the system prompt in `config/config.yaml`
- Add additional MCP integrations as needed
- Configure memory backend for persistence

