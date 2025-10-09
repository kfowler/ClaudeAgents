"""
Archaeology Context Provider - Main interface for AIL Sprint 1

This module provides the ArchaeologyContextProvider class that enables AI agents
to query historical context from the Cognitive Code Archaeology system with
intelligent caching and error handling.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Import CCA components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_archaeology import (
    GitArchaeologist,
    GitHubArchaeologist,
    ContextSynthesizer,
    SearchableIndex,
    Answer,
    Citation,
    RepositoryHistory,
    EnrichedHistory,
    SimpleEmbeddingProvider,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContextSource:
    """Source of archaeological context."""

    commit_sha: str
    commit_message: str
    author: str
    date: datetime
    source_type: str  # "commit", "pr", "issue"
    relevance_score: float
    excerpt: str
    url: str = ""

    @classmethod
    def from_citation(cls, citation: Citation) -> ContextSource:
        """Create ContextSource from CCA Citation."""
        return cls(
            commit_sha=citation.commit_sha,
            commit_message=citation.commit_message,
            author=citation.author,
            date=citation.commit_date,
            source_type=citation.source_type,
            relevance_score=citation.relevance_score,
            excerpt=citation.excerpt,
            url=citation.url,
        )


@dataclass
class ArchaeologicalContext:
    """Archaeological context result for agents."""

    file_path: str
    question: str
    answer: str
    sources: List[ContextSource]
    confidence: float
    cached: bool = False
    query_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_high_confidence(self) -> bool:
        """Check if answer has high confidence (>0.7)."""
        return self.confidence > 0.7

    @property
    def source_count(self) -> int:
        """Number of sources supporting this answer."""
        return len(self.sources)

    def to_markdown(self) -> str:
        """Format context as markdown for agent consumption."""
        lines = [
            f"# Archaeological Context: {self.file_path}",
            f"**Question**: {self.question}",
            "",
            f"## Answer (Confidence: {self.confidence:.1%})",
            self.answer,
            "",
        ]

        if self.sources:
            lines.append("## Sources")
            for i, source in enumerate(self.sources, 1):
                lines.append(f"{i}. **{source.source_type.upper()}** by {source.author} ({source.date.date()})")
                lines.append(f"   - Commit: `{source.commit_sha[:8]}`")
                lines.append(f"   - Relevance: {source.relevance_score:.1%}")
                lines.append(f"   - {source.excerpt[:100]}...")
                if source.url:
                    lines.append(f"   - URL: {source.url}")
                lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms | Cached: {self.cached}*")

        return "\n".join(lines)


@dataclass
class CacheStats:
    """Statistics for cache performance."""

    hits: int = 0
    misses: int = 0
    total_queries: int = 0
    avg_query_time_ms: float = 0.0
    cache_size: int = 0
    max_cache_size: int = 1000

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        if self.total_queries == 0:
            return 0.0
        return self.hits / self.total_queries

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_queries': self.total_queries,
            'hit_rate': self.hit_rate,
            'avg_query_time_ms': self.avg_query_time_ms,
            'cache_size': self.cache_size,
            'max_cache_size': self.max_cache_size,
        }


class LRUCache:
    """LRU (Least Recently Used) cache implementation."""

    def __init__(self, max_size: int = 1000):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of entries to cache
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, ArchaeologicalContext] = OrderedDict()

    def get(self, key: str) -> Optional[ArchaeologicalContext]:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached context or None if not found
        """
        if key not in self.cache:
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: ArchaeologicalContext) -> None:
        """
        Put item in cache.

        Args:
            key: Cache key
            value: Context to cache
        """
        if key in self.cache:
            # Update existing entry
            self.cache.move_to_end(key)
        else:
            # Add new entry
            self.cache[key] = value

            # Evict oldest if over capacity
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    @property
    def size(self) -> int:
        """Current cache size."""
        return len(self.cache)


