# Archaeological Intelligence Layer (AIL) - Technical Specification

## Executive Summary

The Archaeological Intelligence Layer (AIL) provides context-aware capabilities to all 71 Claude agents by seamlessly integrating Cognitive Code Archaeology (CCA) insights. This specification defines the `ArchaeologyContextProvider` class architecture, API contract, caching strategy, and performance requirements.

**Key Goals:**
- Make CCA accessible to all agents automatically
- Achieve <1s p95 latency for context retrieval
- Maintain <100MB memory overhead per agent
- Support concurrent agent requests with 80% cache hit rate

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Layer (71 Agents)                 │
├─────────────────────────────────────────────────────────────┤
│              Archaeological Intelligence Layer (AIL)         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         ArchaeologyContextProvider (Main API)          │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │ │
│  │ │  Query   │ │  Cache   │ │ Context  │ │ Circuit  │  │ │
│  │ │ Optimizer│ │ Manager  │ │ Enricher │ │ Breaker  │  │ │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    CCA Core Components                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │GitArchaeolog.│ │GitHub Integ. │ │Context Synthesiz│   │
│  └──────────────┘ └──────────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Storage & Indexing Layer                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ FAISS Index  │ │ Redis Cache  │ │ SQLite Metadata │   │
│  └──────────────┘ └──────────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. ArchaeologyContextProvider (Main API)
- Primary interface for all agents
- Coordinates sub-components
- Manages lifecycle and error handling
- Implements graceful degradation

#### 2. Query Optimizer
- Normalizes and enhances agent queries
- Identifies query patterns for caching
- Expands queries with semantic variations
- Routes queries to appropriate indexes

#### 3. Cache Manager
- Multi-level caching (L1: in-memory, L2: Redis)
- LRU eviction with TTL management
- Query fingerprinting for cache keys
- Preemptive cache warming for common patterns

#### 4. Context Enricher
- Augments raw CCA results with agent-specific context
- Filters irrelevant information based on agent type
- Adds temporal context and related commits
- Formats output for agent consumption

#### 5. Circuit Breaker
- Monitors CCA component health
- Implements fallback strategies
- Prevents cascade failures
- Provides degraded service when necessary

## API Contract

### Primary Interface

```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class ArchaeologicalContext:
    """Context retrieved from CCA for agent consumption."""

    query: str
    file_path: str
    agent_type: str

    # Core content
    answer: str
    confidence: float  # 0.0 to 1.0

    # Supporting evidence
    citations: List[Citation]
    related_commits: List[CommitSummary]
    architectural_decisions: List[ArchDecision]

    # Metadata
    retrieval_time_ms: float
    cache_hit: bool
    degraded_mode: bool

    # Agent-specific enrichments
    agent_hints: Dict[str, Any]
    suggested_actions: List[str]

    @property
    def is_high_confidence(self) -> bool:
        """Check if context meets confidence threshold."""
        return self.confidence >= 0.7 and len(self.citations) >= 2

@dataclass
class Citation:
    """Simplified citation for agent use."""
    sha: str
    message: str
    author: str
    date: datetime
    relevance: float
    url: Optional[str]

@dataclass
class CommitSummary:
    """Summarized commit information."""
    sha: str
    summary: str
    impact: str  # "high", "medium", "low"
    files_affected: int

@dataclass
class ArchDecision:
    """Architectural decision record."""
    decision: str
    rationale: str
    alternatives: List[str]
    date: datetime
    commit_sha: str
```

### Core API Methods

