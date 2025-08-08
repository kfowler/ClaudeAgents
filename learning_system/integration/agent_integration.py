"""
Agent System Integration Layer

Integrates the learning system with the existing agent infrastructure,
providing seamless hooks for memory, learning, and recommendations
without disrupting existing agent workflows.
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import asyncio
from functools import wraps
import inspect

from ..knowledge_graph.graph_manager import GraphManager
from ..memory.memory_manager import MemoryManager, MemoryType, ContextScope
from ..learning.ml_pipeline import MLPipeline
from ..embeddings.vector_manager import VectorManager
from ..events.event_store import EventStore, create_session_started_event, create_action_event
from ..recommendations.recommendation_engine import RecommendationEngine, RecommendationContext
from ..privacy.privacy_engine import PrivacyEngine


logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Integration modes for different deployment scenarios"""
    PASSIVE = "passive"        # Only observes, doesn't interfere
    ACTIVE = "active"          # Provides recommendations and guidance
    AUTONOMOUS = "autonomous"  # Can take actions based on learning


@dataclass
class AgentIntegrationConfig:
    """Configuration for agent integration"""
    mode: IntegrationMode = IntegrationMode.ACTIVE
    
    # Feature flags
    enable_memory: bool = True
    enable_learning: bool = True
    enable_recommendations: bool = True
    enable_privacy: bool = True
    enable_events: bool = True
    
    # Learning settings
    auto_pattern_detection: bool = True
    auto_decision_tracking: bool = True
    continuous_learning: bool = True
    
    # Privacy settings
    privacy_policy_id: str = "internal"
    require_consent: bool = True
    
    # Performance settings
    async_processing: bool = True
    batch_size: int = 10
    cache_ttl_minutes: int = 30
    
    # Integration hooks
    pre_agent_hooks: List[str] = None
    post_agent_hooks: List[str] = None
    
    def __post_init__(self):
        if self.pre_agent_hooks is None:
            self.pre_agent_hooks = []
        if self.post_agent_hooks is None:
            self.post_agent_hooks = []


class AgentProxy:
    """
    Proxy wrapper for agents that adds learning system capabilities
    without modifying the original agent implementation.
    """
    
    def __init__(
        self, 
        agent_instance: Any,
        agent_type: str,
        learning_integration: 'LearningSystemIntegration'
    ):
        """
        Initialize agent proxy
        
        Args:
            agent_instance: Original agent instance
            agent_type: Type/name of agent
            learning_integration: Learning system integration instance
        """
        self._agent = agent_instance
        self._agent_type = agent_type
        self._integration = learning_integration
        self._session_id: Optional[str] = None
        self._context: Optional[RecommendationContext] = None
        
        # Wrap agent methods
        self._wrap_agent_methods()
    
    def _wrap_agent_methods(self):
        """Wrap agent methods to add learning system hooks"""
        # Get all public methods from the agent
        for attr_name in dir(self._agent):
            if not attr_name.startswith('_'):
                attr = getattr(self._agent, attr_name)
                if callable(attr):
                    wrapped_method = self._create_wrapped_method(attr_name, attr)
                    setattr(self, attr_name, wrapped_method)
    
    def _create_wrapped_method(self, method_name: str, original_method: Callable):
        """Create wrapped version of agent method"""
        @wraps(original_method)
        def wrapped_method(*args, **kwargs):
            # Pre-execution hooks
            start_time = datetime.utcnow()
            
            try:
                # Record method invocation
                if self._integration.config.enable_events:
                    self._integration.record_agent_action(
                        self._session_id,
                        self._agent_type,
                        method_name,
                        "started",
                        inputs={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]}
                    )
                
                # Get recommendations if enabled
                if self._integration.config.enable_recommendations and self._context:
                    recommendations = self._integration.get_method_recommendations(
                        self._agent_type, method_name, self._context
                    )
                    if recommendations:
                        # Log recommendations (could be shown to user in UI)
                        logger.info(f"Recommendations for {method_name}: {[r.title for r in recommendations[:3]]}")
                
                # Execute original method
                result = original_method(*args, **kwargs)
                
                # Post-execution hooks
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Record successful execution
                if self._integration.config.enable_events:
                    self._integration.record_agent_action(
                        self._session_id,
                        self._agent_type,
                        method_name,
                        "completed",
                        outputs={'result_type': str(type(result)), 'execution_time': execution_time},
                        success=True,
                        execution_time_ms=execution_time * 1000
                    )
                
                # Extract patterns if enabled
                if self._integration.config.auto_pattern_detection:
                    self._integration.extract_patterns_from_execution(
                        self._agent_type, method_name, args, kwargs, result
                    )
                
                return result
                
            except Exception as e:
                # Record failed execution
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                if self._integration.config.enable_events:
                    self._integration.record_agent_action(
                        self._session_id,
                        self._agent_type,
                        method_name,
                        "failed",
                        error_message=str(e),
                        success=False,
                        execution_time_ms=execution_time * 1000
                    )
                
                # Re-raise the exception
                raise e
        
        return wrapped_method
    
    def start_session(
        self, 
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        goals: Optional[List[str]] = None
    ) -> str:
        """Start learning session for this agent"""
        self._session_id = self._integration.start_agent_session(
            self._agent_type,
            project_id=project_id,
            user_id=user_id,
            goals=goals
        )
        
        # Update context
        self._context = self._integration.create_context_for_session(self._session_id)
        
        return self._session_id
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """End learning session"""
        if self._session_id:
            summary = self._integration.end_agent_session(self._session_id)
            self._session_id = None
            self._context = None
            return summary
        return None
    
    def get_recommendations(self, task_description: str = "") -> List[Dict[str, Any]]:
        """Get recommendations for current context"""
        if self._context:
            self._context.current_task = task_description
            recs = self._integration.get_contextual_recommendations(self._context)
            return [rec.to_dict() for rec in recs]
        return []
    
    def record_decision(
        self,
        title: str,
        description: str,
        rationale: str,
        alternatives: List[str]
    ) -> str:
        """Record a decision made by this agent"""
        if self._session_id:
            return self._integration.record_agent_decision(
                self._session_id,
                title,
                description,
                rationale,
                alternatives
            )
        return ""
    
    def __getattr__(self, name: str):
        """Forward attribute access to wrapped agent"""
        return getattr(self._agent, name)


