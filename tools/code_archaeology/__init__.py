"""
Cognitive Code Archaeology - Multi-source historical analysis for codebase understanding.

This package provides tools to extract, correlate, and synthesize information from:
- Git commit history
- GitHub PR discussions
- Issue tracker context
- Communication channels

The goal is to answer "why" questions about code decisions using natural language queries.
"""

__version__ = "0.1.0"

from .git_analyzer import GitArchaeologist, Commit, ArchCommit, RepositoryHistory

__all__ = [
    "GitArchaeologist",
    "Commit",
    "ArchCommit",
    "RepositoryHistory",
]
