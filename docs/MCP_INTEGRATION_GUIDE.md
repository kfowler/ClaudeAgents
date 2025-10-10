# MCP Integration Guide for ClaudeAgents

**Version:** 1.0
**Date:** October 6, 2025
**Status:** Preview Implementation
**Target Audience:** Developers, Product Team, Users

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Usage Examples](#usage-examples)
6. [Available MCP Servers](#available-mcp-servers)
7. [Agent Integration](#agent-integration)
8. [Configuration](#configuration)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)
11. [Future Roadmap](#future-roadmap)

## Overview

### What is MCP?

The Model Context Protocol (MCP) is an industry-standard protocol that enables AI applications to connect to external data sources and tools in a standardized way. Think of it as "USB-C for AI" - a universal connector that works across different AI applications and tools.

### Why MCP for ClaudeAgents?

**Benefits:**
- **Industry Standard** - Compatible with OpenAI, Anthropic, Google implementations
- **Extensibility** - Add new capabilities without modifying core agents
- **Ecosystem** - Access 500+ community MCP servers
- **Future-Proof** - Positioned for next-generation agentic workflows

**Current Status:**
- Preview implementation (not production)
- Demonstrates capability and competitive positioning
- Foundation for future expansion if user demand emerges

### What's Included

This preview implementation provides:

1. **MCP Client Library** - TypeScript client for connecting to MCP servers
2. **GitHub MCP Server** - Search code, analyze PRs, manage issues
3. **Filesystem MCP Server** - Safe file operations (read-only)
4. **Documentation** - Complete guides and examples

## Quick Start

### 5-Minute Demo

1. **Install Dependencies**

```bash
# Install MCP client
cd /Users/kfowler/Projects/ClaudeAgents/mcp-client
npm install && npm run build

# Install GitHub server
cd /Users/kfowler/Projects/ClaudeAgents/mcp-servers/github
npm install && npm run build

# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here
```

2. **Run Example**

```bash
cd /Users/kfowler/Projects/ClaudeAgents/mcp-client
node example.ts
```

3. **See Results**

You should see:
- Connection to GitHub MCP server
- List of available tools
- Example code search
- Example issue listing

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                  ClaudeAgents System                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐          ┌──────────────┐            │
│  │ MCP-Aware    │          │  MCP Client  │            │
│  │   Agents     ├─────────►│   Library    │            │
│  └──────────────┘          └──────┬───────┘            │
│                                    │                     │
│                                    │ stdio/JSON-RPC      │
│                                    │                     │
│           ┌────────────────────────┼────────────┐       │
│           │                        │            │       │
│   ┌───────▼────────┐      ┌───────▼────────┐  │       │
│   │ GitHub Server  │      │ Filesystem     │  │       │
│   │                │      │    Server      │  │       │
│   │ - search_code  │      │ - read_file    │  │       │
│   │ - analyze_pr   │      │ - list_files   │  │       │
│   │ - list_issues  │      │ - search_files │  │       │
│   │ - create_issue │      │ - get_stats    │  │       │
│   └────────────────┘      └────────────────┘  │       │
│                                                 │       │
└─────────────────────────────────────────────────────────┘
```

### Components

**1. MCP Client Library** (`@claudeagents/mcp-client`)
- Manages connections to MCP servers
- Handles protocol handshake
- Discovers and invokes tools
- Type-safe TypeScript API

**2. GitHub MCP Server** (`@claudeagents/mcp-server-github`)
- Exposes GitHub operations as tools
- Authenticates with GitHub API
- Returns structured results

**3. Filesystem MCP Server** (`@claudeagents/mcp-server-filesystem`)
- Safe file operations with sandboxing
- Read-only preview mode
- Path validation and security

## Installation

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Git (for GitHub server)
- GitHub personal access token (for GitHub server)

### Step-by-Step Installation

#### 1. Clone Repository (if not already done)

```bash
cd /Users/kfowler/Projects
git clone <claudeagents-repo>
cd ClaudeAgents
```

#### 2. Install MCP Client

```bash
cd mcp-client
npm install
npm run build
```

Verify installation:
```bash
ls dist/  # Should see compiled JavaScript files
```

#### 3. Install GitHub MCP Server

```bash
cd ../mcp-servers/github
npm install
npm run build
```

Create GitHub token:
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:user`
4. Copy token

Set environment variable:
```bash
export GITHUB_TOKEN=ghp_your_token_here
# Add to ~/.bashrc or ~/.zshrc for persistence
```

#### 4. Install Filesystem MCP Server

```bash
cd ../filesystem
npm install
npm run build
```

#### 5. Verify Installation

```bash
# Test MCP client example
cd ../../mcp-client
node example.ts
```

Expected output:
```
MCP Client Example

Connecting to GitHub MCP server...
✓ Connected to github-mcp-server v1.0.0

Server capabilities: [ 'tools' ]

Listing available tools...
✓ Found 4 tools:
...
```

## Usage Examples

### Example 1: Search Code in Repository

```typescript
import { MCPClient, StdioTransport } from '@claudeagents/mcp-client';

const client = new MCPClient();

// Connect to GitHub server
await client.connect(
  new StdioTransport({
    command: 'node',
    args: ['./mcp-servers/github/dist/index.js'],
    env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN },
  })
);

// Search for async functions
const result = await client.callTool('search_code', {
  query: 'async function',
  repo: 'facebook/react',
  language: 'javascript',
});

console.log(result.content[0].text);

await client.disconnect();
```

### Example 2: Analyze Pull Request

```typescript
const result = await client.callTool('analyze_pr', {
  repo: 'facebook/react',
  pr_number: 25000,
});

console.log(result.content[0].text);
// Shows: title, author, files changed, reviews, etc.
```

### Example 3: Read Project Files

```typescript
// Connect to filesystem server
await client.connect(
  new StdioTransport({
    command: 'node',
    args: [
      './mcp-servers/filesystem/dist/index.js',
      '/Users/dev/projects',  // Allowed directory
    ],
  })
);

// Read package.json
const result = await client.callTool('read_file', {
  path: '/Users/dev/projects/myapp/package.json',
});

console.log(result.content[0].text);
```

### Example 4: Search Project Code

```typescript
const result = await client.callTool('search_files', {
  query: 'TODO:|FIXME:',
  path: '/Users/dev/projects/myapp',
  filePattern: '*.ts',
});

console.log(result.content[0].text);
// Shows all TODO/FIXME comments in TypeScript files
```

## Available MCP Servers

### GitHub MCP Server

**Purpose:** Interact with GitHub repositories, issues, and pull requests

**Tools:**

| Tool | Description | Use Case |
|------|-------------|----------|
| `search_code` | Search for code patterns | Find functions, classes, patterns |
| `analyze_pr` | Analyze pull request | Review PR details, changes, reviews |
| `list_issues` | List repository issues | Track bugs, features, tasks |
| `create_issue` | Create new issue | Report bugs, request features |

**Configuration:**

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Permissions Required:**
- `repo` - Full repository access
- `read:user` - Read user profile

**Rate Limits:**
- Standard API: 5,000 requests/hour
- Search API: 30 requests/minute

### Filesystem MCP Server

**Purpose:** Safe file operations within allowed directories

**Tools:**

| Tool | Description | Use Case |
|------|-------------|----------|
| `read_file` | Read file contents | Inspect configurations, code |
| `list_files` | List directory contents | Explore project structure |
| `search_files` | Search in files | Find patterns, TODOs, errors |
| `get_stats` | Get file/dir stats | Check sizes, dates, permissions |

**Configuration:**

```bash
# Specify allowed directories
node dist/index.js /path/to/allowed/dir1 /path/to/allowed/dir2

# Or use environment variable
export ALLOWED_PATHS=/path1:/path2
```

**Security:**
- Path validation prevents directory traversal
- Read-only operations (no writes/deletes)
- Access restricted to allowed directories

## Agent Integration

### MCP-Aware Agents

Five agents have been enhanced with MCP tool awareness:

1. **full-stack-architect** - Code analysis, issue tracking
2. **llm-integration-architect** - Model code review, pipeline inspection
3. **devops-engineer** - Configuration review, deployment verification
4. **data-engineer** - Schema analysis, data pipeline review
5. **systems-engineer** - Performance analysis, systems code review

### How Agents Use MCP

Agents automatically invoke MCP tools when appropriate:

**User Request:**
```
"Review our authentication code for security issues"
```

**Agent Process:**
1. Uses `search_files` to find auth-related code
2. Uses `read_file` to examine each file
3. Analyzes code for security vulnerabilities
4. Uses `create_issue` to track findings
5. Returns summary with issue links

**User Sees:**
```
full-stack-architect:

I've analyzed your authentication code and found 3 security issues:

1. Missing CSRF protection (oauth.ts:45)
2. Weak JWT signing (jwt.ts:23)
3. Session fixation vulnerability (auth.ts:67)

I've created GitHub issue #847 to track these:
https://github.com/owner/repo/issues/847

Would you like me to propose fixes?
```

### Agent Prompt Enhancement

Agents receive tool descriptions in their system prompts:

```markdown
## Available MCP Tools

**search_code** - Search GitHub repositories for code patterns
- Use when: User asks to find specific code, patterns, or implementations
- Parameters: query, repo, language (optional), path (optional)

**read_file** - Read file contents from allowed directories
- Use when: User asks to examine specific files
- Parameters: path, encoding (optional)

**create_issue** - Create GitHub issues
- Use when: Tracking bugs, features, or action items
- Parameters: title, body, labels, assignees

Invoke tools naturally as part of your workflow. Don't ask the user
to run tools - you have direct access via MCP.
```

## Configuration

### MCP Client Configuration

**Basic Configuration:**
```typescript
const client = new MCPClient({
  name: 'MyApp',
  version: '1.0.0',
  protocolVersion: '2024-11-05',  // MCP protocol version
});
```

**Transport Configuration:**
```typescript
const transport = new StdioTransport({
  command: 'node',               // Command to execute
  args: ['server.js', '--flag'], // Arguments
  env: {                         // Environment variables
    API_KEY: 'secret',
    DEBUG: 'true',
  },
  cwd: '/path/to/server',        // Working directory
});
```

### Server Configuration

**GitHub Server:**
```bash
# Required
export GITHUB_TOKEN=ghp_xxx

# Optional
export DEBUG=true  # Enable debug logging
```

**Filesystem Server:**
```bash
# Method 1: Command line arguments
node dist/index.js /path1 /path2

# Method 2: Environment variable
export ALLOWED_PATHS=/path1:/path2
node dist/index.js
```

### Claude Desktop Configuration

To use MCP servers with Claude Desktop:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
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
        "/Users/kfowler/Projects/ClaudeAgents/mcp-servers/filesystem/dist/index.js",
        "/Users/dev/projects"
      ]
    }
  }
}
```

Restart Claude Desktop after configuration changes.

## Security

### Threat Model

**Risks Mitigated:**
- ✓ Directory traversal attacks (filesystem server)
- ✓ Unauthorized repository access (GitHub authentication)
- ✓ Credential exposure (environment variables, not hardcoded)

**Remaining Risks:**
- Malicious MCP server (validate server source)
- Compromised credentials (use short-lived tokens)
- Tool misuse by LLM (implement human confirmation for critical operations)

### Security Best Practices

**1. Filesystem Server Security:**

```typescript
// Good: Restrict to specific project
node dist/index.js /Users/dev/myproject

// Bad: Allow entire home directory
node dist/index.js /Users/dev  // Too broad!

// Terrible: Allow entire filesystem
node dist/index.js /  // Never do this!
```

**2. GitHub Token Security:**

```bash
# Good: Use scoped token
# Scopes: repo (read/write), write:issues

# Good: Short-lived tokens
# Regenerate tokens monthly

# Bad: Personal token with admin:org scope
# Never use tokens with more permissions than needed
```

**3. Environment Variables:**

```bash
# Good: Set in shell profile
echo 'export GITHUB_TOKEN=ghp_xxx' >> ~/.zshrc

# Better: Use secret management
# - macOS Keychain
# - 1Password CLI
# - HashiCorp Vault

# Bad: Hardcode in source
const token = 'ghp_xxx';  // Never do this!
```

### Audit Logging

Enable debug mode for audit trail:

```bash
export MCP_LOG_LEVEL=DEBUG
```

Logs include:
- Tool invocations
- Parameters passed
- Results returned
- Errors encountered

## Troubleshooting

### Common Issues

#### Issue: "GITHUB_TOKEN not found"

**Cause:** Environment variable not set

**Solution:**
```bash
export GITHUB_TOKEN=ghp_your_token_here
# Verify: echo $GITHUB_TOKEN
```

#### Issue: "Access denied: path outside allowed directories"

**Cause:** Trying to access file outside allowed paths

**Solution:**
```bash
# Check allowed paths
node dist/index.js /correct/path

# Or expand allowed paths
node dist/index.js /path1 /path2 /path3
```

#### Issue: "Transport not connected"

**Cause:** MCP server process failed to start

**Solution:**
```bash
# Check server can start manually
node mcp-servers/github/dist/index.js
# Should print: "GitHub MCP Server running on stdio"

# Check dependencies installed
cd mcp-servers/github && npm install
```

#### Issue: "Protocol version mismatch"

**Cause:** Client and server using different MCP versions

**Solution:**
```bash
# Rebuild both client and server
cd mcp-client && npm run build
cd ../mcp-servers/github && npm run build
```

#### Issue: "GitHub API rate limit exceeded"

**Cause:** Too many API requests

**Solution:**
- Wait 1 hour for limit reset
- Use authenticated token (5,000/hr vs 60/hr)
- Reduce search frequency
- Cache results client-side

### Debug Mode

Enable verbose logging:

```bash
# MCP client
export MCP_LOG_LEVEL=DEBUG

# Server stderr
export DEBUG=true

# Node.js debugging
node --inspect dist/index.js
```

### Health Check

Verify system health:

```bash
# 1. Check Node.js version
node --version  # Should be v18+

# 2. Check builds
ls mcp-client/dist/index.js  # Should exist
ls mcp-servers/github/dist/index.js  # Should exist

# 3. Test client
cd mcp-client && node example.ts

# 4. Test GitHub server manually
cd mcp-servers/github
export GITHUB_TOKEN=xxx
node dist/index.js
# Type: {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
# Should get response
```

## Future Roadmap

### Preview Limitations

Current preview implementation:
- ✓ stdio transport only (no HTTP)
- ✓ Tools only (no resources, prompts, sampling)
- ✓ 2 servers only (GitHub, Filesystem)
- ✓ Read-only filesystem operations
- ✓ 5 MCP-aware agents

### Phase 2: Production (Q1 2026) - If User Demand Emerges

**Enhanced Client:**
- HTTP/Streamable transport support
- Resource subscriptions
- Prompt templates
- Sampling (server-requested completions)
- Connection pooling
- Advanced error handling

**Additional Servers:**
- Slack MCP Server (team communication)
- Jira MCP Server (issue tracking)
- AWS MCP Server (cloud infrastructure)
- PostgreSQL MCP Server (database queries)
- Custom ClaudeAgents servers

**Agent Integration:**
- All 25+ agents MCP-aware
- Agent-to-agent MCP communication
- Multi-server workflows
- Caching and optimization

### Phase 3: Ecosystem (Q2 2026) - If Adoption Grows

**Developer Experience:**
- Visual MCP server builder
- CLI for server creation/testing
- Server marketplace
- Community contributions

**Advanced Features:**
- Real-time resource updates
- Multi-agent orchestration
- Workflow automation
- Performance monitoring

### Decision Point

**Re-evaluate Q1 2026:**
- User demand for MCP features
- Competitive landscape (VoltAgent status)
- Resource availability
- ROI assessment

**If no demand:**
- Maintain preview as proof-of-concept
- No further investment
- Revisit quarterly

**If demand emerges:**
- Full production implementation
- 200-hour development effort
- Marketing and documentation
- Community engagement

## Conclusion

This preview implementation demonstrates ClaudeAgents' technical leadership and positions the product competitively with industry-standard MCP support. The modular architecture enables future expansion without over-investment, balancing innovation with pragmatic resource management.

**Key Takeaways:**

1. **Industry Standard** - MCP is production-ready and widely adopted
2. **Competitive Edge** - ClaudeAgents has MCP, VoltAgent doesn't
3. **Low Risk** - Preview scope limits investment while proving capability
4. **Extensible** - Easy to expand if user demand materializes
5. **Learning Value** - Deep understanding of protocol and ecosystem

**Next Steps:**

1. Demo to stakeholders
2. Gather user feedback
3. Monitor competitive landscape
4. Decide on production investment (Q1 2026)

---

**Document Version:** 1.0
**Last Updated:** October 6, 2025
**Maintained By:** ClaudeAgents Engineering Team
**Feedback:** Submit issues to GitHub repository
