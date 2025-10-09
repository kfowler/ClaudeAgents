"""
Tests for Git History Analyzer module.
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.code_archaeology.git_analyzer import (
    GitArchaeologist,
    CommitAnalyzer,
    TemporalCorrelator,
    Commit,
    ArchCommit,
)


class TestGitArchaeologist:
    """Test suite for GitArchaeologist class."""

    @pytest.fixture
    def repo_path(self):
        """Get the ClaudeAgents repository path."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def archaeologist(self, repo_path):
        """Create GitArchaeologist instance."""
        return GitArchaeologist(str(repo_path))

    def test_initialization(self, archaeologist, repo_path):
        """Test archaeologist initializes correctly."""
        assert archaeologist.repo_path == repo_path.resolve()
        assert isinstance(archaeologist.analyzer, CommitAnalyzer)
        assert isinstance(archaeologist.correlator, TemporalCorrelator)

    def test_invalid_repo_path(self):
        """Test that invalid repo path raises ValueError."""
        with pytest.raises(ValueError):
            GitArchaeologist("/tmp/not-a-repo")

    def test_extract_commit_history(self, archaeologist):
        """Test commit history extraction."""
        commits = archaeologist.extract_commit_history(limit=10)

        assert len(commits) <= 10
        assert all(isinstance(c, Commit) for c in commits)

        # Verify commit structure
        for commit in commits:
            assert commit.sha
            assert commit.author
            assert commit.email
            assert isinstance(commit.date, datetime)
            assert isinstance(commit.files_changed, list)
            assert isinstance(commit.additions, int)
            assert isinstance(commit.deletions, int)

    def test_identify_architectural_commits(self, archaeologist):
        """Test architectural commit identification."""
        commits = archaeologist.extract_commit_history(limit=50)
        arch_commits = archaeologist.identify_architectural_commits(commits)

        assert len(arch_commits) > 0
        assert all(isinstance(ac, ArchCommit) for ac in arch_commits)

        # Verify arch commit structure
        for ac in arch_commits:
            assert isinstance(ac.commit, Commit)
            assert ac.significance in ['architecture', 'feature', 'refactor', 'config', 'dependency']
            assert 0.0 <= ac.impact_score <= 1.0
            assert isinstance(ac.patterns, list)
            assert isinstance(ac.related_files, list)

        # Verify sorted by impact score
        scores = [ac.impact_score for ac in arch_commits]
        assert scores == sorted(scores, reverse=True)

    def test_build_temporal_index(self, archaeologist):
        """Test temporal index building."""
        commits = archaeologist.extract_commit_history(limit=50)
        temporal_index = archaeologist.build_temporal_index(commits)

        assert len(temporal_index) > 0

        # Verify date format (YYYY-MM-DD)
        for date_key in temporal_index.keys():
            assert len(date_key) == 10
            assert date_key[4] == '-'
            assert date_key[7] == '-'

        # Verify commits are sorted within each day
        for commits_list in temporal_index.values():
            dates = [c.date for c in commits_list]
            assert dates == sorted(dates)

    def test_analyze_repo(self, archaeologist):
        """Test complete repository analysis."""
        history = archaeologist.analyze_repo(limit=100)

        # Verify basic properties
        assert history.total_commits == len(history.commits)
        assert history.total_commits <= 100
        assert len(history.arch_commits) > 0

        # Verify temporal index
        assert len(history.temporal_index) > 0

        # Verify file history
        assert len(history.file_history) > 0

        # Verify author stats
        assert len(history.author_stats) > 0
        assert sum(history.author_stats.values()) == history.total_commits

        # Verify date range
        start_date, end_date = history.date_range
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        assert start_date <= end_date

        # Verify top contributors
        assert len(history.top_contributors) > 0
        assert all(isinstance(author, str) for author, _ in history.top_contributors)
        assert all(isinstance(count, int) for _, count in history.top_contributors)


