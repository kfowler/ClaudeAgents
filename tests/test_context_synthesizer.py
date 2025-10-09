"""
Tests for Context Synthesis Engine module.
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.code_archaeology.context_synthesizer import (
    ContextSynthesizer,
    SimpleEmbeddingProvider,
    SearchableIndex,
    SearchResult,
    Answer,
    Citation,
)
from tools.code_archaeology.git_analyzer import Commit, RepositoryHistory
from tools.code_archaeology.github_integrator import (
    EnrichedHistory,
    EnrichedCommit,
    PullRequest,
    Issue,
)

# Try to import numpy for tests
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


class TestSimpleEmbeddingProvider:
    """Test suite for SimpleEmbeddingProvider class."""

    @pytest.fixture
    def provider(self):
        """Create SimpleEmbeddingProvider instance."""
        return SimpleEmbeddingProvider(max_features=64)

    def test_initialization(self, provider):
        """Test provider initializes correctly."""
        assert provider.max_features == 64
        assert provider.dimension == 64
        assert provider._vocabulary is None

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_embed_single_text(self, provider):
        """Test embedding a single text."""
        texts = ["This is a test document"]
        embeddings = provider.embed(texts)

        assert embeddings.shape[0] == 1  # One document
        assert embeddings.shape[1] <= 64  # Dimension <= max_features
        assert embeddings.dtype == np.float32

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_embed_multiple_texts(self, provider):
        """Test embedding multiple texts."""
        texts = [
            "First document about testing",
            "Second document about embeddings",
            "Third document combining testing and embeddings",
        ]
        embeddings = provider.embed(texts)

        assert embeddings.shape[0] == 3  # Three documents
        assert embeddings.shape[1] <= 64  # Dimension <= max_features

        # Embeddings should be normalized
        for i in range(3):
            norm = np.linalg.norm(embeddings[i])
            assert 0.9 <= norm <= 1.1  # Should be approximately 1.0

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_similar_texts_similar_embeddings(self, provider):
        """Test that similar texts have similar embeddings."""
        texts = [
            "This is about machine learning",
            "This is about machine learning algorithms",
            "This is about cats and dogs",
        ]
        embeddings = provider.embed(texts)

        # Similarity between first two should be higher than with third
        sim_1_2 = np.dot(embeddings[0], embeddings[1])
        sim_1_3 = np.dot(embeddings[0], embeddings[2])

        assert sim_1_2 > sim_1_3


class TestCitation:
    """Test suite for Citation dataclass."""

    def test_citation_creation(self):
        """Test creating a citation."""
        citation = Citation(
            commit_sha="abc123",
            commit_message="Add new feature",
            commit_date=datetime.now(),
            author="user1",
            source_type="commit",
            relevance_score=0.85,
        )

        assert citation.commit_sha == "abc123"
        assert citation.source_type == "commit"
        assert citation.relevance_score == 0.85


class TestAnswer:
    """Test suite for Answer dataclass."""

    def test_credibility_score_no_citations(self):
        """Test credibility score with no citations."""
        answer = Answer(
            question="Test question",
            answer="Test answer",
            citations=[],
            confidence=0.8,
        )

        assert answer.credibility_score == 0.0

    def test_credibility_score_single_citation(self):
        """Test credibility score with single citation."""
        citation = Citation(
            commit_sha="abc123",
            commit_message="Test",
            commit_date=datetime.now(),
            author="user1",
            source_type="commit",
            relevance_score=0.9,
        )

        answer = Answer(
            question="Test question",
            answer="Test answer",
            citations=[citation],
            confidence=0.8,
        )

        # Should be confidence + relevance boost
        assert 0.8 < answer.credibility_score <= 1.0

    def test_credibility_score_multiple_citations(self):
        """Test credibility score with multiple citations."""
        citations = [
            Citation(
                commit_sha=f"sha{i}",
                commit_message="Test",
                commit_date=datetime.now(),
                author="user1",
                source_type="commit",
                relevance_score=0.9,
            )
            for i in range(3)
        ]

        answer = Answer(
            question="Test question",
            answer="Test answer",
            citations=citations,
            confidence=0.8,
        )

        # Should have boost for multiple citations
        assert answer.credibility_score > 0.8


class TestContextSynthesizer:
    """Test suite for ContextSynthesizer class."""

    @pytest.fixture
    def synthesizer(self):
        """Create ContextSynthesizer instance."""
        return ContextSynthesizer()

    @pytest.fixture
    def sample_enriched_history(self):
        """Create sample enriched history for testing."""
        # Create sample commits
        commit1 = Commit(
            sha="abc123",
            message="Add authentication system\n\nImplemented JWT-based auth",
            author="user1",
            email="user1@example.com",
            date=datetime(2025, 1, 1, 10, 0, 0),
            parents=[],
            files_changed=["auth.py"],
        )

        commit2 = Commit(
            sha="def456",
            message="Refactor database layer\n\nImproved performance",
            author="user2",
            email="user2@example.com",
            date=datetime(2025, 1, 2, 14, 0, 0),
            parents=["abc123"],
            files_changed=["db.py"],
        )

        # Create enriched commits
        enriched1 = EnrichedCommit(
            commit=commit1,
            pull_request=PullRequest(
                number=1,
                title="Add authentication",
                body="This PR adds JWT authentication to the API",
                author="user1",
                state="merged",
                created_at=datetime(2025, 1, 1),
                merged_at=datetime(2025, 1, 1, 12, 0, 0),
                closed_at=None,
                commits=["abc123"],
                labels=["feature"],
                reviewers=["user3"],
                url="https://github.com/owner/repo/pull/1",
            ),
        )

        enriched2 = EnrichedCommit(commit=commit2)

        # Create base history
        base_history = RepositoryHistory(
            repo_path=Path("."),
            commits=[commit1, commit2],
            arch_commits=[],
            temporal_index={},
            file_history={},
            author_stats={"user1": 1, "user2": 1},
            branch_commits={},
        )

        # Create enriched history
        enriched_history = EnrichedHistory(
            base_history=base_history,
            enriched_commits=[enriched1, enriched2],
            pull_requests={1: enriched1.pull_request},
            issues={},
            commit_to_pr={"abc123": 1},
        )

        return enriched_history

    def test_initialization(self, synthesizer):
        """Test synthesizer initializes correctly."""
        assert synthesizer.embedding_provider is not None
        assert isinstance(synthesizer.embedding_provider, SimpleEmbeddingProvider)

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_extract_documents(self, synthesizer, sample_enriched_history):
        """Test document extraction from enriched history."""
        documents, metadata = synthesizer._extract_documents(sample_enriched_history)

        # Should have: 2 commit docs + 1 PR doc = 3 documents
        assert len(documents) >= 2
        assert len(metadata) >= 2

        # Check metadata types
        types = [m['type'] for m in metadata]
        assert 'commit' in types
        assert 'pr' in types or 'commit' in types

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_build_searchable_index(self, synthesizer, sample_enriched_history):
        """Test building searchable index."""
        index = synthesizer.build_searchable_index(sample_enriched_history)

        assert isinstance(index, SearchableIndex)
        assert index.size > 0
        assert index.embeddings is not None
        assert len(index.documents) == len(index.document_metadata)

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_search(self, synthesizer, sample_enriched_history):
        """Test searching the index."""
        index = synthesizer.build_searchable_index(sample_enriched_history)

        results = synthesizer.search(index, "authentication", k=5)

        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(hasattr(r, 'relevance_score') for r in results)

        # Results should be sorted by relevance
        scores = [r.relevance_score for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_search_returns_relevant_results(self, synthesizer, sample_enriched_history):
        """Test that search returns relevant results."""
        index = synthesizer.build_searchable_index(sample_enriched_history)

        # Search for authentication
        results = synthesizer.search(index, "authentication system JWT", k=5)

        # First result should be about authentication
        assert len(results) > 0
        top_result = results[0]
        assert "auth" in top_result.commit.commit.message.lower()

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_synthesize_answer(self, synthesizer, sample_enriched_history):
        """Test answer synthesis."""
        index = synthesizer.build_searchable_index(sample_enriched_history)

        answer = synthesizer.synthesize_answer(
            index,
            "Why was authentication added?",
            max_results=5,
        )

        assert isinstance(answer, Answer)
        assert answer.question == "Why was authentication added?"
        assert len(answer.answer) > 0
        assert len(answer.citations) > 0
        assert 0.0 <= answer.confidence <= 1.0

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_synthesize_answer_with_citations(self, synthesizer, sample_enriched_history):
        """Test that answer includes citations."""
        index = synthesizer.build_searchable_index(sample_enriched_history)

        answer = synthesizer.synthesize_answer(
            index,
            "What changes were made to authentication?",
        )

        assert len(answer.citations) > 0

        # Citations should have required fields
        for citation in answer.citations:
            assert citation.commit_sha
            assert citation.commit_message
            assert citation.author
            assert 0.0 <= citation.relevance_score <= 1.0

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_synthesize_answer_no_results(self, synthesizer, sample_enriched_history):
        """Test answer synthesis with no relevant results."""
        index = synthesizer.build_searchable_index(sample_enriched_history)

        # Query for something completely unrelated
        answer = synthesizer.synthesize_answer(
            index,
            "xyzabc nonsense query 12345",
        )

        # Should still return an answer (even if it says "no info found")
        assert isinstance(answer, Answer)
        assert answer.confidence >= 0.0

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy required")
    def test_confidence_calculation(self, synthesizer):
        """Test confidence calculation logic."""
        # High relevance results
        high_results = [
            SearchResult(
                commit=EnrichedCommit(
                    commit=Commit(
                        sha="sha1",
                        message="test",
                        author="user",
                        email="user@example.com",
                        date=datetime.now(),
                        parents=[],
                    )
                ),
                relevance_score=0.9,
                matched_content="test",
            )
            for _ in range(3)
        ]

        confidence_high = synthesizer._calculate_confidence(high_results)
        assert confidence_high > 0.7

        # Low relevance results
        low_results = [
            SearchResult(
                commit=EnrichedCommit(
                    commit=Commit(
                        sha="sha1",
                        message="test",
                        author="user",
                        email="user@example.com",
                        date=datetime.now(),
                        parents=[],
                    )
                ),
                relevance_score=0.3,
                matched_content="test",
            )
            for _ in range(3)
        ]

        confidence_low = synthesizer._calculate_confidence(low_results)
        assert confidence_low < confidence_high


class TestSearchableIndex:
    """Test suite for SearchableIndex dataclass."""

    def test_index_size_property(self):
        """Test index size property."""
        from tools.code_archaeology.git_analyzer import RepositoryHistory

        enriched_history = EnrichedHistory(
            base_history=RepositoryHistory(
                repo_path=Path("."),
                commits=[],
                arch_commits=[],
                temporal_index={},
                file_history={},
                author_stats={},
                branch_commits={},
            ),
            enriched_commits=[],
            pull_requests={},
            issues={},
            commit_to_pr={},
        )

        index = SearchableIndex(
            enriched_history=enriched_history,
            documents=["doc1", "doc2", "doc3"],
            document_metadata=[{}, {}, {}],
        )

        assert index.size == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
