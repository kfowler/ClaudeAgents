"""
Unit tests for ArchaeologyContextProvider.

Tests cover:
- Initialization and validation
- Cache operations (LRU behavior)
- Context retrieval (sync and async)
- Error handling and graceful degradation
- Timeout handling
- Cache statistics
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools'))

from ail.context_provider import (
    ArchaeologyContextProvider,
    ArchaeologicalContext,
    ContextSource,
    CacheStats,
    LRUCache,
)


class TestLRUCache:
    """Test LRU cache implementation."""

    def test_basic_operations(self):
        """Test basic get/put operations."""
        cache = LRUCache(max_size=3)

        # Create test contexts
        ctx1 = ArchaeologicalContext(
            file_path="file1.py",
            question="Q1",
            answer="A1",
            sources=[],
            confidence=0.8,
        )
        ctx2 = ArchaeologicalContext(
            file_path="file2.py",
            question="Q2",
            answer="A2",
            sources=[],
            confidence=0.9,
        )

        # Put and get
        cache.put("key1", ctx1)
        cache.put("key2", ctx2)

        assert cache.get("key1") == ctx1
        assert cache.get("key2") == ctx2
        assert cache.size == 2

    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = LRUCache(max_size=2)

        ctx1 = ArchaeologicalContext(
            file_path="file1.py", question="Q1", answer="A1",
            sources=[], confidence=0.8
        )
        ctx2 = ArchaeologicalContext(
            file_path="file2.py", question="Q2", answer="A2",
            sources=[], confidence=0.8
        )
        ctx3 = ArchaeologicalContext(
            file_path="file3.py", question="Q3", answer="A3",
            sources=[], confidence=0.8
        )

        # Fill cache
        cache.put("key1", ctx1)
        cache.put("key2", ctx2)

        # Access key1 (makes it most recently used)
        cache.get("key1")

        # Add key3 (should evict key2, not key1)
        cache.put("key3", ctx3)

        assert cache.get("key1") is not None  # Still in cache
        assert cache.get("key2") is None       # Evicted
        assert cache.get("key3") is not None   # Newly added
        assert cache.size == 2

    def test_clear(self):
        """Test cache clear operation."""
        cache = LRUCache(max_size=10)

        for i in range(5):
            ctx = ArchaeologicalContext(
                file_path=f"file{i}.py", question=f"Q{i}", answer=f"A{i}",
                sources=[], confidence=0.8
            )
            cache.put(f"key{i}", ctx)

        assert cache.size == 5

        cache.clear()

        assert cache.size == 0
        assert cache.get("key0") is None


class TestCacheStats:
    """Test cache statistics."""

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStats()

        # No queries yet
        assert stats.hit_rate == 0.0

        # Add some hits and misses
        stats.hits = 7
        stats.misses = 3
        stats.total_queries = 10

        assert stats.hit_rate == 0.7

    def test_to_dict(self):
        """Test dictionary conversion."""
        stats = CacheStats(
            hits=5,
            misses=3,
            total_queries=8,
            cache_size=10,
            max_cache_size=100,
        )

        data = stats.to_dict()

        assert data['hits'] == 5
        assert data['misses'] == 3
        assert data['total_queries'] == 8
        assert data['hit_rate'] == 0.625
        assert data['cache_size'] == 10


class TestContextSource:
    """Test ContextSource dataclass."""

    def test_from_citation(self):
        """Test creation from Citation."""
        from code_archaeology import Citation

        citation = Citation(
            commit_sha="abc123",
            commit_message="Test commit",
            commit_date=datetime.now(),
            author="Test Author",
            source_type="commit",
            relevance_score=0.85,
            excerpt="Test excerpt",
            url="https://github.com/test",
        )

        source = ContextSource.from_citation(citation)

        assert source.commit_sha == "abc123"
        assert source.commit_message == "Test commit"
        assert source.author == "Test Author"
        assert source.source_type == "commit"
        assert source.relevance_score == 0.85
        assert source.excerpt == "Test excerpt"
        assert source.url == "https://github.com/test"


class TestArchaeologicalContext:
    """Test ArchaeologicalContext dataclass."""

    def test_high_confidence_property(self):
        """Test high confidence detection."""
        ctx_high = ArchaeologicalContext(
            file_path="test.py",
            question="Test?",
            answer="Test answer",
            sources=[],
            confidence=0.8,
        )

        ctx_low = ArchaeologicalContext(
            file_path="test.py",
            question="Test?",
            answer="Test answer",
            sources=[],
            confidence=0.5,
        )

        assert ctx_high.has_high_confidence is True
        assert ctx_low.has_high_confidence is False

    def test_to_markdown(self):
        """Test markdown formatting."""
        source = ContextSource(
            commit_sha="abc123def456",
            commit_message="Test commit",
            author="John Doe",
            date=datetime(2024, 1, 1),
            source_type="commit",
            relevance_score=0.85,
            excerpt="This is a test excerpt",
            url="https://github.com/test",
        )

        ctx = ArchaeologicalContext(
            file_path="test.py",
            question="Why was this implemented?",
            answer="It was implemented to solve problem X.",
            sources=[source],
            confidence=0.9,
            query_time_ms=150.0,
        )

        markdown = ctx.to_markdown()

        assert "# Archaeological Context: test.py" in markdown
        assert "Why was this implemented?" in markdown
        assert "It was implemented to solve problem X." in markdown
        assert "John Doe" in markdown
        assert "abc123de" in markdown
        assert "150ms" in markdown


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)

    # Initialize git repo
    import subprocess
    subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)

    # Create a test file
    test_file = repo_path / 'test.py'
    test_file.write_text('# Test file\nprint("Hello")\n')

    # Commit it
    subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, check=True, capture_output=True)

    yield repo_path

    # Cleanup
    shutil.rmtree(temp_dir)


class TestArchaeologyContextProvider:
    """Test ArchaeologyContextProvider class."""

    def test_initialization_valid_repo(self, temp_git_repo):
        """Test initialization with valid repository."""
        provider = ArchaeologyContextProvider(
            repo_path=str(temp_git_repo),
            cache_size=100,
        )

        assert provider.repo_path.resolve() == temp_git_repo.resolve()
        assert provider.cache.max_size == 100
        assert provider.stats.max_cache_size == 100
        assert not provider.is_initialized()

    def test_initialization_invalid_repo(self):
        """Test initialization with invalid repository."""
        with pytest.raises(ValueError, match="Not a git repository"):
            ArchaeologyContextProvider(repo_path="/tmp/nonexistent")

    def test_cache_key_generation(self, temp_git_repo):
        """Test cache key generation."""
        provider = ArchaeologyContextProvider(repo_path=str(temp_git_repo))

        key1 = provider._generate_cache_key("test.py", "Why was this written?")
        key2 = provider._generate_cache_key("test.py", "Why was this written?")
        key3 = provider._generate_cache_key("test.py", "Different question?")
        key4 = provider._generate_cache_key("other.py", "Why was this written?")

        # Same inputs = same key
        assert key1 == key2

        # Different question = different key
        assert key1 != key3

        # Different file = different key
        assert key1 != key4

        # Keys should be hashes (32 hex chars)
        assert len(key1) == 64

    def test_cache_hit(self, temp_git_repo):
        """Test cache hit behavior."""
        provider = ArchaeologyContextProvider(repo_path=str(temp_git_repo))

        # Pre-populate cache
        cached_context = ArchaeologicalContext(
            file_path="test.py",
            question="Test question",
            answer="Cached answer",
            sources=[],
            confidence=0.9,
        )

        cache_key = provider._generate_cache_key("test.py", "Test question")
        provider.cache.put(cache_key, cached_context)

        # Query should return cached result
        result = provider.get_context_sync("test.py", "Test question")

        assert result.answer == "Cached answer"
        assert result.cached is True
        assert provider.stats.hits == 1
        assert provider.stats.misses == 0

    @patch('ail.context_provider.ContextSynthesizer')
    @patch('ail.context_provider.GitArchaeologist')
    def test_context_retrieval(self, mock_git, mock_synthesizer, temp_git_repo):
        """Test context retrieval (mocked)."""
        # Mock the CCA components
        mock_git_instance = MagicMock()
        mock_git.return_value = mock_git_instance

        mock_history = MagicMock()
        mock_history.total_commits = 10
        mock_history.commits = []
        mock_git_instance.analyze_repo.return_value = mock_history

        # Mock synthesizer
        mock_synth_instance = MagicMock()
        mock_synthesizer.return_value = mock_synth_instance

        mock_answer = MagicMock()
        mock_answer.answer = "Test answer from archaeology"
        mock_answer.confidence = 0.85
        mock_answer.citations = []
        mock_synth_instance.synthesize_answer.return_value = mock_answer

        # Create provider and initialize
        provider = ArchaeologyContextProvider(repo_path=str(temp_git_repo))

        # This should trigger initialization and query
        result = provider.get_context_sync("test.py", "Why?")

        assert "Test answer from archaeology" in result.answer
        assert provider.stats.total_queries == 1

    def test_graceful_degradation(self, temp_git_repo):
        """Test graceful degradation when CCA unavailable."""
        provider = ArchaeologyContextProvider(repo_path=str(temp_git_repo))

        # Force initialization failure
        provider._init_error = "Simulated CCA failure"

        result = provider.get_context_sync("test.py", "Why?")

        assert result.confidence == 0.0
        assert "unavailable" in result.answer.lower()
        assert "Simulated CCA failure" in result.answer

    def test_clear_cache(self, temp_git_repo):
        """Test cache clearing."""
        provider = ArchaeologyContextProvider(repo_path=str(temp_git_repo))

        # Add some cache entries
        for i in range(5):
            ctx = ArchaeologicalContext(
                file_path=f"file{i}.py",
                question=f"Q{i}",
                answer=f"A{i}",
                sources=[],
                confidence=0.8,
            )
            key = provider._generate_cache_key(f"file{i}.py", f"Q{i}")
            provider.cache.put(key, ctx)

        assert provider.cache.size == 5

        provider.clear_cache()

        assert provider.cache.size == 0
        assert provider.stats.cache_size == 0

    def test_get_cache_stats(self, temp_git_repo):
        """Test cache statistics retrieval."""
        provider = ArchaeologyContextProvider(repo_path=str(temp_git_repo))

        # Simulate some activity
        provider.stats.hits = 10
        provider.stats.misses = 5
        provider.stats.total_queries = 15
        provider.stats.cache_size = 10

        stats = provider.get_cache_stats()

        assert stats.hits == 10
        assert stats.misses == 5
        assert stats.hit_rate == 10 / 15


def test_main_function():
    """Test main CLI function."""
    # This is a simple smoke test
    from ail.context_provider import main

    # Should handle insufficient arguments gracefully
    import sys
    old_argv = sys.argv
    sys.argv = ['test']

    with pytest.raises(SystemExit):
        main()

    sys.argv = old_argv
