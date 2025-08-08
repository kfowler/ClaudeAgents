# Claude Code Workflow Engine

A comprehensive workflow automation system that orchestrates multiple AI agents for common development scenarios. The engine provides template-based workflows with dependency management, parallel execution, progress tracking, error handling, and rollback capabilities.

## 🚀 Features

### Core Capabilities
- **Multi-Agent Orchestration**: Coordinate multiple specialized agents in complex workflows
- **Dependency Management**: Automatic task dependency resolution and execution ordering
- **Parallel Execution**: Run independent tasks in parallel for optimal performance
- **Progress Tracking**: Real-time monitoring of workflow execution with detailed status
- **Error Handling**: Advanced error recovery with retry, rollback, and manual intervention strategies
- **Hooks System**: Extensible hooks for customization at various workflow lifecycle points
- **Analytics Integration**: Comprehensive analytics for workflow optimization and insights

### Pre-built Workflow Templates
1. **New Feature Pipeline**: Product strategy → Architecture → Implementation → Testing → Security → Deployment
2. **Production Readiness**: Multi-agent parallel validation for security, accessibility, performance, and quality
3. **Code Quality Gate**: Comprehensive validation before merge (static analysis, security, testing, architecture)
4. **AI Integration Workflow**: Specialized workflow for AI/ML feature development and deployment
5. **Legacy Modernization**: End-to-end legacy system modernization with risk management

### Management Interfaces
- **CLI Interface**: Command-line tool for workflow management and monitoring
- **Web Dashboard**: Real-time web interface for workflow visualization and control
- **REST API**: Programmatic access for integration with existing systems

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git (for version control hooks)
- Docker (optional, for containerized deployments)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd ClaudeAgents/workflows

# Install Python dependencies
pip install -r requirements.txt

# Initialize the workflow engine
python -m workflows.cli --help
```

### Dependencies
```text
asyncio>=3.8
pyyaml>=5.4
flask>=2.0
rich>=10.0
tabulate>=0.8
asyncpg>=0.25  # Optional, for PostgreSQL analytics
aioredis>=2.0  # Optional, for Redis caching
requests>=2.25  # For webhook notifications
```

## 🏃 Quick Start

### 1. List Available Templates
```bash
python -m workflows.cli list
```

### 2. Start a Workflow
```bash
# Start the new feature pipeline
python -m workflows.cli start new-feature-pipeline

# Start with custom parameters
python -m workflows.cli start production-readiness \
  --parameters '{"security_level": "high", "compliance_requirements": ["SOC2", "GDPR"]}' \
  --context '{"project_path": "/path/to/project"}'
```

### 3. Monitor Execution
```bash
# List active executions
python -m workflows.cli executions

# Monitor specific execution with live updates
python -m workflows.cli monitor <execution-id> --live
```

### 4. Launch Web Dashboard
```bash
# Start the web dashboard
python -m workflows.dashboard

# Access at http://localhost:8080
```

## 🔧 Configuration

### Workflow Templates
Templates are defined in YAML format and stored in the `workflow_templates/` directory:

```yaml
id: "my-custom-workflow"
name: "My Custom Workflow"
description: "Description of the workflow"
version: "1.0"

global_parameters:
  timeout_default: 600
  retry_count: 3

tasks:
  - id: "analyze_code"
    name: "Code Analysis"
    agent: "code-architect"
    description: "Analyze code quality and architecture"
    parameters:
      analysis_scope: "comprehensive"
    execution_mode: "sequential"
    timeout: 900
    dependencies: []
    
  - id: "security_scan"
    name: "Security Scan"
    agent: "security-audit-specialist"
    dependencies: ["analyze_code"]
    execution_mode: "parallel"
    conditions:
      global_context:
        key: "security_required"
        value: true
```

### Error Handling Rules
Configure custom error handling strategies:

```python
from workflows.error_handling import error_handler, RecoveryAction, RecoveryStrategy

