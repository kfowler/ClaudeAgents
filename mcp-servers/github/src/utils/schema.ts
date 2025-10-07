/**
 * Convert Zod schema to JSON Schema
 */

import { z } from 'zod';

export function zodToJsonSchema(schema: z.ZodType<any>): any {
  // Simplified conversion for common types
  // For production, use @anatine/zod-to-openapi or similar

  if (schema instanceof z.ZodObject) {
    const shape = schema.shape;
    const properties: Record<string, any> = {};
    const required: string[] = [];

    for (const [key, value] of Object.entries(shape)) {
      properties[key] = zodToJsonSchema(value as z.ZodType<any>);

      // Check if required
      if (!(value instanceof z.ZodOptional) && !(value instanceof z.ZodDefault)) {
        required.push(key);
      }
    }

    return {
      type: 'object',
      properties,
      required: required.length > 0 ? required : undefined,
    };
  }

  if (schema instanceof z.ZodString) {
    return {
      type: 'string',
      description: schema.description,
    };
  }

  if (schema instanceof z.ZodNumber) {
    return {
      type: 'number',
      description: schema.description,
    };
  }

  if (schema instanceof z.ZodBoolean) {
    return {
      type: 'boolean',
      description: schema.description,
    };
  }

  if (schema instanceof z.ZodArray) {
    return {
      type: 'array',
      items: zodToJsonSchema(schema.element),
      description: schema.description,
    };
  }

  if (schema instanceof z.ZodEnum) {
    return {
      type: 'string',
      enum: schema.options,
      description: schema.description,
    };
  }

  if (schema instanceof z.ZodOptional) {
    return zodToJsonSchema(schema.unwrap());
  }

  if (schema instanceof z.ZodDefault) {
    const innerSchema = zodToJsonSchema(schema.removeDefault());
    return {
      ...innerSchema,
      default: schema._def.defaultValue(),
    };
  }

  // Fallback
  return { type: 'string' };
}
