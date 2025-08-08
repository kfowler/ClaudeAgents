"""
Vector Similarity Search System

This module provides fast vector similarity search using both pgvector (PostgreSQL)
and FAISS for semantic agent matching.
"""

import os
import pickle
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path
import json
from datetime import datetime, timedelta

# ML/AI imports
import numpy as np
import faiss
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# Database imports
import asyncpg
import redis.asyncio as redis

# Local imports
from .agent_embedder import AgentCapability, EmbeddingResult


logger = logging.getLogger(__name__)


class SearchBackend(Enum):
    """Supported vector search backends."""
    PGVECTOR = "pgvector"
    FAISS = "faiss"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """Result from vector similarity search."""
    agent_name: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[str] = None
    embedding: Optional[np.ndarray] = None


@dataclass 
class SearchQuery:
    """Vector search query configuration."""
    query_vector: np.ndarray
    top_k: int = 10
    similarity_threshold: float = 0.0
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    include_embeddings: bool = False


class VectorSearchCache:
    """Redis-based caching for vector search results."""
    
    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600):
        """Initialize cache with Redis connection."""
        self.redis_url = redis_url
        self.ttl = ttl  # Time to live in seconds
        self.redis_client = None
        
    async def initialize(self):
        """Initialize Redis connection."""
        if self.redis_url:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Vector search cache initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.redis_client = None
        
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    def _create_cache_key(self, query_vector: np.ndarray, top_k: int, filters: Dict) -> str:
        """Create cache key from query parameters."""
        # Create hash of query vector
        vector_hash = hash(query_vector.tobytes())
        filters_str = json.dumps(filters, sort_keys=True)
        return f"vector_search:{vector_hash}:{top_k}:{hash(filters_str)}"
    
    async def get(self, query: SearchQuery) -> Optional[List[SearchResult]]:
        """Get cached search results."""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._create_cache_key(
                query.query_vector, query.top_k, query.metadata_filters
            )
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                results = []
                for item in data:
                    result = SearchResult(
                        agent_name=item['agent_name'],
                        similarity_score=item['similarity_score'],
                        metadata=item.get('metadata', {}),
                        explanation=item.get('explanation')
                    )
                    results.append(result)
                return results
                
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
        
        return None
    
    async def set(self, query: SearchQuery, results: List[SearchResult]):
        """Cache search results."""
        if not self.redis_client:
            return
        
        try:
            cache_key = self._create_cache_key(
                query.query_vector, query.top_k, query.metadata_filters
            )
            
            # Serialize results (excluding embeddings for space)
            data = []
            for result in results:
                data.append({
                    'agent_name': result.agent_name,
                    'similarity_score': result.similarity_score,
                    'metadata': result.metadata,
                    'explanation': result.explanation
                })
            
            await self.redis_client.setex(
                cache_key, self.ttl, json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"Error caching search results: {e}")


