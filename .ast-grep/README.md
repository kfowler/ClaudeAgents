# ast-grep Configuration for StartupStack

AST-based code search, lint, and rewrite tool for SvelteKit + TypeScript codebases.

## Quick Start

```bash
# Scan entire codebase with all rules
ast-grep scan

# Scan specific paths
ast-grep scan src/ agents/

# Run specific rule
ast-grep scan --rule security-no-hardcoded-secrets

# Interactive mode (confirm each fix)
ast-grep scan -i

# Apply all fixes automatically
ast-grep scan -U
```

## Available Rules

### Svelte Patterns (`svelte-patterns.yml`)
- `svelte-store-writable` - Find writable stores
- `svelte-store-readable` - Find readable stores
- `svelte-store-derived` - Find derived stores
- `svelte-onmount` - Find onMount lifecycle hooks
- `svelte-ondestroy` - Find onDestroy lifecycle hooks
- `svelte-component-import` - Find Svelte component imports
- `svelte-each-missing-key` - Warn about missing keys in each blocks
- `svelte-transition` - Find transition directives
- `svelte-event-handler` - Find event handlers
- `svelte-bind` - Find two-way bindings
- `svelte-setcontext` / `svelte-getcontext` - Find context API usage

### API Routes (`api-routes.yml`)
- `sveltekit-get-handler` - Find GET route handlers
- `sveltekit-post-handler` - Find POST route handlers
- `sveltekit-put-handler` - Find PUT route handlers
- `sveltekit-delete-handler` - Find DELETE route handlers
- `sveltekit-form-actions` - Find form actions
- `sveltekit-page-load` - Find page load functions
- `sveltekit-handle-hook` - Find handle hooks
- `sveltekit-json-response` - Find JSON responses
- `sveltekit-redirect` - Find redirect calls
- `sveltekit-cookies-get` / `sveltekit-cookies-set` - Find cookie operations
- `sveltekit-locals-access` - Find event.locals usage

### Security (`security.yml`)
- `security-no-hardcoded-secrets` - Catch hardcoded API keys/passwords (ERROR)
- `security-no-hardcoded-db-connection` - Catch hardcoded DB credentials (ERROR)
- `security-sql-injection-risk` - Catch potential SQL injection (ERROR)
- `security-no-eval` - Warn about eval() usage (ERROR)
- `security-weak-crypto` - Warn about weak crypto (WARNING)
- `security-jwt-weak-secret` - Catch weak JWT secrets (ERROR)
- `security-api-key-in-client` - Catch API keys in client code (ERROR)
- `security-insecure-cookie` - Warn about insecure cookies (WARNING)
- `security-xss-risk` - Warn about XSS risks (WARNING)
- `security-open-redirect` - Catch open redirect vulnerabilities (WARNING)
- `security-stripe-secret-client` - Catch Stripe secret keys in client code (ERROR)
- `security-path-traversal` - Catch path traversal risks (ERROR)

## Common Use Cases

### Find all OAuth implementations
```bash
ast-grep --pattern 'OAuth($$$)' --lang typescript
```

### Find all Stripe API calls
```bash
ast-grep --pattern 'stripe.$METHOD($$$)' --lang typescript
```

### Find all Drizzle ORM queries
```bash
ast-grep --pattern 'db.$TABLE.$METHOD($$$)' --lang typescript
```

### Find all form actions
```bash
ast-grep scan --rule sveltekit-form-actions
```

### Security audit
```bash
ast-grep scan --filter 'security-.*'
```

### Refactor var to const
```bash
ast-grep --pattern 'var $X = $Y' --rewrite 'const $X = $Y' --lang typescript -U
```

## Meta Variables

- `$VAR` - Matches a single AST node (variable, expression, etc.)
- `$$$` - Matches zero or more nodes (arguments, statements, etc.)
- `$_` - Non-capturing match (like regex non-capturing groups)

## Rule Severity

- **error** - Blocks CI/CD (security issues, hardcoded secrets)
- **warning** - Should fix (potential issues, bad practices)
- **info** - Informational (code patterns, statistics)

## CI/CD Integration

Add to your CI pipeline:

```bash
# Fail build on errors
ast-grep scan --error

# Generate GitHub annotations
ast-grep scan --format github

# JSON output for parsing
ast-grep scan --json=compact
```

## Testing Rules

```bash
# Test all rules
ast-grep test

# Test specific rule file
ast-grep test .ast-grep/rules/security.yml
```

## Configuration

Main config: `.ast-grep/sgconfig.yml`

- Defines rule directories
- Sets language file mappings
- Configures ignore patterns
- Sets output style

## Adding New Rules

1. Create a new `.yml` file in `.ast-grep/rules/`
2. Follow the structure:

```yaml
rules:
  - id: my-rule-id
    message: Description of what this rule finds
    language: typescript
    severity: warning
    rule:
      pattern: $PATTERN_HERE
    note: |
      Additional context and fix suggestions.
```

3. Test your rule:
```bash
ast-grep scan --rule my-rule-id
```

## Documentation

- Official docs: https://ast-grep.github.io
- Pattern syntax: https://ast-grep.github.io/guide/pattern-syntax.html
- Rule writing: https://ast-grep.github.io/guide/rule-config.html
- Playground: https://ast-grep.github.io/playground.html

## StartupStack Philosophy

ast-grep aligns with StartupStack's velocity-first approach:

- **Fast** - Scans thousands of files in seconds
- **Accurate** - AST-based = no false positives
- **Pragmatic** - Catches real issues, not nitpicks
- **Actionable** - Clear fixes, not vague warnings

Use it to:
- Ship secure code faster
- Refactor with confidence
- Find patterns across the codebase
- Enforce team conventions
