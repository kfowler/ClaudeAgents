#!/usr/bin/env python3
"""
Workflow CLI Interface

Command-line interface for managing workflow templates and executions.
Provides commands for listing, starting, monitoring, and managing workflows.
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import yaml
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout

# Import workflow engine components
try:
    from engine import WorkflowEngine, WorkflowStatus, TaskStatus
    from agent_integration import ClaudeCodeAgentInterface
    from analytics_integration import WorkflowAnalytics
except ImportError as e:
    print(f"Error importing workflow components: {e}")
    sys.exit(1)

console = Console()

class WorkflowCLI:
    """Command-line interface for workflow management"""
    
    def __init__(self):
        self.engine = WorkflowEngine()
        self.agent_interface = ClaudeCodeAgentInterface()
        self.analytics = WorkflowAnalytics()
    
    async def initialize(self):
        """Initialize the CLI and workflow engine"""
        await self.engine.start()
        console.print("[green]Workflow Engine initialized successfully[/green]")
    
    async def shutdown(self):
        """Shutdown the CLI and workflow engine"""
        await self.engine.shutdown()
        console.print("[yellow]Workflow Engine shut down[/yellow]")
    
    def list_templates(self, format_type: str = "table") -> None:
        """List available workflow templates"""
        templates = self.engine.get_templates()
        
        if not templates:
            console.print("[yellow]No workflow templates found[/yellow]")
            return
        
        if format_type == "json":
            template_data = []
            for template in templates:
                template_data.append({
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "version": template.version,
                    "tasks": len(template.tasks),
                    "author": template.author
                })
            print(json.dumps(template_data, indent=2))
        
        elif format_type == "yaml":
            for template in templates:
                print(f"---")
                print(f"id: {template.id}")
                print(f"name: {template.name}")
                print(f"description: {template.description}")
                print(f"version: {template.version}")
                print(f"tasks: {len(template.tasks)}")
                print(f"author: {template.author}")
        
        else:  # table format
            table = Table(title="Available Workflow Templates")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="bright_white", max_width=30)
            table.add_column("Description", style="white", max_width=50)
            table.add_column("Tasks", justify="center", style="green")
            table.add_column("Version", style="blue")
            table.add_column("Author", style="magenta")
            
            for template in templates:
                table.add_row(
                    template.id,
                    template.name,
                    template.description[:50] + "..." if len(template.description) > 50 else template.description,
                    str(len(template.tasks)),
                    template.version,
                    template.author
                )
            
            console.print(table)
    
    def show_template(self, template_id: str) -> None:
        """Show detailed information about a specific template"""
        template = self.engine.get_template(template_id)
        
        if not template:
            console.print(f"[red]Template '{template_id}' not found[/red]")
            return
        
        # Template overview panel
        overview = Panel(
            f"[bold]{template.name}[/bold]\n\n"
            f"[cyan]Description:[/cyan] {template.description}\n"
            f"[cyan]Version:[/cyan] {template.version}\n"
            f"[cyan]Author:[/cyan] {template.author}\n"
            f"[cyan]Tasks:[/cyan] {len(template.tasks)}\n"
            f"[cyan]Created:[/cyan] {template.created_at}",
            title=f"Template: {template_id}",
            expand=False
        )
        console.print(overview)
        
        # Tasks table
        if template.tasks:
            table = Table(title="Workflow Tasks")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="bright_white", max_width=25)
            table.add_column("Agent", style="yellow")
            table.add_column("Dependencies", style="blue")
            table.add_column("Mode", style="green")
            table.add_column("Timeout", justify="right", style="magenta")
            
            for task in template.tasks:
                dependencies_str = ", ".join(task.dependencies) if task.dependencies else "None"
                timeout_str = f"{task.timeout}s" if task.timeout else "Default"
                
                table.add_row(
                    task.id,
                    task.name[:25] + "..." if len(task.name) > 25 else task.name,
                    task.agent,
                    dependencies_str,
                    task.execution_mode.value,
                    timeout_str
                )
            
            console.print(table)
        
        # Global parameters
        if template.global_parameters:
            console.print("\n[bold cyan]Global Parameters:[/bold cyan]")
            for key, value in template.global_parameters.items():
                console.print(f"  [yellow]{key}:[/yellow] {value}")
    
    async def start_workflow(self, 
                           template_id: str, 
                           parameters: Optional[Dict[str, Any]] = None,
                           context: Optional[Dict[str, Any]] = None,
                           monitor: bool = True) -> str:
        """Start a workflow execution"""
        try:
            execution = await self.engine.start_workflow(template_id, parameters, context)
            
            console.print(f"[green]Started workflow execution: {execution.id}[/green]")
            console.print(f"[cyan]Template:[/cyan] {template_id}")
            console.print(f"[cyan]Total Tasks:[/cyan] {execution.total_tasks}")
            
            if monitor:
                await self.monitor_execution(execution.id, live_updates=True)
            
            return execution.id
            
        except ValueError as e:
            console.print(f"[red]Error starting workflow: {e}[/red]")
            return ""
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            return ""
    
    async def monitor_execution(self, execution_id: str, live_updates: bool = False) -> None:
        """Monitor workflow execution progress"""
        execution = self.engine.get_execution_status(execution_id)
        
        if not execution:
            console.print(f"[red]Execution '{execution_id}' not found[/red]")
            return
        
        if live_updates:
            await self._live_monitor(execution_id)
        else:
            self._static_monitor(execution)
    
    def _static_monitor(self, execution) -> None:
        """Show static execution status"""
        # Execution overview
        status_color = {
            WorkflowStatus.PENDING: "yellow",
            WorkflowStatus.RUNNING: "blue",
            WorkflowStatus.COMPLETED: "green",
            WorkflowStatus.FAILED: "red",
            WorkflowStatus.CANCELLED: "orange"
        }.get(execution.status, "white")
        
        overview = Panel(
            f"[bold]{execution.template.name if execution.template else 'Unknown'}[/bold]\n\n"
            f"[cyan]Execution ID:[/cyan] {execution.id}\n"
            f"[cyan]Status:[/cyan] [{status_color}]{execution.status.value}[/{status_color}]\n"
            f"[cyan]Current Phase:[/cyan] {execution.current_phase}\n"
            f"[cyan]Progress:[/cyan] {execution.completed_tasks}/{execution.total_tasks} tasks\n"
            f"[cyan]Failed Tasks:[/cyan] {execution.failed_tasks}\n"
            f"[cyan]Started:[/cyan] {execution.start_time}",
            title=f"Workflow Execution",
            expand=False
        )
        console.print(overview)
        
        # Task status table
        if execution.template:
            table = Table(title="Task Status")
            table.add_column("Task ID", style="cyan")
            table.add_column("Name", style="bright_white", max_width=25)
            table.add_column("Agent", style="yellow")
            table.add_column("Status", style="white")
            table.add_column("Duration", justify="right", style="magenta")
            
            for task in execution.template.tasks:
                status_color = {
                    TaskStatus.PENDING: "yellow",
                    TaskStatus.RUNNING: "blue",
                    TaskStatus.COMPLETED: "green",
                    TaskStatus.FAILED: "red",
                    TaskStatus.SKIPPED: "orange",
                    TaskStatus.CANCELLED: "orange"
                }.get(task.status, "white")
                
                duration = ""
                if task.start_time and task.end_time:
                    duration = f"{(task.end_time - task.start_time).total_seconds():.1f}s"
                elif task.start_time:
                    duration = f"{(datetime.now(timezone.utc) - task.start_time).total_seconds():.1f}s"
                
                table.add_row(
                    task.id,
                    task.name[:25] + "..." if len(task.name) > 25 else task.name,
                    task.agent,
                    f"[{status_color}]{task.status.value}[/{status_color}]",
                    duration
                )
            
            console.print(table)
    
    async def _live_monitor(self, execution_id: str) -> None:
        """Live monitoring with real-time updates"""
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                execution = self.engine.get_execution_status(execution_id)
                
                if not execution:
                    live.update(Panel("[red]Execution not found[/red]"))
                    break
                
                # Create layout
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="progress", size=5),
                    Layout(name="tasks")
                )
                
                # Header
                status_color = {
                    WorkflowStatus.PENDING: "yellow",
                    WorkflowStatus.RUNNING: "blue", 
                    WorkflowStatus.COMPLETED: "green",
                    WorkflowStatus.FAILED: "red",
                    WorkflowStatus.CANCELLED: "orange"
                }.get(execution.status, "white")
                
                header_text = Text()
                header_text.append(f"Workflow: {execution.template.name if execution.template else 'Unknown'}\n", style="bold")
                header_text.append(f"Status: ", style="cyan")
                header_text.append(f"{execution.status.value}", style=status_color)
                header_text.append(f" | Phase: {execution.current_phase}", style="cyan")
                
                layout["header"].update(Panel(header_text, expand=False))
                
                # Progress
                progress_text = Text()
                progress_pct = (execution.completed_tasks / execution.total_tasks * 100) if execution.total_tasks > 0 else 0
                progress_text.append(f"Progress: {execution.completed_tasks}/{execution.total_tasks} ({progress_pct:.1f}%)\n", style="green")
                progress_text.append(f"Failed: {execution.failed_tasks}", style="red")
                
                layout["progress"].update(Panel(progress_text, expand=False))
                
                # Tasks table
                if execution.template:
                    table = Table(show_header=True, header_style="bold magenta", expand=True)
                    table.add_column("Task", style="cyan", width=20)
                    table.add_column("Agent", style="yellow", width=15)
                    table.add_column("Status", width=12)
                    table.add_column("Duration", justify="right", width=10)
                    
                    for task in execution.template.tasks:
                        status_color = {
                            TaskStatus.PENDING: "yellow",
                            TaskStatus.RUNNING: "blue",
                            TaskStatus.COMPLETED: "green", 
                            TaskStatus.FAILED: "red",
                            TaskStatus.SKIPPED: "orange",
                            TaskStatus.CANCELLED: "orange"
                        }.get(task.status, "white")
                        
                        duration = ""
                        if task.start_time and task.end_time:
                            duration = f"{(task.end_time - task.start_time).total_seconds():.1f}s"
                        elif task.start_time:
                            duration = f"{(datetime.now(timezone.utc) - task.start_time).total_seconds():.1f}s"
                        
                        status_text = Text(task.status.value, style=status_color)
                        
                        table.add_row(
                            task.name[:18] + "..." if len(task.name) > 18 else task.name,
                            task.agent,
                            status_text,
                            duration
                        )
                    
                    layout["tasks"].update(table)
                
                live.update(layout)
                
                # Check if execution is complete
                if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                    console.print(f"\n[bold]Workflow execution {execution.status.value}[/bold]")
                    break
                
                await asyncio.sleep(1)
    
    def list_executions(self) -> None:
        """List active workflow executions"""
        executions = self.engine.get_active_executions()
        
        if not executions:
            console.print("[yellow]No active workflow executions[/yellow]")
            return
        
        table = Table(title="Active Workflow Executions")
        table.add_column("Execution ID", style="cyan", no_wrap=True)
        table.add_column("Template", style="bright_white")
        table.add_column("Status", style="white")
        table.add_column("Progress", style="green", justify="center")
        table.add_column("Started", style="blue")
        table.add_column("Duration", style="magenta", justify="right")
        
        for execution in executions:
            status_color = {
                WorkflowStatus.PENDING: "yellow",
                WorkflowStatus.RUNNING: "blue",
                WorkflowStatus.COMPLETED: "green",
                WorkflowStatus.FAILED: "red",
                WorkflowStatus.CANCELLED: "orange"
            }.get(execution.status, "white")
            
            progress = f"{execution.completed_tasks}/{execution.total_tasks}"
            
            duration = ""
            if execution.start_time:
                end_time = execution.end_time or datetime.now(timezone.utc)
                duration = str(end_time - execution.start_time).split('.')[0]  # Remove microseconds
            
            table.add_row(
                execution.id[:8] + "...",  # Truncate ID
                execution.template.name if execution.template else "Unknown",
                f"[{status_color}]{execution.status.value}[/{status_color}]",
                progress,
                execution.start_time.strftime("%H:%M:%S") if execution.start_time else "Unknown",
                duration
            )
        
        console.print(table)
    
    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running workflow execution"""
        success = await self.engine.cancel_workflow(execution_id)
        
        if success:
            console.print(f"[green]Workflow execution {execution_id} cancelled[/green]")
        else:
            console.print(f"[red]Failed to cancel execution {execution_id}[/red]")
    
    def validate_template(self, template_file: str) -> None:
        """Validate a workflow template file"""
        try:
            template_path = Path(template_file)
            
            if not template_path.exists():
                console.print(f"[red]Template file not found: {template_file}[/red]")
                return
            
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)
            
            template = self.engine._deserialize_template(template_data)
            validation_errors = template.validate()
            
            if validation_errors:
                console.print(f"[red]Template validation failed:[/red]")
                for error in validation_errors:
                    console.print(f"  • {error}")
            else:
                console.print(f"[green]Template validation successful[/green]")
                console.print(f"  • Template: {template.name}")
                console.print(f"  • Tasks: {len(template.tasks)}")
                console.print(f"  • Version: {template.version}")
                
                # Show agent recommendations
                agents_used = set(task.agent for task in template.tasks)
                console.print(f"  • Agents: {', '.join(agents_used)}")
                
        except Exception as e:
            console.print(f"[red]Error validating template: {e}[/red]")
    
    def create_template_scaffold(self, template_name: str, output_file: str) -> None:
        """Create a scaffold for a new workflow template"""
        template_data = {
            "id": template_name.lower().replace(" ", "-"),
            "name": template_name,
            "description": "TODO: Add description",
            "version": "1.0",
            "author": "TODO: Add author",
            "metadata": {
                "category": "TODO: Add category",
                "complexity": "medium",
                "estimated_duration": 1800,
                "suitable_for": ["TODO: Add suitable applications"]
            },
            "global_parameters": {},
            "hooks": {
                "pre_workflow": [],
                "post_workflow": []
            },
            "tasks": [
                {
                    "id": "example_task",
                    "name": "Example Task",
                    "agent": "code-architect",
                    "description": "TODO: Add task description",
                    "parameters": {},
                    "dependencies": [],
                    "execution_mode": "sequential",
                    "timeout": 600,
                    "max_retries": 2
                }
            ]
        }
        
        try:
            with open(output_file, 'w') as f:
                yaml.dump(template_data, f, default_flow_style=False, indent=2)
            
            console.print(f"[green]Template scaffold created: {output_file}[/green]")
            console.print("[cyan]Next steps:[/cyan]")
            console.print("  1. Edit the template file to customize tasks and parameters")
            console.print("  2. Validate the template with: workflow validate <file>")
            console.print("  3. Test the workflow with: workflow start <template-id>")
            
        except Exception as e:
            console.print(f"[red]Error creating template scaffold: {e}[/red]")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Claude Code Workflow Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  workflow list                           # List available templates
  workflow show new-feature-pipeline      # Show template details
  workflow start production-readiness     # Start workflow
  workflow monitor <execution-id>         # Monitor execution
  workflow executions                     # List active executions
  workflow cancel <execution-id>          # Cancel execution
  workflow validate template.yaml         # Validate template
  workflow scaffold "My Workflow" my.yaml # Create template scaffold
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List templates command
    list_parser = subparsers.add_parser("list", help="List available workflow templates")
    list_parser.add_argument("--format", choices=["table", "json", "yaml"], default="table",
                           help="Output format")
    
    # Show template command
    show_parser = subparsers.add_parser("show", help="Show template details")
    show_parser.add_argument("template_id", help="Template ID to show")
    
    # Start workflow command
    start_parser = subparsers.add_parser("start", help="Start workflow execution")
    start_parser.add_argument("template_id", help="Template ID to execute")
    start_parser.add_argument("--parameters", type=str, help="JSON parameters for workflow")
    start_parser.add_argument("--context", type=str, help="JSON context for workflow")
    start_parser.add_argument("--no-monitor", action="store_true", help="Don't monitor execution")
    
    # Monitor execution command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor workflow execution")
    monitor_parser.add_argument("execution_id", help="Execution ID to monitor")
    monitor_parser.add_argument("--live", action="store_true", help="Live updates")
    
    # List executions command
    subparsers.add_parser("executions", help="List active workflow executions")
    
    # Cancel execution command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel workflow execution")
    cancel_parser.add_argument("execution_id", help="Execution ID to cancel")
    
    # Validate template command
    validate_parser = subparsers.add_parser("validate", help="Validate workflow template")
    validate_parser.add_argument("template_file", help="Template file to validate")
    
    # Create template scaffold command
    scaffold_parser = subparsers.add_parser("scaffold", help="Create template scaffold")
    scaffold_parser.add_argument("template_name", help="Name for the new template")
    scaffold_parser.add_argument("output_file", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = WorkflowCLI()
    
    async def run_command():
        try:
            await cli.initialize()
            
            if args.command == "list":
                cli.list_templates(args.format)
            
            elif args.command == "show":
                cli.show_template(args.template_id)
            
            elif args.command == "start":
                parameters = json.loads(args.parameters) if args.parameters else None
                context = json.loads(args.context) if args.context else None
                await cli.start_workflow(args.template_id, parameters, context, 
                                       monitor=not args.no_monitor)
            
            elif args.command == "monitor":
                await cli.monitor_execution(args.execution_id, live_updates=args.live)
            
            elif args.command == "executions":
                cli.list_executions()
            
            elif args.command == "cancel":
                await cli.cancel_execution(args.execution_id)
            
            elif args.command == "validate":
                cli.validate_template(args.template_file)
            
            elif args.command == "scaffold":
                cli.create_template_scaffold(args.template_name, args.output_file)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        finally:
            await cli.shutdown()
    
    # Run the async command
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()