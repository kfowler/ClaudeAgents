"""
CCA Analytics Integration - Track usage, performance, and value delivered.

This module extends the ClaudeAgents telemetry system with CCA-specific metrics:
- Query patterns and topics
- Answer quality (confidence, credibility, citation count)
- Performance (analysis time, query response time)
- Value delivered (time savings, ROI)
- User satisfaction with specific queries

Privacy-first design:
- No query text stored (only topics/patterns)
- No code snippets or file paths
- Aggregate metrics only
- Local-only storage
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

try:
    # Import parent telemetry module if available
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from telemetry import TelemetryCollector, TelemetryEvent
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False


class QueryCategory(Enum):
    """Categories of archaeology queries"""
    ARCHITECTURE_DECISION = "architecture_decision"  # Why was X chosen?
    TECHNICAL_DEBT = "technical_debt"  # Why was this workaround implemented?
    FEATURE_EVOLUTION = "feature_evolution"  # How did X evolve over time?
    CODE_CONTEXT = "code_context"  # What was the context for this change?
    TEAM_KNOWLEDGE = "team_knowledge"  # Who made key decisions?
    BUG_INVESTIGATION = "bug_investigation"  # Why did this bug occur?
    ONBOARDING = "onboarding"  # General understanding questions
    OTHER = "other"


@dataclass
class CCAEvent:
    """CCA-specific telemetry event"""
    timestamp: float
    event_type: str  # "analysis_started", "query_executed", "export_generated"

    # Analysis metrics
    analysis_commits: Optional[int] = None
    analysis_duration_seconds: Optional[float] = None
    github_enriched: Optional[bool] = None

    # Query metrics
    query_category: Optional[str] = None
    query_response_time: Optional[float] = None
    answer_confidence: Optional[float] = None
    answer_credibility: Optional[float] = None
    citation_count: Optional[int] = None

    # Export metrics
    export_format: Optional[str] = None  # "markdown", "html", "json"

    # Value metrics
    estimated_time_saved_minutes: Optional[int] = None
    user_satisfied: Optional[bool] = None

    # Context (non-PII)
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class CCAAnalytics:
    """
    Analytics tracker for Cognitive Code Archaeology.

    Tracks:
    1. Usage patterns (when, how often, what types of queries)
    2. Performance (analysis time, query response time)
    3. Quality (confidence scores, citation counts)
    4. Value (estimated time savings, user satisfaction)
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize CCA analytics tracker.

        Args:
            base_dir: Base directory for analytics storage (defaults to ~/.claude-telemetry/)
        """
        if base_dir is None:
            base_dir = Path.home() / ".claude-telemetry"

        self.base_dir = Path(base_dir)
        self.cca_dir = self.base_dir / "cca"
        self.events_file = self.cca_dir / "events.jsonl"
        self.summary_file = self.cca_dir / "summary.json"

        # Try to use global telemetry collector
        self.telemetry = TelemetryCollector(base_dir) if HAS_TELEMETRY else None

        self._ensure_directories()

    def _ensure_directories(self):
        """Create CCA analytics directories if they don't exist"""
        self.cca_dir.mkdir(parents=True, exist_ok=True)

    def is_enabled(self) -> bool:
        """Check if analytics is enabled (follows telemetry setting)"""
        if self.telemetry:
            # Reload config to get latest state
            self.telemetry._load_config()
            return self.telemetry.is_enabled()
        return False

    def record_event(self, event: CCAEvent):
        """Record a CCA analytics event"""
        if not self.is_enabled():
            return

        # Record to CCA-specific storage
        with open(self.events_file, 'a') as f:
            json.dump(event.to_dict(), f)
            f.write('\n')

        # Also record to global telemetry if available
        if self.telemetry and HAS_TELEMETRY:
            telemetry_event = TelemetryEvent(
                timestamp=event.timestamp,
                event_type=f"cca_{event.event_type}",
                context={
                    "analysis_commits": event.analysis_commits,
                    "query_category": event.query_category,
                    "answer_confidence": event.answer_confidence,
                }
            )
            self.telemetry.record_event(telemetry_event)

    # ==================== Analysis Events ====================

    def analysis_started(
        self,
        commits_count: int,
        github_enriched: bool = False
    ):
        """Record repository analysis start"""
        self.analysis_start_time = time.time()

        event = CCAEvent(
            timestamp=time.time(),
            event_type="analysis_started",
            analysis_commits=commits_count,
            github_enriched=github_enriched
        )
        self.record_event(event)

    def analysis_completed(self, commits_count: int, github_enriched: bool = False):
        """Record repository analysis completion"""
        duration = time.time() - self.analysis_start_time if hasattr(self, 'analysis_start_time') else None

        event = CCAEvent(
            timestamp=time.time(),
            event_type="analysis_completed",
            analysis_commits=commits_count,
            analysis_duration_seconds=duration,
            github_enriched=github_enriched
        )
        self.record_event(event)

    # ==================== Query Events ====================

    def query_executed(
        self,
        category: QueryCategory,
        response_time_seconds: float,
        confidence: float,
        credibility: float,
        citation_count: int,
        estimated_time_saved_minutes: Optional[int] = None
    ):
        """Record a query execution"""
        event = CCAEvent(
            timestamp=time.time(),
            event_type="query_executed",
            query_category=category.value,
            query_response_time=response_time_seconds,
            answer_confidence=confidence,
            answer_credibility=credibility,
            citation_count=citation_count,
            estimated_time_saved_minutes=estimated_time_saved_minutes
        )
        self.record_event(event)

    def user_feedback(
        self,
        satisfied: bool,
        query_category: Optional[QueryCategory] = None
    ):
        """Record user satisfaction feedback"""
        event = CCAEvent(
            timestamp=time.time(),
            event_type="user_feedback",
            query_category=query_category.value if query_category else None,
            user_satisfied=satisfied
        )
        self.record_event(event)

    # ==================== Export Events ====================

    def export_generated(self, format: str, query_count: int):
        """Record export generation"""
        event = CCAEvent(
            timestamp=time.time(),
            event_type="export_generated",
            export_format=format,
            context={"query_count": query_count}
        )
        self.record_event(event)

    # ==================== Analytics & Reporting ====================

    def load_events(self) -> List[Dict]:
        """Load all CCA events"""
        events = []
        if self.events_file.exists():
            with open(self.events_file, 'r') as f:
                events = [json.loads(line) for line in f if line.strip()]
        return events

    def _categorize_query(self, query_text: str) -> QueryCategory:
        """
        Categorize a query based on keywords (privacy-preserving).

        NOTE: This only categorizes, never stores query text.
        """
        query_lower = query_text.lower()

        # Team knowledge (check first - very specific)
        if any(phrase in query_lower for phrase in ["who made", "who decided", "who implemented"]):
            return QueryCategory.TEAM_KNOWLEDGE

        # Architecture decisions (very specific - "why choose/use X")
        if any(phrase in query_lower for phrase in ["why did we choose", "why choose", "why did we use"]):
            return QueryCategory.ARCHITECTURE_DECISION

        # Technical debt (specific patterns)
        if any(word in query_lower for word in ["workaround", "hack", "todo", "fixme", "technical debt", "why temporary"]):
            return QueryCategory.TECHNICAL_DEBT

        # Bug investigation (specific "why did X fail")
        if any(phrase in query_lower for phrase in ["why did", "bug occur", "why fail", "why break"]):
            return QueryCategory.BUG_INVESTIGATION

        # Feature evolution (how/when questions)
        if any(phrase in query_lower for phrase in ["how did", "evolution", "history of", "timeline", "over time"]):
            return QueryCategory.FEATURE_EVOLUTION
        if any(phrase in query_lower for phrase in ["when was", "when did"]):
            return QueryCategory.FEATURE_EVOLUTION

        # Onboarding (general "what is" questions - more general, check later)
        if any(phrase in query_lower for phrase in ["what is", "how does", "explain"]):
            return QueryCategory.ONBOARDING
        if "understand" in query_lower and "why" not in query_lower:
            return QueryCategory.ONBOARDING

        # Architecture (general architecture questions without "why choose")
        if "architecture" in query_lower and "overview" in query_lower:
            return QueryCategory.ONBOARDING  # "architecture overview" is onboarding
        if any(word in query_lower for word in ["design decision", "decision to use"]):
            return QueryCategory.ARCHITECTURE_DECISION

        return QueryCategory.OTHER

    def generate_summary(self) -> Dict:
        """Generate comprehensive analytics summary"""
        events = self.load_events()

        if not events:
            return {
                "total_events": 0,
                "message": "No CCA analytics data available yet. Enable telemetry to start tracking."
            }

        summary = {
            "overview": {
                "total_events": len(events),
                "total_analyses": 0,
                "total_queries": 0,
                "total_exports": 0,
                "period": {
                    "first_event": None,
                    "last_event": None
                }
            },
            "analysis": {
                "total_commits_analyzed": 0,
                "avg_analysis_time": 0.0,
                "github_enrichment_rate": 0.0
            },
            "queries": {
                "by_category": {},
                "avg_response_time": 0.0,
                "avg_confidence": 0.0,
                "avg_credibility": 0.0,
                "avg_citations": 0.0,
                "total_queries": 0
            },
            "quality": {
                "high_confidence_queries": 0,  # >80% confidence
                "well_cited_queries": 0,  # 3+ citations
                "avg_quality_score": 0.0  # Combined confidence + credibility
            },
            "value": {
                "total_time_saved_minutes": 0,
                "total_time_saved_hours": 0.0,
                "avg_time_saved_per_query": 0.0,
                "estimated_roi_multiplier": 0.0
            },
            "satisfaction": {
                "total_feedback": 0,
                "satisfied_count": 0,
                "satisfaction_rate": 0.0,
                "by_category": {}
            },
            "exports": {
                "total": 0,
                "by_format": {}
            }
        }

        # Track timestamps
        timestamps = [e["timestamp"] for e in events]
        summary["overview"]["period"]["first_event"] = datetime.fromtimestamp(min(timestamps)).isoformat()
        summary["overview"]["period"]["last_event"] = datetime.fromtimestamp(max(timestamps)).isoformat()

        # Analyze events
        analysis_times = []
        query_response_times = []
        confidences = []
        credibilities = []
        citations = []
        time_savings = []

        for event in events:
            event_type = event.get("event_type")

            # Analysis events
            if event_type == "analysis_completed":
                summary["overview"]["total_analyses"] += 1
                if commits := event.get("analysis_commits"):
                    summary["analysis"]["total_commits_analyzed"] += commits
                if duration := event.get("analysis_duration_seconds"):
                    analysis_times.append(duration)
                if event.get("github_enriched"):
                    summary["analysis"]["github_enrichment_rate"] += 1

            # Query events
            elif event_type == "query_executed":
                summary["overview"]["total_queries"] += 1
                summary["queries"]["total_queries"] += 1

                # Category tracking
                category = event.get("query_category", "other")
                summary["queries"]["by_category"][category] = \
                    summary["queries"]["by_category"].get(category, 0) + 1

                # Performance metrics
                if response_time := event.get("query_response_time"):
                    query_response_times.append(response_time)

                # Quality metrics
                if confidence := event.get("answer_confidence"):
                    confidences.append(confidence)
                    if confidence > 0.8:
                        summary["quality"]["high_confidence_queries"] += 1

                if credibility := event.get("answer_credibility"):
                    credibilities.append(credibility)

                if citation_count := event.get("citation_count"):
                    citations.append(citation_count)
                    if citation_count >= 3:
                        summary["quality"]["well_cited_queries"] += 1

                # Value metrics
                if time_saved := event.get("estimated_time_saved_minutes"):
                    time_savings.append(time_saved)

            # Feedback events
            elif event_type == "user_feedback":
                summary["satisfaction"]["total_feedback"] += 1
                if event.get("user_satisfied"):
                    summary["satisfaction"]["satisfied_count"] += 1

                # Category-specific satisfaction
                if category := event.get("query_category"):
                    if category not in summary["satisfaction"]["by_category"]:
                        summary["satisfaction"]["by_category"][category] = {
                            "total": 0, "satisfied": 0, "rate": 0.0
                        }
                    summary["satisfaction"]["by_category"][category]["total"] += 1
                    if event.get("user_satisfied"):
                        summary["satisfaction"]["by_category"][category]["satisfied"] += 1

            # Export events
            elif event_type == "export_generated":
                summary["overview"]["total_exports"] += 1
                summary["exports"]["total"] += 1
                export_format = event.get("export_format", "unknown")
                summary["exports"]["by_format"][export_format] = \
                    summary["exports"]["by_format"].get(export_format, 0) + 1

        # Calculate averages
        if analysis_times:
            summary["analysis"]["avg_analysis_time"] = sum(analysis_times) / len(analysis_times)

        if summary["overview"]["total_analyses"] > 0:
            summary["analysis"]["github_enrichment_rate"] = \
                summary["analysis"]["github_enrichment_rate"] / summary["overview"]["total_analyses"]

        if query_response_times:
            summary["queries"]["avg_response_time"] = sum(query_response_times) / len(query_response_times)

        if confidences:
            summary["queries"]["avg_confidence"] = sum(confidences) / len(confidences)

        if credibilities:
            summary["queries"]["avg_credibility"] = sum(credibilities) / len(credibilities)

        if citations:
            summary["queries"]["avg_citations"] = sum(citations) / len(citations)

        # Quality score (combined confidence + credibility)
        if confidences and credibilities:
            summary["quality"]["avg_quality_score"] = \
                (summary["queries"]["avg_confidence"] + summary["queries"]["avg_credibility"]) / 2

        # Value calculations
        if time_savings:
            total_minutes = sum(time_savings)
            summary["value"]["total_time_saved_minutes"] = total_minutes
            summary["value"]["total_time_saved_hours"] = total_minutes / 60
            summary["value"]["avg_time_saved_per_query"] = total_minutes / len(time_savings)

            # ROI multiplier: time saved vs time spent (rough estimate)
            total_time_spent = sum(analysis_times) / 60 + sum(query_response_times) / 60  # Convert to minutes
            if total_time_spent > 0:
                summary["value"]["estimated_roi_multiplier"] = total_minutes / total_time_spent

        # Satisfaction rate
        if summary["satisfaction"]["total_feedback"] > 0:
            summary["satisfaction"]["satisfaction_rate"] = \
                summary["satisfaction"]["satisfied_count"] / summary["satisfaction"]["total_feedback"]

        # Category-specific satisfaction rates
        for category, stats in summary["satisfaction"]["by_category"].items():
            if stats["total"] > 0:
                stats["rate"] = stats["satisfied"] / stats["total"]

        # Save summary
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def print_summary(self):
        """Print formatted analytics summary to console"""
        summary = self.generate_summary()

        if summary.get("total_events") == 0:
            print("\n" + "="*70)
            print("COGNITIVE CODE ARCHAEOLOGY ANALYTICS")
            print("="*70)
            print("\n📊 No data available yet.")
            print("\n💡 Enable telemetry to start tracking CCA usage:")
            print("   python3 tools/telemetry.py enable")
            print("\n" + "="*70 + "\n")
            return

        print("\n" + "="*70)
        print("COGNITIVE CODE ARCHAEOLOGY ANALYTICS")
        print("="*70)

        # Overview
        print(f"\n📊 Overview:")
        overview = summary["overview"]
        print(f"  • Total events: {overview['total_events']}")
        print(f"  • Analyses run: {overview['total_analyses']}")
        print(f"  • Queries executed: {overview['total_queries']}")
        print(f"  • Exports generated: {overview['total_exports']}")
        print(f"  • Period: {overview['period']['first_event']} to {overview['period']['last_event']}")

        # Analysis metrics
        print(f"\n🔍 Analysis Performance:")
        analysis = summary["analysis"]
        print(f"  • Total commits analyzed: {analysis['total_commits_analyzed']:,}")
        print(f"  • Avg analysis time: {analysis['avg_analysis_time']:.1f}s")
        print(f"  • GitHub enrichment rate: {analysis['github_enrichment_rate']*100:.1f}%")

        # Query patterns
        print(f"\n❓ Query Patterns:")
        queries = summary["queries"]
        if queries["by_category"]:
            for category, count in sorted(queries["by_category"].items(), key=lambda x: x[1], reverse=True):
                print(f"  • {category.replace('_', ' ').title()}: {count} queries")
        print(f"  • Avg response time: {queries['avg_response_time']:.2f}s")

        # Quality metrics
        print(f"\n⭐ Quality Metrics:")
        quality = summary["quality"]
        print(f"  • Avg confidence: {queries['avg_confidence']*100:.1f}%")
        print(f"  • Avg credibility: {queries['avg_credibility']*100:.1f}%")
        print(f"  • Avg quality score: {quality['avg_quality_score']*100:.1f}%")
        print(f"  • Avg citations per answer: {queries['avg_citations']:.1f}")
        print(f"  • High-confidence queries (>80%): {quality['high_confidence_queries']}")
        print(f"  • Well-cited queries (3+ citations): {quality['well_cited_queries']}")

        # Value delivered
        print(f"\n💰 Value Delivered:")
        value = summary["value"]
        if value["total_time_saved_minutes"] > 0:
            print(f"  • Total time saved: {value['total_time_saved_hours']:.1f} hours ({value['total_time_saved_minutes']} minutes)")
            print(f"  • Avg time saved per query: {value['avg_time_saved_per_query']:.1f} minutes")
            print(f"  • Estimated ROI: {value['estimated_roi_multiplier']:.1f}x")
        else:
            print(f"  • No time savings data available yet")

        # User satisfaction
        print(f"\n😊 User Satisfaction:")
        satisfaction = summary["satisfaction"]
        if satisfaction["total_feedback"] > 0:
            print(f"  • Feedback received: {satisfaction['total_feedback']}")
            print(f"  • Satisfied: {satisfaction['satisfied_count']}")
            print(f"  • Satisfaction rate: {satisfaction['satisfaction_rate']*100:.1f}%")

            if satisfaction["by_category"]:
                print(f"\n  By category:")
                for category, stats in sorted(satisfaction["by_category"].items(), key=lambda x: x[1]["rate"], reverse=True):
                    print(f"    • {category.replace('_', ' ').title()}: {stats['rate']*100:.1f}% ({stats['satisfied']}/{stats['total']})")
        else:
            print(f"  • No feedback received yet")

        # Exports
        print(f"\n📤 Exports:")
        exports = summary["exports"]
        if exports["total"] > 0:
            print(f"  • Total exports: {exports['total']}")
            for format, count in exports["by_format"].items():
                print(f"    • {format}: {count}")
        else:
            print(f"  • No exports generated yet")

        print("\n" + "="*70 + "\n")


# Convenience function for CLI integration
def get_cca_analytics() -> CCAAnalytics:
    """Get CCA analytics instance (singleton pattern)"""
    if not hasattr(get_cca_analytics, '_instance'):
        get_cca_analytics._instance = CCAAnalytics()
    return get_cca_analytics._instance


def main():
    """CLI interface for CCA analytics"""
    import sys

    analytics = get_cca_analytics()

    if len(sys.argv) < 2:
        print("Usage: python analytics.py [summary|status]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "summary":
        analytics.print_summary()
    elif command == "status":
        print(f"CCA Analytics: {'✅ Enabled' if analytics.is_enabled() else '🔕 Disabled'}")
        print(f"Data directory: {analytics.cca_dir}")
        if analytics.is_enabled():
            print(f"\n💡 View analytics: python3 tools/code_archaeology/analytics.py summary")
        else:
            print(f"\n💡 Enable telemetry first: python3 tools/telemetry.py enable")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
