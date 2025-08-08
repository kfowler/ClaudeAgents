"""
Advanced Error Handling and Recovery for Workflow System

Provides comprehensive error handling, rollback capabilities, and recovery mechanisms
for workflow executions to ensure system reliability and data consistency.
"""

import asyncio
import json
import logging
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field

from engine import WorkflowExecution, WorkflowTask, TaskResult, TaskStatus, WorkflowStatus

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY = "retry"
    SKIP = "skip"
    ROLLBACK = "rollback"
    MANUAL_INTERVENTION = "manual_intervention"
    FAIL_FAST = "fail_fast"
    FALLBACK = "fallback"

class RollbackScope(Enum):
    """Scope of rollback operations"""
    TASK = "task"  # Rollback single task
    PHASE = "phase"  # Rollback current phase
    WORKFLOW = "workflow"  # Rollback entire workflow
    SYSTEM = "system"  # System-wide rollback

@dataclass
class ErrorContext:
    """Context information for errors"""
    workflow_id: str
    task_id: Optional[str] = None
    agent_name: Optional[str] = None
    error: Optional[Exception] = None
    error_message: str = ""
    error_code: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stack_trace: Optional[str] = None
    user_data: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3

@dataclass
class RecoveryAction:
    """Action to take for error recovery"""
    strategy: RecoveryStrategy
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    rollback_steps: List[str] = field(default_factory=list)
    fallback_task: Optional[str] = None
    
@dataclass
class CheckpointData:
    """Data stored at workflow checkpoints"""
    checkpoint_id: str
    workflow_id: str
    timestamp: datetime
    execution_state: Dict[str, Any]
    file_snapshots: Dict[str, str] = field(default_factory=dict)  # file_path -> backup_path
    git_commit_hash: Optional[str] = None
    database_backup: Optional[str] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)