# Register custom error handling rule
error_handler.register_error_rule(
    "custom_error_pattern",
    RecoveryAction(
        strategy=RecoveryStrategy.RETRY,
        description="Custom retry strategy",
        parameters={"retry_delay": 10, "max_retries": 3}
    )
)
```

### Custom Hooks
Create custom hooks for workflow customization:

```python
from workflows.hooks import hook_manager, HookContext

async def my_custom_hook(context: HookContext):
    """Custom hook implementation"""
    print(f"Executing custom hook for workflow {context.execution.id}")
    # Custom logic here

# Register the hook
hook_manager.register_hook("my_custom_hook", my_custom_hook)
```

## 📋 Workflow Templates Deep Dive

### New Feature Pipeline
**Purpose**: Complete feature development from strategy to deployment
**Duration**: ~60 minutes
**Agents**: product-strategist, full-stack-architect, qa-test-engineer, security-audit-specialist, devops-engineer

**Flow**:
1. Product strategy analysis and market validation
2. Technical architecture design
3. Security review and threat modeling
4. Test strategy development
5. Implementation with quality checks
6. Comprehensive testing suite
7. Accessibility compliance validation
8. Performance optimization
9. Final security scan
10. Production deployment preparation

### Production Readiness
**Purpose**: Multi-agent parallel validation for production deployment
**Duration**: ~40 minutes
**Agents**: security-audit-specialist, accessibility-expert, systems-engineer, qa-test-engineer, devops-engineer, code-architect

**Parallel Validations**:
- Comprehensive security audit
- Accessibility compliance (WCAG 2.1 AA)
- Performance benchmarking and load testing
- Quality assurance and regression testing
- Infrastructure and DevOps readiness
- Code quality and architecture review

### Code Quality Gate
**Purpose**: Comprehensive pre-merge validation
**Duration**: ~30 minutes
**Agents**: code-architect, security-audit-specialist, qa-test-engineer, systems-engineer

**Validations**:
- Static code analysis and linting
- Security vulnerability scanning
- Test suite validation and coverage analysis
- Architecture compliance checking
- Documentation quality assessment
- Performance impact analysis
- Dependency security audit

### AI Integration Workflow
**Purpose**: End-to-end AI/ML feature development
**Duration**: ~80 minutes
**Agents**: ai-ml-engineer, data-engineer, systems-engineer, qa-test-engineer, security-audit-specialist, devops-engineer

**Specialized Flow**:
- AI requirements analysis and model architecture design
- Data pipeline setup and feature engineering
- Model development, training, and validation
- Comprehensive AI model testing (accuracy, bias, robustness)
- System integration with error handling and monitoring
- AI security assessment and governance compliance
- Performance optimization and deployment automation

### Legacy Modernization
**Purpose**: Comprehensive legacy system modernization
**Duration**: ~120 minutes
**Agents**: legacy-specialist, code-architect, data-engineer, security-audit-specialist, qa-test-engineer, devops-engineer, systems-engineer

**Modernization Process**:
- Legacy system assessment and dependency mapping
- Modernization strategy and target architecture design
- Data migration planning and ETL pipeline design
- Security modernization and compliance review
- Pilot implementation and validation
- Performance benchmarking and optimization
- Integration testing between legacy and modern components
- User acceptance testing and training
- Production deployment preparation
- Compliance validation and cutover planning

## 🔍 Monitoring and Analytics

### Real-time Monitoring
- Workflow execution status and progress
- Individual task status and duration
- Resource utilization and performance metrics
- Error rates and recovery actions

### Analytics Insights
- Workflow success rates and performance trends
- Agent effectiveness and optimization opportunities
- Common failure patterns and improvement suggestions
- Cost and resource utilization analysis

### Dashboard Features
- Live workflow execution monitoring
- Historical performance analysis
- Agent performance metrics
- Error and recovery tracking
- Workflow template management

## 🛠 Advanced Features

### Error Handling and Recovery
The system provides multiple recovery strategies:

- **Retry**: Automatic retry with exponential backoff
- **Skip**: Skip failed tasks and continue execution
- **Rollback**: Revert to previous checkpoint state
- **Fallback**: Execute alternative task or workflow
- **Manual Intervention**: Pause for human review
- **Fail Fast**: Immediate failure for critical errors

### Checkpoints and Rollback
- Automatic checkpoint creation at key workflow milestones
- File snapshots and git state preservation
- Configurable rollback scopes (task, phase, workflow, system)
- Database backup and restore capabilities

### Hooks System
Extensible hooks for customization:
- `pre_workflow` / `post_workflow`: Workflow lifecycle hooks
- `pre_task` / `post_task`: Task-level hooks
- `on_error` / `on_success`: Error handling hooks
- `on_retry` / `on_cancel`: Recovery action hooks

### Custom Agent Integration
Easy integration with existing or custom agents:

```python
from workflows.agent_integration import ClaudeCodeAgentInterface

