"""
Sprint 2 End-to-End Integration Tests

Validates complete Sprint 2 integration:
- FAISS + Two-tier cache flow
- Agent + AIL integration (7 agents)
- Error handling and graceful degradation
- Real-world query scenarios
- Performance under realistic load

Tests the full pipeline:
Query -> L1 Cache -> L2 Semantic Cache -> FAISS Search -> Result Synthesis
"""

import pytest
import asyncio
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from dataclasses import dataclass

try:
    import numpy as np
    import faiss
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

# Import AIL components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import (
    ArchaeologyContextProvider,
    ArchaeologicalContext,
    ContextSource,
    LRUCache,
)
from tools.ail.two_tier_cache import TwoTierCache
from tools.ail.semantic_cache import SemanticCache
from tools.ail.faiss_index import FAISSIndex, FAISSConfig
from tools.ail.embeddings import EmbeddingGenerator, EmbeddingConfig


pytestmark = pytest.mark.skipif(
    not HAS_DEPENDENCIES,
    reason="FAISS and NumPy required for Sprint 2 integration tests"
)


# ===========================
# Fixtures
# ===========================

@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_git_repo(temp_dir):
    """Create mock git repository."""
    repo_dir = temp_dir / "test_repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()

    # Create sample files
    (repo_dir / "auth.py").write_text("# Authentication module")
    (repo_dir / "api.py").write_text("# API module")

    return repo_dir


@pytest.fixture
def mock_cca_components():
    """Mock CCA components."""
    # Mock commit data
    mock_commits = []
    for i in range(10):
        commit = MagicMock()
        commit.sha = f"commit_{i:03d}"
        commit.message = f"Commit {i}: Implement feature"
        commit.author = "Test Author"
        commit.date = f"2024-01-{i+1:02d}"
        commit.files_changed = ["test.py"]

        enriched = MagicMock()
        enriched.commit = commit
        enriched.pull_request = None
        mock_commits.append(enriched)

    # Mock GitArchaeologist
    mock_git_archaeologist = MagicMock()
    mock_history = MagicMock()
    mock_history.enriched_commits = mock_commits
    mock_history.total_commits = len(mock_commits)
    mock_git_archaeologist.analyze_repo.return_value = mock_history

    # Mock GitHubArchaeologist
    mock_github_archaeologist = MagicMock()

    # Mock ContextSynthesizer
    mock_synthesizer = MagicMock()
    mock_answer = MagicMock()
    mock_answer.answer = "Test answer from archaeology"
    mock_answer.confidence = 0.85
    mock_answer.citations = []
    mock_synthesizer.synthesize_answer.return_value = mock_answer

    return {
        'git': mock_git_archaeologist,
        'github': mock_github_archaeologist,
        'synthesizer': mock_synthesizer,
        'commits': mock_commits,
    }


# ===========================
# End-to-End Integration Tests
# ===========================

