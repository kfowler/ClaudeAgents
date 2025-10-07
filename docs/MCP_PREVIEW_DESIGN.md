# MCP Preview Implementation Design

**Document Version:** 1.0
**Date:** October 6, 2025
**Design Phase:** Architecture & Implementation Plan (30 hours)
**Status:** Complete

## Executive Summary

This document outlines the architecture and implementation plan for integrating Model Context Protocol (MCP) support into ClaudeAgents as a preview capability. The design balances technical sophistication with pragmatic scope constraints, delivering demonstrable MCP integration within 80 total hours while avoiding over-investment in a feature with 0% current user demand.

**Design Philosophy:**
- **Preview, not production** - Demonstrate capability, defer hardening
- **Learning-focused** - Build deep understanding of MCP ecosystem
- **Minimal viable integration** - Core functionality only
- **Extensible foundation** - Easy to expand if user demand emerges

## 1. Architecture Overview

### 1.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                      ClaudeAgents System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐          ┌──────────────────┐              │
│  │  Claude Code   │          │  Agent Runtime   │              │
│  │   (Client)     │          │   (Coordinator)  │              │
│  └────────┬───────┘          └────────┬─────────┘              │
│           │                           │                         │
│           │  Invokes Agent            │                         │
│           └──────────────►────────────┘                         │
│                                        │                         │
│                          ┌─────────────▼──────────────┐         │
│                          │  MCP-Aware Agents          │         │
│                          │  - full-stack-architect    │         │
│                          │  - ai-ml-engineer          │         │
│                          │  - devops-engineer         │         │
│                          │  - data-engineer           │         │
│                          │  - systems-engineer        │         │
│                          └─────────────┬──────────────┘         │
│                                        │                         │
│                          ┌─────────────▼──────────────┐         │
│                          │   MCP Client Library       │         │
│                          │   (TypeScript)             │         │
│                          │                            │         │
│                          │   - Server Discovery       │         │
│                          │   - Tool Discovery         │         │
│                          │   - Tool Invocation        │         │
│                          │   - Resource Access        │         │
│                          │   - Error Handling         │         │
│                          └─────────────┬──────────────┘         │
│                                        │                         │
│                                        │ JSON-RPC 2.0           │
│                                        │                         │
│           ┌────────────────────────────┼─────────────────┐      │
│           │                            │                 │      │
│           │                            │                 │      │
│   ┌───────▼────────┐        ┌─────────▼────────┐  ┌────▼─────┐│
│   │  GitHub MCP    │        │ Filesystem MCP   │  │  Future  ││
│   │    Server      │        │     Server       │  │  Servers ││
│   │                │        │                  │  │          ││
│   │ - search_code  │        │ - read_file      │  │  - Slack ││
│   │ - analyze_pr   │        │ - list_files     │  │  - Jira  ││
│   │ - list_issues  │        │ - search_files   │  │  - AWS   ││
│   │ - create_issue │        │ - get_stats      │  │  - ...   ││
│   └────────────────┘        └──────────────────┘  └──────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

#### **MCP Client Library**
- **Location:** `/Users/kfowler/Projects/ClaudeAgents/mcp-client/`
- **Language:** TypeScript (Node.js runtime)
- **Responsibilities:**
  - Manage MCP server connections (stdio transport only for preview)
  - Handle initialization handshake and capability negotiation
  - Discover available tools from connected servers
  - Invoke tools with parameter validation
  - Parse and return tool results
  - Handle errors gracefully

#### **MCP-Aware Agents**
- **Location:** `/Users/kfowler/Projects/ClaudeAgents/agents/*.md`
- **Modified Agents:** 5 agents receive MCP tool awareness
- **Responsibilities:**
  - Understand which MCP tools are available
  - Invoke MCP tools through client library
  - Integrate MCP tool results into agent responses
  - Handle tool invocation failures gracefully

#### **GitHub MCP Server**
- **Location:** `/Users/kfowler/Projects/ClaudeAgents/mcp-servers/github/`
- **Language:** TypeScript
- **Responsibilities:**
  - Expose GitHub operations as MCP tools
  - Authenticate with GitHub API using PAT
  - Implement search_code, analyze_pr, list_issues, create_issue tools
  - Return structured results

#### **Filesystem MCP Server**
- **Location:** `/Users/kfowler/Projects/ClaudeAgents/mcp-servers/filesystem/`
- **Language:** TypeScript
- **Responsibilities:**
  - Expose file operations as MCP tools
  - Implement safe, sandboxed file access
  - Provide read_file, list_files, search_files, get_stats tools
  - Enforce directory restrictions (read-only for preview)

### 1.3 Data Flow Example

**User Request:** "Search our codebase for authentication logic and create a GitHub issue for the security review"

