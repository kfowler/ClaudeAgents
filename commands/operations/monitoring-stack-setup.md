---
name: monitoring-stack-setup
description: "Complete observability implementation coordinating observability-engineer, site-reliability-engineer, and devops-engineer to deliver production-grade logs, metrics, traces, and alerts with 360-degree system visibility"
agents:
  - observability-engineer
  - site-reliability-engineer
  - devops-engineer
complexity: high
duration: 12-20 hours (initial setup), continuous refinement
---

# Monitoring Stack Setup Workflow

**Command:** `/operations:monitoring-stack-setup`
**Agents:** `observability-engineer`, `site-reliability-engineer`, `devops-engineer`
**Complexity:** High
**Duration:** 12-20 hours (initial setup), continuous refinement

## Overview

Comprehensive observability implementation that establishes production-grade monitoring infrastructure with the "three pillars of observability" - logs, metrics, and distributed traces - plus intelligent alerting and visualization. This workflow transforms blind production deployments into fully observable systems where teams can detect, diagnose, and resolve issues 5-10x faster with complete visibility into system behavior, performance, and health.

## What This Command Does

This command orchestrates the implementation of enterprise-grade monitoring infrastructure across 5 phases, delivering complete system observability that reduces Mean Time to Detection (MTTD) by 70-90%, Mean Time to Resolution (MTTR) by 50-75%, and eliminates monitoring blind spots that cause production incidents to go undetected.

### Phase 1: Observability Strategy and Architecture Design (2-3 hours)
**Lead:** `observability-engineer`

Define comprehensive observability strategy aligned with system architecture and operational needs:

- **Observability Stack Selection**: Choose optimal technology stack
  - **Log Aggregation**: ELK Stack (Elasticsearch, Logstash, Kibana), Grafana Loki, Splunk, CloudWatch Logs, Datadog Logs
  - **Metrics Collection**: Prometheus + Grafana, Datadog, New Relic, CloudWatch Metrics, InfluxDB + Telegraf
  - **Distributed Tracing**: Jaeger, Zipkin, Tempo, AWS X-Ray, Datadog APM, New Relic APM
  - **Alert Management**: PagerDuty, Opsgenie, VictorOps, Alertmanager, CloudWatch Alarms
  - **Unified Platforms**: Datadog (all-in-one), New Relic (full-stack), Grafana Cloud (LGTM stack)

- **Architecture Decision Criteria**: Select based on requirements
  - **Cost Model**: Open-source (self-hosted) vs. commercial SaaS vs. cloud-native
  - **Scale Requirements**: Data volume, retention period, query performance needs
  - **Integration Ecosystem**: Existing tooling, cloud provider, application frameworks
  - **Team Expertise**: Learning curve, operational overhead, support requirements
  - **Compliance Needs**: Data residency, retention policies, audit requirements

- **Data Collection Strategy**: Instrumentation approach
  - **Application Metrics**: RED metrics (Rate, Errors, Duration) for services
  - **Infrastructure Metrics**: USE metrics (Utilization, Saturation, Errors) for resources
  - **Business Metrics**: User actions, revenue events, conversion funnels
  - **Custom Metrics**: Domain-specific KPIs and performance indicators
  - **Cardinality Management**: Avoid metric explosion, label strategy

- **Data Retention and Storage**: Balance cost with visibility needs
  - **Hot Storage**: Recent data (7-30 days) for fast queries and real-time dashboards
  - **Warm Storage**: Medium-term data (30-90 days) for trend analysis
  - **Cold Storage**: Long-term data (90+ days) for compliance and historical analysis
  - **Downsampling Strategy**: Reduce granularity for older data to save costs
  - **Cost Optimization**: Tiered storage, data lifecycle policies, intelligent sampling

- **Observability Maturity Roadmap**: Phased implementation approach
  - **Phase 1 (MVP)**: Critical service monitoring, basic alerts, core dashboards (Week 1-2)
  - **Phase 2 (Production)**: Full service coverage, distributed tracing, SLI/SLO tracking (Week 3-4)
  - **Phase 3 (Advanced)**: Anomaly detection, predictive alerting, custom analytics (Month 2-3)
  - **Phase 4 (Excellence)**: AI-powered insights, auto-remediation, chaos engineering integration (Month 4+)

**Deliverables:**
- **Observability Architecture Document** (15-25 pages)
  - Technology stack selection with rationale and trade-off analysis
  - System architecture diagrams (data flow, component topology)
  - Cost projection model (initial setup + monthly operational costs)
  - Implementation roadmap with milestones and success criteria
  - Team training and onboarding plan
