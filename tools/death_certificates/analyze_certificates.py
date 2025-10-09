#!/usr/bin/env python3
"""
Death Certificate Analytics
Analyzes death certificates to extract patterns, insights, and statistics.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple


class DeathCertificateAnalyzer:
    """
    Analyzes death certificates for patterns and insights.

    Extracts data from death certificate markdown files and generates
    statistics, trends, and actionable insights for agent development.
    """

    def __init__(self, cert_dir: str = 'tools/death_certificates'):
        """Initialize the analyzer.

        Args:
            cert_dir: Path to death certificates directory
        """
        self.cert_dir = Path(cert_dir)
        self.stats: Dict = defaultdict(int)
        self.causes: Dict[str, int] = defaultdict(int)
        self.lifespans: List[int] = []
        self.lessons: List[Tuple[str, str]] = []  # (agent_name, lesson)
        self.certificates: List[Dict] = []

    def extract_certificate_data(self, cert_path: Path) -> Dict:
        """Extract structured data from a death certificate.

        Args:
            cert_path: Path to certificate file

        Returns:
            Dictionary containing extracted data
        """
        try:
            with open(cert_path, 'r') as f:
                content = f.read()

            data = {
                'agent_name': cert_path.stem,
                'file': cert_path.name
            }

            # Extract agent name
            name_match = re.search(r'\*\*Agent Name:\*\* `([^`]+)`', content)
            if name_match:
                data['agent_name'] = name_match.group(1)

            # Extract dates
            creation_match = re.search(r'\*\*Date of Creation:\*\* (\d{4}-\d{2}-\d{2})', content)
            if creation_match:
                data['date_created'] = creation_match.group(1)

            death_match = re.search(r'\*\*Date of Death:\*\* (\d{4}-\d{2}-\d{2})', content)
            if death_match:
                data['date_death'] = death_match.group(1)

            # Extract lifespan
            lifespan_match = re.search(r'\*\*Lifespan:\*\* (\d+)', content)
            if lifespan_match:
                data['lifespan'] = int(lifespan_match.group(1))

            # Extract cause of death - handle both formats
            # Format 1: **Cause of Death:** [Category: Poor Adoption]
            cause_match = re.search(r'\*\*Cause of Death:\*\* \[Category: (.*?)\]', content)
            if cause_match:
                data['cause'] = cause_match.group(1).strip()
            else:
                # Format 2: **Cause of Death:** Scope Creep (description)
                cause_match = re.search(r'\*\*Cause of Death:\*\* ([^\(]+)', content)
                if cause_match:
                    data['cause'] = cause_match.group(1).strip()

            # Extract key lessons - try multiple formats
            lessons = []

            # Format 1: ## Lessons Learned with numbered items
            lessons_section = re.search(
                r'## Lessons Learned\n\n(.*?)(?=\n##|\Z)',
                content,
                re.DOTALL
            )
            if lessons_section:
                lessons_text = lessons_section.group(1).strip()
                # Extract numbered bullet points with bold headers
                lessons = re.findall(r'^\d+\.\s+\*\*(.+?)\*\*:', lessons_text, re.MULTILINE)

            # Format 2: ## Postmortem > What We'd Do Differently
            if not lessons:
                postmortem = re.search(
                    r'\*\*What We\'d Do Differently:\*\*\n\n(.*?)(?=\n\*\*|\Z)',
                    content,
                    re.DOTALL
                )
                if postmortem:
                    lessons_text = postmortem.group(1).strip()
                    # Extract numbered lessons from postmortem
                    lessons = re.findall(r'^\d+\.\s+\*\*([^:]+):\*\*', lessons_text, re.MULTILINE)

            if lessons:
                data['lessons'] = lessons

            # Extract migration path
            migration_match = re.search(
                r'## Migration Path\n\n(.*?)(?=\n##|\Z)',
                content,
                re.DOTALL
            )
            if migration_match:
                data['migration'] = migration_match.group(1).strip()

            return data

        except Exception as e:
            print(f"Error processing {cert_path.name}: {e}")
            return {}

    def analyze_all_certificates(self):
        """Analyze all death certificates in the directory."""
        if not self.cert_dir.exists():
            print(f"Error: Directory {self.cert_dir} does not exist")
            return

        cert_files = [
            f for f in self.cert_dir.glob('*.md')
            if f.name not in ['TEMPLATE.md', 'README.md']
        ]

        for cert_file in cert_files:
            data = self.extract_certificate_data(cert_file)
            if data:
                self.certificates.append(data)

                # Aggregate statistics
                if 'cause' in data:
                    self.causes[data['cause']] += 1

                if 'lifespan' in data:
                    self.lifespans.append(data['lifespan'])

                if 'lessons' in data:
                    for lesson in data['lessons']:
                        self.lessons.append((data['agent_name'], lesson))

        self.stats['total'] = len(self.certificates)

        # Calculate averages
        if self.lifespans:
            self.stats['avg_lifespan'] = sum(self.lifespans) / len(self.lifespans)
            self.stats['min_lifespan'] = min(self.lifespans)
            self.stats['max_lifespan'] = max(self.lifespans)

    def get_top_lessons(self, limit: int = 5) -> List[Tuple[str, str]]:
        """Get the top lessons learned.

        Args:
            limit: Maximum number of lessons to return

        Returns:
            List of (agent_name, lesson) tuples
        """
        return self.lessons[:limit]

    def print_statistics(self):
        """Print formatted statistics to stdout."""
        print("# Death Certificate Statistics\n")
        print(f"**Total Certificates:** {self.stats['total']}\n")

        if self.stats.get('avg_lifespan'):
            print(f"**Average Agent Lifespan:** {self.stats['avg_lifespan']:.1f} days")
            print(f"**Shortest Lifespan:** {self.stats['min_lifespan']} days")
            print(f"**Longest Lifespan:** {self.stats['max_lifespan']} days\n")

        if self.causes:
            print("## Causes of Death\n")
            sorted_causes = sorted(self.causes.items(), key=lambda x: x[1], reverse=True)
            for cause, count in sorted_causes:
                percentage = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                print(f"- **{cause}**: {count} ({percentage:.1f}%)")

        if self.lessons:
            print("\n## Top Lessons Learned\n")
            for i, (agent, lesson) in enumerate(self.get_top_lessons(5), 1):
                print(f"{i}. **{lesson}** (from `{agent}`)")

    def print_markdown_stats(self) -> str:
        """Generate markdown statistics for README insertion.

        Returns:
            Formatted markdown string with statistics
        """
        lines = []

        # Total agents calculation
        agents_dir = Path('agents')
        active_agents = len([f for f in agents_dir.glob('*.md')
                           if f.name not in ['AGENT_TEMPLATE.md', 'AGENT_PROFESSIONAL_BEHAVIOR.md']])
        total_agents = active_agents + self.stats['total']
        survival_rate = (active_agents / total_agents * 100) if total_agents > 0 else 100

        lines.append("## Statistics Dashboard\n")
        lines.append(f"- **Total Agents (All Time)**: {total_agents}")
        lines.append(f"- **Active Agents**: {active_agents}")
        lines.append(f"- **Deprecated Agents**: {self.stats['total']}")
        lines.append(f"- **Survival Rate**: {survival_rate:.1f}%")

        if self.stats.get('avg_lifespan'):
            lines.append(f"- **Average Agent Lifespan**: {self.stats['avg_lifespan']:.1f} days")

        if self.causes:
            most_common = max(self.causes.items(), key=lambda x: x[1])
            lines.append(f"- **Most Common Cause of Death**: {most_common[0]} ({most_common[1]} agents)")

        lines.append("")

        # Causes breakdown
        if self.causes:
            lines.append("## Browse by Cause of Death\n")
            sorted_causes = sorted(self.causes.items(), key=lambda x: x[1], reverse=True)
            for cause, count in sorted_causes:
                lines.append(f"### {cause} ({count} certificates)\n")

                # List agents with this cause
                agents_with_cause = [
                    cert for cert in self.certificates
                    if cert.get('cause') == cause
                ]

                for cert in agents_with_cause:
                    agent_name = cert.get('agent_name', 'unknown')
                    lifespan = cert.get('lifespan', '?')
                    lines.append(f"- [`{agent_name}`]({agent_name}.md) - Lived {lifespan} days")

                lines.append("")

        # Top lessons
        if self.lessons:
            lines.append("## Top Lessons Learned\n")
            for i, (agent, lesson) in enumerate(self.get_top_lessons(10), 1):
                lines.append(f"{i}. **{lesson}** (from [`{agent}`]({agent}.md))")

            lines.append("")

        return '\n'.join(lines)


def main():
    """Main entry point for the analyzer."""
    # Change to repository root
    script_dir = Path(__file__).parent.parent.parent
    os.chdir(script_dir)

    analyzer = DeathCertificateAnalyzer()
    analyzer.analyze_all_certificates()

    # Print statistics to stdout
    analyzer.print_statistics()

    # Also generate markdown for README
    print("\n" + "=" * 60)
    print("MARKDOWN FOR README.md")
    print("=" * 60 + "\n")
    print(analyzer.print_markdown_stats())


if __name__ == '__main__':
    main()
