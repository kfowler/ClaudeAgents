# Slash Commands Reference

**Last Updated:** 2025-10-14
**Available Commands:** 11 high-value workflows

---

## Overview

Slash commands provide instant invocation of ClaudeAgents workflows directly in Claude Code CLI. Instead of copying command text, simply type `/command-name` to launch multi-agent workflows.

### Benefits

- **Zero friction:** Type `/saas-mvp` instead of finding and copying the command
- **Autocomplete:** Claude Code suggests commands as you type
- **Consistent:** Same commands work across all projects
- **Discoverable:** See all available commands with `/` prefix

---

## Available Slash Commands

### Development Workflows

#### `/saas-mvp`
**Complete SaaS Product Development (8-12 hours)**

Orchestrates 6-8 agents to deliver production-ready SaaS application:
- Market validation (product-strategist)
- Architecture design (full-stack-architect)
- Implementation (backend-api-engineer, data-engineer)
- Quality assurance (security-audit-specialist, qa-test-engineer)
- Infrastructure setup (devops-engineer, cloud-architect)
- Launch preparation (technical-writer, seo-meta-optimizer)

**Use when:** Launching new SaaS product from scratch

---

#### `/api-design`
**REST/GraphQL API Design (4-6 hours)**

Coordinates specialists for complete API development:
- API architecture (backend-api-engineer)
- Database schema (data-engineer)
- OpenAPI/GraphQL schema generation
- Security implementation
- Developer documentation (technical-writer)

**Use when:** Building new API or redesigning existing one

---

#### `/database-design`
**Database Schema Design & Optimization (4-6 hours)**

Complete database architecture workflow:
- Schema design with ERD diagrams (data-engineer)
- Migration strategy
- Index optimization (postgresql-expert)
- Performance tuning (database-administrator)
- Query optimization

**Use when:** Designing new database or optimizing existing schema

**MCP Integration:** Uses `mcp__postgres__*` tools for schema analysis

---

#### `/debug-help`
**Interactive Debugging Support (variable)**

Expert debugging assistance:
- Stack trace analysis (debugging-specialist)
- Root cause identification
- Reproduction steps
- Fix recommendations
- Prevention strategies

**Use when:** Stuck on difficult bugs or production issues

---

### Quality Workflows

#### `/code-review`
**Comprehensive Code Quality Analysis (2-4 hours)**

Multi-agent code review:
- Domain-specific review (specialist agent)
- Architectural analysis (code-architect)
- Security audit (security-audit-specialist)
- Performance assessment (frontend-performance-specialist)
- Test coverage (qa-test-engineer)

**Use when:** Before merging major features or refactors

---

#### `/testing-strategy`
**Complete Testing Strategy (4-8 hours)**

Comprehensive test infrastructure:
- Test pyramid design (qa-test-engineer)
- Framework selection (test-automation-engineer)
- E2E test implementation
- Performance testing
- Security testing
- CI/CD integration (devops-engineer)

**Use when:** Setting up testing for new project or improving coverage

**Options:**
- `--domain=web` - Web application testing
- `--domain=api` - API testing with contract tests
- `--domain=mobile` - iOS/Android testing

---

#### `/performance-optimization`
**Performance Tuning & Optimization (2-12 hours)**

Multi-layer performance improvement:
- Frontend optimization (frontend-performance-specialist)
- Backend optimization (systems-engineer)
- Database tuning (data-engineer, postgresql-expert)
- Infrastructure optimization (devops-engineer)
- SEO performance (seo-performance-specialist)

**Use when:** Application is slow or Core Web Vitals poor

**Options:**
- `--phase=audit` - Identify bottlenecks only (2-3 hours)
- `--phase=optimize` - Implement fixes (8-12 hours)
- `--layers=frontend,database` - Target specific layers

**MCP Integration:** Uses `mcp__postgres__*` for database performance analysis

---

### Security & Compliance

#### `/security-audit`
**Security Vulnerability Assessment (4-6 hours)**

Comprehensive security review:
- OWASP Top 10 scanning (security-audit-specialist)
- Authentication/authorization review
- Dependency audit (dependency-security-specialist)
- API security testing
- Secrets management review
- Compliance check (GDPR, CCPA)

**Use when:** Before launch or after major changes

**MCP Integration:** Uses `mcp__github__*` to create security issues

---

### SEO Optimization

#### `/comprehensive-seo-audit`
**Complete SEO Analysis (6-10 hours)**

Full-site SEO health check:
- Technical SEO (seo-technical-auditor)
- Metadata optimization (seo-meta-optimizer)
- Performance for rankings (seo-performance-specialist)
- Content analysis
- Site architecture review

**Use when:** Launching site or improving search rankings

---

### Architecture Workflows

#### `/microservices-architecture`
**Microservices System Design (6-10 hours)**

Distributed systems architecture:
- Service decomposition (project-orchestrator)
- API gateway design (backend-api-engineer)
- Service mesh configuration (cloud-architect)
- Observability setup (observability-engineer)
- Data consistency patterns (data-engineer)

