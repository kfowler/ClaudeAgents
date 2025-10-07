---
name: microservices-architecture
description: "Complete microservices architecture design coordinating project-orchestrator, full-stack-architect, data-engineer, and devops-engineer for distributed system design with service mesh, API gateway, and observability"
agents:
  - project-orchestrator
  - full-stack-architect
  - data-engineer
  - devops-engineer
complexity: high
duration: 8-12 hours
---

# Microservices Architecture Design

**Command:** `/microservices-architecture`
**Agents:** `project-orchestrator`, `full-stack-architect`, `data-engineer`, `devops-engineer`
**Complexity:** High
**Duration:** 8-12 hours

## Overview

Comprehensive microservices architecture design workflow that coordinates four specialized agents to design, implement, and deploy production-ready distributed systems with service mesh, API gateway, event-driven communication, and full observability.

## What This Command Does

This command orchestrates microservices architecture design across 7 phases:

### Phase 1: Service Decomposition & Domain Modeling (1.5-2 hours)
**Lead:** `project-orchestrator`, **Supporting:** `full-stack-architect`

- Analyze monolithic application or new system requirements
- Apply Domain-Driven Design (DDD) principles to identify bounded contexts
- Decompose system into microservices based on business capabilities
- Define service boundaries and responsibilities (single responsibility principle)
- Identify shared services (authentication, logging, notification)
- Map data ownership and service dependencies
- Design service communication patterns (synchronous vs asynchronous)
- Plan service granularity (avoid nano-services and distributed monoliths)

**Deliverables:**
- Service catalog with descriptions and responsibilities
- Bounded context diagram (DDD)
- Service dependency graph
- Data ownership matrix (which service owns which data)
- Communication pattern recommendations (REST, gRPC, message queues)
- Service granularity analysis

### Phase 2: API Gateway & Service Mesh (1-1.5 hours)
**Lead:** `full-stack-architect`, **Supporting:** `devops-engineer`

API Gateway Design:
- Choose API gateway technology (Kong, Ambassador, AWS API Gateway, etc.)
- Design routing rules and path-based routing
- Plan authentication and authorization at gateway
- Configure rate limiting and throttling
- Design request/response transformation
- Plan API versioning strategy
- Configure CORS and security headers

Service Mesh Design:
- Choose service mesh (Istio, Linkerd, Consul Connect)
- Plan service-to-service authentication (mTLS)
- Design traffic management (load balancing, circuit breakers, retries)
- Configure observability (distributed tracing, metrics)
- Plan fault injection for testing
- Design canary deployments and A/B testing

**Deliverables:**
- API gateway configuration (routing, auth, rate limiting)
- Service mesh architecture diagram
- mTLS certificate strategy
- Traffic management policies (circuit breakers, timeouts, retries)
- Observability configuration (tracing, metrics, logs)

### Phase 3: Data Architecture & Event-Driven Design (1.5-2 hours)
**Lead:** `data-engineer`, **Supporting:** `full-stack-architect`

Database Per Service:
- Design database schema for each microservice
- Choose database technology per service (PostgreSQL, MongoDB, Redis, etc.)
- Plan data isolation and ownership
- Design database migration strategy per service
- Plan for eventual consistency across services

Event-Driven Architecture:
- Design event schema and messaging patterns
- Choose message broker (Kafka, RabbitMQ, AWS SQS/SNS, NATS)
- Plan event sourcing and CQRS (if applicable)
- Design saga patterns for distributed transactions
- Plan event versioning and schema evolution
- Configure dead letter queues and retry policies

Data Consistency:
- Design distributed transaction strategies (Saga, 2PC, eventual consistency)
- Plan for data synchronization across services
- Design compensating transactions for rollbacks
- Configure idempotency for event handlers

**Deliverables:**
- Database architecture per service (ERD per microservice)
- Event schema definitions (Avro, Protobuf, JSON Schema)
- Message broker configuration (topics, partitions, retention)
- Saga pattern design for distributed transactions
- Data consistency strategy and trade-offs documentation

### Phase 4: Service Implementation & Communication (1.5-2 hours)
**Lead:** `full-stack-architect`

Synchronous Communication:
- Design REST APIs for each service
- Plan gRPC for high-performance service-to-service calls
- Configure service discovery (Consul, etcd, Kubernetes DNS)
- Design client-side load balancing
- Plan request/response patterns and error handling

Asynchronous Communication:
- Design pub/sub patterns for event-driven flows
- Plan message queue configurations
- Design command and event messages
- Configure consumer groups and partitioning
- Plan for message ordering and delivery guarantees

