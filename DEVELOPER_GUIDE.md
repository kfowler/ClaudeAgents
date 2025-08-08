# Claude Code 2.0: Developer Guide

## Overview

This guide provides comprehensive documentation for developers who want to extend, customize, and integrate with Claude Code 2.0's AI-enhanced agent orchestration system. Whether you're creating custom agents, building integrations, or contributing to the core platform, this guide covers everything you need to know.

## 🚀 Getting Started

### Development Environment Setup

#### **Prerequisites**

```bash
# Install required tools
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
curl -sSL https://get.sonarsource.com/sonarqube | sh

# Install Python 3.11+ and pip
sudo apt update && sudo apt install python3.11 python3.11-pip python3.11-venv

# Install Node.js 18+ (for frontend development)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install development utilities
pip install poetry pre-commit black isort mypy pytest
npm install -g typescript tsx eslint prettier
```

#### **Local Development Setup**

```bash
# Clone the repository
git clone https://github.com/anthropic/claude-agents.git
cd claude-agents

# Set up Python environment
poetry install --with dev,test
poetry shell

# Set up pre-commit hooks
pre-commit install

# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Run initial setup
python scripts/setup_dev_environment.py

# Verify setup
python -m pytest tests/integration/test_setup.py
```

#### **Development Configuration**

```yaml
# config/development.yaml
api:
  debug: true
  reload: true
  host: "0.0.0.0"
  port: 8080

database:
  url: "postgresql://claude_dev:password@localhost:5432/claude_dev"
  echo: true  # SQL query logging
  
redis:
  url: "redis://localhost:6379/0"
  
ai_services:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  cache_embeddings: true
  mock_ml_services: false  # Set to true for faster development
  
logging:
  level: "DEBUG"
  format: "detailed"
  
testing:
  database_url: "postgresql://claude_test:password@localhost:5432/claude_test"
  mock_external_apis: true
```

## 🧠 AI System Architecture

### Core Components Overview

```python
# src/claude/ai/core.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class AgentSelector(ABC):
    """Base class for agent selection strategies"""
    
    @abstractmethod
    async def select_agents(
        self,
        request: UserRequest,
        context: ProjectContext,
        user_profile: UserProfile,
        max_agents: int = 3
    ) -> List[AgentRecommendation]:
        pass

class UserRequest:
    """Structured user request representation"""
    def __init__(
        self,
        text: str,
        project_path: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.project_path = project_path
        self.additional_context = additional_context or {}
        self.embedding: Optional[np.ndarray] = None
        self.processed_intent: Optional[Dict[str, Any]] = None

class ProjectContext:
    """Project context and analysis results"""
    def __init__(self):
        self.tech_stack: List[str] = []
        self.dependencies: Dict[str, str] = {}
        self.architecture_patterns: List[str] = []
        self.complexity_score: float = 0.0
        self.risk_level: str = "low"
        self.file_structure: Dict[str, Any] = {}
        self.git_history: Optional[Dict[str, Any]] = None

class AgentRecommendation:
    """Agent recommendation with confidence and reasoning"""
    def __init__(
        self,
        agent_id: str,
        confidence_score: float,
        reasoning: str,
        estimated_success_rate: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.confidence_score = confidence_score
        self.reasoning = reasoning
        self.estimated_success_rate = estimated_success_rate
        self.metadata = metadata or {}
```

### Implementing Custom Agent Selectors

#### **Rule-Based Agent Selector**

```python
# src/claude/ai/selectors/rule_based.py
import re
from typing import List, Dict, Set
from claude.ai.core import AgentSelector, UserRequest, ProjectContext, UserProfile, AgentRecommendation

class RuleBasedAgentSelector(AgentSelector):
    """Traditional rule-based agent selection using keyword matching"""
    
    def __init__(self, rules_config: Dict[str, Any]):
        self.rules = rules_config
        self.agent_keywords = self._load_agent_keywords()
        self.technology_mappings = self._load_technology_mappings()
    
    async def select_agents(
        self,
        request: UserRequest,
        context: ProjectContext,
        user_profile: UserProfile,
        max_agents: int = 3
    ) -> List[AgentRecommendation]:
        
        # Extract keywords from request
        keywords = self._extract_keywords(request.text)
        
        # Match agents based on keywords
        agent_matches = self._match_agents_by_keywords(keywords)
        
        # Enhance with context information
        context_matches = self._match_agents_by_context(context)
        
        # Combine and score recommendations
        recommendations = self._combine_and_score(
            agent_matches, 
            context_matches, 
            user_profile
        )
        
        return recommendations[:max_agents]
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract relevant keywords from user request"""
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter for technical keywords
        keywords = set()
        for word in words:
            if word in self.agent_keywords or word in self.technology_mappings:
                keywords.add(word)
        
        return keywords
    
    def _match_agents_by_keywords(self, keywords: Set[str]) -> Dict[str, float]:
        """Match agents based on keyword presence"""
        agent_scores = {}
        
        for agent_id, agent_keywords in self.agent_keywords.items():
            score = len(keywords.intersection(set(agent_keywords)))
            if score > 0:
                agent_scores[agent_id] = score / len(agent_keywords)
        
        return agent_scores
    
    def _match_agents_by_context(self, context: ProjectContext) -> Dict[str, float]:
        """Match agents based on project context"""
        agent_scores = {}
        
        # Technology stack matching
        for tech in context.tech_stack:
            if tech in self.technology_mappings:
                for agent_id in self.technology_mappings[tech]:
                    agent_scores[agent_id] = agent_scores.get(agent_id, 0) + 0.5
        
        # Architecture pattern matching
        for pattern in context.architecture_patterns:
            if pattern == "microservices":
                agent_scores["devops-engineer"] = agent_scores.get("devops-engineer", 0) + 0.3
                agent_scores["systems-engineer"] = agent_scores.get("systems-engineer", 0) + 0.2
            elif pattern == "spa":
                agent_scores["full-stack-architect"] = agent_scores.get("full-stack-architect", 0) + 0.4
        
        # Risk-based agent inclusion
        if context.risk_level in ["high", "critical"]:
            agent_scores["security-audit-specialist"] = agent_scores.get("security-audit-specialist", 0) + 0.8
            agent_scores["qa-test-engineer"] = agent_scores.get("qa-test-engineer", 0) + 0.6
        
        return agent_scores
```

#### **ML-Enhanced Agent Selector**

