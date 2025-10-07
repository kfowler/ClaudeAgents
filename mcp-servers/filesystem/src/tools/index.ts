/**
 * Filesystem MCP Server Tools
 */

import { z } from 'zod';
import { readFile, readdir, stat } from 'fs/promises';
import { join, basename } from 'path';
import { validatePath } from '../fs/safe-access.js';

// Tool Schemas
export const readFileSchema = z.object({
  path: z.string().describe('File path to read'),
  encoding: z.enum(['utf8', 'base64']).default('utf8').optional(),
});

export const listFilesSchema = z.object({
  path: z.string().describe('Directory path to list'),
  pattern: z.string().optional().describe('Glob pattern to filter files'),
});

export const searchFilesSchema = z.object({
  query: z.string().describe('Search pattern (regex supported)'),
  path: z.string().describe('Directory to search'),
  filePattern: z.string().optional().describe('File glob pattern (e.g., "*.ts")'),
});

export const getStatsSchema = z.object({
  path: z.string().describe('Path to analyze'),
});

// Helper to format file sizes
function formatSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

// Tool Implementations
export async function readFileTool(
  args: z.infer<typeof readFileSchema>,
  allowedPaths: string[]
) {
  const safePath = validatePath(args.path, allowedPaths);
  const encoding = (args.encoding || 'utf8') as BufferEncoding;

  const content = await readFile(safePath, encoding);

  return {
    content: [
      {
        type: 'text' as const,
        text: `File: ${args.path}\n\n${content}`,
      },
    ],
    isError: false,
  };
}

export async function listFilesTool(
  args: z.infer<typeof listFilesSchema>,
  allowedPaths: string[]
) {
  const safePath = validatePath(args.path, allowedPaths);

  const entries = await readdir(safePath, { withFileTypes: true });

  const formatted = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = join(safePath, entry.name);
      const stats = await stat(fullPath);
      const type = entry.isDirectory() ? 'DIR ' : 'FILE';
      const size = entry.isDirectory() ? '' : ` (${formatSize(stats.size)})`;
      return `[${type}] ${entry.name}${size}`;
    })
  );

  return {
    content: [
      {
        type: 'text' as const,
        text: `Contents of ${args.path}:\n\n${formatted.join('\n')}`,
      },
    ],
    isError: false,
  };
}

export async function searchFilesTool(
  args: z.infer<typeof searchFilesSchema>,
  allowedPaths: string[]
) {
  const safePath = validatePath(args.path, allowedPaths);

  // Simple grep-like search (recursive)
  const results: string[] = [];
  const regex = new RegExp(args.query, 'i');

  async function searchDir(dirPath: string, depth = 0): Promise<void> {
    if (depth > 10) return; // Prevent too deep recursion

    const entries = await readdir(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = join(dirPath, entry.name);

      if (entry.isDirectory()) {
        await searchDir(fullPath, depth + 1);
      } else if (entry.isFile()) {
        // Check file pattern if provided
        if (args.filePattern) {
          const pattern = args.filePattern.replace(/\*/g, '.*');
          const fileRegex = new RegExp(pattern);
          if (!fileRegex.test(entry.name)) {
            continue;
          }
        }

        try {
          const content = await readFile(fullPath, 'utf8');
          const lines = content.split('\n');

          lines.forEach((line, index) => {
            if (regex.test(line)) {
              results.push(`${fullPath}:${index + 1}: ${line.trim()}`);
            }
          });
        } catch (err) {
          // Skip files that can't be read (binary, permission denied, etc.)
        }
      }
    }
  }

  await searchDir(safePath);

  if (results.length === 0) {
    return {
      content: [
        {
          type: 'text' as const,
          text: `No matches found for "${args.query}" in ${args.path}`,
        },
      ],
      isError: false,
    };
  }

  return {
    content: [
      {
        type: 'text' as const,
        text: `Search results for "${args.query}":\n\n${results.slice(0, 50).join('\n')}\n\n${
          results.length > 50 ? `(Showing first 50 of ${results.length} matches)` : ''
        }`,
      },
    ],
    isError: false,
  };
}

export async function getStatsTool(
  args: z.infer<typeof getStatsSchema>,
  allowedPaths: string[]
) {
  const safePath = validatePath(args.path, allowedPaths);
  const stats = await stat(safePath);

  let details = `
**Path:** ${args.path}
**Type:** ${stats.isDirectory() ? 'Directory' : 'File'}
**Size:** ${formatSize(stats.size)}
**Created:** ${stats.birthtime.toISOString()}
**Modified:** ${stats.mtime.toISOString()}
**Permissions:** ${(stats.mode & 0o777).toString(8)}
  `.trim();

  if (stats.isDirectory()) {
    const files = await readdir(safePath);
    details += `\n**Items:** ${files.length}`;
  }

  return {
    content: [{ type: 'text' as const, text: details }],
    isError: false,
  };
}
