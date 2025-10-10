# Archaeological Intelligence Layer - API Contract

## API Overview

The Archaeological Intelligence Layer (AIL) provides a unified interface for all Claude agents to access Cognitive Code Archaeology insights. This document defines the complete API contract including method signatures, return types, error handling, and usage examples.

## Core API Classes

### ArchaeologyContextProvider

The main entry point for all archaeological context retrieval.

```python
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import asyncio

class ArchaeologyContextProvider:
    """
    Main API for Archaeological Intelligence Layer.

    Thread-safe and async-compatible provider for archaeological context.
    Supports both synchronous and asynchronous usage patterns.
    """
```

## Primary Methods

### 1. Initialization

```python
def __init__(
    self,
    repo_path: str,
    cache_config: Optional[CacheConfig] = None,
    performance_config: Optional[PerformanceConfig] = None,
    github_repo: Optional[str] = None,
    api_key: Optional[str] = None
) -> None:
    """
    Initialize the Archaeological Intelligence Layer provider.

    Parameters:
        repo_path (str): Absolute or relative path to git repository
        cache_config (Optional[CacheConfig]): Cache configuration settings
        performance_config (Optional[PerformanceConfig]): Performance tuning parameters
        github_repo (Optional[str]): GitHub repository in "owner/repo" format
        api_key (Optional[str]): API key for LLM services (defaults to env var)

    Raises:
        ValueError: If repo_path is invalid or not a git repository
        ConfigurationError: If configuration parameters are invalid
        InitializationError: If CCA components fail to initialize

    Example:
        provider = ArchaeologyContextProvider(
            repo_path="/path/to/repo",
            github_repo="owner/repo",
            cache_config=CacheConfig(l1_max_size=2000)
        )
    """
```

### 2. Primary Context Retrieval

```python
async def get_context(
    self,
    file_path: str,
    question: str,
    agent_type: Optional[str] = None,
    context_hints: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None
) -> ArchaeologicalContext:
    """
    Retrieve archaeological context for a file and question.

    This is the primary method for agents to get historical context.
    Automatically handles caching, optimization, and degradation.

    Parameters:
        file_path (str): Path to file (absolute or relative to repo)
        question (str): Natural language question about the file
        agent_type (Optional[str]): Type of requesting agent for optimization
            Examples: "security-audit-specialist", "code-architect"
        context_hints (Optional[Dict[str, Any]]): Additional context from agent
            Examples: {"focus": "security", "time_range": "last_month"}
        timeout (Optional[float]): Request timeout in seconds (default: 2.0)

    Returns:
        ArchaeologicalContext: Context with answer, citations, and metadata

    Raises:
        FileNotFoundError: If file_path doesn't exist in repository
        ContextRetrievalError: If context cannot be retrieved
        TimeoutError: If request exceeds timeout

    Performance Guarantees:
        - p50 latency: <500ms
        - p95 latency: <1000ms
        - p99 latency: <2000ms

    Example:
        context = await provider.get_context(
            file_path="src/auth.py",
            question="What security issues were previously found here?",
            agent_type="security-audit-specialist"
        )

        if context.is_high_confidence:
            print(f"Answer: {context.answer}")
            print(f"Confidence: {context.confidence:.2%}")
            for citation in context.citations:
                print(f"  - {citation.message} ({citation.date})")
    """
```

### 3. Synchronous Context Retrieval

```python
def get_context_sync(
    self,
    file_path: str,
    question: str,
    agent_type: Optional[str] = None,
    timeout: Optional[float] = None
) -> ArchaeologicalContext:
    """
    Synchronous version of get_context for non-async agents.

    Parameters:
        Same as get_context (except no context_hints)

    Returns:
        ArchaeologicalContext: Context with answer and citations

    Raises:
        Same as get_context

    Example:
        context = provider.get_context_sync(
            file_path="src/api.py",
            question="Why was this endpoint deprecated?"
        )
    """
```

