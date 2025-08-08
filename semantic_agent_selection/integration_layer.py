"""
Integration Layer for Semantic Agent Selection

This module provides seamless integration between the new semantic agent selection
system and the existing keyword-based decision tree, implementing hybrid approaches
and fallback mechanisms.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
import json
from datetime import datetime

# Local imports
from .request_analyzer import RequestAnalyzer, RequestAnalysis, IntentCategory, ComplexityLevel, RiskLevel, ProjectContext
from .vector_search import VectorSearchManager, SearchResult, SearchBackend
from .multi_agent_orchestrator import MultiAgentOrchestrator, WorkflowRecommendation
from .success_predictor import SuccessPredictor, PredictionResult


logger = logging.getLogger(__name__)


class SelectionStrategy(Enum):
    """Agent selection strategies."""
    SEMANTIC_ONLY = "semantic_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID_SEMANTIC_PRIMARY = "hybrid_semantic_primary"
    HYBRID_KEYWORD_PRIMARY = "hybrid_keyword_primary"
    ADAPTIVE = "adaptive"


@dataclass
class KeywordMatch:
    """Result from keyword-based agent matching."""
    agent_name: str
    match_score: float
    matching_keywords: List[str] = field(default_factory=list)
    tier: int = 1
    confidence: float = 0.0
    rationale: str = ""


@dataclass
class HybridRecommendation:
    """Hybrid recommendation combining semantic and keyword approaches."""
    agent_name: str
    semantic_score: float
    keyword_score: float
    combined_score: float
    confidence_score: float
    success_probability: float
    recommendation_source: str  # "semantic", "keyword", or "hybrid"
    explanation: str = ""
    risk_factors: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)


@dataclass
class EnhancedAgentSelection:
    """Enhanced agent selection result with comprehensive scoring."""
    primary_recommendation: WorkflowRecommendation
    alternative_recommendations: List[WorkflowRecommendation] = field(default_factory=list)
    selection_strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE
    confidence_level: str = "medium"  # low, medium, high
    processing_time: float = 0.0
    fallback_used: bool = False
    explanation: str = ""
    
    def get_all_agent_names(self) -> Set[str]:
        """Get all unique agent names across recommendations."""
        agents = set(self.primary_recommendation.agent_names)
        for alt in self.alternative_recommendations:
            agents.update(alt.agent_names)
        return agents


class KeywordAgentMatcher:
    """Enhanced keyword-based agent matching system."""
    
    def __init__(self):
        """Initialize with keyword patterns from decision tree."""
        # Load keyword patterns from the decision tree
        self.tier_1_patterns = self._load_tier_1_patterns()
        self.tier_2_patterns = self._load_tier_2_patterns()
        self.tier_3_patterns = self._load_tier_3_patterns()
        
        # Agent tier mapping
        self.agent_tiers = {
            # Tier 1 (Core agents)
            'full-stack-architect': 1,
            'mobile-developer': 1,
            'project-orchestrator': 1,
            'security-audit-specialist': 1,
            'qa-test-engineer': 1,
            
            # Tier 2 (Specialized agents)
            'ai-ml-engineer': 2,
            'data-engineer': 2,
            'devops-engineer': 2,
            'systems-engineer': 2,
            'code-architect': 2,
            'accessibility-expert': 2,
            'the-critic': 2,
            'product-strategist': 2,
            'legacy-specialist': 2,
            'platform-integrator': 2,
            
            # Tier 3 (Niche/creative agents)
            'functional-programmer': 3,
            'metaprogramming-specialist': 3,
            'elisp-specialist': 3,
            'artist': 3,
            'writer': 3,
            'ava-the-director': 3,
            'iris-the-modeler': 3,
            'milo-the-comic': 3,
            'echo-the-audio-engineer': 3
        }
    
    def _load_tier_1_patterns(self) -> Dict[str, List[str]]:
        """Load Tier 1 keyword patterns."""
        return {
            'full-stack-architect': [
                'react', 'next.js', 'svelte', 'sveltekit', 'vue', 'frontend', 'backend', 'api', 'web app',
                'typescript', 'javascript', 'node.js', 'express', 'fastapi', 'django', 'flask'
            ],
            'mobile-developer': [
                'ios', 'android', 'swift', 'kotlin', 'react native', 'flutter', 'mobile app', 'app store',
                'xamarin', 'objective-c', 'dart', 'mobile development'
            ],
            'project-orchestrator': [
                'coordinate', 'orchestrate', 'complex project', 'roadmap', 'timeline', 'multiple components',
                'project management', 'planning', 'architecture', 'coordination'
            ],
            'security-audit-specialist': [
                'security', 'vulnerability', 'auth', 'authentication', 'authorization', 'oauth', 'jwt',
                'encryption', 'https', 'penetration', 'audit', 'compliance', 'gdpr', 'hipaa'
            ],
            'qa-test-engineer': [
                'test', 'testing', 'qa', 'quality assurance', 'unit test', 'integration test',
                'e2e test', 'tdd', 'bdd', 'test coverage', 'cypress', 'jest', 'pytest'
            ]
        }
    
    def _load_tier_2_patterns(self) -> Dict[str, List[str]]:
        """Load Tier 2 keyword patterns."""
        return {
            'ai-ml-engineer': [
                'ai', 'ml', 'llm', 'chatgpt', 'claude', 'openai', 'anthropic', 'embeddings', 'vector',
                'rag', 'semantic search', 'recommendation', 'neural', 'model', 'training', 'inference',
                'transformer', 'fine-tuning', 'rlhf', 'agents', 'multimodal', 'computer vision',
                'nlp', 'mlops', 'pytorch', 'tensorflow', 'hugging face'
            ],
            'data-engineer': [
                'database', 'postgresql', 'mongodb', 'data pipeline', 'analytics', 'etl', 'data warehouse',
                'big data', 'spark', 'kafka', 'airflow', 'dbt', 'snowflake', 'redshift'
            ],
            'devops-engineer': [
                'deploy', 'ci/cd', 'docker', 'aws', 'cloud', 'infrastructure', 'devops', 'monitoring',
                'kubernetes', 'terraform', 'ansible', 'jenkins', 'github actions', 'azure', 'gcp'
            ],
            'systems-engineer': [
                'rust', 'c++', 'go', 'performance', 'optimization', 'concurrent', 'memory', 'systems',
                'unsafe', 'zero-copy', 'embedded', 'kernel', 'async', 'threading', 'low-level'
            ],
            'code-architect': [
                'code review', 'best practices', 'clean code', 'architecture', 'refactor', 'maintainability',
                'readability', 'clarity', 'design patterns', 'solid principles', 'technical debt'
            ],
            'accessibility-expert': [
                'accessibility', 'wcag', 'screen reader', 'inclusive', 'disability', 'a11y',
                'aria', 'semantic html', 'keyboard navigation', 'color contrast'
            ],
            'the-critic': [
                'decide', 'choose', 'evaluate', 'trade-off', 'architecture decision', 'analysis',
                'comparison', 'pros and cons', 'technical decision', 'assessment'
            ],
            'product-strategist': [
                'new product', 'startup idea', 'market research', 'business model', 'competition',
                'product validation', 'user research', 'product market fit', 'go to market'
            ],
            'legacy-specialist': [
                'objective-c', 'legacy', 'migration', 'modernize', 'refactor', 'compatibility',
                'legacy system', 'mainframe', 'cobol', 'fortran', 'modernization'
            ],
            'platform-integrator': [
                'api integration', 'third-party', 'webhook', 'external service', 'platform integration',
                'saas integration', 'rest api', 'graphql', 'microservices', 'service mesh'
            ]
        }
    
    def _load_tier_3_patterns(self) -> Dict[str, List[str]]:
        """Load Tier 3 keyword patterns."""
        return {
            'functional-programmer': [
                'haskell', 'functional', 'clojure', 'f#', 'category theory', 'monad', 'immutable',
                'pure functions', 'lambda calculus', 'higher-order functions'
            ],
            'metaprogramming-specialist': [
                'lisp', 'macro', 'dsl', 'metaprogramming', 'code generation', 'compiler',
                'ast', 'reflection', 'template metaprogramming', 'preprocessor'
            ],
            'elisp-specialist': [
                'emacs', 'init.el', 'elisp', 'emacs lisp', 'use-package', 'straight.el',
                'doom emacs', 'spacemacs', 'major mode', 'minor mode', 'melpa'
            ],
            'artist': [
                'design', 'visual', 'art', 'graphics', 'ui design', 'ux design', 'illustration',
                'logo', 'branding', 'color scheme', 'typography', 'photoshop', 'figma'
            ],
            'writer': [
                'writing', 'documentation', 'content', 'blog', 'technical writing', 'copywriting',
                'markdown', 'readme', 'user manual', 'api documentation'
            ],
            'ava-the-director': [
                'video', 'multimedia', 'production', 'editing', 'cinematography', 'directing',
                'screenplay', 'storyboard', 'after effects', 'premiere pro'
            ],
            'iris-the-modeler': [
                '3d', 'modeling', 'visualization', 'blender', 'maya', 'cad', 'rendering',
                'animation', 'mesh', 'texture', 'materials'
            ],
            'milo-the-comic': [
                'comic', 'illustration', 'cartoon', 'character design', 'sequential art',
                'graphic novel', 'webcomic', 'digital art'
            ],
            'echo-the-audio-engineer': [
                'audio', 'sound', 'music', 'recording', 'mixing', 'mastering', 'daw',
                'podcasting', 'sound design', 'audio processing'
            ]
        }
    
    def match_agents(self, request: str, analysis: RequestAnalysis) -> List[KeywordMatch]:
        """Match agents using keyword patterns."""
        request_lower = request.lower()
        matches = []
        
        # Combine all patterns
        all_patterns = {**self.tier_1_patterns, **self.tier_2_patterns, **self.tier_3_patterns}
        
        for agent_name, keywords in all_patterns.items():
            matching_keywords = []
            total_score = 0.0
            
            for keyword in keywords:
                if keyword in request_lower:
                    matching_keywords.append(keyword)
                    # Weight by keyword specificity (longer keywords get higher scores)
                    keyword_score = len(keyword.split()) * 1.0
                    total_score += keyword_score
            
            if matching_keywords:
                # Normalize score by number of total keywords
                match_score = min(1.0, total_score / len(keywords))
                
                # Apply tier-based weighting
                tier = self.agent_tiers.get(agent_name, 2)
                tier_weights = {1: 1.2, 2: 1.0, 3: 0.8}  # Prefer lower tiers
                weighted_score = match_score * tier_weights.get(tier, 1.0)
                
                # Calculate confidence based on match strength
                confidence = self._calculate_keyword_confidence(
                    len(matching_keywords), len(keywords), analysis
                )
                
                matches.append(KeywordMatch(
                    agent_name=agent_name,
                    match_score=weighted_score,
                    matching_keywords=matching_keywords,
                    tier=tier,
                    confidence=confidence,
                    rationale=f"Matched {len(matching_keywords)} keywords: {', '.join(matching_keywords[:3])}"
                ))
        
        # Sort by score
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return matches
    
    def _calculate_keyword_confidence(self, 
                                    matched_count: int, 
                                    total_keywords: int,
                                    analysis: RequestAnalysis) -> float:
        """Calculate confidence in keyword match."""
        # Base confidence from match ratio
        match_ratio = matched_count / max(total_keywords, 1)
        base_confidence = min(0.9, match_ratio * 2.0)
        
        # Boost confidence for high-coverage matches
        if matched_count >= 3:
            base_confidence += 0.1
        elif matched_count >= 5:
            base_confidence += 0.2
        
        # Adjust for request clarity
        if len(analysis.technical_keywords) > 0:
            base_confidence += 0.1
        
        if analysis.confidence_score > 0.8:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)


class HybridAgentSelector:
    """Hybrid agent selection combining semantic and keyword approaches."""
    
    def __init__(self, 
                 semantic_selector: 'SemanticAgentSelector',
                 keyword_matcher: KeywordAgentMatcher,
                 success_predictor: SuccessPredictor):
        """Initialize hybrid selector."""
        self.semantic_selector = semantic_selector
        self.keyword_matcher = keyword_matcher
        self.success_predictor = success_predictor
        
    async def select_agents(self, 
                          request: str,
                          project_path: Optional[Path] = None,
                          strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE,
                          max_agents: int = 5) -> EnhancedAgentSelection:
        """Select agents using hybrid approach."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Analyze request
            analysis = await self.semantic_selector.request_analyzer.analyze_request(
                request, project_path
            )
            
            # Determine optimal strategy if adaptive
            if strategy == SelectionStrategy.ADAPTIVE:
                strategy = self._determine_optimal_strategy(analysis)
            
            # Get recommendations based on strategy
            if strategy == SelectionStrategy.SEMANTIC_ONLY:
                primary_rec = await self._get_semantic_recommendation(analysis, max_agents)
                fallback_used = False
                
            elif strategy == SelectionStrategy.KEYWORD_ONLY:
                primary_rec = await self._get_keyword_recommendation(analysis, request, max_agents)
                fallback_used = False
                
            else:  # Hybrid strategies
                try:
                    primary_rec = await self._get_hybrid_recommendation(
                        analysis, request, strategy, max_agents
                    )
                    fallback_used = False
                except Exception as e:
                    logger.warning(f"Hybrid selection failed, falling back to keyword: {e}")
                    primary_rec = await self._get_keyword_recommendation(analysis, request, max_agents)
                    fallback_used = True
            
            # Generate alternative recommendations
            alternatives = await self._generate_alternatives(analysis, request, primary_rec, max_agents)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(primary_rec, analysis)
            
            # Generate explanation
            explanation = self._generate_selection_explanation(
                primary_rec, strategy, analysis, fallback_used
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return EnhancedAgentSelection(
                primary_recommendation=primary_rec,
                alternative_recommendations=alternatives,
                selection_strategy=strategy,
                confidence_level=confidence_level,
                processing_time=processing_time,
                fallback_used=fallback_used,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid agent selection: {e}")
            # Final fallback to simple keyword matching
            return await self._emergency_fallback(request, analysis if 'analysis' in locals() else None)
    
    def _determine_optimal_strategy(self, analysis: RequestAnalysis) -> SelectionStrategy:
        """Determine optimal selection strategy based on request characteristics."""
        
        # Use semantic if we have good embeddings and high confidence
        if (analysis.embedding is not None and 
            analysis.confidence_score > 0.7 and 
            len(analysis.technical_keywords) > 2):
            return SelectionStrategy.HYBRID_SEMANTIC_PRIMARY
        
        # Use keyword-primary if request has many explicit technical terms
        if (len(analysis.technical_keywords) > 5 or 
            any(keyword.lower() in analysis.original_request.lower() 
                for keyword in ['react', 'python', 'ios', 'android', 'aws', 'docker'])):
            return SelectionStrategy.HYBRID_KEYWORD_PRIMARY
        
        # Default to semantic-primary for complex requests
        if analysis.complexity_level in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]:
            return SelectionStrategy.HYBRID_SEMANTIC_PRIMARY
        
        # Balanced hybrid for most cases
        return SelectionStrategy.HYBRID_SEMANTIC_PRIMARY
    
    async def _get_semantic_recommendation(self, 
                                         analysis: RequestAnalysis,
                                         max_agents: int) -> WorkflowRecommendation:
        """Get recommendation from semantic system only."""
        # Get semantic matches
        semantic_analysis, search_results = await self.semantic_selector.semantic_matcher.match_agents(
            analysis.original_request, analysis.project_context.project_path if analysis.project_context else None
        )
        
        # Generate workflow recommendation
        workflow = await self.semantic_selector.orchestrator.recommend_workflow(
            analysis, search_results[:max_agents * 2], max_agents
        )
        
        return workflow
    
    async def _get_keyword_recommendation(self, 
                                        analysis: RequestAnalysis,
                                        request: str,
                                        max_agents: int) -> WorkflowRecommendation:
        """Get recommendation from keyword system only."""
        # Get keyword matches
        keyword_matches = self.keyword_matcher.match_agents(request, analysis)
        
        # Convert to SearchResult format
        search_results = []
        for match in keyword_matches[:max_agents * 2]:
            search_result = SearchResult(
                agent_name=match.agent_name,
                similarity_score=match.match_score,
                metadata={'tier': match.tier},
                explanation=match.rationale
            )
            search_results.append(search_result)
        
        # Generate workflow recommendation
        workflow = await self.semantic_selector.orchestrator.recommend_workflow(
            analysis, search_results, max_agents
        )
        
        return workflow
    
    async def _get_hybrid_recommendation(self, 
                                       analysis: RequestAnalysis,
                                       request: str,
                                       strategy: SelectionStrategy,
                                       max_agents: int) -> WorkflowRecommendation:
        """Get hybrid recommendation combining semantic and keyword approaches."""
        
        # Get both semantic and keyword results
        semantic_analysis, semantic_results = await self.semantic_selector.semantic_matcher.match_agents(
            request, analysis.project_context.project_path if analysis.project_context else None,
            top_k=max_agents * 3
        )
        
        keyword_matches = self.keyword_matcher.match_agents(request, analysis)
        
        # Create hybrid recommendations
        hybrid_results = await self._combine_results(
            semantic_results, keyword_matches, strategy, analysis
        )
        
        # Generate workflow with hybrid results
        workflow = await self.semantic_selector.orchestrator.recommend_workflow(
            analysis, hybrid_results[:max_agents * 2], max_agents
        )
        
        return workflow
    
    async def _combine_results(self, 
                             semantic_results: List[SearchResult],
                             keyword_matches: List[KeywordMatch],
                             strategy: SelectionStrategy,
                             analysis: RequestAnalysis) -> List[SearchResult]:
        """Combine semantic and keyword results intelligently."""
        
        # Create unified agent scoring
        agent_scores = {}
        
        # Process semantic results
        for result in semantic_results:
            agent_name = result.agent_name
            if agent_name not in agent_scores:
                agent_scores[agent_name] = {
                    'semantic_score': result.similarity_score,
                    'keyword_score': 0.0,
                    'search_result': result
                }
            else:
                agent_scores[agent_name]['semantic_score'] = result.similarity_score
        
        # Process keyword results
        for match in keyword_matches:
            agent_name = match.agent_name
            if agent_name not in agent_scores:
                # Create SearchResult for keyword-only matches
                search_result = SearchResult(
                    agent_name=agent_name,
                    similarity_score=match.match_score,
                    metadata={'tier': match.tier},
                    explanation=match.rationale
                )
                agent_scores[agent_name] = {
                    'semantic_score': 0.0,
                    'keyword_score': match.match_score,
                    'search_result': search_result
                }
            else:
                agent_scores[agent_name]['keyword_score'] = match.match_score
        
        # Combine scores based on strategy
        combined_results = []
        for agent_name, scores in agent_scores.items():
            if strategy == SelectionStrategy.HYBRID_SEMANTIC_PRIMARY:
                # 70% semantic, 30% keyword
                combined_score = scores['semantic_score'] * 0.7 + scores['keyword_score'] * 0.3
            elif strategy == SelectionStrategy.HYBRID_KEYWORD_PRIMARY:
                # 30% semantic, 70% keyword
                combined_score = scores['semantic_score'] * 0.3 + scores['keyword_score'] * 0.7
            else:
                # Equal weighting
                combined_score = (scores['semantic_score'] + scores['keyword_score']) / 2
            
            # Update search result with combined score
            result = scores['search_result']
            result.similarity_score = combined_score
            
            # Enhance explanation
            if scores['semantic_score'] > 0 and scores['keyword_score'] > 0:
                result.explanation = f"Hybrid match - Semantic: {scores['semantic_score']:.2f}, Keyword: {scores['keyword_score']:.2f}"
            elif scores['semantic_score'] > 0:
                result.explanation = f"Semantic match: {scores['semantic_score']:.2f}"
            else:
                result.explanation = f"Keyword match: {scores['keyword_score']:.2f}"
            
            combined_results.append(result)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return combined_results
    
    async def _generate_alternatives(self, 
                                   analysis: RequestAnalysis,
                                   request: str,
                                   primary: WorkflowRecommendation,
                                   max_agents: int) -> List[WorkflowRecommendation]:
        """Generate alternative recommendations."""
        alternatives = []
        
        try:
            # Alternative 1: Different strategy
            if hasattr(self, '_last_strategy'):
                alt_strategy = (SelectionStrategy.KEYWORD_ONLY 
                              if self._last_strategy == SelectionStrategy.SEMANTIC_ONLY
                              else SelectionStrategy.SEMANTIC_ONLY)
                
                if alt_strategy == SelectionStrategy.SEMANTIC_ONLY:
                    alt_rec = await self._get_semantic_recommendation(analysis, max_agents)
                else:
                    alt_rec = await self._get_keyword_recommendation(analysis, request, max_agents)
                
                # Only add if significantly different
                if not self._recommendations_too_similar(primary, alt_rec):
                    alternatives.append(alt_rec)
            
            # Alternative 2: Single-agent approach for simple tasks
            if (analysis.complexity_level == ComplexityLevel.SIMPLE and 
                len(primary.all_agents) > 1):
                
                # Find the highest-scoring single agent
                best_agent = max(primary.all_agents, key=lambda x: x.confidence_score)
                
                # Create minimal workflow
                from .multi_agent_orchestrator import AgentRole, WorkflowPattern
                
                minimal_workflow = WorkflowRecommendation(
                    primary_agents=[best_agent],
                    supporting_agents=[],
                    validation_agents=[],
                    workflow_pattern=WorkflowPattern.SEQUENTIAL,
                    confidence_score=best_agent.confidence_score,
                    explanation="Simplified single-agent approach",
                    success_probability=0.8
                )
                
                alternatives.append(minimal_workflow)
        
        except Exception as e:
            logger.error(f"Error generating alternatives: {e}")
        
        return alternatives[:2]  # Limit to 2 alternatives
    
    def _recommendations_too_similar(self, 
                                   rec1: WorkflowRecommendation,
                                   rec2: WorkflowRecommendation,
                                   threshold: float = 0.7) -> bool:
        """Check if two recommendations are too similar."""
        agents1 = set(rec1.agent_names)
        agents2 = set(rec2.agent_names)
        
        if not agents1 or not agents2:
            return False
        
        overlap = len(agents1 & agents2)
        total = len(agents1 | agents2)
        
        similarity = overlap / total if total > 0 else 0
        return similarity >= threshold
    
    def _determine_confidence_level(self, 
                                  recommendation: WorkflowRecommendation,
                                  analysis: RequestAnalysis) -> str:
        """Determine confidence level in the recommendation."""
        
        confidence_factors = []
        
        # Workflow confidence
        confidence_factors.append(recommendation.confidence_score)
        
        # Analysis confidence
        confidence_factors.append(analysis.confidence_score)
        
        # Success probability
        confidence_factors.append(recommendation.success_probability)
        
        # Agent quality
        if recommendation.all_agents:
            avg_agent_confidence = sum(agent.confidence_score for agent in recommendation.all_agents) / len(recommendation.all_agents)
            confidence_factors.append(avg_agent_confidence)
        
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        if overall_confidence >= 0.8:
            return "high"
        elif overall_confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _generate_selection_explanation(self, 
                                      recommendation: WorkflowRecommendation,
                                      strategy: SelectionStrategy,
                                      analysis: RequestAnalysis,
                                      fallback_used: bool) -> str:
        """Generate explanation for the agent selection."""
        
        explanations = []
        
        # Strategy explanation
        strategy_explanations = {
            SelectionStrategy.SEMANTIC_ONLY: "Used semantic analysis for intelligent agent matching",
            SelectionStrategy.KEYWORD_ONLY: "Used keyword matching for explicit technology alignment",
            SelectionStrategy.HYBRID_SEMANTIC_PRIMARY: "Combined semantic and keyword analysis with semantic priority",
            SelectionStrategy.HYBRID_KEYWORD_PRIMARY: "Combined semantic and keyword analysis with keyword priority",
            SelectionStrategy.ADAPTIVE: "Automatically selected optimal matching strategy"
        }
        
        explanations.append(strategy_explanations.get(strategy, "Used adaptive selection strategy"))
        
        # Fallback indication
        if fallback_used:
            explanations.append("Fallback system activated for reliability")
        
        # Workflow explanation
        explanations.append(recommendation.explanation)
        
        # Agent count explanation
        agent_count = len(recommendation.all_agents)
        if agent_count == 1:
            explanations.append("Single-agent solution for focused execution")
        elif agent_count <= 3:
            explanations.append(f"Lean {agent_count}-agent team for efficient collaboration")
        else:
            explanations.append(f"Comprehensive {agent_count}-agent team for complex requirements")
        
        # Risk consideration
        if analysis.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            explanations.append("Enhanced quality assurance for high-risk requirements")
        
        return "; ".join(explanations)
    
    async def _emergency_fallback(self, 
                                request: str,
                                analysis: Optional[RequestAnalysis]) -> EnhancedAgentSelection:
        """Emergency fallback when all systems fail."""
        from .multi_agent_orchestrator import AgentRole, WorkflowRecommendation, WorkflowPattern
        
        # Simple rule-based fallback
        fallback_agent = "full-stack-architect"  # Default safe choice
        
        # Basic rules for common cases
        request_lower = request.lower()
        if any(keyword in request_lower for keyword in ['ios', 'android', 'mobile', 'swift', 'kotlin']):
            fallback_agent = "mobile-developer"
        elif any(keyword in request_lower for keyword in ['security', 'vulnerability', 'auth']):
            fallback_agent = "security-audit-specialist"
        elif any(keyword in request_lower for keyword in ['test', 'testing', 'qa']):
            fallback_agent = "qa-test-engineer"
        elif any(keyword in request_lower for keyword in ['ai', 'ml', 'llm', 'chatgpt', 'claude']):
            fallback_agent = "ai-ml-engineer"
        
        # Create minimal workflow
        fallback_role = AgentRole(
            agent_name=fallback_agent,
            role_type='primary',
            priority=1,
            confidence_score=0.5,
            rationale="Emergency fallback selection"
        )
        
        fallback_workflow = WorkflowRecommendation(
            primary_agents=[fallback_role],
            supporting_agents=[],
            validation_agents=[],
            workflow_pattern=WorkflowPattern.SEQUENTIAL,
            confidence_score=0.4,
            explanation="Emergency fallback - basic agent selection",
            success_probability=0.6
        )
        
        return EnhancedAgentSelection(
            primary_recommendation=fallback_workflow,
            alternative_recommendations=[],
            selection_strategy=SelectionStrategy.KEYWORD_ONLY,
            confidence_level="low",
            processing_time=0.1,
            fallback_used=True,
            explanation="Emergency fallback system activated due to processing errors"
        )


class SemanticAgentSelector:
    """Main semantic agent selection system."""
    
    def __init__(self, 
                 db_url: str,
                 redis_url: Optional[str] = None,
                 faiss_index_path: Optional[str] = None,
                 model_path: Optional[str] = None):
        """Initialize semantic agent selector."""
        self.db_url = db_url
        
        # Initialize components
        self.request_analyzer = RequestAnalyzer()
        self.vector_search = VectorSearchManager(db_url, redis_url, faiss_index_path)
        self.orchestrator = MultiAgentOrchestrator(db_url)
        self.success_predictor = SuccessPredictor(Path(model_path) if model_path else None)
        
        # Import here to avoid circular imports
        from .request_analyzer import SemanticMatcher
        self.semantic_matcher = SemanticMatcher(self.vector_search, self.request_analyzer)
        
        # Create hybrid selector
        keyword_matcher = KeywordAgentMatcher()
        self.hybrid_selector = HybridAgentSelector(self, keyword_matcher, self.success_predictor)
        
    async def initialize(self):
        """Initialize all components."""
        await self.request_analyzer.initialize()
        await self.vector_search.initialize()
        await self.orchestrator.initialize()
        await self.success_predictor.initialize(self.db_url)
        await self.semantic_matcher.initialize()
        
        logger.info("Semantic agent selector initialized")
    
    async def close(self):
        """Close all connections."""
        await self.vector_search.close()
        await self.orchestrator.close()
        await self.semantic_matcher.close()
    
    async def select_agents(self, 
                          request: str,
                          project_path: Optional[Path] = None,
                          strategy: SelectionStrategy = SelectionStrategy.ADAPTIVE,
                          max_agents: int = 5) -> EnhancedAgentSelection:
        """Main entry point for agent selection."""
        return await self.hybrid_selector.select_agents(
            request, project_path, strategy, max_agents
        )
    
    async def analyze_request_only(self, 
                                 request: str,
                                 project_path: Optional[Path] = None) -> RequestAnalysis:
        """Analyze request without agent selection."""
        return await self.request_analyzer.analyze_request(request, project_path)
    
    async def get_semantic_matches_only(self, 
                                      request: str,
                                      project_path: Optional[Path] = None,
                                      top_k: int = 10) -> Tuple[RequestAnalysis, List[SearchResult]]:
        """Get semantic matches only without orchestration."""
        return await self.semantic_matcher.match_agents(request, project_path, top_k)


# CLI and utility functions
async def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic agent selection system")
    parser.add_argument("--db-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--redis-url", help="Redis URL for caching")
    parser.add_argument("--faiss-index", help="Path to FAISS index directory")
    parser.add_argument("--model-path", help="Path to ML models")
    parser.add_argument("--request", required=True, help="User request to analyze")
    parser.add_argument("--project-path", help="Path to project directory")
    parser.add_argument("--strategy", choices=['semantic', 'keyword', 'hybrid', 'adaptive'],
                       default='adaptive', help="Selection strategy")
    parser.add_argument("--max-agents", type=int, default=5, help="Maximum number of agents")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Map strategy
    strategy_map = {
        'semantic': SelectionStrategy.SEMANTIC_ONLY,
        'keyword': SelectionStrategy.KEYWORD_ONLY,
        'hybrid': SelectionStrategy.HYBRID_SEMANTIC_PRIMARY,
        'adaptive': SelectionStrategy.ADAPTIVE
    }
    
    strategy = strategy_map.get(args.strategy, SelectionStrategy.ADAPTIVE)
    
    # Initialize selector
    selector = SemanticAgentSelector(
        db_url=args.db_url,
        redis_url=args.redis_url,
        faiss_index_path=args.faiss_index,
        model_path=args.model_path
    )
    
    try:
        await selector.initialize()
        
        # Run selection
        project_path = Path(args.project_path) if args.project_path else None
        result = await selector.select_agents(
            args.request, project_path, strategy, args.max_agents
        )
        
        # Display results
        print(f"✓ Agent Selection Results ({result.selection_strategy.value}):")
        print(f"  Confidence: {result.confidence_level}")
        print(f"  Processing time: {result.processing_time:.3f}s")
        if result.fallback_used:
            print("  ⚠️  Fallback system used")
        
        print(f"\n📋 Primary Recommendation:")
        workflow = result.primary_recommendation
        for i, agent in enumerate(workflow.all_agents, 1):
            print(f"  {i}. {agent.agent_name} ({agent.role_type}) - Confidence: {agent.confidence_score:.2f}")
        
        print(f"\n💡 Explanation: {result.explanation}")
        
        if result.alternative_recommendations:
            print(f"\n🔄 Alternatives:")
            for i, alt in enumerate(result.alternative_recommendations, 1):
                agents = ', '.join(alt.agent_names)
                print(f"  {i}. {agents}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await selector.close()


if __name__ == "__main__":
    asyncio.run(main())