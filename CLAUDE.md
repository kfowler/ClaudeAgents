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
- **Mobile Apps**: `mobile-developer` (iOS, Android, React Native, Flutter)
- **AI/ML Features**: `ai-ml-engineer` (LLM integration, RAG systems, vector databases)
- **Database/Data**: `data-engineer` (PostgreSQL, data pipelines, analytics)
- **Infrastructure**: `devops-engineer` (CI/CD, Docker, cloud deployment)
- **Systems Programming**: `systems-engineer` (Rust, C++, Go, performance optimization)

### Quality & Security Agents
- **Security**: `security-audit-specialist` (vulnerability assessment, compliance)
- **Testing**: `qa-test-engineer` (test strategies, implementation)
- **Accessibility**: `accessibility-expert` (WCAG compliance, inclusive design)
- **Code Quality**: `code-architect` (architecture review, maintainability)

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
- "iOS", "Android", "mobile" → `mobile-developer`
- "AI", "LLM", "RAG" → `ai-ml-engineer`
- "security audit", "vulnerability" → `security-audit-specialist`
- "test", "QA" → `qa-test-engineer`

### Anti-Patterns to Avoid
- Don't use overlapping agents simultaneously (e.g., multiple code reviewers)
- Don't skip security/accessibility for production deployments
- Don't implement AI features without `ai-ml-engineer`
- Don't start complex projects without `project-orchestrator`

## Git Workflow

The repository uses standard git branching:
- Main branch: `master`
- Feature branches follow pattern: `kf/feature-name`
- Commits should be descriptive and focused on agent/command improvements