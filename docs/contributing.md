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

### Developer Tools

ClaudeAgents provides interactive generators to streamline contribution:

**Agent Generator** (`tools/create_agent.py`):
- Interactive prompts for all metadata
- Smart model/complexity recommendations
- Built-in validation
- Automatic template population

**Command Generator** (`tools/create_command.py`):
- Category-based organization
- Multi-phase workflow builder
- Agent reference validation
- Automatic flow diagrams

These tools reduce errors, ensure consistency, and make contributing easier.

## Adding a New Agent

### Quick Start (Recommended)

Use the interactive agent generator:
```bash
python3 tools/create_agent.py
```

This tool will guide you through:
- Validating the agent name
- Writing a proper description (50-500 chars)
- Selecting model tier and complexity with smart recommendations
- Generating a complete agent file from template
- Running validation automatically

### Manual Method (Advanced)

If you prefer manual creation:

#### Step 1: Create Agent File

Copy the template:
```bash
cp agents/AGENT_TEMPLATE.md agents/your-agent-name.md
```

#### Step 2: Fill in Required Fields

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

### Quick Start (Recommended)

Use the interactive command generator:
```bash
python3 tools/create_command.py
```

This tool will guide you through:
- Selecting the appropriate category
- Validating the command name
- Writing a clear description
- Defining workflow phases and agent orchestration
- Validating agent references
- Generating execution flow diagrams
- Creating the command file automatically

### Manual Method (Advanced)

If you prefer manual creation:

#### Step 1: Choose Directory

Commands are organized by purpose:
- `commands/development/`: Code-related workflows
- `commands/quality/`: Testing, security, performance
- `commands/deployment/`: Infrastructure, deployment
- `commands/specialized/`: Language/framework-specific
- `commands/workflows/`: Multi-agent orchestration

#### Step 2: Create Command File

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

## Agent Deprecation and Death Certificates

### When to Deprecate an Agent

Deprecate an agent when:
- **Poor Adoption**: Agent has minimal real-world usage after reasonable trial period
- **Scope Creep**: Agent boundaries became unclear, causing confusion with other agents
- **Superseded**: A better agent or approach has replaced this agent's functionality
- **Technical Debt**: Maintaining the agent creates more problems than value

### Deprecation Process

**IMPORTANT**: Never deprecate an agent without creating a death certificate first.

#### Step 1: Create Death Certificate

Use the death certificate template:
```bash
cp tools/death_certificates/TEMPLATE.md tools/death_certificates/your-agent-name.md
```

Fill in all required sections:
- **Agent Name**: The agent being deprecated
- **Date of Creation**: When agent was first introduced
- **Date of Death**: Today's date
- **Lifespan**: Days between creation and deprecation
- **Cause of Death**: Primary reason (Poor Adoption, Scope Creep, Superseded, Technical Debt)
- **Detailed Autopsy**: Honest analysis of what went wrong
- **Lessons Learned**: Key insights for future agent development
- **Migration Path**: How users should transition away from this agent
- **Final Commit**: Last commit hash where agent was active

See [Death Certificate Template](../tools/death_certificates/TEMPLATE.md) for detailed guidance.

#### Step 2: The-Critic Review

Submit death certificate for review by `the-critic`:
- Ensures honest, thorough analysis
- Validates migration path is clear
- Confirms lessons learned are actionable
- Verifies no critical functionality is lost

#### Step 3: Execute Deprecation

Use the deprecation helper script:
```bash
./tools/deprecate_agent.sh your-agent-name
```

This script will:
- Verify death certificate exists
- Move agent to `agents/deprecated/`
- Guide you through documentation updates
- Create properly formatted commit

#### Step 4: Update Documentation

After running the script:
1. Remove agent from `CLAUDE.md` agent list
2. Add agent to death certificates gallery (`tools/death_certificates/README.md`)
3. Update any commands that referenced the deprecated agent
4. Commit with reference to death certificate:
   ```
   Deprecate your-agent-name (see death certificate)

   Agent has been deprecated due to [reason].
   See tools/death_certificates/your-agent-name.md for full analysis.

   Migration path: [brief description]
   ```

### Viewing Death Certificates

Browse the [Death Certificates Gallery](../tools/death_certificates/README.md) to:
- See statistics on agent deprecation patterns
- Learn from past mistakes
- Browse by cause of death
- Review top lessons learned

The gallery includes auto-generated statistics showing:
- Total agents vs deprecated agents
- Agent survival rate
- Average lifespan
- Most common causes of death
- Key insights from each deprecation

### Quality Gates

The validation system checks:
- Deprecated agents must have death certificates
- Death certificates must have all required sections
- Migration paths must reference valid agents
- Warnings for agents with low usage (potential future deprecation)

Run validation to check your deprecation:
```bash
python3 tools/validate_agents.py
```

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
