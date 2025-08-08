"""
Advanced Context Sharing and Learning System

A comprehensive system that enables AI agents to build persistent knowledge
and continuously improve through experience, featuring:

- Knowledge Graph: Persistent knowledge representation using Neo4j
- Cross-Session Memory: Agents remember past interactions and build on previous work
- Decision History Tracking: Complete audit trail of architectural decisions and outcomes
- Pattern Recognition: Identification and reuse of successful patterns
- Team Knowledge: Shared understanding across development team members
- Continuous Learning: ML pipeline for improving agent effectiveness
- Preference Learning: Adaptation to individual developer and team preferences
- Context-Aware Recommendations: Leveraging project history for better suggestions
- Success Prediction: ML models predicting agent effectiveness for specific contexts
- Anti-Pattern Detection: Prevention of repeated mistakes
- Privacy-Preserving Learning: Differential privacy and data isolation
- Event Sourcing: Complete history tracking with audit trails
- Integration Layer: Seamless integration with existing agent systems
- Analytics Dashboard: Comprehensive monitoring and visualization

Usage:
    from learning_system import create_learning_integration
    
    # Create integrated learning system
    integration = create_learning_integration()
    
    # Wrap existing agents with learning capabilities
    learning_agent = integration.wrap_agent(my_agent, "my_agent_type")
    
    # Start learning session
    session_id = learning_agent.start_session(project_id="proj123")
    
    # Agent automatically records actions, decisions, and learns patterns
    result = learning_agent.some_method()
    
    # Get contextual recommendations
    recommendations = learning_agent.get_recommendations("implement authentication")
    
    # Record important decisions
    decision_id = learning_agent.record_decision(
        title="Choose Authentication Method",
        description="Deciding between OAuth2 and JWT",
        rationale="OAuth2 provides better security and scalability",
        alternatives=["JWT tokens", "Session-based auth"]
    )
    
    # End session (triggers learning and pattern extraction)
    summary = learning_agent.end_session()

Enterprise Features:
- Privacy-preserving cross-project learning with differential privacy
- Configurable data isolation and access controls
- Comprehensive audit trails and compliance monitoring
- Scalable vector databases for semantic similarity
- Real-time analytics and monitoring dashboard
- Background processing for continuous learning
- Integration hooks for existing development workflows
"""

from .integration.agent_integration import (
    create_learning_integration,
    LearningSystemIntegration,
    AgentProxy,
    AgentIntegrationConfig,
    IntegrationMode,
    learning_enabled
)

from .knowledge_graph.graph_manager import GraphManager
from .memory.memory_manager import MemoryManager, MemoryType, ContextScope
from .learning.ml_pipeline import MLPipeline, ModelType
from .embeddings.vector_manager import VectorManager, EMBEDDING_CONFIGS
from .events.event_store import EventStore, EventType
from .recommendations.recommendation_engine import (
    RecommendationEngine,
    RecommendationContext,
    RecommendationType
)
from .privacy.privacy_engine import PrivacyEngine, PrivacyLevel
from .dashboard.analytics_dashboard import AnalyticsDashboard, create_analytics_dashboard

__version__ = "1.0.0"
__all__ = [
    # Main integration
    "create_learning_integration",
    "LearningSystemIntegration", 
    "AgentProxy",
    "AgentIntegrationConfig",
    "IntegrationMode",
    "learning_enabled",
    
    # Core components
    "GraphManager",
    "MemoryManager",
    "MLPipeline", 
    "VectorManager",
    "EventStore",
    "RecommendationEngine",
    "PrivacyEngine",
    "AnalyticsDashboard",
    
    # Enums and types
    "MemoryType",
    "ContextScope", 
    "ModelType",
    "EventType",
    "RecommendationType",
    "PrivacyLevel",
    
    # Utilities
    "EMBEDDING_CONFIGS",
    "RecommendationContext",
    "create_analytics_dashboard",
]