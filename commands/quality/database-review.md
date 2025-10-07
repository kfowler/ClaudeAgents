# Database Quality Review

Comprehensive database assessment covering performance optimization, security hardening, schema quality, operational health, and data integrity for production-grade database systems.

## Overview

This command orchestrates a multi-dimensional database quality assessment that evaluates your database systems against production-readiness standards, identifies performance bottlenecks, security vulnerabilities, and operational risks, and provides actionable recommendations for optimization and hardening.

**When to Use This Command:**
- Pre-production deployment readiness validation
- Post-incident database health assessment
- Quarterly database quality audits
- Before major schema migrations or refactoring
- When experiencing performance degradation or scalability issues
- Compliance audit preparation (SOC 2, HIPAA, GDPR)

**Value Delivered:**
- Identify query performance bottlenecks and optimization opportunities
- Discover security vulnerabilities, access control gaps, and compliance issues
- Validate schema design quality, normalization, and data integrity
- Assess operational readiness including backup/recovery, monitoring, and disaster recovery
- Quantify data quality issues and establish governance recommendations
- Provide prioritized remediation roadmap with business impact assessment

## Agents Involved

- **database-administrator** (Primary) - Performance tuning, schema analysis, operational health, backup/recovery validation
- **security-audit-specialist** - Database security review, access controls, encryption, injection vulnerability assessment
- **data-engineer** - Data pipeline integration analysis, ETL quality, analytics query optimization

## Workflow Steps

### 1. Database Discovery & Inventory

**Objective**: Catalog all database instances, schemas, sizes, and critical business functions.

**Actions**:
- Identify all database instances (production, staging, read replicas, analytics databases)
- Document database technologies (PostgreSQL, MySQL, MongoDB, Redis, etc.)
- Inventory schemas, tables, views, stored procedures, functions, triggers
- Measure database sizes, growth rates, transaction volumes
- Map database relationships to application services and business functions
- Identify high-value tables (user data, financial transactions, audit logs)

**Tools & Techniques**:
- Database metadata queries (`information_schema`, `pg_catalog`, `sys` tables)
- Cloud provider database inventory (AWS RDS, Azure Database, GCP Cloud SQL)
- Infrastructure as code analysis (Terraform, CloudFormation)
- Application configuration review (connection strings, ORM configurations)

**Deliverables**:
- Database inventory spreadsheet with versions, sizes, and business criticality
- Schema ERD diagrams showing table relationships and cardinality
- Growth trend analysis and capacity forecasts

### 2. Performance Analysis & Query Optimization

**Objective**: Identify slow queries, missing indexes, inefficient execution plans, and resource bottlenecks.

**Actions**:
- Analyze slow query logs to identify performance bottlenecks (queries >100ms)
- Review query execution plans for table scans, missing indexes, inefficient joins
- Assess index effectiveness, usage statistics, and duplicate/unused indexes
- Evaluate connection pool configuration and connection exhaustion risks
- Analyze lock contention, deadlocks, and transaction isolation issues
- Review database statistics freshness and auto-vacuum effectiveness (PostgreSQL)
- Assess cache hit ratios, buffer pool utilization, and memory allocation
- Identify N+1 query patterns and ORM inefficiencies

**Tools & Techniques**:
- PostgreSQL: `pg_stat_statements`, `EXPLAIN ANALYZE`, `pg_stat_user_indexes`
- MySQL: `slow_query_log`, `EXPLAIN`, `performance_schema`
- MongoDB: `db.currentOp()`, profiler, index usage statistics
- Query performance monitoring: New Relic, Datadog, pganalyze, VividCortex
- Index analysis: `pg_stat_user_indexes`, missing index queries
- Lock monitoring: `pg_locks`, `pg_stat_activity`, deadlock logs

**Deliverables**:
- Top 20 slow queries with execution plans and optimization recommendations
- Missing index recommendations with expected performance impact
- Unused/duplicate index removal candidates to reduce write overhead
- Connection pool tuning recommendations
- Query rewrite examples demonstrating optimization techniques
- Performance baseline metrics for ongoing monitoring

### 3. Security Assessment & Access Control Review

**Objective**: Validate database security posture, access controls, encryption, and compliance with security standards.

