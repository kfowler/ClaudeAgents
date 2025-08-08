"""
Comprehensive Project Context Analysis System

Automatically understands codebases and provides intelligent agent recommendations
by analyzing technology stacks, complexity, architecture patterns, and quality metrics.
"""

import os
import json
import re
import sqlite3
import hashlib
import subprocess
import ast
try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TechStackInfo:
    """Technology stack information detected from project files"""
    languages: Dict[str, float]  # Language -> confidence score
    frameworks: Dict[str, float]  # Framework -> confidence score
    databases: List[str]  # Detected databases
    cloud_providers: List[str]  # AWS, GCP, Azure, etc.
    build_tools: List[str]  # npm, cargo, maven, etc.
    package_managers: List[str]  # yarn, pip, composer, etc.
    testing_frameworks: List[str]  # jest, pytest, rspec, etc.


@dataclass
class ComplexityMetrics:
    """Project complexity assessment metrics"""
    file_count: int
    line_count: int
    directory_depth: int
    dependency_count: int
    cyclomatic_complexity: float
    test_coverage_estimate: float
    technical_debt_score: float  # 0-100, higher = more debt


@dataclass
class ArchitectureInfo:
    """Architecture pattern recognition results"""
    patterns: List[str]  # MVC, microservices, serverless, etc.
    domain_type: str  # web_app, mobile_app, api_service, etc.
    deployment_type: str  # monolith, microservices, serverless
    data_access_patterns: List[str]  # REST, GraphQL, database direct
    
    
@dataclass
class QualityAssessment:
    """Code quality and security assessment"""
    has_tests: bool
    has_ci_cd: bool
    has_documentation: bool
    has_linting: bool
    has_type_checking: bool
    security_config_present: bool
    license_present: bool
    readme_quality_score: float  # 0-100


@dataclass
class ProjectContext:
    """Complete project analysis context"""
    project_path: str
    tech_stack: TechStackInfo
    complexity: ComplexityMetrics
    architecture: ArchitectureInfo
    quality: QualityAssessment
    git_info: Dict[str, Any]
    timestamp: str
    analysis_version: str = "1.0.0"


