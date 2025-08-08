"""
Success Prediction and Confidence Scoring System

This module provides machine learning-based success prediction for agent-request
pairings and comprehensive confidence scoring for recommendations.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

# Database imports
import asyncpg

# Local imports
from .request_analyzer import RequestAnalysis, IntentCategory, ComplexityLevel, RiskLevel
from .vector_search import SearchResult
from .multi_agent_orchestrator import WorkflowRecommendation


logger = logging.getLogger(__name__)


class PredictionFeature(Enum):
    """Features used for success prediction."""
    SIMILARITY_SCORE = "similarity_score"
    CONTEXT_MATCH = "context_match"
    AGENT_TIER = "agent_tier"
    REQUEST_COMPLEXITY = "request_complexity"
    RISK_LEVEL = "risk_level"
    INTENT_CATEGORY = "intent_category"
    TECH_ALIGNMENT = "tech_alignment"
    HISTORICAL_SUCCESS = "historical_success"
    TEAM_HARMONY = "team_harmony"
    MANDATORY_COVERAGE = "mandatory_coverage"


@dataclass
class PredictionInput:
    """Input features for success prediction."""
    agent_name: str
    similarity_score: float
    context_match_score: float
    agent_tier: int
    request_complexity: int  # Mapped from ComplexityLevel
    risk_level: int  # Mapped from RiskLevel
    intent_category: int  # Mapped from IntentCategory
    tech_alignment_score: float
    historical_success_rate: float
    team_harmony_score: float
    mandatory_coverage_score: float
    project_has_ai: bool = False
    project_has_web: bool = False
    project_has_mobile: bool = False
    project_is_production: bool = False
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert to feature vector for ML model."""
        return np.array([
            self.similarity_score,
            self.context_match_score,
            self.agent_tier,
            self.request_complexity,
            self.risk_level,
            self.intent_category,
            self.tech_alignment_score,
            self.historical_success_rate,
            self.team_harmony_score,
            self.mandatory_coverage_score,
            float(self.project_has_ai),
            float(self.project_has_web),
            float(self.project_has_mobile),
            float(self.project_is_production)
        ])


@dataclass
class PredictionResult:
    """Result from success prediction."""
    agent_name: str
    success_probability: float
    confidence_score: float
    feature_importance: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    risk_factors: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)