```
1. User → Claude Code
   "Search our codebase for authentication logic and create
    a GitHub issue for the security review"

2. Claude Code → full-stack-architect Agent
   Invokes agent with user request

3. full-stack-architect → MCP Client Library
   mcpClient.callTool('search_code', {
     query: 'authenticate|login|auth',
     path: '/Users/dev/project/src'
   })

4. MCP Client → Filesystem MCP Server
   JSON-RPC: tools/call with search_code parameters

5. Filesystem Server → File System
   Executes grep/ripgrep to find matches

6. Filesystem Server → MCP Client
   JSON-RPC response: {
     content: [{ type: 'text', text: 'Found matches in...' }]
   }

7. MCP Client → full-stack-architect
   Returns parsed tool results

8. full-stack-architect → LLM (Claude)
   "I found authentication code in these files: [results].
    Now I'll create a GitHub issue for security review."

9. full-stack-architect → MCP Client Library
   mcpClient.callTool('create_issue', {
     title: 'Security Review: Authentication Logic',
     body: 'Found authentication implementations in...'
   })

10. MCP Client → GitHub MCP Server
    JSON-RPC: tools/call with create_issue parameters

11. GitHub Server → GitHub API
    POST /repos/:owner/:repo/issues

12. GitHub Server → MCP Client
    JSON-RPC response: {
      content: [{ type: 'text', text: 'Created issue #123' }]
    }

13. MCP Client → full-stack-architect
    Returns issue creation confirmation

14. full-stack-architect → Claude Code
    "I've searched the codebase and created GitHub issue #123
     for the security review."

15. Claude Code → User
    Display agent response with clickable issue link
```

## 2. Integration Points

### 2.1 Agent Integration Strategy

**Phase 1: 5 MCP-Aware Agents**

1. **full-stack-architect**
   - **MCP Tools:** search_code, read_file, list_files, create_issue
   - **Use Cases:** Code analysis, issue tracking, file inspection
   - **Integration Point:** Add MCP tool discovery to agent initialization

2. **ai-ml-engineer**
   - **MCP Tools:** search_code, read_file, analyze_pr
   - **Use Cases:** Model code review, data pipeline inspection
   - **Integration Point:** Extend agent with MCP-aware code analysis

3. **devops-engineer**
   - **MCP Tools:** search_code, list_files, get_stats
   - **Use Cases:** Configuration review, deployment verification
   - **Integration Point:** Add MCP for infrastructure code inspection

4. **data-engineer**
   - **MCP Tools:** search_code, read_file, get_stats
   - **Use Cases:** Schema analysis, data pipeline review
   - **Integration Point:** MCP-enhanced data infrastructure review

5. **systems-engineer**
   - **MCP Tools:** search_code, read_file, analyze_pr
   - **Use Cases:** Performance analysis, systems code review
   - **Integration Point:** Low-level code analysis via MCP

### 2.2 Agent Prompt Enhancement

**Before MCP:**
```markdown
You are a full-stack architect specializing in React, Next.js, and backend APIs.

When asked to review code, use your knowledge of best practices...
```

**After MCP:**
```markdown
You are a full-stack architect specializing in React, Next.js, and backend APIs.

## Available MCP Tools

You have access to the following MCP tools for code analysis:

**search_code** - Search codebase for patterns
- Parameters: query (string), path (string, optional)
- Returns: List of file paths and line numbers with matches
- Example: Search for "async function.*fetch" to find async fetch calls

**read_file** - Read file contents
- Parameters: path (string)
- Returns: File contents with syntax highlighting
- Example: Read specific files identified in search results

**create_issue** - Create GitHub issue
- Parameters: title (string), body (string), labels (array, optional)
- Returns: Issue number and URL
- Example: Create issue for code improvements found during review

When asked to review code, you should:
1. Use search_code to find relevant files
2. Use read_file to examine specific files
3. Analyze code quality and architecture
4. Use create_issue to track identified improvements

Invoke MCP tools naturally as part of your workflow. Do not ask the user
to invoke tools manually - you have direct access.
```

### 2.3 User Experience

**Transparent MCP Integration:**
- User doesn't need to know MCP is being used
- Agent autonomously decides when to use MCP tools
- Tool invocations appear in conversation as agent "thinking"
- Results are seamlessly integrated into agent responses

**Example Conversation:**

```
User: "Review our authentication code for security issues"

full-stack-architect:
"I'll search the codebase for authentication-related code.

[Invoking MCP tool: search_code]
Searching for: (authenticate|login|auth|jwt|oauth|session)

Found authentication code in 8 files:
- src/auth/oauth.ts
- src/auth/jwt.ts
- src/middleware/auth.ts
- ...

Let me read the OAuth implementation to check for issues.

[Invoking MCP tool: read_file]
Reading: src/auth/oauth.ts

I've identified several security concerns:

1. **Missing CSRF protection** (oauth.ts:45)
   - OAuth state parameter not validated
   - Risk: CSRF attacks

2. **Weak JWT signing** (jwt.ts:23)
   - Using HS256 with short secret
   - Risk: Token forgery

3. **Session fixation vulnerability** (middleware/auth.ts:67)
   - Session ID not regenerated after login
   - Risk: Session hijacking

I'll create a GitHub issue to track these findings.

[Invoking MCP tool: create_issue]
Creating: Security Review: Authentication Vulnerabilities

✓ Created GitHub issue #847
https://github.com/owner/repo/issues/847

Summary: I found 3 security issues in the authentication code
and created issue #847 for tracking. Would you like me to
propose fixes for any of these issues?"
```

## 3. MCP Client Library Design

### 3.1 Directory Structure

```
mcp-client/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                 # Main exports
│   ├── client.ts                # MCPClient class
│   ├── transport/
│   │   ├── base.ts              # Transport interface
│   │   ├── stdio.ts             # Stdio transport implementation
│   │   └── http.ts              # HTTP transport (future)
│   ├── types/
│   │   ├── protocol.ts          # MCP protocol types
│   │   ├── tools.ts             # Tool-related types
│   │   └── errors.ts            # Error types
│   ├── discovery.ts             # Server/tool discovery
│   ├── invocation.ts            # Tool invocation logic
│   └── utils/
│       ├── validation.ts        # Parameter validation
│       └── logger.ts            # Logging utilities
├── test/
│   ├── client.test.ts
│   ├── transport.test.ts
│   └── integration.test.ts
└── README.md
```

