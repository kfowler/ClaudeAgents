# Archaeological Intelligence Layer - Performance Benchmarks Plan

## Executive Summary

This document defines the comprehensive performance benchmark suite for the Archaeological Intelligence Layer (AIL). The benchmarks verify that AIL meets its performance targets: <1s p95 latency, 80% cache hit rate, and <100MB memory per agent.

## Benchmark Categories

### 1. Latency Benchmarks
- Single query latency (cold/warm)
- Concurrent query latency
- Batch processing latency
- Degraded mode latency

### 2. Throughput Benchmarks
- Queries per second
- Concurrent agent handling
- Batch processing efficiency

### 3. Resource Benchmarks
- Memory usage patterns
- CPU utilization
- Network I/O patterns

### 4. Cache Benchmarks
- Hit rate analysis
- Eviction patterns
- Warming effectiveness

### 5. Resilience Benchmarks
- Circuit breaker behavior
- Degradation handling
- Recovery patterns

## Benchmark Implementation

### Core Benchmark Suite

```python
import asyncio
import time
import statistics
import psutil
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np

@dataclass
class BenchmarkResult:
    """Individual benchmark result."""

    name: str
    category: str
    metrics: Dict[str, Any]
    passed: bool
    duration_seconds: float
    timestamp: datetime

    def to_json(self) -> str:
        """Convert to JSON for reporting."""
        data = asdict(self)
        data['timestamp'] = data['timestamp'].isoformat()
        return json.dumps(data, indent=2)

@dataclass
class BenchmarkReport:
    """Complete benchmark report."""

    results: List[BenchmarkResult]
    summary: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def success_rate(self) -> float:
        total = len(self.results)
        return self.passed_count / total if total > 0 else 0.0

    def generate_html_report(self) -> str:
        """Generate HTML report for visualization."""
        # Implementation for HTML report generation
        pass

class AILBenchmarkSuite:
    """Complete benchmark suite for Archaeological Intelligence Layer."""

    def __init__(
        self,
        provider: ArchaeologyContextProvider,
        test_repo_path: str,
        test_files: List[str]
    ):
        self.provider = provider
        self.test_repo_path = test_repo_path
        self.test_files = test_files
        self.results: List[BenchmarkResult] = []
        self.start_time = None
        self.end_time = None

    async def run_all_benchmarks(self) -> BenchmarkReport:
        """Run complete benchmark suite."""

        self.start_time = datetime.now()
        print("Starting AIL Performance Benchmarks...")
        print("=" * 60)

        # 1. Latency Benchmarks
        await self.run_latency_benchmarks()

        # 2. Throughput Benchmarks
        await self.run_throughput_benchmarks()

        # 3. Resource Benchmarks
        await self.run_resource_benchmarks()

        # 4. Cache Benchmarks
        await self.run_cache_benchmarks()

        # 5. Resilience Benchmarks
        await self.run_resilience_benchmarks()

        self.end_time = datetime.now()

        # Generate report
        report = self.generate_report()

        print("\nBenchmark Suite Completed!")
        print(f"Total Duration: {(self.end_time - self.start_time).total_seconds():.2f}s")
        print(f"Success Rate: {report.success_rate:.1%}")

        return report
```

### Latency Benchmarks

