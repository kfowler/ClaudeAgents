/**
 * @claudeagents/mcp-client
 * Model Context Protocol client for ClaudeAgents
 */

export { MCPClient } from './client.js';
export type { MCPClientConfig } from './client.js';

export { StdioTransport } from './transport/stdio.js';
export type { StdioTransportConfig } from './transport/stdio.js';
export type { Transport } from './transport/base.js';

export type {
  ServerInfo,
  ServerCapabilities,
  ClientCapabilities,
  InitializeRequest,
  InitializeResponse,
  JSONRPCRequest,
  JSONRPCResponse,
  JSONRPCNotification,
} from './types/protocol.js';

export type {
  Tool,
  ToolListResponse,
  ToolCallRequest,
  ToolResult,
  Content,
  JSONSchema,
} from './types/tools.js';

export {
  MCPError,
  TransportError,
  ValidationError,
  ConnectionError,
} from './types/errors.js';
