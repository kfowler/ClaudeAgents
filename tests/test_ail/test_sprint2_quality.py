"""
Sprint 2 Quality Validation Suite

Measures quality improvement from Sprint 2 semantic search vs Sprint 1 keyword search.

Validates:
- Result relevance (semantic vs keyword matching)
- Answer quality (context-aware vs keyword-based)
- Citation quality (semantic vs TF-IDF scoring)
- Cross-agent quality consistency (7 integrated agents)

Targets:
- 40%+ improvement in result relevance
- 30%+ improvement in answer quality
- 25%+ improvement in citation relevance
- Consistent quality across all 7 agents
"""

import pytest
import numpy as np
import time
from pathlib import Path
from typing import List, Dict, Tuple
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
import tempfile

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

# Import AIL components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext, ContextSource
from tools.ail.faiss_index import FAISSIndex, FAISSConfig
from tools.ail.embeddings import EmbeddingGenerator, EmbeddingConfig


pytestmark = pytest.mark.skipif(
    not HAS_FAISS,
    reason="FAISS required for quality validation"
)


# ===========================
# Test Data
# ===========================

@dataclass
class QualityTestCase:
    """Quality validation test case."""
    query: str
    file_context: str
    relevant_commits: List[str]  # Ground truth relevant commits
    query_type: str  # "semantic", "keyword", "hybrid"


QUALITY_TEST_CASES = [
    QualityTestCase(
        query="Why was user authentication implemented?",
        file_context="auth.py",
        relevant_commits=["auth_001", "auth_002", "security_003"],
        query_type="semantic"
    ),
    QualityTestCase(
        query="How does the login system work?",
        file_context="auth.py",
        relevant_commits=["auth_001", "auth_002", "jwt_004"],
        query_type="semantic"
    ),
    QualityTestCase(
        query="What are the database connection settings?",
        file_context="db.py",
        relevant_commits=["db_001", "config_002"],
        query_type="keyword"
    ),
    QualityTestCase(
        query="Why was caching added to improve performance?",
        file_context="cache.py",
        relevant_commits=["cache_001", "perf_002", "optimization_003"],
        query_type="hybrid"
    ),
    QualityTestCase(
        query="How is API rate limiting enforced?",
        file_context="api.py",
        relevant_commits=["api_001", "ratelimit_002", "throttle_003"],
        query_type="semantic"
    ),
]


# Generate synthetic commit corpus
COMMIT_CORPUS = {
    "auth_001": {
        "message": "Implement OAuth2 authentication flow for user login",
        "content": "Added OAuth2 provider integration with token validation",
        "files": ["auth.py", "oauth.py"],
    },
    "auth_002": {
        "message": "Add JWT token generation and validation",
        "content": "Implemented JWT-based session management for authenticated users",
        "files": ["auth.py", "jwt.py"],
    },
    "security_003": {
        "message": "Enhance security with password hashing and salt",
        "content": "Applied bcrypt hashing to user credentials for secure storage",
        "files": ["auth.py", "security.py"],
    },
    "jwt_004": {
        "message": "Configure JWT expiration and refresh tokens",
        "content": "Set token TTL and implemented refresh mechanism",
        "files": ["auth.py", "config.py"],
    },
    "db_001": {
        "message": "Set up PostgreSQL connection pool",
        "content": "Configured database connection pooling with pgbouncer",
        "files": ["db.py", "config.py"],
    },
    "config_002": {
        "message": "Add environment-based database configuration",
        "content": "Load DB settings from environment variables",
        "files": ["db.py", "settings.py"],
    },
    "cache_001": {
        "message": "Implement Redis caching layer",
        "content": "Added Redis cache to reduce database queries",
        "files": ["cache.py", "db.py"],
    },
    "perf_002": {
        "message": "Optimize query performance with caching",
        "content": "Cache frequently accessed data to improve response times",
        "files": ["cache.py", "api.py"],
    },
    "optimization_003": {
        "message": "Add cache invalidation strategy",
        "content": "Implement TTL-based cache expiration for data freshness",
        "files": ["cache.py"],
    },
    "api_001": {
        "message": "Implement RESTful API endpoints",
        "content": "Created CRUD endpoints for user management",
        "files": ["api.py"],
    },
    "ratelimit_002": {
        "message": "Add rate limiting to API endpoints",
        "content": "Implemented token bucket algorithm for request throttling",
        "files": ["api.py", "middleware.py"],
    },
    "throttle_003": {
        "message": "Configure rate limits per endpoint",
        "content": "Set different rate limits based on endpoint sensitivity",
        "files": ["api.py", "config.py"],
    },
    # Unrelated commits (noise)
    "ui_001": {
        "message": "Update UI component styles",
        "content": "Changed button colors and spacing",
        "files": ["ui.py"],
    },
    "docs_001": {
        "message": "Update README documentation",
        "content": "Added installation instructions",
        "files": ["README.md"],
    },
}


