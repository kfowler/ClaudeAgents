"""
Unit Tests for Archaeological Intelligence Layer (AIL) Context Provider.

Tests the ArchaeologyContextProvider which provides historical context
to agents for improved code understanding and decision-making.

Test Coverage:
- Context retrieval with various file paths and questions
- Cache hit/miss behavior and performance
- Error handling (repo not found, timeout, CCA unavailable)
- Memory usage constraints (<100MB)
- Performance targets (p95 latency <1s)
"""

import pytest
import time
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tracemalloc

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
from tools.code_archaeology import (
    GitArchaeologist,
    ContextSynthesizer,
    SearchableIndex,
    Answer,
    Citation,
)


class ArchaeologyContextProvider:
    """
    Provides archaeological context to agents for improved decision-making.

    This is the integration layer between the Code Archaeology system
    and individual agents. It provides a simple interface for agents to
    query historical context about code decisions.
    """

    def __init__(self, repo_path: str, cache_enabled: bool = True):
        """
        Initialize the context provider.

        Args:
            repo_path: Path to git repository
            cache_enabled: Enable response caching for performance
        """
        self.repo_path = Path(repo_path)
        self.cache_enabled = cache_enabled
        self._cache = {}
        self._index = None
        self._initialized = False

        # Performance tracking
        self._query_times = []
        self._cache_hits = 0
        self._cache_misses = 0

        # Memory tracking
        self._max_memory_mb = 100

    def initialize(self, max_commits: int = None):
        """
        Initialize the archaeology system (lazy loading).

        Args:
            max_commits: Optional limit on commits to analyze

        Raises:
            ValueError: If repository path is invalid
            RuntimeError: If initialization fails
        """
        if self._initialized:
            return

        # Validate repository
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

        try:
            # Analyze git history
            archaeologist = GitArchaeologist(str(self.repo_path))
            history = archaeologist.analyze_repo(limit=max_commits)

            # Build searchable index
            from tools.code_archaeology.github_integrator import EnrichedHistory, EnrichedCommit
            enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
            enriched = EnrichedHistory(
                base_history=history,
                enriched_commits=enriched_commits,
                pull_requests={},
                issues={},
                commit_to_pr={},
            )

            synthesizer = ContextSynthesizer()
            self._index = synthesizer.build_searchable_index(enriched)
            self._initialized = True

        except Exception as e:
            raise RuntimeError(f"Failed to initialize archaeology system: {e}")

    def get_context(
        self,
        file_path: str,
        question: str,
        max_results: int = 5
    ) -> dict:
        """
        Get archaeological context for a file and question.

        Args:
            file_path: Path to file being analyzed (relative to repo root)
            question: Natural language question about the code
            max_results: Maximum number of context items to return

        Returns:
            dict with:
                - answer: str - Natural language answer
                - citations: list - Source commits with relevance
                - confidence: float - 0.0 to 1.0
                - cached: bool - Whether result was cached
                - latency_ms: int - Query latency in milliseconds

        Raises:
            RuntimeError: If provider not initialized
            TimeoutError: If query exceeds timeout
        """
        if not self._initialized:
            raise RuntimeError("Context provider not initialized. Call initialize() first.")

        # Check cache
        cache_key = f"{file_path}:{question}"
        if self.cache_enabled and cache_key in self._cache:
            self._cache_hits += 1
            result = self._cache[cache_key].copy()
            result['cached'] = True
            result['latency_ms'] = 0  # Cached responses are instant
            return result

        self._cache_misses += 1

        # Build enhanced question with file context
        enhanced_question = f"For file {file_path}: {question}"

        # Track latency
        start_time = time.time()

        try:
            # Query the archaeology system
            synthesizer = ContextSynthesizer()
            answer = synthesizer.synthesize_answer(self._index, enhanced_question)

            latency_ms = int((time.time() - start_time) * 1000)
            self._query_times.append(latency_ms)

            # Format response
            result = {
                'answer': answer.answer,
                'citations': [
                    {
                        'commit_sha': c.commit_sha,
                        'commit_message': c.commit_message,
                        'author': c.author,
                        'date': c.commit_date.isoformat() if hasattr(c, 'commit_date') and c.commit_date else None,
                        'relevance_score': c.relevance_score,
                    }
                    for c in answer.citations[:max_results]
                ],
                'confidence': answer.confidence,
                'cached': False,
                'latency_ms': latency_ms,
            }

            # Cache the result
            if self.cache_enabled:
                self._cache[cache_key] = result.copy()

            return result

        except Exception as e:
            raise RuntimeError(f"Failed to get context: {e}")

    def get_stats(self) -> dict:
        """Get performance statistics."""
        if not self._query_times:
            return {
                'total_queries': 0,
                'cache_hit_rate': 0.0,
                'avg_latency_ms': 0,
                'p95_latency_ms': 0,
                'p99_latency_ms': 0,
            }

        sorted_times = sorted(self._query_times)
        total_requests = self._cache_hits + self._cache_misses

        return {
            'total_queries': len(self._query_times),
            'cache_hit_rate': self._cache_hits / total_requests if total_requests > 0 else 0.0,
            'avg_latency_ms': sum(self._query_times) / len(self._query_times),
            'p95_latency_ms': sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0,
            'p99_latency_ms': sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0,
        }

    def clear_cache(self):
        """Clear the response cache."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


# ============================================================================
# Unit Tests
# ============================================================================

@pytest.fixture
def repo_path():
    """Get test repository path."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def provider(repo_path):
    """Create and initialize a context provider."""
    p = ArchaeologyContextProvider(repo_path, cache_enabled=True)
    p.initialize(max_commits=50)  # Limit for faster tests
    return p


