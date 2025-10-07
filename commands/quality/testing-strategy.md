---
name: testing-strategy
description: "Comprehensive testing strategy design coordinating qa-test-engineer, full-stack-architect, and security-audit-specialist for complete test coverage including unit, integration, E2E, performance, and security testing"
agents:
  - qa-test-engineer
  - full-stack-architect
  - security-audit-specialist
complexity: medium-high
duration: 4-6 hours
---

# Testing Strategy Design

**Command:** `/testing-strategy`
**Agents:** `qa-test-engineer`, `full-stack-architect`, `security-audit-specialist`
**Complexity:** Medium-High
**Duration:** 4-6 hours

## Overview

Comprehensive testing strategy that coordinates QA engineering, architecture, and security expertise to design complete test coverage across unit tests, integration tests, end-to-end tests, performance tests, and security tests with CI/CD integration.

## What This Command Does

This command orchestrates testing strategy design across 6 phases:

### Phase 1: Test Requirements & Coverage Goals (45-60 min)
**Lead:** `qa-test-engineer`

- Analyze application architecture and critical paths
- Define test coverage goals (unit, integration, E2E)
- Identify high-risk areas requiring extensive testing
- Plan test pyramid distribution (70% unit, 20% integration, 10% E2E)
- Define acceptance criteria for test coverage
- Establish quality gates for CI/CD pipeline

**Deliverables:**
- Test requirements document
- Coverage goals by layer (unit: 80%, integration: 70%, E2E: critical paths)
- Risk assessment matrix (critical vs non-critical features)
- Test pyramid strategy
- Quality gates definition (coverage %, pass rate, performance thresholds)

### Phase 2: Unit Testing Strategy (1-1.5 hours)
**Lead:** `qa-test-engineer`, **Supporting:** `full-stack-architect`

- Design unit test framework selection (Jest, PyTest, JUnit, Go test, etc.)
- Plan test isolation strategies (mocking, stubbing, fakes)
- Define naming conventions and test organization
- Design test data factories and fixtures
- Plan code coverage measurement (Istanbul, Coverage.py, JaCoCo)
- Configure mutation testing (Stryker, mutmut)

**Deliverables:**
- Unit test framework configuration
- Mocking strategy (mock external dependencies, databases, APIs)
- Test organization structure (co-located vs separate test folders)
- Test data fixtures and factories
- Code coverage configuration (target: 80% line coverage, 70% branch coverage)
- Mutation testing setup (validate test quality)

### Phase 3: Integration Testing Strategy (1-1.5 hours)
**Lead:** `qa-test-engineer`, **Supporting:** `full-stack-architect`

- Design integration test scope (API, database, external services)
- Plan test database strategy (in-memory, Docker containers, dedicated test DB)
- Configure API integration tests (REST, GraphQL)
- Design service integration tests (microservices communication)
- Plan external service mocking (WireMock, MockServer, VCR)
- Configure test data management and cleanup

**Deliverables:**
- Integration test framework (Postman/Newman, REST Assured, SuperTest)
- Test database configuration (TestContainers, in-memory H2/SQLite)
- API contract testing (Pact, Spring Cloud Contract)
- Service integration test suite
- External service mocking strategy
- Test data seeding and teardown scripts

### Phase 4: End-to-End Testing Strategy (1-1.5 hours)
**Lead:** `qa-test-engineer`

- Design E2E test framework (Playwright, Cypress, Selenium, TestCafe)
- Plan critical user journey tests (registration, checkout, etc.)
- Configure cross-browser testing (Chrome, Firefox, Safari, Edge)
- Design mobile E2E testing (Appium, Detox)
- Plan visual regression testing (Percy, Chromatic, BackstopJS)
- Configure test environment management (staging, pre-prod)

**Deliverables:**
- E2E test framework configuration
- Critical user journey test cases (10-20 scenarios)
- Cross-browser test matrix
- Mobile E2E test setup (if applicable)
- Visual regression testing configuration
- Test environment provisioning scripts

### Phase 5: Performance & Security Testing (1-1.5 hours)
**Lead:** `qa-test-engineer`, **Supporting:** `security-audit-specialist`

Performance Testing:
- Design load testing strategy (k6, JMeter, Gatling)
- Plan stress testing and spike testing
- Configure performance benchmarks (response time, throughput)
- Design scalability testing (vertical, horizontal)
- Plan performance regression testing in CI/CD

Security Testing:
- Design security test automation (OWASP ZAP, Burp Suite)
- Plan dependency vulnerability scanning (Snyk, npm audit, OWASP Dependency-Check)
- Configure SAST (static analysis) tools (SonarQube, Semgrep)
- Design penetration testing schedule (quarterly, after major changes)
- Plan security regression testing

