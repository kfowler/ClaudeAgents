#!/usr/bin/env python3
"""
Creative Output Scorecard Tool
Calculates quality metrics for IDEATION_REPORT outputs.

Metrics:
- Diversity score (0.0-1.0) across dimensions
- Novelty distribution (conventional/moderate/breakthrough)
- Falsifiability coverage (for experiment reports)
- Quality assessment summary

Usage:
    python tools/scorecard_creative.py path/to/report.json
    python tools/scorecard_creative.py path/to/report.json --format json
    python tools/scorecard_creative.py path/to/report.json --format human

Exit Codes:
    0 - Scorecard generated successfully
    1 - Error processing report
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse
from collections import Counter


class CreativeScorecard:
    """
    Calculate quality metrics for IDEATION_REPORT outputs.

    Metrics:
    - Diversity scores per dimension and overall
    - Novelty distribution across spectrum
    - Falsifiability coverage (experiments)
    - Quality grade (A-F based on thresholds)
    """

    def __init__(self, report_path: Path):
        """
        Initialize scorecard with report path.

        Args:
            report_path: Path to IDEATION_REPORT JSON file
        """
        self.report_path = report_path
        self.report = self._load_report()
        self.metrics: Dict[str, Any] = {}

    def _load_report(self) -> Dict:
        """Load and parse IDEATION_REPORT JSON."""
        if not self.report_path.exists():
            raise FileNotFoundError(f"Report not found: {self.report_path}")

        with open(self.report_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {self.report_path}: {e}")

    def calculate_diversity_score(self) -> Dict[str, float]:
        """
        Calculate diversity scores for ideation reports.

        Returns dict with:
        - mechanism_diversity
        - experience_diversity
        - market_diversity
        - data_approach_diversity (if present)
        - overall_diversity_score
        - unique_dimension_combinations

        Diversity = (unique_values / total_ideas) for each dimension
        """
        report_type = self.report.get("report_type")

        if report_type != "ideation":
            return {"note": "Diversity scores only apply to ideation reports"}

        content = self.report.get("content", {})
        ideas = content.get("ideas", [])

        if not ideas:
            return {"error": "No ideas found in report"}

        # Extract dimensions from all ideas
        mechanisms = []
        experiences = []
        markets = []
        data_approaches = []
        dimension_combos = []

        for idea in ideas:
            dims = idea.get("dimensions", {})
            mechanisms.append(dims.get("mechanism", ""))
            experiences.append(dims.get("experience", ""))
            markets.append(dims.get("market", ""))

            if "data_approach" in dims:
                data_approaches.append(dims.get("data_approach"))

            # Track unique dimension combinations
            combo = f"{dims.get('mechanism')}|{dims.get('experience')}|{dims.get('market')}"
            dimension_combos.append(combo)

        total_ideas = len(ideas)

        # Calculate diversity scores (unique / total)
        diversity = {
            "mechanism_diversity": len(set(mechanisms)) / total_ideas if total_ideas > 0 else 0.0,
            "experience_diversity": len(set(experiences)) / total_ideas if total_ideas > 0 else 0.0,
            "market_diversity": len(set(markets)) / total_ideas if total_ideas > 0 else 0.0,
            "unique_dimension_combinations": len(set(dimension_combos)),
        }

        if data_approaches:
            diversity["data_approach_diversity"] = len(set(data_approaches)) / len(data_approaches)

        # Calculate overall diversity (average of dimension diversities)
        dimension_scores = [
            diversity["mechanism_diversity"],
            diversity["experience_diversity"],
            diversity["market_diversity"]
        ]

        if data_approaches:
            dimension_scores.append(diversity["data_approach_diversity"])

        diversity["overall_diversity_score"] = sum(dimension_scores) / len(dimension_scores)

        return diversity

    def calculate_novelty_distribution(self) -> Dict[str, Any]:
        """
        Calculate novelty distribution for ideation reports.

        Returns dict with:
        - conventional_count (novelty 0.0-0.4)
        - moderate_count (novelty 0.4-0.7)
        - breakthrough_count (novelty 0.7-1.0)
        - average_novelty
        - novelty_range (min, max)
        """
        report_type = self.report.get("report_type")

        if report_type != "ideation":
            return {"note": "Novelty distribution only applies to ideation reports"}

        content = self.report.get("content", {})
        ideas = content.get("ideas", [])

        if not ideas:
            return {"error": "No ideas found in report"}

        novelty_scores = [idea.get("novelty_score", 0.0) for idea in ideas]

        # Categorize by novelty ranges
        conventional = sum(1 for score in novelty_scores if 0.0 <= score < 0.4)
        moderate = sum(1 for score in novelty_scores if 0.4 <= score < 0.7)
        breakthrough = sum(1 for score in novelty_scores if 0.7 <= score <= 1.0)

        distribution = {
            "conventional_count": conventional,
            "moderate_count": moderate,
            "breakthrough_count": breakthrough,
            "total_ideas": len(ideas),
            "average_novelty": sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0,
            "novelty_range": {
                "min": min(novelty_scores) if novelty_scores else 0.0,
                "max": max(novelty_scores) if novelty_scores else 0.0
            }
        }

        # Calculate percentages
        total = len(ideas)
        distribution["conventional_pct"] = (conventional / total * 100) if total > 0 else 0.0
        distribution["moderate_pct"] = (moderate / total * 100) if total > 0 else 0.0
        distribution["breakthrough_pct"] = (breakthrough / total * 100) if total > 0 else 0.0

        return distribution

    def calculate_falsifiability_coverage(self) -> Dict[str, Any]:
        """
        Calculate falsifiability coverage for experiment_design reports.

        Returns dict with:
        - experiments_with_kill_conditions
        - total_experiments
        - coverage_ratio (0.0-1.0)
        - experiments_missing_kill_conditions (list of IDs)
        """
        report_type = self.report.get("report_type")

        if report_type != "experiment_design":
            return {"note": "Falsifiability coverage only applies to experiment_design reports"}

        content = self.report.get("content", {})
        experiments = content.get("experiments", [])

        if not experiments:
            return {"error": "No experiments found in report"}

        missing_kill_conditions = []
        experiments_with_kill = 0

        for exp in experiments:
            exp_id = exp.get("id", "unknown")
            if "kill_condition" in exp:
                experiments_with_kill += 1
            else:
                missing_kill_conditions.append(exp_id)

        total = len(experiments)
        coverage_ratio = experiments_with_kill / total if total > 0 else 0.0

        return {
            "experiments_with_kill_conditions": experiments_with_kill,
            "total_experiments": total,
            "coverage_ratio": coverage_ratio,
            "experiments_missing_kill_conditions": missing_kill_conditions,
            "coverage_pct": coverage_ratio * 100
        }

    def calculate_quality_grade(self) -> str:
        """
        Calculate overall quality grade (A-F) based on metrics.

        Grading criteria:
        - A: diversity ≥0.75, balanced novelty, complete falsifiability
        - B: diversity ≥0.65, decent novelty spread
        - C: diversity ≥0.60, some novelty variation
        - D: diversity ≥0.50, minimal variation
        - F: diversity <0.50, homogenous output

        Returns:
            Grade (A, B, C, D, or F)
        """
        report_type = self.report.get("report_type")

        if report_type == "ideation":
            diversity = self.metrics.get("diversity", {})
            novelty = self.metrics.get("novelty_distribution", {})

            overall_diversity = diversity.get("overall_diversity_score", 0.0)
            breakthrough_pct = novelty.get("breakthrough_pct", 0.0)

            # Grade based on diversity and novelty balance
            if overall_diversity >= 0.75 and breakthrough_pct >= 20:
                return "A"
            elif overall_diversity >= 0.65 and breakthrough_pct >= 10:
                return "B"
            elif overall_diversity >= 0.60:
                return "C"
            elif overall_diversity >= 0.50:
                return "D"
            else:
                return "F"

        elif report_type == "experiment_design":
            falsifiability = self.metrics.get("falsifiability", {})
            coverage_ratio = falsifiability.get("coverage_ratio", 0.0)

            # Grade based on falsifiability coverage
            if coverage_ratio >= 0.95:
                return "A"
            elif coverage_ratio >= 0.80:
                return "B"
            elif coverage_ratio >= 0.60:
                return "C"
            elif coverage_ratio >= 0.40:
                return "D"
            else:
                return "F"

        elif report_type == "synthesis":
            # For synthesis reports, grade on frame count and coherence
            content = self.report.get("content", {})
            frames = content.get("frames", [])

            if len(frames) >= 3:
                return "A"
            elif len(frames) >= 2:
                return "B"
            else:
                return "C"

        return "N/A"

    def generate_scorecard(self) -> Dict[str, Any]:
        """
        Generate complete scorecard with all metrics.

        Returns:
            Dict with all calculated metrics and quality grade
        """
        report_type = self.report.get("report_type")
        agent_id = self.report.get("agent_id")
        timestamp = self.report.get("timestamp")

        scorecard = {
            "report_info": {
                "agent_id": agent_id,
                "report_type": report_type,
                "timestamp": timestamp,
                "source_file": str(self.report_path)
            }
        }

        # Calculate type-specific metrics
        if report_type == "ideation":
            self.metrics["diversity"] = self.calculate_diversity_score()
            self.metrics["novelty_distribution"] = self.calculate_novelty_distribution()

            scorecard["diversity"] = self.metrics["diversity"]
            scorecard["novelty_distribution"] = self.metrics["novelty_distribution"]

        elif report_type == "experiment_design":
            self.metrics["falsifiability"] = self.calculate_falsifiability_coverage()
            scorecard["falsifiability"] = self.metrics["falsifiability"]

        elif report_type == "synthesis":
            content = self.report.get("content", {})
            frames = content.get("frames", [])

            scorecard["synthesis_metrics"] = {
                "frame_count": len(frames),
                "total_ideas_synthesized": sum(len(f.get("idea_ids", [])) for f in frames)
            }

        # Calculate quality grade
        scorecard["quality_grade"] = self.calculate_quality_grade()

        return scorecard

    def format_human_readable(self, scorecard: Dict) -> str:
        """
        Format scorecard as human-readable text.

        Args:
            scorecard: Scorecard dict from generate_scorecard()

        Returns:
            Formatted text summary
        """
        lines = []
        lines.append("=" * 60)
        lines.append("CREATIVE OUTPUT SCORECARD")
        lines.append("=" * 60)

        # Report info
        info = scorecard["report_info"]
        lines.append(f"\nAgent: {info['agent_id']}")
        lines.append(f"Report Type: {info['report_type']}")
        lines.append(f"Timestamp: {info['timestamp']}")
        lines.append(f"Source: {info['source_file']}")

        # Quality grade
        grade = scorecard["quality_grade"]
        lines.append(f"\n{'Quality Grade:':<25} {grade}")

        # Type-specific metrics
        if "diversity" in scorecard:
            div = scorecard["diversity"]
            lines.append(f"\n{'DIVERSITY METRICS':-^60}")
            lines.append(f"{'Overall Diversity:':<25} {div['overall_diversity_score']:.2f}")
            lines.append(f"{'  - Mechanism:':<25} {div['mechanism_diversity']:.2f}")
            lines.append(f"{'  - Experience:':<25} {div['experience_diversity']:.2f}")
            lines.append(f"{'  - Market:':<25} {div['market_diversity']:.2f}")

            if "data_approach_diversity" in div:
                lines.append(f"{'  - Data Approach:':<25} {div['data_approach_diversity']:.2f}")

            lines.append(f"{'Unique Combinations:':<25} {div['unique_dimension_combinations']}")

        if "novelty_distribution" in scorecard:
            nov = scorecard["novelty_distribution"]
            lines.append(f"\n{'NOVELTY DISTRIBUTION':-^60}")
            lines.append(f"{'Average Novelty:':<25} {nov['average_novelty']:.2f}")
            lines.append(f"{'Range:':<25} {nov['novelty_range']['min']:.2f} - {nov['novelty_range']['max']:.2f}")
            lines.append(f"\n{'Distribution:':<25}")
            lines.append(f"{'  - Conventional (0.0-0.4):':<25} {nov['conventional_count']:>3} ({nov['conventional_pct']:.1f}%)")
            lines.append(f"{'  - Moderate (0.4-0.7):':<25} {nov['moderate_count']:>3} ({nov['moderate_pct']:.1f}%)")
            lines.append(f"{'  - Breakthrough (0.7-1.0):':<25} {nov['breakthrough_count']:>3} ({nov['breakthrough_pct']:.1f}%)")

        if "falsifiability" in scorecard:
            fals = scorecard["falsifiability"]
            lines.append(f"\n{'FALSIFIABILITY COVERAGE':-^60}")
            lines.append(f"{'Coverage Ratio:':<25} {fals['coverage_ratio']:.2f} ({fals['coverage_pct']:.1f}%)")
            lines.append(f"{'Experiments with Kill Conditions:':<25} {fals['experiments_with_kill_conditions']}/{fals['total_experiments']}")

            if fals['experiments_missing_kill_conditions']:
                lines.append(f"\nMissing Kill Conditions:")
                for exp_id in fals['experiments_missing_kill_conditions']:
                    lines.append(f"  - {exp_id}")

        if "synthesis_metrics" in scorecard:
            syn = scorecard["synthesis_metrics"]
            lines.append(f"\n{'SYNTHESIS METRICS':-^60}")
            lines.append(f"{'Frames Created:':<25} {syn['frame_count']}")
            lines.append(f"{'Ideas Synthesized:':<25} {syn['total_ideas_synthesized']}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate quality metrics for IDEATION_REPORT outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s output.json
  %(prog)s path/to/ideation_report.json --format json
  %(prog)s creative_output.json --format human

Output formats:
  json   - JSON output (default)
  human  - Human-readable text summary
        """
    )

    parser.add_argument(
        "report_path",
        type=Path,
        help="Path to IDEATION_REPORT JSON file"
    )

    parser.add_argument(
        "--format",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    try:
        scorecard_tool = CreativeScorecard(args.report_path)
        scorecard = scorecard_tool.generate_scorecard()

        if args.format == "json":
            print(json.dumps(scorecard, indent=2))
        else:  # human
            print(scorecard_tool.format_human_readable(scorecard))

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
