"""
Integration module for Claude Code Agent Selection System

Provides seamless integration with the existing agent decision tree and
selection framework defined in AGENT_DECISION_TREE.md
"""

import os
import re
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .project_analyzer import ProjectAnalyzer, ProjectContext
from .agent_recommender import AgentRecommender, AgentRecommendation


class DecisionTreeIntegrator:
    """
    Integrates project analysis with the AGENT_DECISION_TREE.md system.
    
    Provides compatibility with existing agent selection patterns while
    enhancing them with automated project context analysis.
    """
    
    def __init__(self, agents_dir: str, decision_tree_path: Optional[str] = None):
        self.agents_dir = agents_dir
        self.decision_tree_path = decision_tree_path
        self.analyzer = ProjectAnalyzer()
        self.recommender = AgentRecommender(agents_dir, decision_tree_path)
        
        # Load decision tree patterns if available
        self.decision_patterns = self._load_decision_patterns()
    
    def _load_decision_patterns(self) -> Dict[str, Any]:
        """Load decision patterns from AGENT_DECISION_TREE.md"""
        patterns = {
            'tier_1_keywords': {},
            'tier_2_keywords': {},
            'tier_3_keywords': {},
            'orchestration_patterns': {},
            'risk_indicators': {}
        }
        
        if not self.decision_tree_path or not os.path.exists(self.decision_tree_path):
            # Use default patterns if decision tree file not found
            return self._get_default_patterns()
        
        try:
            with open(self.decision_tree_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse keywords for each tier from markdown
            patterns['tier_1_keywords'] = self._extract_tier_keywords(content, 1)
            patterns['tier_2_keywords'] = self._extract_tier_keywords(content, 2)
            patterns['tier_3_keywords'] = self._extract_tier_keywords(content, 3)
            patterns['orchestration_patterns'] = self._extract_orchestration_patterns(content)
            patterns['risk_indicators'] = self._extract_risk_indicators(content)
            
        except Exception as e:
            print(f"Warning: Could not load decision tree patterns: {e}")
            return self._get_default_patterns()
        
        return patterns
    
    def _extract_tier_keywords(self, content: str, tier: int) -> Dict[str, List[str]]:
        """Extract keyword mappings for a specific tier from markdown content"""
        tier_section = f"TIER {tier}"
        keywords = {}
        
        # Find sections with keyword patterns
        keyword_patterns = re.findall(
            rf'\*\*(\w+(?:\s+\w+)*)\s+KEYWORDS:\*\*\s*\n`([^`]+)`\s*\n→\s*\*\*`([^`]+)`\*\*',
            content,
            re.IGNORECASE | re.MULTILINE
        )
        
        for category, keyword_list, agent in keyword_patterns:
            if agent not in keywords:
                keywords[agent] = []
            
            # Parse comma-separated keywords, removing backticks and extra spaces
            parsed_keywords = [
                kw.strip().strip('`') for kw in keyword_list.split(',')
            ]
            keywords[agent].extend(parsed_keywords)
        
        return keywords
    
    def _extract_orchestration_patterns(self, content: str) -> Dict[str, List[str]]:
        """Extract orchestration patterns from markdown content"""
        patterns = {}
        
        # Look for pattern definitions
        pattern_matches = re.findall(
            r'\*\*Pattern \d+: ([^*]+)\*\*\s*\n```\s*\n(.*?)\n```',
            content,
            re.DOTALL
        )
        
        for pattern_name, pattern_steps in pattern_matches:
            steps = [
                step.strip().lstrip('0123456789. ')
                for step in pattern_steps.split('\n')
                if step.strip() and not step.strip().startswith('#')
            ]
            patterns[pattern_name.strip()] = steps
        
        return patterns
    
    def _extract_risk_indicators(self, content: str) -> Dict[str, List[str]]:
        """Extract risk level indicators from markdown content"""
        risk_levels = {}
        
        # Look for risk pattern definitions
        risk_patterns = re.findall(
            r'\*\*([A-Z][a-z]+)\s+Risk[^:]*:\*\*\s*\n-\s*([^\n]+(?:\n-\s*[^\n]+)*)',
            content,
            re.MULTILINE
        )
        
        for risk_level, indicators_text in risk_patterns:
            indicators = [
                indicator.strip().lstrip('- ')
                for indicator in indicators_text.split('\n')
                if indicator.strip().startswith('-')
            ]
            risk_levels[risk_level.lower()] = indicators
        
        return risk_levels
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Fallback default patterns if decision tree is not available"""
        return {
            'tier_1_keywords': {
                'full-stack-architect': ['react', 'next.js', 'web app', 'frontend', 'backend', 'api'],
                'mobile-developer': ['ios', 'android', 'mobile', 'swift', 'kotlin', 'react native'],
                'project-orchestrator': ['complex project', 'coordinate', 'roadmap', 'timeline'],
                'security-audit-specialist': ['security', 'auth', 'vulnerability', 'production'],
                'qa-test-engineer': ['test', 'testing', 'qa', 'quality assurance']
            },
            'tier_2_keywords': {
                'ai-ml-engineer': ['ai', 'ml', 'machine learning', 'llm', 'neural network'],
                'data-engineer': ['database', 'analytics', 'data pipeline', 'etl'],
                'devops-engineer': ['docker', 'kubernetes', 'ci/cd', 'deployment'],
                'systems-engineer': ['performance', 'optimization', 'rust', 'c++', 'memory']
            },
            'tier_3_keywords': {
                'functional-programmer': ['haskell', 'functional programming', 'monad'],
                'elisp-specialist': ['emacs', 'elisp', 'emacs lisp']
            },
            'orchestration_patterns': {
                'simple_app': ['Implementation', 'Security review', 'Testing'],
                'new_product': ['Market research', 'Planning', 'Implementation', 'Security', 'Testing', 'Deployment']
            },
            'risk_indicators': {
                'critical': ['financial', 'healthcare', 'government', 'user data'],
                'high': ['production', 'public-facing', 'enterprise'],
                'medium': ['internal tool', 'api service'],
                'low': ['prototype', 'personal project']
            }
        }
    
    def get_context_aware_recommendations(self, project_path: str, 
                                        user_request: Optional[str] = None) -> Dict[str, Any]:
        """
        Get agent recommendations that combine automated analysis with decision tree logic.
        
        Returns enhanced recommendations that include:
        - Standard agent recommendations
        - Decision tree compliance
        - Context-aware tier visibility
        - Integration guidance
        """
        
        # Get base analysis and recommendations
        context = self.analyzer.analyze_project(project_path)
        recommendation = self.recommender.recommend_agents(project_path, user_request)
        
        # Apply decision tree integration
        integrated_recommendation = self._apply_decision_tree_logic(
            context, recommendation, user_request
        )
        
        # Add integration guidance
        integration_guidance = self._generate_integration_guidance(
            context, integrated_recommendation
        )
        
        return {
            'project_analysis': context,
            'agent_recommendation': integrated_recommendation,
            'integration_guidance': integration_guidance,
            'decision_tree_compliance': self._check_decision_tree_compliance(
                integrated_recommendation
            )
        }
    
    def _apply_decision_tree_logic(self, context: ProjectContext, 
                                 recommendation: AgentRecommendation,
                                 user_request: Optional[str] = None) -> AgentRecommendation:
        """Apply decision tree logic to refine recommendations"""
        
        # Ensure mandatory agents are marked as required
        mandatory_agents = self._get_mandatory_agents(context, user_request)
        
        for agent_score in recommendation.primary_agents:
            if agent_score.agent_name in mandatory_agents:
                agent_score.required = True
                agent_score.score = max(agent_score.score, 80)  # Boost required agents
        
        # Apply progressive disclosure rules
        recommendation = self._apply_progressive_disclosure(recommendation, context)
        
        # Adjust orchestration pattern based on decision tree
        recommendation.orchestration_pattern = self._select_orchestration_pattern(
            context, user_request, recommendation.estimated_complexity
        )
        
        return recommendation
    
    def _get_mandatory_agents(self, context: ProjectContext, 
                            user_request: Optional[str] = None) -> List[str]:
        """Determine mandatory agents based on project context and decision tree rules"""
        mandatory = []
        
        # Security audit specialist is mandatory for production systems
        if (context.architecture.domain_type in ['web_app', 'mobile_app', 'api_service'] or
            (user_request and any(keyword in user_request.lower() 
                                for keyword in ['production', 'deploy', 'release']))):
            mandatory.append('security-audit-specialist')
        
        # QA test engineer is mandatory for complex projects or when tests are missing
        if (not context.quality.has_tests or 
            context.complexity.file_count > 50 or
            context.architecture.domain_type in ['web_app', 'mobile_app']):
            mandatory.append('qa-test-engineer')
        
        # Project orchestrator for complex multi-component projects
        if (context.complexity.file_count > 100 or 
            len(context.tech_stack.languages) > 2 or
            'microservices' in context.architecture.patterns):
            mandatory.append('project-orchestrator')
        
        return mandatory
    
    def _apply_progressive_disclosure(self, recommendation: AgentRecommendation,
                                    context: ProjectContext) -> AgentRecommendation:
        """Apply progressive disclosure rules from the decision tree"""
        
        # Filter Tier 2 agents - only show those with score > threshold
        filtered_context_agents = [
            agent for agent in recommendation.context_agents 
            if agent.score >= 25  # Minimum threshold for context agents
        ]
        recommendation.context_agents = filtered_context_agents
        
        # Filter Tier 3 agents - only show those with high scores (explicit request)
        filtered_specialist_agents = [
            agent for agent in recommendation.specialist_agents
            if agent.score >= 70  # High threshold for specialists
        ]
        recommendation.specialist_agents = filtered_specialist_agents
        
        return recommendation
    
    def _select_orchestration_pattern(self, context: ProjectContext,
                                    user_request: Optional[str] = None,
                                    complexity: str = 'simple') -> str:
        """Select orchestration pattern based on decision tree logic"""
        
        request_text = (user_request or '').lower()
        
        # Map to decision tree patterns
        if any(keyword in request_text for keyword in ['new product', 'startup', 'mvp']):
            return 'new_product_development'
        elif any(keyword in request_text for keyword in ['decision', 'choose', 'evaluate']):
            return 'technical_decision'
        elif context.complexity.file_count > 200 or complexity == 'high':
            return 'complex_project_orchestration'
        elif any(keyword in request_text for keyword in ['feature', 'add', 'implement']):
            return 'feature_addition'
        else:
            return 'simple_application'
    
    def _generate_integration_guidance(self, context: ProjectContext,
                                     recommendation: AgentRecommendation) -> Dict[str, Any]:
        """Generate integration guidance for Claude Code"""
        
        return {
            'suggested_workflow': self._get_suggested_workflow(recommendation),
            'parallel_execution_opportunities': self._identify_parallel_opportunities(recommendation),
            'sequential_dependencies': self._identify_sequential_dependencies(recommendation),
            'integration_commands': self._suggest_integration_commands(context, recommendation),
            'quality_gates': self._define_quality_gates(context, recommendation)
        }
    
    def _get_suggested_workflow(self, recommendation: AgentRecommendation) -> List[str]:
        """Get suggested workflow steps"""
        workflow = []
        
        # Primary implementation agents
        primary_impl = [agent for agent in recommendation.primary_agents 
                       if agent.agent_name in ['full-stack-architect', 'mobile-developer']]
        if primary_impl:
            workflow.append(f"Implementation: {primary_impl[0].agent_name}")
        
        # Context-triggered specialists
        for agent in recommendation.context_agents:
            if agent.score >= 60:
                workflow.append(f"Specialist review: {agent.agent_name}")
        
        # Quality gates
        quality_agents = [agent for agent in recommendation.primary_agents 
                         if agent.agent_name in ['security-audit-specialist', 'qa-test-engineer']]
        for agent in quality_agents:
            workflow.append(f"Quality gate: {agent.agent_name}")
        
        return workflow
    
    def _identify_parallel_opportunities(self, recommendation: AgentRecommendation) -> List[List[str]]:
        """Identify agents that can work in parallel"""
        parallel_groups = []
        
        # Security, accessibility, and QA can often run in parallel
        quality_group = []
        for agent in recommendation.primary_agents + recommendation.context_agents:
            if agent.agent_name in ['security-audit-specialist', 'accessibility-expert', 'qa-test-engineer']:
                quality_group.append(agent.agent_name)
        
        if len(quality_group) > 1:
            parallel_groups.append(quality_group)
        
        return parallel_groups
    
    def _identify_sequential_dependencies(self, recommendation: AgentRecommendation) -> List[Tuple[str, str]]:
        """Identify sequential dependencies between agents"""
        dependencies = []
        
        # Implementation should come before review
        impl_agents = [agent.agent_name for agent in recommendation.primary_agents 
                      if agent.agent_name in ['full-stack-architect', 'mobile-developer']]
        review_agents = [agent.agent_name for agent in recommendation.primary_agents + recommendation.context_agents
                        if agent.agent_name in ['security-audit-specialist', 'qa-test-engineer', 'code-architect']]
        
        for impl_agent in impl_agents:
            for review_agent in review_agents:
                dependencies.append((impl_agent, review_agent))
        
        return dependencies
    
    def _suggest_integration_commands(self, context: ProjectContext,
                                    recommendation: AgentRecommendation) -> List[str]:
        """Suggest Claude Code integration commands"""
        commands = []
        
        # Suggest relevant existing commands based on project type
        if context.architecture.domain_type == 'web_app':
            if 'python' in context.tech_stack.languages:
                commands.append('python-web-api')
            if 'react' in context.tech_stack.frameworks:
                commands.append('refactor-component')
        
        if recommendation.risk_level in ['high', 'critical']:
            commands.extend(['security-audit', 'production-readiness'])
        
        if not context.quality.has_tests:
            commands.append('test-coverage')
        
        return commands
    
    def _define_quality_gates(self, context: ProjectContext,
                            recommendation: AgentRecommendation) -> Dict[str, List[str]]:
        """Define quality gates based on project context"""
        gates = {
            'pre_implementation': [],
            'pre_review': [],
            'pre_deployment': []
        }
        
        # Pre-implementation gates
        if context.complexity.file_count > 100:
            gates['pre_implementation'].append('Architecture review required')
        
        # Pre-review gates
        if not context.quality.has_tests:
            gates['pre_review'].append('Tests must be implemented')
        
        # Pre-deployment gates
        if recommendation.risk_level in ['high', 'critical']:
            gates['pre_deployment'].extend([
                'Security audit must pass',
                'Accessibility review required',
                'Performance testing completed'
            ])
        
        return gates
    
    def _check_decision_tree_compliance(self, recommendation: AgentRecommendation) -> Dict[str, Any]:
        """Check compliance with decision tree rules"""
        compliance = {
            'tier_1_coverage': 0,
            'mandatory_agents_included': True,
            'progressive_disclosure_applied': True,
            'warnings': []
        }
        
        # Check Tier 1 coverage
        tier_1_agents = ['full-stack-architect', 'mobile-developer', 'project-orchestrator',
                        'security-audit-specialist', 'qa-test-engineer']
        present_tier_1 = [agent.agent_name for agent in recommendation.primary_agents]
        compliance['tier_1_coverage'] = len(set(present_tier_1) & set(tier_1_agents)) / len(tier_1_agents)
        
        # Check for missing mandatory agents
        required_agents = [agent.agent_name for agent in recommendation.primary_agents if agent.required]
        if 'security-audit-specialist' not in required_agents and recommendation.risk_level in ['high', 'critical']:
            compliance['warnings'].append('Security audit specialist should be required for high/critical risk projects')
        
        return compliance


def create_integration_bridge(agents_dir: str, decision_tree_path: Optional[str] = None) -> DecisionTreeIntegrator:
    """
    Factory function to create a decision tree integrator.
    
    This provides the main integration point for Claude Code to use the
    project analysis system with the existing agent selection framework.
    """
    return DecisionTreeIntegrator(agents_dir, decision_tree_path)


def get_smart_agent_recommendations(project_path: str, user_request: Optional[str] = None,
                                  agents_dir: str = "./agents",
                                  decision_tree_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for getting smart agent recommendations.
    
    This is the primary integration function that Claude Code should use
    to get enhanced agent recommendations with full project context analysis.
    """
    integrator = create_integration_bridge(agents_dir, decision_tree_path)
    return integrator.get_context_aware_recommendations(project_path, user_request)