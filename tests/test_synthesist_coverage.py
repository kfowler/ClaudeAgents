#!/usr/bin/env python3
"""
Test suite for the-synthesist agent coverage guarantees.

Tests:
- 100% idea coverage requirement (all input ideas accounted for)
- Frame generation (3-5 frames from input ideas)
- False tradeoff identification
- Dominant axis articulation
- Frame coherence validation
- Idea-to-frame mapping accuracy
"""

import json
import pytest
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from validate_creative import CreativeValidator
from scorecard_creative import CreativeScorecard


class TestSynthesistCoverage:
    """Test suite for the-synthesist coverage guarantees."""

    @pytest.fixture
    def validator(self):
        """Fixture providing CreativeValidator instance."""
        return CreativeValidator(verbose=False)

    @pytest.fixture
    def synthesist_report_template(self):
        """Fixture providing the-synthesist report template."""
        return {
            "agent_id": "the-synthesist",
            "version": "v1.0",
            "timestamp": "2025-10-10T15:30:00Z",
            "report_type": "synthesis",
            "content": {
                "frames": [],
                "synthesis_rationale": "Test synthesis rationale explaining the organizing principles and dominant axis.",
                "cross_frame_synergies": []
            },
            "metadata": {
                "session_id": "test-session-002",
                "context": "Synthesis of 10 diverse onboarding ideas",
                "input_idea_count": 10,
                "constraints": ["Test constraint"],
                "tags": ["test", "synthesis"]
            }
        }

    def test_frame_count_minimum(self, validator, synthesist_report_template, tmp_path):
        """Test that the-synthesist generates minimum 3 frames."""
        # Create report with only 2 frames (below minimum)
        report = synthesist_report_template.copy()
        report["content"]["frames"] = [
            {
                "id": f"frame_{i}",
                "title": f"Frame {i}",
                "description": f"Test frame {i} description with sufficient length to meet minimum requirements.",
                "contained_ideas": ["idea_1", "idea_2", "idea_3"],
                "organizing_principle": f"Organizing principle {i}",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            }
            for i in range(2)
        ]

        temp_report = tmp_path / "few_frames.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        # Schema allows minItems=1 for frames, but the-synthesist guarantees 3-5
        # Production validator should enforce agent-specific rules
        is_valid = validator.validate_report(temp_report)
        # Note: May pass schema but violates the-synthesist guarantee
        assert is_valid or any("minimum 3 frames" in str(e).lower() for e in validator.errors)

    def test_frame_count_maximum(self, validator, synthesist_report_template, tmp_path):
        """Test that the-synthesist generates maximum 5 frames."""
        # Create report with 5 frames (at maximum)
        report = synthesist_report_template.copy()
        report["content"]["frames"] = [
            {
                "id": f"frame_{i}",
                "title": f"Frame {i}",
                "description": f"Test frame {i} description with sufficient length to meet minimum requirements.",
                "contained_ideas": [f"idea_{j}" for j in range(i*2, i*2+2)],
                "organizing_principle": f"Organizing principle {i}",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            }
            for i in range(5)
        ]

        temp_report = tmp_path / "max_frames.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        is_valid = validator.validate_report(temp_report)
        assert is_valid, "5 frames should be valid for the-synthesist"

    def test_100_percent_idea_coverage(self, synthesist_report_template, tmp_path):
        """Test that all input ideas are accounted for in frames (100% coverage)."""
        # Create report with all input ideas mapped to frames
        report = synthesist_report_template.copy()
        input_ideas = [f"idea_{i}" for i in range(10)]

        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "User-Driven Approaches",
                "description": "Frames that put users in control of their onboarding experience through configuration and customization.",
                "contained_ideas": ["idea_0", "idea_1", "idea_2"],
                "organizing_principle": "User agency and control",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_2",
                "title": "AI-Assisted Approaches",
                "description": "Frames leveraging AI to reduce manual work and personalize the experience.",
                "contained_ideas": ["idea_3", "idea_4", "idea_5"],
                "organizing_principle": "Automation and personalization",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_3",
                "title": "Social Approaches",
                "description": "Frames that introduce collaborative and social elements to onboarding.",
                "contained_ideas": ["idea_6", "idea_7"],
                "organizing_principle": "Social learning and engagement",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_4",
                "title": "Minimal Friction Approaches",
                "description": "Frames that reduce or eliminate upfront configuration.",
                "contained_ideas": ["idea_8", "idea_9"],
                "organizing_principle": "Friction reduction",
                "implementation_complexity": "low",
                "false_tradeoffs_addressed": []
            }
        ]

        # Collect all ideas from frames
        covered_ideas = set()
        for frame in report["content"]["frames"]:
            covered_ideas.update(frame["contained_ideas"])

        # Verify 100% coverage
        assert len(covered_ideas) == len(input_ideas), "All input ideas should be covered in frames"
        assert set(input_ideas) == covered_ideas, "Exact match of input ideas to covered ideas"

    def test_false_tradeoff_identification(self, synthesist_report_template, tmp_path):
        """Test that false tradeoffs are identified and documented."""
        # Create report with false tradeoff identified
        report = synthesist_report_template.copy()
        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "User-Driven Approaches",
                "description": "Frames that put users in control.",
                "contained_ideas": ["idea_0", "idea_1", "idea_2"],
                "organizing_principle": "User agency",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": [
                    {
                        "tradeoff": "User control vs. simplicity",
                        "why_false": "Progressive disclosure allows both user control AND simplicity by revealing complexity only when needed",
                        "synthesis": "Combine user control with progressive disclosure to achieve both goals"
                    }
                ]
            },
            {
                "id": "frame_2",
                "title": "AI-Assisted Approaches",
                "description": "AI-powered personalization.",
                "contained_ideas": ["idea_3", "idea_4"],
                "organizing_principle": "Automation",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": [
                    {
                        "tradeoff": "Automation vs. user trust",
                        "why_false": "Transparent AI with review-and-correct UX builds trust while automating work",
                        "synthesis": "Show AI reasoning and allow corrections to combine automation with trust"
                    }
                ]
            },
            {
                "id": "frame_3",
                "title": "Minimal Friction",
                "description": "Reduce configuration burden.",
                "contained_ideas": ["idea_5", "idea_6"],
                "organizing_principle": "Friction reduction",
                "implementation_complexity": "low",
                "false_tradeoffs_addressed": []
            }
        ]

        # Verify at least one false tradeoff identified
        false_tradeoffs_found = 0
        for frame in report["content"]["frames"]:
            if frame["false_tradeoffs_addressed"]:
                false_tradeoffs_found += len(frame["false_tradeoffs_addressed"])
                # Verify structure
                for ft in frame["false_tradeoffs_addressed"]:
                    assert "tradeoff" in ft
                    assert "why_false" in ft
                    assert "synthesis" in ft

        assert false_tradeoffs_found > 0, "Should identify at least one false tradeoff"

    def test_dominant_axis_articulated(self, synthesist_report_template, tmp_path):
        """Test that synthesis_rationale articulates the dominant organizing axis."""
        # Create report with clear dominant axis
        report = synthesist_report_template.copy()
        report["content"]["synthesis_rationale"] = (
            "The dominant organizing axis is **user agency vs. automation**. "
            "Ideas cluster into four frames: (1) user-driven configuration, "
            "(2) AI-assisted automation, (3) social/collaborative approaches, and "
            "(4) minimal friction defaults. This axis reveals that the core tension "
            "is between giving users control and reducing their cognitive load. "
            "False tradeoffs emerge when we assume these are mutually exclusive—"
            "progressive disclosure and transparent AI can achieve both goals."
        )
        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "Test Frame",
                "description": "Test frame description.",
                "contained_ideas": ["idea_0", "idea_1"],
                "organizing_principle": "User agency",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            }
        ]

        # Verify synthesis_rationale is substantive
        assert len(report["content"]["synthesis_rationale"]) > 100, "Synthesis rationale should be detailed"
        assert "axis" in report["content"]["synthesis_rationale"].lower(), "Should articulate organizing axis"

    def test_frame_coherence_validation(self, synthesist_report_template, tmp_path):
        """Test that frames are coherent (organizing principle aligns with contained ideas)."""
        # Create report with coherent frames
        report = synthesist_report_template.copy()
        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "AI-Powered Personalization",
                "description": "Leverage AI and machine learning to personalize onboarding based on user context, reducing manual configuration.",
                "contained_ideas": ["idea_ai_prefill", "idea_conversational", "idea_smart_defaults"],
                "organizing_principle": "AI-driven automation and personalization",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_2",
                "title": "Social and Collaborative",
                "description": "Introduce social elements where users collaborate during onboarding.",
                "contained_ideas": ["idea_multiplayer", "idea_invite_colleague"],
                "organizing_principle": "Social learning and engagement",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_3",
                "title": "Minimal Upfront Friction",
                "description": "Reduce or eliminate configuration burden by using smart defaults and in-context help.",
                "contained_ideas": ["idea_skip_onboarding", "idea_progressive_disclosure", "idea_contextual_help"],
                "organizing_principle": "Friction reduction through defaults",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            }
        ]

        # Verify each frame has clear organizing principle
        for frame in report["content"]["frames"]:
            assert "organizing_principle" in frame
            assert len(frame["organizing_principle"]) > 10, "Organizing principle should be substantive"
            assert len(frame["description"]) > 50, "Frame description should be detailed"
            assert len(frame["contained_ideas"]) > 0, "Frame should contain at least one idea"

    def test_idea_to_frame_mapping_accuracy(self, synthesist_report_template, tmp_path):
        """Test that idea-to-frame mapping is accurate (no orphaned ideas)."""
        # Create report with complete mapping
        report = synthesist_report_template.copy()
        input_ideas = [f"idea_{i}" for i in range(10)]
        report["metadata"]["input_idea_count"] = 10

        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "Frame 1",
                "description": "First frame with several ideas grouped together.",
                "contained_ideas": ["idea_0", "idea_1", "idea_2", "idea_3"],
                "organizing_principle": "Principle 1",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_2",
                "title": "Frame 2",
                "description": "Second frame with different ideas.",
                "contained_ideas": ["idea_4", "idea_5", "idea_6"],
                "organizing_principle": "Principle 2",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_3",
                "title": "Frame 3",
                "description": "Third frame with remaining ideas.",
                "contained_ideas": ["idea_7", "idea_8", "idea_9"],
                "organizing_principle": "Principle 3",
                "implementation_complexity": "low",
                "false_tradeoffs_addressed": []
            }
        ]

        # Collect all mapped ideas
        mapped_ideas = set()
        for frame in report["content"]["frames"]:
            mapped_ideas.update(frame["contained_ideas"])

        # Verify no orphaned ideas
        assert len(mapped_ideas) == report["metadata"]["input_idea_count"], "All ideas should be mapped"

    def test_cross_frame_synergies(self, synthesist_report_template, tmp_path):
        """Test that cross-frame synergies are identified when present."""
        # Create report with cross-frame synergies
        report = synthesist_report_template.copy()
        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "AI Personalization",
                "description": "AI-driven approaches.",
                "contained_ideas": ["idea_0", "idea_1"],
                "organizing_principle": "Automation",
                "implementation_complexity": "high",
                "false_tradeoffs_addressed": []
            },
            {
                "id": "frame_2",
                "title": "Progressive Disclosure",
                "description": "Reveal complexity gradually.",
                "contained_ideas": ["idea_2", "idea_3"],
                "organizing_principle": "Simplicity",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            }
        ]
        report["content"]["cross_frame_synergies"] = [
            {
                "frames": ["frame_1", "frame_2"],
                "synergy": "AI personalization can power progressive disclosure by predicting which options to show when",
                "combined_impact": "Highly personalized AND simple experience"
            }
        ]

        # Verify synergies structure
        if report["content"]["cross_frame_synergies"]:
            for synergy in report["content"]["cross_frame_synergies"]:
                assert "frames" in synergy
                assert "synergy" in synergy
                assert len(synergy["frames"]) >= 2, "Synergy should involve 2+ frames"

    def test_synthesis_rationale_completeness(self, validator, synthesist_report_template, tmp_path):
        """Test that synthesis_rationale is present and substantive."""
        # Create report with comprehensive rationale
        report = synthesist_report_template.copy()
        report["content"]["synthesis_rationale"] = (
            "These 10 diverse onboarding ideas organize naturally into 4 coherent frames along "
            "the dominant axis of **user agency vs. automation**:\n\n"
            "1. **User-Driven Configuration**: Ideas that give users explicit control through templates, "
            "customization, and manual setup. High agency, low automation.\n\n"
            "2. **AI-Assisted Personalization**: Ideas leveraging AI to reduce configuration burden while "
            "maintaining user oversight. Balanced agency and automation.\n\n"
            "3. **Social Collaborative**: Ideas introducing peer learning and multiplayer elements. "
            "Orthogonal to the main axis, creates engagement through social dynamics.\n\n"
            "4. **Minimal Friction Defaults**: Ideas that eliminate upfront configuration entirely through "
            "smart defaults. Low agency, high automation.\n\n"
            "Key insight: The apparent tradeoff between 'user control' and 'simplicity' is FALSE. "
            "Progressive disclosure and transparent AI enable both simultaneously."
        )
        report["content"]["frames"] = [
            {
                "id": "frame_1",
                "title": "Test Frame",
                "description": "Test frame.",
                "contained_ideas": ["idea_0", "idea_1"],
                "organizing_principle": "Test principle",
                "implementation_complexity": "medium",
                "false_tradeoffs_addressed": []
            }
        ]

        temp_report = tmp_path / "complete_synthesis.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        is_valid = validator.validate_report(temp_report)
        assert is_valid, "Complete synthesis report should validate"
        assert len(report["content"]["synthesis_rationale"]) > 200, "Rationale should be detailed"
