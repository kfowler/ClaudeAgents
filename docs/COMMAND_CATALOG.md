# Command Catalog

**Comprehensive catalog of all 59 AI agent workflows for Claude Code**

This catalog provides a searchable index of all available workflows that orchestrate specialized AI agents to solve complex development tasks. Use this guide to quickly find the right command for your needs, understand what each workflow delivers, and discover powerful multi-command patterns.

## Quick Category Navigation

Jump to any category:
- [Development Commands](#development-commands) (9 commands)
- [Quality Commands](#quality-commands) (10 commands)
- [Operations Commands](#operations-commands) (4 commands)
- [Deployment Commands](#deployment-commands) (4 commands)
- [Specialized Commands](#specialized-commands) (10 commands)
- [Workflow Commands](#workflow-commands) (8 commands)
- [SEO Commands](#seo-commands) (4 commands)
- [Business Commands](#business-commands) (2 commands)
- [Vertical Packages](#vertical-packages) (3 commands)
- [Creative Commands](#creative-commands) (5 commands)

---

## Master Command Table

| Command | Category | Description | Primary Agents | Duration | Use When |
|---------|----------|-------------|----------------|----------|----------|
| `/api-design` | Development | Complete API design (REST/GraphQL) with OpenAPI specs, versioning, database schema | full-stack-architect, data-engineer | 4-6h | Designing new REST or GraphQL APIs with database integration |
| `/database-design` | Development | Comprehensive database schema design with migrations, indexing, performance optimization | data-engineer, full-stack-architect | 4-6h | Creating production-ready database schema from scratch |
| `/database-optimization` | Development | Database optimization and quality review: performance tuning, security hardening, schema quality | postgresql-expert, data-engineer, devops-engineer, security-audit-specialist | 8-12h | Existing databases need performance tuning, security hardening, quality assessment |
| `/development:tech-debt-impact-measurement` | Development | Empirical tech debt cost measurement with velocity impact, incident correlation, maintenance cost | code-architect, data-engineer, product-manager, devops-engineer | 8-14h | Quantifying business impact of technical debt for executive buy-in |
| `/cross-paradigm-translator` | Development | Translate concepts between programming paradigms (functional, OOP, procedural) | functional-programmer, metaprogramming-specialist | 2-4h | Understanding unfamiliar paradigms or designing polyglot systems |
| `/debug-help` | Development | Systematic debugging assistance with root cause analysis and solution strategies | systems-engineer, code-architect | 1-3h | Encountering complex bugs or issues needing investigation |
| `/documentation-generator` | Development | Generate comprehensive documentation (API, code, user, development) | technical-writer, full-stack-architect | 2-4h | Creating or updating project documentation |
| `/git-workflow` | Development | Git operations and workflow management (branching, commits, PRs, conflict resolution) | code-architect | 1-2h | Managing git operations and improving workflow |
| `/refactor-component` | Development | Component refactoring for improved code structure, maintainability, and testability | code-architect, qa-test-engineer | 2-6h | Improving existing components or modules |
| `/quality:code-review` | Quality | Comprehensive code review with configurable depth: component, quality, architecture | code-architect, security-audit-specialist, accessibility-expert, qa-test-engineer, the-critic | 2-8h | Pull request reviews, pre-deployment validation, quality audits |
| `/quality:cognitive-load-optimization` | Quality | Quantify mental effort required to understand code, reduce onboarding time 40-60% | code-architect, qa-test-engineer, technical-writer | 6-10h | High onboarding friction, complex codebase comprehension issues |
| `/quality:compliance-audit-soc2` | Quality | SOC2 Type II compliance preparation with automated evidence collection | compliance-automation-engineer, security-audit-specialist, technical-writer, devops-engineer | 20-30h initial | Preparing for SOC2 audit or establishing continuous compliance |
| `/dependency-audit` | Quality | Analyze and manage dependencies: security vulnerabilities, updates, optimization | security-audit-specialist, code-architect | 1-3h | Dependency updates, security audits, bundle optimization |
| `/infrastructure-audit` | Quality | Comprehensive infrastructure assessment: IaC, cloud architecture, security, cost optimization | infrastructure-as-code-specialist, cloud-architect, security-audit-specialist, devops-engineer | 16-48h | Quarterly infrastructure reviews, pre-migration assessment, compliance audits |
| `/performance-optimization` | Quality | Multi-phase performance optimization: audit, analysis, optimization, validation across all layers | frontend-performance-specialist, seo-performance-specialist, full-stack-architect, systems-engineer, data-engineer, devops-engineer, qa-test-engineer | 8-12h | Performance issues, preparing for traffic growth, cost optimization |
| `/production-readiness` | Quality | Pre-deployment comprehensive checklist: security, performance, testing, monitoring | security-audit-specialist, accessibility-expert, frontend-performance-specialist, devops-engineer, qa-test-engineer | 4-6h | Final validation before major production deployments |
| `/security-audit` | Quality | Deep security assessment with vulnerability scanning and compliance validation | security-audit-specialist, devops-engineer | 4-6h | Security concerns, compliance requirements, post-incident analysis |
| `/testing-strategy` | Quality | Comprehensive testing strategy: unit, integration, E2E, performance, security testing | qa-test-engineer, full-stack-architect, data-engineer, devops-engineer | 4-6h | Establishing or improving testing approach for projects |
| `/quality:architecture-review` | Quality | Comprehensive architectural assessment with strategic recommendations | code-architect, the-critic, security-audit-specialist, accessibility-expert, qa-test-engineer | 6-8h | Evaluating system design, identifying structural issues, strategic planning |
| `/operations:production-learning-loop` | Operations | Continuous production learning with incident analysis and improvement tracking | devops-engineer, code-architect, qa-test-engineer | Continuous | Establishing continuous improvement culture from production insights |
| `/operations:monitoring-stack-setup` | Operations | Complete observability stack: metrics, logging, tracing, alerting | devops-engineer, systems-engineer | 6-8h | Setting up or upgrading monitoring infrastructure |
| `/operations:incident-response-workflow` | Operations | Incident response procedures: detection, triage, resolution, post-mortem | devops-engineer, security-audit-specialist, code-architect | 2-4h setup | Establishing or improving incident response capabilities |
| `/operations:disaster-recovery-plan` | Operations | Disaster recovery planning: RTO/RPO, backup strategy, failover procedures | devops-engineer, data-engineer, security-audit-specialist | 6-8h | Creating or validating disaster recovery capabilities |
| `/deploy-prep` | Deployment | Comprehensive deployment preparation orchestrating multiple agents for production readiness | qa-test-engineer, security-audit-specialist, devops-engineer, systems-engineer, accessibility-expert | 4-8h | Major production deployments requiring thorough validation |
| `/dokku-deploy` | Deployment | Dokku deployment to Raspberry Pi server with configuration management | devops-engineer, linux-sysadmin | 1-2h | Deploying to personal Dokku server on Pi |
| `/orb-stack` | Deployment | OrbStack container and development environment management | devops-engineer | 1-2h | Managing OrbStack containers and development databases |
| `/ssh-pi-ops` | Deployment | SSH operations on Raspberry Pi deployment server | linux-sysadmin, devops-engineer | 1-2h | Managing Pi server operations and maintenance |
| `/lisp-macro-workshop` | Specialized | Lisp metaprogramming and macro development workshop | metaprogramming-specialist, functional-programmer | 4-8h | Learning or implementing Lisp macros and metaprogramming |
| `/python-data-pipeline` | Specialized | Python data pipeline development with modern tooling | data-engineer, backend-api-engineer | 4-6h | Building ETL/ELT pipelines with Python |
| `/python-modern-stack` | Specialized | Modern Python development stack setup and best practices | backend-api-engineer, devops-engineer | 2-4h | Starting new Python projects with modern tooling |
| `/python-uv-workflow` | Specialized | Python UV package manager workflow and optimization | backend-api-engineer | 1-2h | Using UV for fast Python package management |
| `/python-web-api` | Specialized | Python web API development (FastAPI, Flask, Django) | backend-api-engineer, data-engineer | 4-6h | Building Python web APIs |
| `/python-web-scraping` | Specialized | Web scraping with Python (Beautiful Soup, Scrapy, Playwright) | backend-api-engineer, data-engineer | 2-4h | Extracting data from websites |
| `/roswell` | Specialized | Common Lisp development with Roswell tooling | functional-programmer, metaprogramming-specialist | 2-4h | Common Lisp project setup and development |
| `/rust-cargo` | Specialized | Rust development with Cargo ecosystem | systems-engineer, backend-api-engineer | 2-4h | Rust project development and tooling |
| `/safari-web-extension` | Specialized | Safari web extension development for macOS/iOS | mobile-developer, full-stack-architect | 6-10h | Building Safari browser extensions |
| `/xcode-power-tools` | Specialized | Advanced Xcode development and tooling | mobile-developer, systems-engineer | 2-4h | iOS/macOS development with Xcode optimization |
| `/workflows:ai-agent-council` | Workflow | Multi-agent council for complex decisions with diverse perspectives | the-critic, product-strategist, security-audit-specialist, code-architect | 2-4h | Complex technical decisions requiring diverse expert input |
| `/workflows:ai-code-battle` | Workflow | Competitive coding between AI agents for optimal solutions | code-architect, functional-programmer, systems-engineer | 2-3h | Exploring multiple solution approaches for challenging problems |
| `/workflows:crisis-manager` | Workflow | Crisis management workflow for critical incidents | devops-engineer, security-audit-specialist, product-manager, code-architect | 1-4h | Critical production incidents requiring coordinated response |
| `/workflows:team-comm-hub` | Workflow | Team communication hub orchestration | product-manager, code-architect, devops-engineer | Continuous | Improving team collaboration and communication |
| `/workflows:microservices-architecture` | Workflow | Complete microservices architecture design with service mesh and observability | project-orchestrator, full-stack-architect, data-engineer, devops-engineer | 12-20h | Designing distributed systems with microservices |
| `/workflows:debate` | Workflow | Structured debate between AI agents on technical decisions | the-critic, code-architect, security-audit-specialist | 1-2h | Evaluating trade-offs in technical decisions |
| `/workflows:platform-migration` | Workflow | Platform migration planning and execution | legacy-specialist, full-stack-architect, devops-engineer, data-engineer | 16-40h | Migrating between platforms or major technology changes |
| `/workflows:streaming-architecture` | Workflow | Real-time streaming architecture design (Kafka, event-driven) | full-stack-architect, data-engineer, devops-engineer | 8-16h | Designing event-driven or streaming data systems |
| `/seo:comprehensive-seo-audit` | SEO | Complete SEO audit combining all SEO specialists | seo-meta-optimizer, seo-technical-auditor, seo-performance-specialist, seo-keyword-strategist, seo-content-optimizer, seo-structure-architect | 8-12h | Comprehensive SEO assessment and optimization |
| `/seo:content-optimization` | SEO | On-page content optimization for search rankings | seo-content-optimizer, seo-keyword-strategist | 3-5h | Optimizing page content for SEO and user engagement |
| `/seo:keyword-research` | SEO | Keyword research and search intent analysis | seo-keyword-strategist, seo-content-optimizer | 2-4h | Planning content strategy based on search demand |
| `/seo:site-architecture-audit` | SEO | Site architecture and internal linking optimization | seo-structure-architect, seo-technical-auditor | 4-6h | Improving site structure for search engines and users |
| `/business:product-roadmap` | Business | Product roadmap planning with feature prioritization and OKRs | product-manager, product-strategist, business-analyst | 6-10h | Strategic product planning and roadmap development |
| `/business:requirements-analysis` | Business | Business requirements gathering and documentation | business-analyst, product-manager | 4-8h | Defining project requirements and specifications |
| `/vertical:ecommerce-platform` | Vertical | Complete e-commerce platform development | full-stack-architect, backend-api-engineer, frontend-performance-specialist, security-audit-specialist, devops-engineer | 40-80h | Building full e-commerce solutions |
| `/vertical:saas-mvp` | Vertical | SaaS MVP development from concept to launch | product-strategist, full-stack-architect, backend-api-engineer, devops-engineer, security-audit-specialist | 40-120h | Launching new SaaS products |
| `/vertical:fintech-compliance` | Vertical | Fintech application with regulatory compliance | security-audit-specialist, compliance-automation-engineer, backend-api-engineer, data-engineer | 60-120h | Building compliant fintech applications |
| `/creative:film-production` | Creative | Film production workflow from concept to post-production | video-director, digital-artist, audio-engineer, tv-writer | 20-60h | Video/film production projects |
| `/creative:game-development` | Creative | Game development across design, development, art, audio | full-stack-architect, digital-artist, audio-engineer, systems-engineer | 80-200h | Creating games from concept to launch |
| `/creative:album-production` | Creative | Music album production workflow | audio-engineer, digital-artist | 40-80h | Producing music albums |
| `/creative:poetry-collection` | Creative | Poetry collection creation and publication | comedy-writer, technical-writer | 10-20h | Writing and publishing poetry |
| `/creative:dance-performance` | Creative | Dance performance choreography and production | video-director, audio-engineer | 20-40h | Choreographing and producing dance performances |

---

## Development Commands

**9 commands** focused on software development, architecture, and code quality

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/api-design` | Complete API design (REST/GraphQL) with OpenAPI specs, versioning, authentication, database schema integration | full-stack-architect, data-engineer | 4-6 hours | Designing new production-ready APIs with proper documentation and database integration |
| `/database-design` | Comprehensive database schema design with migrations, indexing strategy, performance optimization, disaster recovery | data-engineer, full-stack-architect | 4-6 hours | Creating new database schemas optimized for performance and scalability |
| `/database-optimization` | Existing database optimization: performance tuning, security hardening, schema quality, operational excellence | postgresql-expert, data-engineer, devops-engineer, security-audit-specialist | 8-12 hours | Improving performance of existing databases (50-90% latency reduction typical) |
| `/development:tech-debt-impact-measurement` | Quantify tech debt business impact: velocity loss, incident correlation, maintenance costs with ROI calculations | code-architect, data-engineer, product-manager, devops-engineer | 8-14 hours initial | Building executive business case for refactoring investments |
| `/cross-paradigm-translator` | Translate patterns between programming paradigms (functional ↔ OOP ↔ procedural) | functional-programmer, metaprogramming-specialist | 2-4 hours | Learning unfamiliar paradigms or designing polyglot systems |
| `/debug-help` | Systematic debugging with error analysis, root cause identification, and solution strategies | systems-engineer, code-architect | 1-3 hours | Complex bugs requiring methodical investigation |
| `/documentation-generator` | Generate comprehensive documentation: API docs, code comments, user guides, architecture decisions | technical-writer, full-stack-architect | 2-4 hours | Creating or updating project documentation |
| `/git-workflow` | Git operations: branching, commits, PRs, conflict resolution, code review preparation | code-architect | 1-2 hours | Improving git workflow and managing complex git operations |
| `/refactor-component` | Component refactoring for improved structure, maintainability, testability, and performance | code-architect, qa-test-engineer | 2-6 hours | Improving existing code quality and reducing technical debt |

### Featured Development Command: `/api-design`

**What it does:** Orchestrates complete API development from requirements analysis through OpenAPI specification, database schema design, security implementation, and deployment planning. Delivers production-ready API designs with proper authentication, versioning, documentation, and performance optimization.

**When to use:**
- Starting new REST or GraphQL API development
- Modernizing existing APIs with proper documentation
- Need database schema designed alongside API
- Require security and performance planning upfront
- Building APIs for mobile/web client consumption

**Example usage:**
```bash
# Design REST API for e-commerce platform
/api-design --type=rest --domain=ecommerce

# Design GraphQL API with real-time subscriptions
/api-design --type=graphql --realtime=true --database=postgresql
```

**Expected outcomes:**
- OpenAPI 3.0 spec (REST) or GraphQL schema with complete documentation
- Database migrations ready for execution with rollback capability
- Security implementation plan (authentication, authorization, input validation)
- Performance optimization strategy (caching, rate limiting, pagination)
- Testing strategy with contract tests
- 30-50% faster development with clear API design

**Related commands:**
- `/database-design` - Deep-dive on database schema before API design
- `/security-audit` - Security review after API implementation
- `/documentation-generator` - Auto-generate API client documentation

---

## Quality Commands

**10 commands** ensuring code quality, security, performance, and compliance

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/quality:code-review` | Configurable depth code review: component (quick), quality (maintainability), architecture (system-wide) | code-architect, security-audit-specialist, accessibility-expert, qa-test-engineer, the-critic | 2-8 hours | Pull request reviews, quality audits, pre-deployment validation |
| `/quality:cognitive-load-optimization` | Quantify mental effort to understand code, reduce onboarding time 40-60%, improve developer productivity 25-45% | code-architect, qa-test-engineer, technical-writer | 6-10 hours | High onboarding friction, complex codebase, low developer productivity |
| `/quality:compliance-audit-soc2` | SOC2 Type II compliance: gap analysis, control implementation, automated evidence collection, audit preparation | compliance-automation-engineer, security-audit-specialist, technical-writer, devops-engineer | 20-30 hours initial | Preparing for SOC2 audit, winning enterprise customers, reducing cyber insurance costs |
| `/dependency-audit` | Dependency analysis: security vulnerabilities, outdated packages, license issues, bundle optimization | security-audit-specialist, code-architect | 1-3 hours | Security audits, dependency updates, bundle size reduction |
| `/infrastructure-audit` | Comprehensive infrastructure assessment: IaC quality, cloud architecture, security, cost optimization, reliability | infrastructure-as-code-specialist, cloud-architect, security-audit-specialist, devops-engineer | 16-48 hours | Quarterly reviews, pre-migration assessment, compliance audits, cost optimization |
| `/performance-optimization` | Multi-phase optimization (audit → analysis → optimization → validation) across frontend, backend, database, infrastructure | frontend-performance-specialist, seo-performance-specialist, full-stack-architect, systems-engineer, data-engineer, devops-engineer, qa-test-engineer | 8-12 hours | Performance issues, traffic growth preparation, cost reduction (typical: 50-80% latency reduction, 20-40% cost reduction) |
| `/production-readiness` | Pre-deployment checklist: security, accessibility, performance, testing, monitoring, disaster recovery | security-audit-specialist, accessibility-expert, frontend-performance-specialist, devops-engineer, qa-test-engineer | 4-6 hours | Final validation before major production deployments |
| `/security-audit` | Deep security assessment: vulnerability scanning, penetration testing simulation, compliance validation | security-audit-specialist, devops-engineer | 4-6 hours | Security concerns, compliance requirements, post-incident analysis |
| `/testing-strategy` | Comprehensive testing strategy: unit, integration, E2E, performance, security with tool recommendations | qa-test-engineer, full-stack-architect, data-engineer, devops-engineer | 4-6 hours | Establishing or improving testing approach for projects |
| `/quality:architecture-review` | System-wide architectural assessment with strategic recommendations and evolution roadmap | code-architect, the-critic, security-audit-specialist, accessibility-expert, qa-test-engineer | 6-8 hours | Evaluating system design, identifying structural issues, planning architectural evolution |

### Featured Quality Command: `/performance-optimization`

**What it does:** Four-phase comprehensive performance optimization coordinating 7 specialized agents across all application layers. Delivers measurable improvements in page load time, API latency, database queries, infrastructure costs, and business metrics (conversion rate, revenue).

**When to use:**
- Page load times >3 seconds causing user drop-off
- API response times >300ms impacting user experience
- Database queries causing performance bottlenecks
- Infrastructure costs higher than necessary
- Preparing for traffic growth (Black Friday, product launch)
- Poor Core Web Vitals affecting SEO rankings

**Example usage:**
```bash
# Full performance optimization workflow
/performance-optimization

# Focus on frontend and database only
/performance-optimization --layers=frontend,database

# Quick audit to identify bottlenecks
/performance-optimization --phase=audit
```

**Expected outcomes:**
- **Page Load Time:** 50-70% reduction (6.8s → 2.1s typical)
- **API Latency (p95):** 60-80% reduction (320ms → 85ms typical)
- **Database Queries (p95):** 50-85% reduction (620ms → 95ms typical)
- **Infrastructure Costs:** 20-40% reduction
- **Conversion Rate:** 5-15% improvement
- **ROI:** 10-17x in first year (typical: $600K-$2M revenue impact)

**Related commands:**
- `/quality:architecture-review` - Identify architectural performance issues
- `/database-optimization` - Deep database performance tuning
- `/infrastructure-audit` - Infrastructure cost optimization

---

## Operations Commands

**4 commands** for operational excellence, monitoring, and incident management

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/operations:production-learning-loop` | Continuous improvement from production: incident analysis, pattern detection, proactive improvements | devops-engineer, code-architect, qa-test-engineer | Continuous | Establishing learning culture from production insights |
| `/operations:monitoring-stack-setup` | Complete observability: metrics (Prometheus), logging (ELK), tracing (Jaeger), alerting (PagerDuty) | devops-engineer, systems-engineer | 6-8 hours | Setting up or upgrading monitoring infrastructure |
| `/operations:incident-response-workflow` | Incident response: detection, triage, resolution, communication, post-mortem | devops-engineer, security-audit-specialist, code-architect | 2-4 hours setup | Establishing incident response capabilities |
| `/operations:disaster-recovery-plan` | Disaster recovery: RTO/RPO definition, backup strategy, failover procedures, DR testing | devops-engineer, data-engineer, security-audit-specialist | 6-8 hours | Creating or validating disaster recovery capabilities |

### Featured Operations Command: `/operations:monitoring-stack-setup`

**What it does:** Deploys comprehensive observability stack with metrics collection (Prometheus), centralized logging (ELK/Loki), distributed tracing (Jaeger), and intelligent alerting (PagerDuty). Includes dashboards for visualization and runbooks for incident response.

**When to use:**
- No monitoring infrastructure currently in place
- Existing monitoring inadequate (missing metrics, poor visibility)
- Preparing for production launch
- Need to improve MTTR (Mean Time To Resolve)
- Compliance requirements for audit logging
- Scaling challenges requiring better observability

**Example usage:**
```bash
# Full observability stack setup
/operations:monitoring-stack-setup

# Focus on metrics and alerting only
/operations:monitoring-stack-setup --focus=metrics,alerting

# Kubernetes-specific monitoring
/operations:monitoring-stack-setup --platform=kubernetes
```

**Expected outcomes:**
- Prometheus metrics collection across all services
- Grafana dashboards for real-time visualization
- Centralized logging with 90-day retention
- Distributed tracing for microservices debugging
- PagerDuty alerting with on-call rotation
- MTTR reduction: 50-70% (4 hours → 1.2 hours typical)
- Incident detection: 80% faster (proactive vs. reactive)

**Related commands:**
- `/operations:incident-response-workflow` - Use monitoring data for incident management
- `/operations:production-learning-loop` - Continuous improvement from metrics
- `/quality:production-readiness` - Pre-deployment monitoring validation

---

## Deployment Commands

**4 commands** for deployment preparation and execution

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/deploy-prep` | Comprehensive deployment preparation: testing, security, infrastructure, performance validation | qa-test-engineer, security-audit-specialist, devops-engineer, systems-engineer, accessibility-expert | 4-8 hours | Major production deployments requiring thorough validation |
| `/dokku-deploy` | Dokku deployment to Raspberry Pi: pre-deployment checks, deployment execution, rollback procedures | devops-engineer, linux-sysadmin | 1-2 hours | Deploying to personal Dokku server on Raspberry Pi |
| `/orb-stack` | OrbStack container management: PostgreSQL containers, development databases, environment sync | devops-engineer | 1-2 hours | Managing local OrbStack development environments |
| `/ssh-pi-ops` | SSH operations on Pi server: system monitoring, Dokku management, database operations, nginx configuration | linux-sysadmin, devops-engineer | 1-2 hours | Managing Raspberry Pi deployment server operations |

---

## Specialized Commands

**10 commands** for language-specific and specialized development tasks

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/lisp-macro-workshop` | Lisp metaprogramming workshop: macro development, DSL creation, code generation | metaprogramming-specialist, functional-programmer | 4-8 hours | Learning Lisp macros or implementing metaprogramming solutions |
| `/python-data-pipeline` | Python data pipeline development: ETL/ELT, data processing, Apache Airflow, Pandas | data-engineer, backend-api-engineer | 4-6 hours | Building data pipelines with Python |
| `/python-modern-stack` | Modern Python development: Poetry/UV, pytest, Black, mypy, pre-commit hooks | backend-api-engineer, devops-engineer | 2-4 hours | Starting new Python projects with best practices |
| `/python-uv-workflow` | Python UV package manager: ultra-fast dependency resolution and virtual environment management | backend-api-engineer | 1-2 hours | Using UV for Python package management |
| `/python-web-api` | Python web API development: FastAPI, Flask, Django with async support and database integration | backend-api-engineer, data-engineer | 4-6 hours | Building Python web APIs and microservices |
| `/python-web-scraping` | Web scraping with Python: Beautiful Soup, Scrapy, Playwright for dynamic content | backend-api-engineer, data-engineer | 2-4 hours | Extracting data from websites at scale |
| `/roswell` | Common Lisp development with Roswell: project setup, dependency management, deployment | functional-programmer, metaprogramming-specialist | 2-4 hours | Common Lisp project development |
| `/rust-cargo` | Rust development with Cargo: project setup, dependency management, performance optimization | systems-engineer, backend-api-engineer | 2-4 hours | Rust systems programming and development |
| `/safari-web-extension` | Safari web extension development: macOS/iOS extensions, WebExtensions API, App Store submission | mobile-developer, full-stack-architect | 6-10 hours | Building Safari browser extensions |
| `/xcode-power-tools` | Advanced Xcode development: build optimization, debugging, instruments profiling, SwiftUI/UIKit | mobile-developer, systems-engineer | 2-4 hours | iOS/macOS development with Xcode |

---

## Workflow Commands

**8 commands** for complex multi-agent orchestration workflows

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/workflows:ai-agent-council` | Multi-agent council for complex decisions: diverse perspectives, debate, consensus building | the-critic, product-strategist, security-audit-specialist, code-architect | 2-4 hours | Complex technical decisions requiring expert input from multiple domains |
| `/workflows:ai-code-battle` | Competitive coding between AI agents: multiple solution approaches, performance comparison | code-architect, functional-programmer, systems-engineer | 2-3 hours | Exploring optimal solutions for challenging algorithmic problems |
| `/workflows:crisis-manager` | Crisis management for critical incidents: coordinated response, stakeholder communication, resolution | devops-engineer, security-audit-specialist, product-manager, code-architect | 1-4 hours | Critical production incidents requiring immediate coordinated response |
| `/workflows:team-comm-hub` | Team communication orchestration: async communication, decision tracking, knowledge sharing | product-manager, code-architect, devops-engineer | Continuous | Improving team collaboration and communication patterns |
| `/workflows:microservices-architecture` | Complete microservices design: service mesh, API gateway, observability, deployment strategy | project-orchestrator, full-stack-architect, data-engineer, devops-engineer | 12-20 hours | Designing distributed systems with microservices architecture |
| `/workflows:debate` | Structured debate between AI agents: pros/cons analysis, trade-off evaluation, recommendation | the-critic, code-architect, security-audit-specialist | 1-2 hours | Evaluating technical trade-offs and making informed decisions |
| `/workflows:platform-migration` | Platform migration: legacy assessment, migration planning, risk mitigation, execution | legacy-specialist, full-stack-architect, devops-engineer, data-engineer | 16-40 hours | Migrating between platforms or major technology changes |
| `/workflows:streaming-architecture` | Real-time streaming architecture: Kafka, event-driven systems, stream processing | full-stack-architect, data-engineer, devops-engineer | 8-16 hours | Designing event-driven or real-time streaming data systems |

---

## SEO Commands

**4 commands** for search engine optimization across all dimensions

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/seo:comprehensive-seo-audit` | Complete SEO audit: technical, on-page, performance, keywords, content, architecture | seo-meta-optimizer, seo-technical-auditor, seo-performance-specialist, seo-keyword-strategist, seo-content-optimizer, seo-structure-architect | 8-12 hours | Comprehensive SEO assessment and improvement strategy |
| `/seo:content-optimization` | On-page content optimization: keywords, readability, E-E-A-T, featured snippets, user engagement | seo-content-optimizer, seo-keyword-strategist | 3-5 hours | Optimizing existing content for better search rankings and user engagement |
| `/seo:keyword-research` | Keyword research: search demand, search intent, competitive analysis, keyword clustering | seo-keyword-strategist, seo-content-optimizer | 2-4 hours | Planning content strategy based on actual search demand |
| `/seo:site-architecture-audit` | Site architecture optimization: URL structure, internal linking, content silos, topic clusters | seo-structure-architect, seo-technical-auditor | 4-6 hours | Improving site structure for search engines and user navigation |

---

## Business Commands

**2 commands** for business strategy, requirements, and planning

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/business:product-roadmap` | Product roadmap planning: feature prioritization, OKRs, metrics, timeline | product-manager, product-strategist, business-analyst | 6-10 hours | Strategic product planning and quarterly roadmap development |
| `/business:requirements-analysis` | Business requirements gathering: stakeholder interviews, BRD, user stories, acceptance criteria | business-analyst, product-manager | 4-8 hours | Defining project requirements and specifications for development |

---

## Vertical Packages

**3 commands** for complete vertical solutions (e-commerce, SaaS, fintech)

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/vertical:ecommerce-platform` | Complete e-commerce platform: product catalog, cart, checkout, payments, admin | full-stack-architect, backend-api-engineer, frontend-performance-specialist, security-audit-specialist, devops-engineer | 40-80 hours | Building full-featured e-commerce solutions from scratch |
| `/vertical:saas-mvp` | SaaS MVP development: authentication, multi-tenancy, billing, admin, deployment | product-strategist, full-stack-architect, backend-api-engineer, devops-engineer, security-audit-specialist | 40-120 hours | Launching new SaaS products with core functionality |
| `/vertical:fintech-compliance` | Fintech application with compliance: KYC, AML, PCI-DSS, SOC2, regulatory requirements | security-audit-specialist, compliance-automation-engineer, backend-api-engineer, data-engineer | 60-120 hours | Building compliant fintech applications (banking, payments, lending) |

---

## Creative Commands

**5 commands** for creative production workflows

| Command | Description | Agents | Duration | Best For |
|---------|-------------|--------|----------|----------|
| `/creative:film-production` | Film production: concept, scriptwriting, storyboarding, filming, editing, post-production | video-director, digital-artist, audio-engineer, tv-writer | 20-60 hours | Video and film production projects from concept to delivery |
| `/creative:game-development` | Game development: design, programming, art, audio, testing, deployment | full-stack-architect, digital-artist, audio-engineer, systems-engineer | 80-200 hours | Creating games from concept to published release |
| `/creative:album-production` | Music album production: composition, recording, mixing, mastering, artwork | audio-engineer, digital-artist | 40-80 hours | Producing music albums with professional quality |
| `/creative:poetry-collection` | Poetry collection: writing, editing, design, publication | comedy-writer, technical-writer | 10-20 hours | Creating and publishing poetry collections |
| `/creative:dance-performance` | Dance performance: choreography, music selection, production, recording | video-director, audio-engineer | 20-40 hours | Choreographing and producing dance performances |

---

## Command Comparison Tables

### Performance Optimization Paths

| Command | Focus | Duration | Best For | Typical Savings |
|---------|-------|----------|----------|-----------------|
| `/quality:performance-optimization --phase=audit` | Quick bottleneck identification | 2-3 hours | Initial performance assessment | Identifies $50K-$200K/year savings |
| `/quality:performance-optimization` | Full optimization workflow | 8-12 hours | Comprehensive performance improvement | $600K-$2M revenue impact, 10-17x ROI |
| `/seo:seo-performance-specialist` | SEO-focused speed optimization | 4-6 hours | Improving search rankings via performance | +15-30% organic traffic in 3-6 months |
| `/database-optimization` | Database-specific optimization | 8-12 hours | Slow database queries (50-90% improvement) | $200K-$800K/year efficiency gains |
| `/infrastructure-audit --focus=cost` | Infrastructure cost optimization | 4-8 hours | Cloud cost reduction without performance loss | 20-40% infrastructure cost reduction |

### Security Assessment Options

| Command | Scope | Duration | Best For | Deliverable |
|---------|-------|----------|----------|-------------|
| `/security-audit` | Application security vulnerabilities | 4-6 hours | General security assessment | Vulnerability report with remediation |
| `/quality:compliance-audit-soc2` | SOC2 Type II compliance | 20-30 hours initial | Enterprise sales requirements | SOC2 certification, automated compliance |
| `/dependency-audit` | Supply chain security | 1-3 hours | Dependency vulnerabilities | CVE report, update recommendations |
| `/infrastructure-audit --focus=security` | Infrastructure security posture | 8-16 hours | Cloud security assessment | CIS benchmark compliance, security gaps |

### Code Quality Paths

| Command | Focus | Duration | Best For | Impact |
|---------|-------|----------|----------|--------|
| `/quality:code-review --level=component` | Quick component review | 2-3 hours | Pull request reviews | Find critical bugs, security issues |
| `/quality:code-review --level=quality` | Maintainability focus | 4-6 hours | Technical debt identification | Technical debt assessment, refactoring roadmap |
| `/quality:code-review --level=architecture` | System-wide analysis | 6-8 hours | Architectural evaluation | Architecture recommendations, evolution roadmap |
| `/quality:cognitive-load-optimization` | Developer productivity | 6-10 hours | Reduce onboarding time | 40-60% faster onboarding, 25-45% velocity increase |
| `/development:tech-debt-impact-measurement` | Quantify tech debt costs | 8-14 hours | Executive business case | $720K-$2.15M annual debt burden quantified, 3-8x ROI |

---

## Workflow Combinations (Common Patterns)

### New SaaS Application (End-to-End)
**Timeline:** 50-140 hours over 8-12 weeks

1. `/business:product-roadmap` (6-10 hours)
   - Define product vision and features
   - Prioritize MVP scope

2. `/vertical:saas-mvp` (40-120 hours)
   - Build core SaaS functionality
   - Authentication, multi-tenancy, billing

3. `/quality:security-audit` (4-6 hours)
   - Security validation before launch

4. `/quality:performance-optimization` (6-8 hours)
   - Speed optimization for user experience

5. `/quality:production-readiness` (4-6 hours)
   - Pre-deployment checklist

6. `/operations:monitoring-stack-setup` (6-8 hours)
   - Observability for production

7. `/quality:compliance-audit-soc2` (20-30 hours)
   - SOC2 for enterprise customers (if needed)

**Total:** 86-188 hours | **Result:** Production-ready SaaS with enterprise features

### API Development (Complete)
**Timeline:** 20-30 hours over 2-4 weeks

1. `/api-design` (4-6 hours)
   - Design REST/GraphQL API
   - Database schema design

2. `/development:database-design` (4-6 hours)
   - Deep database optimization
   - Migration strategy

3. `/quality:testing-strategy --domain=api` (4-6 hours)
   - Test strategy and implementation

4. `/quality:security-audit` (2-3 hours)
   - API security review

5. `/operations:monitoring-stack-setup` (6-8 hours)
   - API observability

**Total:** 20-29 hours | **Result:** Production-ready API with full observability

### Performance Crisis Response
**Timeline:** 12-20 hours over 1-2 weeks

1. `/quality:performance-optimization --phase=audit` (2-3 hours)
   - Rapid bottleneck identification

2. `/quality:performance-optimization --phase=optimize` (4-6 hours)
   - Implement critical fixes

3. `/database-optimization --focus=performance` (4-6 hours)
   - Database query optimization

4. `/infrastructure-audit --focus=cost,performance` (2-4 hours)
   - Infrastructure right-sizing

**Total:** 12-19 hours | **Result:** 50-80% performance improvement

### SOC2 Compliance Journey
**Timeline:** 30-50 hours over 12-16 weeks

1. `/quality:compliance-audit-soc2 --assess-readiness` (3-4 hours)
   - Gap analysis and roadmap

2. `/quality:security-audit` (4-6 hours)
   - Security vulnerability remediation

3. `/operations:monitoring-stack-setup` (6-8 hours)
   - Audit logging infrastructure

4. `/operations:incident-response-workflow` (2-4 hours)
   - Incident response procedures

5. `/operations:disaster-recovery-plan` (6-8 hours)
   - DR and backup procedures

6. `/quality:compliance-audit-soc2 --implement` (8-12 hours)
   - Control implementation

7. `/quality:compliance-audit-soc2 --audit-prep` (1-2 hours)
   - Final audit preparation

**Total:** 30-44 hours | **Result:** SOC2 Type II certification

---

## Search Guide

### Find Command by Problem

**"I need to..."**

- **...improve performance** → `/quality:performance-optimization` (comprehensive) or `--phase=audit` (quick assessment)
- **...secure my application** → `/security-audit` (general) or `/quality:compliance-audit-soc2` (enterprise)
- **...design an API** → `/api-design` (REST/GraphQL) or `/python-web-api` (Python-specific)
- **...optimize database** → `/database-optimization` (existing DB) or `/database-design` (new DB)
- **...deploy to production** → `/deploy-prep` (validation) or `/quality:production-readiness` (comprehensive)
- **...monitor production** → `/operations:monitoring-stack-setup` (observability) or `/operations:incident-response-workflow` (incidents)
- **...reduce costs** → `/infrastructure-audit --focus=cost` or `/quality:performance-optimization`
- **...improve code quality** → `/quality:code-review` (review) or `/quality:cognitive-load-optimization` (complexity)
- **...quantify tech debt** → `/development:tech-debt-impact-measurement` (business impact) or `/quality:code-review --level=quality` (assessment)
- **...launch SaaS MVP** → `/vertical:saas-mvp` (full solution) or `/business:product-roadmap` (planning)
- **...improve SEO** → `/seo:comprehensive-seo-audit` (full audit) or `/seo:content-optimization` (quick wins)
- **...pass SOC2 audit** → `/quality:compliance-audit-soc2` (full compliance) or `/security-audit` (security only)

### Find Command by Technology

**React/Next.js:** `/quality:performance-optimization` (frontend focus), `/quality:code-review`, `/refactor-component`
**Python:** `/python-web-api`, `/python-data-pipeline`, `/python-modern-stack`, `/python-web-scraping`
**Database:** `/database-design`, `/database-optimization`, `/api-design` (includes DB design)
**PostgreSQL:** `/database-optimization` (PostgreSQL expert included)
**Kubernetes:** `/infrastructure-audit`, `/operations:monitoring-stack-setup --platform=kubernetes`
**GraphQL:** `/api-design --type=graphql`
**Microservices:** `/workflows:microservices-architecture`, `/quality:architecture-review`
**Event-Driven:** `/workflows:streaming-architecture` (Kafka, event systems)
**Rust:** `/rust-cargo`, `/workflows:ai-code-battle` (systems-engineer included)
**Lisp:** `/lisp-macro-workshop`, `/roswell` (Common Lisp)
**Mobile (iOS/Android):** `/safari-web-extension`, `/xcode-power-tools`

### Find Command by Phase

**Design:** `/api-design`, `/database-design`, `/workflows:microservices-architecture`, `/business:product-roadmap`
**Build:** `/vertical:saas-mvp`, `/python-web-api`, `/refactor-component`
**Test:** `/quality:testing-strategy`, `/quality:code-review`, `/quality:production-readiness`
**Deploy:** `/deploy-prep`, `/quality:production-readiness`, `/operations:monitoring-stack-setup`
**Monitor:** `/operations:monitoring-stack-setup`, `/operations:incident-response-workflow`, `/operations:production-learning-loop`
**Optimize:** `/quality:performance-optimization`, `/database-optimization`, `/quality:cognitive-load-optimization`
**Secure:** `/security-audit`, `/quality:compliance-audit-soc2`, `/dependency-audit`
**Scale:** `/infrastructure-audit`, `/workflows:microservices-architecture`, `/quality:performance-optimization`

---

## Command Options Reference

Common options across workflows:

### Phase Control
```bash
--phase=audit              # Run audit phase only (no changes)
--phase=analysis           # Audit + analysis (no implementation)
--phase=optimize           # Audit + analysis + optimization (no validation)
--phase=validate           # Run validation only (assumes optimization done)
```

### Focus Areas
```bash
--focus=frontend,backend   # Target specific layers
--focus=security,performance # Target specific aspects
--focus=cost               # Cost optimization focus
--layers=frontend,database # Alternative to --focus for layers
```

### Scope Control
```bash
--comprehensive=true       # Full workflow (all phases, all agents)
--quick                    # Quick assessment mode
--dry-run                  # Analysis only, no changes
--scope=path/to/module     # Limit to specific modules
```

### Domain/Platform Specific
```bash
--domain=ecommerce         # Industry-specific optimization
--platform=kubernetes      # Platform-specific configuration
--provider=aws,gcp         # Cloud provider targeting
--database=postgresql      # Database-specific optimization
--framework=nextjs         # Framework-specific optimization
```

### Environment
```bash
--env=production           # Production environment
--env=staging              # Staging environment
--env=development          # Development environment
```

### Output
```bash
--output=json              # JSON output format
--output=markdown          # Markdown report
--report-only              # Generate report without execution
```

---

## Notes

**Discovery Time Improvement:**
- **Before catalog:** 5-10 minutes browsing filesystem
- **After catalog:** <1 minute with table search or Ctrl+F

**Command Count:** 59 total workflows across 10 categories

**Typical ROI:**
- Development commands: 30-50% faster development
- Quality commands: 3-17x ROI in first year
- Performance optimization: $600K-$2M revenue impact
- Compliance: Win enterprise deals, reduce insurance costs
- Operations: 50-70% faster incident resolution

**Multi-Command Workflows:**
Most impactful results come from combining commands sequentially:
- SaaS launch: 6-8 commands over 8-12 weeks
- API development: 4-5 commands over 2-4 weeks
- Performance crisis: 3-4 commands over 1-2 weeks

**Agent Coordination:**
Commands coordinate 1-7 specialized agents depending on complexity. The catalog shows primary agents but many commands involve additional supporting agents for comprehensive coverage.

**Duration Guidance:**
- **Quick assessments:** 1-3 hours
- **Standard workflows:** 4-8 hours
- **Comprehensive reviews:** 8-20 hours
- **Full vertical solutions:** 40-200 hours

**When to Use Multiple Commands:**
Use sequential commands when:
- Problem spans multiple domains (performance + security + compliance)
- Need deep-dive after initial assessment
- Building complete solutions (design → build → test → deploy)
- Establishing ongoing processes (one-time setup + continuous monitoring)
