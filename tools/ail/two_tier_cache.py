"""
Unified two-tier caching interface.

This module combines L1 (exact-match LRU) and L2 (semantic similarity) caches
into a unified interface with transparent fallback and cache promotion.

Features:
- Transparent L1 → L2 → Backend fallback
- Cache promotion (L2 hits → L1)
- Unified statistics tracking
- Optional L2 disable for A/B testing
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from tools.ail.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


@dataclass
class TwoTierCacheStats:
    """Statistics for two-tier cache system."""

    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0

    @property
    def total_queries(self) -> int:
        """Total queries processed."""
        return self.l1_hits + self.l1_misses

    @property
    def l1_hit_rate(self) -> float:
        """L1 cache hit rate."""
        if self.total_queries == 0:
            return 0.0
        return self.l1_hits / self.total_queries

    @property
    def l2_hit_rate(self) -> float:
        """L2 cache hit rate (of L1 misses)."""
        if self.l1_misses == 0:
            return 0.0
        return self.l2_hits / self.l1_misses

    @property
    def combined_hit_rate(self) -> float:
        """Combined cache hit rate."""
        if self.total_queries == 0:
            return 0.0
        return (self.l1_hits + self.l2_hits) / self.total_queries

    @property
    def cache_miss_rate(self) -> float:
        """Cache miss rate (queries hitting backend)."""
        return 1.0 - self.combined_hit_rate

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            'l1_hits': self.l1_hits,
            'l1_misses': self.l1_misses,
            'l1_hit_rate': f"{self.l1_hit_rate:.1%}",
            'l2_hits': self.l2_hits,
            'l2_misses': self.l2_misses,
            'l2_hit_rate': f"{self.l2_hit_rate:.1%}",
            'combined_hit_rate': f"{self.combined_hit_rate:.1%}",
            'cache_miss_rate': f"{self.cache_miss_rate:.1%}",
            'total_queries': self.total_queries,
        }


class TwoTierCache:
    """
    Two-tier caching: L1 (exact match) + L2 (semantic similarity).

    Features:
    - Transparent fallback L1 → L2 → Backend
    - Cache promotion (L2 hits → L1 for future exact matches)
    - Unified statistics tracking
    - Optional L2 disable for A/B testing
    - Adaptive similarity threshold tuning

    Usage:
        l1_cache = LRUCache(max_size=1000)
        l2_cache = SemanticCache(max_entries=500, similarity_threshold=0.85)
        cache = TwoTierCache(l1_cache=l1_cache, l2_cache=l2_cache)

        # Try cache
        result = cache.get(file_path, query, cache_key)
        if result:
            cached_value, cache_level, similarity = result
        else:
            # Query backend and populate cache
            backend_result = query_backend(file_path, query)
            cache.put(file_path, query, cache_key, backend_result)
    """

    def __init__(
        self,
        l1_cache: Any,  # LRUCache
        l2_cache: Optional[SemanticCache] = None,
        l2_enabled: bool = True,
    ):
        """
        Initialize two-tier cache.

        Args:
            l1_cache: Exact match LRU cache (Sprint 1)
            l2_cache: Semantic similarity cache (Sprint 2)
            l2_enabled: Enable L2 semantic cache (default: True)
        """
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache if l2_enabled else None

        # Combined statistics
        self.stats = TwoTierCacheStats()

        logger.info(
            f"TwoTierCache initialized: L2={'enabled' if self.l2_cache else 'disabled'}"
        )

    def get(
        self,
        file_path: str,
        query: str,
        cache_key: str
    ) -> Optional[Tuple[Any, str, float]]:
        """
        Get from two-tier cache.

        Args:
            file_path: File path being queried
            query: Natural language query
            cache_key: L1 exact-match cache key

        Returns:
            Tuple of (result, cache_level, similarity_score) or None
            - cache_level: "L1" or "L2"
            - similarity_score: 1.0 for L1, 0.85-1.0 for L2
        """
        # Try L1 first (exact match)
        l1_result = self.l1_cache.get(cache_key)
        if l1_result:
            self.stats.l1_hits += 1
            logger.debug("L1 cache hit")
            return (l1_result, "L1", 1.0)

        self.stats.l1_misses += 1

        # Try L2 (semantic similarity)
        if self.l2_cache and self.l2_cache.enabled:
            l2_result = self.l2_cache.get(file_path, query)
            if l2_result:
                result, similarity = l2_result
                self.stats.l2_hits += 1
                logger.debug(f"L2 cache hit: similarity={similarity:.3f}")

                # Promote to L1 for future exact matches
                self.l1_cache.put(cache_key, result)

                return (result, "L2", similarity)

            self.stats.l2_misses += 1

        # Both caches missed
        return None

    def put(
        self,
        file_path: str,
        query: str,
        cache_key: str,
        result: Any
    ) -> None:
        """
        Put into both cache levels.

        Args:
            file_path: File path being queried
            query: Natural language query
            cache_key: L1 exact-match cache key
            result: ArchaeologicalContext to cache
        """
        # Add to L1 (exact match)
        self.l1_cache.put(cache_key, result)

        # Add to L2 (semantic)
        if self.l2_cache and self.l2_cache.enabled:
            self.l2_cache.put(file_path, query, result)

    def clear(self) -> None:
        """Clear both cache levels."""
        self.l1_cache.clear()
        if self.l2_cache:
            self.l2_cache.clear()
        logger.info("Two-tier cache cleared")

    def get_combined_stats(self) -> Dict[str, Any]:
        """
        Get combined statistics from both cache levels.

        Returns:
            Dictionary with comprehensive cache statistics
        """
        base_stats = self.stats.to_dict()

        # Add L2-specific stats if available
        if self.l2_cache and self.l2_cache.enabled:
            l2_stats = self.l2_cache.get_stats()
            base_stats['l2_avg_similarity'] = l2_stats.avg_similarity
            base_stats['l2_avg_lookup_time_ms'] = l2_stats.avg_lookup_time_ms
            base_stats['l2_cache_size'] = l2_stats.cache_size
            base_stats['l2_evictions'] = l2_stats.evictions

        # Add L1-specific stats
        base_stats['l1_cache_size'] = self.l1_cache.size

        return base_stats

    def get_stats(self) -> TwoTierCacheStats:
        """Get two-tier cache statistics object."""
        return self.stats

    @property
    def l1_enabled(self) -> bool:
        """Check if L1 cache is enabled."""
        return True  # L1 always enabled

    @property
    def l2_enabled(self) -> bool:
        """Check if L2 cache is enabled."""
        return self.l2_cache is not None and self.l2_cache.enabled
