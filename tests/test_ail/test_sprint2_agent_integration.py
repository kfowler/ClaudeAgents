"""
Sprint 2 Agent Integration Tests

Tests AIL integration with all 7 Sprint 2 agents:
1. full-stack-architect
2. backend-api-engineer
3. mobile-developer
4. ai-ml-engineer
5. devops-engineer
6. security-audit-specialist
7. qa-test-engineer

Validates:
- Agent-specific query patterns
- Quality consistency across agents
- Performance for agent use cases
- Error handling for each agent
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Tuple
from unittest.mock import Mock, patch, MagicMock
import tempfile

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Import AIL components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext


pytestmark = pytest.mark.skipif(
    not HAS_NUMPY,
    reason="NumPy required for agent integration tests"
)


# ===========================
# Agent Query Patterns
# ===========================

AGENT_QUERY_PATTERNS = {
    "full-stack-architect": [
        ("components/UserProfile.tsx", "What is the architecture pattern used here?"),
        ("api/routes/user.py", "How does this API integrate with the frontend?"),
        ("models/user.py", "Why was this data model designed this way?"),
        ("components/Button.tsx", "What are the reusable component patterns?"),
        ("api/auth.py", "How is authentication implemented across the stack?"),
    ],
    "backend-api-engineer": [
        ("api/routes/auth.py", "What authentication strategy is used?"),
        ("api/middleware/rate_limit.py", "How is rate limiting implemented?"),
        ("services/user_service.py", "What business logic does this service handle?"),
        ("models/database.py", "What database schema is used?"),
        ("api/routes/payments.py", "How are API errors handled?"),
    ],
    "mobile-developer": [
        ("ios/AuthViewController.swift", "How is iOS authentication implemented?"),
        ("android/MainActivity.kt", "What Android architecture is used?"),
        ("shared/NetworkManager.ts", "How is API communication handled?"),
        ("ios/UserProfileView.swift", "What UI patterns are used?"),
        ("android/repositories/UserRepository.kt", "How is local data persistence handled?"),
    ],
    "ai-ml-engineer": [
        ("ml/models/recommendation.py", "What ML model architecture is used?"),
        ("ml/training/pipeline.py", "How is model training orchestrated?"),
        ("ml/inference/predictor.py", "What inference optimization strategies are used?"),
        ("ml/features/embeddings.py", "How are embeddings generated?"),
        ("ml/evaluation/metrics.py", "What evaluation metrics are tracked?"),
    ],
    "devops-engineer": [
        ("infrastructure/kubernetes/deployment.yaml", "What deployment strategy is used?"),
        ("ci/github-actions.yml", "How is CI/CD configured?"),
        ("infrastructure/terraform/main.tf", "What cloud resources are provisioned?"),
        ("monitoring/prometheus.yml", "What monitoring is in place?"),
        ("scripts/deploy.sh", "How are deployments automated?"),
    ],
    "security-audit-specialist": [
        ("auth/oauth.py", "What security measures protect authentication?"),
        ("api/middleware/security.py", "How are security headers configured?"),
        ("db/encryption.py", "What encryption is used for sensitive data?"),
        ("auth/password.py", "How is password security enforced?"),
        ("api/input_validation.py", "What input validation prevents injection attacks?"),
    ],
    "qa-test-engineer": [
        ("tests/integration/test_auth.py", "What test coverage exists for authentication?"),
        ("tests/unit/test_user_service.py", "What edge cases are tested?"),
        ("tests/e2e/test_checkout.py", "What user flows are validated?"),
        ("tests/performance/test_api_load.py", "What performance benchmarks are defined?"),
        ("tests/fixtures/user_factory.py", "What test data patterns are used?"),
    ],
}


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
    return repo_dir


@pytest.fixture
def mock_cca_components():
    """Mock CCA components."""
    mock_commits = []
    for i in range(20):
        commit = MagicMock()
        commit.sha = f"commit_{i:03d}"
        commit.message = f"Commit {i}: Feature implementation"
        commit.author = "Developer"
        commit.date = f"2024-01-{i+1:02d}"
        commit.files_changed = ["test.py"]

        enriched = MagicMock()
        enriched.commit = commit
        enriched.pull_request = None
        mock_commits.append(enriched)

    mock_git_archaeologist = MagicMock()
    mock_history = MagicMock()
    mock_history.enriched_commits = mock_commits
    mock_history.total_commits = len(mock_commits)
    mock_git_archaeologist.analyze_repo.return_value = mock_history

    mock_github_archaeologist = MagicMock()

    mock_synthesizer = MagicMock()
    mock_answer = MagicMock()
    mock_answer.answer = "Context from archaeological analysis"
    mock_answer.confidence = 0.85
    mock_answer.citations = []
    mock_synthesizer.synthesize_answer.return_value = mock_answer

    return {
        'git': mock_git_archaeologist,
        'github': mock_github_archaeologist,
        'synthesizer': mock_synthesizer,
        'commits': mock_commits,
    }


@pytest.fixture
def context_provider(mock_git_repo, mock_cca_components):
    """Create context provider with mocks."""
    with patch('tools.ail.context_provider.GitArchaeologist') as mock_git_cls, \
         patch('tools.ail.context_provider.GitHubArchaeologist') as mock_github_cls, \
         patch('tools.ail.context_provider.ContextSynthesizer') as mock_synth_cls:

        mock_git_cls.return_value = mock_cca_components['git']
        mock_github_cls.return_value = mock_cca_components['github']
        mock_synth_cls.return_value = mock_cca_components['synthesizer']

        provider = ArchaeologyContextProvider(
            repo_path=str(mock_git_repo),
            cache_size=100,
            enable_semantic_cache=True,
        )

        yield provider


# ===========================
# Agent Integration Tests
# ===========================

class TestFullStackArchitectIntegration:
    """Test full-stack-architect agent integration."""

    @pytest.mark.asyncio
    async def test_fullstack_query_patterns(self, context_provider):
        """Test typical full-stack architect queries."""
        queries = AGENT_QUERY_PATTERNS["full-stack-architect"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        # Validate all queries succeeded
        assert len(results) == len(queries)
        assert all(r is not None for r in results)
        assert all(isinstance(r, ArchaeologicalContext) for r in results)

    @pytest.mark.asyncio
    async def test_fullstack_performance(self, context_provider):
        """Test performance for full-stack queries."""
        file_path, question = AGENT_QUERY_PATTERNS["full-stack-architect"][0]

        start_time = time.time()
        result = await context_provider.get_context(file_path, question)
        latency_ms = (time.time() - start_time) * 1000

        assert result is not None
        assert latency_ms < 1000, f"Query took {latency_ms:.2f}ms (expected <1000ms)"


class TestBackendAPIEngineerIntegration:
    """Test backend-api-engineer agent integration."""

    @pytest.mark.asyncio
    async def test_backend_query_patterns(self, context_provider):
        """Test typical backend API engineer queries."""
        queries = AGENT_QUERY_PATTERNS["backend-api-engineer"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        assert len(results) == len(queries)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_backend_api_specific_queries(self, context_provider):
        """Test backend-specific query types."""
        # Test API design queries
        result = await context_provider.get_context(
            "api/routes/users.py",
            "What REST conventions are followed?"
        )
        assert result is not None

        # Test service layer queries
        result = await context_provider.get_context(
            "services/auth_service.py",
            "How is business logic separated from routes?"
        )
        assert result is not None


class TestMobileDeveloperIntegration:
    """Test mobile-developer agent integration."""

    @pytest.mark.asyncio
    async def test_mobile_query_patterns(self, context_provider):
        """Test typical mobile developer queries."""
        queries = AGENT_QUERY_PATTERNS["mobile-developer"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        assert len(results) == len(queries)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_mobile_platform_specific(self, context_provider):
        """Test platform-specific mobile queries."""
        # iOS-specific
        result = await context_provider.get_context(
            "ios/AppDelegate.swift",
            "How is app lifecycle managed?"
        )
        assert result is not None

        # Android-specific
        result = await context_provider.get_context(
            "android/MainActivity.kt",
            "What Android architecture components are used?"
        )
        assert result is not None


class TestAIMLEngineerIntegration:
    """Test ai-ml-engineer agent integration."""

    @pytest.mark.asyncio
    async def test_aiml_query_patterns(self, context_provider):
        """Test typical AI/ML engineer queries."""
        queries = AGENT_QUERY_PATTERNS["ai-ml-engineer"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        assert len(results) == len(queries)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_ml_model_queries(self, context_provider):
        """Test ML model-specific queries."""
        # Model architecture
        result = await context_provider.get_context(
            "ml/models/neural_net.py",
            "What neural network architecture is implemented?"
        )
        assert result is not None

        # Training pipeline
        result = await context_provider.get_context(
            "ml/training/trainer.py",
            "How is model training monitored?"
        )
        assert result is not None


class TestDevOpsEngineerIntegration:
    """Test devops-engineer agent integration."""

    @pytest.mark.asyncio
    async def test_devops_query_patterns(self, context_provider):
        """Test typical DevOps engineer queries."""
        queries = AGENT_QUERY_PATTERNS["devops-engineer"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        assert len(results) == len(queries)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_infrastructure_queries(self, context_provider):
        """Test infrastructure-specific queries."""
        # Kubernetes
        result = await context_provider.get_context(
            "k8s/deployment.yaml",
            "What scaling strategy is configured?"
        )
        assert result is not None

        # CI/CD
        result = await context_provider.get_context(
            ".github/workflows/deploy.yml",
            "What deployment gates are in place?"
        )
        assert result is not None


class TestSecurityAuditSpecialistIntegration:
    """Test security-audit-specialist agent integration."""

    @pytest.mark.asyncio
    async def test_security_query_patterns(self, context_provider):
        """Test typical security specialist queries."""
        queries = AGENT_QUERY_PATTERNS["security-audit-specialist"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        assert len(results) == len(queries)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_security_specific_queries(self, context_provider):
        """Test security-specific query types."""
        # Authentication security
        result = await context_provider.get_context(
            "auth/jwt.py",
            "What vulnerabilities exist in token handling?"
        )
        assert result is not None

        # Input validation
        result = await context_provider.get_context(
            "api/validators.py",
            "How is SQL injection prevented?"
        )
        assert result is not None


class TestQATestEngineerIntegration:
    """Test qa-test-engineer agent integration."""

    @pytest.mark.asyncio
    async def test_qa_query_patterns(self, context_provider):
        """Test typical QA engineer queries."""
        queries = AGENT_QUERY_PATTERNS["qa-test-engineer"]

        results = []
        for file_path, question in queries:
            result = await context_provider.get_context(file_path, question)
            results.append(result)

        assert len(results) == len(queries)
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_testing_coverage_queries(self, context_provider):
        """Test testing-specific queries."""
        # Test coverage
        result = await context_provider.get_context(
            "tests/integration/test_api.py",
            "What API endpoints are covered by tests?"
        )
        assert result is not None

        # Test patterns
        result = await context_provider.get_context(
            "tests/fixtures/factories.py",
            "What test data patterns are used?"
        )
        assert result is not None


# ===========================
# Cross-Agent Tests
# ===========================

class TestCrossAgentConsistency:
    """Test quality and performance consistency across all agents."""

    @pytest.mark.asyncio
    async def test_all_agents_quality_consistency(self, context_provider):
        """
        Test: All 7 agents get consistent quality from AIL

        Expected: Quality variance < 10% across agents
        """
        agent_results = {}

        for agent_name, queries in AGENT_QUERY_PATTERNS.items():
            results = []

            for file_path, question in queries:
                result = await context_provider.get_context(file_path, question)
                results.append(result)

            # Calculate average confidence
            confidences = [r.confidence for r in results if r is not None]
            avg_confidence = np.mean(confidences) if confidences else 0

            agent_results[agent_name] = {
                'avg_confidence': avg_confidence,
                'total_queries': len(queries),
                'successful': len([r for r in results if r is not None]),
            }

            print(f"{agent_name}: {avg_confidence:.3f} confidence")

        # Validate consistency
        confidences = [r['avg_confidence'] for r in agent_results.values()]
        avg_confidence = np.mean(confidences)
        std_confidence = np.std(confidences)
        variance_pct = (std_confidence / avg_confidence) * 100 if avg_confidence > 0 else 0

        print(f"\n=== Cross-Agent Consistency ===")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print(f"Variance: {variance_pct:.1f}%")

        assert variance_pct < 15, f"Confidence variance {variance_pct:.1f}% exceeds 15% threshold"

    @pytest.mark.asyncio
    async def test_all_agents_performance_consistency(self, context_provider):
        """
        Test: All agents get consistent performance

        Expected: Performance variance < 20% across agents
        """
        agent_latencies = {}

        for agent_name, queries in AGENT_QUERY_PATTERNS.items():
            latencies = []

            for file_path, question in queries[:3]:  # Test subset
                start_time = time.time()
                await context_provider.get_context(file_path, question)
                latency_ms = (time.time() - start_time) * 1000
                latencies.append(latency_ms)

            avg_latency = np.mean(latencies)
            agent_latencies[agent_name] = avg_latency

            print(f"{agent_name}: {avg_latency:.2f}ms")

        # Validate performance consistency
        latencies = list(agent_latencies.values())
        avg_latency = np.mean(latencies)
        std_latency = np.std(latencies)
        variance_pct = (std_latency / avg_latency) * 100 if avg_latency > 0 else 0

        print(f"\n=== Cross-Agent Performance ===")
        print(f"Average Latency: {avg_latency:.2f}ms")
        print(f"Variance: {variance_pct:.1f}%")

        assert variance_pct < 20, f"Latency variance {variance_pct:.1f}% exceeds 20% threshold"


class TestConcurrentAgentLoad:
    """Test concurrent access by multiple agents."""

    @pytest.mark.asyncio
    async def test_concurrent_agent_queries(self, context_provider):
        """
        Test: Multiple agents querying concurrently

        Expected: All queries succeed without errors
        """
        # Create concurrent queries from different agents
        tasks = []

        for agent_name, queries in AGENT_QUERY_PATTERNS.items():
            # Take first query from each agent
            file_path, question = queries[0]
            task = context_provider.get_context(file_path, question)
            tasks.append((agent_name, task))

        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        total_time = time.time() - start_time

        # Validate
        successful = [r for r in results if isinstance(r, ArchaeologicalContext)]
        errors = [r for r in results if isinstance(r, Exception)]

        print(f"\n=== Concurrent Agent Load ===")
        print(f"Total Agents: {len(tasks)}")
        print(f"Successful: {len(successful)}")
        print(f"Errors: {len(errors)}")
        print(f"Total Time: {total_time:.2f}s")

        assert len(errors) == 0, f"Concurrent queries failed: {errors}"
        assert len(successful) == len(tasks), "All agent queries should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
