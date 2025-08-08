# Semantic Agent Selection System

A production-ready AI-powered agent selection system that replaces keyword matching with intelligent semantic understanding using embeddings, machine learning, and multi-level caching for optimal performance.

## 🚀 Features

### Core Capabilities
- **Semantic Understanding**: Uses sentence transformers and embeddings to understand user intent and agent capabilities
- **Hybrid Approach**: Combines semantic analysis with keyword matching for robust fallback
- **Multi-Agent Orchestration**: Intelligent workflow recommendations with agent role assignment
- **Success Prediction**: ML-based prediction of agent success probability with confidence scoring
- **Context Integration**: Analyzes project structure, technology stack, and historical patterns

### Performance & Reliability
- **Multi-Level Caching**: Memory, Redis, and database caching for sub-second response times
- **Vector Search**: Optimized similarity search with pgvector and FAISS support
- **Circuit Breakers**: Automatic fallback mechanisms for system reliability
- **Performance Monitoring**: Real-time metrics and performance optimization
- **Graceful Degradation**: Maintains functionality even when components fail

### Production Ready
- **Comprehensive Testing**: Unit, integration, and performance test frameworks
- **Analytics Integration**: Connects with existing analytics for continuous improvement
- **Database Schema**: Full PostgreSQL schema with TimescaleDB for time-series data
- **Deployment Support**: Docker, Kubernetes, and cloud deployment configurations

## 📋 Requirements

### System Requirements
- Python 3.8+
- PostgreSQL 12+ with pgvector extension
- Redis 6+ (optional, for caching)
- 4GB+ RAM recommended
- GPU support optional (for faster embedding generation)

### Dependencies
```bash
# Core ML dependencies
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.21.0
faiss-cpu>=1.7.0  # or faiss-gpu for GPU support

# Database dependencies
asyncpg>=0.28.0
redis>=4.5.0

# Performance and utilities
psutil>=5.9.0
cachetools>=5.3.0
aiofiles>=23.0.0
```

## 🛠 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL with pgvector
```bash
# Install PostgreSQL and pgvector extension
# Ubuntu/Debian:
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo apt install postgresql-14-pgvector

# macOS with Homebrew:
brew install postgresql pgvector

# Create database
createdb semantic_agent_db
psql -d semantic_agent_db -c "CREATE EXTENSION vector;"
```

### 3. Initialize Database Schema
```bash
psql -d semantic_agent_db -f semantic_agent_selection/schema.sql
```

### 4. Install Optional Components
```bash
# For TimescaleDB (optional, for better time-series performance)
sudo apt install timescaledb-2-postgresql-14
# or
brew install timescaledb

# For Redis (optional, for distributed caching)
sudo apt install redis-server
# or  
brew install redis
```

## 🚀 Quick Start

### Basic Usage
```python
import asyncio
from semantic_agent_selection import (
    SemanticAgentSelector,
    initialize_system,
    create_development_config
)

async def main():
    # Create configuration
    config = create_development_config(
        db_url="postgresql://user:pass@localhost/semantic_agent_db"
    )
    
    # Initialize system (this processes agent markdown files)
    selector = await initialize_system(config, agents_dir="agents")
    
    try:
        # Select agents for a request
        result = await selector.select_agents(
            request="I want to build a React application with user authentication",
            project_path="./my-project"
        )
        
        print(f"Recommended agents: {result.primary_recommendation.agent_names}")
        print(f"Confidence: {result.confidence_level}")
        print(f"Explanation: {result.explanation}")
        
    finally:
        await selector.close()

# Run the example
asyncio.run(main())
```

