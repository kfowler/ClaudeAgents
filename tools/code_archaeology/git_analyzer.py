"""
Git History Analyzer - Extract and analyze repository commit history.

This module provides tools to:
- Extract complete commit history with full context
- Identify architecturally significant commits
- Build temporal indexes for correlation
- Detect patterns in development history
"""

import subprocess
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import json


@dataclass
class Commit:
    """Represents a single git commit with full context."""

    sha: str
    message: str
    author: str
    email: str
    date: datetime
    parents: List[str]
    branch: Optional[str] = None
    files_changed: List[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    diff: str = ""
    tags: Set[str] = field(default_factory=set)

    def __hash__(self):
        return hash(self.sha)

    @property
    def is_merge(self) -> bool:
        """Check if this is a merge commit."""
        return len(self.parents) > 1

    @property
    def summary(self) -> str:
        """Get first line of commit message."""
        return self.message.split('\n')[0] if self.message else ""


@dataclass
class ArchCommit:
    """Architecturally significant commit with pattern metadata."""

    commit: Commit
    significance: str  # "architecture", "feature", "refactor", "config", "dependency"
    impact_score: float  # 0.0 to 1.0
    patterns: List[str]  # Detected patterns
    related_files: List[str]  # Key files affected

    def __hash__(self):
        return hash(self.commit.sha)


@dataclass
class RepositoryHistory:
    """Complete repository history with analysis metadata."""

    repo_path: Path
    commits: List[Commit]
    arch_commits: List[ArchCommit]
    temporal_index: Dict[str, List[Commit]]  # YYYY-MM-DD -> commits
    file_history: Dict[str, List[Commit]]  # filename -> commits
    author_stats: Dict[str, int]  # author -> commit count
    branch_commits: Dict[str, List[Commit]]  # branch -> commits

    @property
    def total_commits(self) -> int:
        return len(self.commits)

    @property
    def date_range(self) -> Tuple[datetime, datetime]:
        """Get earliest and latest commit dates."""
        if not self.commits:
            return (datetime.now(), datetime.now())
        dates = [c.date for c in self.commits]
        return (min(dates), max(dates))

    @property
    def top_contributors(self) -> List[Tuple[str, int]]:
        """Get top 10 contributors by commit count."""
        return sorted(self.author_stats.items(), key=lambda x: x[1], reverse=True)[:10]


class CommitAnalyzer:
    """Analyzes commits to identify architectural significance."""

    # Patterns that indicate architectural changes
    ARCH_PATTERNS = {
        'architecture': [
            r'package\.json',
            r'pyproject\.toml',
            r'Cargo\.toml',
            r'go\.mod',
            r'pom\.xml',
            r'build\.gradle',
            r'Dockerfile',
            r'docker-compose\.yml',
            r'kubernetes/',
            r'\.github/workflows/',
        ],
        'feature': [
            r'new\s+feature',
            r'add\s+\w+\s+(feature|capability|support)',
            r'implement\s+\w+',
            r'introduce\s+\w+',
        ],
        'refactor': [
            r'refactor',
            r'restructure',
            r'reorganize',
            r'rename\s+\w+\s+to',
            r'move\s+\w+\s+to',
            r'extract\s+\w+',
        ],
        'config': [
            r'\.env',
            r'config/',
            r'settings\.py',
            r'\.eslintrc',
            r'\.prettierrc',
            r'tsconfig\.json',
        ],
        'dependency': [
            r'upgrade\s+\w+',
            r'update\s+dependencies',
            r'bump\s+\w+',
            r'add\s+dependency',
        ],
    }

    # High-impact file patterns
    HIGH_IMPACT_FILES = [
        r'README\.md$',
        r'ARCHITECTURE\.md$',
        r'CLAUDE\.md$',
        r'package\.json$',
        r'requirements\.txt$',
        r'go\.mod$',
        r'Cargo\.toml$',
    ]

    def analyze_commit(self, commit: Commit) -> Optional[ArchCommit]:
        """
        Analyze a commit to determine if it's architecturally significant.

        Returns ArchCommit if significant, None otherwise.
        """
        patterns = []
        significance = None
        impact_score = 0.0

        # Check commit message for patterns
        message_lower = commit.message.lower()
        for sig_type, pattern_list in self.ARCH_PATTERNS.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    patterns.append(pattern)
                    if not significance:
                        significance = sig_type
                    impact_score += 0.2

        # Check files changed for high-impact patterns
        high_impact_files = []
        for file_path in commit.files_changed:
            for pattern in self.HIGH_IMPACT_FILES:
                if re.search(pattern, file_path):
                    high_impact_files.append(file_path)
                    impact_score += 0.3

        # Boost score for large changes
        total_changes = commit.additions + commit.deletions
        if total_changes > 500:
            impact_score += 0.3
        elif total_changes > 200:
            impact_score += 0.2
        elif total_changes > 100:
            impact_score += 0.1

        # Boost score for changes across many files
        if len(commit.files_changed) > 20:
            impact_score += 0.3
        elif len(commit.files_changed) > 10:
            impact_score += 0.2

        # Normalize impact score
        impact_score = min(1.0, impact_score)

        # Only consider significant if score above threshold or has patterns
        if impact_score >= 0.3 or patterns:
            return ArchCommit(
                commit=commit,
                significance=significance or "architecture",
                impact_score=impact_score,
                patterns=patterns,
                related_files=high_impact_files or commit.files_changed[:5],
            )

        return None


class TemporalCorrelator:
    """Builds temporal indexes for time-based correlation."""

    @staticmethod
    def build_temporal_index(commits: List[Commit]) -> Dict[str, List[Commit]]:
        """
        Create a temporal index mapping dates to commits.

        Format: YYYY-MM-DD -> [commits on that date]
        """
        index = {}
        for commit in commits:
            date_key = commit.date.strftime('%Y-%m-%d')
            if date_key not in index:
                index[date_key] = []
            index[date_key].append(commit)

        # Sort commits within each day by timestamp
        for date_key in index:
            index[date_key].sort(key=lambda c: c.date)

        return index

    @staticmethod
    def build_file_history(commits: List[Commit]) -> Dict[str, List[Commit]]:
        """
        Create a file history index mapping files to commits that changed them.

        Format: filename -> [commits that modified this file]
        """
        index = {}
        for commit in commits:
            for file_path in commit.files_changed:
                if file_path not in index:
                    index[file_path] = []
                index[file_path].append(commit)

        # Sort commits for each file chronologically
        for file_path in index:
            index[file_path].sort(key=lambda c: c.date)

        return index

    @staticmethod
    def build_author_stats(commits: List[Commit]) -> Dict[str, int]:
        """
        Create author statistics.

        Format: author -> commit count
        """
        stats = {}
        for commit in commits:
            author = commit.author
            stats[author] = stats.get(author, 0) + 1

        return stats


class GitArchaeologist:
    """Main class for analyzing git repository history."""

    def __init__(self, repo_path: str):
        """
        Initialize the archaeologist with a repository path.

        Args:
            repo_path: Path to the git repository (local directory or URL to clone)
        """
        self.repo_path = Path(repo_path).resolve()
        self.analyzer = CommitAnalyzer()
        self.correlator = TemporalCorrelator()

        if not (self.repo_path / '.git').exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def _run_git_command(self, args: List[str], check: bool = True) -> str:
        """Run a git command and return output."""
        result = subprocess.run(
            ['git', '-C', str(self.repo_path)] + args,
            capture_output=True,
            text=True,
            check=check,
        )
        return result.stdout.strip()

    def extract_commit_history(self, limit: Optional[int] = None) -> List[Commit]:
        """
        Extract complete commit history from the repository.

        Args:
            limit: Maximum number of commits to extract (None for all)

        Returns:
            List of Commit objects, ordered from newest to oldest
        """
        # Get commit log with custom format
        format_str = '%H%n%an%n%ae%n%at%n%P%n%s%n%b%n---COMMIT-END---'

        cmd = ['log', f'--format={format_str}', '--all']
        if limit:
            cmd.append(f'-n {limit}')

        log_output = self._run_git_command(cmd)

        commits = []
        commit_blocks = log_output.split('---COMMIT-END---')

        for block in commit_blocks:
            if not block.strip():
                continue

            lines = block.strip().split('\n')
            if len(lines) < 5:
                continue

            sha = lines[0]
            author = lines[1]
            email = lines[2]
            timestamp = int(lines[3])
            parents = lines[4].split() if lines[4] else []
            message = '\n'.join(lines[5:])

            # Get file stats for this commit
            stats_output = self._run_git_command(['show', '--stat', '--format=', sha])
            files_changed, additions, deletions = self._parse_stat_output(stats_output)

            commit = Commit(
                sha=sha,
                message=message.strip(),
                author=author,
                email=email,
                date=datetime.fromtimestamp(timestamp),
                parents=parents,
                files_changed=files_changed,
                additions=additions,
                deletions=deletions,
            )

            commits.append(commit)

        return commits

    def _parse_stat_output(self, stat_output: str) -> Tuple[List[str], int, int]:
        """Parse git show --stat output to extract files and line counts."""
        files = []
        total_additions = 0
        total_deletions = 0

        for line in stat_output.split('\n'):
            if '|' in line:
                # File change line: "path/to/file.py | 10 ++++------"
                file_path = line.split('|')[0].strip()
                files.append(file_path)

                # Extract additions/deletions
                match = re.search(r'(\d+)\s+\+', line)
                if match:
                    total_additions += int(match.group(1))

                match = re.search(r'(\d+)\s+-', line)
                if match:
                    total_deletions += int(match.group(1))

        return files, total_additions, total_deletions

    def identify_architectural_commits(self, commits: List[Commit]) -> List[ArchCommit]:
        """
        Identify architecturally significant commits from a commit list.

        Args:
            commits: List of commits to analyze

        Returns:
            List of ArchCommit objects, sorted by impact score (descending)
        """
        arch_commits = []

        for commit in commits:
            arch_commit = self.analyzer.analyze_commit(commit)
            if arch_commit:
                arch_commits.append(arch_commit)

        # Sort by impact score (highest first)
        arch_commits.sort(key=lambda ac: ac.impact_score, reverse=True)

        return arch_commits

    def build_temporal_index(self, commits: List[Commit]) -> Dict[str, List[Commit]]:
        """
        Build temporal index for date-based correlation.

        Args:
            commits: List of commits to index

        Returns:
            Dictionary mapping YYYY-MM-DD to commits on that date
        """
        return self.correlator.build_temporal_index(commits)

    def analyze_repo(self, limit: Optional[int] = None) -> RepositoryHistory:
        """
        Perform complete repository analysis.

        Args:
            limit: Maximum number of commits to analyze (None for all)

        Returns:
            RepositoryHistory object with complete analysis
        """
        print(f"Analyzing repository: {self.repo_path}")

        # Extract commit history
        print("Extracting commit history...")
        commits = self.extract_commit_history(limit=limit)
        print(f"  Found {len(commits)} commits")

        # Identify architectural commits
        print("Identifying architectural commits...")
        arch_commits = self.identify_architectural_commits(commits)
        print(f"  Found {len(arch_commits)} architecturally significant commits")

        # Build temporal index
        print("Building temporal index...")
        temporal_index = self.build_temporal_index(commits)
        print(f"  Indexed {len(temporal_index)} days")

        # Build file history
        print("Building file history...")
        file_history = self.correlator.build_file_history(commits)
        print(f"  Tracked {len(file_history)} files")

        # Build author stats
        print("Computing author statistics...")
        author_stats = self.correlator.build_author_stats(commits)
        print(f"  Found {len(author_stats)} contributors")

        # Get branch information
        print("Analyzing branches...")
        branch_commits = self._analyze_branches(commits)
        print(f"  Found {len(branch_commits)} branches")

        return RepositoryHistory(
            repo_path=self.repo_path,
            commits=commits,
            arch_commits=arch_commits,
            temporal_index=temporal_index,
            file_history=file_history,
            author_stats=author_stats,
            branch_commits=branch_commits,
        )

    def _analyze_branches(self, commits: List[Commit]) -> Dict[str, List[Commit]]:
        """Analyze branches and map commits to branches."""
        # Get all branches
        branches_output = self._run_git_command(['branch', '-a'])
        branches = [b.strip().lstrip('* ') for b in branches_output.split('\n')]

        branch_commits = {}

        # For each branch, get its commits
        for branch in branches:
            if not branch or 'HEAD' in branch:
                continue

            try:
                branch_log = self._run_git_command(['log', '--format=%H', branch], check=False)
                branch_shas = set(branch_log.split('\n'))

                # Find commits in this branch
                branch_commits[branch] = [c for c in commits if c.sha in branch_shas]
            except:
                continue

        return branch_commits

    def export_to_json(self, history: RepositoryHistory, output_path: str):
        """
        Export repository history to JSON for further processing.

        Args:
            history: RepositoryHistory to export
            output_path: Path to write JSON file
        """
        data = {
            'repo_path': str(history.repo_path),
            'total_commits': history.total_commits,
            'date_range': {
                'start': history.date_range[0].isoformat(),
                'end': history.date_range[1].isoformat(),
            },
            'commits': [
                {
                    'sha': c.sha,
                    'message': c.message,
                    'author': c.author,
                    'date': c.date.isoformat(),
                    'files_changed': c.files_changed,
                    'additions': c.additions,
                    'deletions': c.deletions,
                }
                for c in history.commits
            ],
            'arch_commits': [
                {
                    'sha': ac.commit.sha,
                    'significance': ac.significance,
                    'impact_score': ac.impact_score,
                    'patterns': ac.patterns,
                    'related_files': ac.related_files,
                }
                for ac in history.arch_commits
            ],
            'top_contributors': [
                {'author': author, 'commits': count}
                for author, count in history.top_contributors
            ],
        }

        output_path = Path(output_path)
        output_path.write_text(json.dumps(data, indent=2))
        print(f"Exported to: {output_path}")


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python git_analyzer.py <repo_path> [output.json]")
        sys.exit(1)

    repo_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    archaeologist = GitArchaeologist(repo_path)
    history = archaeologist.analyze_repo()

    print("\n=== Repository Analysis Summary ===")
    print(f"Total commits: {history.total_commits}")
    print(f"Architecturally significant: {len(history.arch_commits)}")
    print(f"Date range: {history.date_range[0].date()} to {history.date_range[1].date()}")
    print(f"\nTop contributors:")
    for author, count in history.top_contributors[:5]:
        print(f"  {author}: {count} commits")

    print(f"\nTop architectural commits:")
    for ac in history.arch_commits[:10]:
        print(f"  [{ac.significance}] {ac.commit.summary} (impact: {ac.impact_score:.2f})")

    if output_path:
        archaeologist.export_to_json(history, output_path)


if __name__ == '__main__':
    main()