@dataclass
class ModelPerformanceMetrics:
    """Performance metrics for trained models."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    cross_val_mean: float
    cross_val_std: float
    feature_importance: Dict[str, float] = field(default_factory=dict)
    training_samples: int = 0
    last_trained: datetime = field(default_factory=datetime.now)


class FeatureEngineer:
    """Engineer features for success prediction."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.fitted = False
        
    def create_features(self, 
                       agent_result: SearchResult,
                       analysis: RequestAnalysis,
                       historical_data: Optional[Dict[str, Any]] = None,
                       team_agents: Optional[List[str]] = None) -> PredictionInput:
        """Create features for a single agent-request pair."""
        
        # Map enums to integers
        complexity_map = {
            ComplexityLevel.SIMPLE: 1,
            ComplexityLevel.MODERATE: 2,
            ComplexityLevel.COMPLEX: 3,
            ComplexityLevel.VERY_COMPLEX: 4
        }
        
        risk_map = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        intent_map = {
            IntentCategory.UNKNOWN: 0,
            IntentCategory.NEW_PROJECT: 1,
            IntentCategory.FEATURE_ENHANCEMENT: 2,
            IntentCategory.BUG_FIX: 3,
            IntentCategory.CODE_REVIEW: 4,
            IntentCategory.OPTIMIZATION: 5,
            IntentCategory.REFACTORING: 6,
            IntentCategory.TESTING: 7,
            IntentCategory.DEPLOYMENT: 8,
            IntentCategory.ANALYSIS: 9,
            IntentCategory.LEARNING: 10,
            IntentCategory.CREATIVE: 11
        }
        
        # Calculate technology alignment
        tech_alignment = self._calculate_tech_alignment(agent_result, analysis)
        
        # Calculate context match score
        context_match = self._calculate_context_match(agent_result, analysis)
        
        # Get historical success rate
        historical_success = self._get_historical_success_rate(
            agent_result.agent_name, analysis, historical_data
        )
        
        # Calculate team harmony (if part of a team)
        team_harmony = 1.0  # Default for single agent
        if team_agents and len(team_agents) > 1:
            team_harmony = self._calculate_team_harmony(agent_result.agent_name, team_agents)
        
        # Calculate mandatory coverage
        mandatory_coverage = self._calculate_mandatory_coverage(agent_result, analysis)
        
        return PredictionInput(
            agent_name=agent_result.agent_name,
            similarity_score=agent_result.similarity_score,
            context_match_score=context_match,
            agent_tier=agent_result.metadata.get('tier', 1),
            request_complexity=complexity_map.get(analysis.complexity_level, 2),
            risk_level=risk_map.get(analysis.risk_level, 1),
            intent_category=intent_map.get(analysis.intent_category, 0),
            tech_alignment_score=tech_alignment,
            historical_success_rate=historical_success,
            team_harmony_score=team_harmony,
            mandatory_coverage_score=mandatory_coverage,
            project_has_ai=analysis.project_context.has_ai_features if analysis.project_context else False,
            project_has_web=analysis.project_context.has_web_component if analysis.project_context else False,
            project_has_mobile=analysis.project_context.has_mobile_component if analysis.project_context else False,
            project_is_production=analysis.project_context.is_production if analysis.project_context else False
        )
    
    def _calculate_tech_alignment(self, agent_result: SearchResult, analysis: RequestAnalysis) -> float:
        """Calculate how well agent technologies align with request."""
        if not analysis.technical_keywords:
            return 0.5  # Neutral if no tech keywords
        
        agent_technologies = set(agent_result.metadata.get('technologies', []))
        request_technologies = set(analysis.technical_keywords)
        
        if not agent_technologies:
            return 0.3  # Low if agent has no tech info
        
        # Calculate Jaccard similarity
        intersection = len(agent_technologies & request_technologies)
        union = len(agent_technologies | request_technologies)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_context_match(self, agent_result: SearchResult, analysis: RequestAnalysis) -> float:
        """Calculate contextual match score."""
        match_factors = []
        
        # Domain alignment
        agent_domains = set(agent_result.metadata.get('domains', []))
        if analysis.domain_keywords:
            domain_matches = sum(1 for domain in analysis.domain_keywords 
                               if any(d in domain for d in agent_domains))
            match_factors.append(domain_matches / len(analysis.domain_keywords))
        
        # Tier appropriateness for complexity
        tier = agent_result.metadata.get('tier', 1)
        complexity_tier_map = {
            ComplexityLevel.SIMPLE: [1, 2],
            ComplexityLevel.MODERATE: [1, 2],
            ComplexityLevel.COMPLEX: [1, 2, 3],
            ComplexityLevel.VERY_COMPLEX: [1, 2, 3]
        }
        appropriate_tiers = complexity_tier_map.get(analysis.complexity_level, [1, 2, 3])
        tier_match = 1.0 if tier in appropriate_tiers else 0.5
        match_factors.append(tier_match)
        
        # Intent alignment
        intent_agent_map = {
            IntentCategory.NEW_PROJECT: ['project-orchestrator', 'full-stack-architect', 'mobile-developer'],
            IntentCategory.TESTING: ['qa-test-engineer'],
            IntentCategory.DEPLOYMENT: ['devops-engineer'],
            IntentCategory.CODE_REVIEW: ['code-architect', 'security-audit-specialist'],
            IntentCategory.CREATIVE: ['artist', 'writer', 'ava-the-director']
        }
        
        preferred_agents = intent_agent_map.get(analysis.intent_category, [])
        intent_match = 1.0 if agent_result.agent_name in preferred_agents else 0.7
        match_factors.append(intent_match)
        
        return sum(match_factors) / len(match_factors) if match_factors else 0.5
    
    def _get_historical_success_rate(self, 
                                   agent_name: str,
                                   analysis: RequestAnalysis,
                                   historical_data: Optional[Dict[str, Any]]) -> float:
        """Get historical success rate for this agent in similar contexts."""
        if not historical_data:
            return 0.7  # Default assumption
        
        agent_history = historical_data.get(agent_name, {})
        
        # Look for similar contexts
        similar_contexts = []
        for context, success_rate in agent_history.items():
            if context.get('intent_category') == analysis.intent_category.value:
                similar_contexts.append(success_rate)
            elif context.get('complexity_level') == analysis.complexity_level.value:
                similar_contexts.append(success_rate * 0.8)  # Partial match
        
        if similar_contexts:
            return sum(similar_contexts) / len(similar_contexts)
        
        # Fall back to overall agent success rate
        overall_success = agent_history.get('overall_success_rate', 0.7)
        return overall_success
    
    def _calculate_team_harmony(self, agent_name: str, team_agents: List[str]) -> float:
        """Calculate how well this agent works with the team."""
        # Simplified harmony calculation
        # In practice, this would use the compatibility matrix
        
        synergistic_pairs = {
            'full-stack-architect': ['security-audit-specialist', 'qa-test-engineer'],
            'ai-ml-engineer': ['data-engineer', 'full-stack-architect'],
            'devops-engineer': ['security-audit-specialist', 'systems-engineer'],
            'project-orchestrator': ['*'],  # Works well with everyone
        }
        
        if agent_name in synergistic_pairs:
            synergies = synergistic_pairs[agent_name]
            if '*' in synergies:
                return 0.9
            
            synergy_count = sum(1 for agent in team_agents if agent in synergies)
            return 0.6 + (synergy_count * 0.1)
        
        return 0.7  # Default harmony
    
    def _calculate_mandatory_coverage(self, agent_result: SearchResult, analysis: RequestAnalysis) -> float:
        """Calculate if this agent covers mandatory requirements."""
        mandatory_agents = set()
        
        # Risk-based mandatory agents
        if analysis.risk_level == RiskLevel.CRITICAL:
            mandatory_agents.update(['security-audit-specialist', 'qa-test-engineer', 'accessibility-expert'])
        elif analysis.risk_level == RiskLevel.HIGH:
            mandatory_agents.update(['security-audit-specialist', 'qa-test-engineer'])
        
        # Intent-based mandatory agents
        if analysis.intent_category == IntentCategory.NEW_PROJECT:
            mandatory_agents.add('project-orchestrator')
        elif analysis.intent_category == IntentCategory.TESTING:
            mandatory_agents.add('qa-test-engineer')
        
        return 1.0 if agent_result.agent_name in mandatory_agents else 0.5


