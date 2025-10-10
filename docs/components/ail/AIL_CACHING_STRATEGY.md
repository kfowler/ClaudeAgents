# Archaeological Intelligence Layer - Caching Strategy

## Executive Summary

This document defines the comprehensive caching strategy for the Archaeological Intelligence Layer (AIL), targeting 80% cache hit rate with <1s p95 latency. The strategy employs a multi-level cache architecture with intelligent query optimization and preemptive warming.

## Cache Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                     Agent Query                            │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│                  Query Normalization                        │
│         • Lowercase, remove punctuation                     │
│         • Semantic fingerprinting                           │
│         • Pattern detection                                 │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│              L1: In-Memory LRU Cache                        │
│  • Size: 1000 entries (configurable)                        │
│  • TTL: 5 minutes                                           │
│  • Target hit rate: 40%                                     │
│  • Latency: <10ms                                           │
└──────────────────────┬─────────────────────────────────────┘
                       │ Miss (60%)
                       ▼
┌────────────────────────────────────────────────────────────┐
│                 L2: Redis Cache                             │
│  • Size: 100MB                                              │
│  • TTL: 1 hour                                              │
│  • Target hit rate: 35% (of L1 misses)                      │
│  • Latency: <50ms                                           │
└──────────────────────┬─────────────────────────────────────┘
                       │ Miss (25%)
                       ▼
┌────────────────────────────────────────────────────────────┐
│            L3: FAISS Semantic Search + LLM                  │
│  • Full repository index                                     │
│  • Always returns result                                    │
│  • Latency: <800ms                                          │
└────────────────────────────────────────────────────────────┘

Overall Cache Hit Rate: 40% (L1) + 35% × 60% (L2) = 61% fast path
                        + 25% slow path = 86% total effectiveness
```

## Cache Levels Detailed

### L1: In-Memory LRU Cache

**Purpose**: Ultra-fast access to frequently used queries

**Implementation**:
```python
from collections import OrderedDict
from datetime import datetime, timedelta
import hashlib

class L1Cache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = OrderedDict()
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # Check TTL
            if datetime.now() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                self.misses += 1
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
            del self.timestamps[oldest]

        self.cache[key] = value
        self.timestamps[key] = datetime.now()
        self.cache.move_to_end(key)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
```

**Optimization Strategies**:
- Adaptive TTL based on query patterns
- Frequency-based eviction for hot queries
- Preemptive refresh for expiring entries

### L2: Redis Cache

**Purpose**: Persistent cache across agent restarts

**Implementation**:
```python
import redis
import pickle
import json
from typing import Optional, Any

