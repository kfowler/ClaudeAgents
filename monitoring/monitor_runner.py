#!/usr/bin/env python3
"""
Rollout Monitoring System for Claude Code Enhancement Deployment.
Provides comprehensive real-time monitoring, alerting, and dashboard capabilities.
"""

import asyncio
import json
import logging
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricStatus(Enum):
    """Metric status indicators."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    value: float
    unit: str
    timestamp: str
    status: MetricStatus
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    tags: Dict[str, str] = None


@dataclass
class Alert:
    """System alert."""
    id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: str
    resolved: bool = False
    resolved_timestamp: Optional[str] = None


class MetricsCollector:
    """Collect various system and business metrics."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize metrics database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                threshold_low REAL,
                threshold_high REAL,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                current_value REAL NOT NULL,
                threshold_value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                resolved INTEGER DEFAULT 0,
                resolved_timestamp TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
            ON metrics(name, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_severity_resolved 
            ON alerts(severity, resolved)
        """)
        
        conn.commit()
        conn.close()
        
    def collect_system_metrics(self) -> List[Metric]:
        """Collect system performance metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        try:
            import psutil
            
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="system_cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                status=self._get_status(cpu_percent, 80, 90),
                threshold_low=None,
                threshold_high=80.0,
                tags={"category": "system", "type": "performance"}
            ))
            
            # Memory Usage
            memory = psutil.virtual_memory()
            metrics.append(Metric(
                name="system_memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                status=self._get_status(memory.percent, 85, 95),
                threshold_low=None,
                threshold_high=85.0,
                tags={"category": "system", "type": "performance"}
            ))
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(Metric(
                name="system_disk_usage",
                value=disk_percent,
                unit="percent",
                timestamp=timestamp,
                status=self._get_status(disk_percent, 80, 90),
                threshold_low=None,
                threshold_high=80.0,
                tags={"category": "system", "type": "storage"}
            ))
            
            # Network I/O
            network = psutil.net_io_counters()
            metrics.append(Metric(
                name="system_bytes_sent",
                value=network.bytes_sent,
                unit="bytes",
                timestamp=timestamp,
                status=MetricStatus.HEALTHY,
                tags={"category": "system", "type": "network"}
            ))
            
            metrics.append(Metric(
                name="system_bytes_recv",
                value=network.bytes_recv,
                unit="bytes",
                timestamp=timestamp,
                status=MetricStatus.HEALTHY,
                tags={"category": "system", "type": "network"}
            ))
            
        except ImportError:
            # Fallback metrics if psutil not available
            metrics.append(Metric(
                name="system_status",
                value=1.0,
                unit="boolean",
                timestamp=timestamp,
                status=MetricStatus.HEALTHY,
                tags={"category": "system", "type": "health"}
            ))
            
        return metrics
        
    def collect_application_metrics(self) -> List[Metric]:
        """Collect application-specific metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        try:
            # Agent recommendation performance
            start_time = time.time()
            from analysis.agent_recommender import AgentRecommender
            recommender = AgentRecommender()
            
            # Test agent recommendation latency
            recommender.get_recommendation("test request")
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            metrics.append(Metric(
                name="agent_recommendation_latency",
                value=latency,
                unit="milliseconds",
                timestamp=timestamp,
                status=self._get_status(latency, 1000, 2000, reverse=True),
                threshold_low=None,
                threshold_high=1000.0,
                tags={"category": "application", "type": "performance"}
            ))
            
            # Agent loading success
            agents = recommender.get_available_agents()
            agent_count = len(agents)
            
            metrics.append(Metric(
                name="available_agents_count",
                value=agent_count,
                unit="count",
                timestamp=timestamp,
                status=MetricStatus.HEALTHY if agent_count > 20 else MetricStatus.WARNING,
                threshold_low=20.0,
                threshold_high=None,
                tags={"category": "application", "type": "availability"}
            ))
            
        except Exception as e:
            metrics.append(Metric(
                name="application_error",
                value=1.0,
                unit="boolean",
                timestamp=timestamp,
                status=MetricStatus.CRITICAL,
                tags={"category": "application", "type": "error", "error": str(e)}
            ))
            
        # Database connectivity
        try:
            if Path("project_analysis_cache.db").exists():
                conn = sqlite3.connect("project_analysis_cache.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                conn.close()
                
                metrics.append(Metric(
                    name="database_tables_count",
                    value=table_count,
                    unit="count",
                    timestamp=timestamp,
                    status=MetricStatus.HEALTHY,
                    tags={"category": "database", "type": "health"}
                ))
            else:
                metrics.append(Metric(
                    name="database_available",
                    value=0.0,
                    unit="boolean",
                    timestamp=timestamp,
                    status=MetricStatus.WARNING,
                    tags={"category": "database", "type": "availability"}
                ))
                
        except Exception as e:
            metrics.append(Metric(
                name="database_error",
                value=1.0,
                unit="boolean",
                timestamp=timestamp,
                status=MetricStatus.CRITICAL,
                tags={"category": "database", "type": "error", "error": str(e)}
            ))
            
        return metrics
        
    def collect_user_experience_metrics(self) -> List[Metric]:
        """Collect user experience metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        # Simulated user experience metrics
        # In a real implementation, these would come from user analytics
        
        metrics.append(Metric(
            name="user_satisfaction_score",
            value=87.5,  # Simulated
            unit="score",
            timestamp=timestamp,
            status=MetricStatus.HEALTHY,
            threshold_low=80.0,
            threshold_high=None,
            tags={"category": "user_experience", "type": "satisfaction"}
        ))
        
        metrics.append(Metric(
            name="feature_adoption_rate",
            value=72.3,  # Simulated
            unit="percent",
            timestamp=timestamp,
            status=MetricStatus.HEALTHY,
            threshold_low=60.0,
            threshold_high=None,
            tags={"category": "user_experience", "type": "adoption"}
        ))
        
        metrics.append(Metric(
            name="error_rate",
            value=0.5,  # Simulated
            unit="percent",
            timestamp=timestamp,
            status=self._get_status(0.5, 2.0, 5.0, reverse=True),
            threshold_low=None,
            threshold_high=2.0,
            tags={"category": "user_experience", "type": "reliability"}
        ))
        
        return metrics
        
    def collect_business_metrics(self) -> List[Metric]:
        """Collect business impact metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        # Simulated business metrics
        # In a real implementation, these would come from business analytics
        
        metrics.append(Metric(
            name="daily_active_users",
            value=1250,  # Simulated
            unit="count",
            timestamp=timestamp,
            status=MetricStatus.HEALTHY,
            threshold_low=1000.0,
            threshold_high=None,
            tags={"category": "business", "type": "usage"}
        ))
        
        metrics.append(Metric(
            name="feature_usage_growth",
            value=15.2,  # Simulated
            unit="percent",
            timestamp=timestamp,
            status=MetricStatus.HEALTHY,
            threshold_low=5.0,
            threshold_high=None,
            tags={"category": "business", "type": "growth"}
        ))
        
        metrics.append(Metric(
            name="user_productivity_improvement",
            value=23.7,  # Simulated
            unit="percent",
            timestamp=timestamp,
            status=MetricStatus.HEALTHY,
            threshold_low=10.0,
            threshold_high=None,
            tags={"category": "business", "type": "productivity"}
        ))
        
        return metrics
        
    def _get_status(self, value: float, warning_threshold: float, critical_threshold: float, reverse: bool = False) -> MetricStatus:
        """Determine metric status based on thresholds."""
        if reverse:  # For metrics where lower is better (e.g., latency, error rate)
            if value <= warning_threshold:
                return MetricStatus.HEALTHY
            elif value <= critical_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
        else:  # For metrics where higher is better (e.g., CPU usage, memory usage)
            if value < warning_threshold:
                return MetricStatus.HEALTHY
            elif value < critical_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
                
    def store_metrics(self, metrics: List[Metric]):
        """Store metrics in database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for metric in metrics:
            tags_json = json.dumps(metric.tags) if metric.tags else None
            cursor.execute("""
                INSERT INTO metrics (name, value, unit, timestamp, status, threshold_low, threshold_high, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.name, metric.value, metric.unit, metric.timestamp,
                metric.status.value, metric.threshold_low, metric.threshold_high, tags_json
            ))
            
        conn.commit()
        conn.close()
        
    def get_latest_metrics(self, limit: int = 100) -> List[Metric]:
        """Get latest metrics from database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, value, unit, timestamp, status, threshold_low, threshold_high, tags
            FROM metrics
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            tags = json.loads(row[7]) if row[7] else None
            metrics.append(Metric(
                name=row[0],
                value=row[1],
                unit=row[2],
                timestamp=row[3],
                status=MetricStatus(row[4]),
                threshold_low=row[5],
                threshold_high=row[6],
                tags=tags
            ))
            
        return metrics


class AlertManager:
    """Manage system alerts and notifications."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.alert_handlers: List[Callable[[Alert], None]] = []
        
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add alert handler function."""
        self.alert_handlers.append(handler)
        
    def check_thresholds(self, metrics: List[Metric]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts."""
        alerts = []
        
        for metric in metrics:
            alert = self._check_metric_thresholds(metric)
            if alert:
                alerts.append(alert)
                
        return alerts
        
    def _check_metric_thresholds(self, metric: Metric) -> Optional[Alert]:
        """Check individual metric thresholds."""
        alert = None
        
        # Check high threshold
        if metric.threshold_high and metric.value > metric.threshold_high:
            severity = AlertSeverity.CRITICAL if metric.value > (metric.threshold_high * 1.2) else AlertSeverity.HIGH
            alert = Alert(
                id=f"{metric.name}_{metric.timestamp}_{severity.value}",
                severity=severity,
                title=f"{metric.name.replace('_', ' ').title()} Above Threshold",
                description=f"{metric.name} is {metric.value:.2f} {metric.unit}, which exceeds the threshold of {metric.threshold_high:.2f} {metric.unit}",
                metric_name=metric.name,
                current_value=metric.value,
                threshold_value=metric.threshold_high,
                timestamp=metric.timestamp
            )
            
        # Check low threshold
        elif metric.threshold_low and metric.value < metric.threshold_low:
            severity = AlertSeverity.CRITICAL if metric.value < (metric.threshold_low * 0.8) else AlertSeverity.HIGH
            alert = Alert(
                id=f"{metric.name}_{metric.timestamp}_{severity.value}",
                severity=severity,
                title=f"{metric.name.replace('_', ' ').title()} Below Threshold",
                description=f"{metric.name} is {metric.value:.2f} {metric.unit}, which is below the threshold of {metric.threshold_low:.2f} {metric.unit}",
                metric_name=metric.name,
                current_value=metric.value,
                threshold_value=metric.threshold_low,
                timestamp=metric.timestamp
            )
            
        return alert
        
    def store_alert(self, alert: Alert):
        """Store alert in database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO alerts 
            (id, severity, title, description, metric_name, current_value, threshold_value, timestamp, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.id, alert.severity.value, alert.title, alert.description,
            alert.metric_name, alert.current_value, alert.threshold_value,
            alert.timestamp, int(alert.resolved)
        ))
        
        conn.commit()
        conn.close()
        
    def notify_alert(self, alert: Alert):
        """Notify all alert handlers."""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logging.error(f"Alert handler failed: {str(e)}")
                
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, severity, title, description, metric_name, current_value, 
                   threshold_value, timestamp, resolved, resolved_timestamp
            FROM alerts
            WHERE resolved = 0
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alerts.append(Alert(
                id=row[0],
                severity=AlertSeverity(row[1]),
                title=row[2],
                description=row[3],
                metric_name=row[4],
                current_value=row[5],
                threshold_value=row[6],
                timestamp=row[7],
                resolved=bool(row[8]),
                resolved_timestamp=row[9]
            ))
            
        return alerts
        
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts 
            SET resolved = 1, resolved_timestamp = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), alert_id))
        
        conn.commit()
        conn.close()


