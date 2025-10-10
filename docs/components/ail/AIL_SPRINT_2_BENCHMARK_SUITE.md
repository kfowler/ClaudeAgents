# AIL Sprint 2: Performance Benchmark Suite

**Version**: 1.0.0
**Date**: 2025-10-08
**Author**: systems-engineer
**Purpose**: Automated performance validation and regression detection

---

## Executive Summary

This document defines the comprehensive benchmark suite for AIL Sprint 2, providing automated performance validation with production-representative workloads. Every optimization must demonstrate measurable improvement through these benchmarks.

---

## Benchmark Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Benchmark Orchestrator                  │
│              pytest-benchmark + custom fixtures          │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬───────────────┐
        ▼              ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Latency    │ │    Memory    │ │    Cache     │ │     Load     │
│  Benchmarks  │ │  Benchmarks  │ │  Benchmarks  │ │  Benchmarks  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Core Benchmark Implementation

### Base Benchmark Framework

```python
"""
benchmarks/ail_benchmark_suite.py

Comprehensive performance benchmark suite for AIL Sprint 2.
"""

import asyncio
import time
import numpy as np
import pytest
import pytest_benchmark
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from memory_profiler import profile

# Import AIL components
from tools.ail import ArchaeologyContextProvider
from tools.ail.optimized import OptimizedContextProvider  # Sprint 2


@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""

    # Test data
    repo_path: str = str(Path.cwd())
    test_files: List[str] = None
    test_queries: List[str] = None

    # Performance targets
    p95_latency_target_ms: float = 500
    p99_latency_target_ms: float = 1000
    memory_limit_mb: float = 150
    cache_hit_target: float = 0.9

    # Load parameters
    concurrent_agents: int = 20
    queries_per_agent: int = 10
    test_duration_seconds: int = 60

    def __post_init__(self):
        if self.test_files is None:
            self.test_files = [
                "agents/full-stack-architect.md",
                "agents/qa-test-engineer.md",
                "agents/ai-ml-engineer.md",
                "tools/ail/context_provider.py",
                "tools/code_archaeology/git_analyzer.py"
            ]

        if self.test_queries is None:
            self.test_queries = [
                "What is the purpose of this component?",
                "What architectural decisions were made?",
                "How has this evolved over time?",
                "What problems does this solve?",
                "Who contributed to this?"
            ]


class BenchmarkSuite:
    """Main benchmark suite orchestrator"""

    def __init__(self, config: BenchmarkConfig = None):
        self.config = config or BenchmarkConfig()
        self.results = {}

    def run_all(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""

        print("=" * 80)
        print("AIL Sprint 2 Performance Benchmark Suite")
        print("=" * 80)

        # Run benchmark categories
        self.results['latency'] = self.run_latency_benchmarks()
        self.results['memory'] = self.run_memory_benchmarks()
        self.results['cache'] = self.run_cache_benchmarks()
        self.results['load'] = self.run_load_benchmarks()
        self.results['comparison'] = self.run_comparison_benchmarks()

        # Generate report
        self.results['summary'] = self.generate_summary()

        return self.results
```

---

## Latency Benchmarks

### 1. Component Latency Benchmarks