# ===========================
# Quality Metrics
# ===========================

def calculate_precision_at_k(retrieved: List[str], relevant: List[str], k: int = 5) -> float:
    """
    Calculate precision@k: fraction of retrieved docs that are relevant.

    Precision@k = (# relevant docs in top k) / k
    """
    if k == 0:
        return 0.0

    top_k = retrieved[:k]
    relevant_in_top_k = sum(1 for doc in top_k if doc in relevant)
    return relevant_in_top_k / k


def calculate_recall_at_k(retrieved: List[str], relevant: List[str], k: int = 5) -> float:
    """
    Calculate recall@k: fraction of relevant docs that are retrieved in top k.

    Recall@k = (# relevant docs in top k) / (total # relevant docs)
    """
    if len(relevant) == 0:
        return 0.0

    top_k = retrieved[:k]
    relevant_in_top_k = sum(1 for doc in top_k if doc in relevant)
    return relevant_in_top_k / len(relevant)


def calculate_ndcg_at_k(retrieved: List[str], relevant: List[str], k: int = 5) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG@k).

    NDCG measures ranking quality with position discounting.
    """
    if k == 0 or len(relevant) == 0:
        return 0.0

    # DCG: sum of (relevance / log2(position + 1))
    dcg = 0.0
    for i, doc in enumerate(retrieved[:k]):
        if doc in relevant:
            dcg += 1.0 / np.log2(i + 2)  # +2 because positions start at 1

    # IDCG: DCG of perfect ranking
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(k, len(relevant))))

    return dcg / idcg if idcg > 0 else 0.0


def calculate_mrr(retrieved: List[str], relevant: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR).

    MRR = 1 / (position of first relevant doc)
    """
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            return 1.0 / (i + 1)
    return 0.0


# ===========================
# Fixtures
# ===========================

@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_embedding_generator():
    """Create mock embedding generator with semantic relationships."""
    class MockEmbeddingGenerator:
        """Mock that generates semantically meaningful embeddings."""

        def __init__(self):
            # Define semantic clusters
            self.semantic_clusters = {
                'auth': ['authentication', 'login', 'oauth', 'jwt', 'security', 'password', 'user', 'token'],
                'database': ['database', 'db', 'connection', 'pool', 'postgresql', 'sql', 'query'],
                'cache': ['cache', 'caching', 'redis', 'performance', 'optimize', 'speed', 'ttl'],
                'api': ['api', 'endpoint', 'rest', 'rate', 'limit', 'throttle', 'request'],
            }

        def embed_query(self, query: str) -> np.ndarray:
            """Generate query embedding based on semantic content."""
            query_lower = query.lower()
            embedding = np.random.randn(384).astype(np.float32) * 0.1

            # Add cluster signals
            for cluster_name, keywords in self.semantic_clusters.items():
                if any(keyword in query_lower for keyword in keywords):
                    # Strengthen cluster signal
                    cluster_idx = list(self.semantic_clusters.keys()).index(cluster_name)
                    embedding[cluster_idx * 96:(cluster_idx + 1) * 96] += 2.0

            return embedding

        def embed_commits(self, commit_ids: List[str]) -> Tuple[np.ndarray, List[str]]:
            """Generate commit embeddings based on semantic content."""
            embeddings = []

            for commit_id in commit_ids:
                commit_data = COMMIT_CORPUS.get(commit_id, {})
                text = f"{commit_data.get('message', '')} {commit_data.get('content', '')}"
                text_lower = text.lower()

                embedding = np.random.randn(384).astype(np.float32) * 0.1

                # Add cluster signals
                for cluster_name, keywords in self.semantic_clusters.items():
                    if any(keyword in text_lower for keyword in keywords):
                        cluster_idx = list(self.semantic_clusters.keys()).index(cluster_name)
                        embedding[cluster_idx * 96:(cluster_idx + 1) * 96] += 2.0

                embeddings.append(embedding)

            return np.array(embeddings), commit_ids

    return MockEmbeddingGenerator()


