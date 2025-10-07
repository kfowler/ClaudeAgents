# Code Quality Review

**Command:** `/code-quality-review`
**Agents:** `code-architect`, `qa-test-engineer`, `security-audit-specialist`
**Complexity:** Medium-High
**Duration:** 4-8 hours (depending on codebase size)

## Overview

Performs comprehensive code quality review analyzing architecture, readability, maintainability, test coverage, and security to identify technical debt and improvement opportunities.

## What This Command Does

This command orchestrates a complete code quality audit across three specialized agents:

1. **Architecture & Readability** (`code-architect`)
   - Architectural patterns and anti-patterns
   - Code organization and structure
   - Readability and maintainability
   - SOLID principles adherence
   - Design patterns usage
   - Technical debt identification

2. **Test Quality** (`qa-test-engineer`)
   - Test coverage analysis
   - Test quality and effectiveness
   - Testing best practices
   - Missing test scenarios
   - Test maintainability

3. **Security Review** (`security-audit-specialist`)
   - Security vulnerabilities
   - Authentication/authorization issues
   - Input validation gaps
   - Dependency vulnerabilities
   - Security best practices

## Usage

```bash
# Review entire codebase
/code-quality-review --path=src/

# Review specific feature
/code-quality-review --path=src/features/user-auth

# Focus on specific aspects
/code-quality-review --focus=architecture,tests --path=src/

# Pre-PR review
/code-quality-review --pr=123 --severity=high
```

## Execution Workflow

### Phase 1: Codebase Analysis (60-90 min)

**code-architect** performs architectural review:

**Architecture Patterns:**
```
Architectural Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Codebase Structure:
├── src/
│   ├── components/     (142 files) - React components
│   ├── services/       (28 files)  - Business logic
│   ├── utils/          (45 files)  - Shared utilities
│   ├── hooks/          (23 files)  - Custom React hooks
│   └── types/          (67 files)  - TypeScript definitions

Lines of Code: 45,230
Files: 305
Average File Size: 148 lines
Largest File: UserDashboard.tsx (892 lines) ⚠️

Architecture Score: 72/100 (Good, needs improvement)

Patterns Identified:
✓ Feature-based organization (good separation)
✓ Custom hooks for reusable logic
✓ TypeScript for type safety
⚠️ Mixed component patterns (class + functional)
❌ No clear separation of concerns (business logic in components)
❌ Missing service layer abstraction

SOLID Principles:
- Single Responsibility: 68% adherence ⚠️
- Open/Closed: 82% adherence ✓
- Liskov Substitution: N/A (no inheritance)
- Interface Segregation: 75% adherence ✓
- Dependency Inversion: 45% adherence ❌

Critical Issues:
1. God Component: UserDashboard.tsx (892 lines, does too much)
2. Tight Coupling: Components directly call API endpoints
3. Missing Abstraction: No repository pattern for data access
4. Duplicated Logic: Auth logic duplicated across 12 components
```

### Phase 2: Readability Assessment (45-60 min)

**code-architect** evaluates code readability:

**Readability Metrics:**
```
Readability Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Readability Score: 78/100 (Good)

Naming Conventions:
✓ Consistent camelCase for variables/functions
✓ PascalCase for components/classes
✓ Descriptive names (avg length: 18 chars)
⚠️ Some abbreviations unclear (usr, mgr, cfg)
❌ Magic numbers without constants (42 instances)

Function Complexity:
- Average cyclomatic complexity: 4.2 ✓
- Functions >10 complexity: 23 (8%) ⚠️
- Longest function: processUserData (85 lines, complexity 18) ❌

Code Smells:
❌ Long Parameter Lists: 34 functions with >5 parameters
❌ Large Classes: UserService.ts (650 lines, 28 methods)
❌ Feature Envy: DataProcessor accesses User internals 47 times
❌ Duplicated Code: 156 code blocks duplicated 2+ times
⚠️ Comments: 12% of code (low, should be 15-20%)
⚠️ Dead Code: 23 unused functions detected

Readability Issues by File:

UserDashboard.tsx (Readability: 42/100) ❌
- 892 lines (should be <300)
- 18 nested levels (should be <4)
- 156 lines without comments
- Recommendation: Split into 5-7 smaller components

AuthService.ts (Readability: 65/100) ⚠️
- 340 lines (acceptable but large)
- Complex conditional logic (12 nested if statements)
- Missing JSDoc for public methods
- Recommendation: Refactor complex conditionals, add documentation

utils/helpers.ts (Readability: 52/100) ❌
- Catch-all file with 28 unrelated functions
- No clear theme or purpose
- Recommendation: Split by domain (dateHelpers, stringHelpers, etc.)
```

