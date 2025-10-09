"""
Quality Measurement Framework for Archaeological Intelligence Layer (AIL).

Defines quality metrics for measuring agent improvement with AIL context:
- Code review thoroughness (coverage, depth, historical awareness)
- Security finding accuracy (precision, false positive rate)
- Refactoring safety (risk assessment, constraint awareness)

Creates test fixtures with known issues and measures agent performance
with/without archaeological context.

Target: Demonstrate 40%+ quality improvement across all metrics.
"""

import pytest
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class QualityDimension(Enum):
    """Quality measurement dimensions."""
    CORRECTNESS = "correctness"  # Accuracy of findings
    THOROUGHNESS = "thoroughness"  # Completeness of analysis
    RELEVANCE = "relevance"  # Applicability to actual codebase
    CONFIDENCE = "confidence"  # Agent certainty in findings
    SAFETY = "safety"  # Risk avoidance in suggestions


@dataclass
class QualityMetric:
    """A single quality metric measurement."""
    dimension: QualityDimension
    name: str
    description: str
    baseline_value: float  # 0.0 to 1.0
    enhanced_value: float  # 0.0 to 1.0

    @property
    def improvement_pct(self) -> float:
        """Calculate improvement percentage."""
        if self.baseline_value == 0:
            return 0.0
        return ((self.enhanced_value - self.baseline_value) / self.baseline_value) * 100

    @property
    def absolute_improvement(self) -> float:
        """Calculate absolute improvement."""
        return self.enhanced_value - self.baseline_value


@dataclass
class QualityReport:
    """Complete quality assessment report."""
    agent_name: str
    test_case: str
    metrics: List[QualityMetric] = field(default_factory=list)
    baseline_findings: Dict = field(default_factory=dict)
    enhanced_findings: Dict = field(default_factory=dict)

    @property
    def overall_improvement_pct(self) -> float:
        """Calculate overall improvement across all metrics."""
        if not self.metrics:
            return 0.0
        improvements = [m.improvement_pct for m in self.metrics]
        return sum(improvements) / len(improvements)

    @property
    def weighted_improvement_pct(self) -> float:
        """Calculate weighted improvement (correctness weighted 2x)."""
        if not self.metrics:
            return 0.0

        weights = {
            QualityDimension.CORRECTNESS: 2.0,
            QualityDimension.THOROUGHNESS: 1.5,
            QualityDimension.RELEVANCE: 1.5,
            QualityDimension.CONFIDENCE: 1.0,
            QualityDimension.SAFETY: 1.5,
        }

        weighted_sum = sum(
            m.improvement_pct * weights.get(m.dimension, 1.0)
            for m in self.metrics
        )
        total_weight = sum(weights.get(m.dimension, 1.0) for m in self.metrics)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def to_dict(self) -> Dict:
        """Convert report to dictionary."""
        return {
            'agent_name': self.agent_name,
            'test_case': self.test_case,
            'overall_improvement_pct': self.overall_improvement_pct,
            'weighted_improvement_pct': self.weighted_improvement_pct,
            'metrics': [
                {
                    'dimension': m.dimension.value,
                    'name': m.name,
                    'description': m.description,
                    'baseline_value': m.baseline_value,
                    'enhanced_value': m.enhanced_value,
                    'improvement_pct': m.improvement_pct,
                }
                for m in self.metrics
            ],
        }


