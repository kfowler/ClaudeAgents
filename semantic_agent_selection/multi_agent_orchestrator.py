"""
Multi-Agent Recommendation Engine

This module provides intelligent recommendations for optimal agent combinations
and workflow orchestration for complex tasks.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

# Database imports
import asyncpg

# Local imports
from .request_analyzer import RequestAnalysis, IntentCategory, ComplexityLevel, RiskLevel, ProjectContext
from .vector_search import SearchResult


logger = logging.getLogger(__name__)


class WorkflowPattern(Enum):
    """Common workflow patterns for agent orchestration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ITERATIVE = "iterative"
    VALIDATION = "validation"


@dataclass
class AgentRole:
    """Role definition for an agent in a workflow."""
    agent_name: str
    role_type: str  # primary, supporting, validator, coordinator
    priority: int   # execution priority (lower = earlier)
    dependencies: List[str] = field(default_factory=list)  # agents this depends on
    parallel_group: Optional[str] = None  # agents that can run in parallel
    confidence_score: float = 0.0
    rationale: str = ""


@dataclass
class WorkflowRecommendation:
    """Complete workflow recommendation with agent orchestration."""
    primary_agents: List[AgentRole]
    supporting_agents: List[AgentRole]
    validation_agents: List[AgentRole]
    workflow_pattern: WorkflowPattern
    estimated_duration: Optional[timedelta] = None
    confidence_score: float = 0.0
    explanation: str = ""
    risk_mitigation: List[str] = field(default_factory=list)
    success_probability: float = 0.0
    
    @property
    def all_agents(self) -> List[AgentRole]:
        """Get all agents in the workflow."""
        return self.primary_agents + self.supporting_agents + self.validation_agents
    
    @property
    def agent_names(self) -> List[str]:
        """Get list of all agent names."""
        return [agent.agent_name for agent in self.all_agents]


@dataclass
class AgentCombinationPattern:
    """Historical pattern of successful agent combinations."""
    agents: List[str]
    success_rate: float
    usage_count: int
    context_patterns: Dict[str, Any]
    average_duration: Optional[timedelta] = None
    last_used: datetime = field(default_factory=datetime.now)
    
    def matches_context(self, analysis: RequestAnalysis) -> float:
        """Calculate how well this pattern matches the current context."""
        match_factors = []
        
        # Intent matching
        if 'intent_category' in self.context_patterns:
            if self.context_patterns['intent_category'] == analysis.intent_category.value:
                match_factors.append(0.8)
            else:
                match_factors.append(0.2)
        
        # Complexity matching
        if 'complexity_level' in self.context_patterns:
            if self.context_patterns['complexity_level'] == analysis.complexity_level.value:
                match_factors.append(0.7)
            else:
                match_factors.append(0.3)
        
        # Technology matching
        if 'technologies' in self.context_patterns and analysis.technical_keywords:
            pattern_techs = set(self.context_patterns['technologies'])
            request_techs = set(analysis.technical_keywords)
            overlap = len(pattern_techs & request_techs) / max(len(pattern_techs | request_techs), 1)
            match_factors.append(overlap)
        
        # Project context matching
        if analysis.project_context and 'project_characteristics' in self.context_patterns:
            project_chars = self.context_patterns['project_characteristics']
            context_matches = []
            
            if 'has_ai_features' in project_chars:
                context_matches.append(project_chars['has_ai_features'] == analysis.project_context.has_ai_features)
            if 'has_web_component' in project_chars:
                context_matches.append(project_chars['has_web_component'] == analysis.project_context.has_web_component)
            if 'has_mobile_component' in project_chars:
                context_matches.append(project_chars['has_mobile_component'] == analysis.project_context.has_mobile_component)
            if 'is_production' in project_chars:
                context_matches.append(project_chars['is_production'] == analysis.project_context.is_production)
            
            if context_matches:
                match_factors.append(sum(context_matches) / len(context_matches))
        
        # Calculate weighted average
        if not match_factors:
            return 0.5  # Neutral if no patterns to match
        
        return sum(match_factors) / len(match_factors)


