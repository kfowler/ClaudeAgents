---
name: api-design
description: "Complete API design workflow coordinating full-stack-architect and data-engineer for REST/GraphQL API development with OpenAPI specs, versioning, and database schema design"
agents:
  - full-stack-architect
  - data-engineer
complexity: medium-high
duration: 4-6 hours
---

# API Design Workflow

**Command:** `/api-design`
**Agents:** `full-stack-architect`, `data-engineer`
**Complexity:** Medium-High
**Duration:** 4-6 hours

## Overview

Comprehensive API design workflow that coordinates backend architecture and database design to create production-ready REST or GraphQL APIs with proper documentation, versioning, authentication, and performance optimization.

## What This Command Does

This command orchestrates complete API development across 6 phases:

### Phase 1: Requirements & API Strategy (30-45 min)
**Lead:** `full-stack-architect`

- Analyze API requirements and use cases
- Choose API paradigm (REST vs GraphQL vs both)
- Define authentication/authorization strategy (JWT, OAuth2, API keys)
- Plan API versioning strategy (URL, header, content negotiation)
- Determine rate limiting and throttling requirements
- Plan pagination and filtering strategies
- Define API contract and client expectations
- Establish SLAs and performance targets

**Deliverables:**
- API requirements document with use cases
- Technology stack selection (Node.js/Express, Python/FastAPI, Go/Gin, etc.)
- Authentication strategy with flow diagrams
- Versioning approach with migration plan
- Rate limiting and throttling policy
- Pagination strategy (offset vs cursor-based)

### Phase 2: Resource & Endpoint Design (1-1.5 hours)
**Lead:** `full-stack-architect`

REST API Design:
- Design resource model and URL structure
- Define HTTP methods for each endpoint (GET, POST, PUT, PATCH, DELETE)
- Design request/response formats (JSON, XML if needed)
- Define status codes and error responses
- Plan HATEOAS links if applicable
- Design filtering, sorting, and search endpoints
- Plan bulk operations and batch endpoints
- Design idempotency for non-idempotent operations

GraphQL API Design:
- Design schema (types, queries, mutations, subscriptions)
- Plan resolvers and data loaders (N+1 prevention)
- Define input validation and error handling
- Design pagination (cursor-based vs offset)
- Plan subscription real-time updates if needed
- Design unions and interfaces for polymorphic data
- Plan schema directives for authorization
- Design custom scalars for domain types

**Deliverables:**
- REST: Endpoint list with methods, paths, request/response examples
- GraphQL: Complete schema definition (.graphql file)
- Error response formats (400, 401, 403, 404, 409, 422, 429, 500, 503)
- API design documentation with examples
- Request/response validation rules
- Idempotency key strategy (for REST)

### Phase 3: Database Schema Design (1-1.5 hours)
**Lead:** `data-engineer`

- Design database schema for API resources
- Create entity-relationship diagrams (ERD)
- Define tables, columns, data types, constraints
- Plan indexes for query performance (single-column, composite, partial)
- Design foreign key relationships and cascading rules
- Plan for soft deletes, timestamps, audit logs
- Create migration files (Prisma, Sequelize, Alembic, Flyway, etc.)
- Design database views for complex queries
- Plan partitioning strategy for large tables
- Design materialized views for reporting endpoints
- Plan database-level validation and constraints
- Design full-text search indexes if needed

**Deliverables:**
- Database ERD diagram (Mermaid, dbdiagram.io, or similar)
- Migration files for schema creation with rollback capability
- Index strategy for API queries with explain plans
- Database constraints and validations
- Audit logging schema
- Database performance tuning recommendations
- Connection pooling configuration

### Phase 4: API Documentation & OpenAPI Spec (45-60 min)
**Lead:** `full-stack-architect`

REST APIs:
- Create OpenAPI 3.0 specification (openapi.yaml or swagger.yaml)
- Document all endpoints, parameters, request/response schemas
- Define authentication mechanisms in spec (securitySchemes)
- Include example requests and responses for all endpoints
- Set up Swagger UI or Redoc for interactive docs
- Document error responses with examples
- Add operation IDs for code generation
- Document webhooks if applicable
- Add external documentation links
- Configure Try It Out functionality

GraphQL APIs:
- Generate GraphQL schema documentation
- Create example queries and mutations with variables
- Document authentication and authorization rules
- Set up GraphQL Playground or GraphiQL
- Document subscription event types
- Add schema descriptions and deprecation notices
- Create query complexity documentation
- Document introspection security

**Deliverables:**
- OpenAPI 3.0 spec (REST) or GraphQL schema docs
- Interactive API documentation (Swagger UI, GraphQL Playground)
- Example requests for common use cases (Postman collection, cURL examples)
- Authentication flow documentation with diagrams
- Webhook documentation (if applicable)
- API changelog template
- Getting started guide for developers
- SDK generation configuration (if auto-generating clients)

