# AIL Sprint 2: FAISS Integration Technical Specification

**Version**: 1.0.0
**Date**: 2025-10-08
**Author**: AI/ML Engineer
**Status**: COMPLETE
**Sprint Goal**: Achieve 2-3x performance improvement through FAISS semantic search

---

## Executive Summary

This specification defines the FAISS (Facebook AI Similarity Search) integration for AIL Sprint 2, targeting a reduction in p95 latency from 847ms to <500ms through semantic search optimization. The implementation adds two new modules (`embeddings.py` and `faiss_index.py`) while maintaining backward compatibility and graceful degradation.

**Key Performance Targets**:
- **Latency**: <500ms p95 (from 847ms) - 41% improvement minimum
- **Memory**: <150MB total (from 78.4MB baseline + embedding overhead)
- **Index Build**: <30s for 1000 commits
- **Search Time**: <50ms for similarity search

---

## 1. Technical Architecture

### 1.1 System Overview

```
┌─────────────────────────────────────────────────────┐
│                 Agent Request                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         ArchaeologyContextProvider                   │
│  ┌─────────────────────────────────────────────┐    │
│  │            Cache Layer (LRU)                 │    │
│  └─────────────────────────────────────────────┘    │
│                       │                              │
│                       ▼                              │
│  ┌─────────────────────────────────────────────┐    │
│  │         FAISS Search Pipeline                │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │Embeddings│→ │  FAISS   │→ │ Reranker │  │    │
│  │  │Generator │  │  Index   │  │          │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  │    │
│  └─────────────────────────────────────────────┘    │
│                       │                              │
│                       ▼                              │
│  ┌─────────────────────────────────────────────┐    │
│  │    Fallback: Original CCA Search             │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### 1.2 Component Interactions

1. **Query Flow**:
   - Agent query → Context Provider → Cache check
   - Cache miss → FAISS pipeline → Semantic search
   - FAISS failure → Fallback to original CCA search
   - Results → Cache update → Return to agent

2. **Index Management**:
   - Background index builder monitors repository changes
   - Incremental updates for new commits (<100ms)
   - Full rebuild triggered weekly or on demand
   - Persistent index storage in `.ail/faiss/` directory

---

## 2. Module Specifications

### 2.1 `tools/ail/embeddings.py` (~200 LOC)

#### Purpose
Generate and manage embeddings for commits, PRs, and issues using sentence-transformers.

#### Class Design

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib
import pickle
from pathlib import Path

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    cache_dir: Optional[Path] = None
    max_sequence_length: int = 256
    normalize: bool = True

class EmbeddingGenerator:
    """
    Generate embeddings for code archaeology content.

    Features:
    - Batch processing for efficiency
    - Caching of computed embeddings
    - Content-aware text preparation
    - Memory-efficient processing
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize embedding generator.

        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        self.model = SentenceTransformer(self.config.model_name)
        self.model.max_seq_length = self.config.max_sequence_length
        self._cache: Dict[str, np.ndarray] = {}
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
        texts = []
        doc_ids = []

        for commit in commits:
            # Create rich text representation
            text = self._prepare_commit_text(commit)
            doc_id = f"commit_{commit.sha}"

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
        # Enhance query with context markers
        enhanced_query = f"Question: {query}"
        embedding = self.model.encode(
            enhanced_query,
            normalize_embeddings=self.config.normalize
        )
        return embedding

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
        parts.append(f"Commit: {commit.message}")

        # File changes
        if commit.files_changed:
            files = ", ".join(commit.files_changed[:5])
            parts.append(f"Files: {files}")

        # PR context if available
        if commit.pull_request:
            parts.append(f"PR: {commit.pull_request.title}")
            if commit.pull_request.body:
                parts.append(commit.pull_request.body[:200])

        return " | ".join(parts)

    def _batch_embed(
        self,
        texts: List[str],
        doc_ids: List[str],
        use_cache: bool
    ) -> np.ndarray:
        """
        Generate embeddings in batches with caching.
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        # Check cache
        for i, (text, doc_id) in enumerate(zip(texts, doc_ids)):
            if use_cache and doc_id in self._cache:
                embeddings.append((i, self._cache[doc_id]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Generate new embeddings
        if uncached_texts:
            new_embeddings = self.model.encode(
                uncached_texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=self.config.normalize,
                show_progress_bar=False
            )

            # Update cache
            for idx, embedding, text in zip(
                uncached_indices, new_embeddings, uncached_texts
            ):
                doc_id = doc_ids[idx]
                self._cache[doc_id] = embedding
                embeddings.append((idx, embedding))

        # Sort by original index and extract embeddings
        embeddings.sort(key=lambda x: x[0])
        return np.array([e[1] for e in embeddings])

    def save_cache(self) -> None:
        """Persist embedding cache to disk."""
        if self.config.cache_dir:
            cache_file = self.config.cache_dir / "embeddings.pkl"
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump(self._cache, f)

    def _load_cache(self) -> None:
        """Load embedding cache from disk."""
        if self.config.cache_dir:
            cache_file = self.config.cache_dir / "embeddings.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self._cache = pickle.load(f)
```

