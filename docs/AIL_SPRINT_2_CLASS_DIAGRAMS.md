# AIL Sprint 2: FAISS Integration Class Diagrams

**Version**: 1.0.0
**Date**: 2025-10-08
**Status**: COMPLETE

---

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "Agent Layer"
        A[AI Agents]
    end

    subgraph "AIL Core"
        CP[ArchaeologyContextProvider]
        CACHE[LRUCache]
    end

    subgraph "FAISS Pipeline"
        EG[EmbeddingGenerator]
        FI[FAISSIndex]
        EC[EmbeddingCache]
    end

    subgraph "CCA Backend"
        GA[GitArchaeologist]
        GH[GitHubArchaeologist]
        CS[ContextSynthesizer]
    end

    A --> CP
    CP --> CACHE
    CP --> EG
    CP --> FI
    EG --> EC
    CP --> CS
    CS --> GA
    CS --> GH

    style A fill:#e1f5fe
    style CP fill:#b3e5fc
    style EG fill:#ffecb3
    style FI fill:#ffecb3
    style EC fill:#ffecb3
```

---

## 2. EmbeddingGenerator Class Diagram

```mermaid
classDiagram
    class EmbeddingGenerator {
        -config: EmbeddingConfig
        -model: SentenceTransformer
        -_cache: Dict[str, ndarray]
        -_cache_hits: int
        -_cache_misses: int
        +__init__(config: EmbeddingConfig)
        +embed_commits(commits: List[EnrichedCommit]) Tuple[ndarray, List[str]]
        +embed_query(query: str) ndarray
        +embed_batch(texts: List[str]) ndarray
        +save_cache() None
        +load_cache() None
        +clear_cache() None
        +get_cache_stats() Dict
        -_prepare_commit_text(commit: EnrichedCommit) str
        -_prepare_pr_text(pr: PullRequest) str
        -_batch_embed(texts: List[str]) ndarray
        -_normalize_embeddings(embeddings: ndarray) ndarray
    }

    class EmbeddingConfig {
        +model_name: str = "all-MiniLM-L6-v2"
        +dimension: int = 384
        +batch_size: int = 32
        +cache_dir: Optional[Path]
        +max_sequence_length: int = 256
        +normalize: bool = True
        +device: str = "cpu"
        +show_progress: bool = False
    }

    class EmbeddingCache {
        -cache_dir: Path
        -embeddings: Dict[str, ndarray]
        -metadata: Dict[str, Any]
        +save(embeddings: Dict) None
        +load() Dict[str, ndarray]
        +get(key: str) Optional[ndarray]
        +put(key: str, embedding: ndarray) None
        +exists(key: str) bool
        +size() int
    }

    EmbeddingGenerator --> EmbeddingConfig
    EmbeddingGenerator --> EmbeddingCache
    EmbeddingGenerator ..> SentenceTransformer : uses

    note for EmbeddingGenerator "Generates semantic embeddings\nfor commits, PRs, and queries\nwith intelligent caching"
```

---

## 3. FAISSIndex Class Diagram

```mermaid
classDiagram
    class FAISSIndex {
        -config: FAISSConfig
        -index: faiss.Index
        -metadata: Dict[int, str]
        -doc_to_idx: Dict[str, int]
        -_last_rebuild: datetime
        -_total_searches: int
        +__init__(config: FAISSConfig)
        +add_documents(embeddings: ndarray, ids: List[str]) None
        +search(query: ndarray, k: int) List[Tuple[str, float]]
        +search_batch(queries: ndarray, k: int) List[List[Tuple]]
        +update_document(id: str, embedding: ndarray) None
        +remove_document(id: str) None
        +save() None
        +load() None
        +rebuild() None
        +optimize() None
        +get_stats() Dict
        +get_memory_usage() Dict
        -_initialize_index() None
        -_create_base_index(dim: int) faiss.Index
        -_train_index(embeddings: ndarray) None
    }

    class FAISSConfig {
        +index_type: str = "IndexHNSWFlat"
        +dimension: int = 384
        +metric: str = "cosine"
        +hnsw_m: int = 32
        +hnsw_ef_construction: int = 200
        +hnsw_ef_search: int = 50
        +ivf_nlist: int = 100
        +ivf_nprobe: int = 10
        +index_path: Optional[Path]
        +metadata_path: Optional[Path]
        +auto_optimize: bool = True
        +max_memory_mb: int = 100
    }

    class IndexManager {
        -indices: Dict[str, FAISSIndex]
        -active_index: str
        +create_index(name: str, config: FAISSConfig) FAISSIndex
        +get_index(name: str) FAISSIndex
        +switch_index(name: str) None
        +delete_index(name: str) None
        +list_indices() List[str]
    }

    FAISSIndex --> FAISSConfig
    IndexManager --> FAISSIndex : manages
    FAISSIndex ..> faiss : uses

    note for FAISSIndex "High-performance similarity search\nwith multiple index types\nand incremental updates"
