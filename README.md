# Claude Code AI Agent System

A comprehensive ecosystem of 61 specialized AI agents for autonomous software development with Claude Code. Each agent is an expert in their domain, working individually or in coordination to deliver production-ready solutions.

## 📁 Repository Structure

```
ClaudeAgents/
├── agents/              # 61 specialized agent definitions
├── commands/            # Organized workflow commands
│   ├── development/     # Code review, debugging, refactoring
│   ├── quality/         # Testing, security, performance audits
│   ├── deployment/      # Deploy prep, infrastructure setup
│   ├── seo/             # SEO auditing and optimization
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

### 🏗️ Core Development
- **`full-stack-architect`** - Web applications (React, Next.js, Svelte + backends)
- **`backend-api-engineer`** - Backend APIs (REST, GraphQL, microservices, server-side logic)
- **`mobile-developer`** - iOS/Android (Swift, Kotlin, React Native, Flutter)
- **`game-development-engineer`** - Unity/Unreal Engine, 2D/3D games, mobile/VR/AR, multiplayer

### 🏭 Infrastructure & Platform
- **`cloud-architect`** - Multi-cloud strategy, AWS/Azure/GCP architecture, cost optimization
- **`devops-engineer`** - CI/CD, Docker, Kubernetes, cloud deployment
- **`infrastructure-as-code-specialist`** - Terraform, Pulumi, multi-cloud IaC, state management, policy as code
- **`platform-engineering-specialist`** - Internal Developer Platforms (IDPs), Backstage, golden paths, developer experience
- **`edge-computing-specialist`** - Cloudflare Workers, Deno Deploy, Vercel Edge, <50ms global latency
- **`linux-sysadmin`** - System administration, OS hardening, server configuration
- **`macos-specialist`** - macOS administration, MDM integration, Homebrew, Apple Silicon optimization, enterprise Mac fleets
- **`windows-specialist`** - Windows Server, Active Directory, Group Policy, PowerShell DSC, enterprise Windows infrastructure

### 💾 Database & Streaming
- **`data-engineer`** - Data pipelines, analytics, ML infrastructure
- **`database-administrator`** - Production database operations, performance tuning, backup/recovery
- **`postgresql-expert`** - Advanced PostgreSQL optimization, query tuning, replication, high availability, pgvector/PostGIS/TimescaleDB
- **`kafka-expert`** - Apache Kafka architecture, stream processing, event-driven systems, Kafka Streams/Connect, real-time pipelines

### 🤖 AI & Machine Learning
- **`ai-ml-engineer`** - LLM integration, RAG systems, vector databases
- **`systems-engineer`** - Rust, C++, Go, performance-critical systems
- **`metaprogramming-specialist`** - Lisp, macros, DSLs, code generation

### ₿ Blockchain & Web3
- **`blockchain-web3-engineer`** - Solidity smart contracts, Solana/Rust, DeFi, NFTs, dApp development, Web3 security

### 🚨 Operational Excellence
- **`debugging-specialist`** - Advanced debugging across all languages, root cause analysis, memory/performance profiling
- **`observability-engineer`** - Full-stack observability, distributed tracing, SLO/SLI engineering, error budgets
- **`incident-coordinator`** - Incident response, war room coordination, postmortems, on-call engineering

### 🔒 Quality & Security
- **`security-audit-specialist`** - Vulnerability assessment, compliance
- **`qa-test-engineer`** - Testing strategies, automation, quality assurance
- **`test-automation-engineer`** - Playwright/Cypress E2E, visual regression, API testing, CI/CD integration
- **`accessibility-expert`** - WCAG compliance, inclusive design
- **`frontend-performance-specialist`** - Core Web Vitals, bundle optimization, rendering performance
- **`code-architect`** - Architecture review, code quality, maintainability

### 🔍 SEO & Optimization
- **`seo-meta-optimizer`** - Meta tags, Open Graph, structured data, CTR optimization
- **`seo-technical-auditor`** - Crawlability, indexability, sitemaps, mobile-friendliness
- **`seo-performance-specialist`** - Core Web Vitals for rankings, TTFB, mobile-first performance
- **`seo-keyword-strategist`** - Keyword research, search intent analysis, competitive keyword gaps
- **`seo-content-optimizer`** - On-page optimization, readability, E-E-A-T, featured snippets
- **`seo-structure-architect`** - Site architecture, internal linking, URL structure, content silos

### 📋 Business Operations
- **`business-analyst`** - Requirements gathering, stakeholder management, BRD, user stories
- **`technical-writer`** - API docs, user guides, tutorials, developer documentation
- **`product-manager`** - Product roadmap, feature prioritization, OKRs, product metrics

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
- **`embedded-iot-developer`** - C/C++ firmware, ESP32/STM32/Arduino, RTOS, MQTT/BLE, power optimization
- **`elisp-specialist`** - Emacs configuration, package development
- **`merge-conflict-resolver`** - Git conflicts, code integration

### ⚖️ Decision Support
- **`the-critic`** - Technical decision analysis, architectural critique
- **`creative-catalyst`** - Creative problem-solving, lateral thinking
- **`the-skeptic`** - **NEW (Phase 3)** - Questions automation necessity, recommends alternatives, radical honesty about AI limitations

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

## 📋 Available Commands (51 total)

### Development Commands (`commands/development/`)
- `code-review` - Comprehensive code review
- `debug-help` - Debugging assistance
- `refactor-component` - Code refactoring
- `documentation-generator` - Auto-generate docs
- `git-workflow` - Git operations
- `cross-paradigm-translator` - Language translation
- `api-design` - REST/GraphQL API design with OpenAPI specs
- `database-design` - Database schema design with migrations and indexing

### Quality Commands (`commands/quality/`)
- `security-audit` - Security vulnerability scan
- `test-coverage` - Test implementation
- `performance-audit` - Performance optimization
- `architecture-review` - Architecture assessment
- `production-readiness` - Deployment checklist
- `dependency-audit` - Dependency security check
- `code-quality-review` - Comprehensive code quality assessment
- `performance-optimization` - Complete performance optimization workflow
- `testing-strategy` - Complete testing strategy design with CI/CD integration
- `database-review` - Comprehensive database assessment (performance, security, schema, operations)
- `infrastructure-audit` - IaC and cloud infrastructure assessment (security, cost, reliability)
- `api-testing-strategy` - Complete API testing (functional, contract, security, performance)

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
- `microservices-architecture` - Complete microservices design with service mesh
- `debate` - **NEW (Phase 3)** - Agent conflict theater for technical decisions (45-90 min, surfaces hidden tradeoffs)

### SEO Commands (`commands/seo/`)
- `comprehensive-seo-audit` - Full site SEO health check (seo-technical-auditor, seo-meta-optimizer, seo-performance-specialist)
- `content-optimization` - Individual page optimization (seo-keyword-strategist, seo-content-optimizer, seo-meta-optimizer)
- `keyword-research` - Comprehensive keyword strategy (seo-keyword-strategist, seo-technical-auditor, seo-structure-architect)
- `site-architecture-audit` - Site structure optimization (seo-structure-architect, seo-technical-auditor, seo-keyword-strategist)

### Business Commands (`commands/business/`)
- `requirements-analysis` - Complete BRD creation (business-analyst, product-manager, technical-writer)
- `product-roadmap` - Strategic product planning (product-manager, business-analyst, product-strategist)

### Vertical Workflow Packages (`commands/vertical/`) **NEW - Phase 2 & 3**
- `saas-mvp` - Complete SaaS product development (8-12 hours, 6-8 agents, market strategy to production deployment)
- `ecommerce-platform` - E-commerce store launch (10-14 hours, 7-9 agents, mobile storefront to PCI compliance)
- `fintech-compliance` - **NEW (Phase 3)** - FinTech compliance & regulatory workflow (12-16 hours, 8-10 agents, PCI DSS/SOC 2/BSA-AML/GDPR/PSD2)

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

### Agent Registry (NEW - Phase 1)
Fast agent discovery through semantic indexing:
```bash
# View registry statistics
python3 tools/agent_registry.py stats

