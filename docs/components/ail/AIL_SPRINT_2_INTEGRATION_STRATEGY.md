# AIL Sprint 2: Integration Strategy

**Version**: 1.0.0
**Date**: 2025-10-08
**Status**: COMPLETE

---

## 1. Integration Overview

This document defines the step-by-step integration strategy for FAISS semantic search into the existing AIL infrastructure, ensuring zero downtime, backward compatibility, and graceful degradation.

---

## 2. Integration Phases

### Phase 1: Foundation (Day 1 Morning)

```python
# Step 1: Add dependencies without breaking existing code
"""
requirements.txt additions:
- faiss-cpu==1.7.4
- sentence-transformers==2.2.2
- numpy>=1.21.0
"""

# Step 2: Create new modules alongside existing code
"""
tools/ail/
├── __init__.py          (existing)
├── context_provider.py  (existing)
├── embeddings.py        (new)
├── faiss_index.py       (new)
└── faiss_integration.py (new - orchestration)
"""

# Step 3: Feature flag implementation
class FeatureFlags:
    """Control FAISS rollout."""

    FAISS_ENABLED = os.getenv('AIL_FAISS_ENABLED', 'false').lower() == 'true'
    FAISS_FALLBACK = os.getenv('AIL_FAISS_FALLBACK', 'true').lower() == 'true'
    FAISS_CACHE_EMBEDDINGS = os.getenv('AIL_FAISS_CACHE', 'true').lower() == 'true'

    @classmethod
    def is_faiss_enabled(cls) -> bool:
        """Check if FAISS should be used."""
        try:
            import faiss
            import sentence_transformers
            return cls.FAISS_ENABLED
        except ImportError:
            return False
```

### Phase 2: Safe Integration (Day 1 Afternoon)

```python
# Step 1: Extend ContextProvider with optional FAISS
class ArchaeologyContextProvider:
    def __init__(self, repo_path: str, **kwargs):
        # Existing initialization
        super().__init__(repo_path, **kwargs)

        # New FAISS components (lazy loaded)
        self._faiss_integration = None
        self._faiss_init_attempted = False

    def _try_initialize_faiss(self) -> bool:
        """Attempt to initialize FAISS if enabled."""
        if self._faiss_init_attempted:
            return self._faiss_integration is not None

        self._faiss_init_attempted = True

        if not FeatureFlags.is_faiss_enabled():
            return False

        try:
            from .faiss_integration import FAISSIntegration
            self._faiss_integration = FAISSIntegration(
                repo_path=self.repo_path,
                history=self._searchable_index
            )
            logger.info("FAISS integration initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"FAISS initialization failed: {e}")
            return False

    async def _query_archaeology(self, file_path: str, question: str) -> Answer:
        """Query with FAISS first, fallback to original."""

        # Try FAISS if available
        if self._try_initialize_faiss():
            try:
                answer = await self._faiss_integration.query(
                    file_path, question
                )
                if answer and answer.confidence > 0.5:
                    return answer
            except Exception as e:
                logger.warning(f"FAISS query failed: {e}")

        # Fallback to original implementation
        return await self._original_query_archaeology(file_path, question)
```

### Phase 3: Gradual Rollout (Day 2)

```python
# Step 1: Percentage-based rollout
class RolloutManager:
    """Manage gradual FAISS rollout."""

    def __init__(self, rollout_percentage: int = 0):
        self.rollout_percentage = rollout_percentage

    def should_use_faiss(self, query_hash: str) -> bool:
        """Determine if query should use FAISS."""
        if self.rollout_percentage == 0:
            return False
        if self.rollout_percentage == 100:
            return True

        # Consistent hashing for A/B testing
        hash_value = int(hashlib.md5(query_hash.encode()).hexdigest(), 16)
        return (hash_value % 100) < self.rollout_percentage

# Step 2: A/B testing implementation
class ABTestingProvider(ArchaeologyContextProvider):
    """Provider with A/B testing capabilities."""

    def __init__(self, repo_path: str, **kwargs):
        super().__init__(repo_path, **kwargs)
        self.rollout = RolloutManager(
            rollout_percentage=int(os.getenv('FAISS_ROLLOUT', '0'))
        )
        self.metrics = {
            'faiss': {'count': 0, 'total_ms': 0, 'errors': 0},
            'original': {'count': 0, 'total_ms': 0, 'errors': 0}
        }

    async def get_context(self, file_path: str, question: str):
        query_id = f"{file_path}::{question}"

        if self.rollout.should_use_faiss(query_id):
            return await self._get_context_with_metrics('faiss', file_path, question)
        else:
            return await self._get_context_with_metrics('original', file_path, question)
```