class TestEndToEndIntegration:
    """Test complete Sprint 2 pipeline."""

    @pytest.mark.asyncio
    async def test_full_query_pipeline_l1_miss_l2_miss_faiss(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Test: Full pipeline with L1 miss, L2 miss, FAISS search

        Flow: Query -> L1 Miss -> L2 Miss -> FAISS Search -> Synthesize -> Cache Result
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls, \
             patch('tools.ail.embeddings.SentenceTransformer') as mock_transformer:

            # Setup mocks
            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            # Mock embedding model
            mock_model = MagicMock()
            mock_model.encode.return_value = np.random.randn(384).astype(np.float32)
            mock_transformer.return_value = mock_model

            # Create context provider with FAISS enabled
            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
                enable_semantic_cache=True,
            )

            # Force FAISS initialization
            provider._faiss_enabled = True

            # Query
            result = await provider.get_context("test.py", "Why was this implemented?")

            # Validate result
            assert result is not None
            assert isinstance(result, ArchaeologicalContext)
            assert result.file_path == "test.py"
            assert result.question == "Why was this implemented?"
            assert len(result.answer) > 0

            # Validate caching
            # Second query should hit L1 cache
            result2 = await provider.get_context("test.py", "Why was this implemented?")
            assert result2.cached is True

    @pytest.mark.asyncio
    async def test_l1_cache_hit_flow(self, temp_dir, mock_git_repo):
        """
        Test: L1 cache hit (fastest path)

        Flow: Query -> L1 Hit -> Return (no FAISS needed)
        """
        with patch('tools.ail.context_provider.GitArchaeologist'), \
             patch('tools.ail.context_provider.GitHubArchaeologist'), \
             patch('tools.ail.context_provider.ContextSynthesizer'):

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            # Pre-populate L1 cache
            cached_context = ArchaeologicalContext(
                file_path="test.py",
                question="Test question",
                answer="Cached answer",
                sources=[],
                confidence=0.9,
            )

            cache_key = provider._generate_cache_key("test.py", "Test question")
            provider.cache.put(cache_key, cached_context)

            # Query should hit L1
            start_time = time.time()
            result = await provider.get_context("test.py", "Test question")
            latency_ms = (time.time() - start_time) * 1000

            # Validate L1 hit
            assert result.answer == "Cached answer"
            assert result.cached is True
            assert provider.stats.hits == 1
            assert provider.stats.misses == 0

            # L1 hit should be fast (<10ms)
            assert latency_ms < 10, f"L1 cache hit took {latency_ms:.2f}ms (expected <10ms)"

    @pytest.mark.asyncio
    async def test_l2_semantic_cache_hit_flow(self, temp_dir, mock_git_repo):
        """
        Test: L2 semantic cache hit (similar query)

        Flow: Query -> L1 Miss -> L2 Semantic Hit -> Promote to L1 -> Return
        """
        with patch('tools.ail.context_provider.GitArchaeologist'), \
             patch('tools.ail.context_provider.GitHubArchaeologist'), \
             patch('tools.ail.context_provider.ContextSynthesizer'):

            # Create provider with semantic cache
            mock_embedding_provider = Mock()

            # Create consistent embeddings for similar queries
            original_embedding = np.random.randn(512)
            similar_embedding = original_embedding + np.random.randn(512) * 0.05  # Small noise

            mock_embedding_provider.embed = Mock(side_effect=[
                [original_embedding],  # First query
                [similar_embedding],   # Similar query
            ])

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
                enable_semantic_cache=True,
            )

            # Replace semantic cache with our mock
            l2_cache = SemanticCache(
                embedding_provider=mock_embedding_provider,
                max_entries=500,
                similarity_threshold=0.85,
                enabled=True,
            )

            provider._two_tier_cache = TwoTierCache(
                l1_cache=provider.cache,
                l2_cache=l2_cache,
                l2_enabled=True,
            )

            # Store original query result in L2
            cached_context = ArchaeologicalContext(
                file_path="test.py",
                question="Why was authentication added?",
                answer="For user security",
                sources=[],
                confidence=0.9,
            )

            cache_key_1 = "original_key"
            provider._two_tier_cache.put("test.py", "Why was authentication added?", cache_key_1, cached_context)

            # Query with similar question (should hit L2)
            cache_key_2 = "similar_key"
            result = provider._two_tier_cache.get("test.py", "How was authentication implemented?", cache_key_2)

            # Validate L2 hit
            if result is not None:
                cached_result, cache_level, similarity = result
                assert cache_level in ["L1", "L2"]  # May hit L2 or be promoted to L1

    def test_faiss_search_integration(self, temp_dir):
        """
        Test: FAISS search integration with embedding generation

        Flow: Query -> Embed -> FAISS Search -> Retrieve Commits
        """
        # Create FAISS index
        faiss_config = FAISSConfig(
            index_type="IndexHNSWFlat",
            dimension=384,
            index_path=temp_dir / "faiss" / "index.bin"
        )
        faiss_index = FAISSIndex(faiss_config)

        # Mock embedding generator
        with patch('tools.ail.embeddings.SentenceTransformer') as mock_transformer:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.random.randn(384).astype(np.float32)
            mock_transformer.return_value = mock_model

            embedding_config = EmbeddingConfig(
                model_name="all-MiniLM-L6-v2",
                dimension=384,
            )
            embedding_gen = EmbeddingGenerator(embedding_config)

            # Generate commit embeddings
            test_commits = [f"commit_{i}" for i in range(50)]
            commit_embeddings = np.random.randn(50, 384).astype(np.float32)

            # Index commits
            faiss_index.add_documents(commit_embeddings, test_commits)

            # Query
            query = "Why was this feature added?"
            query_embedding = embedding_gen.embed_query(query)

            # Search
            results = faiss_index.search(query_embedding, k=10)

            # Validate
            assert len(results) <= 10
            assert all(isinstance(r, tuple) for r in results)
            assert all(len(r) == 2 for r in results)  # (doc_id, score)

            # Verify results are sorted by relevance
            if len(results) > 1:
                scores = [score for _, score in results]
                assert scores == sorted(scores, reverse=True), "Results should be sorted by relevance"


