"""
Query CLI - Interactive command-line interface for code archaeology.

This module provides tools to:
- Interactive REPL for asking questions
- Natural language query parsing
- Formatted answer presentation
- Follow-up question support
- Export to markdown/HTML
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import json

# Try to import rich for beautiful output
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from .git_analyzer import GitArchaeologist
    from .github_integrator import GitHubArchaeologist
    from .context_synthesizer import ContextSynthesizer, Answer, SearchableIndex
    from .analytics import CCAAnalytics, QueryCategory
except ImportError:
    # Running as script, adjust imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from git_analyzer import GitArchaeologist
    from github_integrator import GitHubArchaeologist
    from context_synthesizer import ContextSynthesizer, Answer, SearchableIndex
    from analytics import CCAAnalytics, QueryCategory


class ArchaeologyCLI:
    """Interactive CLI for code archaeology queries."""

    def __init__(self, repo_path: str, github_repo: Optional[str] = None):
        """
        Initialize archaeology CLI.

        Args:
            repo_path: Path to local git repository
            github_repo: Optional GitHub repo (owner/repo format)
        """
        self.repo_path = Path(repo_path)
        self.github_repo = github_repo
        self.index: Optional[SearchableIndex] = None
        self.console = Console() if HAS_RICH else None
        self.history: List[Answer] = []
        self.analytics = CCAAnalytics()
        self.analysis_start_time = None

    def _print(self, message: str, style: str = ""):
        """Print with optional rich formatting."""
        if self.console and HAS_RICH:
            self.console.print(message, style=style)
        else:
            print(message)

    def _print_panel(self, content: str, title: str, style: str = ""):
        """Print a panel with optional rich formatting."""
        if self.console and HAS_RICH:
            self.console.print(Panel(content, title=title, border_style=style))
        else:
            print(f"\n{'=' * 60}")
            print(f"  {title}")
            print('=' * 60)
            print(content)
            print('=' * 60 + '\n')

    def initialize(self):
        """Initialize the archaeology system (analyze repo, build index)."""
        self._print("\n🔍 Cognitive Code Archaeology", style="bold blue")
        self._print("=" * 60 + "\n")

        # Track analysis start
        self.analysis_start_time = time.time()

        if self.console and HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                # Step 1: Analyze git history
                task1 = progress.add_task("Analyzing git history...", total=None)
                git_arch = GitArchaeologist(str(self.repo_path))
                history = git_arch.analyze_repo()

                # Track analysis in analytics
                self.analytics.analysis_started(
                    commits_count=history.total_commits,
                    github_enriched=self.github_repo is not None
                )

                progress.update(task1, completed=True)
                self._print(f"  ✓ Found {history.total_commits} commits", style="green")

                # Step 2: Enrich with GitHub (if available)
                enriched = None
                if self.github_repo:
                    task2 = progress.add_task("Enriching with GitHub data...", total=None)
                    try:
                        owner, repo = self.github_repo.split('/')
                        gh_arch = GitHubArchaeologist(owner, repo)
                        enriched = gh_arch.enrich_history(history)
                        progress.update(task2, completed=True)
                        self._print(f"  ✓ Enrichment rate: {enriched.enrichment_rate:.1%}", style="green")
                    except Exception as e:
                        progress.update(task2, completed=True)
                        self._print(f"  ⚠ GitHub enrichment failed: {e}", style="yellow")
                else:
                    self._print("  ⓘ GitHub enrichment skipped (no repo specified)", style="dim")

                # Step 3: Build searchable index
                task3 = progress.add_task("Building searchable index...", total=None)
                synthesizer = ContextSynthesizer()
                from .github_integrator import EnrichedHistory
                if enriched:
                    self.index = synthesizer.build_searchable_index(enriched)
                else:
                    # Create minimal enriched history from base history
                    from .github_integrator import EnrichedCommit
                    enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
                    minimal_enriched = EnrichedHistory(
                        base_history=history,
                        enriched_commits=enriched_commits,
                        pull_requests={},
                        issues={},
                        commit_to_pr={},
                    )
                    self.index = synthesizer.build_searchable_index(minimal_enriched)
                progress.update(task3, completed=True)
                self._print(f"  ✓ Indexed {self.index.size} documents\n", style="green")

                # Track analysis completion
                self.analytics.analysis_completed(
                    commits_count=history.total_commits,
                    github_enriched=enriched is not None
                )
        else:
            # Simple progress without rich
            print("Analyzing git history...")
            git_arch = GitArchaeologist(str(self.repo_path))
            history = git_arch.analyze_repo()

            # Track analysis in analytics
            self.analytics.analysis_started(
                commits_count=history.total_commits,
                github_enriched=self.github_repo is not None
            )

            print(f"  ✓ Found {history.total_commits} commits")

            enriched = None
            if self.github_repo:
                print("Enriching with GitHub data...")
                try:
                    owner, repo = self.github_repo.split('/')
                    gh_arch = GitHubArchaeologist(owner, repo)
                    enriched = gh_arch.enrich_history(history)
                    print(f"  ✓ Enrichment rate: {enriched.enrichment_rate:.1%}")
                except Exception as e:
                    print(f"  ⚠ GitHub enrichment failed: {e}")

            print("Building searchable index...")
            synthesizer = ContextSynthesizer()
            from .github_integrator import EnrichedHistory, EnrichedCommit
            if enriched:
                self.index = synthesizer.build_searchable_index(enriched)
            else:
                enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
                minimal_enriched = EnrichedHistory(
                    base_history=history,
                    enriched_commits=enriched_commits,
                    pull_requests={},
                    issues={},
                    commit_to_pr={},
                )
                self.index = synthesizer.build_searchable_index(minimal_enriched)
            print(f"  ✓ Indexed {self.index.size} documents\n")

            # Track analysis completion
            self.analytics.analysis_completed(
                commits_count=history.total_commits,
                github_enriched=enriched is not None
            )

    def format_answer(self, answer: Answer) -> str:
        """Format answer for display."""
        if self.console and HAS_RICH:
            # Rich markdown formatting
            output = []
            output.append(f"## Answer\n")
            output.append(f"{answer.answer}\n")
            output.append(f"**Confidence:** {answer.confidence:.0%} | **Credibility:** {answer.credibility_score:.0%}\n")

            if answer.citations:
                output.append(f"## Citations ({len(answer.citations)})\n")
                for i, citation in enumerate(answer.citations[:5], 1):
                    output.append(f"{i}. **{citation.commit_sha[:8]}** by {citation.author} ({citation.commit_date.date()})")
                    output.append(f"   {citation.commit_message}")
                    if citation.source_type == 'pr' and citation.url:
                        output.append(f"   🔗 {citation.url}")
                    output.append("")

            return "\n".join(output)
        else:
            # Plain text formatting
            output = []
            output.append("\nAnswer:")
            output.append("-" * 60)
            output.append(answer.answer)
            output.append("")
            output.append(f"Confidence: {answer.confidence:.0%} | Credibility: {answer.credibility_score:.0%}")

            if answer.citations:
                output.append(f"\nCitations ({len(answer.citations)}):")
                output.append("-" * 60)
                for i, citation in enumerate(answer.citations[:5], 1):
                    output.append(f"{i}. {citation.commit_sha[:8]} by {citation.author} ({citation.commit_date.date()})")
                    output.append(f"   {citation.commit_message}")
                    if citation.source_type == 'pr' and citation.url:
                        output.append(f"   {citation.url}")
                    output.append("")

            return "\n".join(output)

    def query(self, question: str) -> Answer:
        """
        Execute a single query.

        Args:
            question: Natural language question

        Returns:
            Answer object
        """
        if not self.index:
            raise RuntimeError("Index not initialized. Call initialize() first.")

        # Track query start time
        query_start = time.time()

        synthesizer = ContextSynthesizer()
        answer = synthesizer.synthesize_answer(self.index, question)
        self.history.append(answer)

        # Track query execution
        query_time = time.time() - query_start
        category = self.analytics._categorize_query(question)

        self.analytics.query_executed(
            category=category,
            response_time_seconds=query_time,
            confidence=answer.confidence,
            credibility=answer.credibility_score,
            citation_count=len(answer.citations),
            estimated_time_saved_minutes=self._estimate_time_saved(category)
        )

        return answer

    def _estimate_time_saved(self, category: QueryCategory) -> int:
        """
        Estimate time saved by CCA vs manual investigation.

        Returns time in minutes based on query category.
        """
        # Conservative estimates based on case studies
        estimates = {
            QueryCategory.ARCHITECTURE_DECISION: 120,  # 2 hours vs 8 hours
            QueryCategory.TECHNICAL_DEBT: 90,  # 1.5 hours vs 6 hours
            QueryCategory.FEATURE_EVOLUTION: 60,  # 1 hour vs 4 hours
            QueryCategory.CODE_CONTEXT: 30,  # 30 min vs 2 hours
            QueryCategory.TEAM_KNOWLEDGE: 45,  # 45 min vs 3 hours
            QueryCategory.BUG_INVESTIGATION: 90,  # 1.5 hours vs 6 hours
            QueryCategory.ONBOARDING: 120,  # 2 hours vs 8 hours
            QueryCategory.OTHER: 30,  # 30 min default
        }
        return estimates.get(category, 30)

    def interactive_mode(self):
        """Run interactive REPL for queries."""
        if not self.index:
            self.initialize()

        self._print("Ready for questions!", style="bold green")
        self._print("Type 'help' for commands, 'quit' to exit.\n")

        while True:
            try:
                # Get input
                if self.console and HAS_RICH:
                    question = self.console.input("[bold cyan]❓ Question:[/bold cyan] ").strip()
                else:
                    question = input("❓ Question: ").strip()

                if not question:
                    continue

                # Handle commands
                if question.lower() in ['quit', 'exit', 'q']:
                    self._print("\nGoodbye! 👋", style="bold blue")
                    break
                elif question.lower() == 'help':
                    self._show_help()
                    continue
                elif question.lower() == 'history':
                    self._show_history()
                    continue
                elif question.lower().startswith('export '):
                    filepath = question[7:].strip()
                    self._export_history(filepath)
                    continue

                # Execute query
                answer = self.query(question)

                # Display answer
                if self.console and HAS_RICH:
                    markdown = Markdown(self.format_answer(answer))
                    self.console.print(markdown)
                else:
                    print(self.format_answer(answer))

            except KeyboardInterrupt:
                self._print("\n\nGoodbye! 👋", style="bold blue")
                break
            except EOFError:
                break
            except Exception as e:
                self._print(f"\n❌ Error: {e}", style="bold red")
                continue

    def _show_help(self):
        """Show help information."""
        help_text = """
