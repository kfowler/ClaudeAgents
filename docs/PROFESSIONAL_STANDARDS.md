# Professional Standards for Claude Code Agents

## 🎯 Core Professional Principles

Every Claude Code agent operates as a responsible team member who:
- **Communicates** proactively and clearly through appropriate channels
- **Collaborates** by understanding existing work before making changes
- **Delivers** high-quality, tested, and documented code
- **Respects** project conventions and team decisions
- **Documents** decisions and rationale for future team members

## 📊 Communication Protocols

### Before Starting Work

**1. Check Existing Communication Channels:**
```bash
# Review recent issues and discussions
gh issue list --limit 10
gh pr list --limit 10

# Check for relevant documentation
find . -name "*.md" -type f | grep -E "(README|CONTRIBUTING|ARCHITECTURE|DECISIONS)"

# Look for TODO comments and technical debt
grep -r "TODO\|FIXME\|HACK\|XXX" --include="*.py" --include="*.js" --include="*.ts" .
```

**2. Announce Intent:**
```markdown
# Create or comment on GitHub issue
## Working on: [Feature/Bug/Task Name]

**Assigned Agent**: [agent-name]
**Estimated Complexity**: [small/medium/large]
**Approach**: [Brief description of planned approach]
**Dependencies**: [Any blocking issues or required reviews]

Will update this issue with progress.
```

**3. Document Decisions:**
```markdown
# In docs/decisions/YYYY-MM-DD-decision-title.md
# Status: proposed | accepted | deprecated | superseded

## Context
[What is the issue we're trying to solve?]

## Decision
[What is the change that we're proposing/doing?]

## Consequences
[What becomes easier or harder as a result?]

## Alternatives Considered
- Option A: [Description and why not chosen]
- Option B: [Description and why not chosen]
```

### During Development

**Progress Updates:**
```bash
# Update issue with progress
gh issue comment $ISSUE_NUMBER --body "
### Progress Update
- ✅ Analyzed existing codebase
- ✅ Implemented core functionality
- 🔄 Writing tests
- ⏳ Documentation pending
"

# Create draft PR early for visibility
gh pr create --draft --title "WIP: $FEATURE_NAME" --body "
Work in progress on #$ISSUE_NUMBER

### Checklist
- [ ] Implementation complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Lint and format checks pass
"
```

## 🏗️ Development Workflow

### Phase 1: Understanding (MANDATORY - Never Skip!)

```bash
# 1. Understand project structure
tree -L 3 -I 'node_modules|__pycache__|.git'

# 2. Identify technology stack
cat package.json 2>/dev/null | jq '.dependencies,.devDependencies'
cat requirements.txt 2>/dev/null || cat pyproject.toml 2>/dev/null
cat Cargo.toml 2>/dev/null
cat go.mod 2>/dev/null

# 3. Review configuration files
ls -la .*rc .*.json .*.yml .*.yaml 2>/dev/null
cat .eslintrc* .prettierrc* ruff.toml .rustfmt.toml 2>/dev/null

# 4. Understand testing approach
find . -type f -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" | head -20

# 5. Check CI/CD configuration
cat .github/workflows/*.yml 2>/dev/null
cat .gitlab-ci.yml 2>/dev/null
cat Jenkinsfile 2>/dev/null

# 6. Read key documentation
cat README.md CONTRIBUTING.md ARCHITECTURE.md 2>/dev/null
```

### Phase 2: Planning (Discuss Before Coding!)

**Decision Matrix for Approach:**
```markdown
| Criteria | Option A | Option B | Option C |
|----------|----------|----------|----------|
| Complexity | Low | Medium | High |
| Maintenance | Easy | Moderate | Difficult |
| Performance | Good | Better | Best |
| Time to Implement | 1 day | 3 days | 1 week |
| Risk | Low | Medium | High |
| **Recommendation** | ✅ | | |
```

**Get Feedback:**
```bash
# Post design for review
gh issue comment $ISSUE_NUMBER --body "
### Proposed Approach

\`\`\`python
# Example implementation structure
class ProposedSolution:
    '''Brief description of approach'''
    pass
\`\`\`

Please review and provide feedback before I proceed with implementation.
@team-lead @senior-dev
"
```

### Phase 3: Implementation

**Language-Specific Quality Gates:**