```python
class LatencyBenchmarks:
    """Latency-focused benchmarks"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.provider = OptimizedContextProvider(config.repo_path)

    @pytest.mark.benchmark(group="latency")
    def test_faiss_search_latency(self, benchmark):
        """Benchmark FAISS search performance"""

        # Setup
        import faiss
        import numpy as np

        dimension = 512
        n_vectors = 10000

        # Create index
        index = faiss.IndexIVFFlat(
            faiss.IndexFlatL2(dimension),
            dimension,
            100  # nlist
        )

        # Train and add vectors
        vectors = np.random.rand(n_vectors, dimension).astype('float32')
        index.train(vectors)
        index.add(vectors)

        # Benchmark search
        query = np.random.rand(1, dimension).astype('float32')

        result = benchmark(index.search, query, 10)

        # Assertions
        assert benchmark.stats['mean'] < 0.010  # <10ms mean
        assert benchmark.stats['max'] < 0.020   # <20ms max

        return {
            'mean_ms': benchmark.stats['mean'] * 1000,
            'p95_ms': benchmark.stats['p95'] * 1000,
            'ops_per_sec': benchmark.stats['ops']
        }

    @pytest.mark.benchmark(group="latency")
    def test_semantic_cache_lookup(self, benchmark):
        """Benchmark semantic cache performance"""

        from tools.ail.cache import SemanticCache

        cache = SemanticCache(threshold=0.95)

        # Pre-populate cache
        for i in range(100):
            cache.add(f"query_{i}", f"result_{i}")

        # Benchmark lookup
        result = benchmark(cache.find_similar, "query_50_modified")

        assert benchmark.stats['mean'] < 0.005  # <5ms

    @pytest.mark.benchmark(group="latency")
    def test_end_to_end_latency(self, benchmark):
        """Benchmark complete request latency"""

        # Use asyncio for async provider
        def sync_wrapper():
            return asyncio.run(
                self.provider.get_context(
                    self.config.test_files[0],
                    self.config.test_queries[0]
                )
            )

        result = benchmark.pedantic(
            sync_wrapper,
            rounds=50,
            warmup_rounds=5
        )

        # Check against targets
        assert benchmark.stats['p95'] < self.config.p95_latency_target_ms / 1000
        assert benchmark.stats['p99'] < self.config.p99_latency_target_ms / 1000

        return {
            'mean_ms': benchmark.stats['mean'] * 1000,
            'p50_ms': benchmark.stats['p50'] * 1000,
            'p95_ms': benchmark.stats['p95'] * 1000,
            'p99_ms': benchmark.stats['p99'] * 1000,
            'min_ms': benchmark.stats['min'] * 1000,
            'max_ms': benchmark.stats['max'] * 1000
        }

    @pytest.mark.benchmark(group="latency")
    def test_query_patterns(self, benchmark):
        """Test different query patterns"""

        patterns = {
            'simple': "What is this?",
            'complex': "Analyze the architectural decisions, evolution, and key contributors with detailed historical context",
            'specific': "What changes were made in commit abc123?",
            'broad': "How does this fit into the overall system architecture?"
        }

        results = {}

        for pattern_name, query in patterns.items():
            def query_fn():
                return asyncio.run(
                    self.provider.get_context(
                        self.config.test_files[0],
                        query
                    )
                )

            benchmark.pedantic(query_fn, rounds=10)

            results[pattern_name] = {
                'mean_ms': benchmark.stats['mean'] * 1000,
                'p95_ms': benchmark.stats['p95'] * 1000
            }

        # Complex queries should still meet p99 target
        assert results['complex']['p95_ms'] < self.config.p99_latency_target_ms

        return results
```

### 2. Latency Distribution Analysis

```python
class LatencyDistribution:
    """Analyze latency distribution characteristics"""

    def __init__(self, provider: OptimizedContextProvider):
        self.provider = provider
        self.latencies = []

    async def collect_samples(self, n_samples: int = 1000):
        """Collect latency samples"""

        for i in range(n_samples):
            file_path = f"test_file_{i % 10}.py"
            question = f"Question variant {i % 20}"

            start = time.perf_counter()
            await self.provider.get_context(file_path, question)
            latency_ms = (time.perf_counter() - start) * 1000

            self.latencies.append(latency_ms)

    def analyze_distribution(self) -> dict:
        """Analyze latency distribution"""

        latencies = np.array(self.latencies)

        return {
            'samples': len(latencies),
            'mean': np.mean(latencies),
            'median': np.median(latencies),
            'std': np.std(latencies),
            'percentiles': {
                'p50': np.percentile(latencies, 50),
                'p75': np.percentile(latencies, 75),
                'p90': np.percentile(latencies, 90),
                'p95': np.percentile(latencies, 95),
                'p99': np.percentile(latencies, 99),
                'p99.9': np.percentile(latencies, 99.9)
            },
            'outliers': {
                'count': len(latencies[latencies > np.percentile(latencies, 99)]),
                'max': np.max(latencies),
                'above_1s': len(latencies[latencies > 1000]),
                'above_2s': len(latencies[latencies > 2000])
            },
            'histogram': np.histogram(latencies, bins=50)
        }
```

---

## Memory Benchmarks

### 1. Memory Usage Benchmarks