**Use when:** Migrating to microservices or designing new distributed system

---

### Business Operations

#### `/requirements-analysis`
**Business Requirements Document (4-6 hours)**

Complete BRD creation:
- Stakeholder analysis (business-analyst)
- Functional requirements (25+)
- Non-functional requirements (15+)
- Use cases and user stories
- Process flows (BPMN diagrams)
- Traceability matrix

**Use when:** Starting new project or major feature

---

#### `/product-roadmap`
**Strategic Product Planning (6-10 hours)**

Product strategy and roadmap:
- Feature discovery (product-manager)
- RICE prioritization
- OKR definition
- Quarterly planning
- Release strategy
- Risk assessment

**Use when:** Planning product direction or quarterly planning

---

## Usage Examples

### Basic Invocation
```
/saas-mvp
```

### With Options
```
/performance-optimization --phase=audit --layers=frontend,database
/testing-strategy --domain=api
```

### With Context
```
/api-design

"Design a REST API for a task management system with:
- User authentication
- CRUD operations for tasks
- Team collaboration features
- Real-time notifications"
```

---

## Creating Custom Slash Commands

### Step 1: Create Command File

Place markdown file in `.claude/commands/`:
```bash
.claude/commands/my-workflow.md
```

### Step 2: Command Format

```markdown
# My Workflow Title

## Overview
Description of what this command does

## Agents Involved
- agent-1 - What they do
- agent-2 - What they do

## Execution Steps
1. Step 1
2. Step 2
3. Step 3

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### Step 3: Test Command

Type `/my-workflow` in Claude Code to invoke

---

## Command Discovery

### List All Commands
```bash
ls -1 .claude/commands/
```

### Search Commands
```bash
grep -r "keyword" .claude/commands/
```

### View Command Details
```bash
cat .claude/commands/saas-mvp.md
```

---

## Best Practices

### When to Use Slash Commands

✅ **Use slash commands for:**
- Complete workflows (multiple phases)
- Multi-agent coordination
- Frequently used operations
- Standardized processes

❌ **Don't use slash commands for:**
- Single agent tasks (invoke agent directly)
- One-time custom requests
- Highly variable workflows

### Command Naming Conventions

- **Development:** `/api-design`, `/database-design`
- **Quality:** `/code-review`, `/testing-strategy`
- **Security:** `/security-audit`, `/compliance-check`
- **Operations:** `/deploy-prep`, `/incident-response`

### Organizing Commands

```
.claude/commands/
├── development/
│   ├── api-design.md
│   └── database-design.md
├── quality/
│   ├── code-review.md
│   └── testing-strategy.md
└── workflows/
    └── saas-mvp.md
```

---

## Slash Command vs Direct Agent Invocation

### Use Slash Commands When:
- Multi-phase workflows
- Multiple agents needed
- Standard operating procedures
- Repeatable processes

**Example:** `/saas-mvp` - Orchestrates 6-8 agents across 5 phases

### Use Direct Agent When:
- Single specific task
- Custom requirements
- Exploratory work
- Agent-specific expertise

**Example:** `@postgresql-expert` - Query optimization for specific table

---

## Integration with MCP Servers

Several commands now leverage MCP tools:

**Database Commands:**
- `/database-design` uses `mcp__postgres__get_schema`
- `/performance-optimization` uses `mcp__postgres__explain_query`

**Code Analysis Commands:**
- `/code-review` uses `mcp__filesystem__read_file`
- `/security-audit` uses `mcp__github__search_code`

**Documentation Commands:**
- `/requirements-analysis` uses `mcp__filesystem__list_files`

See [MCP_DEPLOYMENT.md](MCP_DEPLOYMENT.md) for MCP configuration.

---

## Troubleshooting

### Command Not Found

**Problem:** Typing `/my-command` shows "command not found"
- **Solution:** Check file exists in `.claude/commands/`
- **Verify:** File has `.md` extension

### Command Doesn't Execute

**Problem:** Command invoked but nothing happens
- **Solution:** Check command file format is correct
- **Verify:** Command includes agent specifications

### Wrong Agents Selected

**Problem:** Command uses wrong agents for task
- **Solution:** Update command file with correct agent names
- **Verify:** Agent names match `agents/` directory

---

## Next Steps

1. **Try a command:** Start with `/api-design` or `/testing-strategy`
2. **Create custom command:** Build workflow specific to your needs
3. **Share commands:** Submit useful commands via pull request
4. **Give feedback:** Report issues or suggest improvements

---

## Additional Resources

- [Command Catalog](../commands/) - All 68 available commands
- [Agent Guide](users-guide.md) - Individual agent capabilities
- [MCP Integration](MCP_DEPLOYMENT.md) - Enable MCP tools
- [Contributing](contributing.md) - Add new commands

---

**Maintained By:** full-stack-architect, project-orchestrator, technical-writer
**Support:** GitHub Issues for bugs, Discussions for questions
