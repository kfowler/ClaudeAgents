# AIL Sprint 2: Semantic Caching Quick Start

**Status**: Production Ready
**Date**: 2025-10-08

---

## Installation

### 1. Install Dependencies

```bash
pip install numpy faiss-cpu
```

**Note**: If FAISS is not available, semantic cache gracefully disables and falls back to L1-only caching.

### 2. Verify Installation

```bash
python3 -c "import faiss; print('FAISS version:', faiss.__version__)"
```

---

## Basic Usage

### Enable Semantic Caching (Default)

```python
from tools.ail.context_provider import ArchaeologyContextProvider

# Initialize with semantic caching enabled
provider = ArchaeologyContextProvider(
    repo_path=".",
    enable_semantic_cache=True  # Default: True
)

# Query as usual
context = await provider.get_context(
    "auth.py",
    "Why was JWT chosen for authentication?"
)

# Check cache performance
if context.cached:
    print(f"Cache hit: {context.cache_level}")
    print(f"Query time: {context.query_time_ms:.0f}ms")
```

### Monitor Performance

```python
# Get combined statistics
stats = provider.get_combined_cache_stats()

print(f"Combined hit rate: {stats['combined_hit_rate']}")
print(f"L1 hits: {stats['l1_hits']}")
print(f"L2 hits: {stats['l2_hits']}")
print(f"Total queries: {stats['total_queries']}")
```

### Disable Semantic Cache (L1-Only)

```python
# Disable L2 for A/B testing or if FAISS not available
provider = ArchaeologyContextProvider(
    repo_path=".",
    enable_semantic_cache=False  # L1-only (Sprint 1 behavior)
)
```

---

## Configuration Options

### Default (Recommended for Production)

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=1000,              # L1 size
    enable_semantic_cache=True,
    semantic_cache_size=500,      # L2 size
    similarity_threshold=0.85,    # L2 threshold
)
```

### High Performance (More Cache Hits)

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=1000,
    enable_semantic_cache=True,
    semantic_cache_size=500,
    similarity_threshold=0.82,    # Lower = more hits, less precision
)
```

### Memory Constrained

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=500,               # Smaller L1
    enable_semantic_cache=True,
    semantic_cache_size=250,      # Smaller L2
    similarity_threshold=0.88,    # Higher = less memory
)
```

### High Precision

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=1000,
    enable_semantic_cache=True,
    semantic_cache_size=500,
    similarity_threshold=0.90,    # Higher = fewer false positives
)
```

---

## Validation

### Run Performance Validation

```bash
python3 tools/ail/validate_semantic_cache.py
```

**Expected Output**:
```
================================================================================
VALIDATION SUMMARY
================================================================================
Hit Rate                       PASS
L2 Latency                     PASS
Memory Usage                   PASS
Statistics                     PASS

ALL TESTS PASSED
================================================================================
```

### Run Unit Tests

```bash
# With FAISS installed
python3 -m pytest tests/test_ail/test_semantic_cache.py -v

# Without FAISS (tests will skip gracefully)
python3 -m pytest tests/test_ail/test_semantic_cache.py -v
```

---

## Troubleshooting

### FAISS Not Available

**Symptom**: Warning message "FAISS not available, semantic cache disabled"

**Solution**:
```bash
pip install faiss-cpu
```

**Alternative**: Disable semantic cache explicitly:
```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    enable_semantic_cache=False
)
```

### Low Cache Hit Rate

**Symptom**: Combined hit rate < 85%

**Solutions**:
1. Lower similarity threshold:
   ```python
   provider.l2_cache.similarity_threshold = 0.82
   ```

2. Increase L2 cache size:
   ```python
   provider = ArchaeologyContextProvider(
       repo_path=".",
       semantic_cache_size=750  # Increased from 500
   )
   ```

3. Check query patterns:
   ```python
   stats = provider.get_combined_cache_stats()
   print(f"L2 avg similarity: {stats['l2_avg_similarity']:.3f}")
   ```

### High L2 Latency

**Symptom**: L2 lookup time > 50ms

**Solutions**:
1. Reduce L2 cache size:
   ```python
   provider = ArchaeologyContextProvider(
       repo_path=".",
       semantic_cache_size=250  # Reduced from 500
   )
   ```

2. Monitor latency:
   ```python
   stats = provider.l2_cache.get_stats()
   print(f"L2 avg lookup time: {stats.avg_lookup_time_ms:.1f}ms")
   ```

### Memory Usage Too High

**Symptom**: Memory usage > 20MB

**Solutions**:
1. Reduce cache sizes:
   ```python
   provider = ArchaeologyContextProvider(
       repo_path=".",
       cache_size=500,           # L1: reduced from 1000
       semantic_cache_size=250   # L2: reduced from 500
   )
   ```

2. Monitor memory:
   ```python
   import tracemalloc
   tracemalloc.start()
   # ... use provider ...
   current, peak = tracemalloc.get_traced_memory()
   print(f"Peak memory: {peak / (1024 * 1024):.1f} MB")
   ```

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Combined hit rate | ≥90% | ✅ Validated |
| L2 lookup latency | <50ms p95 | ✅ Validated |
| Memory usage | <20MB | ✅ Validated |
| Thread safety | Concurrent | ✅ Validated |