# Search for agents
python3 tools/agent_registry.py search "react mobile app"

# Find by capability/keyword/domain
python3 tools/agent_registry.py find optimization
```

**Features:**
- O(1) capability-based lookup (vs O(n) scanning)
- Semantic search with relevance scoring
- 1,290 keywords indexed across 50 agents
- Multi-index: capabilities, keywords, domains

### Telemetry (Optional - Privacy-First, Enhanced Phase 3)
Opt-in usage tracking with comprehensive performance metrics:
```bash
# Enable telemetry (disabled by default)
python3 tools/telemetry.py enable

# View your usage statistics with performance metrics
python3 tools/telemetry.py summary

# Disable telemetry
python3 tools/telemetry.py disable
```

**Privacy Promise:**
- No PII, code snippets, or project details
- All data stored locally in `~/.claude-telemetry/`
- Completely optional and transparent
- See [Telemetry Guide](docs/telemetry-guide.md) for details

**Performance Metrics (NEW):**
- Percentile analysis (p50, p95, p99 duration)
- Fastest/slowest agent identification
- Performance trend tracking for optimization

### Intelligent Orchestrator (NEW - Phase 2, Enhanced Phase 3)
Context-aware agent selection with tier-based prioritization:
```bash
# Auto-select agents based on project and request
python3 tools/intelligent_orchestrator.py "implement authentication with security best practices"