- **Technology Comparison Matrix** (open-source vs. commercial vs. cloud-native)
- **Proof of Concept Results** (performance benchmarks, integration testing)
- **Executive Summary** (strategic value, ROI projection, resource requirements)

### Phase 2: Metrics Collection Infrastructure (3-4 hours)
**Lead:** `site-reliability-engineer`

Implement comprehensive metrics collection for system and application monitoring:

- **Application Instrumentation**: Expose service-level metrics
  - **RED Metrics for Services**:
    - **Rate**: Requests per second (overall, per endpoint, per customer)
    - **Errors**: Error rate and count (by type, endpoint, severity)
    - **Duration**: Response time percentiles (p50, p95, p99, p99.9)
  - **Framework Integration**:
    - Node.js: `prom-client`, `express-prom-bundle`
    - Python: `prometheus_client`, `opentelemetry-instrumentation`
    - Java: Micrometer, Dropwizard Metrics, OpenTelemetry
    - Go: `prometheus/client_golang`, OpenTelemetry Go
    - .NET: `prometheus-net`, Application Insights
  - **Custom Metrics**: Business-critical KPIs and domain events
    - User signups, logins, feature usage
    - Payment processing, order completion, subscription changes
    - Search queries, recommendations, content views

- **Infrastructure Metrics Collection**: Monitor resource utilization
  - **USE Metrics for Resources**:
    - **Utilization**: CPU, memory, disk, network usage percentages
    - **Saturation**: Queue lengths, thread pool sizes, connection pool usage
    - **Errors**: Failed requests, timeouts, connection errors
  - **System Metrics**:
    - Node Exporter (Prometheus): CPU, memory, disk, network for Linux/Unix
    - Windows Exporter: Windows server metrics
    - cAdvisor: Container resource usage (Docker, Kubernetes)
    - kube-state-metrics: Kubernetes cluster state metrics
  - **Database Metrics**:
    - PostgreSQL: `postgres_exporter`, query performance, connection pools
    - MySQL: `mysqld_exporter`, slow queries, replication lag
    - MongoDB: MongoDB exporter, operations, connections, cache hit ratio
    - Redis: `redis_exporter`, memory usage, key eviction, command stats
  - **Cloud Provider Metrics**:
    - AWS CloudWatch: EC2, RDS, Lambda, ELB, S3, DynamoDB
    - GCP Monitoring: GCE, Cloud SQL, GKE, Cloud Functions
    - Azure Monitor: VMs, SQL Database, AKS, App Service

- **Metrics Storage and Querying**: Centralized metrics database
  - **Prometheus Setup**:
    - Prometheus server deployment (HA mode for production)
    - Service discovery (Kubernetes, Consul, static configs)
    - Remote write to long-term storage (Thanos, Cortex, Mimir)
    - PromQL query optimization and best practices
  - **Time-Series Database Alternatives**:
    - InfluxDB: High-cardinality data, InfluxQL/Flux queries
    - VictoriaMetrics: Prometheus-compatible, cost-effective, high-performance
    - TimescaleDB: PostgreSQL extension, SQL queries, relational joins
  - **SaaS Metrics Platforms**:
    - Datadog: Unified metrics, APM, logs, traces
    - New Relic: Full-stack observability, AI-powered insights
    - Grafana Cloud: Managed Prometheus, Loki, Tempo

- **Metrics Best Practices**: Ensure data quality and performance
  - **Cardinality Control**: Limit unique label combinations to prevent metric explosion
  - **Label Design**: Consistent naming, avoid high-cardinality labels (user IDs, request IDs)
  - **Sampling Strategy**: Sample high-volume metrics intelligently (exemplars, histogram buckets)
  - **Metric Naming**: Follow conventions (prometheus: `app_http_requests_total`, statsd: `app.http.requests`)

**Deliverables:**
- **Metrics Infrastructure** (fully operational, production-ready)
  - Application instrumentation across all services (95%+ coverage)
  - Infrastructure metrics collection (100% of production hosts/containers)
  - Database and dependency monitoring (all critical datastores)
  - Metrics retention: 30 days hot, 90 days warm, 1 year cold
- **Metrics Catalog** (documentation of all metrics)
  - 200-500 metrics documented with descriptions, labels, units, thresholds
  - Service-level metrics inventory per service
  - Infrastructure metrics reference guide
  - Custom business metrics glossary
- **Query Library** (common PromQL/Flux queries for dashboards and alerts)
- **Performance Report** (ingestion rate, query performance, storage costs)