```python
class MemoryBenchmarks:
    """Memory-focused benchmarks"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config

    @pytest.mark.memory
    def test_initialization_memory(self):
        """Test memory usage during initialization"""

        import tracemalloc
        import psutil

        process = psutil.Process()

        # Baseline memory
        baseline_mb = process.memory_info().rss / 1024 / 1024

        # Start tracing
        tracemalloc.start()

        # Initialize provider
        provider = OptimizedContextProvider(self.config.repo_path)

        # Get peak memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        current_mb = process.memory_info().rss / 1024 / 1024

        results = {
            'baseline_mb': baseline_mb,
            'peak_mb': peak_mb,
            'current_mb': current_mb,
            'delta_mb': current_mb - baseline_mb
        }

        # Assert under limit
        assert peak_mb < self.config.memory_limit_mb

        return results

    @pytest.mark.memory
    def test_query_memory_scaling(self):
        """Test memory scaling with query volume"""

        import gc
        import psutil

        provider = OptimizedContextProvider(self.config.repo_path)
        process = psutil.Process()

        memory_samples = []

        for batch in range(10):
            # Run 100 queries
            for i in range(100):
                asyncio.run(
                    provider.get_context(
                        f"file_{i % 10}.py",
                        f"query_{i}"
                    )
                )

            # Sample memory
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_samples.append({
                'batch': batch,
                'queries': (batch + 1) * 100,
                'memory_mb': memory_mb
            })

            # Force GC
            gc.collect()

        # Check for memory leak (linear growth)
        first_sample = memory_samples[0]['memory_mb']
        last_sample = memory_samples[-1]['memory_mb']

        growth_per_query = (last_sample - first_sample) / 1000

        results = {
            'samples': memory_samples,
            'growth_per_query_kb': growth_per_query * 1024,
            'final_memory_mb': last_sample,
            'memory_leak_detected': growth_per_query > 0.1  # >100KB per query
        }

        # Assert no significant leak
        assert not results['memory_leak_detected']
        assert last_sample < self.config.memory_limit_mb

        return results

    @pytest.mark.memory
    def test_cache_memory_bounds(self):
        """Test cache memory boundaries"""

        from tools.ail.cache import BoundedLRUCache
        import sys

        cache = BoundedLRUCache(max_memory_bytes=40 * 1024 * 1024)  # 40MB

        # Fill cache
        large_object = "x" * 1024  # 1KB string

        entries_added = 0
        for i in range(50000):  # Try to add 50MB worth
            cache.put(f"key_{i}", large_object)
            entries_added += 1

            # Check if cache is respecting memory limit
            cache_size = sum(
                sys.getsizeof(v) for v in cache.cache.values()
            )

            if cache_size > 45 * 1024 * 1024:  # Should stay under 45MB
                break

        actual_size_mb = cache_size / 1024 / 1024

        results = {
            'entries_added': entries_added,
            'cache_size_mb': actual_size_mb,
            'within_bounds': actual_size_mb <= 45
        }

        assert results['within_bounds']

        return results
```

### 2. Memory Profiling

```python
class MemoryProfiler:
    """Detailed memory profiling"""

    @profile
    def profile_request_memory(self, provider, file_path, question):
        """Profile memory for single request"""

        result = asyncio.run(
            provider.get_context(file_path, question)
        )
        return result

    def analyze_memory_profile(self, profile_output: str) -> dict:
        """Parse memory profile output"""

        lines = profile_output.split('\n')

        peak_memory = 0
        increments = []

        for line in lines:
            if 'MiB' in line:
                # Parse memory usage
                parts = line.split()
                if len(parts) >= 2:
                    memory_mb = float(parts[0])
                    increment_mb = float(parts[1]) if len(parts) > 1 else 0

                    peak_memory = max(peak_memory, memory_mb)
                    if increment_mb > 0:
                        increments.append({
                            'line': line,
                            'increment_mb': increment_mb
                        })

        return {
            'peak_memory_mb': peak_memory,
            'total_increment_mb': sum(i['increment_mb'] for i in increments),
            'largest_increments': sorted(
                increments,
                key=lambda x: x['increment_mb'],
                reverse=True
            )[:5]
        }
```

---

## Cache Benchmarks

### 1. Cache Performance Benchmarks

