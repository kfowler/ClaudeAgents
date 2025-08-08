"""
Request Analysis and Semantic Matching System

This module analyzes user requests to extract intent, complexity, and context,
then performs semantic matching with agent capabilities.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
import json
from datetime import datetime

# ML/AI imports
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# Local imports
from .vector_search import VectorSearchManager, SearchResult, SearchBackend
from .agent_embedder import AgentCapabilityEmbedder


logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """User intent categories."""
    NEW_PROJECT = "new_project"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    BUG_FIX = "bug_fix"
    CODE_REVIEW = "code_review"
    OPTIMIZATION = "optimization"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    ANALYSIS = "analysis"
    LEARNING = "learning"
    CREATIVE = "creative"
    UNKNOWN = "unknown"


class ComplexityLevel(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class RiskLevel(Enum):
    """Project risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProjectContext:
    """Context information extracted from project analysis."""
    project_path: Optional[Path] = None
    technologies: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    cloud_services: List[str] = field(default_factory=list)
    project_type: Optional[str] = None
    team_size: Optional[str] = None
    deployment_env: Optional[str] = None
    has_ai_features: bool = False
    has_mobile_component: bool = False
    has_web_component: bool = False
    is_production: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'technologies': self.technologies,
            'frameworks': self.frameworks,
            'languages': self.languages,
            'databases': self.databases,
            'cloud_services': self.cloud_services,
            'project_type': self.project_type,
            'team_size': self.team_size,
            'deployment_env': self.deployment_env,
            'has_ai_features': self.has_ai_features,
            'has_mobile_component': self.has_mobile_component,
            'has_web_component': self.has_web_component,
            'is_production': self.is_production
        }


@dataclass
class RequestAnalysis:
    """Comprehensive analysis of a user request."""
    original_request: str
    intent_category: IntentCategory
    complexity_level: ComplexityLevel
    risk_level: RiskLevel
    extracted_requirements: List[str] = field(default_factory=list)
    technical_keywords: List[str] = field(default_factory=list)
    domain_keywords: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    project_context: Optional[ProjectContext] = None
    embedding: Optional[np.ndarray] = None
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            'original_request': self.original_request,
            'intent_category': self.intent_category.value,
            'complexity_level': self.complexity_level.value,
            'risk_level': self.risk_level.value,
            'extracted_requirements': self.extracted_requirements,
            'technical_keywords': self.technical_keywords,
            'domain_keywords': self.domain_keywords,
            'confidence_score': self.confidence_score,
            'project_context': self.project_context.to_dict() if self.project_context else None,
            'embedding': self.embedding.tolist() if self.embedding is not None else None,
            'processing_time': self.processing_time
        }