```python
async def run_latency_benchmarks(self):
    """Test various latency scenarios."""

    print("\n1. LATENCY BENCHMARKS")
    print("-" * 40)

    # 1.1 Cold Start Latency
    result = await self.benchmark_cold_start_latency()
    self.results.append(result)

    # 1.2 Warm Cache Latency
    result = await self.benchmark_warm_cache_latency()
    self.results.append(result)

    # 1.3 Concurrent Query Latency
    result = await self.benchmark_concurrent_latency()
    self.results.append(result)

    # 1.4 Batch Processing Latency
    result = await self.benchmark_batch_latency()
    self.results.append(result)

async def benchmark_cold_start_latency(self) -> BenchmarkResult:
    """Benchmark cold start (no cache) latency."""

    print("  Testing cold start latency...")

    # Clear all caches
    self.provider.clear_cache("all")

    latencies = []
    queries = [
        "What are the recent changes?",
        "Are there any security issues?",
        "Who wrote this code?",
        "What is the test coverage?",
        "Why was this designed this way?"
    ]

    for file_path in self.test_files[:10]:
        for query in queries:
            start = time.perf_counter()

            try:
                context = await self.provider.get_context(
                    file_path=file_path,
                    question=query
                )
                latency = (time.perf_counter() - start) * 1000  # ms
                latencies.append(latency)
            except Exception as e:
                print(f"    Error: {e}")
                latencies.append(2000)  # Penalty for errors

    # Calculate statistics
    p50 = statistics.median(latencies)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    # Success criteria
    passed = p95 < 1000  # p95 < 1s

    metrics = {
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "mean_ms": statistics.mean(latencies),
        "std_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        "samples": len(latencies)
    }

    print(f"    p50: {p50:.0f}ms, p95: {p95:.0f}ms, p99: {p99:.0f}ms")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="cold_start_latency",
        category="latency",
        metrics=metrics,
        passed=passed,
        duration_seconds=sum(latencies) / 1000,
        timestamp=datetime.now()
    )

async def benchmark_warm_cache_latency(self) -> BenchmarkResult:
    """Benchmark warm cache latency."""

    print("  Testing warm cache latency...")

    # Warm the cache first
    await self.provider.warm_cache(agent_type="code-architect")

    latencies = []
    cache_hits = 0
    total_queries = 0

    # Same queries multiple times to ensure cache hits
    for _ in range(3):
        for file_path in self.test_files[:5]:
            query = "What are the recent changes?"

            start = time.perf_counter()
            context = await self.provider.get_context(
                file_path=file_path,
                question=query
            )
            latency = (time.perf_counter() - start) * 1000

            latencies.append(latency)
            if context.cache_hit:
                cache_hits += 1
            total_queries += 1

    # Calculate statistics
    p50 = statistics.median(latencies)
    p95 = np.percentile(latencies, 95)
    hit_rate = cache_hits / total_queries if total_queries > 0 else 0

    # Success criteria
    passed = p50 < 50 and hit_rate > 0.8  # Fast and high hit rate

    metrics = {
        "p50_ms": p50,
        "p95_ms": p95,
        "cache_hit_rate": hit_rate,
        "samples": len(latencies)
    }

    print(f"    p50: {p50:.0f}ms, Hit Rate: {hit_rate:.1%}")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="warm_cache_latency",
        category="latency",
        metrics=metrics,
        passed=passed,
        duration_seconds=sum(latencies) / 1000,
        timestamp=datetime.now()
    )
```

### Throughput Benchmarks

```python
async def run_throughput_benchmarks(self):
    """Test throughput capabilities."""

    print("\n2. THROUGHPUT BENCHMARKS")
    print("-" * 40)

    # 2.1 Queries Per Second
    result = await self.benchmark_queries_per_second()
    self.results.append(result)

    # 2.2 Concurrent Agents
    result = await self.benchmark_concurrent_agents()
    self.results.append(result)

    # 2.3 Batch Efficiency
    result = await self.benchmark_batch_efficiency()
    self.results.append(result)

async def benchmark_queries_per_second(self) -> BenchmarkResult:
    """Benchmark maximum queries per second."""

    print("  Testing queries per second...")

    duration = 10  # seconds
    queries_completed = 0
    errors = 0
    start_time = time.perf_counter()

    async def query_worker():
        nonlocal queries_completed, errors
        while time.perf_counter() - start_time < duration:
            try:
                file = self.test_files[queries_completed % len(self.test_files)]
                await self.provider.get_context(
                    file_path=file,
                    question="What changed?",
                    timeout=2.0
                )
                queries_completed += 1
            except Exception:
                errors += 1

    # Run multiple workers
    workers = [query_worker() for _ in range(5)]
    await asyncio.gather(*workers)

    actual_duration = time.perf_counter() - start_time
    qps = queries_completed / actual_duration
    error_rate = errors / (queries_completed + errors) if queries_completed + errors > 0 else 0

    # Success criteria
    passed = qps > 10 and error_rate < 0.05

    metrics = {
        "queries_per_second": qps,
        "total_queries": queries_completed,
        "errors": errors,
        "error_rate": error_rate,
        "duration_seconds": actual_duration
    }

    print(f"    QPS: {qps:.1f}, Errors: {error_rate:.1%}")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="queries_per_second",
        category="throughput",
        metrics=metrics,
        passed=passed,
        duration_seconds=actual_duration,
        timestamp=datetime.now()
    )

async def benchmark_concurrent_agents(self) -> BenchmarkResult:
    """Benchmark handling multiple concurrent agents."""

    print("  Testing concurrent agents...")

    agent_types = [
        "security-audit-specialist",
        "code-architect",
        "qa-test-engineer",
        "debugging-specialist",
        "frontend-performance-specialist"
    ]

    async def agent_simulation(agent_type: str, num_queries: int):
        """Simulate an agent making queries."""
        latencies = []
        for i in range(num_queries):
            file = self.test_files[i % len(self.test_files)]
            start = time.perf_counter()

            try:
                await self.provider.get_context(
                    file_path=file,
                    question=f"Query from {agent_type}",
                    agent_type=agent_type
                )
                latencies.append((time.perf_counter() - start) * 1000)
            except Exception:
                latencies.append(2000)

        return latencies

    # Run agents concurrently
    start = time.perf_counter()
    results = await asyncio.gather(*[
        agent_simulation(agent_type, 10)
        for agent_type in agent_types
    ])
    duration = time.perf_counter() - start

    # Analyze results
    all_latencies = [lat for agent_lats in results for lat in agent_lats]
    p95 = np.percentile(all_latencies, 95)

    # Success criteria
    passed = p95 < 1500  # Reasonable latency under load

    metrics = {
        "concurrent_agents": len(agent_types),
        "total_queries": len(all_latencies),
        "p95_latency_ms": p95,
        "duration_seconds": duration
    }

    print(f"    Agents: {len(agent_types)}, p95: {p95:.0f}ms")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="concurrent_agents",
        category="throughput",
        metrics=metrics,
        passed=passed,
        duration_seconds=duration,
        timestamp=datetime.now()
    )
```