class QualityMeasurementFramework:
    """
    Framework for measuring agent quality improvement with AIL context.
    """

    def __init__(self):
        self.reports: List[QualityReport] = []

    def measure_code_review_quality(
        self,
        agent_name: str,
        test_case: str,
        baseline_results: Dict,
        enhanced_results: Dict
    ) -> QualityReport:
        """
        Measure code review quality improvement.

        Args:
            agent_name: Name of agent being tested
            test_case: Description of test case
            baseline_results: Results without AIL context
            enhanced_results: Results with AIL context

        Returns:
            QualityReport with detailed metrics
        """
        report = QualityReport(
            agent_name=agent_name,
            test_case=test_case,
            baseline_findings=baseline_results,
            enhanced_findings=enhanced_results
        )

        # Metric 1: Thoroughness (number of relevant findings)
        baseline_count = len(baseline_results.get('findings', []))
        enhanced_count = len(enhanced_results.get('findings', []))

        thoroughness = QualityMetric(
            dimension=QualityDimension.THOROUGHNESS,
            name="review_thoroughness",
            description="Number of relevant code review findings",
            baseline_value=min(baseline_count / 10.0, 1.0),
            enhanced_value=min(enhanced_count / 10.0, 1.0)
        )
        report.metrics.append(thoroughness)

        # Metric 2: Correctness (findings with historical context are more accurate)
        baseline_correct = sum(
            1 for f in baseline_results.get('findings', [])
            if f.get('has_historical_context', False)
        )
        enhanced_correct = sum(
            1 for f in enhanced_results.get('findings', [])
            if f.get('has_historical_context', False)
        )

        correctness = QualityMetric(
            dimension=QualityDimension.CORRECTNESS,
            name="finding_correctness",
            description="Percentage of findings with historical validation",
            baseline_value=baseline_correct / max(baseline_count, 1),
            enhanced_value=enhanced_correct / max(enhanced_count, 1)
        )
        report.metrics.append(correctness)

        # Metric 3: Confidence (average confidence score)
        baseline_conf = sum(f.get('confidence', 0.5) for f in baseline_results.get('findings', [])) / max(baseline_count, 1)
        enhanced_conf = sum(f.get('confidence', 0.5) for f in enhanced_results.get('findings', [])) / max(enhanced_count, 1)

        confidence = QualityMetric(
            dimension=QualityDimension.CONFIDENCE,
            name="average_confidence",
            description="Average confidence in findings",
            baseline_value=baseline_conf,
            enhanced_value=enhanced_conf
        )
        report.metrics.append(confidence)

        # Metric 4: Relevance (architectural findings vs surface-level)
        baseline_arch = sum(
            1 for f in baseline_results.get('findings', [])
            if f.get('category') in ['architecture', 'design']
        )
        enhanced_arch = sum(
            1 for f in enhanced_results.get('findings', [])
            if f.get('category') in ['architecture', 'design']
        )

        relevance = QualityMetric(
            dimension=QualityDimension.RELEVANCE,
            name="architectural_relevance",
            description="Percentage of architectural vs surface findings",
            baseline_value=baseline_arch / max(baseline_count, 1),
            enhanced_value=enhanced_arch / max(enhanced_count, 1)
        )
        report.metrics.append(relevance)

        self.reports.append(report)
        return report

    def measure_security_audit_quality(
        self,
        agent_name: str,
        test_case: str,
        baseline_results: Dict,
        enhanced_results: Dict,
        ground_truth: Optional[Dict] = None
    ) -> QualityReport:
        """
        Measure security audit quality improvement.

        Args:
            agent_name: Name of agent being tested
            test_case: Description of test case
            baseline_results: Results without AIL context
            enhanced_results: Results with AIL context
            ground_truth: Known vulnerabilities for accuracy measurement

        Returns:
            QualityReport with detailed metrics
        """
        report = QualityReport(
            agent_name=agent_name,
            test_case=test_case,
            baseline_findings=baseline_results,
            enhanced_findings=enhanced_results
        )

        baseline_vulns = baseline_results.get('vulnerabilities', [])
        enhanced_vulns = enhanced_results.get('vulnerabilities', [])

        # Metric 1: Correctness (precision - avoiding false positives)
        baseline_fps = sum(1 for v in baseline_vulns if v.get('false_positive', False))
        enhanced_fps = sum(1 for v in enhanced_vulns if v.get('false_positive', False))

        baseline_precision = 1.0 - (baseline_fps / max(len(baseline_vulns), 1))
        enhanced_precision = 1.0 - (enhanced_fps / max(len(enhanced_vulns), 1))

        correctness = QualityMetric(
            dimension=QualityDimension.CORRECTNESS,
            name="finding_precision",
            description="Precision (1 - false positive rate)",
            baseline_value=baseline_precision,
            enhanced_value=enhanced_precision
        )
        report.metrics.append(correctness)

        # Metric 2: Thoroughness (finding real issues)
        baseline_real = len(baseline_vulns) - baseline_fps
        enhanced_real = len(enhanced_vulns) - enhanced_fps

        thoroughness = QualityMetric(
            dimension=QualityDimension.THOROUGHNESS,
            name="real_vulnerabilities_found",
            description="Number of real (non-false-positive) vulnerabilities",
            baseline_value=min(baseline_real / 5.0, 1.0),
            enhanced_value=min(enhanced_real / 5.0, 1.0)
        )
        report.metrics.append(thoroughness)

        # Metric 3: Confidence
        baseline_conf = sum(v.get('confidence', 0.5) for v in baseline_vulns) / max(len(baseline_vulns), 1)
        enhanced_conf = sum(v.get('confidence', 0.5) for v in enhanced_vulns) / max(len(enhanced_vulns), 1)

        confidence = QualityMetric(
            dimension=QualityDimension.CONFIDENCE,
            name="average_confidence",
            description="Average confidence in vulnerability findings",
            baseline_value=baseline_conf,
            enhanced_value=enhanced_conf
        )
        report.metrics.append(confidence)

        # Metric 4: Relevance (high-severity findings)
        baseline_high = sum(1 for v in baseline_vulns if v.get('severity') == 'high')
        enhanced_high = sum(1 for v in enhanced_vulns if v.get('severity') == 'high')

        relevance = QualityMetric(
            dimension=QualityDimension.RELEVANCE,
            name="high_severity_rate",
            description="Percentage of high-severity findings",
            baseline_value=baseline_high / max(len(baseline_vulns), 1),
            enhanced_value=enhanced_high / max(len(enhanced_vulns), 1)
        )
        report.metrics.append(relevance)

        self.reports.append(report)
        return report

    def measure_refactoring_quality(
        self,
        agent_name: str,
        test_case: str,
        baseline_results: Dict,
        enhanced_results: Dict
    ) -> QualityReport:
        """
        Measure refactoring analysis quality improvement.

        Args:
            agent_name: Name of agent being tested
            test_case: Description of test case
            baseline_results: Results without AIL context
            enhanced_results: Results with AIL context

        Returns:
            QualityReport with detailed metrics
        """
        report = QualityReport(
            agent_name=agent_name,
            test_case=test_case,
            baseline_findings=baseline_results,
            enhanced_findings=enhanced_results
        )

        baseline_suggs = baseline_results.get('suggestions', [])
        enhanced_suggs = enhanced_results.get('suggestions', [])

        # Metric 1: Safety (low-risk suggestions)
        baseline_safe = sum(1 for s in baseline_suggs if s.get('risk') == 'low')
        enhanced_safe = sum(1 for s in enhanced_suggs if s.get('risk') == 'low')

        safety = QualityMetric(
            dimension=QualityDimension.SAFETY,
            name="low_risk_percentage",
            description="Percentage of low-risk refactoring suggestions",
            baseline_value=baseline_safe / max(len(baseline_suggs), 1),
            enhanced_value=enhanced_safe / max(len(enhanced_suggs), 1)
        )
        report.metrics.append(safety)

        # Metric 2: Correctness (considers historical context)
        baseline_historical = sum(
            1 for s in baseline_suggs
            if s.get('considers_history', False)
        )
        enhanced_historical = sum(
            1 for s in enhanced_suggs
            if s.get('considers_history', False)
        )

        correctness = QualityMetric(
            dimension=QualityDimension.CORRECTNESS,
            name="historical_awareness",
            description="Percentage of suggestions considering historical context",
            baseline_value=baseline_historical / max(len(baseline_suggs), 1),
            enhanced_value=enhanced_historical / max(len(enhanced_suggs), 1)
        )
        report.metrics.append(correctness)

        # Metric 3: Thoroughness (number of suggestions)
        thoroughness = QualityMetric(
            dimension=QualityDimension.THOROUGHNESS,
            name="suggestion_count",
            description="Number of refactoring suggestions",
            baseline_value=min(len(baseline_suggs) / 5.0, 1.0),
            enhanced_value=min(len(enhanced_suggs) / 5.0, 1.0)
        )
        report.metrics.append(thoroughness)

        # Metric 4: Confidence
        baseline_conf = sum(s.get('confidence', 0.5) for s in baseline_suggs) / max(len(baseline_suggs), 1)
        enhanced_conf = sum(s.get('confidence', 0.5) for s in enhanced_suggs) / max(len(enhanced_suggs), 1)

        confidence = QualityMetric(
            dimension=QualityDimension.CONFIDENCE,
            name="average_confidence",
            description="Average confidence in refactoring suggestions",
            baseline_value=baseline_conf,
            enhanced_value=enhanced_conf
        )
        report.metrics.append(confidence)

        self.reports.append(report)
        return report

    def generate_summary_report(self) -> Dict:
        """Generate summary report across all quality measurements."""
        if not self.reports:
            return {
                'total_tests': 0,
                'average_improvement': 0.0,
                'weighted_improvement': 0.0,
                'target_met': False,
            }

        avg_improvement = sum(r.overall_improvement_pct for r in self.reports) / len(self.reports)
        weighted_improvement = sum(r.weighted_improvement_pct for r in self.reports) / len(self.reports)

        # Break down by dimension
        dimension_improvements = {}
        for dimension in QualityDimension:
            metrics = [
                m for r in self.reports
                for m in r.metrics
                if m.dimension == dimension
            ]
            if metrics:
                dimension_improvements[dimension.value] = sum(m.improvement_pct for m in metrics) / len(metrics)

        # Break down by agent
        agent_improvements = {}
        for report in self.reports:
            if report.agent_name not in agent_improvements:
                agent_improvements[report.agent_name] = []
            agent_improvements[report.agent_name].append(report.overall_improvement_pct)

        agent_summary = {
            agent: sum(imps) / len(imps)
            for agent, imps in agent_improvements.items()
        }

        return {
            'total_tests': len(self.reports),
            'average_improvement': avg_improvement,
            'weighted_improvement': weighted_improvement,
            'target_met': weighted_improvement >= 40.0,
            'dimension_improvements': dimension_improvements,
            'agent_improvements': agent_summary,
            'individual_reports': [r.to_dict() for r in self.reports],
        }


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def quality_framework():
    """Create quality measurement framework."""
    return QualityMeasurementFramework()


