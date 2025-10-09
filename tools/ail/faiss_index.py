"""
FAISS index management for semantic search.

This module provides the FAISSIndex class that manages FAISS indexes for efficient
similarity search across embeddings, with support for multiple index types,
incremental updates, and persistent storage.
"""

from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    faiss = None

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class FAISSConfig:
    """Configuration for FAISS index."""

    index_type: str = "IndexHNSWFlat"  # or "IndexFlatL2", "IndexIVFFlat"
    dimension: int = 384
    metric: str = "cosine"  # or "l2", "ip" (inner product)

    # HNSW parameters
    hnsw_m: int = 32  # Number of connections
    hnsw_ef_construction: int = 200  # Construction time accuracy
    hnsw_ef_search: int = 50  # Search time accuracy

    # IVF parameters (if using IndexIVFFlat)
    ivf_nlist: int = 100  # Number of clusters
    ivf_nprobe: int = 10  # Number of clusters to search

    # Storage
    index_path: Optional[Path] = None
    metadata_path: Optional[Path] = None

    # Performance
    auto_optimize: bool = True
    max_memory_mb: int = 100

    def __post_init__(self):
        """Validate and set up configuration."""
        if self.index_path:
            self.index_path = Path(self.index_path)
        if self.metadata_path:
            self.metadata_path = Path(self.metadata_path)