### Resource Benchmarks

```python
async def run_resource_benchmarks(self):
    """Test resource usage patterns."""

    print("\n3. RESOURCE BENCHMARKS")
    print("-" * 40)

    # 3.1 Memory Usage
    result = await self.benchmark_memory_usage()
    self.results.append(result)

    # 3.2 CPU Utilization
    result = await self.benchmark_cpu_usage()
    self.results.append(result)

async def benchmark_memory_usage(self) -> BenchmarkResult:
    """Benchmark memory usage patterns."""

    print("  Testing memory usage...")

    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

    memory_samples = []

    # Perform various operations
    for i in range(20):
        # Make queries
        for file in self.test_files[:5]:
            await self.provider.get_context(
                file_path=file,
                question=f"Query {i}"
            )

        # Sample memory
        current_memory = process.memory_info().rss / (1024 * 1024)
        memory_samples.append(current_memory - initial_memory)

    # Calculate statistics
    peak_memory = max(memory_samples)
    avg_memory = statistics.mean(memory_samples)

    # Success criteria
    passed = peak_memory < 100  # Less than 100MB overhead

    metrics = {
        "initial_memory_mb": initial_memory,
        "peak_memory_mb": peak_memory,
        "avg_memory_mb": avg_memory,
        "samples": len(memory_samples)
    }

    print(f"    Peak: {peak_memory:.1f}MB, Avg: {avg_memory:.1f}MB")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="memory_usage",
        category="resource",
        metrics=metrics,
        passed=passed,
        duration_seconds=0,
        timestamp=datetime.now()
    )

async def benchmark_cpu_usage(self) -> BenchmarkResult:
    """Benchmark CPU utilization."""

    print("  Testing CPU usage...")

    process = psutil.Process()
    cpu_samples = []

    # Monitor CPU during load
    async def monitor_cpu():
        for _ in range(10):
            cpu_percent = process.cpu_percent(interval=0.1)
            cpu_samples.append(cpu_percent)
            await asyncio.sleep(0.1)

    # Generate load
    async def generate_load():
        for _ in range(20):
            await self.provider.get_context(
                file_path=self.test_files[0],
                question="CPU test query"
            )

    # Run monitoring and load generation concurrently
    await asyncio.gather(monitor_cpu(), generate_load())

    # Calculate statistics
    avg_cpu = statistics.mean(cpu_samples) if cpu_samples else 0
    peak_cpu = max(cpu_samples) if cpu_samples else 0

    # Success criteria
    passed = avg_cpu < 25  # Less than 25% average CPU

    metrics = {
        "avg_cpu_percent": avg_cpu,
        "peak_cpu_percent": peak_cpu,
        "samples": len(cpu_samples)
    }

    print(f"    Avg CPU: {avg_cpu:.1f}%, Peak: {peak_cpu:.1f}%")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="cpu_usage",
        category="resource",
        metrics=metrics,
        passed=passed,
        duration_seconds=1,
        timestamp=datetime.now()
    )
```

### Cache Benchmarks