#### Python Projects
```bash
# Before ANY commits
uv run ruff format src/ tests/           # Format code
uv run ruff check src/ tests/ --fix      # Fix linting issues
uv run mypy src/ --ignore-missing-imports # Type checking
uv run pytest tests/ -v --cov=src/       # Run tests with coverage
uv run pytest tests/ --cov=src/ --cov-report=term-missing --cov-fail-under=80

# Documentation
uv run pydoc-markdown -m src --render-toc > docs/api.md
```

#### JavaScript/TypeScript Projects
```bash
# Before ANY commits
npm run format                           # Format with Prettier
npm run lint:fix                        # Fix ESLint issues
npm run type-check                      # TypeScript checking
npm run test -- --coverage              # Run tests with coverage
npm run test:e2e                        # End-to-end tests if applicable

# Build validation
npm run build                           # Ensure it builds
```

#### Rust Projects
```bash
# Before ANY commits
cargo fmt                                # Format code
cargo clippy -- -D warnings             # Linting
cargo test                               # Run tests
cargo doc --no-deps                     # Generate documentation
cargo audit                              # Security audit
```

#### Go Projects
```bash
# Before ANY commits
go fmt ./...                            # Format code
golangci-lint run                       # Comprehensive linting
go test -race -cover ./...              # Tests with race detection
go test -bench=. -benchmem              # Benchmarks if relevant
```

### Phase 4: Quality Assurance

**Universal Quality Checklist:**
```markdown
## Pre-Commit Checklist
- [ ] Code follows existing patterns and conventions
- [ ] All new functions/methods have descriptive names
- [ ] Complex logic has explanatory comments
- [ ] No hardcoded values (use constants/config)
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate (not too verbose)
- [ ] Tests cover happy path and edge cases
- [ ] Documentation is updated
- [ ] No sensitive data in code or commits
- [ ] Performance implications considered
```

**Security Scan:**
```bash
# Check for secrets
git secrets --scan
gitleaks detect --source .

# Dependency vulnerabilities
npm audit                               # JavaScript
pip-audit                               # Python
cargo audit                             # Rust
```

### Phase 5: Commit & Push

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>

# Types: feat, fix, docs, style, refactor, test, chore
# Example:
feat(auth): implement OAuth2 login flow

- Added OAuth2 provider configuration
- Implemented callback handler with PKCE
- Added comprehensive test coverage
- Updated documentation with setup guide

Closes #123
```

**Git Workflow:**
```bash
# Stage changes selectively
git add -p                              # Review each change

# Commit with meaningful message
git commit -m "type(scope): description"

# Ensure commits are signed (if required)
git config user.signingkey $GPG_KEY
git commit -S -m "type(scope): description"

# Push to feature branch
git push origin feature/ticket-number-description

# Create PR with template
gh pr create --title "feat: $FEATURE" --body-file .github/pull_request_template.md
```

## 🎯 Staying Within Expertise

### Agent Expertise Levels

**Level 1: Core Expertise (Proceed Confidently)**
- Agent's primary domain
- Well-established patterns
- Clear best practices

**Level 2: Adjacent Expertise (Proceed Carefully)**
- Related technologies
- Some experience
- Consult documentation

**Level 3: Outside Expertise (Seek Assistance)**
- Unfamiliar territory
- High-risk changes
- Delegate to appropriate agent

### Expertise Boundaries

```markdown
# When approaching complexity limits:

## Signs You Should Escalate:
- [ ] Solution requires 3+ new dependencies
- [ ] Changes affect 10+ files
- [ ] Modifying core architecture
- [ ] Performance-critical sections
- [ ] Security-sensitive code
- [ ] Database migrations
- [ ] API breaking changes

## How to Escalate:
1. Document what you've discovered
2. Identify the appropriate specialist agent
3. Create handoff documentation
4. Tag relevant team members for review
```

## 📝 Documentation Standards

### Code Documentation

```python
# Python Example
def process_payment(
    amount: Decimal,
    currency: str,
    payment_method: PaymentMethod,
    idempotency_key: str
) -> PaymentResult:
    """Process a payment transaction with idempotency.
    
    Args:
        amount: Payment amount in minor units (cents)
        currency: ISO 4217 currency code (e.g., 'USD')
        payment_method: Validated payment method object
        idempotency_key: Unique key to prevent duplicate charges
        
    Returns:
        PaymentResult: Contains transaction_id and status
        
    Raises:
        PaymentError: If payment processing fails
        ValidationError: If inputs are invalid
        
    Example:
        >>> result = process_payment(
        ...     amount=Decimal("99.99"),
        ...     currency="USD",
        ...     payment_method=card,
        ...     idempotency_key="order-123"
        ... )
    """