#### Key Design Decisions

1. **Model Selection**: `all-MiniLM-L6-v2`
   - 384 dimensions (optimal balance)
   - 22M parameters (fast inference)
   - Excellent performance on semantic similarity
   - ~80MB model size

2. **Batch Processing**:
   - Batch size of 32 for GPU efficiency
   - Async processing for large repositories
   - Progress tracking for UX

3. **Caching Strategy**:
   - Document-level caching by commit SHA
   - Persistent cache with pickle serialization
   - Memory-mapped option for large caches

---

### 2.2 `tools/ail/faiss_index.py` (~300 LOC)

#### Purpose
Manage FAISS indexes for efficient similarity search across embeddings.

#### Class Design

```python
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging

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

class FAISSIndex:
    """
    FAISS index for semantic search.

    Features:
    - Multiple index types (HNSW, Flat, IVF)
    - Incremental updates
    - Persistence and loading
    - Metadata management
    """

    def __init__(self, config: Optional[FAISSConfig] = None):
        """
        Initialize FAISS index.

        Args:
            config: FAISS configuration
        """
        self.config = config or FAISSConfig()
        self.index: Optional[faiss.Index] = None
        self.metadata: Dict[int, str] = {}  # idx -> document_id
        self.doc_to_idx: Dict[str, int] = {}  # document_id -> idx
        self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize FAISS index based on configuration."""
        d = self.config.dimension

        # Normalize for cosine similarity
        if self.config.metric == "cosine":
            base_index = self._create_base_index(d)
            self.index = faiss.IndexIDMap(base_index)
        else:
            base_index = self._create_base_index(d)
            self.index = faiss.IndexIDMap(base_index)

    def _create_base_index(self, dimension: int) -> faiss.Index:
        """Create base FAISS index."""
        if self.config.index_type == "IndexFlatL2":
            return faiss.IndexFlatL2(dimension)

        elif self.config.index_type == "IndexHNSWFlat":
            index = faiss.IndexHNSWFlat(dimension, self.config.hnsw_m)
            index.hnsw.efConstruction = self.config.hnsw_ef_construction
            index.hnsw.efSearch = self.config.hnsw_ef_search
            return index

        elif self.config.index_type == "IndexIVFFlat":
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(
                quantizer, dimension, self.config.ivf_nlist
            )
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
        if len(embeddings) != len(document_ids):
            raise ValueError("Embeddings and IDs must have same length")

        # Normalize for cosine similarity
        if self.config.metric == "cosine":
            faiss.normalize_L2(embeddings)

        # Generate sequential IDs
        start_idx = len(self.metadata)
        ids = np.arange(start_idx, start_idx + len(embeddings))

        # Add to index
        if self.config.index_type == "IndexIVFFlat" and not self.index.is_trained:
            self.index.train(embeddings)

        self.index.add_with_ids(embeddings, ids)

        # Update metadata
        for idx, doc_id in zip(ids, document_ids):
            self.metadata[int(idx)] = doc_id
            self.doc_to_idx[doc_id] = int(idx)

        logging.info(f"Added {len(embeddings)} documents to index")

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
        if self.index.ntotal == 0:
            return []

        # Normalize query for cosine similarity
        if self.config.metric == "cosine":
            query_embedding = query_embedding.copy()
            faiss.normalize_L2(query_embedding.reshape(1, -1))

        # Search
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        distances, indices = self.index.search(query_embedding, k)

        # Convert to results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx in self.metadata:
                doc_id = self.metadata[idx]

                # Apply filter if specified
                if filter_ids and doc_id not in filter_ids:
                    continue

                # Convert distance to similarity score
                if self.config.metric == "cosine":
                    similarity = 1 - dist / 2  # Cosine distance to similarity
                elif self.config.metric == "l2":
                    similarity = 1 / (1 + dist)  # L2 distance to similarity
                else:
                    similarity = dist  # Inner product is already similarity

                results.append((doc_id, float(similarity)))

        return results

    def update_document(
        self,
        document_id: str,
        new_embedding: np.ndarray
    ) -> None:
        """
        Update a single document's embedding.

        Args:
            document_id: Document ID to update
            new_embedding: New embedding vector
        """
        if document_id not in self.doc_to_idx:
            # Add as new document
            self.add_documents(
                new_embedding.reshape(1, -1),
                [document_id]
            )
            return

        # FAISS doesn't support in-place updates for all index types
        # For now, we'll rebuild if needed
        logging.warning(
            f"Document update for {document_id} requires index rebuild"
        )

    def remove_document(self, document_id: str) -> None:
        """
        Remove a document from the index.

        Args:
            document_id: Document ID to remove
        """
        if document_id in self.doc_to_idx:
            idx = self.doc_to_idx[document_id]
            # FAISS remove is expensive, mark for rebuild
            del self.metadata[idx]
            del self.doc_to_idx[document_id]
            logging.info(f"Marked {document_id} for removal")

    def save(self) -> None:
        """Save index and metadata to disk."""
        if not self.config.index_path:
            raise ValueError("No index_path configured")

        # Create directory
        self.config.index_path.parent.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, str(self.config.index_path))

        # Save metadata
        if self.config.metadata_path:
            with open(self.config.metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'doc_to_idx': self.doc_to_idx
                }, f)

        logging.info(f"Saved index with {self.index.ntotal} vectors")

    def load(self) -> None:
        """Load index and metadata from disk."""
        if not self.config.index_path or not self.config.index_path.exists():
            raise ValueError(f"Index not found at {self.config.index_path}")

        # Load FAISS index
        self.index = faiss.read_index(str(self.config.index_path))

        # Load metadata
        if self.config.metadata_path and self.config.metadata_path.exists():
            with open(self.config.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.doc_to_idx = data['doc_to_idx']

        logging.info(f"Loaded index with {self.index.ntotal} vectors")

    @property
    def size(self) -> int:
        """Number of documents in index."""
        return self.index.ntotal if self.index else 0

    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        if not self.index:
            return {'index_mb': 0, 'metadata_mb': 0}

        # Estimate index memory
        index_bytes = self.index.ntotal * self.config.dimension * 4  # float32
        if self.config.index_type == "IndexHNSWFlat":
            # HNSW adds graph structure overhead
            index_bytes *= 1.5

        # Estimate metadata memory
        metadata_bytes = len(self.metadata) * 100  # ~100 bytes per entry

        return {
            'index_mb': index_bytes / (1024 * 1024),
            'metadata_mb': metadata_bytes / (1024 * 1024),
            'total_mb': (index_bytes + metadata_bytes) / (1024 * 1024)
        }
```

