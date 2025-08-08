"""
Integration Example: How to integrate analytics with the existing agent system

This file demonstrates how to integrate the analytics framework into Claude Code
without disrupting existing workflows.
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Import our analytics components
from .collector import AnalyticsCollector, analytics_session, track_agent_use
from .metrics import AnalyticsEngine, get_agent_leaderboard
from .feedback import FeedbackCollector, setup_feedback_collection, ImplicitTracker
from .dashboard import DashboardBuilder, DashboardDataProvider

logger = logging.getLogger(__name__)

class AgentAnalyticsManager:
    """
    Main integration point for analytics in the agent system
    """
    
    def __init__(self, 
                 db_url: Optional[str] = None,
                 enable_feedback: bool = True,
                 analytics_config: Dict[str, Any] = None):
        
        config = analytics_config or {}
        
        # Initialize components
        self.analytics_collector = AnalyticsCollector(
            db_url=db_url,
            redis_url=config.get('redis_url'),
            local_storage_path=config.get('local_storage_path', './analytics_data'),
            buffer_size=config.get('buffer_size', 50),
            flush_interval=config.get('flush_interval', 120)
        )
        
        self.feedback_collector = None
        self.analytics_engine = None
        self.dashboard_provider = None
        
        self.enable_feedback = enable_feedback
        self.active_sessions = {}  # session_id -> session info
        
    async def initialize(self):
        """Initialize all analytics components"""
        
        try:
            # Initialize data collection
            await self.analytics_collector.initialize()
            
            # Set up feedback collection if enabled
            if self.enable_feedback:
                self.feedback_collector = await setup_feedback_collection(self.analytics_collector)
            
            # Initialize analytics engine if we have a database
            if self.analytics_collector.db_pool:
                self.analytics_engine = AnalyticsEngine(self.analytics_collector.db_pool)
                self.dashboard_provider = DashboardDataProvider(self.analytics_collector.db_pool)
            
            logger.info("Agent analytics system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics: {e}")
            logger.info("Analytics will operate in degraded mode")
    
    async def shutdown(self):
        """Clean shutdown of analytics system"""
        await self.analytics_collector.shutdown()
    
    # Integration points for the agent system
    
    async def start_agent_session(self, user_id: str, project_path: str = ".", context: Dict[str, Any] = None) -> str:
        """Start a new agent session with analytics tracking"""
        
        try:
            session = await self.analytics_collector.start_session(user_id, project_path)
            session_id = session.session_id
            
            # Store additional context
            self.active_sessions[session_id] = {
                'start_time': datetime.now(timezone.utc),
                'user_id': user_id,
                'project_path': project_path,
                'context': context or {},
                'invocations': []
            }
            
            # Start feedback tracking if enabled
            if self.feedback_collector:
                self.feedback_collector.start_session_tracking(session_id)
            
            logger.debug(f"Started analytics session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start analytics session: {e}")
            # Return a fallback session ID to avoid breaking the workflow
            return f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def track_agent_invocation(self, 
                                   session_id: str,
                                   agent_name: str, 
                                   user_request: str,
                                   invocation_reason: str = "automatic",
                                   context_match_score: float = 0.0) -> str:
        """Track the start of an agent invocation"""
        
        try:
            invocation = await self.analytics_collector.record_invocation(
                session_id=session_id,
                agent_name=agent_name,
                user_request_text=user_request,
                invocation_reason=invocation_reason,
                context_match_score=context_match_score
            )
            
            # Update session tracking
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['invocations'].append({
                    'invocation_id': invocation.invocation_id,
                    'agent_name': agent_name,
                    'start_time': invocation.start_time
                })
            
            logger.debug(f"Tracking agent invocation: {invocation.invocation_id}")
            return invocation.invocation_id
            
        except Exception as e:
            logger.error(f"Failed to track agent invocation: {e}")
            return f"fallback_inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def complete_agent_invocation(self,
                                      invocation_id: str,
                                      success: bool,
                                      error_info: Optional[Dict[str, Any]] = None,
                                      output_metrics: Optional[Dict[str, Any]] = None):
        """Mark an agent invocation as complete"""
        
        try:
            success_status = "success" if success else "failed"
            
            await self.analytics_collector.complete_invocation(
                invocation_id=invocation_id,
                success_status=success_status,
                tokens_used=output_metrics.get('tokens_used', 0) if output_metrics else 0,
                files_modified=output_metrics.get('files_modified', 0) if output_metrics else 0,
                lines_added=output_metrics.get('lines_added', 0) if output_metrics else 0,
                lines_removed=output_metrics.get('lines_removed', 0) if output_metrics else 0,
                quality_score=output_metrics.get('quality_score') if output_metrics else None,
                error_type=error_info.get('type') if error_info else None,
                error_message=error_info.get('message') if error_info else None
            )
            
            logger.debug(f"Completed agent invocation: {invocation_id} ({success_status})")
            
        except Exception as e:
            logger.error(f"Failed to complete agent invocation: {e}")
    
    async def record_user_feedback(self,
                                 session_id: str,
                                 invocation_id: Optional[str] = None,
                                 rating: Optional[int] = None,
                                 feedback_text: Optional[str] = None,
                                 feedback_type: str = "explicit"):
        """Record explicit user feedback"""
        
        try:
            await self.analytics_collector.record_feedback(
                session_id=session_id,
                invocation_id=invocation_id,
                feedback_type=feedback_type,
                rating=rating,
                feedback_text=feedback_text
            )
            
            logger.debug(f"Recorded user feedback for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to record user feedback: {e}")
    
    async def end_agent_session(self,
                              session_id: str,
                              outcome: str = "completed",
                              user_satisfaction: Optional[int] = None):
        """End an agent session"""
        
        try:
            await self.analytics_collector.end_session(
                session_id=session_id,
                final_outcome=outcome,
                user_satisfaction_score=user_satisfaction
            )
            
            # End feedback tracking
            if self.feedback_collector:
                self.feedback_collector.end_session_tracking(session_id, outcome)
            
            # Clean up session tracking
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            logger.debug(f"Ended analytics session: {session_id} ({outcome})")
            
        except Exception as e:
            logger.error(f"Failed to end analytics session: {e}")
    
    # Implicit behavior tracking
    
    def track_code_modification(self, session_id: str, agent_name: str, time_to_modify: int, extent: str):
        """Track when user modifies agent-generated code"""
        if self.feedback_collector:
            ImplicitTracker.track_code_modification(
                self.feedback_collector, session_id, agent_name, time_to_modify, extent
            )
    
    def track_agent_override(self, session_id: str, recommended_agent: str, selected_agent: str, reason: str):
        """Track when user overrides agent recommendation"""
        if self.feedback_collector:
            ImplicitTracker.track_agent_switching(
                self.feedback_collector, session_id, recommended_agent, selected_agent, reason
            )
    
    def track_task_abandonment(self, session_id: str, agent_name: str, duration: int):
        """Track when user abandons a task mid-way"""
        if self.feedback_collector:
            self.feedback_collector.track_implicit_signal(
                'task_abandonment',
                session_id,
                {'agent': agent_name, 'duration': duration},
                confidence=0.8
            )
    
    # Analytics and insights
    
    async def get_agent_recommendations(self, user_id: str, request_text: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get agent recommendations based on analytics"""
        
        if not self.analytics_engine:
            return []
        
        try:
            # Get user preferences
            user_prefs = await self.analytics_engine.generate_user_preference_profiles(user_id)
            
            # Get top-performing agents
            top_agents = await get_agent_leaderboard(self.analytics_collector.db_pool, days=30)
            
            # Simple recommendation logic (would be more sophisticated in practice)
            recommendations = []
            
            for agent in top_agents[:5]:  # Top 5 agents
                confidence = agent['effectiveness_score'] * 0.8  # Base confidence
                
                # Boost if user has used this agent successfully before
                if user_prefs and agent['agent_name'] in user_prefs.get('preferred_agents', []):
                    confidence += 0.2
                
                recommendations.append({
                    'agent_name': agent['agent_name'],
                    'confidence': min(confidence, 1.0),
                    'reasoning': f"High effectiveness ({agent['effectiveness_score']:.1%}) with {agent['usage_count']} uses",
                    'expected_duration': agent.get('avg_duration', 300)
                })
            
            return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get agent recommendations: {e}")
            return []
    
    async def get_dashboard_data(self, chart_id: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data for dashboard charts"""
        
        if not self.dashboard_provider:
            return {"error": "Dashboard provider not available"}
        
        try:
            # This would normally look up the chart configuration
            # For now, return a simple example
            return {
                "chart_id": chart_id,
                "data": [],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    async def generate_insights_report(self) -> Dict[str, Any]:
        """Generate analytics insights report"""
        
        if not self.analytics_engine:
            return {"error": "Analytics engine not available"}
        
        try:
            return await self.analytics_engine.export_insights_report()
            
        except Exception as e:
            logger.error(f"Failed to generate insights report: {e}")
            return {"error": str(e)}

# Example integration with existing agent workflow
async def example_agent_workflow_integration():
    """
    Example showing how to integrate analytics into an existing agent workflow
    """
    
    # Initialize analytics manager
    analytics = AgentAnalyticsManager(
        db_url="postgresql://user:pass@localhost/analytics",  # Optional
        enable_feedback=True,
        analytics_config={
            'buffer_size': 20,
            'flush_interval': 60
        }
    )
    
    await analytics.initialize()
    
    try:
        # Start a session
        session_id = await analytics.start_agent_session(
            user_id="user123",
            project_path="/path/to/project",
            context={"source": "claude_code", "platform": "vscode"}
        )
        
        # Track agent invocation
        invocation_id = await analytics.track_agent_invocation(
            session_id=session_id,
            agent_name="full-stack-architect",
            user_request="Create a React component for user authentication",
            invocation_reason="automatic",
            context_match_score=0.85
        )
        
        # Simulate agent work (this would be the actual agent execution)
        await asyncio.sleep(2)  # Simulate work
        
        # Complete the invocation
        await analytics.complete_agent_invocation(
            invocation_id=invocation_id,
            success=True,
            output_metrics={
                'tokens_used': 1500,
                'files_modified': 3,
                'lines_added': 120,
                'lines_removed': 15,
                'quality_score': 0.9
            }
        )
        
        # Record user feedback
        await analytics.record_user_feedback(
            session_id=session_id,
            invocation_id=invocation_id,
            rating=4,
            feedback_text="Good solution, minor tweaks needed"
        )
        
        # Track implicit behavior
        analytics.track_code_modification(
            session_id=session_id,
            agent_name="full-stack-architect",
            time_to_modify=300,  # 5 minutes later
            extent="minor"
        )
        
        # End session
        await analytics.end_agent_session(
            session_id=session_id,
            outcome="completed",
            user_satisfaction=4
        )
        
        # Get insights
        insights = await analytics.generate_insights_report()
        print("Analytics Insights:", json.dumps(insights, indent=2, default=str))
        
    finally:
        await analytics.shutdown()

# Configuration helpers for different deployment scenarios
def create_production_config(db_url: str, redis_url: str = None) -> Dict[str, Any]:
    """Production configuration with full database backend"""
    return {
        'db_url': db_url,
        'redis_url': redis_url,
        'local_storage_path': '/var/lib/claude-analytics',
        'buffer_size': 100,
        'flush_interval': 60,
        'enable_feedback': True
    }

def create_development_config() -> Dict[str, Any]:
    """Development configuration with local storage fallback"""
    return {
        'db_url': None,  # Will use local storage
        'local_storage_path': './dev_analytics',
        'buffer_size': 10,
        'flush_interval': 30,
        'enable_feedback': True
    }

def create_minimal_config() -> Dict[str, Any]:
    """Minimal configuration for environments with restricted resources"""
    return {
        'db_url': None,
        'local_storage_path': './analytics',
        'buffer_size': 5,
        'flush_interval': 120,
        'enable_feedback': False  # Disable feedback collection
    }

# Context manager for easy integration
class AnalyticsContext:
    """Context manager for analytics sessions"""
    
    def __init__(self, analytics_manager: AgentAnalyticsManager, user_id: str, project_path: str = "."):
        self.analytics = analytics_manager
        self.user_id = user_id
        self.project_path = project_path
        self.session_id = None
    
    async def __aenter__(self):
        self.session_id = await self.analytics.start_agent_session(self.user_id, self.project_path)
        return self.session_id
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            outcome = "error" if exc_type else "completed"
            await self.analytics.end_agent_session(self.session_id, outcome)

# Example usage with context manager
async def example_with_context_manager():
    """Example using the context manager for cleaner code"""
    
    analytics = AgentAnalyticsManager()
    await analytics.initialize()
    
    try:
        async with AnalyticsContext(analytics, "user123", "/path/to/project") as session_id:
            # Your agent workflow here
            invocation_id = await analytics.track_agent_invocation(
                session_id, "security-audit-specialist", "Review authentication code"
            )
            
            # Agent work happens here
            await asyncio.sleep(1)
            
            await analytics.complete_agent_invocation(invocation_id, True)
            
    finally:
        await analytics.shutdown()

if __name__ == "__main__":
    # Run the example
    asyncio.run(example_agent_workflow_integration())