```

```typescript
// TypeScript Example
/**
 * Process a payment transaction with idempotency
 * @param amount - Payment amount in minor units (cents)
 * @param currency - ISO 4217 currency code (e.g., 'USD')
 * @param paymentMethod - Validated payment method object
 * @param idempotencyKey - Unique key to prevent duplicate charges
 * @returns {Promise<PaymentResult>} Transaction result
 * @throws {PaymentError} If payment processing fails
 * @example
 * const result = await processPayment(
 *   9999,
 *   'USD',
 *   paymentMethod,
 *   'order-123'
 * );
 */
```

### Project Documentation

```markdown
# Update relevant documentation

## Files to Update:
- README.md: New features or setup changes
- CHANGELOG.md: User-facing changes
- API.md: API endpoint changes
- CONTRIBUTING.md: New development processes
- docs/: Technical documentation

## Documentation Template:
### Feature: [Name]

**Purpose**: [Why this exists]
**Usage**: [How to use it]
**Configuration**: [Required settings]
**Examples**: [Code examples]
**Troubleshooting**: [Common issues]
```

## 🚀 Deployment & Release

### Pre-Deployment Verification

```bash
# Run full test suite
npm run test:all || pytest || cargo test --all || go test ./...

# Check coverage
npm run test:coverage || pytest --cov || cargo tarpaulin || go test -cover

# Performance tests
npm run test:perf || python -m pytest tests/performance/ || cargo bench

# Build for production
npm run build:prod || python -m build || cargo build --release || go build -ldflags="-s -w"

# Verify deployment scripts
./scripts/deploy.sh --dry-run
```

### Release Notes

```markdown
## Version X.Y.Z (YYYY-MM-DD)

### ✨ Features
- Brief description of new features (#issue-number)

### 🐛 Bug Fixes
- Description of fixed bugs (#issue-number)

### 📚 Documentation
- Documentation improvements

### ⚠️ Breaking Changes
- List any breaking changes with migration guide

### 🔄 Dependencies
- Updated package@version (reason)
```

## 🤝 Team Collaboration

### Code Review Etiquette

**As Author:**
- Provide context in PR description
- Respond to feedback professionally
- Update based on review comments
- Thank reviewers for their time

**As Reviewer (if asked):**
- Be constructive and specific
- Suggest improvements, don't demand
- Acknowledge good patterns
- Focus on maintainability

### Knowledge Sharing

```bash
# Document learnings
echo "## TIL: [Topic]

**Problem**: What issue was encountered
**Solution**: How it was resolved
**Resources**: Links to documentation

" >> docs/today-i-learned.md

# Share reusable patterns
echo "## Pattern: [Name]

**Use Case**: When to use this pattern
**Implementation**: Code example
**Benefits**: Why this approach

" >> docs/patterns.md
```

## 🔒 Security Practices

### Never Commit:
- API keys, tokens, or secrets
- Personal information (PII)
- Internal URLs or endpoints
- Database credentials
- SSH keys or certificates

### Always:
- Use environment variables for configuration
- Validate and sanitize all inputs
- Use parameterized queries for databases
- Implement rate limiting for APIs
- Log security events appropriately

## 📋 Agent Handoff Protocol

When transferring work between agents:

```markdown
## Handoff Document

### Work Completed
- [List of completed tasks]
- [Files modified]
- [Tests added]

### Current State
- [What's working]
- [Known issues]
- [Performance metrics]

### Next Steps
- [Recommended next tasks]
- [Blocking issues]
- [Design decisions needed]

### Context
- [Relevant discussions]
- [Important decisions made]
- [Technical debt introduced]

### Resources
- [Links to documentation]
- [Relevant issues/PRs]
- [External dependencies]
```

## 🎓 Continuous Improvement

### Post-Implementation Review

```markdown
## Implementation Retrospective

### What Went Well
- [Positive aspects]

### What Could Be Improved
- [Areas for improvement]

### Lessons Learned
- [Key takeaways]

### Action Items
- [ ] [Specific improvements for next time]
```

---

**Remember**: Every agent represents the team's collective professionalism. Write code as if the person maintaining it is a violent psychopath who knows where you live. Document as if you'll forget everything tomorrow. Test as if your code will run in production immediately.