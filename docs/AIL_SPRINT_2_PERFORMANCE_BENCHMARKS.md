# AIL Sprint 2: Performance Benchmark Plan

**Version**: 1.0.0
**Date**: 2025-10-08
**Status**: COMPLETE

---

## 1. Executive Summary

This document defines the comprehensive performance benchmarking strategy for AIL Sprint 2 FAISS integration. The plan ensures we meet our target of <500ms p95 latency (41% improvement from 847ms baseline) while maintaining <150MB memory footprint.

---

## 2. Benchmark Categories

### 2.1 Latency Benchmarks

```python
class LatencyBenchmarks:
    """Measure end-to-end and component latencies."""

    def benchmark_cache_hit(self) -> Dict[str, float]:
        """
        Measure cache hit performance.
        Target: <5ms p95
        """
        results = []
        for _ in range(1000):
            start = time.perf_counter()
            context = provider.get_context_sync(
                "cached_file.py",
                "cached question"
            )
            results.append((time.perf_counter() - start) * 1000)

        return {
            'p50_ms': np.percentile(results, 50),
            'p95_ms': np.percentile(results, 95),
            'p99_ms': np.percentile(results, 99),
            'mean_ms': np.mean(results),
            'std_ms': np.std(results)
        }

    def benchmark_faiss_search(self) -> Dict[str, float]:
        """
        Measure FAISS search performance.
        Target: <50ms p95
        """
        # Prepare test queries
        queries = [
            "Why was this function deprecated?",
            "What was the original design decision?",
            "Who implemented this feature?",
            # ... 100 diverse queries
        ]

        results = []
        for query in queries:
            embedding = embedder.embed_query(query)
            start = time.perf_counter()
            hits = faiss_index.search(embedding, k=20)
            results.append((time.perf_counter() - start) * 1000)

        return analyze_latencies(results)

    def benchmark_end_to_end(self) -> Dict[str, float]:
        """
        Measure complete query latency.
        Target: <500ms p95
        """
        test_cases = load_test_cases()  # 100 diverse queries
        results = []

        for file_path, question in test_cases:
            start = time.perf_counter()
            context = provider.get_context_sync(file_path, question)
            results.append((time.perf_counter() - start) * 1000)

        return analyze_latencies(results)
```

### 2.2 Memory Benchmarks

```python
class MemoryBenchmarks:
    """Measure memory consumption across components."""

    def benchmark_baseline_memory(self) -> Dict[str, float]:
        """
        Measure baseline AIL memory usage.
        Target: ~78.4MB
        """
        import psutil
        import gc

        gc.collect()
        process = psutil.Process()

        # Baseline before initialization
        mem_before = process.memory_info().rss / 1024 / 1024

        # Initialize AIL without FAISS
        provider = ArchaeologyContextProvider(repo_path=".")
        provider._initialize_components()

        # Measure after initialization
        mem_after = process.memory_info().rss / 1024 / 1024

        return {
            'baseline_mb': mem_before,
            'ail_mb': mem_after - mem_before,
            'total_mb': mem_after
        }

    def benchmark_faiss_memory(self) -> Dict[str, float]:
        """
        Measure FAISS component memory.
        Target: <70MB incremental
        """
        measurements = {}

        # Measure embedding model
        mem_before = get_memory_usage()
        embedder = EmbeddingGenerator()
        measurements['embedding_model_mb'] = get_memory_usage() - mem_before

        # Measure FAISS index (1000 docs)
        mem_before = get_memory_usage()
        index = build_faiss_index(1000)
        measurements['faiss_index_1k_mb'] = get_memory_usage() - mem_before

        # Measure with 5000 docs
        index = build_faiss_index(5000)
        measurements['faiss_index_5k_mb'] = get_memory_usage() - mem_before

        return measurements

    def benchmark_memory_growth(self) -> List[Dict[str, float]]:
        """
        Measure memory growth over time.
        Target: <150MB after 1000 queries
        """
        measurements = []
        provider = ArchaeologyContextProvider(repo_path=".")

        for i in range(0, 1001, 100):
            # Run queries
            for _ in range(100):
                provider.get_context_sync(
                    f"file_{random.randint(1,100)}.py",
                    f"question {random.randint(1,1000)}"
                )

            # Measure memory
            measurements.append({
                'queries': i,
                'memory_mb': get_memory_usage(),
                'cache_size': provider.cache.size,
                'embedding_cache_size': len(provider._embedding_generator._cache)
            })

        return measurements
```