```python
async def run_cache_benchmarks(self):
    """Test cache effectiveness."""

    print("\n4. CACHE BENCHMARKS")
    print("-" * 40)

    # 4.1 Hit Rate Analysis
    result = await self.benchmark_cache_hit_rate()
    self.results.append(result)

    # 4.2 Cache Warming
    result = await self.benchmark_cache_warming()
    self.results.append(result)

    # 4.3 Eviction Patterns
    result = await self.benchmark_cache_eviction()
    self.results.append(result)

async def benchmark_cache_hit_rate(self) -> BenchmarkResult:
    """Benchmark cache hit rates."""

    print("  Testing cache hit rate...")

    # Clear cache first
    self.provider.clear_cache("all")

    queries = [
        "What are the recent changes?",
        "Are there security issues?",
        "Who wrote this?"
    ]

    l1_hits = 0
    l2_hits = 0
    total = 0

    # First pass - populate cache
    for file in self.test_files[:10]:
        for query in queries:
            context = await self.provider.get_context(file, query)
            total += 1

    # Second pass - should hit cache
    for file in self.test_files[:10]:
        for query in queries:
            context = await self.provider.get_context(file, query)
            if context.cache_hit:
                if context.retrieval_time_ms < 20:
                    l1_hits += 1
                else:
                    l2_hits += 1
            total += 1

    # Calculate rates
    l1_hit_rate = l1_hits / (total / 2)  # Second pass only
    l2_hit_rate = l2_hits / (total / 2)
    overall_hit_rate = (l1_hits + l2_hits) / (total / 2)

    # Success criteria
    passed = overall_hit_rate > 0.8

    metrics = {
        "l1_hit_rate": l1_hit_rate,
        "l2_hit_rate": l2_hit_rate,
        "overall_hit_rate": overall_hit_rate,
        "total_queries": total
    }

    print(f"    L1: {l1_hit_rate:.1%}, L2: {l2_hit_rate:.1%}, Overall: {overall_hit_rate:.1%}")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="cache_hit_rate",
        category="cache",
        metrics=metrics,
        passed=passed,
        duration_seconds=0,
        timestamp=datetime.now()
    )

async def benchmark_cache_warming(self) -> BenchmarkResult:
    """Benchmark cache warming effectiveness."""

    print("  Testing cache warming...")

    # Clear cache
    self.provider.clear_cache("all")

    # Warm cache
    start = time.perf_counter()
    warmed = await self.provider.warm_cache(
        agent_type="security-audit-specialist"
    )
    warming_time = time.perf_counter() - start

    # Test hit rate after warming
    hits = 0
    total = 0

    test_queries = [
        "What security vulnerabilities were found?",
        "Are there any authentication issues?"
    ]

    for file in self.test_files[:5]:
        for query in test_queries:
            context = await self.provider.get_context(
                file_path=file,
                question=query,
                agent_type="security-audit-specialist"
            )
            if context.cache_hit:
                hits += 1
            total += 1

    hit_rate = hits / total if total > 0 else 0

    # Success criteria
    passed = hit_rate > 0.5 and warming_time < 10

    metrics = {
        "entries_warmed": warmed,
        "warming_time_seconds": warming_time,
        "post_warm_hit_rate": hit_rate
    }

    print(f"    Warmed: {warmed}, Time: {warming_time:.1f}s, Hit Rate: {hit_rate:.1%}")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="cache_warming",
        category="cache",
        metrics=metrics,
        passed=passed,
        duration_seconds=warming_time,
        timestamp=datetime.now()
    )
```

### Resilience Benchmarks

