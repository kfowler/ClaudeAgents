#!/usr/bin/env python3
"""
Test suite for creative output validation and scoring.

Tests:
- JSON schema validation for IDEATION_REPORTs
- Diversity threshold enforcement
- Novelty distribution calculation
- Falsifiability coverage (for experiment reports)
- Scorecard metric calculations
- Golden template validation
"""

import json
import pytest
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from validate_creative import CreativeValidator
from scorecard_creative import CreativeScorecard


class TestCreativeValidator:
    """Test suite for creative output validation."""

    @pytest.fixture
    def validator(self):
        """Fixture providing CreativeValidator instance."""
        return CreativeValidator(verbose=False)

    @pytest.fixture
    def golden_report_path(self):
        """Fixture providing path to golden creative-catalyst template."""
        return Path(__file__).parent / "seed_templates" / "creative-catalyst.golden.json"

    @pytest.fixture
    def golden_report(self, golden_report_path):
        """Fixture providing parsed golden report."""
        with open(golden_report_path, 'r') as f:
            golden = json.load(f)
        return golden["expected_output"]

    def test_validator_initializes(self, validator):
        """Test that validator initializes correctly."""
        assert validator is not None
        assert validator.schema_dir.exists()
        assert (validator.schema_dir / "IDEATION_REPORT_v1.json").exists()
        assert (validator.schema_dir / "common-types.json").exists()

    def test_golden_template_exists(self, golden_report_path):
        """Test that golden template exists and is valid JSON."""
        assert golden_report_path.exists()

        with open(golden_report_path, 'r') as f:
            golden = json.load(f)

        assert golden["agent"] == "creative-catalyst"
        assert "expected_output" in golden
        assert golden["expected_output"]["report_type"] == "ideation"

    def test_golden_report_validates(self, validator, golden_report, tmp_path):
        """Test that golden report passes validation."""
        # Write golden report to temp file
        temp_report = tmp_path / "test_report.json"
        with open(temp_report, 'w') as f:
            json.dump(golden_report, f, indent=2)

        # Validate
        is_valid = validator.validate_report(temp_report)

        # Print errors if validation failed
        if not is_valid:
            print("\nValidation errors:")
            for error in validator.errors:
                print(f"  - {error}")
            print("\nValidation warnings:")
            for warning in validator.warnings:
                print(f"  - {warning}")

        assert is_valid, "Golden report should pass validation"

    def test_diversity_threshold_enforcement(self, validator, golden_report, tmp_path):
        """Test that diversity threshold validation works correctly."""
        # Create report with low diversity
        low_diversity_report = golden_report.copy()
        low_diversity_report["content"]["diversity_metrics"]["overall_diversity_score"] = 0.45

        temp_report = tmp_path / "low_diversity.json"
        with open(temp_report, 'w') as f:
            json.dump(low_diversity_report, f, indent=2)

        # Should fail validation
        is_valid = validator.validate_report(temp_report)
        assert not is_valid
        assert any("diversity threshold" in error.lower() for error in validator.errors)

    def test_dimension_completeness_check(self, validator, golden_report, tmp_path):
        """Test that dimension completeness validation works."""
        # Create report with missing dimension
        incomplete_report = golden_report.copy()
        incomplete_report["content"]["ideas"][0]["dimensions"].pop("mechanism")

        temp_report = tmp_path / "incomplete_dims.json"
        with open(temp_report, 'w') as f:
            json.dump(incomplete_report, f, indent=2)

        # Should fail validation
        is_valid = validator.validate_report(temp_report)
        assert not is_valid
        assert any("missing required dimensions" in error.lower() for error in validator.errors)

    def test_invalid_json_handling(self, validator, tmp_path):
        """Test that validator handles invalid JSON gracefully."""
        invalid_json = tmp_path / "invalid.json"
        with open(invalid_json, 'w') as f:
            f.write("{ invalid json content")

        is_valid = validator.validate_report(invalid_json)
        assert not is_valid
        assert any("invalid json" in error.lower() for error in validator.errors)

    def test_missing_file_handling(self, validator):
        """Test that validator handles missing files gracefully."""
        nonexistent = Path("/tmp/nonexistent_creative_report.json")
        is_valid = validator.validate_report(nonexistent)
        assert not is_valid
        assert any("not found" in error.lower() for error in validator.errors)