**Actions**:
- Review authentication mechanisms (password policies, MFA, certificate authentication)
- Audit user accounts, roles, and privilege assignments (principle of least privilege)
- Identify overprivileged accounts (users with SUPERUSER, DBA, root access)
- Validate network security (firewall rules, VPC isolation, private subnets)
- Assess encryption in transit (SSL/TLS enforcement, certificate validation)
- Assess encryption at rest (transparent data encryption, encrypted volumes)
- Review SQL injection vulnerability surface (prepared statements, input validation)
- Audit logging configuration and retention policies
- Validate backup encryption and secure storage
- Review compliance requirements (PCI DSS, HIPAA, GDPR, SOC 2)

**Tools & Techniques**:
- PostgreSQL: `pg_roles`, `pg_hba.conf`, `information_schema.role_table_grants`
- MySQL: `mysql.user`, `SHOW GRANTS`, security audit plugins
- Cloud security: AWS RDS security groups, IAM policies, encryption settings
- Vulnerability scanning: SQLMap (controlled testing), OWASP ZAP database tests
- Compliance frameworks: CIS benchmarks, STIGs, vendor security guides
- Audit log analysis: pgAudit, MySQL Enterprise Audit, cloud audit logs

**Deliverables**:
- User privilege audit report identifying overprivileged accounts
- Security vulnerability findings with CVSS scores and remediation steps
- Access control matrix showing who can access what data
- Encryption status report (in-transit, at-rest, backup encryption)
- Compliance gap analysis against required standards (HIPAA, PCI, GDPR)
- Security hardening checklist with implementation priorities

### 4. Schema Quality & Design Assessment

**Objective**: Evaluate schema design quality, normalization, data types, constraints, and maintainability.

**Actions**:
- Assess normalization levels and identify denormalization trade-offs
- Review data type choices for efficiency and correctness (INT vs BIGINT, VARCHAR sizing)
- Validate constraint usage (primary keys, foreign keys, unique constraints, check constraints)
- Evaluate naming conventions and schema organization consistency
- Identify missing foreign key relationships causing referential integrity issues
- Review index strategy alignment with query patterns
- Assess table partitioning and sharding strategies for large tables
- Evaluate temporal data handling (timestamps, soft deletes, audit trails)
- Review JSON/JSONB usage and opportunities for structured schema
- Identify code smells (EAV anti-pattern, over-normalization, polymorphic associations)

**Tools & Techniques**:
- Schema analysis queries (table sizes, column statistics, constraint inventory)
- ERD generation tools (SchemaSpy, DBeaver, pgModeler)
- Data type analysis (oversized VARCHARs, missing NOT NULL constraints)
- Foreign key gap analysis (orphaned records, missing relationships)
- Normalization analysis (partial dependencies, transitive dependencies)
- ORM schema validation (Rails schema.rb, Django models, Entity Framework)

**Deliverables**:
- Schema quality scorecard with normalization assessment
- Data type optimization recommendations (storage savings estimates)
- Missing constraint recommendations to enforce data integrity
- Naming convention violations and standardization guidelines
- Schema refactoring roadmap for identified anti-patterns
- ERD with recommended relationship improvements

### 5. Operational Health & Reliability Assessment

**Objective**: Validate backup/recovery procedures, monitoring coverage, disaster recovery readiness, and operational excellence.

**Actions**:
- Review backup strategy (frequency, retention, backup types: full/incremental/differential)
- Validate backup integrity and recoverability (last successful restore test date)
- Assess Recovery Time Objective (RTO) and Recovery Point Objective (RPO) compliance
- Review replication configuration (streaming replication, logical replication, read replicas)
- Evaluate failover mechanisms and high availability architecture
- Assess monitoring coverage (query performance, connection counts, disk space, replication lag)
- Review alerting thresholds and incident response procedures
- Validate capacity planning and resource utilization trends
- Assess maintenance window procedures (VACUUM, ANALYZE, index maintenance)
- Review change management and schema migration processes

**Tools & Techniques**:
- Backup validation: restore testing, backup size monitoring, backup success rates
- Replication monitoring: `pg_stat_replication`, replication lag metrics
- High availability: cluster health checks, failover testing, split-brain prevention
- Monitoring: Prometheus + Grafana, CloudWatch, Datadog, pgMonitor
- Capacity planning: disk growth projections, connection count trends, CPU/memory utilization
- Maintenance automation: pg_cron, scheduled jobs, vacuum monitoring