```

---

## 4. Enhanced ArchaeologyContextProvider

```mermaid
classDiagram
    class ArchaeologyContextProvider {
        -repo_path: Path
        -cache: LRUCache
        -stats: CacheStats
        -_embedding_generator: EmbeddingGenerator
        -_faiss_index: FAISSIndex
        -_faiss_enabled: bool
        -_context_synthesizer: ContextSynthesizer
        +__init__(repo_path: str, config: Dict)
        +get_context(file: str, question: str) ArchaeologicalContext
        +get_context_sync(file: str, question: str) ArchaeologicalContext
        +clear_cache() None
        +rebuild_index() None
        +get_stats() Dict
        -_initialize_faiss() bool
        -_build_faiss_index() None
        -_query_with_faiss(file: str, question: str) Answer
        -_query_archaeology(file: str, question: str) Answer
        -_synthesize_answer(commits: List) Answer
    }

    class ArchaeologicalContext {
        +file_path: str
        +question: str
        +answer: str
        +sources: List[ContextSource]
        +confidence: float
        +cached: bool
        +query_time_ms: float
        +search_method: str
        +to_markdown() str
        +to_json() Dict
    }

    class FAISSIntegration {
        -provider: ArchaeologyContextProvider
        -embedding_gen: EmbeddingGenerator
        -faiss_index: FAISSIndex
        +initialize() bool
        +search(query: str, k: int) List[SearchResult]
        +add_commit(commit: EnrichedCommit) None
        +update_index() None
        +get_performance_metrics() Dict
    }

    ArchaeologyContextProvider --> LRUCache
    ArchaeologyContextProvider --> EmbeddingGenerator
    ArchaeologyContextProvider --> FAISSIndex
    ArchaeologyContextProvider --> ContextSynthesizer
    ArchaeologyContextProvider ..> ArchaeologicalContext : creates
    FAISSIntegration --> ArchaeologyContextProvider
    FAISSIntegration --> EmbeddingGenerator
    FAISSIntegration --> FAISSIndex

    note for ArchaeologyContextProvider "Enhanced with FAISS\nsemantic search\nwhile maintaining\nbackward compatibility"
```

---

## 5. Search Pipeline Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Provider as ContextProvider
    participant Cache as LRUCache
    participant Embedder as EmbeddingGenerator
    participant Index as FAISSIndex
    participant CCA as ContextSynthesizer

    Agent->>Provider: get_context(file, question)
    Provider->>Cache: check(cache_key)

    alt Cache Hit
        Cache-->>Provider: cached_result
        Provider-->>Agent: ArchaeologicalContext
    else Cache Miss
        Provider->>Embedder: embed_query(question)
        Embedder-->>Provider: query_embedding

        Provider->>Index: search(query_embedding, k=20)
        Index-->>Provider: [(doc_id, score), ...]

        alt FAISS Success
            Provider->>Provider: retrieve_commits(doc_ids)
            Provider->>CCA: synthesize_answer(commits, question)
            CCA-->>Provider: Answer
        else FAISS Failure
            Provider->>CCA: fallback_search(question)
            CCA-->>Provider: Answer
        end

        Provider->>Cache: put(cache_key, result)
        Provider-->>Agent: ArchaeologicalContext
    end
```

---

## 6. Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Processing"
        Q[Query Text]
        F[File Path]
    end

    subgraph "Embedding Pipeline"
        QE[Query Embedder]
        CE[Commit Embedder]
        EC[Embedding Cache]
    end

    subgraph "Search Layer"
        FAISS[FAISS Index]
        RERANK[Reranker]
    end

    subgraph "Synthesis"
        SYN[Answer Synthesizer]
        CIT[Citation Builder]
    end

    Q --> QE
    F --> QE
    QE --> FAISS
    CE --> EC
    EC --> FAISS
    FAISS --> RERANK
    RERANK --> SYN
    SYN --> CIT
    CIT --> Result[ArchaeologicalContext]

    style Q fill:#e3f2fd
    style F fill:#e3f2fd
    style Result fill:#c8e6c9
