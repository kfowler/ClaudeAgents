# Agent Discovery System Guide

## Overview

The **Agent Discovery System** helps you find the right specialist agent for any task using natural language queries or keywords. It analyzes 78+ agents across capabilities, expertise domains, and use cases to provide intelligent recommendations with relevance scoring and tier classifications.

## Quick Start

### Basic Discovery

```bash
# Natural language query
python tools/agent_discovery.py "optimize react performance"

# Keyword-based search
python tools/agent_discovery.py "security audit api vulnerabilities"

# Domain exploration
python tools/agent_discovery.py "mobile app development ios android"
```

### Understanding Results

Discovery returns ranked recommendations:

```
Top Recommendations for: "optimize react performance"

1. [CORE] frontend-performance-specialist (relevance: 0.95)
   - Core Web Vitals optimization, bundle size reduction, rendering performance
   - Best for: Frontend performance audits and optimization

2. [CORE] full-stack-architect (relevance: 0.72)
   - React ecosystem expertise, Next.js, state management
   - Best for: Full-stack web application architecture

3. [SPECIALIZED] code-architect (relevance: 0.58)
   - Holistic architecture review, performance patterns
   - Best for: Comprehensive code quality and architecture analysis
```

**Relevance score interpretation:**
- **0.9-1.0:** Perfect match, primary expert for this task
- **0.7-0.9:** Strong match, capable specialist
- **0.5-0.7:** Moderate match, may help with related aspects
- **<0.5:** Weak match, likely not the best choice

**Tier classification:**
- **CORE:** Production-ready agents with proven capabilities
- **SPECIALIZED:** Experts for specific narrow domains
- **EXPERIMENTAL:** Experimental agents still under development

## Discovery Patterns

### Pattern 1: Technology Stack Queries

**Query:** "build graphql api with postgresql database"

**Expected results:**
1. backend-api-engineer (GraphQL, REST, microservices)
2. data-engineer (PostgreSQL, data modeling)
3. devops-engineer (API deployment, infrastructure)

**Usage:** Chain agents for complete solution - backend-api-engineer designs API, data-engineer handles database schema, devops-engineer deploys.

### Pattern 2: Quality Assurance Queries

**Query:** "test mobile app ios android security"

**Expected results:**
1. qa-test-engineer (test strategies, mobile testing)
2. security-audit-specialist (vulnerability assessment, security testing)
3. mobile-developer (platform-specific testing knowledge)

**Usage:** qa-test-engineer designs test strategy, security-audit-specialist performs security testing, mobile-developer validates platform-specific behavior.

### Pattern 3: Workflow/Process Queries

**Query:** "document api for developers create tutorials"

**Expected results:**
1. technical-writer (API docs, tutorials, developer documentation)
2. full-stack-architect (API design context)

**Usage:** technical-writer creates documentation, full-stack-architect reviews for technical accuracy.

### Pattern 4: Creative/Ideation Queries

**Query:** "generate diverse ideas for user retention"

**Expected results:**
1. creative-catalyst (oblique strategies, breakthrough thinking)
2. the-inventor (systematic diversity guarantees)
3. product-strategist (market validation, product strategy)

**Usage:** creative-catalyst generates novel ideas, the-inventor ensures comprehensive coverage, product-strategist validates market fit.

### Pattern 5: Business/Strategic Queries

**Query:** "analyze competitive landscape prioritize features"

**Expected results:**
1. product-manager (feature prioritization, roadmap planning)
2. business-analyst (competitive analysis, requirements gathering)
3. product-strategist (market positioning, strategy)

**Usage:** business-analyst performs competitive analysis, product-manager prioritizes features, product-strategist defines market positioning.

## Advanced Discovery Techniques

### Multi-Keyword Queries

Combine keywords for precision:

```bash
# Specific technology stack
python tools/agent_discovery.py "react nextjs typescript performance optimization"

# Role + technology
python tools/agent_discovery.py "backend engineer microservices kubernetes"

# Problem domain + constraint
python tools/agent_discovery.py "mobile app offline-first data sync"
```

### Negative Filtering

Use discovery to understand what NOT to use:

**Query:** "react native mobile app"
**Expected:** mobile-developer (0.95), NOT full-stack-architect (0.35)

**Why?** full-stack-architect handles web React, but mobile-developer owns React Native.

### Domain Boundary Queries

Understand agent boundaries:

**Query:** "backend api"
- **backend-api-engineer:** Backend-only API development
- **full-stack-architect:** Full-stack including backend APIs

**Query:** "database performance"
- **data-engineer:** Analytics, OLAP, data pipelines
- **database-admin (future):** Operations, OLTP, tuning, backups

**Query:** "linux server"
- **linux-sysadmin:** OS-level (systemd, kernel, firewall)
- **devops-engineer:** Application-level (Docker, CI/CD)