### Phase 3: Log Aggregation and Analysis (3-4 hours)
**Lead:** `observability-engineer`

Implement centralized logging for debugging, auditing, and troubleshooting:

- **Structured Logging Implementation**: Transition from text to structured logs
  - **Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL/CRITICAL
  - **Structured Format**: JSON logs with consistent schema
    ```json
    {
      "timestamp": "2025-10-08T14:32:15.234Z",
      "level": "ERROR",
      "service": "payment-api",
      "request_id": "req_abc123",
      "user_id": "user_456",
      "message": "Payment processing failed",
      "error": "Gateway timeout",
      "duration_ms": 5042,
      "payment_amount": 99.99,
      "payment_method": "credit_card"
    }
    ```
  - **Logging Libraries**:
    - Node.js: `winston`, `pino`, `bunyan`
    - Python: `structlog`, `python-json-logger`
    - Java: Logback with `logstash-logback-encoder`, Log4j2
    - Go: `zap`, `logrus`
  - **Contextual Logging**: Include request IDs, user IDs, correlation IDs for tracing

- **Log Collection Infrastructure**: Ship logs from all sources to centralized system
  - **Log Shippers**:
    - Filebeat: Lightweight, tails log files, ships to Logstash/Elasticsearch
    - Fluentd/Fluent Bit: Unified logging layer, multi-destination support
    - Logstash: Heavy-weight processing, transformation, enrichment
    - Vector: High-performance, Rust-based, observability data pipeline
    - Cloud-Native: CloudWatch Logs agent, Datadog agent, Fluentd DaemonSet (Kubernetes)
  - **Log Sources**:
    - Application logs (stdout/stderr from containers, log files)
    - Web server logs (nginx, Apache access/error logs)
    - System logs (syslog, systemd journal)
    - Database logs (slow queries, error logs, audit logs)
    - Security logs (authentication, authorization, firewall)

- **Log Storage and Indexing**: Fast search and analysis
  - **ELK Stack**:
    - Elasticsearch: Distributed search and analytics engine
    - Logstash: Log processing pipeline (parse, transform, enrich)
    - Kibana: Visualization and exploration interface
    - Index lifecycle management (hot-warm-cold architecture)
  - **Alternative Stacks**:
    - Grafana Loki: Cost-effective, labels-based indexing (like Prometheus for logs)
    - Splunk: Enterprise log management, powerful search, expensive
    - CloudWatch Logs Insights: AWS-native, serverless, SQL-like queries
    - Datadog Logs: Unified platform, APM correlation, fast search
  - **Retention Strategy**:
    - Recent logs (7-14 days): Full-text indexed, sub-second search
    - Medium-term logs (30-90 days): Compressed, slower search
    - Long-term logs (1 year+): Archive to S3/GCS, compliance/audit only

- **Log Analysis and Correlation**: Extract insights from log data
  - **Pattern Detection**: Identify common errors, warnings, anomalies
  - **Log-Metric Correlation**: Link log events to metric spikes
  - **Trace-Log Correlation**: Jump from distributed trace to relevant logs
  - **Anomaly Detection**: ML-based detection of unusual log patterns
  - **Search Optimization**: Index fields for fast filtering (service, environment, level)

- **Log Security and Compliance**: Protect sensitive data
  - **PII Redaction**: Automatically scrub personal information (emails, IPs, SSNs)
  - **Secret Masking**: Never log passwords, API keys, tokens
  - **Access Control**: Role-based access to log data
  - **Audit Logging**: Track who accessed what logs when
  - **Retention Compliance**: GDPR, HIPAA, SOC2 data retention requirements

**Deliverables:**
- **Log Aggregation Infrastructure** (production-ready, scalable)
  - Centralized logging for 100% of production services
  - 500GB-5TB daily log ingestion capacity (scales with traffic)
  - Sub-second search performance for recent logs
  - 99.9% log delivery reliability (at-least-once delivery)
- **Log Parsing Rules** (structured parsing for all log formats)
  - Application log parsers (40-100 parsers for different services)
  - Infrastructure log parsers (nginx, syslog, systemd)
  - Database log parsers (slow queries, errors)
  - Security log parsers (authentication, authorization)
- **Saved Searches and Dashboards** (20-40 common log queries)
- **Log Retention Policy** (documented, automated lifecycle management)
- **PII Redaction Rules** (automated sensitive data protection)

### Phase 4: Distributed Tracing and APM (3-4 hours)
**Lead:** `observability-engineer`