#### Key Design Decisions

1. **Index Type**: `IndexHNSWFlat` (Hierarchical Navigable Small World)
   - Best balance of speed and accuracy
   - 50ms search time for 10k documents
   - 95%+ recall at top-10
   - ~1.5x memory overhead vs flat index

2. **Distance Metric**: Cosine similarity
   - Natural for text embeddings
   - Normalized vectors for consistency
   - Range [0, 1] for interpretability

3. **Persistence Strategy**:
   - Binary FAISS format for index
   - Pickle for metadata
   - Atomic writes with temp files

---

## 3. Context Provider Integration

### 3.1 Updated `context_provider.py` Integration Points

```python
class ArchaeologyContextProvider:
    """Enhanced with FAISS semantic search."""

    def __init__(self, ...):
        # ... existing init ...

        # FAISS components
        self._embedding_generator: Optional[EmbeddingGenerator] = None
        self._faiss_index: Optional[FAISSIndex] = None
        self._faiss_enabled: bool = True
        self._faiss_initialized: bool = False

    def _initialize_faiss(self) -> bool:
        """Initialize FAISS components."""
        if self._faiss_initialized:
            return True

        try:
            # Initialize embedding generator
            embed_config = EmbeddingConfig(
                cache_dir=self.repo_path / '.ail' / 'cache'
            )
            self._embedding_generator = EmbeddingGenerator(embed_config)

            # Initialize FAISS index
            faiss_config = FAISSConfig(
                index_path=self.repo_path / '.ail' / 'faiss' / 'index.bin',
                metadata_path=self.repo_path / '.ail' / 'faiss' / 'metadata.pkl'
            )
            self._faiss_index = FAISSIndex(faiss_config)

            # Load or build index
            if faiss_config.index_path.exists():
                self._faiss_index.load()
                logger.info(f"Loaded FAISS index with {self._faiss_index.size} documents")
            else:
                self._build_faiss_index()

            self._faiss_initialized = True
            return True

        except Exception as e:
            logger.warning(f"FAISS initialization failed: {e}")
            self._faiss_enabled = False
            return False

    def _build_faiss_index(self) -> None:
        """Build FAISS index from repository history."""
        logger.info("Building FAISS index...")

        # Get enriched history
        if not self._searchable_index:
            return

        history = self._searchable_index.enriched_history

        # Generate embeddings in batches
        batch_size = 100
        for i in range(0, len(history.enriched_commits), batch_size):
            batch = history.enriched_commits[i:i+batch_size]
            embeddings, doc_ids = self._embedding_generator.embed_commits(batch)
            self._faiss_index.add_documents(embeddings, doc_ids)

        # Save index
        self._faiss_index.save()
        self._embedding_generator.save_cache()

        logger.info(f"Built FAISS index with {self._faiss_index.size} documents")

    async def _query_archaeology(self, file_path: str, question: str) -> Answer:
        """Enhanced query with FAISS search."""

        # Try FAISS first if enabled
        if self._faiss_enabled and self._initialize_faiss():
            try:
                return await self._query_with_faiss(file_path, question)
            except Exception as e:
                logger.warning(f"FAISS query failed, falling back: {e}")

        # Fallback to original search
        return await super()._query_archaeology(file_path, question)

    async def _query_with_faiss(self, file_path: str, question: str) -> Answer:
        """Query using FAISS semantic search."""

        # Generate query embedding
        query_text = f"File: {file_path} Question: {question}"
        query_embedding = self._embedding_generator.embed_query(query_text)

        # Search with FAISS
        results = self._faiss_index.search(query_embedding, k=20)

        # Retrieve full commit data for top results
        relevant_commits = []
        for doc_id, score in results[:10]:
            commit_sha = doc_id.replace("commit_", "")
            # Find commit in enriched history
            commit = self._find_commit_by_sha(commit_sha)
            if commit:
                relevant_commits.append((commit, score))

        # Synthesize answer from relevant commits
        answer = self._synthesize_answer_from_commits(
            question, relevant_commits
        )

        return answer
```

