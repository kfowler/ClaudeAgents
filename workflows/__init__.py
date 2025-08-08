"""
Claude Code Workflow Engine

A comprehensive workflow automation system that orchestrates multiple AI agents
for common development scenarios with dependency management, parallel execution,
progress tracking, error handling, and rollback capabilities.
"""

__version__ = "1.0.0"
__author__ = "Claude Code Team"
__description__ = "Workflow automation system for multi-agent orchestration"

# Core components
from .engine import WorkflowEngine, WorkflowTemplate, WorkflowTask, WorkflowExecution
from .engine import WorkflowStatus, TaskStatus, ExecutionMode

# Agent integration
from .agent_integration import ClaudeCodeAgentInterface, AgentMetadata

# Analytics and monitoring
from .analytics_integration import WorkflowAnalyticsCollector, WorkflowAnalytics

# Error handling and recovery
from .error_handling import ErrorHandler, ErrorContext, RecoveryAction, RecoveryStrategy

# Hooks system
from .hooks import HookManager, HookContext, HookType, HookConfiguration

# Dashboard
from .dashboard import WorkflowDashboard, create_dashboard

__all__ = [
    # Core
    "WorkflowEngine",
    "WorkflowTemplate", 
    "WorkflowTask",
    "WorkflowExecution",
    "WorkflowStatus",
    "TaskStatus",
    "ExecutionMode",
    
    # Agent integration
    "ClaudeCodeAgentInterface",
    "AgentMetadata",
    
    # Analytics
    "WorkflowAnalyticsCollector",
    "WorkflowAnalytics",
    
    # Error handling
    "ErrorHandler",
    "ErrorContext",
    "RecoveryAction", 
    "RecoveryStrategy",
    
    # Hooks
    "HookManager",
    "HookContext",
    "HookType",
    "HookConfiguration",
    
    # Dashboard
    "WorkflowDashboard",
    "create_dashboard",
]