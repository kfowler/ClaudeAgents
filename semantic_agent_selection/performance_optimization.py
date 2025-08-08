"""
Performance Optimization and Caching System

This module provides comprehensive caching, error handling, and performance
optimization features for the semantic agent selection system.
"""

import os
import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
import functools
import weakref
from contextlib import asynccontextmanager

# Caching imports
import redis.asyncio as redis
from cachetools import TTLCache, LRUCache
import pickle
import gzip

# Performance monitoring
import psutil
import tracemalloc

# Database connection pooling
import asyncpg
from asyncpg.pool import Pool

# ML performance
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache level priorities."""
    L1_MEMORY = "l1_memory"      # In-memory cache (fastest)
    L2_REDIS = "l2_redis"        # Redis cache (fast, shared)
    L3_DATABASE = "l3_database"  # Database cache (persistent)


class PerformanceProfile(Enum):
    """Performance optimization profiles."""
    MINIMAL = "minimal"      # Minimal resources, basic caching
    BALANCED = "balanced"    # Balanced performance and resources
    AGGRESSIVE = "aggressive" # Maximum performance, high resource usage


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enable_memory_cache: bool = True
    enable_redis_cache: bool = True
    enable_database_cache: bool = False
    
    # Memory cache settings
    memory_cache_size: int = 1000
    memory_cache_ttl: int = 3600  # 1 hour
    
    # Redis cache settings
    redis_ttl: int = 7200  # 2 hours
    redis_max_connections: int = 10
    
    # Database cache settings
    db_cache_ttl: int = 86400  # 24 hours
    
    # Compression settings
    enable_compression: bool = True
    compression_threshold: int = 1024  # bytes
    
    # Performance settings
    enable_async_writes: bool = True
    enable_batching: bool = True
    batch_size: int = 50


@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    
    # Resource metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Database metrics
    db_connections_active: int = 0
    db_query_time_avg: float = 0.0
    
    # ML metrics
    embedding_generation_time: float = 0.0
    vector_search_time: float = 0.0
    prediction_time: float = 0.0


class CacheKey:
    """Utility class for generating cache keys."""
    
    @staticmethod
    def agent_embedding(agent_name: str, model_name: str) -> str:
        """Generate cache key for agent embedding."""
        return f"agent_emb:{agent_name}:{model_name}"
    
    @staticmethod
    def request_analysis(request: str, project_path: Optional[str] = None) -> str:
        """Generate cache key for request analysis."""
        content = f"{request}:{project_path or ''}"
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"req_analysis:{hash_key}"
    
    @staticmethod
    def semantic_matches(request_hash: str, top_k: int, filters: Dict[str, Any]) -> str:
        """Generate cache key for semantic matches."""
        filters_str = json.dumps(filters, sort_keys=True)
        filters_hash = hashlib.sha256(filters_str.encode()).hexdigest()[:8]
        return f"sem_matches:{request_hash}:{top_k}:{filters_hash}"
    
    @staticmethod
    def workflow_recommendation(analysis_hash: str, agent_names: List[str]) -> str:
        """Generate cache key for workflow recommendation."""
        agents_str = ",".join(sorted(agent_names))
        agents_hash = hashlib.sha256(agents_str.encode()).hexdigest()[:8]
        return f"workflow:{analysis_hash}:{agents_hash}"
    
    @staticmethod
    def success_prediction(agent_name: str, features_hash: str) -> str:
        """Generate cache key for success prediction."""
        return f"success_pred:{agent_name}:{features_hash}"


class MultiLevelCache:
    """Multi-level caching system with memory, Redis, and database layers."""
    
    def __init__(self, config: CacheConfig, redis_client: Optional[redis.Redis] = None):
        """Initialize multi-level cache."""
        self.config = config
        self.redis_client = redis_client
        
        # L1: Memory cache
        if config.enable_memory_cache:
            self.memory_cache = TTLCache(
                maxsize=config.memory_cache_size,
                ttl=config.memory_cache_ttl
            )
        else:
            self.memory_cache = None
        
        # Statistics
        self.stats = {
            'l1_hits': 0, 'l1_misses': 0,
            'l2_hits': 0, 'l2_misses': 0,
            'l3_hits': 0, 'l3_misses': 0,
            'total_gets': 0, 'total_sets': 0
        }
    
    async def get(self, key: str, cache_levels: Optional[List[CacheLevel]] = None) -> Optional[Any]:
        """Get value from cache with multi-level fallback."""
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        self.stats['total_gets'] += 1
        
        for level in cache_levels:
            try:
                if level == CacheLevel.L1_MEMORY and self.memory_cache is not None:
                    value = self.memory_cache.get(key)
                    if value is not None:
                        self.stats['l1_hits'] += 1
                        # Promote to higher cache levels if retrieved from lower
                        if level != cache_levels[0]:
                            await self._promote_to_higher_levels(key, value, cache_levels, level)
                        return self._deserialize(value)
                    else:
                        self.stats['l1_misses'] += 1
                
                elif level == CacheLevel.L2_REDIS and self.redis_client is not None:
                    value = await self.redis_client.get(key)
                    if value is not None:
                        self.stats['l2_hits'] += 1
                        deserialized = self._deserialize(value)
                        # Promote to L1 if available
                        if CacheLevel.L1_MEMORY in cache_levels and self.memory_cache is not None:
                            self.memory_cache[key] = self._serialize(deserialized)
                        return deserialized
                    else:
                        self.stats['l2_misses'] += 1
                        
            except Exception as e:
                logger.warning(f"Cache get error for level {level.value}: {e}")
        
        return None
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  cache_levels: Optional[List[CacheLevel]] = None) -> bool:
        """Set value in cache across multiple levels."""
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        self.stats['total_sets'] += 1
        serialized_value = self._serialize(value)
        success = False
        
        for level in cache_levels:
            try:
                if level == CacheLevel.L1_MEMORY and self.memory_cache is not None:
                    self.memory_cache[key] = serialized_value
                    success = True
                
                elif level == CacheLevel.L2_REDIS and self.redis_client is not None:
                    cache_ttl = ttl or self.config.redis_ttl
                    
                    if self.config.enable_async_writes:
                        # Fire-and-forget async write
                        asyncio.create_task(self.redis_client.setex(key, cache_ttl, serialized_value))
                    else:
                        await self.redis_client.setex(key, cache_ttl, serialized_value)
                    success = True
                        
            except Exception as e:
                logger.warning(f"Cache set error for level {level.value}: {e}")
        
        return success
    
    async def delete(self, key: str, cache_levels: Optional[List[CacheLevel]] = None) -> bool:
        """Delete value from cache across multiple levels."""
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        success = False
        
        for level in cache_levels:
            try:
                if level == CacheLevel.L1_MEMORY and self.memory_cache is not None:
                    self.memory_cache.pop(key, None)
                    success = True
                
                elif level == CacheLevel.L2_REDIS and self.redis_client is not None:
                    await self.redis_client.delete(key)
                    success = True
                        
            except Exception as e:
                logger.warning(f"Cache delete error for level {level.value}: {e}")
        
        return success
    
    async def _promote_to_higher_levels(self, 
                                      key: str, 
                                      value: Any, 
                                      cache_levels: List[CacheLevel],
                                      current_level: CacheLevel):
        """Promote cache entry to higher priority levels."""
        current_index = cache_levels.index(current_level)
        higher_levels = cache_levels[:current_index]
        
        if higher_levels:
            await self.set(key, self._deserialize(value), cache_levels=higher_levels)
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for caching."""
        try:
            serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress if enabled and data is large enough
            if (self.config.enable_compression and 
                len(serialized) > self.config.compression_threshold):
                serialized = gzip.compress(serialized)
                # Add compression marker
                serialized = b'GZIP:' + serialized
            
            return serialized
            
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(None)
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize value from cache."""
        try:
            # Check for compression marker
            if value.startswith(b'GZIP:'):
                value = gzip.decompress(value[5:])  # Remove 'GZIP:' prefix
            
            return pickle.loads(value)
            
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['l3_hits']
        total_operations = self.stats['total_gets']
        
        return {
            **self.stats,
            'hit_rate': total_hits / max(total_operations, 1),
            'memory_cache_size': len(self.memory_cache) if self.memory_cache else 0
        }
    
    async def clear(self, cache_levels: Optional[List[CacheLevel]] = None):
        """Clear cache across specified levels."""
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        for level in cache_levels:
            try:
                if level == CacheLevel.L1_MEMORY and self.memory_cache is not None:
                    self.memory_cache.clear()
                
                elif level == CacheLevel.L2_REDIS and self.redis_client is not None:
                    # This is dangerous in production - would need key patterns
                    # await self.redis_client.flushdb()
                    pass
                        
            except Exception as e:
                logger.warning(f"Cache clear error for level {level.value}: {e}")


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self, collection_interval: int = 60):
        """Initialize performance monitor."""
        self.collection_interval = collection_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.request_times: List[float] = []
        self.active_requests = 0
        self.monitoring_task = None
        
        # Start memory tracking if available
        try:
            tracemalloc.start()
        except RuntimeError:
            pass  # Already started
    
    async def start_monitoring(self):
        """Start background monitoring task."""
        if not self.monitoring_task:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop background monitoring task."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics (assuming 1-minute intervals)
                max_history = 24 * 60
                if len(self.metrics_history) > max_history:
                    self.metrics_history = self.metrics_history[-max_history:]
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        metrics = PerformanceMetrics()
        
        # Request metrics
        if self.request_times:
            metrics.avg_response_time = sum(self.request_times) / len(self.request_times)
            sorted_times = sorted(self.request_times)
            n = len(sorted_times)
            if n > 0:
                metrics.p95_response_time = sorted_times[int(0.95 * n)]
                metrics.p99_response_time = sorted_times[int(0.99 * n)]
        
        # Resource metrics
        try:
            process = psutil.Process()
            metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            metrics.cpu_usage_percent = process.cpu_percent()
        except Exception:
            pass
        
        return metrics
    
    @asynccontextmanager
    async def track_request(self):
        """Context manager to track request performance."""
        self.active_requests += 1
        start_time = time.time()
        
        try:
            yield
            # Success
            processing_time = time.time() - start_time
            self.request_times.append(processing_time)
            
            # Keep only recent times
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-500:]
                
        except Exception as e:
            # Track failures
            processing_time = time.time() - start_time
            self.request_times.append(processing_time)
            raise
        finally:
            self.active_requests -= 1
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        
        return {
            'timestamp': latest.timestamp.isoformat(),
            'active_requests': self.active_requests,
            'avg_response_time': latest.avg_response_time,
            'p95_response_time': latest.p95_response_time,
            'p99_response_time': latest.p99_response_time,
            'memory_usage_mb': latest.memory_usage_mb,
            'cpu_usage_percent': latest.cpu_usage_percent,
            'total_request_samples': len(self.request_times)
        }


class DatabaseConnectionOptimizer:
    """Optimize database connections and query performance."""
    
    def __init__(self, db_url: str, performance_profile: PerformanceProfile = PerformanceProfile.BALANCED):
        """Initialize database optimizer."""
        self.db_url = db_url
        self.performance_profile = performance_profile
        self.pool = None
        self.query_cache = {}
        
        # Connection pool settings based on performance profile
        if performance_profile == PerformanceProfile.MINIMAL:
            self.min_connections = 2
            self.max_connections = 5
            self.command_timeout = 30
        elif performance_profile == PerformanceProfile.BALANCED:
            self.min_connections = 5
            self.max_connections = 20
            self.command_timeout = 30
        else:  # AGGRESSIVE
            self.min_connections = 10
            self.max_connections = 50
            self.command_timeout = 60
    
    async def initialize(self):
        """Initialize optimized connection pool."""
        self.pool = await asyncpg.create_pool(
            self.db_url,
            min_size=self.min_connections,
            max_size=self.max_connections,
            command_timeout=self.command_timeout,
            server_settings={
                'jit': 'off',  # Disable JIT for faster connection startup
                'application_name': 'semantic_agent_selection'
            }
        )
        
        # Warm up connections
        if self.performance_profile == PerformanceProfile.AGGRESSIVE:
            await self._warm_up_connections()
    
    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
    
    async def _warm_up_connections(self):
        """Pre-warm database connections."""
        try:
            async with self.pool.acquire() as conn:
                # Execute a simple query to warm up the connection
                await conn.fetchval("SELECT 1")
        except Exception as e:
            logger.warning(f"Connection warm-up failed: {e}")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get optimized database connection."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            # Optimize connection settings for this session
            await conn.execute("SET work_mem = '256MB'")  # More memory for complex queries
            await conn.execute("SET random_page_cost = 1.1")  # SSD optimization
            yield conn
    
    async def execute_cached_query(self, 
                                 query: str, 
                                 *args, 
                                 cache_ttl: int = 300) -> List[Any]:
        """Execute query with result caching."""
        # Create cache key
        cache_key = hashlib.sha256(f"{query}:{args}".encode()).hexdigest()
        
        # Check cache
        if cache_key in self.query_cache:
            cached_result, cached_time = self.query_cache[cache_key]
            if time.time() - cached_time < cache_ttl:
                return cached_result
        
        # Execute query
        async with self.get_connection() as conn:
            result = await conn.fetch(query, *args)
        
        # Cache result
        self.query_cache[cache_key] = (result, time.time())
        
        # Clean old cache entries
        if len(self.query_cache) > 1000:
            current_time = time.time()
            self.query_cache = {
                k: v for k, v in self.query_cache.items()
                if current_time - v[1] < cache_ttl
            }
        
        return result


class MLPerformanceOptimizer:
    """Optimize ML operations for better performance."""
    
    def __init__(self, performance_profile: PerformanceProfile = PerformanceProfile.BALANCED):
        """Initialize ML optimizer."""
        self.performance_profile = performance_profile
        self.thread_executor = None
        self.process_executor = None
        
        # Set up executors based on performance profile
        if performance_profile == PerformanceProfile.MINIMAL:
            self.max_workers = 2
            self.enable_multiprocessing = False
        elif performance_profile == PerformanceProfile.BALANCED:
            self.max_workers = min(4, os.cpu_count())
            self.enable_multiprocessing = True
        else:  # AGGRESSIVE
            self.max_workers = os.cpu_count()
            self.enable_multiprocessing = True
        
        # Initialize executors
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        if self.enable_multiprocessing:
            self.process_executor = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def close(self):
        """Close executors."""
        if self.thread_executor:
            self.thread_executor.shutdown(wait=False)
        if self.process_executor:
            self.process_executor.shutdown(wait=False)
    
    async def optimize_embedding_batch(self, 
                                     texts: List[str], 
                                     model, 
                                     batch_size: Optional[int] = None) -> np.ndarray:
        """Optimize batch embedding generation."""
        if not batch_size:
            if self.performance_profile == PerformanceProfile.MINIMAL:
                batch_size = 8
            elif self.performance_profile == PerformanceProfile.BALANCED:
                batch_size = 32
            else:  # AGGRESSIVE
                batch_size = 64
        
        # Process in batches to optimize memory usage
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Run in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self.thread_executor,
                lambda: model.encode(
                    batch,
                    normalize_embeddings=True,
                    batch_size=len(batch),
                    show_progress_bar=False
                )
            )
            
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings) if all_embeddings else np.array([])
    
    async def optimize_vector_search(self, 
                                   query_vector: np.ndarray,
                                   index,
                                   top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Optimize vector search operations."""
        # Normalize query vector for better performance
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        # Run search in thread executor
        loop = asyncio.get_event_loop()
        similarities, indices = await loop.run_in_executor(
            self.thread_executor,
            lambda: index.search(query_vector.reshape(1, -1), top_k)
        )
        
        return similarities[0], indices[0]


