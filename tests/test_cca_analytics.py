"""
Tests for CCA Analytics Integration

Tests the analytics tracking system for Cognitive Code Archaeology.
"""

import pytest
import time
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.code_archaeology.analytics import (
    CCAAnalytics,
    CCAEvent,
    QueryCategory
)


@pytest.fixture
def temp_analytics_dir():
    """Create temporary analytics directory"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def analytics(temp_analytics_dir):
    """Create analytics instance with temp directory"""
    return CCAAnalytics(base_dir=temp_analytics_dir)


class TestCCAEvent:
    """Test CCA event data structure"""

    def test_event_creation(self):
        """Test creating a CCA event"""
        event = CCAEvent(
            timestamp=time.time(),
            event_type="query_executed",
            query_category=QueryCategory.ARCHITECTURE_DECISION.value,
            query_response_time=1.5,
            answer_confidence=0.85,
            answer_credibility=0.90,
            citation_count=5
        )

        assert event.event_type == "query_executed"
        assert event.query_category == QueryCategory.ARCHITECTURE_DECISION.value
        assert event.answer_confidence == 0.85

    def test_event_to_dict(self):
        """Test event serialization"""
        event = CCAEvent(
            timestamp=time.time(),
            event_type="analysis_started",
            analysis_commits=100,
            github_enriched=True
        )

        event_dict = event.to_dict()
        assert event_dict["event_type"] == "analysis_started"
        assert event_dict["analysis_commits"] == 100
        assert event_dict["github_enriched"] is True
        # Null fields should be excluded
        assert "query_category" not in event_dict


class TestCCAAnalytics:
    """Test CCA analytics tracker"""

    def test_initialization(self, temp_analytics_dir):
        """Test analytics initialization"""
        analytics = CCAAnalytics(base_dir=temp_analytics_dir)

        assert analytics.cca_dir.exists()
        assert analytics.events_file.parent.exists()

    def test_record_event_disabled(self, analytics):
        """Test event recording when telemetry is disabled"""
        # Analytics disabled by default
        assert not analytics.is_enabled()

        event = CCAEvent(
            timestamp=time.time(),
            event_type="query_executed",
            query_category=QueryCategory.ONBOARDING.value
        )

        # Should not record when disabled
        analytics.record_event(event)
        assert not analytics.events_file.exists()

    def test_analysis_events(self, analytics, temp_analytics_dir):
        """Test analysis start/completion tracking"""
        # Enable telemetry
        config_file = temp_analytics_dir / "config.json"
        config_file.write_text(json.dumps({"enabled": True}))

        analytics.analysis_started(commits_count=150, github_enriched=True)
        time.sleep(0.1)  # Simulate analysis time
        analytics.analysis_completed(commits_count=150, github_enriched=True)

        # Verify events recorded
        events = analytics.load_events()
        assert len(events) == 2
        assert events[0]["event_type"] == "analysis_started"
        assert events[0]["analysis_commits"] == 150
        assert events[1]["event_type"] == "analysis_completed"

    def test_query_events(self, analytics, temp_analytics_dir):
        """Test query execution tracking"""
        # Enable telemetry
        config_file = temp_analytics_dir / "config.json"
        config_file.write_text(json.dumps({"enabled": True}))

        analytics.query_executed(
            category=QueryCategory.TECHNICAL_DEBT,
            response_time_seconds=2.5,
            confidence=0.88,
            credibility=0.92,
            citation_count=4,
            estimated_time_saved_minutes=90
        )

        events = analytics.load_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "query_executed"
        assert events[0]["query_category"] == QueryCategory.TECHNICAL_DEBT.value
        assert events[0]["answer_confidence"] == 0.88
        assert events[0]["citation_count"] == 4
        assert events[0]["estimated_time_saved_minutes"] == 90

    def test_user_feedback(self, analytics, temp_analytics_dir):
        """Test user feedback tracking"""
        # Enable telemetry
        config_file = temp_analytics_dir / "config.json"
        config_file.write_text(json.dumps({"enabled": True}))

        analytics.user_feedback(
            satisfied=True,
            query_category=QueryCategory.ONBOARDING
        )

        events = analytics.load_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "user_feedback"
        assert events[0]["user_satisfied"] is True

    def test_export_events(self, analytics, temp_analytics_dir):
        """Test export generation tracking"""
        # Enable telemetry
        config_file = temp_analytics_dir / "config.json"
        config_file.write_text(json.dumps({"enabled": True}))

        analytics.export_generated(format="markdown", query_count=5)

        events = analytics.load_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "export_generated"
        assert events[0]["export_format"] == "markdown"

    def test_query_categorization(self, analytics):
        """Test query categorization logic"""
        # Architecture decisions
        category = analytics._categorize_query("Why did we choose PostgreSQL?")
        assert category == QueryCategory.ARCHITECTURE_DECISION

        # Technical debt
        category = analytics._categorize_query("Why was this workaround implemented?")
        assert category == QueryCategory.TECHNICAL_DEBT

        # Feature evolution
        category = analytics._categorize_query("How did authentication evolve over time?")
        assert category == QueryCategory.FEATURE_EVOLUTION

        # Team knowledge
        category = analytics._categorize_query("Who made the decision to refactor?")
        assert category == QueryCategory.TEAM_KNOWLEDGE

        # Bug investigation
        category = analytics._categorize_query("Why did this bug occur?")
        assert category == QueryCategory.BUG_INVESTIGATION

        # Onboarding
        category = analytics._categorize_query("What is the architecture overview?")
        assert category == QueryCategory.ONBOARDING

        # Other
        category = analytics._categorize_query("Random question")
        assert category == QueryCategory.OTHER


class TestAnalyticsSummary:
    """Test analytics summary generation"""

    def test_empty_summary(self, analytics):
        """Test summary with no data"""
        summary = analytics.generate_summary()

        assert summary["total_events"] == 0
        assert "message" in summary

    def test_comprehensive_summary(self, analytics, temp_analytics_dir):
        """Test summary with multiple events"""
        # Enable telemetry
        config_file = temp_analytics_dir / "config.json"
        config_file.write_text(json.dumps({"enabled": True}))

        # Record various events
        analytics.analysis_started(commits_count=200, github_enriched=True)
        analytics.analysis_completed(commits_count=200, github_enriched=True)

        for _ in range(3):
            analytics.query_executed(
                category=QueryCategory.ARCHITECTURE_DECISION,
                response_time_seconds=1.5,
                confidence=0.85,
                credibility=0.90,
                citation_count=5,
                estimated_time_saved_minutes=120
            )

        analytics.query_executed(
            category=QueryCategory.TECHNICAL_DEBT,
            response_time_seconds=2.0,
            confidence=0.75,
            credibility=0.80,
            citation_count=3,
            estimated_time_saved_minutes=90
        )

        analytics.user_feedback(satisfied=True)
        analytics.user_feedback(satisfied=True)
        analytics.user_feedback(satisfied=False)

        analytics.export_generated(format="markdown", query_count=4)

        # Generate summary
        summary = analytics.generate_summary()

        # Verify overview (2 analysis + 4 queries + 3 feedback + 1 export = 10 events)
        assert summary["overview"]["total_events"] == 10
        assert summary["overview"]["total_analyses"] == 1
        assert summary["overview"]["total_queries"] == 4
        assert summary["overview"]["total_exports"] == 1

        # Verify analysis metrics
        assert summary["analysis"]["total_commits_analyzed"] == 200
        assert summary["analysis"]["github_enrichment_rate"] == 1.0

        # Verify query metrics
        assert summary["queries"]["total_queries"] == 4
        assert QueryCategory.ARCHITECTURE_DECISION.value in summary["queries"]["by_category"]
        assert summary["queries"]["by_category"][QueryCategory.ARCHITECTURE_DECISION.value] == 3
        assert summary["queries"]["avg_confidence"] > 0
        assert summary["queries"]["avg_credibility"] > 0

        # Verify quality metrics
        assert summary["quality"]["high_confidence_queries"] > 0
        assert summary["quality"]["well_cited_queries"] > 0
        assert summary["quality"]["avg_quality_score"] > 0

        # Verify value metrics
        assert summary["value"]["total_time_saved_minutes"] == 450  # 3*120 + 90
        assert summary["value"]["total_time_saved_hours"] == 7.5
        assert summary["value"]["avg_time_saved_per_query"] == 112.5

        # Verify satisfaction
        assert summary["satisfaction"]["total_feedback"] == 3
        assert summary["satisfaction"]["satisfied_count"] == 2
        assert summary["satisfaction"]["satisfaction_rate"] == pytest.approx(2/3, 0.01)

        # Verify exports
        assert summary["exports"]["total"] == 1
        assert summary["exports"]["by_format"]["markdown"] == 1

    def test_summary_persistence(self, analytics, temp_analytics_dir):
        """Test that summary is saved to file"""
        # Enable telemetry
        config_file = temp_analytics_dir / "config.json"
        config_file.write_text(json.dumps({"enabled": True}))

        analytics.query_executed(
            category=QueryCategory.ONBOARDING,
            response_time_seconds=1.0,
            confidence=0.90,
            credibility=0.95,
            citation_count=3
        )

        summary = analytics.generate_summary()

        # Verify summary file exists
        assert analytics.summary_file.exists()

        # Verify content
        with open(analytics.summary_file) as f:
            saved_summary = json.load(f)

        assert saved_summary["overview"]["total_queries"] == 1


@pytest.mark.integration
class TestCLIIntegration:
    """Test CLI integration with analytics"""

    def test_cli_tracks_analysis(self, temp_analytics_dir):
        """Test that CLI properly tracks analysis"""
        # This test would require full CLI setup
        # Placeholder for future implementation
        pass

    def test_cli_tracks_queries(self, temp_analytics_dir):
        """Test that CLI properly tracks queries"""
        # Placeholder for future implementation
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
