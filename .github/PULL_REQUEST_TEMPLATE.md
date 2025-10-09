# Pull Request

## Description

<!-- Provide a clear and concise description of what this PR does -->

### Type of Change

- [ ] New agent
- [ ] New command/workflow
- [ ] Bug fix
- [ ] Enhancement to existing agent/command
- [ ] Documentation update
- [ ] Infrastructure/tooling improvement
- [ ] Other (please describe):

## Changes Made

<!-- List the key changes in this PR -->

-
-
-

## Why These Changes?

<!-- Explain the motivation and context for these changes -->



## How to Test

<!-- Provide step-by-step instructions for testing these changes -->

1.
2.
3.

## Screenshots / Examples

<!-- If applicable, add screenshots or command examples -->

```bash
# Example usage

```

## Checklist

### Required

- [ ] Validation passes (`python3 tools/validate_agents.py`)
- [ ] All tests pass (`python3 -m pytest tests/ -v`)
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive data (API keys, credentials, etc.) included

### Agent-Specific (if applicable)

- [ ] Used `tools/create_agent.py` OR manually validated frontmatter
- [ ] Model tier appropriate for complexity (haiku/sonnet/opus)
- [ ] Description is 50-500 characters
- [ ] Agent name matches filename
- [ ] Professional Manifesto Commitment section completed
- [ ] Deliverables and limitations clearly defined
- [ ] Anti-Mock Enforcement principles followed

### Command-Specific (if applicable)

- [ ] Used `tools/create_command.py` OR manually validated structure
- [ ] All referenced agents exist
- [ ] Multi-agent orchestration clearly explained
- [ ] Phase-based workflow is logical
- [ ] Rationale provided for agent selection
- [ ] Success criteria defined

### Documentation

- [ ] Updated README.md (if user-facing changes)
- [ ] Updated CLAUDE.md (if agent selection or patterns changed)
- [ ] Added examples or usage documentation
- [ ] Updated relevant docs/ files

## Breaking Changes

<!-- List any breaking changes or migrations required -->

- [ ] No breaking changes
- [ ] Breaking changes (describe below):

<!-- If breaking changes, describe the impact and migration path -->



## Related Issues

<!-- Link to related issues -->

Closes #
Related to #

## Professional Standards

This PR adheres to [The Manifesto](../docs/manifesto.md) principles:

- [ ] **Truth Over Theater**: Real systems, not mocks or demonstrations
- [ ] **Reality-First Development**: Connects to actual integrations
- [ ] **Professional Accountability**: Work is signed and verifiable
- [ ] **User Value**: Solves real problems with measurable outcomes

## Additional Context

<!-- Add any other context, dependencies, or notes -->



---

**For Reviewers:**
- [ ] Code quality and maintainability
- [ ] Adherence to project standards
- [ ] Test coverage adequate
- [ ] Documentation clarity
- [ ] No security concerns
