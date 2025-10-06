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
