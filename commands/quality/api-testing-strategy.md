# API Testing Strategy

Comprehensive API testing strategy and implementation orchestrating qa-test-engineer, security-audit-specialist, and full-stack-architect to ensure API reliability, security, performance, and contract compliance across REST, GraphQL, gRPC, and WebSocket APIs.

## What This Command Does

This command executes a multi-dimensional API quality assurance workflow covering functional correctness, security hardening, performance optimization, contract validation, and integration testing. The coordinated approach ensures APIs meet production standards for reliability, security, scalability, and maintainability while preventing regressions and establishing automated quality gates in CI/CD pipelines.

The workflow analyzes API specifications, implements comprehensive test suites, validates security controls, benchmarks performance characteristics, and establishes monitoring strategies to ensure APIs deliver consistent, secure, and performant service to consumers.

## When to Use

- **New API Development**: Building REST, GraphQL, gRPC, or WebSocket APIs from scratch requiring comprehensive testing strategy
- **API Refactoring**: Modernizing legacy APIs while ensuring backward compatibility and preventing regressions
- **API Versioning**: Introducing new API versions with contract testing and breaking change detection
- **Pre-Production Quality Gates**: Establishing automated quality validation before production deployment
- **Security Audit Requirements**: Validating API security controls and compliance with OWASP API Security Top 10
- **Performance Optimization**: Identifying and resolving API performance bottlenecks and scalability issues
- **Third-Party Integration**: Validating external API integrations with contract testing and resilience patterns
- **Microservices Testing**: Comprehensive testing across distributed API ecosystems with service dependencies
- **Compliance Requirements**: Ensuring API quality standards for SOC 2, HIPAA, PCI-DSS, or GDPR compliance
- **Production Incident Prevention**: Implementing robust testing to catch issues before customer impact

## Testing Dimensions

### 1. Functional API Testing
**Led by: qa-test-engineer**

