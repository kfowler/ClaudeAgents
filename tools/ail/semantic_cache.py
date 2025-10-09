"""
Semantic caching for archaeological queries.

This module implements L2 semantic similarity caching using FAISS vector search
to complement the L1 exact-match LRU cache. It catches queries with similar
meaning but different wording, targeting 20%+ additional cache hits.

Features:
- FAISS IndexFlatIP for fast similarity search (<50ms)
- Configurable similarity threshold (default 0.85)
- Hybrid LRU+LFU eviction policy
- Thread-safe operations
- Memory-bounded (max 500 entries ~3MB)

Performance Targets:
- L2 hit rate: 20%+ (of L1 misses)
- L2 lookup time: <50ms p95
- Memory usage: <20MB
"""

from __future__ import annotations

import time
import logging
import re
import threading
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None  # type: ignore

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    faiss = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class SemanticCacheEntry:
    """Entry in semantic cache with metadata."""

    query_text: str              # Normalized query
    file_path: str               # File being queried
    cached_result: Any           # ArchaeologicalContext
    embedding: np.ndarray        # Query embedding vector
    access_count: int = 0        # LFU tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    @property
    def age_seconds(self) -> float:
        """Age in seconds since creation."""
        return (datetime.now() - self.created_at).total_seconds()

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if entry is expired."""
        return self.age_seconds > ttl_seconds


@dataclass
class SemanticCacheStats:
    """Statistics for semantic cache performance."""

    hits: int = 0
    misses: int = 0
    total_queries: int = 0
    avg_similarity: float = 0.0
    avg_lookup_time_ms: float = 0.0
    cache_size: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        if self.total_queries == 0:
            return 0.0
        return self.hits / self.total_queries

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_queries': self.total_queries,
            'hit_rate': f"{self.hit_rate:.1%}",
            'avg_similarity': f"{self.avg_similarity:.3f}",
            'avg_lookup_time_ms': f"{self.avg_lookup_time_ms:.1f}ms",
            'cache_size': self.cache_size,
            'evictions': self.evictions,
        }


class SemanticCache:
    """
    Semantic caching using FAISS vector similarity search.

    Complements L1 exact-match cache by catching semantically similar
    queries with different wording.

    Features:
    - FAISS IndexFlatIP for fast similarity search
    - Configurable similarity threshold (default 0.85)
    - LRU + LFU hybrid eviction policy
    - Thread-safe operations
    - Memory-bounded (max 500 entries ~20MB)

    Performance Targets:
    - L2 hit rate: 20%+ (of L1 misses)
    - L2 lookup time: <50ms
    - Memory usage: <20MB
    """

    def __init__(
        self,
        embedding_provider: Optional[Any] = None,
        max_entries: int = 500,
        similarity_threshold: float = 0.85,
        ttl_seconds: int = 3600,
        enabled: bool = True,
    ):
        """
        Initialize semantic cache.

        Args:
            embedding_provider: Provider for query embeddings (reuses CCA's)
            max_entries: Maximum cache entries (default: 500)
            similarity_threshold: Minimum similarity for hit (default: 0.85)
            ttl_seconds: Time-to-live for entries (default: 3600 = 1 hour)
            enabled: Enable semantic cache (default: True)
        """
        if not HAS_NUMPY or not HAS_FAISS:
            logger.warning("FAISS or NumPy not available, semantic cache disabled")
            self.enabled = False
            return

        self.enabled = enabled
        if not enabled:
            logger.info("Semantic cache explicitly disabled")
            return

        # Configuration
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds

        # Embedding provider (reuse CCA's SimpleEmbeddingProvider)
        if embedding_provider is None:
            try:
                from code_archaeology import SimpleEmbeddingProvider
                self.embedding_provider = SimpleEmbeddingProvider(max_features=512)
            except ImportError:
                logger.warning("SimpleEmbeddingProvider not available, disabling semantic cache")
                self.enabled = False
                return
        else:
            self.embedding_provider = embedding_provider

        # Determine embedding dimension
        try:
            test_embedding = self.embedding_provider.embed(["test"])[0]
            dimension = len(test_embedding)
        except Exception:
            dimension = 512  # Default fallback

        # Initialize FAISS index (inner product for cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)
        self.dimension = dimension

        # Storage for cache entries (list indexed by FAISS index ID)
        self.entries: List[SemanticCacheEntry] = []

        # Statistics
        self.stats = SemanticCacheStats()

        # Thread safety
        self._lock = threading.RLock()

        logger.info(
            f"SemanticCache initialized: max_entries={max_entries}, "
            f"threshold={similarity_threshold}, ttl={ttl_seconds}s, dim={dimension}"
        )

    def normalize_query(self, query: str) -> str:
        """
        Normalize query for better similarity matching.

        Transformations:
        - Lowercase
        - Expand contractions
        - Remove excessive punctuation
        - Collapse whitespace

        Args:
            query: Raw query string

        Returns:
            Normalized query string
        """
        # Lowercase
        query = query.lower()

        # Expand common contractions
        contractions = {
            "what's": "what is", "isn't": "is not", "aren't": "are not",
            "won't": "will not", "can't": "cannot", "didn't": "did not",
            "doesn't": "does not", "haven't": "have not", "hasn't": "has not",
            "weren't": "were not", "wouldn't": "would not", "couldn't": "could not",
            "shouldn't": "should not",
        }
        for contraction, expansion in contractions.items():
            query = query.replace(contraction, expansion)

        # Remove excessive punctuation but keep question marks
        query = re.sub(r'[^\w\s?]', ' ', query)

        # Collapse whitespace
        query = ' '.join(query.split())

        return query

    def get(
        self,
        file_path: str,
        query: str
    ) -> Optional[Tuple[Any, float]]:
        """
        Query semantic cache for similar cached results.

        Args:
            file_path: File path being queried
            query: Natural language query

        Returns:
            Tuple of (cached_result, similarity_score) if hit, None if miss
        """
        if not self.enabled:
            return None

        start_time = time.time()

        with self._lock:
            self.stats.total_queries += 1

            # Empty cache
            if len(self.entries) == 0:
                self.stats.misses += 1
                return None

            # Normalize query
            normalized_query = self.normalize_query(query)

            # Create composite query for embedding (include file context)
            composite_query = f"{file_path}: {normalized_query}"

            # Generate embedding
            try:
                query_embedding = self.embedding_provider.embed([composite_query])[0]

                # Normalize for cosine similarity (IndexFlatIP expects normalized)
                norm = np.linalg.norm(query_embedding)
                if norm > 0:
                    query_embedding = query_embedding / norm
                else:
                    logger.warning("Zero norm embedding, skipping semantic cache")
                    self.stats.misses += 1
                    return None

            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
                self.stats.misses += 1
                return None

            # Search FAISS index (top-1 result)
            try:
                scores, indices = self.index.search(
                    query_embedding.reshape(1, -1).astype('float32'),
                    k=1
                )

                if len(indices[0]) == 0 or indices[0][0] == -1:
                    self.stats.misses += 1
                    return None

                top_score = float(scores[0][0])
                top_idx = int(indices[0][0])

            except Exception as e:
                logger.warning(f"FAISS search failed: {e}")
                self.stats.misses += 1
                return None

            # Check similarity threshold
            if top_score < self.similarity_threshold:
                self.stats.misses += 1
                lookup_time_ms = (time.time() - start_time) * 1000
                logger.debug(
                    f"Semantic cache miss: score={top_score:.3f} < "
                    f"threshold={self.similarity_threshold}"
                )
                return None

            # Check TTL expiration
            entry = self.entries[top_idx]
            if entry.is_expired(self.ttl_seconds):
                self.stats.misses += 1
                logger.debug(f"Semantic cache entry expired: age={entry.age_seconds:.0f}s")
                # Note: Expired entries removed during next eviction cycle
                return None

            # Cache hit!
            self.stats.hits += 1
            self.stats.avg_similarity = (
                (self.stats.avg_similarity * (self.stats.hits - 1) + top_score)
                / self.stats.hits
            )

            # Update entry metadata
            entry.access_count += 1
            entry.last_accessed = datetime.now()

            # Update stats
            lookup_time_ms = (time.time() - start_time) * 1000
            total_time = self.stats.avg_lookup_time_ms * (self.stats.total_queries - 1)
            self.stats.avg_lookup_time_ms = (total_time + lookup_time_ms) / self.stats.total_queries

            logger.debug(
                f"Semantic cache HIT: similarity={top_score:.3f}, "
                f"time={lookup_time_ms:.1f}ms"
            )

            return (entry.cached_result, top_score)

    def put(
        self,
        file_path: str,
        query: str,
        result: Any
    ) -> None:
        """
        Add query result to semantic cache.

        Args:
            file_path: File path being queried
            query: Natural language query
            result: ArchaeologicalContext to cache
        """
        if not self.enabled:
            return

        with self._lock:
            # Check capacity - evict if needed
            if len(self.entries) >= self.max_entries:
                self._evict_lru_lfu()

            # Normalize query
            normalized_query = self.normalize_query(query)

            # Create composite query
            composite_query = f"{file_path}: {normalized_query}"

            # Generate embedding
            try:
                query_embedding = self.embedding_provider.embed([composite_query])[0]

                # Normalize for cosine similarity
                norm = np.linalg.norm(query_embedding)
                if norm > 0:
                    query_embedding = query_embedding / norm
                else:
                    logger.warning("Zero norm embedding, skipping cache put")
                    return

            except Exception as e:
                logger.warning(f"Failed to generate embedding for cache entry: {e}")
                return

            # Create cache entry
            entry = SemanticCacheEntry(
                query_text=normalized_query,
                file_path=file_path,
                cached_result=result,
                embedding=query_embedding,
            )

            # Add to FAISS index
            try:
                self.index.add(query_embedding.reshape(1, -1).astype('float32'))
            except Exception as e:
                logger.warning(f"Failed to add to FAISS index: {e}")
                return

            # Add to entries list
            self.entries.append(entry)
            self.stats.cache_size = len(self.entries)

            logger.debug(f"Added to semantic cache: {file_path}::{normalized_query[:50]}")

    def _evict_lru_lfu(self) -> None:
        """
        Evict entries using hybrid LRU + LFU policy.

        Strategy:
        1. Remove expired entries first (TTL)
        2. If still over capacity, use score = recency + frequency
        3. Evict lowest scoring entries
        """
        # Step 1: Remove expired entries
        now = datetime.now()
        valid_indices = [
            i for i, entry in enumerate(self.entries)
            if not entry.is_expired(self.ttl_seconds)
        ]

        if len(valid_indices) < len(self.entries):
            # Rebuild index and entries with only valid entries
            evicted = len(self.entries) - len(valid_indices)
            self._rebuild_index(valid_indices)
            self.stats.evictions += evicted
            logger.debug(f"Evicted {evicted} expired entries")

        # Step 2: If still over capacity, use LRU + LFU score
        if len(self.entries) >= self.max_entries:
            # Calculate scores (higher = keep, lower = evict)
            scores = []
            max_access = max((e.access_count for e in self.entries), default=1)

            for entry in self.entries:
                # Recency: 0-1 (1 = just accessed)
                age_seconds = (now - entry.last_accessed).total_seconds()
                recency_score = 1.0 / (1.0 + age_seconds / 3600)  # Decay over hours

                # Frequency: normalize by max access count
                frequency_score = entry.access_count / max(1, max_access)

                # Hybrid score (weighted: 60% recency, 40% frequency)
                score = 0.6 * recency_score + 0.4 * frequency_score
                scores.append(score)

            # Keep top 80% (evict bottom 20%)
            target_size = int(self.max_entries * 0.8)
            keep_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:target_size]

            evicted_count = len(self.entries) - len(keep_indices)
            self._rebuild_index(keep_indices)
            self.stats.evictions += evicted_count

            logger.debug(
                f"Evicted {evicted_count} entries using LRU+LFU policy "
                f"(cache_size: {len(self.entries)})"
            )

    def _rebuild_index(self, keep_indices: List[int]) -> None:
        """
        Rebuild FAISS index with subset of entries.

        Args:
            keep_indices: Indices of entries to keep
        """
        # Extract entries and embeddings to keep
        new_entries = [self.entries[i] for i in keep_indices]

        if len(new_entries) == 0:
            embeddings = np.array([], dtype='float32').reshape(0, self.dimension)
        else:
            embeddings = np.array([e.embedding for e in new_entries], dtype='float32')

        # Rebuild FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)
        if len(embeddings) > 0:
            self.index.add(embeddings)

        # Update entries list
        self.entries = new_entries
        self.stats.cache_size = len(self.entries)

    def clear(self) -> None:
        """Clear all cache entries."""
        if not self.enabled:
            return

        with self._lock:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.entries = []
            self.stats.cache_size = 0
            logger.info("Semantic cache cleared")

    def get_stats(self) -> SemanticCacheStats:
        """Get cache statistics."""
        return self.stats

    @property
    def size(self) -> int:
        """Current cache size."""
        return len(self.entries)
