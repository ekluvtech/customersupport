# Docker Setup Guide

This directory contains Docker configuration files for containerizing the Customer Support application.

## Architecture

The application consists of three main containers:

1. **MCP Server** (`mcp-server`) - Unified MCP server on port 8000
2. **Agent API** (`agent-api`) - FastAPI server on port 8100
3. **Frontend** (`frontend`) - React/Vite application on port 3000

## Quick Start

### 1. Set Up Environment Variables

```bash
# Copy the example environment file
cp docker/.env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Build and Run

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8100
- **MCP Server**: http://localhost:8000

## Individual Container Management

### Build Individual Containers

```bash
# Build frontend
docker build -f Dockerfile.frontend -t customer-support-frontend .

# Build API
docker build -f Dockerfile.api -t customer-support-api .

# Build MCP server
docker build -f Dockerfile.mcp -t customer-support-mcp .
```

### Run Individual Containers

```bash
# Run MCP server
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e ZENDESK_SUBDOMAIN=your-subdomain \
  -e ZENDESK_EMAIL=your-email@example.com \
  -e ZENDESK_API_KEY=your-key \
  -e SLACK_TOKEN=your-token \
  customer-support-mcp

# Run API
docker run -d \
  --name agent-api \
  -p 8100:8100 \
  -e LLM_PROVIDER=vertexai \
  -e MCP_SERVER_URL=http://mcp-server:8000 \
  --link mcp-server \
  customer-support-api

# Run Frontend
docker run -d \
  --name frontend \
  -p 3000:80 \
  customer-support-frontend
```

## Environment Variables

### Required Variables

- `ZENDESK_SUBDOMAIN` - Your Zendesk subdomain
- `ZENDESK_EMAIL` - Zendesk account email
- `ZENDESK_API_KEY` - Zendesk API token
- `SLACK_TOKEN` - Slack bot token (if using Slack)
- `DATABASE_URL` - PostgreSQL connection string

### Optional Variables

- `LLM_PROVIDER` - LLM provider (default: `vertexai`)
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud credentials JSON
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID
- `MEMORY_BACKEND` - Memory backend (default: `memory`)
- `VITE_API_URL` - Frontend API URL (default: `http://localhost:8100`)

## Google Cloud Credentials

If using Vertex AI, you need to provide Google Cloud credentials:

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Place it in the project root or mount it as a volume
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path

Example:
```bash
# In docker-compose.yml, the credentials are mounted from:
${GOOGLE_APPLICATION_CREDENTIALS:-./.google-credentials}:/app/.google-credentials:ro
```

## Database Setup

### Using External Database

Set `DATABASE_URL` in your `.env` file:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Using Docker Database

1. Uncomment the `db` service in `docker-compose.yml`
2. Set database environment variables in `.env`
3. The database will be available at `db:5432` from other containers

## Health Checks

All containers include health checks:

- **MCP Server**: `http://localhost:8000/health`
- **Agent API**: `http://localhost:8100/health`

Check container health:
```bash
docker-compose ps
```

## Troubleshooting

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp-server
docker-compose logs -f agent-api
docker-compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart mcp-server
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker-compose build mcp-server
docker-compose up -d mcp-server

# Rebuild all
docker-compose build --no-cache
docker-compose up -d
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Production Deployment

For production, consider:

1. **Use specific image tags** instead of `latest`
2. **Set up proper secrets management** (e.g., Docker secrets, Kubernetes secrets)
3. **Use reverse proxy** (nginx, Traefik) for SSL termination
4. **Configure resource limits** in docker-compose.yml
5. **Set up monitoring** and logging
6. **Use health checks** for orchestration
7. **Configure backup** for database volumes

Example production docker-compose override:
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
    restart: always

  agent-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    restart: always

  frontend:
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

