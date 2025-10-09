"""
AIL Integration for full-stack-architect Agent

Enhances full-stack-architect with archaeological intelligence for:
- Architectural evolution and design patterns
- Frontend/backend integration history
- API design decisions and changes
- Technology stack evolution
- Performance optimization history
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext
from tools.ail.agent_integration import get_context_from_input, extract_file_path, formulate_question

logger = logging.getLogger(__name__)


@dataclass
class ArchitecturalEvolution:
    """Architectural evolution event."""

    evolution_type: str  # "pattern_change", "tech_stack", "api_design", "integration"
    description: str
    rationale: str
    impact: str  # "high", "medium", "low"
    date: datetime
    author: str
    commit_sha: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'evolution_type': self.evolution_type,
            'description': self.description,
            'rationale': self.rationale,
            'impact': self.impact,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
        }


@dataclass
class ArchitecturalAnalysis:
    """Enhanced architectural analysis with AIL context."""

    file_path: str
    analysis_question: str
    archaeological_context: ArchaeologicalContext
    evolutionary_events: List[ArchitecturalEvolution]
    design_patterns: List[str]
    integration_history: List[str]
    tech_stack_changes: List[str]
    performance_optimizations: List[str]
    recommendations: List[str]
    confidence: float
    query_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_path': self.file_path,
            'analysis_question': self.analysis_question,
            'archaeological_answer': self.archaeological_context.answer,
            'evolutionary_events': [e.to_dict() for e in self.evolutionary_events],
            'design_patterns': self.design_patterns,
            'integration_history': self.integration_history,
            'tech_stack_changes': self.tech_stack_changes,
            'performance_optimizations': self.performance_optimizations,
            'recommendations': self.recommendations,
            'confidence': self.confidence,
            'query_time_ms': self.query_time_ms,
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Architectural Analysis: {self.file_path}",
            f"**Question**: {self.analysis_question}",
            f"**Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.evolutionary_events:
            lines.append("## Architectural Evolution")
            for event in self.evolutionary_events:
                lines.append(f"### {event.evolution_type.replace('_', ' ').title()} (Impact: {event.impact.upper()})")
                lines.append(f"**Description**: {event.description}")
                lines.append(f"**Rationale**: {event.rationale}")
                lines.append(f"**Date**: {event.date.date()} by {event.author}")
                lines.append("")

        if self.design_patterns:
            lines.append("## Design Patterns")
            for pattern in self.design_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.integration_history:
            lines.append("## Integration History")
            for integration in self.integration_history:
                lines.append(f"- {integration}")
            lines.append("")

        if self.tech_stack_changes:
            lines.append("## Technology Stack Changes")
            for change in self.tech_stack_changes:
                lines.append(f"- {change}")
            lines.append("")

        if self.recommendations:
            lines.append("## Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms*")
        return "\n".join(lines)


class FullStackArchitectAIL:
    """Enhances full-stack-architect with Archaeological Intelligence."""

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"FullStackArchitectAIL initialized for: {repo_path}")

    def enhanced_analysis(self, user_input: str) -> ArchitecturalAnalysis:
        """Perform enhanced architectural analysis with archaeological context."""
        context = get_context_from_input(self.provider, user_input)

        if not context:
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")
            question = formulate_question(user_input, task_type="implement")
            context = self.provider.get_context_sync(file_path, question)

        evolutionary_events = self._extract_evolutionary_events(context)
        design_patterns = self._extract_design_patterns(context)
        integration_history = self._extract_integration_history(context)
        tech_stack_changes = self._extract_tech_stack_changes(context)
        performance_opts = self._extract_performance_optimizations(context)
        recommendations = self._generate_recommendations(
            evolutionary_events, design_patterns, tech_stack_changes
        )

        return ArchitecturalAnalysis(
            file_path=context.file_path,
            analysis_question=context.question,
            archaeological_context=context,
            evolutionary_events=evolutionary_events,
            design_patterns=design_patterns,
            integration_history=integration_history,
            tech_stack_changes=tech_stack_changes,
            performance_optimizations=performance_opts,
            recommendations=recommendations,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_evolutionary_events(self, context: ArchaeologicalContext) -> List[ArchitecturalEvolution]:
        """Extract architectural evolution events."""
        events = []
        keywords = {
            'pattern_change': ['pattern', 'architecture', 'design change', 'restructure'],
            'tech_stack': ['upgrade', 'migrate', 'framework', 'library', 'stack'],
            'api_design': ['api', 'endpoint', 'rest', 'graphql', 'interface'],
            'integration': ['integrate', 'connect', 'service', 'microservice'],
        }

        impact_keywords = {
            'high': ['breaking', 'major', 'significant', 'critical'],
            'medium': ['update', 'improve', 'enhance'],
            'low': ['minor', 'small', 'fix'],
        }

        for source in context.sources[:5]:
            msg_lower = source.commit_message.lower()

            # Determine event type
            event_type = 'pattern_change'
            for etype, words in keywords.items():
                if any(word in msg_lower for word in words):
                    event_type = etype
                    break

            # Determine impact
            impact = 'medium'
            for imp, words in impact_keywords.items():
                if any(word in msg_lower for word in words):
                    impact = imp
                    break

            events.append(ArchitecturalEvolution(
                evolution_type=event_type,
                description=source.commit_message[:200],
                rationale=source.excerpt[:200],
                impact=impact,
                date=source.date,
                author=source.author,
                commit_sha=source.commit_sha,
            ))

        return events

    def _extract_design_patterns(self, context: ArchaeologicalContext) -> List[str]:
        """Extract design patterns from context."""
        patterns = []
        pattern_keywords = [
            'mvc', 'mvvm', 'repository', 'factory', 'singleton', 'observer',
            'decorator', 'adapter', 'strategy', 'command', 'clean architecture',
            'hexagonal', 'layered', 'microservices', 'event-driven'
        ]

        for source in context.sources:
            msg_lower = source.commit_message.lower()
            for pattern in pattern_keywords:
                if pattern in msg_lower:
                    patterns.append(
                        f"{pattern.upper()} pattern in {source.commit_sha[:8]} ({source.date.date()})"
                    )
                    break

        return patterns[:5]

    def _extract_integration_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract integration history."""
        integrations = []
        integration_keywords = [
            'integrate', 'connect', 'api', 'service', 'third-party',
            'webhook', 'oauth', 'authentication', 'database'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in integration_keywords):
                integrations.append(
                    f"{source.commit_message[:100]} ({source.date.date()})"
                )

        return integrations[:5]

    def _extract_tech_stack_changes(self, context: ArchaeologicalContext) -> List[str]:
        """Extract technology stack changes."""
        changes = []
        tech_keywords = [
            'upgrade', 'migrate', 'react', 'vue', 'angular', 'node',
            'python', 'django', 'flask', 'express', 'next.js', 'typescript'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in tech_keywords):
                changes.append(
                    f"{source.commit_message[:100]} ({source.date.date()})"
                )

        return changes[:5]

    def _extract_performance_optimizations(self, context: ArchaeologicalContext) -> List[str]:
        """Extract performance optimization history."""
        optimizations = []
        perf_keywords = [
            'optimize', 'performance', 'speed', 'cache', 'lazy load',
            'bundle', 'minify', 'compress', 'async', 'defer'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in perf_keywords):
                optimizations.append(
                    f"{source.commit_message[:100]} ({source.date.date()})"
                )

        return optimizations[:5]

    def _generate_recommendations(
        self, events: List[ArchitecturalEvolution],
        patterns: List[str], tech_changes: List[str]
    ) -> List[str]:
        """Generate architectural recommendations."""
        recommendations = []

        high_impact_events = [e for e in events if e.impact == 'high']
        if len(high_impact_events) > 2:
            recommendations.append(
                "Multiple high-impact architectural changes detected. Ensure comprehensive "
                "documentation and migration guides are maintained."
            )

        if len(patterns) > 3:
            recommendations.append(
                "Multiple design patterns identified. Consider creating architectural "
                "decision records (ADRs) to document pattern choices and rationale."
            )

        if len(tech_changes) > 3:
            recommendations.append(
                "Frequent technology stack changes detected. Ensure team training and "
                "knowledge transfer processes are in place."
            )

        if not recommendations:
            recommendations.append(
                "Architecture shows stable evolution. Continue documenting major decisions "
                "and maintain architectural consistency."
            )

        return recommendations


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python full_stack_architect_ail.py <repo_path> <question>")
        sys.exit(1)

    repo_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    architect = FullStackArchitectAIL(repo_path)
    analysis = architect.enhanced_analysis(question)
    print(analysis.to_markdown())


if __name__ == '__main__':
    main()
