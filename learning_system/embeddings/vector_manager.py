"""
Vector Embeddings Manager

Manages semantic embeddings for projects, patterns, decisions, and contexts.
Provides similarity search, clustering, and semantic matching capabilities
using various embedding models and vector databases.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from abc import ABC, abstractmethod

# Vector database imports
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    import hnswlib
    HAS_HNSWLIB = True
except ImportError:
    HAS_HNSWLIB = False

# Embedding model imports
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from ..knowledge_graph.graph_manager import GraphManager
from ..knowledge_graph.schema import NodeType


logger = logging.getLogger(__name__)


class EmbeddingModel(Enum):
    """Available embedding models"""
    SENTENCE_TRANSFORMER = "sentence_transformer"
    OPENAI_ADA = "openai_ada"
    OPENAI_SMALL = "openai_small"  
    OPENAI_LARGE = "openai_large"
    LOCAL_BERT = "local_bert"


class VectorDatabase(Enum):
    """Available vector databases"""
    FAISS = "faiss"
    HNSWLIB = "hnswlib"
    IN_MEMORY = "in_memory"


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation"""
    model: EmbeddingModel
    model_name: str
    dimension: int
    batch_size: int = 32
    max_tokens: int = 512
    normalize: bool = True


@dataclass
class VectorEntry:
    """Vector database entry"""
    id: str
    vector: np.ndarray
    metadata: Dict[str, Any]
    node_type: NodeType
    created_at: datetime
    content_hash: str


@dataclass
class SimilarityResult:
    """Similarity search result"""
    id: str
    score: float
    metadata: Dict[str, Any]
    node_type: NodeType
    content: Optional[Dict[str, Any]] = None


class BaseVectorDB(ABC):
    """Abstract base class for vector databases"""
    
    @abstractmethod
    def add_vectors(self, entries: List[VectorEntry]) -> bool:
        """Add vectors to the database"""
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[SimilarityResult]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    def update_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Update an existing vector"""
        pass
    
    @abstractmethod
    def delete_vector(self, id: str) -> bool:
        """Delete a vector"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        pass