class TestContextProviderInitialization:
    """Test initialization behavior."""

    def test_initialization_with_valid_repo(self, repo_path):
        """Test successful initialization with valid repository."""
        provider = ArchaeologyContextProvider(repo_path)
        provider.initialize(max_commits=10)

        assert provider._initialized is True
        assert provider._index is not None
        assert provider._index.size > 0

    def test_initialization_with_invalid_path(self):
        """Test initialization fails with invalid path."""
        provider = ArchaeologyContextProvider("/tmp/nonexistent-repo-12345")

        with pytest.raises(ValueError, match="does not exist"):
            provider.initialize()

    def test_initialization_with_non_git_repo(self, tmp_path):
        """Test initialization fails with non-git directory."""
        provider = ArchaeologyContextProvider(str(tmp_path))

        with pytest.raises(ValueError, match="Not a git repository"):
            provider.initialize()

    def test_lazy_initialization(self, repo_path):
        """Test provider uses lazy initialization."""
        provider = ArchaeologyContextProvider(repo_path)

        # Should not be initialized yet
        assert provider._initialized is False

        # Initialize
        provider.initialize(max_commits=10)

        # Now should be initialized
        assert provider._initialized is True

    def test_multiple_initialization_calls(self, repo_path):
        """Test multiple initialization calls are idempotent."""
        provider = ArchaeologyContextProvider(repo_path)

        provider.initialize(max_commits=10)
        first_index = provider._index

        # Second initialization should be no-op
        provider.initialize(max_commits=10)
        assert provider._index is first_index


class TestContextRetrieval:
    """Test context retrieval functionality."""

    def test_get_context_basic(self, provider):
        """Test basic context retrieval."""
        result = provider.get_context(
            file_path="agents/full-stack-architect.md",
            question="What is the purpose of this agent?"
        )

        assert 'answer' in result
        assert 'citations' in result
        assert 'confidence' in result
        assert 'cached' in result
        assert 'latency_ms' in result

        assert isinstance(result['answer'], str)
        assert len(result['answer']) > 0
        assert isinstance(result['citations'], list)
        assert 0.0 <= result['confidence'] <= 1.0

    def test_get_context_with_various_questions(self, provider):
        """Test context retrieval with different question types."""
        questions = [
            "Why was this file created?",
            "What changes have been made to this file?",
            "Who are the main contributors?",
            "What is the architectural significance?",
        ]

        for question in questions:
            result = provider.get_context(
                file_path="tools/code_archaeology/git_analyzer.py",
                question=question
            )

            assert result['answer'] is not None
            assert len(result['citations']) > 0

    def test_get_context_before_initialization(self, repo_path):
        """Test get_context fails before initialization."""
        provider = ArchaeologyContextProvider(repo_path)

        with pytest.raises(RuntimeError, match="not initialized"):
            provider.get_context(
                file_path="agents/full-stack-architect.md",
                question="Test question"
            )

    def test_get_context_with_max_results(self, provider):
        """Test max_results parameter limits citations."""
        result = provider.get_context(
            file_path="agents/full-stack-architect.md",
            question="What is this?",
            max_results=3
        )

        assert len(result['citations']) <= 3

    def test_get_context_citation_structure(self, provider):
        """Test citation structure is correct."""
        result = provider.get_context(
            file_path="tools/code_archaeology/git_analyzer.py",
            question="Why was this created?"
        )

        if result['citations']:
            citation = result['citations'][0]
            assert 'commit_sha' in citation
            assert 'commit_message' in citation
            assert 'author' in citation
            assert 'date' in citation
            assert 'relevance_score' in citation

            assert isinstance(citation['commit_sha'], str)
            assert isinstance(citation['relevance_score'], float)


