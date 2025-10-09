# AIL (Archaeology Intelligence Layer)

**Sprint 1: Foundation Layer** - Making archaeological context available to all agents

## Overview

AIL (Archaeology Intelligence Layer) provides AI agents with historical context about code decisions, architectural changes, and development patterns by integrating with the Cognitive Code Archaeology (CCA) system.

### Key Features

- **LRU Caching**: Intelligent caching with 1000-entry default for performance
- **Async Support**: Non-blocking queries with configurable timeouts
- **Graceful Degradation**: Continues working when CCA is unavailable
- **Agent-Friendly API**: Simple helpers for natural language queries
- **Type-Safe**: Full type hints throughout
- **Well-Tested**: 57 unit tests with 100% critical path coverage

## Architecture

```
AIL Sprint 1 Components:

┌─────────────────────────────────────────────────────────┐
│                    AI Agents                             │
│  (full-stack-architect, code-architect, etc.)           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Natural Language Queries
                      ▼
┌─────────────────────────────────────────────────────────┐
│           Agent Integration Helpers                      │
│  • extract_file_path()                                  │
│  • formulate_question()                                 │
│  • get_context_from_input()                             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│        ArchaeologyContextProvider                        │
│  • LRU Cache (1000 entries)                             │
│  • Timeout Handling (2s default)                        │
│  • Error Handling & Logging                             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│     Cognitive Code Archaeology (CCA)                    │
│  • GitArchaeologist                                     │
│  • GitHubArchaeologist                                  │
│  • ContextSynthesizer                                   │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Basic Usage

```python
from ail import ArchaeologyContextProvider

# Initialize provider
provider = ArchaeologyContextProvider(
    repo_path="/path/to/repo",
    cache_size=1000,
)

# Get context for a file
context = provider.get_context_sync(
    file_path="src/auth.py",
    question="Why was JWT authentication chosen?"
)

# Use the context
print(context.answer)
print(f"Confidence: {context.confidence:.1%}")
print(f"Sources: {len(context.sources)}")

# Output as markdown for agent consumption
print(context.to_markdown())
```

### Agent Integration Helpers

```python
from ail import ArchaeologyContextProvider, get_context_from_input

provider = ArchaeologyContextProvider(repo_path=".")

# Natural language input from agent
agent_input = 'Why does "src/auth.py" use JWT tokens?'

# Automatically extract file path, formulate question, and get context
context = get_context_from_input(provider, agent_input)

if context:
    print(context.to_markdown())
```

### Advanced: Custom Questions by Task Type

```python
from ail.agent_integration import (
    detect_task_type,
    formulate_question,
    create_agent_query,
)

# Detect what the agent is trying to do
agent_input = "I need to refactor the authentication module"
task_type = detect_task_type(agent_input)  # Returns: "refactor"

# Formulate optimized question
question = formulate_question(agent_input, task_type)
# Returns: "What was the original design intent? What patterns were established?"

# Or create complete query configuration
query = create_agent_query(agent_input, repo_path=".", auto_detect=True)
# Returns: {
#   'file_path': 'src/auth.py',
#   'question': '...',
#   'task_type': 'refactor'
# }
```

## API Reference

### ArchaeologyContextProvider

Main provider class for archaeological context.

**Constructor:**
```python
ArchaeologyContextProvider(
    repo_path: str,              # Path to git repository
    cache_size: int = 1000,      # Maximum cache entries
    github_owner: Optional[str] = None,    # GitHub owner (optional)
    github_repo: Optional[str] = None,     # GitHub repo (optional)
    github_token: Optional[str] = None,    # GitHub token (optional)
    max_query_time_s: float = 2.0,         # Query timeout
)
```

**Methods:**

- `get_context(file_path, question) -> ArchaeologicalContext`: Async context retrieval
- `get_context_sync(file_path, question) -> ArchaeologicalContext`: Synchronous wrapper
- `clear_cache()`: Clear the LRU cache
- `get_cache_stats() -> CacheStats`: Get cache performance statistics
- `is_initialized() -> bool`: Check if provider is initialized
- `get_init_error() -> Optional[str]`: Get initialization error if any

### ArchaeologicalContext

Result object containing context and metadata.

**Properties:**
- `file_path: str`: File being queried
- `question: str`: Question asked
- `answer: str`: Generated answer
- `sources: List[ContextSource]`: Supporting sources
- `confidence: float`: Confidence score (0.0 - 1.0)
- `cached: bool`: Whether result was cached
- `query_time_ms: float`: Query execution time
- `timestamp: datetime`: When context was retrieved

**Methods:**
- `has_high_confidence -> bool`: Check if confidence > 0.7
- `source_count -> int`: Number of supporting sources
- `to_markdown() -> str`: Format as markdown for agents

### Agent Integration Helpers

**File Path Extraction:**
```python
extract_file_path(agent_input: str, repo_path: Optional[str] = None) -> Optional[str]
```

**Question Formulation:**
```python
formulate_question(agent_input: str, task_type: str = "general") -> str
# task_type: "general", "refactor", "debug", "review", "implement", "optimize"
```

**Task Type Detection:**
```python
detect_task_type(agent_input: str) -> str
# Returns: "general", "refactor", "debug", "review", "implement", "optimize"
```

**Complete Query Creation:**
```python
create_agent_query(
    agent_input: str,
    repo_path: str,
    auto_detect: bool = True
) -> Dict[str, Any]
```

**One-Line Helper:**
```python
get_context_from_input(
    provider: ArchaeologyContextProvider,
    agent_input: str,
    repo_path: Optional[str] = None
) -> Optional[ArchaeologicalContext]
```

## Performance

### Caching

- **LRU Cache**: Default 1000 entries
- **Cache Key**: Hash of (file_path, question)
- **Hit Rate**: Typically 30-50% in production

**Example:**
```python
provider = ArchaeologyContextProvider(repo_path=".", cache_size=500)