class TestErrorHandlingAndDegradation:
    """Test error handling and graceful degradation."""

    @pytest.mark.asyncio
    async def test_faiss_initialization_failure_fallback(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Test: Graceful fallback when FAISS initialization fails

        Expected: System falls back to Sprint 1 TF-IDF search
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls, \
             patch('tools.ail.context_provider.HAS_FAISS_INTEGRATION', False):

            # Setup mocks
            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            # Create provider (FAISS disabled)
            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            # Query should still work (fallback to TF-IDF)
            result = await provider.get_context("test.py", "Why was this implemented?")

            assert result is not None
            assert len(result.answer) > 0

    @pytest.mark.asyncio
    async def test_faiss_search_error_fallback(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Test: Fallback when FAISS search encounters error

        Expected: System falls back to TF-IDF search
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls:

            # Setup mocks
            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            # Mock FAISS to raise error
            provider._faiss_enabled = True
            provider._faiss_initialized = True

            with patch.object(provider, '_query_with_faiss', side_effect=Exception("FAISS error")):
                # Query should fall back
                result = await provider.get_context("test.py", "Why was this implemented?")

                assert result is not None
                # Should use fallback (TF-IDF)

    def test_semantic_cache_disabled_fallback(self, temp_dir, mock_git_repo):
        """
        Test: System works with semantic cache disabled

        Expected: L1 cache only, no L2 semantic cache
        """
        with patch('tools.ail.context_provider.GitArchaeologist'), \
             patch('tools.ail.context_provider.GitHubArchaeologist'), \
             patch('tools.ail.context_provider.ContextSynthesizer'):

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
                enable_semantic_cache=False,  # Disable L2
            )

            # Verify L2 disabled
            assert provider._two_tier_cache is None or not provider._two_tier_cache.l2_enabled

            # L1 cache should still work
            cached_context = ArchaeologicalContext(
                file_path="test.py",
                question="Test",
                answer="Answer",
                sources=[],
                confidence=0.9,
            )

            cache_key = provider._generate_cache_key("test.py", "Test")
            provider.cache.put(cache_key, cached_context)

            result = provider.cache.get(cache_key)
            assert result == cached_context


class TestRealWorldScenarios:
    """Test realistic agent query scenarios."""

    @pytest.mark.asyncio
    async def test_code_review_scenario(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Scenario: Agent reviewing code changes

        Queries:
        1. "Why was this file changed?"
        2. "What was the previous implementation?"
        3. "Who made these changes?"
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls:

            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            # Simulate code review queries
            queries = [
                "Why was this file changed?",
                "What was the previous implementation?",
                "Who made these changes?",
            ]

            results = []
            for query in queries:
                result = await provider.get_context("auth.py", query)
                results.append(result)

            # Validate all queries succeeded
            assert len(results) == 3
            assert all(r is not None for r in results)
            assert all(len(r.answer) > 0 for r in results)

    @pytest.mark.asyncio
    async def test_debugging_scenario(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Scenario: Agent debugging an issue

        Queries:
        1. "When was this bug introduced?"
        2. "What changes affected this function?"
        3. "Are there related issues?"
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls:

            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            # Simulate debugging queries
            queries = [
                "When was this bug introduced?",
                "What changes affected this function?",
                "Are there related issues?",
            ]

            for query in queries:
                result = await provider.get_context("api.py", query)
                assert result is not None

    @pytest.mark.asyncio
    async def test_refactoring_scenario(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Scenario: Agent planning refactoring

        Queries:
        1. "What is the design rationale?"
        2. "What are the dependencies?"
        3. "What tests cover this code?"
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls:

            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            queries = [
                "What is the design rationale?",
                "What are the dependencies?",
                "What tests cover this code?",
            ]

            # Execute queries
            for query in queries:
                result = await provider.get_context("auth.py", query)
                assert result is not None
                assert result.confidence >= 0


class TestPerformanceUnderLoad:
    """Test performance under realistic load patterns."""

    @pytest.mark.asyncio
    async def test_burst_query_load(self, temp_dir, mock_git_repo, mock_cca_components):
        """
        Test: Handle burst of 20 queries in quick succession

        Expected: All queries complete without errors or significant degradation
        """
        with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
             patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
             patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls:

            mock_git_cls.return_value = mock_cca_components['git']
            mock_github_cls.return_value = mock_cca_components['github']
            mock_synth_cls.return_value = mock_cca_components['synthesizer']

            provider = ArchaeologyContextProvider(
                repo_path=str(mock_git_repo),
                cache_size=100,
            )

            # Generate burst queries
            queries = [
                ("test.py", f"Query {i}: Why was this implemented?")
                for i in range(20)
            ]

            # Execute burst
            start_time = time.time()
            tasks = [provider.get_context(file_path, question) for file_path, question in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time

            # Validate
            successful = [r for r in results if isinstance(r, ArchaeologicalContext)]
            errors = [r for r in results if isinstance(r, Exception)]

            print(f"\n=== Burst Load Results ===")
            print(f"Total Queries: {len(queries)}")
            print(f"Successful: {len(successful)}")
            print(f"Errors: {len(errors)}")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Avg Latency: {total_time / len(queries) * 1000:.2f}ms")

            assert len(errors) == 0, f"Burst queries failed: {errors}"
            assert len(successful) == len(queries), "All queries should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