### 3.2 Core API Design

```typescript
// src/index.ts
export { MCPClient } from './client';
export { StdioTransport } from './transport/stdio';
export type {
  Tool,
  ToolResult,
  ServerInfo,
  MCPError
} from './types';

// Usage example
import { MCPClient, StdioTransport } from '@claudeagents/mcp-client';

const client = new MCPClient();

// Connect to GitHub server
await client.connect(
  new StdioTransport({
    command: 'node',
    args: ['../mcp-servers/github/dist/index.js'],
    env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN }
  })
);

// Discover tools
const tools = await client.listTools();

// Invoke tool
const result = await client.callTool('search_code', {
  query: 'async function',
  repo: 'owner/repo'
});

console.log(result.content);
```

### 3.3 MCPClient Class

```typescript
// src/client.ts
import { Transport } from './transport/base';
import { Tool, ToolResult, ServerInfo } from './types';

export class MCPClient {
  private transport?: Transport;
  private serverInfo?: ServerInfo;
  private capabilities?: ServerCapabilities;
  private requestId = 0;

  /**
   * Connect to an MCP server
   */
  async connect(transport: Transport): Promise<void> {
    this.transport = transport;
    await transport.connect();
    await this.initialize();
  }

  /**
   * Disconnect from MCP server
   */
  async disconnect(): Promise<void> {
    await this.transport?.disconnect();
    this.transport = undefined;
  }

  /**
   * Initialize connection with handshake
   */
  private async initialize(): Promise<void> {
    const response = await this.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {
        roots: { listChanged: true }
      },
      clientInfo: {
        name: 'ClaudeAgents',
        version: '1.0.0'
      }
    });

    this.serverInfo = response.serverInfo;
    this.capabilities = response.capabilities;

    // Send initialized notification
    await this.sendNotification('notifications/initialized');
  }

  /**
   * List available tools from server
   */
  async listTools(): Promise<Tool[]> {
    if (!this.capabilities?.tools) {
      throw new Error('Server does not support tools capability');
    }

    const response = await this.sendRequest('tools/list', {});
    return response.tools;
  }

  /**
   * Invoke a tool by name
   */
  async callTool(name: string, args: Record<string, unknown>): Promise<ToolResult> {
    if (!this.capabilities?.tools) {
      throw new Error('Server does not support tools capability');
    }

    const response = await this.sendRequest('tools/call', {
      name,
      arguments: args
    });

    return {
      content: response.content,
      isError: response.isError || false
    };
  }

  /**
   * Send JSON-RPC request
   */
  private async sendRequest(
    method: string,
    params: Record<string, unknown>
  ): Promise<any> {
    if (!this.transport) {
      throw new Error('Not connected to server');
    }

    const id = ++this.requestId;
    const request = {
      jsonrpc: '2.0',
      id,
      method,
      params
    };

    const response = await this.transport.send(request);

    if (response.error) {
      throw new MCPError(
        response.error.code,
        response.error.message,
        response.error.data
      );
    }

    return response.result;
  }

  /**
   * Send JSON-RPC notification (no response expected)
   */
  private async sendNotification(
    method: string,
    params?: Record<string, unknown>
  ): Promise<void> {
    if (!this.transport) {
      throw new Error('Not connected to server');
    }

    const notification = {
      jsonrpc: '2.0',
      method,
      params
    };

    await this.transport.send(notification);
  }
}
```

### 3.4 Stdio Transport Implementation

```typescript
// src/transport/stdio.ts
import { spawn, ChildProcess } from 'child_process';
import { Transport } from './base';

export interface StdioTransportConfig {
  command: string;
  args?: string[];
  env?: Record<string, string>;
  cwd?: string;
}

export class StdioTransport implements Transport {
  private process?: ChildProcess;
  private buffer = '';
  private pendingRequests = new Map<number, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
  }>();

  constructor(private config: StdioTransportConfig) {}

  async connect(): Promise<void> {
    const env = { ...process.env, ...this.config.env };

    this.process = spawn(this.config.command, this.config.args || [], {
      env,
      cwd: this.config.cwd,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.process.stdout!.on('data', (data) => {
      this.handleData(data.toString());
    });

    this.process.stderr!.on('data', (data) => {
      console.error('[MCP Server Error]', data.toString());
    });

    this.process.on('exit', (code) => {
      if (code !== 0) {
        console.error(`[MCP Server] Process exited with code ${code}`);
      }
    });
  }

  async disconnect(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = undefined;
    }
  }

  async send(message: any): Promise<any> {
    if (!this.process || !this.process.stdin) {
      throw new Error('Transport not connected');
    }

    const json = JSON.stringify(message) + '\n';
    this.process.stdin.write(json);

    // If this is a request (has id), wait for response
    if (message.id !== undefined) {
      return new Promise((resolve, reject) => {
        this.pendingRequests.set(message.id, { resolve, reject });
      });
    }
  }

  private handleData(data: string): void {
    this.buffer += data;

    // Process complete JSON messages (newline-delimited)
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.trim()) {
        try {
          const message = JSON.parse(line);
          this.handleMessage(message);
        } catch (err) {
          console.error('[MCP Client] Failed to parse message:', err);
        }
      }
    }
  }

  private handleMessage(message: any): void {
    // Handle response to request
    if (message.id !== undefined && this.pendingRequests.has(message.id)) {
      const { resolve } = this.pendingRequests.get(message.id)!;
      this.pendingRequests.delete(message.id);
      resolve(message);
    }
    // Handle notification (no id)
    else if (message.method) {
      console.log('[MCP Notification]', message.method, message.params);
    }
  }
}
```

