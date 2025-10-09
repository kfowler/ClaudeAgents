"""
GitHub Integration - Enrich commit history with GitHub PR and issue context.

This module provides tools to:
- Link commits to pull requests
- Extract PR discussion context
- Capture code review comments
- Track issue references
- Enrich commit metadata with GitHub data
"""

import os
import re
import requests
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import json
import time

from .git_analyzer import Commit, ArchCommit, RepositoryHistory


@dataclass
class PullRequest:
    """Represents a GitHub pull request with discussion context."""

    number: int
    title: str
    body: str
    author: str
    state: str  # "open", "closed", "merged"
    created_at: datetime
    merged_at: Optional[datetime]
    closed_at: Optional[datetime]
    commits: List[str]  # SHA list
    labels: List[str]
    reviewers: List[str]
    comments: List['PRComment'] = field(default_factory=list)
    review_comments: List['ReviewComment'] = field(default_factory=list)
    url: str = ""

    @property
    def is_merged(self) -> bool:
        """Check if PR was merged."""
        return self.state == "merged" or self.merged_at is not None

    @property
    def discussion_summary(self) -> str:
        """Get summary of all discussion."""
        parts = [self.body] if self.body else []
        parts.extend([c.body for c in self.comments])
        parts.extend([c.body for c in self.review_comments])
        return "\n\n".join(filter(None, parts))


@dataclass
class PRComment:
    """General PR comment."""

    author: str
    body: str
    created_at: datetime


@dataclass
class ReviewComment:
    """Code review comment on specific lines."""

    author: str
    body: str
    path: str  # File path
    line: int  # Line number
    created_at: datetime


@dataclass
class Issue:
    """Represents a GitHub issue."""

    number: int
    title: str
    body: str
    author: str
    state: str  # "open", "closed"
    created_at: datetime
    closed_at: Optional[datetime]
    labels: List[str]
    comments: List['IssueComment'] = field(default_factory=list)
    url: str = ""


@dataclass
class IssueComment:
    """Issue comment."""

    author: str
    body: str
    created_at: datetime


@dataclass
class EnrichedCommit:
    """Commit enriched with GitHub metadata."""

    commit: Commit
    pull_request: Optional[PullRequest] = None
    related_issues: List[Issue] = field(default_factory=list)
    discussion_context: str = ""
    decision_rationale: str = ""

    @property
    def has_context(self) -> bool:
        """Check if commit has meaningful GitHub context."""
        return self.pull_request is not None or len(self.related_issues) > 0


@dataclass
class EnrichedHistory:
    """Repository history enriched with GitHub data."""

    base_history: RepositoryHistory
    enriched_commits: List[EnrichedCommit]
    pull_requests: Dict[int, PullRequest]  # PR number -> PR
    issues: Dict[int, Issue]  # Issue number -> Issue
    commit_to_pr: Dict[str, int]  # Commit SHA -> PR number

    @property
    def enrichment_rate(self) -> float:
        """Percentage of commits with GitHub context."""
        if not self.enriched_commits:
            return 0.0
        enriched_count = sum(1 for ec in self.enriched_commits if ec.has_context)
        return enriched_count / len(self.enriched_commits)