### 2.3 Throughput Benchmarks

```python
class ThroughputBenchmarks:
    """Measure system throughput and scalability."""

    def benchmark_embedding_throughput(self) -> Dict[str, float]:
        """
        Measure embedding generation throughput.
        Target: >100 docs/second
        """
        embedder = EmbeddingGenerator()
        test_texts = generate_test_texts(1000)

        start = time.perf_counter()
        embeddings = embedder.embed_batch(test_texts)
        elapsed = time.perf_counter() - start

        return {
            'total_docs': len(test_texts),
            'total_time_s': elapsed,
            'docs_per_second': len(test_texts) / elapsed,
            'ms_per_doc': (elapsed * 1000) / len(test_texts)
        }

    def benchmark_index_build_time(self) -> Dict[str, float]:
        """
        Measure index build performance.
        Target: <30s for 1000 commits
        """
        results = {}

        for num_commits in [100, 500, 1000, 2000, 5000]:
            commits = load_commits(num_commits)

            start = time.perf_counter()
            embeddings, doc_ids = embedder.embed_commits(commits)
            index.add_documents(embeddings, doc_ids)
            elapsed = time.perf_counter() - start

            results[f'build_{num_commits}_commits'] = {
                'time_s': elapsed,
                'commits_per_second': num_commits / elapsed
            }

        return results

    def benchmark_concurrent_queries(self) -> Dict[str, float]:
        """
        Measure concurrent query performance.
        Target: Support 10 concurrent queries
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        async def run_concurrent_test(num_concurrent: int):
            queries = generate_test_queries(num_concurrent * 10)

            async def query_task(q):
                start = time.perf_counter()
                await provider.get_context(q['file'], q['question'])
                return time.perf_counter() - start

            # Run batches concurrently
            results = []
            for i in range(0, len(queries), num_concurrent):
                batch = queries[i:i+num_concurrent]
                tasks = [query_task(q) for q in batch]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)

            return analyze_latencies([r * 1000 for r in results])

        results = {}
        for concurrency in [1, 5, 10, 20]:
            results[f'concurrent_{concurrency}'] = asyncio.run(
                run_concurrent_test(concurrency)
            )

        return results
```

### 2.4 Accuracy Benchmarks

```python
class AccuracyBenchmarks:
    """Measure search accuracy and relevance."""

    def benchmark_recall_at_k(self) -> Dict[str, float]:
        """
        Measure recall at different k values.
        Target: >90% recall@10
        """
        # Create ground truth dataset
        ground_truth = create_ground_truth_dataset()

        results = {}
        for k in [5, 10, 20]:
            recalls = []

            for query, expected_docs in ground_truth.items():
                embedding = embedder.embed_query(query)
                retrieved = faiss_index.search(embedding, k=k)
                retrieved_ids = [doc_id for doc_id, _ in retrieved]

                # Calculate recall
                relevant_retrieved = len(
                    set(expected_docs) & set(retrieved_ids)
                )
                recall = relevant_retrieved / len(expected_docs)
                recalls.append(recall)

            results[f'recall@{k}'] = {
                'mean': np.mean(recalls),
                'std': np.std(recalls),
                'min': np.min(recalls),
                'max': np.max(recalls)
            }

        return results

    def benchmark_semantic_similarity(self) -> Dict[str, float]:
        """
        Measure semantic similarity accuracy.
        Target: >0.8 correlation with human judgments
        """
        # Load human-annotated similarity pairs
        test_pairs = load_similarity_test_pairs()

        correlations = []
        for pair in test_pairs:
            # Generate embeddings
            emb1 = embedder.embed_query(pair['text1'])
            emb2 = embedder.embed_query(pair['text2'])

            # Calculate cosine similarity
            similarity = cosine_similarity(emb1, emb2)

            correlations.append({
                'predicted': similarity,
                'human': pair['human_score']
            })

        # Calculate correlation
        predicted = [c['predicted'] for c in correlations]
        human = [c['human'] for c in correlations]

        return {
            'pearson_correlation': pearsonr(predicted, human)[0],
            'spearman_correlation': spearmanr(predicted, human)[0],
            'mean_absolute_error': mean_absolute_error(predicted, human)
        }
```