Service Contracts:
- Design API contracts (OpenAPI 3.0, gRPC proto files)
- Plan contract testing (Pact, Spring Cloud Contract)
- Configure API mocking for development
- Design backwards compatibility strategy
- Plan API deprecation process

**Deliverables:**
- Service API definitions (OpenAPI or gRPC proto)
- Service discovery configuration
- Message schemas and contracts
- Contract testing setup
- Error handling and retry strategies

### Phase 5: Deployment & Orchestration (1-1.5 hours)
**Lead:** `devops-engineer`, **Supporting:** `full-stack-architect`

Container Orchestration:
- Design Kubernetes deployment manifests
- Configure Deployments, Services, ConfigMaps, Secrets
- Plan resource limits and requests per service
- Design horizontal pod autoscaling (HPA)
- Configure health checks (liveness, readiness, startup probes)
- Plan rolling updates and rollback strategies

CI/CD Pipeline:
- Design multi-repo or mono-repo strategy
- Configure automated builds per service
- Plan Docker image building and registry
- Design deployment pipeline (build, test, deploy)
- Configure automated testing (unit, integration, E2E)
- Plan blue-green or canary deployments

Infrastructure as Code:
- Design Terraform or Helm charts
- Configure environment-specific configurations
- Plan secrets management (HashiCorp Vault, AWS Secrets Manager)
- Design network policies and service mesh integration

**Deliverables:**
- Kubernetes manifests per service
- CI/CD pipeline configuration (GitHub Actions, GitLab CI, Jenkins)
- Docker image build strategy
- Helm charts or Kustomize configurations
- Secrets management plan

### Phase 6: Observability & Monitoring (1-1.5 hours)
**Lead:** `devops-engineer`

Distributed Tracing:
- Configure distributed tracing (Jaeger, Zipkin, AWS X-Ray)
- Plan trace sampling strategies
- Design trace context propagation
- Configure service performance monitoring

Metrics & Monitoring:
- Design metrics collection (Prometheus, Grafana)
- Configure service-level metrics (request rate, latency, error rate)
- Design RED metrics (Rate, Errors, Duration) dashboards
- Plan alerting rules and thresholds
- Configure anomaly detection

Logging:
- Design centralized logging (ELK, Loki, CloudWatch Logs)
- Plan structured logging format (JSON)
- Configure log aggregation and correlation
- Design log retention policies
- Plan log-based alerting

SLOs and Error Budgets:
- Define Service Level Objectives (SLOs) per service
- Calculate error budgets
- Design SLO-based alerting
- Plan incident response based on error budget burn rate

**Deliverables:**
- Distributed tracing configuration
- Prometheus metrics and Grafana dashboards
- Centralized logging setup
- SLO definitions and error budgets
- Alerting rules and on-call rotation

### Phase 7: Security & Resilience (1-1.5 hours)
**Lead:** `full-stack-architect`, **Supporting:** `devops-engineer`

Security:
- Design zero-trust security model
- Configure mTLS for service-to-service communication
- Plan OAuth2/OIDC for user authentication
- Design RBAC for service authorization
- Configure network policies (egress/ingress rules)
- Plan secrets rotation and management
- Design API security (rate limiting, input validation, OWASP)

Resilience Patterns:
- Configure circuit breakers (prevent cascading failures)
- Design retry policies with exponential backoff
- Plan bulkheads for resource isolation
- Configure timeouts for all service calls
- Design fallback strategies (cached data, default responses)
- Plan chaos engineering experiments (chaos monkey)

Disaster Recovery:
- Design multi-region deployment strategy
- Plan database backup and restore procedures
- Configure automated failover
- Design data replication across regions
- Plan for disaster recovery drills

**Deliverables:**
- Security architecture (zero-trust, mTLS, OAuth2)
- Resilience patterns implementation (circuit breakers, retries, bulkheads)
- Network policies and firewall rules
- Disaster recovery runbook
- Chaos engineering test plan

## Expected Outcomes

### Architecture Artifacts
- **Service catalog** with 10-50 microservices (depends on complexity)
- **Service dependency graph** visualizing inter-service communication
- **API gateway configuration** with routing, auth, rate limiting
- **Service mesh setup** (Istio, Linkerd) with mTLS and observability
- **Event-driven architecture** with message broker and saga patterns
- **Kubernetes manifests** for all services with HPA and health checks
- **CI/CD pipelines** for automated deployment
- **Observability stack** (tracing, metrics, logging, alerting)
- **Security architecture** (zero-trust, mTLS, RBAC)