### 3.5 Type Definitions

```typescript
// src/types/protocol.ts
export interface ServerInfo {
  name: string;
  version: string;
}

export interface ServerCapabilities {
  tools?: {};
  resources?: {
    subscribe?: boolean;
  };
  prompts?: {};
  logging?: {};
}

// src/types/tools.ts
export interface Tool {
  name: string;
  title?: string;
  description: string;
  inputSchema: JSONSchema;
  outputSchema?: JSONSchema;
}

export interface ToolResult {
  content: Content[];
  isError: boolean;
}

export interface Content {
  type: 'text' | 'image' | 'audio' | 'resource';
  text?: string;
  data?: string;  // Base64 for images/audio
  uri?: string;   // For resource references
  mimeType?: string;
}

export interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchema>;
  required?: string[];
  items?: JSONSchema;
  [key: string]: unknown;
}

// src/types/errors.ts
export class MCPError extends Error {
  constructor(
    public code: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'MCPError';
  }
}
```

## 4. GitHub MCP Server Design

### 4.1 Directory Structure

```
mcp-servers/github/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                # Server entry point
│   ├── server.ts               # MCP server setup
│   ├── tools/
│   │   ├── search-code.ts      # search_code tool
│   │   ├── analyze-pr.ts       # analyze_pr tool
│   │   ├── list-issues.ts      # list_issues tool
│   │   └── create-issue.ts     # create_issue tool
│   ├── github/
│   │   ├── client.ts           # GitHub API client wrapper
│   │   └── auth.ts             # Authentication
│   └── utils/
│       ├── validation.ts       # Input validation
│       └── formatting.ts       # Result formatting
├── test/
│   └── tools.test.ts
└── README.md
```

### 4.2 Tool Implementations

#### **search_code Tool**

```typescript
// src/tools/search-code.ts
import { z } from 'zod';

export const searchCodeSchema = z.object({
  query: z.string().describe('Search query (code, path, or regex)'),
  repo: z.string().describe('Repository in owner/repo format'),
  language: z.string().optional().describe('Filter by language'),
  path: z.string().optional().describe('Limit search to path')
});

export async function searchCode(
  args: z.infer<typeof searchCodeSchema>
): Promise<ToolResult> {
  const { query, repo, language, path } = args;

  // Build GitHub Code Search API query
  let searchQuery = `${query} repo:${repo}`;
  if (language) searchQuery += ` language:${language}`;
  if (path) searchQuery += ` path:${path}`;

  const results = await githubClient.search.code({
    q: searchQuery,
    per_page: 10
  });

  const formatted = results.data.items.map(item =>
    `**${item.path}** (${item.repository.full_name})\n` +
    `Lines: ${item.text_matches?.[0]?.fragment || 'N/A'}\n` +
    `URL: ${item.html_url}\n`
  ).join('\n---\n');

  return {
    content: [{
      type: 'text',
      text: `Found ${results.data.total_count} results:\n\n${formatted}`
    }],
    isError: false
  };
}
```

#### **analyze_pr Tool**

```typescript
// src/tools/analyze-pr.ts
import { z } from 'zod';

export const analyzePRSchema = z.object({
  repo: z.string().describe('Repository in owner/repo format'),
  pr_number: z.number().describe('Pull request number')
});

export async function analyzePR(
  args: z.infer<typeof analyzePRSchema>
): Promise<ToolResult> {
  const [owner, repo] = args.repo.split('/');
  const prNumber = args.pr_number;

  // Fetch PR details
  const pr = await githubClient.pulls.get({
    owner,
    repo,
    pull_number: prNumber
  });

  // Fetch PR files
  const files = await githubClient.pulls.listFiles({
    owner,
    repo,
    pull_number: prNumber
  });

  // Fetch PR reviews
  const reviews = await githubClient.pulls.listReviews({
    owner,
    repo,
    pull_number: prNumber
  });

  const analysis = `
# Pull Request #${prNumber} Analysis

**Title:** ${pr.data.title}
**Author:** ${pr.data.user?.login}
**Status:** ${pr.data.state} ${pr.data.merged ? '(merged)' : ''}
**Branch:** ${pr.data.head.ref} → ${pr.data.base.ref}

## Changes Summary
- **Files changed:** ${pr.data.changed_files}
- **Additions:** +${pr.data.additions}
- **Deletions:** -${pr.data.deletions}
- **Commits:** ${pr.data.commits}

## Files Modified
${files.data.map(f =>
  `- **${f.filename}** (+${f.additions}/-${f.deletions}) [${f.status}]`
).join('\n')}

## Review Status
${reviews.data.length > 0
  ? reviews.data.map(r =>
      `- ${r.user?.login}: ${r.state} - "${r.body || 'No comment'}"`
    ).join('\n')
  : '- No reviews yet'
}