**Deliverables:**
- Load test scenarios and scripts (k6, JMeter)
- Performance benchmarks (p95 <200ms, throughput >1000 req/s)
- Security test automation (OWASP ZAP in CI/CD)
- Dependency scanning configuration (daily/weekly scans)
- SAST tool integration (SonarQube quality gates)
- Penetration testing schedule and scope

### Phase 6: CI/CD Integration & Test Automation (45-60 min)
**Lead:** `qa-test-engineer`, **Supporting:** `full-stack-architect`

- Design test execution pipeline (unit → integration → E2E)
- Configure parallel test execution for speed
- Plan test result reporting (Allure, ReportPortal, Codecov)
- Design test failure analysis and flaky test detection
- Configure automated test maintenance (self-healing tests)
- Plan test coverage trends and quality metrics

**Deliverables:**
- CI/CD test pipeline configuration (GitHub Actions, GitLab CI, Jenkins)
- Parallel test execution setup (reduce build time 50-70%)
- Test reporting dashboards (Allure, custom dashboards)
- Flaky test detection and quarantine
- Test coverage trends visualization
- Quality metrics and KPIs (test pass rate, coverage %, build time)

## Expected Outcomes

### Test Coverage
- **Unit Tests:** 80%+ line coverage, 70%+ branch coverage
- **Integration Tests:** 70%+ API endpoint coverage, all critical paths
- **E2E Tests:** 100% critical user journey coverage (10-20 scenarios)
- **Performance Tests:** Load, stress, spike testing automated
- **Security Tests:** SAST, dependency scanning, automated pen testing

### Test Quality
- **Fast feedback:** Unit tests <5min, integration tests <15min, E2E <30min
- **Reliable tests:** <2% flaky test rate
- **Maintainable tests:** Clear naming, DRY principles, page object pattern
- **Comprehensive:** Test pyramid followed (70/20/10 distribution)
- **Automated:** 95%+ of tests in CI/CD pipeline

### Business Value
- **Faster releases:** Confident deployments with comprehensive test coverage
- **Fewer bugs:** 60-80% reduction in production bugs
- **Faster debugging:** Clear test failures pinpoint issues quickly
- **Quality assurance:** Automated quality gates prevent regressions
- **Developer productivity:** Fast, reliable tests enable TDD/BDD

## Usage

```bash
# Design complete testing strategy
/testing-strategy

# Focus on specific test types
/testing-strategy --focus=e2e,performance

# For microservices architecture
/testing-strategy --architecture=microservices

# Include mobile testing
/testing-strategy --mobile=true
```

## Prerequisites

- [ ] Application architecture documented (frontend, backend, database)
- [ ] Critical user journeys defined
- [ ] Technology stack selected (languages, frameworks)
- [ ] CI/CD pipeline in place (GitHub Actions, GitLab CI, Jenkins)
- [ ] Test environments available (staging, pre-prod)
- [ ] Performance requirements known (SLA, expected load)

## Success Criteria

### Unit Testing
- [ ] Unit test framework configured (Jest, PyTest, JUnit, etc.)
- [ ] 80%+ line coverage, 70%+ branch coverage
- [ ] Mocking strategy defined and implemented
- [ ] Tests run in <5 minutes
- [ ] Mutation testing configured (validate test quality)

### Integration Testing
- [ ] Integration test framework configured
- [ ] API contract tests automated (Pact, Spring Cloud Contract)
- [ ] Database tests with TestContainers or in-memory DB
- [ ] External service mocking (WireMock, MockServer)
- [ ] Tests run in <15 minutes

### End-to-End Testing
- [ ] E2E framework configured (Playwright, Cypress)
- [ ] Critical user journeys automated (10-20 scenarios)
- [ ] Cross-browser testing configured
- [ ] Visual regression tests automated
- [ ] Tests run in <30 minutes

### Performance & Security
- [ ] Load testing automated (k6, JMeter, Gatling)
- [ ] Performance benchmarks defined (p95, throughput)
- [ ] Security scanning automated (OWASP ZAP, Snyk)
- [ ] SAST integrated in CI/CD (SonarQube)
- [ ] Penetration testing scheduled

### CI/CD Integration
- [ ] All tests automated in pipeline
- [ ] Parallel execution configured
- [ ] Test reports generated (Allure, Codecov)
- [ ] Flaky test detection implemented
- [ ] Quality gates enforced (coverage %, pass rate)

## Real-World Example: E-commerce Testing Strategy

**Design Time:** 5 hours
**Team:** 3 engineers (qa-test-engineer, full-stack-architect, security-audit-specialist)