### Phase 3: Maintainability Review (60-90 min)

**code-architect** assesses maintainability:

**Maintainability Metrics:**
```
Maintainability Index Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Maintainability Index: 68/100 (Moderate)
(Based on: Halstead Volume, Cyclomatic Complexity, Lines of Code, Comments)

Maintainability by Module:

Components: 72/100 ✓
- Generally well-structured
- Good separation of UI and logic (hooks)
- Issue: Some components too large

Services: 58/100 ⚠️
- Business logic mixed with API calls
- No dependency injection
- Hard to unit test
- Issue: Tight coupling to implementation details

Utils: 65/100 ⚠️
- Good reuse potential
- Issue: Catch-all modules, poor organization

Hooks: 82/100 ✓
- Well-designed custom hooks
- Good abstraction
- Minor issue: Some hooks could be simplified

Types: 88/100 ✓
- Comprehensive TypeScript types
- Good type safety
- Excellent documentation via types

Technical Debt Score: 32/100 (High Debt) ❌

Debt Categories:
1. Architecture Debt: 28 issues
   - Missing service layer
   - No dependency injection
   - Tight coupling
   - Est. remediation: 3-4 weeks

2. Code Debt: 67 issues
   - God components (5 files >500 lines)
   - Duplicated code (156 blocks)
   - Complex functions (23 with complexity >10)
   - Est. remediation: 2-3 weeks

3. Test Debt: 45 issues
   - Low coverage (58%)
   - Missing integration tests
   - Brittle tests (coupled to implementation)
   - Est. remediation: 2 weeks

4. Documentation Debt: 34 issues
   - Missing JSDoc (68% of public APIs)
   - Outdated README
   - No architecture docs
   - Est. remediation: 1 week

Total Est. Remediation Effort: 8-10 weeks
Recommended: Address incrementally over 3-6 months
```

### Phase 4: Test Coverage Analysis (60-90 min)

**qa-test-engineer** analyzes test quality:

**Test Coverage Report:**
```
Test Coverage Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Coverage: 58% (Below target of 80%)

Coverage by Type:
- Line Coverage: 58% ⚠️
- Branch Coverage: 42% ❌
- Function Coverage: 65% ⚠️
- Statement Coverage: 60% ⚠️

Coverage by Module:

Components: 72% ✓
- 142 component files
- 102 have tests (72%)
- 40 untested (28%)
- Critical untested: UserDashboard, PaymentForm, AdminPanel

Services: 34% ❌
- 28 service files
- Only 10 have tests (36%)
- 18 untested (64%)
- Critical untested: UserService, PaymentService, AuthService

Utils: 68% ✓
- 45 utility files
- 31 have tests (69%)
- 14 untested (31%)
- Most critical utils are tested

Hooks: 85% ✓
- 23 custom hooks
- 20 have tests (87%)
- 3 untested (useLocalStorage, useDebounce, usePermissions)

Test Quality Assessment:

Test Organization: 75/100 ✓
- Clear naming conventions
- Good use of describe/it blocks
- Colocated tests (*.test.tsx)
- Issue: Some test files too large (>500 lines)

Test Effectiveness: 62/100 ⚠️
- Tests exist but don't catch regressions
- Many tests coupled to implementation details
- Shallow tests (only happy path)
- Missing edge case coverage

Test Maintainability: 58/100 ⚠️
- High test brittleness (32% fail on refactors)
- Duplicated test setup code
- Complex mocking (hard to understand)
- Slow tests (avg 2.3s per test)

Critical Missing Tests:

1. Integration Tests: 0 tests ❌
   - No API integration tests
   - No database integration tests
   - No end-to-end user flows
   - Recommendation: Add 20-30 integration tests

2. Edge Cases: 156 untested scenarios ❌
   - Error handling (78 catch blocks untested)
   - Boundary conditions (min/max values)
   - Null/undefined cases
   - Concurrent operations

3. Security Tests: 0 tests ❌
   - No authentication tests
   - No authorization tests
   - No input validation tests
   - Recommendation: Add security test suite

Test Recommendations:
1. Increase coverage: 58% → 80% (add 1,200 tests)
2. Add integration tests (20-30 tests)
3. Add security tests (15-20 tests)
4. Refactor brittle tests (reduce coupling)
5. Improve test performance (2.3s → <1s avg)
```

### Phase 5: Security Review (45-60 min)

**security-audit-specialist** identifies vulnerabilities:

