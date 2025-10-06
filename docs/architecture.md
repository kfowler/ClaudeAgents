# System Architecture

## Overview

The Claude Code Agent System is a documentation-based ecosystem of specialized AI agents that work individually or in coordination to deliver production-ready software solutions. This architecture document describes the system design, component interactions, and key patterns.

## Core Components

### 1. Agent Definitions (`agents/`)

Each agent is defined in a Markdown file with YAML frontmatter:

```yaml
---
name: agent-name
description: "Brief description of agent's expertise and when to use it"
color: blue
---
```

**Key Characteristics:**
- **Declarative**: Agents are defined through documentation, not code
- **Self-contained**: Each agent includes full context about its responsibilities
- **Validated**: All agents pass through automated validation
- **Version controlled**: Changes tracked through git

**Agent Structure:**
1. **Frontmatter**: Metadata (name, description, color)
2. **Manifesto Commitment**: Professional standards and quality promises
3. **Implementation Principles**: How the agent operates
4. **Responsibilities**: Specific tasks and deliverables
5. **Technical Details**: Technologies, standards, patterns
6. **Agent Coordination Protocol (ACP)**: Inter-agent communication patterns

### 2. Command System (`commands/`)

Pre-defined workflows that orchestrate multiple agents:

```
commands/
├── development/     # Code review, debugging, refactoring
├── quality/         # Testing, security, performance audits
├── deployment/      # Infrastructure, deployment prep
├── specialized/     # Language/framework-specific workflows
└── workflows/       # Multi-agent orchestration patterns
```

**Command Characteristics:**
- **Multi-phase**: Break complex workflows into logical phases
- **Agent orchestration**: Specify which agents handle each phase
- **Sequential or parallel**: Can run agents in sequence or parallel
- **Domain-specific**: Tailored to specific development tasks

### 3. Validation System (`tools/`)

Ensures quality and consistency across all agents:

**Components:**
- `validate_agents.py`: Validates agent file structure and metadata
- `requirements.txt`: Production dependencies (PyYAML)
- `requirements-dev.txt`: Development dependencies (pytest)

**Validation Rules:**
- Required fields: name, description
- Optional fields: color
- Name must match filename
- Description length: 50-500 characters
- Content body must exist and be substantial
- YAML must parse correctly

### 4. Testing Framework (`tests/`)

Integration tests ensure system integrity:

**Test Coverage:**
- Agent file parsing
- Frontmatter field validation
- Name/filename consistency
- No duplicate agent names
- Agent references in commands are valid
- Validator error tracking accuracy

### 5. CI/CD Pipeline (`.github/workflows/`)

Automated quality gates on every push:

**GitHub Actions Workflow:**
1. Install Python 3.11
2. Install dependencies (production + dev)
3. Run agent validation
4. Run integration tests
5. Report results

## Architecture Patterns

### Agent Selection

Agents are selected based on:
1. **Keywords**: Technology mentions (React, Python, security, etc.)
2. **Task Type**: Development, testing, deployment, analysis
3. **Domain**: Web, mobile, AI/ML, infrastructure, etc.
4. **Complexity**: Single agent vs multi-agent orchestration

**Selection Tiers:**
- **Tier 1 (Core)**: Always visible, handle common tasks
- **Tier 2 (Context)**: Triggered by project characteristics
- **Tier 3 (Specialist)**: On-request for specialized needs

### Multi-Agent Coordination

Complex tasks use multiple agents in sequence or parallel:

**Sequential Pattern:**
```
product-strategist → project-orchestrator → specialized agents
```

**Parallel Pattern:**
```
security-audit-specialist
qa-test-engineer           } → Final review
accessibility-expert
```

**Agent Coordination Protocol (ACP):**
- **Agent-to-Agent**: Compressed JSON for efficiency
- **Agent-to-Human**: Natural language for clarity
- Structured status updates with metrics
- Clear handoff between agents

### Quality Enforcement

**Anti-Mock Principles:**
- No mock systems in production code
- All claims must be verifiable
- Connect to real systems, APIs, databases
- Honest failure reporting

