# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains specialized AI agent definitions and commands for Claude Code. It provides a comprehensive ecosystem of 71 specialized agents that can autonomously handle complex software development tasks across multiple domains including web development, mobile apps, AI/ML integration, security, business operations, SEO optimization, creative production, and more.

## Architecture & Structure

### Core Components

1. **Agent System** (`agents/` directory)
   - Each `.md` file defines a specialized agent with specific expertise
   - Agents use YAML frontmatter for metadata (name, description, color)
   - Agents can be invoked individually or orchestrated together for complex tasks

2. **Command System** (`commands/` directory)
   - Pre-defined workflow commands for common development tasks
   - Commands can leverage multiple agents for comprehensive solutions

3. **Hooks** (`hooks/` directory)
   - User-configurable shell commands that execute in response to events

### Key Decision Logic

Agent selection is based on keyword matching, task type analysis, and domain expertise. See [System Architecture](docs/architecture.md) for detailed information on agent selection patterns and multi-agent orchestration.

## Agent Selection Guide

### For New Projects/Products
Start with `product-strategist` for market validation, then use `project-orchestrator` for execution planning.

### Primary Development Agents by Domain
- **Web Applications**: `full-stack-architect` (React, Next.js, Svelte, backend APIs)
  - **Note**: For React Native, use `mobile-developer` instead
  - **Note**: For backend-only API development, use `backend-api-engineer`
- **Backend APIs**: `backend-api-engineer` (REST, GraphQL, microservices, server-side logic)
- **Mobile Apps**: `mobile-developer` (iOS, Android, React Native, Flutter, app store deployment)
- **AI/ML Integration**: Pattern-based AI specialists (vendor-neutral, durable expertise)
  - `llm-integration-architect` (multi-model integration, routing, cost optimization, reliability patterns)
  - `prompt-engineering-specialist` (advanced prompting, chain-of-thought, few-shot, optimization)
  - `rag-systems-engineer` (RAG architecture, vector databases, hybrid search, document processing)
  - `fine-tuning-specialist` (LoRA, QLoRA, dataset engineering, custom model deployment)
  - `inference-optimization-specialist` (self-hosted LLM, quantization, GPU optimization, vLLM)
  - `generative-image-specialist` (Stable Diffusion, DALL-E, Midjourney, LoRA training, ComfyUI)
  - **Note**: We use pattern-based specialists (not vendor-specific) for durability and vendor-neutrality
- **Database/Data**: `data-engineer` (data pipelines, analytics, OLAP workloads)
  - **Note**: Operational database management (OLTP, tuning, backups) will be handled by `database-admin` (Sprint 2)
- **Application Infrastructure**: `devops-engineer` (CI/CD, Docker, Kubernetes, cloud deployment)
  - **Note**: For OS-level configuration (systemd, kernel, firewall), use `linux-sysadmin`
- **System Administration**: `linux-sysadmin` (OS hardening, system services, bare metal/VM setup)
- **Platform Specialists**:
  - `macos-specialist` (macOS administration, MDM, Homebrew, Apple Silicon optimization, enterprise Mac fleet)
  - `windows-specialist` (Windows Server, Active Directory, Group Policy, PowerShell DSC, enterprise Windows)
- **Technology Specialists**:
  - `postgresql-expert` (PostgreSQL optimization, replication, high availability, query tuning, extensions)
  - `kafka-expert` (Kafka architecture, stream processing, event-driven systems, Kafka Streams/Connect)
- **Systems Programming**: `systems-engineer` (Rust, C++, Go, performance optimization)

### Quality & Security Agents
- **Security**: `security-audit-specialist` (vulnerability assessment, compliance)
- **Supply Chain Security**: `dependency-security-specialist` (SBOM generation, license compliance, dependency scanning, SLSA framework)
- **Testing**: `qa-test-engineer` (test strategies, implementation)
- **Accessibility**: `accessibility-expert` (WCAG compliance, inclusive design)
- **Frontend Performance**: `frontend-performance-specialist` (Core Web Vitals, bundle optimization, rendering performance)
- **Code Quality**: `code-architect` (holistic architecture review, maintainability, readability)
  - **Note**: For domain-specific code review, use the domain specialist first, then `code-architect` for comprehensive analysis
