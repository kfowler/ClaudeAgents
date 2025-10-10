#!/usr/bin/env python3
"""
Test suite for creative triad end-to-end integration.

Tests:
- inventor → synthesist → architect pipeline
- Schema compatibility across handoffs
- Data preservation through pipeline
- Handoff rules respected
- Complete workflow validation
"""

import json
import pytest
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from validate_creative import CreativeValidator


class TestCreativeTriadIntegration:
    """Test suite for creative triad end-to-end integration."""

    @pytest.fixture
    def validator(self):
        """Fixture providing CreativeValidator instance."""
        return CreativeValidator(verbose=False)

    @pytest.fixture
    def inventor_output(self):
        """Fixture providing sample the-inventor output."""
        return {
            "agent_id": "the-inventor",
            "version": "v1.0",
            "timestamp": "2025-10-10T10:00:00Z",
            "report_type": "ideation",
            "content": {
                "ideas": [
                    {
                        "id": f"idea_{i}",
                        "description": f"Innovative onboarding idea {i} with detailed description meeting minimum length requirements.",
                        "novelty_score": 0.5 + (i * 0.05),
                        "dimensions": {
                            "mechanism": f"Mechanism_{i}",
                            "experience": f"Experience_{i % 5}",
                            "market": f"Market_{i % 4}"
                        }
                    }
                    for i in range(10)
                ],
                "diversity_metrics": {
                    "mechanism_diversity": 0.90,
                    "experience_diversity": 0.75,
                    "market_diversity": 0.70,
                    "overall_diversity_score": 0.78,
                    "unique_dimension_combinations": 10
                },
                "novelty_distribution": {
                    "conventional": 3,
                    "moderate": 4,
                    "breakthrough": 3
                }
            },
            "metadata": {
                "session_id": "integration-test-001",
                "context": "Reduce onboarding drop-off from 40% to <20%",
                "constraints": ["2 dev-months budget", "Q1 2026 launch"],
                "tags": ["onboarding", "integration-test"]
            }
        }

    @pytest.fixture
    def synthesist_output(self, inventor_output):
        """Fixture providing sample the-synthesist output derived from inventor."""
        return {
            "agent_id": "the-synthesist",
            "version": "v1.0",
            "timestamp": "2025-10-10T11:00:00Z",
            "report_type": "synthesis",
            "content": {
                "frames": [
                    {
                        "id": "frame_1",
                        "title": "Automation-Driven Approaches",
                        "description": "Leverage AI and automation to reduce manual configuration and personalize the experience.",
                        "contained_ideas": ["idea_0", "idea_1", "idea_2"],
                        "organizing_principle": "AI-powered automation",
                        "implementation_complexity": "high",
                        "false_tradeoffs_addressed": []
                    },
                    {
                        "id": "frame_2",
                        "title": "User-Controlled Approaches",
                        "description": "Give users explicit control through templates and customization options.",
                        "contained_ideas": ["idea_3", "idea_4", "idea_5"],
                        "organizing_principle": "User agency and control",
                        "implementation_complexity": "medium",
                        "false_tradeoffs_addressed": []
                    },
                    {
                        "id": "frame_3",
                        "title": "Friction-Reduction Approaches",
                        "description": "Minimize or eliminate upfront configuration burden.",
                        "contained_ideas": ["idea_6", "idea_7"],
                        "organizing_principle": "Minimal friction",
                        "implementation_complexity": "low",
                        "false_tradeoffs_addressed": []
                    },
                    {
                        "id": "frame_4",
                        "title": "Social Approaches",
                        "description": "Introduce collaborative and social elements.",
                        "contained_ideas": ["idea_8", "idea_9"],
                        "organizing_principle": "Social engagement",
                        "implementation_complexity": "high",
                        "false_tradeoffs_addressed": []
                    }
                ],
                "synthesis_rationale": "Ideas organize along the axis of user agency vs. automation, with orthogonal social dimension.",
                "cross_frame_synergies": []
            },
            "metadata": {
                "session_id": "integration-test-001",
                "context": inventor_output["metadata"]["context"],
                "input_idea_count": len(inventor_output["content"]["ideas"]),
                "constraints": inventor_output["metadata"]["constraints"],
                "tags": ["synthesis", "integration-test"]
            }
        }

    @pytest.fixture
    def architect_output(self, synthesist_output):
        """Fixture providing sample the-architect-of-experiments output."""
        return {
            "agent_id": "the-architect-of-experiments",
            "version": "v1.0",
            "timestamp": "2025-10-10T12:00:00Z",
            "report_type": "experiment_design",
            "content": {
                "experiments": [
                    {
                        "id": "exp_1",
                        "hypothesis": "AI-powered adaptive questioning (frame_1) reduces average onboarding time by 30%",
                        "success_metrics": [
                            {"metric": "Avg completion time", "target": "<5 min", "baseline": "8 min"}
                        ],
                        "kill_condition": "Kill if avg time not <6.5 min after 100 users",
                        "method": "A/B test with 50/50 split",
                        "duration_hours": 72,
                        "resource_requirements": ["1 frontend dev (20h)", "Analytics setup (4h)"]
                    },
                    {
                        "id": "exp_2",
                        "hypothesis": "Progressive disclosure (frame_3) increases completion rate from 60% to 80%",
                        "success_metrics": [
                            {"metric": "Completion rate", "target": ">75%", "baseline": "60%"}
                        ],
                        "kill_condition": "Kill if completion rate not >68% after 150 users",
                        "method": "A/B test with variant implementation",
                        "duration_hours": 96,
                        "resource_requirements": ["1 frontend dev (16h)", "1 designer (8h)"]
                    }
                ],
                "falsifiability_coverage": {
                    "total_experiments": 2,
                    "experiments_with_kill_conditions": 2,
                    "coverage_ratio": 1.0
                },
                "experiment_sequencing": [
                    {"order": 1, "experiment_id": "exp_1", "rationale": "Test highest-impact frame first"},
                    {"order": 2, "experiment_id": "exp_2", "rationale": "Validate complementary low-complexity approach"}
                ]
            },
            "metadata": {
                "session_id": "integration-test-001",
                "context": synthesist_output["metadata"]["context"],
                "input_frame_count": len(synthesist_output["content"]["frames"]),
                "constraints": synthesist_output["metadata"]["constraints"],
                "tags": ["experiment", "integration-test"]
            }
        }

    def test_inventor_to_synthesist_handoff(self, validator, inventor_output, synthesist_output, tmp_path):
        """Test that inventor output validates and can be used as synthesist input."""
        # Validate inventor output
        inventor_file = tmp_path / "inventor_output.json"
        with open(inventor_file, 'w') as f:
            json.dump(inventor_output, f, indent=2)

        is_valid = validator.validate_report(inventor_file)
        assert is_valid, "Inventor output should validate"

        # Verify synthesist can consume inventor output
        # Check that all inventor ideas are accounted for in synthesist frames
        inventor_ideas = {idea["id"] for idea in inventor_output["content"]["ideas"]}
        synthesist_ideas = set()
        for frame in synthesist_output["content"]["frames"]:
            synthesist_ideas.update(frame["contained_ideas"])

        assert inventor_ideas == synthesist_ideas, "All inventor ideas should be covered in synthesist frames"

    def test_synthesist_to_architect_handoff(self, validator, synthesist_output, architect_output, tmp_path):
        """Test that synthesist output validates and can be used as architect input."""
        # Validate synthesist output
        synthesist_file = tmp_path / "synthesist_output.json"
        with open(synthesist_file, 'w') as f:
            json.dump(synthesist_output, f, indent=2)

        is_valid = validator.validate_report(synthesist_file)
        assert is_valid, "Synthesist output should validate"

        # Verify architect references synthesist frames in experiments
        # Extract frame references from experiment hypotheses
        frame_ids_in_experiments = []
        for exp in architect_output["content"]["experiments"]:
            hypothesis = exp["hypothesis"]
            # Simple check: does hypothesis mention frame IDs?
            for frame in synthesist_output["content"]["frames"]:
                if frame["id"] in hypothesis:
                    frame_ids_in_experiments.append(frame["id"])

        assert len(frame_ids_in_experiments) > 0, "Experiments should reference synthesist frames"

    def test_complete_pipeline_schema_compatibility(self, validator, inventor_output, synthesist_output, architect_output, tmp_path):
        """Test that all three outputs validate against IDEATION_REPORT schema."""
        # Test inventor
        inventor_file = tmp_path / "inventor.json"
        with open(inventor_file, 'w') as f:
            json.dump(inventor_output, f, indent=2)
        assert validator.validate_report(inventor_file), "Inventor output should validate"

        # Test synthesist
        synthesist_file = tmp_path / "synthesist.json"
        with open(synthesist_file, 'w') as f:
            json.dump(synthesist_output, f, indent=2)
        assert validator.validate_report(synthesist_file), "Synthesist output should validate"

        # Test architect
        architect_file = tmp_path / "architect.json"
        with open(architect_file, 'w') as f:
            json.dump(architect_output, f, indent=2)
        assert validator.validate_report(architect_file), "Architect output should validate"

    def test_data_preservation_through_pipeline(self, inventor_output, synthesist_output, architect_output):
        """Test that context and constraints are preserved through pipeline."""
        # Verify session_id preserved
        assert inventor_output["metadata"]["session_id"] == synthesist_output["metadata"]["session_id"]
        assert synthesist_output["metadata"]["session_id"] == architect_output["metadata"]["session_id"]

        # Verify context preserved
        assert inventor_output["metadata"]["context"] == synthesist_output["metadata"]["context"]
        assert synthesist_output["metadata"]["context"] == architect_output["metadata"]["context"]

        # Verify constraints preserved
        assert inventor_output["metadata"]["constraints"] == synthesist_output["metadata"]["constraints"]
        assert synthesist_output["metadata"]["constraints"] == architect_output["metadata"]["constraints"]

    def test_handoff_rules_inventor_to_synthesist(self, inventor_output, synthesist_output):
        """Test that inventor→synthesist handoff follows documented rules."""
        # Per the-inventor handoff rules:
        # condition: ideas_ready_for_synthesis
        # action: delegate_to_the_synthesist
        # payload: full_IDEATION_REPORT

        # Verify synthesist received full idea payload
        assert "input_idea_count" in synthesist_output["metadata"]
        assert synthesist_output["metadata"]["input_idea_count"] == len(inventor_output["content"]["ideas"])

        # Verify all ideas accounted for
        inventor_ideas = {idea["id"] for idea in inventor_output["content"]["ideas"]}
        synthesist_ideas = set()
        for frame in synthesist_output["content"]["frames"]:
            synthesist_ideas.update(frame["contained_ideas"])

        assert inventor_ideas == synthesist_ideas, "Synthesist should account for all inventor ideas"

    def test_handoff_rules_synthesist_to_architect(self, synthesist_output, architect_output):
        """Test that synthesist→architect handoff follows documented rules."""
        # Per the-synthesist handoff rules:
        # condition: frames_ready_for_experimentation
        # action: delegate_to_the_architect_of_experiments
        # payload: full_IDEATION_REPORT_with_synthesis

        # Verify architect received frame information
        assert "input_frame_count" in architect_output["metadata"]
        assert architect_output["metadata"]["input_frame_count"] == len(synthesist_output["content"]["frames"])

        # Verify experiments reference frames
        frame_ids = {frame["id"] for frame in synthesist_output["content"]["frames"]}
        frame_references_in_experiments = False

        for exp in architect_output["content"]["experiments"]:
            # Check hypothesis or metadata for frame references
            if any(frame_id in exp["hypothesis"] for frame_id in frame_ids):
                frame_references_in_experiments = True
                break

        assert frame_references_in_experiments, "Experiments should reference synthesist frames"

    def test_complete_workflow_end_to_end(self, validator, inventor_output, synthesist_output, architect_output, tmp_path):
        """Test complete workflow from ideation → synthesis → experimentation."""
        # Step 1: Inventor generates ideas
        assert inventor_output["report_type"] == "ideation"
        assert len(inventor_output["content"]["ideas"]) >= 7
        assert inventor_output["content"]["diversity_metrics"]["overall_diversity_score"] >= 0.7

        # Step 2: Synthesist organizes into frames
        assert synthesist_output["report_type"] == "synthesis"
        assert 3 <= len(synthesist_output["content"]["frames"]) <= 5

        # Verify 100% coverage
        inventor_ideas = {idea["id"] for idea in inventor_output["content"]["ideas"]}
        synthesist_ideas = set()
        for frame in synthesist_output["content"]["frames"]:
            synthesist_ideas.update(frame["contained_ideas"])
        assert inventor_ideas == synthesist_ideas

        # Step 3: Architect designs experiments
        assert architect_output["report_type"] == "experiment_design"
        assert len(architect_output["content"]["experiments"]) >= 1
        assert architect_output["content"]["falsifiability_coverage"]["coverage_ratio"] == 1.0

        # Verify all experiments have kill conditions
        for exp in architect_output["content"]["experiments"]:
            assert "kill_condition" in exp
            assert len(exp["kill_condition"]) > 0

        # Step 4: Validate all outputs against schema
        for output, filename in [
            (inventor_output, "complete_inventor.json"),
            (synthesist_output, "complete_synthesist.json"),
            (architect_output, "complete_architect.json")
        ]:
            filepath = tmp_path / filename
            with open(filepath, 'w') as f:
                json.dump(output, f, indent=2)
            assert validator.validate_report(filepath), f"{filename} should validate"

    def test_pipeline_metadata_consistency(self, inventor_output, synthesist_output, architect_output):
        """Test that metadata remains consistent across pipeline stages."""
        # All agents should use v1.0 schema
        assert inventor_output["version"] == "v1.0"
        assert synthesist_output["version"] == "v1.0"
        assert architect_output["version"] == "v1.0"

        # Timestamps should be sequential
        inventor_time = inventor_output["timestamp"]
        synthesist_time = synthesist_output["timestamp"]
        architect_time = architect_output["timestamp"]

        assert inventor_time <= synthesist_time <= architect_time, "Timestamps should be sequential"

        # Tags should accumulate or maintain consistency
        inventor_tags = set(inventor_output["metadata"]["tags"])
        synthesist_tags = set(synthesist_output["metadata"]["tags"])
        architect_tags = set(architect_output["metadata"]["tags"])

        # All should share "integration-test" tag
        assert "integration-test" in inventor_tags
        assert "integration-test" in synthesist_tags
        assert "integration-test" in architect_tags
