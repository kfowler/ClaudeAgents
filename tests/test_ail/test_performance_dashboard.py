"""
Test suite for AIL Performance Dashboard.

This module tests the performance dashboard functionality including
platform-wide statistics, agent-specific views, and JSON output.
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.performance_dashboard import (
    AILPerformanceDashboard,
    AgentStats,
    PlatformStats,
)


class TestAgentStats:
    """Test AgentStats dataclass."""

    def test_agent_stats_creation(self):
        """Test creating AgentStats with default values."""
        stats = AgentStats(agent_name='test-agent')

        assert stats.agent_name == 'test-agent'
        assert stats.learning_db_size == 0
        assert stats.quality_improvement_pct == 0.0
        assert stats.total_queries == 0
        assert stats.avg_latency_ms == 0.0

    def test_agent_stats_with_values(self):
        """Test creating AgentStats with specific values."""
        stats = AgentStats(
            agent_name='security-audit-specialist',
            learning_db_size=1247,
            quality_improvement_pct=54.0,
            total_queries=342,
            avg_latency_ms=287.0,
            cache_hit_rate=0.912,
        )

        assert stats.agent_name == 'security-audit-specialist'
        assert stats.learning_db_size == 1247
        assert stats.quality_improvement_pct == 54.0
        assert stats.total_queries == 342
        assert stats.avg_latency_ms == 287.0
        assert stats.cache_hit_rate == 0.912


class TestPlatformStats:
    """Test PlatformStats dataclass."""

    def test_platform_stats_creation(self):
        """Test creating PlatformStats with default values."""
        stats = PlatformStats()

        assert stats.total_agents == 73
        assert stats.integrated_agents == 7
        assert stats.faiss_dimensions == 384
        assert stats.baseline_quality_score == 6.1

    def test_platform_stats_with_values(self):
        """Test creating PlatformStats with specific values."""
        stats = PlatformStats(
            total_commits=1247,
            total_prs=89,
            total_issues=156,
            l1_hit_rate=0.723,
            l2_hit_rate=0.189,
            combined_hit_rate=0.912,
        )

        assert stats.total_commits == 1247
        assert stats.total_prs == 89
        assert stats.total_issues == 156
        assert stats.l1_hit_rate == 0.723
        assert stats.l2_hit_rate == 0.189
        assert stats.combined_hit_rate == 0.912


class TestAILPerformanceDashboard:
    """Test AILPerformanceDashboard functionality."""

    @pytest.fixture
    def dashboard(self, tmp_path):
        """Create dashboard instance for testing."""
        # Create mock git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        return AILPerformanceDashboard(repo_path=str(tmp_path))

    def test_dashboard_initialization(self, dashboard):
        """Test dashboard initialization."""
        assert dashboard is not None
        assert dashboard.repo_path.exists()
        assert len(dashboard.INTEGRATED_AGENTS) == 7

    def test_integrated_agents_list(self, dashboard):
        """Test that all expected agents are in the integrated list."""
        expected_agents = [
            'code-architect',
            'security-audit-specialist',
            'full-stack-architect',
            'backend-api-engineer',
            'qa-test-engineer',
            'debugging-specialist',
            'frontend-performance-specialist',
        ]

        assert dashboard.INTEGRATED_AGENTS == expected_agents

    def test_get_agent_stats(self, dashboard):
        """Test getting agent-specific stats."""
        stats = dashboard.get_agent_stats('security-audit-specialist')

        assert isinstance(stats, AgentStats)
        assert stats.agent_name == 'security-audit-specialist'
        assert stats.quality_improvement_pct == 54.0  # Expected from Sprint 2

    def test_get_agent_stats_all_agents(self, dashboard):
        """Test getting stats for all integrated agents."""
        for agent_name in dashboard.INTEGRATED_AGENTS:
            stats = dashboard.get_agent_stats(agent_name)

            assert isinstance(stats, AgentStats)
            assert stats.agent_name == agent_name
            assert stats.quality_improvement_pct > 0.0

    def test_get_platform_stats(self, dashboard):
        """Test getting platform-wide stats."""
        stats = dashboard.get_platform_stats()

        assert isinstance(stats, PlatformStats)
        assert stats.total_agents == 73
        assert stats.integrated_agents == 7
        assert stats.avg_quality_score > stats.baseline_quality_score

    def test_quality_improvements_mapping(self, dashboard):
        """Test that quality improvements match Sprint 2 results."""
        expected_improvements = {
            'security-audit-specialist': 54.0,
            'debugging-specialist': 48.0,
            'code-architect': 42.0,
            'qa-test-engineer': 38.0,
            'backend-api-engineer': 35.0,
        }

        for agent_name, expected_improvement in expected_improvements.items():
            stats = dashboard.get_agent_stats(agent_name)
            assert stats.quality_improvement_pct == expected_improvement


class TestDashboardOutput:
    """Test dashboard output functionality."""

    @pytest.fixture
    def dashboard(self, tmp_path):
        """Create dashboard instance for testing."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        return AILPerformanceDashboard(repo_path=str(tmp_path))

    def test_json_output_platform(self, dashboard, capsys):
        """Test JSON output for platform stats."""
        dashboard.display_dashboard(format='json')
        captured = capsys.readouterr()

        # Parse JSON output
        data = json.loads(captured.out)

        # Verify structure
        assert 'platform' in data
        assert 'knowledge_base' in data
        assert 'cache_performance' in data
        assert 'quality_metrics' in data
        assert 'performance' in data
        assert 'recent_activity' in data
        assert 'integrated_agents' in data

        # Verify platform data
        assert data['platform']['total_agents'] == 73
        assert data['platform']['integrated_agents'] == 7
        assert len(data['integrated_agents']) == 7

    def test_json_output_agent(self, dashboard, capsys):
        """Test JSON output for agent-specific stats."""
        dashboard.display_dashboard(agent='code-architect', format='json')
        captured = capsys.readouterr()

        # Parse JSON output
        data = json.loads(captured.out)

        # Verify structure
        assert 'agent_name' in data
        assert 'quality_improvement_pct' in data
        assert 'learning_db_size' in data

        # Verify values
        assert data['agent_name'] == 'code-architect'
        assert data['quality_improvement_pct'] == 42.0

    def test_invalid_agent_error(self, dashboard, capsys):
        """Test error handling for invalid agent name."""
        dashboard.display_dashboard(agent='nonexistent-agent', format='text')
        captured = capsys.readouterr()

        assert 'Error:' in captured.out
        assert 'not integrated with AIL' in captured.out