**Deliverables**:
- Backup and recovery assessment report with RTO/RPO compliance status
- Disaster recovery runbook validation and gap analysis
- Monitoring coverage matrix identifying blind spots
- Alerting configuration review with threshold recommendations
- Capacity planning forecast (6-12 month projection)
- Operational excellence checklist with automation opportunities

### 6. Data Quality & Integrity Validation

**Objective**: Assess data quality, integrity constraints, consistency, and data governance practices.

**Actions**:
- Validate referential integrity (orphaned records, dangling foreign keys)
- Identify NULL values in business-critical columns without NOT NULL constraints
- Assess data consistency across related tables and denormalized columns
- Review data validation rules and check constraints
- Identify duplicate records and data quality issues
- Evaluate data retention and archival policies
- Assess data lineage and transformation documentation
- Review data masking and anonymization for non-production environments
- Validate business rule enforcement (database triggers, application logic)
- Assess data governance policies (data ownership, classification, lifecycle management)

**Tools & Techniques**:
- Data quality queries (NULL analysis, orphaned records, duplicates)
- Referential integrity validation (foreign key violation checks)
- Data profiling tools (Great Expectations, dbt tests, custom SQL queries)
- Constraint violation detection (check constraint candidates)
- ETL validation (data pipeline testing, transformation accuracy)
- Data observability: Monte Carlo, Datafold, dbt test results

**Deliverables**:
- Data quality scorecard with integrity violation counts
- Orphaned record report with cleanup recommendations
- Missing constraint recommendations to prevent future data quality issues
- Data validation rule catalog with coverage assessment
- Data governance maturity assessment
- Data quality monitoring dashboard with ongoing validation queries

### 7. Synthesis & Prioritized Remediation Roadmap

**Objective**: Consolidate findings, prioritize recommendations by business impact, and create actionable remediation plan.

**Actions**:
- Consolidate findings from all assessment areas into unified report
- Prioritize recommendations by severity (critical, high, medium, low)
- Assess business impact of each issue (performance, security, compliance, cost)
- Estimate effort required for each remediation (hours/days, complexity)
- Create phased remediation roadmap with quick wins and strategic improvements
- Identify dependencies between remediation tasks
- Provide implementation guidance and technical specifications
- Establish success metrics and validation criteria for each recommendation

**Deliverables**:
- Executive summary with key findings and business impact
- Comprehensive database quality report (50-100 pages for production systems)
- Prioritized remediation backlog with effort estimates
- Quick win recommendations (high impact, low effort)
- 30-60-90 day improvement roadmap
- Database quality dashboard for ongoing monitoring
- Success metrics and KPIs for quality tracking

## Deliverables

### Comprehensive Reports
- **Executive Summary**: 2-3 page overview with critical findings, business risks, and recommended actions
- **Database Quality Scorecard**: Quantitative assessment across 6 dimensions (performance, security, schema, operations, data quality, compliance)
- **Performance Analysis Report**: Slow query analysis, index recommendations, execution plan optimizations
- **Security Assessment Report**: Vulnerability findings, access control audit, compliance gap analysis
- **Schema Quality Report**: Design assessment, normalization review, constraint recommendations
- **Operational Readiness Report**: Backup/recovery validation, monitoring gaps, capacity planning
- **Data Quality Report**: Integrity violations, consistency issues, governance maturity

### Actionable Recommendations
- **Prioritized Remediation Backlog**: 20-50 specific action items with effort estimates and business impact
- **Quick Win Recommendations**: 5-10 high-impact, low-effort improvements for immediate implementation
- **Query Optimization Examples**: Rewritten queries with before/after performance comparisons
- **Schema Migration Scripts**: DDL for adding missing constraints, indexes, and optimizations
- **Security Hardening Checklist**: Step-by-step implementation guide for security improvements
- **Monitoring Dashboard**: Pre-configured queries and alerts for ongoing database health monitoring

### Implementation Guidance
- **30-60-90 Day Roadmap**: Phased implementation plan with milestones
- **Technical Specifications**: Detailed implementation guidance for complex recommendations
- **Risk Assessment**: Potential risks and mitigation strategies for proposed changes
- **Rollback Procedures**: Safety measures for production changes

