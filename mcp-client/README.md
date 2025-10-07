# @claudeagents/mcp-client

Model Context Protocol (MCP) client library for ClaudeAgents.

## Overview

This is a TypeScript implementation of an MCP client that enables ClaudeAgents to connect to and interact with MCP servers. It supports the stdio transport mechanism for local server communication.

## Features

- Full MCP protocol support (specification 2024-11-05)
- Stdio transport for local MCP servers
- Tool discovery and invocation
- Proper initialization handshake
- Type-safe API with TypeScript
- Error handling and validation
- Graceful connection management

## Installation

```bash
cd mcp-client
npm install
npm run build
```

## Quick Start

```typescript
import { MCPClient, StdioTransport } from '@claudeagents/mcp-client';

// Create client
const client = new MCPClient({
  name: 'MyApp',
  version: '1.0.0',
});

// Connect to server via stdio
await client.connect(
  new StdioTransport({
    command: 'node',
    args: ['./path/to/mcp-server.js'],
    env: { API_KEY: 'secret' },
  })
);

// List available tools
const { tools } = await client.listTools();
console.log('Available tools:', tools.map(t => t.name));

// Invoke a tool
const result = await client.callTool('search_code', {
  query: 'async function',
  path: '/src',
});

console.log('Tool result:', result.content[0].text);

// Disconnect
await client.disconnect();
```

## API Reference

### MCPClient

#### Constructor

```typescript
new MCPClient(config?: MCPClientConfig)
```

Options:
- `name`: Client name (default: 'ClaudeAgents')
- `version`: Client version (default: '1.0.0')
- `protocolVersion`: MCP protocol version (default: '2024-11-05')

#### Methods

##### `connect(transport: Transport): Promise<ServerInfo>`

Connect to an MCP server and perform initialization handshake.

```typescript
const serverInfo = await client.connect(new StdioTransport({ ... }));
console.log(`Connected to ${serverInfo.name} v${serverInfo.version}`);
```

##### `disconnect(): Promise<void>`

Disconnect from the MCP server.

```typescript
await client.disconnect();
```

##### `isConnected(): boolean`

Check if client is connected to a server.

```typescript
if (client.isConnected()) {
  console.log('Connected');
}
```

##### `listTools(cursor?: string): Promise<ToolListResponse>`

List available tools from the server.

```typescript
const { tools, nextCursor } = await client.listTools();

tools.forEach(tool => {
  console.log(`${tool.name}: ${tool.description}`);
});
```

##### `callTool(name: string, args: Record<string, unknown>): Promise<ToolResult>`

Invoke a tool by name.

```typescript
const result = await client.callTool('search_code', {
  query: 'async function',
  repo: 'owner/repo',
});

if (result.isError) {
  console.error('Tool error:', result.content[0].text);
} else {
  console.log('Success:', result.content[0].text);
}
```

##### `onNotification(handler: (notification) => void): void`

Register a handler for server notifications.

```typescript
client.onNotification((notification) => {
  console.log('Notification:', notification.method, notification.params);
});
```

### StdioTransport

#### Constructor

```typescript
new StdioTransport(config: StdioTransportConfig)
```

Options:
- `command`: Command to execute (e.g., 'node', 'python')
- `args`: Command arguments (e.g., ['server.js'])
- `env`: Environment variables for the server process
- `cwd`: Working directory for the server process

## Error Handling

The client throws typed errors for different failure modes:

```typescript
import {
  MCPError,
  ConnectionError,
  TransportError,
  ValidationError,
} from '@claudeagents/mcp-client';

try {
  await client.connect(transport);
} catch (error) {
  if (error instanceof ConnectionError) {
    console.error('Failed to connect:', error.message);
  } else if (error instanceof MCPError) {
    console.error('MCP protocol error:', error.code, error.message);
  }
}
```

## Logging

Set log level via environment variable:

```bash
export MCP_LOG_LEVEL=DEBUG
```

Levels: ERROR, WARN, INFO, DEBUG

## Development

```bash
# Build
npm run build

# Watch mode
npm run dev

# Run tests
npm test

# Lint
npm run lint

# Clean
npm run clean
```

## Architecture

```
mcp-client/
├── src/
│   ├── client.ts          # Main MCPClient class
│   ├── transport/
│   │   ├── base.ts        # Transport interface
│   │   └── stdio.ts       # Stdio transport implementation
│   ├── types/
│   │   ├── protocol.ts    # MCP protocol types
│   │   ├── tools.ts       # Tool-related types
│   │   └── errors.ts      # Error types
│   └── utils/
│       ├── logger.ts      # Logging utilities
│       └── validation.ts  # Validation helpers
└── test/
    └── *.test.ts          # Tests
```

## License

MIT