class TestDashboardHelpers:
    """Test dashboard helper methods."""

    @pytest.fixture
    def dashboard(self, tmp_path):
        """Create dashboard instance for testing."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        return AILPerformanceDashboard(repo_path=str(tmp_path))

    def test_get_repo_commit_count(self, dashboard):
        """Test getting repository commit count."""
        count = dashboard._get_repo_commit_count()
        assert isinstance(count, int)
        assert count > 0

    def test_count_recent_commits(self, dashboard):
        """Test counting recent commits."""
        count = dashboard._count_recent_commits(hours=24)
        assert isinstance(count, int)
        assert count >= 0

    def test_count_architectural_commits(self, dashboard):
        """Test counting architectural commits."""
        count = dashboard._count_architectural_commits()
        assert isinstance(count, int)
        assert count >= 0

    def test_estimate_faiss_memory(self, dashboard):
        """Test FAISS memory estimation."""
        memory = dashboard._estimate_faiss_memory()
        assert isinstance(memory, float)
        assert memory >= 0.0


def test_integrated_agents_match_completion_report():
    """Test that integrated agents match Sprint 2 completion report."""
    expected_agents = [
        'code-architect',
        'security-audit-specialist',
        'full-stack-architect',
        'backend-api-engineer',
        'qa-test-engineer',
        'debugging-specialist',
        'frontend-performance-specialist',
    ]

    assert AILPerformanceDashboard.INTEGRATED_AGENTS == expected_agents


def test_sprint2_quality_improvements():
    """Test that quality improvements match Sprint 2 benchmarks."""
    quality_improvements = {
        'security-audit-specialist': 54.0,
        'debugging-specialist': 48.0,
        'code-architect': 42.0,
        'qa-test-engineer': 38.0,
        'backend-api-engineer': 35.0,
        'full-stack-architect': 33.0,
        'frontend-performance-specialist': 31.0,
    }

    # Verify all agents have quality improvements defined
    assert len(quality_improvements) == len(AILPerformanceDashboard.INTEGRATED_AGENTS)

    # Verify all improvements are positive
    for agent, improvement in quality_improvements.items():
        assert improvement > 0.0
        assert agent in AILPerformanceDashboard.INTEGRATED_AGENTS


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