### Production Setup
```python
from semantic_agent_selection import (
    SemanticAgentSelector,
    create_production_config,
    OptimizedSemanticAgentSelector,
    PerformanceProfile
)

async def production_setup():
    # Production configuration
    config = create_production_config(
        db_url="postgresql://user:pass@prod-db:5432/semantic_agent_db",
        redis_url="redis://redis-cluster:6379",
        faiss_index_path="/data/faiss_index",
        model_path="/data/ml_models"
    )
    
    # Create base selector
    base_selector = SemanticAgentSelector(**config)
    
    # Wrap with performance optimizations
    selector = OptimizedSemanticAgentSelector(
        base_selector=base_selector,
        performance_profile=PerformanceProfile.AGGRESSIVE,
        redis_url=config['redis_url']
    )
    
    await selector.initialize()
    
    # Your application logic here...
    
    await selector.close()
```

## 📊 Configuration Options

### Development Configuration
```python
config = create_development_config(
    db_url="postgresql://localhost/test_db",
    faiss_index_path="./dev_index",
    model_path="./dev_models"
)
```

### Production Configuration
```python
config = create_production_config(
    db_url="postgresql://user:pass@host:5432/db",
    redis_url="redis://host:6379/1",
    faiss_index_path="/data/faiss_index",
    model_path="/data/models",
    embedding_model="all-MiniLM-L6-v2",
    vector_search_backend=SearchBackend.HYBRID,
    max_agents=5,
    similarity_threshold=0.3,
    default_strategy=SelectionStrategy.ADAPTIVE
)
```

### Performance Profiles
- **MINIMAL**: Lowest resource usage, basic functionality
- **BALANCED**: Good performance with reasonable resource usage  
- **AGGRESSIVE**: Maximum performance, high resource usage

## 🎯 Agent Selection Strategies

The system supports multiple selection strategies:

### 1. Adaptive (Recommended)
```python
result = await selector.select_agents(
    request="Build a secure web application",
    strategy=SelectionStrategy.ADAPTIVE
)
```
Automatically chooses the best approach based on request characteristics.

### 2. Semantic Only
```python
result = await selector.select_agents(
    request="Complex AI-powered recommendation system", 
    strategy=SelectionStrategy.SEMANTIC_ONLY
)
```
Uses only semantic understanding for agent matching.

### 3. Hybrid Approaches
```python
# Semantic primary with keyword fallback
result = await selector.select_agents(
    request="React app with TypeScript",
    strategy=SelectionStrategy.HYBRID_SEMANTIC_PRIMARY
)

# Keyword primary with semantic enhancement
result = await selector.select_agents(
    request="iOS Swift development",
    strategy=SelectionStrategy.HYBRID_KEYWORD_PRIMARY
)
```

## 📈 Performance Optimization

### Caching Configuration
```python
from semantic_agent_selection.performance_optimization import (
    CacheConfig,
    create_optimized_config
)

# Custom cache configuration
cache_config = CacheConfig(
    enable_memory_cache=True,
    memory_cache_size=1000,
    memory_cache_ttl=3600,
    enable_redis_cache=True,
    redis_ttl=7200,
    enable_compression=True
)
```

### Performance Monitoring
```python
# Get performance statistics
stats = selector.get_performance_stats()
print(f"Cache hit rate: {stats['cache_stats']['hit_rate']:.2%}")
print(f"Average response time: {stats['monitor_stats']['avg_response_time']:.3f}s")
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest semantic_agent_selection/test_framework.py -v
```

### Run Integration Tests
```bash
python -m semantic_agent_selection.test_framework \
    --db-url postgresql://localhost/test_db \
    --scenario all \
    --performance \
    --output test_report.md
```

### Run Specific Test Scenarios
```bash
# Test web development scenarios only
python -m semantic_agent_selection.test_framework \
    --db-url postgresql://localhost/test_db \
    --scenario web

# Test with performance benchmarks
python -m semantic_agent_selection.test_framework \
    --db-url postgresql://localhost/test_db \
    --performance \
    --num-requests 500
```