**Security Assessment:**
```
Security Vulnerability Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Security Score: 65/100 (Moderate Risk)

Critical Vulnerabilities (3):

CRITICAL-01: SQL Injection Risk
- Location: src/services/UserService.ts:145
- Issue: String concatenation in SQL query
- Code:
  const query = `SELECT * FROM users WHERE id = ${userId}`;
- Impact: Database compromise, data breach
- Fix: Use parameterized queries
- Severity: CRITICAL
- CVE: Similar to CVE-2021-xxxxx

CRITICAL-02: Hardcoded Credentials
- Location: src/config/database.ts:12
- Issue: Database password in source code
- Code:
  const dbPassword = "prod_db_pass_2024";
- Impact: Unauthorized database access
- Fix: Use environment variables
- Severity: CRITICAL

CRITICAL-03: Missing Authentication
- Location: src/api/admin.ts:23-45
- Issue: Admin endpoints without auth check
- Impact: Unauthorized admin access
- Fix: Add authentication middleware
- Severity: CRITICAL

High Severity Issues (12):

HIGH-01: XSS Vulnerability
- Location: src/components/UserProfile.tsx:89
- Issue: Unescaped user input in dangerouslySetInnerHTML
- Impact: Cross-site scripting attack
- Fix: Sanitize user input or avoid dangerouslySetInnerHTML
- Severity: HIGH

HIGH-02: Missing CSRF Protection
- Location: src/api/routes.ts
- Issue: No CSRF tokens for state-changing operations
- Impact: Cross-site request forgery
- Fix: Implement CSRF token validation
- Severity: HIGH

HIGH-03: Weak Password Requirements
- Location: src/utils/validation.ts:56
- Issue: Min length 6 chars, no complexity requirements
- Impact: Brute force attacks
- Fix: Enforce 12+ chars, complexity rules
- Severity: HIGH

[9 more high severity issues...]

Medium Severity Issues (28):

MEDIUM-01: Sensitive Data in Logs
- Location: src/services/AuthService.ts:234
- Issue: Logging user passwords (even if failed login)
- Impact: Password exposure in log files
- Fix: Never log credentials
- Severity: MEDIUM

MEDIUM-02: No Rate Limiting
- Location: src/api/auth.ts
- Issue: Login endpoint without rate limiting
- Impact: Brute force attacks
- Fix: Add rate limiting (5 attempts / 15 min)
- Severity: MEDIUM

[26 more medium severity issues...]

Dependency Vulnerabilities (15):

DEP-VULN-01: lodash@4.17.15
- CVE: CVE-2020-8203
- Severity: HIGH
- Issue: Prototype pollution
- Fix: Upgrade to lodash@4.17.21
- Location: package.json

DEP-VULN-02: axios@0.21.1
- CVE: CVE-2021-3749
- Severity: MEDIUM
- Issue: SSRF vulnerability
- Fix: Upgrade to axios@0.27.2
- Location: package.json

[13 more dependency vulnerabilities...]

Security Best Practices Violations:

Authentication/Authorization:
❌ No JWT expiration (tokens valid forever)
❌ No refresh token rotation
❌ Passwords stored with MD5 (should use bcrypt)
❌ No multi-factor authentication
⚠️ Session timeout too long (7 days, should be 1 hour)

Input Validation:
❌ No input sanitization (23 endpoints)
❌ No content-type validation
❌ No file upload size limits
⚠️ Weak email validation regex

Data Protection:
❌ Sensitive data not encrypted at rest
❌ No HTTPS enforcement
❌ PII in application logs
⚠️ No data retention policy

Security Headers:
❌ Missing Content-Security-Policy
❌ Missing X-Frame-Options
❌ Missing X-Content-Type-Options
✓ HSTS enabled (good)

Recommendations Priority:
1. FIX CRITICAL (3 issues) - THIS WEEK
2. FIX HIGH (12 issues) - NEXT 2 WEEKS
3. FIX MEDIUM (28 issues) - NEXT MONTH
4. Upgrade vulnerable dependencies (15) - THIS WEEK
5. Implement security best practices - ONGOING
```

### Phase 6: Prioritized Action Plan (30-45 min)

**Consolidated recommendations from all agents:**

```markdown
# Code Quality Action Plan
**Generated:** 2024-10-08
**Codebase:** UserManagementApp
**Overall Quality Score:** 68/100 (Needs Improvement)

## Executive Summary

**Critical Issues:** 3 (security vulnerabilities)
**High Priority:** 27 (12 security + 15 architecture/readability)
**Medium Priority:** 78 (28 security + 50 code quality)
**Low Priority:** 45 (documentation, minor improvements)

**Estimated Remediation Effort:** 8-10 weeks (full-time)
**Recommended Approach:** 3-6 month incremental improvement plan

## Immediate Actions (This Week)

### 1. Fix Critical Security Vulnerabilities (Priority: CRITICAL)
**Effort:** 2-3 days
**Owner:** Security + Backend Team

Issues:
- CRITICAL-01: SQL Injection in UserService
- CRITICAL-02: Hardcoded credentials in database config
- CRITICAL-03: Missing authentication on admin endpoints

Actions:
```typescript
// BEFORE (SQL Injection Risk):
const query = `SELECT * FROM users WHERE id = ${userId}`;