## Description
${pr.data.body || 'No description provided'}
  `.trim();

  return {
    content: [{ type: 'text', text: analysis }],
    isError: false
  };
}
```

#### **list_issues Tool**

```typescript
// src/tools/list-issues.ts
import { z } from 'zod';

export const listIssuesSchema = z.object({
  repo: z.string().describe('Repository in owner/repo format'),
  state: z.enum(['open', 'closed', 'all']).default('open'),
  labels: z.array(z.string()).optional().describe('Filter by labels'),
  limit: z.number().default(10).describe('Max results (1-100)')
});

export async function listIssues(
  args: z.infer<typeof listIssuesSchema>
): Promise<ToolResult> {
  const [owner, repo] = args.repo.split('/');

  const issues = await githubClient.issues.listForRepo({
    owner,
    repo,
    state: args.state,
    labels: args.labels?.join(','),
    per_page: Math.min(args.limit, 100)
  });

  const formatted = issues.data.map(issue =>
    `**#${issue.number}** ${issue.title}\n` +
    `State: ${issue.state} | Comments: ${issue.comments}\n` +
    `Labels: ${issue.labels.map(l => typeof l === 'string' ? l : l.name).join(', ') || 'None'}\n` +
    `Created: ${issue.created_at} by ${issue.user?.login}\n` +
    `URL: ${issue.html_url}\n`
  ).join('\n---\n');

  return {
    content: [{
      type: 'text',
      text: `Found ${issues.data.length} issues:\n\n${formatted}`
    }],
    isError: false
  };
}
```

#### **create_issue Tool**

```typescript
// src/tools/create-issue.ts
import { z } from 'zod';

export const createIssueSchema = z.object({
  repo: z.string().describe('Repository in owner/repo format'),
  title: z.string().describe('Issue title'),
  body: z.string().optional().describe('Issue body (markdown)'),
  labels: z.array(z.string()).optional().describe('Labels to apply'),
  assignees: z.array(z.string()).optional().describe('Users to assign')
});

export async function createIssue(
  args: z.infer<typeof createIssueSchema>
): Promise<ToolResult> {
  const [owner, repo] = args.repo.split('/');

  const issue = await githubClient.issues.create({
    owner,
    repo,
    title: args.title,
    body: args.body,
    labels: args.labels,
    assignees: args.assignees
  });

  return {
    content: [{
      type: 'text',
      text: `✓ Created issue #${issue.data.number}\n\n` +
            `**Title:** ${issue.data.title}\n` +
            `**URL:** ${issue.data.html_url}\n` +
            `**State:** ${issue.data.state}`
    }],
    isError: false
  };
}
```

### 4.3 Server Setup

```typescript
// src/server.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

import { searchCode, searchCodeSchema } from './tools/search-code.js';
import { analyzePR, analyzePRSchema } from './tools/analyze-pr.js';
import { listIssues, listIssuesSchema } from './tools/list-issues.js';
import { createIssue, createIssueSchema } from './tools/create-issue.js';

const server = new Server({
  name: 'github-mcp-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

// Register tool list handler
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'search_code',
      description: 'Search for code in a GitHub repository',
      inputSchema: zodToJsonSchema(searchCodeSchema)
    },
    {
      name: 'analyze_pr',
      description: 'Analyze a GitHub pull request in detail',
      inputSchema: zodToJsonSchema(analyzePRSchema)
    },
    {
      name: 'list_issues',
      description: 'List issues in a GitHub repository',
      inputSchema: zodToJsonSchema(listIssuesSchema)
    },
    {
      name: 'create_issue',
      description: 'Create a new GitHub issue',
      inputSchema: zodToJsonSchema(createIssueSchema)
    }
  ]
}));

// Register tool call handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'search_code':
        return await searchCode(searchCodeSchema.parse(args));
      case 'analyze_pr':
        return await analyzePR(analyzePRSchema.parse(args));
      case 'list_issues':
        return await listIssues(listIssuesSchema.parse(args));
      case 'create_issue':
        return await createIssue(createIssueSchema.parse(args));
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `Error: ${error.message}`
      }],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('GitHub MCP Server running on stdio');
}

main().catch(console.error);
```

## 5. Filesystem MCP Server Design

### 5.1 Directory Structure

```
mcp-servers/filesystem/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                # Server entry point
│   ├── server.ts               # MCP server setup
│   ├── tools/
│   │   ├── read-file.ts        # read_file tool
│   │   ├── list-files.ts       # list_files tool
│   │   ├── search-files.ts     # search_files tool
│   │   └── get-stats.ts        # get_stats tool
│   ├── fs/
│   │   ├── safe-access.ts      # Path validation & sandboxing
│   │   └── search.ts           # File search implementation
│   └── utils/
│       └── formatting.ts       # Result formatting
├── test/
│   └── tools.test.ts
└── README.md
```

### 5.2 Tool Implementations

#### **read_file Tool**

```typescript
// src/tools/read-file.ts
import { z } from 'zod';
import { readFile } from 'fs/promises';
import { validatePath } from '../fs/safe-access.js';

export const readFileSchema = z.object({
  path: z.string().describe('File path to read'),
  encoding: z.enum(['utf8', 'base64']).default('utf8')
});

