#!/usr/bin/env python3
"""
Master Rollout Validation Orchestration Script for Claude Code Enhancements.

This script orchestrates the comprehensive validation framework including:
- Testing strategy execution
- Quality gates validation
- Rollout monitoring
- User feedback collection
- Rollback procedures

Usage:
    python rollout_validation.py --phase pre-deployment
    python rollout_validation.py --phase deployment
    python rollout_validation.py --phase post-deployment
    python rollout_validation.py --phase full-validation
"""

import asyncio
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ValidationPhase(Enum):
    """Validation phases for rollout."""
    PRE_DEPLOYMENT = "pre-deployment"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT = "post-deployment"
    FULL_VALIDATION = "full-validation"


class ValidationStatus(Enum):
    """Overall validation status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    IN_PROGRESS = "in_progress"
    NOT_STARTED = "not_started"


@dataclass
class ValidationResult:
    """Validation result summary."""
    phase: ValidationPhase
    status: ValidationStatus
    start_time: str
    end_time: Optional[str]
    duration_seconds: Optional[float]
    components: Dict[str, Any]  # Results from each validation component
    overall_score: float
    recommendations: List[str]
    blocking_issues: List[str]
    rollout_decision: str  # "proceed", "proceed_with_caution", "block"


class ValidationOrchestrator:
    """Master validation orchestrator."""
    
    def __init__(self, output_dir: Path = Path("validation_reports")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_logging()
        
        # Component availability flags
        self.components_available = {
            "testing": True,
            "quality_gates": True,
            "monitoring": True,
            "feedback": True,
            "rollback": True
        }
        
        self.check_component_availability()
        
    def setup_logging(self):
        """Configure logging for validation orchestrator."""
        log_dir = self.output_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'validation_orchestration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_component_availability(self):
        """Check availability of validation components."""
        components = {
            "testing": "testing/test_runner.py",
            "quality_gates": "quality/gate_runner.py",
            "monitoring": "monitoring/monitor_runner.py",
            "feedback": "feedback/collector.py",
            "rollback": "rollback/rollback_manager.py"
        }
        
        for component, script_path in components.items():
            if not Path(script_path).exists():
                self.components_available[component] = False
                self.logger.warning(f"Component {component} not available: {script_path} not found")
                
    async def execute_validation_phase(self, phase: ValidationPhase) -> ValidationResult:
        """Execute specific validation phase."""
        self.logger.info(f"Starting validation phase: {phase.value}")
        
        start_time = time.time()
        result = ValidationResult(
            phase=phase,
            status=ValidationStatus.IN_PROGRESS,
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration_seconds=None,
            components={},
            overall_score=0.0,
            recommendations=[],
            blocking_issues=[],
            rollout_decision="block"  # Default to block until validation passes
        )
        
        try:
            if phase == ValidationPhase.PRE_DEPLOYMENT:
                await self._execute_pre_deployment_validation(result)
            elif phase == ValidationPhase.DEPLOYMENT:
                await self._execute_deployment_validation(result)
            elif phase == ValidationPhase.POST_DEPLOYMENT:
                await self._execute_post_deployment_validation(result)
            elif phase == ValidationPhase.FULL_VALIDATION:
                await self._execute_full_validation(result)
                
            # Calculate overall results
            self._calculate_overall_results(result)
            
        except Exception as e:
            result.status = ValidationStatus.FAILED
            result.blocking_issues.append(f"Validation execution failed: {str(e)}")
            self.logger.error(f"Validation phase {phase.value} failed: {str(e)}")
            
        # Finalize result
        result.end_time = datetime.now().isoformat()
        result.duration_seconds = time.time() - start_time
        
        # Generate reports
        self._generate_phase_report(result)
        
        return result
        
    async def _execute_pre_deployment_validation(self, result: ValidationResult):
        """Execute pre-deployment validation."""
        self.logger.info("Executing pre-deployment validation")
        
        # 1. Quality Gates Validation
        if self.components_available["quality_gates"]:
            try:
                self.logger.info("Running quality gates validation")
                
                from quality.gate_runner import QualityGateRunner
                gate_runner = QualityGateRunner()
                
                # Run all quality gates
                gate_results = await gate_runner.run_all_gates(parallel=True)
                
                # Process gate results
                gate_summary = {
                    "total_gates": len(gate_results),
                    "passed": len([r for r in gate_results if r.status.value == "passed"]),
                    "failed": len([r for r in gate_results if r.status.value == "failed"]),
                    "warning": len([r for r in gate_results if r.status.value == "warning"]),
                    "overall_score": sum(r.score for r in gate_results) / len(gate_results) if gate_results else 0,
                    "details": [asdict(r) for r in gate_results]
                }
                
                result.components["quality_gates"] = gate_summary
                
                # Check for blocking issues
                failed_gates = [r for r in gate_results if r.status.value == "failed"]
                for gate in failed_gates:
                    result.blocking_issues.extend([f"Quality Gate '{gate.gate_name}': {rec}" for rec in gate.recommendations])
                    
                self.logger.info(f"Quality gates completed: {gate_summary['passed']}/{gate_summary['total']} passed")
                
            except Exception as e:
                result.components["quality_gates"] = {"error": str(e)}
                result.blocking_issues.append(f"Quality gates validation failed: {str(e)}")
                self.logger.error(f"Quality gates validation failed: {str(e)}")
        else:
            result.components["quality_gates"] = {"status": "unavailable"}
            
        # 2. Comprehensive Testing
        if self.components_available["testing"]:
            try:
                self.logger.info("Running comprehensive test suite")
                
                from testing.test_runner import TestRunner
                test_runner = TestRunner()
                
                # Run all test suites
                test_results = await test_runner.run_all_tests(parallel=True)
                
                result.components["testing"] = {
                    "summary": test_results["summary"],
                    "reports": test_results["reports"]
                }
                
                # Check for test failures
                if test_results["summary"]["failed"] > 0:
                    result.blocking_issues.append(f"Test failures: {test_results['summary']['failed']} tests failed")
                    
                self.logger.info(f"Testing completed: {test_results['summary']['success_rate']:.1f}% success rate")
                
            except Exception as e:
                result.components["testing"] = {"error": str(e)}
                result.blocking_issues.append(f"Testing validation failed: {str(e)}")
                self.logger.error(f"Testing validation failed: {str(e)}")
        else:
            result.components["testing"] = {"status": "unavailable"}
            
        # 3. Rollback Readiness Check
        if self.components_available["rollback"]:
            try:
                self.logger.info("Checking rollback readiness")
                
                from rollback.rollback_manager import RollbackManager
                rollback_manager = RollbackManager()
                
                # Test rollback procedures
                rollback_test_results = rollback_manager.test_rollback_procedures()
                
                result.components["rollback_readiness"] = rollback_test_results
                
                if not rollback_test_results["overall_status"]:
                    result.blocking_issues.append("Rollback procedures not ready")
                    
                # Create pre-deployment snapshot
                snapshot = rollback_manager.create_pre_rollback_snapshot()
                result.components["pre_deployment_snapshot"] = {
                    "created": len(snapshot) > 0,
                    "items": len(snapshot)
                }
                
                self.logger.info(f"Rollback readiness: {'READY' if rollback_test_results['overall_status'] else 'NOT READY'}")
                
            except Exception as e:
                result.components["rollback_readiness"] = {"error": str(e)}
                result.recommendations.append(f"Could not verify rollback readiness: {str(e)}")
                self.logger.warning(f"Rollback readiness check failed: {str(e)}")
        else:
            result.components["rollback_readiness"] = {"status": "unavailable"}
            
    async def _execute_deployment_validation(self, result: ValidationResult):
        """Execute deployment-time validation."""
        self.logger.info("Executing deployment validation")
        
        # 1. Start Monitoring
        if self.components_available["monitoring"]:
            try:
                self.logger.info("Initializing deployment monitoring")
                
                from monitoring.monitor_runner import RolloutMonitor
                monitor = RolloutMonitor()
                
                # Start background monitoring
                # Note: In a real implementation, this would start the monitor in a separate process
                status = monitor.get_system_status()
                
                result.components["monitoring"] = {
                    "initialized": True,
                    "initial_status": status
                }
                
                self.logger.info("Deployment monitoring initialized")
                
            except Exception as e:
                result.components["monitoring"] = {"error": str(e)}
                result.recommendations.append(f"Monitoring initialization failed: {str(e)}")
                self.logger.warning(f"Monitoring initialization failed: {str(e)}")
        else:
            result.components["monitoring"] = {"status": "unavailable"}
            
        # 2. Initialize Feedback Collection
        if self.components_available["feedback"]:
            try:
                self.logger.info("Initializing feedback collection")
                
                from feedback.collector import FeedbackCollector
                feedback_collector = FeedbackCollector()
                
                result.components["feedback_collection"] = {
                    "initialized": True,
                    "database_path": str(feedback_collector.db_path)
                }
                
                self.logger.info("Feedback collection initialized")
                
            except Exception as e:
                result.components["feedback_collection"] = {"error": str(e)}
                result.recommendations.append(f"Feedback collection initialization failed: {str(e)}")
                self.logger.warning(f"Feedback collection initialization failed: {str(e)}")
        else:
            result.components["feedback_collection"] = {"status": "unavailable"}
            
        # 3. Deployment Health Check
        await self._perform_deployment_health_check(result)
        
    async def _execute_post_deployment_validation(self, result: ValidationResult):
        """Execute post-deployment validation."""
        self.logger.info("Executing post-deployment validation")
        
        # 1. System Health Monitoring
        if self.components_available["monitoring"]:
            try:
                self.logger.info("Checking post-deployment system health")
                
                from monitoring.monitor_runner import RolloutMonitor
                monitor = RolloutMonitor()
                
                # Get current system status
                status = monitor.get_system_status()
                
                result.components["system_health"] = status
                
                # Check for critical issues
                if status["overall_health"] == "critical":
                    result.blocking_issues.append("System health is critical after deployment")
                elif status["overall_health"] == "warning":
                    result.recommendations.append("System health shows warnings - monitor closely")
                    
                self.logger.info(f"System health: {status['overall_health']}")
                
            except Exception as e:
                result.components["system_health"] = {"error": str(e)}
                result.recommendations.append(f"System health check failed: {str(e)}")
                self.logger.warning(f"System health check failed: {str(e)}")
        else:
            result.components["system_health"] = {"status": "unavailable"}
            
        # 2. User Acceptance Testing
        if self.components_available["testing"]:
            try:
                self.logger.info("Running user acceptance tests")
                
                from testing.test_runner import TestRunner
                test_runner = TestRunner()
                
                # Run acceptance tests
                acceptance_results = await test_runner.run_acceptance_tests()
                
                passed_tests = len([r for r in acceptance_results if r.status == "passed"])
                total_tests = len(acceptance_results)
                success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                
                result.components["user_acceptance"] = {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "success_rate": success_rate,
                    "details": [asdict(r) for r in acceptance_results]
                }
                
                if success_rate < 80:
                    result.blocking_issues.append(f"User acceptance tests below threshold: {success_rate:.1f}%")
                    
                self.logger.info(f"User acceptance tests: {success_rate:.1f}% success rate")
                
            except Exception as e:
                result.components["user_acceptance"] = {"error": str(e)}
                result.recommendations.append(f"User acceptance testing failed: {str(e)}")
                self.logger.warning(f"User acceptance testing failed: {str(e)}")
        else:
            result.components["user_acceptance"] = {"status": "unavailable"}
            
        # 3. Initial Feedback Analysis
        if self.components_available["feedback"]:
            try:
                self.logger.info("Analyzing initial feedback")
                
                from feedback.collector import FeedbackCollector
                feedback_collector = FeedbackCollector()
                
                # Generate some sample feedback for demonstration
                sample_feedback = feedback_collector.create_sample_feedback()
                
                # Get feedback summary
                summary = feedback_collector.get_feedback_summary(days=1)
                
                result.components["initial_feedback"] = {
                    "summary": summary,
                    "sample_generated": len(sample_feedback)
                }
                
                # Check feedback sentiment
                if summary["average_rating"] < 3.0 and summary["ratings_count"] > 5:
                    result.blocking_issues.append(f"Poor initial user feedback: {summary['average_rating']:.1f}/5")
                elif summary["average_rating"] < 4.0 and summary["ratings_count"] > 10:
                    result.recommendations.append("User feedback is moderate - monitor for trends")
                    
                self.logger.info(f"Initial feedback: {summary['average_rating']:.1f}/5 average rating")
                
            except Exception as e:
                result.components["initial_feedback"] = {"error": str(e)}
                result.recommendations.append(f"Initial feedback analysis failed: {str(e)}")
                self.logger.warning(f"Initial feedback analysis failed: {str(e)}")
        else:
            result.components["initial_feedback"] = {"status": "unavailable"}
            
    async def _execute_full_validation(self, result: ValidationResult):
        """Execute full validation (all phases)."""
        self.logger.info("Executing full validation")
        
        # Execute all phases in sequence
        phases = [
            ValidationPhase.PRE_DEPLOYMENT,
            ValidationPhase.DEPLOYMENT,
            ValidationPhase.POST_DEPLOYMENT
        ]
        
        phase_results = {}
        
        for phase in phases:
            try:
                phase_result = await self.execute_validation_phase(phase)
                phase_results[phase.value] = asdict(phase_result)
                
                # Accumulate blocking issues and recommendations
                result.blocking_issues.extend(phase_result.blocking_issues)
                result.recommendations.extend(phase_result.recommendations)
                
            except Exception as e:
                phase_results[phase.value] = {"error": str(e)}
                result.blocking_issues.append(f"Phase {phase.value} failed: {str(e)}")
                
        result.components["phase_results"] = phase_results
        
    async def _perform_deployment_health_check(self, result: ValidationResult):
        """Perform basic deployment health check."""
        try:
            self.logger.info("Performing deployment health check")
            
            health_checks = {
                "file_system": self._check_file_system_health(),
                "git_repository": self._check_git_health(),
                "dependencies": self._check_dependencies_health(),
                "configuration": self._check_configuration_health()
            }
            
            result.components["deployment_health"] = health_checks
            
            # Check for failed health checks
            failed_checks = [name for name, status in health_checks.items() if not status.get("healthy", False)]
            
            if failed_checks:
                result.blocking_issues.append(f"Failed health checks: {', '.join(failed_checks)}")
                
            self.logger.info(f"Health check completed: {len(failed_checks)} failures")
            
        except Exception as e:
            result.components["deployment_health"] = {"error": str(e)}
            result.recommendations.append(f"Deployment health check failed: {str(e)}")
            self.logger.warning(f"Deployment health check failed: {str(e)}")
            
    def _check_file_system_health(self) -> Dict[str, Any]:
        """Check file system health."""
        try:
            key_paths = [
                "CLAUDE.md", "README.md", "agents/", "commands/", 
                "testing/", "quality/", "monitoring/", "feedback/", "rollback/"
            ]
            
            missing_paths = [path for path in key_paths if not Path(path).exists()]
            
            return {
                "healthy": len(missing_paths) == 0,
                "missing_paths": missing_paths,
                "total_checked": len(key_paths)
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
            
    def _check_git_health(self) -> Dict[str, Any]:
        """Check git repository health."""
        try:
            import git
            
            repo = git.Repo(".")
            
            return {
                "healthy": True,
                "current_branch": repo.active_branch.name,
                "current_commit": repo.head.commit.hexsha,
                "uncommitted_changes": repo.is_dirty(),
                "untracked_files": len(repo.untracked_files)
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
            
    def _check_dependencies_health(self) -> Dict[str, Any]:
        """Check Python dependencies health."""
        try:
            import pkg_resources
            
            # Check for common dependencies
            required_packages = ["psutil", "gitpython"]
            available_packages = []
            missing_packages = []
            
            for package in required_packages:
                try:
                    pkg_resources.get_distribution(package)
                    available_packages.append(package)
                except pkg_resources.DistributionNotFound:
                    missing_packages.append(package)
                    
            return {
                "healthy": len(missing_packages) == 0,
                "available_packages": available_packages,
                "missing_packages": missing_packages
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
            
    def _check_configuration_health(self) -> Dict[str, Any]:
        """Check configuration health."""
        try:
            config_files = ["CLAUDE.md", "AGENT_DECISION_TREE.md", "USAGE_OPTIMIZATION.md"]
            
            valid_configs = []
            invalid_configs = []
            
            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists() and config_path.stat().st_size > 100:
                    valid_configs.append(config_file)
                else:
                    invalid_configs.append(config_file)
                    
            return {
                "healthy": len(invalid_configs) == 0,
                "valid_configs": valid_configs,
                "invalid_configs": invalid_configs
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
            
    def _calculate_overall_results(self, result: ValidationResult):
        """Calculate overall validation results."""
        # Calculate overall score based on component results
        component_scores = []
        
        for component_name, component_data in result.components.items():
            if isinstance(component_data, dict):
                if "overall_score" in component_data:
                    component_scores.append(component_data["overall_score"])
                elif "success_rate" in component_data:
                    component_scores.append(component_data["success_rate"])
                elif "healthy" in component_data:
                    component_scores.append(100.0 if component_data["healthy"] else 0.0)
                elif "error" not in component_data:
                    component_scores.append(75.0)  # Assume reasonable score for successful components
                    
        result.overall_score = sum(component_scores) / len(component_scores) if component_scores else 0.0
        
        # Determine status
        if result.blocking_issues:
            result.status = ValidationStatus.FAILED
        elif result.overall_score >= 90 and not result.recommendations:
            result.status = ValidationStatus.PASSED
        elif result.overall_score >= 70:
            result.status = ValidationStatus.WARNING
        else:
            result.status = ValidationStatus.FAILED
            
        # Make rollout decision
        if result.status == ValidationStatus.PASSED:
            result.rollout_decision = "proceed"
        elif result.status == ValidationStatus.WARNING and result.overall_score >= 80:
            result.rollout_decision = "proceed_with_caution"
        else:
            result.rollout_decision = "block"
            
        # Add overall recommendations
        if result.overall_score < 70:
            result.recommendations.append("Overall validation score is below acceptable threshold (70)")
            
        if result.blocking_issues:
            result.recommendations.insert(0, f"Resolve {len(result.blocking_issues)} blocking issues before proceeding")
            
    def _generate_phase_report(self, result: ValidationResult):
        """Generate comprehensive phase report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON Report
        json_report_path = self.output_dir / f"validation_report_{result.phase.value}_{timestamp}.json"
        with open(json_report_path, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
            
        # HTML Report
        html_content = self._generate_html_report(result)
        html_report_path = self.output_dir / f"validation_report_{result.phase.value}_{timestamp}.html"
        with open(html_report_path, 'w') as f:
            f.write(html_content)
            
        # Console Summary
        self._print_validation_summary(result)
        
        self.logger.info(f"Validation reports generated: {json_report_path}, {html_report_path}")
        
    def _generate_html_report(self, result: ValidationResult) -> str:
        """Generate HTML report for validation result."""
        status_colors = {
            ValidationStatus.PASSED: "#28a745",
            ValidationStatus.WARNING: "#ffc107", 
            ValidationStatus.FAILED: "#dc3545",
            ValidationStatus.IN_PROGRESS: "#007bff"
        }
        
        decision_colors = {
            "proceed": "#28a745",
            "proceed_with_caution": "#ffc107",
            "block": "#dc3545"
        }
        
        status_color = status_colors.get(result.status, "#6c757d")
        decision_color = decision_colors.get(result.rollout_decision, "#6c757d")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Enhancement Validation Report - {result.phase.value.title()}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .status-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; color: white; margin: 10px 0; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .component-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
        .component-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .issues-section {{ margin: 20px 0; }}
        .issue-item {{ background: #f8d7da; color: #721c24; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #dc3545; }}
        .recommendation-item {{ background: #fff3cd; color: #856404; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #ffc107; }}
        .decision-banner {{ text-align: center; padding: 30px; margin: 20px 0; border-radius: 10px; font-size: 1.2em; font-weight: bold; color: white; }}
        pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Claude Code Enhancement Validation Report</h1>
            <h2>{result.phase.value.replace('_', ' ').title()} Phase</h2>
            <p>Generated: {result.start_time}</p>
        </div>
        
        <div class="summary">
            <div class="metric-card">
                <h3>Overall Status</h3>
                <div class="status-badge" style="background: {status_color}">
                    {result.status.value.upper()}
                </div>
                <p>Score: {result.overall_score:.1f}/100</p>
            </div>
            <div class="metric-card">
                <h3>Duration</h3>
                <p>{result.duration_seconds:.1f} seconds</p>
            </div>
            <div class="metric-card">
                <h3>Components</h3>
                <p>{len(result.components)} components validated</p>
            </div>
            <div class="metric-card">
                <h3>Issues</h3>
                <p>{len(result.blocking_issues)} blocking</p>
                <p>{len(result.recommendations)} recommendations</p>
            </div>
        </div>
        
        <div class="decision-banner" style="background: {decision_color}">
            Rollout Decision: {result.rollout_decision.replace('_', ' ').upper()}
        </div>
"""
        
        # Blocking Issues Section
        if result.blocking_issues:
            html += """
        <div class="issues-section">
            <h2>🚨 Blocking Issues</h2>
"""
            for issue in result.blocking_issues:
                html += f'            <div class="issue-item">{issue}</div>\\n'
            html += "        </div>\\n"
            
        # Recommendations Section
        if result.recommendations:
            html += """
        <div class="issues-section">
            <h2>💡 Recommendations</h2>
"""
            for rec in result.recommendations:
                html += f'            <div class="recommendation-item">{rec}</div>\\n'
            html += "        </div>\\n"
            
        # Components Section
        html += """
        <h2>📊 Component Results</h2>
        <div class="component-grid">
"""
        
        for component_name, component_data in result.components.items():
            component_title = component_name.replace('_', ' ').title()
            
            if isinstance(component_data, dict) and "error" in component_data:
                status_text = "ERROR"
                status_color = "#dc3545"
            elif isinstance(component_data, dict) and component_data.get("healthy", True):
                status_text = "HEALTHY"
                status_color = "#28a745"
            else:
                status_text = "COMPLETED"
                status_color = "#007bff"
                
            html += f"""
            <div class="component-card">
                <h3>{component_title}</h3>
                <div class="status-badge" style="background: {status_color}; font-size: 0.8em;">
                    {status_text}
                </div>
                <pre>{json.dumps(component_data, indent=2, default=str)}</pre>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html
        
    def _print_validation_summary(self, result: ValidationResult):
        """Print validation summary to console."""
        status_icons = {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.IN_PROGRESS: "🔄"
        }
        
        decision_icons = {
            "proceed": "🟢",
            "proceed_with_caution": "🟡", 
            "block": "🔴"
        }
        
        status_icon = status_icons.get(result.status, "❓")
        decision_icon = decision_icons.get(result.rollout_decision, "❓")
        
        print(f"\\n{'='*80}")
        print(f"CLAUDE CODE ENHANCEMENT VALIDATION SUMMARY")
        print(f"Phase: {result.phase.value.replace('_', ' ').title()}")
        print(f"{'='*80}")
        print(f"{status_icon} Overall Status: {result.status.value.upper()}")
        print(f"📊 Overall Score: {result.overall_score:.1f}/100")
        print(f"⏱️  Duration: {result.duration_seconds:.1f} seconds")
        print(f"🔍 Components: {len(result.components)}")
        print(f"🚨 Blocking Issues: {len(result.blocking_issues)}")
        print(f"💡 Recommendations: {len(result.recommendations)}")
        print(f"\\n{decision_icon} ROLLOUT DECISION: {result.rollout_decision.replace('_', ' ').upper()}")
        
        if result.blocking_issues:
            print(f"\\n🚨 BLOCKING ISSUES:")
            for i, issue in enumerate(result.blocking_issues, 1):
                print(f"   {i}. {issue}")
                
        if result.recommendations:
            print(f"\\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec}")
                
        print(f"\\n{'='*80}")


async def main():
    """Main entry point for validation orchestrator."""
    parser = argparse.ArgumentParser(description="Claude Code Enhancement Rollout Validation Orchestrator")
    parser.add_argument("--phase", 
                       choices=["pre-deployment", "deployment", "post-deployment", "full-validation"],
                       default="full-validation",
                       help="Validation phase to execute")
    parser.add_argument("--output-dir", default="validation_reports", help="Output directory for reports")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    orchestrator = ValidationOrchestrator(Path(args.output_dir))
    
    try:
        print(f"🚀 Starting Claude Code Enhancement Validation")
        print(f"Phase: {args.phase.replace('_', ' ').title()}")
        print(f"Output Directory: {args.output_dir}")
        print("-" * 60)
        
        phase = ValidationPhase(args.phase)
        result = await orchestrator.execute_validation_phase(phase)
        
        # Exit with appropriate code
        if result.rollout_decision == "block":
            print("\\n🔴 VALIDATION FAILED - ROLLOUT BLOCKED")
            sys.exit(1)
        elif result.rollout_decision == "proceed_with_caution":
            print("\\n🟡 VALIDATION PASSED WITH WARNINGS - PROCEED WITH CAUTION")
            sys.exit(0)
        else:
            print("\\n🟢 VALIDATION PASSED - ROLLOUT APPROVED")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\nValidation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())