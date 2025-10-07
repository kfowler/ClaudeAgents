#!/usr/bin/env node

/**
 * GitHub MCP Server
 * Exposes GitHub operations as MCP tools
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import {
  searchCode,
  searchCodeSchema,
  analyzePR,
  analyzePRSchema,
  listIssues,
  listIssuesSchema,
  createIssue,
  createIssueSchema,
} from './tools/index.js';

import { zodToJsonSchema } from './utils/schema.js';

const server = new Server(
  {
    name: 'github-mcp-server',
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
      name: 'search_code',
      description: 'Search for code in a GitHub repository',
      inputSchema: zodToJsonSchema(searchCodeSchema),
    },
    {
      name: 'analyze_pr',
      description: 'Analyze a GitHub pull request in detail',
      inputSchema: zodToJsonSchema(analyzePRSchema),
    },
    {
      name: 'list_issues',
      description: 'List issues in a GitHub repository',
      inputSchema: zodToJsonSchema(listIssuesSchema),
    },
    {
      name: 'create_issue',
      description: 'Create a new GitHub issue',
      inputSchema: zodToJsonSchema(createIssueSchema),
    },
  ],
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
  console.error('GitHub MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