class ProjectContextExtractor:
    """Extract context information from project files and structure."""
    
    # File extensions to technology mappings
    TECH_EXTENSIONS = {
        '.js': 'JavaScript',
        '.jsx': 'React',
        '.ts': 'TypeScript',
        '.tsx': 'React TypeScript',
        '.py': 'Python',
        '.java': 'Java',
        '.go': 'Go',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C'
    }
    
    # Configuration file patterns
    CONFIG_PATTERNS = {
        'package.json': ('Node.js', 'npm'),
        'yarn.lock': ('Node.js', 'yarn'),
        'requirements.txt': ('Python', 'pip'),
        'pyproject.toml': ('Python', 'poetry/pdm'),
        'Pipfile': ('Python', 'pipenv'),
        'go.mod': ('Go', 'go modules'),
        'Cargo.toml': ('Rust', 'cargo'),
        'pom.xml': ('Java', 'maven'),
        'build.gradle': ('Java', 'gradle'),
        'composer.json': ('PHP', 'composer'),
        'Gemfile': ('Ruby', 'bundler'),
        '.csproj': ('C#', 'dotnet'),
        'CMakeLists.txt': ('C/C++', 'cmake')
    }
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        'next.config.js': 'Next.js',
        'nuxt.config.js': 'Nuxt.js',
        'vue.config.js': 'Vue.js',
        'svelte.config.js': 'SvelteKit',
        'angular.json': 'Angular',
        'remix.config.js': 'Remix',
        'astro.config.js': 'Astro',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'FastAPI',
        'express': 'Express.js',
        'spring': 'Spring Boot'
    }
    
    # Database detection patterns
    DATABASE_PATTERNS = {
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'redis': 'Redis',
        'sqlite': 'SQLite',
        'dynamodb': 'DynamoDB',
        'supabase': 'Supabase',
        'planetscale': 'PlanetScale'
    }
    
    async def extract_context(self, project_path: Optional[Path]) -> ProjectContext:
        """Extract project context from directory structure and files."""
        if not project_path or not project_path.exists():
            return ProjectContext()
        
        context = ProjectContext(project_path=project_path)
        
        try:
            # Analyze file structure
            await self._analyze_file_structure(project_path, context)
            
            # Analyze configuration files
            await self._analyze_config_files(project_path, context)
            
            # Analyze package dependencies
            await self._analyze_dependencies(project_path, context)
            
            # Determine project characteristics
            await self._determine_project_characteristics(project_path, context)
            
        except Exception as e:
            logger.error(f"Error extracting project context: {e}")
        
        return context
    
    async def _analyze_file_structure(self, project_path: Path, context: ProjectContext):
        """Analyze file structure to detect technologies."""
        file_extensions = set()
        
        # Walk through project files
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                file_extensions.add(file_path.suffix.lower())
        
        # Map extensions to technologies
        for ext in file_extensions:
            if ext in self.TECH_EXTENSIONS:
                tech = self.TECH_EXTENSIONS[ext]
                if tech not in context.technologies:
                    context.technologies.append(tech)
        
        # Detect languages
        context.languages = [tech for tech in context.technologies 
                           if tech in ['JavaScript', 'TypeScript', 'Python', 'Java', 'Go', 'Rust', 'Swift', 'Kotlin']]
    
    async def _analyze_config_files(self, project_path: Path, context: ProjectContext):
        """Analyze configuration files to detect frameworks and tools."""
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                filename = file_path.name
                
                # Check for configuration patterns
                for pattern, (tech, tool) in self.CONFIG_PATTERNS.items():
                    if filename == pattern:
                        if tech not in context.technologies:
                            context.technologies.append(tech)
                
                # Check for framework patterns
                for pattern, framework in self.FRAMEWORK_PATTERNS.items():
                    if filename == pattern or pattern in filename:
                        if framework not in context.frameworks:
                            context.frameworks.append(framework)
    
    async def _analyze_dependencies(self, project_path: Path, context: ProjectContext):
        """Analyze dependency files to detect additional technologies."""
        try:
            # Analyze package.json for Node.js projects
            package_json = project_path / "package.json"
            if package_json.exists():
                await self._analyze_package_json(package_json, context)
            
            # Analyze requirements.txt for Python projects
            requirements_txt = project_path / "requirements.txt"
            if requirements_txt.exists():
                await self._analyze_requirements_txt(requirements_txt, context)
            
            # Analyze pyproject.toml for Python projects
            pyproject_toml = project_path / "pyproject.toml"
            if pyproject_toml.exists():
                await self._analyze_pyproject_toml(pyproject_toml, context)
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
    
    async def _analyze_package_json(self, package_json: Path, context: ProjectContext):
        """Analyze package.json for Node.js dependencies."""
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            # Detect frameworks and libraries
            framework_mapping = {
                'react': 'React',
                'next': 'Next.js',
                'vue': 'Vue.js',
                'nuxt': 'Nuxt.js',
                'svelte': 'Svelte',
                '@sveltejs/kit': 'SvelteKit',
                'angular': 'Angular',
                'remix': 'Remix',
                'astro': 'Astro',
                'express': 'Express.js',
                'fastify': 'Fastify',
                'nestjs': 'NestJS'
            }
            
            for dep in dependencies:
                for key, framework in framework_mapping.items():
                    if key in dep and framework not in context.frameworks:
                        context.frameworks.append(framework)
            
            # Detect databases
            db_mapping = {
                'mongodb': 'MongoDB',
                'mongoose': 'MongoDB',
                'pg': 'PostgreSQL',
                'postgresql': 'PostgreSQL',
                'mysql': 'MySQL',
                'redis': 'Redis',
                'sqlite': 'SQLite'
            }
            
            for dep in dependencies:
                for key, database in db_mapping.items():
                    if key in dep and database not in context.databases:
                        context.databases.append(database)
            
            # Detect AI/ML libraries
            ai_libraries = ['openai', '@anthropic-ai/sdk', 'langchain', 'pinecone', 'weaviate']
            if any(lib in dependencies for lib in ai_libraries):
                context.has_ai_features = True
            
        except Exception as e:
            logger.error(f"Error analyzing package.json: {e}")
    
    async def _analyze_requirements_txt(self, requirements_txt: Path, context: ProjectContext):
        """Analyze requirements.txt for Python dependencies."""
        try:
            with open(requirements_txt, 'r') as f:
                lines = f.readlines()
            
            dependencies = [line.split('==')[0].split('>=')[0].strip() for line in lines if line.strip()]
            
            # Detect frameworks
            framework_mapping = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'streamlit': 'Streamlit',
                'gradio': 'Gradio'
            }
            
            for dep in dependencies:
                for key, framework in framework_mapping.items():
                    if key in dep.lower() and framework not in context.frameworks:
                        context.frameworks.append(framework)
            
            # Detect AI/ML libraries
            ai_libraries = ['openai', 'anthropic', 'langchain', 'transformers', 'torch', 'tensorflow']
            if any(lib in dependencies for lib in ai_libraries):
                context.has_ai_features = True
            
        except Exception as e:
            logger.error(f"Error analyzing requirements.txt: {e}")
    
    async def _analyze_pyproject_toml(self, pyproject_toml: Path, context: ProjectContext):
        """Analyze pyproject.toml for Python dependencies."""
        try:
            import toml
            with open(pyproject_toml, 'r') as f:
                data = toml.load(f)
            
            dependencies = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
            dependencies.update(data.get('project', {}).get('dependencies', []))
            
            # Similar analysis as requirements.txt
            dep_list = list(dependencies.keys()) if isinstance(dependencies, dict) else dependencies
            
            # Detect frameworks and AI libraries
            framework_mapping = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'streamlit': 'Streamlit'
            }
            
            for dep in dep_list:
                dep_name = dep.split('[')[0] if isinstance(dep, str) else str(dep)
                for key, framework in framework_mapping.items():
                    if key in dep_name.lower() and framework not in context.frameworks:
                        context.frameworks.append(framework)
            
            ai_libraries = ['openai', 'anthropic', 'langchain', 'transformers', 'torch', 'tensorflow']
            if any(lib in str(dep_list).lower() for lib in ai_libraries):
                context.has_ai_features = True
            
        except Exception as e:
            logger.error(f"Error analyzing pyproject.toml: {e}")
    
    async def _determine_project_characteristics(self, project_path: Path, context: ProjectContext):
        """Determine high-level project characteristics."""
        # Determine project type
        if any(fw in context.frameworks for fw in ['React', 'Vue.js', 'Angular', 'Svelte']):
            context.has_web_component = True
            context.project_type = 'web_application'
        
        if any(fw in context.frameworks for fw in ['React Native', 'Flutter']) or \
           any(lang in context.languages for lang in ['Swift', 'Kotlin']):
            context.has_mobile_component = True
            if context.project_type:
                context.project_type = 'full_stack_application'
            else:
                context.project_type = 'mobile_application'
        
        if context.has_ai_features:
            context.project_type = 'ai_application'
        
        # Determine production readiness
        docker_files = list(project_path.glob("**/Dockerfile*"))
        k8s_files = list(project_path.glob("**/*.yaml")) + list(project_path.glob("**/*.yml"))
        ci_files = list(project_path.glob("**/.github/workflows/*"))
        
        context.is_production = bool(docker_files or k8s_files or ci_files)
        
        # Estimate team size based on project complexity
        total_files = len(list(project_path.rglob("*")))
        if total_files > 1000:
            context.team_size = 'large'
        elif total_files > 200:
            context.team_size = 'medium'
        else:
            context.team_size = 'small'
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in analysis."""
        ignore_patterns = [
            '.git', 'node_modules', '__pycache__', '.pytest_cache',
            'venv', '.venv', 'env', '.env', 'build', 'dist',
            '.DS_Store', 'target', 'bin', 'obj'
        ]
        
        return any(pattern in str(file_path) for pattern in ignore_patterns)


class RequestAnalyzer:
    """Analyze user requests to extract intent, complexity, and requirements."""
    
    # Intent classification patterns
    INTENT_PATTERNS = {
        IntentCategory.NEW_PROJECT: [
            'new project', 'create project', 'start project', 'build from scratch',
            'fresh start', 'new app', 'new application', 'initialize project'
        ],
        IntentCategory.FEATURE_ENHANCEMENT: [
            'add feature', 'implement feature', 'new functionality', 'enhance',
            'extend', 'improve', 'upgrade', 'add support for'
        ],
        IntentCategory.BUG_FIX: [
            'bug', 'error', 'issue', 'problem', 'fix', 'broken', 'not working',
            'debug', 'troubleshoot', 'resolve issue'
        ],
        IntentCategory.CODE_REVIEW: [
            'review', 'code review', 'audit', 'examine', 'check code',
            'feedback', 'suggestions', 'best practices'
        ],
        IntentCategory.OPTIMIZATION: [
            'optimize', 'performance', 'speed up', 'faster', 'efficiency',
            'memory', 'cpu', 'bandwidth', 'scalability'
        ],
        IntentCategory.REFACTORING: [
            'refactor', 'restructure', 'reorganize', 'clean up', 'modernize',
            'update architecture', 'improve code structure'
        ],
        IntentCategory.TESTING: [
            'test', 'testing', 'unit test', 'integration test', 'e2e test',
            'quality assurance', 'QA', 'test coverage'
        ],
        IntentCategory.DEPLOYMENT: [
            'deploy', 'deployment', 'production', 'release', 'publish',
            'CI/CD', 'continuous integration', 'docker', 'kubernetes'
        ],
        IntentCategory.ANALYSIS: [
            'analyze', 'analysis', 'evaluate', 'assess', 'study',
            'investigate', 'research', 'compare'
        ],
        IntentCategory.CREATIVE: [
            'design', 'creative', 'art', 'visual', 'graphics', 'video',
            'audio', 'content', 'writing', 'illustration'
        ]
    }
    
    # Complexity indicators
    COMPLEXITY_INDICATORS = {
        ComplexityLevel.SIMPLE: [
            'simple', 'basic', 'quick', 'small', 'minimal', 'straightforward'
        ],
        ComplexityLevel.MODERATE: [
            'moderate', 'medium', 'standard', 'typical', 'regular'
        ],
        ComplexityLevel.COMPLEX: [
            'complex', 'advanced', 'sophisticated', 'comprehensive',
            'large scale', 'enterprise', 'production ready'
        ],
        ComplexityLevel.VERY_COMPLEX: [
            'very complex', 'highly complex', 'massive', 'distributed',
            'multi-service', 'microservices', 'enterprise grade'
        ]
    }
    
    # Risk indicators
    RISK_INDICATORS = {
        RiskLevel.CRITICAL: [
            'financial', 'payment', 'banking', 'healthcare', 'medical',
            'safety', 'security critical', 'compliance', 'HIPAA', 'GDPR'
        ],
        RiskLevel.HIGH: [
            'production', 'user data', 'authentication', 'authorization',
            'public facing', 'customer data', 'sensitive'
        ],
        RiskLevel.MEDIUM: [
            'internal', 'business logic', 'integration', 'API',
            'moderate risk', 'standard security'
        ],
        RiskLevel.LOW: [
            'prototype', 'proof of concept', 'learning', 'personal',
            'demo', 'test', 'experimental'
        ]
    }
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize request analyzer."""
        self.model_name = model_name
        self.embedder = None
        self.nlp = None
        self.context_extractor = ProjectContextExtractor()
        
    async def initialize(self):
        """Initialize NLP models."""
        # Initialize sentence transformer
        self.embedder = SentenceTransformer(self.model_name)
        
        # Initialize spaCy for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        logger.info("Request analyzer initialized")
    
    async def analyze_request(self, 
                            request: str, 
                            project_path: Optional[Path] = None) -> RequestAnalysis:
        """Analyze a user request comprehensively."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract project context
            project_context = None
            if project_path:
                project_context = await self.context_extractor.extract_context(project_path)
            
            # Generate embedding
            embedding = None
            if self.embedder:
                embedding = self.embedder.encode(request, normalize_embeddings=True)
            
            # Classify intent
            intent_category = self._classify_intent(request)
            
            # Assess complexity
            complexity_level = self._assess_complexity(request, project_context)
            
            # Assess risk
            risk_level = self._assess_risk(request, project_context)
            
            # Extract requirements
            requirements = self._extract_requirements(request)
            
            # Extract technical keywords
            technical_keywords = self._extract_technical_keywords(request)
            
            # Extract domain keywords
            domain_keywords = self._extract_domain_keywords(request)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                intent_category, complexity_level, requirements, technical_keywords
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return RequestAnalysis(
                original_request=request,
                intent_category=intent_category,
                complexity_level=complexity_level,
                risk_level=risk_level,
                extracted_requirements=requirements,
                technical_keywords=technical_keywords,
                domain_keywords=domain_keywords,
                confidence_score=confidence_score,
                project_context=project_context,
                embedding=embedding,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error analyzing request: {e}")
            raise
    
    def _classify_intent(self, request: str) -> IntentCategory:
        """Classify the user's intent from the request."""
        request_lower = request.lower()
        best_match = IntentCategory.UNKNOWN
        max_matches = 0
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            matches = sum(1 for pattern in patterns if pattern in request_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = intent
        
        return best_match
    
    def _assess_complexity(self, request: str, context: Optional[ProjectContext]) -> ComplexityLevel:
        """Assess the complexity level of the request."""
        request_lower = request.lower()
        
        # Check explicit complexity indicators
        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            if any(indicator in request_lower for indicator in indicators):
                return level
        
        # Infer complexity from context and request content
        complexity_factors = 0
        
        # Request length and detail
        if len(request) > 500:
            complexity_factors += 2
        elif len(request) > 200:
            complexity_factors += 1
        
        # Multiple requirements
        requirement_indicators = [
            'and', 'also', 'additionally', 'furthermore', 'multiple',
            'several', 'various', 'different'
        ]
        complexity_factors += sum(1 for indicator in requirement_indicators 
                                if indicator in request_lower)
        
        # Technical complexity indicators
        complex_tech_terms = [
            'microservices', 'distributed', 'scalable', 'high availability',
            'load balancing', 'caching', 'database', 'authentication',
            'real-time', 'async', 'concurrent', 'performance'
        ]
        complexity_factors += sum(1 for term in complex_tech_terms 
                                if term in request_lower)
        
        # Context-based complexity
        if context:
            if context.is_production:
                complexity_factors += 2
            if context.has_ai_features:
                complexity_factors += 1
            if len(context.technologies) > 5:
                complexity_factors += 1
            if context.team_size == 'large':
                complexity_factors += 1
        
        # Map complexity factors to levels
        if complexity_factors >= 6:
            return ComplexityLevel.VERY_COMPLEX
        elif complexity_factors >= 4:
            return ComplexityLevel.COMPLEX
        elif complexity_factors >= 2:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE
    
    def _assess_risk(self, request: str, context: Optional[ProjectContext]) -> RiskLevel:
        """Assess the risk level of the request."""
        request_lower = request.lower()
        
        # Check explicit risk indicators
        for level, indicators in self.RISK_INDICATORS.items():
            if any(indicator in request_lower for indicator in indicators):
                return level
        
        # Infer risk from context
        if context:
            if context.is_production:
                return RiskLevel.HIGH
            if any(keyword in request_lower for keyword in ['user', 'data', 'api']):
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _extract_requirements(self, request: str) -> List[str]:
        """Extract specific requirements from the request."""
        requirements = []
        
        # Use spaCy for better requirement extraction
        if self.nlp:
            doc = self.nlp(request)
            
            # Extract sentences that contain requirement indicators
            requirement_indicators = ['need', 'want', 'should', 'must', 'require', 'implement']
            
            for sent in doc.sents:
                if any(indicator in sent.text.lower() for indicator in requirement_indicators):
                    requirements.append(sent.text.strip())
        else:
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', request)
            requirement_indicators = ['need', 'want', 'should', 'must', 'require', 'implement']
            
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in requirement_indicators):
                    requirements.append(sentence.strip())
        
        return requirements[:10]  # Limit to top 10 requirements
    
    def _extract_technical_keywords(self, request: str) -> List[str]:
        """Extract technical keywords from the request."""
        # Technology keywords
        tech_keywords = [
            'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt.js',
            'Node.js', 'Python', 'Django', 'Flask', 'FastAPI', 'Java',
            'Spring', 'Go', 'Rust', 'TypeScript', 'JavaScript',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker',
            'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD', 'API',
            'GraphQL', 'REST', 'WebSocket', 'AI', 'ML', 'LLM'
        ]
        
        request_lower = request.lower()
        found_keywords = []
        
        for keyword in tech_keywords:
            if keyword.lower() in request_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_domain_keywords(self, request: str) -> List[str]:
        """Extract domain-specific keywords from the request."""
        domain_keywords = [
            'web development', 'mobile development', 'backend', 'frontend',
            'full-stack', 'devops', 'security', 'testing', 'database',
            'authentication', 'authorization', 'deployment', 'monitoring',
            'analytics', 'performance', 'optimization', 'AI', 'machine learning',
            'data science', 'e-commerce', 'fintech', 'healthtech'
        ]
        
        request_lower = request.lower()
        found_keywords = []
        
        for keyword in domain_keywords:
            if keyword in request_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_confidence(self, 
                            intent: IntentCategory,
                            complexity: ComplexityLevel,
                            requirements: List[str],
                            technical_keywords: List[str]) -> float:
        """Calculate confidence score for the analysis."""
        confidence_factors = []
        
        # Intent classification confidence
        if intent != IntentCategory.UNKNOWN:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)
        
        # Requirements extraction confidence
        if len(requirements) > 0:
            confidence_factors.append(min(0.9, 0.5 + len(requirements) * 0.1))
        else:
            confidence_factors.append(0.4)
        
        # Technical keywords confidence
        if len(technical_keywords) > 0:
            confidence_factors.append(min(0.9, 0.6 + len(technical_keywords) * 0.05))
        else:
            confidence_factors.append(0.5)
        
        # Complexity assessment confidence
        if complexity != ComplexityLevel.SIMPLE:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.6)
        
        # Average confidence
        return sum(confidence_factors) / len(confidence_factors)