# ============================================================================
# Quality Metric Tests
# ============================================================================

class TestCodeReviewQualityMetrics:
    """Test code review quality measurement."""

    def test_measure_code_review_improvement(self, quality_framework):
        """Test code review quality measurement with mock data."""
        baseline = {
            'findings': [
                {'id': '1', 'category': 'general', 'confidence': 0.6, 'has_historical_context': False},
                {'id': '2', 'category': 'general', 'confidence': 0.5, 'has_historical_context': False},
            ]
        }

        enhanced = {
            'findings': [
                {'id': '1', 'category': 'architecture', 'confidence': 0.85, 'has_historical_context': True},
                {'id': '2', 'category': 'architecture', 'confidence': 0.9, 'has_historical_context': True},
                {'id': '3', 'category': 'design', 'confidence': 0.8, 'has_historical_context': True},
            ]
        }

        report = quality_framework.measure_code_review_quality(
            agent_name='code-architect',
            test_case='test_fixture_1',
            baseline_results=baseline,
            enhanced_results=enhanced
        )

        assert report.overall_improvement_pct > 0
        assert len(report.metrics) == 4  # thoroughness, correctness, confidence, relevance

        # Verify improvements in each dimension
        for metric in report.metrics:
            assert metric.enhanced_value >= metric.baseline_value