```python
async def run_resilience_benchmarks(self):
    """Test resilience and degradation handling."""

    print("\n5. RESILIENCE BENCHMARKS")
    print("-" * 40)

    # 5.1 Circuit Breaker
    result = await self.benchmark_circuit_breaker()
    self.results.append(result)

    # 5.2 Degraded Mode
    result = await self.benchmark_degraded_mode()
    self.results.append(result)

    # 5.3 Recovery
    result = await self.benchmark_recovery()
    self.results.append(result)

async def benchmark_degraded_mode(self) -> BenchmarkResult:
    """Benchmark degraded mode operation."""

    print("  Testing degraded mode...")

    # Simulate degradation by disconnecting components
    # This would be done by mocking in actual tests

    degraded_latencies = []
    degraded_contexts = []

    for file in self.test_files[:5]:
        start = time.perf_counter()

        # Force degraded mode (would be done via mock)
        context = await self.provider.get_context(
            file_path=file,
            question="Test in degraded mode"
        )

        latency = (time.perf_counter() - start) * 1000
        degraded_latencies.append(latency)

        if context.degraded_mode:
            degraded_contexts.append(context)

    # Calculate statistics
    if degraded_latencies:
        p95 = np.percentile(degraded_latencies, 95)
        degradation_rate = len(degraded_contexts) / len(degraded_latencies)
    else:
        p95 = 0
        degradation_rate = 0

    # Success criteria
    passed = p95 < 2000  # Still reasonable in degraded mode

    metrics = {
        "degraded_p95_ms": p95,
        "degradation_rate": degradation_rate,
        "samples": len(degraded_latencies)
    }

    print(f"    Degraded p95: {p95:.0f}ms")
    print(f"    Result: {'PASS' if passed else 'FAIL'}")

    return BenchmarkResult(
        name="degraded_mode",
        category="resilience",
        metrics=metrics,
        passed=passed,
        duration_seconds=sum(degraded_latencies) / 1000,
        timestamp=datetime.now()
    )
```

### Report Generation

```python
def generate_report(self) -> BenchmarkReport:
    """Generate comprehensive benchmark report."""

    # Calculate summary statistics
    summary = {
        "total_benchmarks": len(self.results),
        "passed": self.passed_count,
        "failed": self.failed_count,
        "success_rate": self.success_rate,
        "duration_seconds": (self.end_time - self.start_time).total_seconds()
    }

    # Category summaries
    categories = {}
    for result in self.results:
        if result.category not in categories:
            categories[result.category] = {"passed": 0, "failed": 0}

        if result.passed:
            categories[result.category]["passed"] += 1
        else:
            categories[result.category]["failed"] += 1

    summary["categories"] = categories

    # Key metrics
    latency_results = [r for r in self.results if r.category == "latency"]
    if latency_results:
        p95_values = [r.metrics.get("p95_ms", 0) for r in latency_results]
        summary["avg_p95_latency"] = statistics.mean(p95_values)

    cache_results = [r for r in self.results if r.category == "cache"]
    if cache_results:
        hit_rates = [r.metrics.get("overall_hit_rate", 0) for r in cache_results]
        summary["avg_cache_hit_rate"] = statistics.mean(hit_rates)

    # Generate recommendations
    recommendations = self.generate_recommendations()

    return BenchmarkReport(
        results=self.results,
        summary=summary,
        recommendations=recommendations,
        timestamp=datetime.now()
    )

def generate_recommendations(self) -> List[str]:
    """Generate performance recommendations based on results."""

    recommendations = []

    # Analyze latency
    latency_results = [r for r in self.results if r.category == "latency"]
    for result in latency_results:
        if not result.passed:
            if "cold_start" in result.name:
                recommendations.append(
                    "Cold start latency is high. Consider implementing more aggressive cache warming."
                )
            elif "concurrent" in result.name:
                recommendations.append(
                    "Concurrent query latency is high. Consider increasing connection pool size."
                )

    # Analyze cache
    cache_results = [r for r in self.results if r.category == "cache"]
    for result in cache_results:
        if not result.passed:
            if result.metrics.get("overall_hit_rate", 1) < 0.8:
                recommendations.append(
                    f"Cache hit rate is {result.metrics['overall_hit_rate']:.1%}. "
                    "Consider increasing cache size or TTL."
                )

    # Analyze resources
    resource_results = [r for r in self.results if r.category == "resource"]
    for result in resource_results:
        if not result.passed:
            if "memory" in result.name:
                peak = result.metrics.get("peak_memory_mb", 0)
                recommendations.append(
                    f"Peak memory usage is {peak:.1f}MB. Consider optimizing data structures."
                )

    # General recommendations
    if self.success_rate < 0.8:
        recommendations.append(
            "Overall success rate is below 80%. Review failed benchmarks and optimize accordingly."
        )

    return recommendations
```

## Benchmark Execution Script

