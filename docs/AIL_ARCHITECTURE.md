# Archaeological Intelligence Layer (AIL) - Architecture Overview

**Version:** 1.0.0
**Status:** Sprint 1 Complete
**Last Updated:** 2025-10-08

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Integration with CCA](#integration-with-cca)
6. [Caching Strategy](#caching-strategy)
7. [Performance Characteristics](#performance-characteristics)
8. [Security Model](#security-model)
9. [Scalability](#scalability)
10. [Future Roadmap](#future-roadmap)

---

## System Overview

### Vision

The Archaeological Intelligence Layer (AIL) provides all ClaudeAgents agents with deep historical context about code decisions, enabling them to understand not just **what** the code does, but **why** it exists.

### Design Principles

1. **Privacy-First**: All processing is local; no code sent to external servers
2. **Accuracy-First**: Every answer cites sources; confidence scoring for reliability
3. **Performance-First**: Cacheable indexes; sub-second query times
4. **Modular Design**: Each component is independently testable and replaceable
5. **Gradual Enhancement**: Works with git-only; enrichment adds value incrementally

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Layer                             │
│  (code-architect, security-auditor, technical-writer, etc.) │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Archaeological Intelligence Layer              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Git Analyzer │  │   GitHub     │  │   Context    │     │
│  │              │→ │  Integrator  │→ │ Synthesizer  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│   (Git Repository, GitHub API, Local Cache)                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| **GitArchaeologist** | Extract git history | Repository path | RepositoryHistory |
| **GitHubArchaeologist** | Enrich with GitHub | RepositoryHistory + repo name | EnrichedHistory |
| **ContextSynthesizer** | Semantic search & Q&A | EnrichedHistory + question | Answer with citations |
| **ArchaeologyCLI** | User interface | User questions | Formatted answers |

---

## Architecture Diagram

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Users                                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Developers  │  │    Agents    │  │     CLI      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                  │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          └────────┬────────┴────────┬────────┘
                   │                 │
                   ▼                 ▼
┌──────────────────────────────────────────────────────────────┐
│                   Archaeological Intelligence Layer          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Query Interface (CLI/API)                 │ │
│  │  - ArchaeologyCLI: Interactive REPL                   │ │
│  │  - Single query mode                                  │ │
│  │  - Export capabilities                                │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                              │
│               ▼                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Context Synthesis Engine                     │ │
│  │  - Semantic search (TF-IDF/FAISS)                     │ │
│  │  - Answer generation                                   │ │
│  │  - Citation tracking                                   │ │
│  │  - Confidence scoring                                  │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                              │
│               ▼                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Data Integration Layer                    │ │
│  │                                                        │ │
│  │  ┌──────────────────┐      ┌──────────────────┐      │ │
│  │  │  Git Analyzer    │      │ GitHub Integrator│      │ │
│  │  │  - Extract commits│  →   │ - Link PRs       │      │ │
│  │  │  - Detect patterns│      │ - Extract issues │      │ │
│  │  │  - Build indexes │      │ - Get discussions│      │ │
│  │  └──────────────────┘      └──────────────────┘      │ │
│  │                                                        │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                              │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│                      Data Sources                            │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │     Git      │   │    GitHub    │   │    Cache     │   │
│  │  Repository  │   │     API      │   │   (Future)   │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │ 1. Ask question: "Why was X refactored?"
     ▼
┌──────────────────┐
│ ArchaeologyCLI   │
│  - Parse input   │
│  - Initialize    │
└────┬─────────────┘
     │ 2. Get/build index
     ▼
┌──────────────────┐     ┌──────────────────┐
│ GitArchaeologist │────▶│RepositoryHistory │
│  - analyze_repo()│     │  - commits       │
└────┬─────────────┘     │  - arch_commits  │
     │                   └──────────────────┘
     │ 3. Enrich (optional)
     ▼
┌────────────────────┐    ┌──────────────────┐
│GitHubArchaeologist │───▶│ EnrichedHistory  │
│ - enrich_history() │    │  - PR discussions│
└────┬───────────────┘    │  - Issues        │
     │                    └──────────────────┘
     │ 4. Build searchable index
     ▼
┌────────────────────┐    ┌──────────────────┐
│ContextSynthesizer  │───▶│ SearchableIndex  │
│- build_index()     │    │  - embeddings    │
│                    │    │  - documents     │
└────┬───────────────┘    │  - metadata      │
     │                    └──────────────────┘
     │ 5. Query
     │
     │ synthesize_answer(index, question)
     │
     │ 6. Search
     ▼
┌────────────────────┐
│  Semantic Search   │
│  - TF-IDF/FAISS   │
│  - Cosine sim.    │
└────┬───────────────┘
     │ 7. Top results
     ▼
┌────────────────────┐    ┌──────────────────┐
│ Answer Generator   │───▶│     Answer       │
│ - Synthesize text │    │  - answer text   │
│ - Extract citations│    │  - confidence    │
│ - Score confidence │    │  - citations     │
└────────────────────┘    └────┬─────────────┘
                               │
                               │ 8. Return to user
                               ▼
                          ┌──────────┐
                          │   User   │
                          └──────────┘
```

---

## Component Design

### 1. Git Analyzer (GitArchaeologist)

**Responsibility**: Extract and analyze git commit history

**Architecture:**
```
GitArchaeologist
├── CommitAnalyzer (identify architectural commits)
│   ├── Pattern detection (architecture, feature, refactor)
│   ├── Impact scoring (file count, line changes)
│   └── Significance classification
├── TemporalCorrelator (build temporal indexes)
│   ├── Date-based indexing (YYYY-MM-DD)
│   ├── File history tracking
│   └── Author statistics
└── Git CLI wrapper (subprocess)
    ├── Extract commits (git log)
    ├── Get file stats (git show --stat)
    └── Analyze branches (git branch)
```

**Key Algorithms:**

1. **Architectural Commit Detection**:
```python
def analyze_commit(commit):
    patterns = []
    impact_score = 0.0

    # Pattern matching
    for pattern in ARCH_PATTERNS:
        if matches(commit.message, pattern):
            patterns.append(pattern)
            impact_score += 0.2

    # File impact
    for file in commit.files_changed:
        if is_high_impact_file(file):
            impact_score += 0.3

    # Size impact
    if commit.additions + commit.deletions > 500:
        impact_score += 0.3

    return ArchCommit(commit, impact_score, patterns)
```

2. **Temporal Indexing**:
```python
def build_temporal_index(commits):
    index = {}
    for commit in commits:
        date_key = commit.date.strftime('%Y-%m-%d')
        index[date_key].append(commit)
    return index
```

**Performance:**
- Time: O(n) where n = number of commits
- Space: O(n × m) where m = average files per commit
- Throughput: ~38 commits/second

### 2. GitHub Integrator (GitHubArchaeologist)

**Responsibility**: Enrich commits with GitHub PR and issue context

**Architecture:**
```
GitHubArchaeologist
├── GitHubAPIClient (REST API wrapper)
│   ├── Rate limit handling
│   ├── Automatic retry/backoff
│   └── Error recovery
├── PR Enrichment
│   ├── Link commits to PRs
│   ├── Extract PR discussions
│   ├── Get code review comments
│   └── Track decision rationale
└── Issue Enrichment
    ├── Find related issues
    ├── Extract issue context
    └── Link to commits
```

**API Rate Limiting Strategy:**
```python
class GitHubAPIClient:
    def _check_rate_limit(self):
        if self.rate_limit_remaining < 10:
            wait_time = self.rate_limit_reset - time.time()
            if wait_time > 0:
                time.sleep(wait_time + 1)

    def _make_request(self, endpoint):
        self._check_rate_limit()
        response = requests.get(endpoint)
        self.rate_limit_remaining = response.headers['X-RateLimit-Remaining']
        return response.json()
```

**Enrichment Algorithm:**
```python
def enrich_commit(commit):
    # Step 1: Find PR number
    pr_number = extract_pr_from_message(commit.message)
    if not pr_number:
        pr_number = search_pr_by_commit(commit.sha)

    # Step 2: Fetch PR data
    pr = fetch_pull_request(pr_number)

    # Step 3: Find related issues
    issue_numbers = extract_issue_numbers(commit.message)
    issues = [fetch_issue(n) for n in issue_numbers]

    return EnrichedCommit(commit, pr, issues)
```

**Performance:**
- API calls: 3 per PR, 2 per issue
- Rate limits: 60/hour (no token), 5000/hour (with token)
- Automatic backoff when limit < 10

### 3. Context Synthesizer (ContextSynthesizer)

**Responsibility**: Semantic search and answer generation

**Architecture:**
```
ContextSynthesizer
├── Embedding Provider (pluggable)
│   ├── SimpleEmbeddingProvider (TF-IDF, default)
│   ├── ClaudeEmbeddingProvider (future)
│   └── OpenAIEmbeddingProvider (future)
├── Index Builder
│   ├── Document extraction (commits, PRs, issues)
│   ├── Embedding generation
│   └── FAISS index (optional)
├── Semantic Search
│   ├── Query embedding
│   ├── Similarity computation (cosine/L2)
│   └── Result ranking
└── Answer Generator
    ├── Context extraction
    ├── Answer synthesis
    ├── Citation tracking
    └── Confidence scoring
```

**Document Extraction:**
```python
def _extract_documents(enriched_history):
    documents = []
    metadata = []

    for enriched_commit in enriched_history:
        # Document 1: Commit message
        doc = f"{commit.message}\n\n{commit.author}\n{commit.date}"
        documents.append(doc)
        metadata.append({'type': 'commit', 'commit': enriched_commit})

        # Document 2: PR discussion
        if enriched_commit.pull_request:
            pr_doc = f"{pr.title}\n\n{pr.body}\n\n{pr.discussion_summary}"
            documents.append(pr_doc)
            metadata.append({'type': 'pr', 'commit': enriched_commit})

        # Document 3: Issues
        for issue in enriched_commit.related_issues:
            issue_doc = f"{issue.title}\n\n{issue.body}"
            documents.append(issue_doc)
            metadata.append({'type': 'issue', 'commit': enriched_commit})

    return documents, metadata
```

**Semantic Search Algorithm:**
```python
def search(index, query, k=10):
    # Embed query
    query_embedding = index.embedding_provider.embed([query])[0]

    if index.faiss_index:
        # FAISS search (fast)
        distances, indices = index.faiss_index.search(query_embedding, k)
        results = [
            SearchResult(
                commit=index.metadata[idx]['commit'],
                relevance=1.0 / (1.0 + dist),
                content=index.documents[idx]
            )
            for dist, idx in zip(distances, indices)
        ]
    else:
        # Cosine similarity (fallback)
        similarities = []
        for doc_emb in index.embeddings:
            sim = cosine_similarity(query_embedding, doc_emb)
            similarities.append(sim)

        top_indices = argsort(similarities)[-k:]
        results = [
            SearchResult(
                commit=index.metadata[idx]['commit'],
                relevance=similarities[idx],
                content=index.documents[idx]
            )
            for idx in top_indices
        ]

    return sorted(results, key=lambda r: r.relevance, reverse=True)
```

**Confidence Scoring:**
```python
def _calculate_confidence(results):
    if not results:
        return 0.0

    # Average relevance of top 3 results
    top_scores = [r.relevance_score for r in results[:3]]
    avg_score = sum(top_scores) / len(top_scores)

    # Boost if multiple high-quality results
    if len(results) >= 3 and avg_score > 0.7:
        return min(1.0, avg_score + 0.1)

    return avg_score
```

**Performance:**
- Index build: O(n × d) where n = docs, d = embedding dim
- Search (TF-IDF): O(n × d) per query
- Search (FAISS): O(log n × d) per query
- Memory: ~5MB per 100 documents

### 4. Query CLI (ArchaeologyCLI)

**Responsibility**: User interface (interactive and single-query)

**Architecture:**
```
ArchaeologyCLI
├── Interactive Mode (REPL)
│   ├── Command parser
│   ├── Query executor
│   ├── Result formatter
│   └── History manager
├── Single Query Mode
│   ├── One-shot query
│   └── Export to markdown
└── Rich Formatting (optional)
    ├── Colored output
    ├── Progress spinners
    └── Tables and panels
```

**State Management:**
```python
class ArchaeologyCLI:
    def __init__(self, repo_path, github_repo=None):
        self.repo_path = repo_path
        self.github_repo = github_repo
        self.index = None  # Lazy initialization
        self.history = []  # Query history
        self.analytics = CCAAnalytics()

    def initialize(self):
        # Build index once
        self.index = self._build_index()

    def query(self, question):
        # Reuse index
        answer = synthesize_answer(self.index, question)
        self.history.append(answer)
        return answer
```

---

## Data Flow

### Analysis Flow (One-Time Setup)

```
Repository    ──1──▶  Git Analyzer
    │                      │
    │                      │ Extract commits
    │                      │ Detect patterns
    │                      │ Build indexes
    │                      ▼
    │               RepositoryHistory
    │                      │
    │                      │
    ▼                      ▼
GitHub API  ──2──▶  GitHub Integrator
                           │
                           │ Link PRs
                           │ Extract discussions
                           │ Find issues
                           ▼
                    EnrichedHistory
                           │
                           │
                           ▼
                    Context Synthesizer
                           │
                           │ Extract documents
                           │ Generate embeddings
                           │ Build FAISS index
                           ▼
                    SearchableIndex
                    (Cached in memory)
```

### Query Flow (Interactive)

```
User Question
    │
    │ "Why was X refactored?"
    ▼
Query Parser
    │
    │ Parse and normalize
    ▼
Semantic Search
    │
    │ 1. Embed query (TF-IDF/FAISS)
    │ 2. Compute similarity
    │ 3. Rank results
    ▼
Top K Documents
    │
    │ [commit1, PR2, issue3, ...]
    ▼
Answer Generator
    │
    │ 1. Extract context from top results
    │ 2. Synthesize coherent answer
    │ 3. Extract citations
    │ 4. Calculate confidence
    ▼
Answer Object
    │
    │ - answer: str
    │ - confidence: float
    │ - citations: List[Citation]
    ▼
Formatter
    │
    │ Format for display (rich/plain)
    ▼
User
```

---

## Integration with CCA

### CCA (ClaudeAgents) Architecture

AIL is a foundational layer that all agents can leverage:

```
┌─────────────────────────────────────────────────────────────┐
│                    ClaudeAgents (CCA)                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Agent 1   │  │    Agent 2   │  │    Agent 3   │     │
│  │code-architect│  │  security-   │  │  technical-  │     │
│  │              │  │   auditor    │  │   writer     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                           ▼                                │
│         ┌─────────────────────────────────┐               │
│         │ Archaeological Intelligence Layer│               │
│         │         (AIL Sprint 1)           │               │
│         └─────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Integration Points

**1. Direct API Usage:**
```python
from tools.code_archaeology import GitArchaeologist, ContextSynthesizer

class CodeArchitect:
    def review_with_context(self, component):
        # Get historical context
        archaeologist = GitArchaeologist(".")
        history = archaeologist.analyze_repo()

        # Query AIL
        synthesizer = ContextSynthesizer()
        index = synthesizer.build_searchable_index(enriched_history)
        context = synthesizer.synthesize_answer(
            index,
            f"What were the design decisions for {component}?"
        )

        # Use context in review
        return f"Historical context:\n{context.answer}\n\nCurrent review:\n..."
```

**2. Shared Cache (Singleton Pattern):**
```python
class ArchaeologyCache:
    _index = None

    @classmethod
    def get_index(cls, repo_path):
        if cls._index is None:
            cls._index = build_index(repo_path)
        return cls._index

# All agents share the same index
class Agent1:
    def get_context(self, question):
        index = ArchaeologyCache.get_index(".")
        return query(index, question)

class Agent2:
    def get_context(self, question):
        index = ArchaeologyCache.get_index(".")  # Reuses cache
        return query(index, question)
```

**3. Agent Coordination Protocol (ACP):**
```json
{
  "cmd": "GET_ARCHAEOLOGICAL_CONTEXT",
  "query": "Why was authentication refactored?",
  "options": {
    "github_enrichment": true,
    "max_citations": 5
  },
  "respond_format": "STRUCTURED_JSON"
}
```

Response:
```json
{
  "answer": "Authentication was refactored to address...",
  "confidence": 0.85,
  "credibility": 0.92,
  "citations": [
    {
      "commit_sha": "a3f2c1d",
      "commit_message": "Migrate to Auth0 JWT library",
      "relevance": 0.95
    }
  ]
}
```

---

## Caching Strategy

### Multi-Level Caching

```
┌─────────────────────────────────────────────────────────────┐
│                     Cache Hierarchy                         │
│                                                             │
│  Level 1: Query Result Cache (Future)                      │
│  ┌───────────────────────────────────────────────────┐     │
│  │ LRU cache of (question → answer)                 │     │
│  │ Invalidation: Manual or time-based               │     │
│  └───────────────────────────────────────────────────┘     │
│                           │                                │
│                           ▼                                │
│  Level 2: Index Cache (In-Memory)                          │
│  ┌───────────────────────────────────────────────────┐     │
│  │ SearchableIndex singleton                        │     │
│  │ Invalidation: On new commits (future)            │     │
│  └───────────────────────────────────────────────────┘     │
│                           │                                │
│                           ▼                                │
│  Level 3: Analysis Cache (Disk - Future)                   │
│  ┌───────────────────────────────────────────────────┐     │
│  │ Serialized RepositoryHistory                     │     │
│  │ Invalidation: On git HEAD change                 │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Current Implementation (Sprint 1)

**In-Memory Index Cache:**
```python
class ArchaeologyCLI:
    def __init__(self):
        self.index = None  # Cache

    def query(self, question):
        if self.index is None:
            self.index = build_index()  # Build once
        return synthesize_answer(self.index, question)  # Reuse
```

**Benefits:**
- First query: ~5-10 seconds (builds index)
- Subsequent queries: <1 second (uses cache)
- Memory: ~5-10MB for typical repos

### Future Enhancements (Post-Sprint 1)

**1. Query Result Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_context(question: str) -> str:
    # Cache identical questions
    return synthesize_answer(index, question).answer
```

**2. Disk-Based Index Cache:**
```python
def load_or_build_index(repo_path):
    cache_file = f".archaeology/{git_head_sha}.pkl"

    if os.path.exists(cache_file):
        # Load from cache
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    else:
        # Build and save
        index = build_index(repo_path)
        with open(cache_file, 'wb') as f:
            pickle.dump(index, f)
        return index
```

**3. Incremental Updates:**
```python
def update_index(existing_index, new_commits):
    # Only process new commits since last analysis
    new_docs = extract_documents(new_commits)
    new_embeddings = embed(new_docs)

    # Update FAISS index
    existing_index.faiss_index.add(new_embeddings)
    existing_index.documents.extend(new_docs)

    return existing_index
```

---

## Performance Characteristics

### Benchmarks (Sprint 1)

**Test Repository: ClaudeAgents**
- Total commits: 216
- Architecturally significant: 147 (68%)
- Files tracked: 583
- Days indexed: 11

**Performance Results:**

| Operation | Time | Throughput | Memory |
|-----------|------|------------|--------|
| Git analysis | 5.64s | 38 commits/sec | <100MB |
| GitHub enrichment (50 commits) | 30s | ~1.7 commits/sec | <50MB |
| Index building (219 docs) | 1.2s | 182 docs/sec | ~10MB |
| Query (TF-IDF) | 0.05s | - | Negligible |
| Query (FAISS) | 0.01s | - | Negligible |

**Scaling Projections:**

| Repo Size | Git Analysis | Index Build | Query Time | Memory |
|-----------|--------------|-------------|------------|--------|
| 100 commits | ~2s | ~0.5s | <0.1s | ~50MB |
| 500 commits | ~10s | ~2s | <0.2s | ~150MB |
| 1,000 commits | ~20s | ~5s | <0.3s | ~300MB |
| 5,000 commits | ~90s | ~25s | <0.5s | ~1GB |
| 10,000 commits | ~3min | ~50s | <0.5s (FAISS) | ~2GB |

### Optimization Strategies

**1. Limit Analysis Scope:**
```python
# Analyze only recent commits
history = archaeologist.analyze_repo(limit=1000)

# Analyze specific time period
recent_commits = [c for c in history.commits if c.date > cutoff_date]
```

**2. Use FAISS for Large Repos:**
```bash
pip install faiss-cpu
```
```python
# FAISS provides 10x speedup for 10,000+ documents
synthesizer = ContextSynthesizer()
index = synthesizer.build_searchable_index(enriched)
# Automatically uses FAISS if available
```

**3. Parallel Processing (Future):**
```python
# Process commits in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(analyze_commit, c) for c in commits]
    arch_commits = [f.result() for f in futures]
```

**4. Incremental Analysis (Future):**
```python
# Only analyze new commits since last run
last_sha = load_last_analyzed_sha()
new_commits = get_commits_since(last_sha)
updated_index = update_index(existing_index, new_commits)
```

---

## Security Model

### Threat Model

**Assets:**
1. Source code (in git repository)
2. GitHub API token
3. PR/issue discussions (may contain sensitive info)
4. User queries (may reveal business logic)

**Threats:**
1. Code exfiltration to external servers
2. Token leakage
3. Unauthorized API access
4. Data injection attacks

### Security Measures

**1. Local-Only Processing:**
- ✅ All git analysis runs locally via git CLI
- ✅ No code is sent to external servers
- ✅ Embeddings generated locally (TF-IDF)
- ✅ Search executed locally (FAISS)

**2. GitHub Token Protection:**
- ✅ Token stored as environment variable (not in code)
- ✅ Token never logged or printed
- ✅ Token only used for GitHub API calls (HTTPS)
- ✅ User controls token scope (read-only recommended)

**3. Input Validation:**
```python
def safe_git_command(repo_path, args):
    # Validate repo path
    repo = Path(repo_path).resolve()
    if not (repo / '.git').exists():
        raise ValueError("Not a git repository")

    # Sanitize git args (no shell injection)
    result = subprocess.run(
        ['git', '-C', str(repo)] + args,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout
```

**4. API Rate Limiting:**
```python
class GitHubAPIClient:
    def _check_rate_limit(self):
        # Automatic backoff prevents abuse
        if self.rate_limit_remaining < 10:
            wait_time = self.rate_limit_reset - time.time()
            time.sleep(wait_time + 1)
```

**5. Privacy Controls:**
- ✅ GitHub enrichment is opt-in (requires explicit `--github` flag)
- ✅ Users control which repos are analyzed
- ✅ No telemetry or usage tracking
- ✅ All data stays local

### Compliance

**GDPR:**
- All processing is local (data controller = user)
- No data transferred to third parties
- GitHub API only accesses data user has permission to view

**SOC 2 / ISO 27001:**
- No external API calls for core functionality
- Audit trail via git commits (immutable)
- Access control via GitHub token permissions

---

## Scalability

### Current Limits (Sprint 1)

| Metric | Limit | Reason |
|--------|-------|--------|
| Max commits | ~10,000 | Memory constraints with TF-IDF |
| Max documents | ~50,000 | Embedding generation time |
| Query throughput | ~20 queries/sec | Single-threaded search |
| Index size | ~500MB | In-memory storage |

### Scaling Strategies

**1. Horizontal Scaling (Future):**
```
┌──────────────┐
│  Load        │
│  Balancer    │
└──────┬───────┘
       │
       ├────────▶ ┌────────────┐
       │          │  Worker 1  │ (repo A)
       │          └────────────┘
       │
       ├────────▶ ┌────────────┐
       │          │  Worker 2  │ (repo B)
       │          └────────────┘
       │
       └────────▶ ┌────────────┐
                  │  Worker 3  │ (repo C)
                  └────────────┘
```

**2. Sharding (Future):**
```python
# Shard by date range
shard_2024_q1 = build_index(commits_2024_q1)
shard_2024_q2 = build_index(commits_2024_q2)

# Query all shards and merge results
results = []
for shard in shards:
    results.extend(search(shard, query))
return merge_and_rank(results)
```

**3. External Vector Store (Future):**
```
┌──────────────┐
│  AIL Service │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Vector Database │
│  (Pinecone/      │
│   Weaviate/      │
│   Qdrant)        │
└──────────────────┘
```

**4. Distributed FAISS (Future):**
```python
# Use distributed FAISS for massive scale
import faiss

# Build index with IVF (Inverted File Index)
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)
index.train(embeddings)
index.add(embeddings)

# Query with nprobe for speed/accuracy tradeoff
index.nprobe = 10
distances, indices = index.search(query_embedding, k)
```

---

## Future Roadmap

### Sprint 2: Performance & Scale (Q1 2026)

**Goals:**
- Support 100,000+ commit repositories
- Sub-100ms query latency
- Incremental index updates

**Features:**
- [ ] FAISS optimization for large-scale search
- [ ] Incremental analysis (only new commits)
- [ ] Disk-based index caching
- [ ] Parallel commit processing
- [ ] Query result caching (LRU)

### Sprint 3: Advanced Context (Q2 2026)

**Goals:**
- Richer context from additional sources
- Better answer quality

**Features:**
- [ ] Slack integration (channel history)
- [ ] JIRA integration (ticket context)
- [ ] Code comment extraction (inline docs)
- [ ] CI/CD log analysis (build/deploy context)
- [ ] Custom LLM provider support (Claude, GPT-4)

### Sprint 4: Multi-Repo & Collaboration (Q3 2026)

**Goals:**
- Cross-repository analysis
- Team collaboration features

**Features:**
- [ ] Multi-repo indexing (monorepo support)
- [ ] Shared index across team
- [ ] Real-time index updates (git hooks)
- [ ] Collaborative annotations
- [ ] Knowledge graph visualization

### Sprint 5: Intelligence Layer (Q4 2026)

**Goals:**
- Proactive insights
- Automated documentation

**Features:**
- [ ] Automatic decision documentation
- [ ] Technical debt detection
- [ ] Pattern recognition (anti-patterns)
- [ ] Architecture drift detection
- [ ] Automated changelog generation

---

## Technical Decisions

### Design Decisions & Rationale

**1. TF-IDF vs Neural Embeddings**

**Decision:** Use TF-IDF by default, optional FAISS

**Rationale:**
- ✅ No external dependencies (works offline)
- ✅ Deterministic results (reproducible)
- ✅ Fast for <10,000 documents
- ✅ Low memory footprint
- ⚠ Less semantic understanding than neural embeddings

**Future:** Add neural embedding support (Claude, OpenAI) as optional enhancement

**2. Local Processing vs Cloud API**

**Decision:** 100% local processing for core features

**Rationale:**
- ✅ Privacy (code never leaves machine)
- ✅ No API costs
- ✅ Works offline
- ✅ Faster (no network latency)
- ⚠ Limited by local compute

**Future:** Optional cloud acceleration for large-scale analysis

**3. Python vs Other Languages**

**Decision:** Python for all components

**Rationale:**
- ✅ Existing ClaudeAgents ecosystem is Python
- ✅ Rich ecosystem (Git, NLP, FAISS)
- ✅ Rapid development
- ✅ Easy agent integration
- ⚠ Performance (but acceptable for MVP)

**Future:** Rust bindings for performance-critical paths

**4. Git CLI vs libgit2**

**Decision:** Use Git CLI via subprocess

**Rationale:**
- ✅ No external dependencies (git already installed)
- ✅ Stable API (git CLI)
- ✅ Simple implementation
- ⚠ Slower than libgit2
- ⚠ Requires git in PATH

**Future:** Optional libgit2 (pygit2) for performance

---

## See Also

- **[AIL API Reference](AIL_API.md)**: Complete API documentation
- **[AIL Integration Guide](AIL_INTEGRATION_GUIDE.md)**: How to integrate AIL into agents
- **[AIL User Guide](AIL_USER_GUIDE.md)**: User-facing documentation
- **[Cognitive Code Archaeology README](../tools/code_archaeology/README.md)**: Implementation details
- **[CCA Analytics](CCA_ANALYTICS.md)**: Analytics and metrics
- **[CCA Case Studies](CCA_CASE_STUDIES.md)**: Real-world usage examples

---

**Last Updated:** 2025-10-08
**Version:** 1.0.0
**Sprint:** 1 (Foundation) Complete
**Status:** Production Ready
