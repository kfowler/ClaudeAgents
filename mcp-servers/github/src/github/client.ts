/**
 * GitHub API client wrapper
 */

import { Octokit } from '@octokit/rest';

let githubClient: Octokit | null = null;

export function getGitHubClient(): Octokit {
  if (!githubClient) {
    const token = process.env.GITHUB_TOKEN;
    if (!token) {
      throw new Error('GITHUB_TOKEN environment variable is required');
    }

    githubClient = new Octokit({
      auth: token,
    });
  }

  return githubClient;
}

export function parseRepo(repo: string): { owner: string; repo: string } {
  const parts = repo.split('/');
  if (parts.length !== 2) {
    throw new Error(`Invalid repository format: ${repo}. Expected owner/repo`);
  }
  return { owner: parts[0], repo: parts[1] };
}
