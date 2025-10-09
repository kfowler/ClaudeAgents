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

### Specialized Agents
- **Decision Support**: `the-critic` (technical decision analysis)
- **Legacy Systems**: `legacy-specialist` (migration, compatibility)
- **Functional Programming**: `functional-programmer` (Haskell, Clojure, F#)
- **Metaprogramming**: `metaprogramming-specialist` (Lisp, macros, DSLs)

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