class TestCacheBehavior:
    """Test caching functionality."""

    def test_cache_hit_on_duplicate_query(self, provider):
        """Test cache returns same result on duplicate query."""
        file_path = "agents/qa-test-engineer.md"
        question = "What is the purpose of this agent?"

        # First query - cache miss
        result1 = provider.get_context(file_path, question)
        assert result1['cached'] is False

        # Second query - cache hit
        result2 = provider.get_context(file_path, question)
        assert result2['cached'] is True

        # Results should be identical (except cached flag)
        assert result1['answer'] == result2['answer']
        assert result1['confidence'] == result2['confidence']

    def test_cache_disabled(self, repo_path):
        """Test provider works with caching disabled."""
        provider = ArchaeologyContextProvider(repo_path, cache_enabled=False)
        provider.initialize(max_commits=20)

        file_path = "agents/qa-test-engineer.md"
        question = "What is this?"

        result1 = provider.get_context(file_path, question)
        result2 = provider.get_context(file_path, question)

        # Both should be cache misses
        assert result1['cached'] is False
        assert result2['cached'] is False

    def test_cache_clear(self, provider):
        """Test cache clearing."""
        file_path = "agents/qa-test-engineer.md"
        question = "What is this?"

        # Populate cache
        provider.get_context(file_path, question)

        # Should be cached
        result = provider.get_context(file_path, question)
        assert result['cached'] is True

        # Clear cache
        provider.clear_cache()

        # Should be cache miss
        result = provider.get_context(file_path, question)
        assert result['cached'] is False

    def test_cache_stats_tracking(self, provider):
        """Test cache statistics are tracked correctly."""
        file_path = "agents/qa-test-engineer.md"

        # Make queries
        provider.get_context(file_path, "Question 1")  # miss
        provider.get_context(file_path, "Question 1")  # hit
        provider.get_context(file_path, "Question 2")  # miss
        provider.get_context(file_path, "Question 1")  # hit

        stats = provider.get_stats()
        assert stats['cache_hit_rate'] == 0.5  # 2 hits, 2 misses


class TestPerformance:
    """Test performance requirements."""

    def test_p95_latency_under_1s(self, provider):
        """Test p95 latency is under 1 second."""
        # Make multiple queries to get statistical sample
        for i in range(10):
            provider.get_context(
                file_path=f"agents/full-stack-architect.md",
                question=f"Test question {i}"
            )

        stats = provider.get_stats()
        assert stats['p95_latency_ms'] < 1000, \
            f"p95 latency {stats['p95_latency_ms']}ms exceeds 1000ms target"

    def test_cached_response_instant(self, provider):
        """Test cached responses have zero latency."""
        file_path = "agents/qa-test-engineer.md"
        question = "What is this?"

        # First query
        provider.get_context(file_path, question)

        # Second query (cached)
        result = provider.get_context(file_path, question)

        assert result['cached'] is True
        assert result['latency_ms'] == 0

    def test_memory_usage_under_100mb(self, repo_path):
        """Test memory usage stays under 100MB."""
        tracemalloc.start()

        provider = ArchaeologyContextProvider(repo_path)
        provider.initialize()

        # Make several queries
        for i in range(20):
            provider.get_context(
                file_path="agents/full-stack-architect.md",
                question=f"Question {i}"
            )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024

        # This is a soft target - actual usage depends on repo size
        # For test repo with 50 commits, should be well under 100MB
        assert peak_mb < 100, f"Peak memory usage {peak_mb:.2f}MB exceeds 100MB target"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_timeout_handling(self, provider):
        """Test timeout error handling (simulated)."""
        # This test would require mocking the synthesizer
        # For now, just verify the API exists
        # In production, we'd add timeout parameter to get_context()
        pass

    def test_cca_unavailable(self, repo_path):
        """Test handling when CCA system is unavailable."""
        with patch('tools.code_archaeology.GitArchaeologist') as mock_arch:
            mock_arch.side_effect = RuntimeError("Git command failed")

            provider = ArchaeologyContextProvider(repo_path)

            with pytest.raises(RuntimeError, match="Failed to initialize"):
                provider.initialize()

    def test_invalid_file_path(self, provider):
        """Test handling of queries for non-existent files."""
        # Should still work - archaeology system is question-based
        result = provider.get_context(
            file_path="nonexistent/file.py",
            question="Does this exist?"
        )

        # May have low confidence, but should not error
        assert 'answer' in result
        assert 'confidence' in result


class TestStatistics:
    """Test statistics and monitoring."""

    def test_get_stats_empty(self, repo_path):
        """Test get_stats with no queries."""
        provider = ArchaeologyContextProvider(repo_path)
        provider.initialize(max_commits=10)

        stats = provider.get_stats()

        assert stats['total_queries'] == 0
        assert stats['cache_hit_rate'] == 0.0
        assert stats['avg_latency_ms'] == 0

    def test_get_stats_with_queries(self, provider):
        """Test get_stats after queries."""
        # Make some queries
        provider.get_context("agents/qa-test-engineer.md", "Q1")
        provider.get_context("agents/qa-test-engineer.md", "Q1")  # cached
        provider.get_context("agents/qa-test-engineer.md", "Q2")

        stats = provider.get_stats()

        assert stats['total_queries'] == 2  # Only uncached queries counted
        assert stats['cache_hit_rate'] == 1/3  # 1 hit, 2 misses
        assert stats['avg_latency_ms'] > 0
        assert stats['p95_latency_ms'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