**Validation Layers:**
1. **File Structure**: YAML frontmatter validation
2. **Naming Consistency**: Name matches filename
3. **Reference Integrity**: All agent references valid
4. **Content Quality**: Substantial, documented implementations
5. **CI/CD Gates**: Automated validation on every change

## Data Flow

### Agent Invocation Flow

```
User Request
    ↓
Agent Selection (keyword/context matching)
    ↓
Agent Activation (load agent definition)
    ↓
Task Execution (follow agent's implementation principles)
    ↓
Deliverable Production (tests, code, documentation)
    ↓
Quality Validation (verify against agent's standards)
    ↓
User Delivery
```

### Multi-Agent Orchestration Flow

```
Complex Request
    ↓
project-orchestrator (decompose into tasks)
    ↓
Task Assignment (assign to specialist agents)
    ↓
Parallel/Sequential Execution
    ↓
Integration (combine deliverables)
    ↓
Quality Gates (security, testing, accessibility)
    ↓
Production-Ready Deliverable
```

## Component Interactions

### Agent ↔ Command

- Commands specify which agents to use
- Agents provide capabilities commands orchestrate
- Commands define workflow, agents provide implementation

### Agent ↔ Validator

- Validator ensures agent structure correctness
- Agents must pass validation to be usable
- Template provides structure guidance

### Agent ↔ Tests

- Tests verify agent references are valid
- Tests ensure no duplicates or broken links
- Tests validate agent file structure

### Command ↔ Tests

- Tests verify command agent references
- Tests ensure commands reference existing agents
- Tests catch broken references automatically

## Design Decisions

### Why Markdown + YAML?

- **Human-readable**: Easy to review, understand, modify
- **Version-controllable**: Full git history and diffs
- **Tooling-friendly**: Easy to parse and validate
- **Documentation-first**: Agent definition is documentation
- **IDE-compatible**: Works with any text editor

### Why Validation-First?

- **Catch errors early**: Before they reach users
- **Maintain quality**: Consistent structure across agents
- **Enable automation**: CI/CD can enforce standards
- **Support evolution**: Safe to refactor with validation

### Why No Code Implementation?

- **Flexibility**: Claude interprets agent definitions dynamically
- **Rapid iteration**: Change agents without code deployment
- **Context-aware**: Agents adapt to specific project needs
- **Documentation sync**: Definition IS the implementation

## Performance Characteristics

### Agent Selection
- **Speed**: Keyword matching is near-instantaneous
- **Accuracy**: High for well-defined domains
- **Scalability**: Linear with agent count (currently 27 agents)

### Validation
- **Small projects**: ~0.1 seconds for all agents
- **CI/CD**: ~5-10 seconds total including test suite
- **Accuracy**: 100% structural validation

### Testing
- **Test suite**: 8 integration tests in ~0.1 seconds
- **Coverage**: All critical paths validated
- **Reliability**: Catches reference errors before merge

## Extensibility Points

### Adding New Agents

1. Copy `agents/AGENT_TEMPLATE.md`
2. Fill in required fields
3. Run `python3 tools/validate_agents.py`
4. Submit PR (CI validates automatically)

### Adding New Commands

1. Create `.md` file in appropriate `commands/` subdirectory
2. Define multi-phase orchestration
3. Reference existing agents
4. Tests verify agent references

### Adding New Validation Rules

1. Update `tools/validate_agents.py`
2. Add corresponding test in `tests/test_agent_integration.py`
3. Update `agents/AGENT_TEMPLATE.md` with new requirements

### Extending CI/CD

1. Modify `.github/workflows/validate-agents.yml`
2. Add new validation steps
3. Update requirements files as needed

## Agent Boundaries & Delegation Protocols

### Purpose

Clear boundaries between agents prevent overlap, reduce confusion, and ensure the right specialist handles each task. This section documents critical boundary decisions and delegation protocols for common scenarios where responsibilities might overlap.

### Boundary Decision Matrix