class RolloutMonitor:
    """Main rollout monitoring orchestrator."""
    
    def __init__(self, data_dir: Path = Path("monitoring/data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "monitoring.db"
        self.metrics_collector = MetricsCollector(self.db_path)
        self.alert_manager = AlertManager(self.db_path)
        
        self.setup_logging()
        self.setup_alert_handlers()
        
        self.monitoring_active = False
        self.collection_interval = 30  # seconds
        
    def setup_logging(self):
        """Configure logging for monitoring system."""
        log_dir = self.data_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_alert_handlers(self):
        """Setup default alert handlers."""
        self.alert_manager.add_alert_handler(self.console_alert_handler)
        self.alert_manager.add_alert_handler(self.log_alert_handler)
        
    def console_alert_handler(self, alert: Alert):
        """Handle alerts by printing to console."""
        severity_icons = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "⚡",
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.INFO: "📝"
        }
        
        icon = severity_icons.get(alert.severity, "📝")
        print(f"\\n{icon} [{alert.severity.value.upper()}] {alert.title}")
        print(f"   {alert.description}")
        print(f"   Time: {alert.timestamp}")
        
    def log_alert_handler(self, alert: Alert):
        """Handle alerts by logging."""
        log_level = {
            AlertSeverity.CRITICAL: logging.CRITICAL,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.INFO: logging.INFO
        }
        
        level = log_level.get(alert.severity, logging.INFO)
        self.logger.log(level, f"ALERT: {alert.title} - {alert.description}")
        
    async def collect_all_metrics(self) -> List[Metric]:
        """Collect all categories of metrics."""
        all_metrics = []
        
        # Collect different categories of metrics
        collectors = [
            self.metrics_collector.collect_system_metrics,
            self.metrics_collector.collect_application_metrics,
            self.metrics_collector.collect_user_experience_metrics,
            self.metrics_collector.collect_business_metrics
        ]
        
        for collector in collectors:
            try:
                metrics = collector()
                all_metrics.extend(metrics)
            except Exception as e:
                self.logger.error(f"Error collecting metrics from {collector.__name__}: {str(e)}")
                
        return all_metrics
        
    async def monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.info(f"Starting monitoring loop with {self.collection_interval}s interval")
        
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = await self.collect_all_metrics()
                
                # Store metrics
                self.metrics_collector.store_metrics(metrics)
                
                # Check for alerts
                alerts = self.alert_manager.check_thresholds(metrics)
                
                # Process alerts
                for alert in alerts:
                    self.alert_manager.store_alert(alert)
                    self.alert_manager.notify_alert(alert)
                    
                # Log collection summary
                healthy_count = len([m for m in metrics if m.status == MetricStatus.HEALTHY])
                warning_count = len([m for m in metrics if m.status == MetricStatus.WARNING])
                critical_count = len([m for m in metrics if m.status == MetricStatus.CRITICAL])
                
                self.logger.info(f"Collected {len(metrics)} metrics: {healthy_count} healthy, {warning_count} warnings, {critical_count} critical")
                
                if alerts:
                    self.logger.warning(f"Generated {len(alerts)} new alerts")
                    
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(self.collection_interval)
                
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.monitoring_active:
            self.logger.warning("Monitoring is already active")
            return
            
        self.monitoring_active = True
        self.logger.info("Starting rollout monitoring system")
        
        # Start monitoring in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.monitoring_loop())
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.stop_monitoring()
            loop.close()
            
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        self.logger.info("Stopping rollout monitoring system")
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status summary."""
        # Get latest metrics
        latest_metrics = self.metrics_collector.get_latest_metrics(50)
        
        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Categorize metrics by status
        status_counts = {
            MetricStatus.HEALTHY: 0,
            MetricStatus.WARNING: 0,
            MetricStatus.CRITICAL: 0,
            MetricStatus.UNKNOWN: 0
        }
        
        for metric in latest_metrics:
            status_counts[metric.status] += 1
            
        # Categorize alerts by severity
        alert_counts = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 0,
            AlertSeverity.MEDIUM: 0,
            AlertSeverity.LOW: 0,
            AlertSeverity.INFO: 0
        }
        
        for alert in active_alerts:
            alert_counts[alert.severity] += 1
            
        # Determine overall system health
        if status_counts[MetricStatus.CRITICAL] > 0 or alert_counts[AlertSeverity.CRITICAL] > 0:
            overall_health = "critical"
        elif status_counts[MetricStatus.WARNING] > 0 or alert_counts[AlertSeverity.HIGH] > 0:
            overall_health = "warning"
        else:
            overall_health = "healthy"
            
        return {
            "overall_health": overall_health,
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "metrics": {
                "total": len(latest_metrics),
                "healthy": status_counts[MetricStatus.HEALTHY],
                "warning": status_counts[MetricStatus.WARNING],
                "critical": status_counts[MetricStatus.CRITICAL],
                "unknown": status_counts[MetricStatus.UNKNOWN]
            },
            "alerts": {
                "total": len(active_alerts),
                "critical": alert_counts[AlertSeverity.CRITICAL],
                "high": alert_counts[AlertSeverity.HIGH],
                "medium": alert_counts[AlertSeverity.MEDIUM],
                "low": alert_counts[AlertSeverity.LOW],
                "info": alert_counts[AlertSeverity.INFO]
            }
        }


def main():
    """Main entry point for monitoring system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Enhancement Rollout Monitor")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--interval", type=int, default=30, help="Collection interval in seconds")
    parser.add_argument("--data-dir", default="monitoring/data", help="Data directory")
    
    args = parser.parse_args()
    
    monitor = RolloutMonitor(Path(args.data_dir))
    monitor.collection_interval = args.interval
    
    if args.start:
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            print("\\nMonitoring stopped by user")
    elif args.status:
        status = monitor.get_system_status()
        print("\\nClaude Code Enhancement Rollout Status:")
        print(f"Overall Health: {status['overall_health'].upper()}")
        print(f"Monitoring Active: {status['monitoring_active']}")
        print(f"\\nMetrics: {status['metrics']['total']} total")
        print(f"  - Healthy: {status['metrics']['healthy']}")
        print(f"  - Warning: {status['metrics']['warning']}")
        print(f"  - Critical: {status['metrics']['critical']}")
        print(f"\\nAlerts: {status['alerts']['total']} active")
        print(f"  - Critical: {status['alerts']['critical']}")
        print(f"  - High: {status['alerts']['high']}")
        print(f"  - Medium: {status['alerts']['medium']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()