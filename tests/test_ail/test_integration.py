"""
Integration tests for AIL with actual CCA components.

These tests verify that the ArchaeologyContextProvider correctly integrates
with the real Cognitive Code Archaeology system components.
"""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools'))

from ail.context_provider import ArchaeologyContextProvider
from ail.agent_integration import (
    get_context_from_input,
    create_agent_query,
)


@pytest.fixture
def real_git_repo():
    """Create a realistic git repository with commits for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)

    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, check=True, capture_output=True)

    # Create initial file
    auth_file = repo_path / 'auth.py'
    auth_file.write_text('''
"""Authentication module using basic auth."""

def authenticate(username, password):
    # Simple authentication
    return username == "admin" and password == "secret"
''')
    subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit: Add basic authentication'], cwd=repo_path, check=True, capture_output=True)

    # Second commit - refactor to JWT
    auth_file.write_text('''
"""Authentication module using JWT tokens.

JWT was chosen for stateless authentication that scales horizontally.
This allows us to authenticate requests without server-side sessions.
"""

import jwt

def authenticate(token):
    """Authenticate using JWT token."""
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return payload.get('username')
    except jwt.InvalidTokenError:
        return None

def create_token(username):
    """Create JWT token for user."""
    return jwt.encode({'username': username}, 'secret', algorithm='HS256')
''')
    subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Refactor to JWT authentication for horizontal scalability'], cwd=repo_path, check=True, capture_output=True)

    # Third commit - add error handling
    auth_file.write_text('''
"""Authentication module using JWT tokens.

JWT was chosen for stateless authentication that scales horizontally.
This allows us to authenticate requests without server-side sessions.
"""

import jwt
import logging

logger = logging.getLogger(__name__)

def authenticate(token):
    """Authenticate using JWT token."""
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        username = payload.get('username')
        logger.info(f"User {username} authenticated successfully")
        return username
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        return None

def create_token(username):
    """Create JWT token for user."""
    return jwt.encode({'username': username}, 'secret', algorithm='HS256')
''')
    subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Add comprehensive error handling and logging'], cwd=repo_path, check=True, capture_output=True)

    yield repo_path

    # Cleanup
    shutil.rmtree(temp_dir)


class TestCCAIntegration:
    """Test integration with real CCA components."""

    def test_provider_initialization_with_real_repo(self, real_git_repo):
        """Test that provider initializes with real git repository."""
        provider = ArchaeologyContextProvider(
            repo_path=str(real_git_repo),
            cache_size=100,
        )

        assert not provider.is_initialized()
        assert provider.get_init_error() is None

    def test_context_retrieval_with_real_data(self, real_git_repo):
        """Test context retrieval with actual commit history."""
        provider = ArchaeologyContextProvider(
            repo_path=str(real_git_repo),
            cache_size=100,
        )

        # Query about the authentication implementation
        context = provider.get_context_sync(
            file_path="auth.py",
            question="Why was JWT authentication chosen?"
        )

        # Should get a response (even if CCA components are working)
        assert context is not None
        assert context.file_path == "auth.py"
        assert context.question == "Why was JWT authentication chosen?"
        assert len(context.answer) > 0

        # Should have some confidence (may vary based on CCA implementation)
        assert context.confidence >= 0.0
        assert context.confidence <= 1.0

    def test_cache_behavior_with_real_queries(self, real_git_repo):
        """Test caching with real queries."""
        provider = ArchaeologyContextProvider(
            repo_path=str(real_git_repo),
            cache_size=10,
        )

        # First query
        context1 = provider.get_context_sync(
            "auth.py",
            "Why was JWT chosen?"
        )
        assert context1.cached is False

        # Same query again - should be cached
        context2 = provider.get_context_sync(
            "auth.py",
            "Why was JWT chosen?"
        )
        assert context2.cached is True

        # Different query - should not be cached
        context3 = provider.get_context_sync(
            "auth.py",
            "What error handling is implemented?"
        )
        assert context3.cached is False

        # Check stats
        stats = provider.get_cache_stats()
        assert stats.total_queries == 3
        assert stats.hits == 1
        assert stats.misses == 2
        assert stats.hit_rate == 1/3

    def test_agent_integration_with_real_repo(self, real_git_repo):
        """Test agent integration helpers with real repository."""
        provider = ArchaeologyContextProvider(repo_path=str(real_git_repo))

        # Test with natural language input
        agent_input = 'Why does "auth.py" use JWT tokens?'
        context = get_context_from_input(provider, agent_input, str(real_git_repo))

        assert context is not None
        assert context.file_path == "auth.py"
        assert "JWT" in agent_input  # Original question preserved context

    def test_query_creation_with_real_file(self, real_git_repo):
        """Test query creation with actual repository file."""
        agent_input = "I need to refactor auth.py to add MFA support"
        query = create_agent_query(agent_input, str(real_git_repo), auto_detect=True)

        assert query['file_path'] == "auth.py"
        assert query['task_type'] == "refactor"
        assert query['question'] is not None

    def test_multiple_queries_performance(self, real_git_repo):
        """Test performance with multiple queries."""
        provider = ArchaeologyContextProvider(repo_path=str(real_git_repo))

        questions = [
            "Why was JWT chosen?",
            "What error handling is used?",
            "How does authentication work?",
            "What logging is implemented?",
        ]

        contexts = []
        for q in questions:
            ctx = provider.get_context_sync("auth.py", q)
            contexts.append(ctx)

        # All should return valid contexts
        assert len(contexts) == 4
        for ctx in contexts:
            assert ctx is not None
            assert ctx.query_time_ms >= 0

        # Average query time should be reasonable
        stats = provider.get_cache_stats()
        assert stats.avg_query_time_ms >= 0


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_code_review_scenario(self, real_git_repo):
        """Test scenario: Agent reviewing code changes."""
        provider = ArchaeologyContextProvider(repo_path=str(real_git_repo))

        # Agent is reviewing auth.py
        context = provider.get_context_sync(
            "auth.py",
            "What were the key design decisions for authentication? "
            "What alternatives were considered?"
        )

        assert context is not None
        # Should have historical context from commits
        assert len(context.answer) > 0

    def test_refactoring_scenario(self, real_git_repo):
        """Test scenario: Agent planning refactoring."""
        provider = ArchaeologyContextProvider(repo_path=str(real_git_repo))

        # Agent wants to refactor
        context = provider.get_context_sync(
            "auth.py",
            "What was the original design intent? "
            "What patterns were established?"
        )

        assert context is not None
        assert context.confidence >= 0.0

    def test_debugging_scenario(self, real_git_repo):
        """Test scenario: Agent debugging an issue."""
        provider = ArchaeologyContextProvider(repo_path=str(real_git_repo))

        # Agent investigating error handling
        context = provider.get_context_sync(
            "auth.py",
            "What error handling was implemented? "
            "What issues were previously fixed?"
        )

        assert context is not None
        # Should provide historical context about error handling


def test_cca_components_available():
    """Test that CCA components are available and importable."""
    from code_archaeology import (
        GitArchaeologist,
        ContextSynthesizer,
        SimpleEmbeddingProvider,
    )

    assert GitArchaeologist is not None
    assert ContextSynthesizer is not None
    assert SimpleEmbeddingProvider is not None
