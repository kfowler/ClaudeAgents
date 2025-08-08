"""
Contextual Recommendations and Prediction System

Provides intelligent, context-aware recommendations for agent selection,
pattern usage, decision making, and workflow optimization based on
historical data, success patterns, and continuous learning.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
import json
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
import math

from ..knowledge_graph.graph_manager import GraphManager
from ..memory.memory_manager import MemoryManager, MemoryType
from ..learning.ml_pipeline import MLPipeline, ModelType, PredictionResult
from ..embeddings.vector_manager import VectorManager, SimilarityResult
from ..events.event_store import EventStore


logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """Types of recommendations"""
    AGENT_SELECTION = "agent_selection"
    PATTERN_SUGGESTION = "pattern_suggestion"
    DECISION_GUIDANCE = "decision_guidance"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    KNOWLEDGE_DISCOVERY = "knowledge_discovery"
    RISK_MITIGATION = "risk_mitigation"
    BEST_PRACTICE = "best_practice"
    LEARNING_OPPORTUNITY = "learning_opportunity"


class RecommendationReason(Enum):
    """Reasons for recommendations"""
    HISTORICAL_SUCCESS = "historical_success"
    SIMILARITY_MATCH = "similarity_match"
    PATTERN_RECOGNITION = "pattern_recognition"
    ML_PREDICTION = "ml_prediction"
    EXPERT_KNOWLEDGE = "expert_knowledge"
    RISK_PREVENTION = "risk_prevention"
    EFFICIENCY_OPTIMIZATION = "efficiency_optimization"
    KNOWLEDGE_GAP = "knowledge_gap"


@dataclass
class RecommendationContext:
    """Context information for generating recommendations"""
    session_id: Optional[str] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    agent_type: Optional[str] = None
    
    # Current state
    current_task: Optional[str] = None
    current_phase: Optional[str] = None
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    # Project characteristics
    project_domain: Optional[str] = None
    technology_stack: List[str] = field(default_factory=list)
    team_size: Optional[int] = None
    project_complexity: Optional[float] = None
    
    # Historical context
    recent_decisions: List[Dict[str, Any]] = field(default_factory=list)
    applied_patterns: List[Dict[str, Any]] = field(default_factory=list)
    current_issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # Preferences
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    team_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Temporal context
    deadline: Optional[datetime] = None
    time_available: Optional[timedelta] = None
    urgency_level: Optional[str] = None


@dataclass
class Recommendation:
    """A single recommendation with supporting information"""
    id: str
    type: RecommendationType
    title: str
    description: str
    
    # Core recommendation
    recommended_item: str  # Agent, pattern, decision option, etc.
    recommended_action: str
    
    # Supporting information
    confidence_score: float
    relevance_score: float
    impact_score: float
    effort_estimate: Optional[float] = None
    
    # Reasoning
    reasons: List[RecommendationReason] = field(default_factory=list)
    explanation: str = ""
    supporting_evidence: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context
    context: Optional[RecommendationContext] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary"""
        result = asdict(self)
        result['type'] = self.type.value
        result['reasons'] = [r.value for r in self.reasons]
        result['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            result['expires_at'] = self.expires_at.isoformat()
        return result


@dataclass
class RecommendationSet:
    """Set of related recommendations"""
    id: str
    title: str
    description: str
    recommendations: List[Recommendation]
    context: RecommendationContext
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_top_recommendations(self, n: int = 5) -> List[Recommendation]:
        """Get top n recommendations by overall score"""
        scored_recs = [
            (rec, rec.confidence_score * 0.4 + rec.relevance_score * 0.4 + rec.impact_score * 0.2)
            for rec in self.recommendations
        ]
        scored_recs.sort(key=lambda x: x[1], reverse=True)
        return [rec for rec, score in scored_recs[:n]]
    
    def filter_by_type(self, rec_type: RecommendationType) -> List[Recommendation]:
        """Filter recommendations by type"""
        return [rec for rec in self.recommendations if rec.type == rec_type]
    
    def get_high_confidence_recommendations(self, min_confidence: float = 0.7) -> List[Recommendation]:
        """Get recommendations above confidence threshold"""
        return [rec for rec in self.recommendations if rec.confidence_score >= min_confidence]


class BaseRecommender(ABC):
    """Abstract base class for recommendation generators"""
    
    @abstractmethod
    def generate_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 10
    ) -> List[Recommendation]:
        """Generate recommendations for given context"""
        pass
    
    @abstractmethod
    def get_recommendation_types(self) -> List[RecommendationType]:
        """Get types of recommendations this generator produces"""
        pass