## Prerequisites

### Required Access
- Database administrator credentials with read access to system catalogs and statistics
- Access to slow query logs, error logs, and audit logs
- Database monitoring dashboards and historical performance metrics
- Infrastructure access to review backup configurations and network security
- Application code repository to analyze query patterns and ORM usage

### Information Needed
- Database version, configuration files, and deployment architecture
- Business criticality classification for each database/schema
- Current RTO/RPO requirements and SLAs
- Compliance requirements (industry regulations, corporate policies)
- Recent incidents, outages, or performance issues
- Planned changes or upcoming scaling requirements

### Environment Requirements
- Production database access (read-only preferred, some commands require elevated privileges)
- Staging/development databases for comparative analysis
- Monitoring tools integrated (Prometheus, CloudWatch, Datadog, etc.)
- Recent backup to restore for validation testing (non-production environment)

## Time Estimate

**Total Duration**: 16-32 hours (2-4 business days) depending on database complexity

**Breakdown by Phase**:
- Database Discovery & Inventory: 2-4 hours
- Performance Analysis: 4-8 hours (most time-intensive)
- Security Assessment: 3-5 hours
- Schema Quality Review: 3-6 hours
- Operational Health: 2-4 hours
- Data Quality Validation: 2-4 hours
- Synthesis & Reporting: 2-3 hours

**Factors Affecting Duration**:
- Number of database instances (multiply by 70% for each additional database)
- Database size and complexity (tables, stored procedures, triggers)
- Compliance requirements (each standard adds 1-2 hours)
- Historical incident investigation (adds 2-4 hours if deep analysis required)
- Security vulnerability remediation validation (adds 2-4 hours if testing fixes)

**Accelerated Option**: 8-12 hours for focused review targeting specific concern areas (performance OR security OR operations)

## Related Commands

### Complementary Quality Commands
- `/quality:performance-audit` - Application-level performance review (pairs with database performance analysis)
- `/quality:security-audit` - Application security review (extends database security findings)
- `/quality:architecture-review` - System architecture assessment (database architecture context)
- `/quality:production-readiness` - Comprehensive pre-deployment checklist (includes database validation)

### Implementation Support
- Use `database-administrator` agent for implementing performance optimizations and operational improvements
- Use `security-audit-specialist` agent for implementing security hardening recommendations
- Use `data-engineer` agent for data quality remediation and pipeline improvements
- Use `devops-engineer` agent for backup automation, monitoring setup, and infrastructure improvements

### Ongoing Monitoring
- Establish quarterly database quality reviews to track improvement trends
- Integrate automated data quality tests into CI/CD pipelines (dbt tests, Great Expectations)
- Set up continuous monitoring dashboards using recommendations from this review
- Schedule annual disaster recovery testing to validate operational readiness

## Success Criteria

A successful database quality review should result in:
- Clear identification of top 10 critical issues with business impact quantification
- Performance improvement opportunities with measurable expected gains (response time reduction, cost savings)
- Zero critical security vulnerabilities in production databases
- Backup/recovery procedures validated and documented with tested RTO/RPO
- Prioritized roadmap with actionable next steps and owner assignments
- Executive and technical stakeholder alignment on quality priorities

## Best Practices

**Before Running This Command**:
- Notify stakeholders about database analysis activity (may cause minor performance impact)
- Ensure you have appropriate access credentials and permissions
- Back up current database configurations and statistics for baseline comparison
- Schedule review during lower-traffic periods if analyzing production systems

**During the Review**:
- Take snapshots of query performance before making changes for before/after comparison
- Document all findings with specific examples (query text, table names, metrics)
- Avoid making changes to production databases during analysis phase
- Collaborate with application developers to understand query patterns and business logic

**After the Review**:
- Present findings to stakeholders with business impact framing, not just technical details
- Create GitHub issues or tickets for each remediation item with acceptance criteria
- Establish follow-up review date to validate implementation and measure improvements
- Share database quality scorecard with engineering leadership for transparency

**Safety Considerations**:
- Always test schema changes and query optimizations in non-production environments first
- Use transactions and have rollback plans for any production changes
- Schedule disruptive changes (index creation, table partitioning) during maintenance windows
- Monitor performance metrics before, during, and after implementing recommendations