Implement distributed tracing for request-level visibility across microservices:

- **Distributed Tracing Fundamentals**: Understand trace propagation
  - **Trace Context**: Trace ID (unique per request), Span ID (unique per operation)
  - **Span Relationships**: Parent-child spans showing service call hierarchy
  - **Baggage**: Key-value pairs propagated across service boundaries
  - **Sampling**: Intelligent sampling to reduce data volume (head-based, tail-based, adaptive)

- **Tracing Instrumentation**: Auto-instrument services
  - **OpenTelemetry**: Industry-standard, vendor-neutral observability framework
    - Auto-instrumentation for popular frameworks (Express, Django, Spring Boot)
    - Manual instrumentation for custom spans and attributes
    - Exporters for Jaeger, Zipkin, Datadog, New Relic, AWS X-Ray
  - **Framework-Specific Tracing**:
    - Node.js: `@opentelemetry/auto-instrumentations-node`
    - Python: `opentelemetry-instrumentation-*` packages
    - Java: OpenTelemetry Java agent (javaagent)
    - Go: `go.opentelemetry.io/otel` SDK
  - **Service Mesh Tracing**: Istio, Linkerd auto-inject trace headers

- **Trace Collection and Storage**: Centralized trace backend
  - **Jaeger**:
    - Open-source, CNCF project, proven at Uber scale
    - UI for trace visualization and service dependency graphs
    - Cassandra/Elasticsearch backend for storage
    - Sampling strategies (probabilistic, rate-limiting, adaptive)
  - **Alternative Tracing Backends**:
    - Grafana Tempo: Cost-effective, S3-compatible storage, integrates with Loki/Prometheus
    - Zipkin: Mature, battle-tested, simple deployment
    - AWS X-Ray: AWS-native, automatic Lambda integration
    - Datadog APM / New Relic APM: Full-featured commercial solutions
  - **Trace Sampling Strategy**:
    - Head-based sampling: Decide at trace start (1-10% sampling)
    - Tail-based sampling: Decide after trace completes (keep errors, slow requests)
    - Adaptive sampling: Adjust rate based on traffic and error patterns

- **Application Performance Monitoring (APM)**: End-to-end performance visibility
  - **Service Map**: Visual representation of service dependencies
  - **Latency Analysis**: Identify slow services, database queries, external API calls
  - **Error Tracking**: Capture exceptions, stack traces, error contexts
  - **Database Query Profiling**: Slow query detection, N+1 query identification
  - **Transaction Tracing**: Complete request path from user action to database and back

- **Trace-Metric-Log Correlation**: Unified observability
  - **Exemplars**: Link metrics to example traces (Prometheus exemplars)
  - **Trace IDs in Logs**: Include trace ID in structured logs for correlation
  - **Span Metrics**: Generate RED metrics from trace data
  - **Unified UI**: Jump from dashboard metric → trace → logs seamlessly

**Deliverables:**
- **Distributed Tracing Infrastructure** (production-ready)
  - Tracing instrumentation for 95%+ of services
  - Trace backend with 7-30 day retention
  - 1-10% sampling rate (adaptive based on traffic)
  - Service dependency map (auto-generated from traces)
- **APM Dashboards** (service performance overview)
  - Service latency percentiles (p50, p95, p99) over time
  - Error rate trends and anomaly detection
  - Database query performance analysis
  - External dependency latency tracking
- **Trace-Metric-Log Correlation** (seamless navigation)
- **Performance Baselines** (establish normal latency for all services)
- **Sampling Configuration** (optimized for cost vs. visibility)

### Phase 5: Alerting and Incident Management (3-5 hours)
**Lead:** `site-reliability-engineer` + `devops-engineer`

Implement intelligent alerting that notifies the right people at the right time:

- **Alert Strategy and SLI/SLO Definition**: Alerts tied to user impact
  - **SLI Definition (Service Level Indicators)**:
    - Availability: Percentage of successful requests (e.g., 99.9% availability)
    - Latency: Request duration percentiles (e.g., 95% of requests < 200ms)
    - Quality: Error rate thresholds (e.g., error rate < 0.1%)
  - **SLO Definition (Service Level Objectives)**:
    - Target values for SLIs (e.g., "99.9% of requests succeed in 30-day window")
    - Error budget calculation (allowed downtime/errors)
    - Multi-window alerting (5min, 30min, 6hr windows for different sensitivities)
  - **Alert Prioritization**:
    - **P0 (Critical)**: Customer-impacting outage, immediate response required
    - **P1 (High)**: Degraded service, respond within 30 minutes
    - **P2 (Medium)**: Non-critical issue, respond during business hours
    - **P3 (Low)**: Informational, no immediate action required

