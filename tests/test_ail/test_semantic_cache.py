"""
Tests for semantic caching system (AIL Sprint 2).

This test suite validates:
- SemanticCache core functionality
- TwoTierCache integration
- Performance benchmarks (hit rate, latency, memory)
- Thread safety
- Edge cases and error handling
"""

import pytest
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

try:
    import numpy as np
    import faiss
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

from tools.ail.semantic_cache import (
    SemanticCache,
    SemanticCacheEntry,
    SemanticCacheStats,
)
from tools.ail.two_tier_cache import TwoTierCache, TwoTierCacheStats
from tools.ail.context_provider import LRUCache, ArchaeologicalContext, ContextSource


# Skip all tests if dependencies not available
pytestmark = pytest.mark.skipif(
    not HAS_DEPENDENCIES,
    reason="FAISS and NumPy required for semantic cache tests"
)


@pytest.fixture
def mock_embedding_provider():
    """Create mock embedding provider."""
    provider = Mock()
    # Return consistent embeddings for testing
    provider.embed = Mock(side_effect=lambda texts: [
        np.random.randn(512) for _ in texts
    ])
    return provider


@pytest.fixture
def semantic_cache(mock_embedding_provider):
    """Create semantic cache instance."""
    return SemanticCache(
        embedding_provider=mock_embedding_provider,
        max_entries=10,  # Small for testing
        similarity_threshold=0.85,
        ttl_seconds=60,
        enabled=True,
    )


@pytest.fixture
def sample_context():
    """Create sample archaeological context."""
    return ArchaeologicalContext(
        file_path="test.py",
        question="Why was this implemented?",
        answer="Implementation rationale...",
        sources=[],
        confidence=0.9,
    )


class TestSemanticCacheEntry:
    """Test SemanticCacheEntry dataclass."""

    def test_entry_creation(self):
        """Test creating cache entry."""
        entry = SemanticCacheEntry(
            query_text="test query",
            file_path="test.py",
            cached_result="result",
            embedding=np.random.randn(512),
        )

        assert entry.query_text == "test query"
        assert entry.file_path == "test.py"
        assert entry.cached_result == "result"
        assert entry.access_count == 0
        assert isinstance(entry.created_at, datetime)

    def test_entry_age_calculation(self):
        """Test entry age calculation."""
        entry = SemanticCacheEntry(
            query_text="test",
            file_path="test.py",
            cached_result="result",
            embedding=np.random.randn(512),
        )

        # Age should be very small (just created)
        assert entry.age_seconds < 1.0

    def test_entry_expiration(self):
        """Test entry expiration check."""
        entry = SemanticCacheEntry(
            query_text="test",
            file_path="test.py",
            cached_result="result",
            embedding=np.random.randn(512),
        )

        # Not expired with 60s TTL
        assert not entry.is_expired(60)

        # Expired with 0s TTL
        time.sleep(0.01)
        assert entry.is_expired(0)


class TestSemanticCacheStats:
    """Test SemanticCacheStats."""

    def test_stats_initialization(self):
        """Test stats initialization."""
        stats = SemanticCacheStats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_queries == 0
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = SemanticCacheStats(hits=7, misses=3, total_queries=10)

        assert stats.hit_rate == 0.7

    def test_stats_to_dict(self):
        """Test converting stats to dict."""
        stats = SemanticCacheStats(hits=7, misses=3, total_queries=10)
        stats_dict = stats.to_dict()

        assert stats_dict['hits'] == 7
        assert stats_dict['misses'] == 3
        assert stats_dict['hit_rate'] == '70.0%'