```python
#!/usr/bin/env python3
"""
AIL Performance Benchmark Runner

Usage:
    python benchmark_ail.py [--config CONFIG] [--output OUTPUT] [--verbose]
"""

import argparse
import asyncio
import sys
from pathlib import Path

async def main():
    parser = argparse.ArgumentParser(description="Run AIL performance benchmarks")
    parser.add_argument(
        "--config",
        default="benchmark_config.json",
        help="Configuration file path"
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path to test"
    )

    args = parser.parse_args()

    # Load configuration
    if Path(args.config).exists():
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = {
            "test_files": ["src/main.py", "src/api.py", "src/auth.py"],
            "cache_config": {
                "l1_max_size": 1000,
                "l2_enabled": True
            },
            "performance_config": {
                "max_concurrent_requests": 10
            }
        }

    # Initialize provider
    provider = ArchaeologyContextProvider(
        repo_path=args.repo,
        cache_config=CacheConfig(**config.get("cache_config", {})),
        performance_config=PerformanceConfig(**config.get("performance_config", {}))
    )

    # Initialize benchmark suite
    suite = AILBenchmarkSuite(
        provider=provider,
        test_repo_path=args.repo,
        test_files=config.get("test_files", [])
    )

    # Run benchmarks
    report = await suite.run_all_benchmarks()

    # Save results
    with open(args.output, 'w') as f:
        json.dump(asdict(report), f, indent=2, default=str)

    print(f"\nResults saved to {args.output}")

    # Generate HTML report
    html_path = args.output.replace('.json', '.html')
    with open(html_path, 'w') as f:
        f.write(report.generate_html_report())

    print(f"HTML report saved to {html_path}")

    # Exit with appropriate code
    sys.exit(0 if report.success_rate > 0.8 else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Continuous Benchmarking

### GitHub Actions Workflow

```yaml
name: AIL Performance Benchmarks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  benchmark:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-benchmark

      - name: Run benchmarks
        run: |
          python benchmark_ail.py \
            --repo . \
            --output results/benchmark_$(date +%Y%m%d).json \
            --verbose

      - name: Compare with baseline
        run: |
          python compare_benchmarks.py \
            --baseline results/baseline.json \
            --current results/benchmark_$(date +%Y%m%d).json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: results/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('results/comparison.json'));

            let comment = '## Performance Benchmark Results\n\n';
            comment += `Success Rate: ${results.success_rate}%\n\n`;

            if (results.regressions.length > 0) {
              comment += '### ⚠️ Performance Regressions\n';
              results.regressions.forEach(r => {
                comment += `- ${r.name}: ${r.delta}% slower\n`;
              });
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

## Success Criteria Summary

| Category | Metric | Target | Priority |
|----------|--------|--------|----------|
| **Latency** | p95 single query | <1000ms | Critical |
| **Latency** | p50 cached query | <50ms | High |
| **Throughput** | Queries per second | >10 | High |
| **Throughput** | Concurrent agents | 10 | Critical |
| **Cache** | Overall hit rate | >80% | Critical |
| **Cache** | L1 hit rate | >40% | High |
| **Resources** | Memory per agent | <100MB | Critical |
| **Resources** | CPU utilization | <25% | Medium |
| **Resilience** | Degraded p95 | <2000ms | High |
| **Resilience** | Circuit breaker | Working | Critical |

## Monitoring Dashboard

```python
class BenchmarkDashboard:
    """Real-time monitoring dashboard for benchmarks."""

    def __init__(self):
        self.metrics = []
        self.start_time = datetime.now()

    def update_metrics(self, metric: Dict[str, Any]):
        """Update dashboard with new metrics."""
        self.metrics.append({
            "timestamp": datetime.now(),
            "metric": metric
        })

    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard with charts."""

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AIL Performance Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric { display: inline-block; margin: 10px; padding: 15px;
                         border: 1px solid #ddd; border-radius: 5px; }
                .pass { background-color: #d4edda; }
                .fail { background-color: #f8d7da; }
                h1 { color: #333; }
                .chart { width: 100%; height: 400px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>AIL Performance Dashboard</h1>
            <div id="summary"></div>
            <div id="latency-chart" class="chart"></div>
            <div id="cache-chart" class="chart"></div>
            <div id="resource-chart" class="chart"></div>
        </body>
        </html>
        """

        return html
```

## Conclusion

This comprehensive performance benchmark plan ensures the Archaeological Intelligence Layer meets its ambitious performance targets. The automated benchmarking, continuous monitoring, and detailed reporting provide confidence that AIL can deliver <1s p95 latency with 80% cache hit rate while maintaining <100MB memory footprint per agent.

The benchmark suite is designed to be:
- **Comprehensive**: Covers all performance aspects
- **Automated**: Runs in CI/CD pipeline
- **Actionable**: Provides clear recommendations
- **Reproducible**: Consistent test methodology
- **Scalable**: Can be extended for new scenarios