- **Compliance**: `compliance-automation-engineer` (SOC 2, HIPAA, PCI-DSS, GDPR automation, continuous compliance)

### Operational Excellence Agents
- **Site Reliability**: `site-reliability-engineer` (SRE methodology, error budgets, SLO/SLI engineering, toil reduction)
- **Developer Experience**: `developer-experience-engineer` (API usability, SDK design, onboarding optimization, DX metrics)

### SEO & Optimization Agents
- **SEO Metadata**: `seo-meta-optimizer` (meta tags, Open Graph, structured data, CTR optimization)
- **Technical SEO**: `seo-technical-auditor` (crawlability, indexability, sitemaps, mobile-friendliness)
- **SEO Performance**: `seo-performance-specialist` (Core Web Vitals for rankings, TTFB, mobile-first)
- **SEO Keywords**: `seo-keyword-strategist` (keyword research, search intent, competitive analysis, keyword clustering)
- **SEO Content**: `seo-content-optimizer` (on-page optimization, readability, E-E-A-T, featured snippets)
- **SEO Architecture**: `seo-structure-architect` (site architecture, internal linking, URL structure, content silos)

### Business Operations Agents
- **Requirements**: `business-analyst` (requirements gathering, stakeholder management, BRD, user stories)
- **Documentation**: `technical-writer` (API docs, user guides, tutorials, developer documentation)
- **Product Management**: `product-manager` (roadmap planning, feature prioritization, OKRs, product metrics)

### Creative & Artistic Agents
- **Music**: `music-composer` (orchestral scores, film/game soundtracks, adaptive music, thematic development)
- **Visual Arts**: `digital-artist` (game assets, UI/UX graphics, generative art), `cinematographer` (camera work, lighting, visual storytelling)
- **Sound**: `audio-engineer` (mixing, mastering, production), `sound-designer` (SFX, foley, spatial audio, game audio)
- **Writing**: `screenwriter` (feature films, three-act structure), `tv-writer` (episodic content), `poet` (verse forms, literary devices), `comedy-writer` (stand-up, timing)
- **Interactive Media**: `game-designer` (mechanics, level design, player psychology), `narrative-designer` (branching stories, game lore, dialogue systems)
- **Performance**: `choreographer` (dance composition, movement design), `video-director` (video production, cinematography)
- **3D Arts**: `3d-modeler` (modeling, texturing, rendering)

### Creative Triad: Structured Ideation & Validation
The **Creative Triad** transforms ideation from art into science through divergent exploration, convergent synthesis, and rigorous experimental validation. Use these agents for innovation, product design, and strategic exploration.

**Divergent Ideation** (choose one based on approach):
- **creative-catalyst**: Oblique strategies, breakthrough thinking, constraint generation (5-50 ideas, novelty-focused)
  - Use for: Breaking assumptions, creative breakthroughs, challenging conventional thinking
  - Keywords: "oblique strategies", "breakthrough ideas", "challenge assumptions", "creative constraints"
- **the-inventor**: Systematic diversity guarantees, comprehensive exploration (7-12 ideas, diversity-focused)
  - Use for: Comprehensive solution space coverage, guaranteed diversity metrics, balanced exploration
  - Keywords: "diverse ideas", "systematic ideation", "diversity guarantees", "comprehensive exploration"

**Convergent Synthesis**:
- **the-synthesist**: Organizes scattered ideas into coherent strategic frames with 100% coverage
  - Use for: Synthesizing multiple ideas, identifying false tradeoffs, creating implementation paths
  - Keywords: "synthesize ideas", "strategic frames", "false tradeoffs", "organize ideas"
  - **Required input**: Ideation report from creative-catalyst or the-inventor