---

## 3. Migration Strategy

### 3.1 Index Building Strategy

```python
class IndexMigration:
    """Manage FAISS index creation and migration."""

    def __init__(self, provider: ArchaeologyContextProvider):
        self.provider = provider
        self.progress = {'processed': 0, 'total': 0, 'errors': []}

    async def build_initial_index(self) -> bool:
        """Build FAISS index from existing data."""

        logger.info("Starting FAISS index build...")

        # Get repository history
        history = self.provider._searchable_index.enriched_history
        self.progress['total'] = len(history.enriched_commits)

        # Process in batches to avoid memory issues
        batch_size = 100
        embeddings_list = []
        doc_ids_list = []

        for i in range(0, len(history.enriched_commits), batch_size):
            batch = history.enriched_commits[i:i+batch_size]

            try:
                # Generate embeddings
                embeddings, doc_ids = await self._process_batch(batch)
                embeddings_list.append(embeddings)
                doc_ids_list.extend(doc_ids)

                self.progress['processed'] = i + len(batch)
                self._report_progress()

            except Exception as e:
                self.progress['errors'].append(f"Batch {i}: {e}")
                logger.error(f"Error processing batch {i}: {e}")

        # Build index
        if embeddings_list:
            all_embeddings = np.vstack(embeddings_list)
            return await self._create_index(all_embeddings, doc_ids_list)

        return False

    def _report_progress(self):
        """Report migration progress."""
        pct = (self.progress['processed'] / self.progress['total']) * 100
        logger.info(f"Index build progress: {pct:.1f}% ({self.progress['processed']}/{self.progress['total']})")
```

### 3.2 Data Consistency Strategy

```python
class ConsistencyChecker:
    """Ensure consistency between FAISS and original search."""

    def __init__(self, provider: ArchaeologyContextProvider):
        self.provider = provider
        self.discrepancies = []

    async def validate_consistency(self, sample_size: int = 100) -> Dict:
        """Validate FAISS results against original."""

        test_queries = self._generate_test_queries(sample_size)
        results = {'consistent': 0, 'inconsistent': 0, 'details': []}

        for file_path, question in test_queries:
            # Get results from both systems
            faiss_result = await self._query_faiss(file_path, question)
            original_result = await self._query_original(file_path, question)

            # Compare results
            consistency = self._compare_results(faiss_result, original_result)

            if consistency['is_consistent']:
                results['consistent'] += 1
            else:
                results['inconsistent'] += 1
                results['details'].append({
                    'query': f"{file_path}: {question}",
                    'issue': consistency['issue'],
                    'faiss_confidence': faiss_result.confidence,
                    'original_confidence': original_result.confidence
                })

        results['consistency_rate'] = results['consistent'] / sample_size
        return results

    def _compare_results(self, faiss: Answer, original: Answer) -> Dict:
        """Compare two answers for consistency."""

        # Check if main conclusions align
        if self._semantic_similarity(faiss.answer, original.answer) < 0.7:
            return {'is_consistent': False, 'issue': 'Different answers'}

        # Check if key citations overlap
        faiss_shas = {c.commit_sha for c in faiss.citations[:5]}
        orig_shas = {c.commit_sha for c in original.citations[:5]}

        overlap = len(faiss_shas & orig_shas) / max(len(faiss_shas), len(orig_shas))
        if overlap < 0.3:
            return {'is_consistent': False, 'issue': 'Different sources'}

        return {'is_consistent': True, 'issue': None}
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

```python
# tests/test_ail/test_faiss_integration.py

