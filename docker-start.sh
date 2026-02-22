#!/bin/bash
# Docker startup script for Customer Support application

set -e

echo "=========================================="
echo "Customer Support - Docker Setup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env file. Please edit it with your credentials."
        echo "   Edit .env and run this script again."
        exit 1
    else
        echo "❌ env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose."
    exit 1
fi

# Use docker compose (v2) if available, otherwise docker-compose (v1)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "📦 Building Docker images..."
$DOCKER_COMPOSE build

echo ""
echo "🚀 Starting containers..."
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "🏥 Checking service health..."

# Check MCP Server
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ MCP Server is healthy"
else
    echo "⚠️  MCP Server health check failed (may still be starting)"
fi

# Check Agent API
if curl -f http://localhost:8100/health > /dev/null 2>&1; then
    echo "✅ Agent API is healthy"
else
    echo "⚠️  Agent API health check failed (may still be starting)"
fi

echo ""
echo "=========================================="
echo "✅ Services started!"
echo "=========================================="
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   API:       http://localhost:8100"
echo "   MCP Server: http://localhost:8000"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    $DOCKER_COMPOSE logs -f"
echo "   Stop:         $DOCKER_COMPOSE down"
echo "   Restart:      $DOCKER_COMPOSE restart"
echo "   Status:       $DOCKER_COMPOSE ps"
echo ""
echo "📖 For more information, see docker/README.md"
echo ""

