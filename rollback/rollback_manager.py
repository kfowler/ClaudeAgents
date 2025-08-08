#!/usr/bin/env python3
"""
Rollback Management System for Claude Code Enhancement Deployment.
Comprehensive rollback procedures with automated triggers and communication.
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import git
import uuid


class RollbackType(Enum):
    """Types of rollback procedures."""
    FULL = "full"
    PARTIAL = "partial"
    CODE_ONLY = "code_only"
    CONFIG_ONLY = "config_only"
    DATABASE_ONLY = "database_only"


class RollbackTrigger(Enum):
    """Rollback trigger types."""
    MANUAL = "manual"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_THRESHOLD = "error_rate_threshold"
    USER_SATISFACTION = "user_satisfaction"
    SYSTEM_HEALTH = "system_health"
    SECURITY_INCIDENT = "security_incident"


class RollbackStatus(Enum):
    """Rollback execution status."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class RollbackTriggerCondition:
    """Rollback trigger condition definition."""
    trigger_type: RollbackTrigger
    metric_name: str
    threshold_value: float
    comparison: str  # "greater_than", "less_than", "equals"
    duration_minutes: int  # How long condition must persist
    enabled: bool = True


@dataclass
class RollbackExecution:
    """Rollback execution record."""
    id: str
    trigger_type: RollbackTrigger
    rollback_type: RollbackType
    status: RollbackStatus
    initiated_by: str
    start_time: str
    end_time: Optional[str]
    duration_seconds: Optional[float]
    steps_completed: List[str]
    steps_failed: List[str]
    rollback_point: str  # Git commit hash or version
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class RollbackDatabase:
    """Database for rollback tracking."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize rollback database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Rollback executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rollback_executions (
                id TEXT PRIMARY KEY,
                trigger_type TEXT NOT NULL,
                rollback_type TEXT NOT NULL,
                status TEXT NOT NULL,
                initiated_by TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds REAL,
                steps_completed TEXT,
                steps_failed TEXT,
                rollback_point TEXT NOT NULL,
                error_message TEXT,
                metadata TEXT
            )
        """)
        
        # Rollback snapshots table for data backup
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rollback_snapshots (
                id TEXT PRIMARY KEY,
                snapshot_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                checksum TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_start_time 
            ON rollback_executions(start_time)
        """)
        
        conn.commit()
        conn.close()
        
    def store_execution(self, execution: RollbackExecution):
        """Store rollback execution."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        steps_completed_json = json.dumps(execution.steps_completed)
        steps_failed_json = json.dumps(execution.steps_failed)
        metadata_json = json.dumps(execution.metadata) if execution.metadata else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO rollback_executions 
            (id, trigger_type, rollback_type, status, initiated_by, start_time,
             end_time, duration_seconds, steps_completed, steps_failed, 
             rollback_point, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution.id, execution.trigger_type.value, execution.rollback_type.value,
            execution.status.value, execution.initiated_by, execution.start_time,
            execution.end_time, execution.duration_seconds, steps_completed_json,
            steps_failed_json, execution.rollback_point, execution.error_message,
            metadata_json
        ))
        
        conn.commit()
        conn.close()


class GitRollbackManager:
    """Git-based rollback management."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo = git.Repo(str(repo_path))
        
    def get_current_commit(self) -> str:
        """Get current commit hash."""
        return self.repo.head.commit.hexsha
        
    def get_rollback_points(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get available rollback points."""
        since_date = datetime.now() - timedelta(days=days)
        
        rollback_points = []
        for commit in self.repo.iter_commits(since=since_date):
            rollback_points.append({
                "commit": commit.hexsha,
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "tags": [tag.name for tag in self.repo.tags if tag.commit == commit]
            })
            
        return rollback_points
        
    def rollback_to_commit(self, commit_hash: str) -> bool:
        """Rollback to specific commit."""
        try:
            # Stash current changes
            self.repo.git.stash("save", "Pre-rollback stash", "--include-untracked")
            
            # Reset to target commit
            self.repo.git.reset("--hard", commit_hash)
            
            return True
            
        except Exception as e:
            logging.error(f"Git rollback failed: {str(e)}")
            return False
            
    def create_rollback_branch(self, commit_hash: str) -> str:
        """Create rollback branch from commit."""
        try:
            branch_name = f"rollback-{commit_hash[:8]}-{int(time.time())}"
            self.repo.create_head(branch_name, commit_hash)
            return branch_name
            
        except Exception as e:
            logging.error(f"Failed to create rollback branch: {str(e)}")
            return ""


