"""
Workflow Analytics Integration

This module integrates workflow execution data with the existing analytics system
to provide insights into workflow performance, agent effectiveness, and optimization opportunities.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import logging

# Import from existing analytics system
try:
    from analytics.collector import AnalyticsCollector, analytics_session, track_agent_use
    from analytics.metrics import WorkflowMetrics
except ImportError:
    # Fallback for development
    logging.warning("Analytics system not available, using mock implementation")
    AnalyticsCollector = None

from engine import WorkflowExecution, WorkflowStatus, TaskStatus, WorkflowEngine

logger = logging.getLogger(__name__)

@dataclass
class WorkflowAnalytics:
    """Analytics data for workflow execution"""
    execution_id: str
    template_id: str
    template_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    
    # Task metrics
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    
    # Performance metrics
    average_task_duration: Optional[float] = None
    longest_task_duration: Optional[float] = None
    shortest_task_duration: Optional[float] = None
    parallel_efficiency: Optional[float] = None  # How well parallel tasks performed
    
    # Resource metrics
    total_tokens_used: int = 0
    total_files_modified: int = 0
    total_lines_added: int = 0
    total_lines_removed: int = 0
    
    # Quality metrics
    average_quality_score: Optional[float] = None
    error_rate: float = 0.0
    retry_rate: float = 0.0
    
    # Context information
    user_id: Optional[str] = None
    project_context: Dict[str, Any] = field(default_factory=dict)
    global_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class AgentPerformanceMetrics:
    """Performance metrics for individual agents within workflows"""
    agent_name: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_seconds: float = 0.0
    average_duration_seconds: float = 0.0
    total_tokens_used: int = 0
    total_files_modified: int = 0
    quality_scores: List[float] = field(default_factory=list)
    common_failure_reasons: List[str] = field(default_factory=list)

class WorkflowAnalyticsCollector:
    """Collects and analyzes workflow execution data"""
    
    def __init__(self, analytics_collector: Optional[AnalyticsCollector] = None):
        self.analytics_collector = analytics_collector
        self.workflow_executions: Dict[str, WorkflowAnalytics] = {}
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        
    async def start_workflow_tracking(self, 
                                    execution: WorkflowExecution,
                                    user_id: Optional[str] = None) -> None:
        """Start tracking a workflow execution"""
        
        analytics_data = WorkflowAnalytics(
            execution_id=execution.id,
            template_id=execution.template_id,
            template_name=execution.template.name if execution.template else "Unknown",
            start_time=execution.start_time or datetime.now(timezone.utc),
            status=execution.status,
            total_tasks=execution.total_tasks,
            user_id=user_id,
            project_context=execution.global_context.copy(),
            global_parameters=execution.global_context.copy()
        )
        
        self.workflow_executions[execution.id] = analytics_data
        
        # If we have the analytics collector, create a session
        if self.analytics_collector:
            try:
                await self.analytics_collector.start_session(
                    user_id=user_id or "workflow_system",
                    project_path=execution.global_context.get('project_path', '.')
                )
            except Exception as e:
                logger.warning(f"Failed to start analytics session: {e}")
    
    async def track_task_execution(self, 
                                 execution_id: str,
                                 task_id: str,
                                 agent_name: str,
                                 start_time: datetime,
                                 end_time: Optional[datetime] = None,
                                 status: TaskStatus = TaskStatus.PENDING,
                                 result: Optional[Any] = None) -> None:
        """Track individual task execution within a workflow"""
        
        if execution_id not in self.workflow_executions:
            logger.warning(f"Workflow execution {execution_id} not found for task tracking")
            return
        
        workflow_analytics = self.workflow_executions[execution_id]
        
        # Update agent metrics
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentPerformanceMetrics(agent_name=agent_name)
        
        agent_metrics = self.agent_metrics[agent_name]
        agent_metrics.execution_count += 1
        
        if status == TaskStatus.COMPLETED:
            agent_metrics.success_count += 1
        elif status == TaskStatus.FAILED:
            agent_metrics.failure_count += 1
        
        # Calculate duration if available
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds()
            agent_metrics.total_duration_seconds += duration
            agent_metrics.average_duration_seconds = (
                agent_metrics.total_duration_seconds / agent_metrics.execution_count
            )
        
        # Extract metrics from result if available
        if result and hasattr(result, 'metadata'):
            metadata = result.metadata or {}
            agent_metrics.total_tokens_used += metadata.get('tokens_used', 0)
            agent_metrics.total_files_modified += len(result.artifacts) if result.artifacts else 0
            
            # Track quality score if available
            if hasattr(result, 'quality_score') and result.quality_score is not None:
                agent_metrics.quality_scores.append(result.quality_score)
            
            # Track failure reasons
            if status == TaskStatus.FAILED and hasattr(result, 'error') and result.error:
                if result.error not in agent_metrics.common_failure_reasons:
                    agent_metrics.common_failure_reasons.append(result.error)
        
        # Track with main analytics system if available
        if self.analytics_collector:
            try:
                session_id = workflow_analytics.user_id or execution_id
                await track_agent_use(
                    session_id=session_id,
                    agent_name=agent_name,
                    request=f"Workflow task: {task_id}",
                    invocation_reason="workflow_orchestration"
                )
            except Exception as e:
                logger.warning(f"Failed to track agent use: {e}")
    
    async def complete_workflow_tracking(self, execution: WorkflowExecution) -> WorkflowAnalytics:
        """Complete tracking for a workflow execution and calculate final metrics"""
        
        if execution.id not in self.workflow_executions:
            logger.warning(f"Workflow execution {execution.id} not found for completion tracking")
            return None
        
        analytics_data = self.workflow_executions[execution.id]
        
        # Update final status and timing
        analytics_data.status = execution.status
        analytics_data.end_time = execution.end_time or datetime.now(timezone.utc)
        analytics_data.total_duration_seconds = int(
            (analytics_data.end_time - analytics_data.start_time).total_seconds()
        )
        
        # Update task counts
        analytics_data.completed_tasks = execution.completed_tasks
        analytics_data.failed_tasks = execution.failed_tasks
        
        # Calculate derived metrics
        self._calculate_performance_metrics(analytics_data, execution)
        self._calculate_quality_metrics(analytics_data, execution)
        self._calculate_efficiency_metrics(analytics_data, execution)
        
        return analytics_data
    
    def _calculate_performance_metrics(self, analytics: WorkflowAnalytics, execution: WorkflowExecution):
        """Calculate performance-related metrics"""
        if not execution.template:
            return
        
        task_durations = []
        total_tokens = 0
        total_files = 0
        total_lines_added = 0
        total_lines_removed = 0
        
        for task in execution.template.tasks:
            if task.start_time and task.end_time:
                duration = (task.end_time - task.start_time).total_seconds()
                task_durations.append(duration)
            
            if task.result:
                total_tokens += getattr(task.result, 'tokens_used', 0) or 0
                total_files += len(task.result.artifacts) if task.result.artifacts else 0
                
                if hasattr(task.result, 'metadata') and task.result.metadata:
                    metadata = task.result.metadata
                    total_lines_added += metadata.get('lines_added', 0)
                    total_lines_removed += metadata.get('lines_removed', 0)
        
        if task_durations:
            analytics.average_task_duration = sum(task_durations) / len(task_durations)
            analytics.longest_task_duration = max(task_durations)
            analytics.shortest_task_duration = min(task_durations)
        
        analytics.total_tokens_used = total_tokens
        analytics.total_files_modified = total_files
        analytics.total_lines_added = total_lines_added
        analytics.total_lines_removed = total_lines_removed
    
    def _calculate_quality_metrics(self, analytics: WorkflowAnalytics, execution: WorkflowExecution):
        """Calculate quality-related metrics"""
        if not execution.template:
            return
        
        quality_scores = []
        retry_count = 0
        
        for task in execution.template.tasks:
            if task.result and hasattr(task.result, 'quality_score') and task.result.quality_score:
                quality_scores.append(task.result.quality_score)
            
            if task.retry_count > 0:
                retry_count += task.retry_count
        
        if quality_scores:
            analytics.average_quality_score = sum(quality_scores) / len(quality_scores)
        
        # Calculate error rate
        total_tasks = len(execution.template.tasks)
        analytics.error_rate = (analytics.failed_tasks / total_tasks) if total_tasks > 0 else 0.0
        
        # Calculate retry rate
        analytics.retry_rate = (retry_count / total_tasks) if total_tasks > 0 else 0.0
    
    def _calculate_efficiency_metrics(self, analytics: WorkflowAnalytics, execution: WorkflowExecution):
        """Calculate efficiency-related metrics"""
        if not execution.template:
            return
        
        # Calculate parallel efficiency
        parallel_tasks = [t for t in execution.template.tasks if t.execution_mode.value == "parallel"]
        if parallel_tasks:
            # Simple metric: ratio of completed parallel tasks to total parallel tasks
            completed_parallel = sum(1 for t in parallel_tasks if t.status == TaskStatus.COMPLETED)
            analytics.parallel_efficiency = completed_parallel / len(parallel_tasks)
    
    def get_workflow_insights(self, template_id: Optional[str] = None) -> Dict[str, Any]:
        """Get insights and recommendations based on workflow execution data"""
        
        # Filter executions by template if specified
        if template_id:
            executions = [a for a in self.workflow_executions.values() if a.template_id == template_id]
        else:
            executions = list(self.workflow_executions.values())
        
        if not executions:
            return {"message": "No workflow execution data available"}
        
        insights = {
            "summary": self._generate_summary_insights(executions),
            "performance": self._generate_performance_insights(executions),
            "quality": self._generate_quality_insights(executions),
            "agent_performance": self._generate_agent_insights(),
            "recommendations": self._generate_recommendations(executions)
        }
        
        return insights
    
    def _generate_summary_insights(self, executions: List[WorkflowAnalytics]) -> Dict[str, Any]:
        """Generate summary insights"""
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
        failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])
        
        avg_duration = None
        durations = [e.total_duration_seconds for e in executions if e.total_duration_seconds]
        if durations:
            avg_duration = sum(durations) / len(durations)
        
        return {
            "total_executions": total_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "failure_rate": failed_executions / total_executions if total_executions > 0 else 0,
            "average_duration_seconds": avg_duration,
            "total_tasks_executed": sum(e.total_tasks for e in executions),
            "total_tokens_used": sum(e.total_tokens_used for e in executions)
        }
    
    def _generate_performance_insights(self, executions: List[WorkflowAnalytics]) -> Dict[str, Any]:
        """Generate performance insights"""
        avg_task_durations = [e.average_task_duration for e in executions if e.average_task_duration]
        parallel_efficiencies = [e.parallel_efficiency for e in executions if e.parallel_efficiency]
        
        return {
            "average_task_duration": sum(avg_task_durations) / len(avg_task_durations) if avg_task_durations else None,
            "average_parallel_efficiency": sum(parallel_efficiencies) / len(parallel_efficiencies) if parallel_efficiencies else None,
            "performance_trends": self._analyze_performance_trends(executions)
        }
    
    def _generate_quality_insights(self, executions: List[WorkflowAnalytics]) -> Dict[str, Any]:
        """Generate quality insights"""
        quality_scores = [e.average_quality_score for e in executions if e.average_quality_score]
        error_rates = [e.error_rate for e in executions]
        retry_rates = [e.retry_rate for e in executions]
        
        return {
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else None,
            "average_error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
            "average_retry_rate": sum(retry_rates) / len(retry_rates) if retry_rates else 0,
            "quality_trends": self._analyze_quality_trends(executions)
        }
    
    def _generate_agent_insights(self) -> Dict[str, Any]:
        """Generate agent performance insights"""
        agent_insights = {}
        
        for agent_name, metrics in self.agent_metrics.items():
            success_rate = metrics.success_count / metrics.execution_count if metrics.execution_count > 0 else 0
            avg_quality = sum(metrics.quality_scores) / len(metrics.quality_scores) if metrics.quality_scores else None
            
            agent_insights[agent_name] = {
                "execution_count": metrics.execution_count,
                "success_rate": success_rate,
                "average_duration": metrics.average_duration_seconds,
                "average_quality_score": avg_quality,
                "total_tokens_used": metrics.total_tokens_used,
                "common_failures": metrics.common_failure_reasons[:5]  # Top 5
            }
        
        return agent_insights
    
    def _generate_recommendations(self, executions: List[WorkflowAnalytics]) -> List[Dict[str, str]]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Analyze failure patterns
        failed_executions = [e for e in executions if e.status == WorkflowStatus.FAILED]
        if len(failed_executions) / len(executions) > 0.2:  # More than 20% failure rate
            recommendations.append({
                "category": "reliability",
                "priority": "high",
                "recommendation": "High failure rate detected. Review task dependencies and error handling."
            })
        
        # Analyze performance issues
        slow_executions = [e for e in executions if e.total_duration_seconds and e.total_duration_seconds > 3600]  # > 1 hour
        if len(slow_executions) / len(executions) > 0.3:  # More than 30% are slow
            recommendations.append({
                "category": "performance", 
                "priority": "medium",
                "recommendation": "Consider optimizing task parallelization or reducing task complexity."
            })
        
        # Analyze agent performance
        underperforming_agents = [
            name for name, metrics in self.agent_metrics.items()
            if metrics.execution_count > 5 and (metrics.success_count / metrics.execution_count) < 0.8
        ]
        
        if underperforming_agents:
            recommendations.append({
                "category": "agent_optimization",
                "priority": "medium", 
                "recommendation": f"Review configuration for underperforming agents: {', '.join(underperforming_agents)}"
            })
        
        return recommendations
    
    def _analyze_performance_trends(self, executions: List[WorkflowAnalytics]) -> Dict[str, str]:
        """Analyze performance trends over time"""
        # Sort by start time
        sorted_executions = sorted(executions, key=lambda e: e.start_time)
        
        if len(sorted_executions) < 3:
            return {"trend": "insufficient_data"}
        
        # Compare first third vs last third
        first_third = sorted_executions[:len(sorted_executions)//3]
        last_third = sorted_executions[-len(sorted_executions)//3:]
        
        first_avg_duration = sum(e.total_duration_seconds for e in first_third if e.total_duration_seconds) / len(first_third)
        last_avg_duration = sum(e.total_duration_seconds for e in last_third if e.total_duration_seconds) / len(last_third)
        
        if last_avg_duration < first_avg_duration * 0.9:
            return {"trend": "improving", "details": "Performance is improving over time"}
        elif last_avg_duration > first_avg_duration * 1.1:
            return {"trend": "declining", "details": "Performance is declining over time"}
        else:
            return {"trend": "stable", "details": "Performance is stable"}
    
    def _analyze_quality_trends(self, executions: List[WorkflowAnalytics]) -> Dict[str, str]:
        """Analyze quality trends over time"""
        sorted_executions = sorted(executions, key=lambda e: e.start_time)
        
        if len(sorted_executions) < 3:
            return {"trend": "insufficient_data"}
        
        # Compare error rates
        first_third = sorted_executions[:len(sorted_executions)//3]
        last_third = sorted_executions[-len(sorted_executions)//3:]
        
        first_error_rate = sum(e.error_rate for e in first_third) / len(first_third)
        last_error_rate = sum(e.error_rate for e in last_third) / len(last_third)
        
        if last_error_rate < first_error_rate * 0.8:
            return {"trend": "improving", "details": "Quality is improving over time"}
        elif last_error_rate > first_error_rate * 1.2:
            return {"trend": "declining", "details": "Quality is declining over time"}
        else:
            return {"trend": "stable", "details": "Quality is stable"}
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export collected metrics in various formats"""
        data = {
            "workflow_executions": [asdict(analytics) for analytics in self.workflow_executions.values()],
            "agent_metrics": {name: asdict(metrics) for name, metrics in self.agent_metrics.items()},
            "insights": self.get_workflow_insights(),
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
        
        if format_type == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

# Global instance for easy access
workflow_analytics = WorkflowAnalyticsCollector()