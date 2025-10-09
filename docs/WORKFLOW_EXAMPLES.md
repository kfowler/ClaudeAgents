# Workflow Examples

Real-world examples of using ClaudeAgents workflows to solve common software development challenges.

## Table of Contents

- [Building a SaaS MVP](#building-a-saas-mvp)
- [API Design & Development](#api-design--development)
- [Testing Strategy](#testing-strategy)
- [Performance Optimization](#performance-optimization)
- [Security Audit](#security-audit)
- [Database Optimization](#database-optimization)

---

## Building a SaaS MVP

**Scenario**: Building a new SaaS product from scratch with authentication, subscription billing, and admin dashboard.

**Workflow**: `/workflows:saas-mvp`

**Duration**: 8-12 hours

**Process**:
1. Product strategy and market validation
2. Technical architecture design
3. Database schema design
4. API endpoint implementation
5. Frontend components and pages
6. Authentication and authorization
7. Payment integration
8. Admin dashboard
9. Testing and deployment

**Example Output**:
```bash
# Run the workflow
/workflows:saas-mvp

# The orchestrator will coordinate:
- product-strategist: Market validation
- full-stack-architect: Architecture design
- data-engineer: Database schema
- backend-api-engineer: API implementation
- security-audit-specialist: Security review
- qa-test-engineer: Testing strategy
```

**Results**:
- Complete technical architecture document
- Database schema with migrations
- RESTful API with authentication
- React frontend with routing
- Stripe payment integration
- Comprehensive test suite
- Deployment configuration

---

## API Design & Development

**Scenario**: Designing and implementing a RESTful API for a mobile app backend.

**Workflow**: `/development:api-design`

**Duration**: 4-6 hours

**Process**:
1. Requirements analysis
2. OpenAPI specification
3. Database schema design
4. API implementation
5. Authentication setup
6. Documentation generation
7. Testing

**Example**:
```bash
/development:api-design

# Options:
/development:api-design --type=rest
/development:api-design --type=graphql
/development:api-design --auth=jwt
```

**Deliverables**:
- OpenAPI 3.0 specification
- Database schema and migrations
- Implemented API endpoints
- Authentication middleware
- Auto-generated API documentation
- Integration tests
- Postman/Insomnia collection

---

## Testing Strategy

**Scenario**: Establishing comprehensive testing for an existing application.

**Workflow**: `/quality:testing-strategy`

**Duration**: 4-8 hours

**Options**:
```bash
# Web application testing
/quality:testing-strategy --domain=web

# API testing
/quality:testing-strategy --domain=api

# Mobile app testing
/quality:testing-strategy --domain=mobile

# E2E testing
/quality:testing-strategy --domain=e2e

# Specific test types
/quality:testing-strategy --types=unit,integration,e2e
```

**Deliverables**:
- Test strategy document
- Unit test setup (Jest/Pytest/etc)
- Integration test framework
- E2E test suite (Playwright/Cypress)
- CI/CD integration
- Coverage reporting
- Mock/fixture setup

---

## Performance Optimization

**Scenario**: Application is slow, need to identify and fix performance bottlenecks.

**Workflow**: `/quality:performance-optimization`

**Duration**: 6-10 hours

**Phases**:
```bash
# Full optimization
/quality:performance-optimization

# Just audit (no fixes)
/quality:performance-optimization --phase=audit

# Specific layers
/quality:performance-optimization --layers=frontend,database
```

**Process**:
1. Performance audit (profiling, metrics)
2. Bottleneck identification
3. Database query optimization
4. Frontend optimization (bundle size, rendering)
5. Backend optimization (caching, async)
6. Infrastructure optimization (CDN, edge)
7. Validation and benchmarking

**Results**:
- Performance audit report
- Optimized database queries
- Reduced bundle size (40-60%)
- Improved Core Web Vitals
- Caching strategy implementation
- Before/after benchmarks
- Monitoring dashboard

---

## Security Audit

**Scenario**: Preparing for SOC 2 compliance audit.

**Workflow**: `/quality:compliance-audit-soc2`

**Duration**: 12-16 hours

**Process**:
1. Security posture assessment
2. Vulnerability scanning
3. Access control review
4. Data protection analysis
5. Incident response planning
6. Documentation preparation
7. Remediation implementation

**Deliverables**:
- Security audit report
- Vulnerability remediation plan
- Access control policies
- Encryption implementation
- Incident response playbook
- Compliance documentation
- SOC 2 readiness assessment

---

## Database Optimization

**Scenario**: Database queries are slow, need to optimize performance.

**Workflow**: `/development:database-optimization`

**Duration**: 6-8 hours

**Process**:
1. Query performance analysis
2. Index optimization
3. Schema refinement
4. Query rewriting
5. Caching strategy
6. Connection pooling
7. Monitoring setup

**Example**:
```bash
# Full optimization
/development:database-optimization

# Just performance
/development:database-optimization --focus=performance

# Security hardening
/development:database-optimization --focus=security
```

**Results**:
- Query performance report
- Optimized indexes
- Rewritten slow queries
- Caching implementation
- Connection pool configuration
- Monitoring dashboards
- 70-90% query speedup

---

## Common Workflow Combinations

### New Product Launch
```bash
/workflows:saas-mvp
/quality:testing-strategy --domain=web
/quality:performance-optimization
/quality:compliance-audit-soc2
```

### API Modernization
```bash
/development:api-design --type=rest
/quality:testing-strategy --domain=api
/development:database-optimization
/quality:performance-optimization --layers=backend,database
```

### Production Readiness
```bash
/quality:production-readiness
/operations:monitoring-stack-setup
/operations:incident-response-workflow
/operations:disaster-recovery-plan
```

---

## Tips for Success

1. **Start with strategy**: Use `/workflows:debate` to validate approach
2. **Iterate incrementally**: Run workflows in phases, review outputs
3. **Combine workflows**: Chain multiple workflows for complex projects
4. **Review agent output**: Agents provide detailed explanations - read them!
5. **Customize with options**: Most workflows support --option flags
6. **Save outputs**: Export deliverables to your repository
7. **Follow up**: Use follow-up prompts to refine outputs

---

## Getting Help

- **Full workflow catalog**: See [COMMAND_CATALOG.md](COMMAND_CATALOG.md)
- **Quick start guide**: See [QUICKSTART.md](QUICKSTART.md)
- **Agent reference**: See [README.md](../README.md)
- **Report issues**: [GitHub Issues](https://github.com/anthropics/claude-code/issues)

---

Last updated: 2025-10-08
