/**
 * GitHub MCP Server Tools
 * Consolidated tool implementations
 */

import { z } from 'zod';
import { getGitHubClient, parseRepo } from '../github/client.js';

// Tool Schemas
export const searchCodeSchema = z.object({
  query: z.string().describe('Search query (code, path, or regex)'),
  repo: z.string().describe('Repository in owner/repo format'),
  language: z.string().optional().describe('Filter by language'),
  path: z.string().optional().describe('Limit search to path'),
});

export const analyzePRSchema = z.object({
  repo: z.string().describe('Repository in owner/repo format'),
  pr_number: z.number().describe('Pull request number'),
});

export const listIssuesSchema = z.object({
  repo: z.string().describe('Repository in owner/repo format'),
  state: z.enum(['open', 'closed', 'all']).default('open'),
  labels: z.array(z.string()).optional().describe('Filter by labels'),
  limit: z.number().default(10).describe('Max results (1-100)'),
});

export const createIssueSchema = z.object({
  repo: z.string().describe('Repository in owner/repo format'),
  title: z.string().describe('Issue title'),
  body: z.string().optional().describe('Issue body (markdown)'),
  labels: z.array(z.string()).optional().describe('Labels to apply'),
  assignees: z.array(z.string()).optional().describe('Users to assign'),
});

// Tool Implementations
export async function searchCode(args: z.infer<typeof searchCodeSchema>) {
  const github = getGitHubClient();
  const { query, repo, language, path } = args;

  let searchQuery = `${query} repo:${repo}`;
  if (language) searchQuery += ` language:${language}`;
  if (path) searchQuery += ` path:${path}`;

  const results = await github.search.code({
    q: searchQuery,
    per_page: 10,
  });

  const formatted = results.data.items
    .map(
      (item) =>
        `**${item.path}** (${item.repository.full_name})\n` +
        `URL: ${item.html_url}\n`
    )
    .join('\n---\n');

  return {
    content: [
      {
        type: 'text' as const,
        text: `Found ${results.data.total_count} results:\n\n${formatted}`,
      },
    ],
    isError: false,
  };
}

export async function analyzePR(args: z.infer<typeof analyzePRSchema>) {
  const github = getGitHubClient();
  const { owner, repo } = parseRepo(args.repo);
  const prNumber = args.pr_number;

  const [pr, files, reviews] = await Promise.all([
    github.pulls.get({ owner, repo, pull_number: prNumber }),
    github.pulls.listFiles({ owner, repo, pull_number: prNumber }),
    github.pulls.listReviews({ owner, repo, pull_number: prNumber }),
  ]);

  const analysis = `
# Pull Request #${prNumber} Analysis

**Title:** ${pr.data.title}
**Author:** ${pr.data.user?.login}
**Status:** ${pr.data.state} ${pr.data.merged ? '(merged)' : ''}
**Branch:** ${pr.data.head.ref} → ${pr.data.base.ref}

## Changes Summary
- **Files changed:** ${pr.data.changed_files}
- **Additions:** +${pr.data.additions}
- **Deletions:** -${pr.data.deletions}
- **Commits:** ${pr.data.commits}

## Files Modified
${files.data.map((f) => `- **${f.filename}** (+${f.additions}/-${f.deletions}) [${f.status}]`).join('\n')}

## Review Status
${
  reviews.data.length > 0
    ? reviews.data.map((r) => `- ${r.user?.login}: ${r.state}`).join('\n')
    : '- No reviews yet'
}

## Description
${pr.data.body || 'No description provided'}
  `.trim();

  return {
    content: [{ type: 'text' as const, text: analysis }],
    isError: false,
  };
}

export async function listIssues(args: z.infer<typeof listIssuesSchema>) {
  const github = getGitHubClient();
  const { owner, repo } = parseRepo(args.repo);

  const issues = await github.issues.listForRepo({
    owner,
    repo,
    state: args.state,
    labels: args.labels?.join(','),
    per_page: Math.min(args.limit, 100),
  });

  const formatted = issues.data
    .map(
      (issue) =>
        `**#${issue.number}** ${issue.title}\n` +
        `State: ${issue.state} | Comments: ${issue.comments}\n` +
        `Created: ${issue.created_at} by ${issue.user?.login}\n` +
        `URL: ${issue.html_url}\n`
    )
    .join('\n---\n');

  return {
    content: [
      {
        type: 'text' as const,
        text: `Found ${issues.data.length} issues:\n\n${formatted}`,
      },
    ],
    isError: false,
  };
}

export async function createIssue(args: z.infer<typeof createIssueSchema>) {
  const github = getGitHubClient();
  const { owner, repo } = parseRepo(args.repo);

  const issue = await github.issues.create({
    owner,
    repo,
    title: args.title,
    body: args.body,
    labels: args.labels,
    assignees: args.assignees,
  });

  return {
    content: [
      {
        type: 'text' as const,
        text:
          `✓ Created issue #${issue.data.number}\n\n` +
          `**Title:** ${issue.data.title}\n` +
          `**URL:** ${issue.data.html_url}\n` +
          `**State:** ${issue.data.state}`,
      },
    ],
    isError: false,
  };
}
