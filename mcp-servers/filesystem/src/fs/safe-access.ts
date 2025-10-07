/**
 * Safe filesystem access with path validation
 * Prevents directory traversal and restricts access to allowed paths
 */

import { resolve, normalize, relative } from 'path';

/**
 * Validates that a requested path is within allowed directories
 * Prevents directory traversal attacks
 */
export function validatePath(
  requestedPath: string,
  allowedPaths: string[]
): string {
  if (allowedPaths.length === 0) {
    throw new Error('No allowed paths configured. Server must specify allowed directories.');
  }

  const normalizedPath = normalize(resolve(requestedPath));

  for (const allowedPath of allowedPaths) {
    const normalizedAllowed = normalize(resolve(allowedPath));

    // Check if path is within allowed directory
    const rel = relative(normalizedAllowed, normalizedPath);

    // If relative path doesn't start with .. or is empty, it's within allowed path
    if (rel && !rel.startsWith('..') && !path.isAbsolute(rel)) {
      return normalizedPath;
    }

    // Handle exact match
    if (normalizedPath === normalizedAllowed) {
      return normalizedPath;
    }
  }

  throw new Error(
    `Access denied: "${requestedPath}" is outside allowed directories.\n` +
      `Allowed paths: ${allowedPaths.join(', ')}`
  );
}

// Import path module
import path from 'path';