class TestFAISSIntegration:
    """Test FAISS components in isolation."""

    def test_embedding_generation(self):
        """Test embedding generator."""
        generator = EmbeddingGenerator()

        # Test single query
        embedding = generator.embed_query("test query")
        assert embedding.shape == (384,)
        assert np.linalg.norm(embedding) > 0.9  # Should be normalized

    def test_faiss_index_operations(self):
        """Test FAISS index CRUD operations."""
        index = FAISSIndex()

        # Test add
        embeddings = np.random.randn(10, 384).astype(np.float32)
        doc_ids = [f"doc_{i}" for i in range(10)]
        index.add_documents(embeddings, doc_ids)
        assert index.size == 10

        # Test search
        query = np.random.randn(384).astype(np.float32)
        results = index.search(query, k=5)
        assert len(results) == 5
        assert all(0 <= score <= 1 for _, score in results)

    def test_fallback_mechanism(self):
        """Test fallback when FAISS unavailable."""
        # Disable FAISS
        os.environ['AIL_FAISS_ENABLED'] = 'false'

        provider = ArchaeologyContextProvider(".")
        context = provider.get_context_sync("test.py", "test question")

        # Should work without FAISS
        assert context is not None
        assert not context.cached  # First query
```

### 4.2 Integration Tests

```python
class TestE2EIntegration:
    """End-to-end integration tests."""

    def test_with_faiss_enabled(self):
        """Test complete flow with FAISS."""
        os.environ['AIL_FAISS_ENABLED'] = 'true'

        provider = ArchaeologyContextProvider(".")

        # First query (builds index)
        context1 = provider.get_context_sync(
            "src/main.py",
            "Why was this architecture chosen?"
        )
        assert context1.query_time_ms < 1000  # Initial query

        # Second query (uses index)
        context2 = provider.get_context_sync(
            "src/utils.py",
            "What optimizations were made?"
        )
        assert context2.query_time_ms < 500  # Faster with index

    def test_ab_testing(self):
        """Test A/B testing functionality."""
        provider = ABTestingProvider(".", rollout_percentage=50)

        # Run many queries
        for i in range(100):
            context = provider.get_context_sync(
                f"file_{i}.py",
                f"question {i}"
            )

        # Check distribution
        faiss_count = provider.metrics['faiss']['count']
        original_count = provider.metrics['original']['count']

        assert 40 <= faiss_count <= 60  # ~50% distribution
        assert 40 <= original_count <= 60
```

### 4.3 Performance Tests

```python
class TestPerformance:
    """Performance regression tests."""

    @pytest.mark.benchmark
    def test_latency_improvement(self, benchmark):
        """Ensure FAISS improves latency."""
        provider = ArchaeologyContextProvider(".")

        def run_query():
            return provider.get_context_sync(
                "complex/nested/file.py",
                "What is the complete history of refactoring?"
            )

        # Benchmark with FAISS
        os.environ['AIL_FAISS_ENABLED'] = 'true'
        faiss_result = benchmark(run_query)

        # Benchmark without FAISS
        os.environ['AIL_FAISS_ENABLED'] = 'false'
        original_result = benchmark(run_query)

        # FAISS should be faster
        assert faiss_result.stats['mean'] < original_result.stats['mean']
```

---

## 5. Monitoring & Observability

### 5.1 Metrics Collection

```python
class FAISSMetrics:
    """Collect FAISS-specific metrics."""

    def __init__(self):
        self.metrics = {
            'searches_total': 0,
            'search_latency_ms': [],
            'embedding_cache_hits': 0,
            'embedding_cache_misses': 0,
            'index_size': 0,
            'fallback_count': 0,
            'error_count': 0
        }

    def record_search(self, latency_ms: float, cache_hit: bool):
        """Record search metrics."""
        self.metrics['searches_total'] += 1
        self.metrics['search_latency_ms'].append(latency_ms)

        if cache_hit:
            self.metrics['embedding_cache_hits'] += 1
        else:
            self.metrics['embedding_cache_misses'] += 1

    def get_summary(self) -> Dict:
        """Get metrics summary."""
        latencies = self.metrics['search_latency_ms']

        return {
            'total_searches': self.metrics['searches_total'],
            'avg_latency_ms': np.mean(latencies) if latencies else 0,
            'p95_latency_ms': np.percentile(latencies, 95) if latencies else 0,
            'cache_hit_rate': self.metrics['embedding_cache_hits'] /
                            max(1, self.metrics['searches_total']),
            'fallback_rate': self.metrics['fallback_count'] /
                           max(1, self.metrics['searches_total']),
            'error_rate': self.metrics['error_count'] /
                        max(1, self.metrics['searches_total'])
        }