| Technology/Task | Primary Agent | Delegates To | Delegation Trigger |
|----------------|---------------|--------------|-------------------|
| React Native | `mobile-developer` | N/A | Always owns React Native development |
| Web React/Next.js | `full-stack-architect` | `mobile-developer` | Only if mobile-specific concerns arise |
| Code Review (Domain) | Domain specialist | `code-architect` | After domain review for holistic analysis |
| Code Review (Holistic) | `code-architect` | Domain specialists | For domain-specific deep dives |
| App Infrastructure | `devops-engineer` | `linux-sysadmin` | When OS-level changes needed |
| OS/System Administration | `linux-sysadmin` | `devops-engineer` | For application deployment concerns |
| Data Pipelines/Analytics | `data-engineer` | `database-admin` (Sprint 2) | For operational DB tuning/maintenance |
| Database Operations | `database-admin` (Sprint 2) | `data-engineer` | For analytical workloads/ETL design |

### Detailed Boundary Specifications

#### 1. React Native: Mobile vs Full-Stack

**Primary Owner**: `mobile-developer`

**Rationale**: React Native is fundamentally a mobile framework requiring deep knowledge of iOS/Android platforms, native modules, mobile UX patterns, and platform-specific deployment.

**Delegation Rules**:
- `mobile-developer` owns all React Native projects
- `full-stack-architect` may consult on shared state management patterns
- `full-stack-architect` delegates immediately if React Native is mentioned
- Web-based React knowledge does NOT qualify for React Native ownership

**Boundary Signals**:
- Keywords: "React Native", "iOS", "Android", "mobile app", "Expo"
- Context: Mobile platform requirements, app store deployment
- Artifacts: `package.json` with React Native dependencies

#### 2. Code Review: Specialist vs Architect

**Two-Tier Review Pattern**:

**Tier 1 - Domain Review** (Specialist agents):
- Domain specialist reviews code in their expertise area
- Focus: Domain logic, framework best practices, language idioms
- Example: `full-stack-architect` reviews React component architecture
- Example: `security-audit-specialist` reviews authentication implementation

**Tier 2 - Holistic Review** (`code-architect`):
- Reviews overall architecture, maintainability, readability
- Focus: System boundaries, coupling/cohesion, technical debt
- Cross-cutting concerns: naming, complexity, documentation
- Final quality gate before merge

**Delegation Protocol**:
```
User requests code review
  ↓
If domain-specific (React, security, AI) → Specialist review
  ↓
If comprehensive quality needed → code-architect review
  ↓
If both needed → Sequential: Specialist THEN code-architect
```

**When to Use Each**:
- **Specialist Only**: Quick domain-specific review, PR feedback
- **Architect Only**: Refactoring assessment, architecture analysis
- **Both Sequential**: Production code, major features, public APIs

#### 3. Infrastructure: DevOps vs System Administrator

**Application-Level Infrastructure** (`devops-engineer`):
- CI/CD pipelines (GitHub Actions, CircleCI)
- Container orchestration (Docker, Kubernetes)
- Cloud services (AWS ECS, Lambda, RDS)
- Application deployment automation
- Environment configuration (staging, production)
- Application monitoring and observability

**Operating System-Level Administration** (`linux-sysadmin`):
- OS installation, configuration, hardening
- System-level services (systemd, cron, syslog)
- Kernel parameters and tuning
- User/group management, permissions
- System security (SELinux, AppArmor, firewall)
- Bare metal or VM provisioning
- System-level performance tuning

**Delegation Rules**:
- `devops-engineer` owns application deployment; calls `linux-sysadmin` for OS changes
- `linux-sysadmin` owns system configuration; calls `devops-engineer` for app concerns
- Both collaborate on: Docker base images, system resource limits, security policies

**Boundary Signals**:
- DevOps: "CI/CD", "deploy", "Docker", "Kubernetes", "cloud"
- SysAdmin: "systemd", "kernel", "firewall", "OS hardening", "bare metal"

#### 4. Database: Data Engineering vs Database Administration