class PgVectorSearch:
    """PostgreSQL-based vector similarity search using pgvector."""
    
    def __init__(self, db_url: str, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize pgvector search."""
        self.db_url = db_url
        self.model_name = model_name
        self.db_pool = None
        
    async def initialize(self):
        """Initialize database connection pool."""
        self.db_pool = await asyncpg.create_pool(
            self.db_url,
            min_size=2,
            max_size=10,
            command_timeout=30
        )
        
        # Ensure pgvector extension is available
        async with self.db_pool.acquire() as conn:
            try:
                await conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            except Exception:
                logger.warning("pgvector extension not found. Install with: CREATE EXTENSION vector;")
                
        logger.info("PgVector search initialized")
    
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform vector similarity search using PostgreSQL."""
        if not self.db_pool:
            raise RuntimeError("Database pool not initialized")
        
        try:
            # Convert numpy array to PostgreSQL vector format
            query_vector_list = query.query_vector.tolist()
            
            # Build SQL query with optional metadata filters
            where_clauses = ["embedding_model = $2"]
            params = [query_vector_list, self.model_name]
            param_counter = 3
            
            # Add metadata filters
            for key, value in query.metadata_filters.items():
                if key == 'tier':
                    where_clauses.append(f"(metadata->>'tier')::int = ${param_counter}")
                    params.append(value)
                elif key == 'domains':
                    where_clauses.append(f"metadata->'domains' ? ${param_counter}")
                    params.append(value)
                elif key == 'technologies':
                    where_clauses.append(f"metadata->'technologies' ? ${param_counter}")
                    params.append(value)
                else:
                    where_clauses.append(f"metadata->>'{key}' = ${param_counter}")
                    params.append(str(value))
                param_counter += 1
            
            where_clause = " AND ".join(where_clauses)
            
            # Construct full query
            sql_query = f"""
                SELECT 
                    agent_name,
                    1 - (capability_vector <=> $1::vector) as similarity_score,
                    metadata,
                    {'capability_vector' if query.include_embeddings else 'NULL as capability_vector'}
                FROM agent_embeddings
                WHERE {where_clause}
                    AND (1 - (capability_vector <=> $1::vector)) >= {query.similarity_threshold}
                ORDER BY capability_vector <=> $1::vector
                LIMIT {query.top_k}
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(sql_query, *params)
            
            # Convert to SearchResult objects
            results = []
            for row in rows:
                metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                
                result = SearchResult(
                    agent_name=row['agent_name'],
                    similarity_score=float(row['similarity_score']),
                    metadata=metadata,
                    embedding=np.array(row['capability_vector']) if row['capability_vector'] else None
                )
                
                # Add explanation
                result.explanation = self._generate_explanation(result, query)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in pgvector search: {e}")
            raise
    
    def _generate_explanation(self, result: SearchResult, query: SearchQuery) -> str:
        """Generate explanation for why this agent was matched."""
        explanations = []
        
        # Similarity score explanation
        score = result.similarity_score
        if score >= 0.9:
            explanations.append(f"Very high similarity ({score:.3f})")
        elif score >= 0.7:
            explanations.append(f"High similarity ({score:.3f})")
        elif score >= 0.5:
            explanations.append(f"Moderate similarity ({score:.3f})")
        else:
            explanations.append(f"Low similarity ({score:.3f})")
        
        # Metadata explanations
        if 'technologies' in result.metadata:
            tech_count = len(result.metadata['technologies'])
            explanations.append(f"{tech_count} matching technologies")
        
        if 'domains' in result.metadata:
            domain_count = len(result.metadata['domains'])
            explanations.append(f"{domain_count} relevant domains")
        
        if 'tier' in result.metadata:
            tier = result.metadata['tier']
            tier_names = {1: "core", 2: "specialized", 3: "niche"}
            explanations.append(f"{tier_names.get(tier, 'unknown')} tier agent")
        
        return ", ".join(explanations)


class FAISSVectorSearch:
    """FAISS-based vector similarity search for high performance."""
    
    def __init__(self, 
                 index_path: Optional[str] = None,
                 dimension: int = 384,
                 index_type: str = "IVFFlat"):
        """Initialize FAISS search."""
        self.index_path = Path(index_path) if index_path else None
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.agent_names = []
        self.agent_metadata = {}
        self.embeddings = None
        
    async def initialize(self):
        """Initialize FAISS index."""
        if self.index_path and self.index_path.exists():
            await self.load_index()
        else:
            self._create_index()
        
        logger.info(f"FAISS search initialized with {self.index.ntotal} vectors")
    
    def _create_index(self):
        """Create new FAISS index."""
        if self.index_type == "IVFFlat":
            # Index for larger datasets
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, min(100, max(1, self.dimension // 4)))
        elif self.index_type == "HNSW":
            # Index for high-dimensional data
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            # Simple flat index for small datasets
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Use cosine similarity instead of L2
        self.index = faiss.IndexIDMap(self.index)
    
    async def load_index(self):
        """Load existing FAISS index from disk."""
        try:
            # Load index
            self.index = faiss.read_index(str(self.index_path / "faiss.index"))
            
            # Load metadata
            with open(self.index_path / "metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
                self.agent_names = metadata['agent_names']
                self.agent_metadata = metadata['agent_metadata']
                self.embeddings = metadata.get('embeddings')
            
            logger.info(f"Loaded FAISS index with {len(self.agent_names)} agents")
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self._create_index()
    
    async def save_index(self):
        """Save FAISS index to disk."""
        if not self.index_path:
            return
        
        try:
            # Create directory if needed
            self.index_path.mkdir(parents=True, exist_ok=True)
            
            # Save index
            faiss.write_index(self.index, str(self.index_path / "faiss.index"))
            
            # Save metadata
            metadata = {
                'agent_names': self.agent_names,
                'agent_metadata': self.agent_metadata,
                'embeddings': self.embeddings
            }
            with open(self.index_path / "metadata.pkl", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved FAISS index with {len(self.agent_names)} agents")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    async def add_embeddings(self, embeddings: Dict[str, np.ndarray], 
                           metadata: Dict[str, Dict[str, Any]]):
        """Add embeddings to the FAISS index."""
        # Prepare data
        vectors = []
        names = []
        
        for agent_name, embedding in embeddings.items():
            # Normalize for cosine similarity
            normalized = normalize([embedding])[0]
            vectors.append(normalized)
            names.append(agent_name)
        
        if not vectors:
            return
        
        vectors_array = np.array(vectors, dtype=np.float32)
        
        # Train index if needed (for IVF indices)
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            self.index.train(vectors_array)
        
        # Add vectors with IDs
        start_id = len(self.agent_names)
        ids = np.arange(start_id, start_id + len(vectors), dtype=np.int64)
        
        self.index.add_with_ids(vectors_array, ids)
        
        # Update metadata
        self.agent_names.extend(names)
        self.agent_metadata.update(metadata)
        
        # Store embeddings for later use
        if self.embeddings is None:
            self.embeddings = {}
        for i, name in enumerate(names):
            self.embeddings[name] = vectors[i]
        
        logger.info(f"Added {len(vectors)} embeddings to FAISS index")
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform vector similarity search using FAISS."""
        if not self.index or self.index.ntotal == 0:
            return []
        
        try:
            # Normalize query vector for cosine similarity
            query_vector = normalize([query.query_vector])[0].astype(np.float32)
            
            # Perform search
            similarities, indices = self.index.search(
                query_vector.reshape(1, -1), 
                min(query.top_k, self.index.ntotal)
            )
            
            # Convert to results
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx == -1:  # No more valid results
                    break
                
                # Convert L2 distance to cosine similarity
                # FAISS returns squared L2 distance, convert to similarity
                cosine_sim = max(0.0, 1.0 - (similarity / 2.0))
                
                if cosine_sim < query.similarity_threshold:
                    continue
                
                agent_name = self.agent_names[idx]
                metadata = self.agent_metadata.get(agent_name, {})
                
                # Apply metadata filters
                if not self._matches_filters(metadata, query.metadata_filters):
                    continue
                
                result = SearchResult(
                    agent_name=agent_name,
                    similarity_score=cosine_sim,
                    metadata=metadata,
                    embedding=self.embeddings.get(agent_name) if query.include_embeddings else None
                )
                
                # Add explanation
                result.explanation = self._generate_explanation(result, query)
                results.append(result)
            
            return results[:query.top_k]
            
        except Exception as e:
            logger.error(f"Error in FAISS search: {e}")
            raise
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the given filters."""
        for key, value in filters.items():
            if key == 'tier':
                if metadata.get('tier') != value:
                    return False
            elif key == 'domains':
                if value not in metadata.get('domains', []):
                    return False
            elif key == 'technologies':
                if value not in metadata.get('technologies', []):
                    return False
            else:
                if str(metadata.get(key)) != str(value):
                    return False
        return True
    
    def _generate_explanation(self, result: SearchResult, query: SearchQuery) -> str:
        """Generate explanation for why this agent was matched."""
        explanations = []
        
        # Similarity score explanation
        score = result.similarity_score
        if score >= 0.9:
            explanations.append(f"Very high similarity ({score:.3f})")
        elif score >= 0.7:
            explanations.append(f"High similarity ({score:.3f})")
        elif score >= 0.5:
            explanations.append(f"Moderate similarity ({score:.3f})")
        else:
            explanations.append(f"Low similarity ({score:.3f})")
        
        # Metadata explanations
        if 'technologies' in result.metadata:
            tech_count = len(result.metadata['technologies'])
            explanations.append(f"{tech_count} matching technologies")
        
        if 'domains' in result.metadata:
            domain_count = len(result.metadata['domains'])
            explanations.append(f"{domain_count} relevant domains")
        
        if 'tier' in result.metadata:
            tier = result.metadata['tier']
            tier_names = {1: "core", 2: "specialized", 3: "niche"}
            explanations.append(f"{tier_names.get(tier, 'unknown')} tier agent")
        
        return ", ".join(explanations)


class HybridVectorSearch:
    """Hybrid search combining pgvector and FAISS for optimal performance."""
    
    def __init__(self, 
                 pg_search: PgVectorSearch,
                 faiss_search: FAISSVectorSearch,
                 cache: Optional[VectorSearchCache] = None):
        """Initialize hybrid search."""
        self.pg_search = pg_search
        self.faiss_search = faiss_search
        self.cache = cache
        
    async def initialize(self):
        """Initialize both search backends."""
        await self.pg_search.initialize()
        await self.faiss_search.initialize()
        if self.cache:
            await self.cache.initialize()
        
        logger.info("Hybrid vector search initialized")
    
    async def close(self):
        """Close all connections."""
        await self.pg_search.close()
        if self.cache:
            await self.cache.close()
    
    async def search(self, query: SearchQuery, 
                    backend: SearchBackend = SearchBackend.HYBRID) -> List[SearchResult]:
        """Perform hybrid vector similarity search."""
        # Check cache first
        if self.cache:
            cached_results = await self.cache.get(query)
            if cached_results:
                return cached_results
        
        results = []
        
        if backend == SearchBackend.PGVECTOR:
            results = await self.pg_search.search(query)
            
        elif backend == SearchBackend.FAISS:
            results = await self.faiss_search.search(query)
            
        elif backend == SearchBackend.HYBRID:
            # Use FAISS for fast initial filtering, then pgvector for final ranking
            faiss_query = SearchQuery(
                query_vector=query.query_vector,
                top_k=min(query.top_k * 2, 20),  # Get more candidates
                similarity_threshold=max(query.similarity_threshold - 0.1, 0.0),
                metadata_filters=query.metadata_filters,
                include_embeddings=False
            )
            
            faiss_results = await self.faiss_search.search(faiss_query)
            
            if faiss_results:
                # Get agent names from FAISS results
                candidate_agents = [r.agent_name for r in faiss_results]
                
                # Re-rank with pgvector for more accurate scoring
                pg_query = SearchQuery(
                    query_vector=query.query_vector,
                    top_k=query.top_k,
                    similarity_threshold=query.similarity_threshold,
                    metadata_filters={**query.metadata_filters, 'agent_names': candidate_agents},
                    include_embeddings=query.include_embeddings
                )
                
                results = await self.pg_search.search(pg_query)
            
            # Fallback to pgvector if FAISS fails or returns no results
            if not results:
                results = await self.pg_search.search(query)
        
        # Cache results
        if self.cache and results:
            await self.cache.set(query, results)
        
        return results
    
    async def update_embeddings(self, embeddings: Dict[str, np.ndarray], 
                              metadata: Dict[str, Dict[str, Any]]):
        """Update embeddings in both backends."""
        # Update FAISS index
        await self.faiss_search.add_embeddings(embeddings, metadata)
        await self.faiss_search.save_index()
        
        # pgvector is updated through the database directly
        logger.info(f"Updated {len(embeddings)} embeddings in hybrid search")


class VectorSearchManager:
    """High-level manager for vector similarity search."""
    
    def __init__(self, 
                 db_url: str,
                 redis_url: Optional[str] = None,
                 faiss_index_path: Optional[str] = None,
                 model_name: str = 'all-MiniLM-L6-v2',
                 backend: SearchBackend = SearchBackend.HYBRID):
        """Initialize search manager."""
        self.db_url = db_url
        self.redis_url = redis_url
        self.faiss_index_path = faiss_index_path
        self.model_name = model_name
        self.backend = backend
        
        # Initialize components
        self.cache = VectorSearchCache(redis_url) if redis_url else None
        self.pg_search = PgVectorSearch(db_url, model_name)
        self.faiss_search = FAISSVectorSearch(faiss_index_path)
        
        self.search_engine = HybridVectorSearch(
            self.pg_search, self.faiss_search, self.cache
        )
        
    async def initialize(self):
        """Initialize the search manager."""
        await self.search_engine.initialize()
        logger.info("Vector search manager initialized")
    
    async def close(self):
        """Close all connections."""
        await self.search_engine.close()
    
    async def search_agents(self, 
                          query_vector: np.ndarray,
                          top_k: int = 10,
                          similarity_threshold: float = 0.3,
                          metadata_filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search for similar agents."""
        query = SearchQuery(
            query_vector=query_vector,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filters=metadata_filters or {},
            include_embeddings=False
        )
        
        return await self.search_engine.search(query, self.backend)
    
    async def rebuild_faiss_index(self):
        """Rebuild FAISS index from database."""
        # Get all embeddings from database
        embeddings = await self.pg_search.db_pool.fetch("""
            SELECT agent_name, capability_vector, metadata
            FROM agent_embeddings
            WHERE embedding_model = $1
        """, self.model_name)
        
        # Convert to required format
        embedding_dict = {}
        metadata_dict = {}
        
        for row in embeddings:
            agent_name = row['agent_name']
            embedding_dict[agent_name] = np.array(row['capability_vector'])
            metadata_dict[agent_name] = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
        
        # Update FAISS index
        await self.search_engine.update_embeddings(embedding_dict, metadata_dict)
        
        logger.info(f"Rebuilt FAISS index with {len(embedding_dict)} agents")


# CLI and utility functions
async def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector similarity search for agents")
    parser.add_argument("--db-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--redis-url", help="Redis URL for caching")
    parser.add_argument("--faiss-index", help="Path to FAISS index directory")
    parser.add_argument("--backend", choices=['pgvector', 'faiss', 'hybrid'], 
                       default='hybrid', help="Search backend")
    parser.add_argument("--rebuild-index", action='store_true', 
                       help="Rebuild FAISS index from database")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    backend = SearchBackend(args.backend.upper())
    manager = VectorSearchManager(
        db_url=args.db_url,
        redis_url=args.redis_url,
        faiss_index_path=args.faiss_index,
        backend=backend
    )
    
    try:
        await manager.initialize()
        
        if args.rebuild_index:
            await manager.rebuild_faiss_index()
            print("✓ FAISS index rebuilt successfully")
        else:
            print(f"✓ Vector search initialized with {args.backend} backend")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())