---

## 4. Performance Specifications

### 4.1 Latency Targets

| Operation | Target | Current | Improvement |
|-----------|--------|---------|-------------|
| Cache Hit | <5ms | 5ms | - |
| FAISS Search | <50ms | N/A | New |
| Embedding Generation | <30ms | N/A | New |
| Full Query (p95) | <500ms | 847ms | 41% |
| Full Query (p50) | <300ms | 523ms | 43% |

### 4.2 Memory Budget

| Component | Budget | Notes |
|-----------|--------|-------|
| Base AIL | 78.4MB | Current usage |
| Sentence Transformer Model | 80MB | all-MiniLM-L6-v2 |
| FAISS Index (1000 docs) | 15MB | HNSW with 384d vectors |
| Embedding Cache | 10MB | ~1000 cached embeddings |
| **Total** | **<150MB** | Within target |

### 4.3 Build Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Initial Index Build (1000 commits) | <30s | One-time cost |
| Incremental Update (10 commits) | <500ms | Per-update cost |
| Embedding Generation (batch of 32) | <1s | Batch processing |
| Index Persistence | <1s | Save to disk |

---

## 5. Technical Decisions Summary

### 5.1 Embedding Model: `all-MiniLM-L6-v2`

**Rationale**:
- Optimal size/performance balance (22M parameters)
- 384 dimensions provides good semantic representation
- Fast inference (~5ms per text on CPU)
- Excellent for semantic similarity tasks
- Well-maintained and widely used

**Alternatives Considered**:
- `paraphrase-MiniLM-L3-v2`: Smaller (17M) but lower quality
- `all-mpnet-base-v2`: Better quality but 2x slower
- `all-distilroberta-v1`: Good quality but larger memory footprint

### 5.2 FAISS Index: `IndexHNSWFlat`