class LearningSystemIntegration:
    """
    Main integration layer that connects the learning system
    with existing agent infrastructure.
    """
    
    def __init__(
        self,
        config: AgentIntegrationConfig,
        graph_manager: GraphManager,
        memory_manager: MemoryManager,
        ml_pipeline: MLPipeline,
        vector_manager: VectorManager,
        event_store: EventStore,
        recommendation_engine: RecommendationEngine,
        privacy_engine: PrivacyEngine
    ):
        """
        Initialize learning system integration
        
        Args:
            config: Integration configuration
            graph_manager: Knowledge graph manager
            memory_manager: Memory manager
            ml_pipeline: ML pipeline
            vector_manager: Vector manager
            event_store: Event store
            recommendation_engine: Recommendation engine
            privacy_engine: Privacy engine
        """
        self.config = config
        self.graph = graph_manager
        self.memory = memory_manager
        self.ml_pipeline = ml_pipeline
        self.vector_manager = vector_manager
        self.event_store = event_store
        self.recommendation_engine = recommendation_engine
        self.privacy_engine = privacy_engine
        
        # Integration state
        self.wrapped_agents: Dict[str, AgentProxy] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Hooks registry
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
        
        # Background processing
        self.processing_queue: List[Dict[str, Any]] = []
        self.background_processor = None
        
        logger.info(f"Learning system integration initialized in {config.mode.value} mode")
    
    # Agent Wrapping and Registration
    
    def wrap_agent(self, agent_instance: Any, agent_type: str) -> AgentProxy:
        """
        Wrap an existing agent with learning system capabilities
        
        Args:
            agent_instance: Agent instance to wrap
            agent_type: Type/name of the agent
            
        Returns:
            Wrapped agent proxy
        """
        if agent_type in self.wrapped_agents:
            logger.warning(f"Agent {agent_type} already wrapped, returning existing proxy")
            return self.wrapped_agents[agent_type]
        
        proxy = AgentProxy(agent_instance, agent_type, self)
        self.wrapped_agents[agent_type] = proxy
        
        logger.info(f"Wrapped agent: {agent_type}")
        return proxy
    
    def register_agent_class(self, agent_class: Type, agent_type: str) -> Type:
        """
        Create a decorated version of an agent class that includes learning capabilities
        
        Args:
            agent_class: Agent class to decorate
            agent_type: Type/name of the agent
            
        Returns:
            Decorated agent class
        """
        class LearningEnabledAgent(agent_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._learning_proxy = self.wrap_agent(self, agent_type)
            
            def __getattribute__(self, name):
                # Intercept method calls through the learning proxy
                if not name.startswith('_') and hasattr(self._learning_proxy, name):
                    return getattr(self._learning_proxy, name)
                return super().__getattribute__(name)
        
        LearningEnabledAgent.__name__ = f"LearningEnabled{agent_class.__name__}"
        return LearningEnabledAgent
    
    # Session Management
    
    def start_agent_session(
        self,
        agent_type: str,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None
    ) -> str:
        """Start a learning session for an agent"""
        if not self.config.enable_memory:
            return ""
        
        # Start memory session
        session_id = self.memory.start_session(
            agent_type=agent_type,
            project_id=project_id,
            user_id=user_id,
            team_id=team_id,
            goals=goals,
            constraints=constraints
        )
        
        # Store session metadata
        self.active_sessions[session_id] = {
            'agent_type': agent_type,
            'project_id': project_id,
            'user_id': user_id,
            'team_id': team_id,
            'start_time': datetime.utcnow(),
            'action_count': 0,
            'decision_count': 0
        }
        
        # Assign privacy policy if enabled
        if self.config.enable_privacy and project_id:
            self.privacy_engine.assign_policy_to_entity(
                project_id,
                "project",
                self.config.privacy_policy_id
            )
        
        # Record session start event
        if self.config.enable_events:
            event = create_session_started_event(
                session_id=session_id,
                agent_type=agent_type,
                project_id=project_id,
                user_id=user_id,
                goals=goals or []
            )
            self.event_store.publish_event(event)
        
        logger.info(f"Started learning session {session_id} for agent {agent_type}")
        return session_id
    
    def end_agent_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End a learning session"""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        
        # End memory session
        summary = self.memory.end_session(session_id)
        
        # Update session data with final metrics
        session_data.update({
            'end_time': datetime.utcnow(),
            'duration': (datetime.utcnow() - session_data['start_time']).total_seconds(),
            'summary': summary
        })
        
        # Record session end event
        if self.config.enable_events:
            from ..events.event_store import AgentSessionEndedEvent
            event = AgentSessionEndedEvent(
                session_id=session_id,
                agent_type=session_data['agent_type'],
                project_id=session_data['project_id'],
                user_id=session_data['user_id'],
                duration_seconds=session_data['duration'],
                actions_performed=session_data['action_count'],
                decisions_made=session_data['decision_count'],
                summary=summary
            )
            self.event_store.publish_event(event)
        
        # Trigger continuous learning if enabled
        if self.config.continuous_learning:
            self._schedule_background_learning(session_data)
        
        # Clean up
        del self.active_sessions[session_id]
        
        logger.info(f"Ended learning session {session_id}")
        return session_data
    
    def record_agent_action(
        self,
        session_id: Optional[str],
        agent_type: str,
        action_name: str,
        action_status: str,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: float = 0.0
    ):
        """Record an agent action"""
        if not self.config.enable_events or not session_id:
            return
        
        # Update session statistics
        if session_id in self.active_sessions:
            if action_status == "completed" and success:
                self.active_sessions[session_id]['action_count'] += 1
        
        # Record event
        event = create_action_event(
            session_id=session_id,
            action_type=f"{agent_type}.{action_name}",
            action_description=f"{agent_type} executed {action_name}: {action_status}",
            success=success,
            inputs=inputs or {},
            outputs=outputs or {},
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            agent_type=agent_type
        )
        
        # Publish event (async if configured)
        if self.config.async_processing:
            self.processing_queue.append({'type': 'event', 'data': event})
        else:
            self.event_store.publish_event(event)
    
    def record_agent_decision(
        self,
        session_id: str,
        title: str,
        description: str,
        rationale: str,
        alternatives: List[str]
    ) -> str:
        """Record a decision made by an agent"""
        if not self.config.auto_decision_tracking:
            return ""
        
        # Update session statistics
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['decision_count'] += 1
        
        # Record decision in memory
        decision_id = self.memory.record_decision(
            session_id=session_id,
            title=title,
            description=description,
            rationale=rationale,
            alternatives=alternatives
        )
        
        logger.info(f"Recorded decision {decision_id} for session {session_id}")
        return decision_id
    
    # Recommendations and Guidance
    
    def get_contextual_recommendations(
        self, 
        context: RecommendationContext,
        limit: int = 10
    ) -> List['Recommendation']:
        """Get contextual recommendations"""
        if not self.config.enable_recommendations:
            return []
        
        try:
            rec_set = self.recommendation_engine.get_recommendations(context, limit=limit)
            return rec_set.get_top_recommendations(limit)
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def get_method_recommendations(
        self,
        agent_type: str,
        method_name: str,
        context: RecommendationContext
    ) -> List['Recommendation']:
        """Get recommendations specific to a method execution"""
        if not self.config.enable_recommendations:
            return []
        
        # Enhance context with method-specific information
        context.current_task = f"{agent_type}.{method_name}"
        
        return self.get_contextual_recommendations(context, limit=5)
    
    def create_context_for_session(self, session_id: str) -> Optional[RecommendationContext]:
        """Create recommendation context for a session"""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        
        # Get session context from memory
        session_context = self.memory.get_session_context(session_id)
        
        if not session_context:
            return None
        
        # Create recommendation context
        from ..recommendations.recommendation_engine import create_context_from_session
        return create_context_from_session(session_id, self.memory, self.graph)
    
    # Pattern Detection and Learning
    
    def extract_patterns_from_execution(
        self,
        agent_type: str,
        method_name: str,
        args: tuple,
        kwargs: dict,
        result: Any
    ):
        """Extract patterns from method execution"""
        if not self.config.auto_pattern_detection:
            return
        
        # This is a simplified pattern extraction
        # In practice, would use more sophisticated analysis
        
        pattern_data = {
            'agent_type': agent_type,
            'method_name': method_name,
            'input_signature': str(args)[:200] + str(kwargs)[:200],
            'result_type': str(type(result)),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Queue for background processing
        if self.config.async_processing:
            self.processing_queue.append({
                'type': 'pattern_extraction',
                'data': pattern_data
            })
    
    def trigger_model_retraining(self, model_types: Optional[List[str]] = None):
        """Trigger retraining of ML models"""
        if not self.config.continuous_learning:
            return
        
        # Queue retraining task
        task = {
            'type': 'model_retraining',
            'data': {
                'model_types': model_types,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        if self.config.async_processing:
            self.processing_queue.append(task)
        else:
            self._process_retraining_task(task['data'])
    
    # Background Processing
    
    async def start_background_processing(self):
        """Start background processing of queued tasks"""
        if not self.config.async_processing:
            return
        
        logger.info("Starting background processing")
        
        while True:
            try:
                if self.processing_queue:
                    # Process batch of tasks
                    batch_size = min(self.config.batch_size, len(self.processing_queue))
                    batch = self.processing_queue[:batch_size]
                    self.processing_queue = self.processing_queue[batch_size:]
                    
                    await self._process_task_batch(batch)
                
                # Wait before next processing cycle
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Background processing error: {e}")
                await asyncio.sleep(5)
    
    async def _process_task_batch(self, batch: List[Dict[str, Any]]):
        """Process batch of background tasks"""
        for task in batch:
            try:
                task_type = task['type']
                task_data = task['data']
                
                if task_type == 'event':
                    self.event_store.publish_event(task_data)
                elif task_type == 'pattern_extraction':
                    await self._process_pattern_extraction(task_data)
                elif task_type == 'model_retraining':
                    await self._process_retraining_task(task_data)
                    
            except Exception as e:
                logger.error(f"Failed to process task {task['type']}: {e}")
    
    async def _process_pattern_extraction(self, data: Dict[str, Any]):
        """Process pattern extraction in background"""
        # Store pattern data for later analysis
        pattern_content = {
            'extracted_pattern': data,
            'analysis_pending': True
        }
        
        self.memory.store_memory(
            MemoryType.PATTERN_USAGE,
            ContextScope.GLOBAL,
            pattern_content,
            tags=['pattern_extraction', 'background_processing']
        )
    
    def _process_retraining_task(self, data: Dict[str, Any]):
        """Process model retraining task"""
        try:
            model_types = data.get('model_types', [])
            
            if not model_types:
                # Retrain all models
                self.ml_pipeline.retrain_all_models()
            else:
                # Retrain specific models
                for model_type in model_types:
                    try:
                        from ..learning.ml_pipeline import ModelType
                        mt = ModelType(model_type)
                        training_data = self.ml_pipeline.collect_training_data(mt)
                        self.ml_pipeline.train_model(mt, training_data)
                    except Exception as e:
                        logger.error(f"Failed to retrain model {model_type}: {e}")
            
            logger.info("Model retraining completed")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
    
    def _schedule_background_learning(self, session_data: Dict[str, Any]):
        """Schedule background learning tasks after session"""
        # Check if enough new data for retraining
        if session_data.get('action_count', 0) > 10:
            self.processing_queue.append({
                'type': 'model_retraining',
                'data': {
                    'model_types': ['success_predictor', 'agent_selector'],
                    'trigger': 'session_end',
                    'session_data': session_data
                }
            })
    
    # Hooks and Extensibility
    
    def add_pre_hook(self, hook: Callable):
        """Add pre-execution hook"""
        self.pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable):
        """Add post-execution hook"""
        self.post_hooks.append(hook)
    
    def remove_hook(self, hook: Callable):
        """Remove a hook"""
        self.pre_hooks = [h for h in self.pre_hooks if h != hook]
        self.post_hooks = [h for h in self.post_hooks if h != hook]
    
    # Integration Status and Metrics
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration system status"""
        return {
            'config': asdict(self.config),
            'wrapped_agents': len(self.wrapped_agents),
            'active_sessions': len(self.active_sessions),
            'processing_queue_size': len(self.processing_queue),
            'components_status': {
                'memory': self.config.enable_memory,
                'learning': self.config.enable_learning,
                'recommendations': self.config.enable_recommendations,
                'privacy': self.config.enable_privacy,
                'events': self.config.enable_events
            }
        }
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Get metrics about active sessions"""
        if not self.active_sessions:
            return {'active_sessions': 0}
        
        # Calculate metrics
        session_durations = []
        action_counts = []
        decision_counts = []
        agent_types = []
        
        for session_data in self.active_sessions.values():
            duration = (datetime.utcnow() - session_data['start_time']).total_seconds()
            session_durations.append(duration)
            action_counts.append(session_data['action_count'])
            decision_counts.append(session_data['decision_count'])
            agent_types.append(session_data['agent_type'])
        
        from collections import Counter
        import statistics
        
        return {
            'active_sessions': len(self.active_sessions),
            'avg_session_duration': statistics.mean(session_durations) if session_durations else 0,
            'total_actions': sum(action_counts),
            'total_decisions': sum(decision_counts),
            'avg_actions_per_session': statistics.mean(action_counts) if action_counts else 0,
            'avg_decisions_per_session': statistics.mean(decision_counts) if decision_counts else 0,
            'agent_type_distribution': dict(Counter(agent_types))
        }


# Decorators for easy integration
def learning_enabled(
    agent_type: str,
    integration: LearningSystemIntegration
):
    """Decorator to enable learning for a function or class"""
    def decorator(func_or_class):
        if inspect.isclass(func_or_class):
            # Class decorator
            return integration.register_agent_class(func_or_class, agent_type)
        else:
            # Function decorator
            @wraps(func_or_class)
            def wrapper(*args, **kwargs):
                # Create temporary session for function
                session_id = integration.start_agent_session(agent_type)
                try:
                    result = func_or_class(*args, **kwargs)
                    return result
                finally:
                    integration.end_agent_session(session_id)
            return wrapper
    return decorator


# Factory function for easy setup
def create_learning_integration(
    config: Optional[AgentIntegrationConfig] = None,
    graph_uri: str = "bolt://localhost:7687",
    graph_username: str = "neo4j",
    graph_password: str = "password"
) -> LearningSystemIntegration:
    """
    Factory function to create a complete learning system integration
    
    Args:
        config: Integration configuration
        graph_uri: Neo4j URI
        graph_username: Neo4j username
        graph_password: Neo4j password
        
    Returns:
        Configured learning system integration
    """
    if config is None:
        config = AgentIntegrationConfig()
    
    # Initialize all components
    graph_manager = GraphManager(graph_uri, graph_username, graph_password)
    memory_manager = MemoryManager(graph_manager)
    ml_pipeline = MLPipeline(graph_manager, memory_manager)
    
    # Vector manager with default config
    from ..embeddings.vector_manager import VectorManager, EMBEDDING_CONFIGS, VectorDatabase
    vector_manager = VectorManager(
        graph_manager,
        EMBEDDING_CONFIGS['sentence_transformer_all'],
        VectorDatabase.IN_MEMORY
    )
    
    event_store = EventStore()
    privacy_engine = PrivacyEngine(graph_manager, memory_manager, ml_pipeline)
    recommendation_engine = RecommendationEngine(
        graph_manager, memory_manager, ml_pipeline, vector_manager, event_store
    )
    
    # Create integration
    integration = LearningSystemIntegration(
        config,
        graph_manager,
        memory_manager,
        ml_pipeline,
        vector_manager,
        event_store,
        recommendation_engine,
        privacy_engine
    )
    
    return integration