```python
# src/claude/ai/selectors/ml_enhanced.py
import asyncio
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from claude.ai.core import AgentSelector, UserRequest, ProjectContext, UserProfile, AgentRecommendation

class MLEnhancedAgentSelector(AgentSelector):
    """ML-enhanced agent selection using embeddings and learned preferences"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.embedding_model = SentenceTransformer(
            model_config.get("model_name", "all-MiniLM-L6-v2")
        )
        self.agent_embeddings = None
        self.user_preference_model = None
        self.success_predictor = None
        
    async def initialize(self):
        """Initialize ML models and agent embeddings"""
        # Load agent embeddings
        self.agent_embeddings = await self._load_agent_embeddings()
        
        # Load user preference model
        self.user_preference_model = await self._load_user_preference_model()
        
        # Load success predictor
        self.success_predictor = await self._load_success_predictor()
    
    async def select_agents(
        self,
        request: UserRequest,
        context: ProjectContext,
        user_profile: UserProfile,
        max_agents: int = 3
    ) -> List[AgentRecommendation]:
        
        # Generate request embedding
        request_embedding = await self._embed_request(request, context)
        
        # Calculate similarity scores
        similarity_scores = await self._calculate_similarity(request_embedding)
        
        # Apply user preferences
        preference_scores = await self._apply_user_preferences(
            similarity_scores, 
            user_profile
        )
        
        # Predict success rates
        success_predictions = await self._predict_success(
            preference_scores, 
            request, 
            context
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            preference_scores,
            success_predictions,
            max_agents
        )
        
        return recommendations
    
    async def _embed_request(
        self, 
        request: UserRequest, 
        context: ProjectContext
    ) -> np.ndarray:
        """Generate embedding for user request with context"""
        
        # Combine request text with context information
        context_text = self._context_to_text(context)
        combined_text = f"{request.text} {context_text}"
        
        # Generate embedding
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, 
            self.embedding_model.encode, 
            combined_text
        )
        
        return embedding
    
    async def _calculate_similarity(
        self, 
        request_embedding: np.ndarray
    ) -> Dict[str, float]:
        """Calculate cosine similarity between request and agent embeddings"""
        
        similarities = {}
        for agent_id, agent_embedding in self.agent_embeddings.items():
            similarity = cosine_similarity(
                [request_embedding], 
                [agent_embedding]
            )[0][0]
            similarities[agent_id] = float(similarity)
        
        return similarities
    
    async def _apply_user_preferences(
        self,
        similarity_scores: Dict[str, float],
        user_profile: UserProfile
    ) -> Dict[str, float]:
        """Apply learned user preferences to similarity scores"""
        
        if not self.user_preference_model or not user_profile.preference_vector:
            return similarity_scores
        
        # Apply preference weighting
        adjusted_scores = {}
        for agent_id, similarity in similarity_scores.items():
            preference_weight = user_profile.agent_preferences.get(agent_id, 1.0)
            adjusted_scores[agent_id] = similarity * preference_weight
        
        return adjusted_scores
    
    async def _predict_success(
        self,
        scores: Dict[str, float],
        request: UserRequest,
        context: ProjectContext
    ) -> Dict[str, float]:
        """Predict success rate for each agent"""
        
        if not self.success_predictor:
            # Default success prediction based on similarity
            return {agent_id: min(score * 0.8 + 0.2, 1.0) for agent_id, score in scores.items()}
        
        predictions = {}
        for agent_id, score in scores.items():
            features = self._extract_features(agent_id, request, context, score)
            success_rate = await self.success_predictor.predict(features)
            predictions[agent_id] = float(success_rate)
        
        return predictions
```

## 🔧 Creating Custom Agents

### Agent Interface Definition

```python
# src/claude/agents/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentTask:
    task_id: str
    description: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    priority: int = 1
    timeout: Optional[int] = None

@dataclass 
class AgentResult:
    task_id: str
    status: AgentStatus
    output: Any
    metadata: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

class BaseAgent(ABC):
    """Base class for all Claude Code agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = AgentStatus.IDLE
        self.capabilities = self._define_capabilities()
        self.supported_technologies = self._define_supported_technologies()
    
    @abstractmethod
    def _define_capabilities(self) -> List[str]:
        """Define the capabilities of this agent"""
        pass
    
    @abstractmethod
    def _define_supported_technologies(self) -> List[str]:
        """Define technologies this agent can work with"""
        pass
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a task and return results"""
        pass
    
    async def validate_task(self, task: AgentTask) -> bool:
        """Validate if this agent can handle the given task"""
        return True
    
    async def estimate_duration(self, task: AgentTask) -> int:
        """Estimate task duration in seconds"""
        return self.config.get("default_timeout", 300)
    
    async def health_check(self) -> bool:
        """Check if agent is healthy and ready to work"""
        return self.status != AgentStatus.FAILED
    
    async def get_progress(self, task_id: str) -> float:
        """Get task progress (0.0 to 1.0)"""
        return 0.0 if self.status == AgentStatus.IDLE else 0.5
```

### Example Custom Agent Implementation

#### **Database Migration Agent**

```python
# src/claude/agents/database_migration_specialist.py
import asyncio
import subprocess
from typing import List, Dict, Any
from claude.agents.base import BaseAgent, AgentTask, AgentResult, AgentStatus

class DatabaseMigrationSpecialist(BaseAgent):
    """Specialized agent for database schema migrations and data transformations"""
    
    def _define_capabilities(self) -> List[str]:
        return [
            "schema_migration",
            "data_transformation", 
            "migration_rollback",
            "migration_validation",
            "database_backup",
            "migration_planning"
        ]
    
    def _define_supported_technologies(self) -> List[str]:
        return [
            "postgresql",
            "mysql", 
            "sqlite",
            "alembic",
            "flyway",
            "liquibase",
            "django-migrations",
            "rails-migrations"
        ]
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute database migration task"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.status = AgentStatus.RUNNING
            
            # Determine migration type
            migration_type = task.parameters.get("type", "schema")
            
            if migration_type == "schema":
                result = await self._execute_schema_migration(task)
            elif migration_type == "data":
                result = await self._execute_data_migration(task)
            elif migration_type == "rollback":
                result = await self._execute_rollback(task)
            elif migration_type == "validate":
                result = await self._validate_migration(task)
            else:
                raise ValueError(f"Unknown migration type: {migration_type}")
            
            self.status = AgentStatus.COMPLETED
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.COMPLETED,
                output=result,
                metadata={
                    "migration_type": migration_type,
                    "database_type": task.context.get("database_type"),
                    "migrations_applied": result.get("migrations_applied", [])
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                output=None,
                metadata={"error_details": str(e)},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _execute_schema_migration(self, task: AgentTask) -> Dict[str, Any]:
        """Execute schema migration"""
        database_url = task.context.get("database_url")
        migration_files = task.parameters.get("migration_files", [])
        
        # Create backup before migration
        backup_result = await self._create_backup(database_url)
        
        # Apply migrations
        applied_migrations = []
        for migration_file in migration_files:
            result = await self._apply_migration_file(database_url, migration_file)
            if result["success"]:
                applied_migrations.append(migration_file)
            else:
                # Rollback on failure
                await self._rollback_to_backup(database_url, backup_result["backup_file"])
                raise Exception(f"Migration failed: {result['error']}")
        
        # Validate final state
        validation_result = await self._validate_schema(database_url)
        
        return {
            "backup_file": backup_result["backup_file"],
            "migrations_applied": applied_migrations,
            "validation_result": validation_result,
            "success": True
        }
    
    async def _apply_migration_file(self, database_url: str, migration_file: str) -> Dict[str, Any]:
        """Apply a single migration file"""
        try:
            # Determine database type and use appropriate tool
            if "postgresql" in database_url:
                cmd = f"psql {database_url} -f {migration_file}"
            elif "mysql" in database_url:
                cmd = f"mysql --defaults-extra-file=<(echo '[client]'; echo 'password=...') -h host -u user db < {migration_file}"
            else:
                raise ValueError("Unsupported database type")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode(),
                    "migration_file": migration_file
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "migration_file": migration_file
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "migration_file": migration_file
            }
    
    async def validate_task(self, task: AgentTask) -> bool:
        """Validate if this agent can handle the migration task"""
        required_params = ["type"]
        if not all(param in task.parameters for param in required_params):
            return False
        
        database_type = task.context.get("database_type", "").lower()
        if database_type and database_type not in self.supported_technologies:
            return False
        
        return True
```

#### **Performance Optimization Agent**

