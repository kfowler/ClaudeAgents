/**
 * Base Transport Interface
 * Defines contract for MCP transport implementations
 */

import { JSONRPCRequest, JSONRPCResponse, JSONRPCNotification } from '../types/protocol.js';

export interface Transport {
  /**
   * Establish connection to MCP server
   */
  connect(): Promise<void>;

  /**
   * Close connection to MCP server
   */
  disconnect(): Promise<void>;

  /**
   * Send a message to the server
   * @param message JSON-RPC request or notification
   * @returns Promise resolving to response (for requests) or void (for notifications)
   */
  send(message: JSONRPCRequest | JSONRPCNotification): Promise<JSONRPCResponse | void>;

  /**
   * Check if transport is currently connected
   */
  isConnected(): boolean;

  /**
   * Register a handler for server-initiated notifications
   */
  onNotification(handler: (notification: JSONRPCNotification) => void): void;
}
