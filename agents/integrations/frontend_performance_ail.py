"""
AIL Integration for frontend-performance-specialist Agent

Enhances frontend-performance-specialist with archaeological intelligence for:
- Performance optimization history
- Regression patterns and causes
- Core Web Vitals evolution
- Bundle size trends
- Rendering performance history
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
class PerformanceChange:
    """Performance change record."""

    change_type: str  # "optimization", "regression", "refactoring", "feature"
    metric_affected: str  # "LCP", "FID", "CLS", "bundle_size", "render_time"
    description: str
    impact: str  # "positive", "negative", "neutral"
    estimated_improvement: str  # e.g., "-20% bundle size", "+30% render speed"
    date: datetime
    author: str
    commit_sha: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'change_type': self.change_type,
            'metric_affected': self.metric_affected,
            'description': self.description,
            'impact': self.impact,
            'estimated_improvement': self.estimated_improvement,
            'date': self.date.isoformat(),
            'author': self.author,
            'commit_sha': self.commit_sha,
        }


@dataclass
class PerformanceAnalysis:
    """Enhanced performance analysis with AIL context."""

    file_path: str
    analysis_question: str
    archaeological_context: ArchaeologicalContext
    performance_changes: List[PerformanceChange]
    optimization_history: List[str]
    regression_patterns: List[str]
    bundle_size_history: List[str]
    rendering_optimizations: List[str]
    core_web_vitals_history: List[str]
    recommendations: List[str]
    confidence: float
    query_time_ms: float

    def to_markdown(self) -> str:
        lines = [
            f"# Performance Analysis: {self.file_path}",
            f"**Question**: {self.analysis_question}",
            f"**Confidence**: {self.confidence:.1%}",
            "",
            "## Archaeological Context",
            self.archaeological_context.answer,
            "",
        ]

        if self.performance_changes:
            lines.append("## Performance Changes")
            for change in self.performance_changes:
                impact_emoji = "✅" if change.impact == "positive" else "❌" if change.impact == "negative" else "➖"
                lines.append(
                    f"### {impact_emoji} {change.change_type.replace('_', ' ').title()} - "
                    f"{change.metric_affected}"
                )
                lines.append(f"**Description**: {change.description}")
                lines.append(f"**Impact**: {change.estimated_improvement}")
                lines.append(f"**Date**: {change.date.date()} by {change.author}")
                lines.append("")

        if self.regression_patterns:
            lines.append("## Performance Regression Patterns")
            for pattern in self.regression_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        if self.optimization_history:
            lines.append("## Optimization History")
            for opt in self.optimization_history[:5]:
                lines.append(f"- {opt}")
            lines.append("")

        if self.bundle_size_history:
            lines.append("## Bundle Size History")
            for entry in self.bundle_size_history[:5]:
                lines.append(f"- {entry}")
            lines.append("")

        if self.recommendations:
            lines.append("## Performance Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append(f"*Query time: {self.query_time_ms:.0f}ms*")
        return "\n".join(lines)


class FrontendPerformanceAIL:
    """Enhances frontend-performance-specialist with Archaeological Intelligence."""

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path)
        self.repo_path = Path(repo_path).resolve()
        logger.info(f"FrontendPerformanceAIL initialized for: {repo_path}")

    def enhanced_analysis(self, user_input: str) -> PerformanceAnalysis:
        """Perform enhanced performance analysis with archaeological context."""
        context = get_context_from_input(self.provider, user_input)

        if not context:
            file_path = extract_file_path(user_input, str(self.repo_path))
            if not file_path:
                raise ValueError("Could not extract file path from input")
            question = formulate_question(user_input, task_type="optimize")
            context = self.provider.get_context_sync(file_path, question)

        perf_changes = self._extract_performance_changes(context)
        optimization_history = self._extract_optimization_history(context)
        regression_patterns = self._identify_regression_patterns(context, perf_changes)
        bundle_history = self._extract_bundle_size_history(context)
        rendering_opts = self._extract_rendering_optimizations(context)
        cwv_history = self._extract_core_web_vitals_history(context)
        recommendations = self._generate_recommendations(
            perf_changes, regression_patterns, optimization_history
        )

        return PerformanceAnalysis(
            file_path=context.file_path,
            analysis_question=context.question,
            archaeological_context=context,
            performance_changes=perf_changes,
            optimization_history=optimization_history,
            regression_patterns=regression_patterns,
            bundle_size_history=bundle_history,
            rendering_optimizations=rendering_opts,
            core_web_vitals_history=cwv_history,
            recommendations=recommendations,
            confidence=context.confidence,
            query_time_ms=context.query_time_ms,
        )

    def _extract_performance_changes(self, context: ArchaeologicalContext) -> List[PerformanceChange]:
        """Extract performance changes."""
        changes = []
        change_keywords = {
            'optimization': ['optimize', 'improve performance', 'speed up', 'faster'],
            'regression': ['slow', 'regression', 'performance issue', 'bottleneck'],
            'refactoring': ['refactor', 'restructure', 'cleanup'],
            'feature': ['add', 'implement', 'new feature'],
        }

        metric_keywords = {
            'LCP': ['lcp', 'largest contentful paint', 'loading'],
            'FID': ['fid', 'first input delay', 'interactivity', 'responsive'],
            'CLS': ['cls', 'cumulative layout shift', 'layout'],
            'bundle_size': ['bundle', 'size', 'webpack', 'chunk'],
            'render_time': ['render', 'paint', 'frame', 'fps'],
        }

        for source in context.sources[:5]:
            msg_lower = source.commit_message.lower()

            # Determine change type
            change_type = 'feature'
            for ctype, keywords in change_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    change_type = ctype
                    break

            # Determine metric affected
            metric = 'render_time'
            for m, keywords in metric_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    metric = m
                    break

            # Determine impact
            impact = 'neutral'
            if change_type == 'optimization':
                impact = 'positive'
            elif change_type == 'regression':
                impact = 'negative'

            # Extract improvement estimate (if mentioned)
            improvement = "Unknown"
            if '%' in source.commit_message:
                # Try to extract percentage
                import re
                match = re.search(r'(\d+)%', source.commit_message)
                if match:
                    improvement = f"{match.group(1)}% improvement"

            changes.append(PerformanceChange(
                change_type=change_type,
                metric_affected=metric,
                description=source.commit_message[:200],
                impact=impact,
                estimated_improvement=improvement,
                date=source.date,
                author=source.author,
                commit_sha=source.commit_sha,
            ))

        return changes

    def _extract_optimization_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract optimization history."""
        history = []
        opt_keywords = [
            'optimize', 'performance', 'cache', 'lazy load', 'code split',
            'memoize', 'debounce', 'throttle', 'virtualize', 'prefetch'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in opt_keywords):
                history.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return history

    def _identify_regression_patterns(
        self, context: ArchaeologicalContext, changes: List[PerformanceChange]
    ) -> List[str]:
        """Identify performance regression patterns."""
        patterns = []

        # Count regressions
        regressions = [c for c in changes if c.change_type == 'regression']
        if len(regressions) > 1:
            patterns.append(
                f"Multiple performance regressions detected ({len(regressions)} instances). "
                f"Consider implementing performance budgets and automated testing."
            )

        # Check for repeated metrics
        regression_metrics = [r.metric_affected for r in regressions]
        for metric in set(regression_metrics):
            count = regression_metrics.count(metric)
            if count > 1:
                patterns.append(
                    f"Recurring {metric} regressions ({count} instances). "
                    f"Monitor this metric closely in CI/CD."
                )

        return patterns

    def _extract_bundle_size_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract bundle size history."""
        history = []
        bundle_keywords = [
            'bundle', 'webpack', 'rollup', 'vite', 'chunk', 'split',
            'tree-shake', 'minify', 'compress'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in bundle_keywords):
                history.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return history

    def _extract_rendering_optimizations(self, context: ArchaeologicalContext) -> List[str]:
        """Extract rendering optimizations."""
        optimizations = []
        render_keywords = [
            'render', 'paint', 'reflow', 'repaint', 'composite', 'gpu',
            'virtualize', 'react.memo', 'usememo', 'usecallback'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in render_keywords):
                optimizations.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return optimizations

    def _extract_core_web_vitals_history(self, context: ArchaeologicalContext) -> List[str]:
        """Extract Core Web Vitals history."""
        history = []
        cwv_keywords = [
            'lcp', 'fid', 'cls', 'core web vitals', 'web vitals',
            'largest contentful paint', 'first input delay', 'cumulative layout shift'
        ]

        for source in context.sources:
            if any(kw in source.commit_message.lower() for kw in cwv_keywords):
                history.append(f"{source.commit_message[:100]} ({source.date.date()})")

        return history

    def _generate_recommendations(
        self, changes: List[PerformanceChange],
        patterns: List[str], history: List[str]
    ) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []

        # Check for regressions
        regressions = [c for c in changes if c.change_type == 'regression']
        if len(regressions) > 1:
            recommendations.append(
                "Multiple performance regressions detected. Implement performance budgets "
                "in CI/CD (e.g., bundle-size-bot, Lighthouse CI) to catch regressions early."
            )

        # Check optimization frequency
        optimizations = [c for c in changes if c.change_type == 'optimization']
        if len(optimizations) < 2 and len(changes) > 3:
            recommendations.append(
                "Low optimization frequency relative to feature development. Schedule regular "
                "performance audits and implement proactive optimization strategy."
            )

        # Metric-specific recommendations
        metrics = [c.metric_affected for c in changes]
        if 'bundle_size' in metrics:
            recommendations.append(
                "Bundle size concerns detected. Implement code splitting, tree-shaking, "
                "and lazy loading. Consider using bundle analyzer tools."
            )

        if 'LCP' in metrics:
            recommendations.append(
                "LCP (Largest Contentful Paint) issues found. Optimize critical rendering path, "
                "use resource hints (preload, prefetch), and optimize images."
            )

        if 'CLS' in metrics:
            recommendations.append(
                "CLS (Cumulative Layout Shift) concerns. Reserve space for dynamic content, "
                "avoid inserting content above existing content, use CSS aspect-ratio."
            )

        if not recommendations:
            recommendations.append(
                "Performance history shows good optimization practices. Continue monitoring "
                "Core Web Vitals and maintaining performance budgets."
            )

        return recommendations


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python frontend_performance_ail.py <repo_path> <question>")
        sys.exit(1)

    repo_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    perf = FrontendPerformanceAIL(repo_path)
    analysis = perf.enhanced_analysis(question)
    print(analysis.to_markdown())


if __name__ == '__main__':
    main()