---

## 3. Benchmark Test Data

### 3.1 Test Repository Structure

```yaml
test_repository:
  commits: 1000
  pull_requests: 200
  issues: 150
  file_types:
    - python: 60%
    - javascript: 20%
    - markdown: 10%
    - other: 10%
  commit_distribution:
    - feature: 40%
    - bugfix: 30%
    - refactor: 20%
    - docs: 10%
```

### 3.2 Query Test Cases

```python
QUERY_TEST_CASES = [
    # Architecture queries
    {
        'file': 'src/core/engine.py',
        'question': 'Why was the event-driven architecture chosen?',
        'expected_keywords': ['scalability', 'decoupling', 'async']
    },
    # Bug history queries
    {
        'file': 'api/auth/handler.py',
        'question': 'What security issues were previously fixed here?',
        'expected_keywords': ['vulnerability', 'CVE', 'patch']
    },
    # Performance queries
    {
        'file': 'database/queries.py',
        'question': 'What optimizations were made to improve query performance?',
        'expected_keywords': ['index', 'optimization', 'latency']
    },
    # ... 100+ diverse test cases
]
```

---

## 4. Benchmark Execution Plan

### 4.1 Automated Benchmark Suite

```python
class AILBenchmarkSuite:
    """Complete benchmark suite for AIL Sprint 2."""

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Execute all benchmarks and generate report."""

        results = {
            'timestamp': datetime.now().isoformat(),
            'version': 'sprint-2-faiss',
            'environment': self.get_environment_info(),
            'benchmarks': {}
        }

        # Run each category
        benchmark_classes = [
            LatencyBenchmarks(),
            MemoryBenchmarks(),
            ThroughputBenchmarks(),
            AccuracyBenchmarks()
        ]

        for bench_class in benchmark_classes:
            class_name = bench_class.__class__.__name__
            results['benchmarks'][class_name] = {}

            # Run all methods starting with 'benchmark_'
            for method_name in dir(bench_class):
                if method_name.startswith('benchmark_'):
                    method = getattr(bench_class, method_name)
                    try:
                        result = method()
                        results['benchmarks'][class_name][method_name] = result
                    except Exception as e:
                        results['benchmarks'][class_name][method_name] = {
                            'error': str(e)
                        }

        # Generate summary
        results['summary'] = self.generate_summary(results)

        # Check against targets
        results['passed'] = self.check_targets(results)

        return results

    def check_targets(self, results: Dict) -> bool:
        """Check if results meet Sprint 2 targets."""

        checks = {
            'latency_p95': results['benchmarks']['LatencyBenchmarks']
                           ['benchmark_end_to_end']['p95_ms'] < 500,
            'memory_total': results['benchmarks']['MemoryBenchmarks']
                           ['benchmark_memory_growth'][-1]['memory_mb'] < 150,
            'search_time': results['benchmarks']['LatencyBenchmarks']
                          ['benchmark_faiss_search']['p95_ms'] < 50,
            'recall_at_10': results['benchmarks']['AccuracyBenchmarks']
                           ['benchmark_recall_at_k']['recall@10']['mean'] > 0.9
        }

        return all(checks.values())
```

### 4.2 Continuous Benchmarking