class FilePatternAnalyzer:
    """Analyzes file patterns to detect technologies and frameworks"""
    
    # Technology detection patterns
    LANGUAGE_PATTERNS = {
        'python': {
            'extensions': ['.py', '.pyx', '.pyi'],
            'files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'directories': ['__pycache__', '.pytest_cache']
        },
        'javascript': {
            'extensions': ['.js', '.jsx', '.mjs'],
            'files': ['package.json', '.npmrc', 'yarn.lock'],
            'directories': ['node_modules', '.npm']
        },
        'typescript': {
            'extensions': ['.ts', '.tsx', '.d.ts'],
            'files': ['tsconfig.json', 'tslint.json'],
            'directories': []
        },
        'rust': {
            'extensions': ['.rs'],
            'files': ['Cargo.toml', 'Cargo.lock'],
            'directories': ['target']
        },
        'go': {
            'extensions': ['.go'],
            'files': ['go.mod', 'go.sum', 'Gopkg.toml'],
            'directories': ['vendor']
        },
        'java': {
            'extensions': ['.java', '.jar', '.war'],
            'files': ['pom.xml', 'build.gradle', 'gradle.properties'],
            'directories': ['target', 'build', '.gradle']
        },
        'swift': {
            'extensions': ['.swift'],
            'files': ['Package.swift', 'Package.resolved'],
            'directories': ['.build']
        },
        'kotlin': {
            'extensions': ['.kt', '.kts'],
            'files': ['build.gradle.kts'],
            'directories': []
        },
        'cpp': {
            'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
            'files': ['CMakeLists.txt', 'Makefile', 'configure.ac'],
            'directories': ['build', 'cmake-build-debug']
        },
        'csharp': {
            'extensions': ['.cs', '.csx'],
            'files': ['*.csproj', '*.sln', 'packages.config'],
            'directories': ['bin', 'obj', 'packages']
        },
        'ruby': {
            'extensions': ['.rb', '.rbw'],
            'files': ['Gemfile', 'Gemfile.lock', 'Rakefile'],
            'directories': ['vendor/bundle']
        },
        'php': {
            'extensions': ['.php', '.phtml', '.php3', '.php4', '.php5'],
            'files': ['composer.json', 'composer.lock'],
            'directories': ['vendor']
        }
    }
    
    FRAMEWORK_PATTERNS = {
        'react': {
            'files': ['package.json'],
            'content_patterns': [r'"react":', r'import.*from.*["\']react["\']'],
            'directories': []
        },
        'nextjs': {
            'files': ['package.json', 'next.config.js'],
            'content_patterns': [r'"next":', r'from.*["\']next/'],
            'directories': ['.next']
        },
        'vue': {
            'files': ['package.json'],
            'content_patterns': [r'"vue":', r'<template>', r'\.vue$'],
            'directories': []
        },
        'angular': {
            'files': ['angular.json', 'package.json'],
            'content_patterns': [r'"@angular/', r'ng serve', r'ng build'],
            'directories': ['dist', '.angular']
        },
        'svelte': {
            'files': ['package.json', 'svelte.config.js'],
            'content_patterns': [r'"svelte":', r'\.svelte$'],
            'directories': ['.svelte-kit']
        },
        'django': {
            'files': ['manage.py', 'requirements.txt', 'setup.py'],
            'content_patterns': [r'django', r'DJANGO_SETTINGS_MODULE'],
            'directories': []
        },
        'flask': {
            'files': ['requirements.txt', 'app.py'],
            'content_patterns': [r'from flask import', r'Flask\(__name__\)'],
            'directories': []
        },
        'fastapi': {
            'files': ['requirements.txt'],
            'content_patterns': [r'from fastapi import', r'FastAPI\(\)'],
            'directories': []
        },
        'express': {
            'files': ['package.json'],
            'content_patterns': [r'"express":', r'require\(["\']express["\']\)'],
            'directories': []
        },
        'springboot': {
            'files': ['pom.xml', 'build.gradle'],
            'content_patterns': [r'spring-boot-starter', r'@SpringBootApplication'],
            'directories': []
        },
        'rails': {
            'files': ['Gemfile'],
            'content_patterns': [r'gem ["\']rails["\']', r'Rails.application'],
            'directories': ['app', 'config', 'db']
        },
        'laravel': {
            'files': ['composer.json', 'artisan'],
            'content_patterns': [r'"laravel/framework"', r'Illuminate\\'],
            'directories': ['app', 'config', 'resources']
        }
    }
    
    DATABASE_PATTERNS = {
        'postgresql': [r'psycopg2', r'pg_config', r'postgresql://', r'POSTGRES_'],
        'mysql': [r'mysql', r'pymysql', r'mysql://', r'MYSQL_'],
        'sqlite': [r'sqlite3', r'\.db$', r'\.sqlite$', r'sqlite://'],
        'mongodb': [r'pymongo', r'mongoose', r'mongodb://', r'MONGO_'],
        'redis': [r'redis-py', r'redis', r'redis://', r'REDIS_'],
        'elasticsearch': [r'elasticsearch', r'elastic', r'ES_'],
        'influxdb': [r'influxdb', r'influx', r'INFLUX_'],
        'cassandra': [r'cassandra', r'CASSANDRA_'],
        'dynamodb': [r'boto3.*dynamodb', r'DYNAMODB_', r'dynamo']
    }
    
    CLOUD_PATTERNS = {
        'aws': [r'boto3', r'aws-sdk', r'AWS_', r'\.aws/', r'ec2', r's3', r'lambda'],
        'gcp': [r'google-cloud', r'gcp', r'GCP_', r'GOOGLE_', r'bigquery'],
        'azure': [r'azure', r'AZURE_', r'azurecli', r'az login'],
        'vercel': [r'vercel', r'now\.json', r'\.vercel/'],
        'netlify': [r'netlify', r'_redirects', r'netlify\.toml'],
        'heroku': [r'Procfile', r'heroku', r'HEROKU_'],
        'digitalocean': [r'doctl', r'digitalocean', r'DO_']
    }
    
    def __init__(self):
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, Any]:
        """Compile regex patterns for performance"""
        compiled = {}
        for category in ['DATABASE_PATTERNS', 'CLOUD_PATTERNS']:
            patterns = getattr(self, category)
            compiled[category] = {}
            for key, pattern_list in patterns.items():
                compiled[category][key] = [re.compile(pattern, re.IGNORECASE) for pattern in pattern_list]
        
        for framework, config in self.FRAMEWORK_PATTERNS.items():
            if 'content_patterns' in config:
                config['compiled_patterns'] = [re.compile(pattern, re.IGNORECASE) for pattern in config['content_patterns']]
        
        return compiled