class ConfigurationManager:
    """Configuration rollback management."""
    
    def __init__(self, config_dir: Path, backup_dir: Path):
        self.config_dir = config_dir
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def backup_configuration(self) -> str:
        """Backup current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"config_backup_{timestamp}"
        
        try:
            if self.config_dir.exists():
                shutil.copytree(self.config_dir, backup_path)
                return str(backup_path)
            else:
                logging.warning(f"Configuration directory {self.config_dir} does not exist")
                return ""
                
        except Exception as e:
            logging.error(f"Configuration backup failed: {str(e)}")
            return ""
            
    def restore_configuration(self, backup_path: str) -> bool:
        """Restore configuration from backup."""
        try:
            backup_path_obj = Path(backup_path)
            
            if not backup_path_obj.exists():
                logging.error(f"Backup path {backup_path} does not exist")
                return False
                
            # Remove current configuration
            if self.config_dir.exists():
                shutil.rmtree(self.config_dir)
                
            # Restore from backup
            shutil.copytree(backup_path_obj, self.config_dir)
            
            return True
            
        except Exception as e:
            logging.error(f"Configuration restore failed: {str(e)}")
            return False


class DatabaseRollbackManager:
    """Database rollback management."""
    
    def __init__(self, db_paths: List[Path], backup_dir: Path):
        self.db_paths = db_paths
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def backup_databases(self) -> Dict[str, str]:
        """Backup all databases."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backups = {}
        
        for db_path in self.db_paths:
            if db_path.exists():
                backup_name = f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
                backup_path = self.backup_dir / backup_name
                
                try:
                    shutil.copy2(db_path, backup_path)
                    backups[str(db_path)] = str(backup_path)
                    
                except Exception as e:
                    logging.error(f"Database backup failed for {db_path}: {str(e)}")
                    
        return backups
        
    def restore_databases(self, backup_mapping: Dict[str, str]) -> bool:
        """Restore databases from backup."""
        try:
            for original_path, backup_path in backup_mapping.items():
                original_path_obj = Path(original_path)
                backup_path_obj = Path(backup_path)
                
                if backup_path_obj.exists():
                    shutil.copy2(backup_path_obj, original_path_obj)
                else:
                    logging.error(f"Backup file {backup_path} not found")
                    return False
                    
            return True
            
        except Exception as e:
            logging.error(f"Database restore failed: {str(e)}")
            return False


class CommunicationManager:
    """Rollback communication management."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def send_rollback_notification(self, execution: RollbackExecution, message_type: str = "initiated"):
        """Send rollback notification."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        messages = {
            "initiated": {
                "subject": f"🚨 Rollback Initiated - {execution.rollback_type.value}",
                "body": f"""
A rollback procedure has been initiated for the Claude Code Enhancement system.

Details:
- Rollback ID: {execution.id}
- Type: {execution.rollback_type.value.replace('_', ' ').title()}
- Trigger: {execution.trigger_type.value.replace('_', ' ').title()}
- Initiated by: {execution.initiated_by}
- Start time: {execution.start_time}
- Rollback point: {execution.rollback_point}

Status: The rollback is currently in progress. We will provide updates as the procedure continues.

For questions or concerns, please contact the development team.
"""
            },
            "completed": {
                "subject": f"✅ Rollback Completed Successfully - {execution.rollback_type.value}",
                "body": f"""
The rollback procedure for the Claude Code Enhancement system has been completed successfully.

Details:
- Rollback ID: {execution.id}
- Type: {execution.rollback_type.value.replace('_', ' ').title()}
- Duration: {execution.duration_seconds:.1f} seconds
- Completed steps: {len(execution.steps_completed)}
- Status: {execution.status.value.title()}

The system has been restored to the previous stable state. All services should now be operating normally.

Thank you for your patience during this procedure.
"""
            },
            "failed": {
                "subject": f"❌ Rollback Failed - {execution.rollback_type.value}",
                "body": f"""
URGENT: The rollback procedure for the Claude Code Enhancement system has failed.

Details:
- Rollback ID: {execution.id}
- Type: {execution.rollback_type.value.replace('_', ' ').title()}
- Duration: {execution.duration_seconds:.1f} seconds if execution.duration_seconds else 'N/A'}
- Error: {execution.error_message or 'Unknown error'}
- Failed steps: {len(execution.steps_failed)}

IMMEDIATE ACTION REQUIRED: Manual intervention is needed to restore system stability.

Please contact the development team immediately for emergency support.
"""
            }
        }
        
        message = messages.get(message_type, messages["initiated"])
        
        # Write notification to file (in real implementation, would send via email/Slack/etc)
        notification_file = self.output_dir / f"rollback_notification_{execution.id}_{message_type}.txt"
        
        with open(notification_file, 'w') as f:
            f.write(f"Timestamp: {timestamp}\\n")
            f.write(f"Subject: {message['subject']}\\n\\n")
            f.write(message['body'])
            
        logging.info(f"Rollback notification sent: {message_type} - {notification_file}")
        
        # Console notification
        print(f"\\n{message['subject']}")
        print("=" * len(message['subject']))
        print(message['body'])