class FAISSIndex:
    """
    FAISS index for semantic search.

    Features:
    - Multiple index types (HNSW, Flat, IVF)
    - Incremental updates
    - Persistence and loading
    - Metadata management
    - Graceful degradation when FAISS unavailable
    """

    def __init__(self, config: Optional[FAISSConfig] = None):
        """
        Initialize FAISS index.

        Args:
            config: FAISS configuration
        """
        self.config = config or FAISSConfig()
        self.index: Optional[Any] = None  # faiss.Index
        self.metadata: Dict[int, str] = {}  # idx -> document_id
        self.doc_to_idx: Dict[str, int] = {}  # document_id -> idx

        # Performance tracking
        self._last_rebuild: Optional[datetime] = None
        self._total_searches: int = 0
        self._additions_since_rebuild: int = 0

        # Check if FAISS is available
        if not HAS_FAISS:
            logger.warning("FAISS not installed. Semantic search disabled.")
            self._faiss_available = False
        else:
            self._faiss_available = True
            self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize FAISS index based on configuration."""
        if not self._faiss_available:
            return

        try:
            d = self.config.dimension

            # Create base index based on type
            base_index = self._create_base_index(d)

            # Wrap with IDMap for document ID support
            self.index = faiss.IndexIDMap(base_index)

            logger.info(f"Initialized FAISS index: {self.config.index_type}")

        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            self._faiss_available = False

    def _create_base_index(self, dimension: int) -> Any:
        """
        Create base FAISS index.

        Args:
            dimension: Vector dimension

        Returns:
            FAISS index object
        """
        if self.config.index_type == "IndexFlatL2":
            # Exact search with L2 distance
            if self.config.metric == "cosine":
                # Use IP (inner product) for normalized vectors
                return faiss.IndexFlatIP(dimension)
            else:
                return faiss.IndexFlatL2(dimension)

        elif self.config.index_type == "IndexHNSWFlat":
            # Hierarchical Navigable Small World graph
            if self.config.metric == "cosine":
                index = faiss.IndexHNSWFlat(dimension, self.config.hnsw_m, faiss.METRIC_INNER_PRODUCT)
            else:
                index = faiss.IndexHNSWFlat(dimension, self.config.hnsw_m)

            # Set HNSW parameters
            index.hnsw.efConstruction = self.config.hnsw_ef_construction
            index.hnsw.efSearch = self.config.hnsw_ef_search

            return index

        elif self.config.index_type == "IndexIVFFlat":
            # Inverted File with Flat quantizer
            if self.config.metric == "cosine":
                quantizer = faiss.IndexFlatIP(dimension)
                index = faiss.IndexIVFFlat(
                    quantizer, dimension, self.config.ivf_nlist, faiss.METRIC_INNER_PRODUCT
                )
            else:
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFFlat(
                    quantizer, dimension, self.config.ivf_nlist
                )

            # Set search parameters
            index.nprobe = self.config.ivf_nprobe

            return index

        else:
            raise ValueError(f"Unknown index type: {self.config.index_type}")

    def add_documents(
        self,
        embeddings: np.ndarray,
        document_ids: List[str]
    ) -> None:
        """
        Add documents to the index.

        Args:
            embeddings: Document embeddings (n_docs, dimension)
            document_ids: List of document IDs
        """
        if not self._faiss_available or self.index is None:
            logger.warning("FAISS index not available")
            return

        if len(embeddings) != len(document_ids):
            raise ValueError("Embeddings and IDs must have same length")

        # Ensure float32 type
        embeddings = embeddings.astype(np.float32)

        # Normalize for cosine similarity
        if self.config.metric == "cosine":
            faiss.normalize_L2(embeddings)

        # Generate sequential IDs
        start_idx = len(self.metadata)
        ids = np.arange(start_idx, start_idx + len(embeddings), dtype=np.int64)

        try:
            # Train index if needed (for IVF)
            if self.config.index_type == "IndexIVFFlat":
                base_index = self.index.index  # Get base index from IDMap
                if not base_index.is_trained:
                    logger.info("Training IVF index...")
                    base_index.train(embeddings)

            # Add to index
            self.index.add_with_ids(embeddings, ids)

            # Update metadata
            for idx, doc_id in zip(ids, document_ids):
                self.metadata[int(idx)] = doc_id
                self.doc_to_idx[doc_id] = int(idx)

            self._additions_since_rebuild += len(embeddings)
            logger.info(f"Added {len(embeddings)} documents to index (total: {self.index.ntotal})")

        except Exception as e:
            logger.error(f"Failed to add documents to index: {e}")

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        filter_ids: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query vector
            k: Number of results
            filter_ids: Optional list of document IDs to search within

        Returns:
            List of (document_id, similarity_score) tuples
        """
        if not self._faiss_available or self.index is None:
            logger.warning("FAISS index not available")
            return []

        if self.index.ntotal == 0:
            logger.debug("Index is empty")
            return []

        # Ensure float32 type
        query_embedding = query_embedding.astype(np.float32)

        # Normalize query for cosine similarity
        if self.config.metric == "cosine":
            query_embedding = query_embedding.copy()
            faiss.normalize_L2(query_embedding.reshape(1, -1))

        # Reshape for FAISS
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        try:
            # Search
            # Request more results if we need to filter
            search_k = min(k * 3 if filter_ids else k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, search_k)

            # Convert to results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0:  # Invalid index
                    continue

                if idx not in self.metadata:
                    logger.warning(f"Index {idx} not found in metadata")
                    continue

                doc_id = self.metadata[idx]

                # Apply filter if specified
                if filter_ids and doc_id not in filter_ids:
                    continue

                # Convert distance to similarity score
                if self.config.metric == "cosine":
                    # For cosine with normalized vectors, distance is 1 - cosine_similarity
                    # With inner product on normalized vectors, distance IS the similarity
                    similarity = float(dist)
                elif self.config.metric == "l2":
                    # Convert L2 distance to similarity
                    similarity = 1.0 / (1.0 + float(dist))
                else:
                    # Inner product is already similarity
                    similarity = float(dist)

                results.append((doc_id, similarity))

                # Stop if we have enough results
                if len(results) >= k:
                    break

            self._total_searches += 1
            return results

        except Exception as e:
            logger.error(f"Failed to search index: {e}")
            return []

    def search_batch(
        self,
        query_embeddings: np.ndarray,
        k: int = 10
    ) -> List[List[Tuple[str, float]]]:
        """
        Search for similar documents with multiple queries.

        Args:
            query_embeddings: Query vectors (n_queries, dimension)
            k: Number of results per query

        Returns:
            List of result lists, one per query
        """
        if not self._faiss_available or self.index is None:
            logger.warning("FAISS index not available")
            return [[] for _ in range(len(query_embeddings))]

        if self.index.ntotal == 0:
            logger.debug("Index is empty")
            return [[] for _ in range(len(query_embeddings))]

        # Ensure float32 type
        query_embeddings = query_embeddings.astype(np.float32)

        # Normalize queries for cosine similarity
        if self.config.metric == "cosine":
            query_embeddings = query_embeddings.copy()
            faiss.normalize_L2(query_embeddings)

        try:
            # Batch search
            distances, indices = self.index.search(query_embeddings, k)

            # Convert to results
            all_results = []
            for query_dists, query_indices in zip(distances, indices):
                results = []
                for dist, idx in zip(query_dists, query_indices):
                    if idx < 0 or idx not in self.metadata:
                        continue

                    doc_id = self.metadata[idx]

                    # Convert distance to similarity
                    if self.config.metric == "cosine":
                        similarity = float(dist)
                    elif self.config.metric == "l2":
                        similarity = 1.0 / (1.0 + float(dist))
                    else:
                        similarity = float(dist)

                    results.append((doc_id, similarity))

                all_results.append(results)

            self._total_searches += len(query_embeddings)
            return all_results

        except Exception as e:
            logger.error(f"Failed to batch search index: {e}")
            return [[] for _ in range(len(query_embeddings))]

    def update_document(
        self,
        document_id: str,
        new_embedding: np.ndarray
    ) -> None:
        """
        Update a single document's embedding.

        Note: FAISS doesn't support efficient in-place updates for most index types.
        This method adds the document as new if not exists, or logs a warning if update needed.

        Args:
            document_id: Document ID to update
            new_embedding: New embedding vector
        """
        if not self._faiss_available:
            return

        if document_id not in self.doc_to_idx:
            # Add as new document
            self.add_documents(
                new_embedding.reshape(1, -1),
                [document_id]
            )
            return

        # FAISS doesn't support in-place updates efficiently
        # Mark for rebuild if this becomes common
        self._additions_since_rebuild += 1
        logger.warning(
            f"Document update for {document_id} requires index rebuild. "
            f"Consider calling rebuild() after batch updates."
        )

    def remove_document(self, document_id: str) -> None:
        """
        Remove a document from the index.

        Note: FAISS remove is expensive. This marks for rebuild rather than immediate removal.

        Args:
            document_id: Document ID to remove
        """
        if document_id in self.doc_to_idx:
            idx = self.doc_to_idx[document_id]
            # Mark for removal (actual removal happens on rebuild)
            del self.metadata[idx]
            del self.doc_to_idx[document_id]
            self._additions_since_rebuild += 1
            logger.info(f"Marked {document_id} for removal (rebuild required)")

    def save(self) -> None:
        """Save index and metadata to disk."""
        if not self._faiss_available or not self.index:
            logger.warning("No index to save")
            return

        if not self.config.index_path:
            logger.warning("No index_path configured, skipping save")
            return

        try:
            # Create directory
            self.config.index_path.parent.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            faiss.write_index(self.index, str(self.config.index_path))

            # Save metadata
            if self.config.metadata_path:
                self.config.metadata_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config.metadata_path, 'wb') as f:
                    pickle.dump({
                        'metadata': self.metadata,
                        'doc_to_idx': self.doc_to_idx,
                        'config': self.config,
                        'stats': {
                            'last_rebuild': self._last_rebuild,
                            'total_searches': self._total_searches,
                            'additions_since_rebuild': self._additions_since_rebuild,
                        }
                    }, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info(f"Saved index with {self.index.ntotal} vectors to {self.config.index_path}")

        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def load(self) -> None:
        """Load index and metadata from disk."""
        if not self._faiss_available:
            logger.warning("FAISS not available, cannot load index")
            return

        if not self.config.index_path or not self.config.index_path.exists():
            logger.warning(f"Index not found at {self.config.index_path}")
            return

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.config.index_path))

            # Load metadata
            if self.config.metadata_path and self.config.metadata_path.exists():
                with open(self.config.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', {})
                    self.doc_to_idx = data.get('doc_to_idx', {})

                    # Load stats
                    stats = data.get('stats', {})
                    self._last_rebuild = stats.get('last_rebuild')
                    self._total_searches = stats.get('total_searches', 0)
                    self._additions_since_rebuild = stats.get('additions_since_rebuild', 0)

            logger.info(f"Loaded index with {self.index.ntotal} vectors from {self.config.index_path}")

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            # Re-initialize empty index
            self._initialize_index()

    def rebuild(self) -> None:
        """
        Rebuild the index from scratch.

        This is useful after multiple updates/removals or for optimization.
        """
        logger.info("Rebuilding index...")

        # Save current documents
        doc_embeddings = []
        doc_ids = []

        if self.index and self.index.ntotal > 0:
            # Extract all valid documents
            for idx, doc_id in self.metadata.items():
                # Reconstruct would require storing embeddings
                logger.warning("Index rebuild requires stored embeddings (not implemented)")
                break

        # Re-initialize index
        self._initialize_index()

        # Re-add documents if we had stored embeddings
        # (This would require storing embeddings separately)

        self._last_rebuild = datetime.now()
        self._additions_since_rebuild = 0
        logger.info("Index rebuild complete")

    def optimize(self) -> None:
        """
        Optimize the index for better search performance.

        This may reorganize internal structures for faster search.
        """
        if not self._faiss_available or not self.index:
            return

        if self.config.index_type == "IndexHNSWFlat":
            # Adjust search parameters for better accuracy/speed tradeoff
            base_index = self.index.index  # Get base index from IDMap
            if hasattr(base_index, 'hnsw'):
                base_index.hnsw.efSearch = self.config.hnsw_ef_search
                logger.info(f"Optimized HNSW search parameters (efSearch={self.config.hnsw_ef_search})")

        elif self.config.index_type == "IndexIVFFlat":
            # Adjust nprobe for better accuracy
            base_index = self.index.index
            if hasattr(base_index, 'nprobe'):
                base_index.nprobe = self.config.ivf_nprobe
                logger.info(f"Optimized IVF search parameters (nprobe={self.config.ivf_nprobe})")

    @property
    def size(self) -> int:
        """Number of documents in index."""
        if self.index:
            return self.index.ntotal
        return 0

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get memory usage statistics.

        Returns:
            Dictionary with memory usage in MB
        """
        if not self.index:
            return {'index_mb': 0.0, 'metadata_mb': 0.0, 'total_mb': 0.0}

        # Estimate index memory
        index_bytes = self.index.ntotal * self.config.dimension * 4  # float32

        if self.config.index_type == "IndexHNSWFlat":
            # HNSW adds graph structure overhead
            # M connections per node, each connection is 4 bytes (int32)
            graph_bytes = self.index.ntotal * self.config.hnsw_m * 4
            index_bytes += graph_bytes
        elif self.config.index_type == "IndexIVFFlat":
            # IVF adds centroid storage
            centroid_bytes = self.config.ivf_nlist * self.config.dimension * 4
            index_bytes += centroid_bytes

        # Estimate metadata memory
        metadata_bytes = len(self.metadata) * 100  # ~100 bytes per entry

        return {
            'index_mb': index_bytes / (1024 * 1024),
            'metadata_mb': metadata_bytes / (1024 * 1024),
            'total_mb': (index_bytes + metadata_bytes) / (1024 * 1024)
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Dictionary with index statistics
        """
        memory_stats = self.get_memory_usage()

        return {
            'total_documents': self.size,
            'index_type': self.config.index_type,
            'dimension': self.config.dimension,
            'metric': self.config.metric,
            'searches_performed': self._total_searches,
            'last_rebuild': self._last_rebuild.isoformat() if self._last_rebuild else None,
            'additions_since_rebuild': self._additions_since_rebuild,
            'needs_optimization': self.needs_optimization(),
            'memory_mb': memory_stats['total_mb'],
            'faiss_available': self._faiss_available,
        }

    def needs_optimization(self) -> bool:
        """
        Check if index needs optimization.

        Returns:
            True if optimization recommended
        """
        # Suggest optimization after many additions
        if self._additions_since_rebuild > self.size * 0.2:  # >20% changes
            return True

        # Check memory usage
        memory_stats = self.get_memory_usage()
        if memory_stats['total_mb'] > self.config.max_memory_mb:
            return True

        return False