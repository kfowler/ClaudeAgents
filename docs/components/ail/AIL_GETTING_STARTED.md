# AIL Getting Started Guide

**Quick Start**: Get archaeological intelligence for your AI agents in under 10 minutes

**Version**: 2.0.0 (Sprint 2 with FAISS)
**Updated**: 2025-10-09

---

## What is AIL?

The **Archaeological Intelligence Layer (AIL)** provides AI agents with historical context about code decisions, architectural changes, and development patterns by connecting to the Cognitive Code Archaeology (CCA) system.

**Think of it as**: A time machine for your codebase that helps AI agents understand the "why" behind the "what".

### Key Benefits

- **Informed Decisions**: Agents understand historical context before making recommendations
- **Better Code Reviews**: Reference past decisions and patterns
- **Faster Debugging**: Identify similar bugs fixed in the past
- **Architectural Awareness**: Understand design evolution and rationale
- **Security Insights**: Learn from past vulnerabilities and fixes

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Git repository (local or remote)
- 2GB RAM minimum (4GB recommended for FAISS)

### Step 1: Install Core Dependencies

```bash
# Navigate to the project root
cd /path/to/ClaudeAgents

# Install required dependencies (already in tools/requirements.txt)
pip install numpy>=1.21.0 requests>=2.28.0
```

The core dependencies are minimal and likely already installed.

### Step 2: Install Optional Dependencies (Recommended)

For Sprint 2 semantic search features:

```bash
# FAISS for semantic similarity search (2-3x performance boost)
pip install faiss-cpu>=1.7.4

# Sentence Transformers for embeddings
pip install sentence-transformers>=2.2.0
```

**Note**: These are optional. AIL works without them, but Sprint 2 features provide 41% latency reduction.

### Step 3: Verify Installation

```bash
# Quick verification
python3 -c "from tools.ail import ArchaeologyContextProvider; print('✅ AIL installed successfully')"

# Verify FAISS (optional)
python3 tools/ail/validate_faiss.py .
```

---

## Quick Start (5 Minutes)

### Your First Query

Create a simple script to test AIL:

```python
# test_ail.py
from tools.ail import ArchaeologyContextProvider

# Initialize provider with your repository
provider = ArchaeologyContextProvider(repo_path=".")

# Ask a question about a file
context = provider.get_context_sync(
    file_path="README.md",
    question="What is the purpose of this project?"
)

# Display the results
print(f"Answer: {context.answer}")
print(f"Confidence: {context.confidence:.1%}")
print(f"Sources: {len(context.sources)}")
print(f"Query Time: {context.query_time_ms:.0f}ms")
```

Run it:

```bash
python3 test_ail.py
```

**Expected Output**:
```
Answer: This project provides specialized AI agent definitions...
Confidence: 35.2%
Sources: 5
Query Time: 2100ms  # First query (cold start)
```

Run it again to see caching in action:

```bash
python3 test_ail.py
```

**Expected Output** (second run):
```
Answer: This project provides specialized AI agent definitions...
Confidence: 35.2%
Sources: 5
Query Time: 2ms  # Cached! (1000x faster)
```

### Understanding the Results

The `ArchaeologicalContext` object contains:

- **answer**: Generated answer from historical context
- **confidence**: How confident (0.0-1.0) based on source quality
- **sources**: List of commits, PRs, issues that informed the answer
- **query_time_ms**: How long the query took
- **cached**: Whether result came from cache

---

## Basic Usage Patterns

### Pattern 1: Simple Question About a File

```python
from tools.ail import ArchaeologyContextProvider

provider = ArchaeologyContextProvider(repo_path=".")

# Ask about any file in your repository
context = provider.get_context_sync(
    file_path="agents/full-stack-architect.md",
    question="What technologies does this agent specialize in?"
)

print(context.to_markdown())  # Pretty-printed markdown output
```

### Pattern 2: Natural Language Input (Agent Integration)

```python
from tools.ail import ArchaeologyContextProvider, get_context_from_input

provider = ArchaeologyContextProvider(repo_path=".")

# Agent provides natural language input
agent_input = 'Why does "tools/ail/context_provider.py" use LRU caching?'

# Automatically extracts file path and formulates question
context = get_context_from_input(provider, agent_input)

if context:
    print(f"Confidence: {context.confidence:.1%}")
    for source in context.sources[:3]:  # Top 3 sources
        print(f"  - {source.type}: {source.identifier}")
```

