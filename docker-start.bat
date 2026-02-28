@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo Customer Support - Docker Setup (Windows)
echo ==========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Creating .env from env.example...

    if exist "env.example" (
        copy "env.example" ".env" >nul
        echo ✅ Created .env file. Please edit it with your credentials.
        echo    Edit .env and run this script again.
        exit /b 1
    ) else (
        echo ❌ env.example not found. Please create .env manually.
        exit /b 1
    )
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if docker compose (v2) or docker-compose (v1) is available
docker compose version >nul 2>&1
if !errorlevel! equ 0 (
    set "DOCKER_COMPOSE=docker compose"
) else (
    docker-compose version >nul 2>&1
    if !errorlevel! equ 0 (
        set "DOCKER_COMPOSE=docker-compose"
    ) else (
        echo ❌ docker-compose is not installed. Please install Docker Compose.
        exit /b 1
    )
)

echo 📦 Building Docker images...
%DOCKER_COMPOSE% build
if errorlevel 1 (
    echo ❌ Build failed.
    exit /b 1
)

echo.
echo 🚀 Starting containers...
%DOCKER_COMPOSE% up -d
if errorlevel 1 (
    echo ❌ Failed to start containers.
    exit /b 1
)

echo.
echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check health
echo.
echo 🏥 Checking service health...

REM Check MCP Server
curl -f http://localhost:8000/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ MCP Server is healthy
) else (
    echo ⚠️  MCP Server health check failed (may still be starting)
)

REM Check Agent API
curl -f http://localhost:8100/health >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Agent API is healthy
) else (
    echo ⚠️  Agent API health check failed (may still be starting)
)

echo.
echo ==========================================
echo ✅ Services started!
echo ==========================================
echo.
echo 📍 Access points:
echo    Frontend:  http://localhost:3000
echo    API:       http://localhost:8100
echo    MCP Server: http://localhost:8000
echo.
echo 📋 Useful commands:
echo    View logs:    %DOCKER_COMPOSE% logs -f
echo    Stop:         %DOCKER_COMPOSE% down
echo    Restart:      %DOCKER_COMPOSE% restart
echo    Status:       %DOCKER_COMPOSE% ps
echo.
echo 📖 For more information, see docker/README.md
echo.

endlocal