class GitHubAPIClient:
    """GitHub API client with rate limiting and error handling."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.

        Args:
            token: GitHub personal access token (or use GITHUB_TOKEN env var)
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
            })
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json',
            })

        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _check_rate_limit(self):
        """Check and handle rate limiting."""
        if self.rate_limit_remaining is not None and self.rate_limit_remaining < 10:
            if self.rate_limit_reset:
                wait_time = max(0, self.rate_limit_reset - time.time())
                if wait_time > 0:
                    print(f"Rate limit low ({self.rate_limit_remaining}), waiting {wait_time:.0f}s...")
                    time.sleep(wait_time + 1)

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make GitHub API request with error handling.

        Args:
            endpoint: API endpoint (e.g., "/repos/owner/repo/pulls")
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        self._check_rate_limit()

        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params or {})

        # Update rate limit info
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))

        if response.status_code == 404:
            return None
        elif response.status_code == 403:
            raise Exception(f"GitHub API rate limit exceeded or forbidden: {response.text}")
        elif response.status_code != 200:
            raise Exception(f"GitHub API error {response.status_code}: {response.text}")

        return response.json()

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Optional[Dict]:
        """Get pull request data."""
        return self._make_request(f"/repos/{owner}/{repo}/pulls/{pr_number}")

    def get_pull_request_commits(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get commits in a pull request."""
        data = self._make_request(f"/repos/{owner}/{repo}/pulls/{pr_number}/commits")
        return data if data else []

    def get_pull_request_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get general comments on a pull request."""
        data = self._make_request(f"/repos/{owner}/{repo}/issues/{pr_number}/comments")
        return data if data else []

    def get_pull_request_review_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get code review comments on a pull request."""
        data = self._make_request(f"/repos/{owner}/{repo}/pulls/{pr_number}/comments")
        return data if data else []

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Optional[Dict]:
        """Get issue data."""
        return self._make_request(f"/repos/{owner}/{repo}/issues/{issue_number}")

    def get_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict]:
        """Get comments on an issue."""
        data = self._make_request(f"/repos/{owner}/{repo}/issues/{issue_number}/comments")
        return data if data else []

    def search_pulls_by_commit(self, owner: str, repo: str, commit_sha: str) -> List[Dict]:
        """Search for pull requests containing a specific commit."""
        # Note: This is not a direct API, so we use commit API
        data = self._make_request(f"/repos/{owner}/{repo}/commits/{commit_sha}/pulls",
                                   params={'per_page': 10})
        return data if data else []