```

---

## 7. Component Relationships

```mermaid
classDiagram
    class SearchResult {
        +commit: EnrichedCommit
        +relevance_score: float
        +matched_content: str
        +source_type: str
    }

    class ContextSource {
        +commit_sha: str
        +commit_message: str
        +author: str
        +date: datetime
        +source_type: str
        +relevance_score: float
        +excerpt: str
        +url: str
        +from_citation(citation: Citation) ContextSource
    }

    class Answer {
        +question: str
        +answer: str
        +citations: List[Citation]
        +confidence: float
        +reasoning: str
        +search_method: str
        +credibility_score() float
    }

    class Citation {
        +commit_sha: str
        +commit_message: str
        +commit_date: datetime
        +author: str
        +source_type: str
        +source_id: Optional[str]
        +relevance_score: float
        +excerpt: str
        +url: str
    }

    SearchResult --> EnrichedCommit
    Answer --> Citation : contains
    ContextSource ..> Citation : from
    ArchaeologicalContext --> ContextSource : contains

    note for SearchResult "Intermediate search result\nbefore synthesis"
    note for Answer "Final synthesized answer\nwith supporting evidence"
```

---

## 8. Performance Monitoring Classes

```mermaid
classDiagram
    class PerformanceMonitor {
        -metrics: Dict[str, List[float]]
        -thresholds: Dict[str, float]
        +record_latency(operation: str, ms: float) None
        +record_memory(component: str, mb: float) None
        +check_thresholds() List[Alert]
        +get_p95_latency(operation: str) float
        +get_average_memory() float
        +export_metrics() Dict
    }

    class CacheStats {
        +hits: int
        +misses: int
        +total_queries: int
        +avg_query_time_ms: float
        +cache_size: int
        +max_cache_size: int
        +hit_rate() float
        +to_dict() Dict
    }

    class IndexStats {
        +total_documents: int
        +index_size_mb: float
        +searches_performed: int
        +avg_search_time_ms: float
        +last_rebuild: datetime
        +additions_since_rebuild: int
        +needs_optimization() bool
    }

    class Alert {
        +level: str
        +metric: str
        +value: float
        +threshold: float
        +message: str
        +timestamp: datetime
    }

    PerformanceMonitor --> Alert : generates
    ArchaeologyContextProvider --> CacheStats
    FAISSIndex --> IndexStats
    PerformanceMonitor --> CacheStats : monitors
    PerformanceMonitor --> IndexStats : monitors

    note for PerformanceMonitor "Tracks all performance metrics\nand generates alerts"
```

---

## 9. Error Handling & Fallback

```mermaid
stateDiagram-v2
    [*] --> QueryReceived
    QueryReceived --> CheckCache

    CheckCache --> CacheHit: Found
    CheckCache --> FAISSInit: Miss

    CacheHit --> [*]: Return Result

    FAISSInit --> FAISSSearch: Success
    FAISSInit --> FallbackSearch: Failure

    FAISSSearch --> Synthesis: Results Found
    FAISSSearch --> FallbackSearch: No Results/Error

    FallbackSearch --> Synthesis: CCA Search

    Synthesis --> CacheUpdate
    CacheUpdate --> [*]: Return Result

    note right of FAISSInit
        Try to initialize FAISS
        - Load model
        - Load index
        - Validate
    end note

    note right of FallbackSearch
        Original CCA search
        - TF-IDF based
        - Guaranteed to work
    end note
```

---

## 10. Deployment Configuration

```yaml
# AIL Sprint 2 Deployment Configuration

faiss:
  enabled: true
  fallback_enabled: true

  embedding:
    model: "all-MiniLM-L6-v2"
    dimension: 384
    batch_size: 32
    cache_enabled: true
    cache_dir: ".ail/cache/embeddings"

  index:
    type: "IndexHNSWFlat"
    metric: "cosine"
    hnsw:
      m: 32
      ef_construction: 200
      ef_search: 50
    persistence:
      dir: ".ail/faiss"
      auto_save: true
      save_interval_minutes: 30

  performance:
    max_memory_mb: 150
    max_search_time_ms: 50
    max_build_time_s: 30

  monitoring:
    enabled: true
    metrics_endpoint: "/metrics"
    alert_thresholds:
      latency_p95_ms: 500
      memory_mb: 150
      search_accuracy: 0.9
```

---

## Summary

This class diagram document provides:

1. **Complete UML diagrams** for all new components
2. **Sequence diagrams** showing interaction flows
3. **Data flow diagrams** for the search pipeline
4. **State diagrams** for error handling
5. **Deployment configuration** structure

The architecture ensures:
- **Modularity**: Clean separation of concerns
- **Extensibility**: Easy to add new index types or models
- **Reliability**: Comprehensive fallback mechanisms
- **Performance**: Optimized for <500ms p95 latency
- **Maintainability**: Clear interfaces and responsibilities

---

*End of Class Diagrams*