**Experimental Validation**:
- **the-architect-of-experiments**: Designs falsifiable experiments with 100% kill condition coverage
  - Use for: A/B test design, validation planning, rigorous experimentation, hypothesis testing
  - Keywords: "experiments", "a/b test", "validation", "falsifiable", "kill conditions"
  - **Required input**: Synthesis report from the-synthesist OR ideation report

**Typical Creative Triad Workflow**:
```
Problem → creative-catalyst/the-inventor → the-synthesist → the-architect-of-experiments → Validated Strategy
```

**Example Use Cases**:
- "Generate diverse ideas for improving mobile app retention" → creative-catalyst (oblique) OR the-inventor (systematic)
- "Synthesize 10 retention ideas into 3 strategic approaches" → the-synthesist
- "Design A/B tests to validate retention strategies" → the-architect-of-experiments
- "Explore new revenue models challenging subscription assumptions" → creative-catalyst
- "Systematically explore backend architecture approaches" → the-inventor

See [Creative Triad Guide](docs/creative-triad/README.md) for complete documentation and examples.

### Specialized Agents
- **Decision Support**: `the-critic` (technical decision analysis)
- **Legacy Systems**: `legacy-specialist` (migration, compatibility)
- **Functional Programming**: `functional-programmer` (Haskell, Clojure, F#)
- **Metaprogramming**: `metaprogramming-specialist` (Lisp, macros, DSLs)

### Contrarian Agents by Decision Type
Use contrarian agents to challenge assumptions and expose hidden risks, but match the contrarian to the decision domain:

**Technical/Architectural Decisions → `the-critic`**
- System architecture choices (microservices vs monolith)
- Technology stack selection (framework comparisons)
- Code quality and technical debt assessment
- Infrastructure and scalability decisions
- Security architecture review

**Examples:**
- "Should we use microservices or a modular monolith?" → `the-critic`
- "Is this codebase maintainable?" → `the-critic`
- "Will this architecture scale to 1M users?" → `the-critic`

**Business/Market Decisions → `the-realist` (Sprint 17)**
- Market sizing and revenue projections
- Competitive positioning and differentiation
- ROI calculations and business case validation
- Pricing strategy and willingness-to-pay
- Market timing and launch readiness

**Examples:**
- "Is there real demand for this product?" → `the-realist`
- "Can we compete with established players?" → `the-realist`
- "What's the actual TAM, not the fantasy number?" → `the-realist`

**Execution/Shipping Decisions → `the-pragmatist` (Sprint 17)**
- MVP scope definition and feature prioritization
- Deadline feasibility and resource allocation
- Build vs buy vs partner decisions
- Technical debt vs feature velocity tradeoffs
- Scope creep and requirement bloat prevention

**Examples:**
- "Can we ship this in 2 weeks?" → `the-pragmatist`
- "Should we build this feature or cut scope?" → `the-pragmatist`
- "Is this MVP too complex to launch quickly?" → `the-pragmatist`

**Multi-Contrarian Debates:**
When decisions span multiple domains, engage multiple contrarians sequentially or in parallel:
- Product launch decision: `the-critic` (technical readiness) + `the-realist` (market validation) + `the-pragmatist` (timeline feasibility)
- Architecture decision with business impact: `the-critic` (technical analysis) + `the-realist` (cost/ROI) + `the-pragmatist` (implementation time)
- See `project-orchestrator` for multi-contrarian coordination patterns

**Structured Output Contracts (Sprint 17 Enhancement):**
Contrarian agents now provide structured JSON outputs for improved interoperability and reduced variance:

- **the-critic** produces `DECISION_REPORT` with:
  - `dominant_axis`: The ONE factor that matters most in the decision
  - `alternatives`: Each option evaluated with evidence quality scores (0.0-1.0)
  - `false_tradeoffs_identified`: Binary choices that are actually false
  - `emotional_economy`: Hidden psychological forces (fear, ego, politics)
  - `required_proofs`: Specific evidence needed with acceptance criteria
  - `recommendation`: Choice with confidence score and invalidation triggers

- **the-skeptic** produces `AUTOMATION_ASSESSMENT` with:
  - `suitability_analysis`: Good-fit vs poor-fit indicators with severity ratings
  - `alternatives_explored`: Do-nothing, process improvement, better tools, hybrid, full automation
  - `hidden_costs_analysis`: Implementation, ongoing, opportunity, and risk costs quantified
  - `recommendation`: Verdict (do_not_automate, hybrid, pilot, proceed) with confidence
  - `decision_rules`: Executable gates (poor_fit >= 2, ROI < 3x → reject automation)

- **the-pragmatist** produces `DELIVERABILITY_ASSESSMENT` with:
  - `capacity_analysis`: Available hours = team_size × weeks × 40 × 0.65
  - `scope_analysis`: Required hours with 1.3x buffer multiplier
  - `mvp_bloat_analysis`: Features proposed vs truly minimum (bloat ratio)
  - `gates_triggered`: Mandate scope cut, extend timeline, or cancel project
  - `required_proofs`: Vertical slice demo, deploy pipeline proven with timelines

These structured outputs enable:
- Chaining contrarian agents (the-skeptic → the-pragmatist → the-critic)
- Automated validation of decision quality
- Consistent evidence requirements across decisions
- Reduced variance in recommendations

See `tests/seed_templates/` for golden JSON examples and validation rules.

## Development Commands

This project is a collection of markdown-based agent and command definitions. There are no build or test commands as this is a documentation/configuration repository for Claude Code agents.

### Working with the Repository

1. **Adding New Agents**: Use `agents/AGENT_TEMPLATE.md` as a starting point. See [Contributing Guide](docs/contributing.md) for detailed instructions.
2. **Adding Commands**: Create a new `.md` file in appropriate `commands/` subdirectory. Reference existing agents for orchestration.
3. **Testing Changes**: Run `python3 tools/validate_agents.py` and `python3 -m pytest tests/` before committing.
4. **Documentation**: See `docs/` for architecture, contributing guidelines, and professional standards.

## Important Patterns

### Multi-Agent Orchestration
- Use `project-orchestrator` for complex projects requiring multiple specialists
- Security and accessibility reviews should be included for production code
- Testing agents should validate all implementation work

### Agent Selection Keywords
- "new product", "startup idea" → `product-strategist`
- "React", "Next.js", "web app" → `full-stack-architect`
- **"React Native"** → `mobile-developer` (not `full-stack-architect`)
- "backend API", "REST API", "GraphQL", "microservices" → `backend-api-engineer`
- "server-side", "API design", "authentication" → `backend-api-engineer`
- "iOS", "Android", "mobile", "app store" → `mobile-developer`
- "AI", "LLM", "RAG" → `ai-ml-engineer`
- "security audit", "vulnerability" → `security-audit-specialist`
- "test", "QA" → `qa-test-engineer`
- "performance", "Core Web Vitals", "bundle size", "LCP", "optimize frontend" → `frontend-performance-specialist`
- "SEO", "search rankings", "meta tags", "Open Graph" → `seo-meta-optimizer`
- "SEO audit", "crawlability", "indexability", "sitemap" → `seo-technical-auditor`
- "SEO performance", "Core Web Vitals SEO", "mobile-first ranking" → `seo-performance-specialist`
- "keyword research", "search intent", "keyword clustering", "keyword gap" → `seo-keyword-strategist`
- "on-page SEO", "content optimization", "readability", "E-E-A-T", "featured snippets" → `seo-content-optimizer`
- "site architecture", "internal linking", "URL structure", "content silos", "topic clusters" → `seo-structure-architect`
- "CI/CD", "Docker", "Kubernetes", "deploy" → `devops-engineer`
- "systemd", "kernel", "firewall", "OS hardening" → `linux-sysadmin`
- "data pipeline", "ETL", "analytics" → `data-engineer`
- "documentation", "API docs", "user guide", "tutorial", "README" → `technical-writer`
- "developer docs", "SDK docs", "technical writing", "documentation site" → `technical-writer`
- "requirements", "BRD", "user stories", "stakeholder management" → `business-analyst`
- "business requirements", "process analysis", "use cases" → `business-analyst`
- "product roadmap", "feature prioritization", "OKR", "product strategy" → `product-manager`
- "backlog management", "sprint planning", "product metrics" → `product-manager`
- "code review" (domain-specific) → domain specialist
- "code review" (comprehensive) → `code-architect`
- "technical decision", "architecture review", "code quality critique" → `the-critic`
- "market validation", "ROI analysis", "competitive reality check" → `the-realist` (Sprint 17)
- "MVP scope", "deadline feasibility", "shipping decisions" → `the-pragmatist` (Sprint 17)
- "ideation", "generate ideas", "brainstorm", "breakthrough thinking", "oblique strategies" → `creative-catalyst`
- "diverse ideas", "systematic ideation", "diversity guarantees", "comprehensive exploration" → `the-inventor`
- "synthesize ideas", "strategic frames", "organize ideas", "false tradeoffs" → `the-synthesist`
- "experiments", "a/b test", "validation", "falsifiable", "kill conditions", "hypothesis testing" → `the-architect-of-experiments`

### Command Selection Keywords
- "cognitive load", "complexity metrics", "code comprehension", "developer ergonomics" → `/quality:cognitive-load-optimization`
- "technical debt cost", "debt quantification", "business impact", "debt measurement" → `/development:tech-debt-impact-measurement`
- "production learning", "postmortem automation", "incident insights", "organizational memory" → `/operations:production-learning-loop`
- "observability setup", "monitoring stack", "Prometheus", "Grafana", "distributed tracing" → `/operations:monitoring-stack-setup`
- "incident response", "war room", "on-call", "production incident", "incident management" → `/operations:incident-response-workflow`
- "disaster recovery", "business continuity", "RTO", "RPO", "DR planning" → `/operations:disaster-recovery-plan`
- "SOC 2 compliance", "compliance audit", "audit readiness", "security controls" → `/quality:compliance-audit-soc2`
- "database performance", "query optimization", "database tuning", "index optimization" → `/development:database-optimization`

### Creative & Artistic Agent Keywords
- "compose music", "orchestral score", "film score", "game music", "soundtrack" → `music-composer`
- "game mechanics", "level design", "player experience", "game balance", "progression" → `game-designer`
- "screenplay", "feature film", "script", "character development", "three-act structure" → `screenwriter`
- "interactive story", "branching narrative", "game lore", "dialogue tree", "quest design" → `narrative-designer`
- "sound effects", "foley", "spatial audio", "game audio", "FMOD", "Wwise" → `sound-designer`
- "camera work", "lighting design", "shot composition", "visual storytelling", "cinematography" → `cinematographer`
- "choreography", "dance", "movement design", "physical storytelling", "performance" → `choreographer`
- "poetry", "verse", "literary devices", "sonnet", "haiku", "free verse" → `poet`
- "macOS", "Homebrew", "Xcode", "Apple Silicon", "MDM", "Jamf", "Mac fleet" → `macos-specialist`
- "Windows Server", "Active Directory", "Group Policy", "PowerShell", "SCCM", "Intune" → `windows-specialist`
- "PostgreSQL", "query optimization", "EXPLAIN", "pgvector", "PostGIS", "TimescaleDB", "pg tuning" → `postgresql-expert`
- "Kafka", "stream processing", "event-driven", "Kafka Streams", "Kafka Connect", "ksqlDB" → `kafka-expert`
- "SRE", "error budget", "SLO", "SLI", "toil reduction", "reliability", "operational excellence" → `site-reliability-engineer`
- "supply chain security", "SBOM", "dependency scanning", "license compliance", "SLSA", "vulnerability management" → `dependency-security-specialist`
- "developer experience", "API usability", "SDK design", "DX metrics", "onboarding", "API ergonomics" → `developer-experience-engineer`
- "SOC 2", "HIPAA", "PCI-DSS", "GDPR", "compliance automation", "audit readiness", "continuous compliance" → `compliance-automation-engineer`
- "multi-model LLM", "model routing", "LLM cost optimization", "fallback chains", "LiteLLM", "vendor-neutral AI" → `llm-integration-architect`
- "prompt engineering", "chain-of-thought", "few-shot learning", "prompt optimization", "constitutional AI", "system prompts" → `prompt-engineering-specialist`
- "RAG", "vector database", "retrieval augmented generation", "semantic search", "document chunking", "hybrid search", "reranking" → `rag-systems-engineer`
- "fine-tuning", "LoRA", "QLoRA", "LLM training", "dataset curation", "RLHF", "DPO", "custom models" → `fine-tuning-specialist`
- "LLM inference", "quantization", "vLLM", "TensorRT-LLM", "llama.cpp", "GPU optimization", "self-hosted LLM" → `inference-optimization-specialist`
- "image generation", "Stable Diffusion", "DALL-E", "Midjourney", "LoRA training", "ControlNet", "ComfyUI", "diffusion models" → `generative-image-specialist`

### Anti-Patterns to Avoid
- Don't use overlapping agents simultaneously (e.g., multiple code reviewers)
- Don't skip security/accessibility for production deployments
- Don't implement AI features without `ai-ml-engineer`
- Don't start complex projects without `project-orchestrator`
- Don't use `full-stack-architect` for React Native (use `mobile-developer`)
- Don't use `devops-engineer` for OS-level configuration (use `linux-sysadmin`)
- Don't mix domain review and holistic review (use sequential: specialist → `code-architect`)

### Command Platform Improvements (Recent Updates)
**Consolidation for Coherence:**
- Quality commands consolidated: `code-review` (from 3), `testing-strategy` (from 3), `performance-optimization` (from 3)
- Development commands consolidated: `database-optimization` (merged with database-design improvements)
- Removed redundant `database-review` command (integrated into `database-optimization` + `infrastructure-audit`)
- Result: 58 total commands (down from previous sprawl), improved discoverability, clearer selection

**Strategic New Commands:**
- **Tier 1 Innovations** (industry-first capabilities):
  - `/quality:cognitive-load-optimization` - Measurable cognitive complexity reduction
  - `/operations:production-learning-loop` - Self-improving organizational memory
  - `/development:tech-debt-impact-measurement` - Empirical debt cost quantification
- **High-Priority Operations** (production excellence):
  - `/operations:monitoring-stack-setup` - Complete observability implementation
  - `/operations:incident-response-workflow` - Production incident management
  - `/operations:disaster-recovery-plan` - Business continuity planning
  - `/quality:compliance-audit-soc2` - SOC 2 compliance preparation

### Agent Boundary Clarifications

For detailed information on agent boundaries and delegation protocols, see [Agent Boundaries & Delegation Protocols](docs/architecture.md#agent-boundaries--delegation-protocols).

**Key Boundaries**:
1. **React Native**: Always `mobile-developer`, never `full-stack-architect`
2. **Backend APIs**: `backend-api-engineer` (backend-only) vs `full-stack-architect` (full-stack)
3. **Code Review**: Domain specialist first, then `code-architect` for holistic review
4. **Infrastructure**: `devops-engineer` (app-level) vs `linux-sysadmin` (OS-level)
5. **Database**: `data-engineer` (analytics/pipelines) vs `database-admin` (operations - Sprint 2)

## Git Workflow

The repository uses standard git branching:
- Main branch: `master`
- Feature branches follow pattern: `kf/feature-name`
- Commits should be descriptive and focused on agent/command improvements