# Claude Code AI Agent System

A comprehensive ecosystem of 71 specialized AI agents for autonomous software development with Claude Code. Each agent is an expert in their domain, working individually or in coordination to deliver production-ready solutions.

## 📁 Repository Structure

```
ClaudeAgents/
├── agents/              # 71 specialized agent definitions
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

**New to ClaudeAgents?** Get started in 3 minutes:

👉 **[Read the Quick Start Guide](docs/QUICKSTART.md)** - Your first workflow in <5 minutes

**Find a Workflow:**
- 📋 **[Command Catalog](docs/COMMAND_CATALOG.md)** - Browse all 59 workflows by category
- 🔍 **Search by problem** - "I need to build an API" → `/api-design`
- 🎯 **Search by technology** - "React, PostgreSQL" → relevant workflows

**Common Scenarios:**
- Building a web app? → `/saas-mvp` (8-12 hours, full-stack)
- Need an API? → `/api-design` (4-6 hours, REST/GraphQL)
- Testing strategy? → `/quality:testing-strategy` (4-8 hours, comprehensive)
- Performance issues? → `/quality:performance-optimization` (2-3 hours audit)
- Security audit? → `/security-audit` (4-6 hours, vulnerability assessment)

💡 **Pro Tip:** Start with a workflow (commands/), then explore individual agents for custom orchestration.

## 📚 Documentation

**Getting Started:**
- 🚀 **[Quick Start Guide](docs/QUICKSTART.md)** - Your first workflow in 3 minutes
- 📋 **[Command Catalog](docs/COMMAND_CATALOG.md)** - All 59 workflows searchable by category
- 🎯 **[Workflow Examples](docs/WORKFLOW_EXAMPLES.md)** - Real case studies with metrics *(coming soon)*

**Core Documentation:**
- **[The Manifesto](docs/manifesto.md)** - Professional principles and engineering standards
- **[System Architecture](docs/architecture.md)** - Design patterns, component interactions
- **[Users' Guide](docs/users-guide.md)** - Comprehensive guide for using agents
- **[Contributing Guide](docs/contributing.md)** - How to add agents and improvements

**Developer Resources:**
- **[Agent Tiers](docs/agent-tiers.md)** - Quality-based 3-tier organization
- **[Telemetry Guide](docs/telemetry-guide.md)** - Privacy-first usage tracking
- **[Development Process](docs/development-process.md)** - Contributor workflow

**Privacy & Trust:**
- **[Telemetry Privacy](docs/TELEMETRY_PRIVACY.md)** - What we collect, why, and how to opt-in

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

### 🤖 AI & Machine Learning (Pattern-Based Specialists)
- **`llm-integration-architect`** - Multi-model LLM integration, intelligent routing, cost optimization, vendor-neutral architecture
- **`prompt-engineering-specialist`** - Advanced prompting techniques, chain-of-thought, few-shot learning, prompt optimization across all LLMs
- **`rag-systems-engineer`** - Retrieval-Augmented Generation architecture, vector databases, hybrid search, document processing pipelines
- **`fine-tuning-specialist`** - LLM fine-tuning (LoRA, QLoRA), dataset engineering, RLHF/DPO, custom model deployment
- **`inference-optimization-specialist`** - Self-hosted LLM deployment, quantization, GPU optimization, vLLM, TensorRT-LLM, cost-efficient serving
- **`generative-image-specialist`** - Image generation (Stable Diffusion, DALL-E, Midjourney), LoRA training, ControlNet, ComfyUI workflows
- **`systems-engineer`** - Rust, C++, Go, performance-critical systems
- **`metaprogramming-specialist`** - Lisp, macros, DSLs, code generation

### ₿ Blockchain & Web3
- **`blockchain-web3-engineer`** - Solidity smart contracts, Solana/Rust, DeFi, NFTs, dApp development, Web3 security

### 🚨 Operational Excellence
- **`debugging-specialist`** - Advanced debugging across all languages, root cause analysis, memory/performance profiling
- **`observability-engineer`** - Full-stack observability, distributed tracing, SLO/SLI engineering, error budgets
- **`incident-coordinator`** - Incident response, war room coordination, postmortems, on-call engineering
- **`site-reliability-engineer`** - SRE methodology, error budgets, toil reduction, capacity planning, operational maturity
- **`developer-experience-engineer`** - API/SDK usability, developer onboarding, error message design, tooling ergonomics, DX metrics

### 🔒 Quality & Security
- **`security-audit-specialist`** - Vulnerability assessment, compliance
- **`dependency-security-specialist`** - Supply chain security, SBOM generation (CycloneDX/SPDX), license compliance, SLSA framework
- **`compliance-automation-engineer`** - SOC 2, HIPAA, PCI-DSS, GDPR automation, continuous compliance, audit readiness
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

## 📋 Available Commands (59 total)

### Development Commands (`commands/development/`)
- `api-design` - REST/GraphQL API design with OpenAPI specs
- `database-design` - Database schema design with migrations and indexing
- `database-optimization` - Database performance tuning and optimization
- `debug-help` - Debugging assistance
- `refactor-component` - Code refactoring
- `documentation-generator` - Auto-generate docs
- `git-workflow` - Git operations
- `cross-paradigm-translator` - Language translation
- `tech-debt-impact-measurement` - **NEW (Tier 1 Innovation)** - Empirical technical debt cost quantification with business impact metrics

### Quality Commands (`commands/quality/`)
- `code-review` - Comprehensive code review (consolidated from 3 specialized review commands)
- `testing-strategy` - Complete testing strategy design with CI/CD integration (consolidated from 3 testing commands)
- `performance-optimization` - Complete performance optimization workflow (consolidated from 3 performance commands)
- `security-audit` - Security vulnerability scan
- `production-readiness` - Deployment checklist
- `dependency-audit` - Dependency security check
- `infrastructure-audit` - IaC and cloud infrastructure assessment (security, cost, reliability)
- `cognitive-load-optimization` - **NEW (Tier 1 Innovation)** - Industry-first cognitive complexity measurement and reduction strategies
- `compliance-audit-soc2` - **NEW** - SOC 2 compliance preparation and audit readiness

### Operations Commands (`commands/operations/`)
- `monitoring-stack-setup` - **NEW** - Complete observability implementation (Prometheus, Grafana, OpenTelemetry, distributed tracing)
- `incident-response-workflow` - **NEW** - Production incident management with war room coordination and postmortems
- `disaster-recovery-plan` - **NEW** - Business continuity and disaster recovery planning with RTO/RPO targets
- `production-learning-loop` - **NEW (Tier 1 Innovation)** - Self-improving organizational memory system with postmortem automation

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
- `microservices-architecture` - Complete microservices design with service mesh
- `platform-migration` - Platform migration strategy and execution
- `streaming-architecture` - Real-time streaming architecture design
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

### Platform Improvements (Recent Updates)
**Command Consolidation for Coherence:**
- Merged 12 redundant commands into 4 focused workflows (code-review, testing-strategy, performance-optimization, database-optimization)
- Removed overlapping database-review command (functionality integrated into database-optimization and infrastructure-audit)
- Result: Clearer command selection, reduced cognitive overhead, improved discoverability

**Strategic Additions (7 New Commands):**
- **3 Tier 1 Innovations**: Industry-first capabilities (cognitive-load-optimization, production-learning-loop, tech-debt-impact-measurement)
- **4 High-Priority Operations**: Production-ready operational excellence (monitoring-stack-setup, incident-response-workflow, disaster-recovery-plan, compliance-audit-soc2)
- Focus: Measurable business impact, empirical data-driven decision making, continuous improvement culture

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

Each agent is designed to deliver production-ready solutions with appropriate documentation, testing strategies, and deployment guidance for their domain.

---

*For Claude Code-specific instructions and project context, see [CLAUDE.md](CLAUDE.md)*