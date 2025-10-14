# MCP Server Deployment Guide

**Last Updated:** 2025-10-14
**Status:** Production Ready (GitHub + Filesystem), PostgreSQL requires Docker

---

## Overview

ClaudeAgents now integrates with the Model Context Protocol (MCP) to enable agents to interact with real systems. This guide covers deployment and configuration of all 3 MCP servers.

### Available MCP Servers

1. **PostgreSQL MCP** (crystaldba/postgres-mcp) - Database inspection, query execution, performance analysis
2. **GitHub MCP** (custom) - Code search, PR analysis, issue management
3. **Filesystem MCP** (custom) - Safe file operations within allowed directories

---

## Quick Start

### 1. MCP Configuration File

The MCP configuration is located at `.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "-e", "DATABASE_URI",
        "crystaldba/postgres-mcp", "--access-mode=restricted"
      ],
      "env": {
        "DATABASE_URI": "postgresql://user:password@localhost:5432/dbname"
      }
    },
    "github": {
      "command": "node",
      "args": [
        "/Users/kfowler/Projects/ClaudeAgents/mcp-servers/github/dist/index.js"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    },
    "filesystem": {
      "command": "node",
      "args": [
        "/Users/kfowler/Projects/ClaudeAgents/mcp-servers/filesystem/dist/index.js"
      ],
      "env": {
        "ALLOWED_PATHS": "/Users/kfowler/Projects/ClaudeAgents"
      }
    }
  }
}
```

### 2. Build Existing MCP Servers

```bash
# Build GitHub MCP server
cd mcp-servers/github
npm install
npm run build

# Build Filesystem MCP server
cd ../filesystem
npm install
npm run build
```

### 3. Start Docker (for PostgreSQL MCP)

```bash
# Start OrbStack or Docker Desktop
# Then pull the PostgreSQL MCP image
docker pull crystaldba/postgres-mcp
```

### 4. Configure Environment Variables

**GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Create token with `repo` and `read:user` permissions
3. Replace `ghp_your_token_here` in config

**PostgreSQL Connection:**
1. Update `DATABASE_URI` with your database credentials
2. Use `restricted` mode for production (read-only + timeouts)
3. Use `unrestricted` mode for development (read/write access)

**Filesystem Allowed Paths:**
1. Set `ALLOWED_PATHS` to directories agents can access
2. Multiple paths: `/path1:/path2:/path3`
3. Security: Path traversal (..) attempts are blocked

---

## PostgreSQL MCP Server Details

### Features

- **Read-only queries** in restricted mode
- **Schema inspection** (tables, columns, indexes)
- **Query performance analysis** (EXPLAIN plans)
- **Index tuning recommendations**
- **Database health metrics**

### Installation Options

**Option 1: Docker (Recommended)**
```bash
docker pull crystaldba/postgres-mcp
```

**Option 2: Python (pipx)**
```bash
pipx install postgres-mcp
```

**Option 3: Python (uv)**
```bash
uv pip install postgres-mcp
```

### Configuration

**Restricted Mode (Production):**
- Read-only transactions only
- Query timeout enforcement
- Resource utilization limits
- Safe for production databases

**Unrestricted Mode (Development):**
- Full read/write access
- Schema modifications allowed
- Data manipulation permitted
- Use only in development environments

### Usage with Agents

**database-administrator:**
- Schema inspection: `mcp__postgres__get_schema`
- Performance analysis: `mcp__postgres__explain_query`
- Index recommendations: `mcp__postgres__analyze_indexes`

**postgresql-expert:**
- Query optimization: `mcp__postgres__explain_query`
- Index tuning: `mcp__postgres__suggest_indexes`
- Health monitoring: `mcp__postgres__get_health_metrics`

**data-engineer:**
- Data validation: `mcp__postgres__execute_query`
- Pipeline testing: `mcp__postgres__get_schema`
- Performance profiling: `mcp__postgres__analyze_queries`

---

## GitHub MCP Server Details

### Features

- **search_code** - Search for code patterns in repositories
- **analyze_pr** - Analyze pull requests with detailed information
- **list_issues** - List repository issues with filtering
- **create_issue** - Create new GitHub issues