### Tier-Based Selection

**Query same problem, different tiers:**

**Problem:** "improve website performance"

**Core tier:** frontend-performance-specialist (production-ready, proven)
**Experimental tier:** seo-performance-specialist (SEO angle, experimental)

**When to use experimental:** Willing to accept less mature tooling for specialized insight. Always validate experimental agent output with core agents.

## Discovery CLI Options

### Basic Usage

```bash
# Simple query
python tools/agent_discovery.py "query here"

# Limit results
python tools/agent_discovery.py "query" --limit 5

# Filter by tier
python tools/agent_discovery.py "query" --tier core
python tools/agent_discovery.py "query" --tier specialized
python tools/agent_discovery.py "query" --tier experimental

# Verbose output (show all scores)
python tools/agent_discovery.py "query" --verbose
```

### JSON Output

```bash
# Get machine-readable JSON
python tools/agent_discovery.py "query" --format json

# Process with jq
python tools/agent_discovery.py "query" --format json | jq '.recommendations[0]'
```

### Discovery API

Use programmatically in Python:

```python
from tools.agent_discovery import AgentDiscovery

discovery = AgentDiscovery()
results = discovery.query("optimize react performance")

for agent in results:
    print(f"{agent['name']}: {agent['relevance']}")
    print(f"  {agent['description']}")
```

## Common Scenarios

### Scenario 1: Starting New Project

**Goal:** Find agents for greenfield SaaS project

```bash
# Step 1: Product validation
python tools/agent_discovery.py "validate product idea market research"
# → product-strategist

# Step 2: Architecture planning
python tools/agent_discovery.py "web application architecture react nodejs"
# → full-stack-architect, project-orchestrator

# Step 3: Security planning
python tools/agent_discovery.py "security audit web application"
# → security-audit-specialist

# Step 4: Quality planning
python tools/agent_discovery.py "test strategy web application"
# → qa-test-engineer
```

### Scenario 2: Debugging Performance Issue

**Goal:** Fix production performance problem

```bash
# Identify specialist by symptom
python tools/agent_discovery.py "slow page load high ttfb"
# → frontend-performance-specialist, seo-performance-specialist

python tools/agent_discovery.py "database query performance"
# → data-engineer

python tools/agent_discovery.py "api latency microservices"
# → backend-api-engineer, devops-engineer
```

### Scenario 3: Compliance/Audit Requirement

**Goal:** Prepare for compliance audit

```bash
# Security compliance
python tools/agent_discovery.py "security audit vulnerability assessment"
# → security-audit-specialist

# Accessibility compliance
python tools/agent_discovery.py "wcag accessibility audit"
# → accessibility-expert

# Technical SEO audit
python tools/agent_discovery.py "seo technical audit crawlability"
# → seo-technical-auditor
```

### Scenario 4: Learning New Technology

**Goal:** Understand agent capabilities in domain

```bash
# Explore all agents with React expertise
python tools/agent_discovery.py "react" --verbose

# Compare mobile platforms
python tools/agent_discovery.py "ios"
python tools/agent_discovery.py "android"
python tools/agent_discovery.py "react native"
# All → mobile-developer

# Understand SEO specializations
python tools/agent_discovery.py "seo" --verbose
# → Multiple SEO specialists with different focuses
```

## Discovery Quality Indicators

### High-Quality Matches

Strong indicators the discovery found the right agent:

1. **Relevance ≥0.9:** Near-perfect keyword/capability match
2. **Core tier + high relevance:** Production-ready with proven track record
3. **Exact description match:** Agent description mentions your exact use case
4. **Multiple keyword hits:** Agent matches several aspects of your query

### Weak Matches to Avoid

Signs the discovery might not be optimal:

1. **Relevance <0.5:** Weak match, likely tangential connection
2. **Experimental tier with critical task:** Risky for production needs
3. **Generic match:** Agent matches broad keyword but not specific need
4. **Better alternative exists:** Higher-ranked agent is more specialized

### Ambiguous Results Interpretation

When multiple agents score similarly:

**Example:** "api development" returns:
- backend-api-engineer: 0.92
- full-stack-architect: 0.88

**Decision criteria:**
- **Backend-only API?** → backend-api-engineer
- **Full-stack with frontend?** → full-stack-architect
- **Both needed?** → Chain them (backend-api-engineer designs, full-stack-architect integrates)

## Discovery System Architecture

### How It Works

1. **Query parsing:** Extracts keywords and intent from natural language
2. **Agent indexing:** Searches agent descriptions, capabilities, tags, keywords
3. **Relevance scoring:** Calculates match quality based on:
   - Keyword frequency in agent metadata
   - Capability alignment
   - Domain expertise match
   - Tier appropriateness
4. **Ranking:** Sorts agents by relevance score
5. **Presentation:** Returns top N recommendations with context

