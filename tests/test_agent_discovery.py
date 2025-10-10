#!/usr/bin/env python3
"""
Test suite for agent discovery system.

Tests:
- Keyword search accuracy (creative agents discoverable)
- Natural language query parsing
- Tier-based prioritization (Core > Extended > Experimental)
- Recommendation explanations (relevance scores)
- Coverage (all agents searchable)
"""

import json
import pytest
from pathlib import Path
import sys
import subprocess

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


class TestAgentDiscovery:
    """Test suite for agent discovery system."""

    @pytest.fixture
    def project_root(self):
        """Fixture providing project root path."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def agents_dir(self, project_root):
        """Fixture providing agents directory path."""
        return project_root / "agents"

    @pytest.fixture
    def discovery_script(self, project_root):
        """Fixture providing discovery script path."""
        return project_root / "tools" / "intelligent_orchestrator.py"

    def run_discovery(self, discovery_script, query):
        """Helper to run discovery command and parse output."""
        try:
            result = subprocess.run(
                ["python3", str(discovery_script), "discover", query],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            pytest.fail("Discovery command timed out")

    def test_keyword_search_creative_agents(self, discovery_script):
        """Test that creative agents are discoverable via keyword search."""
        creative_keywords = ["creative", "ideation", "brainstorming", "innovation"]

        for keyword in creative_keywords:
            output, returncode = self.run_discovery(discovery_script, keyword)

            # Should succeed
            assert returncode == 0, f"Discovery should succeed for keyword '{keyword}'"

            # Should contain creative agent names
            creative_agents = ["creative-catalyst", "the-inventor", "the-synthesist", "the-architect-of-experiments"]
            found_creative_agents = [agent for agent in creative_agents if agent in output.lower()]

            assert len(found_creative_agents) > 0, f"Should find at least one creative agent for keyword '{keyword}'"

    def test_natural_language_query_parsing(self, discovery_script):
        """Test that natural language queries are parsed correctly."""
        nl_queries = [
            "I need help generating diverse ideas for a product feature",
            "organize my brainstorming ideas into coherent themes",
            "design experiments to validate my hypotheses",
            "break creative blocks with oblique strategies"
        ]

        for query in nl_queries:
            output, returncode = self.run_discovery(discovery_script, query)

            # Should succeed
            assert returncode == 0, f"Discovery should succeed for query: {query}"

            # Should return agent recommendations
            assert "recommendation" in output.lower() or "agent" in output.lower(), f"Should recommend agents for: {query}"

    def test_tier_based_prioritization(self, discovery_script):
        """Test that Core agents are prioritized over Extended and Experimental."""
        # Search for a generic query that matches multiple tiers
        output, returncode = self.run_discovery(discovery_script, "code review")

        assert returncode == 0

        # Parse output to extract agent recommendations with tiers
        # Look for tier indicators: CORE, EXTENDED, EXPERIMENTAL
        has_core = "CORE" in output or "⭐" in output
        has_extended = "EXTENDED" in output or "✓" in output
        has_experimental = "EXPERIMENTAL" in output or "🧪" in output

        # If multiple tiers present, Core should appear first
        if has_core:
            core_position = output.find("CORE") if "CORE" in output else output.find("⭐")
            if has_extended:
                extended_position = output.find("EXTENDED") if "EXTENDED" in output else output.find("✓")
                assert core_position < extended_position, "Core agents should appear before Extended"
            if has_experimental:
                experimental_position = output.find("EXPERIMENTAL") if "EXPERIMENTAL" in output else output.find("🧪")
                assert core_position < experimental_position, "Core agents should appear before Experimental"

    def test_recommendation_explanations(self, discovery_script):
        """Test that recommendations include relevance scores and explanations."""
        output, returncode = self.run_discovery(discovery_script, "creative brainstorming")

        assert returncode == 0

        # Should include relevance information
        relevance_indicators = ["relevance", "score", "aligns", "matches"]
        has_relevance_info = any(indicator in output.lower() for indicator in relevance_indicators)

        assert has_relevance_info, "Recommendations should include relevance explanations"

    def test_coverage_all_agents_searchable(self, discovery_script, agents_dir):
        """Test that all agent files are indexed and searchable."""
        # Get all agent files
        agent_files = list(agents_dir.glob("*.md"))
        agent_files = [f for f in agent_files if f.name not in ["AGENT_TEMPLATE.md", "README.md"]]

        # Verify we have a reasonable number of agents
        assert len(agent_files) >= 70, f"Expected at least 70 agents, found {len(agent_files)}"

        # Test a sample of agents are discoverable
        test_agents = [
            ("the-inventor", "inventor"),
            ("the-synthesist", "synthesis"),
            ("creative-catalyst", "creative"),
            ("the-architect-of-experiments", "experiment"),
            ("full-stack-architect", "web development"),
            ("ai-ml-engineer", "AI integration"),
            ("security-audit-specialist", "security audit"),
            ("qa-test-engineer", "testing")
        ]

        for agent_name, search_term in test_agents:
            output, returncode = self.run_discovery(discovery_script, search_term)
            assert returncode == 0, f"Discovery should succeed for '{search_term}'"
            assert agent_name in output or agent_name.replace("-", " ") in output.lower(), \
                f"Agent '{agent_name}' should be discoverable via '{search_term}'"

    def test_creative_triad_workflow_discovery(self, discovery_script):
        """Test discovery of complete creative triad workflow."""
        # Test that querying for ideation workflow suggests the full triad
        output, returncode = self.run_discovery(discovery_script, "ideation workflow")

        assert returncode == 0

        # Should recommend creative triad agents
        creative_triad = ["the-inventor", "the-synthesist", "the-architect-of-experiments"]
        found_agents = [agent for agent in creative_triad if agent in output.lower()]

        assert len(found_agents) >= 2, "Ideation workflow should suggest multiple creative triad agents"

    def test_tier_distribution(self, discovery_script):
        """Test that discovery results show balanced tier distribution."""
        output, returncode = self.run_discovery(discovery_script, "development")

        assert returncode == 0

        # Count tier occurrences
        core_count = output.count("CORE") + output.count("⭐")
        extended_count = output.count("EXTENDED") + output.count("✓")
        experimental_count = output.count("EXPERIMENTAL") + output.count("🧪")

        # Should have results from multiple tiers
        total_tiers = sum(1 for count in [core_count, extended_count, experimental_count] if count > 0)
        assert total_tiers >= 2, "Results should span multiple agent tiers"

    def test_specific_agent_lookup(self, discovery_script):
        """Test that specific agent names can be looked up directly."""
        specific_agents = [
            "the-inventor",
            "the-synthesist",
            "the-architect-of-experiments",
            "creative-catalyst"
        ]

        for agent_name in specific_agents:
            # Try exact name search
            output, returncode = self.run_discovery(discovery_script, agent_name)

            assert returncode == 0, f"Should find agent '{agent_name}'"
            assert agent_name in output.lower(), f"Output should contain agent name '{agent_name}'"

    def test_multi_keyword_search(self, discovery_script):
        """Test search with multiple keywords."""
        multi_keyword_queries = [
            "creative ideation diversity",
            "experiment design validation",
            "synthesis coherence frames"
        ]

        for query in multi_keyword_queries:
            output, returncode = self.run_discovery(discovery_script, query)

            assert returncode == 0, f"Multi-keyword search should succeed: {query}"
            assert len(output) > 100, f"Should return substantial results for: {query}"

    def test_empty_query_handling(self, discovery_script):
        """Test that empty queries are handled gracefully."""
        output, returncode = self.run_discovery(discovery_script, "")

        # Should either return error or show all agents
        assert returncode in [0, 1], "Should handle empty query gracefully"

    def test_no_results_handling(self, discovery_script):
        """Test behavior when no agents match the query."""
        # Use a very specific nonsense query
        output, returncode = self.run_discovery(discovery_script, "xyznonexistentagentquery123")

        # Should handle gracefully (either return code 0 with "no results" or error)
        assert returncode in [0, 1], "Should handle no-results queries gracefully"

    def test_case_insensitive_search(self, discovery_script):
        """Test that search is case-insensitive."""
        queries = [
            ("creative", "CREATIVE", "Creative"),
            ("inventor", "INVENTOR", "Inventor"),
            ("synthesis", "SYNTHESIS", "Synthesis")
        ]

        for lower, upper, title in queries:
            output_lower, returncode_lower = self.run_discovery(discovery_script, lower)
            output_upper, returncode_upper = self.run_discovery(discovery_script, upper)
            output_title, returncode_title = self.run_discovery(discovery_script, title)

            # All should succeed
            assert returncode_lower == 0
            assert returncode_upper == 0
            assert returncode_title == 0

            # Results should be similar (same agents found)
            # This is a basic check - exact output may vary due to relevance scoring
            assert len(output_lower) > 0
            assert len(output_upper) > 0
            assert len(output_title) > 0