### 4. Batch Processing

```python
async def batch_get_context(
    self,
    requests: List[Tuple[str, str]],
    agent_type: Optional[str] = None,
    max_parallel: int = 5
) -> List[ArchaeologicalContext]:
    """
    Batch retrieve context for multiple file/question pairs.

    Optimized for processing multiple files efficiently.
    Automatically batches and parallelizes requests.

    Parameters:
        requests (List[Tuple[str, str]]): List of (file_path, question) tuples
        agent_type (Optional[str]): Type of requesting agent
        max_parallel (int): Maximum parallel requests (default: 5)

    Returns:
        List[ArchaeologicalContext]: Contexts in same order as requests

    Raises:
        BatchProcessingError: If batch processing fails
        PartialBatchError: Some requests failed (check .failed_indices)

    Example:
        files = ["api.py", "auth.py", "db.py"]
        requests = [(f, "Security issues?") for f in files]

        contexts = await provider.batch_get_context(
            requests,
            agent_type="security-audit-specialist"
        )

        for file, context in zip(files, contexts):
            print(f"{file}: {context.confidence:.2%} confidence")
    """
```

### 5. File History

```python
async def get_file_history(
    self,
    file_path: str,
    limit: int = 10,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None
) -> List[CommitSummary]:
    """
    Get simplified commit history for a file.

    Parameters:
        file_path (str): Target file path
        limit (int): Maximum commits to return (default: 10)
        since (Optional[datetime]): Start date filter
        until (Optional[datetime]): End date filter

    Returns:
        List[CommitSummary]: Simplified commit information

    Example:
        history = await provider.get_file_history(
            "src/auth.py",
            limit=20,
            since=datetime.now() - timedelta(days=30)
        )

        for commit in history:
            print(f"{commit.sha[:7]}: {commit.summary}")
    """
```

### 6. Architectural Decisions Search

```python
async def search_architectural_decisions(
    self,
    query: str,
    limit: int = 5,
    min_confidence: float = 0.7
) -> List[ArchDecision]:
    """
    Search for architectural decisions in repository history.

    Parameters:
        query (str): Search query for architectural decisions
        limit (int): Maximum results (default: 5)
        min_confidence (float): Minimum confidence threshold (0.0-1.0)

    Returns:
        List[ArchDecision]: Architectural decisions matching query

    Example:
        decisions = await provider.search_architectural_decisions(
            "database migration strategy",
            limit=3
        )

        for decision in decisions:
            print(f"Decision: {decision.decision}")
            print(f"Rationale: {decision.rationale}")
            print(f"Alternatives: {', '.join(decision.alternatives)}")
    """
```

### 7. Cache Management

```python
async def warm_cache(
    self,
    patterns: Optional[List[str]] = None,
    agent_type: Optional[str] = None
) -> int:
    """
    Preemptively warm cache with common queries.

    Parameters:
        patterns (Optional[List[str]]): Query patterns to warm
            If None, uses default patterns for agent_type
        agent_type (Optional[str]): Agent type for pattern selection

    Returns:
        int: Number of cache entries warmed

    Example:
        # Warm cache for security agent
        warmed = await provider.warm_cache(
            agent_type="security-audit-specialist"
        )
        print(f"Warmed {warmed} cache entries")

        # Custom patterns
        patterns = [
            "What are the recent changes?",
            "Are there security issues?",
            "Who wrote this code?"
        ]
        warmed = await provider.warm_cache(patterns=patterns)
    """

def clear_cache(
    self,
    level: str = "all"
) -> None:
    """
    Clear cache at specified level.

    Parameters:
        level (str): Cache level to clear
            - "l1": Clear only L1 (in-memory) cache
            - "l2": Clear only L2 (Redis) cache
            - "all": Clear all cache levels

    Example:
        provider.clear_cache("l1")  # Clear memory cache only
    """
```

### 8. Health & Monitoring

