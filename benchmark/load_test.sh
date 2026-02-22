#!/bin/bash
# Comprehensive Load Testing Script
# Tests the system at various load levels

API_URL="${API_URL:-http://localhost:8100}"
MCP_URL="${MCP_URL:-http://localhost:8000}"

echo "=========================================="
echo "Customer Support API - Load Testing"
echo "=========================================="
echo "API URL: $API_URL"
echo "MCP URL: $MCP_URL"
echo ""

# Check if services are running
echo "Checking service health..."
if ! curl -f -s "$API_URL/health" > /dev/null; then
    echo "❌ API is not responding. Please start the services first."
    exit 1
fi
echo "✅ API is healthy"
echo ""

# Test scenarios
echo "Running load tests..."
echo ""

# Test 1: Light load (100 req/s)
echo "Test 1: Light Load (100 req/s for 30s)"
python3 benchmark/benchmark.py \
    --url "$API_URL" \
    --endpoint "/health" \
    --concurrent 10 \
    --duration 30 \
    --output benchmark/results_light.json

# Test 2: Medium load (500 req/s)
echo "Test 2: Medium Load (500 req/s for 30s)"
python3 benchmark/benchmark.py \
    --url "$API_URL" \
    --endpoint "/health" \
    --concurrent 50 \
    --duration 30 \
    --output benchmark/results_medium.json

# Test 3: Heavy load (1000 req/s)
echo "Test 3: Heavy Load (1000 req/s for 30s)"
python3 benchmark/benchmark.py \
    --url "$API_URL" \
    --endpoint "/health" \
    --concurrent 100 \
    --duration 30 \
    --output benchmark/results_heavy.json

# Test 4: Extreme load (5000 req/s)
echo "Test 4: Extreme Load (5000 req/s for 30s)"
python3 benchmark/benchmark.py \
    --url "$API_URL" \
    --endpoint "/health" \
    --concurrent 500 \
    --duration 30 \
    --output benchmark/results_extreme.json

# Test 5: Chat endpoint (realistic load)
echo "Test 5: Chat Endpoint (100 req/s for 60s)"
python3 benchmark/benchmark.py \
    --url "$API_URL" \
    --endpoint "/chat" \
    --method POST \
    --message "What is the status of my order?" \
    --concurrent 20 \
    --duration 60 \
    --output benchmark/results_chat.json

echo ""
echo "=========================================="
echo "Load testing complete!"
echo "Results saved to benchmark/results_*.json"
echo "=========================================="