**Data Engineering** (`data-engineer`):
- Data pipelines and ETL workflows
- Analytics database design (data warehouses, OLAP)
- Data modeling for analytics
- Large-scale data processing (Spark, Airflow)
- Business intelligence integration
- Data quality and validation

**Database Administration** (`database-admin` - Coming Sprint 2):
- Operational database management (OLTP)
- Performance tuning and query optimization
- Backup/recovery and disaster recovery
- Replication and high availability
- Database security and access control
- Capacity planning and resource management

**Delegation Rules**:
- `data-engineer` owns analytical workloads; delegates operational concerns
- `database-admin` owns transactional databases; delegates analytical design
- Both collaborate on: Data modeling, indexing strategies, migration planning

**Current State** (Sprint 1):
- `data-engineer` handles both areas temporarily
- Sprint 2 will introduce `database-admin` agent
- Existing `data-engineer` work will be reviewed for boundary compliance

### Delegation Communication Protocol

**Agent-to-Agent Handoff Format**:
```json
{
  "delegation": {
    "from": "full-stack-architect",
    "to": "mobile-developer",
    "reason": "React Native mobile app implementation",
    "context": {
      "requirement": "iOS and Android app with native camera access",
      "completed_work": ["API design", "data model"],
      "needs_attention": ["mobile UI", "native modules", "app store deployment"]
    }
  }
}
```

**User Communication**:
When delegating, agents must:
1. Explain why delegation is happening
2. Summarize work completed in current domain
3. Introduce the specialist agent taking over
4. Provide clear context for seamless handoff

**Example**:
> "I've designed the API structure for your application. However, since you're building this with React Native, I'm delegating to the `mobile-developer` agent who specializes in iOS and Android development. They'll handle the mobile-specific implementation, native module integration, and app store deployment. Here's the API specification to work with..."

### Anti-Patterns: Common Boundary Violations

**DON'T**:
- ❌ `full-stack-architect` implementing React Native apps
- ❌ Multiple agents reviewing the same code simultaneously
- ❌ `devops-engineer` configuring kernel parameters
- ❌ `linux-sysadmin` setting up CI/CD pipelines
- ❌ `data-engineer` handling operational DB tuning (after Sprint 2)
- ❌ Domain specialists doing holistic architecture review (that's `code-architect`)

**DO**:
- ✅ Recognize boundary crossing and delegate explicitly
- ✅ Provide context when handing off between agents
- ✅ Use sequential review (specialist → architect) for comprehensive quality
- ✅ Collaborate at boundary interfaces (Docker images, data models)
- ✅ Document which agent owns which component

### Boundary Evolution

As the agent ecosystem grows:
- New agents may require boundary clarification (add here)
- Technology evolution may shift boundaries (document changes)
- User feedback may reveal unclear boundaries (refine definitions)
- Sprint planning introduces new agents (update matrix and protocols)

**Change Protocol**:
1. Identify boundary ambiguity or overlap
2. Document in this section with rationale
3. Update `CLAUDE.md` agent selection guide
4. Update affected agent definitions
5. Communicate in sprint retrospectives

## Future Architecture Considerations

### Potential Enhancements

1. **docs/**: Centralized documentation (this file is the start)
2. **Agent versioning**: Semantic versioning for agents
3. **Metrics tracking**: Usage analytics and effectiveness
4. **Reference checker**: Automated broken link detection
5. **Command templates**: Standardized command structure

### Non-Goals

- **Code-based agents**: Keep agents as documentation
- **Runtime validation**: Validate at build/commit time
- **Complex dependencies**: Maintain simple, flat structure
- **State management**: Agents are stateless by design

## Security Considerations

- **No credentials in repo**: All files are public-safe
- **Validation prevents injection**: YAML parsing is safe
- **CI/CD runs in isolation**: Sandboxed GitHub Actions
- **No executable code**: Only documentation and tests

## Monitoring and Metrics

Currently manual. Future considerations:
- Agent selection frequency
- Command usage patterns
- Validation failure rates
- Test coverage trends
- CI/CD performance

---

**Last Updated**: 2025-10-06
**Architecture Version**: 1.0
**Status**: Active Development