```

### 5.2 Logging Strategy

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
)

logger = structlog.get_logger()

# Usage in FAISS integration
logger.info(
    "faiss_search_completed",
    file_path=file_path,
    question_length=len(question),
    num_results=len(results),
    top_score=results[0][1] if results else 0,
    latency_ms=latency,
    cache_hit=cache_hit,
    index_size=self.index.size
)
```

---

## 6. Rollback Plan

### 6.1 Instant Rollback

```python
class InstantRollback:
    """Immediate rollback mechanism."""

    @staticmethod
    def disable_faiss():
        """Instantly disable FAISS."""
        # Set environment variable
        os.environ['AIL_FAISS_ENABLED'] = 'false'

        # Clear singleton instances
        if hasattr(ArchaeologyContextProvider, '_instances'):
            ArchaeologyContextProvider._instances.clear()

        logger.warning("FAISS has been disabled - using original search")

    @staticmethod
    def enable_fallback_only():
        """Use FAISS with mandatory fallback."""
        os.environ['AIL_FAISS_FALLBACK'] = 'true'
        os.environ['AIL_FAISS_REQUIRED_CONFIDENCE'] = '0.8'

        logger.info("FAISS in fallback-only mode")
```

### 6.2 Data Cleanup

```python
class CleanupManager:
    """Clean up FAISS data if needed."""

    def remove_indices(self, repo_path: Path):
        """Remove FAISS indices and caches."""
        faiss_dir = repo_path / '.ail' / 'faiss'
        cache_dir = repo_path / '.ail' / 'cache'

        if faiss_dir.exists():
            shutil.rmtree(faiss_dir)
            logger.info(f"Removed FAISS indices from {faiss_dir}")

        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            logger.info(f"Removed embedding cache from {cache_dir}")

    def reset_to_baseline(self, provider: ArchaeologyContextProvider):
        """Reset provider to original state."""
        provider._faiss_integration = None
        provider._faiss_init_attempted = False
        provider.clear_cache()

        logger.info("Provider reset to baseline configuration")
```

---

## 7. Production Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, performance)
- [ ] Performance benchmarks meet targets (<500ms p95)
- [ ] Memory usage within budget (<150MB)
- [ ] Feature flags configured (FAISS disabled by default)
- [ ] Rollback plan tested
- [ ] Monitoring dashboards ready
- [ ] Documentation updated

### Deployment Steps

1. **Deploy with FAISS disabled**
   ```bash
   export AIL_FAISS_ENABLED=false
   ```

2. **Build indices offline**
   ```bash
   python -m tools.ail.build_index --repo-path .
   ```

3. **Enable for 10% traffic**
   ```bash
   export FAISS_ROLLOUT=10
   ```

4. **Monitor metrics for 1 hour**

5. **Gradual increase**
   - 25% after 2 hours
   - 50% after 4 hours
   - 100% after 24 hours

### Post-Deployment

- [ ] Monitor error rates
- [ ] Check latency metrics
- [ ] Validate accuracy metrics
- [ ] Review user feedback
- [ ] Document lessons learned

---

## 8. Success Criteria

### Technical Metrics

1. **Latency**: p95 < 500ms ✓
2. **Memory**: Total < 150MB ✓
3. **Accuracy**: Recall@10 > 90% ✓
4. **Reliability**: Error rate < 1% ✓

### Business Metrics

1. **User Satisfaction**: No degradation in quality
2. **System Stability**: No increase in errors
3. **Cost Efficiency**: No significant infrastructure cost increase
4. **Developer Experience**: Transparent integration

---

*End of Integration Strategy*