**Request/Response Validation**:
- HTTP method correctness (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- Request header validation (Content-Type, Accept, Authorization, custom headers)
- Request body validation (JSON schema, XML validation, form data, multipart)
- Query parameter handling (pagination, filtering, sorting, search)
- Path parameter validation (resource IDs, slugs, nested resources)
- Response status codes (2xx success, 3xx redirects, 4xx client errors, 5xx server errors)
- Response body validation (schema compliance, data types, required fields, optional fields)
- Response header verification (Content-Type, Cache-Control, CORS headers, rate limit headers)

**Business Logic Validation**:
- Resource creation workflows (POST endpoints with validation rules)
- Resource retrieval operations (GET endpoints with filtering, pagination, sorting)
- Resource update logic (PUT for full replacement, PATCH for partial updates)
- Resource deletion (hard delete, soft delete, cascading deletes)
- Business rule enforcement (authorization logic, state transitions, validation constraints)
- Data consistency across operations (ACID properties, eventual consistency validation)
- Idempotency testing (ensuring safe retries for POST, PUT, DELETE operations)

**Error Handling & Edge Cases**:
- Invalid input validation (malformed JSON, type mismatches, constraint violations)
- Missing required fields and parameters
- Boundary value testing (minimum/maximum values, length limits, numeric ranges)
- Null and empty value handling
- Special character handling (Unicode, escape sequences, injection attempts)
- Large payload handling (size limits, streaming, chunked encoding)
- Rate limiting and throttling behavior
- Circuit breaker and timeout handling
- Graceful degradation with dependency failures

**API Protocol Testing**:
- **REST APIs**: Resource modeling, HATEOAS, content negotiation, caching strategies
- **GraphQL APIs**: Query validation, mutation testing, subscription handling, N+1 query prevention
- **gRPC APIs**: Protocol buffer validation, streaming (unary, server, client, bidirectional), error handling
- **WebSocket APIs**: Connection lifecycle, message framing, reconnection logic, backpressure handling

**Test Automation Framework**:
```javascript
// Example: Jest + Supertest for REST API testing
describe('User API Tests', () => {
  describe('POST /api/users', () => {
    it('should create user with valid data', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'test@example.com',
          name: 'Test User',
          role: 'user'
        })
        .expect(201)
        .expect('Content-Type', /json/);

      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: 'test@example.com',
        name: 'Test User',
        role: 'user',
        createdAt: expect.any(String)
      });
    });

    it('should reject invalid email format', async () => {
      await request(app)
        .post('/api/users')
        .send({ email: 'invalid-email', name: 'Test' })
        .expect(400)
        .expect((res) => {
          expect(res.body.error).toMatch(/email/i);
        });
    });

    it('should enforce authentication', async () => {
      await request(app)
        .post('/api/users')
        .send({ email: 'test@example.com', name: 'Test' })
        .expect(401);
    });
  });
});
```

### 2. API Contract Testing
**Led by: full-stack-architect**

**OpenAPI/Swagger Specification**:
- Complete API documentation with OpenAPI 3.x specification
- Schema definitions for all request and response models
- Parameter documentation (path, query, header, cookie parameters)
- Authentication/authorization schemes (OAuth2, JWT, API keys, basic auth)
- Response status code documentation with examples
- Error response schemas and error code documentation
- Example requests and responses for all operations
- Deprecation notices and migration guides for versioned APIs

**Schema Validation & Enforcement**:
- Automated request validation against OpenAPI schema
- Response validation ensuring API implementation matches contract
- Schema-driven test generation (generate tests from OpenAPI spec)
- Breaking change detection across API versions
- Schema evolution validation (additive changes, deprecation workflows)
- Type safety enforcement (preventing type drift between spec and implementation)

**Contract Testing with Pact**:
```javascript
// Example: Consumer-driven contract testing with Pact
const { Pact } = require('@pact-foundation/pact');
const { UserService } = require('./user-service');

describe('User Service Contract', () => {
  const provider = new Pact({
    consumer: 'WebApp',
    provider: 'UserAPI',
    port: 8080
  });

  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  it('should fetch user by ID', async () => {
    await provider.addInteraction({
      state: 'user 123 exists',
      uponReceiving: 'a request for user 123',
      withRequest: {
        method: 'GET',
        path: '/api/users/123',
        headers: { Accept: 'application/json' }
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: '123',
          email: 'user@example.com',
          name: 'Test User'
        }
      }
    });

    const userService = new UserService('http://localhost:8080');
    const user = await userService.getUser('123');
    expect(user.email).toBe('user@example.com');
  });
});
```

**Versioning Strategy**:
- API version management (URL versioning, header versioning, content negotiation)
- Backward compatibility validation across versions
- Deprecation policy enforcement (sunset headers, deprecation warnings)
- Migration path documentation and tooling
- Version negotiation testing (client version support, fallback strategies)

**Documentation Generation & Validation**:
- Automated API documentation from OpenAPI specs (Swagger UI, Redoc, Stoplight)
- Code generation from schemas (client SDKs, server stubs, type definitions)
- Documentation testing (ensuring examples are valid and executable)
- Interactive API explorers with authentication support

### 3. API Security Testing
**Led by: security-audit-specialist**

**OWASP API Security Top 10 Coverage**:

**API1:2023 - Broken Object Level Authorization**:
- Test unauthorized access to resources belonging to other users
- Validate object-level permissions (can user A access user B's resources?)
- Test indirect object references (predictable IDs, enumeration attacks)
- Verify authorization checks on all CRUD operations

**API2:2023 - Broken Authentication**:
- Test authentication mechanism vulnerabilities (weak passwords, credential stuffing)
- Validate JWT implementation (algorithm confusion, weak secrets, token expiration)
- Test session management (session fixation, hijacking, timeout enforcement)
- Multi-factor authentication validation
- OAuth/OIDC flow testing (authorization code, implicit, client credentials)

**API3:2023 - Broken Object Property Level Authorization**:
- Test mass assignment vulnerabilities (modifying read-only fields)
- Validate field-level permissions (sensitive data exposure)
- Test excessive data exposure in responses
- Verify proper data filtering based on user roles

**API4:2023 - Unrestricted Resource Consumption**:
- Rate limiting validation (per-user, per-endpoint, global limits)
- Request size limits (body size, header size, file upload limits)
- Pagination enforcement (prevent unlimited result sets)
- Query complexity limits (GraphQL depth limits, join limits)
- Connection pool exhaustion testing

**API5:2023 - Broken Function Level Authorization**:
- Test role-based access control (RBAC) enforcement
- Validate permission boundaries (user vs admin endpoints)
- Test privilege escalation attempts
- Verify authorization on administrative functions

**API6:2023 - Unrestricted Access to Sensitive Business Flows**:
- Test business logic abuse (account takeover flows, payment manipulation)
- Validate rate limiting on sensitive operations
- Test for automation detection and CAPTCHA requirements
- Verify anti-fraud controls

**API7:2023 - Server Side Request Forgery (SSRF)**:
- Test URL parameter handling (webhook URLs, image fetching, redirects)
- Validate URL scheme restrictions (block file://, gopher://, internal IPs)
- Test internal service access prevention
- Verify domain whitelist enforcement

**API8:2023 - Security Misconfiguration**:
- Test for exposed debugging endpoints
- Validate error message sanitization (no stack traces in production)
- Test CORS configuration (overly permissive origins)
- Verify security header implementation (HSTS, CSP, X-Frame-Options)
- Test for default credentials and configurations

**API9:2023 - Improper Inventory Management**:
- Identify all API endpoints and versions
- Test deprecated API versions for vulnerabilities
- Validate API documentation accuracy
- Test for shadow APIs and undocumented endpoints

**API10:2023 - Unsafe Consumption of APIs**:
- Test third-party API integration security
- Validate input sanitization from external APIs
- Test timeout and circuit breaker configurations
- Verify data validation for external responses

**Injection Attack Testing**:
```python
# Example: SQL injection testing with SQLMap integration
import subprocess
import json

def test_sql_injection(endpoint_url, parameters):
    """Test API endpoint for SQL injection vulnerabilities"""
    sqlmap_cmd = [
        'sqlmap',
        '-u', endpoint_url,
        '--data', json.dumps(parameters),
        '--batch',
        '--risk', '3',
        '--level', '5',
        '--threads', '10',
        '--technique', 'BEUSTQ',
        '--output-dir', './security-reports'
    ]

    result = subprocess.run(sqlmap_cmd, capture_output=True, text=True)

    if 'vulnerable' in result.stdout.lower():
        raise SecurityVulnerabilityError(
            f"SQL injection vulnerability detected in {endpoint_url}"
        )
```

**Authentication & Authorization Testing**:
- Token validation (expired tokens, malformed tokens, tampered signatures)
- Authorization bypass attempts (parameter tampering, forced browsing)
- API key security (key rotation, key compromise scenarios)
- Certificate validation (mTLS, certificate pinning)

**Security Headers & HTTPS**:
- TLS configuration testing (supported protocols, cipher suites)
- Certificate validation (expiration, chain validation, revocation)
- Security header validation (Strict-Transport-Security, X-Content-Type-Options)
- CORS policy validation (origin whitelist, credential handling)

**Automated Security Scanning**:
```bash
# OWASP ZAP automated API security scan
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable \
  zap-api-scan.py \
  -t https://api.example.com/openapi.json \
  -f openapi \
  -r api-security-report.html \
  -w api-security-report.md \
  -J api-security-report.json
```

### 4. Performance & Load Testing
**Led by: qa-test-engineer**

**Response Time Benchmarking**:
- Latency measurements (P50, P75, P95, P99, P99.9 percentiles)
- Time to first byte (TTFB) analysis
- Request/response payload size optimization
- Network latency simulation (geographic distribution)
- Cold start vs warm cache performance

**Throughput & Concurrency Testing**:
- Requests per second (RPS) capacity testing
- Concurrent user simulation (1x, 10x, 100x normal load)
- Connection pool sizing validation
- Thread pool and worker configuration optimization

**Load Testing with k6**:
```javascript
// Example: k6 load testing script
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],  // Error rate < 1%
    errors: ['rate<0.1'],
  },
};

export default function () {
  const payload = JSON.stringify({
    email: `user${__VU}@example.com`,
    name: `User ${__VU}`
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.API_TOKEN}`
    },
  };

  const res = http.post('https://api.example.com/users', payload, params);

  const success = check(res, {
    'status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has user id': (r) => r.json('id') !== undefined,
  });

  errorRate.add(!success);
  sleep(1);
}
```

**Stress Testing**:
- Breaking point identification (maximum sustainable load)
- Degradation testing (performance under extreme load)
- Recovery testing (system recovery after stress)
- Resource exhaustion scenarios (CPU, memory, connections)

**Spike Testing**:
- Sudden traffic surge handling (10x-100x load spikes)
- Auto-scaling validation (scale-up speed, scale-down behavior)
- Circuit breaker activation testing
- Request queuing and shedding strategies

**Soak Testing (Endurance Testing)**:
- Extended duration testing (24h, 48h, 72h continuous load)
- Memory leak detection
- Connection leak identification
- Performance degradation over time
- Resource cleanup validation

**Scalability Validation**:
- Horizontal scaling testing (adding more instances)
- Vertical scaling testing (increasing instance resources)
- Database connection pool scaling
- Cache effectiveness under load
- CDN and edge caching validation

**Performance Monitoring Integration**:
```yaml
# Example: Prometheus metrics for API performance
apiVersion: v1
kind: Service
metadata:
  name: api-metrics
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
spec:
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
  selector:
    app: api-service