class GitHubArchaeologist:
    """Enriches repository history with GitHub context."""

    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        """
        Initialize GitHub archaeologist.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            token: GitHub personal access token
        """
        self.owner = owner
        self.repo = repo
        self.client = GitHubAPIClient(token)

    @staticmethod
    def parse_repo_url(repo_url: str) -> Tuple[str, str]:
        """
        Parse GitHub repo URL to extract owner and repo name.

        Args:
            repo_url: GitHub URL (https://github.com/owner/repo or git@github.com:owner/repo.git)

        Returns:
            Tuple of (owner, repo)
        """
        # Handle HTTPS URLs
        https_pattern = r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$'
        match = re.search(https_pattern, repo_url)
        if match:
            return match.group(1), match.group(2)

        # Handle SSH URLs
        ssh_pattern = r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'
        match = re.search(ssh_pattern, repo_url)
        if match:
            return match.group(1), match.group(2)

        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    def _extract_issue_numbers(self, text: str) -> Set[int]:
        """Extract issue/PR numbers from text (e.g., #123, fixes #456)."""
        if not text:
            return set()

        # Match #123 patterns
        pattern = r'#(\d+)'
        matches = re.findall(pattern, text)
        return set(int(m) for m in matches)

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse GitHub datetime string."""
        if not dt_str:
            return None
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

    def fetch_pull_request(self, pr_number: int) -> Optional[PullRequest]:
        """
        Fetch complete pull request data including comments.

        Args:
            pr_number: Pull request number

        Returns:
            PullRequest object or None if not found
        """
        pr_data = self.client.get_pull_request(self.owner, self.repo, pr_number)
        if not pr_data:
            return None

        # Get commits in this PR
        pr_commits_data = self.client.get_pull_request_commits(self.owner, self.repo, pr_number)
        commit_shas = [c['sha'] for c in pr_commits_data]

        # Get general comments
        comments_data = self.client.get_pull_request_comments(self.owner, self.repo, pr_number)
        comments = [
            PRComment(
                author=c['user']['login'],
                body=c['body'],
                created_at=self._parse_datetime(c['created_at']),
            )
            for c in comments_data
        ]

        # Get review comments
        review_comments_data = self.client.get_pull_request_review_comments(self.owner, self.repo, pr_number)
        review_comments = [
            ReviewComment(
                author=c['user']['login'],
                body=c['body'],
                path=c['path'],
                line=c.get('line', c.get('original_line', 0)),
                created_at=self._parse_datetime(c['created_at']),
            )
            for c in review_comments_data
        ]

        # Extract reviewers from review comments
        reviewers = list(set(rc.author for rc in review_comments))

        return PullRequest(
            number=pr_number,
            title=pr_data['title'],
            body=pr_data.get('body', ''),
            author=pr_data['user']['login'],
            state="merged" if pr_data.get('merged_at') else pr_data['state'],
            created_at=self._parse_datetime(pr_data['created_at']),
            merged_at=self._parse_datetime(pr_data.get('merged_at')),
            closed_at=self._parse_datetime(pr_data.get('closed_at')),
            commits=commit_shas,
            labels=[label['name'] for label in pr_data.get('labels', [])],
            reviewers=reviewers,
            comments=comments,
            review_comments=review_comments,
            url=pr_data['html_url'],
        )

    def fetch_issue(self, issue_number: int) -> Optional[Issue]:
        """
        Fetch complete issue data including comments.

        Args:
            issue_number: Issue number

        Returns:
            Issue object or None if not found
        """
        issue_data = self.client.get_issue(self.owner, self.repo, issue_number)
        if not issue_data or 'pull_request' in issue_data:
            # This is a PR, not an issue
            return None

        # Get comments
        comments_data = self.client.get_issue_comments(self.owner, self.repo, issue_number)
        comments = [
            IssueComment(
                author=c['user']['login'],
                body=c['body'],
                created_at=self._parse_datetime(c['created_at']),
            )
            for c in comments_data
        ]

        return Issue(
            number=issue_number,
            title=issue_data['title'],
            body=issue_data.get('body', ''),
            author=issue_data['user']['login'],
            state=issue_data['state'],
            created_at=self._parse_datetime(issue_data['created_at']),
            closed_at=self._parse_datetime(issue_data.get('closed_at')),
            labels=[label['name'] for label in issue_data.get('labels', [])],
            comments=comments,
            url=issue_data['html_url'],
        )

    def link_commit_to_pr(self, commit: Commit) -> Optional[int]:
        """
        Find PR number associated with a commit.

        Args:
            commit: Commit to link

        Returns:
            PR number if found, None otherwise
        """
        # First, check commit message for PR references (#123)
        pr_numbers = self._extract_issue_numbers(commit.message)

        if pr_numbers:
            # Return first PR number found
            return min(pr_numbers)

        # Fall back to GitHub API search
        try:
            pulls_data = self.client.search_pulls_by_commit(self.owner, self.repo, commit.sha)
            if pulls_data:
                return pulls_data[0]['number']
        except:
            pass

        return None

    def enrich_commit(self, commit: Commit) -> EnrichedCommit:
        """
        Enrich a single commit with GitHub context.

        Args:
            commit: Commit to enrich

        Returns:
            EnrichedCommit with PR and issue data
        """
        enriched = EnrichedCommit(commit=commit)

        # Find associated PR
        pr_number = self.link_commit_to_pr(commit)
        if pr_number:
            try:
                pr = self.fetch_pull_request(pr_number)
                if pr:
                    enriched.pull_request = pr
                    enriched.discussion_context = pr.discussion_summary
            except Exception as e:
                print(f"Warning: Failed to fetch PR #{pr_number}: {e}")

        # Find related issues from commit message
        issue_numbers = self._extract_issue_numbers(commit.message)
        for issue_num in issue_numbers:
            if issue_num == pr_number:
                continue  # Already handled as PR

            try:
                issue = self.fetch_issue(issue_num)
                if issue:
                    enriched.related_issues.append(issue)
            except Exception as e:
                print(f"Warning: Failed to fetch issue #{issue_num}: {e}")

        return enriched

    def enrich_history(self, history: RepositoryHistory,
                       limit: Optional[int] = None) -> EnrichedHistory:
        """
        Enrich repository history with GitHub data.

        Args:
            history: RepositoryHistory from git analyzer
            limit: Maximum number of commits to enrich (None for all)

        Returns:
            EnrichedHistory with GitHub context
        """
        print(f"Enriching {len(history.commits)} commits with GitHub data...")

        commits_to_process = history.commits[:limit] if limit else history.commits
        enriched_commits = []
        pull_requests = {}
        issues = {}
        commit_to_pr = {}

        for i, commit in enumerate(commits_to_process, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(commits_to_process)} commits...")

            enriched = self.enrich_commit(commit)
            enriched_commits.append(enriched)

            # Track PRs and issues
            if enriched.pull_request:
                pr_num = enriched.pull_request.number
                pull_requests[pr_num] = enriched.pull_request
                commit_to_pr[commit.sha] = pr_num

            for issue in enriched.related_issues:
                issues[issue.number] = issue

        enriched_history = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests=pull_requests,
            issues=issues,
            commit_to_pr=commit_to_pr,
        )

        print(f"✓ Enrichment complete:")
        print(f"  Commits enriched: {len(enriched_commits)}")
        print(f"  Pull requests: {len(pull_requests)}")
        print(f"  Issues: {len(issues)}")
        print(f"  Enrichment rate: {enriched_history.enrichment_rate:.1%}")

        return enriched_history

    def export_to_json(self, enriched_history: EnrichedHistory, output_path: str):
        """
        Export enriched history to JSON.

        Args:
            enriched_history: EnrichedHistory to export
            output_path: Path to write JSON file
        """
        data = {
            'repo': f"{self.owner}/{self.repo}",
            'total_commits': len(enriched_history.enriched_commits),
            'enrichment_rate': enriched_history.enrichment_rate,
            'pull_requests_count': len(enriched_history.pull_requests),
            'issues_count': len(enriched_history.issues),
            'enriched_commits': [
                {
                    'sha': ec.commit.sha,
                    'message': ec.commit.message,
                    'author': ec.commit.author,
                    'date': ec.commit.date.isoformat(),
                    'pr_number': ec.pull_request.number if ec.pull_request else None,
                    'pr_title': ec.pull_request.title if ec.pull_request else None,
                    'has_context': ec.has_context,
                }
                for ec in enriched_history.enriched_commits
            ],
            'pull_requests': {
                str(pr_num): {
                    'number': pr.number,
                    'title': pr.title,
                    'author': pr.author,
                    'state': pr.state,
                    'merged': pr.is_merged,
                    'labels': pr.labels,
                    'reviewers': pr.reviewers,
                    'comments_count': len(pr.comments),
                    'review_comments_count': len(pr.review_comments),
                    'url': pr.url,
                }
                for pr_num, pr in enriched_history.pull_requests.items()
            },
            'issues': {
                str(issue_num): {
                    'number': issue.number,
                    'title': issue.title,
                    'author': issue.author,
                    'state': issue.state,
                    'labels': issue.labels,
                    'comments_count': len(issue.comments),
                    'url': issue.url,
                }
                for issue_num, issue in enriched_history.issues.items()
            },
        }

        output_path = Path(output_path)
        output_path.write_text(json.dumps(data, indent=2))
        print(f"Exported to: {output_path}")


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 4:
        print("Usage: python github_integrator.py <owner> <repo> <history.json> [output.json]")
        print("\nExample:")
        print("  python github_integrator.py anthropics claude-code /tmp/history.json /tmp/enriched.json")
        print("\nRequires GITHUB_TOKEN environment variable for authentication.")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    history_json = sys.argv[3]
    output_json = sys.argv[4] if len(sys.argv) > 4 else None

    # For now, we need to integrate with git_analyzer to load history
    print("Note: Full integration requires git_analyzer.RepositoryHistory")
    print(f"Repository: {owner}/{repo}")
    print(f"Input: {history_json}")

    if not os.environ.get('GITHUB_TOKEN'):
        print("\nWarning: GITHUB_TOKEN not set. API rate limits will be very restrictive.")
        print("Set GITHUB_TOKEN environment variable for better rate limits.")


if __name__ == '__main__':
    main()