### Unit Tests (80% coverage)
- **Framework:** Jest (frontend), PyTest (backend)
- **Tests:** 1,200 unit tests across 150 modules
- **Coverage:** 82% line coverage, 74% branch coverage
- **Execution:** 4 minutes (parallel execution)
- **Mocking:** API clients, database, payment gateway, email service

### Integration Tests (70% coverage)
- **Framework:** SuperTest (API), TestContainers (database)
- **Tests:** 450 integration tests covering 95% of API endpoints
- **Execution:** 12 minutes (parallel execution, Docker containers)
- **Contract Tests:** Pact for microservices communication (5 services)
- **Database:** PostgreSQL in Docker, seeded test data, automatic cleanup

### E2E Tests (Critical Paths)
- **Framework:** Playwright (cross-browser E2E)
- **Tests:** 25 critical user journey tests
  - User registration and login
  - Product search and filtering
  - Add to cart and checkout
  - Payment processing (Stripe test mode)
  - Order confirmation and tracking
- **Execution:** 28 minutes (parallel across 4 browsers)
- **Visual Regression:** Percy for visual testing (10 critical pages)

### Performance Tests
- **Framework:** k6 for load testing
- **Scenarios:**
  - Load test: 1,000 concurrent users (sustained 10 min)
  - Stress test: Gradual ramp to breaking point
  - Spike test: Sudden 5x traffic increase
- **Benchmarks:** p95 <200ms, throughput >1,500 req/s, error rate <0.5%
- **Execution:** Daily automated tests, weekly full suite

### Security Tests
- **SAST:** SonarQube (quality gates: 0 critical issues, coverage >80%)
- **Dependency Scanning:** Snyk (daily scans, auto-PR for critical vulns)
- **DAST:** OWASP ZAP automated scans in CI/CD
- **Penetration Testing:** Quarterly third-party pen tests
- **Compliance:** PCI DSS Level 1 achieved through automated testing

### CI/CD Integration
- **Pipeline:** GitHub Actions (matrix strategy for parallel execution)
- **Stages:**
  1. Lint & Format (2 min)
  2. Unit Tests (4 min, parallel)
  3. Integration Tests (12 min, parallel)
  4. E2E Tests (28 min, parallel, 4 browsers)
  5. Performance Tests (5 min, smoke tests)
  6. Security Scans (8 min, SAST + dependency check)
- **Total Build Time:** 35 minutes (vs 90 min sequential)
- **Test Reports:** Allure reports, Codecov integration, Slack notifications

### Impact
- **Production Bugs:** 75% reduction (from 20/month → 5/month)
- **Deployment Confidence:** 98% (vs 60% before comprehensive testing)
- **Mean Time to Detection (MTTD):** 15 minutes (vs 4 hours)
- **Mean Time to Resolution (MTTR):** 45 minutes (vs 6 hours)
- **Test Execution Speed:** 35 min builds (vs 90 min sequential)
- **Developer Productivity:** +40% (fast, reliable tests enable TDD)

## Related Commands

- `/code-quality-review` - Code quality and maintainability assessment
- `/security-audit` - Security vulnerability review
- `/quality:performance-audit` - Performance assessment
- `/api-design` - API design (informs integration testing)

## Notes

**Test Pyramid (70/20/10):**
- 70% Unit Tests: Fast, isolated, test business logic
- 20% Integration Tests: Test component interactions
- 10% E2E Tests: Test critical user journeys

**When to Deviate from Pyramid:**
- Legacy codebases: May need more integration tests initially
- Microservices: Increased integration/contract testing
- Frontend-heavy apps: More E2E tests for UI interactions

**Flaky Test Management:**
- Quarantine flaky tests (don't block CI/CD)
- Root cause analysis (timing issues, test data, race conditions)
- Self-healing tests (auto-retry with exponential backoff)
- Regular flaky test review and fixing

**Performance Testing Strategies:**
- **Load Testing:** Sustained expected traffic (validate SLA)
- **Stress Testing:** Gradual increase to breaking point (find limits)
- **Spike Testing:** Sudden traffic spike (validate auto-scaling)
- **Soak Testing:** Sustained load for hours (detect memory leaks)

**Security Testing Layers:**
- **SAST (Static):** Analyze code for vulnerabilities (SonarQube, Semgrep)
- **DAST (Dynamic):** Scan running application (OWASP ZAP, Burp Suite)
- **Dependency Scanning:** Known vulnerabilities in dependencies (Snyk, npm audit)
- **Penetration Testing:** Manual testing by security experts (quarterly)

**Test Maintenance:**
- Page Object Pattern for E2E tests (reduce duplication)
- Shared test utilities and helpers
- Regular test review and refactoring
- Delete obsolete tests (don't accumulate dead tests)

This workflow ensures comprehensive test coverage with fast, reliable, maintainable tests that provide confidence for continuous deployment.