class ErrorHandler:
    """Main error handling and recovery system"""
    
    def __init__(self, 
                 checkpoints_directory: str = "./workflow_checkpoints",
                 backups_directory: str = "./workflow_backups"):
        self.checkpoints_directory = Path(checkpoints_directory)
        self.backups_directory = Path(backups_directory)
        
        # Ensure directories exist
        self.checkpoints_directory.mkdir(parents=True, exist_ok=True)
        self.backups_directory.mkdir(parents=True, exist_ok=True)
        
        # Error handling rules
        self.error_rules: Dict[str, RecoveryAction] = {}
        self.global_handlers: List[Callable] = []
        
        # Checkpoints and recovery data
        self.checkpoints: Dict[str, CheckpointData] = {}
        self.recovery_history: Dict[str, List[ErrorContext]] = {}
        
        # Initialize default error handling rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default error handling rules"""
        
        # Timeout errors - retry with exponential backoff
        self.error_rules["timeout_error"] = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            description="Retry task with increased timeout",
            parameters={"retry_delay": 5, "timeout_multiplier": 2},
            timeout_seconds=600
        )
        
        # Network errors - retry with backoff
        self.error_rules["network_error"] = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            description="Retry after network error",
            parameters={"retry_delay": 10, "max_retries": 3},
            timeout_seconds=300
        )
        
        # Resource exhaustion - retry with resource cleanup
        self.error_rules["resource_error"] = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            description="Retry after resource cleanup",
            parameters={"cleanup_required": True, "retry_delay": 30},
            timeout_seconds=900
        )
        
        # Validation errors - manual intervention required
        self.error_rules["validation_error"] = RecoveryAction(
            strategy=RecoveryStrategy.MANUAL_INTERVENTION,
            description="Manual review required for validation errors",
            parameters={"notify_admin": True}
        )
        
        # Data corruption - rollback to last checkpoint
        self.error_rules["data_corruption"] = RecoveryAction(
            strategy=RecoveryStrategy.ROLLBACK,
            description="Rollback to last known good state",
            parameters={"rollback_scope": "workflow"},
            rollback_steps=["restore_files", "revert_database", "reset_git"]
        )
        
        # Critical system errors - fail fast
        self.error_rules["system_error"] = RecoveryAction(
            strategy=RecoveryStrategy.FAIL_FAST,
            description="Fail fast for critical system errors",
            parameters={"notify_admin": True, "create_incident": True}
        )
    
    def register_error_rule(self, error_pattern: str, recovery_action: RecoveryAction):
        """Register a custom error handling rule"""
        self.error_rules[error_pattern] = recovery_action
        logger.info(f"Registered error rule: {error_pattern}")
    
    def register_global_handler(self, handler: Callable[[ErrorContext], None]):
        """Register a global error handler"""
        self.global_handlers.append(handler)
    
    async def handle_error(self, error_context: ErrorContext) -> RecoveryAction:
        """Main error handling entry point"""
        
        # Log the error
        logger.error(f"Handling error in workflow {error_context.workflow_id}: {error_context.error_message}")
        
        # Record error in history
        if error_context.workflow_id not in self.recovery_history:
            self.recovery_history[error_context.workflow_id] = []
        self.recovery_history[error_context.workflow_id].append(error_context)
        
        # Execute global handlers
        for handler in self.global_handlers:
            try:
                await self._execute_handler(handler, error_context)
            except Exception as e:
                logger.error(f"Global error handler failed: {e}")
        
        # Determine recovery strategy
        recovery_action = self._determine_recovery_strategy(error_context)
        
        # Execute recovery action
        try:
            await self._execute_recovery_action(error_context, recovery_action)
            logger.info(f"Recovery action executed: {recovery_action.strategy.value}")
        except Exception as e:
            logger.error(f"Recovery action failed: {e}")
            # Fallback to manual intervention
            recovery_action = RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INTERVENTION,
                description="Automatic recovery failed, manual intervention required",
                parameters={"original_error": error_context.error_message, "recovery_error": str(e)}
            )
        
        return recovery_action
    
    def _determine_recovery_strategy(self, error_context: ErrorContext) -> RecoveryAction:
        """Determine the appropriate recovery strategy for an error"""
        
        # Check if we've exceeded max recovery attempts
        if error_context.recovery_attempts >= error_context.max_recovery_attempts:
            return RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INTERVENTION,
                description="Maximum recovery attempts exceeded"
            )
        
        # Pattern matching for error types
        error_message = error_context.error_message.lower()
        
        # Check specific error patterns
        for pattern, action in self.error_rules.items():
            if pattern.replace("_", " ") in error_message:
                return action
        
        # Check error severity
        if error_context.severity == ErrorSeverity.CRITICAL:
            return self.error_rules.get("system_error", RecoveryAction(
                strategy=RecoveryStrategy.FAIL_FAST,
                description="Critical error - failing fast"
            ))
        
        # Default strategy based on error type
        if "timeout" in error_message or "deadline" in error_message:
            return self.error_rules["timeout_error"]
        elif "network" in error_message or "connection" in error_message:
            return self.error_rules["network_error"]
        elif "memory" in error_message or "resource" in error_message:
            return self.error_rules["resource_error"]
        elif "validation" in error_message or "invalid" in error_message:
            return self.error_rules["validation_error"]
        
        # Default to retry for unknown errors
        return RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            description="Default retry for unknown error",
            parameters={"retry_delay": 10, "max_retries": 2}
        )
    
    async def _execute_recovery_action(self, error_context: ErrorContext, action: RecoveryAction):
        """Execute a recovery action"""
        
        if action.strategy == RecoveryStrategy.RETRY:
            await self._handle_retry(error_context, action)
        
        elif action.strategy == RecoveryStrategy.SKIP:
            await self._handle_skip(error_context, action)
        
        elif action.strategy == RecoveryStrategy.ROLLBACK:
            await self._handle_rollback(error_context, action)
        
        elif action.strategy == RecoveryStrategy.FALLBACK:
            await self._handle_fallback(error_context, action)
        
        elif action.strategy == RecoveryStrategy.MANUAL_INTERVENTION:
            await self._handle_manual_intervention(error_context, action)
        
        elif action.strategy == RecoveryStrategy.FAIL_FAST:
            await self._handle_fail_fast(error_context, action)
    
    async def _handle_retry(self, error_context: ErrorContext, action: RecoveryAction):
        """Handle retry recovery strategy"""
        retry_delay = action.parameters.get("retry_delay", 5)
        
        logger.info(f"Retrying task after {retry_delay} seconds")
        await asyncio.sleep(retry_delay)
        
        # Update retry count
        error_context.recovery_attempts += 1
        
        # If resource cleanup is required
        if action.parameters.get("cleanup_required", False):
            await self._cleanup_resources(error_context)
    
    async def _handle_skip(self, error_context: ErrorContext, action: RecoveryAction):
        """Handle skip recovery strategy"""
        logger.info(f"Skipping failed task: {error_context.task_id}")
        
        # Mark task as skipped
        # This would be implemented in the workflow engine
        
        # Log skip reason
        skip_reason = action.parameters.get("skip_reason", "Task skipped due to error")
        logger.info(f"Skip reason: {skip_reason}")
    
    async def _handle_rollback(self, error_context: ErrorContext, action: RecoveryAction):
        """Handle rollback recovery strategy"""
        rollback_scope = action.parameters.get("rollback_scope", "task")
        
        logger.info(f"Initiating rollback with scope: {rollback_scope}")
        
        # Find appropriate checkpoint
        checkpoint = await self._find_rollback_checkpoint(error_context, rollback_scope)
        
        if checkpoint:
            await self._execute_rollback(checkpoint, action.rollback_steps)
        else:
            logger.warning("No suitable checkpoint found for rollback")
            raise RuntimeError("Rollback failed: No checkpoint available")
    
    async def _handle_fallback(self, error_context: ErrorContext, action: RecoveryAction):
        """Handle fallback recovery strategy"""
        fallback_task = action.parameters.get("fallback_task")
        
        if fallback_task:
            logger.info(f"Executing fallback task: {fallback_task}")
            # This would trigger execution of the fallback task
        else:
            logger.warning("No fallback task specified")
    
    async def _handle_manual_intervention(self, error_context: ErrorContext, action: RecoveryAction):
        """Handle manual intervention recovery strategy"""
        logger.warning(f"Manual intervention required for workflow {error_context.workflow_id}")
        
        # Create intervention record
        intervention_data = {
            "workflow_id": error_context.workflow_id,
            "task_id": error_context.task_id,
            "error_message": error_context.error_message,
            "timestamp": error_context.timestamp.isoformat(),
            "action_required": action.description,
            "parameters": action.parameters
        }
        
        # Save intervention request
        intervention_file = self.checkpoints_directory / f"intervention_{error_context.workflow_id}_{int(error_context.timestamp.timestamp())}.json"
        with open(intervention_file, 'w') as f:
            json.dump(intervention_data, f, indent=2)
        
        # Notify administrators if configured
        if action.parameters.get("notify_admin", False):
            await self._notify_administrators(error_context, action)
    
    async def _handle_fail_fast(self, error_context: ErrorContext, action: RecoveryAction):
        """Handle fail fast recovery strategy"""
        logger.critical(f"Failing fast for critical error in workflow {error_context.workflow_id}")
        
        # Create incident record if configured
        if action.parameters.get("create_incident", False):
            await self._create_incident_record(error_context, action)
        
        # Notify administrators
        if action.parameters.get("notify_admin", False):
            await self._notify_administrators(error_context, action)
        
        # Stop execution immediately
        raise RuntimeError(f"Critical error - failing fast: {error_context.error_message}")
    
    async def create_checkpoint(self, execution: WorkflowExecution, checkpoint_name: str = None) -> str:
        """Create a checkpoint for the workflow execution"""
        
        checkpoint_id = checkpoint_name or f"checkpoint_{execution.id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Creating checkpoint: {checkpoint_id}")
        
        # Create checkpoint data
        checkpoint = CheckpointData(
            checkpoint_id=checkpoint_id,
            workflow_id=execution.id,
            timestamp=datetime.now(timezone.utc),
            execution_state={
                "status": execution.status.value,
                "current_phase": execution.current_phase,
                "completed_tasks": execution.completed_tasks,
                "failed_tasks": execution.failed_tasks,
                "global_context": execution.global_context.copy(),
                "task_results": {k: v.__dict__ for k, v in execution.task_results.items()}
            }
        )
        
        # Create file snapshots
        checkpoint.file_snapshots = await self._create_file_snapshots(execution)
        
        # Get git commit hash if in git repository
        checkpoint.git_commit_hash = await self._get_git_commit_hash()
        
        # Store checkpoint
        self.checkpoints[checkpoint_id] = checkpoint
        
        # Save checkpoint to disk
        checkpoint_file = self.checkpoints_directory / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump({
                "checkpoint_id": checkpoint.checkpoint_id,
                "workflow_id": checkpoint.workflow_id,
                "timestamp": checkpoint.timestamp.isoformat(),
                "execution_state": checkpoint.execution_state,
                "file_snapshots": checkpoint.file_snapshots,
                "git_commit_hash": checkpoint.git_commit_hash,
                "custom_data": checkpoint.custom_data
            }, f, indent=2, default=str)
        
        logger.info(f"Checkpoint created successfully: {checkpoint_id}")
        return checkpoint_id
    
    async def _create_file_snapshots(self, execution: WorkflowExecution) -> Dict[str, str]:
        """Create snapshots of important files"""
        snapshots = {}
        
        # Get files to backup from global context
        files_to_backup = execution.global_context.get("backup_files", [])
        
        # Add commonly modified files
        common_files = [
            "package.json", "requirements.txt", "Cargo.toml", "go.mod",
            "Dockerfile", "docker-compose.yml", ".env", "config.json"
        ]
        
        files_to_backup.extend(common_files)
        
        timestamp = int(datetime.now().timestamp())
        
        for file_path in files_to_backup:
            source_path = Path(file_path)
            
            if source_path.exists():
                # Create backup filename
                backup_filename = f"{source_path.name}_{execution.id}_{timestamp}"
                backup_path = self.backups_directory / backup_filename
                
                try:
                    # Copy file to backup directory
                    shutil.copy2(source_path, backup_path)
                    snapshots[file_path] = str(backup_path)
                    
                except Exception as e:
                    logger.warning(f"Failed to backup file {file_path}: {e}")
        
        return snapshots
    
    async def _get_git_commit_hash(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    async def _find_rollback_checkpoint(self, error_context: ErrorContext, scope: str) -> Optional[CheckpointData]:
        """Find the most appropriate checkpoint for rollback"""
        
        # Get checkpoints for this workflow
        workflow_checkpoints = [
            cp for cp in self.checkpoints.values() 
            if cp.workflow_id == error_context.workflow_id
        ]
        
        if not workflow_checkpoints:
            return None
        
        # Sort by timestamp (newest first)
        workflow_checkpoints.sort(key=lambda cp: cp.timestamp, reverse=True)
        
        # For now, return the most recent checkpoint
        # In a more sophisticated implementation, we might choose based on scope
        return workflow_checkpoints[0]
    
    async def _execute_rollback(self, checkpoint: CheckpointData, rollback_steps: List[str]):
        """Execute rollback to a checkpoint"""
        
        logger.info(f"Executing rollback to checkpoint: {checkpoint.checkpoint_id}")
        
        for step in rollback_steps:
            try:
                if step == "restore_files":
                    await self._restore_files(checkpoint)
                elif step == "revert_database":
                    await self._revert_database(checkpoint)
                elif step == "reset_git":
                    await self._reset_git(checkpoint)
                else:
                    logger.warning(f"Unknown rollback step: {step}")
                    
            except Exception as e:
                logger.error(f"Rollback step '{step}' failed: {e}")
                raise
        
        logger.info("Rollback completed successfully")
    
    async def _restore_files(self, checkpoint: CheckpointData):
        """Restore files from checkpoint snapshots"""
        for original_path, backup_path in checkpoint.file_snapshots.items():
            try:
                if Path(backup_path).exists():
                    shutil.copy2(backup_path, original_path)
                    logger.info(f"Restored file: {original_path}")
            except Exception as e:
                logger.error(f"Failed to restore file {original_path}: {e}")
                raise
    
    async def _revert_database(self, checkpoint: CheckpointData):
        """Revert database to checkpoint state (placeholder)"""
        # This would implement database rollback logic
        # The actual implementation would depend on the database system
        logger.info("Database revert not implemented yet")
    
    async def _reset_git(self, checkpoint: CheckpointData):
        """Reset git to checkpoint commit"""
        if checkpoint.git_commit_hash:
            try:
                subprocess.run(
                    ['git', 'reset', '--hard', checkpoint.git_commit_hash],
                    check=True,
                    capture_output=True
                )
                logger.info(f"Reset git to commit: {checkpoint.git_commit_hash}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Git reset failed: {e}")
                raise
    
    async def _cleanup_resources(self, error_context: ErrorContext):
        """Cleanup system resources"""
        logger.info("Cleaning up system resources")
        
        # Cleanup temporary files
        temp_dir = Path("/tmp")
        workflow_temp_files = list(temp_dir.glob(f"*{error_context.workflow_id}*"))
        
        for temp_file in workflow_temp_files:
            try:
                if temp_file.is_file():
                    temp_file.unlink()
                elif temp_file.is_dir():
                    shutil.rmtree(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_file}: {e}")
        
        # Force garbage collection
        import gc
        gc.collect()
    
    async def _notify_administrators(self, error_context: ErrorContext, action: RecoveryAction):
        """Notify administrators about errors requiring intervention"""
        # This would implement notification logic (email, Slack, etc.)
        logger.warning(f"Administrator notification: {error_context.error_message}")
    
    async def _create_incident_record(self, error_context: ErrorContext, action: RecoveryAction):
        """Create an incident record for critical errors"""
        incident_data = {
            "incident_id": f"INC_{error_context.workflow_id}_{int(error_context.timestamp.timestamp())}",
            "workflow_id": error_context.workflow_id,
            "task_id": error_context.task_id,
            "severity": error_context.severity.value,
            "error_message": error_context.error_message,
            "recovery_action": action.description,
            "timestamp": error_context.timestamp.isoformat(),
            "status": "open"
        }
        
        incident_file = self.checkpoints_directory / f"incident_{incident_data['incident_id']}.json"
        with open(incident_file, 'w') as f:
            json.dump(incident_data, f, indent=2)
        
        logger.critical(f"Created incident record: {incident_data['incident_id']}")
    
    async def _execute_handler(self, handler: Callable, error_context: ErrorContext):
        """Execute an error handler function"""
        if asyncio.iscoroutinefunction(handler):
            await handler(error_context)
        else:
            # Run sync handler in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, handler, error_context)
    
    def get_error_history(self, workflow_id: str) -> List[ErrorContext]:
        """Get error history for a workflow"""
        return self.recovery_history.get(workflow_id, [])
    
    def get_checkpoints(self, workflow_id: str) -> List[CheckpointData]:
        """Get checkpoints for a workflow"""
        return [cp for cp in self.checkpoints.values() if cp.workflow_id == workflow_id]
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Cleanup old checkpoints and error history"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        # Cleanup old checkpoints
        to_remove = [
            cp_id for cp_id, cp in self.checkpoints.items()
            if cp.timestamp < cutoff_date
        ]
        
        for cp_id in to_remove:
            # Remove checkpoint data
            checkpoint = self.checkpoints.pop(cp_id)
            
            # Remove checkpoint file
            checkpoint_file = self.checkpoints_directory / f"{cp_id}.json"
            if checkpoint_file.exists():
                checkpoint_file.unlink()
            
            # Remove file snapshots
            for backup_path in checkpoint.file_snapshots.values():
                backup_file = Path(backup_path)
                if backup_file.exists():
                    backup_file.unlink()
        
        logger.info(f"Cleaned up {len(to_remove)} old checkpoints")

# Global error handler instance
error_handler = ErrorHandler()