// AFTER (Parameterized):
const query = 'SELECT * FROM users WHERE id = ?';
db.execute(query, [userId]);
```

```typescript
// BEFORE (Hardcoded):
const dbPassword = "prod_db_pass_2024";

// AFTER (Environment Variable):
const dbPassword = process.env.DB_PASSWORD;
```

```typescript
// BEFORE (No Auth):
router.delete('/admin/users/:id', deleteUser);

// AFTER (Auth Middleware):
router.delete('/admin/users/:id', authenticateAdmin, deleteUser);
```

Success Criteria:
- [ ] All 3 critical vulnerabilities patched
- [ ] Security scan shows 0 critical issues
- [ ] Penetration test passed

### 2. Upgrade Vulnerable Dependencies (Priority: HIGH)
**Effort:** 1 day
**Owner:** DevOps Team

Actions:
```bash
npm upgrade lodash@4.17.21
npm upgrade axios@0.27.2
npm upgrade express@4.18.2
# [12 more upgrades...]
npm audit fix
```

Success Criteria:
- [ ] All high/critical CVEs resolved
- [ ] No breaking changes introduced
- [ ] All tests still passing

## Short-term Improvements (Weeks 2-4)

### 3. Refactor God Components (Priority: HIGH)
**Effort:** 1 week
**Owner:** Frontend Team

Target: UserDashboard.tsx (892 lines → 5-7 components)

Current Structure:
```
UserDashboard.tsx (892 lines) ❌
├── User profile display
├── Activity feed
├── Analytics charts
├── Settings panel
├── Notification center
└── Admin controls
```

Refactored Structure:
```
UserDashboard.tsx (120 lines) ✓
├── components/
│   ├── UserProfile.tsx (80 lines)
│   ├── ActivityFeed.tsx (140 lines)
│   ├── AnalyticsCharts.tsx (200 lines)
│   ├── SettingsPanel.tsx (160 lines)
│   ├── NotificationCenter.tsx (100 lines)
│   └── AdminControls.tsx (90 lines)
```

Success Criteria:
- [ ] UserDashboard.tsx < 150 lines
- [ ] Each component has single responsibility
- [ ] Improved maintainability score (42 → 75)

### 4. Introduce Service Layer (Priority: HIGH)
**Effort:** 1-2 weeks
**Owner:** Backend Team

Current: Components → API calls (tight coupling)
```typescript
// BEFORE (in component):
const users = await fetch('/api/users').then(r => r.json());
```

Proposed: Components → Services → API (loose coupling)
```typescript
// AFTER (service layer):
// services/UserService.ts
class UserService {
  async getUsers(): Promise<User[]> {
    return this.api.get('/users');
  }
}

// In component:
const users = await userService.getUsers();
```

Benefits:
- Testable business logic (mock service, not API)
- Consistent error handling
- Caching/retry logic centralized
- API changes don't break components

Success Criteria:
- [ ] All API calls abstracted to services
- [ ] Service layer test coverage >90%
- [ ] Components test coverage improves (easier mocking)

### 5. Increase Test Coverage (Priority: HIGH)
**Effort:** 2 weeks
**Owner:** QA + Development Team

Target: 58% → 80% coverage

Focus Areas:
1. Services (34% → 85%): Add 120 unit tests
2. Integration tests (0 → 25 tests): API + Database
3. Security tests (0 → 18 tests): Auth, input validation
4. Edge cases (156 untested → 80% covered)

Test Plan:
```typescript
// Week 1: Service Layer Tests
describe('UserService', () => {
  it('should handle network errors gracefully');
  it('should retry failed requests');
  it('should validate input before API call');
  it('should transform API response correctly');
  // [35 more service tests...]
});