### Phase 5: Security & Performance Planning (45-60 min)
**Lead:** `full-stack-architect`, **Supporting:** `data-engineer`

Security:
- Design authentication middleware (JWT verification, API key validation)
- Plan authorization (RBAC, ABAC, resource-level permissions)
- Define input validation and sanitization (JSON schema, GraphQL validators)
- Plan SQL injection and XSS prevention
- Design CORS policy (allowed origins, methods, headers)
- Plan API security headers (Content Security Policy, X-Frame-Options, etc.)
- Design secrets management (API keys, tokens, credentials)
- Plan audit logging (who accessed what and when)
- Design request signing for sensitive operations
- Plan encryption at rest and in transit
- Design webhook signature verification
- Plan for OWASP API Security Top 10 mitigation

Performance:
- Design caching strategy (Redis for responses, ETag/If-None-Match, CDN)
- Plan database query optimization (N+1 prevention, eager loading, query hints)
- Design rate limiting (token bucket, sliding window, per-user/per-IP)
- Plan API response compression (gzip, brotli)
- Design pagination for large datasets (cursor-based for scalability)
- Plan background jobs for heavy operations (job queues, webhooks)
- Design connection pooling (database, HTTP clients)
- Plan database read replicas for read-heavy APIs
- Design query result caching with invalidation strategy
- Plan GraphQL query complexity limits
- Design batch loading and DataLoader patterns
- Plan API gateway caching and routing

**Deliverables:**
- Security implementation checklist with OWASP coverage
- Caching strategy documentation with TTL policies
- Rate limiting configuration (Redis, API gateway)
- Performance optimization plan with target metrics
- Database query optimization guide
- Authentication and authorization matrix (who can do what)
- Security testing plan (penetration testing, SAST/DAST)
- Performance monitoring dashboard specification

### Phase 6: Implementation Checklist & Testing Strategy (30-45 min)
**Lead:** `full-stack-architect`

- Create implementation task breakdown (user stories, tickets)
- Define testing strategy (unit, integration, E2E, contract testing)
- Plan API versioning and deprecation process
- Create monitoring and logging strategy (metrics, traces, logs)
- Define SLAs and error budgets (uptime, latency, error rate)
- Plan API client SDKs if needed (auto-generation, manual)
- Design deployment strategy (blue-green, canary, rolling)
- Plan API governance and review process
- Design backward compatibility testing
- Plan API analytics and usage tracking
- Design incident response playbook
- Plan API lifecycle management (alpha, beta, GA, deprecated)

**Deliverables:**
- Implementation task list (ready for development with priority)
- Test plan with example test cases (Postman, Jest, PyTest, etc.)
- Monitoring strategy (Prometheus metrics, ELK logs, Jaeger traces)
- API versioning and deprecation policy with timeline
- Deployment checklist with rollback plan
- API usage analytics plan (track endpoints, users, errors)
- Incident response runbook
- API governance guidelines (review process, breaking changes)

## Expected Outcomes

### API Design Artifacts
- **OpenAPI 3.0 Specification** (REST) or **GraphQL Schema** with complete documentation
- **Database migrations** ready for execution with rollback capability
- **ERD diagram** showing data relationships and cardinality
- **Security implementation plan** with authentication and authorization
- **Performance optimization strategy** with caching and rate limiting
- **Testing strategy** with contract tests and integration tests
- **Deployment plan** with monitoring and rollback procedures

### Design Quality
- **RESTful best practices** followed (resource naming, HTTP methods, status codes, HATEOAS)
- **GraphQL best practices** followed (schema design, N+1 prevention, pagination, subscriptions)
- **Security by design** (authentication, authorization, input validation, OWASP coverage)
- **Performance optimized** (database indexes, caching, query optimization, connection pooling)
- **Well-documented** (OpenAPI spec, inline code comments, examples, getting started guide)
- **Versioning strategy** (backward compatibility, deprecation policy, migration guide)
- **Observability** (logging, metrics, tracing, alerting)

### Business Value
- **Faster development** with clear API design and documentation (30-50% faster)
- **Fewer bugs** through comprehensive planning and validation (40-60% fewer production bugs)
- **Better performance** with optimized queries and caching (50-80% faster response times)
- **Easier maintenance** with versioning and deprecation strategy
- **Developer-friendly** with interactive docs and examples (faster onboarding)
- **Scalable architecture** supporting future growth
- **Reduced technical debt** from upfront design decisions

## Usage

```bash
# Design REST API for e-commerce platform
/api-design --type=rest --domain=ecommerce

# Design GraphQL API for social network
/api-design --type=graphql --domain=social

# Design both REST and GraphQL for multi-client app
/api-design --type=hybrid --domain=saas

# Design REST API with specific framework
/api-design --type=rest --framework=fastapi --database=postgresql

# Design GraphQL API with real-time subscriptions
/api-design --type=graphql --realtime=true --database=mongodb
```

