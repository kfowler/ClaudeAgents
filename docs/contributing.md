# Contributing Guide

Thank you for contributing to the Claude Code Agent System! This guide will help you add new agents, commands, and improvements while maintaining the high quality standards of the project.

## Getting Started

### Prerequisites

```bash
# Clone the repository
git clone <repository-url>
cd ClaudeAgents

# Install dependencies
pip install -r tools/requirements.txt
pip install -r tools/requirements-dev.txt
```

### Development Workflow

1. Create a feature branch: `git checkout -b your-username/feature-name`
2. Make your changes
3. Run validation and tests
4. Commit with descriptive messages
5. Submit a pull request

## Adding a New Agent

### Step 1: Create Agent File

Copy the template:
```bash
cp agents/AGENT_TEMPLATE.md agents/your-agent-name.md
```

### Step 2: Fill in Required Fields

**Frontmatter (YAML):**
```yaml
---
name: your-agent-name
description: "Brief description (50-500 chars). Use quotes if it contains colons."
color: blue
---
```

**Important:**
- `name` must match filename (without `.md`)
- `description` must be 50-500 characters
- Use quotes around description if it contains colons
- Choose a valid color (see list in validator)

### Step 3: Complete Agent Definition

Follow the template structure:
1. **Professional Manifesto Commitment**: Specific promises
2. **Core Implementation Principles**: How agent operates
3. **Responsibilities**: What agent does
4. **Technical Implementation**: Technologies used
5. **Deliverables and Limitations**: What agent provides and doesn't
6. **Key Considerations**: Important factors
7. **Agent Coordination Protocol**: Inter-agent communication
8. **Anti-Mock Enforcement**: Quality standards

### Step 4: Validate

```bash
python3 tools/validate_agents.py
```

Fix any errors or warnings before committing.

### Step 5: Test

```bash
python3 -m pytest tests/ -v
```

Ensure all tests pass.

## Adding a New Command

### Step 1: Choose Directory

Commands are organized by purpose:
- `commands/development/`: Code-related workflows
- `commands/quality/`: Testing, security, performance
- `commands/deployment/`: Infrastructure, deployment
- `commands/specialized/`: Language/framework-specific
- `commands/workflows/`: Multi-agent orchestration

### Step 2: Create Command File

```markdown
---
name: command-name
description: Brief description of what this command does
---

# Command Name

## Overview
What this command accomplishes and when to use it.

## Multi-Agent Orchestration Strategy

### **Phase 1: [Phase Name]**
Deploy `agent-name` to:
- Specific task
- Expected outcome
- Quality criteria

### **Phase 2: [Next Phase]**
Engage `another-agent` to:
- Follow-up tasks
- Integration points
- Deliverables
```

### Step 3: Validate References

Ensure all agent names referenced in the command exist:
```bash
python3 -m pytest tests/test_agent_integration.py::TestAgentIntegration::test_agent_references_in_commands_are_valid -v
```

## Code Quality Standards

### Commit Messages

Follow this format:
```
Brief summary (50 chars or less)

Detailed explanation of changes:
- What changed
- Why it changed
- Impact of changes

Resolves #issue-number (if applicable)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Pull Request Guidelines

**Title:** Clear, descriptive summary

**Description:**
- What changes were made
- Why these changes were needed
- How to test the changes
- Any breaking changes or migrations

**Checklist:**
- [ ] Validation passes (`python3 tools/validate_agents.py`)
- [ ] Tests pass (`python3 -m pytest tests/ -v`)
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear
- [ ] No sensitive data included

## Professional Standards

### The Manifesto

All contributions must align with [The Manifesto](manifesto.md):

- **Truth Over Theater**: Build real systems, not demonstrations
- **Reality-First Development**: Connect to actual systems
- **Professional Accountability**: Sign your work, stand behind it
- **User Value**: Solve real problems with measurable outcomes

### Quality Requirements

1. **No Mock Systems**: Agents must connect to real integrations
2. **Verifiable Claims**: Every capability must be demonstrable
3. **Honest Limitations**: Document what agents cannot do
4. **Clear Communication**: Professional, precise language

## Testing

### Running Tests

```bash
# All tests
python3 -m pytest tests/ -v

# Specific test
python3 -m pytest tests/test_agent_integration.py::TestName -v

# With coverage
python3 -m pytest tests/ --cov=tools --cov-report=html
```

### Writing Tests

Add tests for new functionality:
```python
def test_your_feature(self):
    """Test description."""
    # Arrange
    # Act
    # Assert
```

## Validation Rules

### Agent Files

- ✅ Must have YAML frontmatter
- ✅ Must have name, description fields
- ✅ Name must match filename
- ✅ Description 50-500 characters
- ✅ Must have substantial content body
- ✅ YAML must parse without errors

### Commands

- ✅ Must reference only existing agents
- ✅ Should have clear phase structure
- ✅ Should explain orchestration strategy

## Common Issues

### Validation Failures

**"YAML parsing error"**
- Quote descriptions containing colons: `description: "This: that"`

**"Name mismatch"**
- Ensure frontmatter `name:` matches filename exactly

**"Description too long/short"**
- Keep descriptions between 50-500 characters

**"Invalid color"**
- Use colors from the approved list (see validator output)

### Test Failures

**"Agent references non-existent agent"**
- Check spelling of agent names in commands
- Ensure agent file exists in `agents/` directory

**"Duplicate agent names"**
- Check for name conflicts in frontmatter

## Documentation

### Updating Documentation

When adding features, update:
- `README.md`: User-facing changes
- `CLAUDE.md`: Project instructions for Claude Code
- `docs/architecture.md`: System design changes
- `docs/contributing.md`: Process changes (this file)

### Documentation Style

- **Clear and concise**: No unnecessary words
- **Examples**: Show, don't just tell
- **Professional**: Technical but accessible
- **Accurate**: Test code examples before documenting

## Release Process

1. Sprint planning (see TODO.md for priorities)
2. Feature branches for development
3. PR review and validation
4. Merge to `master` when CI passes
5. Tag releases for significant milestones

## Getting Help

- **Architecture questions**: See `docs/architecture.md`
- **Agent patterns**: Review existing agents in `agents/`
- **Command examples**: Browse `commands/` directory
- **Test examples**: Look at `tests/test_agent_integration.py`

## Recognition

Contributors are recognized through:
- Git commit co-authorship
- Pull request acknowledgments
- Agent file authorship (when applicable)

---

**Questions?** Open an issue or review existing agents for patterns.

**Found a bug?** Submit a PR with a failing test first, then the fix.

**Have an idea?** Check TODO.md for alignment with roadmap, then propose in an issue.

Thank you for contributing to professional software development! 🚀
