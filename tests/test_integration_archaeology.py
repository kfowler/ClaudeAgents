"""
Integration tests for Cognitive Code Archaeology end-to-end workflow.

These tests verify the complete pipeline:
1. Git history analysis
2. GitHub enrichment (optional)
3. Semantic indexing
4. Query execution
5. Answer generation
"""

import pytest
from pathlib import Path
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.code_archaeology import (
    GitArchaeologist,
    GitHubArchaeologist,
    ContextSynthesizer,
    ArchaeologyCLI,
)


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete archaeology workflow from analysis to query."""

    @pytest.fixture
    def repo_path(self):
        """Get ClaudeAgents repository path."""
        return str(Path(__file__).parent.parent)

    def test_complete_workflow_git_only(self, repo_path):
        """Test complete workflow with git history only."""
        # Step 1: Analyze git history
        git_arch = GitArchaeologist(repo_path)
        history = git_arch.analyze_repo(limit=50)

        assert history.total_commits == 50
        assert len(history.arch_commits) > 0
        assert len(history.temporal_index) > 0

        # Step 2: Build search index (no GitHub)
        from tools.code_archaeology.github_integrator import EnrichedHistory, EnrichedCommit

        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={},
            issues={},
            commit_to_pr={},
        )

        synthesizer = ContextSynthesizer()
        index = synthesizer.build_searchable_index(enriched)

        assert index.size > 0
        assert index.embeddings is not None

        # Step 3: Execute query
        answer = synthesizer.synthesize_answer(
            index,
            "What is the main purpose of this repository?"
        )

        assert answer is not None
        assert len(answer.answer) > 0
        assert 0.0 <= answer.confidence <= 1.0
        assert len(answer.citations) > 0

    def test_cli_initialization(self, repo_path):
        """Test CLI initialization and setup."""
        cli = ArchaeologyCLI(repo_path)

        # Initialize should complete without errors
        cli.initialize()

        assert cli.index is not None
        assert cli.index.size > 0

    def test_cli_query_execution(self, repo_path):
        """Test CLI query execution."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        # Execute a query
        answer = cli.query("What are the main components?")

        assert answer is not None
        assert len(answer.answer) > 0
        assert len(cli.history) == 1

    def test_cli_export_functionality(self, repo_path, tmp_path):
        """Test CLI export to markdown."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        # Execute queries
        cli.query("Question 1?")
        cli.query("Question 2?")

        # Export
        output_file = tmp_path / "export.md"
        cli._export_history(str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "Code Archaeology Query History" in content
        assert "Question 1?" in content
        assert "Question 2?" in content

    def test_performance_benchmark(self, repo_path):
        """Test that analysis completes within reasonable time."""
        import time

        cli = ArchaeologyCLI(repo_path)

        start = time.time()
        cli.initialize()
        init_time = time.time() - start

        # Should complete initialization in under 30 seconds
        assert init_time < 30, f"Initialization took {init_time:.2f}s, expected <30s"

        start = time.time()
        answer = cli.query("Test query?")
        query_time = time.time() - start

        # Should complete query in under 5 seconds
        assert query_time < 5, f"Query took {query_time:.2f}s, expected <5s"


@pytest.mark.integration
class TestGitHubIntegration:
    """Test GitHub enrichment integration (requires GITHUB_TOKEN)."""

    @pytest.fixture(autouse=True)
    def skip_if_no_token(self):
        """Skip if GITHUB_TOKEN not available."""
        if not os.environ.get('GITHUB_TOKEN'):
            pytest.skip("GITHUB_TOKEN not set, skipping GitHub integration tests")

    def test_github_enrichment_workflow(self):
        """Test workflow with GitHub enrichment."""
        repo_path = str(Path(__file__).parent.parent)

        # Analyze git history
        git_arch = GitArchaeologist(repo_path)
        history = git_arch.analyze_repo(limit=10)

        # Try GitHub enrichment
        # Note: This will only work if repo is public or GITHUB_TOKEN has access
        try:
            gh_arch = GitHubArchaeologist("anthropics", "claude-agents")
            enriched = gh_arch.enrich_history(history, limit=10)

            assert enriched.enrichment_rate >= 0.0
            print(f"Enrichment rate: {enriched.enrichment_rate:.1%}")
        except Exception as e:
            pytest.skip(f"GitHub enrichment not available: {e}")


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integration scenarios."""

    def test_invalid_repository_path(self):
        """Test handling of invalid repository path."""
        with pytest.raises(ValueError):
            GitArchaeologist("/tmp/not-a-git-repo")

    def test_query_before_initialization(self):
        """Test querying before initialization raises error."""
        cli = ArchaeologyCLI(".")

        with pytest.raises(RuntimeError):
            cli.query("Test question?")

    def test_export_empty_history(self, tmp_path):
        """Test exporting with no query history."""
        cli = ArchaeologyCLI(".")

        output_file = tmp_path / "empty.md"
        cli._export_history(str(output_file))

        # Should handle gracefully
        assert not output_file.exists()