```python
# src/claude/agents/performance_optimizer.py
import ast
import re
import asyncio
from typing import List, Dict, Any, Tuple
from claude.agents.base import BaseAgent, AgentTask, AgentResult, AgentStatus

class PerformanceOptimizer(BaseAgent):
    """Agent specialized in performance analysis and optimization"""
    
    def _define_capabilities(self) -> List[str]:
        return [
            "performance_profiling",
            "code_optimization",
            "database_query_optimization", 
            "memory_leak_detection",
            "bottleneck_identification",
            "caching_strategy",
            "async_optimization",
            "resource_usage_analysis"
        ]
    
    def _define_supported_technologies(self) -> List[str]:
        return [
            "python", "javascript", "typescript", "java", "csharp",
            "golang", "rust", "cpp", "postgresql", "mysql", "redis",
            "react", "nodejs", "django", "flask", "fastapi"
        ]
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute performance optimization task"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.status = AgentStatus.RUNNING
            
            optimization_type = task.parameters.get("type", "analysis")
            
            if optimization_type == "analysis":
                result = await self._perform_performance_analysis(task)
            elif optimization_type == "code_optimization":
                result = await self._optimize_code(task)
            elif optimization_type == "database_optimization":
                result = await self._optimize_database_queries(task)
            elif optimization_type == "memory_optimization":
                result = await self._optimize_memory_usage(task)
            else:
                raise ValueError(f"Unknown optimization type: {optimization_type}")
            
            self.status = AgentStatus.COMPLETED
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.COMPLETED,
                output=result,
                metadata={
                    "optimization_type": optimization_type,
                    "technologies_analyzed": result.get("technologies", []),
                    "improvements_found": len(result.get("optimizations", []))
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return AgentResult(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                output=None,
                metadata={"error_details": str(e)},
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _perform_performance_analysis(self, task: AgentTask) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        project_path = task.context.get("project_path", ".")
        
        # Analyze code structure
        code_analysis = await self._analyze_code_structure(project_path)
        
        # Identify performance bottlenecks
        bottlenecks = await self._identify_bottlenecks(project_path, code_analysis)
        
        # Generate optimization recommendations
        recommendations = await self._generate_recommendations(bottlenecks)
        
        # Calculate performance impact estimates
        impact_estimates = await self._estimate_performance_impact(recommendations)
        
        return {
            "analysis_summary": {
                "files_analyzed": code_analysis["files_count"],
                "technologies": code_analysis["technologies"],
                "complexity_score": code_analysis["complexity_score"]
            },
            "bottlenecks": bottlenecks,
            "optimizations": recommendations,
            "impact_estimates": impact_estimates,
            "priority_recommendations": self._prioritize_recommendations(
                recommendations, impact_estimates
            )
        }
    
    async def _analyze_code_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project code structure for performance issues"""
        
        analysis = {
            "files_count": 0,
            "technologies": set(),
            "complexity_score": 0.0,
            "performance_patterns": []
        }
        
        # Walk through project files
        import os
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cs', '.go', '.rs')):
                    file_path = os.path.join(root, file)
                    file_analysis = await self._analyze_file_performance(file_path)
                    
                    analysis["files_count"] += 1
                    analysis["technologies"].update(file_analysis["technologies"])
                    analysis["complexity_score"] += file_analysis["complexity"]
                    analysis["performance_patterns"].extend(file_analysis["patterns"])
        
        analysis["technologies"] = list(analysis["technologies"])
        analysis["complexity_score"] /= max(analysis["files_count"], 1)
        
        return analysis
    
    async def _analyze_file_performance(self, file_path: str) -> Dict[str, Any]:
        """Analyze individual file for performance patterns"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            "technologies": [],
            "complexity": 0.0,
            "patterns": []
        }
        
        # Detect technology from file extension and imports
        if file_path.endswith('.py'):
            analysis["technologies"].append("python")
            analysis["patterns"].extend(await self._analyze_python_performance(content))
        elif file_path.endswith(('.js', '.ts')):
            analysis["technologies"].append("javascript")
            analysis["patterns"].extend(await self._analyze_javascript_performance(content))
        
        # Calculate complexity (simple cyclomatic complexity)
        analysis["complexity"] = self._calculate_cyclomatic_complexity(content)
        
        return analysis
    
    async def _analyze_python_performance(self, code: str) -> List[Dict[str, Any]]:
        """Analyze Python code for performance issues"""
        patterns = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Detect nested loops
                if isinstance(node, ast.For):
                    nested_loops = [n for n in ast.walk(node) if isinstance(n, ast.For)]
                    if len(nested_loops) > 2:  # More than 2 nested loops
                        patterns.append({
                            "type": "nested_loops",
                            "severity": "high",
                            "line": node.lineno,
                            "description": f"Deeply nested loops detected (depth: {len(nested_loops)})"
                        })
                
                # Detect string concatenation in loops
                if isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                            patterns.append({
                                "type": "string_concatenation_in_loop",
                                "severity": "medium",
                                "line": child.lineno,
                                "description": "String concatenation in loop - consider using join()"
                            })
        
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        # Regex-based patterns
        
        # Global variables
        global_vars = re.findall(r'^global\s+\w+', code, re.MULTILINE)
        if global_vars:
            patterns.append({
                "type": "global_variables",
                "severity": "low", 
                "description": f"Global variables found: {len(global_vars)}"
            })
        
        # Inefficient database queries (basic detection)
        if re.search(r'\.all\(\).*for.*in', code):
            patterns.append({
                "type": "n_plus_one_query",
                "severity": "high",
                "description": "Potential N+1 query pattern detected"
            })
        
        return patterns
```

### Agent Registration and Discovery

```python
# src/claude/agents/registry.py
import importlib
import inspect
from typing import Dict, List, Type, Any
from claude.agents.base import BaseAgent

class AgentRegistry:
    """Registry for managing and discovering agents"""
    
    def __init__(self):
        self.agents: Dict[str, Type[BaseAgent]] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(
        self, 
        agent_class: Type[BaseAgent], 
        agent_id: str = None
    ) -> None:
        """Register an agent class"""
        if agent_id is None:
            agent_id = agent_class.__name__.lower().replace('agent', '').replace('_', '-')
        
        self.agents[agent_id] = agent_class
        
        # Extract metadata from agent class
        self.agent_metadata[agent_id] = {
            "class_name": agent_class.__name__,
            "module": agent_class.__module__,
            "capabilities": getattr(agent_class, 'capabilities', []),
            "supported_technologies": getattr(agent_class, 'supported_technologies', []),
            "description": agent_class.__doc__ or "",
            "version": getattr(agent_class, '__version__', '1.0.0')
        }
    
    def discover_agents(self, package_path: str = "claude.agents") -> None:
        """Automatically discover and register agents in a package"""
        try:
            package = importlib.import_module(package_path)
            
            # Walk through all modules in the package
            for module_name in dir(package):
                if module_name.startswith('_'):
                    continue
                
                try:
                    module = importlib.import_module(f"{package_path}.{module_name}")
                    
                    # Find agent classes in module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseAgent) and 
                            obj != BaseAgent):
                            
                            self.register_agent(obj)
                            
                except ImportError as e:
                    print(f"Failed to import {package_path}.{module_name}: {e}")
                    
        except ImportError as e:
            print(f"Failed to import package {package_path}: {e}")
    
    def get_agent(self, agent_id: str) -> Type[BaseAgent]:
        """Get agent class by ID"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        return self.agents[agent_id]
    
    def list_agents(self) -> List[str]:
        """List all registered agent IDs"""
        return list(self.agents.keys())
    
    def get_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability"""
        matching_agents = []
        
        for agent_id, metadata in self.agent_metadata.items():
            if capability in metadata.get("capabilities", []):
                matching_agents.append(agent_id)
        
        return matching_agents
    
    def get_agents_by_technology(self, technology: str) -> List[str]:
        """Find agents that support a specific technology"""
        matching_agents = []
        
        for agent_id, metadata in self.agent_metadata.items():
            if technology in metadata.get("supported_technologies", []):
                matching_agents.append(agent_id)
        
        return matching_agents

# Global registry instance
agent_registry = AgentRegistry()
```

## 🔄 Custom Workflows

### Workflow Definition Language

