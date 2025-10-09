"""
Embedding generation for archaeological content.

This module provides the EmbeddingGenerator class that creates semantic embeddings
for commits, PRs, and issues using sentence-transformers, with intelligent caching
and batch processing for optimal performance.
"""

from __future__ import annotations

import hashlib
import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

# Import CCA components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_archaeology import EnrichedCommit, PullRequest, Issue

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""

    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    cache_dir: Optional[Path] = None
    max_sequence_length: int = 256
    normalize: bool = True
    device: str = "cpu"
    show_progress: bool = False

    def __post_init__(self):
        """Validate and set up configuration."""
        if self.cache_dir:
            self.cache_dir = Path(self.cache_dir)


class EmbeddingGenerator:
    """
    Generate embeddings for code archaeology content.

    Features:
    - Batch processing for efficiency
    - Caching of computed embeddings
    - Content-aware text preparation
    - Memory-efficient processing
    - Graceful degradation when sentence-transformers unavailable
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize embedding generator.

        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()

        # Initialize model if available
        self.model = None
        self._model_loaded = False

        if not HAS_SENTENCE_TRANSFORMERS:
            logger.warning("sentence-transformers not installed. Embedding generation disabled.")
        else:
            try:
                self.model = SentenceTransformer(
                    self.config.model_name,
                    device=self.config.device
                )
                self.model.max_seq_length = self.config.max_sequence_length
                self._model_loaded = True
                logger.info(f"Loaded embedding model: {self.config.model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self._model_loaded = False

        # Initialize cache
        self._cache: Dict[str, np.ndarray] = {}
        self._cache_hits = 0
        self._cache_misses = 0

        # Load persistent cache if configured
        if self.config.cache_dir:
            self._load_cache()

    def embed_commits(
        self,
        commits: List[EnrichedCommit],
        use_cache: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Generate embeddings for commits.

        Args:
            commits: List of enriched commits
            use_cache: Whether to use cached embeddings

        Returns:
            Tuple of (embeddings array, document IDs)
        """
        if not self._model_loaded:
            # Return zero embeddings if model not available
            logger.warning("Model not loaded, returning zero embeddings")
            doc_ids = [f"commit_{c.commit.sha}" for c in commits]
            embeddings = np.zeros((len(commits), self.config.dimension), dtype=np.float32)
            return embeddings, doc_ids

        texts = []
        doc_ids = []

        for commit in commits:
            # Create rich text representation
            text = self._prepare_commit_text(commit)
            doc_id = f"commit_{commit.commit.sha}"

            texts.append(text)
            doc_ids.append(doc_id)

        # Generate embeddings with batching
        embeddings = self._batch_embed(texts, doc_ids, use_cache)

        return embeddings, doc_ids

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query.

        Args:
            query: Natural language query

        Returns:
            Query embedding vector
        """
        if not self._model_loaded:
            # Return zero embedding if model not available
            logger.warning("Model not loaded, returning zero embedding")
            return np.zeros((self.config.dimension,), dtype=np.float32)

        # Enhance query with context markers
        enhanced_query = f"Question: {query}"

        try:
            embedding = self.model.encode(
                enhanced_query,
                normalize_embeddings=self.config.normalize,
                show_progress_bar=False
            )
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return np.zeros((self.config.dimension,), dtype=np.float32)

    def embed_batch(self, texts: List[str], use_cache: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings

        Returns:
            Array of embeddings
        """
        if not self._model_loaded:
            logger.warning("Model not loaded, returning zero embeddings")
            return np.zeros((len(texts), self.config.dimension), dtype=np.float32)

        # Generate unique IDs for texts based on content hash
        doc_ids = [self._get_cache_key(text) for text in texts]

        return self._batch_embed(texts, doc_ids, use_cache)

    def _prepare_commit_text(self, commit: EnrichedCommit) -> str:
        """
        Prepare rich text representation of commit.

        Combines:
        - Commit message
        - File changes summary
        - PR title and description (if available)
        - Key discussions
        """
        parts = []

        # Core commit info
        parts.append(f"Commit: {commit.commit.message}")

        # File changes
        if commit.commit.files_changed:
            files = ", ".join(commit.commit.files_changed[:5])
            parts.append(f"Files: {files}")

        # PR context if available
        if commit.pull_request:
            parts.append(f"PR: {commit.pull_request.title}")
            if commit.pull_request.body:
                # Truncate long PR descriptions
                body_preview = commit.pull_request.body[:200]
                parts.append(f"Description: {body_preview}")

        # Add author info
        parts.append(f"Author: {commit.commit.author}")

        return " | ".join(parts)

    def _prepare_pr_text(self, pr: PullRequest) -> str:
        """
        Prepare text representation of pull request.

        Args:
            pr: Pull request object

        Returns:
            Text representation for embedding
        """
        parts = []

        parts.append(f"PR #{pr.number}: {pr.title}")

        if pr.body:
            parts.append(f"Description: {pr.body[:300]}")

        parts.append(f"Author: {pr.author}")
        parts.append(f"State: {pr.state}")

        if pr.labels:
            parts.append(f"Labels: {', '.join(pr.labels)}")

        return " | ".join(parts)

    def _batch_embed(
        self,
        texts: List[str],
        doc_ids: List[str],
        use_cache: bool
    ) -> np.ndarray:
        """
        Generate embeddings in batches with caching.

        Args:
            texts: List of texts to embed
            doc_ids: List of document IDs
            use_cache: Whether to use cached embeddings

        Returns:
            Array of embeddings
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # Check cache
        for i, (text, doc_id) in enumerate(zip(texts, doc_ids)):
            if use_cache and doc_id in self._cache:
                embeddings.append((i, self._cache[doc_id]))
                self._cache_hits += 1
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                self._cache_misses += 1

        # Generate new embeddings
        if uncached_texts:
            try:
                new_embeddings = self.model.encode(
                    uncached_texts,
                    batch_size=self.config.batch_size,
                    normalize_embeddings=self.config.normalize,
                    show_progress_bar=self.config.show_progress
                )

                # Ensure float32 type
                new_embeddings = new_embeddings.astype(np.float32)

                # Update cache
                for idx, embedding, text in zip(
                    uncached_indices, new_embeddings, uncached_texts
                ):
                    doc_id = doc_ids[idx]
                    self._cache[doc_id] = embedding
                    embeddings.append((idx, embedding))

            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
                # Return zero embeddings for failed items
                for idx in uncached_indices:
                    embedding = np.zeros((self.config.dimension,), dtype=np.float32)
                    embeddings.append((idx, embedding))

        # Sort by original index and extract embeddings
        embeddings.sort(key=lambda x: x[0])
        return np.array([e[1] for e in embeddings], dtype=np.float32)

    def _get_cache_key(self, text: str) -> str:
        """
        Generate cache key for text.

        Args:
            text: Text to generate key for

        Returns:
            SHA256 hash of text
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def save_cache(self) -> None:
        """Persist embedding cache to disk."""
        if not self.config.cache_dir:
            logger.warning("No cache directory configured, skipping cache save")
            return

        try:
            cache_file = self.config.cache_dir / "embeddings.pkl"
            cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(cache_file, 'wb') as f:
                pickle.dump(self._cache, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info(f"Saved {len(self._cache)} cached embeddings to {cache_file}")

        except Exception as e:
            logger.error(f"Failed to save embedding cache: {e}")

    def _load_cache(self) -> None:
        """Load embedding cache from disk."""
        if not self.config.cache_dir:
            return

        cache_file = self.config.cache_dir / "embeddings.pkl"
        if not cache_file.exists():
            logger.debug(f"No cache file found at {cache_file}")
            return

        try:
            with open(cache_file, 'rb') as f:
                self._cache = pickle.load(f)

            logger.info(f"Loaded {len(self._cache)} cached embeddings from {cache_file}")

        except Exception as e:
            logger.error(f"Failed to load embedding cache: {e}")
            self._cache = {}

    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Cleared embedding cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0

        return {
            'cache_size': len(self._cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate,
            'memory_mb': self._estimate_cache_memory(),
        }

    def _estimate_cache_memory(self) -> float:
        """
        Estimate memory usage of cache in MB.

        Returns:
            Estimated memory in megabytes
        """
        if not self._cache:
            return 0.0

        # Each embedding is dimension * 4 bytes (float32)
        # Plus overhead for dictionary keys
        embedding_bytes = len(self._cache) * self.config.dimension * 4
        key_bytes = len(self._cache) * 64  # Approximate for SHA256 keys

        return (embedding_bytes + key_bytes) / (1024 * 1024)

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        if not self._model_loaded:
            return {
                'loaded': False,
                'model_name': self.config.model_name,
                'error': 'Model not loaded'
            }

        return {
            'loaded': True,
            'model_name': self.config.model_name,
            'dimension': self.config.dimension,
            'max_sequence_length': self.config.max_sequence_length,
            'device': self.config.device,
            'normalize': self.config.normalize,
        }