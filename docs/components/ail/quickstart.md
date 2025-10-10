# AIL Quick Start Guide

**Get archaeological context in 3 lines of code**

## Installation

AIL is already part of ClaudeAgents. Just ensure dependencies are installed:

```bash
pip install -r tools/requirements.txt
```

## Simplest Usage

```python
from ail import ArchaeologyContextProvider, get_context_from_input

# 1. Initialize
provider = ArchaeologyContextProvider(repo_path=".")

# 2. Query with natural language
context = get_context_from_input(
    provider,
    'Why does "src/auth.py" use JWT tokens?'
)

# 3. Use the context
if context:
    print(context.to_markdown())
```

## What You Get

```python
context.answer           # Natural language answer
context.confidence       # Confidence score (0.0-1.0)
context.sources          # List of sources (commits, PRs, issues)
context.cached           # Whether result was cached
context.query_time_ms    # How long the query took
```

## Common Patterns

### Pattern 1: File-Specific Questions

```python
context = provider.get_context_sync(
    file_path="tools/ail/context_provider.py",
    question="Why was LRU caching implemented?"
)
```

### Pattern 2: Task-Specific Questions

```python
from ail.agent_integration import detect_task_type, formulate_question

agent_input = "I need to refactor the authentication module"
task_type = detect_task_type(agent_input)  # "refactor"

question = formulate_question(agent_input, task_type)
# Returns: "What was the original design intent? What patterns were established?"

context = provider.get_context_sync("src/auth.py", question)
```

### Pattern 3: Automatic Everything

```python
# Just pass the agent's natural language input
agent_input = 'Why does "config/database.py" use connection pooling?'

context = get_context_from_input(provider, agent_input)
# Automatically:
#   - Extracts file path: "config/database.py"
#   - Detects task type: "general"
#   - Formulates question
#   - Gets context
```

## Task Types

AIL understands these task types and formulates appropriate questions:

- **refactor**: Focus on design intent and patterns
- **debug**: Focus on intended behavior and past bugs
- **review**: Focus on decision factors and alternatives
- **implement**: Focus on conventions and patterns
- **optimize**: Focus on performance considerations
- **general**: General historical context

Example:
```python
from ail.agent_integration import create_agent_query

query = create_agent_query(
    "Fix the authentication bug in auth.py",
    repo_path=".",
    auto_detect=True
)

# Returns:
# {
#   'file_path': 'auth.py',
#   'task_type': 'debug',
#   'question': 'What was the intended behavior? What bugs were fixed?'
# }
```

## Performance Tips

### 1. Reuse Provider

```python
# ❌ Don't create new provider for each query
for file in files:
    provider = ArchaeologyContextProvider(repo_path=".")  # Slow!
    context = provider.get_context_sync(file, "Why?")

# ✅ Create once, reuse many times
provider = ArchaeologyContextProvider(repo_path=".")
for file in files:
    context = provider.get_context_sync(file, "Why?")  # Fast!
```

### 2. Cache Benefits

```python
# First query: ~800ms (loads git history)
context1 = provider.get_context_sync("auth.py", "Why JWT?")

# Same query: ~2ms (cache hit, 400x faster!)
context2 = provider.get_context_sync("auth.py", "Why JWT?")
```

### 3. Check Cache Stats

```python
stats = provider.get_cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Avg time: {stats.avg_query_time_ms:.0f}ms")
```

## Format for Different Outputs

```python
from ail.agent_integration import format_context_for_agent

# Markdown (for agents)
markdown = format_context_for_agent(context, style="markdown")

# Plain text
text = format_context_for_agent(context, style="text")

# JSON (for APIs)
json_str = format_context_for_agent(context, style="json")
```

## Error Handling

AIL gracefully handles errors:

```python
context = provider.get_context_sync("nonexistent.py", "Why?")

if context.confidence == 0.0:
    # Error occurred, check the message
    print(f"Error: {context.answer}")
else:
    # Valid context
    print(context.answer)
```

## GitHub Integration (Optional)

For richer context (PRs, issues, discussions):

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    github_owner="your-org",
    github_repo="your-repo",
    github_token="ghp_...",  # or use GITHUB_TOKEN env var
)
```

## Configuration

```python
provider = ArchaeologyContextProvider(
    repo_path="/path/to/repo",
    cache_size=1000,           # Max cache entries
    max_query_time_s=2.0,      # Query timeout
)
```

## Complete Example

```python
#!/usr/bin/env python3
"""Example: Code review assistant"""

from ail import ArchaeologyContextProvider, get_context_from_input

def review_file(provider, file_path, question):
    """Review a file with archaeological context."""
    context = provider.get_context_sync(file_path, question)

    print(f"\n{'='*60}")
    print(f"File: {file_path}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    if context.has_high_confidence:
        print(f"\n✅ High Confidence ({context.confidence:.0%})")
        print(f"\n{context.answer}")
        print(f"\nBased on {len(context.sources)} sources:")
        for i, source in enumerate(context.sources[:3], 1):
            print(f"  {i}. {source.commit_message} by {source.author}")
    else:
        print(f"\n⚠️  Low Confidence ({context.confidence:.0%})")
        print(f"\n{context.answer}")

# Initialize
provider = ArchaeologyContextProvider(repo_path=".")

# Review files
review_file(
    provider,
    "src/auth.py",
    "Why was JWT authentication chosen? What alternatives were considered?"
)

review_file(
    provider,
    "src/database.py",
    "What was the rationale for connection pooling?"
)

# Check performance
stats = provider.get_cache_stats()
print(f"\n\nCache Performance:")
print(f"  Hit Rate: {stats.hit_rate:.1%}")
print(f"  Queries: {stats.total_queries}")
print(f"  Avg Time: {stats.avg_query_time_ms:.0f}ms")
```

## Next Steps

1. Read [README.md](README.md) for complete documentation
2. Run `python3 tools/ail/examples.py` for more examples
3. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details
4. Run tests: `python3 -m pytest tests/test_ail/ -v`

## Need Help?

- See `tools/ail/examples.py` for 7 working examples
- Check test files for usage patterns
- Review `tools/ail/README.md` for complete API reference

## Pro Tips

1. **Reuse the provider** - initialization is expensive
2. **Use `get_context_from_input()`** for simplest agent integration
3. **Check `context.confidence`** before using the answer
4. **Monitor cache stats** to optimize performance
5. **Use task types** to get better questions
6. **Enable GitHub integration** for richer context

---

**Start coding in 30 seconds:**

```python
from ail import ArchaeologyContextProvider, get_context_from_input

provider = ArchaeologyContextProvider(repo_path=".")
context = get_context_from_input(provider, 'Why does "file.py" work this way?')

print(context.to_markdown() if context else "No context found")
```

That's it! 🚀