```python
class CacheBenchmarks:
    """Cache-focused benchmarks"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.provider = OptimizedContextProvider(config.repo_path)

    @pytest.mark.benchmark(group="cache")
    def test_cache_hit_rate(self, benchmark):
        """Test cache hit rate with realistic patterns"""

        # Simulate realistic query patterns
        # 70% repeated queries, 30% new queries

        queries_executed = []
        cache_hits = 0
        cache_misses = 0

        def execute_queries():
            nonlocal cache_hits, cache_misses

            for i in range(100):
                if i < 30 or np.random.random() > 0.7:
                    # New query
                    file_path = self.config.test_files[i % len(self.config.test_files)]
                    question = f"New question {i}"
                else:
                    # Repeat previous query
                    prev_idx = np.random.randint(0, len(queries_executed))
                    file_path, question = queries_executed[prev_idx]

                result = asyncio.run(
                    self.provider.get_context(file_path, question)
                )

                if result.get('cached', False):
                    cache_hits += 1
                else:
                    cache_misses += 1
                    queries_executed.append((file_path, question))

        benchmark(execute_queries)

        hit_rate = cache_hits / (cache_hits + cache_misses)

        results = {
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'hit_rate': hit_rate,
            'meets_target': hit_rate >= self.config.cache_hit_target
        }

        assert results['meets_target']

        return results

    @pytest.mark.benchmark(group="cache")
    def test_semantic_cache_accuracy(self, benchmark):
        """Test semantic cache similarity matching"""

        from tools.ail.cache import SemanticCache

        cache = SemanticCache(threshold=0.95)

        # Test similar queries
        test_cases = [
            ("What is this agent?", "What does this agent do?", True),
            ("How does it work?", "Explain how this works", True),
            ("What is the purpose?", "Why was this created?", True),
            ("List all features", "Delete everything", False),
        ]

        correct_matches = 0

        for original, similar, should_match in test_cases:
            # Add original
            cache.add(original, f"Answer to: {original}")

            # Check if similar matches
            result = cache.find_similar(similar)

            if should_match and result:
                correct_matches += 1
            elif not should_match and not result:
                correct_matches += 1

        accuracy = correct_matches / len(test_cases)

        results = {
            'test_cases': len(test_cases),
            'correct_matches': correct_matches,
            'accuracy': accuracy,
            'meets_threshold': accuracy >= 0.8
        }

        assert results['meets_threshold']

        return results

    @pytest.mark.benchmark(group="cache")
    def test_cache_eviction(self, benchmark):
        """Test cache eviction performance"""

        from tools.ail.cache import LRUCache

        cache = LRUCache(maxsize=1000)

        def test_eviction():
            # Fill cache beyond capacity
            for i in range(2000):
                cache.put(f"key_{i}", f"value_{i}")

            # Verify size limit
            assert cache.size <= 1000

            # Verify LRU behavior (oldest should be evicted)
            assert cache.get("key_0") is None
            assert cache.get("key_999") is None
            assert cache.get("key_1999") is not None

        result = benchmark(test_eviction)

        return {
            'eviction_time_ms': benchmark.stats['mean'] * 1000,
            'final_cache_size': cache.size
        }
```

### 2. Cache Warming Strategies

```python
class CacheWarming:
    """Cache warming benchmark strategies"""

    def __init__(self, provider: OptimizedContextProvider):
        self.provider = provider

    async def warm_cache_parallel(self, queries: List[tuple]) -> float:
        """Parallel cache warming"""

        start = time.time()

        tasks = [
            self.provider.get_context(file_path, question)
            for file_path, question in queries
        ]

        await asyncio.gather(*tasks)

        return time.time() - start

    async def warm_cache_sequential(self, queries: List[tuple]) -> float:
        """Sequential cache warming"""

        start = time.time()

        for file_path, question in queries:
            await self.provider.get_context(file_path, question)

        return time.time() - start

    def benchmark_warming_strategies(self) -> dict:
        """Compare warming strategies"""

        # Common queries to warm
        queries = [
            ("agents/full-stack-architect.md", "What is this?"),
            ("agents/qa-test-engineer.md", "Testing approach?"),
            ("tools/ail/context_provider.py", "How does it work?"),
        ] * 10  # 30 queries total

        # Clear cache
        self.provider.clear_cache()

        # Test parallel warming
        parallel_time = asyncio.run(
            self.warm_cache_parallel(queries)
        )

        # Clear and test sequential
        self.provider.clear_cache()

        sequential_time = asyncio.run(
            self.warm_cache_sequential(queries)
        )

        return {
            'parallel_time_s': parallel_time,
            'sequential_time_s': sequential_time,
            'speedup': sequential_time / parallel_time,
            'queries_warmed': len(queries)
        }
```

