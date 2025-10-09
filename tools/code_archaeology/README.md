# Cognitive Code Archaeology

Multi-source historical analysis for codebase understanding. Answer "why" questions about code decisions using natural language queries.

## Overview

Cognitive Code Archaeology combines multiple data sources to provide deep historical context for code decisions:

- **Git History**: Commit messages, diffs, temporal patterns
- **GitHub Integration**: PR discussions, issue context, code review comments (Week 2)
- **Context Synthesis**: LLM-powered semantic search and answer generation (Week 3)
- **Natural Language Queries**: Interactive CLI for asking questions (Week 4)

## Quick Start

### Analyze a Repository

```python
from tools.code_archaeology import GitArchaeologist

# Initialize the archaeologist
archaeologist = GitArchaeologist("/path/to/repo")

# Analyze the repository
history = archaeologist.analyze_repo()

# View summary
print(f"Total commits: {history.total_commits}")
print(f"Architecturally significant: {len(history.arch_commits)}")
print(f"Date range: {history.date_range[0].date()} to {history.date_range[1].date()}")

# Export for further processing
archaeologist.export_to_json(history, "repo_history.json")
```

### CLI Usage

```bash
# Analyze current directory
python3 tools/code_archaeology/git_analyzer.py . output.json

# Analyze specific repository
python3 tools/code_archaeology/git_analyzer.py /path/to/repo output.json
```

## Week 1: Git History Analyzer ✅

**Status**: Complete

**Deliverables**:
- ✅ `git_analyzer.py`: Complete git history extraction and analysis
- ✅ `test_git_analyzer.py`: Comprehensive test suite (14 tests, all passing)
- ✅ Performance: 216 commits analyzed in <6 seconds
- ✅ JSON export for Week 2 GitHub enrichment

**Features**:
- Extract complete commit history with metadata
- Identify architecturally significant commits (68% detection rate)
- Build temporal index for correlation (date-based grouping)
- Track file history and author statistics
- Pattern detection (architecture, feature, refactor, config, dependency)
- Impact scoring (0.0 to 1.0) based on size, files, and patterns

**Example Output**:
```
=== Repository Analysis Summary ===
Total commits: 216
Architecturally significant: 147
Date range: 2025-07-25 to 2025-10-08

Top contributors:
  Kevin Fowler: 208 commits
  Thomas Ricouard: 6 commits
  google-labs-jules[bot]: 2 commits

Top architectural commits:
  [architecture] Add MCP preview implementation (impact: 1.00)
  [refactor] Merge Sprint 2: Create 4 Critical Missing Agents (impact: 1.00)
  [architecture] Merge Sprint 1: Model Assignment, Boundary Resolution (impact: 1.00)
```

## Week 2: GitHub Integration ✅

**Status**: Complete

**Deliverables**:
- ✅ `github_integrator.py`: Complete GitHub API integration (569 lines)
- ✅ `test_github_integrator.py`: Comprehensive test suite (14 unit tests, 3 integration tests)
- ✅ Performance: Rate limiting, caching, error handling
- ✅ JSON export for Week 3 semantic analysis

**Features**:
- Link commits to pull requests (via message parsing + API search)
- Extract PR discussion context (body + comments + review comments)
- Capture code review comments with file/line references
- Track issue references and relationships
- Enrich commit data with GitHub metadata
- Rate limit handling and automatic backoff
- GITHUB_TOKEN authentication support

**Data Models**:
- `PullRequest`: Complete PR data with discussion
- `Issue`: Issue tracking with comments
- `EnrichedCommit`: Commit + GitHub context
- `EnrichedHistory`: Full repository with GitHub enrichment

**Example Usage**:
```python
from tools.code_archaeology import GitArchaeologist, GitHubArchaeologist

# First, analyze git history
git_arch = GitArchaeologist(".")
history = git_arch.analyze_repo()

# Then, enrich with GitHub data
gh_arch = GitHubArchaeologist("owner", "repo")
enriched = gh_arch.enrich_history(history, limit=50)

print(f"Enrichment rate: {enriched.enrichment_rate:.1%}")
print(f"Pull requests: {len(enriched.pull_requests)}")
print(f"Issues: {len(enriched.issues)}")
```