```yaml
# workflows/custom_deployment.yaml
name: "Custom Deployment Pipeline"
version: "1.0.0"
description: "Full deployment pipeline with security and performance checks"

variables:
  environment: "production"
  database_backup: true
  rollback_enabled: true

triggers:
  - keywords: ["deploy", "deployment", "production"]
  - file_patterns: ["deployment/*.yml", "k8s/*.yaml"]
  - git_patterns: ["release/*", "hotfix/*"]

steps:
  - id: "security_audit"
    agent: "security-audit-specialist"
    task: "Comprehensive security audit before deployment"
    parameters:
      scope: "full_application"
      include_dependencies: true
      compliance_check: true
    timeout: 900
    required: true
    
  - id: "performance_check"
    agent: "systems-engineer" 
    task: "Performance benchmarking and optimization check"
    parameters:
      benchmark_type: "load_test"
      target_rps: 1000
      memory_limit: "2Gi"
    depends_on: []
    parallel_with: ["security_audit"]
    timeout: 600
    
  - id: "database_backup"
    agent: "data-engineer"
    task: "Create database backup before deployment"
    parameters:
      backup_type: "full"
      encryption: true
      verify_backup: true
    condition: "{{ variables.database_backup }}"
    depends_on: ["security_audit"]
    timeout: 1800
    required: true
    
  - id: "deployment"
    agent: "devops-engineer"
    task: "Execute deployment to production environment"
    parameters:
      environment: "{{ variables.environment }}"
      strategy: "rolling_update"
      health_checks: true
    depends_on: ["security_audit", "performance_check", "database_backup"]
    timeout: 1200
    required: true
    
  - id: "post_deploy_validation"
    agent: "qa-test-engineer"
    task: "Post-deployment validation and smoke tests"
    parameters:
      test_suite: "smoke_tests"
      endpoints_check: true
      performance_validation: true
    depends_on: ["deployment"]
    timeout: 600
    required: true
    
  - id: "monitoring_setup"
    agent: "devops-engineer"
    task: "Configure monitoring and alerting for new deployment"
    parameters:
      metrics_enabled: true
      alert_channels: ["slack", "email"]
      dashboard_update: true
    depends_on: ["deployment"]
    parallel_with: ["post_deploy_validation"]
    timeout: 300

failure_handling:
  rollback:
    enabled: "{{ variables.rollback_enabled }}"
    trigger_on: ["deployment", "post_deploy_validation"]
    strategy: "automatic"
    timeout: 600
    
  notifications:
    - channel: "slack"
      webhook: "{{ secrets.slack_webhook }}"
      on: ["failure", "success"]
    
    - channel: "email" 
      recipients: ["devops@company.com"]
      on: ["failure"]

success_criteria:
  required_steps: ["security_audit", "deployment", "post_deploy_validation"]
  performance_threshold: 0.95
  error_threshold: 0.01
```

### Workflow Execution Engine

```python
# src/claude/workflows/engine.py
import asyncio
import yaml
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from claude.agents.registry import agent_registry

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    id: str
    agent: str
    task: str
    parameters: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    parallel_with: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout: int = 300
    required: bool = True
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class WorkflowDefinition:
    name: str
    version: str
    description: str
    variables: Dict[str, Any]
    triggers: List[Dict[str, Any]]
    steps: List[WorkflowStep]
    failure_handling: Dict[str, Any]
    success_criteria: Dict[str, Any]

class WorkflowExecutor:
    """Execute custom workflows with dependency management"""
    
    def __init__(self):
        self.running_workflows: Dict[str, Dict[str, Any]] = {}
    
    async def execute_workflow(
        self, 
        workflow_def: WorkflowDefinition,
        context: Dict[str, Any],
        workflow_id: str = None
    ) -> Dict[str, Any]:
        """Execute a workflow definition"""
        
        if workflow_id is None:
            workflow_id = f"workflow_{len(self.running_workflows)}"
        
        # Initialize workflow execution context
        self.running_workflows[workflow_id] = {
            "definition": workflow_def,
            "context": context,
            "start_time": asyncio.get_event_loop().time(),
            "status": "running",
            "completed_steps": [],
            "failed_steps": []
        }
        
        try:
            # Resolve workflow variables
            resolved_variables = await self._resolve_variables(
                workflow_def.variables, 
                context
            )
            
            # Execute workflow steps
            execution_result = await self._execute_steps(
                workflow_def.steps,
                resolved_variables,
                context,
                workflow_id
            )
            
            # Check success criteria
            success = await self._check_success_criteria(
                execution_result,
                workflow_def.success_criteria
            )
            
            # Update workflow status
            self.running_workflows[workflow_id]["status"] = "completed" if success else "failed"
            self.running_workflows[workflow_id]["end_time"] = asyncio.get_event_loop().time()
            
            return {
                "workflow_id": workflow_id,
                "status": "completed" if success else "failed",
                "steps_completed": len([s for s in execution_result if s.status == StepStatus.COMPLETED]),
                "steps_failed": len([s for s in execution_result if s.status == StepStatus.FAILED]),
                "execution_time": self.running_workflows[workflow_id]["end_time"] - self.running_workflows[workflow_id]["start_time"],
                "results": {step.id: step.result for step in execution_result if step.result},
                "success": success
            }
            
        except Exception as e:
            # Handle workflow failure
            await self._handle_workflow_failure(workflow_id, str(e))
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "execution_time": asyncio.get_event_loop().time() - self.running_workflows[workflow_id]["start_time"]
            }
    
    async def _execute_steps(
        self,
        steps: List[WorkflowStep],
        variables: Dict[str, Any],
        context: Dict[str, Any],
        workflow_id: str
    ) -> List[WorkflowStep]:
        """Execute workflow steps with dependency management"""
        
        # Create execution graph
        step_dict = {step.id: step for step in steps}
        completed_steps = set()
        
        while len(completed_steps) < len(steps):
            # Find steps ready to execute
            ready_steps = []
            for step in steps:
                if (step.status == StepStatus.PENDING and
                    all(dep in completed_steps for dep in step.depends_on)):
                    
                    # Check condition if specified
                    if step.condition:
                        condition_result = await self._evaluate_condition(
                            step.condition, 
                            variables, 
                            context
                        )
                        if not condition_result:
                            step.status = StepStatus.SKIPPED
                            completed_steps.add(step.id)
                            continue
                    
                    ready_steps.append(step)
            
            if not ready_steps:
                # Check for circular dependencies or failed required steps
                pending_steps = [s for s in steps if s.status == StepStatus.PENDING]
                if pending_steps:
                    failed_deps = []
                    for step in pending_steps:
                        for dep in step.depends_on:
                            if step_dict[dep].status == StepStatus.FAILED:
                                failed_deps.append(dep)
                    
                    if failed_deps:
                        raise Exception(f"Workflow cannot continue due to failed dependencies: {failed_deps}")
                    else:
                        raise Exception("Circular dependency detected in workflow")
                break
            
            # Group steps that can run in parallel
            parallel_groups = self._group_parallel_steps(ready_steps)
            
            # Execute parallel groups sequentially
            for group in parallel_groups:
                # Execute steps in group in parallel
                tasks = []
                for step in group:
                    task = asyncio.create_task(
                        self._execute_single_step(step, variables, context, workflow_id)
                    )
                    tasks.append(task)
                
                # Wait for all steps in group to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update step statuses
                for step, result in zip(group, results):
                    if isinstance(result, Exception):
                        step.status = StepStatus.FAILED
                        step.error = str(result)
                        
                        if step.required:
                            # Handle failure according to workflow policy
                            await self._handle_step_failure(step, workflow_id)
                    else:
                        step.status = StepStatus.COMPLETED
                        step.result = result
                    
                    completed_steps.add(step.id)
        
        return steps
    
    async def _execute_single_step(
        self,
        step: WorkflowStep,
        variables: Dict[str, Any],
        context: Dict[str, Any],
        workflow_id: str
    ) -> Any:
        """Execute a single workflow step"""
        
        step.status = StepStatus.RUNNING
        
        # Get agent for this step
        agent_class = agent_registry.get_agent(step.agent)
        agent_instance = agent_class(step.agent, {})
        
        # Resolve step parameters with variables
        resolved_params = await self._resolve_parameters(
            step.parameters, 
            variables, 
            context
        )
        
        # Create agent task
        from claude.agents.base import AgentTask
        task = AgentTask(
            task_id=f"{workflow_id}_{step.id}",
            description=step.task,
            parameters=resolved_params,
            context=context,
            timeout=step.timeout
        )
        
        # Execute agent task
        try:
            result = await asyncio.wait_for(
                agent_instance.execute_task(task),
                timeout=step.timeout
            )
            
            return result.output if result.status == StepStatus.COMPLETED else None
            
        except asyncio.TimeoutError:
            raise Exception(f"Step {step.id} timed out after {step.timeout} seconds")
    
    async def _resolve_parameters(
        self,
        parameters: Dict[str, Any],
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve parameter templates with variables"""
        
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{ ") and value.endswith(" }}"):
                # Template variable
                var_name = value[3:-3].strip()
                if var_name.startswith("variables."):
                    var_key = var_name[10:]
                    resolved[key] = variables.get(var_key, value)
                elif var_name.startswith("context."):
                    var_key = var_name[8:]
                    resolved[key] = context.get(var_key, value)
                else:
                    resolved[key] = variables.get(var_name, value)
            else:
                resolved[key] = value
        
        return resolved
```

