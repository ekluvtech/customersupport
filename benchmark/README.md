# Benchmarking Guide

This directory contains tools for performance testing and benchmarking the Customer Support API.

## Quick Start

### Prerequisites

```bash
pip install aiohttp
```

### Run Basic Benchmark

```bash
# Health check endpoint
python3 benchmark/benchmark.py \
  --url http://localhost:8100 \
  --endpoint /health \
  --concurrent 100 \
  --total 1000

# Chat endpoint
python3 benchmark/benchmark.py \
  --url http://localhost:8100 \
  --endpoint /chat \
  --method POST \
  --concurrent 50 \
  --duration 60 \
  --message "What is my order status?"
```

### Run Full Load Test Suite

```bash
./benchmark/load_test.sh
```

## Benchmark Script Usage

```bash
python3 benchmark/benchmark.py [OPTIONS]

Options:
  --url URL              API base URL (default: http://localhost:8100)
  --endpoint PATH        Endpoint to test (default: /health)
  --method METHOD        HTTP method: GET or POST (default: GET)
  --concurrent N         Concurrent requests (default: 100)
  --total N              Total requests (default: 1000)
  --duration SECONDS     Duration in seconds (overrides --total)
  --message TEXT         Test message for POST requests
  --output FILE          Save results to JSON file
```

## Test Scenarios

### 1. Light Load (100 req/s)
```bash
python3 benchmark/benchmark.py \
  --concurrent 10 \
  --duration 30 \
  --output results_light.json
```

### 2. Medium Load (500 req/s)
```bash
python3 benchmark/benchmark.py \
  --concurrent 50 \
  --duration 30 \
  --output results_medium.json
```

### 3. Heavy Load (1,000 req/s)
```bash
python3 benchmark/benchmark.py \
  --concurrent 100 \
  --duration 30 \
  --output results_heavy.json
```

### 4. Extreme Load (5,000 req/s)
```bash
python3 benchmark/benchmark.py \
  --concurrent 500 \
  --duration 30 \
  --output results_extreme.json
```

## Interpreting Results

### Key Metrics

- **Requests/Second**: Throughput capacity
- **P95 Response Time**: 95% of requests complete within this time
- **P99 Response Time**: 99% of requests complete within this time
- **Error Rate**: Percentage of failed requests

### Performance Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Health Check P95 | <100ms | <500ms | >1s |
| Chat Endpoint P95 | <2s | <5s | >10s |
| Error Rate | <0.1% | <1% | >5% |
| Throughput | >Target | >50% target | <50% target |

## Results Format

Results are saved as JSON with:
- Timestamp
- Configuration (concurrent, total, duration)
- Results (RPS, response times, error rate)

## Continuous Benchmarking

For CI/CD integration:

```bash
# Run benchmark and check results
python3 benchmark/benchmark.py \
  --concurrent 100 \
  --duration 60 \
  --output results.json

# Check if performance meets targets
python3 benchmark/check_performance.py results.json
```

## Troubleshooting

### Connection Errors
- Check if services are running
- Verify URL and port
- Check firewall settings

### Timeout Errors
- Increase timeout in script
- Check service health
- Review resource limits

### Low Throughput
- Check service capacity
- Review resource usage
- Verify network conditions
- Review application logs