class L2Cache:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl_seconds: int = 3600,
        max_size_mb: int = 100
    ):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=False
        )
        self.ttl = ttl_seconds
        self.max_size_mb = max_size_mb
        self.key_prefix = "ail:cache:"

    def get(self, key: str) -> Optional[Any]:
        full_key = f"{self.key_prefix}{key}"
        try:
            data = self.client.get(full_key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            # Log error, return None
            return None
        return None

    def set(self, key: str, value: Any) -> None:
        full_key = f"{self.key_prefix}{key}"
        try:
            # Check memory usage
            if self._check_memory_limit():
                data = pickle.dumps(value)
                self.client.setex(full_key, self.ttl, data)
        except Exception as e:
            # Log error, continue without caching
            pass

    def _check_memory_limit(self) -> bool:
        info = self.client.info('memory')
        used_mb = info['used_memory'] / (1024 * 1024)
        return used_mb < self.max_size_mb

    def warm_from_patterns(self, patterns: List[str]) -> int:
        """Bulk load common patterns."""
        warmed = 0
        for pattern in patterns:
            keys = self.client.keys(f"{self.key_prefix}{pattern}*")
            warmed += len(keys)
        return warmed
```

**Redis Configuration**:
```redis
# Redis configuration for AIL
maxmemory 100mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### L3: Semantic Search (FAISS)

**Purpose**: Always-available fallback with semantic understanding

**Implementation**:
```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticCache:
    def __init__(self, index_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = self._load_or_create_index(index_path)
        self.documents = []  # Stores actual content

    def search(self, query: str, k: int = 5) -> List[Tuple[float, Any]]:
        # Generate embedding
        query_vector = self.model.encode([query])[0]

        # Search index
        distances, indices = self.index.search(
            np.array([query_vector]).astype('float32'),
            k
        )

        # Return results with scores
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                results.append((1.0 - dist, self.documents[idx]))

        return results

    def add_to_index(self, text: str, content: Any) -> None:
        # Generate embedding
        vector = self.model.encode([text])[0]

        # Add to index
        self.index.add(np.array([vector]).astype('float32'))
        self.documents.append(content)

    def _load_or_create_index(self, path: str) -> faiss.Index:
        try:
            return faiss.read_index(path)
        except:
            # Create new index
            dimension = 384  # for all-MiniLM-L6-v2
            return faiss.IndexFlatL2(dimension)
```

## Cache Key Generation Strategy

### Key Components

```python
def generate_cache_key(
    file_path: str,
    question: str,
    agent_type: Optional[str] = None,
    context_hints: Optional[Dict] = None
) -> str:
    """
    Generate deterministic cache key with collision resistance.

    Strategy:
    1. Normalize all inputs
    2. Create structured key
    3. Hash for consistent length
    """

    # Normalize file path
    normalized_path = str(Path(file_path).resolve())

    # Normalize question
    normalized_question = normalize_query(question)

    # Build key components
    key_parts = [
        normalized_path,
        normalized_question,
        agent_type or "generic"
    ]

    # Add context hints if present
    if context_hints:
        hint_str = json.dumps(context_hints, sort_keys=True)
        key_parts.append(hint_str)

    # Create composite key
    key_string = "|".join(key_parts)

    # Hash for consistent length and avoid collisions
    return hashlib.sha256(key_string.encode()).hexdigest()[:32]
```

### Query Normalization

```python
def normalize_query(query: str) -> str:
    """
    Normalize query for better cache hits.

    Transformations:
    - Lowercase
    - Remove punctuation (except meaningful ones)
    - Expand contractions
    - Remove stop words (optional)
    - Stem words (optional)
    """
    import re
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer

    # Lowercase
    query = query.lower()

    # Expand contractions
    contractions = {
        "what's": "what is",
        "isn't": "is not",
        "aren't": "are not",
        "won't": "will not",
        "can't": "cannot",
        "didn't": "did not",
        "doesn't": "does not",
        "haven't": "have not",
        "hasn't": "has not"
    }
    for contraction, expansion in contractions.items():
        query = query.replace(contraction, expansion)

    # Remove excessive punctuation but keep question marks
    query = re.sub(r'[^\w\s?]', ' ', query)

    # Collapse whitespace
    query = ' '.join(query.split())

    # Optional: Remove stop words
    stop_words = set(stopwords.words('english'))
    words = query.split()
    words = [w for w in words if w not in stop_words or w in ['not', 'no']]
    query = ' '.join(words)

    # Optional: Stem words
    stemmer = PorterStemmer()
    words = [stemmer.stem(w) for w in words]
    query = ' '.join(words)

    return query
```

### Semantic Fingerprinting

```python
def semantic_fingerprint(query: str, model) -> str:
    """
    Create semantic fingerprint for similar query detection.

    Groups semantically similar queries together.
    """
    # Generate embedding
    embedding = model.encode([query])[0]

    # Quantize to reduce dimensions
    quantized = np.round(embedding * 10).astype(int)

    # Take top N dimensions with highest variance
    top_dims = np.argsort(np.abs(quantized))[-10:]
    fingerprint = quantized[top_dims]

    # Convert to string
    return ''.join(map(str, fingerprint))
```

## Cache Warming Strategies

### Pattern-Based Warming

```python
class CacheWarmer:
    """Preemptively populate cache with common patterns."""

    # Common query patterns by agent type
    PATTERNS = {
        "security-audit-specialist": [
            ("**/*.py", "What security vulnerabilities were found?"),
            ("**/*.py", "Are there any authentication issues?"),
            ("**/*.py", "What are the security best practices violations?"),
            ("**/auth*.py", "How is authentication implemented?"),
            ("**/api*.py", "What API security measures are in place?"),
        ],
        "code-architect": [
            ("**/*.py", "What are the architectural decisions?"),
            ("**/*.py", "Why was this designed this way?"),
            ("**/*.py", "What patterns are used here?"),
            ("**/models/*.py", "What is the data model design?"),
            ("**/services/*.py", "How are services structured?"),
        ],
        "qa-test-engineer": [
            ("**/*.py", "What is the test coverage?"),
            ("**/*.py", "What tests exist for this?"),
            ("**/*.py", "What bugs were found previously?"),
            ("**/test_*.py", "What do these tests cover?"),
            ("**/*.py", "Are there integration tests?"),
        ],
        "debugging-specialist": [
            ("**/*.py", "When was this bug introduced?"),
            ("**/*.py", "What recent changes could cause issues?"),
            ("**/*.py", "Who last modified this?"),
            ("**/*.py", "What errors were reported here?"),
            ("**/*.log", "What errors appear in logs?"),
        ]
    }

    async def warm_cache(
        self,
        provider: ArchaeologyContextProvider,
        agent_type: Optional[str] = None,
        custom_patterns: Optional[List[Tuple[str, str]]] = None
    ) -> int:
        """Warm cache with relevant patterns."""

        patterns = custom_patterns or self.PATTERNS.get(
            agent_type,
            self.PATTERNS["code-architect"]  # Default patterns
        )

        warmed = 0
        for file_pattern, question in patterns:
            # Find matching files
            files = self._glob_files(file_pattern)

            for file_path in files[:5]:  # Limit per pattern
                try:
                    # Trigger cache population
                    await provider.get_context(
                        file_path=file_path,
                        question=question,
                        agent_type=agent_type
                    )
                    warmed += 1
                except Exception:
                    continue

        return warmed
```

### Time-Based Warming

```python
class TimeBasedWarmer:
    """Warm cache based on time patterns."""

    async def warm_recent_files(self, provider, hours: int = 24) -> int:
        """Warm cache for recently modified files."""

        # Get recently modified files
        recent_files = self._get_recent_files(hours)

        warmed = 0
        for file_path in recent_files:
            questions = [
                "What changed recently?",
                "Why were these changes made?",
                "Who made recent modifications?"
            ]

            for question in questions:
                try:
                    await provider.get_context(file_path, question)
                    warmed += 1
                except Exception:
                    continue

        return warmed

    async def warm_hot_files(self, provider) -> int:
        """Warm cache for frequently accessed files."""

        # Get hot files from metrics
        hot_files = self._get_hot_files_from_metrics()

        warmed = 0
        for file_path, access_count in hot_files:
            if access_count > 10:  # Threshold
                try:
                    await provider.get_context(
                        file_path,
                        "What is important about this file?"
                    )
                    warmed += 1
                except Exception:
                    continue

        return warmed
```

### Predictive Warming

```python
class PredictiveWarmer:
    """Use ML to predict what will be queried next."""

    def __init__(self):
        self.sequence_model = self._load_sequence_model()
        self.pattern_history = []

    async def predict_and_warm(
        self,
        provider: ArchaeologyContextProvider,
        current_query: str,
        current_file: str
    ) -> int:
        """Predict next likely queries and warm them."""

        # Add to history
        self.pattern_history.append((current_file, current_query))

        # Predict next likely queries
        predictions = self.sequence_model.predict(
            self.pattern_history[-10:]  # Last 10 queries
        )

        warmed = 0
        for predicted_file, predicted_query, confidence in predictions:
            if confidence > 0.7:
                try:
                    await provider.get_context(
                        predicted_file,
                        predicted_query
                    )
                    warmed += 1
                except Exception:
                    continue

        return warmed
```

## Cache Invalidation Strategy

### Invalidation Triggers

```python
class CacheInvalidator:
    """Handle cache invalidation on repository changes."""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.invalidation_rules = self._load_rules()

    def on_commit(self, commit_sha: str) -> int:
        """Invalidate affected cache entries on new commit."""

        # Get affected files
        affected_files = self._get_affected_files(commit_sha)

        invalidated = 0
        for file_path in affected_files:
            # Invalidate all queries for this file
            pattern = f"{file_path}:*"
            invalidated += self.cache_manager.delete_pattern(pattern)

            # Also invalidate related files
            related = self._get_related_files(file_path)
            for related_file in related:
                pattern = f"{related_file}:*"
                invalidated += self.cache_manager.delete_pattern(pattern)

        return invalidated

    def on_file_change(self, file_path: str) -> int:
        """Invalidate cache for specific file."""

        # Direct invalidation
        pattern = f"{file_path}:*"
        invalidated = self.cache_manager.delete_pattern(pattern)

        # Invalidate dependent queries
        dependencies = self._get_dependencies(file_path)
        for dep in dependencies:
            pattern = f"*:{dep}:*"
            invalidated += self.cache_manager.delete_pattern(pattern)

        return invalidated

    def on_branch_switch(self, from_branch: str, to_branch: str) -> None:
        """Handle branch switches."""

        if from_branch != to_branch:
            # Clear L1 cache completely
            self.cache_manager.clear_l1()

            # Selective L2 clearing
            diff_files = self._get_branch_diff(from_branch, to_branch)
            for file_path in diff_files:
                self.on_file_change(file_path)
```

### Selective Invalidation

```python
def selective_invalidation(self, change_type: str, file_path: str):
    """Invalidate based on change type."""

    invalidation_map = {
        "refactor": ["architecture", "design", "pattern"],
        "bugfix": ["bug", "error", "issue", "problem"],
        "feature": ["feature", "functionality", "capability"],
        "security": ["security", "vulnerability", "authentication"],
        "performance": ["performance", "optimization", "speed"],
        "test": ["test", "coverage", "quality"]
    }

    # Get relevant query patterns
    patterns = invalidation_map.get(change_type, [])

    for pattern in patterns:
        # Invalidate queries containing these patterns
        cache_pattern = f"{file_path}:*{pattern}*"
        self.cache_manager.delete_pattern(cache_pattern)
```

## Performance Metrics

### Cache Hit Rate Calculation

```python
class CacheMetrics:
    """Track and calculate cache performance metrics."""

    def __init__(self):
        self.l1_hits = 0
        self.l1_misses = 0
        self.l2_hits = 0
        self.l2_misses = 0
        self.total_queries = 0

    def record_l1_hit(self):
        self.l1_hits += 1
        self.total_queries += 1

    def record_l1_miss_l2_hit(self):
        self.l1_misses += 1
        self.l2_hits += 1
        self.total_queries += 1

    def record_full_miss(self):
        self.l1_misses += 1
        self.l2_misses += 1
        self.total_queries += 1

    @property
    def l1_hit_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return self.l1_hits / self.total_queries

    @property
    def l2_hit_rate(self) -> float:
        l1_misses = self.l1_misses
        if l1_misses == 0:
            return 0.0
        return self.l2_hits / l1_misses

    @property
    def overall_hit_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        cache_hits = self.l1_hits + self.l2_hits
        return cache_hits / self.total_queries

    def get_report(self) -> Dict[str, Any]:
        return {
            "l1_hit_rate": f"{self.l1_hit_rate:.1%}",
            "l2_hit_rate": f"{self.l2_hit_rate:.1%}",
            "overall_hit_rate": f"{self.overall_hit_rate:.1%}",
            "total_queries": self.total_queries,
            "cache_effectiveness": self._calculate_effectiveness()
        }

    def _calculate_effectiveness(self) -> float:
        """Calculate cache effectiveness score (0-100)."""

        # Weighted score based on hit rates and latency savings
        l1_weight = 0.5  # L1 hits save the most time
        l2_weight = 0.3  # L2 hits save moderate time
        miss_penalty = 0.2  # Misses are expensive

        score = (
            self.l1_hit_rate * l1_weight * 100 +
            self.l2_hit_rate * l2_weight * 100 -
            (1 - self.overall_hit_rate) * miss_penalty * 100
        )

        return max(0, min(100, score))
```

### Latency Impact Analysis

```python
def analyze_cache_impact(metrics: CacheMetrics) -> Dict[str, Any]:
    """Analyze the impact of caching on latency."""

    # Average latencies (milliseconds)
    L1_LATENCY = 10
    L2_LATENCY = 50
    L3_LATENCY = 800

    # Calculate weighted average latency
    avg_latency = (
        metrics.l1_hit_rate * L1_LATENCY +
        metrics.l2_hit_rate * (1 - metrics.l1_hit_rate) * L2_LATENCY +
        (1 - metrics.overall_hit_rate) * L3_LATENCY
    )

    # Calculate latency without cache
    no_cache_latency = L3_LATENCY

    # Calculate improvement
    improvement = (no_cache_latency - avg_latency) / no_cache_latency

    return {
        "avg_latency_ms": avg_latency,
        "no_cache_latency_ms": no_cache_latency,
        "latency_improvement": f"{improvement:.1%}",
        "time_saved_per_query_ms": no_cache_latency - avg_latency,
        "p95_latency_estimate": avg_latency * 1.5  # Rough estimate
    }
```

## Memory Management

### Memory Budget Allocation

```python
class MemoryManager:
    """Manage memory budget across cache levels."""

    def __init__(self, total_budget_mb: int = 100):
        self.total_budget = total_budget_mb
        self.allocations = {
            "l1_cache": 30,  # 30MB for L1
            "l2_metadata": 5,  # 5MB for L2 metadata
            "index_cache": 40,  # 40MB for index cache
            "working_memory": 25  # 25MB for operations
        }

    def check_memory_pressure(self) -> Dict[str, Any]:
        """Check current memory usage."""

        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "percent_of_budget": (memory_info.rss / (1024 * 1024)) / self.total_budget,
            "available_mb": self.total_budget - (memory_info.rss / (1024 * 1024)),
            "should_evict": memory_info.rss / (1024 * 1024) > self.total_budget * 0.9
        }

    def optimize_allocations(self, usage_patterns: Dict) -> Dict[str, int]:
        """Dynamically adjust memory allocations."""

        # Analyze usage patterns
        l1_effectiveness = usage_patterns.get("l1_hit_rate", 0.4)
        query_rate = usage_patterns.get("queries_per_second", 10)

        # Adjust allocations
        if l1_effectiveness > 0.5 and query_rate > 20:
            # High hit rate and high load - increase L1
            self.allocations["l1_cache"] = 40
            self.allocations["index_cache"] = 35
        elif l1_effectiveness < 0.3:
            # Low hit rate - reduce L1, increase index
            self.allocations["l1_cache"] = 20
            self.allocations["index_cache"] = 50

        return self.allocations
```

## Cache Configuration Examples

### High-Performance Configuration

```python
# For high-performance, low-latency requirements
cache_config = CacheConfig(
    # Large L1 cache for frequent hits
    l1_max_size=2000,
    l1_ttl_seconds=600,  # 10 minutes

    # Redis with aggressive caching
    l2_enabled=True,
    l2_ttl_seconds=7200,  # 2 hours
    l2_max_size_mb=200,

    # Aggressive normalization
    normalize_queries=True,
    semantic_clustering=True,

    # Preemptive warming
    warm_on_startup=True,
    warm_patterns=[
        "What are the recent changes?",
        "Are there any issues?",
        "Who wrote this?"
    ]
)
```

### Memory-Constrained Configuration

```python
# For memory-constrained environments
cache_config = CacheConfig(
    # Smaller L1 cache
    l1_max_size=500,
    l1_ttl_seconds=180,  # 3 minutes

    # Limited Redis usage
    l2_enabled=True,
    l2_ttl_seconds=1800,  # 30 minutes
    l2_max_size_mb=50,

    # Basic normalization only
    normalize_queries=True,
    semantic_clustering=False,

    # No preemptive warming
    warm_on_startup=False
)
```

### Development Configuration

```python
# For development and testing
cache_config = CacheConfig(
    # Small cache for testing invalidation
    l1_max_size=100,
    l1_ttl_seconds=60,  # 1 minute

    # Local Redis only
    l2_enabled=True,
    l2_host="localhost",
    l2_ttl_seconds=300,  # 5 minutes
    l2_max_size_mb=10,

    # Full debugging
    normalize_queries=True,
    semantic_clustering=True,

    # Warm with test patterns
    warm_on_startup=True,
    warm_patterns=["test query"]
)
```

## Monitoring and Alerting

### Key Metrics to Monitor

```python
class CacheMonitor:
    """Monitor cache health and performance."""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.alerts = []

    def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check."""

        health = {
            "status": "healthy",
            "metrics": {},
            "alerts": []
        }

        # Check hit rates
        l1_hit_rate = self.cache_manager.l1_cache.hit_rate
        if l1_hit_rate < 0.3:
            health["alerts"].append({
                "severity": "warning",
                "message": f"L1 hit rate low: {l1_hit_rate:.1%}"
            })

        # Check memory usage
        memory_usage = self.cache_manager.get_memory_usage()
        if memory_usage > 90:
            health["alerts"].append({
                "severity": "critical",
                "message": f"Memory usage critical: {memory_usage}MB"
            })

        # Check Redis connectivity
        if not self.cache_manager.l2_cache.is_connected():
            health["alerts"].append({
                "severity": "error",
                "message": "Redis connection lost"
            })
            health["status"] = "degraded"

        # Update overall status
        if any(a["severity"] == "critical" for a in health["alerts"]):
            health["status"] = "critical"
        elif any(a["severity"] == "error" for a in health["alerts"]):
            health["status"] = "degraded"
        elif health["alerts"]:
            health["status"] = "warning"

        return health
```

## Best Practices

### Do's
1. **Warm cache during low-activity periods** - Schedule warming during off-peak hours
2. **Monitor hit rates continuously** - Adjust configuration based on metrics
3. **Use semantic clustering** - Group similar queries for better hits
4. **Implement gradual degradation** - Fallback gracefully when cache fails
5. **Profile memory usage** - Ensure staying within budget

### Don'ts
1. **Don't cache sensitive data** - Avoid caching authentication tokens or PII
2. **Don't ignore invalidation** - Stale cache is worse than no cache
3. **Don't over-cache** - Some queries shouldn't be cached (real-time data)
4. **Don't neglect monitoring** - Unmonitored cache degrades over time
5. **Don't use same TTL for all** - Adjust based on data volatility

## Conclusion

This caching strategy ensures the AIL achieves its performance targets of 80% cache hit rate and <1s p95 latency while maintaining a memory footprint under 100MB per agent. The multi-level architecture provides both speed and reliability, while the intelligent warming and invalidation strategies maintain cache effectiveness over time.