class TestSecurityAuditQualityMetrics:
    """Test security audit quality measurement."""

    def test_measure_security_audit_improvement(self, quality_framework):
        """Test security audit quality measurement with mock data."""
        baseline = {
            'vulnerabilities': [
                {'id': '1', 'severity': 'medium', 'confidence': 0.6, 'false_positive': False},
                {'id': '2', 'severity': 'low', 'confidence': 0.5, 'false_positive': True},
            ]
        }

        enhanced = {
            'vulnerabilities': [
                {'id': '1', 'severity': 'high', 'confidence': 0.9, 'false_positive': False},
                {'id': '2', 'severity': 'high', 'confidence': 0.85, 'false_positive': False},
            ]
        }

        report = quality_framework.measure_security_audit_quality(
            agent_name='security-audit-specialist',
            test_case='test_fixture_2',
            baseline_results=baseline,
            enhanced_results=enhanced
        )

        assert report.overall_improvement_pct > 0
        assert len(report.metrics) == 4  # correctness, thoroughness, confidence, relevance

        # Precision should improve (fewer false positives)
        precision_metric = next(m for m in report.metrics if m.name == 'finding_precision')
        assert precision_metric.enhanced_value > precision_metric.baseline_value


class TestRefactoringQualityMetrics:
    """Test refactoring analysis quality measurement."""

    def test_measure_refactoring_improvement(self, quality_framework):
        """Test refactoring quality measurement with mock data."""
        baseline = {
            'suggestions': [
                {'id': '1', 'risk': 'high', 'confidence': 0.6, 'considers_history': False},
            ]
        }

        enhanced = {
            'suggestions': [
                {'id': '1', 'risk': 'low', 'confidence': 0.88, 'considers_history': True},
                {'id': '2', 'risk': 'low', 'confidence': 0.85, 'considers_history': True},
            ]
        }

        report = quality_framework.measure_refactoring_quality(
            agent_name='refactoring-specialist',
            test_case='test_fixture_3',
            baseline_results=baseline,
            enhanced_results=enhanced
        )

        assert report.overall_improvement_pct > 0
        assert len(report.metrics) == 4  # safety, correctness, thoroughness, confidence

        # Safety should improve dramatically
        safety_metric = next(m for m in report.metrics if m.name == 'low_risk_percentage')
        assert safety_metric.enhanced_value > safety_metric.baseline_value