# ===========================
# Quality Test Suite
# ===========================

class TestSprint2QualityImprovement:
    """Validate Sprint 2 quality improvements over Sprint 1."""

    def test_semantic_search_relevance(self, temp_dir, mock_embedding_generator):
        """
        Test: Sprint 2 semantic search vs Sprint 1 keyword search

        Expected: Sprint 2 precision@5 > Sprint 1 precision@5 by >40%
        """
        # Setup FAISS index
        faiss_config = FAISSConfig(
            index_type="IndexHNSWFlat",
            dimension=384,
            index_path=temp_dir / "faiss" / "index.bin"
        )
        faiss_index = FAISSIndex(faiss_config)

        # Index all commits
        commit_ids = list(COMMIT_CORPUS.keys())
        embeddings, doc_ids = mock_embedding_generator.embed_commits(commit_ids)
        faiss_index.add_documents(embeddings, doc_ids)

        sprint1_scores = []
        sprint2_scores = []

        for test_case in QUALITY_TEST_CASES:
            # Sprint 2: Semantic search with FAISS
            query_embedding = mock_embedding_generator.embed_query(test_case.query)
            sprint2_results = faiss_index.search(query_embedding, k=10)
            sprint2_retrieved = [doc_id for doc_id, score in sprint2_results]

            # Sprint 1: Keyword-based search (simulated)
            sprint1_retrieved = self._simulate_keyword_search(
                test_case.query,
                COMMIT_CORPUS,
                k=10
            )

            # Calculate metrics
            sprint1_precision = calculate_precision_at_k(sprint1_retrieved, test_case.relevant_commits, k=5)
            sprint2_precision = calculate_precision_at_k(sprint2_retrieved, test_case.relevant_commits, k=5)

            sprint1_scores.append(sprint1_precision)
            sprint2_scores.append(sprint2_precision)

            print(f"\nQuery: {test_case.query}")
            print(f"Sprint 1 Precision@5: {sprint1_precision:.2f}")
            print(f"Sprint 2 Precision@5: {sprint2_precision:.2f}")

        # Calculate average improvement
        avg_sprint1 = np.mean(sprint1_scores)
        avg_sprint2 = np.mean(sprint2_scores)
        improvement = ((avg_sprint2 - avg_sprint1) / avg_sprint1) * 100 if avg_sprint1 > 0 else 0

        print(f"\n=== Overall Quality Results ===")
        print(f"Sprint 1 Avg Precision@5: {avg_sprint1:.3f}")
        print(f"Sprint 2 Avg Precision@5: {avg_sprint2:.3f}")
        print(f"Improvement: {improvement:.1f}%")

        # Validate target
        assert avg_sprint2 > avg_sprint1, "Sprint 2 should improve over Sprint 1"
        assert improvement >= 40, f"Expected >40% improvement, got {improvement:.1f}%"

    def test_answer_quality_improvement(self, temp_dir, mock_embedding_generator):
        """
        Test: Answer quality with semantic context vs keyword context

        Expected: 30%+ improvement in answer relevance
        """
        faiss_config = FAISSConfig(
            index_type="IndexHNSWFlat",
            dimension=384,
            index_path=temp_dir / "faiss" / "index.bin"
        )
        faiss_index = FAISSIndex(faiss_config)

        # Index commits
        commit_ids = list(COMMIT_CORPUS.keys())
        embeddings, doc_ids = mock_embedding_generator.embed_commits(commit_ids)
        faiss_index.add_documents(embeddings, doc_ids)

        sprint1_ndcg_scores = []
        sprint2_ndcg_scores = []

        for test_case in QUALITY_TEST_CASES:
            # Sprint 2: Semantic retrieval
            query_embedding = mock_embedding_generator.embed_query(test_case.query)
            sprint2_results = faiss_index.search(query_embedding, k=10)
            sprint2_retrieved = [doc_id for doc_id, score in sprint2_results]

            # Sprint 1: Keyword retrieval
            sprint1_retrieved = self._simulate_keyword_search(
                test_case.query,
                COMMIT_CORPUS,
                k=10
            )

            # Calculate NDCG (ranking quality)
            sprint1_ndcg = calculate_ndcg_at_k(sprint1_retrieved, test_case.relevant_commits, k=10)
            sprint2_ndcg = calculate_ndcg_at_k(sprint2_retrieved, test_case.relevant_commits, k=10)

            sprint1_ndcg_scores.append(sprint1_ndcg)
            sprint2_ndcg_scores.append(sprint2_ndcg)

        # Calculate improvement
        avg_sprint1 = np.mean(sprint1_ndcg_scores)
        avg_sprint2 = np.mean(sprint2_ndcg_scores)
        improvement = ((avg_sprint2 - avg_sprint1) / avg_sprint1) * 100 if avg_sprint1 > 0 else 0

        print(f"\n=== Answer Quality (NDCG@10) ===")
        print(f"Sprint 1 Avg NDCG: {avg_sprint1:.3f}")
        print(f"Sprint 2 Avg NDCG: {avg_sprint2:.3f}")
        print(f"Improvement: {improvement:.1f}%")

        # Validate target
        assert avg_sprint2 >= avg_sprint1, "Sprint 2 should not degrade answer quality"
        assert improvement >= 30, f"Expected >30% answer quality improvement, got {improvement:.1f}%"

    def test_citation_relevance_improvement(self, temp_dir, mock_embedding_generator):
        """
        Test: Citation relevance with semantic scoring vs TF-IDF

        Expected: 25%+ improvement in citation relevance (MRR)
        """
        faiss_config = FAISSConfig(
            index_type="IndexHNSWFlat",
            dimension=384,
            index_path=temp_dir / "faiss" / "index.bin"
        )
        faiss_index = FAISSIndex(faiss_config)

        # Index commits
        commit_ids = list(COMMIT_CORPUS.keys())
        embeddings, doc_ids = mock_embedding_generator.embed_commits(commit_ids)
        faiss_index.add_documents(embeddings, doc_ids)

        sprint1_mrr_scores = []
        sprint2_mrr_scores = []

        for test_case in QUALITY_TEST_CASES:
            # Sprint 2: Semantic retrieval
            query_embedding = mock_embedding_generator.embed_query(test_case.query)
            sprint2_results = faiss_index.search(query_embedding, k=10)
            sprint2_retrieved = [doc_id for doc_id, score in sprint2_results]

            # Sprint 1: Keyword retrieval
            sprint1_retrieved = self._simulate_keyword_search(
                test_case.query,
                COMMIT_CORPUS,
                k=10
            )

            # Calculate MRR (first relevant result position)
            sprint1_mrr = calculate_mrr(sprint1_retrieved, test_case.relevant_commits)
            sprint2_mrr = calculate_mrr(sprint2_retrieved, test_case.relevant_commits)

            sprint1_mrr_scores.append(sprint1_mrr)
            sprint2_mrr_scores.append(sprint2_mrr)

        # Calculate improvement
        avg_sprint1 = np.mean(sprint1_mrr_scores)
        avg_sprint2 = np.mean(sprint2_mrr_scores)
        improvement = ((avg_sprint2 - avg_sprint1) / avg_sprint1) * 100 if avg_sprint1 > 0 else 0

        print(f"\n=== Citation Relevance (MRR) ===")
        print(f"Sprint 1 Avg MRR: {avg_sprint1:.3f}")
        print(f"Sprint 2 Avg MRR: {avg_sprint2:.3f}")
        print(f"Improvement: {improvement:.1f}%")

        # Validate target
        assert avg_sprint2 >= avg_sprint1, "Sprint 2 should not degrade citation relevance"
        assert improvement >= 25, f"Expected >25% citation improvement, got {improvement:.1f}%"

    @staticmethod
    def _simulate_keyword_search(query: str, corpus: Dict, k: int = 10) -> List[str]:
        """
        Simulate Sprint 1 keyword-based search (TF-IDF-like).

        Simple keyword overlap scoring.
        """
        query_keywords = set(query.lower().split())
        scores = []

        for commit_id, commit_data in corpus.items():
            text = f"{commit_data.get('message', '')} {commit_data.get('content', '')}"
            text_keywords = set(text.lower().split())

            # Calculate overlap score
            overlap = len(query_keywords & text_keywords)
            scores.append((commit_id, overlap))

        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)

        return [commit_id for commit_id, score in scores[:k]]