### Custom Test Scenarios
```python
from semantic_agent_selection.test_framework import (
    TestScenario,
    SemanticAgentSelectionTester,
    IntentCategory,
    ComplexityLevel,
    RiskLevel
)

# Define custom test scenario
custom_scenario = TestScenario(
    name="E-commerce Platform",
    request="Build a scalable e-commerce platform with payment processing",
    expected_agents=["full-stack-architect", "security-audit-specialist", "devops-engineer"],
    expected_intent=IntentCategory.NEW_PROJECT,
    expected_complexity=ComplexityLevel.COMPLEX,
    expected_risk=RiskLevel.HIGH,
    min_confidence=0.7
)

# Run test
tester = SemanticAgentSelectionTester(db_url="postgresql://localhost/test_db")
await tester.setup()
results = await tester.run_scenario_tests([custom_scenario])
print(f"Test passed: {results[0].passed}")
await tester.teardown()
```

## 📚 API Reference

### Core Classes

#### SemanticAgentSelector
Main entry point for semantic agent selection.

```python
selector = SemanticAgentSelector(
    db_url="postgresql://localhost/db",
    redis_url="redis://localhost:6379",  # optional
    faiss_index_path="./faiss_index",    # optional
    model_path="./models"                # optional
)

await selector.initialize()

result = await selector.select_agents(
    request="User request string",
    project_path=Path("./project"),      # optional
    strategy=SelectionStrategy.ADAPTIVE, # optional
    max_agents=5                         # optional
)
```

#### RequestAnalyzer
Analyzes user requests to extract intent and context.

```python
analyzer = RequestAnalyzer()
await analyzer.initialize()

analysis = await analyzer.analyze_request(
    request="Build a mobile app",
    project_path=Path("./project")
)

print(f"Intent: {analysis.intent_category}")
print(f"Complexity: {analysis.complexity_level}")
print(f"Risk: {analysis.risk_level}")
```

#### MultiAgentOrchestrator
Recommends optimal agent workflows.

```python
orchestrator = MultiAgentOrchestrator(db_url="postgresql://localhost/db")
await orchestrator.initialize()

workflow = await orchestrator.recommend_workflow(
    analysis=request_analysis,
    candidate_agents=search_results,
    max_agents=5
)

print(f"Primary agents: {[a.agent_name for a in workflow.primary_agents]}")
print(f"Workflow pattern: {workflow.workflow_pattern}")
```

### Result Objects

#### EnhancedAgentSelection
Comprehensive agent selection result.

```python
class EnhancedAgentSelection:
    primary_recommendation: WorkflowRecommendation
    alternative_recommendations: List[WorkflowRecommendation]
    selection_strategy: SelectionStrategy
    confidence_level: str  # "low", "medium", "high"
    processing_time: float
    fallback_used: bool
    explanation: str
```

#### WorkflowRecommendation
Multi-agent workflow recommendation.

```python
class WorkflowRecommendation:
    primary_agents: List[AgentRole]
    supporting_agents: List[AgentRole] 
    validation_agents: List[AgentRole]
    workflow_pattern: WorkflowPattern
    confidence_score: float
    success_probability: float
    explanation: str
```

## 🔧 Advanced Usage

### Custom Embedding Models
```python
from semantic_agent_selection import AgentEmbeddingManager

# Use custom embedding model
manager = AgentEmbeddingManager(
    db_url="postgresql://localhost/db",
    agents_dir="./custom_agents",
    model_name="all-mpnet-base-v2"  # Different model
)

await manager.initialize()
results = await manager.scan_and_process_agents()
```

### Project Context Analysis
```python
from semantic_agent_selection.request_analyzer import ProjectContextExtractor

extractor = ProjectContextExtractor()
context = await extractor.extract_context(Path("./my-project"))

print(f"Technologies: {context.technologies}")
print(f"Frameworks: {context.frameworks}")
print(f"Project type: {context.project_type}")
print(f"Has AI features: {context.has_ai_features}")
```