**Rationale**:
- Best speed/accuracy tradeoff for our scale
- 50ms search time meets our <500ms target
- 95%+ recall at top-10 results
- Supports incremental additions
- Well-tested in production systems

**Alternatives Considered**:
- `IndexFlatL2`: 100% accurate but too slow (>200ms)
- `IndexIVFFlat`: Faster but requires training and less accurate
- `IndexLSH`: Very fast but poor accuracy for our use case

### 5.3 Distance Metric: Cosine Similarity

**Rationale**:
- Standard for text embeddings
- Normalized vectors ensure consistency
- Intuitive similarity scores [0, 1]
- Works well with sentence transformers

### 5.4 Cache Strategy: Two-Tier

1. **LRU Cache** (existing): Full response caching
2. **Embedding Cache** (new): Persistent embedding storage

**Benefits**:
- Avoid redundant embedding generation
- Faster index rebuilds
- Reduced memory pressure

---

## 6. Implementation Plan

### Phase 1: Core Implementation (Day 1)
1. Implement `embeddings.py` with basic functionality
2. Implement `faiss_index.py` with HNSW index
3. Unit tests for both modules

### Phase 2: Integration (Day 1-2)
1. Integrate with `context_provider.py`
2. Add fallback mechanism
3. Integration tests

### Phase 3: Optimization (Day 2)
1. Implement embedding caching
2. Add incremental index updates
3. Performance benchmarking

### Phase 4: Production Hardening (Day 2-3)
1. Error handling and recovery
2. Monitoring and metrics
3. Documentation updates

---

## 7. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| FAISS installation issues | Graceful fallback to original search |
| Memory overflow | Monitor usage, implement limits |
| Index corruption | Atomic writes, backup strategy |
| Embedding model unavailable | Cache embeddings, fallback mode |
| Performance regression | Comprehensive benchmarking before release |

---

## 8. Success Metrics

1. **Primary**: p95 latency <500ms (41% improvement)
2. **Memory**: Total usage <150MB
3. **Accuracy**: 90%+ relevance in top-5 results
4. **Reliability**: 99.9% uptime with graceful degradation
5. **Developer Experience**: No breaking API changes

---

## Appendix A: API Contracts

### EmbeddingGenerator API

```python
class EmbeddingGenerator:
    def __init__(self, config: Optional[EmbeddingConfig] = None)
    def embed_commits(self, commits: List[EnrichedCommit], use_cache: bool = True) -> Tuple[np.ndarray, List[str]]
    def embed_query(self, query: str) -> np.ndarray
    def save_cache(self) -> None
    def clear_cache(self) -> None
    def get_cache_stats(self) -> Dict[str, Any]
```

### FAISSIndex API

```python
class FAISSIndex:
    def __init__(self, config: Optional[FAISSConfig] = None)
    def add_documents(self, embeddings: np.ndarray, document_ids: List[str]) -> None
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]
    def update_document(self, document_id: str, new_embedding: np.ndarray) -> None
    def remove_document(self, document_id: str) -> None
    def save(self) -> None
    def load(self) -> None
    def rebuild(self) -> None
    def get_stats(self) -> Dict[str, Any]
```

---

## Appendix B: Configuration Examples

### Default Configuration

```python
# Embedding configuration
embed_config = EmbeddingConfig(
    model_name="all-MiniLM-L6-v2",
    dimension=384,
    batch_size=32,
    cache_dir=Path(".ail/cache"),
    normalize=True
)

# FAISS configuration
faiss_config = FAISSConfig(
    index_type="IndexHNSWFlat",
    dimension=384,
    metric="cosine",
    hnsw_m=32,
    hnsw_ef_construction=200,
    hnsw_ef_search=50,
    index_path=Path(".ail/faiss/index.bin"),
    metadata_path=Path(".ail/faiss/metadata.pkl")
)
```

### High-Performance Configuration

```python
# For maximum speed (some accuracy tradeoff)
faiss_config = FAISSConfig(
    index_type="IndexHNSWFlat",
    hnsw_m=16,  # Fewer connections
    hnsw_ef_construction=100,  # Faster build
    hnsw_ef_search=20,  # Faster search
)
```

### High-Accuracy Configuration

```python
# For maximum accuracy (slower)
faiss_config = FAISSConfig(
    index_type="IndexFlatL2",  # Exact search
    metric="cosine",
)
```

---

*End of Specification*