```

**Performance SLAs & SLOs**:
- **Availability**: 99.9% uptime (43.8 minutes downtime/month)
- **Latency**: P95 < 200ms, P99 < 500ms
- **Throughput**: > 1000 RPS per instance
- **Error Rate**: < 0.1% of all requests
- **Time to Recovery**: < 5 minutes for automated recovery

### 5. Integration Testing
**Led by: full-stack-architect**

**End-to-End Workflow Testing**:
- Complete user journey validation (registration → authentication → resource operations → cleanup)
- Multi-endpoint transaction flows (create order → add items → process payment → confirm)
- State management across requests (session state, transaction state, workflow state)
- Error recovery workflows (retry logic, compensation transactions, rollback)

**Service Dependency Testing**:
- Downstream API integration testing (third-party services, internal microservices)
- Database transaction testing (ACID compliance, isolation levels, deadlock prevention)
- Message queue integration (Kafka, RabbitMQ, SQS - producer/consumer testing)
- Cache integration testing (Redis, Memcached - hit rates, invalidation, consistency)
- File storage integration (S3, GCS, Azure Blob - upload, download, presigned URLs)

**External API Mocking**:
```javascript
// Example: Mock Service Worker for API mocking
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('https://api.stripe.com/v1/payment_intents', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 'pi_mock_123',
        status: 'succeeded',
        amount: 1000,
        currency: 'usd'
      })
    );
  }),

  rest.get('https://api.github.com/user', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        login: 'testuser',
        id: 12345,
        email: 'test@example.com'
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**Contract Testing Between Services**:
- Provider contract verification (API implements expected contract)
- Consumer contract verification (client correctly consumes API)
- Contract evolution testing (backward/forward compatibility)
- Breaking change detection automation

**Database Integration Testing**:
- Transaction isolation testing (read committed, repeatable read, serializable)
- Constraint validation (foreign keys, unique constraints, check constraints)
- Trigger and stored procedure testing
- Database migration testing (up/down migrations, rollback scenarios)

**Event-Driven Integration Testing**:
- Message publishing validation
- Event consumer testing (message processing, error handling, dead letter queues)
- Event ordering guarantees (for systems requiring ordered processing)
- Eventual consistency validation

**Resilience Pattern Testing**:
- Circuit breaker behavior (open, half-open, closed states)
- Retry logic with exponential backoff
- Timeout handling (connection timeout, read timeout)
- Fallback mechanisms (degraded functionality, cached responses)
- Bulkhead isolation (resource pool separation)

### 6. Observability & Monitoring
**Led by: qa-test-engineer**

**Structured Logging**:
- Request/response logging (sanitized for PII)
- Error logging with stack traces and context
- Audit logging for sensitive operations
- Log correlation with distributed tracing IDs
- Log level management (DEBUG, INFO, WARN, ERROR)

**Metrics Collection**:
```javascript
// Example: Prometheus metrics instrumentation
const prometheus = require('prom-client');

const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new prometheus.Gauge({
  name: 'http_active_connections',
  help: 'Number of active HTTP connections'
});

// Middleware to track metrics
app.use((req, res, next) => {
  const start = Date.now();
  activeConnections.inc();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .observe(duration);
    httpRequestTotal
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .inc();
    activeConnections.dec();
  });

  next();
});
```

**Distributed Tracing**:
- Request tracing across microservices (OpenTelemetry, Jaeger, Zipkin)
- Trace context propagation (W3C Trace Context standard)
- Span instrumentation (database queries, external API calls, cache operations)
- Trace sampling strategies (head-based, tail-based sampling)

**Error Tracking & Alerting**:
- Error aggregation and deduplication (Sentry, Rollbar, Bugsnag)
- Error rate monitoring and alerting
- Stack trace analysis and grouping
- Error context capture (user info, request details, environment)

**SLA/SLO Monitoring**:
```yaml
# Example: SLO definition with Prometheus alerting
groups:
  - name: api_slos
    rules:
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "API error rate exceeds 1%"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API P95 latency exceeds 500ms"
          description: "P95 latency is {{ $value }}s"

      - alert: LowAvailability
        expr: |
          (
            sum(rate(http_requests_total{status_code!~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) < 0.999
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "API availability below 99.9%"
          description: "Availability is {{ $value | humanizePercentage }}"
```

**Health Check Endpoints**:
- Liveness probes (is the service running?)
- Readiness probes (is the service ready to accept traffic?)
- Dependency health checks (database, cache, message queue status)
- Graceful shutdown handling

**API Analytics**:
- Endpoint usage statistics (most/least used endpoints)
- Client identification and tracking (user agents, API keys, client versions)
- Geographic distribution of requests
- Feature adoption tracking

## Tools & Frameworks

### Testing Frameworks

**REST API Testing**:
- **Supertest** (Node.js): HTTP assertion library for Express/Koa apps
- **REST Assured** (Java): Domain-specific language for REST API testing
- **Pytest + Requests** (Python): Flexible testing with powerful assertions
- **Postman/Newman**: Collection-based testing with CI/CD integration
- **Insomnia**: REST client with test automation and code generation

**GraphQL API Testing**:
- **Apollo Client Testing**: Mock provider and testing utilities
- **GraphQL Testing Library**: Assertions for GraphQL queries and mutations
- **EasyGraphQL Tester**: Schema-based testing and mocking
- **Postman GraphQL**: Collection-based GraphQL testing

**gRPC API Testing**:
- **grpcurl**: Command-line tool for gRPC testing
- **BloomRPC**: GUI client for gRPC testing
- **ghz**: gRPC performance testing and benchmarking
- **Protocurl**: Protocol buffer debugging and testing

### Load & Performance Testing

**Modern Load Testing Tools**:
- **k6** (JavaScript): Developer-friendly load testing with scripting
- **Locust** (Python): Distributed load testing with Python test scenarios
- **Artillery** (Node.js): Cloud-scale load testing with YAML configuration
- **Gatling** (Scala): High-performance load testing with detailed reports
- **JMeter** (Java): Traditional enterprise load testing platform

**Real-User Monitoring**:
- **WebPageTest**: Performance testing from real browsers in various locations
- **Lighthouse CI**: Automated performance auditing in CI/CD pipelines
- **SpeedCurve**: Continuous performance monitoring and alerting

### Contract Testing

**Contract Testing Frameworks**:
- **Pact**: Consumer-driven contract testing for microservices
- **Spring Cloud Contract**: JVM-based contract testing framework
- **Specmatic**: API-first contract testing from OpenAPI/GraphQL specs
- **Postman Contract Testing**: Contract validation against API specifications

### API Documentation & Specification

**API Specification Tools**:
- **OpenAPI/Swagger**: Industry-standard REST API specification
- **GraphQL Schema**: Type-safe GraphQL API definitions
- **Protocol Buffers**: gRPC service and message definitions
- **API Blueprint**: Markdown-based API documentation

**Documentation Platforms**:
- **Swagger UI**: Interactive API documentation from OpenAPI specs
- **Redoc**: Modern OpenAPI documentation with excellent UX
- **Stoplight**: API design, documentation, and mocking platform
- **ReadMe**: Developer-friendly API documentation and SDK generation

### Security Testing

**Vulnerability Scanning**:
- **OWASP ZAP**: Automated security testing and penetration testing
- **Burp Suite**: Web application security testing platform
- **SQLMap**: Automated SQL injection detection and exploitation
- **Nikto**: Web server vulnerability scanner

**API Security Testing**:
- **42Crunch**: API security testing and protection platform
- **StackHawk**: Dynamic API security testing in CI/CD
- **Astra Security**: Automated penetration testing for APIs
- **HCL AppScan**: Enterprise security testing solution

### Monitoring & Observability

**Metrics & Monitoring**:
- **Prometheus**: Time-series metrics collection and alerting
- **Grafana**: Visualization and dashboards for metrics
- **Datadog**: Full-stack observability platform
- **New Relic**: Application performance monitoring (APM)

**Distributed Tracing**:
- **Jaeger**: Open-source distributed tracing system
- **Zipkin**: Distributed tracing for microservices
- **OpenTelemetry**: Unified observability framework
- **Lightstep**: Enterprise observability with distributed tracing

**Error Tracking**:
- **Sentry**: Real-time error tracking and monitoring
- **Rollbar**: Error monitoring with intelligent grouping
- **Bugsnag**: Stability monitoring and error reporting
- **Raygun**: Application monitoring and crash reporting

### CI/CD Integration

**Continuous Integration Platforms**:
- **GitHub Actions**: Workflow automation with extensive marketplace
- **GitLab CI/CD**: Integrated CI/CD with GitLab repositories
- **Jenkins**: Extensible automation server with plugins
- **CircleCI**: Cloud-based CI/CD with Docker support
- **Travis CI**: Distributed build and test platform

**API Testing in Pipelines**:
```yaml
# Example: GitHub Actions workflow for API testing
name: API Testing Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  functional-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run database migrations
        run: npm run migrate
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb

      - name: Generate coverage report
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run Pact consumer tests
        run: npm run test:pact:consumer

      - name: Publish Pact contracts
        run: |
          npx pact-broker publish ./pacts \
            --consumer-app-version=${{ github.sha }} \
            --branch=${{ github.ref_name }}

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run OWASP ZAP API scan
        uses: zaproxy/action-api-scan@v0.4.0
        with:
          target: 'https://staging-api.example.com/openapi.json'
          format: 'openapi'
          fail_action: true

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  performance-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Setup k6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load tests
        run: k6 run --out json=results.json tests/load/api-load-test.js
        env:
          API_BASE_URL: https://staging-api.example.com
          API_TOKEN: ${{ secrets.STAGING_API_TOKEN }}

      - name: Validate performance SLOs
        run: node scripts/validate-performance-slos.js results.json

      - name: Upload k6 results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: results.json

  openapi-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate OpenAPI spec
        uses: char0n/swagger-editor-validate@v1
        with:
          definition-file: docs/openapi.yaml

      - name: Check for breaking changes
        uses: oasdiff/oasdiff-action@v0.0.15
        with:
          base: 'https://api.example.com/openapi.json'
          revision: 'docs/openapi.yaml'
          fail-on-breaking: true
```

## Multi-Agent Orchestration

### Phase 1: API Discovery & Analysis
**Duration: 2-4 hours**

**qa-test-engineer** initiates comprehensive API inventory:
- Catalogs all API endpoints, methods, and parameters
- Reviews existing API documentation (OpenAPI specs, GraphQL schemas, gRPC proto files)
- Identifies testing gaps in current coverage
- Analyzes API complexity and risk assessment
- Documents authentication mechanisms and authorization patterns

**full-stack-architect** evaluates API architecture:
- Reviews API design patterns (RESTful principles, GraphQL schema design, gRPC service design)
- Assesses API versioning strategy and backward compatibility approach
- Evaluates service dependencies and integration points
- Reviews data models and schema definitions
- Identifies contract testing requirements

**security-audit-specialist** performs security reconnaissance:
- Maps attack surface and threat vectors
- Identifies authentication and authorization mechanisms
- Reviews API security configurations and policies
- Assesses compliance requirements (OWASP API Top 10, GDPR, PCI-DSS)
- Documents sensitive data flows and PII handling

**Deliverable**: Comprehensive API Testing Strategy Document with risk-based testing priorities

### Phase 2: Test Framework Setup
**Duration: 4-8 hours**

**qa-test-engineer** implements testing infrastructure:
- Configures test automation framework (Jest, Pytest, or appropriate stack)
- Sets up test data management and fixtures
- Configures test environment (local, staging, pre-production)
- Implements test utilities and helper functions
- Sets up code coverage tooling

**full-stack-architect** establishes contract testing:
- Creates or validates OpenAPI/GraphQL schema specifications
- Implements schema validation middleware
- Sets up Pact for consumer-driven contract testing
- Configures API mocking services for integration testing
- Establishes contract versioning and evolution strategy

**security-audit-specialist** configures security testing tools:
- Sets up OWASP ZAP or Burp Suite for automated scanning
- Configures authentication testing framework
- Implements security test data (malicious payloads, injection vectors)
- Sets up vulnerability scanning in CI/CD pipeline
- Configures security monitoring and alerting

**Deliverable**: Complete test automation framework with CI/CD integration

### Phase 3: Functional Test Implementation
**Duration: 16-40 hours (varies by API size)**

**qa-test-engineer** develops comprehensive test suites:

**Unit Testing (Endpoint-Level)**:
- Request validation tests (valid/invalid inputs, boundary conditions)
- Response validation tests (status codes, headers, body schema)
- Business logic tests (calculation accuracy, state transitions)
- Error handling tests (validation errors, server errors, timeouts)

**Integration Testing (Workflow-Level)**:
- Multi-endpoint workflow tests (user registration → authentication → operations)
- Database integration tests (CRUD operations, transactions, constraints)
- External service integration tests (third-party APIs, payment gateways)
- Message queue integration tests (event publishing, consumption)

**End-to-End Testing (Business-Level)**:
- Complete user journey tests (registration through checkout)
- Cross-service transaction tests (distributed transactions, saga patterns)
- Data consistency tests (eventual consistency validation)
- Recovery and rollback tests (error scenarios, compensation logic)

**full-stack-architect** ensures architectural compliance:
- Validates API responses match OpenAPI/GraphQL schema
- Tests API versioning and backward compatibility
- Verifies HATEOAS links and resource relationships (for REST APIs)
- Tests GraphQL query optimization and N+1 prevention
- Validates gRPC streaming and error handling

**Parallel Execution**: Both agents work concurrently, with architect reviewing test coverage alignment with contracts

**Deliverable**: Comprehensive functional test suite with >90% endpoint coverage

### Phase 4: Security Testing Implementation
**Duration: 8-16 hours**

**security-audit-specialist** executes security testing:

**Authentication Testing**:
```javascript
// Example: JWT authentication security tests
describe('JWT Authentication Security', () => {
  it('should reject expired tokens', async () => {
    const expiredToken = generateExpiredToken();
    await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${expiredToken}`)
      .expect(401);
  });

  it('should reject tampered tokens', async () => {
    const tamperedToken = tamperTokenSignature(validToken);
    await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${tamperedToken}`)
      .expect(401);
  });

  it('should reject tokens with algorithm confusion', async () => {
    const noneAlgorithmToken = createTokenWithAlgorithm('none');
    await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${noneAlgorithmToken}`)
      .expect(401);
  });
});
```

**Authorization Testing (OWASP API1, API5)**:
- Object-level authorization tests (accessing other users' resources)
- Function-level authorization tests (accessing admin endpoints as regular user)
- Role-based access control validation
- Permission boundary testing

**Injection Testing (OWASP API8)**:
- SQL injection testing (parameterized query validation)
- NoSQL injection testing (MongoDB operator injection)
- Command injection testing (system command execution)
- XML/JSON injection testing (entity expansion, deserialization)

**Rate Limiting & DoS Prevention (OWASP API4)**:
- Rate limit enforcement testing (per-user, per-IP, per-endpoint)
- Request size limit testing (body size, header size)
- Slow request handling (Slowloris-style attacks)
- Resource exhaustion testing (connection pool, memory)

**Input Validation Testing**:
- Boundary value testing (maximum/minimum values)
- Special character handling (Unicode, escape sequences)
- Content-type validation (MIME type confusion)
- File upload security (extension validation, content verification)

**OWASP ZAP Automated Scanning**:
```bash
#!/bin/bash
# Automated API security scanning with OWASP ZAP

