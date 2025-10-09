"""
Tests for Query CLI module.
"""

import pytest
from pathlib import Path
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.code_archaeology.query_cli import ArchaeologyCLI
from tools.code_archaeology.context_synthesizer import Answer, Citation


class TestArchaeologyCLI:
    """Test suite for ArchaeologyCLI class."""

    @pytest.fixture
    def repo_path(self):
        """Get ClaudeAgents repository path."""
        return str(Path(__file__).parent.parent)

    @pytest.fixture
    def cli(self, repo_path):
        """Create ArchaeologyCLI instance."""
        return ArchaeologyCLI(repo_path)

    def test_initialization(self, cli, repo_path):
        """Test CLI initializes correctly."""
        assert cli.repo_path == Path(repo_path)
        assert cli.github_repo is None
        assert cli.index is None
        assert cli.history == []

    def test_initialization_with_github(self, repo_path):
        """Test CLI initialization with GitHub repo."""
        cli = ArchaeologyCLI(repo_path, github_repo="owner/repo")
        assert cli.github_repo == "owner/repo"

    def test_format_answer_plain(self, cli):
        """Test answer formatting without rich."""
        # Ensure no rich console
        cli.console = None

        citation = Citation(
            commit_sha="abc123456",
            commit_message="Add feature",
            commit_date=datetime(2025, 1, 1),
            author="user1",
            source_type="commit",
            relevance_score=0.9,
        )

        answer = Answer(
            question="Test question?",
            answer="This is a test answer.",
            citations=[citation],
            confidence=0.85,
        )

        formatted = cli.format_answer(answer)

        assert "Test question?" in formatted or "This is a test answer" in formatted
        assert "abc12345" in formatted  # SHA prefix
        assert "user1" in formatted
        assert "85%" in formatted or "0.85" in formatted  # Confidence

    def test_format_answer_with_multiple_citations(self, cli):
        """Test answer formatting with multiple citations."""
        cli.console = None

        citations = [
            Citation(
                commit_sha=f"sha{i}",
                commit_message=f"Commit {i}",
                commit_date=datetime(2025, 1, i),
                author=f"user{i}",
                source_type="commit",
                relevance_score=0.9 - (i * 0.1),
            )
            for i in range(1, 6)
        ]

        answer = Answer(
            question="Multi-citation question?",
            answer="Answer with many citations.",
            citations=citations,
            confidence=0.9,
        )

        formatted = cli.format_answer(answer)

        # Should include all citations (up to 5)
        assert "Citations (5)" in formatted or "5" in formatted

    def test_query_without_initialization(self, cli):
        """Test that querying without initialization raises error."""
        with pytest.raises(RuntimeError):
            cli.query("Test question?")


@pytest.mark.integration
class TestArchaeologyCLIIntegration:
    """
    Integration tests for full CLI workflow.

    These tests require a git repository and are more expensive.
    """

    @pytest.fixture
    def repo_path(self):
        """Get ClaudeAgents repository path."""
        return str(Path(__file__).parent.parent)

    def test_initialize_git_only(self, repo_path):
        """Test initialization with git history only."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        assert cli.index is not None
        assert cli.index.size > 0

    def test_query_execution(self, repo_path):
        """Test executing a query."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        answer = cli.query("What is this repository about?")

        assert isinstance(answer, Answer)
        assert answer.question == "What is this repository about?"
        assert len(answer.answer) > 0
        assert 0.0 <= answer.confidence <= 1.0
        assert len(cli.history) == 1

    def test_multiple_queries(self, repo_path):
        """Test executing multiple queries."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        answer1 = cli.query("What is the main purpose?")
        answer2 = cli.query("Who are the contributors?")

        assert len(cli.history) == 2
        assert cli.history[0] == answer1
        assert cli.history[1] == answer2

    def test_export_history(self, repo_path, tmp_path):
        """Test exporting query history."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        # Execute some queries
        cli.query("Test question 1?")
        cli.query("Test question 2?")

        # Export
        output_file = tmp_path / "history.md"
        cli._export_history(str(output_file))

        # Verify file exists and has content
        assert output_file.exists()
        content = output_file.read_text()
        assert "Code Archaeology Query History" in content
        assert "Test question 1?" in content
        assert "Test question 2?" in content

    def test_export_empty_history(self, repo_path, tmp_path):
        """Test exporting empty history."""
        cli = ArchaeologyCLI(repo_path)

        # Export without queries
        output_file = tmp_path / "empty_history.md"
        cli._export_history(str(output_file))

        # Should handle gracefully (no file created)
        assert not output_file.exists()


class TestCLICommands:
    """Test CLI command parsing and handling."""

    def test_help_command(self, capsys):
        """Test help command display."""
        # This is a placeholder - actual testing would require mocking input/output
        pass

    def test_history_command_empty(self):
        """Test history command with no queries."""
        cli = ArchaeologyCLI(".")
        # Should not raise error
        cli._show_history()

    def test_history_command_with_queries(self):
        """Test history command with queries."""
        cli = ArchaeologyCLI(".")

        # Add fake history
        cli.history = [
            Answer(
                question="Q1?",
                answer="A1",
                citations=[],
                confidence=0.8,
            ),
            Answer(
                question="Q2?",
                answer="A2",
                citations=[],
                confidence=0.9,
            ),
        ]

        # Should display without error
        cli._show_history()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
