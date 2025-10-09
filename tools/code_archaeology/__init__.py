"""
Cognitive Code Archaeology - Multi-source historical analysis for codebase understanding.

This package provides tools to extract, correlate, and synthesize information from:
- Git commit history
- GitHub PR discussions
- Issue tracker context
- Communication channels

The goal is to answer "why" questions about code decisions using natural language queries.
"""

__version__ = "0.3.0"

from .git_analyzer import GitArchaeologist, Commit, ArchCommit, RepositoryHistory
from .github_integrator import (
    GitHubArchaeologist,
    EnrichedCommit,
    EnrichedHistory,
    PullRequest,
    Issue,
)
from .context_synthesizer import (
    ContextSynthesizer,
    SearchableIndex,
    Answer,
    Citation,
    SimpleEmbeddingProvider,
)

__all__ = [
    # Git Analysis
    "GitArchaeologist",
    "Commit",
    "ArchCommit",
    "RepositoryHistory",
    # GitHub Integration
    "GitHubArchaeologist",
    "EnrichedCommit",
    "EnrichedHistory",
    "PullRequest",
    "Issue",
    # Context Synthesis
    "ContextSynthesizer",
    "SearchableIndex",
    "Answer",
    "Citation",
    "SimpleEmbeddingProvider",
]
