#!/usr/bin/env python3
"""
ClaudeAgents Telemetry Framework

Lightweight telemetry system for tracking agent usage, success rates,
and user satisfaction without compromising privacy.

Design Principles:
- Privacy-first: No PII, no code snippets, aggregate metrics only
- Opt-in: Disabled by default, user must enable
- Transparent: Clear documentation of what's collected
- Local-first: Data stored locally in .claude-telemetry/
- Simple: Plain JSON files, no databases required
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    """Types of telemetry events we track"""
    AGENT_INVOKED = "agent_invoked"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    COMMAND_INVOKED = "command_invoked"
    COMMAND_COMPLETED = "command_completed"
    USER_FEEDBACK = "user_feedback"


class Outcome(Enum):
    """Task outcome classifications"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ABANDONED = "abandoned"


@dataclass
class TelemetryEvent:
    """Individual telemetry event"""
    timestamp: float
    event_type: str
    agent_name: Optional[str] = None
    command_name: Optional[str] = None
    outcome: Optional[str] = None
    duration_seconds: Optional[float] = None
    user_satisfied: Optional[bool] = None
    error_category: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class TelemetryCollector:
    """
    Collects and persists telemetry events.

    Storage structure:
    .claude-telemetry/
      ├── events/
      │   ├── 2025-10-07.jsonl  # Daily event logs
      │   └── 2025-10-08.jsonl
      ├── config.json            # User preferences
      └── summary.json           # Aggregated metrics
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize telemetry collector"""
        if base_dir is None:
            # Default to user's home directory
            base_dir = Path.home() / ".claude-telemetry"

        self.base_dir = Path(base_dir)
        self.events_dir = self.base_dir / "events"
        self.config_file = self.base_dir / "config.json"
        self.summary_file = self.base_dir / "summary.json"

        self._ensure_directories()
        self._load_config()

    def _ensure_directories(self):
        """Create telemetry directories if they don't exist"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(exist_ok=True)

    def _load_config(self):
        """Load telemetry configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "enabled": False,  # Opt-in by default
                "version": "1.0",
                "created_at": datetime.now().isoformat()
            }
            self._save_config()

    def _save_config(self):
        """Save telemetry configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def is_enabled(self) -> bool:
        """Check if telemetry is enabled"""
        return self.config.get("enabled", False)

    def enable(self):
        """Enable telemetry collection"""
        self.config["enabled"] = True
        self.config["enabled_at"] = datetime.now().isoformat()
        self._save_config()
        print("✅ Telemetry enabled. Data stored in:", self.base_dir)

    def disable(self):
        """Disable telemetry collection"""
        self.config["enabled"] = False
        self.config["disabled_at"] = datetime.now().isoformat()
        self._save_config()
        print("🔕 Telemetry disabled")

    def record_event(self, event: TelemetryEvent):
        """Record a telemetry event"""
        if not self.is_enabled():
            return

        # Get today's event file
        today = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d")
        event_file = self.events_dir / f"{today}.jsonl"

        # Append event as JSON line
        with open(event_file, 'a') as f:
            json.dump(event.to_dict(), f)
            f.write('\n')

    def agent_invoked(self, agent_name: str, context: Optional[Dict] = None):
        """Record agent invocation"""
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type=EventType.AGENT_INVOKED.value,
            agent_name=agent_name,
            context=context
        )
        self.record_event(event)

    def agent_completed(
        self,
        agent_name: str,
        outcome: Outcome,
        duration_seconds: float,
        error_category: Optional[str] = None
    ):
        """Record agent completion"""
        event_type = (
            EventType.AGENT_COMPLETED if outcome == Outcome.SUCCESS
            else EventType.AGENT_FAILED
        )

        event = TelemetryEvent(
            timestamp=time.time(),
            event_type=event_type.value,
            agent_name=agent_name,
            outcome=outcome.value,
            duration_seconds=duration_seconds,
            error_category=error_category
        )
        self.record_event(event)

    def command_invoked(self, command_name: str, context: Optional[Dict] = None):
        """Record command invocation"""
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type=EventType.COMMAND_INVOKED.value,
            command_name=command_name,
            context=context
        )
        self.record_event(event)

    def user_feedback(self, satisfied: bool, agent_name: Optional[str] = None):
        """Record user satisfaction feedback"""
        event = TelemetryEvent(
            timestamp=time.time(),
            event_type=EventType.USER_FEEDBACK.value,
            agent_name=agent_name,
            user_satisfied=satisfied
        )
        self.record_event(event)

    def load_events(self, date: Optional[str] = None) -> List[Dict]:
        """Load events for a specific date or all events"""
        events = []

        if date:
            # Load specific date
            event_file = self.events_dir / f"{date}.jsonl"
            if event_file.exists():
                with open(event_file, 'r') as f:
                    events = [json.loads(line) for line in f]
        else:
            # Load all events
            for event_file in sorted(self.events_dir.glob("*.jsonl")):
                with open(event_file, 'r') as f:
                    events.extend([json.loads(line) for line in f])

        return events

    def generate_summary(self) -> Dict:
        """Generate summary statistics from all events"""
        events = self.load_events()

        summary = {
            "total_events": len(events),
            "agents": {},
            "commands": {},
            "satisfaction": {
                "total_feedback": 0,
                "satisfied_count": 0,
                "satisfaction_rate": 0.0
            },
            "period": {
                "first_event": None,
                "last_event": None
            }
        }

        if not events:
            return summary

        # Track timestamps
        timestamps = [e["timestamp"] for e in events]
        summary["period"]["first_event"] = datetime.fromtimestamp(min(timestamps)).isoformat()
        summary["period"]["last_event"] = datetime.fromtimestamp(max(timestamps)).isoformat()

        # Analyze events
        for event in events:
            # Agent statistics
            if agent_name := event.get("agent_name"):
                if agent_name not in summary["agents"]:
                    summary["agents"][agent_name] = {
                        "invocations": 0,
                        "completions": 0,
                        "failures": 0,
                        "total_duration": 0.0,
                        "avg_duration": 0.0
                    }

                agent_stats = summary["agents"][agent_name]

                if event["event_type"] == EventType.AGENT_INVOKED.value:
                    agent_stats["invocations"] += 1
                elif event["event_type"] == EventType.AGENT_COMPLETED.value:
                    agent_stats["completions"] += 1
                    if duration := event.get("duration_seconds"):
                        agent_stats["total_duration"] += duration
                elif event["event_type"] == EventType.AGENT_FAILED.value:
                    agent_stats["failures"] += 1

            # Command statistics
            if command_name := event.get("command_name"):
                if command_name not in summary["commands"]:
                    summary["commands"][command_name] = {
                        "invocations": 0
                    }
                summary["commands"][command_name]["invocations"] += 1

            # User feedback
            if event["event_type"] == EventType.USER_FEEDBACK.value:
                summary["satisfaction"]["total_feedback"] += 1
                if event.get("user_satisfied"):
                    summary["satisfaction"]["satisfied_count"] += 1

        # Calculate averages
        for agent_stats in summary["agents"].values():
            if agent_stats["completions"] > 0:
                agent_stats["avg_duration"] = (
                    agent_stats["total_duration"] / agent_stats["completions"]
                )

        if summary["satisfaction"]["total_feedback"] > 0:
            summary["satisfaction"]["satisfaction_rate"] = (
                summary["satisfaction"]["satisfied_count"] /
                summary["satisfaction"]["total_feedback"]
            )

        # Save summary
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def print_summary(self):
        """Print formatted summary to console"""
        summary = self.generate_summary()

        print("\n" + "="*60)
        print("CLAUDEAGENTS TELEMETRY SUMMARY")
        print("="*60)

        print(f"\n📊 Overview:")
        print(f"  • Total events: {summary['total_events']}")
        print(f"  • Period: {summary['period']['first_event']} to {summary['period']['last_event']}")

        print(f"\n🤖 Top 10 Most-Used Agents:")
        agents_by_usage = sorted(
            summary["agents"].items(),
            key=lambda x: x[1]["invocations"],
            reverse=True
        )[:10]

        for i, (agent, stats) in enumerate(agents_by_usage, 1):
            success_rate = (
                (stats["completions"] / stats["invocations"] * 100)
                if stats["invocations"] > 0 else 0
            )
            print(f"  {i}. {agent}")
            print(f"     Invocations: {stats['invocations']}, "
                  f"Success: {success_rate:.1f}%, "
                  f"Avg Duration: {stats['avg_duration']:.1f}s")

        print(f"\n📋 Commands Used:")
        for cmd, stats in sorted(summary["commands"].items(),
                                 key=lambda x: x[1]["invocations"],
                                 reverse=True)[:10]:
            print(f"  • {cmd}: {stats['invocations']} times")

        print(f"\n😊 User Satisfaction:")
        sat = summary["satisfaction"]
        print(f"  • Feedback received: {sat['total_feedback']}")
        print(f"  • Satisfied: {sat['satisfied_count']}")
        print(f"  • Satisfaction rate: {sat['satisfaction_rate']*100:.1f}%")

        print("\n" + "="*60 + "\n")


def main():
    """CLI interface for telemetry management"""
    import sys

    collector = TelemetryCollector()

    if len(sys.argv) < 2:
        print("Usage: python telemetry.py [enable|disable|summary|status]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "enable":
        collector.enable()
    elif command == "disable":
        collector.disable()
    elif command == "summary":
        collector.print_summary()
    elif command == "status":
        print(f"Telemetry: {'✅ Enabled' if collector.is_enabled() else '🔕 Disabled'}")
        print(f"Data directory: {collector.base_dir}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