### Design Quality
- **Loosely coupled services** with clear boundaries (DDD bounded contexts)
- **High cohesion** within services (business capabilities aligned)
- **Resilient architecture** (circuit breakers, retries, fallbacks)
- **Observable system** (distributed tracing, metrics, logs)
- **Secure by design** (mTLS, zero-trust, RBAC)
- **Scalable architecture** (horizontal scaling, auto-scaling)
- **Eventual consistency** handled gracefully (Saga patterns, idempotency)

### Business Value
- **Independent deployments** (deploy services independently, faster releases)
- **Technology diversity** (choose best tech for each service)
- **Team autonomy** (teams own services end-to-end)
- **Fault isolation** (service failures don't cascade)
- **Scalability** (scale services independently based on load)
- **Faster time-to-market** (parallel development, smaller deployments)

## Usage

```bash
# Design microservices for e-commerce platform
/microservices-architecture --domain=ecommerce --services=15

# Design event-driven microservices for IoT platform
/microservices-architecture --domain=iot --event-driven=true

# Design microservices with service mesh
/microservices-architecture --service-mesh=istio --gateway=kong

# Migrate monolith to microservices
/microservices-architecture --migration=strangler-fig --monolith=existing-app
```

## Prerequisites

- [ ] Business requirements defined (features, capabilities)
- [ ] Monolith application analyzed (if migrating)
- [ ] Technology stack preferences (language, frameworks, cloud provider)
- [ ] Team structure known (number of teams, ownership model)
- [ ] Performance requirements (SLA, expected load, scalability needs)
- [ ] Compliance requirements (data residency, security standards)
- [ ] Budget constraints (infrastructure costs, operational costs)

## Success Criteria

### Service Decomposition
- [ ] Services aligned with business capabilities (DDD bounded contexts)
- [ ] Clear service boundaries and data ownership
- [ ] Minimal inter-service dependencies (loose coupling)
- [ ] Shared services identified (auth, logging, notification)
- [ ] Service granularity appropriate (not too fine, not too coarse)

### API Gateway & Service Mesh
- [ ] API gateway configured (routing, auth, rate limiting)
- [ ] Service mesh deployed (Istio, Linkerd, or equivalent)
- [ ] mTLS enabled for service-to-service communication
- [ ] Traffic management policies configured (circuit breakers, retries)
- [ ] Observability integrated (tracing, metrics, logs)

### Data Architecture
- [ ] Database per service pattern implemented
- [ ] Event-driven architecture designed (message broker, events)
- [ ] Saga patterns for distributed transactions
- [ ] Idempotency for event handlers
- [ ] Data consistency strategy documented

### Deployment & Orchestration
- [ ] Kubernetes manifests for all services
- [ ] CI/CD pipelines automated (build, test, deploy)
- [ ] Auto-scaling configured (HPA, custom metrics)
- [ ] Rolling updates and rollback tested
- [ ] Infrastructure as Code (Terraform, Helm)

### Observability
- [ ] Distributed tracing enabled (Jaeger, Zipkin)
- [ ] Metrics dashboards created (Grafana, RED metrics)
- [ ] Centralized logging configured (ELK, Loki)
- [ ] SLOs and error budgets defined
- [ ] Alerting rules configured (on-call rotation)

### Security & Resilience
- [ ] Zero-trust security model implemented
- [ ] Resilience patterns configured (circuit breakers, retries, bulkheads)
- [ ] Chaos engineering tests planned
- [ ] Disaster recovery runbook created
- [ ] Multi-region deployment (if required)

## Real-World Example: E-commerce Microservices

**Design Time:** 10 hours
**Team:** 4 engineers (project-orchestrator, full-stack-architect, data-engineer, devops-engineer)

**Services Designed (15 microservices):**
1. **User Service**: User registration, authentication (PostgreSQL)
2. **Product Catalog**: Product management, search (PostgreSQL + Elasticsearch)
3. **Inventory Service**: Stock management, availability (PostgreSQL)
4. **Shopping Cart**: Cart operations (Redis + PostgreSQL)
5. **Order Service**: Order creation, management (PostgreSQL)
6. **Payment Service**: Payment processing (PostgreSQL, Stripe integration)
7. **Shipping Service**: Shipping calculation, tracking (PostgreSQL)
8. **Notification Service**: Email, SMS, push notifications (Kafka consumer)
9. **Recommendation Service**: Product recommendations (PostgreSQL + ML model)
10. **Review Service**: Product reviews, ratings (PostgreSQL)
11. **Search Service**: Full-text search, faceted search (Elasticsearch)
12. **Analytics Service**: Real-time analytics, reporting (ClickHouse)
13. **Image Service**: Image upload, optimization (S3 + CDN)
14. **Auth Service**: OAuth2, JWT tokens (Redis + PostgreSQL)
15. **Gateway Service**: API Gateway (Kong)

**Architecture Components:**
- **API Gateway**: Kong (routing, auth, rate limiting)
- **Service Mesh**: Istio (mTLS, observability, traffic management)
- **Message Broker**: Apache Kafka (order events, inventory updates, notifications)
- **Service Discovery**: Kubernetes DNS
- **Container Orchestration**: Kubernetes (GKE)
- **CI/CD**: GitHub Actions (automated deployment)
- **Observability**: Jaeger (tracing) + Prometheus/Grafana (metrics) + ELK (logs)

**Event-Driven Flows:**
- **Order Creation Saga**: Order Service → Payment Service → Inventory Service → Shipping Service → Notification Service
- **Inventory Updates**: Product Catalog publishes inventory events → Inventory Service consumes → Shopping Cart invalidates cache
- **Recommendation Updates**: User behavior events → Recommendation Service (ML model retraining)

**Delivered:**
- 15 microservices with clear bounded contexts
- API gateway with 50+ routes configured
- Istio service mesh with mTLS and circuit breakers
- 12 Kafka topics for event-driven communication
- Saga pattern for order processing (5 services)
- Kubernetes manifests for all 15 services
- CI/CD pipelines (automated deployment to staging/production)
- Distributed tracing across all services
- SLOs: 99.9% uptime, p95 latency <200ms

**Impact:**
- **Deployment frequency**: 5 deployments/day (vs 1/week monolith)
- **Scalability**: Scaled Product Catalog 10x during Black Friday (other services stable)
- **Fault isolation**: Payment service outage didn't affect browsing/cart
- **Team autonomy**: 5 teams owning services independently
- **Performance**: p95 latency 120ms (vs 450ms monolith)
- **Availability**: 99.95% uptime (vs 99.5% monolith)
- **Time-to-market**: New features deployed in days (vs weeks)

**Technical Highlights:**
- Strangler Fig pattern for gradual monolith migration (6 months)
- Database per service (PostgreSQL, MongoDB, Redis, Elasticsearch, ClickHouse)
- Event sourcing for Order Service (audit trail, replay capabilities)
- CQRS for Analytics Service (optimized read models)
- Chaos engineering (monthly chaos monkey tests, 99.95% resilience maintained)

## Related Commands

- `/api-design` - Design individual microservice APIs
- `/database-design` - Design database schema per service
- `/quality:architecture-review` - Review microservices architecture
- `/devops-setup` - Infrastructure and CI/CD setup
- `/security-audit` - Security review of microservices

## Notes

**When to Use Microservices:**
- Large, complex applications with multiple teams
- Need for independent deployments and scaling
- Different technology requirements per component
- Fault isolation critical (failure of one part doesn't bring down system)

**When NOT to Use Microservices:**
- Small applications or MVPs (monolith is simpler)
- Single team (coordination overhead outweighs benefits)
- Tight coupling between components (distributed monolith)
- Latency-critical applications (network hops add latency)

**Service Granularity:**
- **Too fine (nano-services)**: Excessive network calls, hard to manage
- **Too coarse (distributed monolith)**: Tight coupling, no benefits
- **Right size**: Aligned with business capabilities, team can own end-to-end

**Migration Strategies:**
- **Strangler Fig**: Gradually replace monolith components (recommended, low risk)
- **Big Bang**: Rewrite entire system (high risk, not recommended)
- **Branch by Abstraction**: Create abstraction, swap implementations

**Data Consistency:**
- **Strong consistency**: Use distributed transactions (2PC, slow, not scalable)
- **Eventual consistency**: Use Saga pattern (recommended, scalable, requires design)
- **Trade-off**: CAP theorem (Consistency, Availability, Partition tolerance - pick 2)

**Observability is Critical:**
- Distributed systems are hard to debug without tracing
- Correlate logs across services (trace ID propagation)
- Monitor golden signals: Latency, Traffic, Errors, Saturation

This workflow ensures microservices are well-architected, resilient, observable, and deliver business value while avoiding common pitfalls of distributed systems.
