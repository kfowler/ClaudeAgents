/**
 * MCP Protocol Type Definitions
 * Based on Model Context Protocol specification 2024-11-05
 */

export interface ServerInfo {
  name: string;
  version: string;
}

export interface ClientInfo {
  name: string;
  version: string;
}

export interface ServerCapabilities {
  tools?: Record<string, unknown>;
  resources?: {
    subscribe?: boolean;
    listChanged?: boolean;
  };
  prompts?: Record<string, unknown>;
  logging?: Record<string, unknown>;
}

export interface ClientCapabilities {
  roots?: {
    listChanged?: boolean;
  };
  sampling?: Record<string, unknown>;
  experimental?: Record<string, unknown>;
}

export interface InitializeRequest {
  protocolVersion: string;
  capabilities: ClientCapabilities;
  clientInfo: ClientInfo;
}

export interface InitializeResponse {
  protocolVersion: string;
  capabilities: ServerCapabilities;
  serverInfo: ServerInfo;
}

export interface JSONRPCRequest {
  jsonrpc: '2.0';
  id: number | string;
  method: string;
  params?: Record<string, unknown> | unknown[];
}

export interface JSONRPCResponse {
  jsonrpc: '2.0';
  id: number | string;
  result?: unknown;
  error?: JSONRPCError;
}

export interface JSONRPCNotification {
  jsonrpc: '2.0';
  method: string;
  params?: Record<string, unknown> | unknown[];
}

export interface JSONRPCError {
  code: number;
  message: string;
  data?: unknown;
}

export const JSONRPCErrorCode = {
  ParseError: -32700,
  InvalidRequest: -32600,
  MethodNotFound: -32601,
  InvalidParams: -32602,
  InternalError: -32603,
  ServerError: -32000,
  CapabilityError: -32001,
  ResourceError: -32002,
  ToolError: -32003,
} as const;
