# Performance & Scalability Guide

## Overview

This document provides performance benchmarks, capacity planning, and scaling strategies for the Customer Support application to handle up to **5,000 requests per second**.

## Back-of-the-Envelope Capacity Estimation

### System Components

1. **Frontend (Nginx)**: Static file serving
2. **Agent API (FastAPI/Uvicorn)**: Main API server
3. **MCP Server (FastAPI/Uvicorn)**: Integration server
4. **Database (PostgreSQL)**: Data persistence
5. **LLM Service (Vertex AI/OpenAI)**: External API calls

### Capacity Calculations

#### Single API Instance Capacity

**Assumptions:**
- Average request processing time: 200ms (including LLM call)
- Uvicorn workers: 4 per instance
- Worker concurrency: 1000 connections per worker
- CPU: 2 cores, Memory: 2GB

**Calculation:**
```
Throughput per worker = 1000 connections / 0.2s = 5,000 req/s per worker
Total per instance = 4 workers × 5,000 = 20,000 req/s (theoretical max)

Realistic capacity (70% utilization):
= 4 workers × 3,500 req/s = 14,000 req/s per instance
```

**However**, LLM calls are the bottleneck:
- LLM API latency: ~1-3 seconds
- Effective throughput: 4 workers / 2s = 2 req/s per instance (worst case)
- With async/overlapping: ~50-100 req/s per instance (realistic)

#### Scaled System (10 API Instances)

**Configuration:**
- 10 API instances
- 4 workers per instance = 40 total workers
- Load balancer (Nginx)

**Capacity:**
```
Realistic: 10 instances × 50-100 req/s = 500-1,000 req/s
With optimization: 10 instances × 200 req/s = 2,000 req/s
Target (5k req/s): Requires 25-50 instances or optimization
```

#### MCP Server Capacity

**Assumptions:**
- Average tool execution: 100-500ms
- 5 MCP server instances
- 2 workers per instance

**Capacity:**
```
Per instance: 2 workers / 0.2s = 10 req/s
5 instances: 5 × 10 = 50 req/s (sequential)
With async: 5 × 100 = 500 req/s
```

### Bottleneck Analysis

1. **LLM API Calls** (Primary bottleneck)
   - Vertex AI: ~1-3s per request
   - OpenAI: ~0.5-2s per request
   - **Solution**: Caching, request batching, async processing

2. **Database Queries**
   - Simple queries: <10ms
   - Complex queries: 50-200ms
   - **Solution**: Connection pooling, read replicas, caching

3. **Network Latency**
   - Internal: <1ms
   - External APIs: 50-200ms
   - **Solution**: Connection pooling, keep-alive

### Estimated Capacity by Configuration

| Configuration | Instances | Workers | Est. Capacity (req/s) | Notes |
|--------------|-----------|--------|---------------------|-------|
| Single instance | 1 | 4 | 50-100 | Development |
| Small scale | 3 | 12 | 300-600 | Testing |
| Medium scale | 10 | 40 | 1,000-2,000 | Production |
| Large scale | 25 | 100 | 2,500-5,000 | High traffic |
| Extreme scale | 50 | 200 | 5,000-10,000 | Peak load |

**Note**: Actual capacity depends on:
- LLM API response times
- Database performance
- Network conditions
- Request complexity

## Scaling Configuration

### Docker Compose Scaling

```bash
# Scale to handle 5k req/s
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d

# Scale specific services
docker-compose up -d --scale agent-api=25 --scale mcp-server=10
```

### Recommended Production Setup

```yaml
# For 5k req/s target
agent-api:
  replicas: 25
  workers_per_instance: 4
  total_workers: 100

mcp-server:
  replicas: 10
  workers_per_instance: 2
  total_workers: 20

nginx-lb:
  worker_connections: 10000
  keepalive: 32
```

## Performance Optimization Strategies

### 1. Caching

**Redis Cache Layer:**
- Cache LLM responses for similar queries (TTL: 1 hour)
- Cache database query results (TTL: 5 minutes)
- Cache user session data

**Expected Impact:**
- Reduce LLM calls by 30-50%
- Reduce database load by 60-80%
- Improve response time by 50-70%

### 2. Connection Pooling

**Database:**
- Pool size: 20 connections per instance
- Max overflow: 10
- Total: 25 instances × 20 = 500 connections

**HTTP Clients:**
- Keep-alive connections
- Connection pool: 100 per instance

### 3. Async Processing

- Use async/await for all I/O operations
- Process LLM calls asynchronously
- Batch database queries

### 4. Load Balancing

- Nginx with least_conn algorithm
- Health checks every 10s
- Failover time: <30s

