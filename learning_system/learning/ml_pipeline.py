"""
Machine Learning Pipeline for Pattern Recognition and Learning

Implements continuous learning, pattern recognition, success prediction,
and adaptive recommendations based on historical data and feedback.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, mean_squared_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib
import json

from ..knowledge_graph.graph_manager import GraphManager
from ..memory.memory_manager import MemoryManager


logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of ML models in the pipeline"""
    SUCCESS_PREDICTOR = "success_predictor"
    PATTERN_RECOMMENDER = "pattern_recommender"
    AGENT_SELECTOR = "agent_selector"
    ANOMALY_DETECTOR = "anomaly_detector"
    PREFERENCE_LEARNER = "preference_learner"


@dataclass
class TrainingData:
    """Training data container"""
    features: np.ndarray
    labels: np.ndarray
    feature_names: List[str]
    metadata: Dict[str, Any]


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    cv_score: Optional[float] = None
    feature_importance: Optional[Dict[str, float]] = None


@dataclass
class PredictionResult:
    """Prediction result with confidence and explanations"""
    prediction: Any
    confidence: float
    explanation: Dict[str, Any]
    model_version: str
    timestamp: datetime


class MLPipeline:
    """
    Machine Learning Pipeline for agent learning and adaptation
    """
    
    def __init__(
        self, 
        graph_manager: GraphManager,
        memory_manager: MemoryManager,
        model_storage_path: str = "/tmp/learning_models"
    ):
        """
        Initialize ML pipeline
        
        Args:
            graph_manager: Knowledge graph manager
            memory_manager: Memory manager
            model_storage_path: Path to store trained models
        """
        self.graph = graph_manager
        self.memory = memory_manager
        self.model_storage_path = model_storage_path
        
        # Models
        self.models: Dict[ModelType, Any] = {}
        self.scalers: Dict[ModelType, StandardScaler] = {}
        self.encoders: Dict[ModelType, Dict[str, LabelEncoder]] = {}
        self.model_metrics: Dict[ModelType, ModelMetrics] = {}
        
        # Feature extractors
        self.feature_extractors = {
            ModelType.SUCCESS_PREDICTOR: self._extract_success_features,
            ModelType.PATTERN_RECOMMENDER: self._extract_pattern_features,
            ModelType.AGENT_SELECTOR: self._extract_agent_selection_features,
            ModelType.ANOMALY_DETECTOR: self._extract_anomaly_features,
            ModelType.PREFERENCE_LEARNER: self._extract_preference_features
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        # Success Predictor - Classification
        self.models[ModelType.SUCCESS_PREDICTOR] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Pattern Recommender - Regression for scoring
        self.models[ModelType.PATTERN_RECOMMENDER] = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        
        # Agent Selector - Classification
        self.models[ModelType.AGENT_SELECTOR] = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=42
        )
        
        # Anomaly Detector - Clustering for outlier detection
        self.models[ModelType.ANOMALY_DETECTOR] = KMeans(
            n_clusters=5,
            random_state=42
        )
        
        # Preference Learner - Regression
        self.models[ModelType.PREFERENCE_LEARNER] = GradientBoostingRegressor(
            n_estimators=80,
            max_depth=5,
            random_state=42
        )
        
        # Initialize scalers and encoders
        for model_type in ModelType:
            self.scalers[model_type] = StandardScaler()
            self.encoders[model_type] = {}
    
    # Data Collection and Preparation
    
    def collect_training_data(self, model_type: ModelType, days_back: int = 90) -> TrainingData:
        """
        Collect training data for a specific model type
        
        Args:
            model_type: Type of model to collect data for
            days_back: Number of days to look back for data
            
        Returns:
            Training data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        if model_type == ModelType.SUCCESS_PREDICTOR:
            return self._collect_success_data(cutoff_date)
        elif model_type == ModelType.PATTERN_RECOMMENDER:
            return self._collect_pattern_data(cutoff_date)
        elif model_type == ModelType.AGENT_SELECTOR:
            return self._collect_agent_selection_data(cutoff_date)
        elif model_type == ModelType.ANOMALY_DETECTOR:
            return self._collect_anomaly_data(cutoff_date)
        elif model_type == ModelType.PREFERENCE_LEARNER:
            return self._collect_preference_data(cutoff_date)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _collect_success_data(self, cutoff_date: datetime) -> TrainingData:
        """Collect data for success prediction model"""
        # Query graph for project outcomes
        query = """
        MATCH (p:Project)-[:CONTAINS]->(d:Decision)-[:RESULTED_IN]->(o:Outcome)
        MATCH (p)-[:CONTAINS]->(pat:Pattern)
        MATCH (d)-[:HANDLED_BY]->(a:Agent)
        WHERE o.created_at >= $cutoff_date
        RETURN p, d, o, pat, a
        """
        
        with self.graph.get_session() as session:
            result = session.run(query, cutoff_date=cutoff_date.isoformat())
            
            data_points = []
            for record in result:
                project = dict(record["p"])
                decision = dict(record["d"])
                outcome = dict(record["o"])
                pattern = dict(record["pat"])
                agent = dict(record["a"])
                
                features = self._extract_success_features({
                    'project': project,
                    'decision': decision,
                    'pattern': pattern,
                    'agent': agent
                })
                
                # Success is binary: success vs failure
                label = 1 if outcome['outcome_type'] == 'success' else 0
                
                data_points.append((features, label))
        
        if not data_points:
            # Return empty data
            return TrainingData(
                features=np.array([]).reshape(0, 0),
                labels=np.array([]),
                feature_names=[],
                metadata={'data_points': 0}
            )
        
        features_list, labels_list = zip(*data_points)
        feature_names = list(features_list[0].keys()) if features_list else []
        
        # Convert to numpy arrays
        features_array = np.array([list(f.values()) for f in features_list])
        labels_array = np.array(labels_list)
        
        return TrainingData(
            features=features_array,
            labels=labels_array,
            feature_names=feature_names,
            metadata={'data_points': len(data_points), 'cutoff_date': cutoff_date}
        )
    
    def _collect_pattern_data(self, cutoff_date: datetime) -> TrainingData:
        """Collect data for pattern recommendation model"""
        # Get pattern usage and success rates
        query = """
        MATCH (pat:Pattern)-[:APPLIED_IN]->(p:Project)
        MATCH (p)-[:CONTAINS]->(o:Outcome)
        WHERE o.created_at >= $cutoff_date
        RETURN pat, p, o, 
               count(o) as usage_count,
               sum(case when o.outcome_type = 'success' then 1 else 0 end) as success_count
        """
        
        with self.graph.get_session() as session:
            result = session.run(query, cutoff_date=cutoff_date.isoformat())
            
            data_points = []
            for record in result:
                pattern = dict(record["pat"])
                project = dict(record["p"])
                usage_count = record["usage_count"]
                success_count = record["success_count"]
                
                features = self._extract_pattern_features({
                    'pattern': pattern,
                    'project': project,
                    'usage_count': usage_count
                })
                
                # Label is success rate (0-1)
                success_rate = success_count / usage_count if usage_count > 0 else 0
                
                data_points.append((features, success_rate))
        
        if not data_points:
            return TrainingData(
                features=np.array([]).reshape(0, 0),
                labels=np.array([]),
                feature_names=[],
                metadata={'data_points': 0}
            )
        
        features_list, labels_list = zip(*data_points)
        feature_names = list(features_list[0].keys()) if features_list else []
        
        features_array = np.array([list(f.values()) for f in features_list])
        labels_array = np.array(labels_list)
        
        return TrainingData(
            features=features_array,
            labels=labels_array,
            feature_names=feature_names,
            metadata={'data_points': len(data_points), 'cutoff_date': cutoff_date}
        )
    
    def _collect_agent_selection_data(self, cutoff_date: datetime) -> TrainingData:
        """Collect data for agent selection model"""
        # Get successful agent selections
        query = """
        MATCH (a:Agent)-[:HANDLED_BY]-(d:Decision)-[:RESULTED_IN]->(o:Outcome)
        MATCH (d)-[:BELONGS_TO]->(p:Project)
        WHERE o.created_at >= $cutoff_date
        RETURN a, d, p, o
        """
        
        with self.graph.get_session() as session:
            result = session.run(query, cutoff_date=cutoff_date.isoformat())
            
            data_points = []
            for record in result:
                agent = dict(record["a"])
                decision = dict(record["d"])
                project = dict(record["p"])
                outcome = dict(record["o"])
                
                features = self._extract_agent_selection_features({
                    'project': project,
                    'decision': decision,
                    'outcome': outcome
                })
                
                # Label is agent type
                label = agent['type']
                
                data_points.append((features, label))
        
        if not data_points:
            return TrainingData(
                features=np.array([]).reshape(0, 0),
                labels=np.array([]),
                feature_names=[],
                metadata={'data_points': 0}
            )
        
        features_list, labels_list = zip(*data_points)
        feature_names = list(features_list[0].keys()) if features_list else []
        
        features_array = np.array([list(f.values()) for f in features_list])
        labels_array = np.array(labels_list)
        
        return TrainingData(
            features=features_array,
            labels=labels_array,
            feature_names=feature_names,
            metadata={'data_points': len(data_points), 'cutoff_date': cutoff_date}
        )
    
    def _collect_anomaly_data(self, cutoff_date: datetime) -> TrainingData:
        """Collect data for anomaly detection"""
        # Get project and decision patterns for anomaly detection
        query = """
        MATCH (p:Project)-[:CONTAINS]->(d:Decision)
        OPTIONAL MATCH (d)-[:RESULTED_IN]->(o:Outcome)
        WHERE d.created_at >= $cutoff_date
        RETURN p, d, o
        """
        
        with self.graph.get_session() as session:
            result = session.run(query, cutoff_date=cutoff_date.isoformat())
            
            data_points = []
            for record in result:
                project = dict(record["p"])
                decision = dict(record["d"])
                outcome = dict(record["o"]) if record["o"] else {}
                
                features = self._extract_anomaly_features({
                    'project': project,
                    'decision': decision,
                    'outcome': outcome
                })
                
                data_points.append(features)
        
        if not data_points:
            return TrainingData(
                features=np.array([]).reshape(0, 0),
                labels=np.array([]),
                feature_names=[],
                metadata={'data_points': 0}
            )
        
        feature_names = list(data_points[0].keys()) if data_points else []
        features_array = np.array([list(f.values()) for f in data_points])
        
        # No labels for unsupervised learning
        return TrainingData(
            features=features_array,
            labels=np.array([]),
            feature_names=feature_names,
            metadata={'data_points': len(data_points), 'cutoff_date': cutoff_date}
        )
    
    def _collect_preference_data(self, cutoff_date: datetime) -> TrainingData:
        """Collect data for preference learning"""
        # Get user interaction data
        memories = self.memory.retrieve_memory(
            memory_types=[self.memory.MemoryType.PREFERENCE, self.memory.MemoryType.INTERACTION],
            limit=1000
        )
        
        data_points = []
        for memory in memories:
            if memory.created_at < cutoff_date:
                continue
            
            features = self._extract_preference_features(memory.content)
            
            # Satisfaction score as label
            label = memory.content.get('satisfaction_score', 0.5)
            
            data_points.append((features, label))
        
        if not data_points:
            return TrainingData(
                features=np.array([]).reshape(0, 0),
                labels=np.array([]),
                feature_names=[],
                metadata={'data_points': 0}
            )
        
        features_list, labels_list = zip(*data_points)
        feature_names = list(features_list[0].keys()) if features_list else []
        
        features_array = np.array([list(f.values()) for f in features_list])
        labels_array = np.array(labels_list)
        
        return TrainingData(
            features=features_array,
            labels=labels_array,
            feature_names=feature_names,
            metadata={'data_points': len(data_points), 'cutoff_date': cutoff_date}
        )
    
    # Feature Extraction
    
    def _extract_success_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for success prediction"""
        project = data.get('project', {})
        decision = data.get('decision', {})
        pattern = data.get('pattern', {})
        agent = data.get('agent', {})
        
        return {
            'project_complexity': project.get('complexity_score', 0.5),
            'team_size': project.get('team_size', 5),
            'decision_confidence': decision.get('confidence_level', 0.5),
            'decision_impact': decision.get('impact_score', 0.5),
            'pattern_success_rate': pattern.get('success_rate', 0.5),
            'pattern_usage_count': pattern.get('usage_count', 0),
            'agent_success_rate': agent.get('success_rate', 0.5),
            'agent_usage_count': agent.get('usage_count', 0),
            'alternatives_considered': len(decision.get('alternatives_considered', [])),
            'is_architectural_decision': 1.0 if decision.get('decision_type') == 'architectural' else 0.0
        }
    
    def _extract_pattern_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for pattern recommendation"""
        pattern = data.get('pattern', {})
        project = data.get('project', {})
        usage_count = data.get('usage_count', 0)
        
        return {
            'pattern_complexity': len(pattern.get('consequences', [])) / 10.0,
            'pattern_age_days': (datetime.utcnow() - 
                               datetime.fromisoformat(pattern.get('created_at', datetime.utcnow().isoformat()))
                               ).days,
            'project_complexity': project.get('complexity_score', 0.5),
            'project_team_size': project.get('team_size', 5),
            'pattern_tag_count': len(pattern.get('tags', [])),
            'usage_frequency': usage_count,
            'has_code_examples': 1.0 if pattern.get('code_examples') else 0.0,
            'is_architectural_pattern': 1.0 if pattern.get('pattern_type') == 'architectural' else 0.0,
            'domain_match': 1.0 if project.get('domain') in pattern.get('tags', []) else 0.0
        }
    
    def _extract_agent_selection_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for agent selection"""
        project = data.get('project', {})
        decision = data.get('decision', {})
        outcome = data.get('outcome', {})
        
        tech_stack = project.get('technology_stack', [])
        
        return {
            'project_complexity': project.get('complexity_score', 0.5),
            'team_size': project.get('team_size', 5),
            'decision_type_architectural': 1.0 if decision.get('decision_type') == 'architectural' else 0.0,
            'decision_type_technical': 1.0 if decision.get('decision_type') == 'technical' else 0.0,
            'decision_confidence': decision.get('confidence_level', 0.5),
            'is_web_project': 1.0 if any(tech in ['react', 'nextjs', 'vue'] for tech in tech_stack) else 0.0,
            'is_mobile_project': 1.0 if any(tech in ['ios', 'android', 'react-native'] for tech in tech_stack) else 0.0,
            'is_ai_project': 1.0 if any(tech in ['ai', 'ml', 'llm'] for tech in tech_stack) else 0.0,
            'has_database': 1.0 if any(tech in ['postgres', 'mysql', 'mongodb'] for tech in tech_stack) else 0.0,
            'outcome_confidence': outcome.get('confidence_score', 0.5) if outcome else 0.5
        }
    
    def _extract_anomaly_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for anomaly detection"""
        project = data.get('project', {})
        decision = data.get('decision', {})
        outcome = data.get('outcome', {})
        
        return {
            'project_complexity': project.get('complexity_score', 0.5),
            'team_size': project.get('team_size', 5),
            'decision_confidence': decision.get('confidence_level', 0.5),
            'decision_impact': decision.get('impact_score', 0.5),
            'alternatives_count': len(decision.get('alternatives_considered', [])),
            'outcome_confidence': outcome.get('confidence_score', 0.5) if outcome else 0.5,
            'tech_stack_size': len(project.get('technology_stack', [])),
            'decision_response_time': 1.0,  # Placeholder - would calculate from timestamps
            'project_age_days': (datetime.utcnow() - 
                               datetime.fromisoformat(project.get('created_at', datetime.utcnow().isoformat()))
                               ).days
        }
    
    def _extract_preference_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features for preference learning"""
        return {
            'agent_type_encoded': hash(data.get('agent_type', 'unknown')) % 100 / 100.0,
            'project_domain_encoded': hash(data.get('project_domain', 'unknown')) % 100 / 100.0,
            'interaction_duration': data.get('interaction_duration', 300) / 3600.0,  # Hours
            'complexity_preference': data.get('complexity_preference', 0.5),
            'detail_preference': data.get('detail_preference', 0.5),
            'formality_preference': data.get('formality_preference', 0.5),
            'explanation_preference': data.get('explanation_preference', 0.5),
            'follow_up_count': data.get('follow_up_count', 0),
            'task_completion_rate': data.get('task_completion_rate', 1.0)
        }
    
    # Model Training
    
    def train_model(self, model_type: ModelType, training_data: TrainingData) -> ModelMetrics:
        """
        Train a specific model
        
        Args:
            model_type: Type of model to train
            training_data: Training data
            
        Returns:
            Model metrics
        """
        if training_data.features.size == 0:
            logger.warning(f"No training data available for {model_type}")
            return ModelMetrics()
        
        # Prepare data
        X, y = self._prepare_training_data(model_type, training_data)
        
        if model_type == ModelType.ANOMALY_DETECTOR:
            # Unsupervised learning
            return self._train_unsupervised(model_type, X)
        else:
            # Supervised learning
            return self._train_supervised(model_type, X, y, training_data.feature_names)
    
    def _prepare_training_data(
        self, 
        model_type: ModelType, 
        training_data: TrainingData
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare and preprocess training data"""
        X = training_data.features
        y = training_data.labels
        
        # Handle categorical features for classification models
        if model_type in [ModelType.AGENT_SELECTOR] and len(y) > 0:
            if model_type not in self.encoders or 'label' not in self.encoders[model_type]:
                self.encoders[model_type]['label'] = LabelEncoder()
                y = self.encoders[model_type]['label'].fit_transform(y)
            else:
                y = self.encoders[model_type]['label'].transform(y)
        
        # Scale features
        if len(X) > 0:
            X = self.scalers[model_type].fit_transform(X)
        
        return X, y
    
    def _train_supervised(
        self, 
        model_type: ModelType, 
        X: np.ndarray, 
        y: np.ndarray,
        feature_names: List[str]
    ) -> ModelMetrics:
        """Train supervised learning model"""
        if len(X) < 5:  # Minimum samples required
            logger.warning(f"Insufficient data for training {model_type}")
            return ModelMetrics()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Train model
        model = self.models[model_type]
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        metrics = ModelMetrics()
        
        if hasattr(model, 'predict_proba'):  # Classification
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
            
            metrics.accuracy = accuracy
            metrics.precision = precision
            metrics.recall = recall
            metrics.f1_score = f1
        else:  # Regression
            mse = mean_squared_error(y_test, y_pred)
            mae = np.mean(np.abs(y_test - y_pred))
            
            metrics.mse = mse
            metrics.mae = mae
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=min(5, len(X)//2))
        metrics.cv_score = cv_scores.mean()
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            metrics.feature_importance = importance_dict
        
        self.model_metrics[model_type] = metrics
        logger.info(f"Trained {model_type} - CV Score: {metrics.cv_score:.3f}")
        
        return metrics
    
    def _train_unsupervised(self, model_type: ModelType, X: np.ndarray) -> ModelMetrics:
        """Train unsupervised learning model"""
        if len(X) < 5:
            logger.warning(f"Insufficient data for training {model_type}")
            return ModelMetrics()
        
        model = self.models[model_type]
        model.fit(X)
        
        # For clustering, calculate silhouette score or inertia
        metrics = ModelMetrics()
        if hasattr(model, 'inertia_'):
            metrics.mse = model.inertia_  # Using MSE field to store inertia
        
        self.model_metrics[model_type] = metrics
        logger.info(f"Trained {model_type} - Inertia: {model.inertia_:.3f}")
        
        return metrics
    
    # Prediction and Inference
    
    def predict(
        self, 
        model_type: ModelType,
        features: Dict[str, Any],
        return_confidence: bool = True
    ) -> PredictionResult:
        """
        Make prediction using trained model
        
        Args:
            model_type: Type of model to use
            features: Input features
            return_confidence: Whether to return confidence scores
            
        Returns:
            Prediction result
        """
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not found")
        
        model = self.models[model_type]
        
        # Extract and prepare features
        feature_vector = self._prepare_features_for_prediction(model_type, features)
        
        # Make prediction
        prediction = model.predict([feature_vector])[0]
        
        # Calculate confidence
        confidence = 0.5  # Default confidence
        explanation = {}
        
        if return_confidence:
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba([feature_vector])[0]
                confidence = np.max(proba)
                explanation['probabilities'] = dict(zip(model.classes_, proba))
            elif hasattr(model, 'decision_function'):
                decision = model.decision_function([feature_vector])[0]
                confidence = abs(decision) / (abs(decision) + 1)  # Sigmoid-like normalization
            
            # Add feature importance if available
            if (model_type in self.model_metrics and 
                self.model_metrics[model_type].feature_importance):
                explanation['feature_importance'] = self.model_metrics[model_type].feature_importance
        
        # Decode categorical predictions
        if (model_type in self.encoders and 
            'label' in self.encoders[model_type]):
            prediction = self.encoders[model_type]['label'].inverse_transform([prediction])[0]
        
        return PredictionResult(
            prediction=prediction,
            confidence=confidence,
            explanation=explanation,
            model_version="1.0",  # Would be versioned in production
            timestamp=datetime.utcnow()
        )
    
    def _prepare_features_for_prediction(
        self, 
        model_type: ModelType, 
        features: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare features for prediction"""
        # Extract features using appropriate extractor
        extractor = self.feature_extractors[model_type]
        extracted_features = extractor(features)
        
        # Convert to array
        feature_vector = np.array(list(extracted_features.values()))
        
        # Scale features
        feature_vector = self.scalers[model_type].transform([feature_vector])[0]
        
        return feature_vector
    
    # Model Management
    
    def save_models(self) -> bool:
        """Save trained models to disk"""
        try:
            for model_type, model in self.models.items():
                model_path = f"{self.model_storage_path}/{model_type.value}_model.joblib"
                joblib.dump(model, model_path)
                
                scaler_path = f"{self.model_storage_path}/{model_type.value}_scaler.joblib"
                joblib.dump(self.scalers[model_type], scaler_path)
                
                if self.encoders[model_type]:
                    encoder_path = f"{self.model_storage_path}/{model_type.value}_encoders.joblib"
                    joblib.dump(self.encoders[model_type], encoder_path)
            
            logger.info("Models saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
            return False
    
    def load_models(self) -> bool:
        """Load trained models from disk"""
        try:
            for model_type in ModelType:
                model_path = f"{self.model_storage_path}/{model_type.value}_model.joblib"
                if joblib.os.path.exists(model_path):
                    self.models[model_type] = joblib.load(model_path)
                
                scaler_path = f"{self.model_storage_path}/{model_type.value}_scaler.joblib"
                if joblib.os.path.exists(scaler_path):
                    self.scalers[model_type] = joblib.load(scaler_path)
                
                encoder_path = f"{self.model_storage_path}/{model_type.value}_encoders.joblib"
                if joblib.os.path.exists(encoder_path):
                    self.encoders[model_type] = joblib.load(encoder_path)
            
            logger.info("Models loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models"""
        info = {}
        for model_type, metrics in self.model_metrics.items():
            info[model_type.value] = {
                'metrics': asdict(metrics),
                'model_type': type(self.models[model_type]).__name__,
                'trained': model_type in self.models
            }
        return info
    
    # Continuous Learning
    
    def update_model_with_feedback(
        self,
        model_type: ModelType,
        features: Dict[str, Any],
        actual_outcome: Any,
        feedback_score: float
    ):
        """
        Update model with new feedback data
        
        Args:
            model_type: Type of model to update
            features: Input features
            actual_outcome: Actual outcome observed
            feedback_score: Quality score for the feedback
        """
        # Store feedback for next training cycle
        feedback_data = {
            'model_type': model_type.value,
            'features': features,
            'actual_outcome': actual_outcome,
            'feedback_score': feedback_score,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in memory system
        self.memory.store_memory(
            self.memory.MemoryType.INTERACTION,
            self.memory.ContextScope.GLOBAL,
            feedback_data,
            tags=['model_feedback', model_type.value]
        )
        
        logger.info(f"Recorded feedback for {model_type}")
    
    def retrain_all_models(self, days_back: int = 90) -> Dict[ModelType, ModelMetrics]:
        """
        Retrain all models with latest data
        
        Args:
            days_back: Number of days of data to use for training
            
        Returns:
            Dictionary of model metrics after retraining
        """
        results = {}
        
        for model_type in ModelType:
            try:
                logger.info(f"Retraining {model_type}")
                training_data = self.collect_training_data(model_type, days_back)
                metrics = self.train_model(model_type, training_data)
                results[model_type] = metrics
            except Exception as e:
                logger.error(f"Failed to retrain {model_type}: {e}")
                results[model_type] = ModelMetrics()
        
        # Save updated models
        self.save_models()
        
        return results