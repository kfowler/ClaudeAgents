"""
Tests for FAISS integration in AIL Sprint 2.

This module provides comprehensive tests for the EmbeddingGenerator and FAISSIndex
components, including unit tests, integration tests, and performance benchmarks.
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import pytest
import numpy as np

# Import components to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.embeddings import EmbeddingGenerator, EmbeddingConfig
from tools.ail.faiss_index import FAISSIndex, FAISSConfig
from tools.ail.context_provider import ArchaeologyContextProvider

# Import CCA components for testing
from tools.code_archaeology import (
    EnrichedCommit,
    Commit,
    PullRequest,
    Citation,
    Answer,
)

# Check for optional dependencies
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    import sentence_transformers
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


# ===========================
# Fixtures
# ===========================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_commit():
    """Create a mock enriched commit."""
    commit = MagicMock(spec=Commit)
    commit.sha = "abc123def456"
    commit.message = "Add new feature for user authentication"
    commit.author = "John Doe"
    commit.date = "2024-01-01"
    commit.files_changed = ["auth.py", "tests/test_auth.py"]

    enriched = MagicMock(spec=EnrichedCommit)
    enriched.commit = commit
    enriched.pull_request = None

    return enriched


@pytest.fixture
def mock_commits():
    """Create multiple mock commits."""
    commits = []
    for i in range(5):
        commit = MagicMock(spec=Commit)
        commit.sha = f"sha{i:03d}"
        commit.message = f"Commit message {i}"
        commit.author = f"Author {i}"
        commit.date = f"2024-01-{i+1:02d}"
        commit.files_changed = [f"file{i}.py"]

        enriched = MagicMock(spec=EnrichedCommit)
        enriched.commit = commit
        enriched.pull_request = None
        commits.append(enriched)

    return commits


@pytest.fixture
def embedding_config(temp_dir):
    """Create embedding configuration."""
    return EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",
        dimension=384,
        batch_size=32,
        cache_dir=temp_dir / "cache",
        normalize=True,
    )


@pytest.fixture
def faiss_config(temp_dir):
    """Create FAISS configuration."""
    return FAISSConfig(
        index_type="IndexHNSWFlat",
        dimension=384,
        metric="cosine",
        hnsw_m=32,
        hnsw_ef_construction=200,
        hnsw_ef_search=50,
        index_path=temp_dir / "faiss" / "index.bin",
        metadata_path=temp_dir / "faiss" / "metadata.pkl",
    )


# ===========================
# EmbeddingGenerator Tests
# ===========================

class TestEmbeddingGenerator:
    """Tests for the EmbeddingGenerator class."""

    def test_initialization(self, embedding_config):
        """Test embedding generator initialization."""
        generator = EmbeddingGenerator(embedding_config)

        assert generator.config == embedding_config
        assert generator._cache == {}
        assert generator._cache_hits == 0
        assert generator._cache_misses == 0

    @patch('tools.ail.embeddings.SentenceTransformer')
    def test_embed_commits(self, mock_transformer, embedding_config, mock_commits):
        """Test embedding generation for commits."""
        # Setup mock transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(len(mock_commits), 384).astype(np.float32)
        mock_transformer.return_value = mock_model

        generator = EmbeddingGenerator(embedding_config)
        embeddings, doc_ids = generator.embed_commits(mock_commits)

        # Verify results
        assert embeddings.shape == (len(mock_commits), 384)
        assert len(doc_ids) == len(mock_commits)
        assert all(doc_id.startswith("commit_") for doc_id in doc_ids)

        # Verify model was called
        mock_model.encode.assert_called_once()

    @patch('tools.ail.embeddings.SentenceTransformer')
    def test_embed_query(self, mock_transformer, embedding_config):
        """Test query embedding generation."""
        # Setup mock transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(384).astype(np.float32)
        mock_transformer.return_value = mock_model

        generator = EmbeddingGenerator(embedding_config)
        query = "Why was this feature added?"
        embedding = generator.embed_query(query)

        # Verify results
        assert embedding.shape == (384,)
        assert embedding.dtype == np.float32

        # Verify query was enhanced
        mock_model.encode.assert_called_with(
            f"Question: {query}",
            normalize_embeddings=True,
            show_progress_bar=False
        )

    @patch('tools.ail.embeddings.SentenceTransformer')
    def test_caching(self, mock_transformer, embedding_config, mock_commits):
        """Test embedding caching functionality."""
        # Setup mock transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.randn(len(mock_commits), 384).astype(np.float32)
        mock_transformer.return_value = mock_model

        generator = EmbeddingGenerator(embedding_config)

        # First call - should miss cache
        embeddings1, doc_ids1 = generator.embed_commits(mock_commits)
        assert generator._cache_misses == len(mock_commits)
        assert generator._cache_hits == 0

        # Second call - should hit cache
        embeddings2, doc_ids2 = generator.embed_commits(mock_commits)
        assert generator._cache_hits == len(mock_commits)

        # Embeddings should be identical
        np.testing.assert_array_equal(embeddings1, embeddings2)
        assert doc_ids1 == doc_ids2

    @patch('tools.ail.embeddings.SentenceTransformer')
    def test_batch_processing(self, mock_transformer, embedding_config):
        """Test batch embedding processing."""
        # Setup mock transformer
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        generator = EmbeddingGenerator(embedding_config)
        texts = [f"Text {i}" for i in range(100)]

        # Mock encode to return appropriate sized array
        mock_model.encode.return_value = np.random.randn(len(texts), 384).astype(np.float32)

        embeddings = generator.embed_batch(texts)

        # Verify batch processing was used
        assert embeddings.shape == (100, 384)
        mock_model.encode.assert_called_once()

    def test_cache_persistence(self, embedding_config, temp_dir):
        """Test cache saving and loading."""
        generator = EmbeddingGenerator(embedding_config)

        # Add some entries to cache
        test_cache = {
            "key1": np.random.randn(384).astype(np.float32),
            "key2": np.random.randn(384).astype(np.float32),
        }
        generator._cache = test_cache

        # Save cache
        generator.save_cache()

        # Create new generator and verify cache loaded
        new_generator = EmbeddingGenerator(embedding_config)
        assert len(new_generator._cache) == 2
        np.testing.assert_array_almost_equal(
            new_generator._cache["key1"],
            test_cache["key1"]
        )

    def test_graceful_degradation(self, embedding_config, mock_commits):
        """Test graceful degradation when model unavailable."""
        with patch('tools.ail.embeddings.HAS_SENTENCE_TRANSFORMERS', False):
            generator = EmbeddingGenerator(embedding_config)
            embeddings, doc_ids = generator.embed_commits(mock_commits)

            # Should return zero embeddings
            assert embeddings.shape == (len(mock_commits), 384)
            assert np.allclose(embeddings, 0)
            assert len(doc_ids) == len(mock_commits)


# ===========================
# FAISSIndex Tests
# ===========================

class TestFAISSIndex:
    """Tests for the FAISSIndex class."""

    def test_initialization(self, faiss_config):
        """Test FAISS index initialization."""
        index = FAISSIndex(faiss_config)

        assert index.config == faiss_config
        assert index.metadata == {}
        assert index.doc_to_idx == {}
        assert index._total_searches == 0

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_add_documents(self, faiss_config):
        """Test adding documents to index."""
        index = FAISSIndex(faiss_config)

        # Create test embeddings
        embeddings = np.random.randn(10, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(10)]

        # Add documents
        index.add_documents(embeddings, doc_ids)

        # Verify index updated
        assert index.size == 10
        assert len(index.metadata) == 10
        assert len(index.doc_to_idx) == 10

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_search(self, faiss_config):
        """Test searching the index."""
        index = FAISSIndex(faiss_config)

        # Add test documents
        embeddings = np.random.randn(100, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(100)]
        index.add_documents(embeddings, doc_ids)

        # Search with a query
        query = np.random.randn(384).astype(np.float32)
        results = index.search(query, k=10)

        # Verify results
        assert len(results) <= 10
        assert all(isinstance(r, tuple) for r in results)
        assert all(len(r) == 2 for r in results)  # (doc_id, score)

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_batch_search(self, faiss_config):
        """Test batch searching."""
        index = FAISSIndex(faiss_config)

        # Add test documents
        embeddings = np.random.randn(50, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(50)]
        index.add_documents(embeddings, doc_ids)

        # Search with multiple queries
        queries = np.random.randn(5, 384).astype(np.float32)
        results = index.search_batch(queries, k=10)

        # Verify results
        assert len(results) == 5
        for result in results:
            assert len(result) <= 10

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_persistence(self, faiss_config, temp_dir):
        """Test index saving and loading."""
        index = FAISSIndex(faiss_config)

        # Add documents
        embeddings = np.random.randn(20, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(20)]
        index.add_documents(embeddings, doc_ids)

        # Save index
        index.save()
        assert faiss_config.index_path.exists()
        assert faiss_config.metadata_path.exists()

        # Load into new index
        new_index = FAISSIndex(faiss_config)
        new_index.load()

        # Verify loaded correctly
        assert new_index.size == 20
        assert new_index.metadata == index.metadata
        assert new_index.doc_to_idx == index.doc_to_idx

    def test_graceful_degradation_no_faiss(self, faiss_config):
        """Test graceful degradation when FAISS unavailable."""
        with patch('tools.ail.faiss_index.HAS_FAISS', False):
            index = FAISSIndex(faiss_config)

            # Operations should fail gracefully
            embeddings = np.random.randn(10, 384).astype(np.float32)
            doc_ids = [f"doc_{i}" for i in range(10)]

            index.add_documents(embeddings, doc_ids)
            assert index.size == 0

            query = np.random.randn(384).astype(np.float32)
            results = index.search(query)
            assert results == []

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_memory_usage(self, faiss_config):
        """Test memory usage reporting."""
        index = FAISSIndex(faiss_config)

        # Add documents
        embeddings = np.random.randn(100, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(100)]
        index.add_documents(embeddings, doc_ids)

        # Get memory stats
        memory_stats = index.get_memory_usage()

        assert 'index_mb' in memory_stats
        assert 'metadata_mb' in memory_stats
        assert 'total_mb' in memory_stats
        assert memory_stats['total_mb'] > 0


# ===========================
# Integration Tests
# ===========================

class TestFAISSIntegration:
    """Integration tests for FAISS with ArchaeologyContextProvider."""

    @pytest.fixture
    def mock_repo(self, temp_dir):
        """Create a mock repository."""
        repo_dir = temp_dir / "repo"
        repo_dir.mkdir()
        (repo_dir / ".git").mkdir()
        return repo_dir

    async def test_context_provider_with_faiss(self, mock_repo, monkeypatch):
        """Test ArchaeologyContextProvider with FAISS enabled."""
        # Mock the CCA components
        with patch('tools.ail.context_provider.GitArchaeologist'), \
             patch('tools.ail.context_provider.GitHubArchaeologist'), \
             patch('tools.ail.context_provider.ContextSynthesizer'), \
             patch('tools.ail.context_provider.HAS_FAISS_INTEGRATION', True):

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_repo),
                enable_semantic_cache=False  # Disable L2 cache for this test
            )

            # Mock FAISS components
            provider._faiss_enabled = True
            provider._embedding_generator = MagicMock()
            provider._faiss_index = MagicMock()

            # Mock search results
            provider._faiss_index.search.return_value = [
                ("commit_abc123", 0.95),
                ("commit_def456", 0.85),
            ]

            # Mock enriched history
            mock_history = MagicMock()
            mock_history.enriched_commits = []
            provider._searchable_index = MagicMock()
            provider._searchable_index.enriched_history = mock_history

            # Test query
            with patch.object(provider, '_initialize_faiss', return_value=True):
                with patch.object(provider, '_query_with_faiss') as mock_query:
                    mock_query.return_value = Answer(
                        question="test question",
                        answer="test answer",
                        citations=[],
                        confidence=0.9,
                        reasoning="FAISS"
                    )

                    context = await provider.get_context("test.py", "Why was this added?")

                    assert context.answer == "test answer"
                    assert context.confidence == 0.9
                    mock_query.assert_called_once()

    def test_faiss_initialization_failure(self, mock_repo):
        """Test graceful handling of FAISS initialization failure."""
        with patch('tools.ail.context_provider.HAS_FAISS_INTEGRATION', False):
            provider = ArchaeologyContextProvider(repo_path=str(mock_repo))

            assert provider._faiss_enabled == False
            assert provider._faiss_initialized == False

    async def test_faiss_fallback_on_error(self, mock_repo):
        """Test fallback to original search when FAISS fails."""
        provider = ArchaeologyContextProvider(repo_path=str(mock_repo))

        # Mock FAISS to fail
        provider._faiss_enabled = True
        with patch.object(provider, '_initialize_faiss', return_value=True), \
             patch.object(provider, '_query_with_faiss', side_effect=Exception("FAISS error")), \
             patch.object(provider, '_context_synthesizer') as mock_synthesizer:

            mock_synthesizer.synthesize_answer.return_value = Answer(
                question="test",
                answer="fallback answer",
                citations=[],
                confidence=0.7,
                reasoning="TF-IDF"
            )

            # Initialize components
            provider._initialized = True
            provider._searchable_index = MagicMock()

            # Query should fall back
            answer = await provider._query_archaeology("test.py", "question")

            assert answer.answer == "fallback answer"
            assert answer.reasoning == "TF-IDF"


# ===========================
# Performance Benchmarks
# ===========================

class TestPerformance:
    """Performance benchmarks for FAISS integration."""

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_index_build_performance(self, faiss_config):
        """Test index building performance."""
        index = FAISSIndex(faiss_config)

        # Prepare data
        embeddings = np.random.randn(1000, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(1000)]

        # Measure performance
        start = time.time()
        index.add_documents(embeddings, doc_ids)
        elapsed = time.time() - start

        # Verify target: <30s for 1000 commits
        assert elapsed < 30.0
        assert index.size == 1000

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_search_performance(self, faiss_config):
        """Test search performance."""
        index = FAISSIndex(faiss_config)

        # Build index
        embeddings = np.random.randn(1000, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(1000)]
        index.add_documents(embeddings, doc_ids)

        # Prepare query
        query = np.random.randn(384).astype(np.float32)

        # Measure performance
        start = time.time()
        results = index.search(query, k=10)
        elapsed = time.time() - start

        # Verify target: <50ms for search
        assert elapsed < 0.050
        assert len(results) <= 10

    @pytest.mark.skipif(not HAS_SENTENCE_TRANSFORMERS,
                       reason="sentence-transformers not installed")
    def test_embedding_generation_performance(self, embedding_config):
        """Test embedding generation performance."""
        generator = EmbeddingGenerator(embedding_config)

        # Prepare text
        text = "This is a sample commit message for performance testing"

        # Measure performance
        start = time.time()
        embedding = generator.embed_query(text)
        elapsed = time.time() - start

        # Verify target: <30ms for single embedding (relaxed to 1s for first run with model loading)
        assert elapsed < 1.0
        assert embedding.shape == (384,)


# ===========================
# Error Handling Tests
# ===========================

class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_mismatched_dimensions(self, faiss_config):
        """Test handling of mismatched embedding dimensions."""
        index = FAISSIndex(faiss_config)

        # Try to add embeddings with wrong dimension
        embeddings = np.random.randn(10, 256).astype(np.float32)  # Wrong dimension
        doc_ids = [f"doc_{i}" for i in range(10)]

        # Should fail with FAISS installed due to dimension mismatch
        # Without FAISS, it would just return gracefully
        with pytest.raises(Exception):
            index.add_documents(embeddings, doc_ids)

    def test_empty_index_search(self, faiss_config):
        """Test searching an empty index."""
        index = FAISSIndex(faiss_config)

        query = np.random.randn(384).astype(np.float32)
        results = index.search(query)

        assert results == []

    @pytest.mark.skipif(not HAS_FAISS, reason="FAISS not installed")
    def test_invalid_config(self, temp_dir):
        """Test handling of invalid configuration."""
        # Invalid index type
        config = FAISSConfig(
            index_type="InvalidIndexType",
            dimension=384,
            index_path=temp_dir / "index.bin"
        )

        with pytest.raises(ValueError):
            index = FAISSIndex(config)

    @patch('tools.ail.embeddings.SentenceTransformer')
    def test_model_loading_failure(self, mock_transformer, embedding_config):
        """Test handling of model loading failure."""
        mock_transformer.side_effect = Exception("Model not found")

        generator = EmbeddingGenerator(embedding_config)

        assert generator._model_loaded == False
        assert generator.model is None

        # Should return zero embeddings
        embedding = generator.embed_query("test")
        assert np.allclose(embedding, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])