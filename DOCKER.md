# Docker Deployment Guide

This guide explains how to deploy the Customer Support application using Docker containers.

## Overview

The application consists of three main services:

1. **MCP Server** - Unified MCP server (port 8000)
2. **Agent API** - FastAPI REST API (port 8100)
3. **Frontend** - React web application (port 3000)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+ (or docker-compose 1.29+)
- Environment variables configured (see below)

## Quick Start

### 1. Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit with your credentials
nano .env
```

Required environment variables:
- `ZENDESK_SUBDOMAIN` - Your Zendesk subdomain
- `ZENDESK_EMAIL` - Zendesk account email
- `ZENDESK_API_KEY` - Zendesk API token
- `SLACK_TOKEN` - Slack bot token (if using Slack)
- `DATABASE_URL` - PostgreSQL connection string

### 2. Start Services

**Option A: Using the startup script (recommended)**
```bash
./docker-start.sh
```

**Option B: Using docker-compose directly**
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8100
- **MCP Server**: http://localhost:8000

## Service Details

### MCP Server

The unified MCP server combines all integrations (Zendesk, Slack, Database).

**Container**: `customer-support-mcp`  
**Port**: 8000  
**Health Check**: `GET /health`

**Environment Variables**:
- `ZENDESK_SUBDOMAIN`, `ZENDESK_EMAIL`, `ZENDESK_API_KEY`
- `SLACK_TOKEN`
- `DATABASE_URL`
- `GOOGLE_APPLICATION_CREDENTIALS` (if using Vertex AI)

### Agent API

The main FastAPI server that handles chat requests.

**Container**: `customer-support-api`  
**Port**: 8100  
**Health Check**: `GET /health`

**Environment Variables**:
- `LLM_PROVIDER` (default: `vertexai`)
- `OPENAI_API_KEY` (if using OpenAI)
- `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT` (if using Vertex AI)
- `MCP_SERVER_URL` (default: `http://mcp-server:8000`)
- `DATABASE_URL`
- `MEMORY_BACKEND` (default: `memory`)

### Frontend

React/Vite application served via Nginx.

**Container**: `customer-support-frontend`  
**Port**: 3000 (mapped to Nginx port 80)

**Build Arguments**:
- `VITE_API_URL` - API URL for the frontend (default: `http://localhost:8100`)

## Google Cloud Credentials

If using Vertex AI, you need to provide Google Cloud service account credentials:

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Place it in the project root (e.g., `.google-credentials.json`)
4. Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./.google-credentials.json
   ```

The credentials file will be mounted into the containers automatically.

## Database Setup

### Option 1: External Database

Set `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Option 2: Docker Database

1. Uncomment the `db` service in `docker-compose.yml`
2. Set database variables in `.env`:
   ```
   POSTGRES_USER=customersupport
   POSTGRES_PASSWORD=password
   POSTGRES_DB=customersupport
   ```
3. The database will be available at `db:5432` from other containers

## Common Operations

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

### Stop Services

```bash
docker-compose down
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

### Check Service Status

```bash
docker-compose ps
```

### Execute Commands in Containers

```bash
# MCP Server
docker-compose exec mcp-server bash

# Agent API
docker-compose exec agent-api bash

# Frontend
docker-compose exec frontend sh
```

## Troubleshooting

### Services Won't Start

1. Check logs:
   ```bash
   docker-compose logs
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check Docker resources:
   ```bash
   docker system df
   docker system prune  # Clean up if needed
   ```

### Health Checks Failing

1. Check if services are running:
   ```bash
   docker-compose ps
   ```

2. Test health endpoints manually:
   ```bash
   curl http://localhost:8000/health  # MCP Server
   curl http://localhost:8100/health  # Agent API
   ```

3. Check service logs for errors:
   ```bash
   docker-compose logs mcp-server
   docker-compose logs agent-api
   ```

### Frontend Can't Connect to API

1. Verify `VITE_API_URL` in `.env` matches your setup
2. Rebuild frontend with correct API URL:
   ```bash
   docker-compose build --build-arg VITE_API_URL=http://localhost:8100 frontend
   docker-compose up -d frontend
   ```

### Database Connection Issues

1. Verify `DATABASE_URL` is correct
2. Test database connection:
   ```bash
   docker-compose exec agent-api python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"
   ```

### Google Cloud Credentials Issues

1. Verify credentials file exists and is readable
2. Check file path in `.env`
3. Verify service account has required permissions

## Production Deployment

For production, consider:

1. **Use specific image tags** instead of building from source
2. **Set resource limits** in docker-compose.yml
3. **Use secrets management** (Docker secrets, Kubernetes secrets, etc.)
4. **Configure reverse proxy** (nginx, Traefik) for SSL termination
5. **Set up monitoring** and logging aggregation
6. **Configure backups** for database volumes
7. **Use health checks** for orchestration platforms

### Example Production Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  agent-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Building Individual Images

```bash
# Frontend
docker build -f Dockerfile.frontend -t customer-support-frontend:latest .

# Agent API
docker build -f Dockerfile.api -t customer-support-api:latest .

# MCP Server
docker build -f Dockerfile.mcp -t customer-support-mcp:latest .
```

## Pushing to Registry

```bash
# Tag images
docker tag customer-support-frontend:latest your-registry/customer-support-frontend:latest
docker tag customer-support-api:latest your-registry/customer-support-api:latest
docker tag customer-support-mcp:latest your-registry/customer-support-mcp:latest

# Push
docker push your-registry/customer-support-frontend:latest
docker push your-registry/customer-support-api:latest
docker push your-registry/customer-support-mcp:latest
```

## Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- See `docker/README.md` for more detailed information

