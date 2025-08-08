"""
Analytics and Monitoring Dashboard

Provides comprehensive analytics, monitoring, and visualization capabilities
for the learning system. Tracks performance, usage patterns, learning
effectiveness, and system health.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# Dashboard framework imports (would be actual dashboard framework in production)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output
    HAS_DASH = True
except ImportError:
    HAS_DASH = False

from ..knowledge_graph.graph_manager import GraphManager
from ..memory.memory_manager import MemoryManager
from ..learning.ml_pipeline import MLPipeline
from ..embeddings.vector_manager import VectorManager
from ..events.event_store import EventStore
from ..recommendations.recommendation_engine import RecommendationEngine
from ..privacy.privacy_engine import PrivacyEngine
from ..integration.agent_integration import LearningSystemIntegration


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Single metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class Alert:
    """System alert"""
    id: str
    title: str
    description: str
    level: AlertLevel
    metric_name: str
    threshold_value: float
    current_value: float
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False


@dataclass
class DashboardCard:
    """Dashboard card configuration"""
    id: str
    title: str
    description: str
    chart_type: str  # 'line', 'bar', 'pie', 'gauge', 'table'
    data_source: str
    refresh_interval: int = 60  # seconds
    size: str = "medium"  # small, medium, large
    position: Tuple[int, int] = (0, 0)


class MetricsCollector:
    """
    Collects metrics from all learning system components
    """
    
    def __init__(
        self,
        graph_manager: GraphManager,
        memory_manager: MemoryManager,
        ml_pipeline: MLPipeline,
        vector_manager: VectorManager,
        event_store: EventStore,
        recommendation_engine: RecommendationEngine,
        privacy_engine: PrivacyEngine,
        integration: LearningSystemIntegration
    ):
        """Initialize metrics collector"""
        self.graph = graph_manager
        self.memory = memory_manager
        self.ml_pipeline = ml_pipeline
        self.vector_manager = vector_manager
        self.event_store = event_store
        self.recommendation_engine = recommendation_engine
        self.privacy_engine = privacy_engine
        self.integration = integration
        
        # Metrics storage
        self.metrics_history: Dict[str, List[Metric]] = defaultdict(list)
        self.current_metrics: Dict[str, Metric] = {}
        
        # Collection settings
        self.collection_interval = 30  # seconds
        self.retention_hours = 24 * 7  # 1 week
        
        # Background collection
        self.collection_task = None
        self.running = False
    
    async def start_collection(self):
        """Start background metrics collection"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting metrics collection")
        
        while self.running:
            try:
                await self.collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
        logger.info("Stopped metrics collection")
    
    async def collect_all_metrics(self):
        """Collect metrics from all components"""
        timestamp = datetime.utcnow()
        
        # Collect metrics in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(self.collect_graph_metrics): 'graph',
                executor.submit(self.collect_memory_metrics): 'memory',
                executor.submit(self.collect_ml_metrics): 'ml',
                executor.submit(self.collect_vector_metrics): 'vector',
                executor.submit(self.collect_event_metrics): 'events',
                executor.submit(self.collect_recommendation_metrics): 'recommendations',
                executor.submit(self.collect_privacy_metrics): 'privacy',
                executor.submit(self.collect_integration_metrics): 'integration'
            }
            
            for future in futures:
                try:
                    component_metrics = future.result(timeout=10)
                    for metric in component_metrics:
                        metric.timestamp = timestamp
                        self.store_metric(metric)
                except Exception as e:
                    component = futures[future]
                    logger.error(f"Failed to collect {component} metrics: {e}")
        
        # Clean up old metrics
        self.cleanup_old_metrics()
    
    def collect_graph_metrics(self) -> List[Metric]:
        """Collect knowledge graph metrics"""
        try:
            stats = self.graph.get_system_metrics()
            
            return [
                Metric("graph.total_projects", stats.get('total_projects', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("graph.active_projects", stats.get('active_projects', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("graph.total_patterns", stats.get('total_patterns', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("graph.total_decisions", stats.get('total_decisions', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("graph.successful_outcomes", stats.get('successful_outcomes', 0), MetricType.GAUGE, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect graph metrics: {e}")
            return []
    
    def collect_memory_metrics(self) -> List[Metric]:
        """Collect memory system metrics"""
        try:
            # Get session count and memory usage
            active_sessions = len(self.memory.active_sessions)
            cached_memories = len(self.memory.memory_cache)
            
            return [
                Metric("memory.active_sessions", active_sessions, MetricType.GAUGE, datetime.utcnow()),
                Metric("memory.cached_memories", cached_memories, MetricType.GAUGE, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect memory metrics: {e}")
            return []
    
    def collect_ml_metrics(self) -> List[Metric]:
        """Collect ML pipeline metrics"""
        try:
            model_info = self.ml_pipeline.get_model_info()
            
            metrics = []
            for model_name, info in model_info.items():
                if 'metrics' in info and info['metrics']:
                    model_metrics = info['metrics']
                    
                    if 'cv_score' in model_metrics and model_metrics['cv_score']:
                        metrics.append(
                            Metric(
                                f"ml.{model_name}.cv_score",
                                model_metrics['cv_score'],
                                MetricType.GAUGE,
                                datetime.utcnow(),
                                {'model': model_name}
                            )
                        )
                    
                    if 'accuracy' in model_metrics and model_metrics['accuracy']:
                        metrics.append(
                            Metric(
                                f"ml.{model_name}.accuracy",
                                model_metrics['accuracy'],
                                MetricType.GAUGE,
                                datetime.utcnow(),
                                {'model': model_name}
                            )
                        )
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to collect ML metrics: {e}")
            return []
    
    def collect_vector_metrics(self) -> List[Metric]:
        """Collect vector database metrics"""
        try:
            stats = self.vector_manager.get_embedding_stats()
            
            vector_stats = stats.get('vector_database', {})
            cache_stats = stats.get('cache', {})
            
            return [
                Metric("vector.total_vectors", vector_stats.get('total_vectors', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("vector.cache_hit_rate", cache_stats.get('hit_rate', 0), MetricType.PERCENTAGE, datetime.utcnow()),
                Metric("vector.cached_embeddings", cache_stats.get('cached_embeddings', 0), MetricType.GAUGE, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect vector metrics: {e}")
            return []
    
    def collect_event_metrics(self) -> List[Metric]:
        """Collect event store metrics"""
        try:
            stats = self.event_store.get_storage_stats()
            
            return [
                Metric("events.total_events", stats.get('total_events', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("events.recent_events_24h", stats.get('recent_events_24h', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("events.database_size_mb", stats.get('database_size_mb', 0), MetricType.GAUGE, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect event metrics: {e}")
            return []
    
    def collect_recommendation_metrics(self) -> List[Metric]:
        """Collect recommendation system metrics"""
        try:
            analytics = self.recommendation_engine.get_recommendation_analytics()
            
            return [
                Metric("recommendations.total_generated", analytics.get('total_recommendations_generated', 0), MetricType.COUNTER, datetime.utcnow()),
                Metric("recommendations.feedback_rate", analytics.get('feedback_rate', 0), MetricType.PERCENTAGE, datetime.utcnow()),
                Metric("recommendations.avg_usefulness", analytics.get('average_usefulness_score', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("recommendations.cache_size", analytics.get('cache_size', 0), MetricType.GAUGE, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect recommendation metrics: {e}")
            return []
    
    def collect_privacy_metrics(self) -> List[Metric]:
        """Collect privacy engine metrics"""
        try:
            privacy_metrics = self.privacy_engine.get_privacy_metrics()
            
            return [
                Metric("privacy.active_budgets", privacy_metrics.get('active_budgets', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("privacy.exhausted_budgets", privacy_metrics.get('exhausted_budgets', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("privacy.avg_budget_utilization", privacy_metrics.get('average_budget_utilization', 0), MetricType.PERCENTAGE, datetime.utcnow()),
                Metric("privacy.total_audit_events", privacy_metrics.get('total_audit_events', 0), MetricType.COUNTER, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect privacy metrics: {e}")
            return []
    
    def collect_integration_metrics(self) -> List[Metric]:
        """Collect integration layer metrics"""
        try:
            integration_status = self.integration.get_integration_status()
            session_metrics = self.integration.get_session_metrics()
            
            return [
                Metric("integration.wrapped_agents", integration_status.get('wrapped_agents', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("integration.active_sessions", session_metrics.get('active_sessions', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("integration.queue_size", integration_status.get('processing_queue_size', 0), MetricType.GAUGE, datetime.utcnow()),
                Metric("integration.total_actions", session_metrics.get('total_actions', 0), MetricType.COUNTER, datetime.utcnow()),
                Metric("integration.total_decisions", session_metrics.get('total_decisions', 0), MetricType.COUNTER, datetime.utcnow()),
            ]
        except Exception as e:
            logger.error(f"Failed to collect integration metrics: {e}")
            return []
    
    def store_metric(self, metric: Metric):
        """Store metric in history"""
        self.current_metrics[metric.name] = metric
        self.metrics_history[metric.name].append(metric)
    
    def cleanup_old_metrics(self):
        """Remove old metrics beyond retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        for metric_name in self.metrics_history:
            self.metrics_history[metric_name] = [
                m for m in self.metrics_history[metric_name]
                if m.timestamp > cutoff_time
            ]
    
    def get_current_metrics(self) -> Dict[str, Metric]:
        """Get current metric values"""
        return self.current_metrics.copy()
    
    def get_metric_history(
        self, 
        metric_name: str, 
        hours_back: int = 24
    ) -> List[Metric]:
        """Get historical data for a metric"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        return [
            m for m in self.metrics_history.get(metric_name, [])
            if m.timestamp > cutoff_time
        ]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'total_metrics': len(self.current_metrics),
            'metrics_by_component': defaultdict(int),
            'last_collection': None,
            'oldest_data': None
        }
        
        # Count metrics by component
        for metric_name in self.current_metrics:
            component = metric_name.split('.')[0]
            summary['metrics_by_component'][component] += 1
        
        # Find time range
        all_timestamps = []
        for metrics_list in self.metrics_history.values():
            all_timestamps.extend([m.timestamp for m in metrics_list])
        
        if all_timestamps:
            summary['last_collection'] = max(all_timestamps)
            summary['oldest_data'] = min(all_timestamps)
        
        return summary


class AlertManager:
    """
    Manages alerts and notifications for the learning system
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize alert manager"""
        self.metrics_collector = metrics_collector
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_handlers: List[Callable] = []
        
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alerting rules"""
        self.alert_rules = [
            {
                'name': 'high_memory_usage',
                'metric': 'memory.cached_memories',
                'condition': 'greater_than',
                'threshold': 10000,
                'level': AlertLevel.WARNING,
                'description': 'High memory usage detected'
            },
            {
                'name': 'low_recommendation_feedback',
                'metric': 'recommendations.feedback_rate',
                'condition': 'less_than',
                'threshold': 0.1,
                'level': AlertLevel.WARNING,
                'description': 'Low recommendation feedback rate'
            },
            {
                'name': 'privacy_budget_exhausted',
                'metric': 'privacy.exhausted_budgets',
                'condition': 'greater_than',
                'threshold': 5,
                'level': AlertLevel.ERROR,
                'description': 'Multiple privacy budgets exhausted'
            },
            {
                'name': 'event_database_size',
                'metric': 'events.database_size_mb',
                'condition': 'greater_than',
                'threshold': 1000,  # 1GB
                'level': AlertLevel.WARNING,
                'description': 'Event database size getting large'
            }
        ]
    
    def check_alerts(self):
        """Check all alert rules against current metrics"""
        current_metrics = self.metrics_collector.get_current_metrics()
        
        for rule in self.alert_rules:
            metric_name = rule['metric']
            
            if metric_name not in current_metrics:
                continue
            
            current_value = current_metrics[metric_name].value
            threshold = rule['threshold']
            condition = rule['condition']
            
            alert_triggered = False
            
            if condition == 'greater_than' and current_value > threshold:
                alert_triggered = True
            elif condition == 'less_than' and current_value < threshold:
                alert_triggered = True
            elif condition == 'equals' and current_value == threshold:
                alert_triggered = True
            
            if alert_triggered:
                self._trigger_alert(rule, current_value)
            else:
                self._resolve_alert(rule['name'])
    
    def _trigger_alert(self, rule: Dict[str, Any], current_value: float):
        """Trigger an alert"""
        alert_id = rule['name']
        
        # Don't re-trigger existing alerts
        if alert_id in self.alerts and not self.alerts[alert_id].resolved_at:
            return
        
        alert = Alert(
            id=alert_id,
            title=rule['name'].replace('_', ' ').title(),
            description=rule['description'],
            level=rule['level'],
            metric_name=rule['metric'],
            threshold_value=rule['threshold'],
            current_value=current_value,
            created_at=datetime.utcnow()
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert notification handler failed: {e}")
        
        logger.warning(f"Alert triggered: {alert.title} - {alert.description}")
    
    def _resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts and not self.alerts[alert_id].resolved_at:
            self.alerts[alert_id].resolved_at = datetime.utcnow()
            logger.info(f"Alert resolved: {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved_at]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts.values() if alert.level == level]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            return True
        return False
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add alert notification handler"""
        self.notification_handlers.append(handler)


class DashboardBuilder:
    """
    Builds dashboard visualizations and layouts
    """
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        """Initialize dashboard builder"""
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.dashboard_config: List[DashboardCard] = []
        
        self._setup_default_dashboard()
    
    def _setup_default_dashboard(self):
        """Setup default dashboard layout"""
        self.dashboard_config = [
            DashboardCard(
                id="system_overview",
                title="System Overview",
                description="High-level system metrics",
                chart_type="gauge",
                data_source="overview_metrics",
                size="large"
            ),
            DashboardCard(
                id="agent_activity",
                title="Agent Activity",
                description="Agent sessions and actions over time",
                chart_type="line",
                data_source="integration_metrics",
                size="medium"
            ),
            DashboardCard(
                id="learning_performance",
                title="Learning Performance",
                description="ML model performance metrics",
                chart_type="bar",
                data_source="ml_metrics",
                size="medium"
            ),
            DashboardCard(
                id="recommendation_stats",
                title="Recommendation Statistics",
                description="Recommendation generation and feedback",
                chart_type="line",
                data_source="recommendation_metrics",
                size="medium"
            ),
            DashboardCard(
                id="privacy_compliance",
                title="Privacy Compliance",
                description="Privacy budget utilization",
                chart_type="pie",
                data_source="privacy_metrics",
                size="small"
            ),
            DashboardCard(
                id="active_alerts",
                title="Active Alerts",
                description="Current system alerts",
                chart_type="table",
                data_source="alerts",
                size="medium"
            )
        ]
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for all dashboard cards"""
        current_metrics = self.metrics_collector.get_current_metrics()
        active_alerts = self.alert_manager.get_active_alerts()
        
        dashboard_data = {
            'overview_metrics': self._generate_overview_data(current_metrics),
            'integration_metrics': self._generate_time_series_data('integration', 24),
            'ml_metrics': self._generate_ml_performance_data(current_metrics),
            'recommendation_metrics': self._generate_recommendation_data(current_metrics),
            'privacy_metrics': self._generate_privacy_data(current_metrics),
            'alerts': self._generate_alerts_data(active_alerts),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return dashboard_data
    
    def _generate_overview_data(self, current_metrics: Dict[str, Metric]) -> Dict[str, Any]:
        """Generate overview metrics data"""
        overview = {}
        
        # Key metrics for overview
        key_metrics = [
            'graph.total_projects',
            'integration.active_sessions',
            'integration.total_actions',
            'recommendations.total_generated',
            'events.total_events'
        ]
        
        for metric_name in key_metrics:
            if metric_name in current_metrics:
                clean_name = metric_name.split('.')[1]
                overview[clean_name] = current_metrics[metric_name].value
        
        return overview
    
    def _generate_time_series_data(self, component: str, hours_back: int) -> Dict[str, Any]:
        """Generate time series data for a component"""
        # Get all metrics for the component
        component_metrics = [
            name for name in self.metrics_collector.metrics_history.keys()
            if name.startswith(f"{component}.")
        ]
        
        time_series = {}
        
        for metric_name in component_metrics:
            history = self.metrics_collector.get_metric_history(metric_name, hours_back)
            
            if history:
                times = [m.timestamp.isoformat() for m in history]
                values = [m.value for m in history]
                
                time_series[metric_name] = {
                    'times': times,
                    'values': values
                }
        
        return time_series
    
    def _generate_ml_performance_data(self, current_metrics: Dict[str, Metric]) -> Dict[str, Any]:
        """Generate ML model performance data"""
        ml_data = {
            'models': [],
            'scores': []
        }
        
        # Find ML metrics
        for metric_name, metric in current_metrics.items():
            if metric_name.startswith('ml.') and '.cv_score' in metric_name:
                model_name = metric_name.split('.')[1]
                ml_data['models'].append(model_name)
                ml_data['scores'].append(metric.value)
        
        return ml_data
    
    def _generate_recommendation_data(self, current_metrics: Dict[str, Metric]) -> Dict[str, Any]:
        """Generate recommendation system data"""
        rec_data = {}
        
        rec_metrics = [
            'recommendations.total_generated',
            'recommendations.feedback_rate',
            'recommendations.avg_usefulness'
        ]
        
        for metric_name in rec_metrics:
            if metric_name in current_metrics:
                clean_name = metric_name.split('.')[1]
                rec_data[clean_name] = current_metrics[metric_name].value
        
        return rec_data
    
    def _generate_privacy_data(self, current_metrics: Dict[str, Metric]) -> Dict[str, Any]:
        """Generate privacy compliance data"""
        privacy_data = {}
        
        # Get privacy budget utilization
        if 'privacy.avg_budget_utilization' in current_metrics:
            utilization = current_metrics['privacy.avg_budget_utilization'].value
            privacy_data['budget_utilization'] = {
                'used': utilization * 100,
                'remaining': (1 - utilization) * 100
            }
        
        return privacy_data
    
    def _generate_alerts_data(self, active_alerts: List[Alert]) -> List[Dict[str, Any]]:
        """Generate alerts table data"""
        alerts_data = []
        
        for alert in active_alerts:
            alerts_data.append({
                'id': alert.id,
                'title': alert.title,
                'level': alert.level.value,
                'metric': alert.metric_name,
                'current_value': alert.current_value,
                'threshold': alert.threshold_value,
                'created_at': alert.created_at.isoformat(),
                'acknowledged': alert.acknowledged
            })
        
        return alerts_data
    
    def export_dashboard_config(self) -> Dict[str, Any]:
        """Export dashboard configuration"""
        return {
            'cards': [asdict(card) for card in self.dashboard_config],
            'layout': 'grid',
            'refresh_interval': 60,
            'auto_refresh': True
        }


class AnalyticsDashboard:
    """
    Main analytics dashboard that orchestrates metrics collection,
    alerting, and visualization.
    """
    
    def __init__(
        self,
        graph_manager: GraphManager,
        memory_manager: MemoryManager,
        ml_pipeline: MLPipeline,
        vector_manager: VectorManager,
        event_store: EventStore,
        recommendation_engine: RecommendationEngine,
        privacy_engine: PrivacyEngine,
        integration: LearningSystemIntegration
    ):
        """Initialize analytics dashboard"""
        self.metrics_collector = MetricsCollector(
            graph_manager, memory_manager, ml_pipeline, vector_manager,
            event_store, recommendation_engine, privacy_engine, integration
        )
        
        self.alert_manager = AlertManager(self.metrics_collector)
        self.dashboard_builder = DashboardBuilder(self.metrics_collector, self.alert_manager)
        
        # Dashboard state
        self.running = False
        self.dashboard_data = {}
        self.last_update = datetime.utcnow()
        
        # Setup default notification handlers
        self.alert_manager.add_notification_handler(self._log_alert)
    
    async def start(self):
        """Start the dashboard system"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting analytics dashboard")
        
        # Start metrics collection
        collection_task = asyncio.create_task(self.metrics_collector.start_collection())
        
        # Start alert checking
        alert_task = asyncio.create_task(self._alert_check_loop())
        
        # Start dashboard updates
        dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        
        await asyncio.gather(collection_task, alert_task, dashboard_task)
    
    def stop(self):
        """Stop the dashboard system"""
        self.running = False
        self.metrics_collector.stop_collection()
        logger.info("Stopped analytics dashboard")
    
    async def _alert_check_loop(self):
        """Background loop for checking alerts"""
        while self.running:
            try:
                self.alert_manager.check_alerts()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Alert check error: {e}")
                await asyncio.sleep(30)
    
    async def _dashboard_update_loop(self):
        """Background loop for updating dashboard data"""
        while self.running:
            try:
                self.dashboard_data = self.dashboard_builder.generate_dashboard_data()
                self.last_update = datetime.utcnow()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(60)
    
    def _log_alert(self, alert: Alert):
        """Default alert notification handler"""
        logger.warning(
            f"ALERT [{alert.level.value.upper()}] {alert.title}: "
            f"{alert.description} (Current: {alert.current_value}, "
            f"Threshold: {alert.threshold_value})"
        )
    
    # Public API
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return self.dashboard_data
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return self.metrics_collector.get_metrics_summary()
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return self.alert_manager.get_active_alerts()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health assessment"""
        current_metrics = self.metrics_collector.get_current_metrics()
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Calculate health score
        critical_alerts = len([a for a in active_alerts if a.level == AlertLevel.CRITICAL])
        error_alerts = len([a for a in active_alerts if a.level == AlertLevel.ERROR])
        warning_alerts = len([a for a in active_alerts if a.level == AlertLevel.WARNING])
        
        # Simple health scoring
        health_score = 100
        health_score -= critical_alerts * 30
        health_score -= error_alerts * 20
        health_score -= warning_alerts * 10
        health_score = max(0, health_score)
        
        health_status = "healthy"
        if health_score < 50:
            health_status = "critical"
        elif health_score < 70:
            health_status = "degraded"
        elif health_score < 90:
            health_status = "warning"
        
        return {
            'health_score': health_score,
            'health_status': health_status,
            'total_alerts': len(active_alerts),
            'critical_alerts': critical_alerts,
            'error_alerts': error_alerts,
            'warning_alerts': warning_alerts,
            'metrics_count': len(current_metrics),
            'last_update': self.last_update.isoformat(),
            'uptime_hours': (datetime.utcnow() - self.last_update).total_seconds() / 3600
        }
    
    def get_performance_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """Generate performance report"""
        report = {
            'time_range': f"Last {hours_back} hours",
            'generated_at': datetime.utcnow().isoformat(),
            'summary': self.get_system_health(),
            'components': {}
        }
        
        # Component-specific reports
        components = ['graph', 'memory', 'ml', 'vector', 'events', 'recommendations', 'privacy', 'integration']
        
        for component in components:
            component_data = self.dashboard_builder._generate_time_series_data(component, hours_back)
            
            # Calculate trends and statistics
            component_summary = {
                'metrics_count': len(component_data),
                'trends': self._calculate_trends(component_data)
            }
            
            report['components'][component] = component_summary
        
        return report
    
    def _calculate_trends(self, time_series_data: Dict[str, Any]) -> Dict[str, str]:
        """Calculate trends for time series data"""
        trends = {}
        
        for metric_name, data in time_series_data.items():
            if len(data.get('values', [])) >= 2:
                values = data['values']
                start_value = values[0]
                end_value = values[-1]
                
                if start_value != 0:
                    change_percent = ((end_value - start_value) / start_value) * 100
                    if abs(change_percent) < 5:
                        trend = "stable"
                    elif change_percent > 0:
                        trend = "increasing"
                    else:
                        trend = "decreasing"
                else:
                    trend = "stable"
                
                trends[metric_name] = trend
        
        return trends
    
    def export_metrics(self, format: str = "json", hours_back: int = 24) -> str:
        """Export metrics data"""
        if format == "json":
            data = {
                'export_time': datetime.utcnow().isoformat(),
                'time_range_hours': hours_back,
                'current_metrics': {
                    name: asdict(metric) 
                    for name, metric in self.metrics_collector.get_current_metrics().items()
                },
                'alerts': [asdict(alert) for alert in self.get_active_alerts()],
                'system_health': self.get_system_health()
            }
            return json.dumps(data, indent=2, default=str)
        
        elif format == "csv":
            # Convert to pandas DataFrame and export as CSV
            try:
                import pandas as pd
                
                records = []
                for metric_name in self.metrics_collector.metrics_history:
                    history = self.metrics_collector.get_metric_history(metric_name, hours_back)
                    for metric in history:
                        records.append({
                            'timestamp': metric.timestamp,
                            'metric_name': metric.name,
                            'value': metric.value,
                            'type': metric.metric_type.value
                        })
                
                df = pd.DataFrame(records)
                return df.to_csv(index=False)
            
            except ImportError:
                logger.error("pandas not available for CSV export")
                return ""
        
        return ""


# Web interface (if Dash is available)
def create_web_dashboard(analytics_dashboard: AnalyticsDashboard) -> Optional[Any]:
    """Create web-based dashboard using Dash"""
    if not HAS_DASH:
        logger.warning("Dash not available. Install with: pip install dash")
        return None
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.H1("Learning System Analytics Dashboard"),
        
        # System health overview
        html.Div(id="system-health"),
        
        # Metrics graphs
        html.Div([
            dcc.Graph(id="metrics-overview"),
            dcc.Graph(id="agent-activity"),
            dcc.Graph(id="ml-performance")
        ]),
        
        # Alerts table
        html.Div(id="alerts-table"),
        
        # Auto-refresh
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # Update every minute
            n_intervals=0
        )
    ])
    
    @app.callback(
        [Output('system-health', 'children'),
         Output('metrics-overview', 'figure'),
         Output('alerts-table', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_dashboard(n):
        # Get fresh data
        dashboard_data = analytics_dashboard.get_dashboard_data()
        health = analytics_dashboard.get_system_health()
        alerts = analytics_dashboard.get_active_alerts()
        
        # System health component
        health_color = {
            'healthy': 'green',
            'warning': 'orange',
            'degraded': 'red',
            'critical': 'darkred'
        }.get(health['health_status'], 'gray')
        
        health_component = html.Div([
            html.H3(f"System Health: {health['health_status'].title()}", 
                   style={'color': health_color}),
            html.P(f"Health Score: {health['health_score']}/100"),
            html.P(f"Active Alerts: {health['total_alerts']}")
        ])
        
        # Metrics overview figure
        if HAS_PLOTLY:
            fig = go.Figure()
            
            # Add some example metrics
            overview_data = dashboard_data.get('overview_metrics', {})
            if overview_data:
                fig.add_trace(go.Bar(
                    x=list(overview_data.keys()),
                    y=list(overview_data.values()),
                    name='Current Values'
                ))
            
            fig.update_layout(title="System Metrics Overview")
        else:
            fig = {}
        
        # Alerts table
        alerts_rows = []
        for alert in alerts:
            alerts_rows.append(html.Tr([
                html.Td(alert.title),
                html.Td(alert.level.value),
                html.Td(f"{alert.current_value:.2f}"),
                html.Td(alert.created_at.strftime("%H:%M:%S"))
            ]))
        
        alerts_table = html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Alert"),
                    html.Th("Level"),
                    html.Th("Value"),
                    html.Th("Time")
                ])
            ]),
            html.Tbody(alerts_rows)
        ])
        
        return health_component, fig, alerts_table
    
    return app


# Factory function
def create_analytics_dashboard(integration: LearningSystemIntegration) -> AnalyticsDashboard:
    """Create analytics dashboard for learning system integration"""
    return AnalyticsDashboard(
        integration.graph,
        integration.memory,
        integration.ml_pipeline,
        integration.vector_manager,
        integration.event_store,
        integration.recommendation_engine,
        integration.privacy_engine,
        integration
    )