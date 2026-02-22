# Advanced AI Customer Support Agent with MCP

An intelligent customer support agent powered by Model Context Protocol (MCP) that integrates with CRMs, ticketing systems, communication tools, and databases to provide personalized, real-time assistance.

## Features

- **Real-time Data Access**: Pull current order status, shipping details, account history from databases/APIs via MCP
- **Context Awareness**: Access previous conversations, tickets, emails, Slack threads through unified memory layer
- **Action Capabilities**: Update tickets in Zendesk, create new tickets, send notifications instantly
- **Context Persistence**: Maintain conversation history across channels
- **Flexible LLM Support**: Choose between Ollama (local, private), OpenAI (cloud, powerful), or Vertex AI/Gemini (Google Cloud)
- **MCP Integrations**: Secure connections to enterprise systems (CRMs, ERPs, helpdesk tools) in real-time

## Architecture

```
customersupport/
├── agent/              # Main agent application
├── mcp_integrations/   # MCP server integrations
├── integrations/       # External system connectors
├── memory/             # Context persistence layer
├── config/             # Configuration files
├── utils/              # Utility functions
└── frontend/           # React UI for customer support chat
```

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

### Basic Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the agent:**
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config/config.yaml with your settings
   ```

3. **Configure LLM Provider:**
   
   The agent supports three LLM providers:
   
   **Option A: Ollama (Local, Private)**
   - Start Ollama (if not already running):
     ```bash
     ollama pull llama2
     ```
   - Configure in `config/config.yaml`:
     ```yaml
     llm:
       provider: ollama
     ```
   
   **Option B: OpenAI (Cloud, Powerful)**
   - Set your OpenAI API key:
     ```bash
     export OPENAI_API_KEY=your-api-key-here
     ```
   - Configure in `config/config.yaml`:
     ```yaml
     llm:
       provider: openai
     openai:
       api_key: "${OPENAI_API_KEY}"
       model: gpt-4
     ```
   
   **Option C: Vertex AI / Gemini (Google Cloud)**
   - **Option 1: Service Account JSON (Recommended)**
     - Create a service account in Google Cloud Console
     - Download the JSON key file
     - Set credentials path:
       ```bash
       export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
       ```
   - **Option 2: User Credentials**
     - Authenticate with Google Cloud:
       ```bash
       gcloud auth application-default login
       export GOOGLE_CLOUD_PROJECT=your-project-id
       ```
   - Install Vertex AI dependencies:
     ```bash
     pip install google-cloud-aiplatform
     ```
   - Configure in `config/config.yaml`:
     ```yaml
     llm:
       provider: vertexai  # or "gemini"
     vertexai:
       credentials_path: "${GOOGLE_APPLICATION_CREDENTIALS}"  # For JSON file
       project_id: "${GOOGLE_CLOUD_PROJECT}"
       location: us-central1
       model: gemini-pro
     ```
   - See [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) for detailed setup instructions
   - See [VERTEX_AI_TROUBLESHOOTING.md](VERTEX_AI_TROUBLESHOOTING.md) if you encounter rate limit errors (429)

4. **Run the interactive chat:**
   ```bash
   python -m examples.interactive_chat
   ```

   Or start the API server:
   ```bash
   python -m agent.api
   ```

pip install --upgrade certifi
export SSL_CERT_FILE=$(python -m certifi)

## Usage

The agent can be used via:

- **Web UI (React)**: Modern chat interface for customers (see [Frontend Setup](#frontend-setup))
- **Interactive Chat**: `python -m examples.interactive_chat`
- **MCP Server**: `python -m mcp_integrations.unified_server --http --port 8000` (running all the tools under unified server)
- **REST API**: `python -m agent.api` (requires FastAPI/uvicorn)
- **Programmatic**: Import and use the `SupportAgent` class directly

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The React app will open at `http://localhost:3000`

4. **Make sure the MCP Server is running:**
   ```bash
   # In a separate terminal
    python -m mcp_integrations.unified_server --http --port 8000
   ```

   The MCP Server runs on `http://localhost:8000/` by default. and you can verify the tools available by querying http://localhost:8000/tools


5. **Make sure the backend API is running:**
   ```bash
   # In a separate terminal
   python -m agent.api
   ```

   The API runs on `http://localhost:8100` by default.

6. **Start chatting!** The UI will automatically connect to the backend API.

For more details, see [frontend/README.md](frontend/README.md).

## Demo Data

To populate Zendesk, Salesforce, Slack, and your database with sample data for testing:

1. See [demo_data/README.md](demo_data/README.md) for detailed instructions
2. Set up environment variables for each service
3. Run the population scripts:
   ```bash
   # Populate all services
   python demo_data/populate_all.py
   
   # Or populate individually:
   python demo_data/populate_database.py
   python demo_data/populate_zendesk.py
   python demo_data/populate_salesforce.py
   python demo_data/populate_slack.py
   ```

This will create sample tickets, orders, cases, and messages that you can use to test the agent's capabilities.

## Privacy & Security

- **Ollama (Local)**: All data processed locally, no data leaves customer premises
- **OpenAI (Cloud)**: Data is sent to OpenAI's API - review OpenAI's privacy policy
- **Vertex AI (Google Cloud)**: Data is sent to Google Cloud - review Google Cloud's privacy policy
- Secure MCP connections with authentication
- Customer identity verification before accessing sensitive data
- Configurable encryption and data retention policies

## License

MIT