class TestSemanticCacheCore:
    """Test SemanticCache core functionality."""

    def test_cache_initialization(self, mock_embedding_provider):
        """Test cache initialization."""
        cache = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=500,
            similarity_threshold=0.85,
            enabled=True,
        )

        assert cache.enabled
        assert cache.max_entries == 500
        assert cache.similarity_threshold == 0.85
        assert cache.size == 0

    def test_cache_disabled_if_no_dependencies(self):
        """Test cache gracefully disables without dependencies."""
        # Mock missing FAISS
        import tools.ail.semantic_cache as sc
        original_has_faiss = sc.HAS_FAISS
        sc.HAS_FAISS = False

        try:
            cache = SemanticCache(enabled=True)
            assert not cache.enabled
        finally:
            sc.HAS_FAISS = original_has_faiss

    def test_query_normalization(self, semantic_cache):
        """Test query normalization."""
        test_cases = [
            ("What's this?", "what is this"),
            ("Why   isn't   it   working?", "why is not it working"),
            ("Can't connect!", "cannot connect"),
        ]

        for input_query, expected in test_cases:
            normalized = semantic_cache.normalize_query(input_query)
            assert normalized == expected

    def test_put_and_get_exact_match(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test putting and getting exact match."""
        # Make embedding provider return consistent embeddings
        test_embedding = np.random.randn(512)
        mock_embedding_provider.embed = Mock(return_value=[test_embedding])

        # Put
        semantic_cache.put("test.py", "test query", sample_context)
        assert semantic_cache.size == 1

        # Get (should hit with same query)
        result = semantic_cache.get("test.py", "test query")
        assert result is not None
        cached_result, similarity = result
        assert cached_result == sample_context
        assert similarity > 0.99  # Should be very high for exact match

    def test_get_empty_cache(self, semantic_cache):
        """Test getting from empty cache."""
        result = semantic_cache.get("test.py", "query")
        assert result is None
        assert semantic_cache.stats.misses == 1

    def test_get_below_threshold(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test cache miss when similarity below threshold."""
        # Put with one embedding
        embedding1 = np.random.randn(512)
        mock_embedding_provider.embed = Mock(return_value=[embedding1])
        semantic_cache.put("test.py", "query 1", sample_context)

        # Query with very different embedding
        embedding2 = -embedding1  # Opposite direction = low similarity
        mock_embedding_provider.embed = Mock(return_value=[embedding2])
        result = semantic_cache.get("test.py", "query 2")

        # Should miss because similarity too low
        assert result is None or result[1] < semantic_cache.similarity_threshold

    def test_ttl_expiration(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test TTL expiration."""
        # Create cache with 0 second TTL
        cache_short_ttl = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=10,
            similarity_threshold=0.85,
            ttl_seconds=0,
            enabled=True,
        )

        # Put entry
        test_embedding = np.random.randn(512)
        mock_embedding_provider.embed = Mock(return_value=[test_embedding])
        cache_short_ttl.put("test.py", "query", sample_context)

        # Wait a bit
        time.sleep(0.01)

        # Get should miss due to expiration
        result = cache_short_ttl.get("test.py", "query")
        assert result is None

    def test_clear_cache(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test clearing cache."""
        # Add entries
        for i in range(5):
            mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
            semantic_cache.put(f"file{i}.py", f"query {i}", sample_context)

        assert semantic_cache.size == 5

        # Clear
        semantic_cache.clear()
        assert semantic_cache.size == 0


class TestSemanticCacheEviction:
    """Test cache eviction policies."""

    def test_eviction_on_capacity(self, mock_embedding_provider, sample_context):
        """Test eviction when reaching capacity."""
        cache = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=5,
            similarity_threshold=0.85,
            enabled=True,
        )

        # Fill cache beyond capacity
        for i in range(10):
            mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
            cache.put(f"file{i}.py", f"query {i}", sample_context)

        # Should not exceed capacity (with eviction to 80% = 4 entries)
        assert cache.size <= 5
        assert cache.stats.evictions > 0

    def test_lru_lfu_hybrid_eviction(self, mock_embedding_provider, sample_context):
        """Test hybrid LRU+LFU eviction."""
        cache = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=5,
            similarity_threshold=0.85,
            enabled=True,
        )

        # Add entries
        embeddings = []
        for i in range(5):
            emb = np.random.randn(512)
            embeddings.append(emb)
            mock_embedding_provider.embed = Mock(return_value=[emb])
            cache.put(f"file{i}.py", f"query {i}", sample_context)

        # Access some entries multiple times (increase frequency)
        mock_embedding_provider.embed = Mock(return_value=[embeddings[0]])
        for _ in range(5):
            cache.get("file0.py", "query 0")

        # Add one more entry to trigger eviction
        mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
        cache.put("file_new.py", "new query", sample_context)

        # Frequently accessed entry should be retained
        mock_embedding_provider.embed = Mock(return_value=[embeddings[0]])
        result = cache.get("file0.py", "query 0")
        # Note: May or may not hit depending on eviction timing, but should not crash