class AgentSelectionRecommender(BaseRecommender):
    """Recommends appropriate agents based on context"""
    
    def __init__(self, graph_manager: GraphManager, ml_pipeline: MLPipeline):
        self.graph = graph_manager
        self.ml_pipeline = ml_pipeline
    
    def get_recommendation_types(self) -> List[RecommendationType]:
        return [RecommendationType.AGENT_SELECTION]
    
    def generate_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 10
    ) -> List[Recommendation]:
        """Generate agent selection recommendations"""
        recommendations = []
        
        # Use ML model for agent selection if available
        ml_prediction = self._get_ml_agent_prediction(context)
        if ml_prediction:
            rec = self._create_agent_recommendation_from_ml(ml_prediction, context)
            recommendations.append(rec)
        
        # Historical success analysis
        historical_recs = self._get_historical_agent_recommendations(context)
        recommendations.extend(historical_recs[:3])  # Top 3 from history
        
        # Similarity-based recommendations
        similar_recs = self._get_similar_context_agents(context)
        recommendations.extend(similar_recs[:2])  # Top 2 from similarity
        
        # Remove duplicates and sort by confidence
        seen_agents = set()
        unique_recs = []
        for rec in recommendations:
            if rec.recommended_item not in seen_agents:
                seen_agents.add(rec.recommended_item)
                unique_recs.append(rec)
        
        unique_recs.sort(key=lambda r: r.confidence_score, reverse=True)
        return unique_recs[:limit]
    
    def _get_ml_agent_prediction(self, context: RecommendationContext) -> Optional[PredictionResult]:
        """Get ML model prediction for agent selection"""
        try:
            features = {
                'project_complexity': context.project_complexity or 0.5,
                'team_size': context.team_size or 5,
                'is_web_project': 1.0 if 'web' in (context.project_domain or '') else 0.0,
                'is_mobile_project': 1.0 if 'mobile' in (context.project_domain or '') else 0.0,
                'is_ai_project': 1.0 if 'ai' in (context.project_domain or '') else 0.0,
                'has_database': 1.0 if any(tech in ['postgres', 'mysql', 'mongodb'] 
                                         for tech in context.technology_stack) else 0.0,
                'decision_type_architectural': 1.0 if 'architectural' in context.current_task else 0.0,
                'decision_type_technical': 1.0 if 'technical' in context.current_task else 0.0,
                'decision_confidence': 0.8,  # Default
                'outcome_confidence': 0.5   # Default
            }
            
            return self.ml_pipeline.predict(ModelType.AGENT_SELECTOR, features)
        except Exception as e:
            logger.error(f"Failed to get ML agent prediction: {e}")
            return None
    
    def _create_agent_recommendation_from_ml(
        self, 
        prediction: PredictionResult, 
        context: RecommendationContext
    ) -> Recommendation:
        """Create recommendation from ML prediction"""
        return Recommendation(
            id=f"ml_agent_{prediction.timestamp.timestamp()}",
            type=RecommendationType.AGENT_SELECTION,
            title=f"Recommended Agent: {prediction.prediction}",
            description=f"ML model suggests {prediction.prediction} agent for this context",
            recommended_item=prediction.prediction,
            recommended_action=f"Use {prediction.prediction} agent for this task",
            confidence_score=prediction.confidence,
            relevance_score=0.9,  # ML predictions are highly relevant
            impact_score=0.8,
            reasons=[RecommendationReason.ML_PREDICTION],
            explanation=f"Machine learning model predicts {prediction.prediction} "
                       f"with {prediction.confidence:.2f} confidence based on project characteristics",
            supporting_evidence=[{
                'type': 'ml_prediction',
                'model_version': prediction.model_version,
                'explanation': prediction.explanation
            }],
            context=context
        )
    
    def _get_historical_agent_recommendations(
        self, 
        context: RecommendationContext
    ) -> List[Recommendation]:
        """Get recommendations based on historical success"""
        recommendations = []
        
        # Query graph for successful agent usage in similar contexts
        if context.project_domain:
            successful_patterns = self.graph.get_agent_success_patterns(context.project_domain)
            
            for pattern in successful_patterns[:5]:  # Top 5 patterns
                if pattern.get('success_rate', 0) > 0.6:  # Only high success rate
                    rec = Recommendation(
                        id=f"hist_agent_{pattern['id']}",
                        type=RecommendationType.AGENT_SELECTION,
                        title=f"Historically Successful: {pattern['agent_type']}",
                        description=f"{pattern['agent_type']} has {pattern['success_rate']:.1%} success rate in similar projects",
                        recommended_item=pattern['agent_type'],
                        recommended_action=f"Consider using {pattern['agent_type']} agent",
                        confidence_score=min(0.9, pattern['success_rate']),
                        relevance_score=0.8,
                        impact_score=0.7,
                        reasons=[RecommendationReason.HISTORICAL_SUCCESS],
                        explanation=f"Based on {pattern['usage_count']} similar projects with "
                                   f"{pattern['success_rate']:.1%} success rate",
                        supporting_evidence=[{
                            'type': 'historical_success',
                            'success_rate': pattern['success_rate'],
                            'usage_count': pattern['usage_count']
                        }],
                        context=context
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _get_similar_context_agents(self, context: RecommendationContext) -> List[Recommendation]:
        """Get agents used in similar contexts"""
        # This would use vector similarity to find similar projects
        # and their successful agent combinations
        # Simplified implementation for now
        return []


class PatternRecommender(BaseRecommender):
    """Recommends patterns and best practices"""
    
    def __init__(
        self, 
        graph_manager: GraphManager, 
        vector_manager: VectorManager,
        ml_pipeline: MLPipeline
    ):
        self.graph = graph_manager
        self.vector_manager = vector_manager
        self.ml_pipeline = ml_pipeline
    
    def get_recommendation_types(self) -> List[RecommendationType]:
        return [RecommendationType.PATTERN_SUGGESTION, RecommendationType.BEST_PRACTICE]
    
    def generate_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 10
    ) -> List[Recommendation]:
        """Generate pattern recommendations"""
        recommendations = []
        
        # Semantic similarity based recommendations
        if context.current_task or context.goals:
            query_text = f"{context.current_task} {' '.join(context.goals)}"
            semantic_recs = self._get_semantic_pattern_recommendations(query_text, context)
            recommendations.extend(semantic_recs)
        
        # Success-based pattern recommendations
        success_recs = self._get_success_pattern_recommendations(context)
        recommendations.extend(success_recs)
        
        # Gap analysis recommendations
        gap_recs = self._get_knowledge_gap_recommendations(context)
        recommendations.extend(gap_recs)
        
        # Remove duplicates and sort
        seen_patterns = set()
        unique_recs = []
        for rec in recommendations:
            if rec.recommended_item not in seen_patterns:
                seen_patterns.add(rec.recommended_item)
                unique_recs.append(rec)
        
        unique_recs.sort(key=lambda r: r.confidence_score * r.relevance_score, reverse=True)
        return unique_recs[:limit]
    
    def _get_semantic_pattern_recommendations(
        self, 
        query_text: str, 
        context: RecommendationContext
    ) -> List[Recommendation]:
        """Get pattern recommendations using semantic similarity"""
        try:
            from ..knowledge_graph.schema import NodeType
            similar_patterns = self.vector_manager.find_similar_nodes(
                query_text, 
                node_types=[NodeType.PATTERN],
                k=5,
                min_score=0.5
            )
            
            recommendations = []
            for result in similar_patterns:
                # Get full pattern data from graph
                pattern = self.graph.get_node(result.id, NodeType.PATTERN)
                if pattern:
                    rec = Recommendation(
                        id=f"sem_pattern_{result.id}",
                        type=RecommendationType.PATTERN_SUGGESTION,
                        title=f"Similar Pattern: {pattern.name}",
                        description=pattern.description[:200] + "...",
                        recommended_item=result.id,
                        recommended_action=f"Consider applying {pattern.name} pattern",
                        confidence_score=result.score,
                        relevance_score=result.score,
                        impact_score=pattern.success_rate,
                        reasons=[RecommendationReason.SIMILARITY_MATCH],
                        explanation=f"Pattern semantically similar to your current task "
                                   f"with {result.score:.2f} similarity score",
                        supporting_evidence=[{
                            'type': 'semantic_similarity',
                            'similarity_score': result.score,
                            'pattern_success_rate': pattern.success_rate
                        }],
                        context=context
                    )
                    recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get semantic pattern recommendations: {e}")
            return []
    
    def _get_success_pattern_recommendations(
        self, 
        context: RecommendationContext
    ) -> List[Recommendation]:
        """Get patterns with high success rates for similar contexts"""
        recommendations = []
        
        if context.project_id:
            # Find knowledge gaps for this project
            gaps = self.graph.find_knowledge_gaps(context.project_id)
            
            for gap in gaps[:3]:  # Top 3 gaps
                rec = Recommendation(
                    id=f"success_pattern_{gap['id']}",
                    type=RecommendationType.PATTERN_SUGGESTION,
                    title=f"High Success Pattern: {gap['name']}",
                    description=gap.get('description', 'Successful pattern from similar projects'),
                    recommended_item=gap['id'],
                    recommended_action=f"Apply {gap['name']} pattern",
                    confidence_score=min(0.9, gap['usage_frequency'] / 10.0),
                    relevance_score=0.8,
                    impact_score=0.8,
                    reasons=[RecommendationReason.HISTORICAL_SUCCESS, RecommendationReason.KNOWLEDGE_GAP],
                    explanation=f"Pattern used successfully in {gap['usage_frequency']} similar projects",
                    supporting_evidence=[{
                        'type': 'knowledge_gap',
                        'usage_frequency': gap['usage_frequency']
                    }],
                    context=context
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _get_knowledge_gap_recommendations(
        self, 
        context: RecommendationContext
    ) -> List[Recommendation]:
        """Get recommendations to fill knowledge gaps"""
        # This would analyze current project patterns vs successful patterns
        # and recommend missing elements
        return []


class DecisionGuidanceRecommender(BaseRecommender):
    """Provides guidance for decision making"""
    
    def __init__(self, graph_manager: GraphManager, memory_manager: MemoryManager):
        self.graph = graph_manager
        self.memory = memory_manager
    
    def get_recommendation_types(self) -> List[RecommendationType]:
        return [RecommendationType.DECISION_GUIDANCE, RecommendationType.RISK_MITIGATION]
    
    def generate_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 10
    ) -> List[Recommendation]:
        """Generate decision guidance recommendations"""
        recommendations = []
        
        # Historical decision analysis
        if context.project_id:
            decision_history = self.graph.get_project_decision_history(context.project_id)
            
            # Analyze patterns in decision outcomes
            successful_decisions = [d for d in decision_history if d.get('outcome', {}).get('outcome_type') == 'success']
            failed_decisions = [d for d in decision_history if d.get('outcome', {}).get('outcome_type') == 'failure']
            
            # Find common patterns in successful decisions
            if successful_decisions:
                success_patterns = self._analyze_decision_patterns(successful_decisions)
                for pattern in success_patterns:
                    rec = self._create_decision_guidance_from_pattern(pattern, context, True)
                    recommendations.append(rec)
            
            # Find risk patterns from failed decisions
            if failed_decisions:
                risk_patterns = self._analyze_decision_patterns(failed_decisions)
                for pattern in risk_patterns:
                    rec = self._create_risk_mitigation_recommendation(pattern, context)
                    recommendations.append(rec)
        
        return recommendations[:limit]
    
    def _analyze_decision_patterns(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns in decisions"""
        patterns = []
        
        # Analyze decision types
        decision_types = Counter(d.get('decision_type', 'unknown') for d in decisions)
        for decision_type, count in decision_types.most_common(3):
            patterns.append({
                'type': 'decision_type_pattern',
                'decision_type': decision_type,
                'frequency': count,
                'percentage': count / len(decisions)
            })
        
        # Analyze confidence levels
        high_confidence_decisions = [d for d in decisions if d.get('confidence_level', 0) > 0.8]
        if high_confidence_decisions:
            patterns.append({
                'type': 'confidence_pattern',
                'pattern': 'high_confidence_correlation',
                'frequency': len(high_confidence_decisions),
                'percentage': len(high_confidence_decisions) / len(decisions)
            })
        
        return patterns
    
    def _create_decision_guidance_from_pattern(
        self, 
        pattern: Dict[str, Any], 
        context: RecommendationContext, 
        is_success: bool
    ) -> Recommendation:
        """Create decision guidance recommendation from pattern"""
        if pattern['type'] == 'decision_type_pattern':
            return Recommendation(
                id=f"decision_guidance_{pattern['decision_type']}",
                type=RecommendationType.DECISION_GUIDANCE,
                title=f"Decision Type Guidance: {pattern['decision_type'].title()}",
                description=f"{pattern['decision_type'].title()} decisions have shown good results in similar projects",
                recommended_item=pattern['decision_type'],
                recommended_action=f"Consider framing this as a {pattern['decision_type']} decision",
                confidence_score=min(0.9, pattern['percentage']),
                relevance_score=0.8,
                impact_score=0.7,
                reasons=[RecommendationReason.PATTERN_RECOGNITION, RecommendationReason.HISTORICAL_SUCCESS],
                explanation=f"{pattern['percentage']:.1%} of successful decisions in similar projects were {pattern['decision_type']} type",
                supporting_evidence=[{
                    'type': 'decision_pattern',
                    'pattern_data': pattern
                }],
                context=context,
                priority="medium"
            )
        
        # Default recommendation
        return Recommendation(
            id=f"decision_guidance_default_{datetime.utcnow().timestamp()}",
            type=RecommendationType.DECISION_GUIDANCE,
            title="Decision Pattern Identified",
            description="A decision pattern has been identified from historical data",
            recommended_item="pattern_guidance",
            recommended_action="Consider applying historical decision patterns",
            confidence_score=0.6,
            relevance_score=0.7,
            impact_score=0.6,
            reasons=[RecommendationReason.PATTERN_RECOGNITION],
            explanation="Historical analysis suggests certain decision approaches",
            context=context
        )
    
    def _create_risk_mitigation_recommendation(
        self, 
        pattern: Dict[str, Any], 
        context: RecommendationContext
    ) -> Recommendation:
        """Create risk mitigation recommendation"""
        return Recommendation(
            id=f"risk_mitigation_{pattern['type']}",
            type=RecommendationType.RISK_MITIGATION,
            title="Risk Mitigation",
            description="Potential risk identified based on historical patterns",
            recommended_item="risk_awareness",
            recommended_action="Be aware of potential risks in similar decision contexts",
            confidence_score=0.7,
            relevance_score=0.8,
            impact_score=0.9,  # High impact for risk mitigation
            reasons=[RecommendationReason.RISK_PREVENTION],
            explanation="Historical data shows this pattern is associated with decision failures",
            supporting_evidence=[{
                'type': 'risk_pattern',
                'pattern_data': pattern
            }],
            context=context,
            priority="high"
        )


class RecommendationEngine:
    """
    Main recommendation engine that orchestrates different recommenders
    and provides contextual, intelligent recommendations.
    """
    
    def __init__(
        self,
        graph_manager: GraphManager,
        memory_manager: MemoryManager,
        ml_pipeline: MLPipeline,
        vector_manager: VectorManager,
        event_store: EventStore
    ):
        """
        Initialize recommendation engine
        
        Args:
            graph_manager: Knowledge graph manager
            memory_manager: Memory manager  
            ml_pipeline: ML pipeline
            vector_manager: Vector manager
            event_store: Event store
        """
        self.graph = graph_manager
        self.memory = memory_manager
        self.ml_pipeline = ml_pipeline
        self.vector_manager = vector_manager
        self.event_store = event_store
        
        # Initialize recommenders
        self.recommenders = {
            'agent_selection': AgentSelectionRecommender(graph_manager, ml_pipeline),
            'pattern_suggestion': PatternRecommender(graph_manager, vector_manager, ml_pipeline),
            'decision_guidance': DecisionGuidanceRecommender(graph_manager, memory_manager)
        }
        
        # Recommendation cache
        self.recommendation_cache: Dict[str, RecommendationSet] = {}
        self.cache_ttl = timedelta(minutes=30)
    
    def get_recommendations(
        self,
        context: RecommendationContext,
        recommendation_types: Optional[List[RecommendationType]] = None,
        limit: int = 20
    ) -> RecommendationSet:
        """
        Get comprehensive recommendations for given context
        
        Args:
            context: Recommendation context
            recommendation_types: Types of recommendations to generate
            limit: Maximum number of recommendations
            
        Returns:
            Set of recommendations
        """
        # Generate cache key
        cache_key = self._generate_cache_key(context, recommendation_types)
        
        # Check cache
        if cache_key in self.recommendation_cache:
            cached_set = self.recommendation_cache[cache_key]
            if datetime.utcnow() - cached_set.created_at < self.cache_ttl:
                logger.debug(f"Returning cached recommendations for {cache_key}")
                return cached_set
        
        # Generate new recommendations
        all_recommendations = []
        
        # If no specific types requested, generate all types
        if recommendation_types is None:
            recommendation_types = list(RecommendationType)
        
        # Generate recommendations from each relevant recommender
        for recommender_name, recommender in self.recommenders.items():
            recommender_types = recommender.get_recommendation_types()
            
            # Check if this recommender produces any of the requested types
            if any(rt in recommendation_types for rt in recommender_types):
                try:
                    recs = recommender.generate_recommendations(context, limit=10)
                    all_recommendations.extend(recs)
                except Exception as e:
                    logger.error(f"Recommender {recommender_name} failed: {e}")
        
        # Filter by requested types
        filtered_recommendations = [
            rec for rec in all_recommendations 
            if rec.type in recommendation_types
        ]
        
        # Rank and limit recommendations
        ranked_recommendations = self._rank_recommendations(
            filtered_recommendations, context
        )[:limit]
        
        # Create recommendation set
        rec_set = RecommendationSet(
            id=f"rec_set_{datetime.utcnow().timestamp()}",
            title=f"Recommendations for {context.current_task or 'Current Context'}",
            description=f"Contextual recommendations based on project state and historical data",
            recommendations=ranked_recommendations,
            context=context
        )
        
        # Cache the result
        self.recommendation_cache[cache_key] = rec_set
        
        # Log recommendation generation
        self.event_store.publish_event(
            self._create_recommendation_event(rec_set, context)
        )
        
        return rec_set
    
    def get_agent_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 5
    ) -> List[Recommendation]:
        """Get agent selection recommendations"""
        rec_set = self.get_recommendations(
            context, 
            recommendation_types=[RecommendationType.AGENT_SELECTION],
            limit=limit
        )
        return rec_set.recommendations
    
    def get_pattern_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 10
    ) -> List[Recommendation]:
        """Get pattern and best practice recommendations"""
        rec_set = self.get_recommendations(
            context,
            recommendation_types=[
                RecommendationType.PATTERN_SUGGESTION,
                RecommendationType.BEST_PRACTICE
            ],
            limit=limit
        )
        return rec_set.recommendations
    
    def get_decision_guidance(
        self, 
        context: RecommendationContext,
        limit: int = 5
    ) -> List[Recommendation]:
        """Get decision guidance and risk mitigation recommendations"""
        rec_set = self.get_recommendations(
            context,
            recommendation_types=[
                RecommendationType.DECISION_GUIDANCE,
                RecommendationType.RISK_MITIGATION
            ],
            limit=limit
        )
        return rec_set.recommendations
    
    def provide_feedback(
        self,
        recommendation_id: str,
        feedback: Dict[str, Any]
    ) -> bool:
        """
        Provide feedback on recommendation quality
        
        Args:
            recommendation_id: ID of recommendation
            feedback: Feedback data (usefulness, accuracy, etc.)
            
        Returns:
            True if feedback recorded successfully
        """
        try:
            # Store feedback in memory system
            feedback_data = {
                'recommendation_id': recommendation_id,
                'feedback': feedback,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.memory.store_memory(
                MemoryType.INTERACTION,
                self.memory.ContextScope.GLOBAL,
                feedback_data,
                tags=['recommendation_feedback']
            )
            
            # Update ML models with feedback if applicable
            if 'usefulness_score' in feedback:
                # This would feed back to the ML pipeline for continuous learning
                pass
            
            logger.info(f"Recorded feedback for recommendation {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record recommendation feedback: {e}")
            return False
    
    def _rank_recommendations(
        self, 
        recommendations: List[Recommendation],
        context: RecommendationContext
    ) -> List[Recommendation]:
        """Rank recommendations by overall utility"""
        def calculate_score(rec: Recommendation) -> float:
            # Base score from recommendation metrics
            base_score = (
                rec.confidence_score * 0.4 +
                rec.relevance_score * 0.3 +
                rec.impact_score * 0.2
            )
            
            # Priority boost
            priority_multiplier = {
                'critical': 1.5,
                'high': 1.3,
                'medium': 1.0,
                'low': 0.8
            }.get(rec.priority, 1.0)
            
            # Recency factor (newer recommendations get slight boost)
            age_hours = (datetime.utcnow() - rec.created_at).total_seconds() / 3600
            recency_factor = max(0.8, 1.0 - age_hours / 24)  # Decay over 24 hours
            
            # Context relevance boost
            context_boost = 1.0
            if context.current_task and context.current_task.lower() in rec.title.lower():
                context_boost = 1.2
            
            return base_score * priority_multiplier * recency_factor * context_boost
        
        # Calculate scores and sort
        scored_recs = [(rec, calculate_score(rec)) for rec in recommendations]
        scored_recs.sort(key=lambda x: x[1], reverse=True)
        
        return [rec for rec, score in scored_recs]
    
    def _generate_cache_key(
        self, 
        context: RecommendationContext,
        recommendation_types: Optional[List[RecommendationType]]
    ) -> str:
        """Generate cache key for recommendations"""
        key_parts = [
            context.session_id or "",
            context.project_id or "",
            context.current_task or "",
            str(sorted([rt.value for rt in recommendation_types or [])))
        ]
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _create_recommendation_event(
        self,
        rec_set: RecommendationSet,
        context: RecommendationContext
    ):
        """Create event for recommendation generation"""
        from ..events.event_store import BaseEvent, EventType
        
        class RecommendationGeneratedEvent(BaseEvent):
            event_type = EventType.SYSTEM_MAINTENANCE  # Would add proper event type
        
        return RecommendationGeneratedEvent(
            session_id=context.session_id,
            project_id=context.project_id,
            user_id=context.user_id,
            agent_type=context.agent_type,
            metadata={
                'recommendation_set_id': rec_set.id,
                'recommendations_count': len(rec_set.recommendations),
                'recommendation_types': [rec.type.value for rec in rec_set.recommendations]
            }
        )
    
    def get_recommendation_analytics(self) -> Dict[str, Any]:
        """Get analytics on recommendation system performance"""
        # Get recent recommendation events
        recent_events = self.event_store.get_events(limit=1000)
        
        # Get feedback data
        feedback_memories = self.memory.retrieve_memory(
            tags=['recommendation_feedback'],
            limit=100
        )
        
        # Calculate metrics
        total_recommendations = len([e for e in recent_events if 'recommendation' in e.event_type.value.lower()])
        feedback_count = len(feedback_memories)
        
        # Calculate average feedback scores
        avg_usefulness = 0.0
        if feedback_memories:
            usefulness_scores = [
                m.content.get('feedback', {}).get('usefulness_score', 0)
                for m in feedback_memories
            ]
            avg_usefulness = np.mean([s for s in usefulness_scores if s > 0])
        
        return {
            'total_recommendations_generated': total_recommendations,
            'feedback_received': feedback_count,
            'feedback_rate': feedback_count / total_recommendations if total_recommendations > 0 else 0,
            'average_usefulness_score': avg_usefulness,
            'cache_size': len(self.recommendation_cache),
            'active_recommenders': len(self.recommenders)
        }
    
    def clear_cache(self):
        """Clear recommendation cache"""
        self.recommendation_cache.clear()
        logger.info("Recommendation cache cleared")
    
    def add_custom_recommender(self, name: str, recommender: BaseRecommender):
        """Add custom recommender to the engine"""
        self.recommenders[name] = recommender
        logger.info(f"Added custom recommender: {name}")


# Utility functions for creating recommendation contexts
def create_context_from_session(
    session_id: str,
    memory_manager: MemoryManager,
    graph_manager: GraphManager
) -> RecommendationContext:
    """Create recommendation context from active session"""
    session = memory_manager.get_session_context(session_id)
    
    if not session:
        return RecommendationContext(session_id=session_id)
    
    # Get project details if available
    project_data = {}
    if session.project_id:
        from ..knowledge_graph.schema import NodeType
        project = graph_manager.get_node(session.project_id, NodeType.PROJECT)
        if project:
            project_data = {
                'project_domain': project.domain,
                'technology_stack': project.technology_stack,
                'team_size': project.team_size,
                'project_complexity': project.complexity_score
            }
    
    return RecommendationContext(
        session_id=session_id,
        project_id=session.project_id,
        user_id=session.user_id,
        team_id=session.team_id,
        agent_type=session.agent_type,
        goals=session.goals,
        constraints=session.constraints,
        user_preferences=session.preferences,
        **project_data
    )