```python
def get_health_status(self) -> Dict[str, Any]:
    """
    Get health status of AIL components.

    Returns:
        Dict containing component health metrics:
        {
            "status": "healthy" | "degraded" | "unhealthy",
            "components": {
                "git_archaeologist": {"status": "healthy", "latency_ms": 45},
                "github_integrator": {"status": "degraded", "error": "rate_limited"},
                "context_synthesizer": {"status": "healthy", "latency_ms": 120},
                "cache_l1": {"status": "healthy", "hit_rate": 0.82, "size": 750},
                "cache_l2": {"status": "healthy", "hit_rate": 0.45, "size_mb": 42},
                "index": {"status": "healthy", "size": 5000, "memory_mb": 35}
            },
            "metrics": {
                "total_queries": 1523,
                "avg_latency_ms": 345,
                "cache_hit_rate": 0.78,
                "degradation_events": 2
            }
        }

    Example:
        health = provider.get_health_status()
        if health["status"] == "degraded":
            print(f"System degraded: {health['components']}")
    """

def get_metrics(self) -> Dict[str, Any]:
    """
    Get performance metrics for monitoring.

    Returns:
        Dict containing performance metrics:
        {
            "latency": {
                "p50": 234,
                "p95": 567,
                "p99": 1234
            },
            "cache": {
                "l1_hit_rate": 0.42,
                "l2_hit_rate": 0.35,
                "total_hit_rate": 0.77
            },
            "throughput": {
                "queries_per_second": 12.5,
                "concurrent_requests": 3
            },
            "errors": {
                "timeout_errors": 2,
                "circuit_breaker_trips": 0,
                "degradation_events": 1
            }
        }

    Example:
        metrics = provider.get_metrics()
        print(f"p95 latency: {metrics['latency']['p95']}ms")
        print(f"Cache hit rate: {metrics['cache']['total_hit_rate']:.1%}")
    """
```

### 9. Lifecycle Management

```python
async def shutdown(self, timeout: float = 5.0) -> None:
    """
    Gracefully shutdown AIL components.

    Parameters:
        timeout (float): Maximum time to wait for shutdown (seconds)

    Example:
        await provider.shutdown()

    Note:
        Should be called when agent is terminating to ensure
        clean resource cleanup and cache persistence.
    """

async def refresh_index(self) -> None:
    """
    Refresh the search index with latest repository changes.

    Automatically called periodically, but can be triggered manually
    after significant repository changes.

    Example:
        await provider.refresh_index()
    """
```

## Data Models

### ArchaeologicalContext

```python
@dataclass
class ArchaeologicalContext:
    """
    Complete archaeological context for agent consumption.

    Attributes:
        query (str): Original query that generated this context
        file_path (str): File path this context relates to
        agent_type (str): Type of agent that requested context

        answer (str): Natural language answer to query
        confidence (float): Confidence score (0.0 to 1.0)

        citations (List[Citation]): Supporting evidence
        related_commits (List[CommitSummary]): Related commits
        architectural_decisions (List[ArchDecision]): Architectural decisions

        retrieval_time_ms (float): Time taken to retrieve context
        cache_hit (bool): Whether result was from cache
        degraded_mode (bool): Whether running in degraded mode

        agent_hints (Dict[str, Any]): Agent-specific hints
        suggested_actions (List[str]): Suggested next actions

    Properties:
        is_high_confidence (bool): True if confidence >= 0.7 and citations >= 2
        is_cached (bool): True if retrieved from cache
        is_degraded (bool): True if retrieved in degraded mode
    """

    def to_json(self) -> str:
        """Serialize to JSON string."""

    @classmethod
    def from_json(cls, json_str: str) -> 'ArchaeologicalContext':
        """Deserialize from JSON string."""

    def get_relevant_citations(self, min_relevance: float = 0.7) -> List[Citation]:
        """Get citations above relevance threshold."""

    def get_time_range(self) -> Tuple[datetime, datetime]:
        """Get date range of citations."""
```

