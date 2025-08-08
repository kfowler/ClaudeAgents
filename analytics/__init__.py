"""
Agent Usage Analytics Framework

A comprehensive system for tracking agent effectiveness, collecting user feedback,
and optimizing agent recommendations in the Claude Code ecosystem.
"""

from .collector import (
    AnalyticsCollector,
    ProjectContext,
    UserRequest,
    AgentInvocation,
    AgentSession,
    analytics_session,
    track_agent_use,
    record_user_rating
)

from .feedback import (
    FeedbackCollector,
    FeedbackTrigger,
    FeedbackType,
    FeedbackPrompt,
    ImplicitTracker,
    setup_feedback_collection,
    create_feedback_hooks
)

from .metrics import (
    AnalyticsEngine,
    MetricType,
    AgentMetric,
    RecommendationInsight,
    get_agent_leaderboard,
    get_recommendation_accuracy,
    get_user_satisfaction_summary
)

from .dashboard import (
    DashboardBuilder,
    DashboardConfiguration,
    DashboardTab,
    ChartConfiguration,
    ChartType,
    TimeRange,
    DashboardDataProvider,
    generate_dashboard_config
)

from .integration_example import (
    AgentAnalyticsManager,
    AnalyticsContext,
    create_production_config,
    create_development_config,
    create_minimal_config
)

__version__ = "1.0.0"

__all__ = [
    # Core data collection
    "AnalyticsCollector",
    "ProjectContext", 
    "UserRequest",
    "AgentInvocation",
    "AgentSession",
    "analytics_session",
    "track_agent_use",
    "record_user_rating",
    
    # Feedback collection
    "FeedbackCollector",
    "FeedbackTrigger",
    "FeedbackType", 
    "FeedbackPrompt",
    "ImplicitTracker",
    "setup_feedback_collection",
    "create_feedback_hooks",
    
    # Analytics and metrics
    "AnalyticsEngine",
    "MetricType",
    "AgentMetric",
    "RecommendationInsight",
    "get_agent_leaderboard",
    "get_recommendation_accuracy",
    "get_user_satisfaction_summary",
    
    # Dashboard and visualization
    "DashboardBuilder",
    "DashboardConfiguration",
    "DashboardTab", 
    "ChartConfiguration",
    "ChartType",
    "TimeRange",
    "DashboardDataProvider",
    "generate_dashboard_config",
    
    # Integration helpers
    "AgentAnalyticsManager",
    "AnalyticsContext",
    "create_production_config",
    "create_development_config", 
    "create_minimal_config"
]