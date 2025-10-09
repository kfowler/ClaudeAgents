"""
Performance Tests for Archaeological Intelligence Layer (AIL).

Tests performance characteristics under various loads:
- Latency under different query patterns
- Memory profiling and leak detection
- Cache hit rate validation
- Concurrent request handling
- Scalability with repository size

Performance Targets:
- p95 latency <1s for cached queries
- p99 latency <3s for uncached queries
- Memory usage <100MB for 1000 commits
- Cache hit rate >70% for repeated queries
- Support 10+ concurrent agent requests
"""

import pytest
import time
import threading
import tracemalloc
from pathlib import Path
from typing import List, Dict
import sys
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_ail_context_provider import ArchaeologyContextProvider


@pytest.fixture
def repo_path():
    """Get test repository path."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def provider(repo_path):
    """Create and initialize a context provider."""
    p = ArchaeologyContextProvider(repo_path, cache_enabled=True)
    p.initialize()  # Full repo for performance tests
    return p


class TestLatencyPerformance:
    """Test query latency under various conditions."""

    def test_p95_latency_target(self, provider):
        """Test p95 latency meets <1s target for queries."""
        latencies = []

        test_queries = [
            ("agents/full-stack-architect.md", "What is this agent's purpose?"),
            ("tools/code_archaeology/git_analyzer.py", "Why was this file created?"),
            ("CLAUDE.md", "What are the key instructions?"),
            ("agents/qa-test-engineer.md", "What testing strategies are recommended?"),
            ("tools/code_archaeology/context_synthesizer.py", "How does context synthesis work?"),
        ]

        # Run queries multiple times
        for _ in range(10):
            for file_path, question in test_queries:
                start = time.time()
                result = provider.get_context(file_path, question)
                latency = (time.time() - start) * 1000  # ms

                if not result.get('cached', False):
                    latencies.append(latency)

        # Calculate p95
        sorted_latencies = sorted(latencies)
        p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        avg_latency = sum(latencies) / len(latencies)

        print(f"\n=== Latency Performance ===")
        print(f"Total queries: {len(latencies)}")
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"p95 latency: {p95_latency:.2f}ms")
        print(f"p99 latency: {sorted_latencies[int(len(sorted_latencies) * 0.99)]:.2f}ms")
        print(f"Min latency: {min(latencies):.2f}ms")
        print(f"Max latency: {max(latencies):.2f}ms")

        # p95 should be under 1000ms
        assert p95_latency < 1000, f"p95 latency {p95_latency:.2f}ms exceeds 1000ms target"

    def test_p99_latency_target(self, provider):
        """Test p99 latency meets <3s target for complex queries."""
        latencies = []

        # More complex queries that require deeper analysis
        complex_queries = [
            ("tools/code_archaeology/git_analyzer.py",
             "What architectural decisions were made and why? Include all historical context."),
            ("tools/code_archaeology/github_integrator.py",
             "What were the major refactorings and what problems did they solve?"),
            ("tools/code_archaeology/context_synthesizer.py",
             "How has the embedding strategy evolved over time?"),
        ]

        # Run queries
        for _ in range(20):
            for file_path, question in complex_queries:
                start = time.time()
                result = provider.get_context(file_path, question)
                latency = (time.time() - start) * 1000  # ms

                if not result.get('cached', False):
                    latencies.append(latency)

        # Calculate p99
        sorted_latencies = sorted(latencies)
        p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]

        print(f"\n=== Complex Query Latency ===")
        print(f"Total queries: {len(latencies)}")
        print(f"p99 latency: {p99_latency:.2f}ms")

        # p99 should be under 3000ms
        assert p99_latency < 3000, f"p99 latency {p99_latency:.2f}ms exceeds 3000ms target"

    def test_cached_query_instant_response(self, provider):
        """Test cached queries return instantly."""
        file_path = "agents/full-stack-architect.md"
        question = "What is this?"

        # First query (uncached)
        provider.get_context(file_path, question)

        # Subsequent queries (cached)
        cached_latencies = []
        for _ in range(10):
            start = time.time()
            result = provider.get_context(file_path, question)
            latency = (time.time() - start) * 1000  # ms
            cached_latencies.append(latency)

            assert result['cached'] is True
            assert result['latency_ms'] == 0

        avg_cached_latency = sum(cached_latencies) / len(cached_latencies)

        print(f"\n=== Cached Query Performance ===")
        print(f"Average cached latency: {avg_cached_latency:.2f}ms")

        # Cached queries should be near-instant (< 10ms overhead)
        assert avg_cached_latency < 10, \
            f"Cached query overhead {avg_cached_latency:.2f}ms exceeds 10ms target"


class TestMemoryPerformance:
    """Test memory usage and leak detection."""

    def test_memory_usage_under_100mb(self, repo_path):
        """Test memory usage stays under 100MB."""
        tracemalloc.start()

        # Initialize provider with full repository
        provider = ArchaeologyContextProvider(repo_path, cache_enabled=True)
        provider.initialize()

        # Baseline memory after initialization
        current, peak = tracemalloc.get_traced_memory()
        init_mb = peak / 1024 / 1024

        # Make queries to populate cache
        test_files = [
            "agents/full-stack-architect.md",
            "agents/qa-test-engineer.md",
            "tools/code_archaeology/git_analyzer.py",
            "tools/code_archaeology/github_integrator.py",
            "tools/code_archaeology/context_synthesizer.py",
        ]

        questions = [
            "What is this?",
            "Why was it created?",
            "What are the key features?",
            "Who are the main contributors?",
        ]

        # Run 100 queries
        for i in range(100):
            file_path = random.choice(test_files)
            question = random.choice(questions)
            provider.get_context(file_path, question)

        # Check memory after queries
        current, peak = tracemalloc.get_traced_memory()
        query_mb = peak / 1024 / 1024

        tracemalloc.stop()

        print(f"\n=== Memory Usage ===")
        print(f"After initialization: {init_mb:.2f}MB")
        print(f"After 100 queries: {query_mb:.2f}MB")
        print(f"Memory growth: {query_mb - init_mb:.2f}MB")

        # Total memory should be under 100MB
        assert query_mb < 100, f"Memory usage {query_mb:.2f}MB exceeds 100MB target"

    def test_no_memory_leak(self, provider):
        """Test for memory leaks over extended use."""
        tracemalloc.start()

        # Run queries and clear cache periodically
        for batch in range(5):
            # Make 20 queries
            for i in range(20):
                provider.get_context(
                    "agents/full-stack-architect.md",
                    f"Question {i}"
                )

            # Clear cache
            provider.clear_cache()

        # Memory should stabilize (no continuous growth)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        final_mb = current / 1024 / 1024

        print(f"\n=== Memory Leak Test ===")
        print(f"Final memory: {final_mb:.2f}MB")

        # After clearing caches, memory should be reasonable
        assert final_mb < 50, f"Potential memory leak detected: {final_mb:.2f}MB"


class TestCachePerformance:
    """Test cache hit rate and effectiveness."""

    def test_cache_hit_rate_target(self, provider):
        """Test cache achieves >70% hit rate for repeated queries."""
        # Pattern: Agents repeatedly ask similar questions about same files
        test_patterns = [
            ("agents/full-stack-architect.md", "What is this agent?"),
            ("agents/qa-test-engineer.md", "What testing approach?"),
            ("tools/code_archaeology/git_analyzer.py", "How does it work?"),
        ]

        # Make initial queries (cache misses)
        for file_path, question in test_patterns:
            provider.get_context(file_path, question)

        # Simulate realistic usage pattern (70% repeat queries, 30% new)
        for _ in range(100):
            if random.random() < 0.7:
                # Repeat query (should hit cache)
                file_path, question = random.choice(test_patterns)
            else:
                # New query (cache miss)
                file_path = random.choice([fp for fp, _ in test_patterns])
                question = f"New question {random.randint(1, 100)}"

            provider.get_context(file_path, question)

        stats = provider.get_stats()

        print(f"\n=== Cache Performance ===")
        print(f"Total queries: {stats['total_queries']}")
        print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")

        # Should achieve >70% hit rate with realistic pattern
        assert stats['cache_hit_rate'] >= 0.7, \
            f"Cache hit rate {stats['cache_hit_rate']:.1%} below 70% target"

    def test_cache_effectiveness_reduces_latency(self, provider):
        """Test cache significantly reduces average latency."""
        file_path = "agents/full-stack-architect.md"
        question = "What is this?"

        # Measure uncached latency
        provider.clear_cache()
        start = time.time()
        provider.get_context(file_path, question)
        uncached_latency = (time.time() - start) * 1000

        # Measure cached latency
        cached_latencies = []
        for _ in range(10):
            start = time.time()
            provider.get_context(file_path, question)
            cached_latencies.append((time.time() - start) * 1000)

        avg_cached_latency = sum(cached_latencies) / len(cached_latencies)

        print(f"\n=== Cache Latency Reduction ===")
        print(f"Uncached: {uncached_latency:.2f}ms")
        print(f"Cached (avg): {avg_cached_latency:.2f}ms")
        print(f"Speedup: {uncached_latency / max(avg_cached_latency, 0.001):.1f}x")

        # Cached should be at least 10x faster
        assert avg_cached_latency < uncached_latency / 10, \
            "Cache not providing sufficient latency reduction"


class TestConcurrentPerformance:
    """Test concurrent request handling."""

    def test_concurrent_agent_queries(self, repo_path):
        """Test handling 10+ concurrent agent queries."""
        provider = ArchaeologyContextProvider(repo_path, cache_enabled=True)
        provider.initialize()

        results = []
        errors = []

        def query_task(thread_id: int):
            """Task for concurrent query."""
            try:
                result = provider.get_context(
                    f"agents/full-stack-architect.md",
                    f"Question from thread {thread_id}"
                )
                results.append({
                    'thread_id': thread_id,
                    'latency_ms': result['latency_ms'],
                    'success': True
                })
            except Exception as e:
                errors.append({
                    'thread_id': thread_id,
                    'error': str(e)
                })

        # Start 15 concurrent queries
        threads = []
        start_time = time.time()

        for i in range(15):
            t = threading.Thread(target=query_task, args=(i,))
            t.start()
            threads.append(t)

        # Wait for all to complete
        for t in threads:
            t.join(timeout=10)

        total_time = time.time() - start_time

        print(f"\n=== Concurrent Query Performance ===")
        print(f"Threads: 15")
        print(f"Successful: {len(results)}")
        print(f"Errors: {len(errors)}")
        print(f"Total time: {total_time:.2f}s")

        if results:
            avg_latency = sum(r['latency_ms'] for r in results) / len(results)
            print(f"Average latency: {avg_latency:.2f}ms")

        # All queries should succeed
        assert len(errors) == 0, f"Concurrent queries failed: {errors}"
        assert len(results) == 15, "Not all queries completed"

        # Total time should be reasonable (not serialized)
        # If serialized, would take 15x single query time
        # With proper concurrency, should be much less
        assert total_time < 10, f"Concurrent execution too slow: {total_time:.2f}s"

    def test_concurrent_cache_safety(self, repo_path):
        """Test cache is thread-safe under concurrent access."""
        provider = ArchaeologyContextProvider(repo_path, cache_enabled=True)
        provider.initialize()

        file_path = "agents/full-stack-architect.md"
        question = "What is this?"

        # Pre-populate cache
        provider.get_context(file_path, question)

        cache_results = []

        def cache_query_task():
            """Task that should hit cache."""
            result = provider.get_context(file_path, question)
            cache_results.append(result['cached'])

        # 20 threads all querying same cached item
        threads = []
        for _ in range(20):
            t = threading.Thread(target=cache_query_task)
            t.start()
            threads.append(t)

        for t in threads:
            t.join(timeout=5)

        print(f"\n=== Cache Thread Safety ===")
        print(f"Total queries: {len(cache_results)}")
        print(f"Cache hits: {sum(cache_results)}")

        # All should be cache hits
        assert len(cache_results) == 20
        assert all(cache_results), "Cache not thread-safe"


class TestScalabilityPerformance:
    """Test scalability with repository size."""

    def test_performance_with_limited_commits(self, repo_path):
        """Test performance with different commit limits."""
        commit_limits = [10, 50, 100, None]  # None = all commits
        results = {}

        for limit in commit_limits:
            provider = ArchaeologyContextProvider(repo_path, cache_enabled=False)

            start = time.time()
            provider.initialize(max_commits=limit)
            init_time = time.time() - start

            start = time.time()
            result = provider.get_context(
                "agents/full-stack-architect.md",
                "What is this?"
            )
            query_time = time.time() - start

            results[str(limit)] = {
                'init_time': init_time,
                'query_time': query_time,
                'total_time': init_time + query_time,
            }

        print(f"\n=== Scalability Performance ===")
        for limit, times in results.items():
            print(f"Commits: {limit}")
            print(f"  Init: {times['init_time']:.2f}s")
            print(f"  Query: {times['query_time']:.2f}s")
            print(f"  Total: {times['total_time']:.2f}s")

        # Verify reasonable scaling
        # Full repo should complete in reasonable time
        if 'None' in results:
            assert results['None']['total_time'] < 60, \
                "Full repository analysis too slow"


class TestPerformanceRegression:
    """Test for performance regressions."""

    def test_query_performance_baseline(self, provider):
        """Establish performance baseline for regression testing."""
        # Standard query set
        queries = [
            ("agents/full-stack-architect.md", "What is this agent?"),
            ("tools/code_archaeology/git_analyzer.py", "How does it work?"),
            ("CLAUDE.md", "What are the instructions?"),
        ]

        latencies = []
        for file_path, question in queries:
            start = time.time()
            provider.get_context(file_path, question)
            latency = (time.time() - start) * 1000
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)

        print(f"\n=== Performance Baseline ===")
        print(f"Average query latency: {avg_latency:.2f}ms")
        print(f"Min latency: {min(latencies):.2f}ms")
        print(f"Max latency: {max(latencies):.2f}ms")

        # Store baseline for comparison
        # In CI/CD, this would be compared against historical data
        baseline_file = Path(__file__).parent / "performance_baseline.json"

        import json
        baseline_data = {
            'avg_latency_ms': avg_latency,
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'timestamp': time.time(),
        }

        # Would write to file in actual implementation
        # baseline_file.write_text(json.dumps(baseline_data, indent=2))

        print(f"Baseline established: {baseline_data}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