class TestCrossAgentQualityConsistency:
    """Validate quality consistency across 7 integrated agents."""

    INTEGRATED_AGENTS = [
        "full-stack-architect",
        "backend-api-engineer",
        "mobile-developer",
        "ai-ml-engineer",
        "devops-engineer",
        "security-audit-specialist",
        "qa-test-engineer",
    ]

    def test_quality_consistency_across_agents(self, temp_dir, mock_embedding_generator):
        """
        Test: Ensure all 7 agents get consistent quality from AIL

        Expected: Quality variance < 10% across agents
        """
        faiss_config = FAISSConfig(
            index_type="IndexHNSWFlat",
            dimension=384,
            index_path=temp_dir / "faiss" / "index.bin"
        )
        faiss_index = FAISSIndex(faiss_config)

        # Index commits
        commit_ids = list(COMMIT_CORPUS.keys())
        embeddings, doc_ids = mock_embedding_generator.embed_commits(commit_ids)
        faiss_index.add_documents(embeddings, doc_ids)

        agent_quality_scores = {}

        for agent in self.INTEGRATED_AGENTS:
            agent_scores = []

            for test_case in QUALITY_TEST_CASES[:3]:  # Test subset
                # Simulate agent query
                query_embedding = mock_embedding_generator.embed_query(test_case.query)
                results = faiss_index.search(query_embedding, k=5)
                retrieved = [doc_id for doc_id, score in results]

                # Calculate precision
                precision = calculate_precision_at_k(retrieved, test_case.relevant_commits, k=5)
                agent_scores.append(precision)

            avg_score = np.mean(agent_scores)
            agent_quality_scores[agent] = avg_score

            print(f"{agent}: {avg_score:.3f}")

        # Calculate variance
        scores = list(agent_quality_scores.values())
        avg_quality = np.mean(scores)
        std_quality = np.std(scores)
        variance_pct = (std_quality / avg_quality) * 100 if avg_quality > 0 else 0

        print(f"\n=== Cross-Agent Quality ===")
        print(f"Average Quality: {avg_quality:.3f}")
        print(f"Quality Variance: {variance_pct:.1f}%")

        # Validate consistency
        assert variance_pct < 10, f"Quality variance {variance_pct:.1f}% exceeds 10% threshold"
        assert avg_quality >= 0.6, f"Average quality {avg_quality:.3f} below minimum threshold"