```yaml
# .github/workflows/benchmark.yml
name: AIL Performance Benchmarks

on:
  push:
    branches: [main, sprint-2-faiss]
  pull_request:
    paths:
      - 'tools/ail/**'
      - 'tests/benchmarks/**'

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install faiss-cpu sentence-transformers

      - name: Run benchmarks
        run: |
          python -m pytest tests/benchmarks/test_ail_performance.py \
            --benchmark-only \
            --benchmark-json=benchmark_results.json

      - name: Check performance targets
        run: |
          python scripts/check_performance_targets.py benchmark_results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark_results.json
```

---

## 5. Performance Targets Summary

| Metric | Current (Sprint 1) | Target (Sprint 2) | Improvement |
|--------|-------------------|-------------------|-------------|
| **Latency (p95)** | 847ms | <500ms | 41% |
| **Latency (p50)** | 523ms | <300ms | 43% |
| **Cache Hit** | 5ms | <5ms | - |
| **FAISS Search** | N/A | <50ms | New |
| **Memory Total** | 78.4MB | <150MB | +91% allowed |
| **Index Build (1k)** | N/A | <30s | New |
| **Throughput** | 50 q/s | 100 q/s | 100% |
| **Recall@10** | N/A | >90% | New |
| **Concurrent Queries** | 5 | 10 | 100% |

---

## 6. Benchmark Report Template

```markdown
# AIL Sprint 2 Performance Report

**Date**: {{timestamp}}
**Version**: {{version}}
**Status**: {{PASS/FAIL}}

## Executive Summary
{{summary}}

## Latency Performance
- **p95 End-to-End**: {{p95_ms}}ms (Target: <500ms) {{✅/❌}}
- **p50 End-to-End**: {{p50_ms}}ms (Target: <300ms) {{✅/❌}}
- **FAISS Search p95**: {{search_p95}}ms (Target: <50ms) {{✅/❌}}

## Memory Performance
- **Total Usage**: {{total_mb}}MB (Target: <150MB) {{✅/❌}}
- **Embedding Model**: {{model_mb}}MB
- **FAISS Index**: {{index_mb}}MB
- **Cache**: {{cache_mb}}MB

## Accuracy Metrics
- **Recall@10**: {{recall_10}}% (Target: >90%) {{✅/❌}}
- **Semantic Correlation**: {{correlation}} (Target: >0.8) {{✅/❌}}

## Recommendations
{{recommendations}}
```

---

## 7. Performance Optimization Strategies

### 7.1 If Latency Target Not Met

1. **Reduce Embedding Dimension**
   - Try 256d instead of 384d
   - Use distilled models

2. **Optimize FAISS Parameters**
   - Reduce `ef_search` for faster queries
   - Use IVF index for larger datasets

3. **Implement Caching**
   - Cache query embeddings
   - Pre-compute common queries

### 7.2 If Memory Target Not Met

1. **Use Smaller Model**
   - paraphrase-MiniLM-L3-v2 (17M params)
   - TinyBERT variants

2. **Optimize Index Storage**
   - Use quantized indexes (IndexPQ)
   - Implement index pruning

3. **Manage Cache Size**
   - Reduce LRU cache size
   - Implement TTL for embeddings

### 7.3 If Accuracy Target Not Met

1. **Improve Embeddings**
   - Fine-tune on code-specific data
   - Use larger models (mpnet-base)

2. **Enhance Text Preparation**
   - Include more context
   - Better commit text representation

3. **Implement Reranking**
   - Cross-encoder reranking
   - Ensemble methods

---

## 8. Monitoring Dashboard Metrics

```python
DASHBOARD_METRICS = {
    'real_time': [
        'current_latency_p95',
        'current_memory_mb',
        'queries_per_second',
        'cache_hit_rate'
    ],
    'hourly': [
        'avg_latency_p95',
        'max_memory_mb',
        'total_queries',
        'error_rate'
    ],
    'daily': [
        'latency_trend',
        'memory_trend',
        'accuracy_metrics',
        'index_statistics'
    ]
}
```

---

*End of Performance Benchmark Plan*