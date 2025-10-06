# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains specialized AI agent definitions and commands for Claude Code. It provides a comprehensive ecosystem of 25+ specialized agents that can autonomously handle complex software development tasks across multiple domains including web development, mobile apps, AI/ML integration, security, and more.

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
- **AI/ML Features**: `ai-ml-engineer` (LLM integration, RAG systems, vector databases)
- **Database/Data**: `data-engineer` (data pipelines, analytics, OLAP workloads)
  - **Note**: Operational database management (OLTP, tuning, backups) will be handled by `database-admin` (Sprint 2)
- **Application Infrastructure**: `devops-engineer` (CI/CD, Docker, Kubernetes, cloud deployment)
  - **Note**: For OS-level configuration (systemd, kernel, firewall), use `linux-sysadmin`
- **System Administration**: `linux-sysadmin` (OS hardening, system services, bare metal/VM setup)
- **Systems Programming**: `systems-engineer` (Rust, C++, Go, performance optimization)

### Quality & Security Agents
- **Security**: `security-audit-specialist` (vulnerability assessment, compliance)
- **Testing**: `qa-test-engineer` (test strategies, implementation)
- **Accessibility**: `accessibility-expert` (WCAG compliance, inclusive design)
- **Code Quality**: `code-architect` (holistic architecture review, maintainability, readability)
  - **Note**: For domain-specific code review, use the domain specialist first, then `code-architect` for comprehensive analysis

### Specialized Agents
- **Decision Support**: `the-critic` (technical decision analysis)
- **Legacy Systems**: `legacy-specialist` (migration, compatibility)
- **Functional Programming**: `functional-programmer` (Haskell, Clojure, F#)
- **Metaprogramming**: `metaprogramming-specialist` (Lisp, macros, DSLs)
- **Creative**: `digital-artist`, `video-director`, `3d-modeler`, `comedy-writer`, `audio-engineer`, `tv-writer`

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
- "CI/CD", "Docker", "Kubernetes", "deploy" → `devops-engineer`
- "systemd", "kernel", "firewall", "OS hardening" → `linux-sysadmin`
- "data pipeline", "ETL", "analytics" → `data-engineer`
- "code review" (domain-specific) → domain specialist
- "code review" (comprehensive) → `code-architect`

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