---

## Load Testing Benchmarks

### 1. Concurrent Load Testing

```python
class LoadBenchmarks:
    """Load testing benchmarks"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config

    async def test_concurrent_agents(self, n_agents: int = 20) -> dict:
        """Test with concurrent agents"""

        provider = OptimizedContextProvider(self.config.repo_path)

        results = {
            'agent_results': [],
            'errors': [],
            'start_time': time.time()
        }

        async def agent_workload(agent_id: int):
            """Single agent workload"""

            agent_latencies = []

            for query_id in range(self.config.queries_per_agent):
                try:
                    file_path = self.config.test_files[
                        agent_id % len(self.config.test_files)
                    ]
                    question = f"Query {query_id} from agent {agent_id}"

                    start = time.perf_counter()
                    result = await provider.get_context(file_path, question)
                    latency_ms = (time.perf_counter() - start) * 1000

                    agent_latencies.append(latency_ms)

                    # Simulate think time
                    await asyncio.sleep(np.random.uniform(0.1, 0.3))

                except Exception as e:
                    results['errors'].append({
                        'agent_id': agent_id,
                        'query_id': query_id,
                        'error': str(e)
                    })

            return {
                'agent_id': agent_id,
                'latencies': agent_latencies,
                'mean_latency': np.mean(agent_latencies),
                'p95_latency': np.percentile(agent_latencies, 95)
            }

        # Launch concurrent agents
        tasks = [
            agent_workload(i) for i in range(n_agents)
        ]

        agent_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        all_latencies = []
        for result in agent_results:
            if isinstance(result, dict):
                all_latencies.extend(result['latencies'])
                results['agent_results'].append(result)

        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']

        if all_latencies:
            results['aggregate'] = {
                'total_queries': len(all_latencies),
                'mean_latency_ms': np.mean(all_latencies),
                'p50_latency_ms': np.percentile(all_latencies, 50),
                'p95_latency_ms': np.percentile(all_latencies, 95),
                'p99_latency_ms': np.percentile(all_latencies, 99),
                'qps': len(all_latencies) / results['duration']
            }

            # Check SLA
            results['meets_sla'] = (
                results['aggregate']['p95_latency_ms'] < self.config.p95_latency_target_ms
            )

        return results

    @pytest.mark.load
    def test_scaling_limits(self):
        """Find scaling limits"""

        results = {}

        for n_agents in [1, 5, 10, 15, 20, 25, 30]:
            print(f"Testing with {n_agents} agents...")

            test_result = asyncio.run(
                self.test_concurrent_agents(n_agents)
            )

            results[n_agents] = test_result['aggregate']

            # Stop if SLA violated
            if test_result['aggregate']['p95_latency_ms'] > self.config.p95_latency_target_ms:
                print(f"SLA violated at {n_agents} agents")
                break

        # Find knee point
        agent_counts = sorted(results.keys())
        latencies = [results[n]['p95_latency_ms'] for n in agent_counts]

        knee_point = agent_counts[-1]  # Default to max
        for i in range(1, len(latencies)):
            if latencies[i] > latencies[i-1] * 1.2:  # 20% degradation
                knee_point = agent_counts[i-1]
                break

        return {
            'results_by_agents': results,
            'max_agents_under_sla': knee_point,
            'scaling_characteristic': 'linear' if knee_point >= 20 else 'sublinear'
        }
```

### 2. Stress Testing

