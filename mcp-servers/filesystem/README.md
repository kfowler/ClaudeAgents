# Filesystem MCP Server

MCP server that exposes safe filesystem operations for AI agents.

## Features

- **read_file** - Read file contents with encoding support
- **list_files** - List files and directories
- **search_files** - Search for patterns in files (grep-like)
- **get_stats** - Get file/directory statistics

## Security

This server implements strict path validation to prevent directory traversal attacks:
- All paths must be within allowed directories
- Path traversal attempts (..) are blocked
- Symbolic links outside allowed paths are rejected

**Preview Limitation:** Read-only operations only. No write/delete operations.

## Installation

```bash
cd mcp-servers/filesystem
npm install
npm run build
```

## Usage

### Standalone

```bash
npm start /path/to/allowed/dir1 /path/to/allowed/dir2
```

Or set environment variable:

```bash
export ALLOWED_PATHS=/path1:/path2
npm start
```

### With MCP Client

```typescript
import { MCPClient, StdioTransport } from '@claudeagents/mcp-client';

const client = new MCPClient();
await client.connect(
  new StdioTransport({
    command: 'node',
    args: [
      './mcp-servers/filesystem/dist/index.js',
      '/Users/dev/projects',
    ],
  })
);

// Read file
const result = await client.callTool('read_file', {
  path: '/Users/dev/projects/README.md',
});
```

### With Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": [
        "/path/to/mcp-servers/filesystem/dist/index.js",
        "/Users/dev/projects"
      ]
    }
  }
}
```

## Tools

### read_file

Read contents of a file.

**Parameters:**
- `path` (string, required) - File path to read
- `encoding` (enum, optional) - Encoding: utf8 or base64 (default: utf8)

**Example:**
```json
{
  "path": "/Users/dev/project/README.md",
  "encoding": "utf8"
}
```

### list_files

List files and directories in a path.

**Parameters:**
- `path` (string, required) - Directory path to list
- `pattern` (string, optional) - Glob pattern to filter files

**Example:**
```json
{
  "path": "/Users/dev/project/src"
}
```

### search_files

Search for patterns in files (recursive grep-like search).

**Parameters:**
- `query` (string, required) - Search pattern (regex supported)
- `path` (string, required) - Directory to search
- `filePattern` (string, optional) - File glob pattern (e.g., "*.ts")

**Example:**
```json
{
  "query": "async function.*authenticate",
  "path": "/Users/dev/project/src",
  "filePattern": "*.ts"
}
```

### get_stats

Get file or directory statistics.

**Parameters:**
- `path` (string, required) - Path to analyze

**Example:**
```json
{
  "path": "/Users/dev/project"
}
```

**Returns:**
- Type (file/directory)
- Size
- Creation/modification dates
- Permissions
- Item count (for directories)

## Security Features

### Path Validation

All paths are validated against allowed directories:

```typescript
// Allowed: /Users/dev/projects
validatePath('/Users/dev/projects/myapp/src/index.ts')  // ✓ Allowed
validatePath('/Users/dev/projects/../secrets')          // ✗ Blocked
validatePath('/etc/passwd')                             // ✗ Blocked
```

### Read-Only Mode

Preview version only supports read operations:
- ✓ read_file
- ✓ list_files
- ✓ search_files
- ✓ get_stats
- ✗ write_file (not implemented)
- ✗ delete_file (not implemented)
- ✗ create_directory (not implemented)

## Error Handling

All tool errors return:
```json
{
  "content": [{ "type": "text", "text": "Error: ..." }],
  "isError": true
}
```

Common errors:
- Path outside allowed directories
- File not found
- Permission denied
- Invalid encoding

## Performance

Search operations are limited to:
- Max depth: 10 levels
- Max results: 50 matches displayed
- Binary files: Automatically skipped
- Large files: May timeout

## Development

```bash
# Build
npm run build

# Watch mode
npm run dev

# Test
npm test
```

## Future Enhancements

Post-preview improvements:
- Write operations (with safety checks)
- Real-time file watching (resources)
- Binary file support
- Syntax highlighting in results
- Performance optimization for large directories
- Integration with ripgrep for faster search

## License

MIT
