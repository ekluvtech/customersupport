#!/usr/bin/env python3
"""
Performance Benchmarking Script
Tests the Customer Support API under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import argparse


@dataclass
class BenchmarkResult:
    """Benchmark result data"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    requests_per_second: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float


class BenchmarkRunner:
    """Runs benchmarks against the API"""
    
    def __init__(self, base_url: str = "http://localhost:8100"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=1000, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> tuple:
        """Make a single HTTP request"""
        start_time = time.time()
        try:
            if method == "GET":
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    await response.read()
                    return (response.status == 200, response_time, None)
            elif method == "POST":
                async with self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=data
                ) as response:
                    response_time = time.time() - start_time
                    await response.read()
                    return (response.status == 200, response_time, None)
        except Exception as e:
            response_time = time.time() - start_time
            return (False, response_time, str(e))
    
    async def run_benchmark(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
        concurrent_requests: int = 100,
        total_requests: int = 1000,
        duration: float = None
    ) -> BenchmarkResult:
        """Run a benchmark test"""
        print(f"\n{'='*60}")
        print(f"Benchmark: {method} {endpoint}")
        print(f"Concurrent: {concurrent_requests}, Total: {total_requests}")
        if duration:
            print(f"Duration: {duration}s")
        print(f"{'='*60}\n")
        
        response_times: List[float] = []
        successful = 0
        failed = 0
        errors: List[str] = []
        
        start_time = time.time()
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def worker():
            nonlocal successful, failed
            requests_made = 0
            
            while True:
                if duration:
                    if time.time() - start_time >= duration:
                        break
                elif requests_made >= total_requests:
                    break
                
                async with semaphore:
                    success, resp_time, error = await self.make_request(endpoint, method, data)
                    response_times.append(resp_time)
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        if error:
                            errors.append(error)
                    
                    requests_made += 1
                    
                    # Progress indicator
                    if requests_made % 100 == 0:
                        elapsed = time.time() - start_time
                        rps = requests_made / elapsed if elapsed > 0 else 0
                        print(f"  Progress: {requests_made} requests, {rps:.2f} req/s", end='\r')
        
        # Create workers
        workers = [worker() for _ in range(concurrent_requests)]
        await asyncio.gather(*workers)
        
        total_time = time.time() - start_time
        total_requests_made = successful + failed
        
        # Calculate statistics
        if response_times:
            response_times.sort()
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50 = response_times[int(len(response_times) * 0.50)]
            p95 = response_times[int(len(response_times) * 0.95)]
            p99 = response_times[int(len(response_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50 = p95 = p99 = 0
        
        requests_per_second = total_requests_made / total_time if total_time > 0 else 0
        error_rate = (failed / total_requests_made * 100) if total_requests_made > 0 else 0
        
        result = BenchmarkResult(
            total_requests=total_requests_made,
            successful_requests=successful,
            failed_requests=failed,
            total_time=total_time,
            requests_per_second=requests_per_second,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50,
            p95_response_time=p95,
            p99_response_time=p99,
            error_rate=error_rate
        )
        
        return result
    
    def print_results(self, result: BenchmarkResult):
        """Print benchmark results"""
        print(f"\n{'='*60}")
        print("BENCHMARK RESULTS")
        print(f"{'='*60}")
        print(f"Total Requests:      {result.total_requests:,}")
        print(f"Successful:           {result.successful_requests:,}")
        print(f"Failed:               {result.failed_requests:,}")
        print(f"Error Rate:           {result.error_rate:.2f}%")
        print(f"Total Time:           {result.total_time:.2f}s")
        print(f"Requests/Second:      {result.requests_per_second:,.2f}")
        print(f"\nResponse Times:")
        print(f"  Average:            {result.avg_response_time*1000:.2f}ms")
        print(f"  Min:                {result.min_response_time*1000:.2f}ms")
        print(f"  Max:                {result.max_response_time*1000:.2f}ms")
        print(f"  P50 (Median):        {result.p50_response_time*1000:.2f}ms")
        print(f"  P95:                {result.p95_response_time*1000:.2f}ms")
        print(f"  P99:                {result.p99_response_time*1000:.2f}ms")
        print(f"{'='*60}\n")


async def main():
    parser = argparse.ArgumentParser(description="Benchmark Customer Support API")
    parser.add_argument("--url", default="http://localhost:8100", help="API base URL")
    parser.add_argument("--concurrent", type=int, default=100, help="Concurrent requests")
    parser.add_argument("--total", type=int, default=1000, help="Total requests")
    parser.add_argument("--duration", type=float, help="Duration in seconds (overrides --total)")
    parser.add_argument("--endpoint", default="/health", help="Endpoint to test")
    parser.add_argument("--method", default="GET", choices=["GET", "POST"], help="HTTP method")
    parser.add_argument("--message", default="What is the status of my order?", help="Test message for POST")
    parser.add_argument("--output", help="Output JSON file for results")
    
    args = parser.parse_args()
    
    data = None
    if args.method == "POST":
        data = {
            "message": args.message,
            "user_id": "benchmark_user",
            "channel": "web"
        }
    
    async with BenchmarkRunner(args.url) as runner:
        result = await runner.run_benchmark(
            endpoint=args.endpoint,
            method=args.method,
            data=data,
            concurrent_requests=args.concurrent,
            total_requests=args.total,
            duration=args.duration
        )
        
        runner.print_results(result)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "config": {
                        "url": args.url,
                        "endpoint": args.endpoint,
                        "method": args.method,
                        "concurrent": args.concurrent,
                        "total": args.total,
                        "duration": args.duration
                    },
                    "results": {
                        "total_requests": result.total_requests,
                        "successful_requests": result.successful_requests,
                        "failed_requests": result.failed_requests,
                        "total_time": result.total_time,
                        "requests_per_second": result.requests_per_second,
                        "avg_response_time": result.avg_response_time,
                        "min_response_time": result.min_response_time,
                        "max_response_time": result.max_response_time,
                        "p50_response_time": result.p50_response_time,
                        "p95_response_time": result.p95_response_time,
                        "p99_response_time": result.p99_response_time,
                        "error_rate": result.error_rate
                    }
                }, f, indent=2)
            print(f"Results saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())