- **Alert Rule Design**: Actionable, low false-positive alerts
  - **Symptom-Based Alerts**: Alert on user impact (high latency, errors), not causes (high CPU)
  - **Multi-Signal Alerts**: Combine signals to reduce false positives (error rate AND latency spike)
  - **Threshold Selection**: Use percentiles, avoid static thresholds
    ```promql
    # Good: Alert on p95 latency increase (adaptive to traffic)
    histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5

    # Better: Alert on SLO burn rate (how fast you're consuming error budget)
    (
      slo_errors_total / slo_requests_total > 0.001  # 0.1% error rate
    ) and (
      rate(slo_errors_total[5m]) / rate(slo_requests_total[5m]) > 0.005  # 0.5% in last 5min
    )
    ```
  - **Alert Message Template**: Include context, impact, and runbook link
    ```yaml
    alert: HighErrorRate
    annotations:
      summary: "Payment API error rate is {{ $value | humanizePercentage }}"
      description: |
        Payment API has {{ $value | humanizePercentage }} error rate (threshold: 0.1%).
        This affects customer checkout and may result in revenue loss.

        Runbook: https://wiki/runbooks/payment-api-errors
        Dashboard: https://grafana/d/payment-api
        Service: payment-api
      impact: "Customers cannot complete purchases. Estimated revenue loss: $500/minute"
    ```

- **Alert Routing and On-Call Management**: Right notification to right person
  - **PagerDuty / Opsgenie / VictorOps Setup**:
    - On-call schedules and rotations
    - Escalation policies (no response in 5min → escalate to manager)
    - Alert grouping and deduplication
    - Acknowledgment and snooze workflows
  - **Notification Channels**:
    - **Critical**: PagerDuty phone call + SMS + push notification
    - **High**: PagerDuty push notification + Slack critical channel
    - **Medium**: Slack engineering channel, email digest
    - **Low**: Ticket creation (Jira, GitHub Issues)
  - **Alert Fatigue Prevention**:
    - Suppress duplicate alerts for same incident
    - Silence alerts during known maintenance windows
    - Alert throttling for flapping metrics
    - Regular alert tuning based on false positive rate

- **Runbook Integration**: Every alert has a runbook
  - **Runbook Structure**:
    - **Impact**: What is broken? Who is affected?
    - **Diagnosis**: How to confirm the issue? Key metrics to check?
    - **Mitigation**: Immediate actions to reduce customer impact?
    - **Resolution**: How to fix the root cause?
    - **Prevention**: How to prevent recurrence?
  - **Runbook Automation**: Scripts for common remediation tasks
  - **Runbook Links**: Embed runbook URL in alert annotations

- **Dashboards and Visualization**: Real-time system health visibility
  - **Golden Signals Dashboard**: Latency, Traffic, Errors, Saturation
  - **SLI/SLO Tracking Dashboard**: Error budget consumption, burn rate
  - **Service Health Overview**: All services at a glance (red/yellow/green)
  - **Infrastructure Health**: CPU, memory, disk, network across all hosts
  - **Business Metrics Dashboard**: Revenue, signups, active users
  - **On-Call Dashboard**: Active incidents, alerts, on-call rotation

**Deliverables:**
- **Alert Rules** (40-80 production alerts)
  - SLO-based alerts for all critical services
  - Infrastructure health alerts (CPU, memory, disk, network)
  - Database alerts (connection pool, slow queries, replication lag)
  - Security alerts (unauthorized access, rate limiting, anomalies)
  - <5% false positive rate (well-tuned alerts)
- **On-Call Infrastructure** (PagerDuty/Opsgenie)
  - On-call schedules for 3-5 teams
  - Escalation policies documented and tested
  - Alert routing rules (right alert → right team)
  - Incident response workflows integrated
- **Runbooks** (25-50 runbooks for common alerts)
  - Runbook for every critical alert
  - Automated remediation scripts where possible
  - Regular runbook testing and updates
- **Dashboards** (15-30 Grafana/Datadog dashboards)
  - Executive dashboard (high-level system health)
  - Engineering dashboards (service-specific deep dives)
  - On-call dashboard (active incidents, alerts, metrics)
  - Business metrics dashboard (user-facing KPIs)
- **SLI/SLO Documentation** (service level objectives for all critical services)
  - Error budgets and burn rate calculations
  - Historical SLO compliance reporting

