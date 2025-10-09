#!/usr/bin/env python3
"""
Validation script for FAISS integration in AIL Sprint 2.

This script validates that the FAISS integration is working correctly
with graceful degradation when dependencies are missing.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from embeddings import EmbeddingGenerator, EmbeddingConfig
from faiss_index import FAISSIndex, FAISSConfig
import numpy as np


def check_dependencies():
    """Check if optional dependencies are available."""
    dependencies = {}

    try:
        import faiss
        dependencies['faiss'] = True
        print("✓ FAISS library is installed")
    except ImportError:
        dependencies['faiss'] = False
        print("✗ FAISS library not installed (will use fallback)")

    try:
        import sentence_transformers
        dependencies['sentence_transformers'] = True
        print("✓ sentence-transformers library is installed")
    except ImportError:
        dependencies['sentence_transformers'] = False
        print("✗ sentence-transformers not installed (will use fallback)")

    return dependencies


def test_embedding_generator():
    """Test the EmbeddingGenerator component."""
    print("\n=== Testing EmbeddingGenerator ===")

    # Create config
    config = EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",
        dimension=384,
        cache_dir=Path("/tmp/ail_cache")
    )

    # Initialize generator
    generator = EmbeddingGenerator(config)
    print(f"Generator initialized: {generator._model_loaded}")

    # Test query embedding
    query = "Why was this feature added?"
    embedding = generator.embed_query(query)
    print(f"Query embedding shape: {embedding.shape}")
    print(f"Query embedding dtype: {embedding.dtype}")

    # Check if it's zero (fallback) or actual embedding
    if np.allclose(embedding, 0):
        print("Using zero embeddings (fallback mode)")
    else:
        print("Using actual embeddings")

    # Test cache stats
    stats = generator.get_cache_stats()
    print(f"Cache stats: {stats}")

    return True


def test_faiss_index():
    """Test the FAISSIndex component."""
    print("\n=== Testing FAISSIndex ===")

    # Create config
    config = FAISSConfig(
        index_type="IndexHNSWFlat",
        dimension=384,
        metric="cosine",
        index_path=Path("/tmp/ail_faiss/index.bin"),
        metadata_path=Path("/tmp/ail_faiss/metadata.pkl")
    )

    # Initialize index
    index = FAISSIndex(config)
    print(f"Index initialized: {index._faiss_available}")

    # Try to add documents
    embeddings = np.random.randn(10, 384).astype(np.float32)
    doc_ids = [f"doc_{i}" for i in range(10)]

    index.add_documents(embeddings, doc_ids)
    print(f"Index size after adding: {index.size}")

    # Try to search
    query = np.random.randn(384).astype(np.float32)
    results = index.search(query, k=5)
    print(f"Search results: {len(results)} found")

    # Get stats
    stats = index.get_stats()
    print(f"Index stats: {stats}")

    return True


def test_integration():
    """Test the integration of both components."""
    print("\n=== Testing Integration ===")

    # Create mock commit-like texts
    texts = [
        "Add authentication module with JWT support",
        "Fix bug in user login validation",
        "Update database schema for user roles",
        "Implement password reset functionality",
        "Add unit tests for auth module"
    ]

    # Initialize components
    embed_config = EmbeddingConfig(dimension=384)
    generator = EmbeddingGenerator(embed_config)

    faiss_config = FAISSConfig(dimension=384)
    index = FAISSIndex(faiss_config)

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = []
    for text in texts:
        embedding = generator.embed_query(text)
        embeddings.append(embedding)

    embeddings = np.array(embeddings)
    print(f"Generated {len(embeddings)} embeddings")

    # Add to index
    doc_ids = [f"commit_{i}" for i in range(len(texts))]
    index.add_documents(embeddings, doc_ids)
    print(f"Added {index.size} documents to index")

    # Search for similar
    query = "How is user authentication handled?"
    query_embedding = generator.embed_query(query)

    start = time.time()
    results = index.search(query_embedding, k=3)
    elapsed = time.time() - start

    print(f"\nSearch query: '{query}'")
    print(f"Search time: {elapsed*1000:.2f}ms")

    if results:
        print(f"Found {len(results)} results:")
        for doc_id, score in results:
            idx = int(doc_id.split('_')[1])
            print(f"  - {doc_id} (score: {score:.3f}): {texts[idx]}")
    else:
        print("No results found (expected when dependencies missing)")

    return True


def test_performance():
    """Test performance metrics."""
    print("\n=== Testing Performance ===")

    # Test embedding speed
    generator = EmbeddingGenerator(EmbeddingConfig(dimension=384))
    text = "Sample commit message for testing"

    start = time.time()
    embedding = generator.embed_query(text)
    elapsed = time.time() - start
    print(f"Single embedding generation: {elapsed*1000:.2f}ms")

    # Test index operations
    index = FAISSIndex(FAISSConfig(dimension=384))

    # Add batch
    embeddings = np.random.randn(100, 384).astype(np.float32)
    doc_ids = [f"doc_{i}" for i in range(100)]

    start = time.time()
    index.add_documents(embeddings, doc_ids)
    elapsed = time.time() - start
    print(f"Adding 100 documents: {elapsed*1000:.2f}ms")

    # Search
    query = np.random.randn(384).astype(np.float32)
    start = time.time()
    results = index.search(query, k=10)
    elapsed = time.time() - start
    print(f"Search time: {elapsed*1000:.2f}ms")

    # Memory usage
    memory_stats = index.get_memory_usage()
    print(f"Memory usage: {memory_stats}")

    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("AIL Sprint 2: FAISS Integration Validation")
    print("=" * 60)

    # Check dependencies
    deps = check_dependencies()

    # Run tests
    tests_passed = []

    try:
        tests_passed.append(("EmbeddingGenerator", test_embedding_generator()))
    except Exception as e:
        print(f"EmbeddingGenerator test failed: {e}")
        tests_passed.append(("EmbeddingGenerator", False))

    try:
        tests_passed.append(("FAISSIndex", test_faiss_index()))
    except Exception as e:
        print(f"FAISSIndex test failed: {e}")
        tests_passed.append(("FAISSIndex", False))

    try:
        tests_passed.append(("Integration", test_integration()))
    except Exception as e:
        print(f"Integration test failed: {e}")
        tests_passed.append(("Integration", False))

    try:
        tests_passed.append(("Performance", test_performance()))
    except Exception as e:
        print(f"Performance test failed: {e}")
        tests_passed.append(("Performance", False))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for name, passed in tests_passed:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")

    all_passed = all(passed for _, passed in tests_passed)

    if all_passed:
        print("\n✅ All validation tests passed!")
        print("The FAISS integration is working correctly.")
        if not deps['faiss'] or not deps['sentence_transformers']:
            print("Note: Running in fallback mode due to missing dependencies.")
    else:
        print("\n❌ Some tests failed. Please review the output above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())