```python
class ArchaeologyContextProvider:
    """Main API for Archaeological Intelligence Layer."""

    def __init__(
        self,
        repo_path: str,
        cache_config: Optional[CacheConfig] = None,
        performance_config: Optional[PerformanceConfig] = None
    ):
        """
        Initialize AIL provider.

        Args:
            repo_path: Path to repository
            cache_config: Cache configuration
            performance_config: Performance tuning parameters
        """
        pass

    async def get_context(
        self,
        file_path: str,
        question: str,
        agent_type: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> ArchaeologicalContext:
        """
        Get archaeological context for a file and question.

        Args:
            file_path: Target file path (absolute or relative)
            question: Natural language question
            agent_type: Type of agent making request (for optimization)
            context_hints: Additional context from agent

        Returns:
            ArchaeologicalContext with relevant information

        Raises:
            ContextRetrievalError: If context cannot be retrieved

        Performance:
            - p50 latency: <500ms
            - p95 latency: <1000ms
            - p99 latency: <2000ms
        """
        pass

    def get_context_sync(
        self,
        file_path: str,
        question: str,
        agent_type: Optional[str] = None
    ) -> ArchaeologicalContext:
        """Synchronous version of get_context."""
        pass

    async def batch_get_context(
        self,
        requests: List[Tuple[str, str]],
        agent_type: Optional[str] = None
    ) -> List[ArchaeologicalContext]:
        """
        Batch retrieve context for multiple file/question pairs.

        Args:
            requests: List of (file_path, question) tuples
            agent_type: Type of agent making request

        Returns:
            List of contexts in same order as requests

        Performance:
            - Optimized for batch processing
            - Parallel retrieval where possible
        """
        pass

    async def warm_cache(
        self,
        patterns: Optional[List[str]] = None
    ) -> int:
        """
        Preemptively warm cache with common queries.

        Args:
            patterns: Query patterns to warm (None = use defaults)

        Returns:
            Number of cache entries warmed
        """
        pass

    async def get_file_history(
        self,
        file_path: str,
        limit: int = 10
    ) -> List[CommitSummary]:
        """
        Get simplified commit history for a file.

        Args:
            file_path: Target file
            limit: Maximum commits to return

        Returns:
            List of commit summaries
        """
        pass

    async def search_architectural_decisions(
        self,
        query: str,
        limit: int = 5
    ) -> List[ArchDecision]:
        """
        Search for architectural decisions.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of architectural decisions
        """
        pass

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of AIL components.

        Returns:
            Dictionary with component health metrics
        """
        pass

    async def shutdown(self):
        """Graceful shutdown of AIL components."""
        pass
```

### Configuration Classes

```python
@dataclass
class CacheConfig:
    """Cache configuration parameters."""

    # L1 Cache (in-memory)
    l1_max_size: int = 1000  # entries
    l1_ttl_seconds: int = 300  # 5 minutes

    # L2 Cache (Redis)
    l2_enabled: bool = True
    l2_host: str = "localhost"
    l2_port: int = 6379
    l2_db: int = 0
    l2_ttl_seconds: int = 3600  # 1 hour
    l2_max_size_mb: int = 100

    # Query fingerprinting
    normalize_queries: bool = True
    semantic_clustering: bool = True

    # Preemptive warming
    warm_on_startup: bool = True
    warm_patterns: List[str] = None

@dataclass
class PerformanceConfig:
    """Performance tuning configuration."""

    # Concurrency
    max_concurrent_requests: int = 10
    request_timeout_ms: int = 2000

    # Circuit breaker
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60

    # Resource limits
    max_memory_mb: int = 100
    max_index_size_mb: int = 500

    # Degraded mode thresholds
    enable_degraded_mode: bool = True
    degraded_mode_latency_ms: int = 1500

    # Batching
    batch_size: int = 20
    batch_timeout_ms: int = 100
```

## Caching Strategy

### Multi-Level Cache Architecture

```
┌─────────────────────────────────────────┐
│            Agent Request                │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│     L1: In-Memory LRU Cache             │
│   • Size: 1000 entries                  │
│   • TTL: 5 minutes                      │
│   • Hit rate target: 40%                │
└─────────────┬───────────────────────────┘
              │ Miss
              ▼
┌─────────────────────────────────────────┐
│        L2: Redis Cache                  │
│   • Size: 100MB                         │
│   • TTL: 1 hour                         │
│   • Hit rate target: 35%                │
└─────────────┬───────────────────────────┘
              │ Miss
              ▼
┌─────────────────────────────────────────┐
│    L3: FAISS Semantic Search            │
│   • Full index search                   │
│   • Query optimization                  │
│   • Hit rate: 100% (always returns)     │
└─────────────────────────────────────────┘
```