# First query - cache miss
context1 = provider.get_context_sync("auth.py", "Why JWT?")
# query_time_ms: ~800ms

# Same query - cache hit
context2 = provider.get_context_sync("auth.py", "Why JWT?")
# query_time_ms: ~2ms

# Check performance
stats = provider.get_cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Avg query time: {stats.avg_query_time_ms:.0f}ms")
```

### Timeouts

Default timeout: 2 seconds per query. Configurable:

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    max_query_time_s=5.0  # 5 second timeout
)
```

## Error Handling

AIL gracefully degrades when components are unavailable:

```python
provider = ArchaeologyContextProvider(repo_path="/invalid/path")

context = provider.get_context_sync("file.py", "Why?")
# context.confidence == 0.0
# context.answer contains error message
```

**Common Scenarios:**
- **Invalid repo path**: ValueError on construction
- **CCA initialization failure**: Returns error context with confidence=0.0
- **Query timeout**: Returns timeout context with confidence=0.0
- **Network issues (GitHub)**: Falls back to git-only data

## Testing

Run the test suite:

```bash
# All tests
python3 -m pytest tests/test_ail/ -v

# Unit tests only
python3 -m pytest tests/test_ail/test_context_provider.py -v
python3 -m pytest tests/test_ail/test_agent_integration.py -v

# Integration tests (slower)
python3 -m pytest tests/test_ail/test_integration.py -v

# With coverage
python3 -m pytest tests/test_ail/ --cov=tools/ail --cov-report=html
```

**Test Coverage:**
- 47 unit tests
- 10 integration tests
- 100% coverage of critical paths

## Examples

### Example 1: Code Review Agent

```python
from ail import ArchaeologyContextProvider

provider = ArchaeologyContextProvider(repo_path=".")

# Agent is reviewing a pull request
context = provider.get_context_sync(
    "src/database/connection.py",
    "Why was connection pooling implemented this way? "
    "What alternatives were considered?"
)

if context.has_high_confidence:
    print(f"High-confidence answer ({context.confidence:.0%}):")
    print(context.answer)
    print(f"\nBased on {len(context.sources)} sources")
```

### Example 2: Refactoring Assistant

```python
from ail import ArchaeologyContextProvider, get_context_from_input

provider = ArchaeologyContextProvider(repo_path=".")

# Agent wants to refactor
agent_input = "I need to refactor src/auth.py to support OAuth"

context = get_context_from_input(provider, agent_input)

if context:
    # Provide historical context to inform refactoring
    print("Historical Context for Refactoring:")
    print(context.to_markdown())
```

### Example 3: Debugging Assistant

```python
from ail.agent_integration import detect_task_type, formulate_question

agent_input = "Why is the authentication failing for some users?"

# Detect this is a debugging task
task_type = detect_task_type(agent_input)  # "debug"

# Formulate debugging-specific question
question = formulate_question(agent_input, task_type)
# "What was the intended behavior? What bugs were previously fixed?"

context = provider.get_context_sync("auth.py", question)
```

### Example 4: Batch Processing

```python
# Process multiple files efficiently
files_to_analyze = ["auth.py", "database.py", "api.py"]

for file_path in files_to_analyze:
    context = provider.get_context_sync(
        file_path,
        "What is the architectural purpose of this module?"
    )

    print(f"\n{file_path}:")
    print(f"  Confidence: {context.confidence:.0%}")
    print(f"  Sources: {context.source_count}")
    print(f"  Cached: {context.cached}")

# Check overall performance
stats = provider.get_cache_stats()
print(f"\nCache hit rate: {stats.hit_rate:.1%}")
```

## CLI Tools

### Test Context Provider

```bash
python3 tools/ail/context_provider.py . auth.py "Why was JWT chosen?"
```

### Test Agent Integration

```bash
python3 tools/ail/agent_integration.py . "Why does auth.py use JWT?"
```

## Configuration

### Environment Variables

```bash
# Optional: GitHub integration
export GITHUB_TOKEN=ghp_...

# Provider will automatically use token for enhanced context
```

### GitHub Integration

```python
provider = ArchaeologyContextProvider(
    repo_path=".",
    github_owner="anthropics",
    github_repo="claude-code",
    github_token=os.environ.get("GITHUB_TOKEN"),
)
```

## Logging

Configure logging level:

```python
import logging

logging.basicConfig(level=logging.INFO)
# or
logging.basicConfig(level=logging.DEBUG)
```

**Log levels:**
- `INFO`: Initialization, major operations
- `DEBUG`: Cache hits/misses, detailed operations
- `WARNING`: Timeouts, degraded functionality
- `ERROR`: Failures, exceptions

## Future Enhancements (Sprint 2+)

Sprint 1 provides the foundation. Future sprints will add:

- **Sprint 2**: Agent API integration (REST/GraphQL)
- **Sprint 3**: Real-time indexing and live updates
- **Sprint 4**: Multi-repository context
- **Sprint 5**: Custom embedding models
- **Sprint 6**: Agent feedback loop for improved answers

## Dependencies

**Required:**
- Python 3.9+
- numpy>=1.21.0
- requests>=2.28.0

**Optional:**
- faiss-cpu>=1.7.4 (for 10k+ documents)
- anthropic>=0.18.0 (future embeddings API)

Install:
```bash
pip install -r tools/requirements.txt
```

## License

Part of the ClaudeAgents project. See main project LICENSE.

## Contributing

See main project CONTRIBUTING.md for guidelines.

## Support

For issues or questions:
1. Check test files for usage examples
2. Review integration tests for real-world scenarios
3. Open an issue on the main project repository