class SuccessPredictor:
    """Machine learning-based success prediction system."""
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path
        self.success_classifier = None
        self.confidence_regressor = None
        self.feature_engineer = FeatureEngineer()
        self.performance_metrics = None
        self.feature_names = [
            'similarity_score', 'context_match_score', 'agent_tier',
            'request_complexity', 'risk_level', 'intent_category',
            'tech_alignment_score', 'historical_success_rate',
            'team_harmony_score', 'mandatory_coverage_score',
            'project_has_ai', 'project_has_web', 'project_has_mobile',
            'project_is_production'
        ]
        
    async def initialize(self, db_url: Optional[str] = None):
        """Initialize the success predictor."""
        # Try to load existing models
        if self.model_path and self.model_path.exists():
            await self.load_models()
        
        # If no models exist and database is available, train new models
        if (self.success_classifier is None or self.confidence_regressor is None) and db_url:
            await self.train_models_from_database(db_url)
        
        # Create default models if still none available
        if self.success_classifier is None:
            self._create_default_models()
        
        logger.info("Success predictor initialized")
    
    async def predict_success(self, 
                            agent_results: List[SearchResult],
                            analysis: RequestAnalysis,
                            historical_data: Optional[Dict[str, Any]] = None,
                            team_agents: Optional[List[str]] = None) -> List[PredictionResult]:
        """Predict success probability for agent-request pairings."""
        predictions = []
        
        for agent_result in agent_results:
            try:
                # Create features
                features = self.feature_engineer.create_features(
                    agent_result, analysis, historical_data, team_agents
                )
                
                # Get feature vector
                feature_vector = features.to_feature_vector().reshape(1, -1)
                
                # Predict success probability
                if self.success_classifier:
                    success_prob = self.success_classifier.predict_proba(feature_vector)[0][1]
                else:
                    success_prob = self._fallback_success_prediction(features)
                
                # Predict confidence
                if self.confidence_regressor:
                    confidence = self.confidence_regressor.predict(feature_vector)[0]
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
                else:
                    confidence = self._fallback_confidence_prediction(features, success_prob)
                
                # Get feature importance
                feature_importance = self._get_feature_importance(features)
                
                # Generate explanation
                explanation = self._generate_prediction_explanation(features, success_prob, confidence)
                
                # Identify risk and success factors
                risk_factors, success_factors = self._identify_factors(features, success_prob)
                
                predictions.append(PredictionResult(
                    agent_name=agent_result.agent_name,
                    success_probability=success_prob,
                    confidence_score=confidence,
                    feature_importance=feature_importance,
                    explanation=explanation,
                    risk_factors=risk_factors,
                    success_factors=success_factors
                ))
                
            except Exception as e:
                logger.error(f"Error predicting success for {agent_result.agent_name}: {e}")
                # Create fallback prediction
                predictions.append(PredictionResult(
                    agent_name=agent_result.agent_name,
                    success_probability=0.7,  # Default assumption
                    confidence_score=0.5,
                    explanation="Fallback prediction due to processing error"
                ))
        
        return predictions
    
    async def train_models_from_database(self, db_url: str):
        """Train models using historical data from database."""
        try:
            # Connect to database
            conn = await asyncpg.connect(db_url)
            
            # Fetch training data
            training_data = await self._fetch_training_data(conn)
            
            await conn.close()
            
            if len(training_data) < 50:  # Need minimum data for training
                logger.warning(f"Insufficient training data ({len(training_data)} samples). Using default models.")
                self._create_default_models()
                return
            
            # Prepare features and targets
            X, y_success, y_confidence = self._prepare_training_data(training_data)
            
            # Train success classifier
            await self._train_success_classifier(X, y_success)
            
            # Train confidence regressor
            await self._train_confidence_regressor(X, y_confidence)
            
            # Save models
            if self.model_path:
                await self.save_models()
            
            logger.info(f"Trained models on {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Error training models from database: {e}")
            self._create_default_models()
    
    async def _fetch_training_data(self, conn) -> List[Dict[str, Any]]:
        """Fetch training data from database."""
        # This would fetch historical invocation data with outcomes
        # For now, return empty list - would be implemented based on actual schema
        query = """
            SELECT 
                ai.agent_name,
                ai.success,
                ai.user_satisfaction_score,
                ai.completion_time,
                ra.request_text,
                ra.extracted_context,
                ra.complexity_score,
                ra.risk_level,
                ra.intent_classification,
                sm.similarity_score,
                sm.context_score,
                sm.confidence_score
            FROM agent_invocations ai
            JOIN request_analysis ra ON ai.request_id = ra.id
            LEFT JOIN semantic_matches sm ON ai.request_id = sm.request_id 
                AND ai.agent_name = sm.agent_name
            WHERE ai.created_at >= NOW() - INTERVAL '6 months'
                AND ai.completion_time IS NOT NULL
            ORDER BY ai.created_at DESC
            LIMIT 10000
        """
        
        try:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching training data: {e}")
            return []
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for ML models."""
        # Convert training data to feature vectors
        # This is a simplified version - would need full implementation
        
        features = []
        success_targets = []
        confidence_targets = []
        
        for data in training_data:
            # Extract features (simplified)
            feature_vector = np.array([
                data.get('similarity_score', 0.5),
                data.get('context_score', 0.5),
                1,  # agent_tier (would need to look up)
                data.get('complexity_score', 2),
                2,  # risk_level (would need to map)
                1,  # intent_category (would need to map)
                0.5,  # tech_alignment_score (would need to calculate)
                0.7,  # historical_success_rate (would need to calculate)
                0.7,  # team_harmony_score (would need to calculate)
                0.5,  # mandatory_coverage_score (would need to calculate)
                0,  # project_has_ai
                0,  # project_has_web
                0,  # project_has_mobile
                0   # project_is_production
            ])
            
            features.append(feature_vector)
            success_targets.append(1 if data.get('success', False) else 0)
            
            # Use user satisfaction as proxy for confidence
            satisfaction = data.get('user_satisfaction_score', 3)
            confidence_targets.append(min(1.0, satisfaction / 5.0))
        
        return np.array(features), np.array(success_targets), np.array(confidence_targets)
    
    async def _train_success_classifier(self, X: np.ndarray, y: np.ndarray):
        """Train the success classification model."""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train Random Forest classifier
            self.success_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            )
            
            self.success_classifier.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.success_classifier.predict(X_test)
            y_pred_proba = self.success_classifier.predict_proba(X_test)[:, 1]
            
            # Cross-validation
            cv_scores = cross_val_score(self.success_classifier, X, y, cv=5)
            
            # Store performance metrics
            self.performance_metrics = ModelPerformanceMetrics(
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred),
                recall=recall_score(y_test, y_pred),
                f1_score=f1_score(y_test, y_pred),
                cross_val_mean=cv_scores.mean(),
                cross_val_std=cv_scores.std(),
                feature_importance=dict(zip(self.feature_names, self.success_classifier.feature_importances_)),
                training_samples=len(X)
            )
            
            logger.info(f"Success classifier trained - Accuracy: {self.performance_metrics.accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error training success classifier: {e}")
            self._create_default_models()
    
    async def _train_confidence_regressor(self, X: np.ndarray, y: np.ndarray):
        """Train the confidence regression model."""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train Gradient Boosting regressor
            self.confidence_regressor = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                min_samples_split=10,
                random_state=42
            )
            
            self.confidence_regressor.fit(X_train, y_train)
            
            logger.info("Confidence regressor trained successfully")
            
        except Exception as e:
            logger.error(f"Error training confidence regressor: {e}")
            self.confidence_regressor = None
    
    def _create_default_models(self):
        """Create default models when no training data is available."""
        # Create simple rule-based models
        self.success_classifier = None  # Will use fallback prediction
        self.confidence_regressor = None
        
        logger.info("Using default rule-based prediction models")
    
    def _fallback_success_prediction(self, features: PredictionInput) -> float:
        """Fallback success prediction using rules."""
        success_factors = []
        
        # Similarity score weight
        success_factors.append(features.similarity_score * 0.3)
        
        # Context match weight
        success_factors.append(features.context_match_score * 0.2)
        
        # Historical success weight
        success_factors.append(features.historical_success_rate * 0.2)
        
        # Mandatory coverage weight
        success_factors.append(features.mandatory_coverage_score * 0.15)
        
        # Team harmony weight
        success_factors.append(features.team_harmony_score * 0.1)
        
        # Tier appropriateness
        tier_bonus = 0.05 if features.agent_tier <= 2 else 0.0
        success_factors.append(tier_bonus)
        
        return sum(success_factors)
    
    def _fallback_confidence_prediction(self, features: PredictionInput, success_prob: float) -> float:
        """Fallback confidence prediction using rules."""
        confidence_factors = []
        
        # High similarity gives high confidence
        if features.similarity_score > 0.8:
            confidence_factors.append(0.9)
        elif features.similarity_score > 0.6:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # Good context match increases confidence
        confidence_factors.append(features.context_match_score * 0.8)
        
        # Historical success rate affects confidence
        confidence_factors.append(features.historical_success_rate * 0.9)
        
        # Mandatory agent coverage increases confidence
        if features.mandatory_coverage_score > 0.8:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.6)
        
        base_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Adjust based on success probability
        if success_prob > 0.8:
            return min(1.0, base_confidence + 0.1)
        elif success_prob < 0.4:
            return max(0.3, base_confidence - 0.2)
        
        return base_confidence
    
    def _get_feature_importance(self, features: PredictionInput) -> Dict[str, float]:
        """Get feature importance for this prediction."""
        if self.success_classifier and hasattr(self.success_classifier, 'feature_importances_'):
            return dict(zip(self.feature_names, self.success_classifier.feature_importances_))
        
        # Fallback importance weights
        return {
            'similarity_score': 0.25,
            'context_match_score': 0.20,
            'historical_success_rate': 0.15,
            'mandatory_coverage_score': 0.15,
            'tech_alignment_score': 0.10,
            'team_harmony_score': 0.05,
            'agent_tier': 0.05,
            'request_complexity': 0.03,
            'risk_level': 0.02
        }
    
    def _generate_prediction_explanation(self, 
                                       features: PredictionInput,
                                       success_prob: float,
                                       confidence: float) -> str:
        """Generate explanation for the prediction."""
        explanations = []
        
        # Success probability explanation
        if success_prob > 0.8:
            explanations.append(f"High success probability ({success_prob:.2f})")
        elif success_prob > 0.6:
            explanations.append(f"Good success probability ({success_prob:.2f})")
        elif success_prob > 0.4:
            explanations.append(f"Moderate success probability ({success_prob:.2f})")
        else:
            explanations.append(f"Lower success probability ({success_prob:.2f})")
        
        # Confidence explanation
        if confidence > 0.8:
            explanations.append("high confidence")
        elif confidence > 0.6:
            explanations.append("good confidence")
        else:
            explanations.append("moderate confidence")
        
        # Key factors
        if features.similarity_score > 0.7:
            explanations.append("strong semantic match")
        
        if features.historical_success_rate > 0.8:
            explanations.append("excellent track record")
        
        if features.mandatory_coverage_score > 0.8:
            explanations.append("covers mandatory requirements")
        
        if features.team_harmony_score > 0.8:
            explanations.append("excellent team fit")
        
        return "; ".join(explanations)
    
    def _identify_factors(self, features: PredictionInput, success_prob: float) -> Tuple[List[str], List[str]]:
        """Identify risk and success factors."""
        risk_factors = []
        success_factors = []
        
        # Analyze key features
        if features.similarity_score < 0.4:
            risk_factors.append("Low semantic similarity with request")
        elif features.similarity_score > 0.8:
            success_factors.append("Excellent semantic match")
        
        if features.context_match_score < 0.3:
            risk_factors.append("Poor contextual alignment")
        elif features.context_match_score > 0.7:
            success_factors.append("Strong contextual fit")
        
        if features.historical_success_rate < 0.5:
            risk_factors.append("Below-average historical performance")
        elif features.historical_success_rate > 0.8:
            success_factors.append("Proven track record of success")
        
        if features.mandatory_coverage_score < 0.5:
            risk_factors.append("Does not cover mandatory requirements")
        elif features.mandatory_coverage_score > 0.8:
            success_factors.append("Addresses critical requirements")
        
        if features.team_harmony_score < 0.5:
            risk_factors.append("Potential team compatibility issues")
        elif features.team_harmony_score > 0.8:
            success_factors.append("Excellent team synergy")
        
        if features.tech_alignment_score < 0.3:
            risk_factors.append("Limited technology alignment")
        elif features.tech_alignment_score > 0.7:
            success_factors.append("Strong technology expertise match")
        
        return risk_factors, success_factors
    
    async def save_models(self):
        """Save trained models to disk."""
        if not self.model_path:
            return
        
        try:
            self.model_path.mkdir(parents=True, exist_ok=True)
            
            if self.success_classifier:
                joblib.dump(self.success_classifier, 
                           self.model_path / "success_classifier.joblib")
            
            if self.confidence_regressor:
                joblib.dump(self.confidence_regressor, 
                           self.model_path / "confidence_regressor.joblib")
            
            if self.performance_metrics:
                with open(self.model_path / "performance_metrics.json", 'w') as f:
                    json.dump({
                        'accuracy': self.performance_metrics.accuracy,
                        'precision': self.performance_metrics.precision,
                        'recall': self.performance_metrics.recall,
                        'f1_score': self.performance_metrics.f1_score,
                        'cross_val_mean': self.performance_metrics.cross_val_mean,
                        'cross_val_std': self.performance_metrics.cross_val_std,
                        'feature_importance': self.performance_metrics.feature_importance,
                        'training_samples': self.performance_metrics.training_samples,
                        'last_trained': self.performance_metrics.last_trained.isoformat()
                    }, f, indent=2)
            
            logger.info(f"Models saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def load_models(self):
        """Load trained models from disk."""
        if not self.model_path or not self.model_path.exists():
            return
        
        try:
            # Load success classifier
            classifier_path = self.model_path / "success_classifier.joblib"
            if classifier_path.exists():
                self.success_classifier = joblib.load(classifier_path)
            
            # Load confidence regressor
            regressor_path = self.model_path / "confidence_regressor.joblib"
            if regressor_path.exists():
                self.confidence_regressor = joblib.load(regressor_path)
            
            # Load performance metrics
            metrics_path = self.model_path / "performance_metrics.json"
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    data = json.load(f)
                    self.performance_metrics = ModelPerformanceMetrics(
                        accuracy=data['accuracy'],
                        precision=data['precision'],
                        recall=data['recall'],
                        f1_score=data['f1_score'],
                        cross_val_mean=data['cross_val_mean'],
                        cross_val_std=data['cross_val_std'],
                        feature_importance=data['feature_importance'],
                        training_samples=data['training_samples'],
                        last_trained=datetime.fromisoformat(data['last_trained'])
                    )
            
            logger.info(f"Models loaded from {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self._create_default_models()


# CLI and utility functions
async def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Success prediction system")
    parser.add_argument("--db-url", help="PostgreSQL database URL for training")
    parser.add_argument("--model-path", help="Path to save/load models")
    parser.add_argument("--train", action='store_true', help="Train models from database")
    parser.add_argument("--evaluate", action='store_true', help="Evaluate model performance")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize predictor
    model_path = Path(args.model_path) if args.model_path else None
    predictor = SuccessPredictor(model_path)
    
    try:
        await predictor.initialize(args.db_url)
        
        if args.train and args.db_url:
            await predictor.train_models_from_database(args.db_url)
            print("✓ Models trained successfully")
        
        if args.evaluate and predictor.performance_metrics:
            metrics = predictor.performance_metrics
            print(f"✓ Model Performance:")
            print(f"  Accuracy: {metrics.accuracy:.3f}")
            print(f"  Precision: {metrics.precision:.3f}")
            print(f"  Recall: {metrics.recall:.3f}")
            print(f"  F1 Score: {metrics.f1_score:.3f}")
            print(f"  Cross-validation: {metrics.cross_val_mean:.3f} ± {metrics.cross_val_std:.3f}")
            print(f"  Training samples: {metrics.training_samples}")
        else:
            print("✓ Success predictor initialized successfully")
            
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())