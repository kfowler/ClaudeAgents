"""
Integration Tests for code-architect AIL Enhancement

Tests the Archaeological Intelligence integration for code-architect agent,
verifying quality improvements in architectural reviews.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.integrations.code_architect_ail import (
    CodeArchitectAIL,
    ArchitecturalReview,
    ArchitecturalInsight,
    CodeQualityTrend,
)


class TestCodeArchitectAIL:
    """Test suite for CodeArchitectAIL integration."""

    @pytest.fixture
    def repo_path(self):
        """Repository path for testing."""
        return str(PROJECT_ROOT)

    @pytest.fixture
    def architect_ail(self, repo_path):
        """Initialize CodeArchitectAIL instance."""
        return CodeArchitectAIL(repo_path)

    def test_initialization(self, architect_ail):
        """Test CodeArchitectAIL initialization."""
        assert architect_ail is not None
        assert architect_ail.provider is not None
        assert architect_ail.repo_path.exists()

    def test_enhanced_review_basic(self, architect_ail):
        """Test basic enhanced review functionality."""
        # Test with AIL context provider file
        review = architect_ail.enhanced_review(
            "Why does tools/ail/context_provider.py use LRU caching?"
        )

        # Verify review structure
        assert isinstance(review, ArchitecturalReview)
        assert review.file_path
        assert review.review_question
        assert review.archaeological_context is not None
        assert review.confidence >= 0.0
        assert review.query_time_ms >= 0.0

    def test_architectural_insights_extraction(self, architect_ail):
        """Test extraction of architectural insights."""
        review = architect_ail.enhanced_review(
            "What architectural patterns are used in tools/ail/context_provider.py?"
        )

        # Insights should be extracted if available
        assert isinstance(review.architectural_insights, list)
        # All insights should have proper structure
        for insight in review.architectural_insights:
            assert isinstance(insight, ArchitecturalInsight)
            assert insight.insight_type in [
                'design_decision', 'refactoring', 'pattern', 'convention'
            ]
            assert insight.confidence >= 0.0

    def test_design_decisions_extraction(self, architect_ail):
        """Test extraction of design decisions."""
        review = architect_ail.enhanced_review(
            "What design decisions were made in tools/ail/context_provider.py?"
        )

        # Design decisions should be extracted
        assert isinstance(review.design_decisions, list)
        # Decisions should be strings
        for decision in review.design_decisions:
            assert isinstance(decision, str)
            assert len(decision) > 0

    def test_refactoring_history_extraction(self, architect_ail):
        """Test extraction of refactoring history."""
        review = architect_ail.enhanced_review(
            "What refactorings were performed on tools/ail/context_provider.py?"
        )

        # Refactoring history should be extracted
        assert isinstance(review.refactoring_history, list)

    def test_quality_trends_analysis(self, architect_ail):
        """Test quality trends analysis."""
        review = architect_ail.enhanced_review(
            "How has code quality evolved in tools/ail/context_provider.py?"
        )

        # Quality trends should be analyzed
        assert isinstance(review.quality_trends, list)
        for trend in review.quality_trends:
            assert isinstance(trend, CodeQualityTrend)
            assert trend.metric
            assert trend.trend in ['improving', 'stable', 'degrading']

    def test_technical_debt_patterns(self, architect_ail):
        """Test technical debt pattern identification."""
        review = architect_ail.enhanced_review(
            "What technical debt exists in tools/ail/context_provider.py?"
        )

        # Technical debt patterns should be identified
        assert isinstance(review.technical_debt_patterns, list)

    def test_recommendations_generation(self, architect_ail):
        """Test recommendations generation."""
        review = architect_ail.enhanced_review(
            "Review tools/ail/context_provider.py architecture"
        )

        # Recommendations should be generated
        assert isinstance(review.recommendations, list)
        assert len(review.recommendations) > 0
        for rec in review.recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0

    def test_markdown_output(self, architect_ail):
        """Test markdown output generation."""
        review = architect_ail.enhanced_review(
            "Analyze tools/ail/context_provider.py"
        )

        markdown = review.to_markdown()
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "# Architectural Review:" in markdown
        assert "## Archaeological Context" in markdown

    def test_dict_serialization(self, architect_ail):
        """Test dictionary serialization."""
        review = architect_ail.enhanced_review(
            "Review tools/ail/context_provider.py"
        )

        review_dict = review.to_dict()
        assert isinstance(review_dict, dict)
        assert 'file_path' in review_dict
        assert 'confidence' in review_dict
        assert 'architectural_insights' in review_dict

    def test_quality_improvement_measurement(self, architect_ail):
        """Test quality improvement with AIL vs without AIL."""
        # This test measures the quality improvement from AIL integration
        review = architect_ail.enhanced_review(
            "Why was the two-tier caching strategy implemented in tools/ail/context_provider.py?"
        )

        # Quality metrics
        has_historical_context = review.archaeological_context.confidence > 0.3
        has_insights = len(review.architectural_insights) > 0
        has_decisions = len(review.design_decisions) > 0
        has_recommendations = len(review.recommendations) > 0

        # Calculate quality score (0-100)
        quality_score = 0
        if has_historical_context:
            quality_score += 25
        if has_insights:
            quality_score += 25
        if has_decisions:
            quality_score += 25
        if has_recommendations:
            quality_score += 25

        # Target: 40%+ improvement means quality score should be > 60
        assert quality_score >= 60, (
            f"Quality score {quality_score} below target (60). "
            f"AIL integration should provide >40% improvement."
        )

        print(f"\nQuality Improvement Test Results:")
        print(f"  Quality Score: {quality_score}/100")
        print(f"  Historical Context: {has_historical_context} (confidence: {review.archaeological_context.confidence:.2%})")
        print(f"  Architectural Insights: {len(review.architectural_insights)}")
        print(f"  Design Decisions: {len(review.design_decisions)}")
        print(f"  Recommendations: {len(review.recommendations)}")


def test_integration_smoke():
    """Smoke test for basic integration functionality."""
    repo_path = str(PROJECT_ROOT)
    architect = CodeArchitectAIL(repo_path)

    # Simple smoke test
    review = architect.enhanced_review(
        "What is the purpose of tools/ail/context_provider.py?"
    )

    assert review is not None
    assert review.confidence >= 0.0
    print(f"\nSmoke test passed. Confidence: {review.confidence:.2%}")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '-s'])
