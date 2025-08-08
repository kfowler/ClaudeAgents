#!/usr/bin/env python3
"""
Workflow Engine Usage Examples

This file demonstrates various ways to use the Claude Code Workflow Engine
through Python API, including basic usage, advanced configurations, and
custom integrations.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Import workflow components
from workflows.engine import WorkflowEngine, WorkflowTemplate, WorkflowTask, ExecutionMode
from workflows.agent_integration import ClaudeCodeAgentInterface
from workflows.analytics_integration import WorkflowAnalyticsCollector
from workflows.error_handling import ErrorHandler, RecoveryAction, RecoveryStrategy
from workflows.hooks import HookManager, HookContext, HookType


async def example_1_basic_workflow_execution():
    """Example 1: Basic workflow execution"""
    print("=== Example 1: Basic Workflow Execution ===")
    
    # Initialize the workflow engine
    engine = WorkflowEngine()
    await engine.start()
    
    try:
        # Start a pre-built workflow
        execution = await engine.start_workflow(
            template_id="new-feature-pipeline",
            parameters={
                "feature_name": "user-authentication",
                "security_level": "high",
                "testing_required": True
            },
            context={
                "project_path": "/path/to/my/project",
                "git_branch": "feature/user-auth",
                "notification_email": "developer@example.com"
            }
        )
        
        print(f"Started workflow execution: {execution.id}")
        print(f"Template: {execution.template.name}")
        print(f"Total tasks: {execution.total_tasks}")
        
        # Monitor execution progress
        while execution.status.value in ["pending", "running"]:
            await asyncio.sleep(2)  # Poll every 2 seconds
            execution = engine.get_execution_status(execution.id)
            
            progress = (execution.completed_tasks / execution.total_tasks) * 100
            print(f"Progress: {progress:.1f}% ({execution.completed_tasks}/{execution.total_tasks})")
            
            if execution.current_phase:
                print(f"Current phase: {execution.current_phase}")
        
        print(f"Workflow completed with status: {execution.status.value}")
        
        if execution.failed_tasks > 0:
            print(f"Failed tasks: {execution.failed_tasks}")
            for error in execution.error_log:
                print(f"  Error: {error}")
    
    finally:
        await engine.shutdown()


async def example_2_custom_workflow_creation():
    """Example 2: Creating and executing a custom workflow"""
    print("\n=== Example 2: Custom Workflow Creation ===")
    
    # Create a custom workflow template
    custom_workflow = WorkflowTemplate(
        id="code-review-workflow",
        name="Code Review Automation",
        description="Automated code review process with multiple validation steps",
        version="1.0",
        tasks=[
            WorkflowTask(
                id="static_analysis",
                name="Static Code Analysis",
                agent="code-architect",
                description="Perform comprehensive static code analysis",
                parameters={
                    "analysis_scope": "comprehensive",
                    "include_metrics": True,
                    "complexity_check": True
                },
                execution_mode=ExecutionMode.SEQUENTIAL,
                timeout=600,
                max_retries=2
            ),
            WorkflowTask(
                id="security_scan",
                name="Security Vulnerability Scan",
                agent="security-audit-specialist",
                description="Scan for security vulnerabilities and issues",
                parameters={
                    "scan_depth": "thorough",
                    "include_dependencies": True
                },
                dependencies=["static_analysis"],
                execution_mode=ExecutionMode.PARALLEL,
                timeout=900,
                max_retries=1
            ),
            WorkflowTask(
                id="test_validation", 
                name="Test Suite Validation",
                agent="qa-test-engineer",
                description="Validate test coverage and quality",
                parameters={
                    "coverage_threshold": 85,
                    "mutation_testing": False
                },
                dependencies=["static_analysis"],
                execution_mode=ExecutionMode.PARALLEL,
                timeout=1200,
                max_retries=2
            ),
            WorkflowTask(
                id="final_review",
                name="Final Code Review Summary",
                agent="code-architect", 
                description="Generate final review summary and recommendations",
                dependencies=["security_scan", "test_validation"],
                parameters={
                    "generate_report": True,
                    "include_recommendations": True
                },
                execution_mode=ExecutionMode.SEQUENTIAL,
                timeout=300,
                max_retries=1
            )
        ],
        global_parameters={
            "project_language": "python",
            "review_standards": "strict"
        }
    )
    
    # Validate the workflow
    validation_errors = custom_workflow.validate()
    if validation_errors:
        print(f"Workflow validation errors: {validation_errors}")
        return
    
    print("Custom workflow created and validated successfully!")
    
    # Save workflow template to file
    import yaml
    template_data = {
        "id": custom_workflow.id,
        "name": custom_workflow.name,
        "description": custom_workflow.description,
        "version": custom_workflow.version,
        "global_parameters": custom_workflow.global_parameters,
        "tasks": []
    }
    
    for task in custom_workflow.tasks:
        task_data = {
            "id": task.id,
            "name": task.name,
            "agent": task.agent,
            "description": task.description,
            "parameters": task.parameters,
            "dependencies": task.dependencies,
            "execution_mode": task.execution_mode.value,
            "timeout": task.timeout,
            "max_retries": task.max_retries
        }
        template_data["tasks"].append(task_data)
    
    # Save to workflow_templates directory
    template_file = Path("workflow_templates/code-review-workflow.yaml")
    template_file.parent.mkdir(exist_ok=True)
    
    with open(template_file, 'w') as f:
        yaml.dump(template_data, f, default_flow_style=False, indent=2)
    
    print(f"Workflow template saved to: {template_file}")


async def example_3_advanced_error_handling():
    """Example 3: Advanced error handling and recovery"""
    print("\n=== Example 3: Advanced Error Handling ===")
    
    # Initialize error handler
    error_handler = ErrorHandler()
    
    # Register custom error handling rules
    error_handler.register_error_rule(
        "model_training_timeout",
        RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            description="Retry model training with reduced dataset",
            parameters={
                "reduce_dataset_size": True,
                "retry_delay": 60,
                "max_retries": 2
            },
            timeout_seconds=7200  # 2 hours
        )
    )
    
    error_handler.register_error_rule(
        "api_rate_limit",
        RecoveryAction(
            strategy=RecoveryStrategy.FALLBACK,
            description="Use fallback API or cached results",
            parameters={
                "use_cache": True,
                "fallback_endpoint": "backup_api"
            },
            fallback_task="use_cached_results"
        )
    )
    
    # Register global error handler
    async def global_error_logger(error_context):
        """Log all errors to monitoring system"""
        print(f"Global error handler: {error_context.workflow_id} - {error_context.error_message}")
        
        # In a real implementation, this would send to monitoring system
        error_data = {
            "timestamp": error_context.timestamp.isoformat(),
            "workflow_id": error_context.workflow_id,
            "task_id": error_context.task_id,
            "error_message": error_context.error_message,
            "severity": error_context.severity.value
        }
        
        # Save to error log file
        error_log_file = Path("error_logs") / f"{error_context.workflow_id}_errors.json"
        error_log_file.parent.mkdir(exist_ok=True)
        
        if error_log_file.exists():
            with open(error_log_file, 'r') as f:
                errors = json.load(f)
        else:
            errors = []
        
        errors.append(error_data)
        
        with open(error_log_file, 'w') as f:
            json.dump(errors, f, indent=2)
    
    error_handler.register_global_handler(global_error_logger)
    
    print("Advanced error handling configuration completed!")
    print(f"Registered {len(error_handler.error_rules)} error handling rules")


async def example_4_custom_hooks():
    """Example 4: Custom hooks for workflow customization"""
    print("\n=== Example 4: Custom Hooks ===")
    
    # Initialize hook manager
    hook_manager = HookManager()
    
    # Create custom pre-workflow hook
    async def setup_development_environment(context: HookContext):
        """Setup development environment before workflow execution"""
        print(f"Setting up development environment for workflow {context.execution.id}")
        
        # Create temporary directories
        temp_dir = Path(f"/tmp/workflow_{context.execution.id}")
        temp_dir.mkdir(exist_ok=True)
        
        # Store temp directory in context for cleanup
        context.execution.global_context["temp_directory"] = str(temp_dir)
        
        # Setup virtual environment (mock)
        print("Creating virtual environment...")
        print("Installing dependencies...")
        
        # In real implementation, would run actual setup commands
        await asyncio.sleep(1)  # Simulate setup time
        
        print("Development environment setup complete!")
    
    # Create custom post-workflow hook
    async def generate_workflow_report(context: HookContext):
        """Generate comprehensive workflow execution report"""
        print(f"Generating report for workflow {context.execution.id}")
        
        # Gather execution metrics
        total_duration = (context.timestamp - context.execution.start_time).total_seconds() if context.execution.start_time else 0
        success_rate = (context.execution.completed_tasks / context.execution.total_tasks * 100) if context.execution.total_tasks > 0 else 0
        
        report_data = {
            "workflow_id": context.execution.id,
            "template_name": context.execution.template.name if context.execution.template else "Unknown",
            "execution_summary": {
                "status": context.execution.status.value,
                "total_duration_seconds": total_duration,
                "total_tasks": context.execution.total_tasks,
                "completed_tasks": context.execution.completed_tasks,
                "failed_tasks": context.execution.failed_tasks,
                "success_rate": success_rate
            },
            "task_details": []
        }
        
        # Add task details if template is available
        if context.execution.template:
            for task in context.execution.template.tasks:
                task_duration = None
                if task.start_time and task.end_time:
                    task_duration = (task.end_time - task.start_time).total_seconds()
                
                task_detail = {
                    "id": task.id,
                    "name": task.name,
                    "agent": task.agent,
                    "status": task.status.value,
                    "duration_seconds": task_duration,
                    "retry_count": task.retry_count
                }
                
                if task.result and task.result.error:
                    task_detail["error"] = task.result.error
                
                report_data["task_details"].append(task_detail)
        
        # Save report to file
        report_file = Path(f"reports/workflow_report_{context.execution.id}.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"Workflow report saved to: {report_file}")
        
        # Store report path in context
        context.execution.global_context["workflow_report"] = str(report_file)
    
    # Create task-level hook for monitoring
    async def monitor_task_resources(context: HookContext):
        """Monitor resource usage during task execution"""
        if context.task:
            print(f"Monitoring resources for task: {context.task.name}")
            
            # In real implementation, would monitor CPU, memory, etc.
            # For demo, just log the monitoring
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            resource_data = {
                "task_id": context.task.id,
                "timestamp": context.timestamp.isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
            
            print(f"Resource usage - CPU: {cpu_percent}%, Memory: {memory_percent}%")
            
            # Store resource data
            if "resource_monitoring" not in context.execution.global_context:
                context.execution.global_context["resource_monitoring"] = []
            
            context.execution.global_context["resource_monitoring"].append(resource_data)
    
    # Register hooks
    hook_manager.register_hook("setup_development_environment", setup_development_environment)
    hook_manager.register_hook("generate_workflow_report", generate_workflow_report)
    hook_manager.register_hook("monitor_task_resources", monitor_task_resources)
    
    print("Custom hooks registered successfully!")
    
    # List all available hooks
    hooks = hook_manager.list_hooks()
    print(f"Available hooks: {hooks}")


async def example_5_analytics_and_insights():
    """Example 5: Analytics and workflow insights"""
    print("\n=== Example 5: Analytics and Insights ===")
    
    # Initialize analytics collector
    analytics = WorkflowAnalyticsCollector()
    
    # Simulate some workflow execution data for analytics
    from workflows.analytics_integration import WorkflowAnalytics, AgentPerformanceMetrics
    from workflows.engine import WorkflowStatus
    
    # Create sample analytics data
    sample_analytics = [
        WorkflowAnalytics(
            execution_id="exec-1",
            template_id="new-feature-pipeline",
            template_name="New Feature Pipeline",
            start_time=datetime.now(),
            status=WorkflowStatus.COMPLETED,
            total_tasks=8,
            completed_tasks=8,
            failed_tasks=0,
            average_task_duration=120.5,
            total_tokens_used=15000,
            total_files_modified=12,
            average_quality_score=8.5,
            error_rate=0.0
        ),
        WorkflowAnalytics(
            execution_id="exec-2", 
            template_id="production-readiness",
            template_name="Production Readiness",
            start_time=datetime.now(),
            status=WorkflowStatus.COMPLETED,
            total_tasks=10,
            completed_tasks=9,
            failed_tasks=1,
            average_task_duration=95.2,
            total_tokens_used=22000,
            total_files_modified=8,
            average_quality_score=7.8,
            error_rate=0.1
        )
    ]
    
    # Add sample data to analytics collector
    for analytics_data in sample_analytics:
        analytics.workflow_executions[analytics_data.execution_id] = analytics_data
    
    # Generate insights
    insights = analytics.get_workflow_insights()
    
    print("Workflow Analytics Insights:")
    print(f"Total executions: {insights['summary']['total_executions']}")
    print(f"Success rate: {insights['summary']['success_rate']:.2%}")
    print(f"Average duration: {insights['summary']['average_duration_seconds']:.1f} seconds")
    
    if insights['recommendations']:
        print("\nRecommendations:")
        for rec in insights['recommendations']:
            print(f"- [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    
    # Export analytics data
    analytics_export = analytics.export_metrics("json")
    
    # Save analytics export
    analytics_file = Path("analytics/workflow_analytics.json")
    analytics_file.parent.mkdir(exist_ok=True)
    
    with open(analytics_file, 'w') as f:
        f.write(analytics_export)
    
    print(f"\nAnalytics data exported to: {analytics_file}")


async def example_6_agent_integration():
    """Example 6: Advanced agent integration and customization"""
    print("\n=== Example 6: Agent Integration ===")
    
    # Initialize agent interface
    agent_interface = ClaudeCodeAgentInterface()
    
    # Get available agents
    available_agents = agent_interface.get_available_agents()
    print(f"Available agents: {len(available_agents)}")
    
    for agent in available_agents[:5]:  # Show first 5
        print(f"  - {agent.name}: {', '.join(agent.expertise_areas[:3])}...")
    
    # Recommend agents for a specific task
    recommendations = agent_interface.recommend_agents(
        "I need to implement secure user authentication with OAuth2 integration",
        context={"tech_stack": ["python", "flask", "react"]}
    )
    
    print(f"\nAgent recommendations for OAuth2 implementation:")
    for agent_name, score in recommendations[:3]:
        print(f"  - {agent_name}: {score:.2f}")
    
    # Validate agent chain
    agent_chain = ["security-audit-specialist", "full-stack-architect", "qa-test-engineer"]
    validation_errors = agent_interface.validate_agent_chain(agent_chain)
    
    if validation_errors:
        print(f"Agent chain validation errors: {validation_errors}")
    else:
        print("Agent chain validation passed!")
    
    # Get suggestions for missing agents
    suggestions = agent_interface.suggest_missing_agents(
        agent_chain,
        context={"deployment_target": "production", "compliance_required": True}
    )
    
    if suggestions:
        print("Missing agent suggestions:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")


async def main():
    """Run all examples"""
    print("Claude Code Workflow Engine - Usage Examples")
    print("=" * 50)
    
    try:
        # Run examples (comment out any you don't want to run)
        await example_1_basic_workflow_execution()
        await example_2_custom_workflow_creation()
        await example_3_advanced_error_handling()
        await example_4_custom_hooks()
        await example_5_analytics_and_insights()
        await example_6_agent_integration()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())