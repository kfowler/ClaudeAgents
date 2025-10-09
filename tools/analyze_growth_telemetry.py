#!/usr/bin/env python3
"""
Growth Commands Telemetry Analyzer

Analyzes privacy-preserving usage logs to inform validation decisions.
Run this script to generate usage reports for growth command validation.

Usage:
    python3 tools/analyze_growth_telemetry.py
    python3 tools/analyze_growth_telemetry.py --command conversion-audit
    python3 tools/analyze_growth_telemetry.py --export report.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any


class GrowthTelemetryAnalyzer:
    """Analyzes growth command telemetry data for validation decisions."""

    COMMANDS = [
        "conversion-audit",
        "viral-loop",
        "retention-playbook",
        "metrics-setup",
        "experiment-design"
    ]

    def __init__(self, telemetry_dir: Path):
        self.telemetry_dir = telemetry_dir
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, List[Dict]]:
        """Load all telemetry log files."""
        data = {}
        for command in self.COMMANDS:
            log_file = self.telemetry_dir / f"{command}.log"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    data[command] = [json.loads(line) for line in f if line.strip()]
            else:
                data[command] = []
        return data

    def get_command_stats(self, command: str) -> Dict[str, Any]:
        """Calculate statistics for a specific command."""
        events = self.data.get(command, [])

        if not events:
            return {
                "command": f"growth:{command}",
                "total_events": 0,
                "invocations": 0,
                "completed": 0,
                "failed": 0,
                "partial": 0,
                "unique_sessions": 0,
                "completion_rate": 0.0,
                "avg_execution_time": 0.0,
                "avg_phases_completed": 0.0
            }

        # Count by status
        status_counts = defaultdict(int)
        for event in events:
            status_counts[event.get("status")] += 1

        # Calculate unique sessions
        sessions = set(event.get("session_id") for event in events)

        # Calculate started invocations (actual command runs)
        invocations = status_counts["started"]

        # Calculate completion rate
        completed = status_counts["completed"]
        completion_rate = (completed / invocations * 100) if invocations > 0 else 0.0

        # Calculate average execution time (from completed/failed/partial events)
        execution_times = [
            event.get("execution_time_minutes", 0)
            for event in events
            if event.get("execution_time_minutes") is not None
        ]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0

        # Calculate average phases completed
        phases = [
            event.get("phases_completed", 0)
            for event in events
            if event.get("phases_completed") is not None
        ]
        avg_phases = sum(phases) / len(phases) if phases else 0.0

        return {
            "command": f"growth:{command}",
            "total_events": len(events),
            "invocations": invocations,
            "completed": completed,
            "failed": status_counts["failed"],
            "partial": status_counts["partial"],
            "unique_sessions": len(sessions),
            "completion_rate": round(completion_rate, 1),
            "avg_execution_time": round(avg_execution_time, 1),
            "avg_phases_completed": round(avg_phases, 1)
        }

    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Calculate aggregate statistics across all commands."""
        all_stats = [self.get_command_stats(cmd) for cmd in self.COMMANDS]

        total_invocations = sum(s["invocations"] for s in all_stats)
        total_completed = sum(s["completed"] for s in all_stats)
        total_unique_sessions = len(set(
            event.get("session_id")
            for command_events in self.data.values()
            for event in command_events
        ))

        overall_completion_rate = (
            total_completed / total_invocations * 100
            if total_invocations > 0 else 0.0
        )

        # Get most and least popular commands
        by_invocations = sorted(all_stats, key=lambda x: x["invocations"], reverse=True)
        most_popular = by_invocations[0] if by_invocations else None
        least_popular = by_invocations[-1] if by_invocations else None

        return {
            "total_invocations": total_invocations,
            "total_completed": total_completed,
            "total_unique_sessions": total_unique_sessions,
            "overall_completion_rate": round(overall_completion_rate, 1),
            "most_popular_command": most_popular["command"] if most_popular else None,
            "least_popular_command": least_popular["command"] if least_popular else None,
            "by_command": all_stats
        }

    def assess_validation_status(self) -> Dict[str, Any]:
        """Assess validation experiment status against success criteria."""
        aggregate = self.get_aggregate_stats()

        total_invocations = aggregate["total_invocations"]
        unique_users = aggregate["total_unique_sessions"]
        completion_rate = aggregate["overall_completion_rate"]

        # Decision criteria from README.md
        if total_invocations >= 20 and unique_users >= 10 and completion_rate >= 70:
            decision = "BUILD"
            recommendation = "Strong demand validated. Build dedicated growth-engineer agent."
        elif total_invocations >= 10:
            decision = "ITERATE"
            recommendation = "Moderate demand. Iterate on command design and extend validation period."
        else:
            decision = "DEPRECATE"
            recommendation = "Low demand. Deprioritize growth features, focus on other domains."

        return {
            "validation_status": decision,
            "recommendation": recommendation,
            "criteria": {
                "total_invocations": {
                    "value": total_invocations,
                    "threshold": "20+ (strong) | 10-19 (moderate) | <10 (low)",
                    "status": "✓" if total_invocations >= 20 else ("~" if total_invocations >= 10 else "✗")
                },
                "unique_users": {
                    "value": unique_users,
                    "threshold": "10+ (strong) | 5-9 (moderate) | <5 (low)",
                    "status": "✓" if unique_users >= 10 else ("~" if unique_users >= 5 else "✗")
                },
                "completion_rate": {
                    "value": f"{completion_rate}%",
                    "threshold": "70%+ (strong) | 50-69% (moderate) | <50% (low)",
                    "status": "✓" if completion_rate >= 70 else ("~" if completion_rate >= 50 else "✗")
                }
            }
        }

    def generate_report(self) -> str:
        """Generate human-readable validation report."""
        aggregate = self.get_aggregate_stats()
        validation = self.assess_validation_status()

        report = []
        report.append("=" * 70)
        report.append("GROWTH COMMANDS VALIDATION REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Overall metrics
        report.append("OVERALL METRICS")
        report.append("-" * 70)
        report.append(f"Total Invocations:     {aggregate['total_invocations']}")
        report.append(f"Completed:             {aggregate['total_completed']}")
        report.append(f"Unique Sessions:       {aggregate['total_unique_sessions']}")
        report.append(f"Completion Rate:       {aggregate['overall_completion_rate']}%")
        report.append(f"Most Popular:          {aggregate['most_popular_command']}")
        report.append("")

        # By command
        report.append("BY COMMAND")
        report.append("-" * 70)
        for cmd_stats in aggregate["by_command"]:
            report.append(f"\n{cmd_stats['command']}")
            report.append(f"  Invocations:         {cmd_stats['invocations']}")
            report.append(f"  Completed:           {cmd_stats['completed']}")
            report.append(f"  Failed:              {cmd_stats['failed']}")
            report.append(f"  Partial:             {cmd_stats['partial']}")
            report.append(f"  Completion Rate:     {cmd_stats['completion_rate']}%")
            report.append(f"  Avg Execution Time:  {cmd_stats['avg_execution_time']} min")
            report.append(f"  Avg Phases Done:     {cmd_stats['avg_phases_completed']}")

        report.append("")
        report.append("VALIDATION ASSESSMENT")
        report.append("-" * 70)
        report.append(f"Decision:              {validation['validation_status']}")
        report.append(f"Recommendation:        {validation['recommendation']}")
        report.append("")
        report.append("Success Criteria:")
        for criterion, data in validation["criteria"].items():
            status_symbol = data["status"]
            report.append(f"  [{status_symbol}] {criterion}: {data['value']} (threshold: {data['threshold']})")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def export_json(self, output_file: Path):
        """Export full analysis as JSON."""
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "aggregate": self.get_aggregate_stats(),
            "validation": self.assess_validation_status(),
            "raw_events": self.data
        }

        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze growth command telemetry for validation"
    )
    parser.add_argument(
        "--command",
        help="Analyze specific command only",
        choices=GrowthTelemetryAnalyzer.COMMANDS
    )
    parser.add_argument(
        "--export",
        help="Export analysis to JSON file",
        type=Path
    )

    args = parser.parse_args()

    # Find telemetry directory
    project_root = Path(__file__).parent.parent
    telemetry_dir = project_root / ".claude-telemetry" / "growth"

    if not telemetry_dir.exists():
        print(f"Warning: Telemetry directory not found at {telemetry_dir}")
        print("Creating directory for future use...")
        telemetry_dir.mkdir(parents=True, exist_ok=True)
        print("\nNo telemetry data available yet. Run some growth commands first!")
        return

    analyzer = GrowthTelemetryAnalyzer(telemetry_dir)

    if args.command:
        # Show stats for specific command
        stats = analyzer.get_command_stats(args.command)
        print(json.dumps(stats, indent=2))
    else:
        # Show full report
        report = analyzer.generate_report()
        print(report)

    if args.export:
        analyzer.export_json(args.export)


if __name__ == "__main__":
    main()