class SemanticMatcher:
    """Match user requests with agent capabilities using semantic analysis."""
    
    def __init__(self, 
                 vector_search: VectorSearchManager,
                 request_analyzer: RequestAnalyzer):
        """Initialize semantic matcher."""
        self.vector_search = vector_search
        self.request_analyzer = request_analyzer
        
    async def initialize(self):
        """Initialize components."""
        await self.vector_search.initialize()
        await self.request_analyzer.initialize()
        logger.info("Semantic matcher initialized")
    
    async def close(self):
        """Close connections."""
        await self.vector_search.close()
    
    async def match_agents(self, 
                          request: str,
                          project_path: Optional[Path] = None,
                          top_k: int = 10,
                          include_explanation: bool = True) -> Tuple[RequestAnalysis, List[SearchResult]]:
        """Match user request with most suitable agents."""
        try:
            # Analyze the request
            analysis = await self.request_analyzer.analyze_request(request, project_path)
            
            if analysis.embedding is None:
                raise ValueError("Could not generate embedding for request")
            
            # Prepare metadata filters based on analysis
            metadata_filters = self._prepare_metadata_filters(analysis)
            
            # Perform semantic search
            search_results = await self.vector_search.search_agents(
                query_vector=analysis.embedding,
                top_k=top_k,
                similarity_threshold=0.3,
                metadata_filters=metadata_filters
            )
            
            # Enhance results with contextual scoring
            enhanced_results = self._enhance_results_with_context(
                search_results, analysis, include_explanation
            )
            
            return analysis, enhanced_results
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            raise
    
    def _prepare_metadata_filters(self, analysis: RequestAnalysis) -> Dict[str, Any]:
        """Prepare metadata filters based on request analysis."""
        filters = {}
        
        # Filter by complexity/tier based on request complexity
        if analysis.complexity_level == ComplexityLevel.SIMPLE:
            # Prefer tier 1 agents for simple tasks
            filters['tier'] = 1
        elif analysis.complexity_level == ComplexityLevel.VERY_COMPLEX:
            # Allow all tiers for very complex tasks
            pass
        
        # Filter by domain if specific domains detected
        if analysis.domain_keywords:
            # Use the most specific domain keyword
            primary_domain = analysis.domain_keywords[0]
            if 'web' in primary_domain:
                filters['domains'] = 'web_development'
            elif 'mobile' in primary_domain:
                filters['domains'] = 'mobile_development'
            elif 'AI' in primary_domain or 'machine learning' in primary_domain:
                filters['domains'] = 'ai_ml'
            elif 'security' in primary_domain:
                filters['domains'] = 'security'
        
        return filters
    
    def _enhance_results_with_context(self, 
                                    results: List[SearchResult],
                                    analysis: RequestAnalysis,
                                    include_explanation: bool) -> List[SearchResult]:
        """Enhance search results with contextual information."""
        enhanced_results = []
        
        for result in results:
            # Apply contextual scoring adjustments
            context_score = self._calculate_context_score(result, analysis)
            
            # Combine similarity and context scores
            final_score = (result.similarity_score * 0.7) + (context_score * 0.3)
            
            # Create enhanced result
            enhanced_result = SearchResult(
                agent_name=result.agent_name,
                similarity_score=final_score,
                metadata=result.metadata,
                embedding=result.embedding
            )
            
            # Generate detailed explanation
            if include_explanation:
                enhanced_result.explanation = self._generate_detailed_explanation(
                    result, analysis, context_score
                )
            
            enhanced_results.append(enhanced_result)
        
        # Re-sort by enhanced scores
        enhanced_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return enhanced_results
    
    def _calculate_context_score(self, 
                               result: SearchResult,
                               analysis: RequestAnalysis) -> float:
        """Calculate context-based scoring adjustment."""
        score_factors = []
        
        # Intent-based scoring
        intent_bonuses = {
            IntentCategory.NEW_PROJECT: {'tier': 1, 'project-orchestrator': 0.2},
            IntentCategory.BUG_FIX: {'security-audit-specialist': 0.1},
            IntentCategory.TESTING: {'qa-test-engineer': 0.3},
            IntentCategory.DEPLOYMENT: {'devops-engineer': 0.3},
            IntentCategory.CREATIVE: {'tier': 3}
        }
        
        intent_bonus = intent_bonuses.get(analysis.intent_category, {})
        if result.agent_name in intent_bonus:
            score_factors.append(intent_bonus[result.agent_name])
        elif 'tier' in intent_bonus and result.metadata.get('tier') == intent_bonus['tier']:
            score_factors.append(0.1)
        
        # Technology alignment
        if analysis.technical_keywords:
            agent_technologies = result.metadata.get('technologies', [])
            matching_techs = set(analysis.technical_keywords) & set(agent_technologies)
            if matching_techs:
                score_factors.append(min(0.3, len(matching_techs) * 0.1))
        
        # Project context alignment
        if analysis.project_context:
            context = analysis.project_context
            agent_domains = result.metadata.get('domains', [])
            
            # Web project bonus
            if context.has_web_component and 'web_development' in agent_domains:
                score_factors.append(0.2)
            
            # Mobile project bonus
            if context.has_mobile_component and 'mobile_development' in agent_domains:
                score_factors.append(0.2)
            
            # AI project bonus
            if context.has_ai_features and 'ai_ml' in agent_domains:
                score_factors.append(0.3)
            
            # Production readiness bonus
            if context.is_production:
                production_agents = ['security-audit-specialist', 'qa-test-engineer', 'devops-engineer']
                if result.agent_name in production_agents:
                    score_factors.append(0.2)
        
        # Risk-based adjustments
        risk_bonuses = {
            RiskLevel.CRITICAL: {'security-audit-specialist': 0.4, 'qa-test-engineer': 0.2},
            RiskLevel.HIGH: {'security-audit-specialist': 0.3, 'qa-test-engineer': 0.1}
        }
        
        risk_bonus = risk_bonuses.get(analysis.risk_level, {})
        if result.agent_name in risk_bonus:
            score_factors.append(risk_bonus[result.agent_name])
        
        # Calculate average context score
        return sum(score_factors) / max(1, len(score_factors)) if score_factors else 0.0
    
    def _generate_detailed_explanation(self, 
                                     result: SearchResult,
                                     analysis: RequestAnalysis,
                                     context_score: float) -> str:
        """Generate detailed explanation for agent recommendation."""
        explanations = []
        
        # Similarity explanation
        sim_score = result.similarity_score
        if sim_score >= 0.8:
            explanations.append(f"Excellent semantic match ({sim_score:.3f})")
        elif sim_score >= 0.6:
            explanations.append(f"Good semantic match ({sim_score:.3f})")
        else:
            explanations.append(f"Moderate semantic match ({sim_score:.3f})")
        
        # Intent alignment
        intent_alignments = {
            IntentCategory.NEW_PROJECT: "Ideal for new project development",
            IntentCategory.TESTING: "Specialized in testing and quality assurance",
            IntentCategory.DEPLOYMENT: "Expert in deployment and infrastructure",
            IntentCategory.CREATIVE: "Perfect for creative and design tasks"
        }
        
        if analysis.intent_category in intent_alignments:
            explanations.append(intent_alignments[analysis.intent_category])
        
        # Technology alignment
        if analysis.technical_keywords:
            agent_techs = result.metadata.get('technologies', [])
            matching_techs = set(analysis.technical_keywords) & set(agent_techs)
            if matching_techs:
                explanations.append(f"Supports {len(matching_techs)} requested technologies")
        
        # Context explanation
        if context_score > 0.1:
            explanations.append(f"Strong contextual fit (+{context_score:.2f})")
        
        # Risk consideration
        if analysis.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if result.agent_name in ['security-audit-specialist', 'qa-test-engineer']:
                explanations.append("Essential for high-risk projects")
        
        # Tier explanation
        tier = result.metadata.get('tier', 1)
        tier_descriptions = {
            1: "Core agent - always available",
            2: "Specialized agent - domain expert", 
            3: "Niche agent - unique expertise"
        }
        explanations.append(tier_descriptions.get(tier, "Unknown tier"))
        
        return "; ".join(explanations)