### Pattern 3: Task-Specific Questions

```python
from tools.ail.agent_integration import detect_task_type, formulate_question

# Detect what the user wants to do
agent_input = "I need to refactor the authentication module"
task_type = detect_task_type(agent_input)  # Returns: "refactor"

# Get optimized question for that task
question = formulate_question(agent_input, task_type)
# Returns: "What was the original design intent? What patterns were established?"

context = provider.get_context_sync("src/auth.py", question)
```

**Supported Task Types**:
- `general`: Default queries
- `refactor`: Code restructuring
- `debug`: Bug investigation
- `review`: Code review
- `implement`: New feature development
- `optimize`: Performance improvement

---

## Agent Integration (Production Usage)

### Using Pre-Built Agent Integrations

Sprint 2 includes 7 production-ready agent integrations:

```python
from agents.integrations import CodeArchitectAIL

# Initialize agent integration
architect = CodeArchitectAIL(repo_path=".")

# Get architectural analysis with historical context
review = architect.enhanced_review(
    "Why does tools/ail/context_provider.py use LRU caching?"
)

# Access structured results
print(f"Confidence: {review.confidence:.1%}")
print(f"Design Decisions Found: {len(review.design_decisions)}")

for decision in review.design_decisions:
    print(f"\n{decision.title}")
    print(f"  Rationale: {decision.rationale}")
    print(f"  Date: {decision.date}")

print(f"\nRecommendations:")
for rec in review.recommendations:
    print(f"  - {rec}")
```

**Available Agent Integrations**:
- **CodeArchitectAIL**: Architectural insights and design decisions
- **SecurityAuditAIL**: Security incident history and vulnerability patterns
- **FullStackArchitectAIL**: Architectural evolution tracking
- **BackendAPIEngineerAIL**: API change tracking and schema history
- **QATestEngineerAIL**: Bug history and regression patterns
- **DebuggingSpecialistAIL**: Bug fix cataloging and root cause analysis
- **FrontendPerformanceAIL**: Performance tracking and optimization history

### Creating Custom Agent Integrations

```python
from tools.ail import ArchaeologyContextProvider, get_context_from_input
from dataclasses import dataclass
from typing import List

@dataclass
class CustomInsight:
    """Your domain-specific insight."""
    title: str
    description: str
    confidence: float
    sources: List[str]

class MyCustomAgentAIL:
    """Custom agent with AIL integration."""

    def __init__(self, repo_path: str):
        self.provider = ArchaeologyContextProvider(repo_path=repo_path)

    def analyze(self, user_input: str) -> List[CustomInsight]:
        """Analyze with historical context."""
        # Get archaeological context
        context = get_context_from_input(self.provider, user_input)

        if not context:
            return []

        # Extract domain-specific insights
        insights = []
        for source in context.sources:
            insight = CustomInsight(
                title=f"Insight from {source.identifier}",
                description=source.summary,
                confidence=context.confidence,
                sources=[source.url]
            )
            insights.append(insight)

        return insights

# Use your custom agent
agent = MyCustomAgentAIL(repo_path=".")
insights = agent.analyze("What security measures are in place?")

for insight in insights:
    print(f"{insight.title} (confidence: {insight.confidence:.1%})")
    print(f"  {insight.description}")
```

---

## Configuration Options

### Basic Configuration

```python
from tools.ail import ArchaeologyContextProvider

provider = ArchaeologyContextProvider(
    repo_path=".",                # Repository path (required)
    cache_size=1000,              # L1 cache entries (default: 1000)
    max_query_time_s=2.0,         # Query timeout (default: 2s)
)
```

### Advanced Configuration (GitHub Integration)

```python
import os

provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=2000,              # Larger cache for busy systems
    max_query_time_s=5.0,         # Longer timeout for complex queries
    github_owner="your-org",      # GitHub organization
    github_repo="your-repo",      # GitHub repository
    github_token=os.environ.get("GITHUB_TOKEN"),  # GitHub token (optional)
)
```

**GitHub Token Benefits**:
- Access to pull request discussions
- Issue comments and history
- Enhanced context from GitHub metadata
- Rate limit: 5,000 requests/hour (vs 60 without token)

**Getting a GitHub Token**:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope (for private repos) or `public_repo` (for public repos)
3. Set environment variable: `export GITHUB_TOKEN=ghp_your_token_here`

