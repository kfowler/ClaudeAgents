/**
 * Example usage of MCP client
 * This demonstrates connecting to an MCP server and invoking tools
 */

import { MCPClient, StdioTransport } from './src/index.js';

async function main() {
  console.log('MCP Client Example\n');

  // Create client
  const client = new MCPClient({
    name: 'ExampleClient',
    version: '1.0.0',
  });

  try {
    // Connect to GitHub MCP server
    console.log('Connecting to GitHub MCP server...');
    const serverInfo = await client.connect(
      new StdioTransport({
        command: 'node',
        args: ['../mcp-servers/github/dist/index.js'],
        env: {
          GITHUB_TOKEN: process.env.GITHUB_TOKEN || '',
        },
      })
    );

    console.log(`✓ Connected to ${serverInfo.name} v${serverInfo.version}\n`);

    // Get server capabilities
    const capabilities = client.getCapabilities();
    console.log('Server capabilities:', Object.keys(capabilities || {}));
    console.log();

    // List available tools
    console.log('Listing available tools...');
    const { tools } = await client.listTools();
    console.log(`✓ Found ${tools.length} tools:\n`);

    tools.forEach((tool) => {
      console.log(`  ${tool.name}`);
      console.log(`    ${tool.description}`);
      console.log(`    Input: ${JSON.stringify(tool.inputSchema.properties)}`);
      console.log();
    });

    // Example 1: Search code
    console.log('Example 1: Searching for code...');
    const searchResult = await client.callTool('search_code', {
      query: 'async function',
      repo: 'facebook/react',
      language: 'javascript',
    });

    if (searchResult.isError) {
      console.error('  Error:', searchResult.content[0].text);
    } else {
      console.log('  ✓ Search results:');
      console.log(searchResult.content[0].text);
    }
    console.log();

    // Example 2: List issues
    console.log('Example 2: Listing repository issues...');
    const issuesResult = await client.callTool('list_issues', {
      repo: 'facebook/react',
      state: 'open',
      limit: 5,
    });

    if (issuesResult.isError) {
      console.error('  Error:', issuesResult.content[0].text);
    } else {
      console.log('  ✓ Issues:');
      console.log(issuesResult.content[0].text);
    }
    console.log();

    // Disconnect
    console.log('Disconnecting...');
    await client.disconnect();
    console.log('✓ Disconnected');
  } catch (error) {
    console.error('Error:', error);
    await client.disconnect();
    process.exit(1);
  }
}

main();
