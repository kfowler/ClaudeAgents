"""
Workflow Engine for Multi-Agent Orchestration

This module provides a comprehensive workflow automation system that orchestrates
multiple agents for common development scenarios with dependency management,
parallel execution, progress tracking, and error handling.
"""

import asyncio
import json
import uuid
import yaml
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from contextlib import asynccontextmanager
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskStatus(Enum):
    """Individual task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class ExecutionMode(Enum):
    """Task execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    status: TaskStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    artifacts: List[str] = field(default_factory=list)  # Files created/modified

@dataclass
class WorkflowTask:
    """Individual task in a workflow"""
    id: str
    name: str
    agent: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    timeout: Optional[int] = None  # seconds
    retry_count: int = 0
    max_retries: int = 3
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditional execution
    hooks: Dict[str, List[str]] = field(default_factory=dict)  # pre/post hooks
    
    # Runtime state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[TaskResult] = None

@dataclass
class WorkflowTemplate:
    """Workflow definition template"""
    id: str
    name: str
    description: str
    version: str = "1.0"
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tasks: List[WorkflowTask] = field(default_factory=list)
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    hooks: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate workflow template for consistency"""
        errors = []
        
        # Check for unique task IDs
        task_ids = [task.id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Duplicate task IDs found")
        
        # Check dependency references
        for task in self.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(f"Task {task.id} references unknown dependency: {dep_id}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies():
            errors.append("Circular dependencies detected")
        
        return errors
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies using DFS"""
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            # Find task by ID
            task = next((t for t in self.tasks if t.id == node), None)
            if not task:
                return False
            
            for dep in task.dependencies:
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for task in self.tasks:
            if task.id not in visited:
                if has_cycle(task.id, visited, set()):
                    return True
        return False