### Feature Flags (Sprint 2)

```python
import os

# Enable/disable FAISS semantic search
os.environ['AIL_FAISS_ENABLED'] = 'true'   # Default: true if installed
os.environ['FAISS_ROLLOUT'] = '100'        # Percentage: 0-100 (default: 100)

# Initialize provider (automatically uses feature flags)
provider = ArchaeologyContextProvider(repo_path=".")
```

---

## Performance Tips

### 1. Cache Optimization

```python
# Increase cache size for high-traffic scenarios
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=5000  # Default: 1000
)

# Monitor cache performance
stats = provider.get_cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"L1 hit rate: {stats.l1_hit_rate:.1%}")
print(f"L2 hit rate: {stats.l2_hit_rate:.1%}")  # Sprint 2 only

# Adjust if hit rate is low (<30%)
```

### 2. Batch Processing

```python
# Process multiple files efficiently
files = ["src/auth.py", "src/api.py", "src/database.py"]

for file_path in files:
    context = provider.get_context_sync(
        file_path,
        "What is the purpose of this module?"
    )
    print(f"{file_path}: {context.confidence:.1%} confidence")
```

### 3. Async Usage (Non-Blocking)

```python
import asyncio
from tools.ail import ArchaeologyContextProvider

async def process_multiple_queries():
    provider = ArchaeologyContextProvider(repo_path=".")

    # Run queries concurrently
    queries = [
        provider.get_context("auth.py", "Why JWT?"),
        provider.get_context("api.py", "Why REST?"),
        provider.get_context("db.py", "Why PostgreSQL?"),
    ]

    contexts = await asyncio.gather(*queries)

    for context in contexts:
        print(f"{context.file_path}: {context.answer[:100]}...")

# Run async queries
asyncio.run(process_multiple_queries())
```

### 4. Warming the Cache

```python
# Pre-warm cache with common queries at startup
common_queries = [
    ("README.md", "What is this project?"),
    ("src/main.py", "What is the entry point?"),
    ("src/config.py", "What configuration options exist?"),
]

for file_path, question in common_queries:
    provider.get_context_sync(file_path, question)

# Subsequent queries will be fast
```

---

## Troubleshooting

### Issue: Slow First Query

**Problem**: First query takes 2-3 seconds

**Solution**: This is expected (cold start). Subsequent queries are cached and return in ~2ms.

```python
# First query: ~2000ms (building index)
context1 = provider.get_context_sync("file.py", "Why?")

# Second query: ~2ms (cached)
context2 = provider.get_context_sync("file.py", "Why?")
```

**Workaround**: Pre-warm cache at initialization (see Performance Tips).

### Issue: Low Confidence Scores

**Problem**: Confidence consistently <20%

**Possible Causes**:
1. **Generic questions**: Ask more specific questions
2. **Poor commit messages**: Limited historical information available
3. **New file**: File has limited history
4. **Wrong file path**: File doesn't exist or path is incorrect

**Solution**:
```python
# ❌ Generic question (low confidence)
context = provider.get_context_sync("auth.py", "Tell me about this file")

# ✅ Specific question (higher confidence)
context = provider.get_context_sync("auth.py", "Why was JWT authentication chosen over session-based auth?")
```

### Issue: FAISS Not Working

**Problem**: Sprint 2 features not activating

**Diagnosis**:
```bash
python3 tools/ail/validate_faiss.py .
```

**Solution**:
```bash
# Install FAISS
pip install faiss-cpu>=1.7.4
pip install sentence-transformers>=2.2.0

# Verify
python3 tools/ail/validate_faiss.py .
```

If installation fails, AIL gracefully falls back to L1 cache only (still works, just slower).

### Issue: Memory Usage High

**Problem**: Process using >1GB RAM

**Solution**:
```python
# Reduce cache size
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=500  # Default: 1000
)

# Check memory usage
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.0f}MB")
```

**Memory Budget**:
- Base AIL: ~78MB
- FAISS (if enabled): ~80MB (model) + ~12MB (index per 1k docs)
- L1 cache: ~10KB per entry
- L2 cache: ~18MB for 100 entries

**Total typical usage**: 140-250MB

### Issue: Import Error

**Problem**: `ModuleNotFoundError: No module named 'tools.ail'`

