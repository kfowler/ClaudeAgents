"""
Agent Recommendation Scoring Engine

Integrates with the project analysis system to provide intelligent agent recommendations
based on project context, complexity, technology stack, and domain requirements.
"""

import os
import json
import re
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

from .project_analyzer import ProjectContext, ProjectAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class AgentScore:
    """Agent recommendation score with reasoning"""
    agent_name: str
    score: float  # 0-100
    tier: int  # 1, 2, or 3 (per AGENT_DECISION_TREE.md)
    confidence: float  # 0-100
    reasoning: List[str]  # Why this agent was recommended
    required: bool = False  # Mandatory for this project type


@dataclass
class AgentRecommendation:
    """Complete agent recommendation for a project"""
    project_path: str
    primary_agents: List[AgentScore]  # Tier 1 agents (always visible)
    context_agents: List[AgentScore]  # Tier 2 agents (context-triggered)
    specialist_agents: List[AgentScore]  # Tier 3 agents (explicit request)
    orchestration_pattern: str  # Recommended execution pattern
    risk_level: str  # low, medium, high, critical
    estimated_complexity: str  # simple, medium, high, specialized


class AgentDatabase:
    """Agent information database loaded from agent markdown files"""
    
    def __init__(self, agents_dir: str):
        self.agents_dir = agents_dir
        self.agents = self._load_agents()
    
    def _load_agents(self) -> Dict[str, Dict[str, Any]]:
        """Load agent definitions from markdown files"""
        agents = {}
        
        try:
            for filename in os.listdir(self.agents_dir):
                if filename.endswith('.md') and not filename.startswith('AGENT_'):
                    agent_path = os.path.join(self.agents_dir, filename)
                    agent_name = filename.replace('.md', '')
                    
                    try:
                        with open(agent_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Parse YAML frontmatter
                        if content.startswith('---') and HAS_YAML:
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                try:
                                    frontmatter = yaml.safe_load(parts[1])
                                except Exception:
                                    frontmatter = {}
                                agent_content = parts[2].strip()
                            else:
                                frontmatter = {}
                                agent_content = content
                        else:
                            frontmatter = {}
                            agent_content = content
                        
                        agents[agent_name] = {
                            'name': frontmatter.get('name', agent_name.replace('-', ' ').title()),
                            'description': frontmatter.get('description', ''),
                            'color': frontmatter.get('color', '#6366f1'),
                            'content': agent_content,
                            'keywords': self._extract_keywords(agent_content),
                            'specializations': self._extract_specializations(agent_content)
                        }
                        
                    except Exception as e:
                        logger.warning(f"Failed to load agent {agent_name}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Failed to load agents from {self.agents_dir}: {e}")
        
        return agents
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from agent content"""
        # Common technology keywords to look for
        tech_keywords = [
            'react', 'next.js', 'vue', 'angular', 'svelte', 'typescript', 'javascript',
            'python', 'django', 'flask', 'fastapi', 'rust', 'go', 'java', 'spring',
            'ios', 'android', 'swift', 'kotlin', 'flutter', 'react native',
            'postgresql', 'mongodb', 'redis', 'mysql', 'sqlite',
            'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'ci/cd',
            'ai', 'ml', 'machine learning', 'llm', 'gpt', 'claude', 'embeddings',
            'security', 'testing', 'qa', 'accessibility', 'a11y',
            'performance', 'optimization', 'monitoring',
            'api', 'rest', 'graphql', 'microservices', 'serverless',
            'database', 'data pipeline', 'analytics', 'etl'
        ]
        
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in tech_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_specializations(self, content: str) -> List[str]:
        """Extract specialization areas from agent content"""
        # Look for common specialization patterns
        specializations = []
        
        spec_patterns = [
            r'speciali[sz]es? in ([\w\s,]+)',
            r'expert in ([\w\s,]+)',
            r'focus(?:es)? on ([\w\s,]+)',
            r'responsible for ([\w\s,]+)'
        ]
        
        for pattern in spec_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the match and split on commas
                specs = [spec.strip() for spec in match.split(',')]
                specializations.extend(specs)
        
        return list(set(specializations))


class AgentRecommender:
    """Main agent recommendation engine"""
    
    # Tier assignments from AGENT_DECISION_TREE.md
    AGENT_TIERS = {
        # Tier 1: Core Agents (Default View) - Handle 80% of tasks
        1: [
            'full-stack-architect',
            'mobile-developer', 
            'project-orchestrator',
            'security-audit-specialist',
            'qa-test-engineer'
        ],
        
        # Tier 2: Specialized Agents (Context-Triggered) - Domain experts
        2: [
            'ai-ml-engineer',
            'data-engineer',
            'devops-engineer',
            'systems-engineer',
            'code-architect',
            'accessibility-expert',
            'the-critic',
            'product-strategist',
            'legacy-specialist',
            'platform-integrator'
        ],
        
        # Tier 3: Expert/Niche Agents (Explicit Request Only)
        3: [
            'functional-programmer',
            'metaprogramming-specialist',
            'elisp-specialist',
            'digital-artist', 'tv-writer', 'video-director', '3d-modeler', 
            'comedy-writer', 'audio-engineer',
            'merge-conflict-resolver',
            'creative-catalyst',
            'agent-orchestrator'
        ]
    }
    
    # Technology stack to agent mapping
    TECH_STACK_MAPPING = {
        'web_development': {
            'languages': ['javascript', 'typescript'],
            'frameworks': ['react', 'nextjs', 'vue', 'angular', 'svelte'],
            'primary_agent': 'full-stack-architect',
            'supporting_agents': ['devops-engineer', 'security-audit-specialist']
        },
        'mobile_development': {
            'languages': ['swift', 'kotlin', 'dart'],
            'frameworks': ['react_native', 'flutter'],
            'primary_agent': 'mobile-developer',
            'supporting_agents': ['full-stack-architect', 'security-audit-specialist']
        },
        'ai_ml': {
            'keywords': ['ai', 'ml', 'machine learning', 'llm', 'neural', 'model', 'training'],
            'primary_agent': 'ai-ml-engineer',
            'supporting_agents': ['data-engineer', 'systems-engineer']
        },
        'data_engineering': {
            'keywords': ['database', 'analytics', 'pipeline', 'etl', 'data'],
            'databases': ['postgresql', 'mongodb', 'redis', 'mysql'],
            'primary_agent': 'data-engineer',
            'supporting_agents': ['devops-engineer', 'systems-engineer']
        },
        'systems_programming': {
            'languages': ['rust', 'cpp', 'go'],
            'keywords': ['performance', 'optimization', 'systems', 'memory'],
            'primary_agent': 'systems-engineer',
            'supporting_agents': ['code-architect']
        },
        'infrastructure': {
            'keywords': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'ci/cd'],
            'primary_agent': 'devops-engineer',
            'supporting_agents': ['security-audit-specialist', 'systems-engineer']
        }
    }
    
    # Risk level assessment patterns
    RISK_PATTERNS = {
        'critical': [
            'financial', 'payment', 'billing', 'bank', 'money',
            'healthcare', 'medical', 'hipaa', 'patient',
            'government', 'security clearance', 'classified',
            'authentication', 'authorization', 'user data', 'personal data'
        ],
        'high': [
            'production', 'enterprise', 'saas', 'public-facing',
            'mobile app', 'app store', 'b2b', 'customer data'
        ],
        'medium': [
            'internal tool', 'api', 'service', 'dashboard', 'admin'
        ],
        'low': [
            'prototype', 'proof of concept', 'poc', 'demo', 'personal project'
        ]
    }
    
    # Orchestration patterns from AGENT_DECISION_TREE.md
    ORCHESTRATION_PATTERNS = {
        'simple_app': [
            'Implementation agent (Tier 1)',
            'Security review',
            'Testing'
        ],
        'new_product': [
            'Market research (product-strategist)',
            'Project planning (project-orchestrator)',
            'Implementation (primary agent)',
            'Security review',
            'Accessibility review',
            'Testing',
            'Deployment (devops-engineer)'
        ],
        'feature_addition': [
            'Implementation (Tier 1 agent)',
            'Architecture review (if needed)',
            'Testing',
            'Security review (if security-relevant)'
        ],
        'technical_decision': [
            'Analysis (the-critic)',
            'Feasibility assessment (specialists)',
            'Implementation planning'
        ],
        'specialized_work': [
            'Specialist implementation (Tier 3)',
            'Integration (if needed)',
            'Testing (if applicable)'
        ]
    }
    
    def __init__(self, agents_dir: str, decision_tree_path: Optional[str] = None):
        self.agent_db = AgentDatabase(agents_dir)
        self.decision_tree_path = decision_tree_path
        self.analyzer = ProjectAnalyzer()
    
    def recommend_agents(self, project_path: str, user_request: Optional[str] = None, 
                        force_refresh: bool = False) -> AgentRecommendation:
        """Generate agent recommendations for a project"""
        
        # Analyze project context
        context = self.analyzer.analyze_project(project_path, force_refresh=force_refresh)
        
        # Assess risk level
        risk_level = self._assess_risk_level(context, user_request)
        
        # Determine complexity
        complexity = self._assess_complexity(context)
        
        # Generate agent scores
        primary_agents = self._score_tier1_agents(context, user_request)
        context_agents = self._score_tier2_agents(context, user_request)
        specialist_agents = self._score_tier3_agents(context, user_request)
        
        # Determine orchestration pattern
        orchestration_pattern = self._determine_orchestration_pattern(context, user_request, complexity)
        
        return AgentRecommendation(
            project_path=project_path,
            primary_agents=sorted(primary_agents, key=lambda x: x.score, reverse=True),
            context_agents=sorted([a for a in context_agents if a.score > 20], key=lambda x: x.score, reverse=True),
            specialist_agents=sorted([a for a in specialist_agents if a.score > 10], key=lambda x: x.score, reverse=True),
            orchestration_pattern=orchestration_pattern,
            risk_level=risk_level,
            estimated_complexity=complexity
        )
    
    def _assess_risk_level(self, context: ProjectContext, user_request: Optional[str] = None) -> str:
        """Assess project risk level"""
        request_text = (user_request or '').lower()
        project_indicators = ' '.join([
            context.project_path.lower(),
            ' '.join(context.tech_stack.databases),
            ' '.join(context.tech_stack.cloud_providers),
            str(context.architecture.domain_type),
            str(context.architecture.deployment_type)
        ]).lower()
        
        combined_text = f"{request_text} {project_indicators}"
        
        # Check for critical risk indicators
        for pattern in self.RISK_PATTERNS['critical']:
            if pattern in combined_text:
                return 'critical'
        
        # Check for high risk indicators
        for pattern in self.RISK_PATTERNS['high']:
            if pattern in combined_text:
                return 'high'
        
        # Check for medium risk indicators
        for pattern in self.RISK_PATTERNS['medium']:
            if pattern in combined_text:
                return 'medium'
        
        # Check for low risk indicators
        for pattern in self.RISK_PATTERNS['low']:
            if pattern in combined_text:
                return 'low'
        
        # Default based on project characteristics
        if context.git_info['is_git_repo'] and context.git_info['commit_count'] > 50:
            return 'medium'
        elif context.quality.has_ci_cd and context.quality.has_tests:
            return 'medium'
        else:
            return 'low'
    
    def _assess_complexity(self, context: ProjectContext) -> str:
        """Assess project complexity level"""
        complexity_score = 0
        
        # File and line count factors
        if context.complexity.file_count > 200:
            complexity_score += 3
        elif context.complexity.file_count > 50:
            complexity_score += 2
        elif context.complexity.file_count > 10:
            complexity_score += 1
        
        if context.complexity.line_count > 50000:
            complexity_score += 3
        elif context.complexity.line_count > 10000:
            complexity_score += 2
        elif context.complexity.line_count > 1000:
            complexity_score += 1
        
        # Technology stack complexity
        if len(context.tech_stack.languages) > 3:
            complexity_score += 2
        elif len(context.tech_stack.languages) > 1:
            complexity_score += 1
        
        if len(context.tech_stack.frameworks) > 2:
            complexity_score += 2
        
        if len(context.tech_stack.databases) > 1:
            complexity_score += 1
        
        # Architecture patterns
        if 'microservices' in context.architecture.patterns:
            complexity_score += 3
        elif 'serverless' in context.architecture.patterns:
            complexity_score += 2
        
        # Dependency count
        if context.complexity.dependency_count > 100:
            complexity_score += 2
        elif context.complexity.dependency_count > 25:
            complexity_score += 1
        
        # Map score to complexity level
        if complexity_score >= 10:
            return 'high'
        elif complexity_score >= 6:
            return 'medium'
        elif complexity_score >= 2:
            return 'simple'
        else:
            # Check for specialized indicators
            specialized_keywords = ['functional', 'lisp', 'haskell', 'clojure', 'emacs', 
                                  'creative', 'art', 'design', 'audio', 'video']
            project_text = context.project_path.lower()
            if any(keyword in project_text for keyword in specialized_keywords):
                return 'specialized'
            return 'simple'
    
    def _score_tier1_agents(self, context: ProjectContext, user_request: Optional[str] = None) -> List[AgentScore]:
        """Score Tier 1 (core) agents"""
        scores = []
        request_text = (user_request or '').lower()
        
        for agent_name in self.AGENT_TIERS[1]:
            score = AgentScore(
                agent_name=agent_name,
                score=0.0,
                tier=1,
                confidence=0.0,
                reasoning=[],
                required=False
            )
            
            # Full-stack architect scoring
            if agent_name == 'full-stack-architect':
                if context.architecture.domain_type == 'web_app':
                    score.score += 80
                    score.reasoning.append("Project identified as web application")
                
                web_frameworks = ['react', 'nextjs', 'vue', 'angular', 'svelte', 'express']
                matching_frameworks = [fw for fw in web_frameworks if fw in context.tech_stack.frameworks]
                if matching_frameworks:
                    score.score += 60
                    score.reasoning.append(f"Uses web frameworks: {', '.join(matching_frameworks)}")
                
                web_keywords = ['web', 'frontend', 'backend', 'api', 'react', 'next.js']
                if any(keyword in request_text for keyword in web_keywords):
                    score.score += 40
                    score.reasoning.append("Web development keywords in request")
                
                if 'javascript' in context.tech_stack.languages or 'typescript' in context.tech_stack.languages:
                    score.score += 30
                    score.reasoning.append("Uses JavaScript/TypeScript")
            
            # Mobile developer scoring  
            elif agent_name == 'mobile-developer':
                if context.architecture.domain_type == 'mobile_app':
                    score.score += 80
                    score.reasoning.append("Project identified as mobile application")
                
                mobile_frameworks = ['react_native', 'flutter']
                matching_mobile_fw = [fw for fw in mobile_frameworks if fw in context.tech_stack.frameworks]
                if matching_mobile_fw:
                    score.score += 70
                    score.reasoning.append(f"Uses mobile frameworks: {', '.join(matching_mobile_fw)}")
                
                mobile_keywords = ['mobile', 'ios', 'android', 'app store', 'swift', 'kotlin']
                if any(keyword in request_text for keyword in mobile_keywords):
                    score.score += 60
                    score.reasoning.append("Mobile development keywords in request")
                
                if 'swift' in context.tech_stack.languages or 'kotlin' in context.tech_stack.languages:
                    score.score += 50
                    score.reasoning.append("Uses mobile development languages")
            
            # Project orchestrator scoring
            elif agent_name == 'project-orchestrator':
                if context.complexity.file_count > 100 or len(context.tech_stack.languages) > 2:
                    score.score += 60
                    score.reasoning.append("Large/complex project requiring coordination")
                
                orchestration_keywords = ['coordinate', 'orchestrate', 'manage', 'roadmap', 'timeline', 'complex']
                if any(keyword in request_text for keyword in orchestration_keywords):
                    score.score += 70
                    score.reasoning.append("Project coordination keywords in request")
                
                if 'microservices' in context.architecture.patterns:
                    score.score += 50
                    score.reasoning.append("Microservices architecture detected")
                
                if context.git_info['contributor_count'] > 3:
                    score.score += 30
                    score.reasoning.append("Multi-contributor project")
            
            # Security audit specialist scoring
            elif agent_name == 'security-audit-specialist':
                # Always important, but more so for certain contexts
                base_score = 40  # Base importance
                
                if 'production' in request_text or 'deploy' in request_text:
                    base_score += 40
                    score.reasoning.append("Production deployment mentioned")
                    score.required = True
                
                security_keywords = ['security', 'auth', 'authentication', 'vulnerability', 'audit']
                if any(keyword in request_text for keyword in security_keywords):
                    base_score += 50
                    score.reasoning.append("Security keywords in request")
                
                if context.architecture.domain_type in ['web_app', 'mobile_app', 'api_service']:
                    base_score += 30
                    score.reasoning.append("User-facing application type")
                
                if any(db in ['postgresql', 'mongodb', 'mysql'] for db in context.tech_stack.databases):
                    base_score += 20
                    score.reasoning.append("Uses database with user data")
                
                score.score = base_score
                if base_score >= 60:
                    score.required = True
            
            # QA test engineer scoring
            elif agent_name == 'qa-test-engineer':
                base_score = 50  # Always important
                
                if not context.quality.has_tests:
                    base_score += 40
                    score.reasoning.append("No existing tests detected")
                    score.required = True
                
                test_keywords = ['test', 'testing', 'qa', 'quality']
                if any(keyword in request_text for keyword in test_keywords):
                    base_score += 30
                    score.reasoning.append("Testing keywords in request")
                
                if context.complexity.file_count > 50:
                    base_score += 20
                    score.reasoning.append("Large codebase needs testing")
                
                score.score = base_score
            
            # Set confidence based on score
            score.confidence = min(100.0, score.score * 1.2)
            scores.append(score)
        
        return scores
    
    def _score_tier2_agents(self, context: ProjectContext, user_request: Optional[str] = None) -> List[AgentScore]:
        """Score Tier 2 (context-triggered) agents"""
        scores = []
        request_text = (user_request or '').lower()
        
        for agent_name in self.AGENT_TIERS[2]:
            score = AgentScore(
                agent_name=agent_name,
                score=0.0,
                tier=2,
                confidence=0.0,
                reasoning=[]
            )
            
            # AI/ML engineer scoring
            if agent_name == 'ai-ml-engineer':
                ai_keywords = ['ai', 'ml', 'machine learning', 'llm', 'gpt', 'claude', 
                              'neural', 'model', 'embeddings', 'vector', 'rag']
                matching_keywords = [kw for kw in ai_keywords if kw in request_text]
                if matching_keywords:
                    score.score += 80
                    score.reasoning.append(f"AI/ML keywords: {', '.join(matching_keywords)}")
                
                # Check for AI-related dependencies or files
                ai_patterns = ['tensorflow', 'pytorch', 'sklearn', 'openai', 'anthropic']
                project_content = f"{context.project_path} {' '.join(context.tech_stack.frameworks.keys())}"
                if any(pattern in project_content.lower() for pattern in ai_patterns):
                    score.score += 60
                    score.reasoning.append("AI/ML frameworks detected")
            
            # Data engineer scoring
            elif agent_name == 'data-engineer':
                data_keywords = ['database', 'data', 'analytics', 'pipeline', 'etl', 'warehouse']
                if any(keyword in request_text for keyword in data_keywords):
                    score.score += 70
                    score.reasoning.append("Data-related keywords in request")
                
                if len(context.tech_stack.databases) > 0:
                    score.score += 50
                    score.reasoning.append(f"Uses databases: {', '.join(context.tech_stack.databases)}")
                
                if context.architecture.domain_type == 'data_pipeline':
                    score.score += 80
                    score.reasoning.append("Data pipeline project detected")
            
            # DevOps engineer scoring
            elif agent_name == 'devops-engineer':
                devops_keywords = ['deploy', 'deployment', 'ci/cd', 'docker', 'kubernetes', 
                                 'aws', 'gcp', 'azure', 'infrastructure']
                if any(keyword in request_text for keyword in devops_keywords):
                    score.score += 70
                    score.reasoning.append("DevOps keywords in request")
                
                if context.quality.has_ci_cd:
                    score.score += 40
                    score.reasoning.append("CI/CD configuration detected")
                
                if len(context.tech_stack.cloud_providers) > 0:
                    score.score += 50
                    score.reasoning.append(f"Uses cloud providers: {', '.join(context.tech_stack.cloud_providers)}")
                
                if context.architecture.deployment_type in ['microservices', 'containerized']:
                    score.score += 40
                    score.reasoning.append(f"Deployment type: {context.architecture.deployment_type}")
            
            # Systems engineer scoring
            elif agent_name == 'systems-engineer':
                systems_keywords = ['performance', 'optimization', 'memory', 'concurrent', 
                                  'rust', 'c++', 'go', 'systems']
                if any(keyword in request_text for keyword in systems_keywords):
                    score.score += 70
                    score.reasoning.append("Systems programming keywords in request")
                
                systems_languages = ['rust', 'cpp', 'go']
                matching_langs = [lang for lang in systems_languages 
                                if lang in context.tech_stack.languages]
                if matching_langs:
                    score.score += 80
                    score.reasoning.append(f"Systems languages: {', '.join(matching_langs)}")
                
                if context.complexity.line_count > 50000:
                    score.score += 30
                    score.reasoning.append("Large codebase may need optimization")
            
            # Code architect scoring
            elif agent_name == 'code-architect':
                arch_keywords = ['architecture', 'refactor', 'code review', 'clean code', 
                               'best practices', 'maintainability']
                if any(keyword in request_text for keyword in arch_keywords):
                    score.score += 70
                    score.reasoning.append("Architecture/quality keywords in request")
                
                if context.complexity.technical_debt_score > 60:
                    score.score += 50
                    score.reasoning.append(f"High technical debt score: {context.complexity.technical_debt_score:.1f}")
                
                if context.complexity.file_count > 200:
                    score.score += 40
                    score.reasoning.append("Large codebase needs architectural review")
            
            # Accessibility expert scoring
            elif agent_name == 'accessibility-expert':
                a11y_keywords = ['accessibility', 'a11y', 'wcag', 'screen reader', 'inclusive']
                if any(keyword in request_text for keyword in a11y_keywords):
                    score.score += 80
                    score.reasoning.append("Accessibility keywords in request")
                
                if context.architecture.domain_type in ['web_app', 'mobile_app']:
                    score.score += 40
                    score.reasoning.append("User-facing application needs accessibility review")
                
                # Required for certain domains
                public_indicators = ['public', 'government', 'education', 'healthcare']
                if any(indicator in request_text for indicator in public_indicators):
                    score.score += 60
                    score.reasoning.append("Public-facing application detected")
            
            # The critic scoring
            elif agent_name == 'the-critic':
                decision_keywords = ['decide', 'choose', 'evaluate', 'compare', 'trade-off', 
                                   'architecture decision', 'which', 'should i']
                if any(keyword in request_text for keyword in decision_keywords):
                    score.score += 80
                    score.reasoning.append("Decision-making keywords in request")
                
                if len(context.tech_stack.languages) > 2 or len(context.tech_stack.frameworks) > 3:
                    score.score += 30
                    score.reasoning.append("Multiple technology choices may need evaluation")
            
            # Product strategist scoring
            elif agent_name == 'product-strategist':
                product_keywords = ['product', 'startup', 'business model', 'market research', 
                                  'competition', 'mvp', 'user research']
                if any(keyword in request_text for keyword in product_keywords):
                    score.score += 80
                    score.reasoning.append("Product strategy keywords in request")
                
                # New project indicators
                if context.git_info['commit_count'] < 10 and 'new' in request_text:
                    score.score += 50
                    score.reasoning.append("New project may need product strategy")
            
            # Legacy specialist scoring
            elif agent_name == 'legacy-specialist':
                legacy_keywords = ['legacy', 'migration', 'modernize', 'upgrade', 'refactor', 
                                 'objective-c', 'old']
                if any(keyword in request_text for keyword in legacy_keywords):
                    score.score += 80
                    score.reasoning.append("Legacy system keywords in request")
                
                # Old technology indicators
                old_indicators = ['jquery', 'php4', 'python2', 'objective-c']
                project_content = f"{context.project_path} {' '.join(context.tech_stack.frameworks.keys())}"
                if any(indicator in project_content.lower() for indicator in old_indicators):
                    score.score += 60
                    score.reasoning.append("Legacy technology detected")
            
            # Platform integrator scoring
            elif agent_name == 'platform-integrator':
                integration_keywords = ['integration', 'api', 'third-party', 'webhook', 
                                      'external service', 'platform']
                if any(keyword in request_text for keyword in integration_keywords):
                    score.score += 70
                    score.reasoning.append("Integration keywords in request")
                
                # Multiple cloud providers suggest integrations
                if len(context.tech_stack.cloud_providers) > 1:
                    score.score += 40
                    score.reasoning.append("Multiple cloud providers detected")
            
            # Set confidence
            score.confidence = min(100.0, score.score * 1.1)
            scores.append(score)
        
        return scores
    
    def _score_tier3_agents(self, context: ProjectContext, user_request: Optional[str] = None) -> List[AgentScore]:
        """Score Tier 3 (specialist/niche) agents"""
        scores = []
        request_text = (user_request or '').lower()
        
        for agent_name in self.AGENT_TIERS[3]:
            score = AgentScore(
                agent_name=agent_name,
                score=0.0,
                tier=3,
                confidence=0.0,
                reasoning=[]
            )
            
            # Functional programmer scoring
            if agent_name == 'functional-programmer':
                fp_keywords = ['functional', 'haskell', 'clojure', 'f#', 'scala', 'erlang', 
                             'elixir', 'monad', 'immutable']
                if any(keyword in request_text for keyword in fp_keywords):
                    score.score += 90
                    score.reasoning.append("Functional programming keywords in request")
                
                fp_languages = ['haskell', 'clojure', 'scala']
                if any(lang in context.tech_stack.languages for lang in fp_languages):
                    score.score += 80
                    score.reasoning.append("Functional programming languages detected")
            
            # Metaprogramming specialist scoring
            elif agent_name == 'metaprogramming-specialist':
                meta_keywords = ['lisp', 'macro', 'dsl', 'metaprogramming', 'code generation']
                if any(keyword in request_text for keyword in meta_keywords):
                    score.score += 90
                    score.reasoning.append("Metaprogramming keywords in request")
            
            # Elisp specialist scoring
            elif agent_name == 'elisp-specialist':
                elisp_keywords = ['emacs', 'elisp', 'emacs lisp', 'init.el', 'doom emacs']
                if any(keyword in request_text for keyword in elisp_keywords):
                    score.score += 95
                    score.reasoning.append("Emacs/Elisp keywords in request")
            
            # Creative agents scoring
            elif agent_name in ['digital-artist', 'tv-writer', 'video-director', '3d-modeler', 
                              'comedy-writer', 'audio-engineer']:
                creative_mapping = {
                    'digital-artist': ['design', 'art', 'graphics', 'visual', 'ui', 'ux'],
                    'tv-writer': ['writing', 'documentation', 'content', 'copy'],
                    'video-director': ['video', 'multimedia', 'production', 'film'],
                    '3d-modeler': ['3d', 'modeling', 'visualization', 'render'],
                    'comedy-writer': ['comic', 'illustration', 'cartoon'],
                    'audio-engineer': ['audio', 'sound', 'music', 'podcast']
                }
                
                keywords = creative_mapping.get(agent_name, [])
                if any(keyword in request_text for keyword in keywords):
                    score.score += 85
                    score.reasoning.append(f"Creative keywords for {agent_name}: {keywords}")
            
            # Set confidence
            score.confidence = min(100.0, score.score * 0.9)  # Lower confidence for Tier 3
            scores.append(score)
        
        return scores
    
    def _determine_orchestration_pattern(self, context: ProjectContext, 
                                       user_request: Optional[str] = None,
                                       complexity: str = 'simple') -> str:
        """Determine the recommended orchestration pattern"""
        request_text = (user_request or '').lower()
        
        # New product development
        if any(keyword in request_text for keyword in ['new product', 'startup', 'mvp']):
            return 'new_product'
        
        # Technical decision making
        if any(keyword in request_text for keyword in ['decide', 'choose', 'which', 'should i']):
            return 'technical_decision'
        
        # Feature addition
        if any(keyword in request_text for keyword in ['add', 'feature', 'implement', 'build']):
            return 'feature_addition'
        
        # Specialized work (Tier 3 agents)
        specialized_keywords = ['functional', 'lisp', 'emacs', 'creative', 'art', 'design']
        if any(keyword in request_text for keyword in specialized_keywords):
            return 'specialized_work'
        
        # Default based on complexity
        if complexity == 'high' or context.complexity.file_count > 100:
            return 'new_product'  # Use full orchestration for complex projects
        else:
            return 'simple_app'  # Simple pattern for straightforward projects


def main():
    """CLI entry point for agent recommendations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Get agent recommendations for a project')
    parser.add_argument('path', help='Path to project directory')
    parser.add_argument('--request', help='User request description')
    parser.add_argument('--agents-dir', default='../agents', help='Path to agents directory')
    parser.add_argument('--output', choices=['json', 'summary'], default='summary', help='Output format')
    parser.add_argument('--tier', type=int, choices=[1, 2, 3], help='Show only specific tier')
    
    args = parser.parse_args()
    
    # Initialize recommender
    recommender = AgentRecommender(args.agents_dir)
    
    try:
        # Get recommendations
        recommendation = recommender.recommend_agents(args.path, args.request)
        
        if args.output == 'json':
            print(json.dumps(asdict(recommendation), indent=2))
        else:
            # Print summary
            print(f"Agent Recommendations for: {recommendation.project_path}")
            print(f"Risk Level: {recommendation.risk_level.upper()}")
            print(f"Estimated Complexity: {recommendation.estimated_complexity.upper()}")
            print(f"Orchestration Pattern: {recommendation.orchestration_pattern}")
            
            if not args.tier or args.tier == 1:
                print("\n=== TIER 1: Primary Agents (Always Visible) ===")
                for agent in recommendation.primary_agents:
                    required = " (REQUIRED)" if agent.required else ""
                    print(f"• {agent.agent_name}: {agent.score:.1f}/100{required}")
                    for reason in agent.reasoning[:2]:  # Show top 2 reasons
                        print(f"  - {reason}")
            
            if not args.tier or args.tier == 2:
                print("\n=== TIER 2: Context-Triggered Agents ===")
                if recommendation.context_agents:
                    for agent in recommendation.context_agents:
                        print(f"• {agent.agent_name}: {agent.score:.1f}/100")
                        for reason in agent.reasoning[:2]:
                            print(f"  - {reason}")
                else:
                    print("No context-triggered agents recommended")
            
            if not args.tier or args.tier == 3:
                print("\n=== TIER 3: Specialist Agents (On Request) ===")
                if recommendation.specialist_agents:
                    for agent in recommendation.specialist_agents:
                        print(f"• {agent.agent_name}: {agent.score:.1f}/100")
                        for reason in agent.reasoning[:2]:
                            print(f"  - {reason}")
                else:
                    print("No specialist agents recommended")
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())