## Prerequisites

- [ ] API requirements defined (features, use cases, user stories)
- [ ] Technology stack selected (backend framework, database)
- [ ] Database choice made (PostgreSQL, MongoDB, MySQL, etc.)
- [ ] Authentication requirements understood (JWT, OAuth2, API keys)
- [ ] Performance requirements known (SLA, expected load, concurrent users)
- [ ] Security requirements defined (compliance, data sensitivity)
- [ ] Client types identified (web, mobile, third-party integrations)

## Success Criteria

### REST API Design
- [ ] OpenAPI 3.0 spec complete and valid (passes linting)
- [ ] All endpoints documented with request/response examples
- [ ] Authentication and authorization defined for all endpoints
- [ ] Error handling comprehensive (all error codes with examples)
- [ ] Database schema optimized for API queries (indexes, constraints)
- [ ] Pagination strategy implemented for list endpoints
- [ ] Rate limiting and throttling configured
- [ ] Caching strategy defined with TTL policies
- [ ] Versioning strategy documented with migration plan
- [ ] Idempotency keys designed for non-idempotent operations

### GraphQL API Design
- [ ] GraphQL schema complete and valid (passes validation)
- [ ] Queries and mutations documented with examples
- [ ] N+1 query prevention planned (DataLoader, batch loading)
- [ ] Pagination strategy defined (cursor-based recommended)
- [ ] Subscription design complete (if real-time needed)
- [ ] Schema directives for authorization implemented
- [ ] Query complexity limits configured
- [ ] Introspection security configured (disable in production)
- [ ] Custom scalars defined for domain types
- [ ] Schema versioning and evolution strategy planned

### General API Quality
- [ ] Database migrations ready to execute (with rollback)
- [ ] ERD diagram complete with relationships
- [ ] Security checklist complete (OWASP API Security Top 10)
- [ ] Performance optimization planned (caching, indexes, query optimization)
- [ ] Testing strategy defined (unit, integration, E2E, contract)
- [ ] Monitoring and logging planned (metrics, traces, logs)
- [ ] Deployment strategy documented (blue-green, canary)
- [ ] API governance process established
- [ ] Documentation complete (OpenAPI, examples, getting started)
- [ ] SLAs and error budgets defined (uptime, latency, error rate)

## Real-World Examples

### Example 1: E-commerce REST API
**Design Time:** 5 hours

Resources Designed:
- Products API (catalog, search, filtering)
- Orders API (checkout, management, tracking)
- Users API (registration, profile, auth)
- Cart API (add/remove, totals, coupons)
- Payments API (Stripe integration)

Delivered:
- 24 endpoints across 5 resources
- OpenAPI 3.0 spec (1,200 lines)
- Database schema: 12 tables
- JWT auth (15min access, 7d refresh)
- Redis caching (90% hit rate, 5min TTL)

Impact:
- Developed in 3 weeks (vs. 6 weeks ad-hoc)
- 95% test coverage
- 85ms avg response (p95 <200ms)
- Zero breaking changes in 6 months
- 99.9% uptime, 10x Black Friday traffic

### Example 2: SaaS GraphQL API
**Design Time:** 4.5 hours

Schema Designed:
- User/workspace management
- Project/task management
- Real-time collaboration (subscriptions)
- Analytics queries

Delivered:
- 45 types, 32 queries, 28 mutations, 5 subscriptions
- DataLoader for N+1 prevention
- Cursor-based pagination
- Database: 18 tables with RLS policies
- WebSocket subscriptions (Redis pub/sub)

Impact:
- Single API for web/mobile/desktop
- 60% fewer API calls vs REST
- <100ms real-time latency
- 50ms avg query (p95 <150ms)
- 99.95% uptime with auto-scaling

## Related Commands

- `/database-design` - Database schema design
- `/security-audit` - API security review
- `/quality:architecture-review` - Architecture assessment
- `/documentation-generator` - Auto-generate docs

## Notes

**API Paradigm Choice:**
- REST: Simple CRUD, public APIs, strong caching
- GraphQL: Complex data graphs, mobile apps, exact data fetching
- Hybrid: REST for public, GraphQL for internal/mobile

**Performance Targets:**
- p95 response time: <200ms
- p95 query time: <100ms
- Cache hit rate: >80%
- Rate limit: 1000-5000 req/hour per user

**Security Priorities:**
1. Authentication/authorization (JWT, OAuth2, RBAC)
2. Input validation (JSON schema, sanitization)
3. Rate limiting (prevent abuse)
4. Encryption (HTTPS, at-rest for sensitive data)
5. OWASP API Security Top 10 coverage

This workflow ensures APIs are secure, performant, well-documented, and maintainable from day one.
