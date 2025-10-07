# GitHub MCP Server

MCP server that exposes GitHub operations as tools for AI agents.

## Features

- **search_code** - Search for code patterns in repositories
- **analyze_pr** - Analyze pull requests with detailed information
- **list_issues** - List repository issues with filtering
- **create_issue** - Create new GitHub issues

## Installation

```bash
cd mcp-servers/github
npm install
npm run build
```

## Configuration

Set GitHub personal access token:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Required permissions:
- `repo` - Full repository access
- `read:user` - Read user profile data

## Usage

### Standalone

```bash
npm start
```

### With MCP Client

```typescript
import { MCPClient, StdioTransport } from '@claudeagents/mcp-client';

const client = new MCPClient();
await client.connect(
  new StdioTransport({
    command: 'node',
    args: ['./mcp-servers/github/dist/index.js'],
    env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN },
  })
);

// Search code
const result = await client.callTool('search_code', {
  query: 'async function',
  repo: 'facebook/react',
  language: 'javascript',
});
```

### With Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/path/to/mcp-servers/github/dist/index.js"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

## Tools

### search_code

Search for code patterns in a repository.

**Parameters:**
- `query` (string, required) - Search query
- `repo` (string, required) - Repository in owner/repo format
- `language` (string, optional) - Filter by programming language
- `path` (string, optional) - Limit search to specific path

**Example:**
```json
{
  "query": "async function.*authenticate",
  "repo": "myorg/backend",
  "language": "typescript"
}
```

### analyze_pr

Analyze a pull request with comprehensive details.

**Parameters:**
- `repo` (string, required) - Repository in owner/repo format
- `pr_number` (number, required) - Pull request number

**Example:**
```json
{
  "repo": "facebook/react",
  "pr_number": 12345
}
```

### list_issues

List issues in a repository.

**Parameters:**
- `repo` (string, required) - Repository in owner/repo format
- `state` (enum, optional) - Issue state: open, closed, all (default: open)
- `labels` (array, optional) - Filter by labels
- `limit` (number, optional) - Max results, 1-100 (default: 10)

**Example:**
```json
{
  "repo": "facebook/react",
  "state": "open",
  "labels": ["bug", "priority-high"],
  "limit": 20
}
```

### create_issue

Create a new GitHub issue.

**Parameters:**
- `repo` (string, required) - Repository in owner/repo format
- `title` (string, required) - Issue title
- `body` (string, optional) - Issue body in Markdown
- `labels` (array, optional) - Labels to apply
- `assignees` (array, optional) - GitHub usernames to assign

**Example:**
```json
{
  "repo": "myorg/backend",
  "title": "Security Review: Authentication Logic",
  "body": "Found potential security issues in auth code...",
  "labels": ["security", "priority-high"],
  "assignees": ["security-team"]
}
```

## Rate Limiting

GitHub API has rate limits:
- Authenticated requests: 5,000/hour
- Search API: 30 requests/minute

The server respects these limits but does not implement retry logic in preview version.

## Error Handling

All tool errors return:
```json
{
  "content": [{ "type": "text", "text": "Error: ..." }],
  "isError": true
}
```

Common errors:
- Missing GITHUB_TOKEN
- Invalid repository format
- Repository not found
- Insufficient permissions
- Rate limit exceeded

## Development

```bash
# Build
npm run build

# Watch mode
npm run dev

# Test
npm test
```

## License

MIT
