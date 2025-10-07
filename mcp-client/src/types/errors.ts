/**
 * MCP Error Types
 */

export class MCPError extends Error {
  constructor(
    public code: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'MCPError';
    Object.setPrototypeOf(this, MCPError.prototype);
  }

  static isRPCError(error: unknown): error is MCPError {
    return error instanceof MCPError;
  }

  static fromJSONRPCError(error: { code: number; message: string; data?: unknown }): MCPError {
    return new MCPError(error.code, error.message, error.data);
  }

  toJSON() {
    return {
      code: this.code,
      message: this.message,
      data: this.data,
    };
  }
}

export class TransportError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'TransportError';
    Object.setPrototypeOf(this, TransportError.prototype);
  }
}

export class ValidationError extends Error {
  constructor(message: string, public details?: unknown) {
    super(message);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

export class ConnectionError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'ConnectionError';
    Object.setPrototypeOf(this, ConnectionError.prototype);
  }
}