@dataclass
class WorkflowExecution:
    """Runtime workflow execution instance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    template: Optional[WorkflowTemplate] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_phase: str = ""
    
    # Execution state
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    global_context: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    
    # Progress tracking
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    
    # Runtime configuration
    max_parallel_tasks: int = 5
    continue_on_error: bool = False

class AgentInterface:
    """Interface for agent execution"""
    
    async def execute_agent(self, 
                           agent_name: str, 
                           parameters: Dict[str, Any],
                           context: Dict[str, Any] = None) -> TaskResult:
        """Execute an agent with given parameters"""
        # This would integrate with the existing agent system
        # For now, return a mock result
        await asyncio.sleep(1)  # Simulate work
        
        return TaskResult(
            task_id=parameters.get('task_id', 'unknown'),
            status=TaskStatus.COMPLETED,
            output=f"Agent {agent_name} executed successfully",
            metadata={'agent': agent_name, 'parameters': parameters}
        )

class WorkflowEngine:
    """Main workflow execution engine"""
    
    def __init__(self, 
                 template_directory: str = "./workflow_templates",
                 execution_directory: str = "./workflow_executions",
                 agent_interface: Optional[AgentInterface] = None):
        self.template_directory = Path(template_directory)
        self.execution_directory = Path(execution_directory)
        self.agent_interface = agent_interface or AgentInterface()
        
        # Runtime state
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.hooks: Dict[str, Callable] = {}
        
        # Background tasks
        self._cleanup_task = None
        self._running = False
        
        # Ensure directories exist
        self.template_directory.mkdir(parents=True, exist_ok=True)
        self.execution_directory.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        self.load_templates()
    
    def load_templates(self):
        """Load workflow templates from directory"""
        self.templates.clear()
        
        for template_file in self.template_directory.glob("*.yaml"):
            try:
                with open(template_file, 'r') as f:
                    template_data = yaml.safe_load(f)
                
                template = self._deserialize_template(template_data)
                validation_errors = template.validate()
                
                if validation_errors:
                    logger.error(f"Template {template_file} validation failed: {validation_errors}")
                    continue
                
                self.templates[template.id] = template
                logger.info(f"Loaded workflow template: {template.name}")
                
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
    
    def _deserialize_template(self, data: Dict[str, Any]) -> WorkflowTemplate:
        """Convert dictionary to WorkflowTemplate object"""
        tasks = []
        for task_data in data.get('tasks', []):
            task = WorkflowTask(
                id=task_data['id'],
                name=task_data['name'],
                agent=task_data['agent'],
                description=task_data.get('description', ''),
                parameters=task_data.get('parameters', {}),
                dependencies=task_data.get('dependencies', []),
                execution_mode=ExecutionMode(task_data.get('execution_mode', 'sequential')),
                timeout=task_data.get('timeout'),
                max_retries=task_data.get('max_retries', 3),
                conditions=task_data.get('conditions', {}),
                hooks=task_data.get('hooks', {})
            )
            tasks.append(task)
        
        return WorkflowTemplate(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0'),
            author=data.get('author', ''),
            tasks=tasks,
            global_parameters=data.get('global_parameters', {}),
            hooks=data.get('hooks', {}),
            metadata=data.get('metadata', {})
        )
    
    def get_templates(self) -> List[WorkflowTemplate]:
        """Get all available workflow templates"""
        return list(self.templates.values())
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get specific workflow template"""
        return self.templates.get(template_id)
    
    async def start_workflow(self, 
                           template_id: str, 
                           parameters: Dict[str, Any] = None,
                           context: Dict[str, Any] = None) -> WorkflowExecution:
        """Start a workflow execution"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        execution = WorkflowExecution(
            template_id=template_id,
            template=template,
            total_tasks=len(template.tasks),
            global_context=context or {},
            max_parallel_tasks=parameters.get('max_parallel_tasks', 5) if parameters else 5,
            continue_on_error=parameters.get('continue_on_error', False) if parameters else False
        )
        
        # Merge global parameters
        if parameters:
            execution.global_context.update(parameters)
        execution.global_context.update(template.global_parameters)
        
        self.active_executions[execution.id] = execution
        
        # Start execution in background
        asyncio.create_task(self._execute_workflow(execution))
        
        return execution
    
    async def _execute_workflow(self, execution: WorkflowExecution):
        """Execute a workflow"""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now(timezone.utc)
            
            logger.info(f"Starting workflow execution: {execution.id}")
            
            # Execute pre-workflow hooks
            await self._execute_hooks(execution.template.hooks.get('pre_workflow', []), execution)
            
            # Build execution plan
            execution_plan = self._build_execution_plan(execution.template)
            
            # Execute tasks in phases
            for phase_tasks in execution_plan:
                execution.current_phase = f"Phase with {len(phase_tasks)} tasks"
                await self._execute_phase(execution, phase_tasks)
                
                if execution.status == WorkflowStatus.FAILED and not execution.continue_on_error:
                    break
                    
                if execution.status == WorkflowStatus.CANCELLED:
                    break
            
            # Execute post-workflow hooks
            await self._execute_hooks(execution.template.hooks.get('post_workflow', []), execution)
            
            # Determine final status
            if execution.status == WorkflowStatus.RUNNING:
                if execution.failed_tasks > 0 and not execution.continue_on_error:
                    execution.status = WorkflowStatus.FAILED
                else:
                    execution.status = WorkflowStatus.COMPLETED
            
            execution.end_time = datetime.now(timezone.utc)
            
            logger.info(f"Workflow execution completed: {execution.id} - {execution.status}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now(timezone.utc)
            execution.error_log.append(f"Workflow execution failed: {str(e)}")
            logger.error(f"Workflow execution failed: {e}\n{traceback.format_exc()}")
        
        finally:
            # Save execution results
            await self._save_execution_results(execution)
    
    def _build_execution_plan(self, template: WorkflowTemplate) -> List[List[WorkflowTask]]:
        """Build execution plan with dependency resolution"""
        # Topological sort for dependency resolution
        in_degree = {task.id: 0 for task in template.tasks}
        task_map = {task.id: task for task in template.tasks}
        
        # Calculate in-degrees
        for task in template.tasks:
            for dep_id in task.dependencies:
                if dep_id in in_degree:
                    in_degree[task.id] += 1
        
        # Build execution phases
        phases = []
        remaining_tasks = set(task.id for task in template.tasks)
        
        while remaining_tasks:
            # Find tasks with no dependencies (in-degree = 0)
            ready_tasks = [
                task_map[task_id] for task_id in remaining_tasks 
                if in_degree[task_id] == 0
            ]
            
            if not ready_tasks:
                # This shouldn't happen if validation passed
                logger.error("Circular dependency detected during execution")
                break
            
            phases.append(ready_tasks)
            
            # Remove completed tasks and update in-degrees
            for task in ready_tasks:
                remaining_tasks.remove(task.id)
                # Update dependencies for other tasks
                for remaining_task_id in remaining_tasks:
                    remaining_task = task_map[remaining_task_id]
                    if task.id in remaining_task.dependencies:
                        in_degree[remaining_task_id] -= 1
        
        return phases
    
    async def _execute_phase(self, execution: WorkflowExecution, tasks: List[WorkflowTask]):
        """Execute a phase of tasks (potentially in parallel)"""
        # Separate parallel and sequential tasks
        parallel_tasks = [task for task in tasks if task.execution_mode == ExecutionMode.PARALLEL]
        sequential_tasks = [task for task in tasks if task.execution_mode == ExecutionMode.SEQUENTIAL]
        
        # Execute parallel tasks
        if parallel_tasks:
            await self._execute_parallel_tasks(execution, parallel_tasks)
        
        # Execute sequential tasks
        for task in sequential_tasks:
            await self._execute_single_task(execution, task)
            if execution.status in [WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                break
    
    async def _execute_parallel_tasks(self, execution: WorkflowExecution, tasks: List[WorkflowTask]):
        """Execute multiple tasks in parallel"""
        semaphore = asyncio.Semaphore(execution.max_parallel_tasks)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self._execute_single_task(execution, task)
        
        # Start all parallel tasks
        task_coroutines = [execute_with_semaphore(task) for task in tasks]
        
        # Wait for completion
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parallel task failed: {result}")
    
    async def _execute_single_task(self, execution: WorkflowExecution, task: WorkflowTask):
        """Execute a single workflow task"""
        try:
            # Check if task should be skipped due to conditions
            if not self._evaluate_conditions(task, execution):
                task.status = TaskStatus.SKIPPED
                logger.info(f"Task {task.id} skipped due to conditions")
                return
            
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now(timezone.utc)
            
            logger.info(f"Executing task: {task.name} ({task.id})")
            
            # Execute pre-task hooks
            await self._execute_hooks(task.hooks.get('pre_task', []), execution, task)
            
            # Prepare task parameters
            task_parameters = {**execution.global_context, **task.parameters}
            task_parameters['task_id'] = task.id
            
            # Execute with retries
            result = await self._execute_with_retries(task, task_parameters, execution.global_context)
            
            # Store result
            task.result = result
            execution.task_results[task.id] = result
            
            # Update task status
            task.status = result.status
            task.end_time = datetime.now(timezone.utc)
            
            # Update execution counters
            if result.status == TaskStatus.COMPLETED:
                execution.completed_tasks += 1
            elif result.status == TaskStatus.FAILED:
                execution.failed_tasks += 1
                if not execution.continue_on_error:
                    execution.status = WorkflowStatus.FAILED
            
            # Execute post-task hooks
            await self._execute_hooks(task.hooks.get('post_task', []), execution, task)
            
            logger.info(f"Task completed: {task.name} - {result.status}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.end_time = datetime.now(timezone.utc)
            execution.failed_tasks += 1
            execution.error_log.append(f"Task {task.id} failed: {str(e)}")
            logger.error(f"Task {task.id} failed: {e}")
            
            if not execution.continue_on_error:
                execution.status = WorkflowStatus.FAILED
    
    def _evaluate_conditions(self, task: WorkflowTask, execution: WorkflowExecution) -> bool:
        """Evaluate task execution conditions"""
        if not task.conditions:
            return True
        
        # Simple condition evaluation
        for condition_type, condition_value in task.conditions.items():
            if condition_type == "previous_task_status":
                prev_task_id = condition_value.get("task_id")
                expected_status = condition_value.get("status")
                
                if prev_task_id in execution.task_results:
                    actual_status = execution.task_results[prev_task_id].status
                    if actual_status.value != expected_status:
                        return False
                else:
                    return False
            
            elif condition_type == "global_context":
                key = condition_value.get("key")
                expected_value = condition_value.get("value")
                
                if key not in execution.global_context:
                    return False
                
                if execution.global_context[key] != expected_value:
                    return False
        
        return True
    
    async def _execute_with_retries(self, 
                                  task: WorkflowTask, 
                                  parameters: Dict[str, Any],
                                  context: Dict[str, Any]) -> TaskResult:
        """Execute task with retry logic"""
        last_error = None
        
        for attempt in range(task.max_retries + 1):
            try:
                if task.timeout:
                    result = await asyncio.wait_for(
                        self.agent_interface.execute_agent(task.agent, parameters, context),
                        timeout=task.timeout
                    )
                else:
                    result = await self.agent_interface.execute_agent(task.agent, parameters, context)
                
                # If successful, return result
                if result.status == TaskStatus.COMPLETED:
                    result.execution_time = (datetime.now(timezone.utc) - task.start_time).total_seconds()
                    return result
                
                # If failed, prepare for retry
                last_error = result.error
                if attempt < task.max_retries:
                    logger.warning(f"Task {task.id} failed (attempt {attempt + 1}), retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except asyncio.TimeoutError:
                last_error = f"Task timed out after {task.timeout} seconds"
                logger.warning(f"Task {task.id} timed out (attempt {attempt + 1})")
            
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Task {task.id} failed with exception (attempt {attempt + 1}): {e}")
        
        # All retries exhausted
        return TaskResult(
            task_id=task.id,
            status=TaskStatus.FAILED,
            error=f"Failed after {task.max_retries + 1} attempts. Last error: {last_error}",
            execution_time=(datetime.now(timezone.utc) - task.start_time).total_seconds() if task.start_time else 0
        )
    
    async def _execute_hooks(self, 
                           hook_names: List[str], 
                           execution: WorkflowExecution,
                           task: Optional[WorkflowTask] = None):
        """Execute workflow/task hooks"""
        for hook_name in hook_names:
            if hook_name in self.hooks:
                try:
                    await self.hooks[hook_name](execution, task)
                except Exception as e:
                    logger.error(f"Hook {hook_name} failed: {e}")
    
    def register_hook(self, name: str, hook_func: Callable):
        """Register a custom hook function"""
        self.hooks[name] = hook_func
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            logger.info(f"Workflow {execution_id} cancelled")
            return True
        return False
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a running workflow (to be implemented)"""
        # This would require more complex state management
        logger.warning("Workflow pausing not yet implemented")
        return False
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status of a workflow execution"""
        return self.active_executions.get(execution_id)
    
    def get_active_executions(self) -> List[WorkflowExecution]:
        """Get all active workflow executions"""
        return list(self.active_executions.values())
    
    async def _save_execution_results(self, execution: WorkflowExecution):
        """Save workflow execution results to disk"""
        try:
            execution_data = asdict(execution)
            # Convert datetime objects to strings
            execution_data = json.loads(json.dumps(execution_data, default=str))
            
            filename = f"execution_{execution.id}_{execution.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.execution_directory / filename
            
            with open(filepath, 'w') as f:
                json.dump(execution_data, f, indent=2)
            
            logger.info(f"Execution results saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save execution results: {e}")
    
    async def start(self):
        """Start the workflow engine"""
        self._running = True
        logger.info("Workflow engine started")
    
    async def shutdown(self):
        """Shutdown the workflow engine"""
        self._running = False
        
        # Cancel all active executions
        for execution_id in list(self.active_executions.keys()):
            await self.cancel_workflow(execution_id)
        
        logger.info("Workflow engine shutdown")

# Singleton instance
workflow_engine = WorkflowEngine()