// Week 2: Integration + Security Tests
describe('User Authentication Flow', () => {
  it('should prevent SQL injection in login');
  it('should enforce rate limiting');
  it('should invalidate tokens after password change');
  // [20 more integration tests...]
});
```

Success Criteria:
- [ ] Overall coverage ≥80%
- [ ] Services coverage ≥85%
- [ ] 25 integration tests passing
- [ ] 18 security tests passing
- [ ] Test suite runtime <5 minutes

## Medium-term Improvements (Months 2-3)

### 6. Address Technical Debt
**Effort:** 4-6 weeks
**Owner:** Engineering Team (distributed)

Debt Reduction Plan:

Week 1-2: Code Duplication (156 blocks)
- Extract common patterns to shared utilities
- Create reusable components
- Reduce code by ~2,000 lines

Week 3-4: Complex Functions (23 functions with complexity >10)
- Refactor complex conditionals
- Extract helper functions
- Simplify control flow

Week 5-6: Documentation (68% missing JSDoc)
- Document all public APIs
- Add inline comments for complex logic
- Create architecture documentation

### 7. Improve Security Posture
**Effort:** 3 weeks
**Owner:** Security Team

Security Improvements:
1. Implement rate limiting (all endpoints)
2. Add CSRF protection
3. Strengthen password requirements
4. Add JWT expiration and refresh
5. Encrypt sensitive data at rest
6. Add security headers (CSP, X-Frame-Options)
7. Implement audit logging
8. Add penetration testing to CI/CD

## Success Metrics

Track improvement through:

### Code Quality Metrics
- **Maintainability Index:** 68 → 85 (target)
- **Technical Debt:** 32/100 → 75/100
- **Cyclomatic Complexity:** Avg 4.2 → 3.5
- **Code Duplication:** 156 blocks → <50 blocks

### Test Metrics
- **Coverage:** 58% → 80%
- **Test Quality:** 62/100 → 85/100
- **Test Performance:** 2.3s → <1s avg

### Security Metrics
- **Security Score:** 65/100 → 90/100
- **Critical Vulnerabilities:** 3 → 0
- **High Vulnerabilities:** 12 → 0
- **Dependency Vulnerabilities:** 15 → 0

### Architecture Metrics
- **SOLID Adherence:** 60% → 85%
- **God Components:** 5 → 0
- **Service Layer Coverage:** 0% → 100%

## Timeline & Milestones

**Week 1:** Critical security fixes + dependency upgrades
**Week 2-4:** Refactor god components + service layer
**Week 5-6:** Increase test coverage to 80%
**Month 2-3:** Address technical debt + security improvements
**Month 4-6:** Continuous improvement + monitoring

**Quarterly Reviews:** Track metrics, adjust priorities
**Goal:** Quality score 68 → 85 within 6 months
```

## Success Metrics

Track code quality improvements through:
- **Overall Quality Score:** Target >85/100
- **Test Coverage:** Target >80%
- **Security Score:** Target >90/100
- **Maintainability Index:** Target >80/100
- **Technical Debt Reduction:** 50% reduction in 6 months

## Common Use Cases

### Pre-Release Review
```bash
/code-quality-review --path=src/ --severity=high --report=pre-release.md
```

### PR Quality Gate
```bash
/code-quality-review --pr=456 --block-on=critical,high
```

### Legacy Code Assessment
```bash
/code-quality-review --path=legacy/ --focus=debt,security --output=assessment.pdf
```

### Continuous Monitoring
```bash
/code-quality-review --path=src/ --compare=last-month --trends
```

## Integration with Other Commands

This command works well with:
- `/security-audit` - Deep dive security assessment
- `/performance-audit` - Performance optimization
- `/refactor-component` - Execute recommended refactorings
- `/test-coverage` - Expand test coverage
- `/architecture-review` - Architectural deep dive

## Prerequisites

### Required Tools
- Static analysis tools (ESLint, TypeScript)
- Test coverage tool (Jest, NYC)
- Security scanner (npm audit, Snyk)
- Code metrics tool (SonarQube, CodeClimate)

### Codebase Access
- Source code repository access
- Test suite access
- Dependency manifest (package.json, requirements.txt)

## Limitations

- **Analysis Depth:** Static analysis only (no runtime profiling)
- **Language Support:** Best for JavaScript/TypeScript, Python, Java
- **Codebase Size:** Optimal for <100k lines (larger = longer analysis)
- **Custom Rules:** Uses standard best practices (may need customization)

## Best Practices

1. **Run Regularly:** Monthly quality reviews catch issues early
2. **Fix Incrementally:** Address highest priority issues first, avoid "big bang" refactors
3. **Track Trends:** Compare quality scores over time
4. **Automate:** Integrate quality gates into CI/CD
5. **Team Ownership:** Assign issues to teams, not individuals
6. **Celebrate Progress:** Recognize quality improvements
7. **Balance Speed:** Don't let perfect be enemy of good

---

**Pro Tip**: Run code quality reviews before major releases and after onboarding new team members. Quality reviews during onboarding help new devs understand codebase standards and identify areas for contribution.