export async function readFileTool(
  args: z.infer<typeof readFileSchema>,
  allowedPaths: string[]
): Promise<ToolResult> {
  // Validate path is within allowed directories
  const safePath = validatePath(args.path, allowedPaths);

  const content = await readFile(safePath, args.encoding);

  return {
    content: [{
      type: 'text',
      text: `File: ${args.path}\n\n${content}`
    }],
    isError: false
  };
}
```

#### **list_files Tool**

```typescript
// src/tools/list-files.ts
import { z } from 'zod';
import { readdir, stat } from 'fs/promises';
import { join } from 'path';
import { validatePath } from '../fs/safe-access.js';

export const listFilesSchema = z.object({
  path: z.string().describe('Directory path to list'),
  recursive: z.boolean().default(false).describe('Recursively list subdirectories'),
  pattern: z.string().optional().describe('Glob pattern to filter files')
});

export async function listFilesTool(
  args: z.infer<typeof listFilesSchema>,
  allowedPaths: string[]
): Promise<ToolResult> {
  const safePath = validatePath(args.path, allowedPaths);

  const files = await readdir(safePath, {
    recursive: args.recursive,
    withFileTypes: true
  });

  const formatted = await Promise.all(
    files.map(async (file) => {
      const fullPath = join(file.path, file.name);
      const stats = await stat(fullPath);
      const type = file.isDirectory() ? 'DIR' : 'FILE';
      const size = stats.size;
      return `[${type}] ${file.name} (${formatSize(size)})`;
    })
  );

  return {
    content: [{
      type: 'text',
      text: `Contents of ${args.path}:\n\n${formatted.join('\n')}`
    }],
    isError: false
  };
}
```

#### **search_files Tool**

```typescript
// src/tools/search-files.ts
import { z } from 'zod';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { validatePath } from '../fs/safe-access.js';

const execFileAsync = promisify(execFile);

export const searchFilesSchema = z.object({
  query: z.string().describe('Search pattern (regex supported)'),
  path: z.string().describe('Directory to search'),
  filePattern: z.string().optional().describe('File glob pattern (e.g., "*.ts")')
});

export async function searchFilesTool(
  args: z.infer<typeof searchFilesSchema>,
  allowedPaths: string[]
): Promise<ToolResult> {
  const safePath = validatePath(args.path, allowedPaths);

  // Use ripgrep for fast searching
  const rgArgs = [
    '--line-number',
    '--heading',
    '--color', 'never'
  ];

  if (args.filePattern) {
    rgArgs.push('--glob', args.filePattern);
  }

  rgArgs.push(args.query, safePath);

  try {
    const { stdout } = await execFileAsync('rg', rgArgs);

    return {
      content: [{
        type: 'text',
        text: `Search results for "${args.query}":\n\n${stdout}`
      }],
      isError: false
    };
  } catch (error) {
    if (error.code === 1) {
      // No matches found
      return {
        content: [{
          type: 'text',
          text: `No matches found for "${args.query}"`
        }],
        isError: false
      };
    }
    throw error;
  }
}
```

#### **get_stats Tool**

```typescript
// src/tools/get-stats.ts
import { z } from 'zod';
import { stat, readdir } from 'fs/promises';
import { join } from 'path';
import { validatePath } from '../fs/safe-access.js';

export const getStatsSchema = z.object({
  path: z.string().describe('Path to analyze')
});

export async function getStatsTool(
  args: z.infer<typeof getStatsSchema>,
  allowedPaths: string[]
): Promise<ToolResult> {
  const safePath = validatePath(args.path, allowedPaths);
  const stats = await stat(safePath);

  let details = `
**Path:** ${args.path}
**Type:** ${stats.isDirectory() ? 'Directory' : 'File'}
**Size:** ${formatSize(stats.size)}
**Created:** ${stats.birthtime.toISOString()}
**Modified:** ${stats.mtime.toISOString()}
**Permissions:** ${stats.mode.toString(8)}
  `.trim();

  if (stats.isDirectory()) {
    const files = await readdir(safePath);
    details += `\n**Items:** ${files.length}`;
  }

  return {
    content: [{ type: 'text', text: details }],
    isError: false
  };
}
```

### 5.3 Safe Path Validation

```typescript
// src/fs/safe-access.ts
import { resolve, normalize } from 'path';

/**
 * Validates that a requested path is within allowed directories
 * Prevents directory traversal attacks
 */
