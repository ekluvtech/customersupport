# Scaling Guide - Quick Reference

## Scaling to 5k Requests/Second

### Quick Start

```bash
# 1. Start with scaled configuration
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d

# 2. Scale services
docker-compose up -d --scale agent-api=25 --scale mcp-server=10

# 3. Verify scaling
docker-compose ps
```

### Scaling Commands

```bash
# Scale to handle 1k req/s
docker-compose up -d --scale agent-api=10 --scale mcp-server=5

# Scale to handle 2.5k req/s
docker-compose up -d --scale agent-api=20 --scale mcp-server=8

# Scale to handle 5k req/s (target)
docker-compose up -d --scale agent-api=25 --scale mcp-server=10

# Scale down
docker-compose up -d --scale agent-api=5 --scale mcp-server=3
```

### Instance Recommendations

| Target RPS | API Instances | MCP Instances | Workers Total |
|------------|---------------|--------------|---------------|
| 100        | 3             | 2            | 12            |
| 500        | 10            | 5            | 40            |
| 1,000      | 15            | 7            | 60            |
| 2,500      | 20            | 8            | 80            |
| 5,000      | 25            | 10           | 100           |

### Load Balancer Configuration

The load balancers are automatically configured:
- **API LB**: `http://localhost:8100` → routes to agent-api instances
- **MCP LB**: `http://localhost:8000` → routes to mcp-server instances

### Monitoring

```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f agent-api

# Check metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### Benchmarking

```bash
# Quick benchmark
python3 benchmark/benchmark.py \
  --url http://localhost:8100 \
  --concurrent 500 \
  --duration 30

# Full load test
./benchmark/load_test.sh
```

### Performance Targets

- **5k req/s**: 25 API instances, 10 MCP instances
- **P95 latency**: <2s for chat, <500ms for health
- **Error rate**: <1%
- **CPU usage**: <70%
- **Memory usage**: <80%

See `PERFORMANCE.md` for detailed calculations and optimization strategies.