## Error Handling

### Exception Hierarchy

```python
class AILError(Exception):
    """Base exception for all AIL errors."""
    pass

class ConfigurationError(AILError):
    """Invalid configuration provided."""
    pass

class InitializationError(AILError):
    """Failed to initialize AIL components."""
    pass

class ContextRetrievalError(AILError):
    """Failed to retrieve context."""
    pass

class FileNotFoundError(AILError):
    """File not found in repository."""
    pass

class TimeoutError(AILError):
    """Request exceeded timeout."""
    pass

class BatchProcessingError(AILError):
    """Batch processing failed."""
    pass

class PartialBatchError(BatchProcessingError):
    """Some batch requests failed."""
    def __init__(self, message: str, failed_indices: List[int]):
        super().__init__(message)
        self.failed_indices = failed_indices

class DegradedServiceError(AILError):
    """Service is running in degraded mode."""
    pass

class CircuitOpenError(AILError):
    """Circuit breaker is open due to failures."""
    pass
```

### Error Handling Examples

```python
# Basic error handling
try:
    context = await provider.get_context(
        file_path="src/missing.py",
        question="What does this do?"
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except ContextRetrievalError as e:
    print(f"Failed to retrieve context: {e}")

# Batch error handling
try:
    contexts = await provider.batch_get_context(requests)
except PartialBatchError as e:
    print(f"Some requests failed: {e.failed_indices}")
    # Process successful contexts
    for i, context in enumerate(contexts):
        if i not in e.failed_indices:
            process_context(context)

# Degraded mode handling
context = await provider.get_context(file_path, question)
if context.degraded_mode:
    print("Warning: Operating in degraded mode")
    print(f"Confidence may be lower: {context.confidence}")
```

## Usage Examples

### Example 1: Security Agent Integration

```python
class SecurityAgent:
    def __init__(self, repo_path: str):
        self.ail = ArchaeologyContextProvider(
            repo_path=repo_path,
            cache_config=CacheConfig(
                l1_max_size=2000,
                warm_on_startup=True
            )
        )
        # Warm cache with security patterns
        asyncio.run(self.ail.warm_cache(
            agent_type="security-audit-specialist"
        ))

    async def review_file(self, file_path: str) -> SecurityReview:
        # Get historical security context
        context = await self.ail.get_context(
            file_path=file_path,
            question="What security vulnerabilities were found previously?",
            agent_type="security-audit-specialist"
        )

        if context.is_high_confidence:
            # Use historical context for informed review
            previous_issues = self.extract_issues(context)
            related_fixes = context.related_commits

            # Check if previous issues were properly fixed
            for issue in previous_issues:
                if not self.verify_fix(issue, related_fixes):
                    self.flag_unresolved_issue(issue)

        # Continue with standard security review
        return self.perform_security_scan(file_path, context)
```

### Example 2: Code Review with Context

```python
class CodeReviewAgent:
    async def review_pull_request(self, files: List[str]) -> PRReview:
        # Batch get context for all changed files
        requests = [
            (file, "What are the key design decisions here?")
            for file in files
        ]

        contexts = await self.ail.batch_get_context(
            requests,
            agent_type="code-architect"
        )

        review = PRReview()
        for file, context in zip(files, contexts):
            if context.architectural_decisions:
                # Check if changes align with architectural decisions
                for decision in context.architectural_decisions:
                    if self.violates_decision(file, decision):
                        review.add_comment(
                            file=file,
                            message=f"This change may violate the architectural decision: {decision.decision}",
                            severity="warning"
                        )

        return review
```

### Example 3: Debugging with History