## Expected Outcomes

### Operational Excellence
- **70-90% reduction in MTTD (Mean Time to Detection)**: Alerts detect issues in seconds/minutes vs. hours/days
  - Before: Customer reports outage after 2 hours of downtime
  - After: Alert fires within 30 seconds of error rate spike
- **50-75% reduction in MTTR (Mean Time to Resolution)**: Faster diagnosis and remediation
  - Before: 45 minutes to diagnose database connection pool exhaustion
  - After: 8 minutes to identify issue via traces, apply fix from runbook
- **60-85% reduction in alert fatigue**: Well-tuned alerts, low false positives
  - Before: 50 alerts/day, 90% false positives, ignored by on-call
  - After: 8 alerts/day, 95% actionable, fast response
- **95%+ observability coverage**: Complete visibility into all production services
- **3-5x faster incident triage**: Dashboards, traces, logs available instantly

### System Reliability
- **40-60% reduction in incident count**: Proactive detection prevents escalation
- **30-50% improvement in SLO compliance**: Meet availability and latency targets
- **80-95% reduction in "mystery" incidents**: Unknowns become knowable with traces
- **70-90% reduction in customer-reported issues**: Internal detection beats customer reports
- **99.9%+ monitoring uptime**: Observability infrastructure is highly available

### Team Productivity
- **50-70% reduction in debugging time**: Traces show exact problem location
- **60-80% faster onboarding for new engineers**: Dashboards and runbooks accelerate learning
- **40-60% reduction in "war room" time**: Faster diagnosis = shorter incidents
- **30-50% reduction in "unknown unknowns"**: Comprehensive metrics reveal hidden issues
- **4-6 hours/week saved per engineer**: Less time firefighting, more time building

### Business Impact
- **$300K-$1.2M annual value from prevented downtime**
  - Example: 10 prevented outages × 2hr each × $15K/hr downtime cost = $300K
- **$150K-$500K annual value from faster incident resolution**
  - Example: 200 incidents × 30min faster MTTR × $50/min = $300K
- **$100K-$350K annual value from reduced on-call burden**
  - Example: 50% reduction in alerts × 500 alerts/month × $60/alert = $180K
- **8-15x ROI in first year** (typical: 11x)
- **$550K-$2M+ total annual impact**

## Usage

```bash
# Full monitoring stack setup (initial deployment)
/operations:monitoring-stack-setup --full

# Setup specific pillar only
/operations:monitoring-stack-setup --logs-only
/operations:monitoring-stack-setup --metrics-only
/operations:monitoring-stack-setup --traces-only
/operations:monitoring-stack-setup --alerts-only

# Setup for specific technology stack
/operations:monitoring-stack-setup --stack=prometheus,loki,tempo,grafana  # LGTM stack
/operations:monitoring-stack-setup --stack=datadog  # Datadog all-in-one
/operations:monitoring-stack-setup --stack=elk,jaeger,pagerduty  # Open-source stack

# Setup for specific cloud provider
/operations:monitoring-stack-setup --cloud=aws  # CloudWatch-optimized
/operations:monitoring-stack-setup --cloud=gcp  # GCP Monitoring-optimized
/operations:monitoring-stack-setup --cloud=azure  # Azure Monitor-optimized

# Generate observability maturity assessment
/operations:monitoring-stack-setup --assess-maturity

# Generate executive summary and ROI report
/operations:monitoring-stack-setup --report=executive
```

## Prerequisites

- [ ] Production environment access (cloud accounts, Kubernetes clusters, servers)
- [ ] Infrastructure provisioning permissions (create VMs, storage, networking)
- [ ] Application source code access for instrumentation
- [ ] Budget approval for observability tooling ($500-$5K/month typical SaaS costs)
- [ ] Team commitment to observability culture (SLIs, SLOs, blameless post-mortems)
- [ ] Stakeholder alignment on observability strategy and priorities
- [ ] Incident response process defined (who gets paged, escalation paths)
- [ ] On-call rotation established or planned

## Success Criteria

### Technical Metrics
- [ ] Metrics collection for 95%+ of production services and infrastructure
- [ ] Log aggregation for 100% of production services with <1% log loss
- [ ] Distributed tracing for 90%+ of user-facing requests (with intelligent sampling)
- [ ] Alert rules covering all critical SLIs (availability, latency, errors)
- [ ] Dashboards for all critical services and infrastructure components
- [ ] <5% alert false positive rate (well-tuned, actionable alerts)
- [ ] Sub-second query performance for recent metrics and logs
- [ ] 99.9%+ uptime for observability infrastructure itself