---

## API Reference

### ArchaeologyContextProvider

**New Parameters**:
- `enable_semantic_cache` (bool): Enable L2 semantic cache (default: True)
- `semantic_cache_size` (int): Max L2 entries (default: 500)
- `similarity_threshold` (float): L2 similarity threshold (default: 0.85)

**New Methods**:
- `get_combined_cache_stats()`: Get comprehensive cache statistics

### ArchaeologicalContext

**New Fields**:
- `cache_level` (str): "L1", "L2", or "" for no cache
- `similarity_score` (float): 1.0 for L1, 0.85-1.0 for L2

### TwoTierCache

**Methods**:
- `get(file_path, query, cache_key)`: Try both cache tiers
- `put(file_path, query, cache_key, result)`: Populate both tiers
- `get_combined_stats()`: Get comprehensive statistics
- `clear()`: Clear both cache levels

**Properties**:
- `l1_enabled`: True (always)
- `l2_enabled`: True if L2 cache initialized

### SemanticCache

**Methods**:
- `get(file_path, query)`: Search with semantic similarity
- `put(file_path, query, result)`: Add to cache
- `normalize_query(query)`: Normalize query text
- `clear()`: Clear all entries
- `get_stats()`: Get L2 statistics

**Properties**:
- `size`: Current cache size
- `enabled`: Whether L2 is enabled

---

## Examples

### Example 1: Similar Query Detection

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    enable_semantic_cache=True
)

# Query 1: Original
context1 = await provider.get_context(
    "auth.py",
    "Why was JWT chosen for authentication?"
)
# Result: Backend query, populates L1+L2

# Query 2: Exact repeat
context2 = await provider.get_context(
    "auth.py",
    "Why was JWT chosen for authentication?"
)
# Result: L1 hit (2ms)
assert context2.cache_level == "L1"
assert context2.similarity_score == 1.0

# Query 3: Similar wording
context3 = await provider.get_context(
    "auth.py",
    "What's the reason for JWT?"
)
# Result: L2 hit (30ms), promoted to L1
assert context3.cache_level == "L2"
assert context3.similarity_score >= 0.85

# Query 4: Same as Query 3
context4 = await provider.get_context(
    "auth.py",
    "What's the reason for JWT?"
)
# Result: L1 hit (2ms) - promoted from L2
assert context4.cache_level == "L1"
```

### Example 2: Performance Monitoring

```python
import asyncio

async def monitor_performance():
    provider = ArchaeologyContextProvider(
        repo_path=".",
        enable_semantic_cache=True
    )

    # Simulate workload
    queries = [
        ("auth.py", "Why JWT?"),
        ("auth.py", "Why JWT?"),  # Exact repeat
        ("auth.py", "JWT reason?"),  # Similar
        ("config.py", "Config purpose?"),
    ]

    for file_path, question in queries:
        context = await provider.get_context(file_path, question)
        print(f"{context.cache_level or 'MISS':>4} | "
              f"{context.query_time_ms:>6.0f}ms | "
              f"{question}")

    # Display statistics
    stats = provider.get_combined_cache_stats()
    print("\nCache Performance:")
    print(f"  Combined hit rate: {stats['combined_hit_rate']}")
    print(f"  L1 hits: {stats['l1_hits']}")
    print(f"  L2 hits: {stats['l2_hits']}")

asyncio.run(monitor_performance())
```

### Example 3: Adaptive Threshold Tuning

```python
async def adaptive_tuning():
    provider = ArchaeologyContextProvider(
        repo_path=".",
        enable_semantic_cache=True
    )

    # Run queries
    for i in range(100):
        await provider.get_context("file.py", f"query {i}")

    # Check L2 performance
    stats = provider.l2_cache.get_stats()

    if stats.hit_rate < 0.15:
        # Too few hits, lower threshold
        old_threshold = provider.l2_cache.similarity_threshold
        provider.l2_cache.similarity_threshold = 0.82
        print(f"Lowered threshold: {old_threshold} → 0.82")

    elif stats.avg_similarity < 0.90:
        # Low quality hits, raise threshold
        old_threshold = provider.l2_cache.similarity_threshold
        provider.l2_cache.similarity_threshold = 0.88
        print(f"Raised threshold: {old_threshold} → 0.88")

asyncio.run(adaptive_tuning())
```

---

## Resources

- **Full Documentation**: `AIL_SPRINT_2_IMPLEMENTATION.md`
- **Design Spec**: `AIL_SPRINT_2_SEMANTIC_CACHE_DESIGN.md`
- **Executive Summary**: `AIL_SPRINT_2_SEMANTIC_CACHE_SUMMARY.md`
- **Test Suite**: `tests/test_ail/test_semantic_cache.py`
- **Validation Tool**: `tools/ail/validate_semantic_cache.py`

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Run validation tool: `python3 tools/ail/validate_semantic_cache.py`
3. Review full documentation
4. Check test output: `pytest tests/test_ail/test_semantic_cache.py -v`

---

**Sprint 2 Status**: ✅ COMPLETE
**Production Ready**: ✅ YES
**Last Updated**: 2025-10-08
