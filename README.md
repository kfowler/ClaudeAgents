# Claude Code AI Agent System

A comprehensive ecosystem of 29 specialized AI agents for autonomous software development with Claude Code. Each agent is an expert in their domain, working individually or in coordination to deliver production-ready solutions.

## 📁 Repository Structure

```
ClaudeAgents/
├── agents/              # 29 specialized agent definitions
├── commands/            # Organized workflow commands
│   ├── development/     # Code review, debugging, refactoring
│   ├── quality/         # Testing, security, performance audits
│   ├── deployment/      # Deploy prep, infrastructure setup
│   ├── specialized/     # Language-specific tools (Rust, Python, etc.)
│   └── workflows/       # Multi-agent orchestration patterns
├── tools/               # Validation and utilities
│   └── validate_agents.py  # Agent consistency validation
├── examples/            # Design specifications and prototypes
│   └── analysis/        # Project analysis system (prototype)
├── docs/                # Comprehensive documentation
│   ├── manifesto.md     # Professional principles
│   ├── architecture.md  # System design and patterns
│   └── contributing.md  # Contribution guidelines
├── CLAUDE.md           # Core project instructions for Claude Code
└── TODO.md             # Improvement roadmap and tasks
```

## 🚀 Quick Start

### For New Projects
1. **Start with Strategy**: Use `product-strategist` for market validation
2. **Plan Execution**: Use `project-orchestrator` to break down complex requirements
3. **Implement**: Deploy specialized agents based on technology needs
4. **Validate**: Use quality agents for security, testing, and accessibility

### For Existing Projects
1. **Analyze Current State**: Use `code-architect` for architecture review
2. **Identify Improvements**: Deploy domain-specific agents for enhancements
3. **Ensure Quality**: Use `qa-test-engineer` and `security-audit-specialist`

## 🎯 Agent Categories

### 📊 Strategy & Planning
- **`product-strategist`** - Market research, competitive analysis, product ideation
- **`project-orchestrator`** - Complex project coordination, multi-agent orchestration
- **`agent-orchestrator`** - Agent selection and workflow optimization

### 🏗️ Core Development
- **`full-stack-architect`** - Web applications (React, Next.js, Svelte + backends)
- **`backend-api-engineer`** - Backend APIs (REST, GraphQL, microservices, server-side logic)
- **`mobile-developer`** - iOS/Android (Swift, Kotlin, React Native, Flutter)
- **`data-engineer`** - Databases, pipelines, analytics, ML infrastructure
- **`devops-engineer`** - CI/CD, Docker, Kubernetes, cloud deployment

### 🤖 AI & Machine Learning
- **`ai-ml-engineer`** - LLM integration, RAG systems, vector databases
- **`systems-engineer`** - Rust, C++, Go, performance-critical systems
- **`metaprogramming-specialist`** - Lisp, macros, DSLs, code generation

### 🔒 Quality & Security
- **`security-audit-specialist`** - Vulnerability assessment, compliance
- **`qa-test-engineer`** - Testing strategies, automation, quality assurance
- **`accessibility-expert`** - WCAG compliance, inclusive design
- **`code-architect`** - Architecture review, code quality, maintainability

### 🎨 Creative & Specialized
- **`digital-artist`** - UI/UX graphics, game assets, visual design
- **`video-director`** - Video production, editing, post-production
- **`audio-engineer`** - Audio production, Logic Pro, CoreAudio
- **`3d-modeler`** - 3D assets, Blender workflows, game development
- **`comedy-writer`** - Creative writing, humor, narrative structures
- **`tv-writer`** - Television scripts, procedural dramas

### 🔧 Specialized Development
- **`functional-programmer`** - Haskell, Clojure, F#, type systems
- **`legacy-specialist`** - Legacy code migration, compatibility
- **`platform-integrator`** - Native platform APIs (macOS, Windows, Linux)
- **`elisp-specialist`** - Emacs configuration, package development
- **`merge-conflict-resolver`** - Git conflicts, code integration

### ⚖️ Decision Support
- **`the-critic`** - Technical decision analysis, architectural critique
- **`creative-catalyst`** - Creative problem-solving, lateral thinking

## 💡 Usage Examples

### Web Application Development
```
"Use project-orchestrator to plan a task management app with React frontend and Node.js backend"
```

### Mobile App Creation
```
"Have mobile-developer create a cross-platform fitness tracking app"
```

### AI Feature Integration
```
"Get ai-ml-engineer to implement semantic search with RAG for my documentation"
```

### Security Review
```
"Ask security-audit-specialist to review my authentication system"
```

### Architecture Decision
```
"Use the-critic to evaluate PostgreSQL vs MongoDB for real-time analytics"
```