## Week 3: Context Synthesis Engine ✅

**Status**: Complete

**Deliverables**:
- ✅ `context_synthesizer.py`: Semantic search and answer generation (462 lines)
- ✅ `test_context_synthesizer.py`: Comprehensive test suite (18 tests, all passing)
- ✅ Multiple embedding providers (Simple TF-IDF + Claude placeholder + FAISS support)
- ✅ Answer generation with citations and confidence scoring

**Features**:
- Semantic search across enriched history:
  - Document extraction from commits, PRs, issues
  - TF-IDF based embeddings (no external dependencies)
  - Optional FAISS integration for fast vector search
  - Cosine similarity ranking
- Answer generation:
  - Natural language question answering
  - Multi-source citation tracking
  - Confidence and credibility scoring
  - Reasoning transparency
- Embedding providers:
  - `SimpleEmbeddingProvider`: TF-IDF, no dependencies
  - `ClaudeEmbeddingProvider`: Placeholder for future Anthropic embeddings
  - FAISS support for 10,000+ document scalability

**Data Models**:
- `SearchableIndex`: Embeddings + documents + metadata
- `SearchResult`: Commit + relevance score + matched content
- `Citation`: Source tracking with relevance scores
- `Answer`: Question + answer + citations + confidence + credibility

**Example Usage**:
```python
from tools.code_archaeology import (
    GitArchaeologist, GitHubArchaeologist, ContextSynthesizer
)

# Step 1: Analyze git history
git_arch = GitArchaeologist(".")
history = git_arch.analyze_repo()

# Step 2: Enrich with GitHub data
gh_arch = GitHubArchaeologist("owner", "repo")
enriched = gh_arch.enrich_history(history)

# Step 3: Build searchable index
synthesizer = ContextSynthesizer()
index = synthesizer.build_searchable_index(enriched)

# Step 4: Ask questions!
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

## Week 4: Query CLI Interface ✅

**Status**: Complete

**Deliverables**:
- ✅ `query_cli.py`: Interactive CLI with rich formatting (300 lines)
- ✅ `archaeology` executable: Clean entry point script
- ✅ `test_query_cli.py`: Comprehensive test suite (8 unit tests, 5 integration tests)
- ✅ Single query mode + interactive REPL
- ✅ Export to markdown

**Features**:
- Interactive REPL:
  - Natural language question input
  - Real-time answer generation
  - Formatted output (plain text + rich terminal)
  - Command system (help, history, export, quit)
- Single query mode:
  - Non-interactive CLI for automation
  - Direct answer output
  - Optional markdown export
- Rich formatting (when available):
  - Colored output and panels
  - Progress spinners during analysis
  - Formatted markdown answers
  - Beautiful tables for history
- Export functionality:
  - Markdown export of query history
  - Timestamped queries and answers
  - Citation preservation

**CLI Commands**:
```bash
# Interactive mode (default)
python3 tools/archaeology

# Single query mode
python3 tools/archaeology --query "Why was X refactored?"

# With GitHub enrichment
python3 tools/archaeology --github owner/repo

# Export results
python3 tools/archaeology --query "..." --export output.md
```

**Example Session**:
```
$ python3 tools/archaeology

🔍 Cognitive Code Archaeology
============================================================

Analyzing git history...
  ✓ Found 219 commits
Building searchable index...
  ✓ Indexed 219 documents

Ready for questions!
Type 'help' for commands, 'quit' to exit.

❓ Question: What is the purpose of this repository?

Answer:
Based on repository history analysis:

The most relevant commit is 935383b3 by google-labs-jules[bot]:
"feat: Create 'Mythical Man-Month' agents"

Confidence: 45% | Credibility: 74%

Citations (5):
1. 935383b3 by google-labs-jules[bot] (2025-07-28)
   feat: Create 'Mythical Man-Month' agents