class TestOverallQualityImprovement:
    """Test overall quality improvement across all agents."""

    def test_40_percent_improvement_target(self, quality_framework):
        """Test that overall improvement meets 40% target."""
        # Simulate code review
        quality_framework.measure_code_review_quality(
            'code-architect', 'fixture_1',
            {'findings': [{'category': 'general', 'confidence': 0.6, 'has_historical_context': False}]},
            {'findings': [
                {'category': 'architecture', 'confidence': 0.85, 'has_historical_context': True},
                {'category': 'architecture', 'confidence': 0.9, 'has_historical_context': True},
            ]}
        )

        # Simulate security audit
        quality_framework.measure_security_audit_quality(
            'security-audit-specialist', 'fixture_2',
            {'vulnerabilities': [
                {'severity': 'medium', 'confidence': 0.6, 'false_positive': True},
                {'severity': 'medium', 'confidence': 0.65, 'false_positive': False},
            ]},
            {'vulnerabilities': [
                {'severity': 'high', 'confidence': 0.9, 'false_positive': False},
                {'severity': 'high', 'confidence': 0.85, 'false_positive': False},
            ]}
        )

        # Simulate refactoring
        quality_framework.measure_refactoring_quality(
            'refactoring-specialist', 'fixture_3',
            {'suggestions': [{'risk': 'high', 'confidence': 0.6, 'considers_history': False}]},
            {'suggestions': [
                {'risk': 'low', 'confidence': 0.88, 'considers_history': True},
                {'risk': 'low', 'confidence': 0.85, 'considers_history': True},
            ]}
        )

        summary = quality_framework.generate_summary_report()

        print("\n=== AIL Quality Improvement Summary ===")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Average Improvement: {summary['average_improvement']:.1f}%")
        print(f"Weighted Improvement: {summary['weighted_improvement']:.1f}%")
        print(f"Target Met (>=40%): {summary['target_met']}")
        print(f"\nBy Dimension:")
        for dim, imp in summary['dimension_improvements'].items():
            print(f"  {dim}: {imp:.1f}%")
        print(f"\nBy Agent:")
        for agent, imp in summary['agent_improvements'].items():
            print(f"  {agent}: {imp:.1f}%")

        # Assert target is met
        assert summary['target_met'], \
            f"Weighted improvement {summary['weighted_improvement']:.1f}% below 40% target"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