### Operational Metrics
- [ ] MTTD (Mean Time to Detection) reduced by 70%+ vs. baseline
- [ ] MTTR (Mean Time to Resolution) reduced by 50%+ vs. baseline
- [ ] 80%+ of incidents detected by monitoring (vs. customer reports)
- [ ] 90%+ of alerts have associated runbooks
- [ ] On-call engineers respond to alerts within 5 minutes (P0/P1)
- [ ] Incident retrospectives cite observability data 95%+ of the time
- [ ] Zero "blind spot" incidents (unknown state during incident)

### Business Metrics
- [ ] SLO compliance: 99%+ of services meet availability targets
- [ ] Customer satisfaction: <5% of support tickets due to undetected issues
- [ ] Team satisfaction: On-call engineers rate observability 8+/10
- [ ] ROI: 8x+ return on investment in first year
- [ ] Downtime reduction: 40%+ fewer customer-impacting incidents
- [ ] Cost efficiency: Observability costs <2% of infrastructure budget

## Real-World Impact Examples

### E-Commerce Platform (Scale: 50M requests/day, 200 microservices)
- **Before:** 2-6 hour MTTD, 45-90 min MTTR, 15 major outages/year, blind spot incidents
- **After:** 30 second MTTD, 12 min MTTR, 3 major outages/year, complete visibility
- **Impact:** $1.8M annual savings (prevented downtime + faster resolution), 12x ROI

**Specific Improvements:**
- Checkout flow latency spike detected in 30 seconds (was 2 hours via customer complaints)
- Database connection pool exhaustion traced in 5 minutes (was 45 minutes of guesswork)
- Payment gateway timeout issue identified with distributed traces (was unknown cause)
- Prevented 12 outages by detecting anomalies before customer impact

**Stack:** Prometheus + Thanos, Grafana Loki, Tempo, Grafana, PagerDuty
**Cost:** $12K/month (self-hosted) vs. $1.8M annual value = 150x monthly ROI

### SaaS Platform (Scale: 10K customers, 50 services, multi-tenant)
- **Before:** 45 min MTTD, 60 min MTTR, 80 incidents/year, 70% false positive alerts
- **After:** 2 min MTTD, 15 min MTTR, 32 incidents/year, 5% false positive alerts
- **Impact:** $650K annual savings, 50% reduction in on-call burden, 9x ROI

**Specific Improvements:**
- Tenant isolation issue detected via metrics before data leak (prevented security incident)
- API rate limiting false positives eliminated with proper alert thresholds
- Multi-region latency issues identified with distributed tracing across regions
- Database slow queries auto-detected and optimized, improving p95 latency 60%

**Stack:** Datadog (all-in-one)
**Cost:** $6K/month (SaaS) vs. $650K annual value = 108x monthly ROI

### Fintech Startup (Scale: 5M transactions/day, high compliance requirements)
- **Before:** No distributed tracing, manual log searching, reactive incident response
- **After:** Full observability stack, proactive monitoring, compliance-ready audit logs
- **Impact:** $425K annual value (prevented fraud + faster compliance audits), 11x ROI

**Specific Improvements:**
- Fraud detection latency reduced from 5 minutes to 200ms with APM optimization
- Compliance audit log search reduced from hours (grep) to seconds (Elasticsearch)
- Payment processing race condition identified with distributed tracing (prevented $50K loss)
- PCI-DSS compliance audit completed 60% faster with centralized, searchable logs

**Stack:** AWS CloudWatch + X-Ray, Elasticsearch (self-hosted), Grafana, Opsgenie
**Cost:** $3.5K/month vs. $425K annual value = 121x monthly ROI

## Common Challenges and Solutions

### Challenge: Alert Fatigue from High False Positive Rate
**Problem:** Teams receive 50-100 alerts/day, 80-90% are false positives, alerts get ignored
**Solution:**
- Implement SLO-based alerting (multi-window, multi-burn-rate) instead of static thresholds
- Use symptom-based alerts (user impact) rather than cause-based (CPU high)
- Set up alert tuning process: Review weekly, disable noisy alerts, refine thresholds
- Require runbooks for all critical alerts (if no runbook, probably not critical)
- Use alert suppression during deployments and known maintenance windows

