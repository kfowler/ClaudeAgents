"""
Semantic Agent Selection System

A production-ready AI-powered agent selection system that replaces keyword matching
with intelligent semantic understanding using embeddings and machine learning.
"""

__version__ = "1.0.0"
__author__ = "AI/ML Engineering Team"
__email__ = "ai-engineering@company.com"

# Core system imports
from .agent_embedder import (
    AgentCapabilityEmbedder,
    AgentEmbeddingManager,
    AgentCapability,
    EmbeddingResult
)

from .vector_search import (
    VectorSearchManager,
    SearchResult,
    SearchQuery,
    SearchBackend,
    PgVectorSearch,
    FAISSVectorSearch,
    HybridVectorSearch
)

from .request_analyzer import (
    RequestAnalyzer,
    RequestAnalysis,
    SemanticMatcher,
    ProjectContext,
    IntentCategory,
    ComplexityLevel,
    RiskLevel
)

from .multi_agent_orchestrator import (
    MultiAgentOrchestrator,
    WorkflowRecommendation,
    AgentRole,
    WorkflowPattern
)

from .success_predictor import (
    SuccessPredictor,
    PredictionResult,
    ModelPerformanceMetrics
)

from .integration_layer import (
    SemanticAgentSelector,
    HybridAgentSelector,
    EnhancedAgentSelection,
    SelectionStrategy,
    HybridRecommendation
)

# Main entry point
__all__ = [
    # Core Classes
    "SemanticAgentSelector",
    "HybridAgentSelector",
    "EnhancedAgentSelection",
    
    # Selection Strategies
    "SelectionStrategy",
    
    # Analysis Components
    "RequestAnalyzer",
    "RequestAnalysis", 
    "ProjectContext",
    "IntentCategory",
    "ComplexityLevel", 
    "RiskLevel",
    
    # Vector Search
    "VectorSearchManager",
    "SearchResult",
    "SearchQuery",
    "SearchBackend",
    
    # Agent Embeddings
    "AgentCapabilityEmbedder",
    "AgentEmbeddingManager",
    "AgentCapability",
    "EmbeddingResult",
    
    # Orchestration
    "MultiAgentOrchestrator",
    "WorkflowRecommendation",
    "AgentRole",
    "WorkflowPattern",
    
    # Success Prediction
    "SuccessPredictor",
    "PredictionResult",
    "ModelPerformanceMetrics",
    
    # Results
    "HybridRecommendation",
    
    # Utilities
    "create_production_config",
    "create_development_config",
    "initialize_system"
]


def create_production_config(
    db_url: str,
    redis_url: str,
    faiss_index_path: str,
    model_path: str,
    **kwargs
) -> dict:
    """
    Create production configuration for the semantic agent selection system.
    
    Args:
        db_url: PostgreSQL database URL with pgvector extension
        redis_url: Redis URL for caching
        faiss_index_path: Path to FAISS index directory
        model_path: Path to ML models directory
        **kwargs: Additional configuration options
        
    Returns:
        Configuration dictionary for production deployment
    """
    return {
        "db_url": db_url,
        "redis_url": redis_url,
        "faiss_index_path": faiss_index_path,
        "model_path": model_path,
        "embedding_model": kwargs.get("embedding_model", "all-MiniLM-L6-v2"),
        "vector_search_backend": kwargs.get("vector_search_backend", SearchBackend.HYBRID),
        "enable_caching": kwargs.get("enable_caching", True),
        "enable_analytics": kwargs.get("enable_analytics", True),
        "max_agents": kwargs.get("max_agents", 5),
        "similarity_threshold": kwargs.get("similarity_threshold", 0.3),
        "confidence_threshold": kwargs.get("confidence_threshold", 0.5),
        "default_strategy": kwargs.get("default_strategy", SelectionStrategy.ADAPTIVE),
        "cache_ttl": kwargs.get("cache_ttl", 3600),  # 1 hour
        "performance_monitoring": kwargs.get("performance_monitoring", True),
        "auto_retrain": kwargs.get("auto_retrain", False),
        "retrain_threshold": kwargs.get("retrain_threshold", 1000),  # samples
        "fallback_enabled": kwargs.get("fallback_enabled", True),
        "debug_mode": kwargs.get("debug_mode", False)
    }


def create_development_config(
    db_url: str,
    **kwargs
) -> dict:
    """
    Create development configuration with reduced dependencies.
    
    Args:
        db_url: PostgreSQL database URL
        **kwargs: Additional configuration options
        
    Returns:
        Configuration dictionary for development
    """
    return {
        "db_url": db_url,
        "redis_url": None,  # No Redis in dev
        "faiss_index_path": kwargs.get("faiss_index_path", "./dev_faiss_index"),
        "model_path": kwargs.get("model_path", "./dev_models"),
        "embedding_model": kwargs.get("embedding_model", "all-MiniLM-L6-v2"),
        "vector_search_backend": SearchBackend.PGVECTOR,  # Simpler in dev
        "enable_caching": False,
        "enable_analytics": True,
        "max_agents": kwargs.get("max_agents", 3),
        "similarity_threshold": kwargs.get("similarity_threshold", 0.2),
        "confidence_threshold": kwargs.get("confidence_threshold", 0.3),
        "default_strategy": SelectionStrategy.HYBRID_SEMANTIC_PRIMARY,
        "cache_ttl": 300,  # 5 minutes
        "performance_monitoring": False,
        "auto_retrain": False,
        "fallback_enabled": True,
        "debug_mode": True
    }


