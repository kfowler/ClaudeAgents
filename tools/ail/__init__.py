"""
AIL (Archaeology Intelligence Layer) - Sprint 1 Foundation

This module provides archaeological context to AI agents by integrating with
the Cognitive Code Archaeology system. It enables agents to access historical
context about code decisions, architectural changes, and development patterns.

Sprint 1 Components:
- ArchaeologyContextProvider: Main interface for agents to query context
- Agent integration helpers for seamless context access
- LRU caching for performance optimization
- Error handling and graceful degradation
"""

__version__ = "1.0.0"

from .context_provider import (
    ArchaeologyContextProvider,
    ArchaeologicalContext,
    ContextSource,
    CacheStats,
)
from .agent_integration import (
    get_file_context,
    get_architectural_context,
    extract_file_path,
    formulate_question,
)

__all__ = [
    # Core provider
    "ArchaeologyContextProvider",
    "ArchaeologicalContext",
    "ContextSource",
    "CacheStats",
    # Agent helpers
    "get_file_context",
    "get_architectural_context",
    "extract_file_path",
    "formulate_question",
]