## 📋 Available Commands

### Development Commands (`commands/development/`)
- `code-review` - Comprehensive code review
- `debug-help` - Debugging assistance
- `refactor-component` - Code refactoring
- `documentation-generator` - Auto-generate docs
- `git-workflow` - Git operations
- `cross-paradigm-translator` - Language translation

### Quality Commands (`commands/quality/`)
- `security-audit` - Security vulnerability scan
- `test-coverage` - Test implementation
- `performance-audit` - Performance optimization
- `architecture-review` - Architecture assessment
- `production-readiness` - Deployment checklist
- `dependency-audit` - Dependency security check

### Deployment Commands (`commands/deployment/`)
- `deploy-prep` - Deployment preparation
- `dokku-deploy` - Dokku deployment
- `orb-stack` - OrbStack configuration
- `ssh-pi-ops` - Raspberry Pi operations

### Specialized Commands (`commands/specialized/`)
- Python tools (uv-workflow, modern-stack, data-pipeline, web-api, scraping)
- `rust-cargo` - Rust development
- `xcode-power-tools` - iOS development
- `safari-web-extension` - Safari extensions
- `lisp-macro-workshop` - Lisp macros
- `roswell` - Common Lisp setup

### Workflow Commands (`commands/workflows/`)
- `ai-agent-council` - Multi-agent collaboration
- `team-comm-hub` - Team communication
- `crisis-manager` - Emergency response
- `ai-code-battle` - Code comparison
- `optimize-performance` - Performance tuning

## 🔍 Agent Selection Guide

The system uses intelligent agent selection based on:
- **Keywords**: Technology mentions (React, Python, database, etc.)
- **Task Type**: Development, testing, deployment, analysis
- **Complexity**: Single agent vs multi-agent orchestration
- **Domain**: Web, mobile, AI/ML, infrastructure, etc.

Agent selection is based on keyword analysis, task type, and domain expertise.

## 🛠️ Tools & Utilities

### Installation
```bash
# Install required dependencies for validation tools
pip install -r tools/requirements.txt
```

### Agent Validation
```bash
python3 tools/validate_agents.py
```
Validates all agent definitions for consistency and completeness.

### Examples and Prototypes
The `examples/` directory contains design specifications and proof-of-concept implementations:
- **Project analysis system**: Prototype for ML-based agent recommendations
- **Implementation examples**: Design patterns for future features

*Note: These are not production-ready. See examples/README.md for details.*

## 📚 Documentation

### Core Documentation
- **[The Manifesto](docs/manifesto.md)** - Professional principles and engineering standards
- **[System Architecture](docs/architecture.md)** - Design patterns, component interactions, data flow
- **[Users' Guide](docs/users-guide.md)** - Comprehensive guide for using agents with Claude Code 2.0
- **[Contributing Guide](docs/contributing.md)** - How to add agents, commands, and improvements

### Developer Resources
- **[Development Process](docs/development-process.md)** - Mandatory workflow for contributors (branching, commits, agent delegation)
- **[Lessons Learned](docs/lessons-learned.md)** - Process improvements and best practices
- **[Project Instructions](CLAUDE.md)** - Guidance for Claude Code when working with this repository
- **[TODO Roadmap](TODO.md)** - Prioritized improvements and development roadmap

## 🎯 Model Assignment & Cost Optimization

ClaudeAgents uses strategic model assignment for cost optimization:

- **8 Haiku agents (30%)** - Creative and specialized tasks
- **14 Sonnet agents (52%)** - Development and coordination
- **5 Opus agents (18%)** - Complex analysis and critical systems

This distribution achieves ~71.5% cost savings vs using Opus for all tasks while maintaining appropriate capability levels.

See [Model Assignment Strategy](docs/model-assignment-strategy.md) for details.

## 🏆 Success Metrics

Track agent effectiveness through:
- **Feature Completion Rate**: Delivered features working as specified
- **Code Quality Scores**: Maintainability, security, performance
- **Integration Success**: Seamless agent handoffs
- **Development Velocity**: Time from concept to production

## 🚦 Getting Started

1. **Read [The Manifesto](docs/manifesto.md)** to understand professional standards
2. **Review [System Architecture](docs/architecture.md)** for design overview
3. **Browse available agents** in the `agents/` directory
4. **Check commands** in `commands/` for pre-built workflows
5. **See [Contributing Guide](docs/contributing.md)** to add your own agents
6. **Start with simple requests** and progress to multi-agent orchestration

Each agent is designed to deliver production-ready solutions with appropriate documentation, testing strategies, and deployment guidance for their domain.

---

*For Claude Code-specific instructions and project context, see [CLAUDE.md](CLAUDE.md)*