```python
class StressTesting:
    """Stress testing to find breaking points"""

    async def stress_test(self, provider, duration_seconds: int = 60):
        """Apply increasing load until failure"""

        results = {
            'phases': [],
            'breaking_point': None
        }

        phase = 1
        concurrent_requests = 10

        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            print(f"Phase {phase}: {concurrent_requests} concurrent requests")

            # Run phase
            phase_results = await self.run_phase(
                provider,
                concurrent_requests,
                duration=10
            )

            results['phases'].append({
                'phase': phase,
                'concurrent_requests': concurrent_requests,
                'results': phase_results
            })

            # Check for breaking point
            if phase_results['error_rate'] > 0.01:  # >1% errors
                results['breaking_point'] = concurrent_requests
                break

            if phase_results['p95_latency_ms'] > 2000:  # >2s latency
                results['breaking_point'] = concurrent_requests
                break

            # Increase load
            phase += 1
            concurrent_requests = int(concurrent_requests * 1.5)

        return results

    async def run_phase(self, provider, concurrent: int, duration: int):
        """Run single stress test phase"""

        end_time = time.time() + duration
        results = []
        errors = []

        async def request_loop():
            while time.time() < end_time:
                try:
                    start = time.perf_counter()
                    await provider.get_context("test.py", "stress test")
                    latency_ms = (time.perf_counter() - start) * 1000
                    results.append(latency_ms)
                except Exception as e:
                    errors.append(str(e))

        # Run concurrent loops
        tasks = [request_loop() for _ in range(concurrent)]
        await asyncio.gather(*tasks, return_exceptions=True)

        return {
            'total_requests': len(results) + len(errors),
            'successful': len(results),
            'errors': len(errors),
            'error_rate': len(errors) / (len(results) + len(errors)) if results else 1.0,
            'p95_latency_ms': np.percentile(results, 95) if results else 0,
            'qps': len(results) / duration
        }
```

---

## Comparison Benchmarks

### Sprint 1 vs Sprint 2 Comparison

```python
class ComparisonBenchmarks:
    """Compare Sprint 1 vs Sprint 2 performance"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.sprint1_provider = ArchaeologyContextProvider(config.repo_path)
        self.sprint2_provider = OptimizedContextProvider(config.repo_path)

    async def compare_latency(self) -> dict:
        """Compare latency between versions"""

        queries = list(zip(self.config.test_files, self.config.test_queries))

        sprint1_latencies = []
        sprint2_latencies = []

        for file_path, question in queries * 10:  # 50 queries total
            # Sprint 1
            start = time.perf_counter()
            await self.sprint1_provider.get_context(file_path, question)
            sprint1_latencies.append((time.perf_counter() - start) * 1000)

            # Sprint 2
            start = time.perf_counter()
            await self.sprint2_provider.get_context(file_path, question)
            sprint2_latencies.append((time.perf_counter() - start) * 1000)

        return {
            'sprint1': {
                'mean_ms': np.mean(sprint1_latencies),
                'p95_ms': np.percentile(sprint1_latencies, 95),
                'p99_ms': np.percentile(sprint1_latencies, 99)
            },
            'sprint2': {
                'mean_ms': np.mean(sprint2_latencies),
                'p95_ms': np.percentile(sprint2_latencies, 95),
                'p99_ms': np.percentile(sprint2_latencies, 99)
            },
            'improvement': {
                'mean_reduction': (
                    1 - np.mean(sprint2_latencies) / np.mean(sprint1_latencies)
                ) * 100,
                'p95_reduction': (
                    1 - np.percentile(sprint2_latencies, 95) /
                    np.percentile(sprint1_latencies, 95)
                ) * 100
            }
        }

    def compare_memory(self) -> dict:
        """Compare memory usage"""

        import tracemalloc

        # Sprint 1 memory
        tracemalloc.start()
        s1 = ArchaeologyContextProvider(self.config.repo_path)
        s1_peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()

        # Sprint 2 memory
        tracemalloc.start()
        s2 = OptimizedContextProvider(self.config.repo_path)
        s2_peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()

        return {
            'sprint1_peak_mb': s1_peak,
            'sprint2_peak_mb': s2_peak,
            'memory_increase_mb': s2_peak - s1_peak,
            'within_budget': s2_peak < self.config.memory_limit_mb
        }
```

---

## Benchmark Reporting

### Report Generator