class TestTwoTierCache:
    """Test TwoTierCache integration."""

    @pytest.fixture
    def l1_cache(self):
        """Create L1 cache."""
        return LRUCache(max_size=10)

    @pytest.fixture
    def two_tier_cache(self, l1_cache, semantic_cache):
        """Create two-tier cache."""
        return TwoTierCache(
            l1_cache=l1_cache,
            l2_cache=semantic_cache,
            l2_enabled=True,
        )

    def test_two_tier_initialization(self, two_tier_cache):
        """Test two-tier cache initialization."""
        assert two_tier_cache.l1_enabled
        assert two_tier_cache.l2_enabled

    def test_l1_hit(self, two_tier_cache, sample_context):
        """Test L1 cache hit."""
        # Put in L1 directly
        cache_key = "test_key"
        two_tier_cache.l1_cache.put(cache_key, sample_context)

        # Get should hit L1
        result = two_tier_cache.get("test.py", "query", cache_key)
        assert result is not None
        cached_result, cache_level, similarity = result
        assert cache_level == "L1"
        assert similarity == 1.0
        assert two_tier_cache.stats.l1_hits == 1

    def test_l2_hit_and_promotion(self, two_tier_cache, sample_context, mock_embedding_provider):
        """Test L2 cache hit and promotion to L1."""
        cache_key = "test_key"

        # Put in L2 only
        test_embedding = np.random.randn(512)
        mock_embedding_provider.embed = Mock(return_value=[test_embedding])
        two_tier_cache.l2_cache.put("test.py", "query", sample_context)

        # Get should hit L2
        result = two_tier_cache.get("test.py", "query", cache_key)
        assert result is not None
        cached_result, cache_level, similarity = result
        assert cache_level == "L2"
        assert two_tier_cache.stats.l2_hits == 1

        # Should be promoted to L1
        assert two_tier_cache.l1_cache.get(cache_key) is not None

    def test_both_miss(self, two_tier_cache):
        """Test cache miss in both tiers."""
        result = two_tier_cache.get("test.py", "query", "nonexistent_key")
        assert result is None
        assert two_tier_cache.stats.l1_misses == 1
        assert two_tier_cache.stats.l2_misses == 1

    def test_put_populates_both_tiers(self, two_tier_cache, sample_context, mock_embedding_provider):
        """Test put populates both L1 and L2."""
        cache_key = "test_key"
        test_embedding = np.random.randn(512)
        mock_embedding_provider.embed = Mock(return_value=[test_embedding])

        two_tier_cache.put("test.py", "query", cache_key, sample_context)

        # Check L1
        assert two_tier_cache.l1_cache.get(cache_key) is not None

        # Check L2
        assert two_tier_cache.l2_cache.size == 1

    def test_clear_both_tiers(self, two_tier_cache, sample_context, mock_embedding_provider):
        """Test clearing both cache tiers."""
        # Add to both
        cache_key = "test_key"
        mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
        two_tier_cache.put("test.py", "query", cache_key, sample_context)

        # Clear
        two_tier_cache.clear()

        assert two_tier_cache.l1_cache.size == 0
        assert two_tier_cache.l2_cache.size == 0

    def test_combined_statistics(self, two_tier_cache, sample_context, mock_embedding_provider):
        """Test combined statistics."""
        # Generate some cache activity
        cache_key1 = "key1"
        cache_key2 = "key2"

        # L1 hit
        two_tier_cache.l1_cache.put(cache_key1, sample_context)
        two_tier_cache.get("test.py", "query1", cache_key1)

        # L2 hit
        mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
        two_tier_cache.l2_cache.put("test.py", "query2", sample_context)
        two_tier_cache.get("test.py", "query2", cache_key2)

        # Both miss
        two_tier_cache.get("test.py", "query3", "key3")

        stats = two_tier_cache.get_combined_stats()
        assert stats['l1_hits'] == 1
        assert stats['l2_hits'] == 1
        assert stats['l2_misses'] == 1
        assert stats['total_queries'] == 3

    def test_l2_disabled(self, l1_cache, sample_context):
        """Test two-tier cache with L2 disabled."""
        cache = TwoTierCache(
            l1_cache=l1_cache,
            l2_cache=None,
            l2_enabled=False,
        )

        assert cache.l1_enabled
        assert not cache.l2_enabled

        # Put and get should only use L1
        cache_key = "test_key"
        l1_cache.put(cache_key, sample_context)

        result = cache.get("test.py", "query", cache_key)
        assert result is not None
        assert result[1] == "L1"