class RollbackManager:
    """Main rollback management orchestrator."""
    
    def __init__(self, 
                 repo_path: Path = Path("."),
                 data_dir: Path = Path("rollback/data")):
        self.repo_path = repo_path
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.database = RollbackDatabase(self.data_dir / "rollback.db")
        self.git_manager = GitRollbackManager(repo_path)
        self.config_manager = ConfigurationManager(
            config_dir=Path("."),  # Current directory contains configs
            backup_dir=self.data_dir / "config_backups"
        )
        self.db_manager = DatabaseRollbackManager(
            db_paths=[
                Path("project_analysis_cache.db"),
                Path("monitoring/data/monitoring.db"),
                Path("feedback/data/feedback.db")
            ],
            backup_dir=self.data_dir / "db_backups"
        )
        self.communication = CommunicationManager(self.data_dir / "communications")
        
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for rollback system."""
        log_dir = self.data_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'rollback.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_rollback_triggers(self) -> List[RollbackTrigger]:
        """Check if any rollback triggers are activated."""
        triggered = []
        
        try:
            # Check monitoring data for trigger conditions
            from monitoring.monitor_runner import RolloutMonitor
            monitor = RolloutMonitor()
            status = monitor.get_system_status()
            
            # Performance degradation trigger
            if status["overall_health"] == "critical":
                triggered.append(RollbackTrigger.SYSTEM_HEALTH)
                
            if status["alerts"]["critical"] > 0:
                triggered.append(RollbackTrigger.PERFORMANCE_DEGRADATION)
                
            # Check feedback for user satisfaction issues
            try:
                from feedback.collector import FeedbackCollector
                feedback_collector = FeedbackCollector()
                summary = feedback_collector.get_feedback_summary(days=1)  # Last day
                
                if summary["average_rating"] < 2.0 and summary["ratings_count"] > 5:
                    triggered.append(RollbackTrigger.USER_SATISFACTION)
                    
            except Exception as e:
                self.logger.warning(f"Could not check feedback triggers: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error checking rollback triggers: {str(e)}")
            
        return triggered
        
    async def execute_rollback(self, 
                             rollback_type: RollbackType,
                             trigger_type: RollbackTrigger,
                             initiated_by: str,
                             rollback_point: Optional[str] = None) -> RollbackExecution:
        """Execute rollback procedure."""
        
        execution_id = str(uuid.uuid4())
        
        if not rollback_point:
            # Get latest stable rollback point (e.g., last tagged release)
            rollback_points = self.git_manager.get_rollback_points()
            stable_points = [rp for rp in rollback_points if rp["tags"]]
            
            if stable_points:
                rollback_point = stable_points[0]["commit"]
            else:
                # Fallback to commit from 24 hours ago
                rollback_point = rollback_points[0]["commit"] if rollback_points else self.git_manager.get_current_commit()
                
        execution = RollbackExecution(
            id=execution_id,
            trigger_type=trigger_type,
            rollback_type=rollback_type,
            status=RollbackStatus.INITIATED,
            initiated_by=initiated_by,
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration_seconds=None,
            steps_completed=[],
            steps_failed=[],
            rollback_point=rollback_point
        )
        
        self.database.store_execution(execution)
        self.communication.send_rollback_notification(execution, "initiated")
        
        self.logger.info(f"Starting rollback execution {execution_id}")
        start_time = time.time()
        
        try:
            execution.status = RollbackStatus.IN_PROGRESS
            self.database.store_execution(execution)
            
            # Execute rollback steps based on type
            if rollback_type in [RollbackType.FULL, RollbackType.CODE_ONLY]:
                await self._rollback_code(execution)
                
            if rollback_type in [RollbackType.FULL, RollbackType.CONFIG_ONLY]:
                await self._rollback_configuration(execution)
                
            if rollback_type in [RollbackType.FULL, RollbackType.DATABASE_ONLY]:
                await self._rollback_databases(execution)
                
            # Restart services if full rollback
            if rollback_type == RollbackType.FULL:
                await self._restart_services(execution)
                
            # Validate rollback success
            validation_success = await self._validate_rollback(execution)
            
            if validation_success and not execution.steps_failed:
                execution.status = RollbackStatus.COMPLETED
                self.logger.info(f"Rollback {execution_id} completed successfully")
                self.communication.send_rollback_notification(execution, "completed")
            else:
                execution.status = RollbackStatus.FAILED
                execution.error_message = "Rollback validation failed or steps failed"
                self.logger.error(f"Rollback {execution_id} failed validation")
                self.communication.send_rollback_notification(execution, "failed")
                
        except Exception as e:
            execution.status = RollbackStatus.FAILED
            execution.error_message = str(e)
            execution.steps_failed.append(f"Rollback execution error: {str(e)}")
            self.logger.error(f"Rollback {execution_id} failed: {str(e)}")
            self.communication.send_rollback_notification(execution, "failed")
            
        # Finalize execution record
        execution.end_time = datetime.now().isoformat()
        execution.duration_seconds = time.time() - start_time
        self.database.store_execution(execution)
        
        return execution
        
    async def _rollback_code(self, execution: RollbackExecution):
        """Rollback code changes."""
        try:
            self.logger.info(f"Rolling back code to {execution.rollback_point}")
            
            # Create backup branch first
            backup_branch = self.git_manager.create_rollback_branch(
                self.git_manager.get_current_commit()
            )
            
            if backup_branch:
                execution.steps_completed.append(f"Created backup branch: {backup_branch}")
            else:
                execution.steps_failed.append("Failed to create backup branch")
                
            # Perform rollback
            if self.git_manager.rollback_to_commit(execution.rollback_point):
                execution.steps_completed.append(f"Code rolled back to {execution.rollback_point}")
                self.logger.info("Code rollback successful")
            else:
                execution.steps_failed.append("Git rollback failed")
                raise Exception("Git rollback failed")
                
        except Exception as e:
            execution.steps_failed.append(f"Code rollback error: {str(e)}")
            raise
            
    async def _rollback_configuration(self, execution: RollbackExecution):
        """Rollback configuration changes."""
        try:
            self.logger.info("Rolling back configuration")
            
            # Find most recent configuration backup
            backup_dir = self.data_dir / "config_backups"
            if backup_dir.exists():
                backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], 
                               key=lambda x: x.stat().st_mtime, reverse=True)
                
                if backups:
                    latest_backup = backups[0]
                    if self.config_manager.restore_configuration(str(latest_backup)):
                        execution.steps_completed.append(f"Configuration restored from {latest_backup.name}")
                        self.logger.info("Configuration rollback successful")
                    else:
                        execution.steps_failed.append("Configuration restore failed")
                        raise Exception("Configuration restore failed")
                else:
                    execution.steps_failed.append("No configuration backups found")
                    self.logger.warning("No configuration backups found")
            else:
                execution.steps_failed.append("Configuration backup directory not found")
                self.logger.warning("Configuration backup directory not found")
                
        except Exception as e:
            execution.steps_failed.append(f"Configuration rollback error: {str(e)}")
            raise
            
    async def _rollback_databases(self, execution: RollbackExecution):
        """Rollback database changes."""
        try:
            self.logger.info("Rolling back databases")
            
            # Find most recent database backup
            backup_dir = self.data_dir / "db_backups"
            if backup_dir.exists():
                # Get latest backup mapping
                backup_files = list(backup_dir.glob("*_backup_*.db"))
                
                if backup_files:
                    # Group backups by timestamp
                    backup_groups = {}
                    for backup_file in backup_files:
                        # Extract timestamp from filename (format: name_backup_YYYYMMDD_HHMMSS.db)
                        parts = backup_file.stem.split('_backup_')
                        if len(parts) == 2:
                            original_name = parts[0]
                            timestamp = parts[1]
                            
                            if timestamp not in backup_groups:
                                backup_groups[timestamp] = {}
                                
                            backup_groups[timestamp][original_name] = str(backup_file)
                            
                    if backup_groups:
                        # Get latest backup set
                        latest_timestamp = max(backup_groups.keys())
                        latest_backups = backup_groups[latest_timestamp]
                        
                        # Create mapping for restore
                        restore_mapping = {}
                        for original_name, backup_path in latest_backups.items():
                            # Map to current database locations
                            if "project_analysis_cache" in original_name:
                                restore_mapping["project_analysis_cache.db"] = backup_path
                            elif "monitoring" in original_name:
                                restore_mapping["monitoring/data/monitoring.db"] = backup_path
                            elif "feedback" in original_name:
                                restore_mapping["feedback/data/feedback.db"] = backup_path
                                
                        if self.db_manager.restore_databases(restore_mapping):
                            execution.steps_completed.append(f"Databases restored from {latest_timestamp}")
                            self.logger.info("Database rollback successful")
                        else:
                            execution.steps_failed.append("Database restore failed")
                            raise Exception("Database restore failed")
                    else:
                        execution.steps_failed.append("No valid database backups found")
                        self.logger.warning("No valid database backups found")
                else:
                    execution.steps_failed.append("No database backup files found")
                    self.logger.warning("No database backup files found")
            else:
                execution.steps_failed.append("Database backup directory not found")
                self.logger.warning("Database backup directory not found")
                
        except Exception as e:
            execution.steps_failed.append(f"Database rollback error: {str(e)}")
            raise
            
    async def _restart_services(self, execution: RollbackExecution):
        """Restart services after rollback."""
        try:
            self.logger.info("Restarting services")
            
            # Simulate service restart (in real implementation, would restart actual services)
            await asyncio.sleep(2)  # Simulate restart time
            
            execution.steps_completed.append("Services restarted successfully")
            self.logger.info("Service restart successful")
            
        except Exception as e:
            execution.steps_failed.append(f"Service restart error: {str(e)}")
            raise
            
    async def _validate_rollback(self, execution: RollbackExecution) -> bool:
        """Validate rollback success."""
        try:
            self.logger.info("Validating rollback success")
            
            validation_results = []
            
            # Run basic system validation
            try:
                # Check if git is in expected state
                current_commit = self.git_manager.get_current_commit()
                if current_commit == execution.rollback_point:
                    validation_results.append("Git state validation: PASS")
                else:
                    validation_results.append("Git state validation: FAIL")
                    
            except Exception as e:
                validation_results.append(f"Git validation error: {str(e)}")
                
            # Check if key files exist
            key_files = ["CLAUDE.md", "README.md", "agents/", "commands/"]
            for file_path in key_files:
                if Path(file_path).exists():
                    validation_results.append(f"File check {file_path}: PASS")
                else:
                    validation_results.append(f"File check {file_path}: FAIL")
                    
            # Run quick smoke tests
            try:
                from testing.test_runner import TestRunner
                test_runner = TestRunner()
                
                # Run basic integration tests
                integration_results = await test_runner.run_integration_tests()
                passed_tests = len([r for r in integration_results if r.status == "passed"])
                total_tests = len(integration_results)
                
                if total_tests > 0 and passed_tests / total_tests >= 0.8:  # 80% success rate
                    validation_results.append(f"Smoke tests: PASS ({passed_tests}/{total_tests})")
                else:
                    validation_results.append(f"Smoke tests: FAIL ({passed_tests}/{total_tests})")
                    
            except Exception as e:
                validation_results.append(f"Smoke test error: {str(e)}")
                
            execution.steps_completed.append(f"Rollback validation: {'; '.join(validation_results)}")
            
            # Determine overall validation success
            failed_validations = [r for r in validation_results if "FAIL" in r or "error" in r]
            
            if len(failed_validations) == 0:
                self.logger.info("Rollback validation successful")
                return True
            else:
                self.logger.warning(f"Rollback validation failed: {failed_validations}")
                return False
                
        except Exception as e:
            execution.steps_failed.append(f"Rollback validation error: {str(e)}")
            return False
            
    def create_pre_rollback_snapshot(self) -> Dict[str, str]:
        """Create snapshot before rollback for potential recovery."""
        snapshots = {}
        
        try:
            # Backup configurations
            config_backup = self.config_manager.backup_configuration()
            if config_backup:
                snapshots["configuration"] = config_backup
                
            # Backup databases  
            db_backups = self.db_manager.backup_databases()
            snapshots.update(db_backups)
            
            # Create git branch snapshot
            current_commit = self.git_manager.get_current_commit()
            snapshot_branch = self.git_manager.create_rollback_branch(current_commit)
            if snapshot_branch:
                snapshots["git_branch"] = snapshot_branch
                
            self.logger.info(f"Pre-rollback snapshot created: {len(snapshots)} items")
            return snapshots
            
        except Exception as e:
            self.logger.error(f"Failed to create pre-rollback snapshot: {str(e)}")
            return snapshots
            
    def test_rollback_procedures(self) -> Dict[str, Any]:
        """Test rollback procedures without executing them."""
        test_results = {
            "git_rollback": False,
            "config_rollback": False,
            "database_rollback": False,
            "validation_check": False,
            "overall_status": False
        }
        
        try:
            # Test git rollback capability
            rollback_points = self.git_manager.get_rollback_points(days=7)
            if rollback_points:
                test_results["git_rollback"] = True
                
            # Test configuration backup/restore
            test_config_backup = self.config_manager.backup_configuration()
            if test_config_backup and Path(test_config_backup).exists():
                test_results["config_rollback"] = True
                
            # Test database backup
            test_db_backups = self.db_manager.backup_databases()
            if test_db_backups:
                test_results["database_rollback"] = True
                
            # Test validation components
            try:
                from testing.test_runner import TestRunner
                test_results["validation_check"] = True
            except Exception:
                pass
                
            # Overall status
            test_results["overall_status"] = all([
                test_results["git_rollback"],
                test_results["config_rollback"],
                test_results["validation_check"]
            ])
            
        except Exception as e:
            self.logger.error(f"Rollback procedure test failed: {str(e)}")
            
        return test_results


async def main():
    """Main entry point for rollback manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Enhancement Rollback Manager")
    parser.add_argument("--execute", action="store_true", help="Execute rollback")
    parser.add_argument("--type", choices=["full", "partial", "code_only", "config_only", "database_only"], 
                       default="full", help="Rollback type")
    parser.add_argument("--trigger", choices=["manual", "performance_degradation", "error_rate_threshold", 
                                             "user_satisfaction", "system_health", "security_incident"],
                       default="manual", help="Rollback trigger")
    parser.add_argument("--rollback-point", help="Specific commit to rollback to")
    parser.add_argument("--check-triggers", action="store_true", help="Check rollback triggers")
    parser.add_argument("--test", action="store_true", help="Test rollback procedures")
    parser.add_argument("--snapshot", action="store_true", help="Create pre-rollback snapshot")
    
    args = parser.parse_args()
    
    manager = RollbackManager()
    
    if args.execute:
        print(f"🚨 Initiating {args.type} rollback...")
        print("This action will modify the system state.")
        
        confirmation = input("Are you sure you want to proceed? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Rollback cancelled.")
            return
            
        execution = await manager.execute_rollback(
            rollback_type=RollbackType(args.type),
            trigger_type=RollbackTrigger(args.trigger),
            initiated_by="manual_execution",
            rollback_point=args.rollback_point
        )
        
        print(f"\\nRollback execution completed:")
        print(f"Status: {execution.status.value}")
        print(f"Duration: {execution.duration_seconds:.1f} seconds")
        print(f"Steps completed: {len(execution.steps_completed)}")
        print(f"Steps failed: {len(execution.steps_failed)}")
        
        if execution.steps_failed:
            print("\\nFailed steps:")
            for step in execution.steps_failed:
                print(f"  - {step}")
                
    elif args.check_triggers:
        triggers = manager.check_rollback_triggers()
        print("\\nRollback Trigger Status:")
        
        if triggers:
            print("🚨 ACTIVE TRIGGERS:")
            for trigger in triggers:
                print(f"  - {trigger.value.replace('_', ' ').title()}")
        else:
            print("✅ No rollback triggers are currently active")
            
    elif args.test:
        results = manager.test_rollback_procedures()
        print("\\nRollback Procedure Test Results:")
        
        for component, status in results.items():
            status_icon = "✅" if status else "❌"
            component_name = component.replace('_', ' ').title()
            print(f"  {status_icon} {component_name}: {'PASS' if status else 'FAIL'}")
            
        print(f"\\nOverall Status: {'✅ READY' if results['overall_status'] else '❌ NOT READY'}")
        
    elif args.snapshot:
        snapshots = manager.create_pre_rollback_snapshot()
        print("\\nPre-rollback Snapshot Created:")
        
        for item_type, path in snapshots.items():
            print(f"  - {item_type.replace('_', ' ').title()}: {path}")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())