"""
Workflow Hooks System

Provides extensible hooks for workflow customization, allowing users to inject
custom logic at various points in the workflow execution lifecycle.
"""

import asyncio
import inspect
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum

from engine import WorkflowExecution, WorkflowTask, TaskResult, TaskStatus

logger = logging.getLogger(__name__)

class HookType(Enum):
    """Types of hooks available in the workflow system"""
    PRE_WORKFLOW = "pre_workflow"
    POST_WORKFLOW = "post_workflow"
    PRE_TASK = "pre_task"
    POST_TASK = "post_task"
    ON_ERROR = "on_error"
    ON_SUCCESS = "on_success"
    ON_RETRY = "on_retry"
    ON_CANCEL = "on_cancel"

class HookExecutionMode(Enum):
    """Execution modes for hooks"""
    BLOCKING = "blocking"  # Wait for hook completion
    NON_BLOCKING = "non_blocking"  # Fire and forget
    CONDITIONAL = "conditional"  # Execute based on condition

@dataclass
class HookConfiguration:
    """Configuration for a hook"""
    name: str
    hook_type: HookType
    execution_mode: HookExecutionMode = HookExecutionMode.BLOCKING
    timeout_seconds: Optional[int] = 30
    retry_count: int = 0
    condition: Optional[str] = None  # Python expression
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class HookContext:
    """Context passed to hook functions"""
    execution: WorkflowExecution
    task: Optional[WorkflowTask] = None
    task_result: Optional[TaskResult] = None
    error: Optional[Exception] = None
    hook_config: Optional[HookConfiguration] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class HookManager:
    """Manages workflow hooks and their execution"""
    
    def __init__(self, hooks_directory: str = "./workflow_hooks"):
        self.hooks_directory = Path(hooks_directory)
        self.hooks_directory.mkdir(parents=True, exist_ok=True)
        
        # Registered hooks
        self.function_hooks: Dict[str, Callable] = {}
        self.script_hooks: Dict[str, str] = {}
        self.builtin_hooks: Dict[str, Callable] = {}
        
        # Hook configurations
        self.hook_configs: Dict[str, HookConfiguration] = {}
        
        # Initialize built-in hooks
        self._register_builtin_hooks()
        
        # Load hooks from directory
        self._load_hooks_from_directory()
    
    def _register_builtin_hooks(self):
        """Register built-in hooks"""
        
        async def validate_prerequisites(context: HookContext):
            """Validate workflow prerequisites"""
            logger.info(f"Validating prerequisites for workflow {context.execution.id}")
            
            # Check if required parameters are present
            required_params = context.hook_config.parameters.get('required_parameters', [])
            missing_params = []
            
            for param in required_params:
                if param not in context.execution.global_context:
                    missing_params.append(param)
            
            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")
            
            logger.info("Prerequisites validation passed")
        
        async def setup_feature_branch(context: HookContext):
            """Setup a feature branch for the workflow"""
            branch_name = context.execution.global_context.get('branch_name')
            if not branch_name:
                # Generate branch name from workflow
                template_name = context.execution.template.name if context.execution.template else "workflow"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                branch_name = f"workflow/{template_name.lower().replace(' ', '-')}_{timestamp}"
            
            try:
                # Check if we're in a git repository
                subprocess.run(['git', 'status'], check=True, capture_output=True)
                
                # Create and checkout new branch
                subprocess.run(['git', 'checkout', '-b', branch_name], check=True, capture_output=True)
                logger.info(f"Created and checked out branch: {branch_name}")
                
                # Store branch name in context for later use
                context.execution.global_context['workflow_branch'] = branch_name
                
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to create feature branch: {e}")
        
        async def cleanup_temporary_files(context: HookContext):
            """Cleanup temporary files created during workflow"""
            temp_files = context.execution.global_context.get('temp_files', [])
            
            cleaned_count = 0
            for temp_file in temp_files:
                try:
                    temp_path = Path(temp_file)
                    if temp_path.exists():
                        if temp_path.is_file():
                            temp_path.unlink()
                        elif temp_path.is_dir():
                            import shutil
                            shutil.rmtree(temp_path)
                        cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_file}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} temporary files")
        
        async def send_completion_notification(context: HookContext):
            """Send notification when workflow completes"""
            webhook_url = context.execution.global_context.get('webhook_url')
            email = context.execution.global_context.get('notification_email')
            
            message = {
                'workflow_id': context.execution.id,
                'template_name': context.execution.template.name if context.execution.template else 'Unknown',
                'status': context.execution.status.value,
                'completed_tasks': context.execution.completed_tasks,
                'total_tasks': context.execution.total_tasks,
                'duration_seconds': (context.timestamp - context.execution.start_time).total_seconds() if context.execution.start_time else 0
            }
            
            # Send webhook notification
            if webhook_url:
                try:
                    import requests
                    response = requests.post(webhook_url, json=message, timeout=10)
                    response.raise_for_status()
                    logger.info("Webhook notification sent successfully")
                except Exception as e:
                    logger.warning(f"Failed to send webhook notification: {e}")
            
            # Send email notification (placeholder - would need email configuration)
            if email:
                logger.info(f"Email notification would be sent to: {email}")
        
        async def backup_current_state(context: HookContext):
            """Backup current state before workflow execution"""
            backup_enabled = context.execution.global_context.get('backup_enabled', False)
            if not backup_enabled:
                return
            
            try:
                # Create backup using git stash
                result = subprocess.run(['git', 'stash', 'push', '-m', f'Workflow backup {context.execution.id}'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    context.execution.global_context['backup_stash'] = result.stdout.strip()
                    logger.info("Created backup stash")
                else:
                    logger.warning(f"Failed to create backup: {result.stderr}")
            
            except Exception as e:
                logger.warning(f"Backup creation failed: {e}")
        
        async def generate_readiness_report(context: HookContext):
            """Generate production readiness report"""
            report_data = {
                'workflow_id': context.execution.id,
                'template_name': context.execution.template.name if context.execution.template else 'Unknown',
                'execution_summary': {
                    'status': context.execution.status.value,
                    'total_tasks': context.execution.total_tasks,
                    'completed_tasks': context.execution.completed_tasks,
                    'failed_tasks': context.execution.failed_tasks,
                    'start_time': context.execution.start_time.isoformat() if context.execution.start_time else None,
                    'end_time': context.timestamp.isoformat()
                },
                'task_details': []
            }
            
            # Add task details
            if context.execution.template:
                for task in context.execution.template.tasks:
                    task_detail = {
                        'id': task.id,
                        'name': task.name,
                        'agent': task.agent,
                        'status': task.status.value,
                        'duration_seconds': None
                    }
                    
                    if task.start_time and task.end_time:
                        task_detail['duration_seconds'] = (task.end_time - task.start_time).total_seconds()
                    
                    if task.result:
                        task_detail['output_summary'] = str(task.result.output)[:200] if task.result.output else None
                        task_detail['error'] = task.result.error
                        task_detail['artifacts'] = task.result.artifacts
                    
                    report_data['task_details'].append(task_detail)
            
            # Save report
            report_file = Path(f"readiness_report_{context.execution.id}.json")
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Generated readiness report: {report_file}")
            context.execution.global_context['readiness_report'] = str(report_file)
        
        # Register built-in hooks
        self.builtin_hooks.update({
            'validate_prerequisites': validate_prerequisites,
            'setup_feature_branch': setup_feature_branch,
            'cleanup_temporary_files': cleanup_temporary_files,
            'send_completion_notification': send_completion_notification,
            'backup_current_state': backup_current_state,
            'generate_readiness_report': generate_readiness_report
        })
    
    def _load_hooks_from_directory(self):
        """Load hooks from the hooks directory"""
        
        # Load Python hook files
        for hook_file in self.hooks_directory.glob("*.py"):
            try:
                self._load_python_hook(hook_file)
            except Exception as e:
                logger.error(f"Failed to load Python hook {hook_file}: {e}")
        
        # Load shell script hooks
        for hook_file in self.hooks_directory.glob("*.sh"):
            try:
                self._load_script_hook(hook_file)
            except Exception as e:
                logger.error(f"Failed to load script hook {hook_file}: {e}")
        
        # Load hook configurations
        for config_file in self.hooks_directory.glob("*.json"):
            try:
                self._load_hook_config(config_file)
            except Exception as e:
                logger.error(f"Failed to load hook config {config_file}: {e}")
    
    def _load_python_hook(self, hook_file: Path):
        """Load a Python hook file"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(hook_file.stem, hook_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for hook functions (functions that take HookContext as parameter)
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith('_'):
                # Check if it's a valid hook function
                sig = inspect.signature(obj)
                if len(sig.parameters) == 1:
                    param = next(iter(sig.parameters.values()))
                    if param.annotation == HookContext or 'context' in param.name.lower():
                        self.function_hooks[name] = obj
                        logger.info(f"Loaded Python hook: {name}")
    
    def _load_script_hook(self, hook_file: Path):
        """Load a shell script hook"""
        if hook_file.is_file() and hook_file.stat().st_mode & 0o111:  # Executable
            self.script_hooks[hook_file.stem] = str(hook_file)
            logger.info(f"Loaded script hook: {hook_file.stem}")
    
    def _load_hook_config(self, config_file: Path):
        """Load hook configuration from JSON file"""
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        for hook_name, hook_config in config_data.items():
            config = HookConfiguration(
                name=hook_name,
                hook_type=HookType(hook_config['hook_type']),
                execution_mode=HookExecutionMode(hook_config.get('execution_mode', 'blocking')),
                timeout_seconds=hook_config.get('timeout_seconds', 30),
                retry_count=hook_config.get('retry_count', 0),
                condition=hook_config.get('condition'),
                parameters=hook_config.get('parameters', {})
            )
            
            self.hook_configs[hook_name] = config
            logger.info(f"Loaded hook configuration: {hook_name}")
    
    def register_hook(self, name: str, hook_func: Callable, config: Optional[HookConfiguration] = None):
        """Register a new hook function"""
        self.function_hooks[name] = hook_func
        
        if config:
            self.hook_configs[name] = config
        
        logger.info(f"Registered hook: {name}")
    
    def register_script_hook(self, name: str, script_path: str, config: Optional[HookConfiguration] = None):
        """Register a new script hook"""
        self.script_hooks[name] = script_path
        
        if config:
            self.hook_configs[name] = config
        
        logger.info(f"Registered script hook: {name}")
    
    async def execute_hooks(self, 
                          hook_names: List[str], 
                          hook_type: HookType,
                          context: HookContext) -> Dict[str, Any]:
        """Execute a list of hooks"""
        results = {}
        
        for hook_name in hook_names:
            try:
                result = await self.execute_hook(hook_name, hook_type, context)
                results[hook_name] = {'status': 'success', 'result': result}
            except Exception as e:
                results[hook_name] = {'status': 'error', 'error': str(e)}
                logger.error(f"Hook {hook_name} failed: {e}")
                
                # Check if this is a critical hook that should stop execution
                config = self.hook_configs.get(hook_name)
                if config and config.execution_mode == HookExecutionMode.BLOCKING:
                    raise
        
        return results
    
    async def execute_hook(self, 
                         hook_name: str, 
                         hook_type: HookType, 
                         context: HookContext) -> Any:
        """Execute a single hook"""
        
        # Get hook configuration
        config = self.hook_configs.get(hook_name)
        if config:
            context.hook_config = config
            
            # Check execution condition
            if config.condition and not self._evaluate_condition(config.condition, context):
                logger.info(f"Skipping hook {hook_name} due to condition: {config.condition}")
                return None
        
        # Execute the hook with timeout and retries
        retry_count = config.retry_count if config else 0
        timeout = config.timeout_seconds if config else 30
        
        for attempt in range(retry_count + 1):
            try:
                if hook_name in self.builtin_hooks:
                    result = await self._execute_function_hook(self.builtin_hooks[hook_name], context, timeout)
                elif hook_name in self.function_hooks:
                    result = await self._execute_function_hook(self.function_hooks[hook_name], context, timeout)
                elif hook_name in self.script_hooks:
                    result = await self._execute_script_hook(self.script_hooks[hook_name], context, timeout)
                else:
                    raise ValueError(f"Hook not found: {hook_name}")
                
                return result
                
            except Exception as e:
                if attempt < retry_count:
                    logger.warning(f"Hook {hook_name} failed (attempt {attempt + 1}), retrying: {e}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        return None
    
    async def _execute_function_hook(self, hook_func: Callable, context: HookContext, timeout: int) -> Any:
        """Execute a Python function hook"""
        if asyncio.iscoroutinefunction(hook_func):
            return await asyncio.wait_for(hook_func(context), timeout=timeout)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, hook_func, context)
    
    async def _execute_script_hook(self, script_path: str, context: HookContext, timeout: int) -> Any:
        """Execute a script hook"""
        
        # Prepare environment variables
        env = {
            'WORKFLOW_ID': context.execution.id,
            'WORKFLOW_TEMPLATE_ID': context.execution.template_id,
            'WORKFLOW_STATUS': context.execution.status.value,
            'WORKFLOW_START_TIME': context.execution.start_time.isoformat() if context.execution.start_time else '',
            'WORKFLOW_TOTAL_TASKS': str(context.execution.total_tasks),
            'WORKFLOW_COMPLETED_TASKS': str(context.execution.completed_tasks),
            'WORKFLOW_FAILED_TASKS': str(context.execution.failed_tasks)
        }
        
        if context.task:
            env.update({
                'TASK_ID': context.task.id,
                'TASK_NAME': context.task.name,
                'TASK_AGENT': context.task.agent,
                'TASK_STATUS': context.task.status.value
            })
        
        # Add global context as JSON
        env['WORKFLOW_CONTEXT'] = json.dumps(context.execution.global_context, default=str)
        
        # Execute script
        process = await asyncio.create_subprocess_exec(
            script_path,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Script execution failed"
                raise RuntimeError(f"Script hook failed with code {process.returncode}: {error_msg}")
            
            return stdout.decode().strip() if stdout else None
            
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Script hook timed out after {timeout} seconds")
    
    def _evaluate_condition(self, condition: str, context: HookContext) -> bool:
        """Evaluate a condition expression"""
        try:
            # Create evaluation context
            eval_context = {
                'execution': context.execution,
                'task': context.task,
                'task_result': context.task_result,
                'error': context.error,
                'status': context.execution.status,
                'completed_tasks': context.execution.completed_tasks,
                'failed_tasks': context.execution.failed_tasks,
                'total_tasks': context.execution.total_tasks,
                'global_context': context.execution.global_context
            }
            
            # Add task-specific context
            if context.task:
                eval_context.update({
                    'task_status': context.task.status,
                    'task_agent': context.task.agent,
                    'task_retry_count': context.task.retry_count
                })
            
            # Evaluate condition (restricted to safe operations)
            return eval(condition, {"__builtins__": {}}, eval_context)
            
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def list_hooks(self) -> Dict[str, List[str]]:
        """List all available hooks by type"""
        return {
            'builtin': list(self.builtin_hooks.keys()),
            'function': list(self.function_hooks.keys()),
            'script': list(self.script_hooks.keys())
        }
    
    def get_hook_info(self, hook_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific hook"""
        info = None
        
        if hook_name in self.builtin_hooks:
            func = self.builtin_hooks[hook_name]
            info = {
                'type': 'builtin',
                'function': func.__name__,
                'doc': func.__doc__
            }
        elif hook_name in self.function_hooks:
            func = self.function_hooks[hook_name]
            info = {
                'type': 'function',
                'function': func.__name__,
                'doc': func.__doc__
            }
        elif hook_name in self.script_hooks:
            info = {
                'type': 'script',
                'script_path': self.script_hooks[hook_name]
            }
        
        if info and hook_name in self.hook_configs:
            info['config'] = self.hook_configs[hook_name]
        
        return info

# Global hook manager instance
hook_manager = HookManager()