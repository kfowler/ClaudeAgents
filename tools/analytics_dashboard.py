#!/usr/bin/env python3
"""
ClaudeAgents Analytics Dashboard

Provides comprehensive visualization and analysis of agent usage patterns,
performance trends, and quality metrics from telemetry data.

Features:
- Agent usage ranking and tier analysis
- Performance trend visualization (text-based)
- Quality metrics (success rate, satisfaction, failure analysis)
- Emergence candidate identification
- Tier promotion/demotion recommendations
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass

try:
    from telemetry import TelemetryCollector, EventType
    from agent_emergence import AgentEmergenceTracker
    from intelligent_orchestrator import TierManager, AgentTier
except ImportError:
    print("Error: Required modules not found. Run from tools/ directory.")
    import sys
    sys.exit(1)


@dataclass
class AgentMetrics:
    """Comprehensive metrics for a single agent"""
    name: str
    tier: AgentTier
    invocations: int
    completions: int
    failures: int
    success_rate: float
    avg_duration: float
    satisfaction_score: Optional[float]
    trend: str  # "improving", "stable", "degrading"
    recommendation: Optional[str]  # tier movement recommendation


class AnalyticsDashboard:
    """
    Comprehensive analytics dashboard for ClaudeAgents.

    Combines data from:
    - Telemetry (usage, performance, satisfaction)
    - Emergence tracking (composite patterns)
    - Tier system (quality assignments)
    """

    def __init__(self):
        """Initialize analytics dashboard"""
        self.telemetry = TelemetryCollector()
        self.emergence = AgentEmergenceTracker()

    def generate_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        if not self.telemetry.is_enabled():
            return {
                "error": "Telemetry not enabled. Enable with: python telemetry.py enable"
            }

        summary = self.telemetry.generate_summary()

        report = {
            "generated_at": datetime.now().isoformat(),
            "overview": self._overview_metrics(summary),
            "agent_rankings": self._agent_rankings(summary),
            "tier_analysis": self._tier_analysis(summary),
            "performance_trends": self._performance_trends(summary),
            "quality_metrics": self._quality_metrics(summary),
            "emergence_insights": self._emergence_insights(),
            "recommendations": self._generate_recommendations(summary)
        }

        return report

    def _overview_metrics(self, summary: Dict) -> Dict:
        """High-level overview metrics"""
        return {
            "total_events": summary["total_events"],
            "unique_agents": len(summary["agents"]),
            "period_start": summary["period"]["first_event"],
            "period_end": summary["period"]["last_event"],
            "avg_performance": summary["performance"]["avg_duration"],
            "satisfaction_rate": summary["satisfaction"]["satisfaction_rate"]
        }

    def _agent_rankings(self, summary: Dict) -> List[Dict]:
        """Rank agents by usage and quality"""
        rankings = []

        for agent_name, stats in summary["agents"].items():
            tier = TierManager.get_tier(agent_name)
            success_rate = (
                (stats["completions"] / stats["invocations"] * 100)
                if stats["invocations"] > 0 else 0
            )

            rankings.append({
                "name": agent_name,
                "tier": tier.name,
                "invocations": stats["invocations"],
                "success_rate": success_rate,
                "avg_duration": stats["avg_duration"]
            })

        # Sort by invocations (most-used first)
        rankings.sort(key=lambda x: x["invocations"], reverse=True)

        return rankings

    def _tier_analysis(self, summary: Dict) -> Dict:
        """Analyze agent distribution across tiers"""
        tier_stats = {
            "CORE": {"count": 0, "invocations": 0, "avg_success": 0.0},
            "EXTENDED": {"count": 0, "invocations": 0, "avg_success": 0.0},
            "EXPERIMENTAL": {"count": 0, "invocations": 0, "avg_success": 0.0},
            "UNKNOWN": {"count": 0, "invocations": 0, "avg_success": 0.0}
        }

        for agent_name, stats in summary["agents"].items():
            tier = TierManager.get_tier(agent_name)
            tier_name = tier.name

            tier_stats[tier_name]["count"] += 1
            tier_stats[tier_name]["invocations"] += stats["invocations"]

            success_rate = (
                (stats["completions"] / stats["invocations"])
                if stats["invocations"] > 0 else 0
            )
            tier_stats[tier_name]["avg_success"] += success_rate

        # Calculate averages
        for tier_name, stats in tier_stats.items():
            if stats["count"] > 0:
                stats["avg_success"] = stats["avg_success"] / stats["count"]

        return tier_stats

    def _performance_trends(self, summary: Dict) -> Dict:
        """Analyze performance trends"""
        perf = summary["performance"]

        trends = {
            "overall": {
                "avg": perf["avg_duration"],
                "median": perf["median_duration"],
                "p95": perf["p95_duration"],
                "p99": perf["p99_duration"]
            },
            "fastest_agents": [],
            "slowest_agents": [],
            "outliers": []
        }

        # Identify fastest and slowest agents
        agent_durations = [
            (name, stats["avg_duration"])
            for name, stats in summary["agents"].items()
            if stats["avg_duration"] > 0
        ]
        agent_durations.sort(key=lambda x: x[1])

        if agent_durations:
            # Top 5 fastest
            trends["fastest_agents"] = [
                {"name": name, "duration": dur}
                for name, dur in agent_durations[:5]
            ]

            # Top 5 slowest
            trends["slowest_agents"] = [
                {"name": name, "duration": dur}
                for name, dur in agent_durations[-5:]
            ]

            # Outliers (agents > 2x p95)
            p95_threshold = perf["p95_duration"] * 2
            trends["outliers"] = [
                {"name": name, "duration": dur}
                for name, dur in agent_durations
                if dur > p95_threshold
            ]

        return trends

    def _quality_metrics(self, summary: Dict) -> Dict:
        """Analyze quality metrics"""
        quality = {
            "high_performers": [],  # >95% success rate
            "underperformers": [],  # <75% success rate
            "satisfaction": summary["satisfaction"],
            "failure_analysis": {}
        }

        for agent_name, stats in summary["agents"].items():
            success_rate = (
                (stats["completions"] / stats["invocations"])
                if stats["invocations"] > 0 else 0
            )

            if success_rate >= 0.95 and stats["invocations"] >= 5:
                quality["high_performers"].append({
                    "name": agent_name,
                    "success_rate": success_rate * 100,
                    "invocations": stats["invocations"]
                })
            elif success_rate < 0.75 and stats["invocations"] >= 5:
                quality["underperformers"].append({
                    "name": agent_name,
                    "success_rate": success_rate * 100,
                    "invocations": stats["invocations"],
                    "failures": stats["failures"]
                })

        # Sort by success rate
        quality["high_performers"].sort(key=lambda x: x["success_rate"], reverse=True)
        quality["underperformers"].sort(key=lambda x: x["success_rate"])

        return quality

    def _emergence_insights(self) -> Dict:
        """Get insights from emergence tracking"""
        top_patterns = self.emergence.get_top_patterns(5)
        candidates = self.emergence.get_promotion_candidates()
        emergent = self.emergence.get_emergent_agents("proposed")

        return {
            "top_patterns": [
                {
                    "agents": list(p.agent_combination),
                    "frequency": p.frequency,
                    "satisfaction": p.avg_satisfaction,
                    "promoted": p.promoted
                }
                for p in top_patterns
            ],
            "promotion_candidates": len(candidates),
            "proposed_emergent": len(emergent)
        }

    def _generate_recommendations(self, summary: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []

        # Tier promotion recommendations
        for agent_name, stats in summary["agents"].items():
            tier = TierManager.get_tier(agent_name)
            success_rate = (
                (stats["completions"] / stats["invocations"])
                if stats["invocations"] > 0 else 0
            )

            # Check for promotion to Core
            if tier == AgentTier.EXTENDED and stats["invocations"] >= 50 and success_rate >= 0.90:
                recommendations.append({
                    "type": "tier_promotion",
                    "agent": agent_name,
                    "current_tier": "EXTENDED",
                    "recommended_tier": "CORE",
                    "reason": f"{stats['invocations']} uses, {success_rate*100:.1f}% success rate",
                    "priority": "high"
                })

            # Check for demotion from Core
            elif tier == AgentTier.CORE and success_rate < 0.85:
                recommendations.append({
                    "type": "tier_demotion",
                    "agent": agent_name,
                    "current_tier": "CORE",
                    "recommended_tier": "EXTENDED",
                    "reason": f"Success rate {success_rate*100:.1f}% below 85% threshold",
                    "priority": "medium"
                })

        # Performance optimization recommendations
        perf = summary["performance"]
        if perf.get("slowest_agent"):
            slowest = perf["slowest_agent"]
            if slowest["avg_duration"] > perf["p95_duration"] * 1.5:
                recommendations.append({
                    "type": "performance_optimization",
                    "agent": slowest["name"],
                    "reason": f"Avg duration {slowest['avg_duration']:.1f}s >> p95 {perf['p95_duration']:.1f}s",
                    "priority": "medium"
                })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order[x["priority"]])

        return recommendations

    def print_dashboard(self):
        """Print formatted analytics dashboard"""
        report = self.generate_report()

        if "error" in report:
            print(f"\n❌ {report['error']}\n")
            return

        print("\n" + "="*70)
        print("CLAUDEAGENTS ANALYTICS DASHBOARD")
        print("="*70)

        # Overview
        overview = report["overview"]
        print(f"\n📊 Overview:")
        print(f"  • Period: {overview['period_start']} to {overview['period_end']}")
        print(f"  • Total events: {overview['total_events']}")
        print(f"  • Unique agents: {overview['unique_agents']}")
        print(f"  • Avg performance: {overview['avg_performance']:.1f}s")
        print(f"  • Satisfaction rate: {overview['satisfaction_rate']*100:.1f}%")

        # Top agents
        print(f"\n🏆 Top 10 Most-Used Agents:")
        for i, agent in enumerate(report["agent_rankings"][:10], 1):
            tier_badge = {"CORE": "⭐", "EXTENDED": "✓", "EXPERIMENTAL": "🧪", "UNKNOWN": "?"}[agent["tier"]]
            print(f"  {i}. {tier_badge} {agent['name']}")
            print(f"     Uses: {agent['invocations']}, Success: {agent['success_rate']:.1f}%, "
                  f"Avg: {agent['avg_duration']:.1f}s")

        # Tier analysis
        print(f"\n📊 Tier Distribution:")
        tier_analysis = report["tier_analysis"]
        for tier_name in ["CORE", "EXTENDED", "EXPERIMENTAL"]:
            stats = tier_analysis[tier_name]
            if stats["count"] > 0:
                print(f"  • {tier_name}: {stats['count']} agents, "
                      f"{stats['invocations']} uses, "
                      f"{stats['avg_success']*100:.1f}% avg success")

        # Performance trends
        print(f"\n⚡ Performance Trends:")
        trends = report["performance_trends"]
        overall = trends["overall"]
        print(f"  • Average: {overall['avg']:.1f}s")
        print(f"  • Median (p50): {overall['median']:.1f}s")
        print(f"  • p95: {overall['p95']:.1f}s, p99: {overall['p99']:.1f}s")

        if trends["fastest_agents"]:
            fastest = trends["fastest_agents"][0]
            print(f"  • Fastest: {fastest['name']} ({fastest['duration']:.1f}s)")

        if trends["slowest_agents"]:
            slowest = trends["slowest_agents"][-1]
            print(f"  • Slowest: {slowest['name']} ({slowest['duration']:.1f}s)")

        # Quality metrics
        print(f"\n✨ Quality Metrics:")
        quality = report["quality_metrics"]
        print(f"  • High performers (>95% success): {len(quality['high_performers'])}")
        if quality["high_performers"]:
            for agent in quality["high_performers"][:3]:
                print(f"    - {agent['name']}: {agent['success_rate']:.1f}% ({agent['invocations']} uses)")

        if quality["underperformers"]:
            print(f"  • Underperformers (<75% success): {len(quality['underperformers'])}")
            for agent in quality["underperformers"][:3]:
                print(f"    - {agent['name']}: {agent['success_rate']:.1f}% "
                      f"({agent['failures']} failures)")

        # Emergence insights
        print(f"\n🌱 Emergence Tracking:")
        emergence = report["emergence_insights"]
        print(f"  • Top composite patterns: {len(emergence['top_patterns'])}")
        for pattern in emergence["top_patterns"][:3]:
            print(f"    - {' + '.join(pattern['agents'])}: {pattern['frequency']} uses, "
                  f"{pattern['satisfaction']*100:.1f}% satisfaction")
        print(f"  • Promotion candidates: {emergence['promotion_candidates']}")
        print(f"  • Proposed emergent agents: {emergence['proposed_emergent']}")

        # Recommendations
        print(f"\n💡 Recommendations:")
        recommendations = report["recommendations"]
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec["priority"]]
                print(f"  {i}. {priority_emoji} {rec['type']}: {rec['agent']}")
                print(f"     {rec['reason']}")
        else:
            print(f"  • No recommendations at this time")

        print("\n" + "="*70 + "\n")


def main():
    """CLI interface for analytics dashboard"""
    import sys

    dashboard = AnalyticsDashboard()

    if len(sys.argv) > 1 and sys.argv[1] == "json":
        # Output JSON report
        report = dashboard.generate_report()
        print(json.dumps(report, indent=2))
    else:
        # Print formatted dashboard
        dashboard.print_dashboard()


if __name__ == "__main__":
    main()
