/**
 * MCP Tool Type Definitions
 */

export interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchema>;
  required?: string[];
  items?: JSONSchema;
  description?: string;
  enum?: unknown[];
  default?: unknown;
  [key: string]: unknown;
}

export interface Tool {
  name: string;
  title?: string;
  description: string;
  inputSchema: JSONSchema;
  outputSchema?: JSONSchema;
}

export interface ToolListResponse {
  tools: Tool[];
  nextCursor?: string;
}

export interface ToolCallRequest {
  name: string;
  arguments: Record<string, unknown>;
}

export interface Content {
  type: 'text' | 'image' | 'audio' | 'resource' | 'embedded_resource';
  text?: string;
  data?: string; // Base64 encoded for images/audio
  uri?: string; // For resource references
  mimeType?: string;
  [key: string]: unknown;
}

export interface ToolResult {
  content: Content[];
  isError?: boolean;
}

export interface ToolCallResponse {
  content: Content[];
  isError?: boolean;
}
