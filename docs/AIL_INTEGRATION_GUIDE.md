# Archaeological Intelligence Layer (AIL) - Integration Guide

**Version:** 1.0.0
**Audience:** Agent Developers
**Last Updated:** 2025-10-08

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Integration Patterns](#integration-patterns)
4. [Agent Integration Examples](#agent-integration-examples)
5. [Best Practices](#best-practices)
6. [Performance Optimization](#performance-optimization)
7. [Common Pitfalls](#common-pitfalls)
8. [Testing Your Integration](#testing-your-integration)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Archaeological Intelligence Layer (AIL) provides agents with deep historical context about code decisions. This guide shows you how to integrate AIL into your agent's workflow.

### What AIL Provides

- **Historical Context**: Answer "why" questions about code decisions
- **Multi-Source Analysis**: Git commits + GitHub PRs + issue discussions
- **Semantic Search**: Natural language queries across repository history
- **Citations**: Every answer includes source references
- **Confidence Scoring**: Understand answer reliability

### When to Use AIL

| Agent Type | Use Case | Example |
|------------|----------|---------|
| `code-architect` | Review architectural decisions | "Why was this pattern chosen?" |
| `security-audit-specialist` | Investigate security fixes | "What vulnerability did this fix?" |
| `legacy-specialist` | Understand legacy code | "Why was this workaround needed?" |
| `technical-writer` | Document historical decisions | "What led to this design?" |
| `qa-test-engineer` | Find context for tests | "What bug did this test prevent?" |

---

## Quick Start

### Step 1: Install Dependencies

```bash
# Core dependencies (already in project)
# No additional installation needed

# Optional: For large repositories (10,000+ commits)
pip install faiss-cpu

# Optional: For GitHub enrichment
export GITHUB_TOKEN="your_github_personal_access_token"
```

### Step 2: Basic Integration

```python
from tools.code_archaeology import (
    GitArchaeologist,
    ContextSynthesizer,
)

def get_code_context(repo_path: str, question: str) -> str:
    """
    Get historical context for a question.

    Args:
        repo_path: Path to git repository
        question: Natural language question

    Returns:
        Answer text with citations
    """
    # Analyze repository
    archaeologist = GitArchaeologist(repo_path)
    history = archaeologist.analyze_repo()

    # Build search index (git-only, no GitHub)
    from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory
    enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
    enriched = EnrichedHistory(
        base_history=history,
        enriched_commits=enriched_commits,
        pull_requests={},
        issues={},
        commit_to_pr={},
    )

    # Query
    synthesizer = ContextSynthesizer()
    index = synthesizer.build_searchable_index(enriched)
    answer = synthesizer.synthesize_answer(index, question)

    # Format response
    response = f"{answer.answer}\n\n"
    response += f"Confidence: {answer.confidence:.0%}, "
    response += f"Credibility: {answer.credibility_score:.0%}\n\n"
    response += "Citations:\n"
    for i, citation in enumerate(answer.citations[:3], 1):
        response += f"{i}. {citation.commit_sha[:8]} - {citation.commit_message}\n"

    return response

# Usage
context = get_code_context(".", "Why was authentication refactored?")
print(context)
```

### Step 3: Add to Your Agent

```python
class MyAgent:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.archaeology_cache = None  # Cache for performance

    def get_historical_context(self, question: str) -> str:
        """Get archaeological context for question."""
        if not self.archaeology_cache:
            # Initialize on first use
            self.archaeology_cache = self._build_archaeology_index()

        synthesizer = ContextSynthesizer()
        answer = synthesizer.synthesize_answer(
            self.archaeology_cache,
            question
        )
        return answer.answer

    def _build_archaeology_index(self):
        """Build and cache archaeology index."""
        from tools.code_archaeology import GitArchaeologist, ContextSynthesizer
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

        archaeologist = GitArchaeologist(self.repo_path)
        history = archaeologist.analyze_repo()

        # Create minimal enriched history
        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={},
            issues={},
            commit_to_pr={},
        )

        synthesizer = ContextSynthesizer()
        return synthesizer.build_searchable_index(enriched)

    def analyze_code(self, code: str):
        """Example: Analyze code with historical context."""
        # Ask relevant questions
        context = self.get_historical_context(
            f"What were the design decisions for this component?"
        )

        # Use context in your analysis
        return f"Analysis incorporating historical context:\n{context}"
```

---

## Integration Patterns

### Pattern 1: On-Demand Context (Simple)

Best for: Infrequent queries, small repositories (<1000 commits)

```python
def get_context_simple(question: str) -> str:
    """Simple one-shot context retrieval."""
    from tools.code_archaeology import GitArchaeologist, ContextSynthesizer
    from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

    # Analyze
    archaeologist = GitArchaeologist(".")
    history = archaeologist.analyze_repo()

    # Index
    enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
    enriched = EnrichedHistory(
        base_history=history,
        enriched_commits=enriched_commits,
        pull_requests={}, issues={}, commit_to_pr={}
    )

    synthesizer = ContextSynthesizer()
    index = synthesizer.build_searchable_index(enriched)

    # Query
    answer = synthesizer.synthesize_answer(index, question)
    return answer.answer

# Usage
context = get_context_simple("Why was X refactored?")
```

**Pros:** Simple, no state management
**Cons:** Slow for repeated queries (~5-10 seconds per query)

### Pattern 2: Cached Index (Recommended)

Best for: Multiple queries, medium repositories (1000-10,000 commits)

```python
class ArchaeologyCache:
    """Singleton cache for archaeology index."""

    _instance = None
    _index = None
    _repo_path = None

    @classmethod
    def get_index(cls, repo_path: str):
        """Get or build cached index."""
        if cls._instance is None or cls._repo_path != repo_path:
            cls._instance = cls()
            cls._repo_path = repo_path
            cls._index = cls._build_index(repo_path)
        return cls._index

    @staticmethod
    def _build_index(repo_path: str):
        """Build archaeology index."""
        from tools.code_archaeology import GitArchaeologist, ContextSynthesizer
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

        print("Building archaeology index (one-time setup)...")

        archaeologist = GitArchaeologist(repo_path)
        history = archaeologist.analyze_repo()

        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={}, issues={}, commit_to_pr={}
        )

        synthesizer = ContextSynthesizer()
        index = synthesizer.build_searchable_index(enriched)

        print(f"✓ Index built: {index.size} documents")
        return index

# Usage in agent
class MyAgent:
    def get_context(self, question: str) -> str:
        """Get context with caching."""
        index = ArchaeologyCache.get_index(".")

        synthesizer = ContextSynthesizer()
        answer = synthesizer.synthesize_answer(index, question)

        return answer.answer

# First query: ~5 seconds (builds index)
# Subsequent queries: <1 second (uses cache)
```

**Pros:** Fast repeated queries, automatic caching
**Cons:** Memory usage (index stays in RAM)

### Pattern 3: GitHub-Enriched (Advanced)

Best for: High-value contexts, open-source projects with PR discussions

```python
def get_enriched_context(repo_path: str, github_repo: str, question: str) -> str:
    """Get context with GitHub PR/issue enrichment."""
    from tools.code_archaeology import (
        GitArchaeologist,
        GitHubArchaeologist,
        ContextSynthesizer
    )

    # Step 1: Analyze git history
    git_arch = GitArchaeologist(repo_path)
    history = git_arch.analyze_repo()

    # Step 2: Enrich with GitHub (requires GITHUB_TOKEN)
    try:
        owner, repo = github_repo.split('/')
        gh_arch = GitHubArchaeologist(owner, repo)
        enriched = gh_arch.enrich_history(history, limit=100)  # Limit for speed
        print(f"GitHub enrichment: {enriched.enrichment_rate:.1%}")
    except Exception as e:
        print(f"GitHub enrichment failed: {e}, using git-only")
        # Fall back to git-only
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory
        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={}, issues={}, commit_to_pr={}
        )

    # Step 3: Build index and query
    synthesizer = ContextSynthesizer()
    index = synthesizer.build_searchable_index(enriched)
    answer = synthesizer.synthesize_answer(index, question)

    return answer.answer

# Usage
context = get_enriched_context(
    ".",
    "anthropics/claude-code",
    "Why was the API redesigned?"
)
```

**Pros:** Richest context with PR discussions
**Cons:** Requires GitHub token, slower (API rate limits)

### Pattern 4: Pre-Computed Index (Production)

Best for: Large repositories, production deployments, CI/CD

```python
# Step 1: Build index offline (CI/CD job)
def build_and_save_index(repo_path: str, output_dir: str):
    """Build index and save to disk."""
    from tools.code_archaeology import GitArchaeologist, ContextSynthesizer
    from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory
    import pickle
    from pathlib import Path

    # Analyze
    archaeologist = GitArchaeologist(repo_path)
    history = archaeologist.analyze_repo()

    # Create index
    enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
    enriched = EnrichedHistory(
        base_history=history,
        enriched_commits=enriched_commits,
        pull_requests={}, issues={}, commit_to_pr={}
    )

    synthesizer = ContextSynthesizer()
    index = synthesizer.build_searchable_index(enriched)

    # Save to disk
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / 'index.pkl', 'wb') as f:
        pickle.dump(index, f)

    print(f"Index saved to {output_path}")

# Step 2: Load index at runtime
def load_index(index_dir: str):
    """Load pre-built index from disk."""
    from pathlib import Path
    import pickle

    with open(Path(index_dir) / 'index.pkl', 'rb') as f:
        return pickle.load(f)

# Usage in agent
class MyAgent:
    def __init__(self, index_dir: str = ".archaeology_cache"):
        self.index = load_index(index_dir)

    def get_context(self, question: str) -> str:
        synthesizer = ContextSynthesizer()
        answer = synthesizer.synthesize_answer(self.index, question)
        return answer.answer

# CI/CD: build_and_save_index(".", ".archaeology_cache")
# Runtime: agent = MyAgent(".archaeology_cache")
```

**Pros:** Instant startup, no runtime indexing
**Cons:** Requires pre-computation, index can become stale

---

## Agent Integration Examples

### Example 1: code-architect Integration

```python
class CodeArchitect:
    """Enhanced code architect with archaeological context."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._archaeology_index = None

    def review_architecture(self, component: str) -> str:
        """Review architecture with historical context."""

        # Get archaeological context
        context = self._get_context(
            f"What were the key architectural decisions for {component}?"
        )

        # Perform review with context
        review = f"Architecture Review: {component}\n\n"
        review += "Historical Context:\n"
        review += context + "\n\n"
        review += "Current Analysis:\n"
        review += self._analyze_current_state(component)

        return review

    def _get_context(self, question: str) -> str:
        """Get archaeological context (cached)."""
        if self._archaeology_index is None:
            self._archaeology_index = self._build_index()

        from tools.code_archaeology import ContextSynthesizer
        synthesizer = ContextSynthesizer()
        answer = synthesizer.synthesize_answer(self._archaeology_index, question)

        result = answer.answer + "\n\n"
        if answer.citations:
            result += "Key commits:\n"
            for citation in answer.citations[:3]:
                result += f"  - {citation.commit_sha[:8]}: {citation.commit_message}\n"

        return result

    def _build_index(self):
        """Build archaeology index."""
        from tools.code_archaeology import GitArchaeologist, ContextSynthesizer
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

        archaeologist = GitArchaeologist(self.repo_path)
        history = archaeologist.analyze_repo()

        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={}, issues={}, commit_to_pr={}
        )

        synthesizer = ContextSynthesizer()
        return synthesizer.build_searchable_index(enriched)

    def _analyze_current_state(self, component: str) -> str:
        """Analyze current state (placeholder)."""
        return "Current analysis of " + component
```

### Example 2: security-audit-specialist Integration

```python
class SecurityAuditor:
    """Security auditor with security fix history."""

    def audit_with_history(self, file_path: str) -> str:
        """Audit file with security fix history."""
        from tools.code_archaeology import GitArchaeologist

        # Analyze repository
        archaeologist = GitArchaeologist(".")
        history = archaeologist.analyze_repo()

        # Find security-related commits for this file
        security_commits = []
        if file_path in history.file_history:
            for commit in history.file_history[file_path]:
                if self._is_security_commit(commit.message):
                    security_commits.append(commit)

        # Build report
        report = f"Security Audit: {file_path}\n\n"

        if security_commits:
            report += "Historical Security Fixes:\n"
            for commit in security_commits[:5]:
                report += f"  - {commit.date.date()}: {commit.summary}\n"
            report += "\n"

        # Get context on patterns
        if security_commits:
            context = self._get_context(
                f"What security vulnerabilities were fixed in {file_path}?"
            )
            report += "Security Pattern Analysis:\n"
            report += context + "\n\n"

        # Current audit
        report += "Current Security Analysis:\n"
        report += self._audit_current_code(file_path)

        return report

    def _is_security_commit(self, message: str) -> bool:
        """Check if commit is security-related."""
        keywords = ['security', 'vulnerability', 'CVE', 'exploit', 'XSS', 'SQL injection']
        return any(keyword.lower() in message.lower() for keyword in keywords)

    def _get_context(self, question: str) -> str:
        """Get archaeological context."""
        # Implementation similar to CodeArchitect example
        pass

    def _audit_current_code(self, file_path: str) -> str:
        """Audit current code (placeholder)."""
        return "Current security analysis"
```

### Example 3: technical-writer Integration

```python
class TechnicalWriter:
    """Technical writer with automatic context extraction."""

    def document_component(self, component: str, github_repo: str = None) -> str:
        """Generate documentation with historical context."""
        from tools.code_archaeology import (
            GitArchaeologist,
            GitHubArchaeologist,
            ContextSynthesizer
        )

        # Analyze
        git_arch = GitArchaeologist(".")
        history = git_arch.analyze_repo()

        # Optionally enrich with GitHub
        if github_repo:
            try:
                owner, repo = github_repo.split('/')
                gh_arch = GitHubArchaeologist(owner, repo)
                enriched = gh_arch.enrich_history(history, limit=50)
            except:
                enriched = self._create_basic_enriched(history)
        else:
            enriched = self._create_basic_enriched(history)

        # Build index
        synthesizer = ContextSynthesizer()
        index = synthesizer.build_searchable_index(enriched)

        # Ask multiple questions
        questions = [
            f"What is the purpose of {component}?",
            f"What were the key design decisions for {component}?",
            f"What problems does {component} solve?",
            f"How has {component} evolved over time?"
        ]

        # Generate documentation
        doc = f"# {component} Documentation\n\n"
        doc += "## Overview\n\n"

        for question in questions:
            answer = synthesizer.synthesize_answer(index, question, max_results=5)
            if answer.confidence > 0.3:  # Only include confident answers
                doc += f"### {question}\n\n"
                doc += answer.answer + "\n\n"

                if answer.citations:
                    doc += "**References:**\n"
                    for citation in answer.citations[:3]:
                        doc += f"- {citation.commit_date.date()}: {citation.commit_message}\n"
                    doc += "\n"

        return doc

    def _create_basic_enriched(self, history):
        """Create basic enriched history."""
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        return EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={}, issues={}, commit_to_pr={}
        )
```

---

## Best Practices

### 1. Cache the Index

**Do:**
```python
class MyAgent:
    def __init__(self):
        self._index = None  # Build once, reuse

    def get_context(self, question):
        if self._index is None:
            self._index = self._build_index()
        # Use cached index
```

**Don't:**
```python
def get_context(question):
    # Rebuilds index every query (slow!)
    index = build_index()
    return query(index, question)
```

### 2. Limit Scope for Performance

**Do:**
```python
# Limit commits analyzed
history = archaeologist.analyze_repo(limit=500)

# Limit GitHub enrichment
enriched = gh_arch.enrich_history(history, limit=100)

# Limit search results
answer = synthesizer.synthesize_answer(index, question, max_results=5)
```

**Don't:**
```python
# Analyze entire 50,000 commit history (slow!)
history = archaeologist.analyze_repo()  # No limit
```

### 3. Handle Errors Gracefully

**Do:**
```python
try:
    gh_arch = GitHubArchaeologist(owner, repo)
    enriched = gh_arch.enrich_history(history)
except Exception as e:
    print(f"GitHub enrichment failed: {e}, using git-only")
    # Fall back to git-only analysis
    enriched = create_basic_enriched(history)
```

**Don't:**
```python
# Fails completely if GitHub unavailable
gh_arch = GitHubArchaeologist(owner, repo)
enriched = gh_arch.enrich_history(history)  # No error handling
```

### 4. Use Appropriate Context Window

**Do:**
```python
# Ask focused questions
context = get_context("Why was authentication refactored in Q2 2024?")

# Use path filtering for specific components
history = archaeologist.analyze_repo()
auth_commits = [c for c in history.commits if any('auth' in f for f in c.files_changed)]
```

**Don't:**
```python
# Too broad, low-quality results
context = get_context("Tell me everything about the codebase")
```

### 5. Validate Answer Quality

**Do:**
```python
answer = synthesizer.synthesize_answer(index, question)

if answer.confidence < 0.5:
    # Low confidence, be cautious
    return f"Limited historical context available. {answer.answer}"
elif answer.confidence >= 0.8:
    # High confidence
    return answer.answer
else:
    # Medium confidence
    return f"Based on available history: {answer.answer}"
```

**Don't:**
```python
# Blindly trust all answers
answer = synthesizer.synthesize_answer(index, question)
return answer.answer  # No confidence check
```

### 6. Provide Citations

**Do:**
```python
response = answer.answer + "\n\nSources:\n"
for citation in answer.citations[:3]:
    response += f"- {citation.commit_sha[:8]}: {citation.commit_message}\n"
```

**Don't:**
```python
# No attribution, users can't verify
response = answer.answer
```

---

## Performance Optimization

### Optimization 1: Pre-warm Cache

```python
# In agent initialization
class MyAgent:
    def __init__(self, repo_path: str, preload: bool = True):
        self.repo_path = repo_path
        self._index = None

        if preload:
            # Build index during initialization (parallel to other setup)
            self._index = self._build_index()

    def _build_index(self):
        # Build and cache index
        pass
```

### Optimization 2: Incremental Updates (Future)

```python
# Future feature: Only analyze new commits
def update_index(existing_index, new_commits):
    """Update index with new commits only."""
    # Add embeddings for new commits
    # Update FAISS index
    # Return updated index
    pass
```

### Optimization 3: Query Result Caching

```python
from functools import lru_cache

class MyAgent:
    @lru_cache(maxsize=100)
    def get_context(self, question: str) -> str:
        """Cache query results."""
        # Identical questions return cached results
        index = self._get_index()
        synthesizer = ContextSynthesizer()
        answer = synthesizer.synthesize_answer(index, question)
        return answer.answer
```

### Optimization 4: Use FAISS for Large Repos

```bash
# Install FAISS for 10x faster search on large repos
pip install faiss-cpu
```

```python
# FAISS automatically used if available
synthesizer = ContextSynthesizer()
index = synthesizer.build_searchable_index(enriched)
# Uses FAISS if installed, falls back to TF-IDF otherwise
```

---

## Common Pitfalls

### Pitfall 1: Not Initializing Repository Check

**Problem:**
```python
archaeologist = GitArchaeologist("/tmp/not-a-repo")
# ValueError: Not a git repository
```

**Solution:**
```python
from pathlib import Path

def safe_init_archaeology(repo_path: str):
    repo = Path(repo_path)
    if not (repo / '.git').exists():
        raise ValueError(f"Not a git repository: {repo_path}")

    return GitArchaeologist(repo_path)
```

### Pitfall 2: GitHub Rate Limiting

**Problem:**
```python
# Enriches 1000 commits, hits rate limit quickly
enriched = gh_arch.enrich_history(history)  # No limit
```

**Solution:**
```python
# Limit enrichment to most recent commits
enriched = gh_arch.enrich_history(history, limit=100)

# Or use exponential backoff (built-in)
# GitHubArchaeologist automatically waits on rate limits
```

### Pitfall 3: Memory Issues with Large Repos

**Problem:**
```python
# Loads 50,000 commits into memory
history = archaeologist.analyze_repo()  # No limit
```

**Solution:**
```python
# Analyze recent history only
history = archaeologist.analyze_repo(limit=1000)

# Or use streaming (future feature)
```

### Pitfall 4: Ignoring Confidence Scores

**Problem:**
```python
answer = synthesizer.synthesize_answer(index, "Random question")
return answer.answer  # May be low quality
```

**Solution:**
```python
answer = synthesizer.synthesize_answer(index, question)

if answer.confidence < 0.3:
    return "Insufficient historical context to answer this question."

return f"{answer.answer}\n\n(Confidence: {answer.confidence:.0%})"
```

### Pitfall 5: Not Handling Missing GitHub Token

**Problem:**
```python
gh_arch = GitHubArchaeologist(owner, repo)  # No token
enriched = gh_arch.enrich_history(history)
# Fails with rate limit (60 requests/hour without token)
```

**Solution:**
```python
import os

if os.environ.get('GITHUB_TOKEN'):
    gh_arch = GitHubArchaeologist(owner, repo)
    enriched = gh_arch.enrich_history(history, limit=100)
else:
    print("Warning: GITHUB_TOKEN not set, using git-only analysis")
    enriched = create_basic_enriched(history)
```

---

## Testing Your Integration

### Unit Test Example

```python
import unittest
from tools.code_archaeology import GitArchaeologist

class TestArchaeologyIntegration(unittest.TestCase):

    def test_basic_analysis(self):
        """Test basic git analysis."""
        archaeologist = GitArchaeologist(".")
        history = archaeologist.analyze_repo(limit=10)

        self.assertIsNotNone(history)
        self.assertGreater(history.total_commits, 0)
        self.assertGreater(len(history.arch_commits), 0)

    def test_query_with_context(self):
        """Test querying with context."""
        from tools.code_archaeology import ContextSynthesizer
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

        # Analyze
        archaeologist = GitArchaeologist(".")
        history = archaeologist.analyze_repo(limit=50)

        # Create enriched history
        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={}, issues={}, commit_to_pr={}
        )

        # Query
        synthesizer = ContextSynthesizer()
        index = synthesizer.build_searchable_index(enriched)
        answer = synthesizer.synthesize_answer(index, "What is this repository?")

        self.assertIsNotNone(answer)
        self.assertGreater(len(answer.answer), 0)
        self.assertGreaterEqual(answer.confidence, 0.0)
        self.assertLessEqual(answer.confidence, 1.0)

    def test_caching_performance(self):
        """Test that caching improves performance."""
        import time

        # First query (builds index)
        start = time.time()
        context1 = self.get_cached_context("Question 1")
        time1 = time.time() - start

        # Second query (uses cache)
        start = time.time()
        context2 = self.get_cached_context("Question 2")
        time2 = time.time() - start

        # Second query should be much faster
        self.assertLess(time2, time1 * 0.1)  # 10x faster

    def get_cached_context(self, question):
        # Implementation with caching
        pass

if __name__ == '__main__':
    unittest.main()
```

### Integration Test Example

```python
def test_full_workflow():
    """Test complete archaeology workflow."""
    from tools.code_archaeology import (
        GitArchaeologist,
        GitHubArchaeologist,
        ContextSynthesizer
    )

    print("Testing full archaeology workflow...")

    # Step 1: Git analysis
    print("  1. Analyzing git history...")
    git_arch = GitArchaeologist(".")
    history = git_arch.analyze_repo(limit=100)
    assert history.total_commits > 0
    print(f"    ✓ Found {history.total_commits} commits")

    # Step 2: GitHub enrichment (optional)
    print("  2. Enriching with GitHub...")
    try:
        gh_arch = GitHubArchaeologist("owner", "repo")
        enriched = gh_arch.enrich_history(history, limit=10)
        print(f"    ✓ Enrichment rate: {enriched.enrichment_rate:.1%}")
    except Exception as e:
        print(f"    ⚠ GitHub enrichment failed: {e}")
        from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory
        enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
        enriched = EnrichedHistory(
            base_history=history,
            enriched_commits=enriched_commits,
            pull_requests={}, issues={}, commit_to_pr={}
        )

    # Step 3: Build index
    print("  3. Building search index...")
    synthesizer = ContextSynthesizer()
    index = synthesizer.build_searchable_index(enriched)
    assert index.size > 0
    print(f"    ✓ Indexed {index.size} documents")

    # Step 4: Query
    print("  4. Testing queries...")
    answer = synthesizer.synthesize_answer(index, "What is this repository?")
    assert len(answer.answer) > 0
    assert answer.confidence >= 0.0
    print(f"    ✓ Query completed (confidence: {answer.confidence:.0%})")

    print("✓ All tests passed!")

if __name__ == '__main__':
    test_full_workflow()
```

---

## Troubleshooting

### Issue: "Not a git repository"

**Symptom:**
```
ValueError: Not a git repository: /path/to/dir
```

**Solution:**
```python
# Verify git repository
import subprocess
result = subprocess.run(['git', 'status'], cwd=repo_path, capture_output=True)
if result.returncode != 0:
    print("Not a git repository")
```

### Issue: GitHub API Rate Limit

**Symptom:**
```
Exception: GitHub API rate limit exceeded
```

**Solution:**
```bash
# Set GitHub token
export GITHUB_TOKEN="your_github_personal_access_token"
```

Or limit enrichment:
```python
enriched = gh_arch.enrich_history(history, limit=50)
```

### Issue: Slow Query Performance

**Symptom:**
Queries take >5 seconds each

**Solution:**
```bash
# Install FAISS
pip install faiss-cpu
```

Or cache the index:
```python
# Build once, query many times
index = build_index()  # Once
answer1 = query(index, "Q1")  # Fast
answer2 = query(index, "Q2")  # Fast
```

### Issue: Low-Quality Answers

**Symptom:**
Answers are generic or irrelevant

**Solution:**
```python
# Check confidence score
answer = synthesizer.synthesize_answer(index, question)
if answer.confidence < 0.5:
    # Ask more specific question or increase max_results
    answer = synthesizer.synthesize_answer(index, question, max_results=20)
```

### Issue: Out of Memory

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Limit commits analyzed
history = archaeologist.analyze_repo(limit=1000)

# Or increase swap space (OS-level)
```

---

## See Also

- [AIL API Reference](AIL_API.md) - Complete API documentation
- [AIL User Guide](AIL_USER_GUIDE.md) - User-facing guide
- [AIL Architecture](AIL_ARCHITECTURE.md) - System design
- [Cognitive Code Archaeology Command](../commands/development/cognitive-archaeology.md) - CLI usage

---

**Last Updated:** 2025-10-08
**Version:** 1.0.0
**Status:** Production Ready