class AgentCompatibilityMatrix:
    """Track agent compatibility and synergy patterns."""
    
    def __init__(self):
        self.compatibility_scores = {}
        self.synergy_bonuses = {}
        self.conflict_penalties = {}
        
    def load_default_rules(self):
        """Load default compatibility and synergy rules."""
        # High synergy combinations
        self.synergy_bonuses.update({
            ('full-stack-architect', 'security-audit-specialist'): 0.2,
            ('full-stack-architect', 'qa-test-engineer'): 0.15,
            ('mobile-developer', 'full-stack-architect'): 0.1,  # For backend API
            ('ai-ml-engineer', 'data-engineer'): 0.25,
            ('ai-ml-engineer', 'full-stack-architect'): 0.15,
            ('devops-engineer', 'security-audit-specialist'): 0.2,
            ('devops-engineer', 'systems-engineer'): 0.15,
            ('project-orchestrator', 'any'): 0.1,  # Project orchestrator helps all
            ('code-architect', 'systems-engineer'): 0.15,
            ('accessibility-expert', 'full-stack-architect'): 0.1,
            ('accessibility-expert', 'mobile-developer'): 0.1,
            ('the-critic', 'code-architect'): 0.1,
            ('product-strategist', 'project-orchestrator'): 0.15,
        })
        
        # Conflict penalties (overlapping roles)
        self.conflict_penalties.update({
            ('full-stack-architect', 'mobile-developer'): 0.05,  # Only if doing both web and mobile
            ('functional-programmer', 'systems-engineer'): 0.1,  # Different paradigms
            ('metaprogramming-specialist', 'functional-programmer'): 0.05,  # Could overlap
        })
        
        # Basic compatibility (0.0 to 1.0 scale)
        # Tier 1 agents are highly compatible
        tier_1_agents = ['full-stack-architect', 'mobile-developer', 'project-orchestrator', 
                        'security-audit-specialist', 'qa-test-engineer']
        
        for agent1 in tier_1_agents:
            for agent2 in tier_1_agents:
                if agent1 != agent2:
                    self.compatibility_scores[(agent1, agent2)] = 0.8
    
    def get_compatibility_score(self, agent1: str, agent2: str) -> float:
        """Get compatibility score between two agents."""
        pair = tuple(sorted([agent1, agent2]))
        
        # Check for explicit compatibility scores
        if pair in self.compatibility_scores:
            return self.compatibility_scores[pair]
        
        # Check for synergy bonuses
        synergy = 0.0
        for (a1, a2), bonus in self.synergy_bonuses.items():
            if (a1 == agent1 and a2 == agent2) or (a1 == agent2 and a2 == agent1) or a2 == 'any':
                synergy += bonus
        
        # Check for conflict penalties
        penalty = 0.0
        for (a1, a2), pen in self.conflict_penalties.items():
            if (a1 == agent1 and a2 == agent2) or (a1 == agent2 and a2 == agent1):
                penalty += pen
        
        # Base compatibility
        base_score = 0.6  # Neutral compatibility
        
        return max(0.0, min(1.0, base_score + synergy - penalty))
    
    def calculate_team_harmony(self, agents: List[str]) -> float:
        """Calculate overall team harmony score."""
        if len(agents) <= 1:
            return 1.0
        
        total_pairs = 0
        total_score = 0.0
        
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                score = self.get_compatibility_score(agent1, agent2)
                total_score += score
                total_pairs += 1
        
        return total_score / total_pairs if total_pairs > 0 else 1.0