class ErrorHandler:
    """Comprehensive error handling and recovery system."""
    
    def __init__(self):
        """Initialize error handler."""
        self.error_counts = {}
        self.circuit_breakers = {}
        self.fallback_handlers = {}
    
    def register_fallback(self, operation: str, fallback_func):
        """Register fallback function for operation."""
        self.fallback_handlers[operation] = fallback_func
    
    def circuit_breaker(self, 
                       operation: str,
                       failure_threshold: int = 5,
                       recovery_timeout: int = 60):
        """Circuit breaker decorator."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Check circuit breaker state
                breaker_state = self.circuit_breakers.get(operation, {
                    'failures': 0,
                    'last_failure': None,
                    'state': 'closed'  # closed, open, half-open
                })
                
                current_time = time.time()
                
                # If circuit is open, check if we can try again
                if breaker_state['state'] == 'open':
                    if (breaker_state['last_failure'] and 
                        current_time - breaker_state['last_failure'] > recovery_timeout):
                        breaker_state['state'] = 'half-open'
                    else:
                        # Circuit is open, use fallback
                        if operation in self.fallback_handlers:
                            return await self.fallback_handlers[operation](*args, **kwargs)
                        raise RuntimeError(f"Circuit breaker open for {operation}")
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Success - reset circuit breaker
                    if breaker_state['state'] == 'half-open':
                        breaker_state['state'] = 'closed'
                        breaker_state['failures'] = 0
                    
                    self.circuit_breakers[operation] = breaker_state
                    return result
                    
                except Exception as e:
                    # Failure - update circuit breaker
                    breaker_state['failures'] += 1
                    breaker_state['last_failure'] = current_time
                    
                    if breaker_state['failures'] >= failure_threshold:
                        breaker_state['state'] = 'open'
                    
                    self.circuit_breakers[operation] = breaker_state
                    
                    # Try fallback
                    if operation in self.fallback_handlers:
                        try:
                            return await self.fallback_handlers[operation](*args, **kwargs)
                        except Exception as fallback_error:
                            logger.error(f"Fallback failed for {operation}: {fallback_error}")
                    
                    raise e
                    
            return wrapper
        return decorator
    
    async def handle_graceful_degradation(self, 
                                        primary_func, 
                                        fallback_func,
                                        *args, 
                                        **kwargs):
        """Handle graceful degradation between primary and fallback functions."""
        try:
            return await primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary function failed, using fallback: {e}")
            return await fallback_func(*args, **kwargs)


# Performance-optimized semantic agent selector
class OptimizedSemanticAgentSelector:
    """Performance-optimized version of semantic agent selector."""
    
    def __init__(self, 
                 base_selector,
                 cache_config: Optional[CacheConfig] = None,
                 performance_profile: PerformanceProfile = PerformanceProfile.BALANCED,
                 redis_url: Optional[str] = None):
        """Initialize optimized selector."""
        self.base_selector = base_selector
        self.performance_profile = performance_profile
        
        # Initialize caching
        self.cache_config = cache_config or CacheConfig()
        self.redis_client = None
        if redis_url and self.cache_config.enable_redis_cache:
            asyncio.create_task(self._init_redis(redis_url))
        
        self.cache = MultiLevelCache(self.cache_config, self.redis_client)
        
        # Initialize performance monitoring
        self.monitor = PerformanceMonitor()
        
        # Initialize optimizers
        self.ml_optimizer = MLPerformanceOptimizer(performance_profile)
        self.error_handler = ErrorHandler()
        
        # Register fallbacks
        self._register_fallbacks()
    
    async def _init_redis(self, redis_url: str):
        """Initialize Redis client."""
        try:
            self.redis_client = await redis.from_url(
                redis_url,
                max_connections=self.cache_config.redis_max_connections,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            self.cache.redis_client = self.redis_client
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
    
    def _register_fallbacks(self):
        """Register fallback handlers for error recovery."""
        
        async def analysis_fallback(request: str, project_path: Optional[Path] = None):
            """Fallback for request analysis."""
            # Simple rule-based analysis
            from .request_analyzer import RequestAnalysis, IntentCategory, ComplexityLevel, RiskLevel
            
            return RequestAnalysis(
                original_request=request,
                intent_category=IntentCategory.UNKNOWN,
                complexity_level=ComplexityLevel.MODERATE,
                risk_level=RiskLevel.MEDIUM,
                confidence_score=0.3,
                processing_time=0.1
            )
        
        async def selection_fallback(request: str, **kwargs):
            """Fallback for agent selection."""
            # Return basic recommendation
            from .integration_layer import EnhancedAgentSelection
            from .multi_agent_orchestrator import WorkflowRecommendation, AgentRole, WorkflowPattern
            
            basic_role = AgentRole(
                agent_name="full-stack-architect",
                role_type="primary",
                priority=1,
                confidence_score=0.4,
                rationale="Fallback selection"
            )
            
            basic_workflow = WorkflowRecommendation(
                primary_agents=[basic_role],
                supporting_agents=[],
                validation_agents=[],
                workflow_pattern=WorkflowPattern.SEQUENTIAL,
                confidence_score=0.4,
                explanation="Fallback recommendation due to system issues"
            )
            
            return EnhancedAgentSelection(
                primary_recommendation=basic_workflow,
                confidence_level="low",
                fallback_used=True,
                explanation="System fallback activated"
            )
        
        self.error_handler.register_fallback("request_analysis", analysis_fallback)
        self.error_handler.register_fallback("agent_selection", selection_fallback)
    
    @functools.lru_cache(maxsize=1000)
    def _get_request_hash(self, request: str, project_path_str: str) -> str:
        """Get cached request hash."""
        content = f"{request}:{project_path_str}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def select_agents_optimized(self, 
                                    request: str,
                                    project_path: Optional[Path] = None,
                                    **kwargs) -> Any:
        """Optimized agent selection with caching and performance monitoring."""
        
        async with self.monitor.track_request():
            # Generate cache key
            project_path_str = str(project_path) if project_path else ""
            request_hash = self._get_request_hash(request, project_path_str)
            cache_key = CacheKey.workflow_recommendation(request_hash, [])
            
            # Try cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Apply circuit breaker and fallback
            @self.error_handler.circuit_breaker("agent_selection")
            async def _select_agents():
                return await self.base_selector.select_agents(
                    request=request,
                    project_path=project_path,
                    **kwargs
                )
            
            try:
                result = await _select_agents()
                
                # Cache successful result
                await self.cache.set(cache_key, result, ttl=3600)  # 1 hour
                
                return result
                
            except Exception as e:
                logger.error(f"Optimized agent selection failed: {e}")
                # Fallback will be handled by circuit breaker
                raise
    
    async def initialize(self):
        """Initialize optimized selector."""
        await self.base_selector.initialize()
        await self.monitor.start_monitoring()
    
    async def close(self):
        """Close optimized selector."""
        await self.base_selector.close()
        await self.monitor.stop_monitoring()
        self.ml_optimizer.close()
        
        if self.redis_client:
            await self.redis_client.close()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            'cache_stats': self.cache.get_stats(),
            'monitor_stats': self.monitor.get_current_stats(),
            'circuit_breakers': {
                name: state for name, state in self.error_handler.circuit_breakers.items()
            },
            'performance_profile': self.performance_profile.value
        }


# Utility functions
def create_optimized_config(
    performance_profile: PerformanceProfile = PerformanceProfile.BALANCED,
    redis_url: Optional[str] = None
) -> Tuple[CacheConfig, Dict[str, Any]]:
    """Create optimized configuration based on performance profile."""
    
    if performance_profile == PerformanceProfile.MINIMAL:
        cache_config = CacheConfig(
            enable_memory_cache=True,
            enable_redis_cache=False,
            memory_cache_size=100,
            memory_cache_ttl=1800,
            enable_compression=False,
            enable_async_writes=False,
            enable_batching=False
        )
        
        optimizer_config = {
            'max_workers': 1,
            'batch_size': 8,
            'enable_monitoring': False
        }
        
    elif performance_profile == PerformanceProfile.BALANCED:
        cache_config = CacheConfig(
            enable_memory_cache=True,
            enable_redis_cache=bool(redis_url),
            memory_cache_size=500,
            memory_cache_ttl=3600,
            redis_ttl=7200,
            enable_compression=True,
            enable_async_writes=True,
            enable_batching=True,
            batch_size=32
        )
        
        optimizer_config = {
            'max_workers': min(4, os.cpu_count()),
            'batch_size': 32,
            'enable_monitoring': True
        }
        
    else:  # AGGRESSIVE
        cache_config = CacheConfig(
            enable_memory_cache=True,
            enable_redis_cache=bool(redis_url),
            memory_cache_size=2000,
            memory_cache_ttl=7200,
            redis_ttl=14400,
            redis_max_connections=20,
            enable_compression=True,
            enable_async_writes=True,
            enable_batching=True,
            batch_size=64
        )
        
        optimizer_config = {
            'max_workers': os.cpu_count(),
            'batch_size': 64,
            'enable_monitoring': True
        }
    
    return cache_config, optimizer_config


# Export main classes
__all__ = [
    'CacheConfig',
    'CacheLevel', 
    'PerformanceProfile',
    'PerformanceMetrics',
    'MultiLevelCache',
    'PerformanceMonitor',
    'DatabaseConnectionOptimizer',
    'MLPerformanceOptimizer',
    'ErrorHandler',
    'OptimizedSemanticAgentSelector',
    'create_optimized_config'
]