### Cache Key Generation

```python
def generate_cache_key(
    file_path: str,
    question: str,
    agent_type: Optional[str]
) -> str:
    """
    Generate deterministic cache key.

    Strategy:
    1. Normalize file path (resolve symlinks, relative paths)
    2. Normalize question (lowercase, remove punctuation)
    3. Include agent type for specialization
    4. Hash for consistent length
    """
    normalized_path = Path(file_path).resolve()
    normalized_question = normalize_query(question)

    key_parts = [
        str(normalized_path),
        normalized_question,
        agent_type or "generic"
    ]

    key_string = "|".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()[:32]
```

### Cache Warming Strategy

```python
# Common query patterns for preemptive warming
WARM_PATTERNS = [
    # Code review patterns
    ("**/src/**/*.py", "What are the recent changes?"),
    ("**/src/**/*.py", "Are there any security issues?"),
    ("**/src/**/*.py", "What is the test coverage?"),

    # Architecture patterns
    ("**/src/**/*.py", "Why was this designed this way?"),
    ("**/src/**/*.py", "What are the architectural decisions?"),

    # Debugging patterns
    ("**/src/**/*.py", "When was this bug introduced?"),
    ("**/src/**/*.py", "Who worked on this feature?"),

    # Refactoring patterns
    ("**/src/**/*.py", "Can this be simplified?"),
    ("**/src/**/*.py", "What are the dependencies?"),
]
```

### Cache Invalidation

```python
class CacheInvalidator:
    """Handle cache invalidation on repository changes."""

    def on_commit(self, commit_sha: str):
        """Invalidate affected cache entries on new commit."""
        affected_files = self.get_affected_files(commit_sha)
        for file_path in affected_files:
            self.invalidate_file_cache(file_path)

    def on_file_change(self, file_path: str):
        """Invalidate cache for specific file."""
        pattern = f"{file_path}:*"
        self.l1_cache.delete_pattern(pattern)
        self.l2_cache.delete_pattern(pattern)

    def on_reindex(self):
        """Full cache clear on reindex."""
        self.l1_cache.clear()
        self.l2_cache.flushdb()
```

## Performance Requirements

### Latency Targets

| Metric | Target | Measurement Point |
|--------|--------|-------------------|
| p50 latency | <500ms | `get_context()` method |
| p95 latency | <1000ms | `get_context()` method |
| p99 latency | <2000ms | `get_context()` method |
| Cache hit (L1) | <10ms | L1 cache retrieval |
| Cache hit (L2) | <50ms | L2 cache retrieval |
| FAISS search | <200ms | Semantic search |
| LLM synthesis | <800ms | Answer generation |

### Throughput Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Concurrent requests | 10 | Per provider instance |
| Requests per second | 50 | With caching |
| Batch size | 20 | For batch operations |
| Queue depth | 100 | Maximum queued requests |

### Resource Constraints

| Resource | Limit | Monitoring |
|----------|-------|------------|
| Memory per agent | <100MB | RSS memory |
| L1 cache size | 1000 entries | LRU eviction |
| L2 cache size | 100MB | Redis memory |
| FAISS index | 500MB | Disk usage |
| CPU usage | <25% | Average over 1 min |

## Integration with Existing CCA

### Component Reuse

```python
class ArchaeologyContextProvider:
    def __init__(self, repo_path: str, **kwargs):
        # Reuse existing CCA components
        self.git_archaeologist = GitArchaeologist(repo_path)
        self.github_integrator = GitHubArchaeologist(
            owner=kwargs.get('github_owner'),
            repo=kwargs.get('github_repo')
        )
        self.context_synthesizer = ContextSynthesizer()

        # Initialize history and index once
        self._initialize_index()

    def _initialize_index(self):
        """One-time initialization of search index."""
        # Analyze repository
        history = self.git_archaeologist.analyze_repo()

        # Enrich with GitHub if available
        if self.github_integrator.is_configured():
            enriched = self.github_integrator.enrich_history(history)
        else:
            enriched = self._create_minimal_enriched(history)

        # Build searchable index
        self.index = self.context_synthesizer.build_searchable_index(enriched)
```

