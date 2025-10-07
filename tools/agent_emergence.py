#!/usr/bin/env python3
"""
ClaudeAgents Emergence Tracking System

Tracks agent usage gaps and identifies patterns where composite agents
would be valuable. Implements the "agent emergence protocol" from Phase 3.

Core Concept:
- Users request capabilities not covered by existing agents
- System tracks these "agent gaps"
- When a gap pattern reaches 10+ requests, synthesize composite agent
- Promote successful composites to permanent agents

Design Goals:
- Identify unmet needs organically
- Prevent agent proliferation (only promote validated patterns)
- Community-driven agent evolution
- Data-driven agent creation
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
from datetime import datetime


@dataclass
class AgentGap:
    """Represents an unmet need - user request not fully satisfied by existing agents"""
    timestamp: float
    user_request: str
    selected_agents: List[str]  # What the orchestrator selected
    satisfaction_score: Optional[float] = None  # User feedback (0.0-1.0)
    missing_capabilities: List[str] = field(default_factory=list)
    suggested_composite: Optional[str] = None  # Synthesized agent name

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CompositeAgentPattern:
    """Pattern of agent combinations that appear frequently"""
    agent_combination: Tuple[str, ...]  # Sorted tuple of agent names
    frequency: int = 0
    avg_satisfaction: float = 0.0
    use_cases: List[str] = field(default_factory=list)  # User requests that led to this combo
    first_seen: Optional[float] = None
    last_seen: Optional[float] = None
    promoted: bool = False  # Has this been promoted to permanent agent?
    composite_name: Optional[str] = None

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['agent_combination'] = list(d['agent_combination'])  # Convert tuple to list for JSON
        return d


@dataclass
class EmergentAgent:
    """Specification for a composite agent that should be created"""
    name: str
    component_agents: List[str]
    description: str
    use_cases: List[str]
    frequency: int
    avg_satisfaction: float
    created_at: float
    status: str = "proposed"  # proposed, created, validated, promoted

    def to_dict(self) -> Dict:
        return asdict(self)


class AgentEmergenceTracker:
    """
    Tracks agent usage patterns and identifies emergent composite agents.

    Storage structure:
    .claude-telemetry/
      ├── emergence/
      │   ├── gaps.jsonl           # Agent gap records
      │   ├── patterns.json        # Composite patterns
      │   ├── emergent.json        # Proposed emergent agents
      │   └── promotions.json      # Promotion decisions
    """

    # Thresholds for emergence
    MIN_FREQUENCY_FOR_PROMOTION = 10  # Pattern must appear 10+ times
    MIN_SATISFACTION_FOR_PROMOTION = 0.7  # Average satisfaction >70%
    MIN_USE_CASES_FOR_PROMOTION = 5  # At least 5 distinct use cases

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize emergence tracker"""
        if base_dir is None:
            base_dir = Path.home() / ".claude-telemetry" / "emergence"

        self.base_dir = Path(base_dir)
        self.gaps_file = self.base_dir / "gaps.jsonl"
        self.patterns_file = self.base_dir / "patterns.json"
        self.emergent_file = self.base_dir / "emergent.json"
        self.promotions_file = self.base_dir / "promotions.json"

        self._ensure_directories()
        self._load_data()

    def _ensure_directories(self):
        """Create emergence tracking directories"""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _load_data(self):
        """Load existing patterns and emergent agents"""
        # Load patterns
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                self.patterns = {
                    tuple(p['agent_combination']): CompositeAgentPattern(
                        agent_combination=tuple(p['agent_combination']),
                        frequency=p['frequency'],
                        avg_satisfaction=p['avg_satisfaction'],
                        use_cases=p['use_cases'],
                        first_seen=p.get('first_seen'),
                        last_seen=p.get('last_seen'),
                        promoted=p.get('promoted', False),
                        composite_name=p.get('composite_name')
                    )
                    for p in data
                }
        else:
            self.patterns: Dict[Tuple[str, ...], CompositeAgentPattern] = {}

        # Load emergent agents
        if self.emergent_file.exists():
            with open(self.emergent_file, 'r') as f:
                data = json.load(f)
                self.emergent_agents = [
                    EmergentAgent(**agent) for agent in data
                ]
        else:
            self.emergent_agents: List[EmergentAgent] = []

    def _save_patterns(self):
        """Save patterns to disk"""
        with open(self.patterns_file, 'w') as f:
            json.dump([p.to_dict() for p in self.patterns.values()], f, indent=2)

    def _save_emergent(self):
        """Save emergent agents to disk"""
        with open(self.emergent_file, 'w') as f:
            json.dump([a.to_dict() for a in self.emergent_agents], f, indent=2)

    def record_gap(
        self,
        user_request: str,
        selected_agents: List[str],
        satisfaction_score: Optional[float] = None,
        missing_capabilities: Optional[List[str]] = None
    ):
        """
        Record an agent gap - when existing agents don't fully satisfy request.

        Args:
            user_request: What the user asked for
            selected_agents: Which agents were selected by orchestrator
            satisfaction_score: User feedback (0.0-1.0), None if no feedback yet
            missing_capabilities: What capabilities were missing
        """
        gap = AgentGap(
            timestamp=time.time(),
            user_request=user_request,
            selected_agents=selected_agents,
            satisfaction_score=satisfaction_score,
            missing_capabilities=missing_capabilities or []
        )

        # Append to gaps log
        with open(self.gaps_file, 'a') as f:
            json.dump(gap.to_dict(), f)
            f.write('\n')

        # Update patterns
        self._update_patterns(gap)

    def _update_patterns(self, gap: AgentGap):
        """Update composite agent patterns based on gap"""
        if len(gap.selected_agents) < 2:
            return  # Single agent, not a composite

        # Create sorted tuple for pattern matching
        combination = tuple(sorted(gap.selected_agents))

        # Update or create pattern
        if combination in self.patterns:
            pattern = self.patterns[combination]
            pattern.frequency += 1
            pattern.last_seen = gap.timestamp
            pattern.use_cases.append(gap.user_request)

            # Update average satisfaction if provided
            if gap.satisfaction_score is not None:
                # Running average
                n = pattern.frequency
                pattern.avg_satisfaction = (
                    (pattern.avg_satisfaction * (n - 1) + gap.satisfaction_score) / n
                )
        else:
            pattern = CompositeAgentPattern(
                agent_combination=combination,
                frequency=1,
                avg_satisfaction=gap.satisfaction_score or 0.0,
                use_cases=[gap.user_request],
                first_seen=gap.timestamp,
                last_seen=gap.timestamp
            )
            self.patterns[combination] = pattern

        # Save updated patterns
        self._save_patterns()

        # Check if pattern should be promoted
        self._check_for_emergence(pattern)

    def _check_for_emergence(self, pattern: CompositeAgentPattern):
        """Check if pattern qualifies for emergence promotion"""
        if pattern.promoted:
            return  # Already promoted

        # Check promotion criteria
        qualifies = (
            pattern.frequency >= self.MIN_FREQUENCY_FOR_PROMOTION and
            pattern.avg_satisfaction >= self.MIN_SATISFACTION_FOR_PROMOTION and
            len(set(pattern.use_cases)) >= self.MIN_USE_CASES_FOR_PROMOTION
        )

        if qualifies:
            # Synthesize emergent agent
            emergent = self._synthesize_emergent_agent(pattern)
            self.emergent_agents.append(emergent)
            self._save_emergent()

            # Mark pattern as promoted
            pattern.promoted = True
            pattern.composite_name = emergent.name
            self._save_patterns()

            print(f"✨ Emergent agent identified: {emergent.name}")
            print(f"   Based on {pattern.frequency} uses with {pattern.avg_satisfaction*100:.1f}% satisfaction")

    def _synthesize_emergent_agent(self, pattern: CompositeAgentPattern) -> EmergentAgent:
        """Synthesize specification for emergent composite agent"""
        # Generate composite name from component agents
        agent_names = list(pattern.agent_combination)
        if len(agent_names) == 2:
            # Simple concatenation for 2 agents
            name = f"{agent_names[0]}-{agent_names[1]}-composite"
        else:
            # Use domain-based naming for 3+ agents
            name = self._generate_domain_name(agent_names)

        # Extract common themes from use cases
        description = self._generate_description(pattern)

        emergent = EmergentAgent(
            name=name,
            component_agents=list(pattern.agent_combination),
            description=description,
            use_cases=pattern.use_cases[:10],  # First 10 use cases
            frequency=pattern.frequency,
            avg_satisfaction=pattern.avg_satisfaction,
            created_at=time.time(),
            status="proposed"
        )

        return emergent

    def _generate_domain_name(self, agent_names: List[str]) -> str:
        """Generate domain-based name for composite agent"""
        # Simple heuristic: identify common domain
        domains = {
            'security': ['security', 'audit'],
            'performance': ['performance', 'optimization'],
            'frontend': ['frontend', 'web', 'ui'],
            'backend': ['backend', 'api', 'data'],
            'mobile': ['mobile', 'ios', 'android'],
        }

        # Find matching domain
        agent_str = ' '.join(agent_names).lower()
        for domain, keywords in domains.items():
            if any(kw in agent_str for kw in keywords):
                return f"{domain}-specialist-composite"

        # Default: multi-domain-specialist
        return "multi-domain-specialist"

    def _generate_description(self, pattern: CompositeAgentPattern) -> str:
        """Generate description for emergent agent"""
        # Extract keywords from use cases
        keywords = []
        common_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'to', 'in', 'on'}

        for use_case in pattern.use_cases[:5]:
            words = use_case.lower().split()
            keywords.extend([w for w in words if w not in common_words and len(w) > 3])

        # Get most common keywords
        keyword_freq = Counter(keywords)
        top_keywords = [k for k, _ in keyword_freq.most_common(3)]

        # Build description
        agent_list = ", ".join(pattern.agent_combination)
        keyword_str = ", ".join(top_keywords) if top_keywords else "multi-domain tasks"

        description = (
            f"Composite agent combining {agent_list} for {keyword_str}. "
            f"Emerged from {pattern.frequency} uses with {pattern.avg_satisfaction*100:.1f}% satisfaction."
        )

        return description

    def get_emergent_agents(self, status: Optional[str] = None) -> List[EmergentAgent]:
        """Get emergent agents, optionally filtered by status"""
        if status:
            return [a for a in self.emergent_agents if a.status == status]
        return self.emergent_agents

    def get_top_patterns(self, limit: int = 10) -> List[CompositeAgentPattern]:
        """Get top composite patterns by frequency"""
        patterns = sorted(
            self.patterns.values(),
            key=lambda p: (p.frequency, p.avg_satisfaction),
            reverse=True
        )
        return patterns[:limit]

    def get_promotion_candidates(self) -> List[CompositeAgentPattern]:
        """Get patterns that are close to promotion threshold"""
        candidates = []
        for pattern in self.patterns.values():
            if pattern.promoted:
                continue

            # Check how close to promotion
            freq_progress = pattern.frequency / self.MIN_FREQUENCY_FOR_PROMOTION
            sat_progress = pattern.avg_satisfaction / self.MIN_SATISFACTION_FOR_PROMOTION
            cases_progress = len(set(pattern.use_cases)) / self.MIN_USE_CASES_FOR_PROMOTION

            # If at least 70% toward any threshold
            if min(freq_progress, sat_progress, cases_progress) >= 0.7:
                candidates.append(pattern)

        return sorted(candidates, key=lambda p: p.frequency, reverse=True)

    def promote_to_permanent(self, emergent_name: str):
        """Mark emergent agent as promoted to permanent status"""
        for agent in self.emergent_agents:
            if agent.name == emergent_name:
                agent.status = "promoted"
                self._save_emergent()

                # Record promotion
                promotion = {
                    "agent_name": emergent_name,
                    "promoted_at": time.time(),
                    "frequency": agent.frequency,
                    "satisfaction": agent.avg_satisfaction,
                    "component_agents": agent.component_agents
                }

                promotions = []
                if self.promotions_file.exists():
                    with open(self.promotions_file, 'r') as f:
                        promotions = json.load(f)

                promotions.append(promotion)

                with open(self.promotions_file, 'w') as f:
                    json.dump(promotions, f, indent=2)

                print(f"✅ Promoted {emergent_name} to permanent agent")
                return

        print(f"❌ Emergent agent {emergent_name} not found")

    def print_dashboard(self):
        """Print emergence tracking dashboard"""
        print("\n" + "="*70)
        print("AGENT EMERGENCE DASHBOARD")
        print("="*70)

        # Summary stats
        total_patterns = len(self.patterns)
        promoted_count = sum(1 for p in self.patterns.values() if p.promoted)
        emergent_count = len(self.emergent_agents)

        print(f"\n📊 Summary:")
        print(f"  • Total composite patterns: {total_patterns}")
        print(f"  • Promoted to permanent: {promoted_count}")
        print(f"  • Emergent agents identified: {emergent_count}")

        # Top patterns
        print(f"\n🔥 Top 10 Composite Patterns:")
        for i, pattern in enumerate(self.get_top_patterns(10), 1):
            status = "✅ PROMOTED" if pattern.promoted else "⏳ Tracking"
            print(f"\n  {i}. {' + '.join(pattern.agent_combination)}")
            print(f"     Uses: {pattern.frequency}, Satisfaction: {pattern.avg_satisfaction*100:.1f}%, {status}")
            if pattern.use_cases:
                print(f"     Example: {pattern.use_cases[0][:60]}...")

        # Promotion candidates
        candidates = self.get_promotion_candidates()
        if candidates:
            print(f"\n🎯 Promotion Candidates ({len(candidates)}):")
            for pattern in candidates[:5]:
                freq_pct = (pattern.frequency / self.MIN_FREQUENCY_FOR_PROMOTION) * 100
                sat_pct = (pattern.avg_satisfaction / self.MIN_SATISFACTION_FOR_PROMOTION) * 100
                print(f"  • {' + '.join(pattern.agent_combination)}")
                print(f"    Progress: {freq_pct:.0f}% frequency, {sat_pct:.0f}% satisfaction")

        # Emergent agents
        proposed = self.get_emergent_agents("proposed")
        if proposed:
            print(f"\n✨ Proposed Emergent Agents ({len(proposed)}):")
            for agent in proposed:
                print(f"\n  • {agent.name}")
                print(f"    Components: {', '.join(agent.component_agents)}")
                print(f"    {agent.description[:80]}...")
                print(f"    Status: Ready for review")

        print("\n" + "="*70 + "\n")


def main():
    """CLI interface for emergence tracking"""
    import sys

    tracker = AgentEmergenceTracker()

    if len(sys.argv) < 2:
        print("Usage: python agent_emergence.py [dashboard|promote|candidates]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "dashboard":
        tracker.print_dashboard()

    elif command == "promote":
        if len(sys.argv) < 3:
            print("Usage: python agent_emergence.py promote <agent-name>")
            sys.exit(1)
        agent_name = sys.argv[2]
        tracker.promote_to_permanent(agent_name)

    elif command == "candidates":
        candidates = tracker.get_promotion_candidates()
        print(f"\n🎯 Promotion Candidates: {len(candidates)}\n")
        for pattern in candidates:
            print(f"  • {' + '.join(pattern.agent_combination)}")
            print(f"    Frequency: {pattern.frequency}/{tracker.MIN_FREQUENCY_FOR_PROMOTION}")
            print(f"    Satisfaction: {pattern.avg_satisfaction*100:.1f}%/{tracker.MIN_SATISFACTION_FOR_PROMOTION*100:.0f}%")
            print(f"    Use cases: {len(set(pattern.use_cases))}/{tracker.MIN_USE_CASES_FOR_PROMOTION}\n")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
