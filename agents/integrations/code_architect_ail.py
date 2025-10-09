"""
AIL Integration for code-architect Agent

Enhances code-architect with archaeological intelligence for:
- Historical design decisions and rationale
- Architectural evolution and refactoring patterns
- Code quality trends over time
- Team conventions and coding standards history
- Technical debt accumulation patterns
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext
from tools.ail.agent_integration import (
    get_context_from_input,
    extract_file_path,
    formulate_question,
)

logger = logging.getLogger(__name__)


@dataclass
class ArchitecturalInsight:
    """Architectural insight extracted from archaeological context."""

    insight_type: str  # "design_decision", "refactoring", "pattern", "convention"
    description: str
    rationale: str
    date: datetime
    author: str
    commit_sha: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'insight_type': self.insight_type,
            'description': self.description,
            'rationale': self.rationale,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
            'confidence': self.confidence,
        }


@dataclass
class CodeQualityTrend:
    """Code quality trend analysis."""

    metric: str  # "complexity", "test_coverage", "documentation"
    trend: str  # "improving", "stable", "degrading"
    current_value: float
    historical_values: List[float]
    time_period: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'metric': self.metric,
            'trend': self.trend,
            'current_value': self.current_value,
            'historical_values': self.historical_values,
            'time_period': self.time_period,
        }


@dataclass
class ArchitecturalReview:
    """Enhanced architectural review with AIL context."""

    file_path: str
    review_question: str
    archaeological_context: ArchaeologicalContext
    architectural_insights: List[ArchitecturalInsight]
    quality_trends: List[CodeQualityTrend]
    design_decisions: List[str]
    refactoring_history: List[str]
    team_conventions: List[str]
    technical_debt_patterns: List[str]
    recommendations: List[str]
    confidence: float
    query_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'file_path': self.file_path,
            'review_question': self.review_question,
            'archaeological_answer': self.archaeological_context.answer,
            'archaeological_confidence': self.archaeological_context.confidence,
            'architectural_insights': [i.to_dict() for i in self.architectural_insights],
            'quality_trends': [t.to_dict() for t in self.quality_trends],
            'design_decisions': self.design_decisions,
            'refactoring_history': self.refactoring_history,
            'team_conventions': self.team_conventions,
            'technical_debt_patterns': self.technical_debt_patterns,
            'recommendations': self.recommendations,
            'confidence': self.confidence,
            'query_time_ms': self.query_time_ms,
            'source_count': len(self.archaeological_context.sources),
        }

    def to_markdown(self) -> str:
        """Format review as markdown."""
        lines = [
            f"# Architectural Review: {self.file_path}",
            f"**Question**: {self.review_question}",
            f"**Overall Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.design_decisions:
            lines.append("## Design Decisions")
            for decision in self.design_decisions:
                lines.append(f"- {decision}")
            lines.append("")

        if self.refactoring_history:
            lines.append("## Refactoring History")
            for refactoring in self.refactoring_history:
                lines.append(f"- {refactoring}")
            lines.append("")

        if self.team_conventions:
            lines.append("## Team Conventions")
            for convention in self.team_conventions:
                lines.append(f"- {convention}")
            lines.append("")

        if self.technical_debt_patterns:
            lines.append("## Technical Debt Patterns")
            for pattern in self.technical_debt_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.architectural_insights:
            lines.append("## Architectural Insights")
            for insight in self.architectural_insights:
                lines.append(f"### {insight.insight_type.replace('_', ' ').title()}")
                lines.append(f"**Description**: {insight.description}")
                lines.append(f"**Rationale**: {insight.rationale}")
                lines.append(f"**Author**: {insight.author} ({insight.date.date()})")
                lines.append(f"**Confidence**: {insight.confidence:.1%}")
                lines.append("")

        if self.quality_trends:
            lines.append("## Code Quality Trends")
            for trend in self.quality_trends:
                lines.append(f"### {trend.metric.replace('_', ' ').title()}")
                lines.append(f"**Trend**: {trend.trend} (Current: {trend.current_value:.2f})")
                lines.append(f"**Time Period**: {trend.time_period}")
                lines.append("")

        if self.recommendations:
            lines.append("## Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms | Sources: {len(self.archaeological_context.sources)}*")

        return "\n".join(lines)


class CodeArchitectAIL:
    """
    Enhances code-architect agent with Archaeological Intelligence.

    This integration provides code-architect with historical context about:
    - Design decisions and architectural evolution
    - Refactoring patterns and code quality trends
    - Team conventions and coding standards
    - Technical debt accumulation

    Example Usage:
        >>> architect = CodeArchitectAIL(repo_path=".")
        >>> review = architect.enhanced_review(
        ...     "Why does tools/ail/context_provider.py use LRU caching?"
        ... )
        >>> print(review.to_markdown())
    """

    def __init__(self, repo_path: str):
        """
        Initialize code-architect AIL integration.

        Args:
            repo_path: Path to git repository
        """
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"CodeArchitectAIL initialized for: {repo_path}")

    def enhanced_review(self, user_input: str) -> ArchitecturalReview:
        """
        Perform enhanced architectural review with archaeological context.

        Args:
            user_input: Natural language input (e.g., "Why was JWT chosen in auth.py?")

        Returns:
            ArchitecturalReview with comprehensive historical analysis
        """
        # Get archaeological context
        context = get_context_from_input(self.provider, user_input)

        if not context:
            # Fallback: extract file path manually
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")

            # Formulate architectural question
            question = formulate_question(user_input, task_type="review")
            context = self.provider.get_context_sync(file_path, question)

        # Extract architectural insights
        insights = self._extract_architectural_insights(context)

        # Extract design decisions
        design_decisions = self._extract_design_decisions(context)

        # Extract refactoring history
        refactoring_history = self._extract_refactoring_history(context)

        # Extract team conventions
        team_conventions = self._extract_team_conventions(context)

        # Analyze quality trends
        quality_trends = self._analyze_quality_trends(context)

        # Identify technical debt patterns
        debt_patterns = self._identify_debt_patterns(context)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            context, insights, quality_trends, debt_patterns
        )

        return ArchitecturalReview(
            file_path=context.file_path,
            review_question=context.question,
            archaeological_context=context,
            architectural_insights=insights,
            quality_trends=quality_trends,
            design_decisions=design_decisions,
            refactoring_history=refactoring_history,
            team_conventions=team_conventions,
            technical_debt_patterns=debt_patterns,
            recommendations=recommendations,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_architectural_insights(
        self, context: ArchaeologicalContext
    ) -> List[ArchitecturalInsight]:
        """Extract architectural insights from archaeological context."""
        insights = []

        # Keywords for insight types
        keywords = {
            'design_decision': ['chose', 'decided', 'selected', 'opted', 'design decision'],
            'refactoring': ['refactor', 'restructure', 'reorganize', 'improve'],
            'pattern': ['pattern', 'architecture', 'design pattern', 'approach'],
            'convention': ['convention', 'standard', 'guideline', 'practice'],
        }

        answer_lower = context.answer.lower()

        for source in context.sources[:5]:  # Top 5 most relevant
            for insight_type, words in keywords.items():
                if any(word in answer_lower or word in source.commit_message.lower()
                       for word in words):
                    insight = ArchitecturalInsight(
                        insight_type=insight_type,
                        description=source.commit_message[:200],
                        rationale=source.excerpt[:300],
                        date=source.date,
                        author=source.author,
                        commit_sha=source.commit_sha,
                        confidence=source.relevance_score,
                    )
                    insights.append(insight)
                    break  # Only one insight type per source

        return insights

    def _extract_design_decisions(self, context: ArchaeologicalContext) -> List[str]:
        """Extract design decisions from context."""
        decisions = []

        # Look for decision indicators in answer
        decision_markers = [
            'decided to', 'chose to', 'implemented', 'adopted',
            'selected', 'designed', 'architecture'
        ]

        sentences = context.answer.split('.')
        for sentence in sentences:
            if any(marker in sentence.lower() for marker in decision_markers):
                decisions.append(sentence.strip())

        # Add decisions from high-relevance sources
        for source in context.sources:
            if source.relevance_score > 0.7:
                if any(marker in source.commit_message.lower()
                       for marker in decision_markers):
                    decisions.append(
                        f"{source.commit_message[:100]} (by {source.author})"
                    )

        return decisions[:5]  # Top 5 decisions

    def _extract_refactoring_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract refactoring history from context."""
        refactorings = []

        refactor_keywords = [
            'refactor', 'restructure', 'reorganize', 'improve',
            'clean up', 'simplify', 'optimize'
        ]

        for source in context.sources:
            if any(keyword in source.commit_message.lower()
                   for keyword in refactor_keywords):
                refactorings.append(
                    f"{source.commit_message[:100]} ({source.date.date()}) by {source.author}"
                )

        return refactorings[:5]  # Top 5 refactorings

    def _extract_team_conventions(self, context: ArchaeologicalContext) -> List[str]:
        """Extract team conventions from context."""
        conventions = []

        convention_keywords = [
            'convention', 'standard', 'guideline', 'practice',
            'pattern', 'approach', 'style'
        ]

        sentences = context.answer.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in convention_keywords):
                conventions.append(sentence.strip())

        return conventions[:3]  # Top 3 conventions

    def _analyze_quality_trends(
        self, context: ArchaeologicalContext
    ) -> List[CodeQualityTrend]:
        """Analyze code quality trends from historical data."""
        trends = []

        # Analyze commit frequency as a proxy for maintenance activity
        if len(context.sources) >= 3:
            dates = sorted([s.date for s in context.sources])
            time_span = (dates[-1] - dates[0]).days

            if time_span > 0:
                commit_rate = len(dates) / max(time_span, 1)

                # Determine maintenance trend
                recent_commits = sum(1 for d in dates if (datetime.now() - d).days < 90)
                older_commits = len(dates) - recent_commits

                trend = "stable"
                if recent_commits > older_commits * 1.5:
                    trend = "improving"
                elif recent_commits < older_commits * 0.5:
                    trend = "degrading"

                trends.append(CodeQualityTrend(
                    metric="maintenance_activity",
                    trend=trend,
                    current_value=recent_commits,
                    historical_values=[recent_commits, older_commits],
                    time_period=f"{time_span} days",
                ))

        return trends

    def _identify_debt_patterns(self, context: ArchaeologicalContext) -> List[str]:
        """Identify technical debt patterns from context."""
        patterns = []

        debt_keywords = [
            'todo', 'fixme', 'hack', 'workaround', 'temporary',
            'debt', 'technical debt', 'legacy', 'deprecated'
        ]

        for source in context.sources:
            msg_lower = source.commit_message.lower()
            if any(keyword in msg_lower for keyword in debt_keywords):
                patterns.append(
                    f"Potential debt in {source.commit_sha[:8]}: {source.commit_message[:100]}"
                )

        return patterns[:3]  # Top 3 debt patterns

    def _generate_recommendations(
        self,
        context: ArchaeologicalContext,
        insights: List[ArchitecturalInsight],
        trends: List[CodeQualityTrend],
        debt_patterns: List[str],
    ) -> List[str]:
        """Generate architectural recommendations based on analysis."""
        recommendations = []

        # Recommendation based on confidence
        if context.confidence < 0.5:
            recommendations.append(
                "Low confidence in historical context. Consider adding more "
                "detailed commit messages and documentation for future reviews."
            )

        # Recommendation based on insights
        if len(insights) < 2:
            recommendations.append(
                "Limited architectural insights found. Ensure design decisions "
                "are documented in commit messages and ADRs (Architectural Decision Records)."
            )

        # Recommendation based on trends
        for trend in trends:
            if trend.trend == "degrading":
                recommendations.append(
                    f"Code quality metric '{trend.metric}' is degrading. "
                    f"Consider scheduling refactoring work."
                )

        # Recommendation based on debt
        if len(debt_patterns) > 2:
            recommendations.append(
                "Multiple technical debt patterns identified. Prioritize debt "
                "reduction in upcoming sprints to maintain long-term velocity."
            )

        # Default recommendation
        if not recommendations:
            recommendations.append(
                "Code has good historical documentation. Continue maintaining "
                "clear commit messages and architectural decision records."
            )

        return recommendations


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python code_architect_ail.py <repo_path> <review_question>")
        print("\nExample:")
        print("  python code_architect_ail.py . 'Why does tools/ail/context_provider.py use LRU caching?'")
        sys.exit(1)

    repo_path = sys.argv[1]
    review_question = " ".join(sys.argv[2:])

    print(f"Code Architect AIL Review")
    print("=" * 80)
    print(f"Repository: {repo_path}")
    print(f"Question: {review_question}")
    print("=" * 80)
    print()

    # Initialize and run review
    architect = CodeArchitectAIL(repo_path)
    review = architect.enhanced_review(review_question)

    # Display results
    print(review.to_markdown())


if __name__ == '__main__':
    main()