class GitAnalyzer:
    """Analyzes Git repository information for project maturity and patterns"""
    
    @staticmethod
    def analyze_repository(project_path: str) -> Dict[str, Any]:
        """Analyze git repository information"""
        git_info = {
            'is_git_repo': False,
            'commit_count': 0,
            'contributor_count': 0,
            'last_commit_date': None,
            'repository_age_days': 0,
            'branch_count': 0,
            'tag_count': 0,
            'has_ci_cd': False,
            'activity_level': 'unknown'
        }
        
        try:
            # Check if it's a git repository
            git_dir = os.path.join(project_path, '.git')
            if not os.path.exists(git_dir):
                return git_info
            
            git_info['is_git_repo'] = True
            
            # Change to project directory for git commands
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            try:
                # Get commit count
                result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    git_info['commit_count'] = int(result.stdout.strip())
                
                # Get contributor count
                result = subprocess.run(['git', 'log', '--format=%ae', '--all'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    contributors = set(result.stdout.strip().split('\n'))
                    git_info['contributor_count'] = len([c for c in contributors if c])
                
                # Get last commit date
                result = subprocess.run(['git', 'log', '-1', '--format=%ci'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    git_info['last_commit_date'] = result.stdout.strip()
                
                # Get first commit date for repository age
                result = subprocess.run(['git', 'log', '--reverse', '--format=%ci', '-1'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    first_commit = datetime.fromisoformat(result.stdout.strip().replace(' +', '+'))
                    age = datetime.now(first_commit.tzinfo) - first_commit
                    git_info['repository_age_days'] = age.days
                
                # Get branch count
                result = subprocess.run(['git', 'branch', '-a'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    branches = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                    git_info['branch_count'] = len(branches)
                
                # Get tag count
                result = subprocess.run(['git', 'tag'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    tags = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                    git_info['tag_count'] = len(tags)
                
                # Check for CI/CD indicators
                ci_indicators = ['.github/workflows', '.gitlab-ci.yml', '.travis.yml', 
                               'Jenkinsfile', '.circleci', 'azure-pipelines.yml']
                git_info['has_ci_cd'] = any(os.path.exists(os.path.join(project_path, indicator)) 
                                          for indicator in ci_indicators)
                
                # Determine activity level
                if git_info['commit_count'] > 100 and git_info['contributor_count'] > 5:
                    git_info['activity_level'] = 'high'
                elif git_info['commit_count'] > 20 and git_info['contributor_count'] > 1:
                    git_info['activity_level'] = 'medium'
                else:
                    git_info['activity_level'] = 'low'
                
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            logger.warning(f"Git analysis failed: {e}")
        
        return git_info


class ComplexityAnalyzer:
    """Analyzes project complexity metrics"""
    
    @staticmethod
    def analyze_complexity(project_path: str, tech_stack: TechStackInfo) -> ComplexityMetrics:
        """Analyze project complexity metrics"""
        metrics = ComplexityMetrics(
            file_count=0,
            line_count=0,
            directory_depth=0,
            dependency_count=0,
            cyclomatic_complexity=0.0,
            test_coverage_estimate=0.0,
            technical_debt_score=0.0
        )
        
        # Count files and lines
        source_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.rs', '.go', '.java', 
                           '.swift', '.kt', '.cpp', '.cc', '.cxx', '.hpp', '.h', '.cs', 
                           '.rb', '.php', '.vue', '.svelte'}
        
        max_depth = 0
        total_lines = 0
        total_files = 0
        
        for root, dirs, files in os.walk(project_path):
            # Skip common ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in {'node_modules', 'target', 'build', 'dist', '__pycache__', 
                               'vendor', 'venv', '.git', '.svn', '.hg'}]
            
            depth = root[len(project_path):].count(os.sep)
            max_depth = max(max_depth, depth)
            
            for file in files:
                if any(file.endswith(ext) for ext in source_extensions):
                    total_files += 1
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            total_lines += lines
                    except Exception:
                        continue
        
        metrics.file_count = total_files
        metrics.line_count = total_lines
        metrics.directory_depth = max_depth
        
        # Analyze dependencies
        metrics.dependency_count = ComplexityAnalyzer._count_dependencies(project_path, tech_stack)
        
        # Estimate test coverage
        metrics.test_coverage_estimate = ComplexityAnalyzer._estimate_test_coverage(project_path)
        
        # Calculate technical debt score
        metrics.technical_debt_score = ComplexityAnalyzer._calculate_technical_debt(project_path, tech_stack)
        
        return metrics
    
    @staticmethod
    def _count_dependencies(project_path: str, tech_stack: TechStackInfo) -> int:
        """Count project dependencies from various manifest files"""
        dependency_count = 0
        
        # JavaScript/TypeScript dependencies
        package_json = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependency_count += len(deps) + len(dev_deps)
            except Exception:
                pass
        
        # Python dependencies
        requirements_files = ['requirements.txt', 'requirements-dev.txt', 'requirements-test.txt']
        for req_file in requirements_files:
            req_path = os.path.join(project_path, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        dependency_count += len(lines)
                except Exception:
                    pass
        
        # Rust dependencies
        cargo_toml = os.path.join(project_path, 'Cargo.toml')
        if os.path.exists(cargo_toml) and HAS_TOML:
            try:
                with open(cargo_toml, 'r') as f:
                    data = toml.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('dev-dependencies', {})
                    dependency_count += len(deps) + len(dev_deps)
            except Exception:
                pass
        
        # Go dependencies
        go_mod = os.path.join(project_path, 'go.mod')
        if os.path.exists(go_mod):
            try:
                with open(go_mod, 'r') as f:
                    content = f.read()
                    # Count require statements
                    require_count = len(re.findall(r'^\s*[^/\s]+\s+v\d+', content, re.MULTILINE))
                    dependency_count += require_count
            except Exception:
                pass
        
        return dependency_count
    
    @staticmethod
    def _estimate_test_coverage(project_path: str) -> float:
        """Estimate test coverage based on test file presence"""
        source_files = 0
        test_files = 0
        
        test_patterns = [
            r'test_.*\.py$', r'.*_test\.py$',  # Python
            r'.*\.test\.(js|ts)x?$', r'.*\.spec\.(js|ts)x?$',  # JavaScript/TypeScript
            r'.*_test\.rs$',  # Rust
            r'.*_test\.go$',  # Go
            r'.*Test\.java$', r'.*Tests\.java$',  # Java
            r'.*Test\.swift$', r'.*Tests\.swift$',  # Swift
            r'.*Test\.kt$', r'.*Tests\.kt$',  # Kotlin
        ]
        
        compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in test_patterns]
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in {'node_modules', 'target', 'build', 'dist', '__pycache__'}]
            
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.rs', '.go', 
                                '.java', '.swift', '.kt')):
                    source_files += 1
                    if any(pattern.match(file) for pattern in compiled_patterns):
                        test_files += 1
        
        if source_files == 0:
            return 0.0
        
        # Rough estimation: assume each test file covers 3-5 source files
        estimated_coverage = min(100.0, (test_files * 4) / source_files * 100)
        return estimated_coverage
    
    @staticmethod
    def _calculate_technical_debt(project_path: str, tech_stack: TechStackInfo) -> float:
        """Calculate technical debt score based on various indicators"""
        debt_score = 0.0
        
        # Check for common debt indicators
        debt_indicators = [
            'TODO', 'FIXME', 'HACK', 'XXX', 'WORKAROUND', 'TEMPORARY'
        ]
        
        total_lines = 0
        debt_comments = 0
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in {'node_modules', 'target', 'build'}]
            
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.rs', '.go', 
                                '.java', '.swift', '.kt', '.cpp', '.hpp')):
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.count('\n')
                            total_lines += lines
                            
                            for indicator in debt_indicators:
                                debt_comments += len(re.findall(indicator, content, re.IGNORECASE))
                    except Exception:
                        continue
        
        if total_lines > 0:
            debt_score = min(100.0, (debt_comments / total_lines) * 1000)
        
        # Additional debt indicators
        if not os.path.exists(os.path.join(project_path, 'README.md')):
            debt_score += 10
        
        if not os.path.exists(os.path.join(project_path, 'LICENSE')):
            debt_score += 5
        
        # Check for outdated dependencies (simplified check)
        package_json = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    # Check for old React versions as an example
                    react_version = data.get('dependencies', {}).get('react', '')
                    if react_version and react_version.startswith('^16'):
                        debt_score += 15  # Using older React version
            except Exception:
                pass
        
        return min(100.0, debt_score)


class ArchitectureAnalyzer:
    """Analyzes architecture patterns and project structure"""
    
    ARCHITECTURE_PATTERNS = {
        'mvc': {
            'indicators': ['models', 'views', 'controllers', 'app/models', 'app/views', 'app/controllers'],
            'file_patterns': [r'.*[Mm]odel.*', r'.*[Vv]iew.*', r'.*[Cc]ontroller.*']
        },
        'mvp': {
            'indicators': ['presenters', 'app/presenters'],
            'file_patterns': [r'.*[Pp]resenter.*']
        },
        'mvvm': {
            'indicators': ['viewmodels', 'app/viewmodels'],
            'file_patterns': [r'.*[Vv]iew[Mm]odel.*']
        },
        'microservices': {
            'indicators': ['services', 'service', 'docker-compose.yml', 'kubernetes', 'k8s'],
            'file_patterns': [r'service.*\.py$', r'.*-service/', r'Dockerfile']
        },
        'serverless': {
            'indicators': ['serverless.yml', 'lambda', 'functions', 'netlify/functions', 'vercel/api'],
            'file_patterns': [r'lambda.*\.py$', r'function.*\.js$', r'handler.*']
        },
        'jamstack': {
            'indicators': ['static', 'public', 'dist', '_site', 'build'],
            'file_patterns': [r'gatsby-.*', r'next\.config\.js', r'nuxt\.config\.js']
        },
        'spa': {
            'indicators': ['src/components', 'src/pages', 'src/routes'],
            'file_patterns': [r'App\.(js|jsx|ts|tsx)$', r'index\.html']
        },
        'api_first': {
            'indicators': ['api', 'endpoints', 'routes'],
            'file_patterns': [r'api/.*', r'routes/.*', r'endpoints/.*']
        }
    }
    
    DOMAIN_TYPES = {
        'web_app': ['src/components', 'public', 'static', 'templates', 'views'],
        'mobile_app': ['ios', 'android', 'src/main/java', 'src/main/kotlin', 'lib/main.dart'],
        'api_service': ['api', 'endpoints', 'routes', 'controllers'],
        'desktop_app': ['electron', 'tauri', 'src-tauri', 'main.js'],
        'cli_tool': ['bin', 'cmd', 'cli', 'main.py', 'main.go', 'src/main.rs'],
        'library': ['lib', 'src/lib', 'package', '__init__.py'],
        'data_pipeline': ['pipelines', 'etl', 'airflow', 'dags', 'jobs'],
        'ml_project': ['models', 'notebooks', 'experiments', 'training', 'inference'],
        'game': ['game', 'unity', 'unreal', 'godot', 'assets', 'scenes'],
        'devops': ['infrastructure', 'terraform', 'ansible', 'docker', 'k8s', 'kubernetes']
    }
    
    @staticmethod
    def analyze_architecture(project_path: str, tech_stack: TechStackInfo) -> ArchitectureInfo:
        """Analyze project architecture patterns and domain type"""
        architecture = ArchitectureInfo(
            patterns=[],
            domain_type='unknown',
            deployment_type='unknown',
            data_access_patterns=[]
        )
        
        # Collect all directory and file paths
        all_paths = []
        all_files = []
        
        for root, dirs, files in os.walk(project_path):
            rel_root = os.path.relpath(root, project_path)
            if rel_root != '.':
                all_paths.append(rel_root)
            
            for file in files:
                file_path = os.path.join(rel_root, file) if rel_root != '.' else file
                all_files.append(file_path)
        
        # Detect architecture patterns
        for pattern_name, config in ArchitectureAnalyzer.ARCHITECTURE_PATTERNS.items():
            score = 0
            
            # Check directory/file indicators
            for indicator in config['indicators']:
                if any(indicator in path for path in all_paths + all_files):
                    score += 1
            
            # Check file patterns
            for pattern in config.get('file_patterns', []):
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
                if any(compiled_pattern.search(file) for file in all_files):
                    score += 1
            
            if score > 0:
                architecture.patterns.append(pattern_name)
        
        # Detect domain type
        domain_scores = {}
        for domain, indicators in ArchitectureAnalyzer.DOMAIN_TYPES.items():
            score = sum(1 for indicator in indicators 
                       if any(indicator in path for path in all_paths + all_files))
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            architecture.domain_type = max(domain_scores, key=domain_scores.get)
        
        # Determine deployment type
        if 'docker-compose.yml' in all_files or any('service' in path for path in all_paths):
            architecture.deployment_type = 'microservices'
        elif any('lambda' in path or 'serverless' in path for path in all_paths + all_files):
            architecture.deployment_type = 'serverless'
        elif any('Dockerfile' in file for file in all_files):
            architecture.deployment_type = 'containerized'
        else:
            architecture.deployment_type = 'monolith'
        
        # Detect data access patterns
        data_patterns = []
        
        # Check for GraphQL
        if any('graphql' in file.lower() or 'gql' in file.lower() for file in all_files):
            data_patterns.append('graphql')
        
        # Check for REST API
        if any('api' in path or 'rest' in path for path in all_paths):
            data_patterns.append('rest')
        
        # Check for database ORM/ODM
        orm_indicators = ['models.py', 'schema.py', 'entity', 'repository']
        if any(indicator in file for file in all_files for indicator in orm_indicators):
            data_patterns.append('orm')
        
        architecture.data_access_patterns = data_patterns
        
        return architecture


class ProjectAnalyzer:
    """Main project analysis engine"""
    
    def __init__(self, cache_db_path: Optional[str] = None):
        self.file_analyzer = FilePatternAnalyzer()
        self.cache_db_path = cache_db_path or "project_analysis_cache.db"
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_analysis (
                project_path TEXT PRIMARY KEY,
                path_hash TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                analysis_version TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON project_analysis (timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def _calculate_path_hash(self, project_path: str) -> str:
        """Calculate hash of project structure for cache invalidation"""
        hasher = hashlib.md5()
        
        try:
            for root, dirs, files in os.walk(project_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in {'node_modules', 'target', 'build', '__pycache__'}]
                
                for file in sorted(files):
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            hasher.update(f"{file_path}:{stat.st_mtime}:{stat.st_size}".encode())
                        except OSError:
                            continue
        except Exception as e:
            logger.warning(f"Error calculating path hash: {e}")
            return hashlib.md5(str(datetime.now()).encode()).hexdigest()
        
        return hasher.hexdigest()
    
    def _get_cached_analysis(self, project_path: str, path_hash: str) -> Optional[ProjectContext]:
        """Get cached analysis if available and valid"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT analysis_data, timestamp, analysis_version 
                FROM project_analysis 
                WHERE project_path = ? AND path_hash = ?
            ''', (project_path, path_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                analysis_data, timestamp, analysis_version = result
                # Check if cache is still valid (24 hours)
                cached_time = datetime.fromisoformat(timestamp)
                if datetime.now() - cached_time < timedelta(hours=24):
                    return ProjectContext(**json.loads(analysis_data))
        
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
        
        return None
    
    def _cache_analysis(self, project_path: str, path_hash: str, context: ProjectContext):
        """Cache analysis results"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO project_analysis 
                (project_path, path_hash, analysis_data, timestamp, analysis_version)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project_path, 
                path_hash, 
                json.dumps(asdict(context)), 
                context.timestamp,
                context.analysis_version
            ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.warning(f"Error caching analysis: {e}")
    
    def analyze_project(self, project_path: str, force_refresh: bool = False) -> ProjectContext:
        """Perform comprehensive project analysis"""
        project_path = os.path.abspath(project_path)
        
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        # Check cache first
        path_hash = self._calculate_path_hash(project_path)
        if not force_refresh:
            cached = self._get_cached_analysis(project_path, path_hash)
            if cached:
                logger.info(f"Using cached analysis for {project_path}")
                return cached
        
        logger.info(f"Analyzing project: {project_path}")
        
        # Analyze technology stack
        tech_stack = self._analyze_tech_stack(project_path)
        
        # Analyze complexity
        complexity = ComplexityAnalyzer.analyze_complexity(project_path, tech_stack)
        
        # Analyze architecture
        architecture = ArchitectureAnalyzer.analyze_architecture(project_path, tech_stack)
        
        # Analyze quality
        quality = self._analyze_quality(project_path)
        
        # Analyze git information
        git_info = GitAnalyzer.analyze_repository(project_path)
        
        # Create project context
        context = ProjectContext(
            project_path=project_path,
            tech_stack=tech_stack,
            complexity=complexity,
            architecture=architecture,
            quality=quality,
            git_info=git_info,
            timestamp=datetime.now().isoformat(),
            analysis_version="1.0.0"
        )
        
        # Cache results
        self._cache_analysis(project_path, path_hash, context)
        
        return context
    
    def _analyze_tech_stack(self, project_path: str) -> TechStackInfo:
        """Analyze technology stack"""
        tech_stack = TechStackInfo(
            languages={},
            frameworks={},
            databases=[],
            cloud_providers=[],
            build_tools=[],
            package_managers=[],
            testing_frameworks=[]
        )
        
        # Collect all files for analysis
        all_files = []
        file_contents = {}
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in {'node_modules', 'target', 'build', '__pycache__'}]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                all_files.append((rel_path, file))
                
                # Read certain files for content analysis
                if file in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 
                           'pom.xml', 'build.gradle', 'Gemfile', 'composer.json']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_contents[rel_path] = f.read()
                    except Exception:
                        continue
        
        # Detect languages
        language_scores = defaultdict(float)
        for rel_path, filename in all_files:
            for lang, config in self.file_analyzer.LANGUAGE_PATTERNS.items():
                score = 0
                
                # Check file extensions
                if any(filename.endswith(ext) for ext in config['extensions']):
                    score += 1.0
                
                # Check specific files
                if filename in config['files']:
                    score += 2.0
                
                # Check directories
                if any(dir_name in rel_path for dir_name in config['directories']):
                    score += 0.5
                
                language_scores[lang] += score
        
        # Normalize language scores
        total_score = sum(language_scores.values())
        if total_score > 0:
            tech_stack.languages = {lang: score/total_score 
                                   for lang, score in language_scores.items() if score > 0}
        
        # Detect frameworks
        framework_scores = defaultdict(float)
        for framework, config in self.file_analyzer.FRAMEWORK_PATTERNS.items():
            score = 0
            
            # Check specific files
            for file_pattern in config['files']:
                if any(filename == file_pattern or filename.endswith(file_pattern.lstrip('*')) 
                      for rel_path, filename in all_files):
                    score += 1.0
            
            # Check content patterns
            if 'compiled_patterns' in config:
                for rel_path, content in file_contents.items():
                    for pattern in config['compiled_patterns']:
                        if pattern.search(content):
                            score += 1.0
            
            framework_scores[framework] = score
        
        tech_stack.frameworks = {fw: score for fw, score in framework_scores.items() if score > 0}
        
        # Detect databases, cloud providers, etc.
        all_content = ' '.join(file_contents.values())
        
        for db_name, patterns in self.file_analyzer.compiled_patterns['DATABASE_PATTERNS'].items():
            if any(pattern.search(all_content) for pattern in patterns):
                tech_stack.databases.append(db_name)
        
        for cloud_name, patterns in self.file_analyzer.compiled_patterns['CLOUD_PATTERNS'].items():
            if any(pattern.search(all_content) for pattern in patterns):
                tech_stack.cloud_providers.append(cloud_name)
        
        # Detect build tools and package managers
        build_tools = {
            'npm': 'package.json',
            'yarn': 'yarn.lock',
            'cargo': 'Cargo.toml',
            'maven': 'pom.xml',
            'gradle': 'build.gradle',
            'pip': 'requirements.txt',
            'poetry': 'pyproject.toml',
            'bundler': 'Gemfile',
            'composer': 'composer.json',
            'make': 'Makefile',
            'cmake': 'CMakeLists.txt'
        }
        
        for tool, indicator_file in build_tools.items():
            if any(filename == indicator_file for rel_path, filename in all_files):
                tech_stack.build_tools.append(tool)
                if tool in ['npm', 'yarn', 'pip', 'cargo', 'bundler', 'composer']:
                    tech_stack.package_managers.append(tool)
        
        # Detect testing frameworks
        test_frameworks = {
            'jest': [r'"jest":', r'jest\.config'],
            'mocha': [r'"mocha":', r'mocha\.opts'],
            'pytest': [r'pytest', r'conftest\.py'],
            'unittest': [r'import unittest', r'from unittest'],
            'rspec': [r'gem.*rspec', r'spec_helper'],
            'junit': [r'junit', r'@Test'],
            'cargo_test': [r'#\[test\]'],
            'go_test': [r'func Test.*testing\.T']
        }
        
        for framework, patterns in test_frameworks.items():
            compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            if any(pattern.search(all_content) for pattern in compiled_patterns):
                tech_stack.testing_frameworks.append(framework)
        
        return tech_stack
    
    def _analyze_quality(self, project_path: str) -> QualityAssessment:
        """Analyze code quality indicators"""
        quality = QualityAssessment(
            has_tests=False,
            has_ci_cd=False,
            has_documentation=False,
            has_linting=False,
            has_type_checking=False,
            security_config_present=False,
            license_present=False,
            readme_quality_score=0.0
        )
        
        # Check for common files
        files_to_check = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                files_to_check.append(file.lower())
                if len(files_to_check) > 1000:  # Limit for performance
                    break
        
        # Check for tests
        test_indicators = ['test', 'spec', '__tests__', 'tests']
        quality.has_tests = any(indicator in ' '.join(files_to_check) for indicator in test_indicators)
        
        # Check for CI/CD
        ci_files = ['.github', '.gitlab-ci.yml', '.travis.yml', 'jenkinsfile', 
                   '.circleci', 'azure-pipelines.yml']
        quality.has_ci_cd = any(ci_file in ' '.join(files_to_check) for ci_file in ci_files)
        
        # Check for documentation
        doc_files = ['readme.md', 'readme.rst', 'readme.txt', 'docs', 'documentation']
        quality.has_documentation = any(doc_file in ' '.join(files_to_check) for doc_file in doc_files)
        
        # Check for linting
        lint_files = ['.eslintrc', '.pylintrc', '.rubocop.yml', 'clippy.toml', 'golangci.yml']
        quality.has_linting = any(lint_file in ' '.join(files_to_check) for lint_file in lint_files)
        
        # Check for type checking
        type_files = ['tsconfig.json', 'mypy.ini', '.mypy.ini', 'pyrightconfig.json']
        quality.has_type_checking = any(type_file in ' '.join(files_to_check) for type_file in type_files)
        
        # Check for security configuration
        security_files = ['.env.example', 'security.md', 'dockerfile', 'docker-compose.yml']
        quality.security_config_present = any(sec_file in ' '.join(files_to_check) for sec_file in security_files)
        
        # Check for license
        license_files = ['license', 'licence', 'copying']
        quality.license_present = any(lic_file in ' '.join(files_to_check) for lic_file in license_files)
        
        # Analyze README quality
        readme_path = None
        for filename in ['README.md', 'README.rst', 'README.txt', 'readme.md']:
            full_path = os.path.join(project_path, filename)
            if os.path.exists(full_path):
                readme_path = full_path
                break
        
        if readme_path:
            quality.readme_quality_score = self._analyze_readme_quality(readme_path)
        
        return quality
    
    def _analyze_readme_quality(self, readme_path: str) -> float:
        """Analyze README file quality"""
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return 0.0
        
        score = 0.0
        
        # Length check
        if len(content) > 200:
            score += 20
        elif len(content) > 100:
            score += 10
        
        # Section headers
        quality_sections = [
            'installation', 'usage', 'api', 'example', 'contributing', 
            'license', 'documentation', 'getting started', 'requirements'
        ]
        
        content_lower = content.lower()
        for section in quality_sections:
            if section in content_lower:
                score += 8
        
        # Code blocks
        if '```' in content or '    ' in content:  # Markdown or indented code
            score += 15
        
        # Links
        if 'http' in content or '[' in content:
            score += 10
        
        # Badges (common quality indicator)
        if 'badge' in content or 'shield' in content:
            score += 10
        
        return min(100.0, score)


def main():
    """CLI entry point for project analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze project context and recommend agents')
    parser.add_argument('path', help='Path to project directory')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh of cached analysis')
    parser.add_argument('--output', choices=['json', 'summary'], default='summary', help='Output format')
    parser.add_argument('--cache-db', help='Path to cache database')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = ProjectAnalyzer(cache_db_path=args.cache_db)
    
    try:
        # Analyze project
        context = analyzer.analyze_project(args.path, force_refresh=args.force_refresh)
        
        if args.output == 'json':
            print(json.dumps(asdict(context), indent=2))
        else:
            # Print summary
            print(f"Project Analysis: {context.project_path}")
            print(f"Analysis Date: {context.timestamp}")
            print("\n=== Technology Stack ===")
            print(f"Languages: {', '.join(f'{lang} ({score:.1%})' for lang, score in context.tech_stack.languages.items())}")
            print(f"Frameworks: {', '.join(f'{fw} (score: {score})' for fw, score in context.tech_stack.frameworks.items())}")
            print(f"Databases: {', '.join(context.tech_stack.databases) if context.tech_stack.databases else 'None detected'}")
            print(f"Cloud Providers: {', '.join(context.tech_stack.cloud_providers) if context.tech_stack.cloud_providers else 'None detected'}")
            
            print("\n=== Project Complexity ===")
            print(f"Files: {context.complexity.file_count}")
            print(f"Lines of Code: {context.complexity.line_count:,}")
            print(f"Directory Depth: {context.complexity.directory_depth}")
            print(f"Dependencies: {context.complexity.dependency_count}")
            print(f"Test Coverage Estimate: {context.complexity.test_coverage_estimate:.1f}%")
            print(f"Technical Debt Score: {context.complexity.technical_debt_score:.1f}/100")
            
            print("\n=== Architecture ===")
            print(f"Domain Type: {context.architecture.domain_type}")
            print(f"Deployment Type: {context.architecture.deployment_type}")
            print(f"Architecture Patterns: {', '.join(context.architecture.patterns) if context.architecture.patterns else 'None detected'}")
            print(f"Data Access Patterns: {', '.join(context.architecture.data_access_patterns) if context.architecture.data_access_patterns else 'None detected'}")
            
            print("\n=== Quality Assessment ===")
            print(f"Has Tests: {'Yes' if context.quality.has_tests else 'No'}")
            print(f"Has CI/CD: {'Yes' if context.quality.has_ci_cd else 'No'}")
            print(f"Has Documentation: {'Yes' if context.quality.has_documentation else 'No'}")
            print(f"Has Linting: {'Yes' if context.quality.has_linting else 'No'}")
            print(f"README Quality: {context.quality.readme_quality_score:.1f}/100")
            
            print("\n=== Git Repository ===")
            if context.git_info['is_git_repo']:
                print(f"Commits: {context.git_info['commit_count']}")
                print(f"Contributors: {context.git_info['contributor_count']}")
                print(f"Repository Age: {context.git_info['repository_age_days']} days")
                print(f"Activity Level: {context.git_info['activity_level']}")
            else:
                print("Not a Git repository")
    
    except Exception as e:
        print(f"Error analyzing project: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())