```python
class DebuggingAgent:
    async def investigate_bug(self, error_file: str, error_message: str):
        # Get context about when this might have been introduced
        context = await self.ail.get_context(
            file_path=error_file,
            question=f"When were changes made that could cause: {error_message}",
            agent_type="debugging-specialist"
        )

        if context.is_high_confidence:
            # Get detailed history of the file
            history = await self.ail.get_file_history(
                error_file,
                limit=50
            )

            # Find commits that might have introduced the bug
            suspicious_commits = []
            for commit in history:
                if self.is_suspicious(commit, error_message):
                    suspicious_commits.append(commit)

            # Return debugging insights
            return {
                "likely_cause": context.answer,
                "suspicious_commits": suspicious_commits,
                "suggested_fixes": context.suggested_actions
            }
```

### Example 4: Architectural Analysis

```python
class ArchitectureAgent:
    async def analyze_architecture(self, component: str):
        # Search for architectural decisions
        decisions = await self.ail.search_architectural_decisions(
            f"{component} design",
            limit=10
        )

        # Build architectural narrative
        narrative = []
        for decision in decisions:
            narrative.append({
                "decision": decision.decision,
                "rationale": decision.rationale,
                "alternatives_considered": decision.alternatives,
                "made_on": decision.date,
                "commit": decision.commit_sha
            })

        # Get evolution of the component
        context = await self.ail.get_context(
            file_path=f"src/{component}",
            question="How has this component evolved over time?",
            agent_type="code-architect"
        )

        return {
            "architectural_decisions": narrative,
            "evolution": context.answer,
            "current_state_confidence": context.confidence
        }
```

## Performance Considerations

### Optimization Tips

1. **Use agent_type parameter** - Enables agent-specific optimizations
2. **Batch requests when possible** - More efficient than individual calls
3. **Warm cache proactively** - Reduces latency for common queries
4. **Set appropriate timeouts** - Prevent hanging on slow operations
5. **Check degraded_mode flag** - Adjust behavior when degraded

### Resource Usage

```python
# Monitor resource usage
health = provider.get_health_status()
if health["components"]["cache_l1"]["size"] > 900:
    # L1 cache nearly full, may see evictions
    provider.clear_cache("l1")

metrics = provider.get_metrics()
if metrics["throughput"]["concurrent_requests"] > 8:
    # High concurrency, may see increased latency
    # Consider backing off or queueing
    await asyncio.sleep(0.1)
```

## Migration Guide

### For Existing CCA Users

```python
# Old CCA CLI usage
from tools.code_archaeology import ArchaeologyCLI

cli = ArchaeologyCLI(repo_path)
cli.initialize()
answer = cli.query("What changed recently?")

# New AIL usage
from ail import ArchaeologyContextProvider

provider = ArchaeologyContextProvider(repo_path)
context = await provider.get_context(
    file_path=".",  # Repository root
    question="What changed recently?"
)
answer = context.answer
```

### For New Agent Implementations

```python
# Standard agent integration pattern
class MyAgent:
    def __init__(self, repo_path: str):
        # Initialize AIL provider
        self.ail = ArchaeologyContextProvider(
            repo_path=repo_path,
            cache_config=CacheConfig(warm_on_startup=True)
        )
        self.agent_type = "my-agent"

    async def process_file(self, file_path: str):
        # Get context for decision making
        context = await self.ail.get_context(
            file_path=file_path,
            question="What is important about this file?",
            agent_type=self.agent_type
        )

        # Use context to enhance processing
        if context.is_high_confidence:
            return self.informed_processing(file_path, context)
        else:
            return self.standard_processing(file_path)

    async def cleanup(self):
        # Ensure proper shutdown
        await self.ail.shutdown()
```

## Versioning

The AIL API follows semantic versioning:

- **1.0.0** - Initial release with core functionality
- **1.1.0** - Added batch processing and cache warming
- **1.2.0** - Enhanced degradation handling
- **2.0.0** - Breaking changes to data models (future)

## Support

For issues, questions, or feature requests:
- Check health status: `provider.get_health_status()`
- Review metrics: `provider.get_metrics()`
- Enable debug logging: Set `AIL_DEBUG=true` environment variable
- File issues in the project repository