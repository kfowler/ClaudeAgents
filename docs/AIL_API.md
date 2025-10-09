# Archaeological Intelligence Layer (AIL) - API Reference

**Version:** 1.0.0
**Status:** Sprint 1 - Foundation Complete
**Last Updated:** 2025-10-08

---

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Git Analysis API](#git-analysis-api)
4. [GitHub Integration API](#github-integration-api)
5. [Context Synthesis API](#context-synthesis-api)
6. [Query Interface API](#query-interface-api)
7. [Data Models](#data-models)
8. [Error Handling](#error-handling)
9. [Performance Characteristics](#performance-characteristics)

---

## Overview

The Archaeological Intelligence Layer (AIL) provides agents with deep historical context about code decisions through multi-source analysis of git history, GitHub discussions, and semantic search capabilities.

**Key Capabilities:**
- Extract and analyze git commit history
- Enrich with GitHub PR and issue context
- Build searchable semantic indexes
- Answer natural language questions with citations
- Track confidence and credibility scores

**Package Structure:**
```python
from tools.code_archaeology import (
    # Git Analysis
    GitArchaeologist, Commit, ArchCommit, RepositoryHistory,
    # GitHub Integration
    GitHubArchaeologist, EnrichedCommit, EnrichedHistory, PullRequest, Issue,
    # Context Synthesis
    ContextSynthesizer, SearchableIndex, Answer, Citation,
    # Query Interface
    ArchaeologyCLI
)
```

---

## Core Classes

### GitArchaeologist

Main class for analyzing git repository history.

```python
class GitArchaeologist:
    """Extract and analyze repository commit history."""

    def __init__(self, repo_path: str)
```

**Constructor Parameters:**
- `repo_path` (str): Path to local git repository (must contain `.git` directory)

**Raises:**
- `ValueError`: If `repo_path` is not a valid git repository

**Example:**
```python
from tools.code_archaeology import GitArchaeologist

# Initialize with repository path
archaeologist = GitArchaeologist("/path/to/repo")

# Current directory
archaeologist = GitArchaeologist(".")
```

#### Methods

##### `extract_commit_history(limit: Optional[int] = None) -> List[Commit]`

Extract complete commit history with metadata.

**Parameters:**
- `limit` (int, optional): Maximum number of commits to extract. Default: all commits

**Returns:**
- `List[Commit]`: Commits ordered from newest to oldest

**Performance:**
- ~38 commits/second
- Linear time complexity O(n) where n = number of commits

**Example:**
```python
# Extract all commits
commits = archaeologist.extract_commit_history()

# Extract last 100 commits only
recent_commits = archaeologist.extract_commit_history(limit=100)

print(f"Found {len(commits)} commits")
for commit in commits[:5]:
    print(f"{commit.sha[:8]} - {commit.summary}")
```

##### `identify_architectural_commits(commits: List[Commit]) -> List[ArchCommit]`

Identify architecturally significant commits based on patterns and impact.

**Parameters:**
- `commits` (List[Commit]): List of commits to analyze

**Returns:**
- `List[ArchCommit]`: Architecturally significant commits sorted by impact score (descending)

**Detection Criteria:**
- **Architecture**: Changes to build files, Docker, CI/CD
- **Feature**: New feature additions, major capabilities
- **Refactor**: Code restructuring, renaming, extraction
- **Config**: Configuration file changes
- **Dependency**: Dependency updates and additions

**Impact Scoring (0.0 to 1.0):**
- Pattern matches: +0.2 per pattern
- Large changes (500+ lines): +0.3
- Many files (20+ files): +0.3
- High-impact files (README, package.json): +0.3

**Example:**
```python
commits = archaeologist.extract_commit_history()
arch_commits = archaeologist.identify_architectural_commits(commits)

print(f"Found {len(arch_commits)} architecturally significant commits")
for ac in arch_commits[:10]:
    print(f"[{ac.significance}] {ac.commit.summary}")
    print(f"  Impact: {ac.impact_score:.2f}, Patterns: {ac.patterns}")
```

##### `build_temporal_index(commits: List[Commit]) -> Dict[str, List[Commit]]`

Build temporal index for date-based correlation.

**Parameters:**
- `commits` (List[Commit]): Commits to index

**Returns:**
- `Dict[str, List[Commit]]`: Mapping of date strings (YYYY-MM-DD) to commits

**Example:**
```python
commits = archaeologist.extract_commit_history()
temporal_index = archaeologist.build_temporal_index(commits)

# Find all commits on a specific date
date_commits = temporal_index.get("2024-10-08", [])
print(f"Commits on 2024-10-08: {len(date_commits)}")

# Find all active dates
active_dates = sorted(temporal_index.keys())
print(f"Repository active from {active_dates[0]} to {active_dates[-1]}")
```

##### `analyze_repo(limit: Optional[int] = None) -> RepositoryHistory`

Perform complete repository analysis (recommended entry point).

**Parameters:**
- `limit` (int, optional): Maximum commits to analyze. Default: all

**Returns:**
- `RepositoryHistory`: Complete analysis results

**Processing Steps:**
1. Extract commit history
2. Identify architectural commits
3. Build temporal index
4. Build file history index
5. Compute author statistics
6. Analyze branches

**Performance:**
- 216 commits analyzed in ~5.64 seconds
- Memory usage: <100MB for typical repositories

**Example:**
```python
archaeologist = GitArchaeologist(".")
history = archaeologist.analyze_repo()

# Access results
print(f"Total commits: {history.total_commits}")
print(f"Architectural commits: {len(history.arch_commits)}")
print(f"Date range: {history.date_range[0].date()} to {history.date_range[1].date()}")

# Top contributors
for author, count in history.top_contributors[:5]:
    print(f"  {author}: {count} commits")

# Top architectural commits
for ac in history.arch_commits[:5]:
    print(f"  [{ac.significance}] {ac.commit.summary} (impact: {ac.impact_score:.2f})")
```

##### `export_to_json(history: RepositoryHistory, output_path: str)`

Export repository history to JSON for further processing.

**Parameters:**
- `history` (RepositoryHistory): Analysis results to export
- `output_path` (str): Path to write JSON file

**Example:**
```python
history = archaeologist.analyze_repo()
archaeologist.export_to_json(history, "repo_analysis.json")
```

---

### GitHubArchaeologist

Enrich commit history with GitHub PR and issue context.

```python
class GitHubArchaeologist:
    """Enrich repository history with GitHub data."""

    def __init__(self, owner: str, repo: str, token: Optional[str] = None)
```

**Constructor Parameters:**
- `owner` (str): Repository owner (username or organization)
- `repo` (str): Repository name
- `token` (str, optional): GitHub personal access token (or use `GITHUB_TOKEN` env var)

**Example:**
```python
from tools.code_archaeology import GitHubArchaeologist

# With environment variable GITHUB_TOKEN
gh_arch = GitHubArchaeologist("anthropics", "claude-code")

# With explicit token
gh_arch = GitHubArchaeologist("owner", "repo", token="ghp_xxxx")
```

#### Methods

##### `fetch_pull_request(pr_number: int) -> Optional[PullRequest]`

Fetch complete pull request data including all discussion.

**Parameters:**
- `pr_number` (int): Pull request number

**Returns:**
- `PullRequest`: PR data with comments and reviews, or `None` if not found

**API Calls:** 3 per PR (PR data, commits, comments, review comments)

**Example:**
```python
pr = gh_arch.fetch_pull_request(123)
if pr:
    print(f"PR #{pr.number}: {pr.title}")
    print(f"Author: {pr.author}, State: {pr.state}")
    print(f"Comments: {len(pr.comments)}, Review comments: {len(pr.review_comments)}")
    print(f"Discussion:\n{pr.discussion_summary[:200]}...")
```

##### `fetch_issue(issue_number: int) -> Optional[Issue]`

Fetch complete issue data including all comments.

**Parameters:**
- `issue_number` (int): Issue number

**Returns:**
- `Issue`: Issue data with comments, or `None` if not found

**Example:**
```python
issue = gh_arch.fetch_issue(456)
if issue:
    print(f"Issue #{issue.number}: {issue.title}")
    print(f"State: {issue.state}, Labels: {issue.labels}")
    print(f"Comments: {len(issue.comments)}")
```

##### `link_commit_to_pr(commit: Commit) -> Optional[int]`

Find PR number associated with a commit.

**Parameters:**
- `commit` (Commit): Commit to link

**Returns:**
- `int`: PR number if found, `None` otherwise

**Lookup Strategy:**
1. Parse commit message for PR references (#123)
2. Fall back to GitHub API search

**Example:**
```python
pr_number = gh_arch.link_commit_to_pr(commit)
if pr_number:
    print(f"Commit {commit.sha[:8]} is part of PR #{pr_number}")
```

##### `enrich_commit(commit: Commit) -> EnrichedCommit`

Enrich a single commit with GitHub context.

**Parameters:**
- `commit` (Commit): Commit to enrich

**Returns:**
- `EnrichedCommit`: Commit with PR and issue data

**Example:**
```python
enriched = gh_arch.enrich_commit(commit)
if enriched.pull_request:
    print(f"Part of PR #{enriched.pull_request.number}: {enriched.pull_request.title}")
if enriched.related_issues:
    print(f"Related issues: {[i.number for i in enriched.related_issues]}")
```

##### `enrich_history(history: RepositoryHistory, limit: Optional[int] = None) -> EnrichedHistory`

Enrich complete repository history with GitHub data.

**Parameters:**
- `history` (RepositoryHistory): Git analysis results
- `limit` (int, optional): Maximum commits to enrich. Default: all

**Returns:**
- `EnrichedHistory`: Enriched history with PR/issue context

**Performance:**
- Rate limited: ~60 commits/minute (without token), ~5000 commits/hour (with token)
- Automatic backoff on rate limit

**Example:**
```python
from tools.code_archaeology import GitArchaeologist, GitHubArchaeologist

# Step 1: Analyze git history
git_arch = GitArchaeologist(".")
history = git_arch.analyze_repo()

# Step 2: Enrich with GitHub data
gh_arch = GitHubArchaeologist("owner", "repo")
enriched = gh_arch.enrich_history(history, limit=50)

print(f"Enrichment rate: {enriched.enrichment_rate:.1%}")
print(f"Pull requests: {len(enriched.pull_requests)}")
print(f"Issues: {len(enriched.issues)}")
```

##### `export_to_json(enriched_history: EnrichedHistory, output_path: str)`

Export enriched history to JSON.

**Parameters:**
- `enriched_history` (EnrichedHistory): Enriched analysis results
- `output_path` (str): Path to write JSON file

**Example:**
```python
gh_arch.export_to_json(enriched, "enriched_history.json")
```

---

### ContextSynthesizer

Semantic search and answer generation engine.

```python
class ContextSynthesizer:
    """Main context synthesis engine."""

    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None)
```

**Constructor Parameters:**
- `embedding_provider` (EmbeddingProvider, optional): Provider for text embeddings. Default: `SimpleEmbeddingProvider()`

**Available Providers:**
- `SimpleEmbeddingProvider()`: TF-IDF based, no dependencies (default)
- `ClaudeEmbeddingProvider(api_key)`: Placeholder for future Anthropic embeddings

**Example:**
```python
from tools.code_archaeology import ContextSynthesizer, SimpleEmbeddingProvider

# Use default provider (TF-IDF)
synthesizer = ContextSynthesizer()

# Use custom provider
provider = SimpleEmbeddingProvider(max_features=1024)
synthesizer = ContextSynthesizer(embedding_provider=provider)
```

#### Methods

##### `build_searchable_index(enriched_history: EnrichedHistory) -> SearchableIndex`

Build searchable semantic index from enriched history.

**Parameters:**
- `enriched_history` (EnrichedHistory): Enriched history to index

**Returns:**
- `SearchableIndex`: Ready for querying

**Indexing Process:**
1. Extract documents from commits, PRs, issues
2. Generate embeddings for each document
3. Build FAISS index (if available) or use simple search
4. Store metadata for result retrieval

**Performance:**
- ~1-2 seconds for 200 documents
- Memory: ~5MB per 100 documents

**Example:**
```python
from tools.code_archaeology import (
    GitArchaeologist, GitHubArchaeologist, ContextSynthesizer
)

# Analyze and enrich
git_arch = GitArchaeologist(".")
history = git_arch.analyze_repo()

gh_arch = GitHubArchaeologist("owner", "repo")
enriched = gh_arch.enrich_history(history)

# Build index
synthesizer = ContextSynthesizer()
index = synthesizer.build_searchable_index(enriched)

print(f"Indexed {index.size} documents")
```

##### `search(index: SearchableIndex, query: str, k: int = 10) -> List[SearchResult]`

Search the index with a natural language query.

**Parameters:**
- `index` (SearchableIndex): Index to search
- `query` (str): Natural language query
- `k` (int): Number of results to return. Default: 10

**Returns:**
- `List[SearchResult]`: Search results sorted by relevance

**Search Algorithm:**
- TF-IDF cosine similarity (default)
- FAISS L2 distance (if available)
- Returns top-k most relevant documents

**Example:**
```python
results = synthesizer.search(index, "Why was authentication refactored?", k=5)

for result in results:
    commit = result.commit.commit
    print(f"{commit.sha[:8]} - {commit.summary}")
    print(f"  Relevance: {result.relevance_score:.2f}")
    print(f"  Excerpt: {result.matched_content[:100]}...")
```

##### `synthesize_answer(index: SearchableIndex, question: str, max_results: int = 10) -> Answer`

Generate coherent answer from search results.

**Parameters:**
- `index` (SearchableIndex): Index to query
- `question` (str): Natural language question
- `max_results` (int): Maximum search results to consider. Default: 10

**Returns:**
- `Answer`: Answer with citations and confidence scores

**Answer Generation:**
1. Search for relevant documents
2. Extract top 5 citations
3. Generate answer from search results
4. Calculate confidence score (0.0 to 1.0)
5. Calculate credibility score (0.0 to 1.0)

**Confidence Factors:**
- Average relevance of top 3 results
- Boosted if multiple high-quality results

**Credibility Factors:**
- Base confidence score
- Number of citations (3+ boosts score)
- Average relevance of citations

**Example:**
```python
answer = synthesizer.synthesize_answer(
    index,
    "Why was the authentication system refactored?"
)

print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence:.1%}")
print(f"Credibility: {answer.credibility_score:.1%}")
print(f"\nCitations ({len(answer.citations)}):")
for citation in answer.citations:
    print(f"  - {citation.commit_sha[:8]}: {citation.commit_message}")
```

##### `export_index(index: SearchableIndex, output_path: str)`

Export searchable index to disk for reuse.

**Parameters:**
- `index` (SearchableIndex): Index to export
- `output_path` (str): Directory path to write index files

**Exported Files:**
- `documents.json`: Documents and metadata
- `embeddings.npy`: NumPy array of embeddings
- `faiss.index`: FAISS index (if available)

**Example:**
```python
synthesizer.export_index(index, "/tmp/index_cache")
# Later: Load from cache (future feature)
```

---

### ArchaeologyCLI

Interactive command-line interface for queries.

```python
class ArchaeologyCLI:
    """Interactive CLI for code archaeology queries."""

    def __init__(self, repo_path: str, github_repo: Optional[str] = None)
```

**Constructor Parameters:**
- `repo_path` (str): Path to local git repository
- `github_repo` (str, optional): GitHub repo in "owner/repo" format

**Example:**
```python
from tools.code_archaeology import ArchaeologyCLI

# Basic usage (git only)
cli = ArchaeologyCLI(".")

# With GitHub enrichment
cli = ArchaeologyCLI(".", github_repo="anthropics/claude-code")
```

#### Methods

##### `initialize()`

Initialize the archaeology system (analyze repo, build index).

**Processing Steps:**
1. Analyze git history
2. Enrich with GitHub data (if configured)
3. Build searchable index
4. Track analytics

**Output:** Progress indicators and summary statistics

**Example:**
```python
cli = ArchaeologyCLI(".")
cli.initialize()
# Output:
# 🔍 Cognitive Code Archaeology
# Analyzing git history...
#   ✓ Found 219 commits
# Building searchable index...
#   ✓ Indexed 219 documents
```

##### `query(question: str) -> Answer`

Execute a single query.

**Parameters:**
- `question` (str): Natural language question

**Returns:**
- `Answer`: Answer object with citations

**Raises:**
- `RuntimeError`: If `initialize()` not called first

**Example:**
```python
cli.initialize()
answer = cli.query("Why was authentication refactored?")

print(answer.answer)
print(f"Confidence: {answer.confidence:.0%}")
```

##### `interactive_mode()`

Run interactive REPL for queries.

**Features:**
- Natural language question input
- Rich terminal formatting (if available)
- Command system (help, history, export, quit)
- Query history tracking
- Error recovery

**Commands:**
- `help`: Show help information
- `history`: Display query history
- `export <file>`: Export history to markdown
- `quit` / `exit` / `q`: Exit the program

**Example:**
```python
cli = ArchaeologyCLI(".", github_repo="owner/repo")
cli.interactive_mode()
# Enters interactive REPL:
# ❓ Question: Why was X refactored?
# [Answer displayed]
# ❓ Question: [next question]
```

##### `format_answer(answer: Answer) -> str`

Format answer for display (markdown or plain text).

**Parameters:**
- `answer` (Answer): Answer to format

**Returns:**
- `str`: Formatted answer (markdown with rich, plain text otherwise)

**Example:**
```python
answer = cli.query("Why was X changed?")
formatted = cli.format_answer(answer)
print(formatted)
```

---

## Data Models

### Commit

```python
@dataclass
class Commit:
    """Represents a single git commit with full context."""

    sha: str                        # Commit SHA (40 characters)
    message: str                    # Full commit message
    author: str                     # Author name
    email: str                      # Author email
    date: datetime                  # Commit timestamp
    parents: List[str]              # Parent commit SHAs
    branch: Optional[str]           # Branch name
    files_changed: List[str]        # List of modified files
    additions: int                  # Lines added
    deletions: int                  # Lines deleted
    diff: str                       # Commit diff
    tags: Set[str]                  # Git tags

    @property
    def is_merge(self) -> bool:
        """Check if this is a merge commit."""
        return len(self.parents) > 1

    @property
    def summary(self) -> str:
        """Get first line of commit message."""
        return self.message.split('\n')[0]
```

### ArchCommit

```python
@dataclass
class ArchCommit:
    """Architecturally significant commit with pattern metadata."""

    commit: Commit                  # The commit
    significance: str               # "architecture", "feature", "refactor", "config", "dependency"
    impact_score: float             # 0.0 to 1.0
    patterns: List[str]             # Detected patterns
    related_files: List[str]        # Key files affected
```

### RepositoryHistory

```python
@dataclass
class RepositoryHistory:
    """Complete repository history with analysis metadata."""

    repo_path: Path                             # Repository path
    commits: List[Commit]                       # All commits
    arch_commits: List[ArchCommit]              # Architecturally significant
    temporal_index: Dict[str, List[Commit]]     # YYYY-MM-DD -> commits
    file_history: Dict[str, List[Commit]]       # filename -> commits
    author_stats: Dict[str, int]                # author -> commit count
    branch_commits: Dict[str, List[Commit]]     # branch -> commits

    @property
    def total_commits(self) -> int:
        """Total number of commits."""
        return len(self.commits)

    @property
    def date_range(self) -> Tuple[datetime, datetime]:
        """Get earliest and latest commit dates."""

    @property
    def top_contributors(self) -> List[Tuple[str, int]]:
        """Get top 10 contributors by commit count."""
```

### PullRequest

```python
@dataclass
class PullRequest:
    """Represents a GitHub pull request with discussion context."""

    number: int                             # PR number
    title: str                              # PR title
    body: str                               # PR description
    author: str                             # PR author
    state: str                              # "open", "closed", "merged"
    created_at: datetime                    # Creation timestamp
    merged_at: Optional[datetime]           # Merge timestamp
    closed_at: Optional[datetime]           # Close timestamp
    commits: List[str]                      # Commit SHAs in PR
    labels: List[str]                       # PR labels
    reviewers: List[str]                    # Code reviewers
    comments: List[PRComment]               # General comments
    review_comments: List[ReviewComment]    # Code review comments
    url: str                                # GitHub URL

    @property
    def is_merged(self) -> bool:
        """Check if PR was merged."""

    @property
    def discussion_summary(self) -> str:
        """Get summary of all discussion."""
```

### Issue

```python
@dataclass
class Issue:
    """Represents a GitHub issue."""

    number: int                     # Issue number
    title: str                      # Issue title
    body: str                       # Issue description
    author: str                     # Issue author
    state: str                      # "open", "closed"
    created_at: datetime            # Creation timestamp
    closed_at: Optional[datetime]   # Close timestamp
    labels: List[str]               # Issue labels
    comments: List[IssueComment]    # Issue comments
    url: str                        # GitHub URL
```

### EnrichedCommit

```python
@dataclass
class EnrichedCommit:
    """Commit enriched with GitHub metadata."""

    commit: Commit                      # The commit
    pull_request: Optional[PullRequest] # Associated PR
    related_issues: List[Issue]         # Related issues
    discussion_context: str             # Full discussion text
    decision_rationale: str             # Extracted rationale

    @property
    def has_context(self) -> bool:
        """Check if commit has meaningful GitHub context."""
```

### EnrichedHistory

```python
@dataclass
class EnrichedHistory:
    """Repository history enriched with GitHub data."""

    base_history: RepositoryHistory         # Base git analysis
    enriched_commits: List[EnrichedCommit]  # Enriched commits
    pull_requests: Dict[int, PullRequest]   # PR number -> PR
    issues: Dict[int, Issue]                # Issue number -> Issue
    commit_to_pr: Dict[str, int]            # Commit SHA -> PR number

    @property
    def enrichment_rate(self) -> float:
        """Percentage of commits with GitHub context."""
```

### SearchableIndex

```python
@dataclass
class SearchableIndex:
    """Searchable index of repository history."""

    enriched_history: EnrichedHistory       # Source data
    embeddings: Optional[np.ndarray]        # Document embeddings
    documents: List[str]                    # Indexed documents
    document_metadata: List[Dict]           # Document metadata
    faiss_index: Optional[object]           # FAISS index
    embedding_provider: EmbeddingProvider   # Embedding provider

    @property
    def size(self) -> int:
        """Number of indexed documents."""
```

### SearchResult

```python
@dataclass
class SearchResult:
    """Single search result with score."""

    commit: EnrichedCommit      # Matched commit
    relevance_score: float      # 0.0 to 1.0
    matched_content: str        # Specific content that matched
```

### Answer

```python
@dataclass
class Answer:
    """Generated answer with citations and confidence."""

    question: str               # Original question
    answer: str                 # Generated answer
    citations: List[Citation]   # Source citations
    confidence: float           # 0.0 to 1.0
    timestamp: datetime         # Answer timestamp
    reasoning: str              # Internal reasoning

    @property
    def credibility_score(self) -> float:
        """Calculate credibility based on citations and confidence."""
```

### Citation

```python
@dataclass
class Citation:
    """Source citation for an answer."""

    commit_sha: str             # Commit SHA
    commit_message: str         # Commit message
    commit_date: datetime       # Commit date
    author: str                 # Commit author
    source_type: str            # "commit", "pr", "issue", "comment"
    source_id: Optional[str]    # PR/issue number
    relevance_score: float      # 0.0 to 1.0
    excerpt: str                # Text excerpt
    url: str                    # Source URL
```

---

## Error Handling

### Common Exceptions

**`ValueError`**: Invalid input parameters
```python
try:
    archaeologist = GitArchaeologist("/invalid/path")
except ValueError as e:
    print(f"Invalid repository: {e}")
```

**`RuntimeError`**: System state errors
```python
try:
    cli = ArchaeologyCLI(".")
    answer = cli.query("question")  # Without initialize()
except RuntimeError as e:
    print(f"Not initialized: {e}")
```

**`requests.exceptions.RequestException`**: GitHub API errors
```python
from requests.exceptions import RequestException

try:
    gh_arch = GitHubArchaeologist("owner", "repo")
    enriched = gh_arch.enrich_history(history)
except RequestException as e:
    print(f"GitHub API error: {e}")
```

### Error Recovery Patterns

**Pattern 1: Graceful Degradation**
```python
# Try GitHub enrichment, fall back to git-only
try:
    gh_arch = GitHubArchaeologist("owner", "repo")
    enriched = gh_arch.enrich_history(history)
except Exception as e:
    print(f"GitHub enrichment failed: {e}")
    # Use base history without enrichment
    from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory
    enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
    enriched = EnrichedHistory(
        base_history=history,
        enriched_commits=enriched_commits,
        pull_requests={},
        issues={},
        commit_to_pr={},
    )
```

**Pattern 2: Rate Limit Handling**
```python
# GitHub API rate limiting is handled automatically
# The GitHubAPIClient will wait when rate limit is low
gh_arch = GitHubArchaeologist("owner", "repo")
enriched = gh_arch.enrich_history(history)
# Automatic backoff if rate limit < 10 requests remaining
```

**Pattern 3: Partial Results**
```python
# Limit analysis to avoid timeouts
history = archaeologist.analyze_repo(limit=100)  # Only last 100 commits
enriched = gh_arch.enrich_history(history, limit=50)  # Only enrich 50
```

---

## Performance Characteristics

### Git Analysis

| Operation | Complexity | Performance | Memory |
|-----------|-----------|-------------|--------|
| Extract commits | O(n) | ~38 commits/sec | ~1KB per commit |
| Identify arch commits | O(n) | ~200 commits/sec | Negligible |
| Build temporal index | O(n) | ~1000 commits/sec | ~500 bytes per commit |
| Build file history | O(n × m) | ~100 commits/sec | m = avg files per commit |

**Benchmark (ClaudeAgents repo):**
- 216 commits analyzed in 5.64 seconds
- 147 architectural commits identified
- Memory usage: <100MB

### GitHub Enrichment

| Operation | API Calls | Rate Limit | Performance |
|-----------|-----------|------------|-------------|
| Fetch PR | 3 | 5000/hour (authenticated) | ~500ms per PR |
| Fetch issue | 2 | 5000/hour | ~300ms per issue |
| Link commit to PR | 0-1 | 5000/hour | ~100ms (cached) |

**Rate Limiting:**
- Unauthenticated: 60 requests/hour
- Authenticated: 5000 requests/hour
- Automatic backoff when limit < 10

### Semantic Search

| Operation | Complexity | Performance | Memory |
|-----------|-----------|-------------|--------|
| Build index | O(n × d) | ~1-2 sec for 200 docs | ~5MB per 100 docs |
| Search (TF-IDF) | O(n × d) | ~50ms for 200 docs | Negligible |
| Search (FAISS) | O(log n × d) | ~10ms for 10,000 docs | ~20MB per 10,000 docs |

Where:
- n = number of documents
- d = embedding dimension (default: 512)

**Scaling Recommendations:**
- < 1,000 commits: Use default TF-IDF
- 1,000 - 10,000 commits: Install FAISS (`pip install faiss-cpu`)
- \> 10,000 commits: Use FAISS + limit analysis to recent commits

---

## Usage Examples

### Complete Workflow

```python
from tools.code_archaeology import (
    GitArchaeologist,
    GitHubArchaeologist,
    ContextSynthesizer,
    ArchaeologyCLI
)

# Step 1: Analyze git history
print("Step 1: Analyzing git history...")
git_arch = GitArchaeologist(".")
history = git_arch.analyze_repo()
print(f"  Found {history.total_commits} commits")

# Step 2: Enrich with GitHub data
print("Step 2: Enriching with GitHub...")
gh_arch = GitHubArchaeologist("owner", "repo")
enriched = gh_arch.enrich_history(history, limit=50)
print(f"  Enrichment rate: {enriched.enrichment_rate:.1%}")

# Step 3: Build searchable index
print("Step 3: Building search index...")
synthesizer = ContextSynthesizer()
index = synthesizer.build_searchable_index(enriched)
print(f"  Indexed {index.size} documents")

# Step 4: Ask questions
print("Step 4: Asking questions...")
answer = synthesizer.synthesize_answer(
    index,
    "Why was the authentication system refactored?"
)
print(f"\nAnswer: {answer.answer}")
print(f"Confidence: {answer.confidence:.0%}")
print(f"Credibility: {answer.credibility_score:.0%}")

# Step 5: Export results
print("\nStep 5: Exporting results...")
git_arch.export_to_json(history, "git_history.json")
gh_arch.export_to_json(enriched, "enriched_history.json")
synthesizer.export_index(index, "/tmp/search_index")
```

### CLI Usage

```python
# Interactive mode
cli = ArchaeologyCLI(".", github_repo="owner/repo")
cli.interactive_mode()

# Single query mode
cli = ArchaeologyCLI(".")
cli.initialize()
answer = cli.query("Why was X refactored?")
print(cli.format_answer(answer))
```

---

## See Also

- [AIL Integration Guide](AIL_INTEGRATION_GUIDE.md) - How to integrate AIL into agents
- [AIL User Guide](AIL_USER_GUIDE.md) - User-facing documentation
- [AIL Architecture](AIL_ARCHITECTURE.md) - System design and architecture
- [Cognitive Code Archaeology README](../tools/code_archaeology/README.md) - Implementation details

---

**Last Updated:** 2025-10-08
**Version:** 1.0.0
**Status:** Production Ready