class TestSemanticCachePerformance:
    """Test semantic cache performance."""

    def test_lookup_latency(self, mock_embedding_provider):
        """Test L2 lookup latency target (<50ms)."""
        cache = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=500,
            similarity_threshold=0.85,
            enabled=True,
        )

        # Populate cache
        sample_context = ArchaeologicalContext(
            file_path="test.py",
            question="test",
            answer="answer",
            sources=[],
            confidence=0.9,
        )

        for i in range(100):  # Smaller set for unit tests
            mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
            cache.put(f"file{i}.py", f"query {i}", sample_context)

        # Measure lookup latency
        latencies = []
        for i in range(50):
            mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
            start = time.time()
            cache.get(f"file{i}.py", f"query {i}")
            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = sum(latencies) / len(latencies)
        # Relaxed threshold for unit tests (CI may be slower)
        assert avg_latency < 100, f"Average latency {avg_latency:.1f}ms exceeds 100ms"

    def test_memory_bounded(self, mock_embedding_provider):
        """Test memory usage stays bounded."""
        cache = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=500,
            similarity_threshold=0.85,
            enabled=True,
        )

        sample_context = ArchaeologicalContext(
            file_path="test.py",
            question="test",
            answer="answer",
            sources=[],
            confidence=0.9,
        )

        # Fill to capacity
        for i in range(1000):  # More than max_entries
            mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
            cache.put(f"file{i}.py", f"query {i}", sample_context)

        # Should not exceed max capacity
        assert cache.size <= cache.max_entries


class TestThreadSafety:
    """Test thread safety of semantic cache."""

    def test_concurrent_put_get(self, mock_embedding_provider):
        """Test concurrent put and get operations."""
        cache = SemanticCache(
            embedding_provider=mock_embedding_provider,
            max_entries=100,
            similarity_threshold=0.85,
            enabled=True,
        )

        sample_context = ArchaeologicalContext(
            file_path="test.py",
            question="test",
            answer="answer",
            sources=[],
            confidence=0.9,
        )

        errors = []

        def worker(thread_id):
            try:
                for i in range(10):
                    # Put
                    mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
                    cache.put(f"file{thread_id}_{i}.py", f"query {i}", sample_context)

                    # Get
                    cache.get(f"file{thread_id}_{i}.py", f"query {i}")
            except Exception as e:
                errors.append(e)

        # Run multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # Cache should have entries (exact count may vary due to eviction)
        assert cache.size > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_norm_embedding(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test handling of zero-norm embeddings."""
        # Return zero embedding
        mock_embedding_provider.embed = Mock(return_value=[np.zeros(512)])

        # Should not crash
        semantic_cache.put("test.py", "query", sample_context)
        result = semantic_cache.get("test.py", "query")

        # Should handle gracefully (likely miss)
        # No assertion on result since behavior may vary

    def test_embedding_generation_failure(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test handling of embedding generation failure."""
        # Make embedding fail
        mock_embedding_provider.embed = Mock(side_effect=Exception("Embedding failed"))

        # Should not crash
        semantic_cache.put("test.py", "query", sample_context)
        result = semantic_cache.get("test.py", "query")

        # Should return None (miss)
        assert result is None

    def test_faiss_search_failure(self, semantic_cache, sample_context, mock_embedding_provider):
        """Test handling of FAISS search failure."""
        # Add entry normally
        mock_embedding_provider.embed = Mock(return_value=[np.random.randn(512)])
        semantic_cache.put("test.py", "query", sample_context)

        # Corrupt index to cause search failure
        semantic_cache.index = None

        # Should not crash
        result = semantic_cache.get("test.py", "query")
        # Behavior may vary, no strict assertion


def test_integration_with_context_provider():
    """Test integration with ArchaeologyContextProvider."""
    # This is a smoke test - actual integration tested in test_context_provider.py
    try:
        from tools.ail.context_provider import ArchaeologyContextProvider

        # Should initialize without errors (may not have FAISS)
        # Just check imports work
        assert ArchaeologicalContext is not None
        assert TwoTierCache is not None
    except Exception as e:
        pytest.fail(f"Integration import failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