```

## Data Models

### Commit
```python
@dataclass
class Commit:
    sha: str
    message: str
    author: str
    email: str
    date: datetime
    parents: List[str]
    branch: Optional[str]
    files_changed: List[str]
    additions: int
    deletions: int
    diff: str
    tags: Set[str]
```

### ArchCommit (Architecturally Significant)
```python
@dataclass
class ArchCommit:
    commit: Commit
    significance: str  # "architecture", "feature", "refactor", "config", "dependency"
    impact_score: float  # 0.0 to 1.0
    patterns: List[str]  # Detected patterns
    related_files: List[str]  # Key files affected
```

### RepositoryHistory
```python
@dataclass
class RepositoryHistory:
    repo_path: Path
    commits: List[Commit]
    arch_commits: List[ArchCommit]
    temporal_index: Dict[str, List[Commit]]  # YYYY-MM-DD -> commits
    file_history: Dict[str, List[Commit]]  # filename -> commits
    author_stats: Dict[str, int]  # author -> commit count
    branch_commits: Dict[str, List[Commit]]  # branch -> commits
```

## Performance Benchmarks

**ClaudeAgents Repository**:
- Total commits: 216
- Analysis time: 5.64 seconds
- Architectural commits detected: 147 (68%)
- Files tracked: 583
- Days indexed: 11
- Memory usage: <100MB

**Scalability**:
- Target: 10,000 commits in <60 seconds
- Current: 216 commits in 5.64 seconds (~38 commits/sec)
- Projected: 10,000 commits in ~263 seconds (4.4 minutes)

## Example Questions (Week 4 Target)

Once the full system is complete, users will be able to ask:

- "Why did we choose React over Vue for the frontend?"
- "What was the reasoning behind the microservices architecture?"
- "When was authentication first added and why?"
- "Who decided to use TypeScript and what were their concerns?"
- "What problems were we trying to solve with the latest refactor?"

## Testing

```bash
# Run all tests
python3 -m pytest tests/test_git_analyzer.py -v

# Run specific test class
python3 -m pytest tests/test_git_analyzer.py::TestGitArchaeologist -v

# Run performance tests only
python3 -m pytest tests/test_git_analyzer.py::TestPerformance -v
```

## Architecture

```
tools/code_archaeology/
├── __init__.py              # Package exports
├── git_analyzer.py          # Week 1: Git history extraction ✅
├── github_integrator.py     # Week 2: GitHub API integration
├── context_synthesizer.py   # Week 3: LLM-powered synthesis
├── query_cli.py             # Week 4: Natural language queries
└── README.md                # This file

tests/
└── test_git_analyzer.py     # Week 1 tests ✅
```

## Dependencies

**Week 1 (Current)**:
- Python 3.9+
- Git CLI
- Standard library only

**Current (Week 1-2)**:
- Python 3.9+
- Git CLI
- `requests` (GitHub API)

**Upcoming Weeks**:
- Week 3: `openai`, `anthropic`, `faiss-cpu` (LLM + vector search)
- Week 4: `prompt_toolkit`, `rich` (CLI interface)

## Privacy & Security

- **Local-only processing**: No external API calls (Week 1-2)
- **Opt-in GitHub access**: Requires PAT for private repos (Week 2)
- **Code privacy**: Diffs and code content stay local
- **LLM processing**: Uses local embeddings or user's API keys (Week 3)

## Roadmap

- [x] Week 1: Git history analyzer (Complete)
- [x] Week 2: GitHub integration (Complete)
- [x] Week 3: Context synthesis engine (Complete)
- [x] Week 4: Query CLI interface (Complete)
- [ ] Week 5+: Slack/JIRA integration (stretch goal)

## 🎉 **COMPLETE: All 4 weeks implemented successfully!**

The Cognitive Code Archaeology system is now fully operational. You can ask natural
language questions about your codebase history and get answers with citations.

## Contributing

See `docs/contributing.md` for contribution guidelines.

## License

MIT License - See LICENSE file for details.