```python
class BenchmarkReporter:
    """Generate comprehensive benchmark reports"""

    def __init__(self, results: dict):
        self.results = results

    def generate_report(self) -> str:
        """Generate markdown report"""

        report = []
        report.append("# AIL Sprint 2 Performance Benchmark Report")
        report.append(f"\n**Date**: {datetime.now().isoformat()}")
        report.append(f"**Version**: Sprint 2 Optimized")
        report.append("\n---\n")

        # Executive Summary
        report.append("## Executive Summary\n")

        passed = self.check_requirements()

        for requirement, status in passed.items():
            icon = "✅" if status else "❌"
            report.append(f"- {icon} {requirement}")

        # Detailed Results
        report.append("\n## Detailed Results\n")

        # Latency Results
        if 'latency' in self.results:
            report.append("### Latency Performance\n")
            latency = self.results['latency']['end_to_end']
            report.append(f"- **p95 Latency**: {latency['p95_ms']:.2f}ms")
            report.append(f"- **p99 Latency**: {latency['p99_ms']:.2f}ms")
            report.append(f"- **Mean Latency**: {latency['mean_ms']:.2f}ms")

        # Memory Results
        if 'memory' in self.results:
            report.append("\n### Memory Usage\n")
            memory = self.results['memory']
            report.append(f"- **Peak Memory**: {memory['peak_mb']:.2f}MB")
            report.append(f"- **Memory Leak**: {'Detected' if memory.get('leak_detected') else 'None'}")

        # Cache Results
        if 'cache' in self.results:
            report.append("\n### Cache Performance\n")
            cache = self.results['cache']
            report.append(f"- **Hit Rate**: {cache['hit_rate']:.1%}")
            report.append(f"- **Semantic Match Accuracy**: {cache.get('accuracy', 0):.1%}")

        # Load Testing
        if 'load' in self.results:
            report.append("\n### Load Testing\n")
            load = self.results['load']
            report.append(f"- **Max Concurrent Agents**: {load.get('max_agents', 0)}")
            report.append(f"- **Throughput**: {load.get('qps', 0):.1f} QPS")

        # Comparison
        if 'comparison' in self.results:
            report.append("\n### Sprint 1 vs Sprint 2\n")
            comp = self.results['comparison']
            report.append(f"- **Latency Reduction**: {comp['latency']['improvement']['p95_reduction']:.1f}%")
            report.append(f"- **Memory Increase**: {comp['memory']['memory_increase_mb']:.1f}MB")

        return '\n'.join(report)

    def check_requirements(self) -> dict:
        """Check if requirements are met"""

        passed = {}

        # Latency requirements
        if 'latency' in self.results:
            latency = self.results['latency'].get('end_to_end', {})
            passed['p95 < 500ms'] = latency.get('p95_ms', float('inf')) < 500
            passed['p99 < 1000ms'] = latency.get('p99_ms', float('inf')) < 1000

        # Memory requirement
        if 'memory' in self.results:
            memory = self.results['memory']
            passed['Memory < 150MB'] = memory.get('peak_mb', float('inf')) < 150

        # Cache requirement
        if 'cache' in self.results:
            cache = self.results['cache']
            passed['Cache Hit Rate > 90%'] = cache.get('hit_rate', 0) > 0.9

        # Concurrency requirement
        if 'load' in self.results:
            load = self.results['load']
            passed['20+ Concurrent Agents'] = load.get('max_agents', 0) >= 20

        return passed
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/performance-benchmarks.yml

name: AIL Performance Benchmarks

on:
  push:
    branches: [main, sprint-2]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest-benchmark memory-profiler

    - name: Run benchmarks
      run: |
        pytest benchmarks/ail_benchmark_suite.py \
          --benchmark-only \
          --benchmark-json=benchmark_results.json

    - name: Check performance requirements
      run: |
        python scripts/check_performance.py benchmark_results.json

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: benchmark_results.json

    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const results = JSON.parse(fs.readFileSync('benchmark_results.json'));

          const comment = `## Performance Benchmark Results

          - p95 Latency: ${results.p95_ms}ms (Target: <500ms)
          - Memory: ${results.memory_mb}MB (Target: <150MB)
          - Cache Hit Rate: ${results.cache_hit_rate}% (Target: >90%)
          `;

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

---

## Conclusion

This comprehensive benchmark suite provides automated, reproducible performance validation for AIL Sprint 2. With production-representative workloads, detailed profiling, and CI/CD integration, we can confidently validate that our optimizations deliver the promised <500ms p95 latency while maintaining system stability and correctness.

Key capabilities:
- **Automated validation** of all performance requirements
- **Regression detection** through continuous benchmarking
- **Detailed profiling** of individual components
- **Load testing** to verify concurrent capacity
- **Comparison benchmarks** to measure improvement

The suite ensures every optimization is validated with empirical data, providing confidence in our performance claims.