### Success Prediction
```python
from semantic_agent_selection import SuccessPredictor

predictor = SuccessPredictor()
await predictor.initialize(db_url="postgresql://localhost/db")

predictions = await predictor.predict_success(
    agent_results=search_results,
    analysis=request_analysis,
    historical_data=historical_performance
)

for pred in predictions:
    print(f"{pred.agent_name}: {pred.success_probability:.2f} ({pred.confidence_score:.2f})")
```

## 🐳 Docker Deployment

### Docker Compose Setup
```yaml
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: semantic_agent_db
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - ./semantic_agent_selection/schema.sql:/docker-entrypoint-initdb.d/schema.sql
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    
  semantic-agent-api:
    build: .
    environment:
      DATABASE_URL: postgresql://agent_user:secure_password@postgres:5432/semantic_agent_db
      REDIS_URL: redis://redis:6379
      FAISS_INDEX_PATH: /data/faiss_index
      MODEL_PATH: /data/models
    volumes:
      - ./agents:/app/agents:ro
      - faiss_data:/data/faiss_index
      - model_data:/data/models
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
  faiss_data:
  model_data:
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY semantic_agent_selection/ ./semantic_agent_selection/
COPY agents/ ./agents/

# Initialize system
RUN python -c "
import asyncio
from semantic_agent_selection import initialize_system, create_production_config
# Pre-download models
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
"

EXPOSE 8000

CMD ["python", "-m", "semantic_agent_selection.api_server"]
```

## 🔍 Monitoring and Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable component-specific logging
logging.getLogger('semantic_agent_selection').setLevel(logging.DEBUG)
logging.getLogger('semantic_agent_selection.vector_search').setLevel(logging.INFO)
```

### Performance Monitoring
```python
from semantic_agent_selection.performance_optimization import PerformanceMonitor

monitor = PerformanceMonitor(collection_interval=30)
await monitor.start_monitoring()

# Get real-time stats
stats = monitor.get_current_stats()
print(f"Active requests: {stats['active_requests']}")
print(f"Average response time: {stats['avg_response_time']:.3f}s")
print(f"Memory usage: {stats['memory_usage_mb']:.1f} MB")
```

### Database Monitoring
```python
# Check database performance
async with selector.vector_search.pg_search.db_pool.acquire() as conn:
    # Check connection count
    result = await conn.fetchval("SELECT count(*) FROM pg_stat_activity")
    print(f"Active connections: {result}")
    
    # Check vector index performance  
    result = await conn.fetchval("""
        SELECT schemaname, tablename, attname, n_distinct, correlation 
        FROM pg_stats 
        WHERE tablename = 'agent_embeddings' AND attname = 'capability_vector'
    """)
```

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd semantic_agent_selection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all public APIs
- Write comprehensive docstrings
- Add unit tests for new features
- Use async/await for I/O operations

### Adding New Features
1. Create feature branch from main
2. Implement feature with tests
3. Update documentation
4. Run full test suite
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

### Documentation
- [API Reference](./docs/api.md)
- [Architecture Guide](./docs/architecture.md)
- [Performance Tuning](./docs/performance.md)
- [Deployment Guide](./docs/deployment.md)

### Getting Help
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas
- Wiki: Community documentation and examples

### Common Issues

#### "pgvector extension not found"
```bash
# Install pgvector extension
sudo apt install postgresql-14-pgvector
# or
brew install pgvector

# Enable in database
psql -d your_db -c "CREATE EXTENSION vector;"
```

#### "Redis connection failed"
```bash
# Install and start Redis
sudo apt install redis-server
sudo systemctl start redis

# or disable Redis caching
config = create_development_config(db_url, enable_redis=False)
```

#### "Embedding model download failed"
```bash
# Pre-download models
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
"
```

#### Performance Issues
```python
# Use performance profiling
config = create_production_config(
    # ... your config
    performance_profile=PerformanceProfile.AGGRESSIVE,
    enable_caching=True
)
```

---

**Built with ❤️ for intelligent agent orchestration**