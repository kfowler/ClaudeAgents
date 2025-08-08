"""
Claude Agents Project Context Analysis System

A comprehensive project analysis system that automatically understands codebases
and provides intelligent agent recommendations based on technology stack,
complexity, architecture patterns, and quality metrics.

Key Features:
- Technology stack detection (languages, frameworks, databases, cloud providers)
- Project complexity assessment (files, lines, dependencies, technical debt)
- Architecture pattern recognition (MVC, microservices, serverless, etc.)
- Code quality assessment (tests, CI/CD, documentation, security)
- Git repository analysis (commits, contributors, activity level)
- Intelligent agent recommendation scoring
- Performance-optimized caching system
- CLI tool for standalone analysis
- Integration with Claude Code agent selection system

Usage:
    from analysis import ProjectAnalyzer, AgentRecommender
    
    # Analyze a project
    analyzer = ProjectAnalyzer()
    context = analyzer.analyze_project("/path/to/project")
    
    # Get agent recommendations
    recommender = AgentRecommender("./agents")
    recommendation = recommender.recommend_agents("/path/to/project", "add AI features")
    
    print(f"Recommended primary agent: {recommendation.primary_agents[0].agent_name}")
"""

from .project_analyzer import (
    ProjectAnalyzer,
    ProjectContext,
    TechStackInfo,
    ComplexityMetrics,
    ArchitectureInfo,
    QualityAssessment,
    FilePatternAnalyzer,
    GitAnalyzer,
    ComplexityAnalyzer,
    ArchitectureAnalyzer
)

from .agent_recommender import (
    AgentRecommender,
    AgentRecommendation,
    AgentScore,
    AgentDatabase
)

__version__ = "1.0.0"
__author__ = "Claude Code"
__license__ = "MIT"

__all__ = [
    # Core analysis classes
    "ProjectAnalyzer",
    "ProjectContext", 
    "TechStackInfo",
    "ComplexityMetrics",
    "ArchitectureInfo",
    "QualityAssessment",
    
    # Specialized analyzers
    "FilePatternAnalyzer",
    "GitAnalyzer", 
    "ComplexityAnalyzer",
    "ArchitectureAnalyzer",
    
    # Agent recommendation system
    "AgentRecommender",
    "AgentRecommendation",
    "AgentScore",
    "AgentDatabase",
]


def analyze_project_quick(project_path: str, agents_dir: str = "./agents") -> dict:
    """
    Quick analysis function for simple use cases.
    
    Returns both project analysis and agent recommendations in a single call.
    
    Args:
        project_path: Path to the project directory
        agents_dir: Path to the agents directory (default: "./agents")
    
    Returns:
        Dictionary containing 'analysis' and 'recommendations' keys
    """
    try:
        analyzer = ProjectAnalyzer()
        recommender = AgentRecommender(agents_dir)
        
        context = analyzer.analyze_project(project_path)
        recommendation = recommender.recommend_agents(project_path)
        
        return {
            'analysis': context,
            'recommendations': recommendation,
            'summary': {
                'domain_type': context.architecture.domain_type,
                'primary_language': max(context.tech_stack.languages.items(), key=lambda x: x[1])[0] if context.tech_stack.languages else 'unknown',
                'complexity': recommendation.estimated_complexity,
                'risk_level': recommendation.risk_level,
                'top_agent': recommendation.primary_agents[0].agent_name if recommendation.primary_agents else 'unknown'
            }
        }
    except Exception as e:
        return {
            'error': str(e),
            'analysis': None,
            'recommendations': None
        }


def get_recommended_agents(project_path: str, request: str = None, agents_dir: str = "./agents") -> list:
    """
    Get a simple list of recommended agent names for a project.
    
    Args:
        project_path: Path to the project directory
        request: Optional user request for context
        agents_dir: Path to the agents directory
    
    Returns:
        List of recommended agent names in priority order
    """
    try:
        recommender = AgentRecommender(agents_dir)
        recommendation = recommender.recommend_agents(project_path, request)
        
        agents = []
        
        # Add Tier 1 agents (required and high-scoring)
        for agent in recommendation.primary_agents:
            if agent.required or agent.score >= 50:
                agents.append(agent.agent_name)
        
        # Add Tier 2 agents with high scores
        for agent in recommendation.context_agents:
            if agent.score >= 60:
                agents.append(agent.agent_name)
        
        return agents
        
    except Exception as e:
        return ['full-stack-architect', 'security-audit-specialist', 'qa-test-engineer']  # Safe defaults


def detect_project_type(project_path: str) -> str:
    """
    Quick project type detection.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        Project type string ('web_app', 'mobile_app', 'api_service', etc.)
    """
    try:
        analyzer = ProjectAnalyzer()
        context = analyzer.analyze_project(project_path)
        return context.architecture.domain_type
    except Exception:
        return 'unknown'


# Configuration constants
DEFAULT_CACHE_EXPIRY_HOURS = 24
DEFAULT_PERFORMANCE_CACHE_DAYS = 30
SUPPORTED_LANGUAGES = [
    'python', 'javascript', 'typescript', 'rust', 'go', 'java', 'swift', 
    'kotlin', 'cpp', 'csharp', 'ruby', 'php'
]
SUPPORTED_FRAMEWORKS = [
    'react', 'nextjs', 'vue', 'angular', 'svelte', 'django', 'flask', 
    'fastapi', 'express', 'springboot', 'rails', 'laravel'
]