### Backward Compatibility

The AIL maintains full backward compatibility with the existing CCA CLI:

1. **CLI continues to work**: Existing `archaeology` command unchanged
2. **Shared indexes**: CLI and AIL use same FAISS indexes
3. **Common cache**: Redis cache shared between CLI and AIL
4. **Analytics integration**: Telemetry flows to same system

## Graceful Degradation

### Degradation Levels

```python
class DegradationLevel(Enum):
    NONE = 0  # Full functionality
    GITHUB_UNAVAILABLE = 1  # No GitHub enrichment
    LLM_UNAVAILABLE = 2  # No semantic synthesis
    INDEX_CORRUPTED = 3  # Fallback to git log
    TOTAL_FAILURE = 4  # Return empty context

class DegradationHandler:
    def handle_degradation(
        self,
        level: DegradationLevel,
        original_request: Dict
    ) -> ArchaeologicalContext:
        """Provide best possible service at degradation level."""

        if level == DegradationLevel.GITHUB_UNAVAILABLE:
            # Use git-only data
            return self.git_only_context(original_request)

        elif level == DegradationLevel.LLM_UNAVAILABLE:
            # Return raw search results without synthesis
            return self.raw_search_context(original_request)

        elif level == DegradationLevel.INDEX_CORRUPTED:
            # Fallback to basic git log search
            return self.git_log_context(original_request)

        else:  # TOTAL_FAILURE
            # Return minimal context with explanation
            return self.empty_context(
                message="CCA temporarily unavailable",
                degraded_mode=True
            )
```

### Circuit Breaker Implementation

```python
class CircuitBreaker:
    """Prevent cascade failures in CCA components."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError()

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e
```

## Performance Benchmarks Plan

### Benchmark Suite

```python
class AILBenchmarkSuite:
    """Performance benchmarks for AIL."""

    def __init__(self, provider: ArchaeologyContextProvider):
        self.provider = provider
        self.results = []

    async def run_all_benchmarks(self):
        """Run complete benchmark suite."""

        # 1. Latency benchmarks
        await self.benchmark_single_query_latency()
        await self.benchmark_cached_query_latency()
        await self.benchmark_cold_query_latency()

        # 2. Throughput benchmarks
        await self.benchmark_concurrent_requests()
        await self.benchmark_batch_processing()

        # 3. Resource benchmarks
        await self.benchmark_memory_usage()
        await self.benchmark_cpu_usage()

        # 4. Cache benchmarks
        await self.benchmark_cache_hit_rate()
        await self.benchmark_cache_eviction()

        # 5. Degradation benchmarks
        await self.benchmark_degraded_mode()
        await self.benchmark_circuit_breaker()

        return self.generate_report()
```

### Benchmark Scenarios

1. **Cold Start Performance**
   - Index loading time
   - First query latency
   - Memory allocation

2. **Warm Cache Performance**
   - Cache hit latency
   - Throughput with 80% cache hits
   - Memory stability

3. **Concurrent Load**
   - 10 concurrent agents
   - Mixed query patterns
   - Resource contention

4. **Large Repository**
   - 10,000+ commits
   - 1,000+ files
   - Index size and search performance

5. **Degraded Mode**
   - GitHub unavailable
   - LLM timeout
   - Circuit breaker activation

### Success Criteria

| Benchmark | Success Criteria | Measurement |
|-----------|------------------|-------------|
| p95 latency | <1000ms | 1000 queries |
| Cache hit rate | >80% | After warm-up |
| Memory per agent | <100MB | Peak RSS |
| Concurrent requests | 10 | No degradation |
| Degraded mode | <2000ms | p95 latency |
| Circuit breaker | <100ms | Fail-fast time |

## Implementation Timeline

### Phase 1: Core Implementation (Days 1-2)
- Implement `ArchaeologyContextProvider` class
- Integrate with existing CCA components
- Basic caching (L1 only)
- Synchronous API