interface = ClaudeCodeAgentInterface()

# Register custom agent
interface.register_custom_agent("my-agent", MyAgentClass())

# Validate agent chains
validation_errors = interface.validate_agent_chain([
    "my-agent", "code-architect", "qa-test-engineer"
])
```

## 📚 API Reference

### CLI Commands
```bash
# Template Management
workflow list                           # List available templates
workflow show <template-id>             # Show template details
workflow validate <template-file>       # Validate template
workflow scaffold <name> <output>       # Create template scaffold

# Execution Management
workflow start <template-id>            # Start workflow
workflow monitor <execution-id>         # Monitor execution
workflow executions                     # List active executions
workflow cancel <execution-id>          # Cancel execution
```

### REST API Endpoints
```
GET  /api/status                        # System status
GET  /api/templates                     # List templates
GET  /api/executions                    # List executions
GET  /api/execution/<id>                # Execution details
POST /api/workflow/start                # Start workflow
POST /api/execution/<id>/cancel         # Cancel execution
GET  /api/analytics/summary             # Analytics summary
GET  /api/agents                        # Available agents
```

### Python API
```python
from workflows.engine import WorkflowEngine

# Initialize engine
engine = WorkflowEngine()
await engine.start()

# Start workflow
execution = await engine.start_workflow(
    "new-feature-pipeline",
    parameters={"feature_name": "user-authentication"},
    context={"project_path": "/path/to/project"}
)

# Monitor progress
status = engine.get_execution_status(execution.id)
print(f"Status: {status.status}, Progress: {status.completed_tasks}/{status.total_tasks}")
```

## 🔒 Security Considerations

- **Input Validation**: All user inputs are validated and sanitized
- **Secure Execution**: Workflows run in isolated execution contexts
- **Access Control**: Role-based access control for workflow management
- **Audit Logging**: Comprehensive audit trail of all workflow operations
- **Secret Management**: Secure handling of sensitive parameters and credentials

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY workflows/ /app/workflows/
COPY requirements.txt /app/

RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "-m", "workflows.dashboard"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-engine
  template:
    metadata:
      labels:
        app: workflow-engine
    spec:
      containers:
      - name: workflow-engine
        image: workflow-engine:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: workflow-secrets
              key: database-url
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
python -m flake8 workflows/
python -m black workflows/
```

### Creating Custom Templates
1. Create YAML template file in `workflow_templates/`
2. Validate template: `workflow validate my-template.yaml`
3. Test template: `workflow start my-template-id`
4. Submit pull request with template and tests

### Adding New Agents
1. Create agent in `agents/` directory following existing patterns
2. Update `agent_integration.py` to include new agent
3. Add agent to relevant workflow templates
4. Update documentation and examples

## 📞 Support and Community

- **Documentation**: Complete API and usage documentation
- **Examples**: Extensive examples and tutorials
- **Issue Tracking**: GitHub issues for bug reports and feature requests
- **Community**: Discord/Slack community for discussions and support

## 📄 License

MIT License - see LICENSE file for details.

## 🏆 Acknowledgments

Built on top of the Claude Code agent ecosystem, leveraging the power of specialized AI agents for comprehensive development workflow automation.

---

**Ready to automate your development workflows? Get started with the Claude Code Workflow Engine today!**