class ArchaeologyContextProvider:
    """
    Main provider for archaeological context to AI agents.

    This class integrates with the Cognitive Code Archaeology system to provide
    agents with historical context about code decisions, architectural changes,
    and development patterns.

    Features:
    - LRU caching for performance
    - Async support for non-blocking queries
    - Graceful degradation when CCA unavailable
    - Timeout handling
    - Comprehensive error handling
    """

    def __init__(
        self,
        repo_path: str,
        cache_size: int = 1000,
        github_owner: Optional[str] = None,
        github_repo: Optional[str] = None,
        github_token: Optional[str] = None,
        max_query_time_s: float = 2.0,
    ):
        """
        Initialize the archaeology context provider.

        Args:
            repo_path: Path to git repository
            cache_size: Maximum cache entries (default: 1000)
            github_owner: GitHub repository owner (optional)
            github_repo: GitHub repository name (optional)
            github_token: GitHub API token (optional)
            max_query_time_s: Maximum query time in seconds (default: 2.0)
        """
        self.repo_path = Path(repo_path).resolve()
        self.max_query_time_s = max_query_time_s

        # Validate repository
        if not (self.repo_path / '.git').exists():
            raise ValueError(f"Not a git repository: {repo_path}")

        # Initialize cache
        self.cache = LRUCache(max_size=cache_size)
        self.stats = CacheStats(max_cache_size=cache_size)

        # Initialize CCA components (lazy loading)
        self._git_archaeologist: Optional[GitArchaeologist] = None
        self._github_archaeologist: Optional[GitHubArchaeologist] = None
        self._context_synthesizer: Optional[ContextSynthesizer] = None
        self._searchable_index: Optional[SearchableIndex] = None

        # GitHub configuration
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.github_token = github_token

        # Initialization state
        self._initialized = False
        self._init_error: Optional[str] = None

        logger.info(f"ArchaeologyContextProvider initialized for: {self.repo_path}")

    def _initialize_components(self) -> bool:
        """
        Lazy initialization of CCA components.

        Returns:
            True if successful, False otherwise
        """
        if self._initialized:
            return True

        if self._init_error:
            return False

        try:
            logger.info("Initializing CCA components...")

            # Initialize Git Archaeologist
            logger.info("Loading git history...")
            self._git_archaeologist = GitArchaeologist(str(self.repo_path))

            # Analyze repository (limit to recent commits for performance)
            history = self._git_archaeologist.analyze_repo(limit=500)
            logger.info(f"Analyzed {history.total_commits} commits")

            # Initialize GitHub Archaeologist if configured
            enriched_history = None
            if self.github_owner and self.github_repo:
                logger.info("Enriching with GitHub data...")
                self._github_archaeologist = GitHubArchaeologist(
                    owner=self.github_owner,
                    repo=self.github_repo,
                    token=self.github_token,
                )
                enriched_history = self._github_archaeologist.enrich_history(
                    history, limit=100  # Limit to avoid rate limits
                )
            else:
                logger.info("GitHub integration not configured, using git data only")
                # Create minimal enriched history without GitHub data
                from code_archaeology.github_integrator import EnrichedHistory, EnrichedCommit
                enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
                enriched_history = EnrichedHistory(
                    base_history=history,
                    enriched_commits=enriched_commits,
                    pull_requests={},
                    issues={},
                    commit_to_pr={},
                )

            # Initialize Context Synthesizer
            logger.info("Building searchable index...")
            self._context_synthesizer = ContextSynthesizer(
                embedding_provider=SimpleEmbeddingProvider(max_features=512)
            )
            self._searchable_index = self._context_synthesizer.build_searchable_index(
                enriched_history
            )

            self._initialized = True
            logger.info("CCA components initialized successfully")
            return True

        except Exception as e:
            self._init_error = str(e)
            logger.error(f"Failed to initialize CCA components: {e}")
            return False

    def _generate_cache_key(self, file_path: str, question: str) -> str:
        """
        Generate cache key from file path and question.

        Args:
            file_path: File path being queried
            question: Natural language question

        Returns:
            Cache key (hash of normalized inputs)
        """
        # Normalize inputs
        normalized_path = str(Path(file_path).resolve())
        normalized_question = question.lower().strip()

        # Generate hash
        key_input = f"{normalized_path}::{normalized_question}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    async def get_context(
        self,
        file_path: str,
        question: str,
    ) -> ArchaeologicalContext:
        """
        Get archaeological context for a file and question.

        Args:
            file_path: Path to file (relative to repo root)
            question: Natural language question about the file

        Returns:
            ArchaeologicalContext with answer and sources
        """
        start_time = time.time()

        # Update stats
        self.stats.total_queries += 1

        # Check cache
        cache_key = self._generate_cache_key(file_path, question)
        cached_result = self.cache.get(cache_key)

        if cached_result:
            self.stats.hits += 1
            self.stats.cache_size = self.cache.size
            logger.debug(f"Cache hit for: {file_path}")

            # Update query time stats
            query_time_ms = (time.time() - start_time) * 1000
            cached_result.cached = True
            cached_result.query_time_ms = query_time_ms

            return cached_result

        # Cache miss
        self.stats.misses += 1
        logger.debug(f"Cache miss for: {file_path}")

        # Initialize components if needed
        if not self._initialize_components():
            # Return error context
            query_time_ms = (time.time() - start_time) * 1000
            error_context = ArchaeologicalContext(
                file_path=file_path,
                question=question,
                answer=f"Archaeological context unavailable: {self._init_error}",
                sources=[],
                confidence=0.0,
                cached=False,
                query_time_ms=query_time_ms,
            )
            return error_context

        try:
            # Query with timeout
            answer = await asyncio.wait_for(
                self._query_archaeology(file_path, question),
                timeout=self.max_query_time_s,
            )

            # Convert to ArchaeologicalContext
            query_time_ms = (time.time() - start_time) * 1000
            context = ArchaeologicalContext(
                file_path=file_path,
                question=question,
                answer=answer.answer,
                sources=[ContextSource.from_citation(c) for c in answer.citations],
                confidence=answer.confidence,
                cached=False,
                query_time_ms=query_time_ms,
            )

            # Cache result
            self.cache.put(cache_key, context)
            self.stats.cache_size = self.cache.size

            # Update average query time
            total_time = self.stats.avg_query_time_ms * (self.stats.total_queries - 1)
            self.stats.avg_query_time_ms = (total_time + query_time_ms) / self.stats.total_queries

            logger.info(f"Context retrieved for {file_path} in {query_time_ms:.0f}ms")
            return context

        except asyncio.TimeoutError:
            query_time_ms = (time.time() - start_time) * 1000
            logger.warning(f"Query timeout for {file_path} after {self.max_query_time_s}s")

            timeout_context = ArchaeologicalContext(
                file_path=file_path,
                question=question,
                answer=f"Query timeout after {self.max_query_time_s}s. Try a more specific question.",
                sources=[],
                confidence=0.0,
                cached=False,
                query_time_ms=query_time_ms,
            )
            return timeout_context

        except Exception as e:
            query_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Error querying context for {file_path}: {e}")

            error_context = ArchaeologicalContext(
                file_path=file_path,
                question=question,
                answer=f"Error retrieving context: {str(e)}",
                sources=[],
                confidence=0.0,
                cached=False,
                query_time_ms=query_time_ms,
            )
            return error_context

    async def _query_archaeology(self, file_path: str, question: str) -> Answer:
        """
        Query the archaeology system (async wrapper).

        Args:
            file_path: File path to query
            question: Natural language question

        Returns:
            Answer from CCA system
        """
        # Enhance question with file context
        enhanced_question = f"For file '{file_path}': {question}"

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None,
            self._context_synthesizer.synthesize_answer,
            self._searchable_index,
            enhanced_question,
            10,  # max_results
        )

        return answer

    def get_context_sync(self, file_path: str, question: str) -> ArchaeologicalContext:
        """
        Synchronous version of get_context.

        Args:
            file_path: Path to file (relative to repo root)
            question: Natural language question about the file

        Returns:
            ArchaeologicalContext with answer and sources
        """
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run async function
        return loop.run_until_complete(self.get_context(file_path, question))

    def clear_cache(self) -> None:
        """Clear the context cache."""
        self.cache.clear()
        self.stats.cache_size = 0
        logger.info("Cache cleared")

    def get_cache_stats(self) -> CacheStats:
        """
        Get cache performance statistics.

        Returns:
            CacheStats object with current statistics
        """
        return self.stats

    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._initialized

    def get_init_error(self) -> Optional[str]:
        """Get initialization error if any."""
        return self._init_error


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python context_provider.py <repo_path> <file_path> <question>")
        print("\nExample:")
        print("  python context_provider.py . tools/ail/context_provider.py 'Why was LRU caching chosen?'")
        sys.exit(1)

    repo_path = sys.argv[1]
    file_path = sys.argv[2]
    question = " ".join(sys.argv[3:])

    # Initialize provider
    provider = ArchaeologyContextProvider(repo_path=repo_path)

    # Get context
    print(f"\nQuerying archaeological context...")
    print(f"Repository: {repo_path}")
    print(f"File: {file_path}")
    print(f"Question: {question}")
    print("=" * 80)

    context = provider.get_context_sync(file_path, question)

    # Display results
    print(context.to_markdown())
    print("\n" + "=" * 80)

    # Display stats
    stats = provider.get_cache_stats()
    print(f"\nCache Stats:")
    print(f"  Hit Rate: {stats.hit_rate:.1%}")
    print(f"  Cache Size: {stats.cache_size}/{stats.max_cache_size}")
    print(f"  Avg Query Time: {stats.avg_query_time_ms:.0f}ms")


if __name__ == '__main__':
    main()