**Commands:**
- `help` - Show this help message
- `history` - Show query history
- `export <file>` - Export history to markdown file
- `quit` / `exit` / `q` - Exit the program

**Tips:**
- Ask "why" questions: "Why was X refactored?"
- Ask "when" questions: "When was authentication added?"
- Ask "who" questions: "Who designed the API architecture?"
- Ask "what" questions: "What problems did feature X solve?"
        """
        self._print_panel(help_text, "Help", style="blue")

    def _show_history(self):
        """Show query history."""
        if not self.history:
            self._print("  No query history yet.", style="dim")
            return

        if self.console and HAS_RICH:
            table = Table(title="Query History", show_header=True, header_style="bold magenta")
            table.add_column("#", style="dim", width=3)
            table.add_column("Question", style="cyan")
            table.add_column("Confidence", justify="right", style="green")
            table.add_column("Citations", justify="right", style="yellow")

            for i, answer in enumerate(self.history, 1):
                table.add_row(
                    str(i),
                    answer.question[:60] + "..." if len(answer.question) > 60 else answer.question,
                    f"{answer.confidence:.0%}",
                    str(len(answer.citations)),
                )

            self.console.print(table)
        else:
            print("\nQuery History:")
            print("-" * 80)
            for i, answer in enumerate(self.history, 1):
                print(f"{i}. {answer.question}")
                print(f"   Confidence: {answer.confidence:.0%}, Citations: {len(answer.citations)}")
            print("-" * 80 + "\n")

    def _export_history(self, filepath: str):
        """Export query history to markdown file."""
        if not self.history:
            self._print("  No history to export.", style="yellow")
            return

        output_path = Path(filepath)
        lines = []

        lines.append(f"# Code Archaeology Query History\n")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"Repository: {self.repo_path}\n")
        lines.append(f"Total queries: {len(self.history)}\n")
        lines.append("---\n")

        for i, answer in enumerate(self.history, 1):
            lines.append(f"## Query {i}: {answer.question}\n")
            lines.append(f"**Timestamp:** {answer.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            lines.append(f"**Confidence:** {answer.confidence:.0%} | **Credibility:** {answer.credibility_score:.0%}\n")
            lines.append(f"\n### Answer\n")
            lines.append(f"{answer.answer}\n")

            if answer.citations:
                lines.append(f"\n### Citations ({len(answer.citations)})\n")
                for citation in answer.citations:
                    lines.append(f"- **{citation.commit_sha[:8]}** by {citation.author} ({citation.commit_date.date()})\n")
                    lines.append(f"  {citation.commit_message}\n")
                    if citation.url:
                        lines.append(f"  {citation.url}\n")

            lines.append("\n---\n")

        output_path.write_text("".join(lines))
        self._print(f"  ✓ Exported to: {output_path}", style="green")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cognitive Code Archaeology - Ask questions about your codebase history"
    )
    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='Path to git repository (default: current directory)'
    )
    parser.add_argument(
        '--github',
        metavar='OWNER/REPO',
        help='GitHub repository for enrichment (e.g., anthropics/claude-code)'
    )
    parser.add_argument(
        '--query',
        '-q',
        metavar='QUESTION',
        help='Single query mode (non-interactive)'
    )
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export results to markdown file'
    )

    args = parser.parse_args()

    # Initialize CLI
    cli = ArchaeologyCLI(args.repo_path, github_repo=args.github)

    if args.query:
        # Single query mode
        cli.initialize()
        answer = cli.query(args.query)

        if HAS_RICH:
            console = Console()
            markdown = Markdown(cli.format_answer(answer))
            console.print(markdown)
        else:
            print(cli.format_answer(answer))

        if args.export:
            cli._export_history(args.export)
    else:
        # Interactive mode
        cli.interactive_mode()


if __name__ == '__main__':
    main()
