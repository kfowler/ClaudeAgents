"""
Tests for GitHub Integration module.
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.code_archaeology.github_integrator import (
    GitHubArchaeologist,
    GitHubAPIClient,
    PullRequest,
    Issue,
    PRComment,
    ReviewComment,
    IssueComment,
    EnrichedCommit,
)
from tools.code_archaeology.git_analyzer import Commit


class TestGitHubArchaeologist:
    """Test suite for GitHubArchaeologist class."""

    def test_parse_repo_url_https(self):
        """Test parsing HTTPS GitHub URLs."""
        owner, repo = GitHubArchaeologist.parse_repo_url(
            "https://github.com/anthropics/claude-code"
        )
        assert owner == "anthropics"
        assert repo == "claude-code"

        owner, repo = GitHubArchaeologist.parse_repo_url(
            "https://github.com/owner/repo.git"
        )
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_repo_url_ssh(self):
        """Test parsing SSH GitHub URLs."""
        owner, repo = GitHubArchaeologist.parse_repo_url(
            "git@github.com:anthropics/claude-code.git"
        )
        assert owner == "anthropics"
        assert repo == "claude-code"

        owner, repo = GitHubArchaeologist.parse_repo_url(
            "git@github.com:owner/repo"
        )
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_repo_url_invalid(self):
        """Test that invalid URLs raise ValueError."""
        with pytest.raises(ValueError):
            GitHubArchaeologist.parse_repo_url("not-a-url")

        with pytest.raises(ValueError):
            GitHubArchaeologist.parse_repo_url("https://gitlab.com/owner/repo")

    def test_extract_issue_numbers(self):
        """Test extracting issue numbers from text."""
        archaeologist = GitHubArchaeologist("owner", "repo")

        # Single reference
        numbers = archaeologist._extract_issue_numbers("Fixes #123")
        assert numbers == {123}

        # Multiple references
        numbers = archaeologist._extract_issue_numbers("Related to #42 and #123, closes #456")
        assert numbers == {42, 123, 456}

        # No references
        numbers = archaeologist._extract_issue_numbers("No issues here")
        assert numbers == set()

        # None input
        numbers = archaeologist._extract_issue_numbers(None)
        assert numbers == set()


class TestPullRequest:
    """Test suite for PullRequest dataclass."""

    def test_is_merged_property(self):
        """Test is_merged property."""
        # Merged PR (state = merged)
        pr = PullRequest(
            number=1,
            title="Test PR",
            body="Description",
            author="user1",
            state="merged",
            created_at=datetime.now(),
            merged_at=datetime.now(),
            closed_at=None,
            commits=[],
            labels=[],
            reviewers=[],
        )
        assert pr.is_merged is True

        # Merged PR (merged_at set)
        pr = PullRequest(
            number=2,
            title="Test PR",
            body="Description",
            author="user1",
            state="closed",
            created_at=datetime.now(),
            merged_at=datetime.now(),
            closed_at=datetime.now(),
            commits=[],
            labels=[],
            reviewers=[],
        )
        assert pr.is_merged is True

        # Closed but not merged
        pr = PullRequest(
            number=3,
            title="Test PR",
            body="Description",
            author="user1",
            state="closed",
            created_at=datetime.now(),
            merged_at=None,
            closed_at=datetime.now(),
            commits=[],
            labels=[],
            reviewers=[],
        )
        assert pr.is_merged is False

    def test_discussion_summary(self):
        """Test discussion summary aggregation."""
        pr = PullRequest(
            number=1,
            title="Test PR",
            body="PR description",
            author="user1",
            state="open",
            created_at=datetime.now(),
            merged_at=None,
            closed_at=None,
            commits=[],
            labels=[],
            reviewers=[],
            comments=[
                PRComment(author="user2", body="General comment", created_at=datetime.now()),
            ],
            review_comments=[
                ReviewComment(
                    author="user3",
                    body="Code review comment",
                    path="file.py",
                    line=10,
                    created_at=datetime.now(),
                ),
            ],
        )

        summary = pr.discussion_summary
        assert "PR description" in summary
        assert "General comment" in summary
        assert "Code review comment" in summary


class TestEnrichedCommit:
    """Test suite for EnrichedCommit dataclass."""

    def test_has_context_with_pr(self):
        """Test has_context with PR."""
        commit = Commit(
            sha="abc123",
            message="Test commit",
            author="user1",
            email="user1@example.com",
            date=datetime.now(),
            parents=[],
        )

        pr = PullRequest(
            number=1,
            title="Test PR",
            body="Description",
            author="user1",
            state="merged",
            created_at=datetime.now(),
            merged_at=datetime.now(),
            closed_at=None,
            commits=["abc123"],
            labels=[],
            reviewers=[],
        )

        enriched = EnrichedCommit(commit=commit, pull_request=pr)
        assert enriched.has_context is True

    def test_has_context_with_issues(self):
        """Test has_context with issues."""
        commit = Commit(
            sha="abc123",
            message="Test commit",
            author="user1",
            email="user1@example.com",
            date=datetime.now(),
            parents=[],
        )

        issue = Issue(
            number=1,
            title="Test issue",
            body="Description",
            author="user1",
            state="closed",
            created_at=datetime.now(),
            closed_at=datetime.now(),
            labels=[],
        )

        enriched = EnrichedCommit(commit=commit, related_issues=[issue])
        assert enriched.has_context is True

    def test_has_context_without_context(self):
        """Test has_context without PR or issues."""
        commit = Commit(
            sha="abc123",
            message="Test commit",
            author="user1",
            email="user1@example.com",
            date=datetime.now(),
            parents=[],
        )

        enriched = EnrichedCommit(commit=commit)
        assert enriched.has_context is False


class TestGitHubAPIClient:
    """Test suite for GitHubAPIClient class."""

    def test_initialization_with_token(self):
        """Test client initialization with explicit token."""
        client = GitHubAPIClient(token="test_token")
        assert client.token == "test_token"
        assert 'Authorization' in client.session.headers
        assert client.session.headers['Authorization'] == "token test_token"

    def test_initialization_from_env(self, monkeypatch):
        """Test client initialization from environment variable."""
        monkeypatch.setenv('GITHUB_TOKEN', 'env_token')
        client = GitHubAPIClient()
        assert client.token == "env_token"

    def test_initialization_without_token(self, monkeypatch):
        """Test client initialization without token."""
        monkeypatch.delenv('GITHUB_TOKEN', raising=False)
        client = GitHubAPIClient()
        assert client.token is None
        assert 'Authorization' not in client.session.headers


@pytest.mark.integration
class TestGitHubIntegration:
    """
    Integration tests requiring GITHUB_TOKEN.

    These tests make real API calls and will be skipped if GITHUB_TOKEN is not set.
    """

    @pytest.fixture(autouse=True)
    def skip_if_no_token(self):
        """Skip integration tests if GITHUB_TOKEN is not set."""
        if not os.environ.get('GITHUB_TOKEN'):
            pytest.skip("GITHUB_TOKEN not set, skipping integration tests")

    @pytest.fixture
    def archaeologist(self):
        """Create GitHubArchaeologist for a known public repo."""
        # Use a small, stable public repo for testing
        return GitHubArchaeologist("octocat", "Hello-World")

    def test_fetch_pull_request_real(self, archaeologist):
        """Test fetching a real pull request."""
        # PR #1 in octocat/Hello-World (if it exists)
        pr = archaeologist.fetch_pull_request(1)

        # PR may not exist, so just test the mechanism works
        if pr:
            assert isinstance(pr, PullRequest)
            assert pr.number == 1
            assert pr.title
            assert pr.author

    def test_fetch_issue_real(self, archaeologist):
        """Test fetching a real issue."""
        # Try to fetch issue #1
        issue = archaeologist.fetch_issue(1)

        # Issue may not exist or might be a PR
        if issue:
            assert isinstance(issue, Issue)
            assert issue.number == 1
            assert issue.title
            assert issue.author

    def test_link_commit_to_pr_real(self, archaeologist):
        """Test linking a commit to PR."""
        # Create a sample commit with PR reference
        commit = Commit(
            sha="test_sha",
            message="Fix bug (#1)",
            author="Test",
            email="test@example.com",
            date=datetime.now(),
            parents=[],
        )

        pr_number = archaeologist.link_commit_to_pr(commit)

        # Should extract #1 from message
        assert pr_number == 1


class TestEnrichedHistory:
    """Test suite for EnrichedHistory dataclass."""

    def test_enrichment_rate_calculation(self):
        """Test enrichment rate calculation."""
        from tools.code_archaeology.github_integrator import EnrichedHistory
        from tools.code_archaeology.git_analyzer import RepositoryHistory

        # Create sample commits
        commit1 = Commit(
            sha="sha1",
            message="Commit 1",
            author="user1",
            email="user1@example.com",
            date=datetime.now(),
            parents=[],
        )
        commit2 = Commit(
            sha="sha2",
            message="Commit 2",
            author="user1",
            email="user1@example.com",
            date=datetime.now(),
            parents=[],
        )

        # Create enriched commits (1 with context, 1 without)
        enriched1 = EnrichedCommit(
            commit=commit1,
            pull_request=PullRequest(
                number=1,
                title="PR 1",
                body="",
                author="user1",
                state="merged",
                created_at=datetime.now(),
                merged_at=datetime.now(),
                closed_at=None,
                commits=[],
                labels=[],
                reviewers=[],
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
            author_stats={},
            branch_commits={},
        )

        # Create enriched history
        enriched_history = EnrichedHistory(
            base_history=base_history,
            enriched_commits=[enriched1, enriched2],
            pull_requests={1: enriched1.pull_request},
            issues={},
            commit_to_pr={"sha1": 1},
        )

        # 1 out of 2 commits has context = 50%
        assert enriched_history.enrichment_rate == 0.5

    def test_enrichment_rate_zero(self):
        """Test enrichment rate when no commits have context."""
        from tools.code_archaeology.github_integrator import EnrichedHistory
        from tools.code_archaeology.git_analyzer import RepositoryHistory

        commit = Commit(
            sha="sha1",
            message="Commit",
            author="user1",
            email="user1@example.com",
            date=datetime.now(),
            parents=[],
        )

        enriched = EnrichedCommit(commit=commit)

        base_history = RepositoryHistory(
            repo_path=Path("."),
            commits=[commit],
            arch_commits=[],
            temporal_index={},
            file_history={},
            author_stats={},
            branch_commits={},
        )

        enriched_history = EnrichedHistory(
            base_history=base_history,
            enriched_commits=[enriched],
            pull_requests={},
            issues={},
            commit_to_pr={},
        )

        assert enriched_history.enrichment_rate == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
