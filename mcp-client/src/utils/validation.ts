/**
 * Validation utilities for MCP client
 */

import { JSONSchema } from '../types/tools.js';
import { ValidationError } from '../types/errors.js';

/**
 * Basic JSON Schema validation
 * Note: This is a simplified implementation for preview.
 * Production should use a full JSON Schema validator like Ajv.
 */
export function validateAgainstSchema(
  data: unknown,
  schema: JSONSchema,
  path = 'root'
): void {
  // Type validation
  const actualType = Array.isArray(data) ? 'array' : typeof data;

  if (schema.type && actualType !== schema.type) {
    throw new ValidationError(
      `Type mismatch at ${path}: expected ${schema.type}, got ${actualType}`
    );
  }

  // Object property validation
  if (schema.type === 'object' && typeof data === 'object' && data !== null) {
    const obj = data as Record<string, unknown>;

    // Required properties
    if (schema.required) {
      for (const requiredProp of schema.required) {
        if (!(requiredProp in obj)) {
          throw new ValidationError(
            `Missing required property: ${path}.${requiredProp}`
          );
        }
      }
    }

    // Validate nested properties
    if (schema.properties) {
      for (const [key, value] of Object.entries(obj)) {
        if (schema.properties[key]) {
          validateAgainstSchema(value, schema.properties[key], `${path}.${key}`);
        }
      }
    }
  }

  // Array item validation
  if (schema.type === 'array' && Array.isArray(data)) {
    if (schema.items) {
      data.forEach((item, index) => {
        validateAgainstSchema(item, schema.items!, `${path}[${index}]`);
      });
    }
  }

  // Enum validation
  if (schema.enum && !schema.enum.includes(data)) {
    throw new ValidationError(
      `Value at ${path} must be one of: ${schema.enum.join(', ')}`
    );
  }
}
