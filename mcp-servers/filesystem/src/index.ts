#!/usr/bin/env node

/**
 * Filesystem MCP Server
 * Exposes safe file operations as MCP tools
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import {
  readFileTool,
  readFileSchema,
  listFilesTool,
  listFilesSchema,
  searchFilesTool,
  searchFilesSchema,
  getStatsTool,
  getStatsSchema,
} from './tools/index.js';

import { zodToJsonSchema } from './utils/schema.js';

// Get allowed paths from command line args or environment
const allowedPaths = process.argv.slice(2).length > 0
  ? process.argv.slice(2)
  : (process.env.ALLOWED_PATHS || '').split(':').filter(Boolean);

if (allowedPaths.length === 0) {
  console.error('Error: No allowed paths specified');
  console.error('Usage: mcp-server-filesystem <path1> [path2] [...]');
  console.error('Or set ALLOWED_PATHS environment variable');
  process.exit(1);
}

console.error('Filesystem MCP Server');
console.error('Allowed paths:', allowedPaths);

const server = new Server(
  {
    name: 'filesystem-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool list handler
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'read_file',
      description: 'Read contents of a file',
      inputSchema: zodToJsonSchema(readFileSchema),
    },
    {
      name: 'list_files',
      description: 'List files and directories',
      inputSchema: zodToJsonSchema(listFilesSchema),
    },
    {
      name: 'search_files',
      description: 'Search for patterns in files',
      inputSchema: zodToJsonSchema(searchFilesSchema),
    },
    {
      name: 'get_stats',
      description: 'Get file or directory statistics',
      inputSchema: zodToJsonSchema(getStatsSchema),
    },
  ],
}));

// Register tool call handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'read_file':
        return await readFileTool(readFileSchema.parse(args), allowedPaths);
      case 'list_files':
        return await listFilesTool(listFilesSchema.parse(args), allowedPaths);
      case 'search_files':
        return await searchFilesTool(searchFilesSchema.parse(args), allowedPaths);
      case 'get_stats':
        return await getStatsTool(getStatsSchema.parse(args), allowedPaths);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text' as const,
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Filesystem MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