class FAISSVectorDB(BaseVectorDB):
    """FAISS-based vector database"""
    
    def __init__(self, dimension: int):
        if not HAS_FAISS:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        self.id_to_metadata: Dict[int, Dict[str, Any]] = {}
        self.id_to_string: Dict[int, str] = {}
        self.string_to_id: Dict[str, int] = {}
        self.next_id = 0
    
    def add_vectors(self, entries: List[VectorEntry]) -> bool:
        """Add vectors to FAISS index"""
        try:
            vectors = np.array([entry.vector for entry in entries], dtype=np.float32)
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(vectors)
            
            # Add to index
            start_id = self.next_id
            self.index.add(vectors)
            
            # Store metadata
            for i, entry in enumerate(entries):
                idx = start_id + i
                self.id_to_metadata[idx] = entry.metadata
                self.id_to_string[idx] = entry.id
                self.string_to_id[entry.id] = idx
            
            self.next_id += len(entries)
            return True
        except Exception as e:
            logger.error(f"Failed to add vectors to FAISS: {e}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[SimilarityResult]:
        """Search for similar vectors"""
        try:
            # Normalize query vector
            query_vector = query_vector.astype(np.float32).reshape(1, -1)
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.index.search(query_vector, k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # No more results
                    break
                
                string_id = self.id_to_string.get(idx)
                metadata = self.id_to_metadata.get(idx, {})
                
                result = SimilarityResult(
                    id=string_id or str(idx),
                    score=float(score),
                    metadata=metadata,
                    node_type=NodeType(metadata.get('node_type', 'Project'))
                )
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Failed to search FAISS index: {e}")
            return []
    
    def update_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Update vector (FAISS doesn't support updates, so we'd need to rebuild)"""
        logger.warning("FAISS doesn't support efficient updates. Consider rebuilding index.")
        return False
    
    def delete_vector(self, id: str) -> bool:
        """Delete vector (FAISS doesn't support efficient deletion)"""
        logger.warning("FAISS doesn't support efficient deletion. Consider rebuilding index.")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': 'FAISS_IndexFlatIP'
        }


class HNSWVectorDB(BaseVectorDB):
    """HNSWLIB-based vector database"""
    
    def __init__(self, dimension: int, max_elements: int = 10000):
        if not HAS_HNSWLIB:
            raise ImportError("HNSWlib not available. Install with: pip install hnswlib")
        
        self.dimension = dimension
        self.max_elements = max_elements
        self.index = hnswlib.Index(space='cosine', dim=dimension)
        self.index.init_index(max_elements=max_elements, ef_construction=200, M=16)
        
        self.id_to_metadata: Dict[int, Dict[str, Any]] = {}
        self.id_to_string: Dict[int, str] = {}
        self.string_to_id: Dict[str, int] = {}
        self.next_id = 0
    
    def add_vectors(self, entries: List[VectorEntry]) -> bool:
        """Add vectors to HNSW index"""
        try:
            vectors = np.array([entry.vector for entry in entries], dtype=np.float32)
            ids = list(range(self.next_id, self.next_id + len(entries)))
            
            # Add to index
            self.index.add_items(vectors, ids)
            
            # Store metadata
            for i, entry in enumerate(entries):
                idx = ids[i]
                self.id_to_metadata[idx] = entry.metadata
                self.id_to_string[idx] = entry.id
                self.string_to_id[entry.id] = idx
            
            self.next_id += len(entries)
            return True
        except Exception as e:
            logger.error(f"Failed to add vectors to HNSW: {e}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[SimilarityResult]:
        """Search for similar vectors"""
        try:
            query_vector = query_vector.astype(np.float32)
            labels, distances = self.index.knn_query(query_vector, k=k)
            
            results = []
            for label, distance in zip(labels[0], distances[0]):
                # Convert distance to similarity score (cosine similarity)
                score = 1.0 - distance
                
                string_id = self.id_to_string.get(label)
                metadata = self.id_to_metadata.get(label, {})
                
                result = SimilarityResult(
                    id=string_id or str(label),
                    score=float(score),
                    metadata=metadata,
                    node_type=NodeType(metadata.get('node_type', 'Project'))
                )
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Failed to search HNSW index: {e}")
            return []
    
    def update_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Update vector"""
        if id not in self.string_to_id:
            return False
        
        try:
            idx = self.string_to_id[id]
            vector = vector.astype(np.float32)
            
            # Update vector
            self.index.add_items([vector], [idx])
            
            # Update metadata
            self.id_to_metadata[idx] = metadata
            
            return True
        except Exception as e:
            logger.error(f"Failed to update vector in HNSW: {e}")
            return False
    
    def delete_vector(self, id: str) -> bool:
        """Delete vector (HNSW doesn't support efficient deletion)"""
        logger.warning("HNSW doesn't support efficient deletion. Consider rebuilding index.")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_vectors': self.index.get_current_count(),
            'dimension': self.dimension,
            'max_elements': self.max_elements,
            'index_type': 'HNSW'
        }


class InMemoryVectorDB(BaseVectorDB):
    """Simple in-memory vector database for development/testing"""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def add_vectors(self, entries: List[VectorEntry]) -> bool:
        """Add vectors to memory"""
        try:
            for entry in entries:
                self.vectors[entry.id] = entry.vector
                self.metadata[entry.id] = entry.metadata
            return True
        except Exception as e:
            logger.error(f"Failed to add vectors to memory: {e}")
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 10) -> List[SimilarityResult]:
        """Search for similar vectors using cosine similarity"""
        try:
            scores = []
            
            # Normalize query vector
            query_norm = np.linalg.norm(query_vector)
            if query_norm == 0:
                return []
            query_vector = query_vector / query_norm
            
            # Calculate cosine similarity with all vectors
            for vector_id, vector in self.vectors.items():
                vector_norm = np.linalg.norm(vector)
                if vector_norm == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query_vector, vector / vector_norm)
                
                scores.append((vector_id, float(similarity)))
            
            # Sort by similarity and take top k
            scores.sort(key=lambda x: x[1], reverse=True)
            top_results = scores[:k]
            
            results = []
            for vector_id, score in top_results:
                metadata = self.metadata.get(vector_id, {})
                result = SimilarityResult(
                    id=vector_id,
                    score=score,
                    metadata=metadata,
                    node_type=NodeType(metadata.get('node_type', 'Project'))
                )
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Failed to search in-memory vectors: {e}")
            return []
    
    def update_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """Update vector"""
        try:
            self.vectors[id] = vector
            self.metadata[id] = metadata
            return True
        except Exception as e:
            logger.error(f"Failed to update vector: {e}")
            return False
    
    def delete_vector(self, id: str) -> bool:
        """Delete vector"""
        try:
            self.vectors.pop(id, None)
            self.metadata.pop(id, None)
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_vectors': len(self.vectors),
            'dimension': self.dimension,
            'index_type': 'InMemory'
        }


