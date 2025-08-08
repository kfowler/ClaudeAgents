"""
Analytics Metrics Calculation and Reporting

This module provides comprehensive analytics queries and metric calculations
for agent usage optimization and recommendation engine improvements.
"""

import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import asyncpg
    import numpy as np
    import pandas as pd
except ImportError:
    # Graceful degradation
    asyncpg = None
    np = None
    pd = None

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics we can calculate"""
    USAGE = "usage"
    EFFECTIVENESS = "effectiveness"
    SATISFACTION = "satisfaction"
    PERFORMANCE = "performance"
    RECOMMENDATION = "recommendation"

@dataclass
class AgentMetric:
    """Standard agent metric structure"""
    agent_name: str
    metric_type: MetricType
    value: float
    period: str
    context: Dict[str, Any]
    calculated_at: datetime

@dataclass
class RecommendationInsight:
    """Insights for improving agent recommendations"""
    insight_type: str
    confidence: float
    description: str
    suggested_action: str
    supporting_data: Dict[str, Any]

class AnalyticsEngine:
    """
    Main analytics engine for calculating metrics and generating insights
    """
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        
    async def calculate_agent_effectiveness(self, 
                                          time_period: int = 30, 
                                          min_samples: int = 5) -> List[AgentMetric]:
        """
        Calculate comprehensive effectiveness metrics for all agents
        
        Args:
            time_period: Number of days to analyze
            min_samples: Minimum number of invocations required
            
        Returns:
            List of effectiveness metrics per agent
        """
        
        query = """
        WITH agent_stats AS (
            SELECT 
                agent_name,
                COUNT(*) as total_invocations,
                AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(duration_seconds) as avg_duration,
                AVG(quality_score) as avg_quality,
                AVG(context_match_score) as avg_context_match,
                AVG(tokens_used) as avg_tokens,
                SUM(lines_added + lines_removed) as total_code_changes,
                STDDEV(duration_seconds) as duration_stddev,
                COUNT(DISTINCT session_id) as unique_sessions,
                
                -- Time-based patterns
                EXTRACT(hour FROM start_time) as hour_of_day,
                AVG(CASE WHEN EXTRACT(dow FROM start_time) IN (0,6) THEN 1.0 ELSE 0.0 END) as weekend_usage,
                
                -- Error analysis
                COUNT(CASE WHEN error_type IS NOT NULL THEN 1 END) as error_count,
                array_agg(DISTINCT error_type) FILTER (WHERE error_type IS NOT NULL) as error_types
                
            FROM agent_invocations 
            WHERE created_at >= NOW() - INTERVAL '%s days'
            GROUP BY agent_name
            HAVING COUNT(*) >= %s
        ),
        satisfaction_stats AS (
            SELECT 
                ai.agent_name,
                AVG(uf.rating) as avg_user_rating,
                COUNT(uf.rating) as rating_count,
                AVG(CASE WHEN uf.user_correction IS NOT NULL THEN 1.0 ELSE 0.0 END) as correction_rate,
                COUNT(CASE WHEN uf.feedback_type = 'suggestion' THEN 1 END) as suggestion_count
            FROM agent_invocations ai
            LEFT JOIN user_feedback uf ON ai.invocation_id = uf.invocation_id
            WHERE ai.created_at >= NOW() - INTERVAL '%s days'
            GROUP BY ai.agent_name
        )
        SELECT 
            a.*,
            COALESCE(s.avg_user_rating, 3.0) as user_rating,
            COALESCE(s.rating_count, 0) as feedback_volume,
            COALESCE(s.correction_rate, 0.0) as user_correction_rate,
            COALESCE(s.suggestion_count, 0) as improvement_suggestions,
            
            -- Calculated effectiveness scores
            (success_rate * 0.3 + 
             LEAST(avg_quality, 1.0) * 0.25 + 
             avg_context_match * 0.2 +
             GREATEST(0, 1 - (avg_duration / 300.0)) * 0.15 +  -- Penalty for >5min tasks
             COALESCE(s.avg_user_rating / 5.0, 0.6) * 0.1) as effectiveness_score,
             
            -- Efficiency score
            (total_code_changes / GREATEST(avg_duration, 1.0)) as code_velocity,
            (avg_tokens / GREATEST(avg_duration, 1.0)) as token_efficiency
            
        FROM agent_stats a
        LEFT JOIN satisfaction_stats s ON a.agent_name = s.agent_name
        ORDER BY effectiveness_score DESC
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, time_period, min_samples, time_period)
        
        metrics = []
        for row in rows:
            # Core effectiveness metric
            metrics.append(AgentMetric(
                agent_name=row['agent_name'],
                metric_type=MetricType.EFFECTIVENESS,
                value=row['effectiveness_score'],
                period=f"{time_period}d",
                context={
                    'total_invocations': row['total_invocations'],
                    'success_rate': row['success_rate'],
                    'avg_quality': row['avg_quality'],
                    'user_rating': row['user_rating'],
                    'context_match': row['avg_context_match'],
                    'error_types': row['error_types'] or []
                },
                calculated_at=datetime.now(timezone.utc)
            ))
            
            # Performance metrics
            if row['avg_duration']:
                metrics.append(AgentMetric(
                    agent_name=row['agent_name'],
                    metric_type=MetricType.PERFORMANCE,
                    value=row['code_velocity'],
                    period=f"{time_period}d",
                    context={
                        'avg_duration': row['avg_duration'],
                        'total_code_changes': row['total_code_changes'],
                        'token_efficiency': row['token_efficiency']
                    },
                    calculated_at=datetime.now(timezone.utc)
                ))
        
        return metrics
    
    async def analyze_agent_combinations(self, time_period: int = 60) -> List[Dict[str, Any]]:
        """
        Analyze effectiveness of agent combinations and workflows
        """
        
        query = """
        WITH combination_performance AS (
            SELECT 
                primary_agent,
                secondary_agents,
                combination_pattern,
                COUNT(*) as usage_count,
                AVG(CASE WHEN combination_success THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(synergy_score) as avg_synergy,
                AVG(total_duration_seconds) as avg_duration,
                AVG(user_intervention_count) as avg_interventions,
                
                -- Context analysis
                array_agg(DISTINCT 
                    CASE WHEN as_session.project_context->>'domain' IS NOT NULL 
                         THEN as_session.project_context->>'domain' 
                    END
                ) FILTER (WHERE as_session.project_context->>'domain' IS NOT NULL) as domains,
                
                array_agg(DISTINCT 
                    CASE WHEN as_session.project_context->>'project_size' IS NOT NULL 
                         THEN as_session.project_context->>'project_size' 
                    END
                ) FILTER (WHERE as_session.project_context->>'project_size' IS NOT NULL) as project_sizes
                
            FROM agent_combinations ac
            JOIN agent_sessions as_session ON ac.session_id = as_session.session_id
            WHERE ac.created_at >= NOW() - INTERVAL '%s days'
            GROUP BY primary_agent, secondary_agents, combination_pattern
            HAVING COUNT(*) >= 3
        ),
        user_satisfaction AS (
            SELECT 
                ac.primary_agent,
                ac.secondary_agents,
                ac.combination_pattern,
                AVG(as_session.user_satisfaction_score) as avg_satisfaction
            FROM agent_combinations ac
            JOIN agent_sessions as_session ON ac.session_id = as_session.session_id
            WHERE ac.created_at >= NOW() - INTERVAL '%s days'
            AND as_session.user_satisfaction_score IS NOT NULL
            GROUP BY ac.primary_agent, ac.secondary_agents, ac.combination_pattern
        )
        SELECT 
            cp.*,
            COALESCE(us.avg_satisfaction, 3.0) as user_satisfaction,
            
            -- Calculate recommendation score
            (success_rate * 0.4 + 
             avg_synergy * 0.3 + 
             GREATEST(0, 1 - (avg_duration / 1800.0)) * 0.2 +  -- Penalty for >30min combinations
             COALESCE(us.avg_satisfaction / 5.0, 0.6) * 0.1) as recommendation_score
             
        FROM combination_performance cp
        LEFT JOIN user_satisfaction us ON (
            cp.primary_agent = us.primary_agent AND 
            cp.secondary_agents = us.secondary_agents AND
            cp.combination_pattern = us.combination_pattern
        )
        ORDER BY recommendation_score DESC, usage_count DESC
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, time_period, time_period)
        
        return [dict(row) for row in rows]
    
    async def detect_optimization_opportunities(self) -> List[RecommendationInsight]:
        """
        Use ML-style analysis to detect optimization opportunities
        """
        insights = []
        
        # 1. Underutilized high-performing agents
        underutilized_query = """
        WITH recent_performance AS (
            SELECT 
                agent_name,
                COUNT(*) as usage_count,
                AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(quality_score) as avg_quality
            FROM agent_invocations 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            GROUP BY agent_name
            HAVING AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) > 0.8
            AND AVG(quality_score) > 0.7
        )
        SELECT agent_name, usage_count, success_rate, avg_quality
        FROM recent_performance
        ORDER BY usage_count ASC, success_rate DESC
        LIMIT 5
        """
        
        async with self.db_pool.acquire() as conn:
            underutilized = await conn.fetch(underutilized_query)
        
        for row in underutilized:
            if row['usage_count'] < 10:  # Arbitrarily low usage threshold
                insights.append(RecommendationInsight(
                    insight_type="underutilized_agent",
                    confidence=0.8,
                    description=f"Agent '{row['agent_name']}' has high success rate ({row['success_rate']:.1%}) but low usage",
                    suggested_action=f"Promote {row['agent_name']} for relevant use cases",
                    supporting_data={
                        'agent': row['agent_name'],
                        'success_rate': row['success_rate'],
                        'usage_count': row['usage_count'],
                        'quality_score': row['avg_quality']
                    }
                ))
        
        # 2. Context mismatch patterns
        context_mismatch_query = """
        SELECT 
            agent_name,
            AVG(context_match_score) as avg_match,
            COUNT(*) as invocation_count,
            AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate
        FROM agent_invocations 
        WHERE created_at >= NOW() - INTERVAL '30 days'
        AND context_match_score < 0.6
        GROUP BY agent_name
        HAVING COUNT(*) >= 5
        ORDER BY avg_match ASC
        """
        
        mismatch_results = await conn.fetch(context_mismatch_query)
        
        for row in mismatch_results:
            insights.append(RecommendationInsight(
                insight_type="context_mismatch",
                confidence=0.7,
                description=f"Agent '{row['agent_name']}' frequently used in poor-match contexts",
                suggested_action="Improve context detection or agent selection logic",
                supporting_data={
                    'agent': row['agent_name'],
                    'avg_context_match': row['avg_match'],
                    'invocation_count': row['invocation_count'],
                    'success_rate': row['success_rate']
                }
            ))
        
        # 3. High-correction agents (users frequently fix their output)
        correction_query = """
        SELECT 
            ai.agent_name,
            COUNT(uf.feedback_id) as feedback_count,
            AVG(CASE WHEN uf.user_correction IS NOT NULL THEN 1.0 ELSE 0.0 END) as correction_rate,
            AVG(uf.rating) as avg_rating
        FROM agent_invocations ai
        JOIN user_feedback uf ON ai.invocation_id = uf.invocation_id
        WHERE ai.created_at >= NOW() - INTERVAL '30 days'
        GROUP BY ai.agent_name
        HAVING COUNT(uf.feedback_id) >= 5
        AND AVG(CASE WHEN uf.user_correction IS NOT NULL THEN 1.0 ELSE 0.0 END) > 0.4
        ORDER BY correction_rate DESC
        """
        
        correction_results = await conn.fetch(correction_query)
        
        for row in correction_results:
            insights.append(RecommendationInsight(
                insight_type="high_correction_rate",
                confidence=0.85,
                description=f"Agent '{row['agent_name']}' has high user correction rate ({row['correction_rate']:.1%})",
                suggested_action="Review agent capabilities or improve training for this use case",
                supporting_data={
                    'agent': row['agent_name'],
                    'correction_rate': row['correction_rate'],
                    'avg_rating': row['avg_rating'],
                    'feedback_count': row['feedback_count']
                }
            ))
        
        return insights
    
    async def generate_user_preference_profiles(self, user_id: str = None) -> Dict[str, Any]:
        """
        Generate user preference profiles for personalized recommendations
        """
        
        if user_id:
            user_filter = "AND as_session.user_id = $1"
            params = [user_id]
        else:
            user_filter = ""
            params = []
        
        query = f"""
        WITH user_patterns AS (
            SELECT 
                as_session.user_id,
                ai.agent_name,
                COUNT(*) as usage_count,
                AVG(CASE WHEN ai.success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                AVG(uf.rating) as avg_rating,
                array_agg(DISTINCT 
                    CASE WHEN as_session.project_context->>'domain' IS NOT NULL 
                         THEN as_session.project_context->>'domain' 
                    END
                ) FILTER (WHERE as_session.project_context->>'domain' IS NOT NULL) as preferred_domains,
                array_agg(DISTINCT ai.invocation_reason) as selection_patterns,
                AVG(ai.duration_seconds) as avg_duration_preference
                
            FROM agent_sessions as_session
            JOIN agent_invocations ai ON as_session.session_id = ai.session_id
            LEFT JOIN user_feedback uf ON ai.invocation_id = uf.invocation_id
            WHERE as_session.created_at >= NOW() - INTERVAL '90 days'
            {user_filter}
            GROUP BY as_session.user_id, ai.agent_name
            HAVING COUNT(*) >= 2
        ),
        user_preferences AS (
            SELECT 
                user_id,
                
                -- Preferred agents (high usage + good ratings)
                array_agg(agent_name ORDER BY (usage_count * COALESCE(avg_rating, 3.0)) DESC) 
                    FILTER (WHERE COALESCE(avg_rating, 3.0) >= 3.5) as preferred_agents,
                    
                -- Avoided agents (low ratings or abandoned frequently)
                array_agg(agent_name ORDER BY COALESCE(avg_rating, 3.0) ASC) 
                    FILTER (WHERE COALESCE(avg_rating, 3.0) < 2.5) as avoided_agents,
                    
                -- Workflow preferences
                mode() WITHIN GROUP (ORDER BY 
                    CASE WHEN 'user_selected' = ANY(selection_patterns) THEN 'manual'
                         WHEN 'automatic' = ANY(selection_patterns) THEN 'automatic'
                         ELSE 'mixed' END
                ) as selection_preference,
                
                AVG(avg_duration_preference) as duration_tolerance,
                
                -- Domain expertise
                unnest(preferred_domains) as expertise_domains
                
            FROM user_patterns
            GROUP BY user_id
        )
        SELECT * FROM user_preferences
        """
        
        async with self.db_pool.acquire() as conn:
            if user_id:
                rows = await conn.fetch(query, user_id)
            else:
                rows = await conn.fetch(query)
        
        if user_id:
            return dict(rows[0]) if rows else {}
        else:
            return {row['user_id']: dict(row) for row in rows}
    
    async def calculate_recommendation_metrics(self) -> Dict[str, float]:
        """
        Calculate metrics for the recommendation engine itself
        """
        
        query = """
        WITH recommendation_performance AS (
            SELECT 
                COUNT(*) as total_recommendations,
                AVG(CASE WHEN outcome_success THEN 1.0 ELSE 0.0 END) as accuracy,
                AVG(learning_weight) as avg_confidence,
                
                -- Time-based analysis
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_recommendations,
                AVG(CASE WHEN created_at >= NOW() - INTERVAL '7 days' AND outcome_success 
                         THEN 1.0 ELSE 0.0 END) as recent_accuracy
                
            FROM selection_optimization
            WHERE created_at >= NOW() - INTERVAL '30 days'
        ),
        user_acceptance AS (
            SELECT 
                AVG(CASE WHEN invocation_reason = 'recommended' THEN 1.0 ELSE 0.0 END) as recommendation_acceptance,
                COUNT(CASE WHEN invocation_reason = 'user_selected' THEN 1 END) as manual_selections,
                COUNT(CASE WHEN invocation_reason = 'recommended' THEN 1 END) as accepted_recommendations
            FROM agent_invocations
            WHERE created_at >= NOW() - INTERVAL '30 days'
        )
        SELECT 
            rp.*,
            ua.recommendation_acceptance,
            ua.manual_selections,
            ua.accepted_recommendations,
            
            -- Overall recommendation engine health
            (rp.accuracy * 0.5 + 
             ua.recommendation_acceptance * 0.3 + 
             LEAST(rp.avg_confidence, 1.0) * 0.2) as engine_health_score
             
        FROM recommendation_performance rp
        CROSS JOIN user_acceptance ua
        """
        
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow(query)
        
        return dict(result) if result else {}
    
    async def generate_trend_analysis(self, days: int = 90) -> Dict[str, List[Dict]]:
        """
        Generate trend analysis for various metrics over time
        """
        
        # Daily usage trends
        usage_trend_query = """
        SELECT 
            date_trunc('day', created_at) as day,
            agent_name,
            COUNT(*) as daily_usage,
            AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as daily_success_rate,
            AVG(duration_seconds) as avg_duration
        FROM agent_invocations 
        WHERE created_at >= NOW() - INTERVAL '%s days'
        GROUP BY date_trunc('day', created_at), agent_name
        ORDER BY day DESC, daily_usage DESC
        """ % days
        
        # Satisfaction trends
        satisfaction_trend_query = """
        SELECT 
            date_trunc('day', timestamp) as day,
            AVG(rating) as avg_rating,
            COUNT(*) as feedback_count,
            AVG(CASE WHEN user_correction IS NOT NULL THEN 1.0 ELSE 0.0 END) as correction_rate
        FROM user_feedback
        WHERE timestamp >= NOW() - INTERVAL '%s days'
        AND rating IS NOT NULL
        GROUP BY date_trunc('day', timestamp)
        ORDER BY day DESC
        """ % days
        
        async with self.db_pool.acquire() as conn:
            usage_trends = await conn.fetch(usage_trend_query)
            satisfaction_trends = await conn.fetch(satisfaction_trend_query)
        
        return {
            'usage_trends': [dict(row) for row in usage_trends],
            'satisfaction_trends': [dict(row) for row in satisfaction_trends]
        }
    
    async def export_insights_report(self, format: str = "json") -> str:
        """
        Generate a comprehensive insights report
        """
        
        # Gather all metrics
        effectiveness_metrics = await self.calculate_agent_effectiveness()
        combination_analysis = await self.analyze_agent_combinations()
        optimization_opportunities = await self.detect_optimization_opportunities()
        recommendation_metrics = await self.calculate_recommendation_metrics()
        trend_analysis = await self.generate_trend_analysis()
        
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_agents_analyzed': len(effectiveness_metrics),
                'top_performing_agent': effectiveness_metrics[0].agent_name if effectiveness_metrics else None,
                'optimization_opportunities': len(optimization_opportunities),
                'recommendation_engine_health': recommendation_metrics.get('engine_health_score', 0.0)
            },
            'agent_effectiveness': [
                {
                    'agent_name': m.agent_name,
                    'effectiveness_score': m.value,
                    'context': m.context
                } for m in effectiveness_metrics
            ],
            'optimal_combinations': combination_analysis[:10],  # Top 10
            'optimization_insights': [
                {
                    'type': insight.insight_type,
                    'confidence': insight.confidence,
                    'description': insight.description,
                    'action': insight.suggested_action,
                    'data': insight.supporting_data
                } for insight in optimization_opportunities
            ],
            'recommendation_engine': recommendation_metrics,
            'trends': trend_analysis
        }
        
        if format == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            # Could add other formats like CSV, HTML reports, etc.
            return json.dumps(report, indent=2, default=str)

# Convenience functions for common metric calculations
async def get_agent_leaderboard(db_pool, days: int = 30) -> List[Dict[str, Any]]:
    """Get top-performing agents"""
    engine = AnalyticsEngine(db_pool)
    metrics = await engine.calculate_agent_effectiveness(days)
    return [
        {
            'agent_name': m.agent_name,
            'effectiveness_score': m.value,
            'success_rate': m.context.get('success_rate', 0),
            'usage_count': m.context.get('total_invocations', 0)
        }
        for m in metrics[:10]
    ]

async def get_recommendation_accuracy(db_pool) -> float:
    """Get current recommendation engine accuracy"""
    engine = AnalyticsEngine(db_pool)
    metrics = await engine.calculate_recommendation_metrics()
    return metrics.get('accuracy', 0.0)

async def get_user_satisfaction_summary(db_pool, days: int = 30) -> Dict[str, float]:
    """Get user satisfaction summary"""
    query = """
    SELECT 
        AVG(rating) as avg_rating,
        COUNT(*) as total_feedback,
        AVG(CASE WHEN rating >= 4 THEN 1.0 ELSE 0.0 END) as satisfaction_rate
    FROM user_feedback
    WHERE timestamp >= NOW() - INTERVAL '%s days'
    AND rating IS NOT NULL
    """ % days
    
    async with db_pool.acquire() as conn:
        result = await conn.fetchrow(query)
    
    return dict(result) if result else {'avg_rating': 0, 'total_feedback': 0, 'satisfaction_rate': 0}