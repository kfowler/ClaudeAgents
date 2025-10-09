"""
AIL Integration for debugging-specialist Agent

Enhances debugging-specialist with archaeological intelligence for:
- Bug fix history and patterns
- Root cause analysis from past fixes
- Debugging strategy evolution
- Common failure modes
- Fix effectiveness tracking
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
class BugFix:
    """Bug fix record."""

    bug_category: str  # "race_condition", "null_pointer", "logic_error", "memory_leak"
    symptoms: str
    root_cause: str
    solution: str
    date: datetime
    author: str
    commit_sha: str
    time_to_fix_days: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'bug_category': self.bug_category,
            'symptoms': self.symptoms,
            'root_cause': self.root_cause,
            'solution': self.solution,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
            'time_to_fix_days': self.time_to_fix_days,
        }


@dataclass
class DebuggingAnalysis:
    """Enhanced debugging analysis with AIL context."""

    file_path: str
    debug_question: str
    archaeological_context: ArchaeologicalContext
    bug_fixes: List[BugFix]
    common_failure_modes: List[str]
    root_cause_patterns: List[str]
    debugging_strategies: List[str]
    similar_past_issues: List[str]
    recommendations: List[str]
    confidence: float
    query_time_ms: float

    def to_markdown(self) -> str:
        lines = [
            f"# Debugging Analysis: {self.file_path}",
            f"**Question**: {self.debug_question}",
            f"**Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.bug_fixes:
            lines.append("## Historical Bug Fixes")
            for fix in self.bug_fixes:
                lines.append(f"### {fix.bug_category.replace('_', ' ').title()}")
                lines.append(f"**Symptoms**: {fix.symptoms}")
                lines.append(f"**Root Cause**: {fix.root_cause}")
                lines.append(f"**Solution**: {fix.solution}")
                lines.append(f"**Date**: {fix.date.date()} by {fix.author} (fixed in {fix.time_to_fix_days} days)")
                lines.append("")

        if self.common_failure_modes:
            lines.append("## Common Failure Modes")
            for mode in self.common_failure_modes:
                lines.append(f"- {mode}")
            lines.append("")

        if self.root_cause_patterns:
            lines.append("## Root Cause Patterns")
            for pattern in self.root_cause_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.similar_past_issues:
            lines.append("## Similar Past Issues")
            for issue in self.similar_past_issues:
                lines.append(f"- {issue}")
            lines.append("")

        if self.recommendations:
            lines.append("## Debugging Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms*")
        return "\n".join(lines)


class DebuggingSpecialistAIL:
    """Enhances debugging-specialist with Archaeological Intelligence."""

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"DebuggingSpecialistAIL initialized for: {repo_path}")

    def enhanced_analysis(self, user_input: str) -> DebuggingAnalysis:
        """Perform enhanced debugging analysis with archaeological context."""
        context = get_context_from_input(self.provider, user_input)

        if not context:
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")
            question = formulate_question(user_input, task_type="debug")
            context = self.provider.get_context_sync(file_path, question)

        bug_fixes = self._extract_bug_fixes(context)
        failure_modes = self._identify_failure_modes(context, bug_fixes)
        root_causes = self._extract_root_cause_patterns(bug_fixes)
        strategies = self._extract_debugging_strategies(context)
        similar_issues = self._find_similar_issues(context, bug_fixes)
        recommendations = self._generate_recommendations(
            bug_fixes, failure_modes, root_causes
        )

        return DebuggingAnalysis(
            file_path=context.file_path,
            debug_question=context.question,
            archaeological_context=context,
            bug_fixes=bug_fixes,
            common_failure_modes=failure_modes,
            root_cause_patterns=root_causes,
            debugging_strategies=strategies,
            similar_past_issues=similar_issues,
            recommendations=recommendations,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_bug_fixes(self, context: ArchaeologicalContext) -> List[BugFix]:
        """Extract bug fix records."""
        fixes = []
        bug_categories = {
            'race_condition': ['race', 'concurrency', 'thread', 'async', 'timing'],
            'null_pointer': ['null', 'undefined', 'none', 'nil', 'null pointer'],
            'logic_error': ['logic', 'algorithm', 'calculation', 'wrong result'],
            'memory_leak': ['memory', 'leak', 'garbage', 'heap', 'oom'],
        }

        for source in context.sources[:5]:
            msg_lower = source.commit_message.lower()

            # Check if it's a bug fix
            if not any(kw in msg_lower for kw in ['fix', 'bug', 'issue', 'error', 'problem', 'resolve']):
                continue

            # Determine bug category
            bug_category = 'logic_error'
            for category, keywords in bug_categories.items():
                if any(kw in msg_lower for kw in keywords):
                    bug_category = category
                    break

            # Estimate time to fix (placeholder - could be enhanced with issue tracking integration)
            time_to_fix = 1  # Default to 1 day

            fixes.append(BugFix(
                bug_category=bug_category,
                symptoms=source.commit_message[:150],
                root_cause=source.excerpt[:200],
                solution=source.commit_message[:200],
                date=source.date,
                author=source.author,
                commit_sha=source.commit_sha,
                time_to_fix_days=time_to_fix,
            ))

        return fixes

    def _identify_failure_modes(
        self, context: ArchaeologicalContext, fixes: List[BugFix]
    ) -> List[str]:
        """Identify common failure modes."""
        modes = []

        # Analyze bug categories
        categories = [f.bug_category for f in fixes]
        for category in set(categories):
            count = categories.count(category)
            if count > 1:
                modes.append(
                    f"{category.replace('_', ' ').title()}: {count} occurrences - "
                    f"common failure pattern in this code"
                )

        # Look for error patterns in commit messages
        error_keywords = ['crash', 'fail', 'error', 'exception', 'timeout']
        for keyword in error_keywords:
            matches = sum(1 for s in context.sources
                         if keyword in s.commit_message.lower())
            if matches > 1:
                modes.append(f"{keyword.title()} issues: {matches} occurrences")

        return modes

    def _extract_root_cause_patterns(self, fixes: List[BugFix]) -> List[str]:
        """Extract root cause patterns from fixes."""
        patterns = []

        # Common root cause keywords
        root_cause_keywords = {
            'missing_validation': ['validation', 'check', 'verify', 'sanitize'],
            'incorrect_assumption': ['assume', 'expect', 'should', 'supposed'],
            'edge_case': ['edge', 'boundary', 'corner', 'special case'],
            'state_management': ['state', 'synchronization', 'consistency'],
        }

        for fix in fixes:
            root_cause_lower = fix.root_cause.lower()
            for pattern_name, keywords in root_cause_keywords.items():
                if any(kw in root_cause_lower for kw in keywords):
                    patterns.append(
                        f"{pattern_name.replace('_', ' ').title()} in {fix.commit_sha[:8]}: "
                        f"{fix.root_cause[:100]}"
                    )
                    break

        return patterns[:5]

    def _extract_debugging_strategies(self, context: ArchaeologicalContext) -> List[str]:
        """Extract debugging strategies from context."""
        strategies = []
        strategy_keywords = [
            'debug', 'log', 'trace', 'breakpoint', 'inspect',
            'profile', 'monitor', 'diagnostic', 'reproduce'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in strategy_keywords):
                strategies.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return strategies[:5]

    def _find_similar_issues(
        self, context: ArchaeologicalContext, fixes: List[BugFix]
    ) -> List[str]:
        """Find similar past issues."""
        similar = []

        # Look for repeated bug categories
        categories = [f.bug_category for f in fixes]
        for category in set(categories):
            count = categories.count(category)
            if count > 1:
                examples = [f for f in fixes if f.bug_category == category][:2]
                for example in examples:
                    similar.append(
                        f"{category.replace('_', ' ').title()}: {example.symptoms[:80]} "
                        f"({example.date.date()})"
                    )

        return similar

    def _generate_recommendations(
        self, fixes: List[BugFix], modes: List[str], root_causes: List[str]
    ) -> List[str]:
        """Generate debugging recommendations."""
        recommendations = []

        if len(fixes) > 2:
            recommendations.append(
                "This area has a history of bugs. Investigate with extra caution and "
                "review historical fixes for insights into root causes."
            )

        # Category-specific recommendations
        categories = [f.bug_category for f in fixes]
        if 'race_condition' in categories:
            recommendations.append(
                "Race condition bugs detected in history. Use thread-safe data structures, "
                "proper locking mechanisms, and consider using debugging tools like "
                "ThreadSanitizer or race detectors."
            )

        if 'null_pointer' in categories:
            recommendations.append(
                "Null/undefined reference bugs found. Implement null-safety patterns, "
                "use optional types, and add defensive null checks at boundaries."
            )

        if 'memory_leak' in categories:
            recommendations.append(
                "Memory leak history detected. Use memory profilers (Valgrind, heaptrack), "
                "implement proper resource cleanup, and review object lifecycle management."
            )

        if len(modes) > 2:
            recommendations.append(
                "Multiple failure modes identified. Add comprehensive error handling, "
                "logging, and monitoring to catch issues early in production."
            )

        if not fixes:
            recommendations.append(
                "No historical bugs found. This appears to be a stable area, but still "
                "follow standard debugging practices: reproduce issue, isolate cause, "
                "implement fix, add regression test."
            )

        return recommendations


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python debugging_specialist_ail.py <repo_path> <question>")
        sys.exit(1)

    repo_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    debugger = DebuggingSpecialistAIL(repo_path)
    analysis = debugger.enhanced_analysis(question)
    print(analysis.to_markdown())


if __name__ == '__main__':
    main()