# Start ZAP daemon
docker run -d --name zap-daemon \
  -p 8080:8080 \
  -v $(pwd)/zap-reports:/zap/reports \
  owasp/zap2docker-stable \
  zap.sh -daemon -port 8080 -config api.disablekey=true

# Wait for ZAP to start
sleep 30

# Import OpenAPI specification
curl -X POST "http://localhost:8080/JSON/openapi/action/importUrl/" \
  --data "url=https://api.example.com/openapi.json"

# Run active scan
SCAN_ID=$(curl -X POST "http://localhost:8080/JSON/ascan/action/scan/" \
  --data "url=https://api.example.com&recurse=true" | jq -r '.scan')

# Wait for scan completion
while [[ $(curl -s "http://localhost:8080/JSON/ascan/view/status/?scanId=$SCAN_ID" | jq -r '.status') != "100" ]]; do
  echo "Scan progress: $(curl -s "http://localhost:8080/JSON/ascan/view/status/?scanId=$SCAN_ID" | jq -r '.status')%"
  sleep 10
done

# Generate reports
curl "http://localhost:8080/OTHER/core/other/htmlreport/" > zap-reports/api-security-report.html
curl "http://localhost:8080/JSON/core/view/alerts/" > zap-reports/api-security-alerts.json

# Check for high-risk vulnerabilities
HIGH_RISK=$(curl -s "http://localhost:8080/JSON/core/view/alerts/?risk=High" | jq '.alerts | length')
if [[ $HIGH_RISK -gt 0 ]]; then
  echo "ERROR: $HIGH_RISK high-risk vulnerabilities found!"
  exit 1