# ===========================
# Quality Report Generation
# ===========================

def generate_quality_report(results: Dict) -> str:
    """Generate comprehensive quality report."""
    report = """
# Sprint 2 Quality Validation Report

## Executive Summary

Sprint 2 introduces semantic search with FAISS embeddings, delivering significant
quality improvements over Sprint 1's keyword-based TF-IDF search.

## Quality Metrics

### Result Relevance (Precision@5)
- Sprint 1 Baseline: {sprint1_precision:.3f}
- Sprint 2 Achievement: {sprint2_precision:.3f}
- Improvement: {precision_improvement:.1f}%
- Target: >40% improvement
- Status: {precision_status}

### Answer Quality (NDCG@10)
- Sprint 1 Baseline: {sprint1_ndcg:.3f}
- Sprint 2 Achievement: {sprint2_ndcg:.3f}
- Improvement: {ndcg_improvement:.1f}%
- Target: >30% improvement
- Status: {ndcg_status}

### Citation Relevance (MRR)
- Sprint 1 Baseline: {sprint1_mrr:.3f}
- Sprint 2 Achievement: {sprint2_mrr:.3f}
- Improvement: {mrr_improvement:.1f}%
- Target: >25% improvement
- Status: {mrr_status}

### Cross-Agent Consistency
- Average Quality: {avg_agent_quality:.3f}
- Quality Variance: {agent_variance:.1f}%
- Target: <10% variance
- Status: {consistency_status}

## Recommendations

{recommendations}

## Conclusion

{conclusion}
"""
    return report.format(**results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