export function validatePath(
  requestedPath: string,
  allowedPaths: string[]
): string {
  const normalizedPath = normalize(resolve(requestedPath));

  const isAllowed = allowedPaths.some(allowedPath => {
    const normalizedAllowed = normalize(resolve(allowedPath));
    return normalizedPath.startsWith(normalizedAllowed);
  });

  if (!isAllowed) {
    throw new Error(
      `Access denied: ${requestedPath} is outside allowed directories`
    );
  }

  return normalizedPath;
}
```

## 6. Implementation Plan

### 6.1 Phase Breakdown (80 hours total)

**Phase 1: Research (20 hours) ✓ COMPLETE**
- Deep technical research on MCP protocol
- Study specification and examples
- Review official SDKs
- Document findings

**Phase 2: Design (30 hours) ← IN PROGRESS**
- Architecture design (10 hours)
- API design for MCP client (8 hours)
- GitHub server design (6 hours)
- Filesystem server design (6 hours)

**Phase 3: Implementation (20 hours)**
- MCP Client Library (8 hours)
  - Core client class
  - Stdio transport
  - Type definitions
  - Basic tests
- GitHub MCP Server (6 hours)
  - Server setup
  - 4 tools implementation
  - GitHub API integration
- Filesystem MCP Server (6 hours)
  - Server setup
  - 4 tools implementation
  - Safe path validation

**Phase 4: Integration (5 hours)**
- Modify 5 agents with MCP awareness (1 hour each)
  - Add tool discovery section to agent prompts
  - Document available MCP tools
  - Examples of when to use tools

**Phase 5: Documentation (5 hours)**
- Integration guide (3 hours)
- Usage examples (1 hour)
- Future roadmap (1 hour)

### 6.2 Development Sequence

**Week 1 (Sprint 14 Week 1):**
- ✓ Complete technical research
- → Complete architecture design
- → Begin MCP client implementation

**Week 2 (Sprint 14 Week 2):**
- Complete MCP client
- Implement GitHub MCP server
- Implement Filesystem MCP server
- Integrate with 5 agents
- Write documentation
- Demo to stakeholders

### 6.3 Success Criteria

**Technical:**
- [ ] MCP client connects to servers via stdio
- [ ] Client performs handshake and capability negotiation
- [ ] Client discovers and invokes tools
- [ ] GitHub server implements 4 working tools
- [ ] Filesystem server implements 4 working tools
- [ ] 5 agents successfully invoke MCP tools

**Documentation:**
- [ ] Technical research document complete
- [ ] Architecture design document complete
- [ ] Integration guide published
- [ ] Code examples provided

**Demonstration:**
- [ ] Live demo of agent using MCP tools
- [ ] Example: Search code + create GitHub issue
- [ ] Example: Read files + analyze patterns
- [ ] Performance acceptable (< 2s per tool call)

## 7. Agent Integration Examples

### 7.1 Full-Stack Architect

**Use Case:** Code review with automated issue creation

```markdown
## Example Workflow

User: "Review our authentication implementation for security issues"

Agent Process:
1. Use search_files to find auth-related files
2. Use read_file to examine each file
3. Identify security vulnerabilities
4. Use create_issue to track each vulnerability
5. Return summary with issue links
```

### 7.2 AI/ML Engineer

**Use Case:** Model code review

```markdown
## Example Workflow

User: "Review the model training pipeline for optimization opportunities"

Agent Process:
1. Use search_files to find model training code
2. Use read_file to examine training loops
3. Analyze for performance bottlenecks
4. Use create_issue for optimization suggestions
5. Return analysis with recommendations
```

### 7.3 DevOps Engineer

**Use Case:** Configuration audit

```markdown
## Example Workflow

User: "Audit our Kubernetes configuration files"

