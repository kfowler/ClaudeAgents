/**
 * MCP Client Implementation
 * Main client class for connecting to and interacting with MCP servers
 */

import { Transport } from './transport/base.js';
import {
  ServerInfo,
  ServerCapabilities,
  InitializeRequest,
  InitializeResponse,
  JSONRPCRequest,
  JSONRPCResponse,
  JSONRPCNotification,
} from './types/protocol.js';
import {
  Tool,
  ToolListResponse,
  ToolCallRequest,
  ToolResult,
} from './types/tools.js';
import {
  MCPError,
  ConnectionError,
  ValidationError,
} from './types/errors.js';

export interface MCPClientConfig {
  name?: string;
  version?: string;
  protocolVersion?: string;
}

export class MCPClient {
  private transport?: Transport;
  private serverInfo?: ServerInfo;
  private capabilities?: ServerCapabilities;
  private requestId = 0;
  private initialized = false;

  private readonly config: Required<MCPClientConfig>;

  constructor(config: MCPClientConfig = {}) {
    this.config = {
      name: config.name || 'ClaudeAgents',
      version: config.version || '1.0.0',
      protocolVersion: config.protocolVersion || '2024-11-05',
    };
  }

  /**
   * Connect to an MCP server and perform initialization handshake
   */
  async connect(transport: Transport): Promise<ServerInfo> {
    if (this.initialized) {
      throw new ConnectionError('Client already connected to a server');
    }

    this.transport = transport;

    // Establish transport connection
    await transport.connect();

    // Perform initialization handshake
    await this.initialize();

    return this.serverInfo!;
  }

  /**
   * Disconnect from MCP server
   */
  async disconnect(): Promise<void> {
    if (this.transport) {
      await this.transport.disconnect();
      this.transport = undefined;
    }
    this.initialized = false;
    this.serverInfo = undefined;
    this.capabilities = undefined;
  }

  /**
   * Check if client is connected to server
   */
  isConnected(): boolean {
    return this.initialized && !!this.transport?.isConnected();
  }

  /**
   * Get server information
   */
  getServerInfo(): ServerInfo | undefined {
    return this.serverInfo;
  }

  /**
   * Get server capabilities
   */
  getCapabilities(): ServerCapabilities | undefined {
    return this.capabilities;
  }

  /**
   * List available tools from server
   * @param cursor Pagination cursor (optional)
   */
  async listTools(cursor?: string): Promise<ToolListResponse> {
    this.ensureInitialized();
    this.ensureCapability('tools');

    const params: Record<string, unknown> = {};
    if (cursor) {
      params.cursor = cursor;
    }

    const response = await this.sendRequest('tools/list', params);

    return {
      tools: response.tools as Tool[],
      nextCursor: response.nextCursor as string | undefined,
    };
  }

  /**
   * Invoke a tool by name
   * @param name Tool name
   * @param args Tool arguments
   */
  async callTool(name: string, args: Record<string, unknown> = {}): Promise<ToolResult> {
    this.ensureInitialized();
    this.ensureCapability('tools');

    const request: ToolCallRequest = {
      name,
      arguments: args,
    };

    const response = await this.sendRequest('tools/call', request);

    return {
      content: response.content || [],
      isError: response.isError || false,
    };
  }

  /**
   * Register a handler for server notifications
   */
  onNotification(handler: (notification: JSONRPCNotification) => void): void {
    if (!this.transport) {
      throw new ConnectionError('Not connected to server');
    }
    this.transport.onNotification(handler);
  }

  /**
   * Perform initialization handshake with server
   */
  private async initialize(): Promise<void> {
    const initRequest: InitializeRequest = {
      protocolVersion: this.config.protocolVersion,
      capabilities: {
        roots: {
          listChanged: true,
        },
      },
      clientInfo: {
        name: this.config.name,
        version: this.config.version,
      },
    };

    const response = await this.sendRequest('initialize', initRequest);

    const initResponse = response as unknown as InitializeResponse;

    // Validate protocol version compatibility
    if (initResponse.protocolVersion !== this.config.protocolVersion) {
      throw new ValidationError(
        `Protocol version mismatch: client=${this.config.protocolVersion}, server=${initResponse.protocolVersion}`
      );
    }

    this.serverInfo = initResponse.serverInfo;
    this.capabilities = initResponse.capabilities;

    // Send initialized notification
    await this.sendNotification('notifications/initialized');

    this.initialized = true;
  }

  /**
   * Send JSON-RPC request to server
   */
  private async sendRequest(
    method: string,
    params?: Record<string, unknown>
  ): Promise<any> {
    if (!this.transport) {
      throw new ConnectionError('Not connected to server');
    }

    const id = ++this.requestId;
    const request: JSONRPCRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params: params || {},
    };

    const response = await this.transport.send(request) as JSONRPCResponse;

    if (response.error) {
      throw MCPError.fromJSONRPCError(response.error);
    }

    return response.result;
  }

  /**
   * Send JSON-RPC notification to server (no response expected)
   */
  private async sendNotification(
    method: string,
    params?: Record<string, unknown>
  ): Promise<void> {
    if (!this.transport) {
      throw new ConnectionError('Not connected to server');
    }

    const notification: JSONRPCNotification = {
      jsonrpc: '2.0',
      method,
      params,
    };

    await this.transport.send(notification);
  }

  /**
   * Ensure client is initialized
   */
  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new ConnectionError('Client not initialized. Call connect() first.');
    }
  }

  /**
   * Ensure server supports required capability
   */
  private ensureCapability(capability: keyof ServerCapabilities): void {
    if (!this.capabilities?.[capability]) {
      throw new MCPError(
        -32001,
        `Server does not support '${capability}' capability`,
        { capability }
      );
    }
  }
}
