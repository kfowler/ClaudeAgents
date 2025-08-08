"""
Analytics Dashboard Configuration and Components

This module defines the structure and components for a comprehensive
analytics dashboard to visualize agent usage patterns and effectiveness.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Supported chart types for visualizations"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TABLE = "table"
    METRIC = "metric"
    GAUGE = "gauge"

class TimeRange(Enum):
    """Standard time ranges for dashboard filters"""
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"
    YEAR = "365d"

@dataclass
class ChartConfiguration:
    """Configuration for individual chart components"""
    id: str
    title: str
    chart_type: ChartType
    query: str
    refresh_interval: int = 300  # seconds
    parameters: Dict[str, Any] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    filters: List[str] = field(default_factory=list)
    drill_down: Optional[str] = None

@dataclass
class DashboardTab:
    """Dashboard tab containing related charts"""
    id: str
    title: str
    description: str
    charts: List[ChartConfiguration]
    layout: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardConfiguration:
    """Complete dashboard configuration"""
    title: str
    description: str
    tabs: List[DashboardTab]
    global_filters: List[Dict[str, Any]] = field(default_factory=list)
    refresh_interval: int = 300
    default_time_range: TimeRange = TimeRange.WEEK

class DashboardBuilder:
    """Builder for creating dashboard configurations"""
    
    def __init__(self):
        self.config = None
    
    def create_standard_dashboard(self) -> DashboardConfiguration:
        """Create the standard agent analytics dashboard"""
        
        # Define reusable queries
        queries = {
            'agent_effectiveness': """
                SELECT 
                    agent_name,
                    COUNT(*) as usage_count,
                    AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(quality_score) as avg_quality,
                    AVG(duration_seconds) as avg_duration,
                    MAX(created_at) as last_used
                FROM agent_invocations 
                WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                GROUP BY agent_name
                ORDER BY usage_count DESC
            """,
            
            'usage_trends': """
                SELECT 
                    date_trunc('{{time_bucket}}', created_at) as time_bucket,
                    agent_name,
                    COUNT(*) as usage_count,
                    AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate
                FROM agent_invocations 
                WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                GROUP BY date_trunc('{{time_bucket}}', created_at), agent_name
                ORDER BY time_bucket DESC
            """,
            
            'satisfaction_trends': """
                SELECT 
                    date_trunc('day', uf.timestamp) as day,
                    AVG(uf.rating) as avg_rating,
                    COUNT(*) as feedback_count
                FROM user_feedback uf
                WHERE uf.timestamp >= NOW() - INTERVAL '{{time_range}}'
                AND uf.rating IS NOT NULL
                GROUP BY date_trunc('day', uf.timestamp)
                ORDER BY day DESC
            """,
            
            'top_combinations': """
                SELECT 
                    primary_agent,
                    array_to_string(secondary_agents, ', ') as secondary_agents,
                    COUNT(*) as usage_count,
                    AVG(CASE WHEN combination_success THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(synergy_score) as avg_synergy
                FROM agent_combinations
                WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                GROUP BY primary_agent, secondary_agents
                HAVING COUNT(*) >= 3
                ORDER BY success_rate DESC, avg_synergy DESC
                LIMIT 10
            """,
            
            'error_analysis': """
                SELECT 
                    agent_name,
                    error_type,
                    COUNT(*) as error_count,
                    AVG(duration_seconds) as avg_duration_before_error
                FROM agent_invocations 
                WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                AND error_type IS NOT NULL
                GROUP BY agent_name, error_type
                ORDER BY error_count DESC
            """,
            
            'user_satisfaction_by_agent': """
                SELECT 
                    ai.agent_name,
                    AVG(uf.rating) as avg_rating,
                    COUNT(uf.rating) as rating_count,
                    STDDEV(uf.rating) as rating_stddev
                FROM agent_invocations ai
                JOIN user_feedback uf ON ai.invocation_id = uf.invocation_id
                WHERE ai.created_at >= NOW() - INTERVAL '{{time_range}}'
                AND uf.rating IS NOT NULL
                GROUP BY ai.agent_name
                HAVING COUNT(uf.rating) >= 3
                ORDER BY avg_rating DESC
            """,
            
            'performance_metrics': """
                SELECT 
                    agent_name,
                    AVG(duration_seconds) as avg_duration,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as median_duration,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_seconds) as p95_duration,
                    AVG(tokens_used) as avg_tokens,
                    AVG(lines_added + lines_removed) as avg_code_changes
                FROM agent_invocations 
                WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                AND success_status = 'success'
                GROUP BY agent_name
                ORDER BY avg_duration ASC
            """,
            
            'context_match_analysis': """
                SELECT 
                    agent_name,
                    AVG(context_match_score) as avg_context_match,
                    COUNT(CASE WHEN context_match_score < 0.5 THEN 1 END) as poor_matches,
                    COUNT(*) as total_invocations,
                    AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate
                FROM agent_invocations 
                WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                GROUP BY agent_name
                HAVING COUNT(*) >= 5
                ORDER BY avg_context_match DESC
            """
        }
        
        # Overview Tab
        overview_tab = DashboardTab(
            id="overview",
            title="Overview",
            description="High-level metrics and key performance indicators",
            charts=[
                # Key metrics at the top
                ChartConfiguration(
                    id="total_sessions",
                    title="Total Sessions",
                    chart_type=ChartType.METRIC,
                    query="SELECT COUNT(DISTINCT session_id) as value FROM agent_sessions WHERE created_at >= NOW() - INTERVAL '{{time_range}}'",
                    parameters={"format": "number"}
                ),
                ChartConfiguration(
                    id="avg_satisfaction",
                    title="Avg User Satisfaction",
                    chart_type=ChartType.GAUGE,
                    query="SELECT AVG(rating) as value FROM user_feedback WHERE timestamp >= NOW() - INTERVAL '{{time_range}}' AND rating IS NOT NULL",
                    parameters={"min": 1, "max": 5, "format": "decimal"}
                ),
                ChartConfiguration(
                    id="success_rate",
                    title="Overall Success Rate",
                    chart_type=ChartType.GAUGE,
                    query="SELECT AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as value FROM agent_invocations WHERE created_at >= NOW() - INTERVAL '{{time_range}}'",
                    parameters={"min": 0, "max": 1, "format": "percentage"}
                ),
                
                # Usage trends
                ChartConfiguration(
                    id="daily_usage",
                    title="Daily Usage Trends",
                    chart_type=ChartType.LINE,
                    query="""
                        SELECT 
                            date_trunc('day', created_at) as date,
                            COUNT(*) as invocations,
                            COUNT(DISTINCT session_id) as sessions
                        FROM agent_invocations 
                        WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                        GROUP BY date_trunc('day', created_at)
                        ORDER BY date
                    """,
                    parameters={"x_axis": "date", "y_axes": ["invocations", "sessions"]}
                ),
                
                # Top agents
                ChartConfiguration(
                    id="top_agents",
                    title="Most Used Agents",
                    chart_type=ChartType.BAR,
                    query=queries['agent_effectiveness'],
                    parameters={"x_axis": "agent_name", "y_axis": "usage_count", "limit": 10}
                )
            ],
            layout={
                "rows": [
                    {"height": "150px", "charts": ["total_sessions", "avg_satisfaction", "success_rate"]},
                    {"height": "300px", "charts": ["daily_usage"]},
                    {"height": "400px", "charts": ["top_agents"]}
                ]
            }
        )
        
        # Agent Performance Tab
        performance_tab = DashboardTab(
            id="performance",
            title="Agent Performance",
            description="Detailed performance metrics for individual agents",
            charts=[
                ChartConfiguration(
                    id="agent_effectiveness_table",
                    title="Agent Effectiveness Rankings",
                    chart_type=ChartType.TABLE,
                    query=queries['agent_effectiveness'],
                    parameters={
                        "columns": [
                            {"field": "agent_name", "title": "Agent", "sortable": True},
                            {"field": "usage_count", "title": "Usage", "type": "number"},
                            {"field": "success_rate", "title": "Success Rate", "type": "percentage"},
                            {"field": "avg_quality", "title": "Avg Quality", "type": "decimal"},
                            {"field": "avg_duration", "title": "Avg Duration (s)", "type": "number"}
                        ]
                    }
                ),
                
                ChartConfiguration(
                    id="performance_scatter",
                    title="Success Rate vs Usage",
                    chart_type=ChartType.SCATTER,
                    query=queries['agent_effectiveness'],
                    parameters={
                        "x_axis": "usage_count",
                        "y_axis": "success_rate",
                        "size": "avg_quality",
                        "label": "agent_name"
                    }
                ),
                
                ChartConfiguration(
                    id="duration_comparison",
                    title="Performance Duration Metrics",
                    chart_type=ChartType.BAR,
                    query=queries['performance_metrics'],
                    parameters={
                        "x_axis": "agent_name",
                        "y_axes": ["avg_duration", "median_duration", "p95_duration"],
                        "chart_type": "grouped"
                    }
                ),
                
                ChartConfiguration(
                    id="context_match_heatmap",
                    title="Context Match vs Success Rate",
                    chart_type=ChartType.HEATMAP,
                    query=queries['context_match_analysis'],
                    parameters={
                        "x_axis": "agent_name",
                        "y_axis": "avg_context_match",
                        "value": "success_rate"
                    }
                )
            ]
        )
        
        # User Satisfaction Tab
        satisfaction_tab = DashboardTab(
            id="satisfaction",
            title="User Satisfaction",
            description="User feedback and satisfaction metrics",
            charts=[
                ChartConfiguration(
                    id="satisfaction_trends",
                    title="Satisfaction Trends Over Time",
                    chart_type=ChartType.LINE,
                    query=queries['satisfaction_trends'],
                    parameters={"x_axis": "day", "y_axis": "avg_rating"}
                ),
                
                ChartConfiguration(
                    id="satisfaction_by_agent",
                    title="User Satisfaction by Agent",
                    chart_type=ChartType.BAR,
                    query=queries['user_satisfaction_by_agent'],
                    parameters={
                        "x_axis": "agent_name",
                        "y_axis": "avg_rating",
                        "error_bars": "rating_stddev"
                    }
                ),
                
                ChartConfiguration(
                    id="feedback_volume",
                    title="Feedback Volume by Agent",
                    chart_type=ChartType.PIE,
                    query="SELECT ai.agent_name, COUNT(*) as feedback_count FROM agent_invocations ai JOIN user_feedback uf ON ai.invocation_id = uf.invocation_id WHERE ai.created_at >= NOW() - INTERVAL '{{time_range}}' GROUP BY ai.agent_name",
                    parameters={"value_field": "feedback_count", "label_field": "agent_name"}
                ),
                
                ChartConfiguration(
                    id="correction_analysis",
                    title="User Correction Patterns",
                    chart_type=ChartType.TABLE,
                    query="""
                        SELECT 
                            ai.agent_name,
                            COUNT(uf.feedback_id) as total_feedback,
                            COUNT(CASE WHEN uf.user_correction IS NOT NULL THEN 1 END) as corrections,
                            ROUND(COUNT(CASE WHEN uf.user_correction IS NOT NULL THEN 1 END)::decimal / COUNT(uf.feedback_id) * 100, 2) as correction_rate
                        FROM agent_invocations ai
                        LEFT JOIN user_feedback uf ON ai.invocation_id = uf.invocation_id
                        WHERE ai.created_at >= NOW() - INTERVAL '{{time_range}}'
                        GROUP BY ai.agent_name
                        HAVING COUNT(uf.feedback_id) > 0
                        ORDER BY correction_rate DESC
                    """,
                    parameters={
                        "columns": [
                            {"field": "agent_name", "title": "Agent"},
                            {"field": "total_feedback", "title": "Total Feedback", "type": "number"},
                            {"field": "corrections", "title": "Corrections", "type": "number"},
                            {"field": "correction_rate", "title": "Correction Rate (%)", "type": "percentage"}
                        ]
                    }
                )
            ]
        )
        
        # Agent Combinations Tab
        combinations_tab = DashboardTab(
            id="combinations",
            title="Agent Combinations",
            description="Analysis of multi-agent workflows and combinations",
            charts=[
                ChartConfiguration(
                    id="top_combinations_table",
                    title="Most Effective Agent Combinations",
                    chart_type=ChartType.TABLE,
                    query=queries['top_combinations'],
                    parameters={
                        "columns": [
                            {"field": "primary_agent", "title": "Primary Agent"},
                            {"field": "secondary_agents", "title": "Secondary Agents"},
                            {"field": "usage_count", "title": "Usage", "type": "number"},
                            {"field": "success_rate", "title": "Success Rate", "type": "percentage"},
                            {"field": "avg_synergy", "title": "Synergy Score", "type": "decimal"}
                        ]
                    }
                ),
                
                ChartConfiguration(
                    id="combination_success_heatmap",
                    title="Agent Combination Success Matrix",
                    chart_type=ChartType.HEATMAP,
                    query="""
                        SELECT 
                            primary_agent,
                            unnest(secondary_agents) as secondary_agent,
                            AVG(CASE WHEN combination_success THEN 1.0 ELSE 0.0 END) as success_rate,
                            COUNT(*) as usage_count
                        FROM agent_combinations
                        WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                        GROUP BY primary_agent, unnest(secondary_agents)
                        HAVING COUNT(*) >= 2
                    """,
                    parameters={
                        "x_axis": "primary_agent",
                        "y_axis": "secondary_agent",
                        "value": "success_rate"
                    }
                ),
                
                ChartConfiguration(
                    id="workflow_patterns",
                    title="Common Workflow Patterns",
                    chart_type=ChartType.BAR,
                    query="""
                        SELECT 
                            combination_pattern,
                            COUNT(*) as usage_count,
                            AVG(synergy_score) as avg_synergy
                        FROM agent_combinations
                        WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                        GROUP BY combination_pattern
                        ORDER BY usage_count DESC
                    """,
                    parameters={"x_axis": "combination_pattern", "y_axis": "usage_count"}
                )
            ]
        )
        
        # Errors & Issues Tab
        issues_tab = DashboardTab(
            id="issues",
            title="Errors & Issues",
            description="Error analysis and troubleshooting insights",
            charts=[
                ChartConfiguration(
                    id="error_frequency",
                    title="Error Frequency by Agent",
                    chart_type=ChartType.BAR,
                    query=queries['error_analysis'],
                    parameters={"x_axis": "agent_name", "y_axis": "error_count"}
                ),
                
                ChartConfiguration(
                    id="error_types",
                    title="Common Error Types",
                    chart_type=ChartType.PIE,
                    query="""
                        SELECT 
                            error_type,
                            COUNT(*) as error_count
                        FROM agent_invocations 
                        WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                        AND error_type IS NOT NULL
                        GROUP BY error_type
                        ORDER BY error_count DESC
                    """,
                    parameters={"value_field": "error_count", "label_field": "error_type"}
                ),
                
                ChartConfiguration(
                    id="error_trends",
                    title="Error Rate Trends",
                    chart_type=ChartType.LINE,
                    query="""
                        SELECT 
                            date_trunc('day', created_at) as date,
                            AVG(CASE WHEN error_type IS NOT NULL THEN 1.0 ELSE 0.0 END) as error_rate,
                            COUNT(*) as total_invocations
                        FROM agent_invocations 
                        WHERE created_at >= NOW() - INTERVAL '{{time_range}}'
                        GROUP BY date_trunc('day', created_at)
                        ORDER BY date
                    """,
                    parameters={"x_axis": "date", "y_axis": "error_rate"}
                ),
                
                ChartConfiguration(
                    id="problematic_contexts",
                    title="Contexts with High Error Rates",
                    chart_type=ChartType.TABLE,
                    query="""
                        SELECT 
                            ai.agent_name,
                            COUNT(*) as total_invocations,
                            COUNT(CASE WHEN ai.error_type IS NOT NULL THEN 1 END) as errors,
                            ROUND(COUNT(CASE WHEN ai.error_type IS NOT NULL THEN 1 END)::decimal / COUNT(*) * 100, 2) as error_rate,
                            array_agg(DISTINCT ai.error_type) FILTER (WHERE ai.error_type IS NOT NULL) as error_types
                        FROM agent_invocations ai
                        WHERE ai.created_at >= NOW() - INTERVAL '{{time_range}}'
                        GROUP BY ai.agent_name
                        HAVING COUNT(*) >= 5 AND COUNT(CASE WHEN ai.error_type IS NOT NULL THEN 1 END) > 0
                        ORDER BY error_rate DESC
                    """,
                    parameters={
                        "columns": [
                            {"field": "agent_name", "title": "Agent"},
                            {"field": "total_invocations", "title": "Total Uses", "type": "number"},
                            {"field": "errors", "title": "Errors", "type": "number"},
                            {"field": "error_rate", "title": "Error Rate (%)", "type": "percentage"},
                            {"field": "error_types", "title": "Error Types"}
                        ]
                    }
                )
            ]
        )
        
        # Create the complete dashboard configuration
        dashboard = DashboardConfiguration(
            title="Agent Analytics Dashboard",
            description="Comprehensive analytics for Claude Code agent system",
            tabs=[overview_tab, performance_tab, satisfaction_tab, combinations_tab, issues_tab],
            global_filters=[
                {
                    "type": "time_range",
                    "parameter": "time_range",
                    "default": "7 days",
                    "options": ["1 hour", "1 day", "7 days", "30 days", "90 days"]
                },
                {
                    "type": "multi_select",
                    "parameter": "agent_filter",
                    "title": "Filter Agents",
                    "query": "SELECT DISTINCT agent_name FROM agent_invocations ORDER BY agent_name"
                }
            ],
            refresh_interval=300,
            default_time_range=TimeRange.WEEK
        )
        
        return dashboard
    
    def export_config(self, dashboard: DashboardConfiguration, format: str = "json") -> str:
        """Export dashboard configuration"""
        
        if format == "json":
            return self._export_json(dashboard)
        elif format == "grafana":
            return self._export_grafana(dashboard)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, dashboard: DashboardConfiguration) -> str:
        """Export as JSON configuration"""
        
        def convert_enums(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif hasattr(obj, '__dict__'):
                return {k: convert_enums(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            else:
                return obj
        
        return json.dumps(convert_enums(dashboard), indent=2)
    
    def _export_grafana(self, dashboard: DashboardConfiguration) -> str:
        """Export as Grafana dashboard JSON"""
        
        # This would create a Grafana-compatible dashboard
        # For now, return a basic structure
        grafana_dashboard = {
            "dashboard": {
                "title": dashboard.title,
                "description": dashboard.description,
                "tags": ["agent-analytics", "claude-code"],
                "timezone": "browser",
                "refresh": f"{dashboard.refresh_interval}s",
                "time": {
                    "from": "now-7d",
                    "to": "now"
                },
                "panels": []
            }
        }
        
        panel_id = 1
        for tab in dashboard.tabs:
            for chart in tab.charts:
                panel = {
                    "id": panel_id,
                    "title": chart.title,
                    "type": self._grafana_chart_type(chart.chart_type),
                    "targets": [
                        {
                            "expr": chart.query,
                            "legendFormat": chart.title
                        }
                    ]
                }
                grafana_dashboard["dashboard"]["panels"].append(panel)
                panel_id += 1
        
        return json.dumps(grafana_dashboard, indent=2)
    
    def _grafana_chart_type(self, chart_type: ChartType) -> str:
        """Map our chart types to Grafana panel types"""
        mapping = {
            ChartType.LINE: "timeseries",
            ChartType.BAR: "barchart",
            ChartType.PIE: "piechart",
            ChartType.SCATTER: "scatterplot",
            ChartType.HEATMAP: "heatmap",
            ChartType.TABLE: "table",
            ChartType.METRIC: "stat",
            ChartType.GAUGE: "gauge"
        }
        return mapping.get(chart_type, "timeseries")

# Usage example and configuration export
def generate_dashboard_config():
    """Generate and export the standard dashboard configuration"""
    
    builder = DashboardBuilder()
    dashboard = builder.create_standard_dashboard()
    
    # Export as JSON
    json_config = builder.export_config(dashboard, "json")
    
    # Export as Grafana
    grafana_config = builder.export_config(dashboard, "grafana")
    
    return {
        "json": json_config,
        "grafana": grafana_config
    }

# Real-time dashboard data provider
class DashboardDataProvider:
    """Provides real-time data for dashboard components"""
    
    def __init__(self, db_pool, cache_ttl: int = 300):
        self.db_pool = db_pool
        self.cache_ttl = cache_ttl
        self.cache = {}
    
    async def get_chart_data(self, chart: ChartConfiguration, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data for a specific chart with caching"""
        
        # Build cache key
        cache_key = f"{chart.id}_{hash(str(filters))}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now(timezone.utc) - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
        
        # Execute query with filters
        query = self._apply_filters(chart.query, filters or {})
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        # Format data based on chart type
        data = self._format_chart_data(rows, chart)
        
        # Cache the result
        self.cache[cache_key] = (data, datetime.now(timezone.utc))
        
        return data
    
    def _apply_filters(self, query: str, filters: Dict[str, Any]) -> str:
        """Apply filters to query template"""
        
        # Replace template variables
        formatted_query = query
        for key, value in filters.items():
            formatted_query = formatted_query.replace(f"{{{{{key}}}}}", str(value))
        
        return formatted_query
    
    def _format_chart_data(self, rows: List, chart: ChartConfiguration) -> Dict[str, Any]:
        """Format database rows for chart consumption"""
        
        data = [dict(row) for row in rows]
        
        return {
            "chart_id": chart.id,
            "chart_type": chart.chart_type.value,
            "data": data,
            "parameters": chart.parameters,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }