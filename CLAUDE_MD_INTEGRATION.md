# CLAUDE.md Integration Guide

## Purpose

This guide ensures Claude Code agents properly read, respect, and contribute to CLAUDE.md files in projects, maintaining consistency with project-specific standards and conventions.

## 🔍 Agent Behavior with CLAUDE.md

### On Project Entry

**EVERY agent MUST:**

```bash
# 1. First, check for CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    echo "📋 Project-specific instructions found"
    cat CLAUDE.md
elif [ -f ".claude/instructions.md" ]; then
    echo "📋 Project instructions in .claude directory"
    cat .claude/instructions.md
else
    echo "⚠️  No CLAUDE.md found - will follow general best practices"
fi

# 2. Check for other configuration files
for config in .clauderc claude.config.json .claude.yml; do
    [ -f "$config" ] && echo "Found config: $config"
done

# 3. Scan for project-specific patterns
find . -name "*.md" -type f | xargs grep -l "Claude\|AI\|Agent" 2>/dev/null
```

### Priority Order

Agents follow instructions in this precedence:
1. **CLAUDE.md** - Project-specific overrides (highest priority)
2. **PROFESSIONAL_STANDARDS.md** - General professional practices
3. **Agent specialty defaults** - Domain-specific best practices
4. **Universal conventions** - Industry standards (lowest priority)

## 📝 CLAUDE.md Template for Projects

```markdown
# CLAUDE.md

This file provides project-specific guidance for Claude Code agents working on this repository.

## Project Overview

[Brief description of the project, its purpose, and key technologies]

## 🚨 CRITICAL: Must Read Before Any Changes

### DO NOT MODIFY
- `src/core/legacy/` - Legacy code pending careful migration
- `config/production.yml` - Requires security team approval
- Database migrations - Must be reviewed by data team

### ALWAYS USE
- Service layer pattern in `src/services/`
- Error handling from `src/core/errors/`
- Logging via `src/utils/logger/`

## Development Workflow

### Before Coding
1. Run `make setup` to configure environment
2. Check `docs/architecture/` for system design
3. Review recent PRs for coding patterns

### Testing Requirements
- Minimum 85% coverage for new code
- All endpoints need integration tests
- Performance tests for data-heavy operations

### Code Style
\`\`\`bash
# Auto-format and lint
make format
make lint

# Type checking
make typecheck
\`\`\`

## Architecture Decisions

### Pattern: Repository Pattern
- All database access through repositories
- No direct database queries in controllers
- Use `src/repositories/base.py` as template

### Pattern: Event-Driven Updates
- State changes emit events via `EventBus`
- Subscribers handle side effects asynchronously
- See `src/events/` for examples

## Testing Strategy

### Unit Tests
\`\`\`python
# Use the project's custom test fixtures
from tests.fixtures import mock_service, test_client

def test_feature(mock_service):
    # Test implementation
    pass
\`\`\`

### Integration Tests
- Use `tests/integration/base.py` test class
- Transactions auto-rollback after each test
- See `tests/integration/examples/`

## Deployment

### Environments
- Development: Auto-deploy on merge to `develop`
- Staging: Deploy via `make deploy-staging`
- Production: Requires approval in #deployments Slack

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security scan clean
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Migration scripts tested

## Communication

### Channels
- **Slack**: #dev-team for questions
- **Issues**: Use GitHub issues for bugs/features
- **PRs**: Tag @teamlead for review

### Status Updates
Post daily progress in Slack thread:
\`\`\`
📍 Working on: [Feature]
✅ Completed: [What's done]
🔄 In Progress: [Current focus]
🚧 Blockers: [Any issues]
\`\`\`

## Common Pitfalls

### ❌ Avoid
- Direct database access outside repositories
- Synchronous external API calls (use job queue)
- Large transactions (break into smaller chunks)
- Global state mutations

### ✅ Instead Use
- Repository pattern with dependency injection
- Async job processing with Celery/Bull
- Batch processing with progress tracking
- Immutable state with event sourcing

## Resources

- [Architecture Docs](docs/architecture/)
- [API Documentation](docs/api/)
- [Runbook](docs/runbook/)
- [Security Guidelines](docs/security/)

## Team Contacts

- **Tech Lead**: @johndoe
- **DevOps**: @janedoe  
- **Security**: @security-team
- **Product**: @product-team
```

## 🤖 Agent Instructions Enhancement

### Reading CLAUDE.md

Agents should parse CLAUDE.md for specific sections:

```python
import re
from pathlib import Path

def parse_claude_md():
    """Extract actionable instructions from CLAUDE.md"""
    
    claude_md = Path("CLAUDE.md")
    if not claude_md.exists():
        return None
    
    content = claude_md.read_text()
    
    instructions = {
        "critical": extract_section(content, "CRITICAL|Must Read"),
        "do_not_modify": extract_list(content, "DO NOT MODIFY"),
        "always_use": extract_list(content, "ALWAYS USE"),
        "workflow": extract_section(content, "Development Workflow"),
        "testing": extract_section(content, "Testing Requirements"),
        "patterns": extract_patterns(content),
        "commands": extract_commands(content),
    }
    
    return instructions

def extract_commands(content):
    """Extract all make/npm/script commands"""
    commands = re.findall(r'(?:make|npm run|yarn|pnpm|cargo|go) (\S+)', content)
    return list(set(commands))
```

### Contributing to CLAUDE.md

When agents discover new patterns or requirements:

```markdown
## Suggested Addition to CLAUDE.md

### Pattern Discovered: [Name]
**Context**: Found this pattern used consistently in 5+ files
**Location**: `src/services/*.py`
**Description**: All services inherit from BaseService and implement standard interface

### Suggested Documentation:
\`\`\`markdown
### Pattern: Service Interface
All services must:
1. Inherit from `BaseService`
2. Implement `validate()`, `execute()`, and `rollback()` methods
3. Use dependency injection for repositories
\`\`\`

Should this be added to CLAUDE.md? @teamlead
```

## 🔄 Synchronization Protocol

### When CLAUDE.md Conflicts with Code

```python
def resolve_conflicts():
    """
    Priority resolution when CLAUDE.md conflicts with actual code:
    
    1. Recent code changes (last 7 days) likely supersede CLAUDE.md
    2. Check git history for CLAUDE.md updates
    3. Ask for clarification rather than assume
    """
    
    # Check last modified dates
    claude_modified = get_file_modified_date("CLAUDE.md")
    code_modified = get_most_recent_code_change()
    
    if code_modified > claude_modified:
        return "Follow code patterns, suggest CLAUDE.md update"
    else:
        return "Follow CLAUDE.md, code may need updating"
```

### Updating CLAUDE.md

```bash
# Create a PR specifically for CLAUDE.md updates
git checkout -b docs/update-claude-md
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with new patterns

- Added new testing requirements
- Updated deployment process
- Documented error handling patterns"

gh pr create --title "docs: update CLAUDE.md" --body "
## Changes to CLAUDE.md

### Added
- New testing requirements discovered in recent PRs
- Deployment process updates from DevOps team

### Updated  
- Error handling patterns to match current implementation

### Removed
- Deprecated jQuery patterns no longer used

Please review for accuracy @teamlead @devops"
```

## 📊 CLAUDE.md Analytics

Agents should track compliance with CLAUDE.md instructions:

```python
def audit_claude_compliance():
    """Check if codebase follows CLAUDE.md guidelines"""
    
    report = {
        "compliance_score": 0,
        "violations": [],
        "suggestions": []
    }
    
    # Check for forbidden modifications
    do_not_modify = parse_claude_md()["do_not_modify"]
    for path in do_not_modify:
        if has_recent_changes(path):
            report["violations"].append(f"Modified forbidden path: {path}")
    
    # Check for required patterns
    always_use = parse_claude_md()["always_use"]
    for pattern in always_use:
        usage_count = count_pattern_usage(pattern)
        if usage_count < expected_usage(pattern):
            report["suggestions"].append(f"Underused pattern: {pattern}")
    
    # Calculate compliance score
    report["compliance_score"] = calculate_score(report)
    
    return report
```

## 🎯 Best Practices for CLAUDE.md

### For Project Maintainers

**DO:**
- Keep CLAUDE.md updated with significant changes
- Include specific examples and anti-patterns
- Reference actual files and functions
- Provide clear commands and scripts
- Update when architecture changes

**DON'T:**
- Make it too long (>500 lines is too much)
- Duplicate general best practices
- Include outdated information
- Use vague instructions
- Forget to version control it

### For Agents

**DO:**
- Read CLAUDE.md before ANY work
- Follow project-specific overrides
- Suggest updates when patterns change
- Ask for clarification when uncertain
- Document deviations with reasoning

**DON'T:**
- Ignore CLAUDE.md instructions
- Apply general patterns that conflict
- Modify forbidden files/areas
- Skip project-specific setup steps
- Assume CLAUDE.md is outdated

## 🔗 Integration with CI/CD

### Automated CLAUDE.md Validation

```yaml
# .github/workflows/claude-md-check.yml
name: CLAUDE.md Compliance Check

on: [pull_request]

jobs:
  check-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check CLAUDE.md exists
        run: |
          if [ ! -f "CLAUDE.md" ]; then
            echo "⚠️ No CLAUDE.md found"
            exit 0
          fi
      
      - name: Validate CLAUDE.md format
        run: |
          python scripts/validate_claude_md.py
      
      - name: Check compliance with rules
        run: |
          python scripts/check_claude_compliance.py
      
      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '⚠️ CLAUDE.md compliance check failed. Please review agent instructions.'
            })
```

## 📚 Learning from CLAUDE.md

Agents should extract and learn patterns:

```python
def learn_from_claude_md():
    """Extract patterns and conventions from CLAUDE.md"""
    
    patterns = {
        "naming_conventions": extract_naming_patterns(),
        "file_structure": extract_structure_patterns(),
        "testing_approach": extract_testing_patterns(),
        "error_handling": extract_error_patterns(),
        "logging_style": extract_logging_patterns()
    }
    
    # Generate agent-specific guidelines
    agent_guidelines = adapt_patterns_to_agent_specialty(patterns)
    
    return agent_guidelines
```

## 🚀 Quick Start for New Projects

### Creating CLAUDE.md for Your Project

```bash
# Generate initial CLAUDE.md
cat > CLAUDE.md << 'EOF'
# CLAUDE.md

## Project Overview
[Your project description]

## Critical Instructions
- DO NOT modify: [protected files]
- ALWAYS use: [required patterns]

## Development Workflow
1. [Step 1]
2. [Step 2]

## Testing Requirements
- Coverage: X%
- Test command: `[command]`

## Code Style
- Format: `[command]`
- Lint: `[command]`

EOF

# Add to git
git add CLAUDE.md
git commit -m "Add CLAUDE.md for AI agent guidance"
```

---

**Remember**: CLAUDE.md is the contract between the project and AI agents. It should be treated as executable documentation that directly influences agent behavior. Keep it current, clear, and actionable.