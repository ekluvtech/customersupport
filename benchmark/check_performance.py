#!/usr/bin/env python3
"""
Performance Checker
Validates benchmark results against performance targets
"""

import json
import sys
from typing import Dict, Any


PERFORMANCE_TARGETS = {
    "health": {
        "p95_max": 0.5,  # 500ms
        "error_rate_max": 0.1,  # 0.1%
        "min_rps": 100
    },
    "chat": {
        "p95_max": 5.0,  # 5 seconds
        "error_rate_max": 1.0,  # 1%
        "min_rps": 50
    }
}


def check_performance(results_file: str, endpoint_type: str = "health") -> bool:
    """Check if performance meets targets"""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data.get("results", {})
    config = data.get("config", {})
    endpoint = config.get("endpoint", "")
    
    # Determine endpoint type
    if "/chat" in endpoint:
        endpoint_type = "chat"
    else:
        endpoint_type = "health"
    
    targets = PERFORMANCE_TARGETS.get(endpoint_type, PERFORMANCE_TARGETS["health"])
    
    print(f"\n{'='*60}")
    print(f"Performance Check: {endpoint_type.upper()}")
    print(f"{'='*60}\n")
    
    # Check metrics
    p95 = results.get("p95_response_time", 0)
    error_rate = results.get("error_rate", 0)
    rps = results.get("requests_per_second", 0)
    
    all_passed = True
    
    # Check P95
    if p95 > targets["p95_max"]:
        print(f"❌ P95 Response Time: {p95*1000:.2f}ms (target: <{targets['p95_max']*1000}ms)")
        all_passed = False
    else:
        print(f"✅ P95 Response Time: {p95*1000:.2f}ms (target: <{targets['p95_max']*1000}ms)")
    
    # Check error rate
    if error_rate > targets["error_rate_max"]:
        print(f"❌ Error Rate: {error_rate:.2f}% (target: <{targets['error_rate_max']}%)")
        all_passed = False
    else:
        print(f"✅ Error Rate: {error_rate:.2f}% (target: <{targets['error_rate_max']}%)")
    
    # Check throughput
    if rps < targets["min_rps"]:
        print(f"❌ Throughput: {rps:.2f} req/s (target: >{targets['min_rps']} req/s)")
        all_passed = False
    else:
        print(f"✅ Throughput: {rps:.2f} req/s (target: >{targets['min_rps']} req/s)")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ All performance targets met!")
    else:
        print("❌ Some performance targets not met")
    print(f"{'='*60}\n")
    
    return all_passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_performance.py <results.json> [endpoint_type]")
        sys.exit(1)
    
    results_file = sys.argv[1]
    endpoint_type = sys.argv[2] if len(sys.argv) > 2 else "health"
    
    passed = check_performance(results_file, endpoint_type)
    sys.exit(0 if passed else 1)

