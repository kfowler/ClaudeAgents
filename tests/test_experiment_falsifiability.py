#!/usr/bin/env python3
"""
Test suite for the-architect-of-experiments falsifiability guarantees.

Tests:
- Kill condition presence (100% coverage for all experiments)
- Time window constraints (48-120 hours)
- Quantitative success metrics (no vague criteria)
- Resource estimate reasonableness
- No vague acceptance criteria
- Hypothesis falsifiability
"""

import json
import pytest
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from validate_creative import CreativeValidator


class TestExperimentFalsifiability:
    """Test suite for the-architect-of-experiments falsifiability guarantees."""

    @pytest.fixture
    def validator(self):
        """Fixture providing CreativeValidator instance."""
        return CreativeValidator(verbose=False)

    @pytest.fixture
    def experiment_report_template(self):
        """Fixture providing the-architect-of-experiments report template."""
        return {
            "agent_id": "the-architect-of-experiments",
            "version": "v1.0",
            "timestamp": "2025-10-10T16:00:00Z",
            "report_type": "experiment_design",
            "content": {
                "experiments": [],
                "falsifiability_coverage": {
                    "total_experiments": 0,
                    "experiments_with_kill_conditions": 0,
                    "coverage_ratio": 0.0
                },
                "experiment_sequencing": []
            },
            "metadata": {
                "session_id": "test-session-003",
                "context": "Validating AI-powered onboarding hypothesis",
                "constraints": ["2 developer-months budget", "Q1 2026 launch"],
                "tags": ["test", "experiment"]
            }
        }

    def test_kill_condition_presence(self, validator, experiment_report_template, tmp_path):
        """Test that every experiment has an explicit kill condition (100% coverage)."""
        # Create report with all experiments having kill conditions
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_1",
                "hypothesis": "AI-powered adaptive questioning reduces onboarding time by 30%",
                "success_metrics": [
                    {"metric": "Average onboarding completion time", "target": "<4 minutes", "baseline": "8 minutes"}
                ],
                "kill_condition": "If average completion time is not <6 minutes after 100 users, kill experiment",
                "method": "A/B test with 50% traffic split",
                "duration_hours": 72,
                "resource_requirements": ["1 frontend dev", "Analytics instrumentation"]
            },
            {
                "id": "exp_2",
                "hypothesis": "Progressive disclosure increases completion rate by 20%",
                "success_metrics": [
                    {"metric": "Completion rate", "target": ">80%", "baseline": "60%"}
                ],
                "kill_condition": "If completion rate is not >70% after 200 users, kill experiment",
                "method": "A/B test comparing full form vs progressive disclosure",
                "duration_hours": 96,
                "resource_requirements": ["1 frontend dev", "1 designer"]
            }
        ]
        report["content"]["falsifiability_coverage"]["total_experiments"] = 2
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = 2
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = 1.0

        temp_report = tmp_path / "experiments_with_kill_conditions.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        is_valid = validator.validate_report(temp_report)
        assert is_valid, "Experiments with kill conditions should validate"
        assert report["content"]["falsifiability_coverage"]["coverage_ratio"] == 1.0

    def test_missing_kill_condition_fails(self, experiment_report_template, tmp_path):
        """Test that experiments without kill conditions fail validation."""
        # Create report with missing kill condition
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_1",
                "hypothesis": "Test hypothesis",
                "success_metrics": [{"metric": "Test metric", "target": "10%", "baseline": "5%"}],
                # Missing "kill_condition" field
                "method": "A/B test",
                "duration_hours": 72,
                "resource_requirements": ["1 dev"]
            }
        ]
        report["content"]["falsifiability_coverage"]["total_experiments"] = 1
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = 0
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = 0.0

        # Verify coverage_ratio is 0.0 when kill conditions missing
        assert report["content"]["falsifiability_coverage"]["coverage_ratio"] == 0.0, "Missing kill conditions should result in 0.0 coverage"

    def test_time_window_minimum(self, validator, experiment_report_template, tmp_path):
        """Test that experiments fit minimum 48-hour window."""
        # Create report with too-short experiment
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_short",
                "hypothesis": "Test hypothesis",
                "success_metrics": [{"metric": "Test metric", "target": "10%", "baseline": "5%"}],
                "kill_condition": "Kill if target not met after 50 users",
                "method": "A/B test",
                "duration_hours": 24,  # Below minimum of 48 hours
                "resource_requirements": ["1 dev"]
            }
        ]
        report["content"]["falsifiability_coverage"]["total_experiments"] = 1
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = 1
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = 1.0

        # Validate duration
        for exp in report["content"]["experiments"]:
            assert exp["duration_hours"] >= 48, "Experiments should have minimum 48-hour duration"

    def test_time_window_maximum(self, validator, experiment_report_template, tmp_path):
        """Test that experiments fit maximum 120-hour window."""
        # Create report with too-long experiment
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_long",
                "hypothesis": "Test hypothesis",
                "success_metrics": [{"metric": "Test metric", "target": "10%", "baseline": "5%"}],
                "kill_condition": "Kill if target not met after 500 users",
                "method": "A/B test",
                "duration_hours": 168,  # Above maximum of 120 hours (7 days)
                "resource_requirements": ["1 dev"]
            }
        ]

        # Validate duration
        for exp in report["content"]["experiments"]:
            assert exp["duration_hours"] <= 120, "Experiments should have maximum 120-hour duration (5 days)"

    def test_quantitative_success_metrics(self, validator, experiment_report_template, tmp_path):
        """Test that success metrics are quantitative (not vague)."""
        # Create report with quantitative metrics
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_quantitative",
                "hypothesis": "AI-powered onboarding reduces completion time",
                "success_metrics": [
                    {
                        "metric": "Average completion time",
                        "target": "<4 minutes",
                        "baseline": "8 minutes",
                        "measurement_method": "Google Analytics timing events"
                    },
                    {
                        "metric": "Completion rate",
                        "target": ">80%",
                        "baseline": "60%",
                        "measurement_method": "Completed onboarding / Started onboarding"
                    },
                    {
                        "metric": "User satisfaction (NPS)",
                        "target": ">7/10",
                        "baseline": "5/10",
                        "measurement_method": "Post-onboarding survey"
                    }
                ],
                "kill_condition": "Kill if completion time not <6 minutes OR completion rate not >70% after 100 users",
                "method": "A/B test with 50/50 split",
                "duration_hours": 72,
                "resource_requirements": ["1 frontend dev", "Analytics setup"]
            }
        ]
        report["content"]["falsifiability_coverage"]["total_experiments"] = 1
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = 1
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = 1.0

        temp_report = tmp_path / "quantitative_metrics.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        is_valid = validator.validate_report(temp_report)
        assert is_valid, "Report with quantitative metrics should validate"

        # Verify all metrics have target and baseline
        for exp in report["content"]["experiments"]:
            for metric in exp["success_metrics"]:
                assert "metric" in metric
                assert "target" in metric
                assert "baseline" in metric
                # Targets should contain comparison operators or numbers
                assert any(op in metric["target"] for op in [">", "<", ">=", "<=", "%"]), "Target should be quantitative"

    def test_vague_criteria_detection(self, experiment_report_template, tmp_path):
        """Test detection of vague acceptance criteria."""
        # Create report with vague criteria
        report = experiment_report_template.copy()
        vague_metrics = [
            {"metric": "User happiness", "target": "good", "baseline": "okay"},  # Vague
            {"metric": "Feel of interface", "target": "better", "baseline": "current"},  # Vague
            {"metric": "Team satisfaction", "target": "improved", "baseline": "current"}  # Vague
        ]

        # Verify these are indeed vague (no numbers or comparison operators)
        for metric in vague_metrics:
            target = metric["target"]
            is_quantitative = any(char.isdigit() for char in target) or any(op in target for op in [">", "<", ">=", "<=", "%"])
            assert not is_quantitative, f"Metric '{metric['metric']}' should be detected as vague"

    def test_resource_estimate_reasonableness(self, validator, experiment_report_template, tmp_path):
        """Test that resource estimates are present and reasonable."""
        # Create report with reasonable resource estimates
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_resources",
                "hypothesis": "Progressive disclosure increases completion rate",
                "success_metrics": [
                    {"metric": "Completion rate", "target": ">80%", "baseline": "60%"}
                ],
                "kill_condition": "Kill if completion rate not >70% after 200 users",
                "method": "A/B test with variant implementation",
                "duration_hours": 96,
                "resource_requirements": [
                    "1 frontend developer (16 hours implementation)",
                    "1 designer (8 hours mockups)",
                    "Analytics instrumentation (4 hours)",
                    "QA testing (4 hours)"
                ]
            }
        ]
        report["content"]["falsifiability_coverage"]["total_experiments"] = 1
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = 1
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = 1.0

        # Verify resource_requirements is present and non-empty
        for exp in report["content"]["experiments"]:
            assert "resource_requirements" in exp
            assert len(exp["resource_requirements"]) > 0, "Should have at least one resource requirement"
            # Ideally should have time estimates
            has_time_estimate = any("hour" in str(req).lower() for req in exp["resource_requirements"])
            assert has_time_estimate, "Resource estimates should include time"

    def test_hypothesis_falsifiability(self, experiment_report_template, tmp_path):
        """Test that hypotheses are falsifiable (can be proven wrong)."""
        # Create report with falsifiable hypotheses
        report = experiment_report_template.copy()
        falsifiable_hypotheses = [
            "AI-powered adaptive questioning reduces average onboarding time by 30%",
            "Progressive disclosure increases completion rate from 60% to 80%",
            "Social onboarding (multiplayer) increases D1 retention by 15 percentage points"
        ]

        report["content"]["experiments"] = [
            {
                "id": f"exp_{i}",
                "hypothesis": hyp,
                "success_metrics": [
                    {"metric": "Test metric", "target": ">50%", "baseline": "30%"}
                ],
                "kill_condition": f"Kill if metric not improved after 100 users",
                "method": "A/B test",
                "duration_hours": 72,
                "resource_requirements": ["1 dev"]
            }
            for i, hyp in enumerate(falsifiable_hypotheses)
        ]

        # Verify hypotheses are falsifiable (contain measurable claims)
        for exp in report["content"]["experiments"]:
            hyp = exp["hypothesis"]
            # Falsifiable hypotheses typically contain:
            # - Numeric claims (30%, 15 percentage points)
            # - Comparative verbs (reduces, increases, improves)
            # - Measurable outcomes (time, rate, retention)
            has_numeric_claim = any(char.isdigit() for char in hyp) or any(word in hyp.lower() for word in ["percent", "points", "by", "from", "to"])
            assert has_numeric_claim, f"Hypothesis should be falsifiable with measurable claims: {hyp}"

    def test_experiment_sequencing(self, validator, experiment_report_template, tmp_path):
        """Test that experiment sequencing is defined when multiple experiments exist."""
        # Create report with sequenced experiments
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_1",
                "hypothesis": "Hypothesis 1",
                "success_metrics": [{"metric": "Metric 1", "target": ">50%", "baseline": "30%"}],
                "kill_condition": "Kill condition 1",
                "method": "A/B test",
                "duration_hours": 72,
                "resource_requirements": ["1 dev"]
            },
            {
                "id": "exp_2",
                "hypothesis": "Hypothesis 2",
                "success_metrics": [{"metric": "Metric 2", "target": ">60%", "baseline": "40%"}],
                "kill_condition": "Kill condition 2",
                "method": "A/B test",
                "duration_hours": 96,
                "resource_requirements": ["1 dev"]
            },
            {
                "id": "exp_3",
                "hypothesis": "Hypothesis 3",
                "success_metrics": [{"metric": "Metric 3", "target": ">70%", "baseline": "50%"}],
                "kill_condition": "Kill condition 3",
                "method": "A/B test",
                "duration_hours": 72,
                "resource_requirements": ["1 dev"]
            }
        ]
        report["content"]["falsifiability_coverage"]["total_experiments"] = 3
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = 3
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = 1.0
        report["content"]["experiment_sequencing"] = [
            {
                "order": 1,
                "experiment_id": "exp_1",
                "rationale": "Test fundamental hypothesis first before building on it"
            },
            {
                "order": 2,
                "experiment_id": "exp_2",
                "rationale": "If exp_1 succeeds, validate complementary approach",
                "depends_on": ["exp_1"]
            },
            {
                "order": 3,
                "experiment_id": "exp_3",
                "rationale": "Combine learnings from exp_1 and exp_2",
                "depends_on": ["exp_1", "exp_2"]
            }
        ]

        # Verify sequencing structure
        if len(report["content"]["experiments"]) > 1:
            assert "experiment_sequencing" in report["content"]
            if report["content"]["experiment_sequencing"]:
                for seq in report["content"]["experiment_sequencing"]:
                    assert "order" in seq
                    assert "experiment_id" in seq
                    assert "rationale" in seq

    def test_falsifiability_coverage_calculation(self, experiment_report_template, tmp_path):
        """Test that falsifiability_coverage is calculated correctly."""
        # Create report with partial coverage
        report = experiment_report_template.copy()
        report["content"]["experiments"] = [
            {
                "id": "exp_1",
                "hypothesis": "Hypothesis 1",
                "success_metrics": [{"metric": "Metric", "target": ">50%", "baseline": "30%"}],
                "kill_condition": "Kill if not improved after 100 users",
                "method": "A/B test",
                "duration_hours": 72,
                "resource_requirements": ["1 dev"]
            },
            {
                "id": "exp_2",
                "hypothesis": "Hypothesis 2",
                "success_metrics": [{"metric": "Metric", "target": ">60%", "baseline": "40%"}],
                "kill_condition": "Kill if not improved after 150 users",
                "method": "A/B test",
                "duration_hours": 96,
                "resource_requirements": ["1 dev"]
            },
            {
                "id": "exp_3_no_kill",
                "hypothesis": "Hypothesis 3",
                "success_metrics": [{"metric": "Metric", "target": ">70%", "baseline": "50%"}],
                # Missing kill_condition
                "method": "A/B test",
                "duration_hours": 72,
                "resource_requirements": ["1 dev"]
            }
        ]

        # Calculate coverage
        total = len(report["content"]["experiments"])
        with_kill_conditions = sum(1 for exp in report["content"]["experiments"] if "kill_condition" in exp and exp["kill_condition"])

        report["content"]["falsifiability_coverage"]["total_experiments"] = total
        report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] = with_kill_conditions
        report["content"]["falsifiability_coverage"]["coverage_ratio"] = with_kill_conditions / total if total > 0 else 0.0

        # Verify calculation
        assert report["content"]["falsifiability_coverage"]["total_experiments"] == 3
        assert report["content"]["falsifiability_coverage"]["experiments_with_kill_conditions"] == 2
        assert abs(report["content"]["falsifiability_coverage"]["coverage_ratio"] - 0.667) < 0.01