class TestCreativeScorecard:
    """Test suite for creative output scoring."""

    @pytest.fixture
    def golden_report_path(self):
        """Fixture providing path to golden creative-catalyst template."""
        return Path(__file__).parent / "seed_templates" / "creative-catalyst.golden.json"

    @pytest.fixture
    def golden_report(self, golden_report_path, tmp_path):
        """Fixture providing golden report as temp file."""
        with open(golden_report_path, 'r') as f:
            golden = json.load(f)

        report = golden["expected_output"]

        # Write to temp file
        temp_report = tmp_path / "golden_report.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        return temp_report

    def test_scorecard_initializes(self, golden_report):
        """Test that scorecard initializes correctly."""
        scorecard = CreativeScorecard(golden_report)
        assert scorecard is not None
        assert scorecard.report is not None

    def test_diversity_score_calculation(self, golden_report):
        """Test diversity score calculation for ideation reports."""
        scorecard = CreativeScorecard(golden_report)
        diversity = scorecard.calculate_diversity_score()

        assert "overall_diversity_score" in diversity
        assert diversity["overall_diversity_score"] >= 0.0
        assert diversity["overall_diversity_score"] <= 1.0

        assert "mechanism_diversity" in diversity
        assert "experience_diversity" in diversity
        assert "market_diversity" in diversity

    def test_novelty_distribution_calculation(self, golden_report):
        """Test novelty distribution calculation."""
        scorecard = CreativeScorecard(golden_report)
        novelty = scorecard.calculate_novelty_distribution()

        assert "conventional_count" in novelty
        assert "moderate_count" in novelty
        assert "breakthrough_count" in novelty
        assert "average_novelty" in novelty

        # Total should match number of ideas
        total_categorized = (
            novelty["conventional_count"] +
            novelty["moderate_count"] +
            novelty["breakthrough_count"]
        )
        assert total_categorized == novelty["total_ideas"]

    def test_quality_grade_calculation(self, golden_report):
        """Test quality grade calculation."""
        scorecard = CreativeScorecard(golden_report)
        scorecard.metrics["diversity"] = scorecard.calculate_diversity_score()
        scorecard.metrics["novelty_distribution"] = scorecard.calculate_novelty_distribution()

        grade = scorecard.calculate_quality_grade()
        assert grade in ["A", "B", "C", "D", "F", "N/A"]

        # Golden report should get high grade
        assert grade in ["A", "B"], f"Golden report should get A or B grade, got {grade}"

    def test_full_scorecard_generation(self, golden_report):
        """Test complete scorecard generation."""
        scorecard = CreativeScorecard(golden_report)
        full_scorecard = scorecard.generate_scorecard()

        assert "report_info" in full_scorecard
        assert "diversity" in full_scorecard
        assert "novelty_distribution" in full_scorecard
        assert "quality_grade" in full_scorecard

        # Check report info
        assert full_scorecard["report_info"]["agent_id"] == "creative-catalyst"
        assert full_scorecard["report_info"]["report_type"] == "ideation"

    def test_human_readable_formatting(self, golden_report):
        """Test human-readable scorecard formatting."""
        scorecard = CreativeScorecard(golden_report)
        full_scorecard = scorecard.generate_scorecard()

        human_output = scorecard.format_human_readable(full_scorecard)

        assert "CREATIVE OUTPUT SCORECARD" in human_output
        assert "Quality Grade:" in human_output
        assert "DIVERSITY METRICS" in human_output
        assert "NOVELTY DISTRIBUTION" in human_output

    def test_scorecard_handles_missing_file(self):
        """Test scorecard handles missing files gracefully."""
        nonexistent = Path("/tmp/nonexistent_report.json")

        with pytest.raises(FileNotFoundError):
            CreativeScorecard(nonexistent)


class TestIntegration:
    """Integration tests for validation + scoring workflow."""

    @pytest.fixture
    def golden_report_path(self):
        """Fixture providing path to golden creative-catalyst template."""
        return Path(__file__).parent / "seed_templates" / "creative-catalyst.golden.json"

    def test_golden_report_validation_and_scoring(self, golden_report_path, tmp_path):
        """Test complete workflow: validate then score golden report."""
        # Load golden report
        with open(golden_report_path, 'r') as f:
            golden = json.load(f)

        report = golden["expected_output"]

        # Write to temp file
        temp_report = tmp_path / "test_report.json"
        with open(temp_report, 'w') as f:
            json.dump(report, f, indent=2)

        # Step 1: Validate
        validator = CreativeValidator(verbose=False)
        is_valid = validator.validate_report(temp_report)

        if not is_valid:
            print("\nValidation errors:")
            for error in validator.errors:
                print(f"  - {error}")

        assert is_valid, "Golden report should validate"

        # Step 2: Score
        scorecard_tool = CreativeScorecard(temp_report)
        scorecard = scorecard_tool.generate_scorecard()

        assert scorecard["quality_grade"] in ["A", "B"]
        assert scorecard["diversity"]["overall_diversity_score"] >= 0.6
        assert scorecard["novelty_distribution"]["total_ideas"] >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