class VectorManager:
    """
    Manages vector embeddings and semantic similarity search
    """
    
    def __init__(
        self,
        graph_manager: GraphManager,
        embedding_config: EmbeddingConfig,
        vector_db_type: VectorDatabase = VectorDatabase.IN_MEMORY,
        vector_db_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize vector manager
        
        Args:
            graph_manager: Knowledge graph manager
            embedding_config: Embedding model configuration
            vector_db_type: Type of vector database to use
            vector_db_params: Additional parameters for vector database
        """
        self.graph = graph_manager
        self.embedding_config = embedding_config
        self.vector_db_type = vector_db_type
        
        # Initialize embedding model
        self.embedding_model = self._initialize_embedding_model()
        
        # Initialize vector database
        params = vector_db_params or {}
        self.vector_db = self._initialize_vector_db(params)
        
        # Cache for embeddings
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model"""
        config = self.embedding_config
        
        if config.model == EmbeddingModel.SENTENCE_TRANSFORMER:
            if not HAS_SENTENCE_TRANSFORMERS:
                raise ImportError("sentence-transformers not available. Install with: pip install sentence-transformers")
            return SentenceTransformer(config.model_name)
        
        elif config.model in [EmbeddingModel.OPENAI_ADA, EmbeddingModel.OPENAI_SMALL, EmbeddingModel.OPENAI_LARGE]:
            if not HAS_OPENAI:
                raise ImportError("openai not available. Install with: pip install openai")
            return openai  # Will use openai.embeddings.create()
        
        else:
            raise ValueError(f"Unsupported embedding model: {config.model}")
    
    def _initialize_vector_db(self, params: Dict[str, Any]) -> BaseVectorDB:
        """Initialize the vector database"""
        if self.vector_db_type == VectorDatabase.FAISS:
            return FAISSVectorDB(self.embedding_config.dimension)
        
        elif self.vector_db_type == VectorDatabase.HNSWLIB:
            max_elements = params.get('max_elements', 10000)
            return HNSWVectorDB(self.embedding_config.dimension, max_elements)
        
        elif self.vector_db_type == VectorDatabase.IN_MEMORY:
            return InMemoryVectorDB(self.embedding_config.dimension)
        
        else:
            raise ValueError(f"Unsupported vector database: {self.vector_db_type}")
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute hash for content caching"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def generate_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            use_cache: Whether to use caching
            
        Returns:
            Embedding vector
        """
        # Check cache first
        if use_cache:
            content_hash = self._compute_content_hash(text)
            if content_hash in self.embedding_cache:
                self.cache_hits += 1
                return self.embedding_cache[content_hash]
        
        self.cache_misses += 1
        
        # Generate embedding
        config = self.embedding_config
        
        try:
            if config.model == EmbeddingModel.SENTENCE_TRANSFORMER:
                embedding = self.embedding_model.encode(text, normalize_embeddings=config.normalize)
            
            elif config.model in [EmbeddingModel.OPENAI_ADA, EmbeddingModel.OPENAI_SMALL, EmbeddingModel.OPENAI_LARGE]:
                response = openai.embeddings.create(
                    input=text[:config.max_tokens],
                    model=config.model_name
                )
                embedding = np.array(response.data[0].embedding)
                
                if config.normalize:
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
            
            else:
                raise ValueError(f"Unsupported model: {config.model}")
            
            # Cache the result
            if use_cache:
                self.embedding_cache[content_hash] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(config.dimension)
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        config = self.embedding_config
        
        try:
            if config.model == EmbeddingModel.SENTENCE_TRANSFORMER:
                embeddings = self.embedding_model.encode(
                    texts, 
                    normalize_embeddings=config.normalize,
                    batch_size=config.batch_size
                )
                return [embedding for embedding in embeddings]
            
            elif config.model in [EmbeddingModel.OPENAI_ADA, EmbeddingModel.OPENAI_SMALL, EmbeddingModel.OPENAI_LARGE]:
                # Process in batches for OpenAI
                all_embeddings = []
                for i in range(0, len(texts), config.batch_size):
                    batch = texts[i:i + config.batch_size]
                    response = openai.embeddings.create(
                        input=[text[:config.max_tokens] for text in batch],
                        model=config.model_name
                    )
                    
                    batch_embeddings = []
                    for data in response.data:
                        embedding = np.array(data.embedding)
                        if config.normalize:
                            norm = np.linalg.norm(embedding)
                            if norm > 0:
                                embedding = embedding / norm
                        batch_embeddings.append(embedding)
                    
                    all_embeddings.extend(batch_embeddings)
                
                return all_embeddings
            
            else:
                # Fallback to individual generation
                return [self.generate_embedding(text) for text in texts]
                
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [np.zeros(config.dimension) for _ in texts]
    
    # Graph Node Embedding
    
    def embed_node(self, node_id: str, node_type: NodeType) -> Optional[str]:
        """
        Generate and store embedding for a graph node
        
        Args:
            node_id: Node identifier
            node_type: Type of node
            
        Returns:
            Embedding ID if successful
        """
        # Get node data from graph
        node = self.graph.get_node(node_id, node_type)
        if not node:
            logger.error(f"Node {node_id} not found in graph")
            return None
        
        # Extract text content for embedding
        text_content = self._extract_text_content(node, node_type)
        if not text_content:
            logger.warning(f"No text content found for node {node_id}")
            return None
        
        # Generate embedding
        embedding = self.generate_embedding(text_content)
        
        # Create vector entry
        vector_entry = VectorEntry(
            id=node_id,
            vector=embedding,
            metadata={
                'node_type': node_type.value,
                'content_hash': self._compute_content_hash(text_content),
                'text_content': text_content[:500],  # Store snippet for reference
                'node_data': node.to_dict() if hasattr(node, 'to_dict') else {}
            },
            node_type=node_type,
            created_at=datetime.utcnow(),
            content_hash=self._compute_content_hash(text_content)
        )
        
        # Add to vector database
        success = self.vector_db.add_vectors([vector_entry])
        
        if success:
            logger.info(f"Embedded node {node_id} ({node_type.value})")
            return node_id
        else:
            logger.error(f"Failed to store embedding for node {node_id}")
            return None
    
    def embed_nodes_batch(
        self, 
        node_ids: List[str], 
        node_types: List[NodeType]
    ) -> List[Optional[str]]:
        """
        Generate embeddings for multiple nodes in batch
        
        Args:
            node_ids: List of node identifiers
            node_types: List of node types (matching node_ids)
            
        Returns:
            List of embedding IDs (None for failed embeddings)
        """
        if len(node_ids) != len(node_types):
            raise ValueError("node_ids and node_types must have same length")
        
        # Extract text content for all nodes
        text_contents = []
        valid_nodes = []
        
        for node_id, node_type in zip(node_ids, node_types):
            node = self.graph.get_node(node_id, node_type)
            if node:
                text_content = self._extract_text_content(node, node_type)
                if text_content:
                    text_contents.append(text_content)
                    valid_nodes.append((node_id, node_type, node, text_content))
                else:
                    text_contents.append("")
                    valid_nodes.append((node_id, node_type, None, ""))
            else:
                text_contents.append("")
                valid_nodes.append((node_id, node_type, None, ""))
        
        # Generate embeddings in batch
        embeddings = self.generate_embeddings_batch([
            content for content in text_contents if content
        ])
        
        # Create vector entries
        vector_entries = []
        results = []
        embedding_idx = 0
        
        for node_id, node_type, node, text_content in valid_nodes:
            if text_content and embedding_idx < len(embeddings):
                embedding = embeddings[embedding_idx]
                embedding_idx += 1
                
                vector_entry = VectorEntry(
                    id=node_id,
                    vector=embedding,
                    metadata={
                        'node_type': node_type.value,
                        'content_hash': self._compute_content_hash(text_content),
                        'text_content': text_content[:500],
                        'node_data': node.to_dict() if hasattr(node, 'to_dict') else {}
                    },
                    node_type=node_type,
                    created_at=datetime.utcnow(),
                    content_hash=self._compute_content_hash(text_content)
                )
                
                vector_entries.append(vector_entry)
                results.append(node_id)
            else:
                results.append(None)
        
        # Add to vector database
        if vector_entries:
            success = self.vector_db.add_vectors(vector_entries)
            if not success:
                logger.error("Failed to store batch embeddings")
                return [None] * len(node_ids)
        
        logger.info(f"Embedded {len(vector_entries)} nodes in batch")
        return results
    
    def _extract_text_content(self, node: Any, node_type: NodeType) -> str:
        """Extract text content from a node for embedding"""
        try:
            if node_type == NodeType.PROJECT:
                return f"{node.name} {node.description} {' '.join(node.technology_stack)} {node.domain}"
            
            elif node_type == NodeType.DECISION:
                return f"{node.title} {node.description} {node.rationale} {' '.join(node.alternatives_considered)}"
            
            elif node_type == NodeType.PATTERN:
                return f"{node.name} {node.description} {node.problem} {node.solution} {' '.join(node.tags)}"
            
            elif node_type == NodeType.CONTEXT:
                return f"{node.context_type} {json.dumps(node.data)}"
            
            elif node_type == NodeType.OUTCOME:
                return f"{node.outcome_type} {node.description} {' '.join(node.lessons_learned)}"
            
            elif node_type == NodeType.AGENT:
                return f"{node.name} {node.type} {' '.join(node.capabilities)}"
            
            else:
                # Generic fallback
                node_dict = node.to_dict() if hasattr(node, 'to_dict') else {}
                text_fields = []
                
                for key, value in node_dict.items():
                    if isinstance(value, str):
                        text_fields.append(value)
                    elif isinstance(value, list) and value and isinstance(value[0], str):
                        text_fields.extend(value)
                
                return " ".join(text_fields)
                
        except Exception as e:
            logger.error(f"Failed to extract text content from node: {e}")
            return ""
    
    # Similarity Search
    
    def find_similar_nodes(
        self,
        query_text: str,
        node_types: Optional[List[NodeType]] = None,
        k: int = 10,
        min_score: float = 0.1
    ) -> List[SimilarityResult]:
        """
        Find nodes similar to query text
        
        Args:
            query_text: Text to search for
            node_types: Filter by node types
            k: Maximum number of results
            min_score: Minimum similarity score
            
        Returns:
            List of similar nodes
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Search vector database
        results = self.vector_db.search(query_embedding, k * 2)  # Get more to filter
        
        # Filter by node types and score
        filtered_results = []
        for result in results:
            if result.score < min_score:
                continue
            
            if node_types and result.node_type not in node_types:
                continue
            
            filtered_results.append(result)
        
        return filtered_results[:k]
    
    def find_similar_to_node(
        self,
        node_id: str,
        node_type: NodeType,
        k: int = 10,
        min_score: float = 0.1
    ) -> List[SimilarityResult]:
        """
        Find nodes similar to a given node
        
        Args:
            node_id: Node to find similar nodes for
            node_type: Type of the node
            k: Maximum number of results
            min_score: Minimum similarity score
            
        Returns:
            List of similar nodes
        """
        # Get node text content
        node = self.graph.get_node(node_id, node_type)
        if not node:
            return []
        
        text_content = self._extract_text_content(node, node_type)
        if not text_content:
            return []
        
        # Find similar nodes
        results = self.find_similar_nodes(text_content, k=k+1, min_score=min_score)
        
        # Remove the original node from results
        return [r for r in results if r.id != node_id][:k]
    
    def cluster_nodes(
        self,
        node_types: List[NodeType],
        n_clusters: int = 5,
        min_cluster_size: int = 2
    ) -> Dict[int, List[str]]:
        """
        Cluster nodes by semantic similarity
        
        Args:
            node_types: Types of nodes to cluster
            n_clusters: Number of clusters
            min_cluster_size: Minimum size for a cluster
            
        Returns:
            Dictionary mapping cluster ID to node IDs
        """
        # Get all embeddings for specified node types
        all_results = self.vector_db.search(
            np.zeros(self.embedding_config.dimension),  # Dummy query
            k=10000  # Get all
        )
        
        # Filter by node types
        filtered_results = [
            r for r in all_results 
            if r.node_type in node_types
        ]
        
        if len(filtered_results) < n_clusters:
            return {}
        
        # Extract embeddings
        embeddings = []
        node_ids = []
        
        for result in filtered_results:
            # We need to get the actual embedding - this is a limitation
            # In practice, we'd store embeddings separately or in metadata
            node = self.graph.get_node(result.id, result.node_type)
            if node:
                text_content = self._extract_text_content(node, result.node_type)
                embedding = self.generate_embedding(text_content)
                embeddings.append(embedding)
                node_ids.append(result.id)
        
        if not embeddings:
            return {}
        
        # Perform clustering
        try:
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(np.array(embeddings))
            
            # Group by cluster
            clusters = {}
            for node_id, cluster_id in zip(node_ids, cluster_labels):
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(node_id)
            
            # Filter by minimum cluster size
            return {
                cluster_id: node_list 
                for cluster_id, node_list in clusters.items()
                if len(node_list) >= min_cluster_size
            }
            
        except ImportError:
            logger.error("scikit-learn not available for clustering")
            return {}
    
    # Analytics and Management
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding system statistics"""
        vector_stats = self.vector_db.get_stats()
        
        return {
            'vector_database': vector_stats,
            'embedding_model': {
                'type': self.embedding_config.model.value,
                'model_name': self.embedding_config.model_name,
                'dimension': self.embedding_config.dimension
            },
            'cache': {
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
                'cached_embeddings': len(self.embedding_cache)
            }
        }
    
    def rebuild_embeddings(self, node_types: Optional[List[NodeType]] = None) -> Dict[NodeType, int]:
        """
        Rebuild embeddings for all nodes of specified types
        
        Args:
            node_types: Types of nodes to rebuild (all if None)
            
        Returns:
            Count of embeddings created by node type
        """
        if node_types is None:
            node_types = list(NodeType)
        
        results = {}
        
        for node_type in node_types:
            # Get all nodes of this type from graph
            # This would need to be implemented in GraphManager
            # For now, we'll use a placeholder
            
            logger.info(f"Rebuilding embeddings for {node_type.value}")
            # nodes = self.graph.get_all_nodes(node_type)  # Would need this method
            # results[node_type] = len(self.embed_nodes_batch(nodes))
            results[node_type] = 0  # Placeholder
        
        return results


# Pre-configured embedding configurations
EMBEDDING_CONFIGS = {
    'sentence_transformer_all': EmbeddingConfig(
        model=EmbeddingModel.SENTENCE_TRANSFORMER,
        model_name='all-MiniLM-L6-v2',
        dimension=384
    ),
    'sentence_transformer_large': EmbeddingConfig(
        model=EmbeddingModel.SENTENCE_TRANSFORMER,
        model_name='all-mpnet-base-v2',
        dimension=768
    ),
    'openai_ada': EmbeddingConfig(
        model=EmbeddingModel.OPENAI_ADA,
        model_name='text-embedding-ada-002',
        dimension=1536
    ),
    'openai_small': EmbeddingConfig(
        model=EmbeddingModel.OPENAI_SMALL,
        model_name='text-embedding-3-small',
        dimension=1536
    ),
    'openai_large': EmbeddingConfig(
        model=EmbeddingModel.OPENAI_LARGE,
        model_name='text-embedding-3-large',
        dimension=3072
    )
}