### Indexed Metadata

Each agent contributes:
- **Name:** Agent identifier (e.g., "frontend-performance-specialist")
- **Description:** Brief capability summary
- **Tier:** core/specialized/experimental classification
- **Keywords:** Searchable terms (e.g., "React", "performance", "Core Web Vitals")
- **Capabilities:** Structured list of what agent can do
- **Domains:** Areas of expertise (e.g., "web development", "performance optimization")

## Best Practices

### DO:

✅ **Use natural language** - "optimize mobile app battery usage" works better than "mobile battery"
✅ **Be specific** - "react performance core web vitals" beats "performance"
✅ **Explore results** - Check top 3-5 recommendations, not just #1
✅ **Validate tier** - Prefer core agents for production, experimental for exploration
✅ **Chain agents** - Use discovery to find multiple specialists for complex tasks

### DON'T:

❌ **Don't trust low scores** - Relevance <0.5 is rarely the right agent
❌ **Don't ignore tier** - Experimental agents may not be production-ready
❌ **Don't assume single agent** - Complex tasks often need multiple specialists
❌ **Don't skip validation** - Discovery suggests, you decide based on full agent description
❌ **Don't over-rely** - Discovery is a tool, not a replacement for understanding agent capabilities

## Troubleshooting

### "No relevant agents found"

**Cause:** Query too specific or uses uncommon terminology

**Solution:**
1. Broaden query: "rust systems programming" → "systems programming"
2. Use synonyms: "machine learning" vs "AI" vs "neural networks"
3. Check agent list manually: `ls agents/*.md`

### "Wrong agent recommended"

**Cause:** Keyword overlap with unrelated domain

**Solution:**
1. Add context keywords: "mobile" + "app" + "ios" (not just "mobile")
2. Check agent description directly: `agents/agent-name.md`
3. Use negative examples: Understand what NOT to use

### "Too many results, can't decide"

**Cause:** Generic query matching multiple domains

**Solution:**
1. Narrow with specifics: "web development" → "react next.js typescript"
2. Use --limit flag: `--limit 3` for top 3 only
3. Check tier and relevance together: Prefer high relevance + core tier

## Examples by Domain

### Web Development

```bash
python tools/agent_discovery.py "build react application"
# → full-stack-architect, frontend-performance-specialist

python tools/agent_discovery.py "nextjs server side rendering"
# → full-stack-architect

python tools/agent_discovery.py "api backend nodejs"
# → backend-api-engineer
```

### Mobile Development

```bash
python tools/agent_discovery.py "ios app swift"
# → mobile-developer

python tools/agent_discovery.py "react native cross platform"
# → mobile-developer (NOT full-stack-architect)

python tools/agent_discovery.py "app store deployment"
# → mobile-developer
```

### AI/ML

```bash
python tools/agent_discovery.py "llm integration rag system"
# → llm-integration-architect

python tools/agent_discovery.py "vector database embeddings"
# → llm-integration-architect

python tools/agent_discovery.py "machine learning pipeline"
# → llm-integration-architect, data-engineer
```

### DevOps/Infrastructure

```bash
python tools/agent_discovery.py "kubernetes deployment ci/cd"
# → devops-engineer

python tools/agent_discovery.py "docker containerization"
# → devops-engineer

python tools/agent_discovery.py "linux server hardening firewall"
# → linux-sysadmin (NOT devops-engineer)
```

### Quality & Testing

```bash
python tools/agent_discovery.py "unit tests integration tests"
# → qa-test-engineer

python tools/agent_discovery.py "security vulnerability scan"
# → security-audit-specialist

python tools/agent_discovery.py "wcag accessibility compliance"
# → accessibility-expert
```

### SEO Optimization

```bash
python tools/agent_discovery.py "meta tags open graph structured data"
# → seo-meta-optimizer

python tools/agent_discovery.py "sitemap robots.txt crawlability"
# → seo-technical-auditor

python tools/agent_discovery.py "keyword research search intent"
# → seo-keyword-strategist

python tools/agent_discovery.py "on-page seo content optimization"
# → seo-content-optimizer

python tools/agent_discovery.py "core web vitals seo performance"
# → seo-performance-specialist
```

### Business Operations

```bash
python tools/agent_discovery.py "requirements gathering user stories"
# → business-analyst

python tools/agent_discovery.py "api documentation tutorials"
# → technical-writer

python tools/agent_discovery.py "feature prioritization product roadmap"
# → product-manager
```

## Related Documentation

- [Creative Triad Guide](creative-triad/README.md) - Creative ideation system
- [System Architecture](architecture.md) - Agent ecosystem design
- [CLAUDE.md](../CLAUDE.md) - Agent selection keywords
- [Agent Registry](../tools/agent_registry.py) - Programmatic agent access