### Security

- Requires personal access token with appropriate permissions
- Token stored in environment variable (not committed to repo)
- Read-only by default (safe for automated agents)

### Usage with Agents

**project-orchestrator:**
- Create project structure via GitHub issues
- Track multi-agent workflows
- Coordinate task dependencies

**devops-engineer:**
- Search infrastructure code
- Analyze deployment configurations
- Create deployment issues

**security-audit-specialist:**
- Search for security vulnerabilities
- Create security issues automatically
- Track vulnerability remediation

---

## Filesystem MCP Server Details

### Features

- **read_file** - Read file contents with encoding support
- **list_files** - List files and directories
- **search_files** - Search for patterns in files (grep-like)
- **get_stats** - Get file/directory statistics

### Security

- Strict path validation prevents directory traversal
- Only operates within `ALLOWED_PATHS`
- Symbolic links outside allowed paths are rejected
- Read-only operations only (no write/delete)

### Usage with Agents

**technical-writer:**
- Read existing documentation
- Generate updated docs
- Analyze documentation coverage

**qa-test-engineer:**
- Analyze test coverage
- Read test files
- Identify untested code paths

**code-architect:**
- Read codebase structure
- Analyze architectural patterns
- Identify technical debt

---

## Verification

### Check MCP Servers are Running

1. Open Claude Code CLI
2. Check for `mcp__` prefixed tools in tool list
3. Expected tools:
   - `mcp__postgres__*` (PostgreSQL)
   - `mcp__github__*` (GitHub)
   - `mcp__filesystem__*` (Filesystem)

### Test Each Server

**PostgreSQL:**
```
Try: mcp__postgres__get_schema
Expected: Returns database schema information
```

**GitHub:**
```
Try: mcp__github__search_code
Expected: Searches code in GitHub repositories
```

**Filesystem:**
```
Try: mcp__filesystem__list_files
Expected: Lists files in allowed directory
```

---

## Troubleshooting

### PostgreSQL MCP Not Working

**Problem:** Docker not running
- **Solution:** Start OrbStack or Docker Desktop
- **Verify:** `docker ps` should list running containers

**Problem:** Connection refused
- **Solution:** Check DATABASE_URI is correct
- **Verify:** Can connect with `psql` using same credentials

**Problem:** Permission denied
- **Solution:** Check database user has read permissions
- **Verify:** Run `SELECT 1` query manually

### GitHub MCP Not Working

**Problem:** Authentication failed
- **Solution:** Check GITHUB_TOKEN is valid
- **Verify:** Token has `repo` and `read:user` scopes

**Problem:** Rate limit exceeded
- **Solution:** Use authenticated requests
- **Verify:** Token provides 5000 req/hr vs 60 req/hr unauthenticated

### Filesystem MCP Not Working

**Problem:** Path not allowed
- **Solution:** Check ALLOWED_PATHS includes target directory
- **Verify:** Path is absolute, not relative

**Problem:** Permission denied
- **Solution:** Check file/directory permissions
- **Verify:** Node.js process can read files

---

## Production Deployment Checklist

- [ ] PostgreSQL MCP in restricted mode
- [ ] GitHub token has minimal required permissions
- [ ] Filesystem allowed paths limited to necessary directories
- [ ] All MCP servers tested and working
- [ ] Environment variables secured (not committed to repo)
- [ ] Monitoring configured for MCP server health
- [ ] Backup strategy for database connections
- [ ] Rate limiting configured for GitHub API

---

## Next Steps

1. **Enable More Agents:** Update agent definitions to use MCP tools
2. **Create Workflows:** Build multi-agent workflows using MCP servers
3. **Monitor Usage:** Track which MCP tools are most valuable
4. **Add More Servers:** Consider Database, API Testing, Performance Profiling

---

## Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [PostgreSQL MCP Documentation](https://github.com/crystaldba/postgres-mcp)
- [Claude Code MCP Integration](https://docs.claude.com/mcp)
- [ClaudeAgents Architecture](architecture.md)

---

**Maintained By:** devops-engineer, systems-engineer, postgresql-expert
**Support:** See [Contributing Guide](contributing.md) for questions
