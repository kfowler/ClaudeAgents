/**
 * Stdio Transport Implementation
 * Communicates with MCP server via standard input/output
 */

import { spawn, ChildProcess } from 'child_process';
import { Transport } from './base.js';
import { JSONRPCRequest, JSONRPCResponse, JSONRPCNotification } from '../types/protocol.js';
import { TransportError, ConnectionError } from '../types/errors.js';

export interface StdioTransportConfig {
  command: string;
  args?: string[];
  env?: Record<string, string>;
  cwd?: string;
}

interface PendingRequest {
  resolve: (value: JSONRPCResponse) => void;
  reject: (error: Error) => void;
  timeout?: NodeJS.Timeout;
}

export class StdioTransport implements Transport {
  private process?: ChildProcess;
  private buffer = '';
  private pendingRequests = new Map<number | string, PendingRequest>();
  private notificationHandlers: Array<(notification: JSONRPCNotification) => void> = [];
  private connected = false;
  private readonly requestTimeout = 30000; // 30 seconds

  constructor(private config: StdioTransportConfig) {}

  async connect(): Promise<void> {
    if (this.connected) {
      throw new ConnectionError('Transport already connected');
    }

    try {
      const env = { ...process.env, ...this.config.env };

      this.process = spawn(this.config.command, this.config.args || [], {
        env,
        cwd: this.config.cwd,
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      // Handle stdout (server messages)
      this.process.stdout!.setEncoding('utf8');
      this.process.stdout!.on('data', (data: string) => {
        this.handleData(data);
      });

      // Handle stderr (server logs/errors)
      this.process.stderr!.setEncoding('utf8');
      this.process.stderr!.on('data', (data: string) => {
        // Log stderr but don't treat as fatal
        if (process.env.DEBUG) {
          console.error('[MCP Server]', data.trim());
        }
      });

      // Handle process exit
      this.process.on('exit', (code, signal) => {
        this.connected = false;
        const error = new ConnectionError(
          `MCP server process exited with code ${code}, signal ${signal}`
        );
        this.rejectAllPending(error);
      });

      // Handle process errors
      this.process.on('error', (err) => {
        this.connected = false;
        const error = new TransportError('Failed to spawn MCP server process', err);
        this.rejectAllPending(error);
        throw error;
      });

      this.connected = true;
    } catch (error) {
      throw new ConnectionError(
        'Failed to connect to MCP server',
        error as Error
      );
    }
  }

  async disconnect(): Promise<void> {
    if (!this.process) {
      return;
    }

    // Reject all pending requests
    this.rejectAllPending(new ConnectionError('Transport disconnected'));

    // Kill process
    this.process.kill('SIGTERM');

    // Wait for process to exit (with timeout)
    await new Promise<void>((resolve) => {
      if (!this.process) {
        resolve();
        return;
      }

      const timeout = setTimeout(() => {
        if (this.process) {
          this.process.kill('SIGKILL');
        }
        resolve();
      }, 5000);

      this.process.once('exit', () => {
        clearTimeout(timeout);
        resolve();
      });
    });

    this.process = undefined;
    this.connected = false;
    this.buffer = '';
  }

  async send(message: JSONRPCRequest | JSONRPCNotification): Promise<JSONRPCResponse | void> {
    if (!this.connected || !this.process || !this.process.stdin) {
      throw new ConnectionError('Transport not connected');
    }

    try {
      // Serialize message
      const json = JSON.stringify(message) + '\n';

      // Write to stdin
      const written = this.process.stdin.write(json);
      if (!written) {
        throw new TransportError('Failed to write to server stdin');
      }

      // If this is a request (has id), wait for response
      if ('id' in message && message.id !== undefined) {
        return new Promise<JSONRPCResponse>((resolve, reject) => {
          const timeout = setTimeout(() => {
            this.pendingRequests.delete(message.id);
            reject(new TransportError(`Request ${message.id} timed out after ${this.requestTimeout}ms`));
          }, this.requestTimeout);

          this.pendingRequests.set(message.id, { resolve, reject, timeout });
        });
      }

      // Notification - no response expected
      return undefined;
    } catch (error) {
      throw new TransportError('Failed to send message', error as Error);
    }
  }

  isConnected(): boolean {
    return this.connected && this.process !== undefined && !this.process.killed;
  }

  onNotification(handler: (notification: JSONRPCNotification) => void): void {
    this.notificationHandlers.push(handler);
  }

  private handleData(data: string): void {
    this.buffer += data;

    // Process complete JSON messages (newline-delimited)
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.trim()) {
        try {
          const message = JSON.parse(line);
          this.handleMessage(message);
        } catch (err) {
          console.error('[MCP Client] Failed to parse message:', line, err);
        }
      }
    }
  }

  private handleMessage(message: JSONRPCResponse | JSONRPCNotification): void {
    // Handle response to request
    if ('id' in message && message.id !== undefined) {
      const pending = this.pendingRequests.get(message.id);
      if (pending) {
        if (pending.timeout) {
          clearTimeout(pending.timeout);
        }
        this.pendingRequests.delete(message.id);
        pending.resolve(message as JSONRPCResponse);
      } else {
        console.warn('[MCP Client] Received response for unknown request:', message.id);
      }
    }
    // Handle notification (no id)
    else if ('method' in message && message.method) {
      const notification = message as JSONRPCNotification;
      for (const handler of this.notificationHandlers) {
        try {
          handler(notification);
        } catch (err) {
          console.error('[MCP Client] Error in notification handler:', err);
        }
      }
    }
  }

  private rejectAllPending(error: Error): void {
    for (const [id, pending] of this.pendingRequests) {
      if (pending.timeout) {
        clearTimeout(pending.timeout);
      }
      pending.reject(error);
    }
    this.pendingRequests.clear();
  }
}