**Solution**:
```python
# Option 1: Use absolute imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ail import ArchaeologyContextProvider

# Option 2: Set PYTHONPATH
# export PYTHONPATH=/path/to/ClaudeAgents:$PYTHONPATH

# Option 3: Install in development mode
# pip install -e /path/to/ClaudeAgents
```

---

## Next Steps

### Learn More

1. **[User Guide](AIL_USER_GUIDE.md)**: Comprehensive feature documentation
2. **[API Reference](AIL_API.md)**: Complete API documentation
3. **[Architecture](AIL_ARCHITECTURE.md)**: System architecture and design
4. **[Deployment Guide](AIL_DEPLOYMENT_GUIDE.md)**: Production deployment

### Explore Examples

```bash
# Run all examples
python3 tools/ail/examples.py

# Sprint 2 quickstart
python3 -m tools.ail.SPRINT_2_QUICKSTART

# Test agent integrations
python3 tests/test_ail/test_agent_integrations/verify_integration.py
```

### Join the Community

- Read the [Sprint 2 Complete Summary](AIL_SPRINT_2_COMPLETE.md) for full capabilities
- Check the [Changelog](../tools/ail/CHANGELOG.md) for latest updates
- Review [Sprint 2 Completion Report](ail_sprint2_completion_report.md) for quality metrics

---

## Quick Reference

### Essential Commands

```bash
# Install dependencies
pip install numpy requests faiss-cpu sentence-transformers

# Verify installation
python3 -c "from tools.ail import ArchaeologyContextProvider; print('✅ OK')"

# Validate FAISS
python3 tools/ail/validate_faiss.py .

# Run tests
python3 -m pytest tests/test_ail/ -v

# Run examples
python3 tools/ail/examples.py
```

### Essential Code Snippets

```python
# Basic usage
from tools.ail import ArchaeologyContextProvider
provider = ArchaeologyContextProvider(repo_path=".")
context = provider.get_context_sync("file.py", "question")
print(context.to_markdown())

# Natural language (agent integration)
from tools.ail import get_context_from_input
context = get_context_from_input(provider, 'Why does "file.py" use X?')

# Agent integration
from agents.integrations import CodeArchitectAIL
architect = CodeArchitectAIL(repo_path=".")
review = architect.enhanced_review("Review this file")

# Cache statistics
stats = provider.get_cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
```

### Performance Expectations

| Operation | Sprint 1 | Sprint 2 (FAISS) |
|-----------|----------|------------------|
| Cold query | ~2500ms | ~2200ms |
| Cache hit (L1) | ~5ms | ~2ms |
| Cache hit (L2) | N/A | ~35ms |
| Queries/second | 50 | 110 |

---

## Support

### Getting Help

1. **Check Documentation**: Start with this guide and the [User Guide](AIL_USER_GUIDE.md)
2. **Run Validation**: Use `validate_faiss.py` and `validate_semantic_cache.py`
3. **Review Examples**: Check `tools/ail/examples.py` for working code
4. **Check Tests**: Look at `tests/test_ail/` for usage patterns

### Common Questions

**Q: Do I need FAISS?**
A: No, but recommended. AIL works without FAISS (Sprint 1 features only).

**Q: How much memory does AIL use?**
A: 140-250MB typically (base + FAISS + cache).

**Q: Can I use AIL with multiple repositories?**
A: Yes, initialize one provider per repository.

**Q: Does AIL work without GitHub access?**
A: Yes, works with git-only data. GitHub token adds PR/issue context.

**Q: How do I improve confidence scores?**
A: Ask specific questions, ensure good commit messages, use files with history.

**Q: Can I use AIL in production?**
A: Yes, Sprint 2 is production-ready with comprehensive testing.

---

## Version Information

- **Current Version**: 2.0.0 (Sprint 2)
- **Released**: 2025-10-09
- **Status**: Production Ready
- **Previous Version**: 1.0.0 (Sprint 1)

For version history, see [CHANGELOG.md](../tools/ail/CHANGELOG.md).

---

**Congratulations!** You're now ready to use AIL to give your AI agents historical intelligence.

Start with simple queries, explore the agent integrations, and gradually incorporate AIL into your agent workflows for 40%+ quality improvements.

---

*For detailed documentation, see [AIL User Guide](AIL_USER_GUIDE.md) and [API Reference](AIL_API.md).*