def create_minimal_config(db_url: str) -> dict:
    """
    Create minimal configuration for testing or resource-constrained environments.
    
    Args:
        db_url: PostgreSQL database URL
        
    Returns:
        Minimal configuration dictionary
    """
    return {
        "db_url": db_url,
        "redis_url": None,
        "faiss_index_path": None,  # Use only pgvector
        "model_path": None,  # Use rule-based predictions
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_search_backend": SearchBackend.PGVECTOR,
        "enable_caching": False,
        "enable_analytics": False,
        "max_agents": 2,
        "similarity_threshold": 0.1,
        "confidence_threshold": 0.1,
        "default_strategy": SelectionStrategy.HYBRID_KEYWORD_PRIMARY,
        "cache_ttl": 0,
        "performance_monitoring": False,
        "auto_retrain": False,
        "fallback_enabled": True,
        "debug_mode": False
    }


async def initialize_system(config: dict, agents_dir: str = "agents") -> SemanticAgentSelector:
    """
    Initialize the complete semantic agent selection system.
    
    Args:
        config: Configuration dictionary from create_*_config functions
        agents_dir: Path to agents directory with markdown files
        
    Returns:
        Initialized SemanticAgentSelector instance
        
    Raises:
        ValueError: If required configuration is missing
        RuntimeError: If initialization fails
    """
    # Validate required configuration
    if not config.get("db_url"):
        raise ValueError("Database URL is required")
    
    try:
        # Initialize main selector
        selector = SemanticAgentSelector(
            db_url=config["db_url"],
            redis_url=config.get("redis_url"),
            faiss_index_path=config.get("faiss_index_path"),
            model_path=config.get("model_path")
        )
        
        # Initialize all components
        await selector.initialize()
        
        # Generate agent embeddings if agents directory exists
        import os
        if os.path.exists(agents_dir):
            from pathlib import Path
            
            # Initialize embedding manager
            embedding_manager = AgentEmbeddingManager(
                db_url=config["db_url"],
                agents_dir=agents_dir,
                model_name=config.get("embedding_model", "all-MiniLM-L6-v2")
            )
            
            await embedding_manager.initialize()
            
            # Scan and process agents
            embedding_results = await embedding_manager.scan_and_process_agents()
            
            print(f"✓ Processed {len(embedding_results)} agent capabilities")
            
            # Rebuild FAISS index if configured
            if config.get("faiss_index_path"):
                await selector.vector_search.rebuild_faiss_index()
                print("✓ FAISS index rebuilt")
            
            await embedding_manager.close()
        
        print("✓ Semantic agent selection system initialized successfully")
        return selector
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize system: {e}")


# Version compatibility check
def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import asyncpg
    except ImportError:
        missing_deps.append("asyncpg")
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        missing_deps.append("sentence-transformers")
    
    try:
        import sklearn
    except ImportError:
        missing_deps.append("scikit-learn")
    
    try:
        import faiss
    except ImportError:
        missing_deps.append("faiss-cpu or faiss-gpu")
    
    if missing_deps:
        raise ImportError(
            f"Missing required dependencies: {', '.join(missing_deps)}\n"
            f"Install with: pip install {' '.join(missing_deps)}"
        )
    
    return True


# Run dependency check on import
try:
    check_dependencies()
except ImportError as e:
    import warnings
    warnings.warn(f"Dependency check failed: {e}", ImportWarning)


# Module-level convenience functions
async def quick_select_agents(
    request: str,
    config: dict,
    agents_dir: str = "agents",
    project_path: str = None
) -> EnhancedAgentSelection:
    """
    Quick agent selection for simple use cases.
    
    Args:
        request: User request string
        config: Configuration dictionary
        agents_dir: Path to agents directory
        project_path: Optional project path for context
        
    Returns:
        EnhancedAgentSelection with recommended agents
    """
    from pathlib import Path
    
    selector = await initialize_system(config, agents_dir)
    
    try:
        return await selector.select_agents(
            request=request,
            project_path=Path(project_path) if project_path else None
        )
    finally:
        await selector.close()


def get_system_info() -> dict:
    """Get system information and status."""
    import platform
    import sys
    
    try:
        import torch
        torch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
        cuda_devices = torch.cuda.device_count() if cuda_available else 0
    except ImportError:
        torch_version = "Not installed"
        cuda_available = False
        cuda_devices = 0
    
    return {
        "version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "torch_version": torch_version,
        "cuda_available": cuda_available,
        "cuda_devices": cuda_devices,
        "dependencies_ok": True  # If we got here, dependencies are OK
    }


# Export configuration for external tools
SYSTEM_CONFIG = {
    "name": "Semantic Agent Selection System",
    "version": __version__,
    "description": __doc__,
    "author": __author__,
    "supported_backends": ["pgvector", "faiss", "hybrid"],
    "supported_strategies": [strategy.value for strategy in SelectionStrategy],
    "embedding_models": ["all-MiniLM-L6-v2", "all-mpnet-base-v2"],
    "database_requirements": ["PostgreSQL 12+", "pgvector extension"],
    "optional_dependencies": ["Redis", "TimescaleDB"]
}