## 🔌 Integration APIs

### REST API Integration

```python
# src/claude/api/v2/endpoints.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio

app = FastAPI(title="Claude Code 2.0 API", version="2.0.0")
security = HTTPBearer()

class AgentSelectionRequest(BaseModel):
    request_text: str = Field(..., description="Natural language description of the task")
    project_context: Optional[Dict[str, Any]] = Field(None, description="Project context information")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences and settings")
    max_agents: int = Field(3, description="Maximum number of agents to recommend")

class AgentRecommendation(BaseModel):
    agent_id: str
    confidence_score: float
    reasoning: str
    estimated_success_rate: float
    metadata: Dict[str, Any]

class WorkflowExecutionRequest(BaseModel):
    workflow_name: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    
class CustomAgentRequest(BaseModel):
    agent_definition: Dict[str, Any]
    config: Dict[str, Any]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user information from JWT token"""
    # Implementation depends on your authentication system
    return {"user_id": "user123", "permissions": ["agent:use", "workflow:create"]}

@app.post("/api/v2/agents/select", response_model=List[AgentRecommendation])
async def select_agents(
    request: AgentSelectionRequest,
    user = Depends(get_current_user)
):
    """Select optimal agents for a given request using AI"""
    try:
        from claude.ai.selectors.ml_enhanced import MLEnhancedAgentSelector
        from claude.ai.core import UserRequest, ProjectContext, UserProfile
        
        # Create selector
        selector = MLEnhancedAgentSelector({})
        await selector.initialize()
        
        # Prepare request objects
        user_request = UserRequest(
            text=request.request_text,
            additional_context=request.project_context or {}
        )
        
        project_context = ProjectContext()
        if request.project_context:
            project_context.tech_stack = request.project_context.get("tech_stack", [])
            project_context.complexity_score = request.project_context.get("complexity", 0.0)
        
        user_profile = UserProfile(
            user_id=user["user_id"],
            preferences=request.user_preferences or {}
        )
        
        # Get recommendations
        recommendations = await selector.select_agents(
            user_request,
            project_context,
            user_profile,
            request.max_agents
        )
        
        # Convert to response format
        return [
            AgentRecommendation(
                agent_id=rec.agent_id,
                confidence_score=rec.confidence_score,
                reasoning=rec.reasoning,
                estimated_success_rate=rec.estimated_success_rate,
                metadata=rec.metadata
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/workflows/execute")
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Execute a predefined workflow"""
    try:
        from claude.workflows.engine import WorkflowExecutor
        from claude.workflows.loader import load_workflow
        
        # Load workflow definition
        workflow_def = load_workflow(request.workflow_name)
        
        # Create executor
        executor = WorkflowExecutor()
        
        # Start workflow execution in background
        workflow_id = f"workflow_{user['user_id']}_{len(executor.running_workflows)}"
        
        background_tasks.add_task(
            executor.execute_workflow,
            workflow_def,
            request.context,
            workflow_id
        )
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": f"Workflow {request.workflow_name} started successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str, user = Depends(get_current_user)):
    """Get the status of a running workflow"""
    try:
        from claude.workflows.engine import WorkflowExecutor
        
        executor = WorkflowExecutor()
        
        if workflow_id not in executor.running_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = executor.running_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "status": workflow_data["status"],
            "start_time": workflow_data["start_time"],
            "completed_steps": len(workflow_data["completed_steps"]),
            "failed_steps": len(workflow_data["failed_steps"]),
            "current_step": workflow_data.get("current_step")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/agents/custom")
async def register_custom_agent(
    request: CustomAgentRequest,
    user = Depends(get_current_user)
):
    """Register a custom agent (enterprise feature)"""
    
    # Check permissions
    if "agent:manage" not in user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from claude.agents.factory import AgentFactory
        
        # Create custom agent from definition
        agent_factory = AgentFactory()
        agent_class = agent_factory.create_from_definition(
            request.agent_definition,
            request.config
        )
        
        # Register in registry
        from claude.agents.registry import agent_registry
        agent_registry.register_agent(agent_class)
        
        return {
            "agent_id": agent_class.agent_id,
            "status": "registered",
            "message": "Custom agent registered successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/agents")
async def list_agents(
    capability: Optional[str] = None,
    technology: Optional[str] = None,
    user = Depends(get_current_user)
):
    """List available agents with optional filtering"""
    try:
        from claude.agents.registry import agent_registry
        
        if capability:
            agents = agent_registry.get_agents_by_capability(capability)
        elif technology:
            agents = agent_registry.get_agents_by_technology(technology)
        else:
            agents = agent_registry.list_agents()
        
        # Get metadata for each agent
        agent_info = []
        for agent_id in agents:
            metadata = agent_registry.agent_metadata.get(agent_id, {})
            agent_info.append({
                "id": agent_id,
                "name": metadata.get("class_name", agent_id),
                "description": metadata.get("description", ""),
                "capabilities": metadata.get("capabilities", []),
                "technologies": metadata.get("supported_technologies", []),
                "version": metadata.get("version", "1.0.0")
            })
        
        return {
            "agents": agent_info,
            "total": len(agent_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### WebSocket API for Real-time Updates

```python
# src/claude/api/v2/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = []
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
    
    async def send_message(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
    
    async def broadcast_to_subscribers(self, topic: str, message: dict):
        """Broadcast message to all users subscribed to a topic"""
        for user_id, subscriptions in self.user_subscriptions.items():
            if topic in subscriptions:
                await self.send_message(user_id, {
                    "type": "broadcast",
                    "topic": topic,
                    "data": message
                })

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_websocket_message(user_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)

async def handle_websocket_message(user_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # Subscribe to workflow updates, agent recommendations, etc.
        topic = message.get("topic")
        if topic and user_id in manager.user_subscriptions:
            manager.user_subscriptions[user_id].append(topic)
            
        await manager.send_message(user_id, {
            "type": "subscription_confirmed",
            "topic": topic
        })
    
    elif message_type == "agent_selection_request":
        # Stream agent recommendations as they're computed
        await stream_agent_recommendations(user_id, message.get("data", {}))
    
    elif message_type == "workflow_status_request":
        # Stream workflow execution status
        workflow_id = message.get("workflow_id")
        if workflow_id:
            await stream_workflow_status(user_id, workflow_id)

async def stream_agent_recommendations(user_id: str, request_data: dict):
    """Stream agent recommendations as they're computed"""
    
    try:
        from claude.ai.selectors.ml_enhanced import MLEnhancedAgentSelector
        
        selector = MLEnhancedAgentSelector({})
        await selector.initialize()
        
        # Send initial acknowledgment
        await manager.send_message(user_id, {
            "type": "agent_selection_started",
            "request_id": request_data.get("request_id")
        })
        
        # Simulate streaming recommendations (in real implementation, 
        # this would yield recommendations as they're computed)
        for i in range(3):
            await asyncio.sleep(0.5)  # Simulate computation time
            
            recommendation = {
                "agent_id": f"agent_{i}",
                "confidence_score": 0.8 - i * 0.1,
                "reasoning": f"Recommendation {i+1} based on semantic analysis",
                "estimated_success_rate": 0.9 - i * 0.05
            }
            
            await manager.send_message(user_id, {
                "type": "agent_recommendation",
                "request_id": request_data.get("request_id"),
                "recommendation": recommendation,
                "position": i + 1
            })
        
        await manager.send_message(user_id, {
            "type": "agent_selection_completed",
            "request_id": request_data.get("request_id")
        })
        
    except Exception as e:
        await manager.send_message(user_id, {
            "type": "agent_selection_error",
            "request_id": request_data.get("request_id"),
            "error": str(e)
        })

async def stream_workflow_status(user_id: str, workflow_id: str):
    """Stream workflow execution status updates"""
    
    from claude.workflows.engine import WorkflowExecutor
    executor = WorkflowExecutor()
    
    if workflow_id not in executor.running_workflows:
        await manager.send_message(user_id, {
            "type": "workflow_error",
            "workflow_id": workflow_id,
            "error": "Workflow not found"
        })
        return
    
    # Stream status updates every 2 seconds until workflow completes
    while True:
        workflow_data = executor.running_workflows.get(workflow_id)
        if not workflow_data:
            break
        
        status = {
            "workflow_id": workflow_id,
            "status": workflow_data["status"],
            "completed_steps": len(workflow_data["completed_steps"]),
            "failed_steps": len(workflow_data["failed_steps"]),
            "current_step": workflow_data.get("current_step")
        }
        
        await manager.send_message(user_id, {
            "type": "workflow_status",
            "data": status
        })
        
        # Stop streaming if workflow is complete
        if workflow_data["status"] in ["completed", "failed", "cancelled"]:
            break
        
        await asyncio.sleep(2)
```

## 📚 SDK Development

### Python SDK

```python
# claude_code_sdk/client.py
import asyncio
import httpx
import websockets
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

@dataclass
class AgentRecommendation:
    agent_id: str
    confidence_score: float
    reasoning: str
    estimated_success_rate: float
    metadata: Dict[str, Any]

class ClaudeCodeClient:
    """Python SDK for Claude Code 2.0 API"""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        
        if api_key:
            self.client.headers.update({"Authorization": f"Bearer {api_key}"})
    
    async def select_agents(
        self,
        request_text: str,
        project_context: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        max_agents: int = 3
    ) -> List[AgentRecommendation]:
        """Select optimal agents for a given request"""
        
        payload = {
            "request_text": request_text,
            "max_agents": max_agents
        }
        
        if project_context:
            payload["project_context"] = project_context
        if user_preferences:
            payload["user_preferences"] = user_preferences
        
        response = await self.client.post(
            f"{self.base_url}/api/v2/agents/select",
            json=payload
        )
        response.raise_for_status()
        
        recommendations_data = response.json()
        return [
            AgentRecommendation(
                agent_id=rec["agent_id"],
                confidence_score=rec["confidence_score"],
                reasoning=rec["reasoning"],
                estimated_success_rate=rec["estimated_success_rate"],
                metadata=rec["metadata"]
            )
            for rec in recommendations_data
        ]
    
    async def execute_workflow(
        self,
        workflow_name: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Execute a predefined workflow and return workflow ID"""
        
        payload = {
            "workflow_name": workflow_name,
            "parameters": parameters,
            "context": context
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v2/workflows/execute",
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        return result["workflow_id"]
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow"""
        
        response = await self.client.get(
            f"{self.base_url}/api/v2/workflows/{workflow_id}/status"
        )
        response.raise_for_status()
        
        return response.json()
    
    async def list_agents(
        self,
        capability: Optional[str] = None,
        technology: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available agents with optional filtering"""
        
        params = {}
        if capability:
            params["capability"] = capability
        if technology:
            params["technology"] = technology
        
        response = await self.client.get(
            f"{self.base_url}/api/v2/agents",
            params=params
        )
        response.raise_for_status()
        
        result = response.json()
        return result["agents"]
    
    async def stream_agent_recommendations(
        self,
        request_text: str,
        project_context: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> AsyncGenerator[AgentRecommendation, None]:
        """Stream agent recommendations in real-time"""
        
        ws_url = f"ws://{self.base_url.split('//')[1]}/ws/{user_id}"
        
        async with websockets.connect(ws_url) as websocket:
            # Send agent selection request
            request = {
                "type": "agent_selection_request",
                "data": {
                    "request_text": request_text,
                    "project_context": project_context,
                    "request_id": "stream_request"
                }
            }
            
            await websocket.send(json.dumps(request))
            
            # Listen for recommendations
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "agent_recommendation":
                    rec_data = data["recommendation"]
                    yield AgentRecommendation(
                        agent_id=rec_data["agent_id"],
                        confidence_score=rec_data["confidence_score"],
                        reasoning=rec_data["reasoning"],
                        estimated_success_rate=rec_data["estimated_success_rate"],
                        metadata=rec_data.get("metadata", {})
                    )
                elif data["type"] == "agent_selection_completed":
                    break
                elif data["type"] == "agent_selection_error":
                    raise Exception(f"Agent selection failed: {data['error']}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Example usage
async def main():
    client = ClaudeCodeClient(api_key="your-api-key")
    
    try:
        # Select agents
        recommendations = await client.select_agents(
            "I need to add user authentication to my React app",
            project_context={"tech_stack": ["react", "nodejs", "postgresql"]},
            max_agents=3
        )
        
        print("Recommended agents:")
        for rec in recommendations:
            print(f"  {rec.agent_id}: {rec.confidence_score:.2f} confidence")
            print(f"    Reasoning: {rec.reasoning}")
        
        # Execute workflow
        workflow_id = await client.execute_workflow(
            "authentication_setup",
            {"framework": "react", "backend": "nodejs"},
            {"project_path": "/path/to/project"}
        )
        
        print(f"Started workflow: {workflow_id}")
        
        # Monitor workflow status
        while True:
            status = await client.get_workflow_status(workflow_id)
            print(f"Workflow status: {status['status']}")
            
            if status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(2)
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript/TypeScript SDK

```typescript
// claude-code-sdk/src/client.ts
export interface AgentRecommendation {
  agentId: string;
  confidenceScore: number;
  reasoning: string;
  estimatedSuccessRate: number;
  metadata: Record<string, any>;
}

export interface WorkflowStatus {
  workflowId: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: number;
  completedSteps: number;
  failedSteps: number;
  currentStep?: string;
}

export class ClaudeCodeClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;

  constructor(options: {
    baseUrl?: string;
    apiKey?: string;
    timeout?: number;
  } = {}) {
    this.baseUrl = (options.baseUrl || 'http://localhost:8080').replace(/\/$/, '');
    this.apiKey = options.apiKey;
    this.timeout = options.timeout || 30000;
  }

  async selectAgents(params: {
    requestText: string;
    projectContext?: Record<string, any>;
    userPreferences?: Record<string, any>;
    maxAgents?: number;
  }): Promise<AgentRecommendation[]> {
    const response = await this.request('POST', '/api/v2/agents/select', {
      request_text: params.requestText,
      project_context: params.projectContext,
      user_preferences: params.userPreferences,
      max_agents: params.maxAgents || 3,
    });

    return response.map((rec: any) => ({
      agentId: rec.agent_id,
      confidenceScore: rec.confidence_score,
      reasoning: rec.reasoning,
      estimatedSuccessRate: rec.estimated_success_rate,
      metadata: rec.metadata,
    }));
  }

  async executeWorkflow(params: {
    workflowName: string;
    parameters: Record<string, any>;
    context: Record<string, any>;
  }): Promise<string> {
    const response = await this.request('POST', '/api/v2/workflows/execute', {
      workflow_name: params.workflowName,
      parameters: params.parameters,
      context: params.context,
    });

    return response.workflow_id;
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    const response = await this.request('GET', `/api/v2/workflows/${workflowId}/status`);

    return {
      workflowId: response.workflow_id,
      status: response.status,
      startTime: response.start_time,
      completedSteps: response.completed_steps,
      failedSteps: response.failed_steps,
      currentStep: response.current_step,
    };
  }

  async listAgents(filters: {
    capability?: string;
    technology?: string;
  } = {}): Promise<Array<{
    id: string;
    name: string;
    description: string;
    capabilities: string[];
    technologies: string[];
    version: string;
  }>> {
    const params = new URLSearchParams();
    if (filters.capability) params.append('capability', filters.capability);
    if (filters.technology) params.append('technology', filters.technology);

    const response = await this.request('GET', `/api/v2/agents?${params}`);
    return response.agents;
  }

  streamAgentRecommendations(params: {
    requestText: string;
    projectContext?: Record<string, any>;
    userId?: string;
  }): AsyncIterable<AgentRecommendation> {
    return this.createWebSocketStream(params.userId || 'default', {
      type: 'agent_selection_request',
      data: {
        request_text: params.requestText,
        project_context: params.projectContext,
        request_id: 'stream_request',
      },
    });
  }

  private async request(method: string, path: string, body?: any): Promise<any> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  private async* createWebSocketStream(
    userId: string,
    initialMessage: any
  ): AsyncIterable<AgentRecommendation> {
    const wsUrl = `ws://${this.baseUrl.split('//')[1]}/ws/${userId}`;
    const ws = new WebSocket(wsUrl);

    try {
      // Wait for connection
      await new Promise((resolve, reject) => {
        ws.onopen = resolve;
        ws.onerror = reject;
      });

      // Send initial message
      ws.send(JSON.stringify(initialMessage));

      // Yield recommendations as they arrive
      while (true) {
        const message = await new Promise<any>((resolve, reject) => {
          ws.onmessage = (event) => resolve(JSON.parse(event.data));
          ws.onerror = reject;
        });

        if (message.type === 'agent_recommendation') {
          const rec = message.recommendation;
          yield {
            agentId: rec.agent_id,
            confidenceScore: rec.confidence_score,
            reasoning: rec.reasoning,
            estimatedSuccessRate: rec.estimated_success_rate,
            metadata: rec.metadata || {},
          };
        } else if (message.type === 'agent_selection_completed') {
          break;
        } else if (message.type === 'agent_selection_error') {
          throw new Error(`Agent selection failed: ${message.error}`);
        }
      }
    } finally {
      ws.close();
    }
  }
}

// Example usage
export async function example() {
  const client = new ClaudeCodeClient({
    baseUrl: 'https://api.claude-ai.com',
    apiKey: 'your-api-key',
  });

  // Select agents
  const recommendations = await client.selectAgents({
    requestText: 'I need to add user authentication to my React app',
    projectContext: { tech_stack: ['react', 'nodejs', 'postgresql'] },
    maxAgents: 3,
  });

  console.log('Recommended agents:');
  recommendations.forEach((rec) => {
    console.log(`  ${rec.agentId}: ${rec.confidenceScore.toFixed(2)} confidence`);
    console.log(`    Reasoning: ${rec.reasoning}`);
  });

  // Stream recommendations
  console.log('\nStreaming recommendations:');
  for await (const recommendation of client.streamAgentRecommendations({
    requestText: 'Optimize my database queries for better performance',
    projectContext: { database_type: 'postgresql' },
  })) {
    console.log(`Stream: ${recommendation.agentId} (${recommendation.confidenceScore.toFixed(2)})`);
  }
}
```

## 🧪 Testing Framework

### Agent Testing

```python
# tests/agents/test_agent_base.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from claude.agents.base import BaseAgent, AgentTask, AgentResult, AgentStatus

class TestAgent(BaseAgent):
    """Test agent implementation"""
    
    def _define_capabilities(self):
        return ["test_capability"]
    
    def _define_supported_technologies(self):
        return ["python", "javascript"]
    
    async def execute_task(self, task: AgentTask) -> AgentResult:
        await asyncio.sleep(0.1)  # Simulate work
        
        return AgentResult(
            task_id=task.task_id,
            status=AgentStatus.COMPLETED,
            output=f"Completed task: {task.description}",
            metadata={"test": True},
            execution_time=0.1
        )

@pytest.fixture
def test_agent():
    return TestAgent("test-agent", {"timeout": 300})

@pytest.fixture
def sample_task():
    return AgentTask(
        task_id="test-task-1",
        description="Test task description",
        parameters={"param1": "value1"},
        context={"project_path": "/test/path"}
    )

@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """Test agent initialization"""
    assert test_agent.agent_id == "test-agent"
    assert test_agent.status == AgentStatus.IDLE
    assert "test_capability" in test_agent.capabilities
    assert "python" in test_agent.supported_technologies

@pytest.mark.asyncio
async def test_agent_execute_task(test_agent, sample_task):
    """Test agent task execution"""
    result = await test_agent.execute_task(sample_task)
    
    assert result.task_id == sample_task.task_id
    assert result.status == AgentStatus.COMPLETED
    assert "Completed task" in result.output
    assert result.metadata["test"] is True
    assert result.execution_time > 0

@pytest.mark.asyncio
async def test_agent_validate_task(test_agent, sample_task):
    """Test agent task validation"""
    is_valid = await test_agent.validate_task(sample_task)
    assert is_valid is True

@pytest.mark.asyncio
async def test_agent_health_check(test_agent):
    """Test agent health check"""
    is_healthy = await test_agent.health_check()
    assert is_healthy is True

@pytest.mark.asyncio
async def test_agent_estimate_duration(test_agent, sample_task):
    """Test agent duration estimation"""
    duration = await test_agent.estimate_duration(sample_task)
    assert duration == 300  # Default timeout from config
```

### Integration Testing

```python
# tests/integration/test_agent_selection.py
import pytest
import asyncio
from claude.ai.core import UserRequest, ProjectContext, UserProfile
from claude.ai.selectors.ml_enhanced import MLEnhancedAgentSelector
from claude.agents.registry import agent_registry

@pytest.fixture
async def ml_selector():
    """Create and initialize ML-enhanced agent selector"""
    selector = MLEnhancedAgentSelector({
        "model_name": "sentence-transformers/all-MiniLM-L6-v2"
    })
    await selector.initialize()
    return selector

@pytest.fixture
def sample_request():
    return UserRequest(
        text="I need to add user authentication to my React application",
        project_path="/test/react-app"
    )

@pytest.fixture
def sample_context():
    context = ProjectContext()
    context.tech_stack = ["react", "nodejs", "postgresql"]
    context.complexity_score = 0.6
    context.risk_level = "medium"
    return context

@pytest.fixture
def sample_user_profile():
    return UserProfile(
        user_id="test-user",
        preferences={"preferred_agents": ["full-stack-architect"]},
        agent_affinities={"full-stack-architect": 0.8}
    )

@pytest.mark.asyncio
async def test_agent_selection_integration(
    ml_selector, 
    sample_request, 
    sample_context, 
    sample_user_profile
):
    """Test end-to-end agent selection"""
    
    # Ensure some agents are registered
    agent_registry.discover_agents("claude.agents")
    
    recommendations = await ml_selector.select_agents(
        sample_request,
        sample_context,
        sample_user_profile,
        max_agents=3
    )
    
    assert len(recommendations) <= 3
    assert all(rec.confidence_score >= 0 for rec in recommendations)
    assert all(rec.agent_id in agent_registry.list_agents() for rec in recommendations)
    
    # Check that recommendations are sorted by confidence
    for i in range(1, len(recommendations)):
        assert recommendations[i-1].confidence_score >= recommendations[i].confidence_score

@pytest.mark.asyncio
async def test_context_aware_selection(
    ml_selector,
    sample_user_profile
):
    """Test that context affects agent selection"""
    
    # Web development request
    web_request = UserRequest(text="Build a React dashboard with charts")
    web_context = ProjectContext()
    web_context.tech_stack = ["react", "typescript"]
    
    web_recommendations = await ml_selector.select_agents(
        web_request, web_context, sample_user_profile
    )
    
    # Mobile development request
    mobile_request = UserRequest(text="Create an iOS app with user authentication")
    mobile_context = ProjectContext()
    mobile_context.tech_stack = ["swift", "ios"]
    
    mobile_recommendations = await ml_selector.select_agents(
        mobile_request, mobile_context, sample_user_profile
    )
    
    # Verify different agents are recommended for different contexts
    web_agents = {rec.agent_id for rec in web_recommendations}
    mobile_agents = {rec.agent_id for rec in mobile_recommendations}
    
    # Should have some different recommendations
    assert web_agents != mobile_agents
```

### Performance Testing

```python
# tests/performance/test_agent_selection_performance.py
import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from claude.ai.selectors.ml_enhanced import MLEnhancedAgentSelector
from claude.ai.core import UserRequest, ProjectContext, UserProfile

@pytest.fixture
async def performance_selector():
    """Create selector optimized for performance testing"""
    selector = MLEnhancedAgentSelector({
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "cache_embeddings": True
    })
    await selector.initialize()
    return selector

@pytest.mark.performance
@pytest.mark.asyncio
async def test_agent_selection_latency(performance_selector):
    """Test agent selection latency under normal conditions"""
    
    request = UserRequest(text="Help me build a web application with authentication")
    context = ProjectContext()
    context.tech_stack = ["react", "nodejs"]
    user_profile = UserProfile(user_id="perf-test")
    
    # Warm up
    await performance_selector.select_agents(request, context, user_profile)
    
    # Measure latency over multiple runs
    latencies = []
    for _ in range(50):
        start_time = time.time()
        recommendations = await performance_selector.select_agents(
            request, context, user_profile
        )
        end_time = time.time()
        
        latencies.append(end_time - start_time)
        assert len(recommendations) > 0
    
    # Performance assertions
    avg_latency = statistics.mean(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    
    print(f"Average latency: {avg_latency:.3f}s")
    print(f"95th percentile latency: {p95_latency:.3f}s")
    
    assert avg_latency < 0.5  # Average should be under 500ms
    assert p95_latency < 1.0  # 95th percentile should be under 1s

@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_agent_selection(performance_selector):
    """Test agent selection under concurrent load"""
    
    async def single_selection():
        request = UserRequest(text="Optimize database performance")
        context = ProjectContext()
        user_profile = UserProfile(user_id="concurrent-test")
        
        start_time = time.time()
        recommendations = await performance_selector.select_agents(
            request, context, user_profile
        )
        end_time = time.time()
        
        return end_time - start_time, len(recommendations)
    
    # Run concurrent selections
    concurrent_requests = 20
    start_time = time.time()
    
    results = await asyncio.gather(*[
        single_selection() for _ in range(concurrent_requests)
    ])
    
    total_time = time.time() - start_time
    
    # Analyze results
    latencies = [result[0] for result in results]
    recommendation_counts = [result[1] for result in results]
    
    avg_latency = statistics.mean(latencies)
    throughput = concurrent_requests / total_time
    
    print(f"Concurrent requests: {concurrent_requests}")
    print(f"Total time: {total_time:.3f}s")
    print(f"Throughput: {throughput:.2f} requests/second")
    print(f"Average latency under load: {avg_latency:.3f}s")
    
    # Performance assertions
    assert all(count > 0 for count in recommendation_counts)
    assert throughput > 10  # Should handle at least 10 requests/second
    assert avg_latency < 2.0  # Latency shouldn't degrade too much under load

@pytest.mark.benchmark
def test_embedding_generation_performance(benchmark):
    """Benchmark embedding generation performance"""
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    test_texts = [
        "Build a React application with user authentication",
        "Optimize database queries for better performance", 
        "Create a mobile app for iOS and Android",
        "Set up CI/CD pipeline with automated testing",
        "Implement real-time chat functionality"
    ]
    
    def generate_embeddings():
        return model.encode(test_texts)
    
    result = benchmark(generate_embeddings)
    
    # Verify embeddings were generated
    assert result.shape[0] == len(test_texts)
    assert result.shape[1] > 0  # Should have embedding dimensions
```

## 📈 Monitoring & Analytics

### Custom Metrics Collection

```python
# src/claude/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Dict, Any, Optional
import time
import asyncio

class AgentMetricsCollector:
    """Collect and expose metrics for agent performance monitoring"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        
        # Agent selection metrics
        self.agent_selection_requests = Counter(
            'claude_agent_selection_requests_total',
            'Total number of agent selection requests',
            ['user_id', 'success'],
            registry=self.registry
        )
        
        self.agent_selection_duration = Histogram(
            'claude_agent_selection_duration_seconds',
            'Time spent selecting agents',
            ['model_type'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.agent_recommendation_confidence = Histogram(
            'claude_agent_recommendation_confidence',
            'Confidence scores of agent recommendations',
            ['agent_id'],
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        # User satisfaction metrics
        self.user_satisfaction_score = Gauge(
            'claude_user_satisfaction_score',
            'User satisfaction ratings',
            ['agent_id', 'task_type'],
            registry=self.registry
        )
        
        # Model performance metrics
        self.model_accuracy = Gauge(
            'claude_model_accuracy',
            'ML model prediction accuracy',
            ['model_name', 'version'],
            registry=self.registry
        )
        
        # System health metrics
        self.active_sessions = Gauge(
            'claude_active_sessions_total',
            'Number of currently active user sessions',
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'claude_cache_hit_rate',
            'Cache hit rate for various caches',
            ['cache_type'],
            registry=self.registry
        )
    
    def record_agent_selection(
        self,
        user_id: str,
        duration: float,
        success: bool,
        model_type: str = "ml_enhanced"
    ):
        """Record agent selection metrics"""
        self.agent_selection_requests.labels(
            user_id=user_id,
            success=str(success)
        ).inc()
        
        self.agent_selection_duration.labels(
            model_type=model_type
        ).observe(duration)
    
    def record_agent_recommendation(
        self,
        agent_id: str,
        confidence: float
    ):
        """Record agent recommendation metrics"""
        self.agent_recommendation_confidence.labels(
            agent_id=agent_id
        ).observe(confidence)
    
    def update_user_satisfaction(
        self,
        agent_id: str,
        task_type: str,
        satisfaction_score: float
    ):
        """Update user satisfaction metrics"""
        self.user_satisfaction_score.labels(
            agent_id=agent_id,
            task_type=task_type
        ).set(satisfaction_score)
    
    def update_model_accuracy(
        self,
        model_name: str,
        version: str,
        accuracy: float
    ):
        """Update model accuracy metrics"""
        self.model_accuracy.labels(
            model_name=model_name,
            version=version
        ).set(accuracy)
    
    def update_active_sessions(self, count: int):
        """Update active session count"""
        self.active_sessions.set(count)
    
    def update_cache_hit_rate(self, cache_type: str, hit_rate: float):
        """Update cache hit rate metrics"""
        self.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)

# Usage example with context manager
class MetricsContext:
    """Context manager for automatic metrics collection"""
    
    def __init__(self, metrics_collector: AgentMetricsCollector, user_id: str):
        self.metrics = metrics_collector
        self.user_id = user_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        
        self.metrics.record_agent_selection(
            self.user_id,
            duration,
            success
        )

# Global metrics instance
metrics_collector = AgentMetricsCollector()
```

## 🎓 Best Practices & Guidelines

### Code Quality Standards

```python
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]

  - repo: https://github.com/pycqa/pylint
    rev: v3.0.0a6
    hooks:
      - id: pylint
```

### Development Guidelines

#### **Agent Development Best Practices**

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Idempotent Operations**: Agent tasks should be safe to retry
3. **Comprehensive Error Handling**: Graceful failure with detailed error messages
4. **Performance Conscious**: Optimize for latency and resource usage
5. **Well Documented**: Clear docstrings and type hints

#### **Testing Strategy**

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Performance Tests**: Validate latency and throughput requirements
4. **End-to-End Tests**: Test complete user workflows
5. **Load Tests**: Validate system behavior under stress

#### **Security Considerations**

1. **Input Validation**: Sanitize all user inputs
2. **Authentication**: Verify user identity for all requests
3. **Authorization**: Check user permissions for actions
4. **Data Encryption**: Encrypt sensitive data at rest and in transit
5. **Audit Logging**: Log all security-relevant events

#### **Deployment Best Practices**

1. **Containerization**: Use Docker for consistent environments
2. **Configuration Management**: Externalize configuration
3. **Health Checks**: Implement comprehensive health monitoring
4. **Graceful Shutdown**: Handle shutdown signals properly
5. **Rolling Updates**: Deploy without downtime

This comprehensive Developer Guide provides everything needed to extend, customize, and integrate with Claude Code 2.0's AI-enhanced agent orchestration system. From creating custom agents to building integrations and following best practices, developers have all the tools and knowledge needed to build upon this powerful platform.