### Challenge: Metric Cardinality Explosion and High Costs
**Problem:** Millions of unique time series, slow queries, $50K+/month SaaS costs
**Solution:**
- Audit high-cardinality labels (user IDs, request IDs should NOT be labels)
- Use relabeling rules to drop unused labels
- Implement intelligent sampling for high-volume metrics
- Use recording rules to pre-aggregate expensive queries
- Consider open-source stack (Prometheus + Thanos) for cost reduction

### Challenge: Distributed Tracing Overhead and Sampling Decisions
**Problem:** Tracing adds latency, 100% sampling is too expensive, but missing critical traces
**Solution:**
- Implement tail-based sampling (sample after trace completes, keep errors and slow requests)
- Use adaptive sampling (higher rate during incidents, lower during normal operation)
- Optimize instrumentation (minimize span creation, use async exporters)
- Focus on critical paths (trace user-facing requests, sample internal batch jobs lower)
- Use exemplars to link metrics to example traces (Prometheus exemplars feature)

### Challenge: Log Volume and Storage Costs
**Problem:** Ingesting 5TB/day of logs, $20K/month storage costs, slow searches
**Solution:**
- Implement log levels correctly (DEBUG only in dev, INFO/WARN/ERROR in production)
- Sample high-volume logs (e.g., keep 10% of INFO logs, 100% of ERROR logs)
- Use structured logging to avoid full-text indexing (index only key fields)
- Implement log lifecycle management (7 days hot, 30 days warm, 90 days cold archive)
- Consider cost-effective alternatives (Grafana Loki vs. Elasticsearch, S3 archive)

### Challenge: Observability Stack Reliability ("Who Monitors the Monitors?")
**Problem:** Monitoring system goes down during incident, blind during critical time
**Solution:**
- Deploy observability infrastructure in separate, isolated environment
- Implement high availability (HA Prometheus, Elasticsearch cluster, multi-region)
- Use external monitoring for observability stack health (Pingdom, UptimeRobot)
- Set up backup alerting (CloudWatch alarms as fallback to Prometheus)
- Regular DR testing for observability infrastructure

## Related Commands

- `/operations:incident-response-workflow` - Production incident management procedures
- `/operations:disaster-recovery-plan` - Business continuity and DR setup
- `/quality:production-readiness` - Pre-deployment validation including monitoring checks
- `/quality:performance-optimization` - Performance tuning using observability data
- `/development:database-optimization` - Database performance monitoring and tuning

## Notes

**Three Pillars of Observability:** Logs (what happened), Metrics (how much/how fast), Traces (where in the system). All three are required for complete observability - metrics show the problem, traces show the location, logs show the details.

**Observability vs. Monitoring:** Monitoring answers known questions ("is service up?"). Observability answers unknown questions ("why is checkout slow for users in EU on mobile?"). Aim for observability, not just monitoring.

**SLI/SLO-Driven Alerting:** Best practice is to define SLIs (measurable indicators of user experience) and SLOs (target values), then alert on error budget burn rate. This aligns alerts with business impact and reduces false positives.

**Instrumentation is Product Code:** Treat observability instrumentation as first-class product code. Include in code reviews, test coverage, documentation. Poor instrumentation = blind production systems.

**Cost-Benefit Trade-offs:** Open-source self-hosted (lower cost, higher operational burden) vs. commercial SaaS (higher cost, lower burden). For small teams (<20 engineers), SaaS often cheaper total cost. For large teams (100+ engineers), self-hosted often more cost-effective.

**Progressive Instrumentation:** Don't try to instrument everything on day 1. Start with critical user journeys, expand coverage over time. 80% coverage delivers 95% of the value.

**Cardinality is the Enemy:** High-cardinality labels (millions of unique values) kill performance and explode costs. Avoid labels like user_id, request_id, timestamp in metrics. Use traces for request-level detail, metrics for aggregates.

**Cultural Foundation:** Observability requires cultural change. Teams must prioritize instrumentation, runbook creation, alert tuning. Leadership must support investment in "non-functional" work. Blameless post-mortems and learning culture are essential.

**Avoid Vendor Lock-in:** Use open standards (OpenTelemetry, Prometheus metrics, OTLP traces) to avoid vendor lock-in. Makes it easy to switch providers or migrate from SaaS to self-hosted.

**Security and Compliance:** Implement PII redaction in logs, RBAC for observability data access, audit logging for sensitive queries. Many compliance frameworks (SOC2, HIPAA) require centralized logging and audit trails.

**Continuous Improvement:** Observability is never "done". Continuously tune alerts, add new dashboards, expand instrumentation, optimize costs, improve runbooks. Schedule quarterly observability retrospectives to assess and improve.