class MultiAgentOrchestrator:
    """Orchestrate multiple agents for complex tasks."""
    
    # Mandatory agents based on risk level and context
    MANDATORY_AGENTS = {
        RiskLevel.CRITICAL: ['security-audit-specialist', 'qa-test-engineer', 'accessibility-expert'],
        RiskLevel.HIGH: ['security-audit-specialist', 'qa-test-engineer'],
        RiskLevel.MEDIUM: ['security-audit-specialist'],  # At least security for medium risk
    }
    
    # Complexity-based agent requirements
    COMPLEXITY_REQUIREMENTS = {
        ComplexityLevel.VERY_COMPLEX: {'coordinator': True, 'min_agents': 3},
        ComplexityLevel.COMPLEX: {'coordinator': True, 'min_agents': 2},
        ComplexityLevel.MODERATE: {'coordinator': False, 'min_agents': 1},
        ComplexityLevel.SIMPLE: {'coordinator': False, 'min_agents': 1},
    }
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.db_pool = None
        self.compatibility_matrix = AgentCompatibilityMatrix()
        self.historical_patterns = {}
        
    async def initialize(self):
        """Initialize the orchestrator."""
        # Initialize database connection
        self.db_pool = await asyncpg.create_pool(
            self.db_url,
            min_size=2,
            max_size=10,
            command_timeout=30
        )
        
        # Load compatibility rules
        self.compatibility_matrix.load_default_rules()
        
        # Load historical patterns
        await self._load_historical_patterns()
        
        logger.info("Multi-agent orchestrator initialized")
    
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()
    
    async def recommend_workflow(self, 
                               analysis: RequestAnalysis,
                               candidate_agents: List[SearchResult],
                               max_agents: int = 5) -> WorkflowRecommendation:
        """Recommend optimal agent workflow for the given request."""
        try:
            # Determine mandatory agents based on risk and complexity
            mandatory_agents = self._get_mandatory_agents(analysis)
            
            # Find best historical pattern
            best_pattern = self._find_best_historical_pattern(analysis)
            
            # Select optimal agent combination
            selected_agents = await self._select_optimal_combination(
                analysis, candidate_agents, mandatory_agents, best_pattern, max_agents
            )
            
            # Assign roles and priorities
            agent_roles = self._assign_agent_roles(selected_agents, analysis)
            
            # Determine workflow pattern
            workflow_pattern = self._determine_workflow_pattern(agent_roles, analysis)
            
            # Calculate confidence and success probability
            confidence_score = self._calculate_workflow_confidence(agent_roles, analysis)
            success_probability = self._predict_success_probability(agent_roles, analysis)
            
            # Generate explanation
            explanation = self._generate_workflow_explanation(agent_roles, analysis, workflow_pattern)
            
            # Identify risk mitigation strategies
            risk_mitigation = self._identify_risk_mitigation(agent_roles, analysis)
            
            # Estimate duration
            estimated_duration = self._estimate_workflow_duration(agent_roles, analysis)
            
            # Separate agents by role type
            primary_agents = [role for role in agent_roles if role.role_type == 'primary']
            supporting_agents = [role for role in agent_roles if role.role_type == 'supporting']
            validation_agents = [role for role in agent_roles if role.role_type == 'validator']
            
            return WorkflowRecommendation(
                primary_agents=primary_agents,
                supporting_agents=supporting_agents,
                validation_agents=validation_agents,
                workflow_pattern=workflow_pattern,
                estimated_duration=estimated_duration,
                confidence_score=confidence_score,
                explanation=explanation,
                risk_mitigation=risk_mitigation,
                success_probability=success_probability
            )
            
        except Exception as e:
            logger.error(f"Error recommending workflow: {e}")
            raise
    
    def _get_mandatory_agents(self, analysis: RequestAnalysis) -> Set[str]:
        """Get mandatory agents based on risk level and context."""
        mandatory = set()
        
        # Risk-based mandatory agents
        if analysis.risk_level in self.MANDATORY_AGENTS:
            mandatory.update(self.MANDATORY_AGENTS[analysis.risk_level])
        
        # Context-based mandatory agents
        if analysis.project_context:
            # Production systems need security and testing
            if analysis.project_context.is_production:
                mandatory.add('security-audit-specialist')
                mandatory.add('qa-test-engineer')
            
            # Public-facing applications need accessibility
            if analysis.project_context.has_web_component:
                mandatory.add('accessibility-expert')
        
        # Intent-based mandatory agents
        if analysis.intent_category == IntentCategory.NEW_PROJECT:
            mandatory.add('project-orchestrator')
        elif analysis.intent_category == IntentCategory.TESTING:
            mandatory.add('qa-test-engineer')
        elif analysis.intent_category == IntentCategory.DEPLOYMENT:
            mandatory.add('devops-engineer')
        
        # Complexity-based requirements
        complexity_req = self.COMPLEXITY_REQUIREMENTS.get(analysis.complexity_level, {})
        if complexity_req.get('coordinator', False):
            mandatory.add('project-orchestrator')
        
        return mandatory
    
    def _find_best_historical_pattern(self, analysis: RequestAnalysis) -> Optional[AgentCombinationPattern]:
        """Find the best matching historical pattern."""
        if not self.historical_patterns:
            return None
        
        best_pattern = None
        best_score = 0.0
        
        for pattern in self.historical_patterns.values():
            match_score = pattern.matches_context(analysis)
            # Weight by success rate and usage count
            weighted_score = match_score * pattern.success_rate * min(1.0, pattern.usage_count / 10)
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_pattern = pattern
        
        # Only return if score is above threshold
        return best_pattern if best_score > 0.6 else None
    
    async def _select_optimal_combination(self, 
                                        analysis: RequestAnalysis,
                                        candidates: List[SearchResult],
                                        mandatory: Set[str],
                                        best_pattern: Optional[AgentCombinationPattern],
                                        max_agents: int) -> List[SearchResult]:
        """Select optimal combination of agents."""
        selected = {}
        
        # Add mandatory agents first
        for candidate in candidates:
            if candidate.agent_name in mandatory:
                selected[candidate.agent_name] = candidate
        
        # If we have a good historical pattern, prioritize those agents
        if best_pattern:
            for agent_name in best_pattern.agents:
                if agent_name not in selected and len(selected) < max_agents:
                    # Find this agent in candidates
                    for candidate in candidates:
                        if candidate.agent_name == agent_name:
                            selected[agent_name] = candidate
                            break
        
        # Fill remaining slots with highest-scoring candidates
        remaining_candidates = [c for c in candidates if c.agent_name not in selected]
        remaining_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        
        for candidate in remaining_candidates:
            if len(selected) >= max_agents:
                break
            
            # Check team harmony
            current_agents = list(selected.keys())
            team_harmony = self.compatibility_matrix.calculate_team_harmony(current_agents + [candidate.agent_name])
            
            # Only add if it doesn't hurt team harmony too much
            if team_harmony > 0.5:
                selected[candidate.agent_name] = candidate
        
        # Ensure minimum agents for complexity level
        min_agents = self.COMPLEXITY_REQUIREMENTS.get(analysis.complexity_level, {}).get('min_agents', 1)
        if len(selected) < min_agents and remaining_candidates:
            # Add more agents even if harmony is lower
            for candidate in remaining_candidates:
                if len(selected) >= min_agents:
                    break
                if candidate.agent_name not in selected:
                    selected[candidate.agent_name] = candidate
        
        return list(selected.values())
    
    def _assign_agent_roles(self, agents: List[SearchResult], analysis: RequestAnalysis) -> List[AgentRole]:
        """Assign roles and priorities to selected agents."""
        roles = []
        
        # Define role assignment logic
        primary_agents = set()
        supporting_agents = set()
        validator_agents = set()
        coordinator_agents = set()
        
        # Intent-based primary agents
        if analysis.intent_category == IntentCategory.NEW_PROJECT:
            if analysis.project_context and analysis.project_context.has_web_component:
                primary_agents.add('full-stack-architect')
            elif analysis.project_context and analysis.project_context.has_mobile_component:
                primary_agents.add('mobile-developer')
        
        # Technology-based primary agents
        for agent in agents:
            agent_name = agent.agent_name
            
            # Primary role assignments
            if agent_name in ['full-stack-architect', 'mobile-developer', 'ai-ml-engineer'] and \
               agent.similarity_score > 0.7:
                primary_agents.add(agent_name)
            
            # Supporting role assignments
            elif agent_name in ['data-engineer', 'devops-engineer', 'systems-engineer', 'code-architect']:
                supporting_agents.add(agent_name)
            
            # Validator role assignments
            elif agent_name in ['security-audit-specialist', 'qa-test-engineer', 'accessibility-expert', 'the-critic']:
                validator_agents.add(agent_name)
            
            # Coordinator role
            elif agent_name == 'project-orchestrator':
                coordinator_agents.add(agent_name)
        
        # Create agent roles
        priority = 0
        
        # Coordinators first
        for agent in agents:
            if agent.agent_name in coordinator_agents:
                roles.append(AgentRole(
                    agent_name=agent.agent_name,
                    role_type='coordinator',
                    priority=priority,
                    confidence_score=agent.similarity_score,
                    rationale="Orchestrates complex multi-agent workflows"
                ))
                priority += 1
        
        # Primary agents next
        for agent in agents:
            if agent.agent_name in primary_agents:
                roles.append(AgentRole(
                    agent_name=agent.agent_name,
                    role_type='primary',
                    priority=priority,
                    confidence_score=agent.similarity_score,
                    rationale="Core implementation specialist"
                ))
                priority += 1
        
        # Supporting agents
        for agent in agents:
            if agent.agent_name in supporting_agents:
                roles.append(AgentRole(
                    agent_name=agent.agent_name,
                    role_type='supporting',
                    priority=priority,
                    confidence_score=agent.similarity_score,
                    rationale="Specialized domain expert"
                ))
                priority += 1
        
        # Validators last
        for agent in agents:
            if agent.agent_name in validator_agents:
                dependencies = []
                # Validators depend on implementation agents
                if primary_agents:
                    dependencies.extend(list(primary_agents))
                if supporting_agents:
                    dependencies.extend(list(supporting_agents))
                
                roles.append(AgentRole(
                    agent_name=agent.agent_name,
                    role_type='validator',
                    priority=priority,
                    dependencies=dependencies,
                    confidence_score=agent.similarity_score,
                    rationale="Quality assurance and validation"
                ))
                priority += 1
        
        return roles
    
    def _determine_workflow_pattern(self, roles: List[AgentRole], analysis: RequestAnalysis) -> WorkflowPattern:
        """Determine the optimal workflow pattern."""
        # Simple projects: sequential
        if analysis.complexity_level == ComplexityLevel.SIMPLE and len(roles) <= 2:
            return WorkflowPattern.SEQUENTIAL
        
        # Complex projects with validators: validation pattern
        validators = [r for r in roles if r.role_type == 'validator']
        if validators and analysis.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return WorkflowPattern.VALIDATION
        
        # Projects with coordinator: hierarchical
        coordinators = [r for r in roles if r.role_type == 'coordinator']
        if coordinators:
            return WorkflowPattern.HIERARCHICAL
        
        # Multiple independent agents: parallel
        primary_agents = [r for r in roles if r.role_type == 'primary']
        if len(primary_agents) > 1:
            return WorkflowPattern.PARALLEL
        
        # Default: sequential
        return WorkflowPattern.SEQUENTIAL
    
    def _calculate_workflow_confidence(self, roles: List[AgentRole], analysis: RequestAnalysis) -> float:
        """Calculate confidence in the workflow recommendation."""
        confidence_factors = []
        
        # Average agent confidence
        if roles:
            avg_agent_confidence = sum(role.confidence_score for role in roles) / len(roles)
            confidence_factors.append(avg_agent_confidence)
        
        # Team harmony
        agent_names = [role.agent_name for role in roles]
        team_harmony = self.compatibility_matrix.calculate_team_harmony(agent_names)
        confidence_factors.append(team_harmony)
        
        # Mandatory agent coverage
        mandatory = self._get_mandatory_agents(analysis)
        coverage = len(mandatory & set(agent_names)) / max(len(mandatory), 1)
        confidence_factors.append(coverage)
        
        # Complexity alignment
        complexity_req = self.COMPLEXITY_REQUIREMENTS.get(analysis.complexity_level, {})
        min_agents = complexity_req.get('min_agents', 1)
        agent_adequacy = min(1.0, len(roles) / min_agents)
        confidence_factors.append(agent_adequacy)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _predict_success_probability(self, roles: List[AgentRole], analysis: RequestAnalysis) -> float:
        """Predict the probability of workflow success."""
        success_factors = []
        
        # Base success probability by complexity
        base_probs = {
            ComplexityLevel.SIMPLE: 0.9,
            ComplexityLevel.MODERATE: 0.8,
            ComplexityLevel.COMPLEX: 0.7,
            ComplexityLevel.VERY_COMPLEX: 0.6
        }
        success_factors.append(base_probs.get(analysis.complexity_level, 0.7))
        
        # Agent quality factor
        if roles:
            avg_quality = sum(role.confidence_score for role in roles) / len(roles)
            success_factors.append(avg_quality)
        
        # Risk mitigation factor
        mandatory = self._get_mandatory_agents(analysis)
        agent_names = [role.agent_name for role in roles]
        risk_coverage = len(mandatory & set(agent_names)) / max(len(mandatory), 1)
        success_factors.append(risk_coverage)
        
        # Team synergy factor
        team_harmony = self.compatibility_matrix.calculate_team_harmony(agent_names)
        success_factors.append(team_harmony)
        
        return sum(success_factors) / len(success_factors)
    
    def _generate_workflow_explanation(self, 
                                     roles: List[AgentRole],
                                     analysis: RequestAnalysis,
                                     pattern: WorkflowPattern) -> str:
        """Generate explanation for the workflow recommendation."""
        explanations = []
        
        # Overall strategy
        strategy_explanations = {
            WorkflowPattern.SEQUENTIAL: "Sequential workflow for straightforward execution",
            WorkflowPattern.PARALLEL: "Parallel workflow for efficient concurrent development", 
            WorkflowPattern.HIERARCHICAL: "Hierarchical workflow with coordination and oversight",
            WorkflowPattern.VALIDATION: "Validation-focused workflow ensuring quality and security",
            WorkflowPattern.ITERATIVE: "Iterative workflow for continuous improvement"
        }
        
        explanations.append(strategy_explanations.get(pattern, "Custom workflow"))
        
        # Agent selection rationale
        primary_agents = [r for r in roles if r.role_type == 'primary']
        if primary_agents:
            agent_names = [r.agent_name for r in primary_agents]
            explanations.append(f"Primary implementation by {', '.join(agent_names)}")
        
        # Risk mitigation
        validators = [r for r in roles if r.role_type == 'validator']
        if validators:
            explanations.append(f"Quality assured by {len(validators)} validation agents")
        
        # Complexity handling
        if analysis.complexity_level in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]:
            coordinators = [r for r in roles if r.role_type == 'coordinator']
            if coordinators:
                explanations.append("Coordinated approach for complex requirements")
        
        # Technology alignment
        if analysis.technical_keywords:
            explanations.append(f"Optimized for {len(analysis.technical_keywords)} specified technologies")
        
        return "; ".join(explanations)
    
    def _identify_risk_mitigation(self, roles: List[AgentRole], analysis: RequestAnalysis) -> List[str]:
        """Identify risk mitigation strategies in the workflow."""
        mitigations = []
        
        agent_names = [role.agent_name for role in roles]
        
        # Security mitigation
        if 'security-audit-specialist' in agent_names:
            mitigations.append("Security vulnerabilities will be identified and addressed")
        
        # Quality mitigation
        if 'qa-test-engineer' in agent_names:
            mitigations.append("Comprehensive testing ensures reliability")
        
        # Accessibility mitigation
        if 'accessibility-expert' in agent_names:
            mitigations.append("Accessibility compliance reduces legal and usability risks")
        
        # Coordination mitigation
        if 'project-orchestrator' in agent_names:
            mitigations.append("Project coordination prevents scope creep and delays")
        
        # Technical review mitigation
        if 'code-architect' in agent_names:
            mitigations.append("Code architecture review prevents technical debt")
        
        # Decision validation
        if 'the-critic' in agent_names:
            mitigations.append("Technical decisions will be critically evaluated")
        
        return mitigations
    
    def _estimate_workflow_duration(self, roles: List[AgentRole], analysis: RequestAnalysis) -> timedelta:
        """Estimate workflow duration based on complexity and agents."""
        # Base duration by complexity
        base_durations = {
            ComplexityLevel.SIMPLE: timedelta(days=2),
            ComplexityLevel.MODERATE: timedelta(days=5),
            ComplexityLevel.COMPLEX: timedelta(days=14),
            ComplexityLevel.VERY_COMPLEX: timedelta(days=30)
        }
        
        base_duration = base_durations.get(analysis.complexity_level, timedelta(days=7))
        
        # Adjust for number of agents (more agents can parallelize but add coordination)
        agent_factor = 1.0
        if len(roles) > 3:
            agent_factor = 0.8 + (len(roles) - 3) * 0.1  # Diminishing returns
        
        # Adjust for validation requirements
        validators = [r for r in roles if r.role_type == 'validator']
        if len(validators) > 1:
            agent_factor *= 1.2  # Additional time for thorough validation
        
        return timedelta(seconds=int(base_duration.total_seconds() * agent_factor))
    
    async def _load_historical_patterns(self):
        """Load historical agent combination patterns from database."""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT combination_hash, agents, success_rate, usage_count,
                           context_patterns, average_duration, last_used
                    FROM agent_combinations
                    WHERE usage_count >= 3 AND success_rate >= 0.6
                    ORDER BY success_rate DESC, usage_count DESC
                    LIMIT 100
                """)
            
            for row in rows:
                pattern = AgentCombinationPattern(
                    agents=row['agents'],
                    success_rate=float(row['success_rate']),
                    usage_count=int(row['usage_count']),
                    context_patterns=row['context_patterns'],
                    average_duration=row['average_duration'],
                    last_used=row['last_used']
                )
                
                self.historical_patterns[row['combination_hash']] = pattern
            
            logger.info(f"Loaded {len(self.historical_patterns)} historical patterns")
            
        except Exception as e:
            logger.error(f"Error loading historical patterns: {e}")
    
    async def record_workflow_outcome(self, 
                                    workflow: WorkflowRecommendation,
                                    analysis: RequestAnalysis,
                                    success: bool,
                                    actual_duration: Optional[timedelta] = None,
                                    user_feedback: Optional[Dict[str, Any]] = None):
        """Record workflow outcome for learning."""
        if not self.db_pool:
            return
        
        try:
            # Create combination hash
            agents_sorted = sorted(workflow.agent_names)
            combination_hash = hash(tuple(agents_sorted))
            
            # Prepare context patterns
            context_patterns = {
                'intent_category': analysis.intent_category.value,
                'complexity_level': analysis.complexity_level.value,
                'risk_level': analysis.risk_level.value,
                'technologies': analysis.technical_keywords
            }
            
            if analysis.project_context:
                context_patterns['project_characteristics'] = {
                    'has_ai_features': analysis.project_context.has_ai_features,
                    'has_web_component': analysis.project_context.has_web_component,
                    'has_mobile_component': analysis.project_context.has_mobile_component,
                    'is_production': analysis.project_context.is_production
                }
            
            # Update database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO agent_combinations 
                    (combination_hash, agents, success_rate, usage_count, context_patterns, 
                     average_duration, last_used)
                    VALUES ($1, $2, $3, 1, $4, $5, NOW())
                    ON CONFLICT (combination_hash)
                    DO UPDATE SET
                        success_rate = (
                            (agent_combinations.success_rate * agent_combinations.usage_count + $3) / 
                            (agent_combinations.usage_count + 1)
                        ),
                        usage_count = agent_combinations.usage_count + 1,
                        average_duration = CASE 
                            WHEN $5 IS NOT NULL THEN (
                                (COALESCE(agent_combinations.average_duration, INTERVAL '0') * agent_combinations.usage_count + $5) /
                                (agent_combinations.usage_count + 1)
                            )
                            ELSE agent_combinations.average_duration
                        END,
                        last_used = NOW()
                """, 
                    str(combination_hash),
                    agents_sorted,
                    1.0 if success else 0.0,
                    json.dumps(context_patterns),
                    actual_duration
                )
            
            logger.info(f"Recorded workflow outcome: {agents_sorted}, success: {success}")
            
        except Exception as e:
            logger.error(f"Error recording workflow outcome: {e}")


# CLI and utility functions
async def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-agent workflow orchestrator")
    parser.add_argument("--db-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--load-patterns", action='store_true', 
                       help="Load and display historical patterns")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(args.db_url)
    
    try:
        await orchestrator.initialize()
        
        if args.load_patterns:
            print(f"✓ Loaded {len(orchestrator.historical_patterns)} historical patterns")
            for i, (hash_key, pattern) in enumerate(list(orchestrator.historical_patterns.items())[:10]):
                print(f"  {i+1}. {pattern.agents} - Success: {pattern.success_rate:.2f}, Usage: {pattern.usage_count}")
        else:
            print("✓ Multi-agent orchestrator initialized successfully")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await orchestrator.close()


if __name__ == "__main__":
    asyncio.run(main())