# Analyzes your project structure and selects optimal agents
python3 tools/intelligent_orchestrator.py "optimize frontend performance"
```

**Features:**
- Detects project type (web, mobile, data, ml, backend)
- Parses intent from natural language (implement, review, debug, optimize)
- Selects core + quality + support agents automatically
- **Tier-based prioritization** (Core > Extended > Experimental)
- Shows tier badges in output (⭐ CORE, ✓ EXTENDED, 🧪 EXPERIMENTAL)
- Generates workflow with reasoning and success criteria
- Estimates duration and defines prerequisites

### Agent Emergence Tracking (NEW - Phase 3)
Organic agent evolution through usage pattern tracking:
```bash
# View emergence tracking dashboard
python3 tools/agent_emergence.py dashboard

# See patterns approaching promotion threshold
python3 tools/agent_emergence.py candidates

# Promote emergent agent to permanent status
python3 tools/agent_emergence.py promote <agent-name>
```

**Features:**
- Tracks agent usage gaps and combination patterns
- Auto-synthesizes composite agents when threshold met (10+ uses, 70%+ satisfaction, 5+ distinct use cases)
- Identifies unmet needs organically from real usage
- Prevents agent proliferation (only promotes validated patterns)
- Storage in `~/.claude-telemetry/emergence/`

### Analytics Dashboard (NEW - Phase 3)
Comprehensive visualization and analysis of agent usage patterns:
```bash
# View formatted analytics dashboard
python3 tools/analytics_dashboard.py

# Export analytics report as JSON
python3 tools/analytics_dashboard.py json
```

**Features:**
- **Agent Rankings**: Top agents by usage, success rate, and tier
- **Tier Analysis**: Distribution and performance by tier (Core, Extended, Experimental)
- **Performance Trends**: Fastest/slowest agents, outlier detection
- **Quality Metrics**: High performers (>95% success) and underperformers (<75%)
- **Emergence Insights**: Top composite patterns, promotion candidates
- **Recommendations**: Tier promotions/demotions, performance optimization targets
- **Multi-format output**: Human-readable dashboard or JSON export

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
- **[Strategic Roadmap](docs/ROADMAP.md)** - 6-month strategic plan with phases and milestones
- **[Agent Tiers](docs/agent-tiers.md)** - **NEW (Phase 3)** - Quality-based 3-tier organization system (Core, Extended, Experimental)
- **[Telemetry Guide](docs/telemetry-guide.md)** - Optional privacy-first usage tracking
- **[TODO Roadmap](TODO.md)** - Prioritized improvements and development roadmap

## 🎯 Model Assignment & Cost Optimization

ClaudeAgents uses strategic model assignment for cost optimization:

- **9 Haiku agents (18%)** - Creative and specialized tasks
- **32 Sonnet agents (63%)** - Development, coordination, and operational excellence
- **10 Opus agents (19%)** - Complex analysis and critical systems (includes the-skeptic)

This distribution achieves ~75% cost savings vs using Opus for all tasks while maintaining appropriate capability levels.

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