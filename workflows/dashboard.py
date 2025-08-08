"""
Workflow Status Dashboard

Web-based dashboard for monitoring workflow executions, viewing analytics,
and managing workflow templates. Built with Flask for simplicity and ease of deployment.
"""

import asyncio
import json
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import logging

try:
    from engine import WorkflowEngine, WorkflowStatus, TaskStatus
    from analytics_integration import WorkflowAnalyticsCollector
    from agent_integration import ClaudeCodeAgentInterface
except ImportError as e:
    logging.error(f"Failed to import workflow components: {e}")
    raise

logger = logging.getLogger(__name__)

class WorkflowDashboard:
    """Web dashboard for workflow monitoring and management"""
    
    def __init__(self, workflow_engine: WorkflowEngine, port: int = 8080):
        self.engine = workflow_engine
        self.analytics = WorkflowAnalyticsCollector()
        self.agent_interface = ClaudeCodeAgentInterface()
        self.port = port
        
        # Flask app setup
        self.app = Flask(__name__)
        self.app.secret_key = 'workflow-dashboard-secret-key'
        
        # Background thread for async operations
        self.loop = None
        self.thread = None
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for dashboard status"""
            try:
                templates = self.engine.get_templates()
                active_executions = self.engine.get_active_executions()
                
                return jsonify({
                    'status': 'running',
                    'templates_count': len(templates),
                    'active_executions_count': len(active_executions),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/api/templates')
        def api_templates():
            """Get all available workflow templates"""
            try:
                templates = self.engine.get_templates()
                template_data = []
                
                for template in templates:
                    template_data.append({
                        'id': template.id,
                        'name': template.name,
                        'description': template.description,
                        'version': template.version,
                        'author': template.author,
                        'tasks_count': len(template.tasks),
                        'estimated_duration': template.metadata.get('estimated_duration'),
                        'complexity': template.metadata.get('complexity'),
                        'category': template.metadata.get('category')
                    })
                
                return jsonify(template_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/executions')
        def api_executions():
            """Get all active workflow executions"""
            try:
                executions = self.engine.get_active_executions()
                execution_data = []
                
                for execution in executions:
                    progress = 0
                    if execution.total_tasks > 0:
                        progress = (execution.completed_tasks / execution.total_tasks) * 100
                    
                    duration = None
                    if execution.start_time:
                        end_time = execution.end_time or datetime.now(timezone.utc)
                        duration = int((end_time - execution.start_time).total_seconds())
                    
                    execution_data.append({
                        'id': execution.id,
                        'template_id': execution.template_id,
                        'template_name': execution.template.name if execution.template else 'Unknown',
                        'status': execution.status.value,
                        'progress': round(progress, 1),
                        'current_phase': execution.current_phase,
                        'total_tasks': execution.total_tasks,
                        'completed_tasks': execution.completed_tasks,
                        'failed_tasks': execution.failed_tasks,
                        'start_time': execution.start_time.isoformat() if execution.start_time else None,
                        'duration_seconds': duration
                    })
                
                return jsonify(execution_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/execution/<execution_id>')
        def api_execution_details(execution_id):
            """Get detailed information about a specific execution"""
            try:
                execution = self.engine.get_execution_status(execution_id)
                
                if not execution:
                    return jsonify({'error': 'Execution not found'}), 404
                
                task_details = []
                if execution.template:
                    for task in execution.template.tasks:
                        duration = None
                        if task.start_time and task.end_time:
                            duration = (task.end_time - task.start_time).total_seconds()
                        elif task.start_time:
                            duration = (datetime.now(timezone.utc) - task.start_time).total_seconds()
                        
                        task_details.append({
                            'id': task.id,
                            'name': task.name,
                            'agent': task.agent,
                            'status': task.status.value,
                            'dependencies': task.dependencies,
                            'execution_mode': task.execution_mode.value,
                            'start_time': task.start_time.isoformat() if task.start_time else None,
                            'end_time': task.end_time.isoformat() if task.end_time else None,
                            'duration_seconds': duration,
                            'retry_count': task.retry_count,
                            'max_retries': task.max_retries,
                            'error': task.result.error if task.result and hasattr(task.result, 'error') else None
                        })
                
                return jsonify({
                    'id': execution.id,
                    'template_id': execution.template_id,
                    'template_name': execution.template.name if execution.template else 'Unknown',
                    'status': execution.status.value,
                    'current_phase': execution.current_phase,
                    'start_time': execution.start_time.isoformat() if execution.start_time else None,
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'total_tasks': execution.total_tasks,
                    'completed_tasks': execution.completed_tasks,
                    'failed_tasks': execution.failed_tasks,
                    'global_context': execution.global_context,
                    'error_log': execution.error_log,
                    'tasks': task_details
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/execution/<execution_id>/cancel', methods=['POST'])
        def api_cancel_execution(execution_id):
            """Cancel a workflow execution"""
            try:
                if self.loop and not self.loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self.engine.cancel_workflow(execution_id), 
                        self.loop
                    )
                    success = future.result(timeout=10)
                    
                    if success:
                        return jsonify({'message': 'Execution cancelled successfully'})
                    else:
                        return jsonify({'error': 'Failed to cancel execution'}), 400
                else:
                    return jsonify({'error': 'Workflow engine not running'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/workflow/start', methods=['POST'])
        def api_start_workflow():
            """Start a new workflow execution"""
            try:
                data = request.get_json()
                template_id = data.get('template_id')
                parameters = data.get('parameters', {})
                context = data.get('context', {})
                
                if not template_id:
                    return jsonify({'error': 'template_id is required'}), 400
                
                if self.loop and not self.loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self.engine.start_workflow(template_id, parameters, context),
                        self.loop
                    )
                    execution = future.result(timeout=30)
                    
                    return jsonify({
                        'execution_id': execution.id,
                        'message': 'Workflow started successfully'
                    })
                else:
                    return jsonify({'error': 'Workflow engine not running'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics/summary')
        def api_analytics_summary():
            """Get workflow analytics summary"""
            try:
                insights = self.analytics.get_workflow_insights()
                return jsonify(insights)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/agents')
        def api_agents():
            """Get information about available agents"""
            try:
                agents = self.agent_interface.get_available_agents()
                agent_data = []
                
                for agent in agents:
                    agent_data.append({
                        'name': agent.name,
                        'description': agent.description,
                        'expertise_areas': agent.expertise_areas,
                        'estimated_duration': agent.estimated_duration,
                        'input_parameters': agent.input_parameters,
                        'output_artifacts': agent.output_artifacts
                    })
                
                return jsonify(agent_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def start_background_loop(self):
        """Start the background asyncio loop in a separate thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
        # Wait a bit for the loop to start
        import time
        time.sleep(0.1)
    
    def run(self, debug: bool = False):
        """Run the dashboard server"""
        self.start_background_loop()
        
        # Initialize the workflow engine in the background loop
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.engine.start(), self.loop)
        
        logger.info(f"Starting workflow dashboard on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug, threaded=True)
    
    def stop(self):
        """Stop the dashboard server"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.engine.shutdown(), self.loop)
            self.loop.call_soon_threadsafe(self.loop.stop)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code Workflow Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { font-size: 1.8rem; font-weight: 600; }
        .header .status { opacity: 0.8; font-size: 0.9rem; margin-top: 0.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }
        .card-header { padding: 1.5rem; border-bottom: 1px solid #eee; background: #f8f9fa; }
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; }
        .card-content { padding: 1.5rem; }
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .stat { text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 6px; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #3498db; }
        .stat-label { font-size: 0.9rem; opacity: 0.7; margin-top: 0.5rem; }
        .table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #eee; }
        .table th { background: #f8f9fa; font-weight: 600; }
        .status { padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem; font-weight: 500; }
        .status-running { background: #3498db; color: white; }
        .status-completed { background: #27ae60; color: white; }
        .status-failed { background: #e74c3c; color: white; }
        .status-pending { background: #f39c12; color: white; }
        .progress-bar { width: 100%; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
        .progress-fill { height: 100%; background: #3498db; transition: width 0.3s ease; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-danger:hover { background: #c0392b; }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .refresh-indicator { opacity: 0; transition: opacity 0.2s; }
        .refresh-indicator.active { opacity: 1; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); }
        .modal-content { background: white; margin: 5% auto; padding: 2rem; width: 80%; max-width: 600px; border-radius: 8px; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Claude Code Workflow Dashboard</h1>
        <div class="status" id="systemStatus">Initializing...</div>
    </div>

    <div class="container">
        <div class="stat-grid">
            <div class="stat">
                <div class="stat-value" id="templatesCount">-</div>
                <div class="stat-label">Templates</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="activeExecutionsCount">-</div>
                <div class="stat-label">Active Executions</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="successRate">-</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="avgDuration">-</div>
                <div class="stat-label">Avg Duration</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Active Executions</div>
                    <span class="refresh-indicator" id="refreshIndicator">
                        <span class="spinner"></span> Refreshing...
                    </span>
                </div>
                <div class="card-content">
                    <table class="table" id="executionsTable">
                        <thead>
                            <tr>
                                <th>Template</th>
                                <th>Status</th>
                                <th>Progress</th>
                                <th>Duration</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                    <div id="noExecutions" style="text-align: center; color: #666; padding: 2rem; display: none;">
                        No active executions
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Workflow Templates</div>
                    <button class="btn btn-primary" onclick="showStartWorkflowModal()">Start Workflow</button>
                </div>
                <div class="card-content">
                    <table class="table" id="templatesTable">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Tasks</th>
                                <th>Complexity</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Start Workflow Modal -->
    <div id="startWorkflowModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="hideStartWorkflowModal()">&times;</span>
            <h2>Start Workflow</h2>
            <form id="startWorkflowForm">
                <div class="form-group">
                    <label for="templateSelect">Template:</label>
                    <select id="templateSelect" required></select>
                </div>
                <div class="form-group">
                    <label for="workflowParameters">Parameters (JSON):</label>
                    <textarea id="workflowParameters" rows="4" placeholder='{"key": "value"}'>{}</textarea>
                </div>
                <div class="form-group">
                    <label for="workflowContext">Context (JSON):</label>
                    <textarea id="workflowContext" rows="4" placeholder='{"project_path": "."}'>{}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Start Workflow</button>
            </form>
        </div>
    </div>

    <script>
        // Dashboard state
        let templates = [];
        let executions = [];
        let refreshInterval;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            refreshInterval = setInterval(refreshData, 5000); // Refresh every 5 seconds
        });

        async function refreshData() {
            const indicator = document.getElementById('refreshIndicator');
            indicator.classList.add('active');

            try {
                await Promise.all([
                    refreshSystemStatus(),
                    refreshTemplates(),
                    refreshExecutions(),
                    refreshAnalytics()
                ]);
            } catch (error) {
                console.error('Error refreshing data:', error);
            } finally {
                indicator.classList.remove('active');
            }
        }

        async function refreshSystemStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('systemStatus').textContent = 
                    `System ${data.status} - ${data.templates_count} templates, ${data.active_executions_count} active executions`;
            } catch (error) {
                document.getElementById('systemStatus').textContent = 'System error';
            }
        }

        async function refreshTemplates() {
            try {
                const response = await fetch('/api/templates');
                templates = await response.json();
                
                document.getElementById('templatesCount').textContent = templates.length;
                
                const tbody = document.querySelector('#templatesTable tbody');
                tbody.innerHTML = '';
                
                templates.forEach(template => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><strong>${template.name}</strong><br><small>${template.description?.substring(0, 50)}...</small></td>
                        <td><span class="badge">${template.category || 'General'}</span></td>
                        <td>${template.tasks_count}</td>
                        <td>${template.complexity || 'Medium'}</td>
                        <td><button class="btn btn-primary btn-sm" onclick="startWorkflow('${template.id}')">Start</button></td>
                    `;
                    tbody.appendChild(row);
                });

                // Update template selector in modal
                const selector = document.getElementById('templateSelect');
                selector.innerHTML = '';
                templates.forEach(template => {
                    const option = document.createElement('option');
                    option.value = template.id;
                    option.textContent = template.name;
                    selector.appendChild(option);
                });
            } catch (error) {
                console.error('Error refreshing templates:', error);
            }
        }

        async function refreshExecutions() {
            try {
                const response = await fetch('/api/executions');
                executions = await response.json();
                
                document.getElementById('activeExecutionsCount').textContent = executions.length;
                
                const tbody = document.querySelector('#executionsTable tbody');
                const noExecutions = document.getElementById('noExecutions');
                
                tbody.innerHTML = '';
                
                if (executions.length === 0) {
                    noExecutions.style.display = 'block';
                } else {
                    noExecutions.style.display = 'none';
                    
                    executions.forEach(execution => {
                        const row = document.createElement('tr');
                        
                        const statusClass = `status-${execution.status.replace('_', '-')}`;
                        const duration = execution.duration_seconds ? formatDuration(execution.duration_seconds) : '-';
                        
                        row.innerHTML = `
                            <td><strong>${execution.template_name}</strong><br><small>${execution.current_phase}</small></td>
                            <td><span class="status ${statusClass}">${execution.status}</span></td>
                            <td>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${execution.progress}%"></div>
                                </div>
                                <small>${execution.completed_tasks}/${execution.total_tasks} (${execution.progress}%)</small>
                            </td>
                            <td>${duration}</td>
                            <td>
                                <button class="btn btn-sm" onclick="viewExecution('${execution.id}')">View</button>
                                ${execution.status === 'running' ? `<button class="btn btn-danger btn-sm" onclick="cancelExecution('${execution.id}')">Cancel</button>` : ''}
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                }
            } catch (error) {
                console.error('Error refreshing executions:', error);
            }
        }

        async function refreshAnalytics() {
            try {
                const response = await fetch('/api/analytics/summary');
                const data = await response.json();
                
                if (data.summary) {
                    document.getElementById('successRate').textContent = 
                        `${Math.round(data.summary.success_rate * 100)}%`;
                    document.getElementById('avgDuration').textContent = 
                        data.summary.average_duration_seconds ? 
                        formatDuration(data.summary.average_duration_seconds) : '-';
                }
            } catch (error) {
                console.error('Error refreshing analytics:', error);
            }
        }

        function formatDuration(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            } else {
                return `${secs}s`;
            }
        }

        function showStartWorkflowModal() {
            document.getElementById('startWorkflowModal').style.display = 'block';
        }

        function hideStartWorkflowModal() {
            document.getElementById('startWorkflowModal').style.display = 'none';
        }

        async function startWorkflow(templateId) {
            if (templateId) {
                document.getElementById('templateSelect').value = templateId;
            }
            showStartWorkflowModal();
        }

        document.getElementById('startWorkflowForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const templateId = document.getElementById('templateSelect').value;
            const parameters = document.getElementById('workflowParameters').value;
            const context = document.getElementById('workflowContext').value;
            
            try {
                const response = await fetch('/api/workflow/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        template_id: templateId,
                        parameters: JSON.parse(parameters || '{}'),
                        context: JSON.parse(context || '{}')
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`Workflow started successfully! Execution ID: ${result.execution_id}`);
                    hideStartWorkflowModal();
                    refreshData();
                } else {
                    alert(`Error starting workflow: ${result.error}`);
                }
            } catch (error) {
                alert(`Error starting workflow: ${error.message}`);
            }
        });

        async function cancelExecution(executionId) {
            if (confirm('Are you sure you want to cancel this execution?')) {
                try {
                    const response = await fetch(`/api/execution/${executionId}/cancel`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        alert('Execution cancelled successfully');
                        refreshData();
                    } else {
                        const result = await response.json();
                        alert(`Error cancelling execution: ${result.error}`);
                    }
                } catch (error) {
                    alert(`Error cancelling execution: ${error.message}`);
                }
            }
        }

        function viewExecution(executionId) {
            // Open detailed view in new window or modal
            window.open(`/execution/${executionId}`, '_blank');
        }

        // Handle modal clicks
        window.onclick = function(event) {
            const modal = document.getElementById('startWorkflowModal');
            if (event.target === modal) {
                hideStartWorkflowModal();
            }
        };
    </script>
</body>
</html>
"""

def create_dashboard(workflow_engine: WorkflowEngine = None, port: int = 8080) -> WorkflowDashboard:
    """Create and return a workflow dashboard instance"""
    if not workflow_engine:
        workflow_engine = WorkflowEngine()
    
    return WorkflowDashboard(workflow_engine, port)

if __name__ == "__main__":
    # Run dashboard standalone
    from engine import WorkflowEngine
    
    engine = WorkflowEngine()
    dashboard = create_dashboard(engine, port=8080)
    
    try:
        dashboard.run(debug=True)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
        dashboard.stop()