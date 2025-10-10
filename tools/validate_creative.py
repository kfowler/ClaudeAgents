#!/usr/bin/env python3
"""
Creative Output Validation Tool
Validates IDEATION_REPORT JSON outputs against schema definitions.

Usage:
    python tools/validate_creative.py path/to/report.json
    python tools/validate_creative.py path/to/report.json --verbose

Exit Codes:
    0 - Validation successful
    1 - Validation failed (schema errors, diversity thresholds, etc.)
    2 - File/system errors
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse

try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError, RefResolver
except ImportError:
    print("❌ Error: jsonschema library is not installed.", file=sys.stderr)
    print("Please install it by running:", file=sys.stderr)
    print("  pip install jsonschema", file=sys.stderr)
    sys.exit(2)


class CreativeValidator:
    """
    Validates IDEATION_REPORT outputs against JSON Schema and quality thresholds.

    Validates:
    - JSON Schema compliance (IDEATION_REPORT_v1.json)
    - Diversity thresholds (≥0.6 overall_diversity_score)
    - Novelty distribution balance
    - Required dimension population
    - Falsifiability for experiments (kill_condition required)
    """

    def __init__(self, schema_dir: Path = None, verbose: bool = False):
        """
        Initialize validator with schema directory.

        Args:
            schema_dir: Path to schemas/creative/ directory (default: auto-detect)
            verbose: Enable verbose output
        """
        self.verbose = verbose

        # Auto-detect schema directory if not provided
        if schema_dir is None:
            # Assume script is in tools/, schemas/ is sibling directory
            tool_dir = Path(__file__).parent
            repo_root = tool_dir.parent
            schema_dir = repo_root / "schemas" / "creative"

        self.schema_dir = Path(schema_dir)

        if not self.schema_dir.exists():
            raise FileNotFoundError(f"Schema directory not found: {self.schema_dir}")

        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_schema(self, schema_name: str) -> Dict:
        """Load JSON Schema from file."""
        schema_path = self.schema_dir / schema_name

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, 'r') as f:
            return json.load(f)

    def load_report(self, report_path: Path) -> Dict:
        """Load IDEATION_REPORT JSON from file."""
        if not report_path.exists():
            raise FileNotFoundError(f"Report not found: {report_path}")

        with open(report_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {report_path}: {e}")

    def validate_schema(self, report: Dict) -> bool:
        """
        Validate report against IDEATION_REPORT_v1.json schema.

        Returns:
            True if valid, False otherwise (errors stored in self.errors)
        """
        try:
            schema = self.load_schema("IDEATION_REPORT_v1.json")
            common_types = self.load_schema("common-types.json")

            # Create resolver for $ref to local files
            schema_store = {
                schema["$id"]: schema,
                common_types["$id"]: common_types
            }

            resolver = RefResolver.from_schema(schema, store=schema_store)

            # Validate with resolver
            validate(instance=report, schema=schema, resolver=resolver)

            if self.verbose:
                print("✓ Schema validation passed")

            return True

        except ValidationError as e:
            self.errors.append(f"Schema validation failed: {e.message}")
            if self.verbose:
                print(f"✗ Schema validation failed at path: {'.'.join(str(p) for p in e.path)}")
                print(f"  Error: {e.message}")
            return False

        except SchemaError as e:
            self.errors.append(f"Schema definition error: {e.message}")
            return False

    def validate_diversity_thresholds(self, report: Dict) -> bool:
        """
        Validate diversity thresholds for ideation reports.

        Requirements:
        - overall_diversity_score ≥ 0.6
        - All required dimensions populated (mechanism, experience, market)

        Returns:
            True if thresholds met, False otherwise
        """
        report_type = report.get("report_type")

        if report_type != "ideation":
            # Diversity thresholds only apply to ideation reports
            return True

        content = report.get("content", {})
        diversity_metrics = content.get("diversity_metrics", {})

        overall_diversity = diversity_metrics.get("overall_diversity_score")

        if overall_diversity is None:
            self.errors.append("Missing overall_diversity_score in diversity_metrics")
            return False

        # Check threshold
        MINIMUM_DIVERSITY = 0.6
        if overall_diversity < MINIMUM_DIVERSITY:
            self.errors.append(
                f"Diversity threshold not met: {overall_diversity:.2f} < {MINIMUM_DIVERSITY} (minimum)"
            )
            return False

        if self.verbose:
            print(f"✓ Diversity threshold met: {overall_diversity:.2f} ≥ {MINIMUM_DIVERSITY}")

        return True

    def validate_dimension_completeness(self, report: Dict) -> bool:
        """
        Validate that all ideas have required dimensions populated.

        Required dimensions: mechanism, experience, market

        Returns:
            True if all ideas have required dimensions, False otherwise
        """
        report_type = report.get("report_type")

        if report_type != "ideation":
            # Dimension completeness only applies to ideation reports
            return True

        content = report.get("content", {})
        ideas = content.get("ideas", [])

        required_dimensions = ["mechanism", "experience", "market"]
        incomplete_ideas = []

        for idea in ideas:
            idea_id = idea.get("id", "unknown")
            dimensions = idea.get("dimensions", {})

            missing_dims = [dim for dim in required_dimensions if not dimensions.get(dim)]

            if missing_dims:
                incomplete_ideas.append((idea_id, missing_dims))

        if incomplete_ideas:
            for idea_id, missing in incomplete_ideas:
                self.errors.append(
                    f"Idea '{idea_id}' missing required dimensions: {', '.join(missing)}"
                )
            return False

        if self.verbose:
            print(f"✓ All {len(ideas)} ideas have required dimensions (mechanism, experience, market)")

        return True

    def validate_falsifiability(self, report: Dict) -> bool:
        """
        Validate falsifiability for experiment_design reports.

        Requirements:
        - All experiments must have kill_condition defined
        - coverage_ratio should be 1.0

        Returns:
            True if falsifiable, False otherwise
        """
        report_type = report.get("report_type")

        if report_type != "experiment_design":
            # Falsifiability only applies to experiment reports
            return True

        content = report.get("content", {})
        experiments = content.get("experiments", [])
        falsifiability = content.get("falsifiability_coverage", {})

        coverage_ratio = falsifiability.get("coverage_ratio")

        if coverage_ratio is None:
            self.errors.append("Missing coverage_ratio in falsifiability_coverage")
            return False

        # Check that all experiments have kill conditions
        if coverage_ratio < 1.0:
            self.warnings.append(
                f"Falsifiability coverage incomplete: {coverage_ratio:.2f} < 1.0 "
                f"(some experiments lack kill_condition)"
            )

        # Validate each experiment has kill_condition
        missing_kill_conditions = []
        for exp in experiments:
            exp_id = exp.get("id", "unknown")
            if "kill_condition" not in exp:
                missing_kill_conditions.append(exp_id)

        if missing_kill_conditions:
            self.errors.append(
                f"Experiments missing kill_condition: {', '.join(missing_kill_conditions)}"
            )
            return False

        if self.verbose:
            print(f"✓ All {len(experiments)} experiments have kill_condition (falsifiable)")

        return True

    def validate_novelty_distribution(self, report: Dict) -> bool:
        """
        Validate that novelty distribution exists and is reasonable.

        Checks:
        - novelty_distribution present for ideation reports
        - Counts match number of ideas

        Returns:
            True if valid, False otherwise
        """
        report_type = report.get("report_type")

        if report_type != "ideation":
            return True

        content = report.get("content", {})
        ideas = content.get("ideas", [])
        novelty_dist = content.get("novelty_distribution", {})

        if not novelty_dist:
            self.warnings.append("Missing novelty_distribution for ideation report")
            return True  # Warning, not error

        # Verify counts match number of ideas
        conventional = novelty_dist.get("conventional", 0)
        moderate = novelty_dist.get("moderate", 0)
        breakthrough = novelty_dist.get("breakthrough", 0)

        total_categorized = conventional + moderate + breakthrough
        total_ideas = len(ideas)

        if total_categorized != total_ideas:
            self.warnings.append(
                f"Novelty distribution count mismatch: {total_categorized} categorized, "
                f"{total_ideas} ideas total"
            )

        if self.verbose:
            print(f"✓ Novelty distribution: {conventional} conventional, "
                  f"{moderate} moderate, {breakthrough} breakthrough")

        return True

    def validate_report(self, report_path: Path) -> bool:
        """
        Run all validations on an IDEATION_REPORT.

        Args:
            report_path: Path to JSON report file

        Returns:
            True if all validations passed, False otherwise
        """
        self.errors = []
        self.warnings = []

        try:
            report = self.load_report(report_path)
        except (FileNotFoundError, ValueError) as e:
            self.errors.append(str(e))
            return False

        # Run all validation checks
        validations = [
            self.validate_schema(report),
            self.validate_diversity_thresholds(report),
            self.validate_dimension_completeness(report),
            self.validate_falsifiability(report),
            self.validate_novelty_distribution(report),
        ]

        return all(validations)

    def print_report(self) -> None:
        """Print validation results summary."""
        if self.errors:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ Validation successful - all checks passed!")
        elif not self.errors:
            print("\n✅ Validation passed (with warnings)")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate IDEATION_REPORT JSON outputs against schema and quality thresholds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s output.json
  %(prog)s path/to/ideation_report.json --verbose
  %(prog)s creative_output.json -v

Exit codes:
  0 - Validation successful
  1 - Validation failed
  2 - File or system error
        """
    )

    parser.add_argument(
        "report_path",
        type=Path,
        help="Path to IDEATION_REPORT JSON file to validate"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--schema-dir",
        type=Path,
        help="Path to schemas/creative/ directory (default: auto-detect)"
    )

    args = parser.parse_args()

    try:
        validator = CreativeValidator(schema_dir=args.schema_dir, verbose=args.verbose)

        if args.verbose:
            print(f"Validating: {args.report_path}")
            print(f"Schema directory: {validator.schema_dir}\n")

        success = validator.validate_report(args.report_path)
        validator.print_report()

        sys.exit(0 if success else 1)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