### Phase 2: Performance & Caching (Day 2-3)
- Add Redis L2 cache
- Implement cache warming
- Add async support
- Circuit breaker implementation

### Phase 3: Agent Integration (Day 3)
- Create agent helper utilities
- Add batch processing
- Implement graceful degradation
- Performance optimization

### Testing Strategy
- Unit tests for each component
- Integration tests with CCA
- Performance benchmark suite
- Agent integration tests
- Chaos testing for degradation

## Security Considerations

1. **Input Validation**
   - Sanitize file paths
   - Validate query content
   - Rate limiting per agent

2. **Data Privacy**
   - No sensitive data in cache keys
   - Configurable data retention
   - Audit logging for access

3. **Resource Protection**
   - Memory limits enforced
   - CPU throttling
   - Queue depth limits

## Monitoring & Observability

### Metrics to Track

```python
class AILMetrics:
    """Metrics collected by AIL."""

    # Performance metrics
    query_latency_histogram: Histogram
    cache_hit_rate: Gauge
    concurrent_requests: Gauge

    # Resource metrics
    memory_usage_bytes: Gauge
    index_size_bytes: Gauge
    cache_size_entries: Gauge

    # Quality metrics
    answer_confidence_histogram: Histogram
    citation_count_histogram: Histogram
    degradation_events: Counter

    # Error metrics
    circuit_breaker_trips: Counter
    timeout_errors: Counter
    cache_errors: Counter
```

### Logging Strategy

```python
import structlog

logger = structlog.get_logger()

# Structured logging for analysis
logger.info(
    "context_retrieved",
    agent_type=agent_type,
    file_path=file_path,
    latency_ms=latency,
    cache_hit=cache_hit,
    confidence=confidence,
    degraded=degraded_mode
)
```

## Appendix A: Agent-Specific Optimizations

### Code Review Agents
- Pre-cache recent changes
- Prioritize security-related queries
- Include diff context

### Architecture Agents
- Pre-cache architectural decisions
- Include dependency graphs
- Prioritize design patterns

### Debugging Agents
- Pre-cache error patterns
- Include stack traces
- Prioritize recent bugs

### Performance Agents
- Pre-cache performance metrics
- Include profiling data
- Prioritize bottlenecks

## Appendix B: Example Usage

```python
# Initialize AIL
provider = ArchaeologyContextProvider(
    repo_path="/path/to/repo",
    cache_config=CacheConfig(
        l1_max_size=2000,
        l2_enabled=True,
        warm_on_startup=True
    ),
    performance_config=PerformanceConfig(
        max_concurrent_requests=20,
        circuit_breaker_enabled=True
    )
)

# Agent using AIL
async def security_agent_review(file_path: str):
    # Get archaeological context
    context = await provider.get_context(
        file_path=file_path,
        question="What security vulnerabilities were previously found here?",
        agent_type="security-audit-specialist"
    )

    if context.is_high_confidence:
        # Use historical context for review
        previous_issues = context.architectural_decisions
        related_fixes = context.related_commits

        # Perform security review with context
        return perform_security_review(
            file_path,
            historical_context=context
        )
    else:
        # Fallback to standard review
        return perform_standard_review(file_path)

# Batch processing for multiple files
files_to_review = ["src/api.py", "src/auth.py", "src/db.py"]
requests = [(f, "Security issues?") for f in files_to_review]

contexts = await provider.batch_get_context(
    requests,
    agent_type="security-audit-specialist"
)
```

## Conclusion

The Archaeological Intelligence Layer provides a robust, performant, and scalable solution for integrating CCA insights into all Claude agents. By implementing intelligent caching, graceful degradation, and agent-specific optimizations, AIL ensures that historical code context enhances agent decision-making without impacting performance.

The modular architecture allows for easy extension and maintenance while the comprehensive monitoring ensures operational excellence. With this foundation, every agent becomes context-aware, leading to better code reviews, more informed architectural decisions, and improved debugging capabilities.