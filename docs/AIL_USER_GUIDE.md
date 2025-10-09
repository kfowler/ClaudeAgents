# Archaeological Intelligence Layer (AIL) - User Guide

**Version:** 1.0.0
**Audience:** Developers using ClaudeAgents
**Last Updated:** 2025-10-08

---

## Table of Contents

1. [What is AIL?](#what-is-ail)
2. [Getting Started](#getting-started)
3. [How It Works](#how-it-works)
4. [Using AIL](#using-ail)
5. [Configuration](#configuration)
6. [Use Cases](#use-cases)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## What is AIL?

The **Archaeological Intelligence Layer (AIL)** is a breakthrough feature that gives AI agents the ability to understand the "why" behind your code decisions by analyzing your repository's complete history.

### The Problem

Traditional code analysis tools can tell you **what** your code does, but they can't answer:

- "Why was this approach chosen over alternatives?"
- "What problem was this solving?"
- "Who made this decision and what were their concerns?"
- "When was this workaround added and why?"

This context is often lost to:
- Team turnover
- Time passing
- Undocumented decisions
- Scattered knowledge across tools (Git, GitHub, Slack, JIRA)

### The Solution

AIL recovers lost context by:

1. **Analyzing Git History**: Extracts commits, diffs, and metadata
2. **Enriching with GitHub**: Adds PR discussions, issue context, code reviews
3. **Semantic Search**: Lets you ask questions in natural language
4. **Citing Sources**: Every answer includes references to actual commits/PRs

**Example:**
```
❓ Question: Why was authentication refactored in 2024?

Answer:
The authentication system was refactored to address security
vulnerabilities discovered during an audit. The team switched
from a custom JWT implementation to an industry-standard library
to fix weak signature validation and add token rotation.

Confidence: 85% | Credibility: 92%

Citations:
1. a3f2c1d by jane.smith (2024-04-15)
   "Migrate to Auth0 JWT library for better security"
   🔗 https://github.com/owner/repo/pull/156

2. b4e8d2a by mike.jones (2024-04-18)
   "Add refresh token rotation per OWASP guidelines"
```

### Key Benefits

- **Faster Onboarding**: New developers understand "why" in minutes vs. days
- **Better Decisions**: Refactor with full context of original design choices
- **Preserved Knowledge**: Institutional knowledge never gets lost
- **Reduced Risk**: Avoid removing "defensive code" that was solving real problems

---

## Getting Started

### Prerequisites

- **Git repository**: Your project must use Git version control
- **Python 3.9+**: AIL is written in Python
- **Optional**: GitHub personal access token for PR/issue enrichment

### Quick Start (5 minutes)

#### Step 1: Verify Installation

AIL is included in ClaudeAgents by default. Verify it's available:

```bash
cd /path/to/your/project
python3 -c "from tools.code_archaeology import GitArchaeologist; print('✓ AIL available')"
```

#### Step 2: Run Your First Query

```bash
# Interactive mode (recommended for first use)
python3 tools/code_archaeology/query_cli.py

# Or use the archaeology command
python3 tools/archaeology
```

You'll see:
```
🔍 Cognitive Code Archaeology
============================================================

Analyzing git history...
  ✓ Found 219 commits
Building searchable index...
  ✓ Indexed 219 documents

Ready for questions!
Type 'help' for commands, 'quit' to exit.

❓ Question: _
```

#### Step 3: Ask a Question

Try asking:
- "What is the purpose of this repository?"
- "Why was [component] designed this way?"
- "When was [feature] first added?"

#### Step 4: Review the Answer

Each answer includes:
- **Answer text**: Natural language explanation
- **Confidence**: How confident AIL is (0-100%)
- **Credibility**: Overall answer quality (0-100%)
- **Citations**: Links to commits/PRs that support the answer

### Next Steps

- Read [How It Works](#how-it-works) to understand the system
- Explore [Use Cases](#use-cases) for real-world applications
- Review [Configuration](#configuration) for GitHub enrichment
- Check [Troubleshooting](#troubleshooting) if you encounter issues

---

## How It Works

### The Four Stages

#### Stage 1: Git History Analysis

AIL extracts your complete commit history:

```
Analyzing git history...
  ✓ Found 219 commits
  ✓ Identified 147 architecturally significant commits
  ✓ Built temporal index (11 days)
  ✓ Tracked 583 files
```

**What's extracted:**
- Commit messages and diffs
- Author information
- File changes and line counts
- Temporal relationships
- Architectural significance detection

**Performance:** ~38 commits/second

#### Stage 2: GitHub Enrichment (Optional)

If you provide a GitHub repository, AIL adds:

```
Enriching with GitHub...
  ✓ Pull requests: 45
  ✓ Issues: 23
  ✓ Enrichment rate: 68%
```

**What's added:**
- PR titles, descriptions, discussions
- Code review comments
- Issue descriptions and comments
- Decision rationale from PRs

**Requirements:** `GITHUB_TOKEN` environment variable

#### Stage 3: Semantic Indexing

AIL builds a searchable index of all context:

```
Building searchable index...
  ✓ Indexed 219 documents
  ✓ Embedding dimension: 512
  ✓ Using TF-IDF similarity
```

**What's indexed:**
- Commit messages
- PR discussions
- Issue threads
- Code review comments

**Search method:** TF-IDF cosine similarity (or FAISS for large repos)

#### Stage 4: Question Answering

When you ask a question, AIL:

1. **Searches** the index for relevant context
2. **Ranks** results by relevance
3. **Synthesizes** an answer from top results
4. **Cites** sources with commit/PR links
5. **Scores** confidence and credibility

---

## Using AIL

### Interactive Mode (REPL)

The easiest way to use AIL is interactive mode:

```bash
python3 tools/archaeology
```

**Available Commands:**

| Command | Description |
|---------|-------------|
| `help` | Show command help |
| `history` | Show query history |
| `export <file>` | Export history to markdown |
| `quit` / `exit` / `q` | Exit program |

**Example Session:**

```
❓ Question: Why was the database refactored?

Answer:
The database was refactored to improve performance and scalability.
The original schema had denormalization issues causing slow queries...

Confidence: 78% | Credibility: 85%

Citations (3):
1. 7a3b2f1 by alice (2024-03-15)
   "Refactor database schema for better performance"
2. 8c4d9e2 by bob (2024-03-18)
   "Add indexes on frequently queried columns"
3. 9f5a1b3 by alice (2024-03-20)
   "Complete database migration with zero downtime"

❓ Question: Who designed the current API architecture?

Answer:
The API architecture was designed by the backend team led by
@bob in Q1 2024. The design discussions in PR #234 show the
team evaluated REST vs GraphQL and chose REST for simplicity...

Confidence: 82% | Credibility: 88%

❓ Question: quit

Goodbye! 👋
```

### Single Query Mode

For scripting or quick questions:

```bash
# Ask a single question
python3 tools/archaeology --query "Why was authentication refactored?"

# With GitHub enrichment
python3 tools/archaeology --github owner/repo --query "Why was X changed?"

# Export results
python3 tools/archaeology --query "Question?" --export output.md
```

### Command-Line Options

```bash
python3 tools/archaeology [OPTIONS] [REPO_PATH]

Options:
  --query, -q QUESTION      Single query mode (non-interactive)
  --github OWNER/REPO       Enable GitHub PR/issue enrichment
  --export FILE             Export results to markdown file
  REPO_PATH                 Path to repository (default: current directory)
```

### Programmatic Usage

For advanced users who want to integrate AIL into their own scripts:

```python
from tools.code_archaeology import (
    GitArchaeologist,
    ContextSynthesizer,
)
from tools.code_archaeology.github_integrator import EnrichedCommit, EnrichedHistory

# Analyze repository
archaeologist = GitArchaeologist(".")
history = archaeologist.analyze_repo()

# Create enriched history (git-only)
enriched_commits = [EnrichedCommit(commit=c) for c in history.commits]
enriched = EnrichedHistory(
    base_history=history,
    enriched_commits=enriched_commits,
    pull_requests={},
    issues={},
    commit_to_pr={},
)

# Build search index
synthesizer = ContextSynthesizer()
index = synthesizer.build_searchable_index(enriched)

# Ask questions
answer = synthesizer.synthesize_answer(index, "Why was X refactored?")

print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence:.0%}")
```

---

## Configuration

### Basic Configuration

No configuration needed for git-only analysis. Just run:

```bash
python3 tools/archaeology
```

### GitHub Integration

To include PR discussions and issue context:

#### Step 1: Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) or `public_repo` (for public only)
4. Generate and copy the token

#### Step 2: Set Environment Variable

```bash
# Temporary (current shell only)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GITHUB_TOKEN="ghp_xxxx"' >> ~/.bashrc
source ~/.bashrc
```

#### Step 3: Use GitHub Enrichment

```bash
python3 tools/archaeology --github owner/repo
```

### Advanced Configuration

#### Limit Commits Analyzed

For faster analysis on large repositories:

```python
# In Python
history = archaeologist.analyze_repo(limit=500)  # Only last 500 commits

# Or modify query_cli.py (future feature)
```

#### Use FAISS for Large Repos

For repositories with 10,000+ commits:

```bash
# Install FAISS
pip install faiss-cpu

# FAISS will be automatically used if available
python3 tools/archaeology
```

#### Pre-Build Index (CI/CD)

For faster startup in production:

```python
# Build index once (e.g., in CI/CD)
archaeologist = GitArchaeologist(".")
history = archaeologist.analyze_repo()

# Save to disk
archaeologist.export_to_json(history, "archaeology_cache.json")

# Later: Load from cache (future feature)
```

---

## Use Cases

### Use Case 1: Onboarding New Developers

**Scenario:** New developer joining the team needs to understand the codebase

**Questions to Ask:**
- "What is the overall architecture of this application?"
- "Why was [framework] chosen over alternatives?"
- "What are the key design decisions I should know?"
- "Who designed the [component] and what were their goals?"

**Benefit:** Reduce onboarding time from days to hours

**Example:**
```
❓ Question: What is the overall architecture?

Answer:
The application uses a microservices architecture with:
- API Gateway (added in commit 3a4b5c6 by @architect)
- 5 core services: auth, users, products, orders, payments
- Redis for caching (PR #123)
- PostgreSQL for persistent storage

The architecture was designed for horizontal scalability as
documented in PR #89 where the team evaluated monolith vs
microservices and chose microservices for independent deployment.

Key architectural commits:
1. 3a4b5c6 (2023-01-15): "Initial microservices architecture"
2. 7d8e9f0 (2023-02-20): "Add API gateway with Kong"
3. 2c3d4e5 (2023-03-10): "Implement service mesh with Istio"
```

### Use Case 2: Code Review with Context

**Scenario:** Reviewing a refactoring PR and want to understand original design

**Questions to Ask:**
- "Why was this component designed this way originally?"
- "What problems was the original approach solving?"
- "Have we tried this refactoring before? What happened?"

**Benefit:** Make informed review decisions with full historical context

**Example:**
```
❓ Question: Why does the payment processing use a custom retry mechanism?

Answer:
The custom retry mechanism was added in commit 7a3b2f1 (2022-06-15)
after Stripe webhook deliveries proved unreliable in production.

PR #234 discussion shows the team considered using a job queue
(Bull/Sidekiq) but chose inline retries for simplicity given the
low payment volume at the time (< 100/day).

The decision was explicitly documented as technical debt with a
note to migrate to proper job queue when volume exceeds 1000/day.

Citations:
1. 7a3b2f1: "Add custom retry for Stripe webhooks"
2. PR #234: "Stripe integration - webhook reliability"
```

### Use Case 3: Technical Debt Prioritization

**Scenario:** Need to decide which technical debt to tackle first

**Questions to Ask:**
- "Why was this workaround implemented?"
- "What was the urgency that led to this shortcut?"
- "Was this always intended as temporary?"
- "What were the documented risks?"

**Benefit:** Prioritize debt with full understanding of trade-offs made

**Example:**
```
❓ Question: Why do we have two different caching implementations?

Answer:
The dual caching approach emerged from:

1. Redis caching (2023-01): Original cache for user sessions
2. In-memory cache (2023-09): Added during incident response
   when Redis became a bottleneck during Black Friday traffic spike

PR #456 shows this was explicitly marked as temporary with plan
to migrate to distributed Redis cluster in Q1 2024, but that
migration was deprioritized for feature work.

The in-memory cache is now stale and should be removed, but
need to complete Redis cluster migration first.

Technical debt severity: High (complexity cost > performance benefit)
```

### Use Case 4: Security Audit

**Scenario:** Security team needs to understand security-related changes

**Questions to Ask:**
- "What security vulnerabilities have been fixed in [component]?"
- "When was authentication last audited?"
- "What security improvements were made in the last year?"

**Benefit:** Complete security audit trail with context

**Example:**
```
❓ Question: What security vulnerabilities were fixed in authentication?

Answer:
Authentication security fixes over the past year:

1. SQL Injection (2024-03-15, Critical)
   Commit a1b2c3d: "Fix SQL injection in login endpoint"
   CVE-2024-1234, reported by security@example.com

2. JWT Signature Bypass (2024-05-20, Critical)
   Commit d4e5f6a: "Enforce JWT signature validation"
   Discovered during external audit (PR #567)

3. Session Fixation (2024-07-10, High)
   Commit g7h8i9j: "Regenerate session IDs on login"
   OWASP Top 10 compliance (PR #678)

All fixes have been backported to production and verified.
```

### Use Case 5: Documentation Generation

**Scenario:** Need to document component design decisions

**Questions to Ask:**
- "What is the purpose of [component]?"
- "What were the key design decisions?"
- "What problems does it solve?"
- "How has it evolved over time?"

**Benefit:** Auto-generate architecture documentation with citations

**Example:**
```bash
# Generate documentation
python3 tools/archaeology --query "
What are the key architectural decisions for the API layer?
" --export docs/api-architecture.md
```

**Output (docs/api-architecture.md):**
```markdown
# API Layer Architecture

Generated: 2024-10-08

## Key Architectural Decisions

### REST API Design (2023-01-15)
The team chose RESTful API design over GraphQL for simplicity...

**References:**
- a3b4c5d (2023-01-15): "Initial REST API implementation"
- PR #45: "API design discussion: REST vs GraphQL"

### Authentication Strategy (2023-02-20)
JWT-based authentication was implemented with OAuth2...

**References:**
- d6e7f8a (2023-02-20): "Add JWT authentication"
```

### Use Case 6: Bug Investigation

**Scenario:** Debugging a production issue and need historical context

**Questions to Ask:**
- "When was [feature] last modified?"
- "What changes were made to [component] recently?"
- "Have we had similar bugs before?"
- "What was the fix for [related issue]?"

**Benefit:** Faster root cause analysis with historical patterns

**Example:**
```
❓ Question: When did the payment timeout issue first appear?

Answer:
The payment timeout issue first appeared after commit 8c9d0e1
(2024-09-15) which increased payment processing complexity by
adding fraud detection checks.

The team anticipated this in PR #789 and added a TODO to
implement async processing, but it was deprioritized.

Similar timeouts occurred in 2023-06 (commit 5f6a7b8) when
inventory checks were added, fixed by increasing timeout from
5s to 30s.

Suggested fix: Implement async payment processing as originally
planned, or increase timeout to 60s as short-term workaround.
```

---

## Troubleshooting

### Issue: "Not a git repository"

**Error:**
```
ValueError: Not a git repository: /path/to/dir
```

**Solution:**
Ensure you're in a git repository:
```bash
git status
# If not a repo:
git init
```

### Issue: "Command not found: archaeology"

**Error:**
```
bash: archaeology: command not found
```

**Solution:**
Use the full path:
```bash
python3 tools/code_archaeology/query_cli.py
# Or
python3 tools/archaeology  # If the script exists
```

### Issue: GitHub API Rate Limit

**Error:**
```
GitHub API rate limit exceeded
```

**Solution:**
Set your GitHub token:
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

Or limit enrichment:
```bash
# In Python
enriched = gh_arch.enrich_history(history, limit=50)
```

### Issue: Slow Performance

**Symptom:**
Analysis takes >2 minutes for small repo

**Solutions:**

1. **Install FAISS** (for large repos):
```bash
pip install faiss-cpu
```

2. **Limit analysis**:
```python
history = archaeologist.analyze_repo(limit=500)
```

3. **Check disk speed**:
```bash
# Ensure repo is on fast storage (not network drive)
```

### Issue: Low-Quality Answers

**Symptom:**
Answers are generic or irrelevant

**Solutions:**

1. **Ask more specific questions**:
   - Bad: "Tell me about the code"
   - Good: "Why was authentication refactored in Q2 2024?"

2. **Check confidence scores**:
```
Confidence: 25% | Credibility: 30%
```
Low scores indicate insufficient historical context

3. **Add GitHub enrichment** for richer context:
```bash
python3 tools/archaeology --github owner/repo
```

### Issue: Out of Memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Limit commits**:
```python
history = archaeologist.analyze_repo(limit=1000)
```

2. **Increase swap space** (OS-level)

3. **Use incremental analysis** (future feature)

### Issue: No Results for Query

**Symptom:**
```
Answer: No relevant information found in repository history.
Confidence: 0%
```

**Solutions:**

1. **Rephrase question** to match commit language:
   - Instead of: "How does caching work?"
   - Try: "When was caching first added?"

2. **Check if feature exists** in repo history:
   - Feature may be too new
   - Feature may use different terminology

3. **Increase search depth**:
```python
answer = synthesizer.synthesize_answer(index, question, max_results=20)
```

---

## FAQ

### General Questions

**Q: Is my code sent to external servers?**
A: No. All git analysis is 100% local. GitHub enrichment only queries GitHub's API for PR/issue metadata (which is already public for open-source projects).

**Q: Does AIL work with private repositories?**
A: Yes. For git-only analysis, everything is local. For GitHub enrichment, set `GITHUB_TOKEN` with access to private repos.

**Q: How much disk space does AIL use?**
A: Minimal. Index files are ~5MB per 100 documents. No large files are created.

**Q: Can I use AIL with GitLab/Bitbucket?**
A: Currently only GitHub is supported for enrichment. Git-only analysis works with any Git repository.

**Q: How often should I rebuild the index?**
A: For active repos, rebuild daily/weekly. Future versions will support incremental updates.

### Technical Questions

**Q: What embedding model does AIL use?**
A: By default, TF-IDF (no external dependencies). You can optionally use FAISS for large repos.

**Q: How accurate are the answers?**
A: Accuracy depends on:
- Commit message quality (detailed commits = better answers)
- GitHub enrichment (PR discussions add context)
- Question specificity (focused questions = better results)

Average confidence scores: 60-80% for well-documented repos

**Q: Can I customize the search algorithm?**
A: Yes. See [AIL Integration Guide](AIL_INTEGRATION_GUIDE.md) for custom embedding providers.

**Q: Does AIL support incremental updates?**
A: Not yet. Currently, you must rebuild the index for new commits. This is planned for a future release.

**Q: What's the performance on large repositories?**
A:
- Small repos (<1K commits): ~2-5 seconds
- Medium repos (1K-10K commits): ~10-30 seconds
- Large repos (>10K commits): ~60-120 seconds (use FAISS)

### Use Case Questions

**Q: Should I use AIL for every code review?**
A: Use AIL when you need historical context (refactorings, legacy code, design decisions). Not needed for simple changes.

**Q: Can AIL replace documentation?**
A: No. AIL complements documentation by recovering lost context. You should still write proper docs.

**Q: Is AIL useful for greenfield projects?**
A: Less useful initially (no history). Value grows over time as decisions accumulate.

**Q: Can non-technical users use AIL?**
A: Yes. Product managers, designers, and QA can ask questions about features and decisions.

### Privacy & Security Questions

**Q: What data does AIL access?**
A:
- Git commits (local)
- GitHub PRs/issues (via API with token)
- No code is sent externally

**Q: Is my GitHub token secure?**
A: Yes. The token is stored as an environment variable and only used for GitHub API calls. It's never logged or transmitted elsewhere.

**Q: Can I use AIL on a network-restricted machine?**
A: Yes, for git-only analysis. GitHub enrichment requires internet access.

**Q: Does AIL comply with GDPR/privacy regulations?**
A: All processing is local. GitHub API calls only access already-public data (for open-source) or data you have permission to access (via your token).

---

## Next Steps

### Learn More

- **[AIL API Reference](AIL_API.md)**: Complete API documentation
- **[AIL Integration Guide](AIL_INTEGRATION_GUIDE.md)**: How to integrate AIL into agents
- **[AIL Architecture](AIL_ARCHITECTURE.md)**: System design and architecture
- **[Cognitive Archaeology Command](../commands/development/cognitive-archaeology.md)**: Command-line usage

### Get Help

- **Issues**: Report bugs at [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/your-repo/discussions)
- **Contributing**: See [Contributing Guide](contributing.md)

### Provide Feedback

We'd love to hear how you're using AIL:

- What questions are you asking?
- How has it helped your workflow?
- What features would you like to see?

Share your feedback in GitHub Discussions or open a feature request!

---

## Version History

**1.0.0** (2025-10-08)
- Initial release
- Git history analysis
- GitHub PR/issue enrichment
- Semantic search and Q&A
- Interactive CLI
- Export to markdown

---

**Last Updated:** 2025-10-08
**Version:** 1.0.0
**Status:** Production Ready