@pytest.mark.integration
class TestDataIntegrity:
    """Test data integrity across the pipeline."""

    @pytest.fixture
    def repo_path(self):
        """Get repository path."""
        return str(Path(__file__).parent.parent)

    def test_commit_data_preservation(self, repo_path):
        """Test that commit data is preserved through pipeline."""
        # Analyze repository
        git_arch = GitArchaeologist(repo_path)
        history = git_arch.analyze_repo(limit=10)

        original_commits = history.commits[:5]

        # Create enriched history
        from tools.code_archaeology.github_integrator import EnrichedHistory, EnrichedCommit

        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={},
            issues={},
            commit_to_pr={},
        )

        # Build index
        synthesizer = ContextSynthesizer()
        index = synthesizer.build_searchable_index(enriched)

        # Verify original commit data is accessible
        for orig_commit in original_commits:
            found = False
            for enriched_commit in index.enriched_history.enriched_commits:
                if enriched_commit.commit.sha == orig_commit.sha:
                    assert enriched_commit.commit.message == orig_commit.message
                    assert enriched_commit.commit.author == orig_commit.author
                    found = True
                    break
            assert found, f"Commit {orig_commit.sha[:8]} not found in index"

    def test_citation_accuracy(self, repo_path):
        """Test that citations accurately reference source commits."""
        cli = ArchaeologyCLI(repo_path)
        cli.initialize()

        answer = cli.query("What is this repository?")

        # Verify all citations reference actual commits
        for citation in answer.citations:
            # SHA should exist in the index
            found = False
            for commit in cli.index.enriched_history.enriched_commits:
                if commit.commit.sha.startswith(citation.commit_sha[:8]):
                    found = True
                    # Message should match
                    assert citation.commit_message in commit.commit.message or \
                           commit.commit.message in citation.commit_message
                    break
            assert found, f"Citation references unknown commit: {citation.commit_sha}"


@pytest.mark.integration
class TestScalability:
    """Test system scalability with larger datasets."""

    @pytest.fixture
    def repo_path(self):
        """Get repository path."""
        return str(Path(__file__).parent.parent)

    def test_large_repository_analysis(self, repo_path):
        """Test analysis of complete repository."""
        git_arch = GitArchaeologist(repo_path)
        history = git_arch.analyze_repo()  # No limit - analyze all

        print(f"\nAnalyzed {history.total_commits} commits")
        print(f"Architectural commits: {len(history.arch_commits)}")
        print(f"Date range: {history.date_range[0].date()} to {history.date_range[1].date()}")

        assert history.total_commits > 0

    def test_index_scalability(self, repo_path):
        """Test index building with full repository."""
        import time

        git_arch = GitArchaeologist(repo_path)
        history = git_arch.analyze_repo()

        from tools.code_archaeology.github_integrator import EnrichedHistory, EnrichedCommit

        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={},
            issues={},
            commit_to_pr={},
        )

        synthesizer = ContextSynthesizer()

        start = time.time()
        index = synthesizer.build_searchable_index(enriched)
        index_time = time.time() - start

        print(f"\nIndexed {index.size} documents in {index_time:.2f}s")
        print(f"Performance: {index.size / index_time:.1f} docs/second")

        # Should be reasonably fast (>10 docs/second)
        assert index.size / index_time > 10, "Indexing too slow"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