Agent Process:
1. Use list_files to find all k8s YAML files
2. Use read_file to examine each config
3. Identify misconfigurations or security issues
4. Use get_stats to check file permissions
5. Return audit report with findings
```

## 8. Testing Strategy

### 8.1 Unit Tests

**MCP Client:**
```typescript
describe('MCPClient', () => {
  it('should initialize with handshake', async () => {
    const client = new MCPClient();
    await client.connect(mockTransport);
    expect(client.isConnected()).toBe(true);
  });

  it('should list tools from server', async () => {
    const tools = await client.listTools();
    expect(tools).toHaveLength(4);
    expect(tools[0].name).toBe('search_code');
  });

  it('should invoke tool and return result', async () => {
    const result = await client.callTool('search_code', {
      query: 'test',
      repo: 'owner/repo'
    });
    expect(result.isError).toBe(false);
    expect(result.content).toBeDefined();
  });
});
```

**GitHub Server:**
```typescript
describe('GitHub MCP Server', () => {
  it('should search code in repository', async () => {
    const result = await searchCode({
      query: 'async function',
      repo: 'facebook/react'
    });
    expect(result.content[0].text).toContain('Found');
  });

  it('should create GitHub issue', async () => {
    const result = await createIssue({
      repo: 'test/repo',
      title: 'Test Issue',
      body: 'Test body'
    });
    expect(result.content[0].text).toContain('Created issue');
  });
});
```

### 8.2 Integration Tests

```typescript
describe('End-to-End MCP Integration', () => {
  it('should connect client to GitHub server and invoke tool', async () => {
    const client = new MCPClient();

    await client.connect(new StdioTransport({
      command: 'node',
      args: ['../mcp-servers/github/dist/index.js'],
      env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN }
    }));

    const tools = await client.listTools();
    expect(tools.find(t => t.name === 'search_code')).toBeDefined();

    const result = await client.callTool('search_code', {
      query: 'useState',
      repo: 'facebook/react'
    });

    expect(result.isError).toBe(false);
    expect(result.content[0].text).toContain('Found');

    await client.disconnect();
  });
});
```

### 8.3 Manual Testing

**Test Plan:**
1. Start GitHub MCP server manually
2. Connect MCP client via stdio
3. List available tools
4. Invoke each tool with valid parameters
5. Verify results are correct
6. Test error handling with invalid parameters
7. Test with real agent invocation

## 9. Security Considerations

### 9.1 Filesystem Server Security

**Sandboxing:**
- Validate all paths against allowlist
- Prevent directory traversal (../)
- Reject absolute paths outside allowed directories
- No write operations in preview (read-only)

**Example Configuration:**
```json
{
  "allowedPaths": [
    "/Users/dev/projects/myproject",
    "/Users/dev/workspace"
  ]
}
```

### 9.2 GitHub Server Security

**Authentication:**
- Require GITHUB_TOKEN environment variable
- Use personal access token (PAT)
- Scoped permissions (read:repo, write:issues)
- Token not logged or exposed

**Rate Limiting:**
- Respect GitHub API rate limits
- Implement exponential backoff
- Return clear errors when rate limited

### 9.3 Client Security

**Input Validation:**
- Validate all tool parameters against schema
- Sanitize file paths
- Escape special characters in queries

**Error Handling:**
- Never expose sensitive data in errors
- Redact tokens/credentials from logs
- Safe error messages to users

## 10. Performance Optimization

### 10.1 Expected Performance

**stdio Transport:**
- Connection setup: < 100ms
- Tool discovery: < 50ms
- Tool invocation: 200ms - 2s (depending on operation)

**GitHub API Calls:**
- Code search: 500ms - 1.5s
- Issue creation: 300ms - 800ms
- PR analysis: 800ms - 2s (multiple API calls)

**Filesystem Operations:**
- Read file: < 50ms (small files)
- List directory: < 100ms
- Search files (ripgrep): 100ms - 500ms

### 10.2 Optimization Strategies

**Caching:**
- Cache tool definitions client-side
- Cache GitHub API responses (short TTL)
- Cache file stats for directory listings

**Concurrent Requests:**
- Parallel tool invocations when independent
- Batch GitHub API calls where possible

**Lazy Loading:**
- Don't connect to all servers on startup
- Connect on first tool invocation
- Disconnect after idle timeout

## 11. Future Enhancements (Post-Preview)

### 11.1 Additional Transports

**HTTP/Streamable Transport:**
- Remote MCP server support
- Serverless deployment
- Horizontal scaling

### 11.2 Additional Servers

**Priority Servers:**
1. Slack MCP Server (team communication)
2. Jira MCP Server (issue tracking)
3. AWS MCP Server (cloud infrastructure)
4. PostgreSQL MCP Server (database queries)

### 11.3 Advanced Features

**Resource Support:**
- Expose project files as MCP resources
- Real-time resource subscriptions
- Resource caching

**Prompt Templates:**
- Predefined agent workflow prompts
- Shareable prompt library
- Prompt composition

**Sampling:**
- Server-side LLM completions
- Multi-agent workflows via sampling

### 11.4 Developer Experience

**MCP Server CLI:**
```bash
claude-agents mcp create my-server
claude-agents mcp test my-server
claude-agents mcp deploy my-server
```

**Visual Server Builder:**
- Web UI for building MCP servers
- No-code tool definition
- Automatic code generation

## 12. Risks and Mitigations

### 12.1 Technical Risks

**Risk:** Stdio transport process management complexity
**Mitigation:** Use battle-tested MCP SDK, handle process lifecycle carefully

**Risk:** GitHub API rate limiting
**Mitigation:** Implement rate limit detection, exponential backoff, clear user messaging

**Risk:** Performance degradation with many tool calls
**Mitigation:** Set performance budgets, optimize critical paths, cache aggressively

### 12.2 Product Risks

**Risk:** Users don't understand MCP value
**Mitigation:** Clear documentation, compelling demos, hide complexity

**Risk:** Low adoption due to setup friction
**Mitigation:** Sensible defaults, auto-configuration where possible, troubleshooting guides

**Risk:** Security vulnerabilities in servers
**Mitigation:** Security review, input validation, sandboxing, principle of least privilege

### 12.3 Business Risks

**Risk:** Time investment with no user demand
**Mitigation:** Preview-only scope, defer production investment, quarterly re-evaluation

**Risk:** Maintenance burden
**Mitigation:** Well-documented code, automated tests, clear ownership

## 13. Success Metrics

### 13.1 Technical Metrics

- [ ] MCP client handles 100% of test scenarios
- [ ] Tool invocation success rate > 95%
- [ ] Average tool invocation latency < 2s
- [ ] Zero security vulnerabilities in preview
- [ ] Code coverage > 80% for client and servers

### 13.2 Demonstration Metrics

- [ ] Successfully demo to 3+ stakeholders
- [ ] Positive feedback from technical team
- [ ] Working integration with all 5 agents
- [ ] Clear documentation with examples

### 13.3 Strategic Metrics

- [ ] Competitive differentiation vs VoltAgent
- [ ] Technical leadership demonstrated
- [ ] Foundation for future MCP expansion
- [ ] Learning objectives achieved

## 14. Conclusion

This preview implementation strikes an optimal balance between technical sophistication and pragmatic scope management. By focusing on core MCP capabilities (tools only, stdio transport only) and limiting to 2 demonstration servers, we achieve:

**Value Delivered:**
- Deep technical understanding of MCP
- Working proof-of-concept integration
- Competitive positioning advantage
- Extensible foundation for future work

**Risks Managed:**
- Time-boxed to 80 hours
- No production commitments
- Can defer or abandon if no user demand
- Learning value independent of adoption

**Next Steps:**
1. Complete MCP client implementation (Week 1)
2. Build GitHub and Filesystem servers (Week 2)
3. Integrate with 5 agents (Week 2)
4. Document and demonstrate (Week 2)
5. Evaluate user feedback and decide on production investment (Q1 2026)

---

**Document Status:** Complete
**Next Phase:** Implementation (20 hours)
**Review Date:** End of Sprint 14 Week 2
**Target Audience:** Engineering team, technical leadership