fi
```

**qa-test-engineer** integrates security tests into main suite:
- Incorporates security tests into CI/CD pipeline
- Configures security test reporting and alerting
- Establishes security regression testing

**Deliverable**: Comprehensive security test suite with OWASP API Top 10 coverage

### Phase 5: Performance Testing
**Duration: 8-16 hours**

**qa-test-engineer** implements performance testing:

**Baseline Performance Testing**:
```javascript
// k6 baseline performance test
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const errorCounter = new Counter('errors');
const customTrend = new Trend('custom_duration');

export const options = {
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
    errors: ['count<10'],
  },
  scenarios: {
    baseline: {
      executor: 'constant-vus',
      vus: 10,
      duration: '5m',
    },
  },
};

export default function () {
  const payload = JSON.stringify({
    email: `user-${__VU}-${__ITER}@example.com`,
    name: `User ${__VU}`,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.API_TOKEN}`,
    },
  };

  const res = http.post(`${__ENV.API_BASE_URL}/users`, payload, params);

  const success = check(res, {
    'status is 201': (r) => r.status === 201,
    'has user id': (r) => r.json('id') !== undefined,
    'response time OK': (r) => r.timings.duration < 500,
  });

  if (!success) {
    errorCounter.add(1);
  }

  customTrend.add(res.timings.duration);
  sleep(1);
}
```

**Load Testing Scenarios**:
- Normal load testing (typical traffic patterns)
- Peak load testing (expected maximum load)
- Stress testing (beyond maximum capacity)
- Spike testing (sudden traffic surges)
- Soak testing (sustained load over extended period)

**Performance Profiling**:
- Database query optimization (slow query identification, index usage)
- N+1 query detection (especially critical for GraphQL)
- Memory profiling (heap analysis, memory leak detection)
- CPU profiling (hot path identification, optimization opportunities)

**Caching Strategy Validation**:
- Cache hit/miss ratio measurement
- Cache invalidation testing
- CDN effectiveness validation
- Redis/Memcached performance testing

**full-stack-architect** analyzes performance bottlenecks:
- Reviews database query plans and optimization opportunities
- Evaluates API pagination and filtering strategies
- Assesses serialization/deserialization performance
- Reviews connection pooling and resource management
- Recommends architectural improvements for scalability

**Deliverable**: Performance test suite with baseline benchmarks and SLO validation

### Phase 6: Monitoring & Observability
**Duration: 4-8 hours**

**qa-test-engineer** implements monitoring:

**Metrics Instrumentation**:
```javascript
// Prometheus metrics for API monitoring
const prometheus = require('prom-client');
const express = require('express');

// Create metrics registry
const register = new prometheus.Registry();

// HTTP request duration histogram
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
  registers: [register],
});

// HTTP request counter
const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register],
});

// Active connections gauge
const activeConnections = new prometheus.Gauge({
  name: 'http_active_connections',
  help: 'Number of active HTTP connections',
  registers: [register],
});

// Database query duration histogram
const dbQueryDuration = new prometheus.Histogram({
  name: 'db_query_duration_seconds',
  help: 'Duration of database queries',
  labelNames: ['operation', 'table'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1],
  registers: [register],
});

// Express middleware for automatic instrumentation
function metricsMiddleware(req, res, next) {
  const start = Date.now();
  activeConnections.inc();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || req.path;

    httpRequestDuration
      .labels(req.method, route, res.statusCode)
      .observe(duration);

    httpRequestTotal
      .labels(req.method, route, res.statusCode)
      .inc();

    activeConnections.dec();
  });

  next();
}

// Metrics endpoint
const app = express();
app.use(metricsMiddleware);
app.get('/metrics', (req, res) => {
  res.set('Content-Type', register.contentType);
  register.metrics().then(metrics => res.send(metrics));
});
```

**Distributed Tracing Setup**:
```javascript
// OpenTelemetry distributed tracing
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');

const provider = new NodeTracerProvider();

const jaegerExporter = new JaegerExporter({
  endpoint: 'http://jaeger:14268/api/traces',
  serviceName: 'api-service',
});

provider.addSpanProcessor(new BatchSpanProcessor(jaegerExporter));
provider.register();

registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
  ],
});
```

**Health Check Implementation**:
```javascript
// Comprehensive health check endpoint
app.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {},
  };

  try {
    // Database health check
    const dbStart = Date.now();
    await db.raw('SELECT 1');
    health.checks.database = {
      status: 'healthy',
      latency: Date.now() - dbStart,
    };
  } catch (error) {
    health.status = 'unhealthy';
    health.checks.database = {
      status: 'unhealthy',
      error: error.message,
    };
  }

  try {
    // Redis health check
    const redisStart = Date.now();
    await redis.ping();
    health.checks.redis = {
      status: 'healthy',
      latency: Date.now() - redisStart,
    };
  } catch (error) {
    health.status = 'degraded';
    health.checks.redis = {
      status: 'unhealthy',
      error: error.message,
    };
  }

  try {
    // External API health check
    const apiStart = Date.now();
    await axios.get('https://external-api.com/health', { timeout: 2000 });
    health.checks.external_api = {
      status: 'healthy',
      latency: Date.now() - apiStart,
    };
  } catch (error) {
    health.status = 'degraded';
    health.checks.external_api = {
      status: 'unhealthy',
      error: error.message,
    };
  }

  const statusCode = health.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(health);
});
```

**SLO Alerting Configuration**:
```yaml
# Prometheus alerting rules for API SLOs
groups:
  - name: api_slos
    interval: 30s
    rules:
      - alert: APIHighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.01
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "API error rate exceeds 1% SLO"
          description: "Current error rate: {{ $value | humanizePercentage }}"
          runbook: "https://wiki.example.com/runbooks/high-error-rate"

      - alert: APIHighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.2
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "API P95 latency exceeds 200ms SLO"
          description: "Current P95 latency: {{ $value }}s"
          runbook: "https://wiki.example.com/runbooks/high-latency"

      - alert: APILowAvailability
        expr: |
          (
            sum(rate(http_requests_total{status_code!~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) < 0.999
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "API availability below 99.9% SLO"
          description: "Current availability: {{ $value | humanizePercentage }}"
          runbook: "https://wiki.example.com/runbooks/low-availability"

      - alert: DatabaseSlowQueries
        expr: |
          histogram_quantile(0.95,
            sum(rate(db_query_duration_seconds_bucket[5m])) by (le)
          ) > 0.1
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "Database P95 query time exceeds 100ms"
          description: "Current P95 query time: {{ $value }}s"
          runbook: "https://wiki.example.com/runbooks/slow-queries"
```

**Error Tracking Integration**:
```javascript
// Sentry error tracking setup
const Sentry = require('@sentry/node');
const Tracing = require('@sentry/tracing');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Tracing.Integrations.Express({ app }),
  ],
  beforeSend(event, hint) {
    // Filter out sensitive data
    if (event.request) {
      delete event.request.cookies;
      if (event.request.headers) {
        delete event.request.headers['authorization'];
      }
    }
    return event;
  },
});

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());
app.use(Sentry.Handlers.errorHandler());
```

**full-stack-architect** establishes observability architecture:
- Designs logging strategy (structured logging, log aggregation)
- Plans metrics retention and storage strategy
- Establishes distributed tracing architecture
- Designs alerting and on-call workflows

**Deliverable**: Complete observability stack with monitoring, tracing, and alerting

### Phase 7: CI/CD Integration & Documentation
**Duration: 4-8 hours**

**qa-test-engineer** integrates testing into CI/CD:
- Configures automated test execution in pipeline
- Sets up parallel test execution for speed
- Implements quality gates (coverage thresholds, performance SLOs)
- Configures test result reporting and visualization
- Sets up automated test environment provisioning

**full-stack-architect** creates comprehensive documentation:
- API testing guide (how to run tests, add new tests)
- API documentation (OpenAPI/GraphQL schema, examples)
- Architecture diagrams (API structure, dependencies)
- Troubleshooting guide (common issues, debugging strategies)

**security-audit-specialist** documents security practices:
- Security testing procedures
- Vulnerability remediation guide
- Security compliance checklist
- Incident response procedures

**Deliverable**: Fully automated CI/CD pipeline with comprehensive documentation

### Phase 8: Quality Review & Handoff
**Duration: 2-4 hours**

**All agents collaborate** for final review:

**qa-test-engineer** validates:
- Test coverage meets targets (>90% endpoint coverage, >85% critical path coverage)
- All tests passing in CI/CD pipeline
- Performance benchmarks meeting SLOs
- Quality gates properly configured

**full-stack-architect** confirms:
- API contracts validated and documented
- Contract tests passing for all service integrations
- Breaking change detection functional
- Documentation complete and accurate

**security-audit-specialist** verifies:
- OWASP API Top 10 coverage complete
- No critical or high vulnerabilities remaining
- Security monitoring operational
- Compliance requirements satisfied

**Deliverable**: Final quality report with test coverage metrics, performance benchmarks, security assessment, and handoff documentation

## Deliverables

### 1. Comprehensive API Test Suite

**Unit Tests (Endpoint-Level Testing)**:
- Request validation tests for all parameters (path, query, body, headers)
- Response validation tests (status codes, headers, body schema)
- Business logic validation tests
- Error handling and edge case tests
- Boundary value tests
- **Coverage Target**: >95% of endpoints tested

**Integration Tests (Service-Level Testing)**:
- Multi-endpoint workflow tests
- Database integration tests (transactions, constraints, rollbacks)
- External service integration tests (third-party APIs, payment gateways)
- Message queue integration tests (event publishing, consumption)
- Cache integration tests (Redis, Memcached)
- File storage integration tests (S3, GCS, Azure Blob)
- **Coverage Target**: >85% of critical workflows tested

**End-to-End Tests (Business-Level Testing)**:
- Complete user journey tests
- Cross-service transaction tests
- Data consistency validation tests
- Recovery and rollback scenario tests
- **Coverage Target**: >80% of critical business flows tested

**Test Organization**:
```
tests/
├── unit/
│   ├── users/
│   │   ├── create-user.test.js
│   │   ├── get-user.test.js
│   │   ├── update-user.test.js
│   │   └── delete-user.test.js
│   ├── auth/
│   │   ├── login.test.js
│   │   ├── logout.test.js
│   │   └── refresh-token.test.js
│   └── products/
│       └── ...
├── integration/
│   ├── user-workflows.test.js
│   ├── order-processing.test.js
│   ├── payment-integration.test.js
│   └── database-transactions.test.js
├── e2e/
│   ├── user-registration-flow.test.js
│   ├── checkout-flow.test.js
│   └── subscription-flow.test.js
├── security/
│   ├── authentication.test.js
│   ├── authorization.test.js
│   ├── injection-attacks.test.js
│   └── rate-limiting.test.js
├── performance/
│   ├── load-test.js
│   ├── stress-test.js
│   ├── spike-test.js
│   └── soak-test.js
├── contract/
│   ├── pact-consumer.test.js
│   └── pact-provider.test.js
└── fixtures/
    ├── users.json
    ├── products.json
    └── orders.json
```

### 2. OpenAPI/GraphQL Specification

**OpenAPI Specification (REST APIs)**:
```yaml
openapi: 3.0.3
info:
  title: Example API
  version: 1.0.0
  description: Comprehensive API with full testing coverage
  contact:
    name: API Support
    email: api-support@example.com

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

security:
  - bearerAuth: []

paths:
  /users:
    post:
      summary: Create new user
      operationId: createUser
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              validUser:
                value:
                  email: user@example.com
                  name: John Doe
                  role: user
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      required: [id, email, name, role, createdAt]
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
        role:
          type: string
          enum: [user, admin]
        createdAt:
          type: string
          format: date-time
    CreateUserRequest:
      type: object
      required: [email, name]
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
        role:
          type: string
          enum: [user, admin]
          default: user
    Error:
      type: object
      required: [error, message]
      properties:
        error:
          type: string
        message:
          type: string
        details:
          type: object
          additionalProperties: true

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

**GraphQL Schema (GraphQL APIs)**:
```graphql
"""
User type representing a registered user
"""
type User {
  id: ID!
  email: String!
  name: String!
  role: Role!
  createdAt: DateTime!
  updatedAt: DateTime!
}

"""
User role enumeration
"""
enum Role {
  USER
  ADMIN
}

"""
Input for creating a new user
"""
input CreateUserInput {
  email: String!
  name: String!
  role: Role = USER
}

"""
Input for updating an existing user
"""
input UpdateUserInput {
  email: String
  name: String
  role: Role
}

type Query {
  """
  Get user by ID
  Requires authentication
  """
  user(id: ID!): User

  """
  List all users with pagination
  Requires admin role
  """
  users(
    first: Int = 10
    after: String
    filter: UserFilter
  ): UserConnection!
}

type Mutation {
  """
  Create a new user
  Requires authentication
  """
  createUser(input: CreateUserInput!): User!

  """
  Update an existing user
  Requires authentication and ownership or admin role
  """
  updateUser(id: ID!, input: UpdateUserInput!): User!

  """
  Delete a user
  Requires authentication and ownership or admin role
  """
  deleteUser(id: ID!): Boolean!
}

"""
Custom scalar for date-time values
"""
scalar DateTime
```

### 3. Security Assessment Report

**Executive Summary**:
- Overall security posture assessment
- Critical findings requiring immediate attention
- Medium/low priority recommendations
- Compliance status (OWASP API Top 10, industry standards)

**OWASP API Security Top 10 Assessment**:
| Vulnerability | Status | Test Coverage | Findings | Remediation |
|---------------|---------|---------------|----------|-------------|
| API1: Broken Object Level Authorization | PASS | 100% | No issues found | N/A |
| API2: Broken Authentication | PASS | 100% | JWT implementation secure | N/A |
| API3: Broken Object Property Level Authorization | PASS | 100% | Field-level permissions enforced | N/A |
| API4: Unrestricted Resource Consumption | PASS | 100% | Rate limiting implemented | N/A |
| API5: Broken Function Level Authorization | PASS | 100% | RBAC properly enforced | N/A |
| API6: Unrestricted Access to Sensitive Business Flows | PASS | 100% | Anti-automation controls in place | N/A |
| API7: Server Side Request Forgery | PASS | 100% | URL validation implemented | N/A |
| API8: Security Misconfiguration | PASS | 100% | Security headers configured | N/A |
| API9: Improper Inventory Management | PASS | 100% | API documentation complete | N/A |
| API10: Unsafe Consumption of APIs | PASS | 100% | External API validation implemented | N/A |

**Detailed Findings**:
- Authentication vulnerabilities (if any)
- Authorization issues (if any)
- Injection vulnerabilities (if any)
- Data exposure issues (if any)
- Configuration weaknesses (if any)

**Security Testing Evidence**:
- Automated scan results (OWASP ZAP, Burp Suite)
- Manual testing results (authentication bypass attempts, authorization tests)
- Penetration testing results (if conducted)

**Recommendations**:
- Short-term fixes (critical issues)
- Medium-term improvements (security enhancements)
- Long-term strategies (security program maturity)

### 4. Performance Benchmarks & Load Testing Results

**Baseline Performance Metrics**:
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| P50 Latency | <100ms | 78ms | PASS |
| P95 Latency | <200ms | 156ms | PASS |
| P99 Latency | <500ms | 342ms | PASS |
| Throughput (RPS) | >1000 | 1547 | PASS |
| Error Rate | <0.1% | 0.03% | PASS |
| Availability | >99.9% | 99.97% | PASS |

**Load Testing Results**:

**Normal Load (100 concurrent users)**:
- Average response time: 82ms
- Peak response time: 234ms
- Throughput: 1234 RPS
- Error rate: 0.02%
- Duration: 10 minutes

**Peak Load (500 concurrent users)**:
- Average response time: 187ms
- Peak response time: 456ms
- Throughput: 4567 RPS
- Error rate: 0.08%
- Duration: 10 minutes

**Stress Test (1000 concurrent users)**:
- Average response time: 423ms
- Peak response time: 1200ms
- Throughput: 6234 RPS
- Error rate: 0.15%
- Breaking point: 1200 concurrent users

**Spike Test (0 → 500 → 0 users in 1 minute)**:
- Recovery time: 45 seconds
- Error spike: 0.23% during surge
- Auto-scaling triggered: Yes
- Graceful degradation: Yes

**Soak Test (24 hours at 100 concurrent users)**:
- Memory growth: 2.3% over 24 hours
- Performance degradation: <1%
- Connection leaks detected: None
- Errors over time: Stable at 0.02%

**Performance Bottlenecks Identified**:
1. Database query optimization needed for user search endpoint (addressed)
2. N+1 queries in GraphQL resolver for nested data (addressed with DataLoader)
3. Large payload serialization causing high CPU usage (implemented streaming)
4. Cache miss rate higher than expected on product catalog (increased cache TTL)

**Performance Improvement Recommendations**:
- Implement database query result caching for frequently accessed data
- Add CDN for static assets and API responses where appropriate
- Optimize JSON serialization for large payloads
- Consider implementing response compression (gzip/brotli)

### 5. CI/CD Pipeline Integration

**Automated Testing Pipeline**:
```yaml
# Complete CI/CD pipeline with quality gates
name: API Testing Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  COVERAGE_THRESHOLD: 80
  PERFORMANCE_SLO_P95: 200

jobs:
  # Job 1: Code quality and static analysis
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm run security-audit

  # Job 2: Unit and integration tests
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      - run: npm ci
      - run: npm run migrate
      - run: npm run test:unit
      - run: npm run test:integration
      - run: npm run test:coverage
      - name: Check coverage threshold
        run: |
          COVERAGE=$(npx nyc report --reporter=text-summary | grep "Lines" | awk '{print $3}' | tr -d '%')
          if [ "$COVERAGE" -lt "${{ env.COVERAGE_THRESHOLD }}" ]; then
            echo "Coverage $COVERAGE% is below threshold ${{ env.COVERAGE_THRESHOLD }}%"
            exit 1
          fi
      - uses: codecov/codecov-action@v3

  # Job 3: Contract testing
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      - run: npm ci
      - run: npm run test:pact:consumer
      - run: npm run test:pact:provider
      - name: Publish Pact contracts
        run: |
          npx pact-broker publish ./pacts \
            --consumer-app-version=${{ github.sha }} \
            --branch=${{ github.ref_name }} \
            --broker-base-url=${{ secrets.PACT_BROKER_URL }} \
            --broker-token=${{ secrets.PACT_BROKER_TOKEN }}

  # Job 4: Security testing
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm run test:security
      - name: OWASP ZAP API scan
        uses: zaproxy/action-api-scan@v0.4.0
        with:
          target: 'https://staging-api.example.com/openapi.json'
          format: 'openapi'
          fail_action: true
      - name: Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # Job 5: Performance testing (only on main branch)
  performance-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      - name: Run load tests
        run: k6 run --out json=results.json tests/performance/load-test.js
        env:
          API_BASE_URL: https://staging-api.example.com
          API_TOKEN: ${{ secrets.STAGING_API_TOKEN }}
      - name: Validate performance SLOs
        run: |
          P95_LATENCY=$(jq '.metrics.http_req_duration.values["p(95)"]' results.json)
          if (( $(echo "$P95_LATENCY > ${{ env.PERFORMANCE_SLO_P95 }}" | bc -l) )); then
            echo "P95 latency $P95_LATENCY ms exceeds SLO ${{ env.PERFORMANCE_SLO_P95 }} ms"
            exit 1
          fi
      - uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: results.json

  # Job 6: OpenAPI validation
  openapi-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate OpenAPI spec
        uses: char0n/swagger-editor-validate@v1
        with:
          definition-file: docs/openapi.yaml
      - name: Check for breaking changes
        uses: oasdiff/oasdiff-action@v0.0.15
        with:
          base: 'https://api.example.com/openapi.json'
          revision: 'docs/openapi.yaml'
          fail-on-breaking: true

  # Job 7: Quality gate
  quality-gate:
    runs-on: ubuntu-latest
    needs: [code-quality, test, contract-tests, security-tests, openapi-validation]
    steps:
      - run: echo "All quality gates passed"
```

**Quality Gate Configuration**:
- Code coverage: >80% (configurable per project)
- Security vulnerabilities: 0 critical, 0 high
- Performance SLOs: P95 <200ms, P99 <500ms, error rate <0.1%
- Contract tests: All provider/consumer contracts passing
- OpenAPI validation: No breaking changes (for non-major versions)

### 6. API Documentation & Testing Guides

**API Documentation**:
- Complete OpenAPI/GraphQL specification
- Interactive API explorer (Swagger UI, GraphQL Playground)
- Authentication guide (obtaining tokens, using API keys)
- Request/response examples for all endpoints
- Error code reference
- Rate limiting and pagination documentation
- Versioning and deprecation policy

**Testing Guide for Developers**:
```markdown
# API Testing Guide

## Running Tests Locally

### Prerequisites
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

### Setup
```bash
# Install dependencies
npm install

# Start test services
docker-compose up -d postgres redis

# Run database migrations
npm run migrate

# Seed test data
npm run seed:test
```

### Running Tests

**Unit Tests**:
```bash
npm run test:unit
```

**Integration Tests**:
```bash
npm run test:integration
```

**End-to-End Tests**:
```bash
npm run test:e2e
```

**All Tests with Coverage**:
```bash
npm run test:coverage
```

**Security Tests**:
```bash
npm run test:security
```

**Performance Tests**:
```bash
npm run test:performance
```

### Adding New Tests

**Adding Unit Tests**:
1. Create test file in `tests/unit/` matching the endpoint path
2. Follow naming convention: `<operation>-<resource>.test.js`
3. Use `describe` blocks for grouping related tests
4. Use `it` blocks for individual test cases
5. Ensure proper setup/teardown in `beforeEach`/`afterEach`

Example:
```javascript
describe('POST /api/users', () => {
  beforeEach(async () => {
    await db('users').del(); // Clean state
  });

  it('should create user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test User' })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'test@example.com',
      name: 'Test User',
    });
  });
});
```

**Adding Integration Tests**:
1. Create test file in `tests/integration/`
2. Test complete workflows across multiple endpoints
3. Validate database state after operations
4. Test error handling and recovery

**Adding Security Tests**:
1. Create test file in `tests/security/`
2. Test authentication bypass attempts
3. Test authorization violations
4. Test injection vulnerabilities
5. Test rate limiting

### Test Data Management

**Using Fixtures**:
```javascript
const fixtures = require('../fixtures');

beforeEach(async () => {
  await db('users').insert(fixtures.users);
  await db('products').insert(fixtures.products);
});
```

**Creating Test Users**:
```javascript
const { createTestUser } = require('../helpers/auth');

it('should require authentication', async () => {
  const user = await createTestUser({ role: 'admin' });
  const token = await generateToken(user);

  await request(app)
    .get('/api/admin/users')
    .set('Authorization', `Bearer ${token}`)
    .expect(200);
});
```

### Debugging Tests

**Running Single Test File**:
```bash
npm test -- tests/unit/users/create-user.test.js
```

**Running Tests in Watch Mode**:
```bash
npm run test:watch
```

**Debugging with VSCode**:
Add to `.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand", "${file}"],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

### Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Clean State**: Use `beforeEach` to ensure clean database state
3. **Descriptive Names**: Test descriptions should clearly state what is being tested
4. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and validation
5. **Don't Test Implementation**: Test behavior, not internal implementation details
6. **Use Realistic Data**: Test with data that matches production patterns
7. **Test Error Scenarios**: Don't just test happy paths
8. **Mock External Services**: Use mocks for third-party APIs to ensure reliability
```

### 7. Monitoring & Alerting Configuration

**Prometheus Configuration**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts/api-slos.yml'
  - 'alerts/security.yml'

scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api:9090']
    metrics_path: '/metrics'
```

**Grafana Dashboards**:
- API Performance Dashboard (latency, throughput, error rate)
- API Usage Dashboard (endpoint popularity, client distribution)
- API Security Dashboard (failed auth attempts, rate limit violations)
- API Health Dashboard (service health, dependency status, SLO tracking)

**Alerting Rules** (provided in deliverables)

**On-Call Runbooks**:
- High error rate response procedure
- High latency investigation steps
- Security incident response
- Database failover procedure
- Service degradation handling

## Test Coverage Goals

### Functional Coverage Targets

**Endpoint Coverage**: >90%
- All documented endpoints tested
- All HTTP methods tested (GET, POST, PUT, PATCH, DELETE)
- All query parameters tested
- All request body variations tested

**Business Logic Coverage**: >85%
- All critical business workflows tested
- All state transitions validated
- All calculation logic verified
- All validation rules tested

**Error Scenario Coverage**: 100%
- All 4xx client error responses tested
- All 5xx server error responses tested
- All validation error messages tested
- All authentication/authorization errors tested

### Security Coverage Targets

**OWASP API Top 10**: 100% coverage
- All 10 categories tested comprehensively
- Automated security scanning integrated
- Manual security testing for critical flows
- Regular security regression testing

**Authentication Testing**: 100% coverage
- All authentication mechanisms tested
- Token validation tested (expiry, tampering, algorithm confusion)
- Session management tested (fixation, hijacking)
- Multi-factor authentication tested

**Authorization Testing**: 100% coverage
- All permission boundaries tested
- Role-based access control validated
- Object-level authorization tested
- Function-level authorization tested

### Performance Coverage Targets

**Performance SLOs**: 100% validated
- Latency targets measured and validated
- Throughput capacity measured and validated
- Error rate limits validated
- Availability SLOs monitored

**Load Scenarios**: 100% coverage
- Normal load tested
- Peak load tested
- Stress testing conducted
- Spike testing conducted
- Soak testing conducted (24h+)

## Estimated Time

### Small API (<20 endpoints)
**Total: 8-16 hours**
- Discovery & Analysis: 1-2 hours
- Test Framework Setup: 2-3 hours
- Functional Tests: 3-5 hours
- Security Tests: 1-2 hours
- Performance Tests: 1-2 hours
- Documentation: 1-2 hours

### Medium API (20-50 endpoints)
**Total: 24-40 hours**
- Discovery & Analysis: 2-4 hours
- Test Framework Setup: 4-6 hours
- Functional Tests: 10-16 hours
- Security Tests: 3-5 hours
- Performance Tests: 3-5 hours
- Documentation: 2-4 hours

### Large API (50-100 endpoints)
**Total: 48-72 hours**
- Discovery & Analysis: 4-8 hours
- Test Framework Setup: 6-10 hours
- Functional Tests: 20-30 hours
- Security Tests: 6-10 hours
- Performance Tests: 6-10 hours
- Documentation: 6-4 hours

### Microservices Suite (Multiple APIs with dependencies)
**Total: 80-120 hours**
- Discovery & Analysis: 8-12 hours
- Test Framework Setup: 10-15 hours
- Functional Tests: 30-45 hours
- Contract Tests: 10-15 hours
- Security Tests: 10-15 hours
- Performance Tests: 8-12 hours
- Documentation: 4-6 hours

Time estimates include:
- Initial setup and configuration
- Test implementation
- Security testing
- Performance testing
- CI/CD integration
- Documentation

Time estimates assume:
- Clear API specifications available
- Reasonable API complexity
- Standard authentication/authorization patterns
- Existing test infrastructure (CI/CD, test environments)

Additional time may be required for:
- Complex business logic validation
- Custom authentication mechanisms
- Third-party API integration testing
- Complex distributed transaction testing
- Regulatory compliance testing

## Example Usage

```bash
# Full API testing strategy with all dimensions
/api-testing-strategy

# Focus on specific API type
/api-testing-strategy --type=rest
/api-testing-strategy --type=graphql
/api-testing-strategy --type=grpc
/api-testing-strategy --type=websocket

# Security-focused testing for compliance audit
/api-testing-strategy --focus=security

# Performance testing emphasis for scalability planning
/api-testing-strategy --focus=performance

# Contract testing for microservices integration
/api-testing-strategy --focus=contracts

# Quick assessment without full implementation
/api-testing-strategy --mode=assessment

# Include specific endpoints only
/api-testing-strategy --endpoints=/api/users,/api/orders

# Exclude specific tests
/api-testing-strategy --exclude=performance,load

# Fast feedback mode (essential tests only)
/api-testing-strategy --mode=fast

# Comprehensive mode (all tests, all scenarios)
/api-testing-strategy --mode=comprehensive
```

## Related Commands

- **`/security-audit`**: Deep dive security assessment with penetration testing and compliance validation
- **`/performance-audit`**: System-wide performance optimization including database, caching, and infrastructure
- **`/production-readiness`**: Comprehensive pre-deployment checklist covering all production requirements
- **`/architecture-review`**: Architectural assessment of API design, scalability, and maintainability
- **`/testing-strategy`**: Comprehensive testing approach for entire application stack (not just APIs)
- **`/code-quality-review`**: Code quality assessment with focus on maintainability and best practices

## Success Criteria

This API testing strategy is successful when:

1. **Comprehensive Test Coverage**: >90% endpoint coverage, >85% business logic coverage, 100% error scenario coverage
2. **Security Validation**: OWASP API Top 10 fully addressed, zero critical vulnerabilities, security monitoring operational
3. **Performance Validation**: All SLOs met (P95 <200ms, P99 <500ms, availability >99.9%, error rate <0.1%)
4. **Contract Compliance**: OpenAPI/GraphQL schemas validated, contract tests passing, breaking changes detected
5. **CI/CD Integration**: Automated testing in pipeline, quality gates enforced, test results visualized
6. **Documentation Complete**: API documentation comprehensive, testing guide clear, runbooks available
7. **Monitoring Operational**: Metrics collected, alerts configured, dashboards available, SLOs tracked
8. **Team Enablement**: Development team trained on testing practices, testing becomes routine part of workflow

The ultimate measure of success is confidence in API quality at every stage of development, enabling rapid iteration without compromising reliability, security, or performance.
