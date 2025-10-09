"""
AIL Integration for qa-test-engineer Agent

Enhances qa-test-engineer with archaeological intelligence for:
- Bug history and patterns
- Test coverage evolution
- Regression patterns and fixes
- Test strategy changes
- Quality metrics trends
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.ail.context_provider import ArchaeologyContextProvider, ArchaeologicalContext
from tools.ail.agent_integration import get_context_from_input, extract_file_path, formulate_question

logger = logging.getLogger(__name__)


@dataclass
class BugHistory:
    """Bug history record."""

    bug_type: str  # "regression", "edge_case", "integration", "logic_error"
    description: str
    severity: str  # "critical", "high", "medium", "low"
    fix_description: str
    date: datetime
    author: str
    commit_sha: str
    was_regression: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            'bug_type': self.bug_type,
            'description': self.description,
            'severity': self.severity,
            'fix_description': self.fix_description,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
            'was_regression': self.was_regression,
        }


@dataclass
class TestingAnalysis:
    """Enhanced testing analysis with AIL context."""

    file_path: str
    analysis_question: str
    archaeological_context: ArchaeologicalContext
    bug_history: List[BugHistory]
    regression_patterns: List[str]
    test_coverage_evolution: List[str]
    test_strategy_changes: List[str]
    quality_trends: List[str]
    recommendations: List[str]
    risk_areas: List[str]
    confidence: float
    query_time_ms: float

    def to_markdown(self) -> str:
        lines = [
            f"# Testing Analysis: {self.file_path}",
            f"**Question**: {self.analysis_question}",
            f"**Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.bug_history:
            lines.append("## Bug History")
            for bug in self.bug_history:
                lines.append(f"### {bug.bug_type.replace('_', ' ').title()} ({bug.severity.upper()})")
                lines.append(f"**Description**: {bug.description}")
                lines.append(f"**Fix**: {bug.fix_description}")
                lines.append(f"**Date**: {bug.date.date()} by {bug.author}")
                if bug.was_regression:
                    lines.append("**REGRESSION**: This was a regression bug")
                lines.append("")

        if self.regression_patterns:
            lines.append("## Regression Patterns")
            for pattern in self.regression_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.risk_areas:
            lines.append("## High-Risk Areas")
            for area in self.risk_areas:
                lines.append(f"- {area}")
            lines.append("")

        if self.recommendations:
            lines.append("## Testing Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms*")
        return "\n".join(lines)


class QATestEngineerAIL:
    """Enhances qa-test-engineer with Archaeological Intelligence."""

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"QATestEngineerAIL initialized for: {repo_path}")

    def enhanced_analysis(self, user_input: str) -> TestingAnalysis:
        """Perform enhanced testing analysis with archaeological context."""
        context = get_context_from_input(self.provider, user_input)

        if not context:
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")
            question = formulate_question(user_input, task_type="debug")
            context = self.provider.get_context_sync(file_path, question)

        bug_history = self._extract_bug_history(context)
        regression_patterns = self._identify_regression_patterns(context, bug_history)
        test_coverage = self._extract_test_coverage_evolution(context)
        test_strategy = self._extract_test_strategy_changes(context)
        quality_trends = self._analyze_quality_trends(context, bug_history)
        risk_areas = self._identify_risk_areas(bug_history, regression_patterns)
        recommendations = self._generate_recommendations(
            bug_history, regression_patterns, risk_areas
        )

        return TestingAnalysis(
            file_path=context.file_path,
            analysis_question=context.question,
            archaeological_context=context,
            bug_history=bug_history,
            regression_patterns=regression_patterns,
            test_coverage_evolution=test_coverage,
            test_strategy_changes=test_strategy,
            quality_trends=quality_trends,
            recommendations=recommendations,
            risk_areas=risk_areas,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_bug_history(self, context: ArchaeologicalContext) -> List[BugHistory]:
        """Extract bug history from context."""
        bugs = []
        bug_keywords = {
            'regression': ['regression', 'reintroduce', 'broke again'],
            'edge_case': ['edge case', 'corner case', 'boundary'],
            'integration': ['integration', 'interface', 'connection'],
            'logic_error': ['logic', 'algorithm', 'calculation', 'incorrect'],
        }

        severity_keywords = {
            'critical': ['critical', 'crash', 'data loss', 'security'],
            'high': ['high', 'broken', 'fails'],
            'medium': ['medium', 'issue', 'problem'],
            'low': ['low', 'minor', 'cosmetic'],
        }

        for source in context.sources[:5]:
            msg_lower = source.commit_message.lower()

            # Check if it's a bug fix
            if not any(kw in msg_lower for kw in ['fix', 'bug', 'issue', 'error', 'problem']):
                continue

            # Determine bug type
            bug_type = 'logic_error'
            for btype, keywords in bug_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    bug_type = btype
                    break

            # Determine severity
            severity = 'medium'
            for sev, keywords in severity_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    severity = sev
                    break

            # Check if regression
            was_regression = 'regression' in msg_lower or 'reintroduce' in msg_lower

            bugs.append(BugHistory(
                bug_type=bug_type,
                description=source.commit_message[:200],
                severity=severity,
                fix_description=source.excerpt[:200],
                date=source.date,
                author=source.author,
                commit_sha=source.commit_sha,
                was_regression=was_regression,
            ))

        return bugs

    def _identify_regression_patterns(
        self, context: ArchaeologicalContext, bugs: List[BugHistory]
    ) -> List[str]:
        """Identify regression patterns."""
        patterns = []

        # Count regressions
        regressions = [b for b in bugs if b.was_regression]
        if len(regressions) > 1:
            patterns.append(
                f"Multiple regression bugs detected ({len(regressions)} instances). "
                f"Suggests insufficient test coverage or missing regression tests."
            )

        # Check for repeated bug types
        bug_types = [b.bug_type for b in bugs]
        for bug_type in set(bug_types):
            count = bug_types.count(bug_type)
            if count > 1:
                patterns.append(
                    f"Repeated {bug_type.replace('_', ' ')} bugs ({count} instances). "
                    f"Consider adding targeted tests for this category."
                )

        return patterns

    def _extract_test_coverage_evolution(self, context: ArchaeologicalContext) -> List[str]:
        """Extract test coverage evolution."""
        evolution = []
        test_keywords = ['test', 'coverage', 'unit test', 'integration test', 'e2e', 'spec']

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in test_keywords):
                evolution.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return evolution[:5]

    def _extract_test_strategy_changes(self, context: ArchaeologicalContext) -> List[str]:
        """Extract test strategy changes."""
        changes = []
        strategy_keywords = [
            'test strategy', 'testing framework', 'jest', 'pytest', 'mocha',
            'selenium', 'cypress', 'playwright', 'tdd', 'bdd'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in strategy_keywords):
                changes.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return changes[:5]

    def _analyze_quality_trends(
        self, context: ArchaeologicalContext, bugs: List[BugHistory]
    ) -> List[str]:
        """Analyze quality trends."""
        trends = []

        if len(bugs) > 3:
            # Analyze bug severity distribution
            critical = sum(1 for b in bugs if b.severity == 'critical')
            high = sum(1 for b in bugs if b.severity == 'high')

            if critical > 0:
                trends.append(f"Quality trend: {critical} critical bugs found in history")
            if high > 1:
                trends.append(f"Quality trend: {high} high-severity bugs found in history")

            # Analyze regression rate
            regressions = sum(1 for b in bugs if b.was_regression)
            if regressions > 0:
                regression_rate = regressions / len(bugs) * 100
                trends.append(
                    f"Regression rate: {regression_rate:.1f}% of bugs are regressions"
                )

        return trends

    def _identify_risk_areas(
        self, bugs: List[BugHistory], patterns: List[str]
    ) -> List[str]:
        """Identify high-risk areas."""
        risks = []

        if len(bugs) > 3:
            risks.append(
                f"High bug frequency: {len(bugs)} bugs found in historical analysis. "
                f"This area requires comprehensive test coverage."
            )

        critical_bugs = [b for b in bugs if b.severity in ['critical', 'high']]
        if len(critical_bugs) > 1:
            risks.append(
                f"Critical bug history: {len(critical_bugs)} high-severity bugs. "
                f"Implement additional safety checks and validation."
            )

        if len(patterns) > 1:
            risks.append(
                "Multiple regression patterns detected. Increase regression test coverage."
            )

        return risks

    def _generate_recommendations(
        self, bugs: List[BugHistory], patterns: List[str], risks: List[str]
    ) -> List[str]:
        """Generate testing recommendations."""
        recommendations = []

        if len(bugs) > 2:
            recommendations.append(
                "Implement comprehensive regression test suite covering historical bug fixes. "
                "Consider using mutation testing to verify test effectiveness."
            )

        if any(b.was_regression for b in bugs):
            recommendations.append(
                "Add regression tests for each fixed bug before closing tickets. "
                "Implement CI/CD pipeline with mandatory test execution."
            )

        if len(risks) > 1:
            recommendations.append(
                "This is a high-risk area. Increase test coverage to >90% and implement "
                "property-based testing for edge cases."
            )

        if not bugs:
            recommendations.append(
                "Low bug history indicates good test coverage. Maintain current testing "
                "practices and continue with regular regression testing."
            )

        return recommendations


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python qa_test_engineer_ail.py <repo_path> <question>")
        sys.exit(1)

    repo_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    qa = QATestEngineerAIL(repo_path)
    analysis = qa.enhanced_analysis(question)
    print(analysis.to_markdown())


if __name__ == '__main__':
    main()