class TestCommitAnalyzer:
    """Test suite for CommitAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create CommitAnalyzer instance."""
        return CommitAnalyzer()

    def test_analyze_architectural_commit(self, analyzer):
        """Test analysis of architectural commit."""
        commit = Commit(
            sha="abc123",
            message="Add new microservices architecture with Docker",
            author="Test Author",
            email="test@example.com",
            date=datetime.now(),
            parents=["parent123"],
            files_changed=["Dockerfile", "docker-compose.yml", "package.json"],
            additions=500,
            deletions=100,
        )

        arch_commit = analyzer.analyze_commit(commit)

        assert arch_commit is not None
        assert isinstance(arch_commit, ArchCommit)
        assert arch_commit.significance in ['architecture', 'feature', 'refactor', 'config', 'dependency']
        assert arch_commit.impact_score > 0.3

    def test_analyze_non_architectural_commit(self, analyzer):
        """Test analysis of non-architectural commit."""
        commit = Commit(
            sha="xyz789",
            message="Fix typo in comment",
            author="Test Author",
            email="test@example.com",
            date=datetime.now(),
            parents=["parent456"],
            files_changed=["src/utils.py"],
            additions=1,
            deletions=1,
        )

        arch_commit = analyzer.analyze_commit(commit)

        # Small typo fix should not be considered architectural
        assert arch_commit is None or arch_commit.impact_score < 0.5

    def test_analyze_large_refactor(self, analyzer):
        """Test analysis of large refactoring commit."""
        commit = Commit(
            sha="def456",
            message="Refactor database layer for better performance",
            author="Test Author",
            email="test@example.com",
            date=datetime.now(),
            parents=["parent789"],
            files_changed=[f"src/db/model_{i}.py" for i in range(15)],
            additions=800,
            deletions=600,
        )

        arch_commit = analyzer.analyze_commit(commit)

        assert arch_commit is not None
        assert arch_commit.significance == 'refactor'
        assert arch_commit.impact_score >= 0.5  # Should have high impact


class TestTemporalCorrelator:
    """Test suite for TemporalCorrelator class."""

    @pytest.fixture
    def sample_commits(self):
        """Create sample commits for testing."""
        return [
            Commit(
                sha="commit1",
                message="First commit",
                author="Author1",
                email="author1@example.com",
                date=datetime(2025, 1, 1, 10, 0, 0),
                parents=[],
                files_changed=["file1.py"],
            ),
            Commit(
                sha="commit2",
                message="Second commit",
                author="Author2",
                email="author2@example.com",
                date=datetime(2025, 1, 1, 14, 0, 0),
                parents=["commit1"],
                files_changed=["file1.py", "file2.py"],
            ),
            Commit(
                sha="commit3",
                message="Third commit",
                author="Author1",
                email="author1@example.com",
                date=datetime(2025, 1, 2, 9, 0, 0),
                parents=["commit2"],
                files_changed=["file3.py"],
            ),
        ]

    def test_build_temporal_index(self, sample_commits):
        """Test temporal index building."""
        index = TemporalCorrelator.build_temporal_index(sample_commits)

        assert len(index) == 2  # Two days
        assert "2025-01-01" in index
        assert "2025-01-02" in index
        assert len(index["2025-01-01"]) == 2
        assert len(index["2025-01-02"]) == 1

    def test_build_file_history(self, sample_commits):
        """Test file history building."""
        file_history = TemporalCorrelator.build_file_history(sample_commits)

        assert len(file_history) == 3  # Three files
        assert "file1.py" in file_history
        assert "file2.py" in file_history
        assert "file3.py" in file_history
        assert len(file_history["file1.py"]) == 2  # Changed in 2 commits
        assert len(file_history["file2.py"]) == 1  # Changed in 1 commit

    def test_build_author_stats(self, sample_commits):
        """Test author statistics building."""
        stats = TemporalCorrelator.build_author_stats(sample_commits)

        assert len(stats) == 2  # Two authors
        assert stats["Author1"] == 2
        assert stats["Author2"] == 1


class TestPerformance:
    """Performance tests for git analyzer."""

    @pytest.fixture
    def repo_path(self):
        """Get the ClaudeAgents repository path."""
        return Path(__file__).parent.parent

    def test_analysis_performance(self, repo_path):
        """Test that analysis completes in reasonable time."""
        import time

        archaeologist = GitArchaeologist(str(repo_path))

        start_time = time.time()
        history = archaeologist.analyze_repo(limit=100)
        elapsed = time.time() - start_time

        # Should complete 100 commits in under 30 seconds
        assert elapsed < 30, f"Analysis took {elapsed:.2f}s, expected <30s"
        assert history.total_commits == 100

    def test_full_repo_analysis_performance(self, repo_path):
        """Test full repository analysis performance."""
        import time

        archaeologist = GitArchaeologist(str(repo_path))

        start_time = time.time()
        history = archaeologist.analyze_repo()  # No limit
        elapsed = time.time() - start_time

        print(f"\nFull analysis: {history.total_commits} commits in {elapsed:.2f}s")

        # Should complete full repo in under 60 seconds
        assert elapsed < 60, f"Full analysis took {elapsed:.2f}s, expected <60s"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