### 5. Database Optimization

- Read replicas for queries
- Write to primary, read from replicas
- Index optimization
- Query result caching

## Benchmarking

### Running Benchmarks

```bash
# Quick health check benchmark
python3 benchmark/benchmark.py \
  --url http://localhost:8100 \
  --endpoint /health \
  --concurrent 100 \
  --total 1000

# Chat endpoint benchmark
python3 benchmark/benchmark.py \
  --url http://localhost:8100 \
  --endpoint /chat \
  --method POST \
  --concurrent 50 \
  --duration 60 \
  --message "What is my order status?"

# Full load test suite
./benchmark/load_test.sh
```

### Benchmark Results Interpretation

**Good Performance:**
- P95 response time < 500ms (health check)
- P95 response time < 3s (chat endpoint)
- Error rate < 0.1%
- CPU utilization < 70%
- Memory utilization < 80%

**Scaling Triggers:**
- P95 response time > 1s (health) or > 5s (chat)
- Error rate > 1%
- CPU utilization > 80%
- Request queue depth > 100

## Monitoring

### Key Metrics

1. **Request Rate**: Requests per second
2. **Response Time**: P50, P95, P99 latencies
3. **Error Rate**: Percentage of failed requests
4. **Throughput**: Successful requests per second
5. **Resource Usage**: CPU, memory, network
6. **Queue Depth**: Pending requests
7. **LLM API Latency**: External API response times

### Monitoring Setup

```bash
# Start with monitoring
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

### Grafana Dashboards

Import dashboards for:
- API performance metrics
- System resource usage
- Error rates and alerts
- LLM API latency tracking

## Load Testing Scenarios

### Scenario 1: Baseline (100 req/s)
- **Purpose**: Verify basic functionality
- **Duration**: 5 minutes
- **Expected**: <1% error rate, <500ms P95

### Scenario 2: Normal Load (500 req/s)
- **Purpose**: Production baseline
- **Duration**: 30 minutes
- **Expected**: <0.5% error rate, <1s P95

### Scenario 3: Peak Load (2,000 req/s)
- **Purpose**: Peak traffic simulation
- **Duration**: 15 minutes
- **Expected**: <1% error rate, <2s P95

### Scenario 4: Stress Test (5,000 req/s)
- **Purpose**: Maximum capacity
- **Duration**: 10 minutes
- **Expected**: <5% error rate, graceful degradation

### Scenario 5: Endurance Test (1,000 req/s)
- **Purpose**: Long-term stability
- **Duration**: 2 hours
- **Expected**: Stable performance, no memory leaks

## Capacity Planning

### Growth Projections

| Month | Expected Traffic | Required Instances | Cost Estimate |
|-------|----------------|-------------------|---------------|
| 1 | 100 req/s | 3 API, 2 MCP | $200/month |
| 3 | 500 req/s | 10 API, 5 MCP | $500/month |
| 6 | 2,000 req/s | 25 API, 10 MCP | $1,200/month |
| 12 | 5,000 req/s | 50 API, 20 MCP | $2,500/month |

### Auto-Scaling Rules

```yaml
# Kubernetes HPA example
minReplicas: 10
maxReplicas: 50
targetCPUUtilization: 70
targetMemoryUtilization: 80
```

## Performance Tuning Checklist

- [ ] Enable Redis caching
- [ ] Configure connection pooling
- [ ] Optimize database queries
- [ ] Enable response compression
- [ ] Configure CDN for static assets
- [ ] Implement request rate limiting
- [ ] Set up monitoring and alerts
- [ ] Configure auto-scaling
- [ ] Optimize LLM API calls (batching, caching)
- [ ] Use database read replicas
- [ ] Enable HTTP/2
- [ ] Configure keep-alive connections

## Troubleshooting Performance Issues

### High Response Times

1. Check LLM API latency
2. Review database query performance
3. Check network connectivity
4. Monitor resource usage (CPU/memory)
5. Review application logs for errors

### High Error Rates

1. Check service health endpoints
2. Review error logs
3. Check resource limits
4. Verify database connectivity
5. Check external API status

### Resource Exhaustion

1. Scale up instances
2. Increase resource limits
3. Optimize memory usage
4. Enable caching to reduce load
5. Review and optimize code

## Conclusion

With proper scaling and optimization:
- **Target**: 5,000 requests/second
- **Required**: 25-50 API instances, 10-20 MCP instances
- **Optimization**: Caching, connection pooling, async processing
- **Monitoring**: Essential for maintaining performance

Actual capacity will vary based on:
- Request complexity
- LLM API performance
- Database performance
- Network conditions
- Caching effectiveness

