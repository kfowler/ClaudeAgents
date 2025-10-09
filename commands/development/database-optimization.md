---
name: database-optimization
description: "Comprehensive database optimization and quality review covering performance tuning, security hardening, schema quality, operational excellence, and data integrity for production-grade database systems"
agents:
  - postgresql-expert
  - data-engineer
  - devops-engineer
  - security-audit-specialist
complexity: high
duration: 8-12 hours
---

# Database Optimization & Quality Review

**Command:** `/database-optimization`
**Agents:** `postgresql-expert`, `data-engineer`, `devops-engineer`, `security-audit-specialist`
**Complexity:** High
**Duration:** 8-12 hours (full review) or 6-8 hours (performance focus)

## Overview

Comprehensive database optimization and quality assessment workflow that coordinates database specialists, data engineers, DevOps, and security experts to identify bottlenecks, optimize performance, validate security, assess schema quality, ensure data integrity, and establish operational excellence for production-ready database systems.

## What This Command Does

This command orchestrates complete database optimization and quality review across 7 phases:

### Phase 1: Performance Audit & Problem Identification (1.5-2 hours)
**Lead:** `postgresql-expert`, **Supporting:** `data-engineer`

Database Health Assessment:
- Analyze current performance metrics (query latency, throughput, connections)
- Review slow query logs (pg_stat_statements, slow query log)
- Identify N+1 query problems and missing indexes
- Assess connection pool utilization and saturation
- Analyze cache hit ratios (buffer cache, index cache)
- Review table and index bloat (autovacuum effectiveness)
- Identify lock contention and blocking queries
- Analyze transaction isolation issues and deadlocks
- Review replication lag (if replicas exist)
- Assess disk I/O patterns and bottlenecks

Query Analysis:
- Extract top 20 slowest queries by total time and execution count
- Analyze query execution plans (EXPLAIN ANALYZE)
- Identify sequential scans on large tables
- Detect missing or unused indexes
- Identify queries with high buffer reads
- Find queries causing excessive disk writes
- Analyze queries with suboptimal join strategies
- Review queries with expensive sorting and aggregation

Configuration Review:
- Review postgresql.conf settings (shared_buffers, work_mem, effective_cache_size)
- Analyze connection limits and connection pooling
- Review autovacuum settings (thresholds, scale factors, max workers)
- Assess WAL configuration (wal_level, checkpoint settings)
- Review logging configuration (statement logging, auto_explain)
- Analyze maintenance windows and vacuum schedules

**Deliverables:**
- Performance audit report with top issues (prioritized by impact)
- Slow query report (top 20 queries with execution plans)
- Index analysis report (missing, unused, bloated indexes)
- Cache hit ratio analysis (buffer cache, table cache, index cache)
- Configuration review with recommended changes
- Baseline performance metrics (before optimization)
- Problem prioritization matrix (impact vs effort)

### Phase 2: Query Optimization & Indexing Strategy (2-2.5 hours)
**Lead:** `postgresql-expert`, **Supporting:** `data-engineer`

Query Optimization:
- Rewrite N+1 queries with JOINs or subqueries
- Optimize WHERE clauses (avoid functions on indexed columns)
- Improve JOIN strategies (INNER vs LEFT vs hash vs merge)
- Optimize subqueries (use CTEs, window functions, or JOINs)
- Add LIMIT clauses to unbounded queries
- Use EXISTS instead of COUNT(*) for existence checks
- Optimize GROUP BY and DISTINCT operations
- Implement query result caching (application-level or materialized views)
- Use partial indexes for filtered queries
- Implement covering indexes for index-only scans

Index Design:
- Create missing indexes on frequently filtered columns (WHERE, JOIN)
- Design composite indexes (optimize column order by selectivity)
- Implement partial indexes for subset queries (WHERE status = 'active')
- Create expression indexes for computed columns (LOWER(email))
- Design GIN/GIST indexes for full-text search and arrays
- Remove unused indexes (identified by pg_stat_user_indexes)
- Consolidate redundant indexes (B-tree on (a,b,c) covers (a) and (a,b))
- Implement BRIN indexes for time-series data
- Create unique indexes for data integrity (performance benefit)
- Plan index maintenance strategy (REINDEX, CONCURRENTLY)

Materialized Views:
- Identify expensive reporting queries for materialized views
- Design materialized view refresh strategy (REFRESH MATERIALIZED VIEW)
- Plan incremental refresh for large views (custom logic)
- Create indexes on materialized views
- Schedule automatic refresh (cron, pg_cron extension)

**Deliverables:**
- Optimized query versions with execution plans (before/after comparison)
- Index creation DDL (CREATE INDEX CONCURRENTLY statements)
- Materialized view definitions with refresh schedules
- Query performance comparison (before/after metrics)
- Index maintenance scripts (REINDEX, ANALYZE)
- Application code changes required (ORM query modifications)
- Estimated performance improvements by query

### Phase 3: Configuration Tuning & Resource Optimization (1.5-2 hours)
**Lead:** `postgresql-expert`, **Supporting:** `devops-engineer`

Memory Configuration:
- Tune shared_buffers (25% of RAM, typically 2-8GB)
- Configure work_mem (per query memory, 4MB-64MB per connection)
- Set maintenance_work_mem (for VACUUM, CREATE INDEX, 256MB-2GB)
- Configure effective_cache_size (50-75% of total RAM)
- Tune temp_buffers for temporary tables (8MB-16MB)

Connection Management:
- Configure max_connections (100-500 based on workload)
- Implement connection pooling (PgBouncer, pgpool-II)
- Choose pooling mode (session, transaction, statement)
- Configure pool size (25-50 connections per app server)
- Set pool timeout and max client connections
- Implement read/write connection separation

Autovacuum Tuning:
- Configure autovacuum_naptime (frequency of autovacuum runs)
- Tune autovacuum_vacuum_scale_factor (0.1-0.2, lower for large tables)
- Set autovacuum_analyze_scale_factor (0.05-0.1)
- Configure autovacuum_max_workers (2-8 based on I/O capacity)
- Set autovacuum_vacuum_cost_delay (balancing I/O impact)
- Configure vacuum_cost_limit (200-1000 based on I/O)
- Plan manual VACUUM FULL for heavily bloated tables (requires downtime)

Checkpoint and WAL Configuration:
- Tune checkpoint_timeout (5min-15min based on write load)
- Configure checkpoint_completion_target (0.9, spread checkpoints)
- Set max_wal_size (1GB-16GB based on write load)
- Configure wal_buffers (16MB, -1 for auto)
- Tune synchronous_commit (off for performance, on for durability)
- Configure wal_compression (on for space savings)
- Set archive_mode and archive_command (for PITR backups)

Query Planner Configuration:
- Tune random_page_cost (1.1 for SSD, 4.0 for HDD)
- Configure seq_page_cost (1.0 baseline)
- Set effective_io_concurrency (200 for SSD, 2 for HDD)
- Configure default_statistics_target (100-1000 for complex queries)
- Set cpu_tuple_cost and cpu_index_tuple_cost (rare to change)

**Deliverables:**
- Optimized postgresql.conf with rationale for each setting
- Connection pooler configuration (pgbouncer.ini, pgpool.conf)
- Autovacuum tuning parameters with per-table overrides
- Checkpoint and WAL configuration with performance projections
- Configuration deployment plan (rolling restart, zero-downtime)
- Monitoring for new configuration (metrics to watch)
- Rollback plan if performance degrades

### Phase 4: Replication & High Availability (1.5-2.5 hours)
**Lead:** `postgresql-expert`, **Supporting:** `devops-engineer`

Read Replica Setup:
- Design replication topology (1 primary, N replicas)
- Configure streaming replication (replication slots, WAL level)
- Setup read replicas for read-heavy workloads
- Configure hot standby parameters (hot_standby, max_standby_delay)
- Implement connection routing (read queries → replicas, writes → primary)
- Plan replica lag monitoring and alerting
- Design replica failover procedures (manual or automatic)
- Configure cascading replication for geographically distributed replicas

Load Balancing:
- Implement read query load balancing (HAProxy, pgpool-II, DNS)
- Configure health checks (pg_isready, replication lag)
- Design routing rules (route by query type, user, database)
- Plan session affinity for transactions
- Configure connection limits per replica

High Availability:
- Design failover strategy (manual, automatic with Patroni/repmgr)
- Configure Patroni/repmgr for automatic failover
- Setup VIP or DNS for connection redirection
- Design split-brain prevention (fencing, quorum)
- Plan backup restoration procedures (PITR with WAL archives)
- Configure synchronous replication for zero data loss (synchronous_commit=on)
- Design disaster recovery runbook (failover, failback, rebuild replica)

Backup Strategy:
- Configure continuous archiving (WAL archiving to S3, NFS)
- Setup pg_basebackup for physical backups (full database snapshots)
- Implement logical backups (pg_dump, pg_dumpall) for disaster recovery
- Design backup retention policy (daily 7 days, weekly 4 weeks, monthly 12 months)
- Plan PITR (Point-in-Time Recovery) capability
- Test restore procedures (monthly restore drill)
- Configure backup monitoring and alerting

**Deliverables:**
- Replication architecture diagram (primary, replicas, load balancers)
- Replication configuration (postgresql.conf, recovery.conf, replication slots)
- Load balancer configuration (HAProxy, pgpool-II, DNS)
- Patroni/repmgr configuration for automatic failover
- Backup scripts and schedules (pg_basebackup, WAL archiving)
- Disaster recovery runbook (failover procedures, restore steps)
- Replication monitoring dashboards (lag, streaming status)
- Failover testing report (successful failover test)

### Phase 5: Monitoring, Alerting & Operational Excellence (1-2 hours)
**Lead:** `devops-engineer`, **Supporting:** `postgresql-expert`

Monitoring Setup:
- Deploy PostgreSQL exporter (postgres_exporter for Prometheus)
- Configure Grafana dashboards (query performance, connections, replication)
- Setup slow query logging (pg_stat_statements, auto_explain)
- Monitor cache hit ratios (buffer cache, table cache, index cache)
- Track table and index bloat (pgstattuple extension)
- Monitor replication lag (pg_stat_replication)
- Track connection pool utilization (PgBouncer stats)
- Monitor disk usage and I/O (pg_stat_io, iostat)
- Track lock contention (pg_locks, pg_stat_activity)
- Monitor autovacuum activity (pg_stat_progress_vacuum)

Alerting Configuration:
- Alert on high replication lag (>1s for sync, >10s for async)
- Alert on connection saturation (>80% of max_connections)
- Alert on cache hit ratio drops (<95%)
- Alert on long-running queries (>5 minutes)
- Alert on table/index bloat (>50% bloat)
- Alert on disk space (>80% full)
- Alert on autovacuum disabled or failing
- Alert on query performance regression (p95 latency increase)
- Alert on failover events (primary down, replica promoted)

Performance Baselines:
- Document baseline metrics (query latency, throughput, connections)
- Create performance regression tests (continuous benchmarking)
- Track query performance over time (pg_stat_statements history)
- Monitor slow query trends (increasing frequency, new slow queries)
- Track database size growth (table, index, total database)
- Document performance targets (SLAs, p50/p95/p99 latency)

Operational Procedures:
- Document routine maintenance procedures (VACUUM, REINDEX, ANALYZE)
- Create runbooks for common issues (connection saturation, slow queries, replication lag)
- Plan capacity management (storage, connections, compute)
- Design performance review cadence (weekly, monthly)
- Create incident response procedures (query killed, database down, replica lag)
- Document configuration change procedures (review, test, deploy, rollback)
- Plan database upgrade strategy (minor versions, major versions)

**Deliverables:**
- Grafana dashboards for database monitoring (query, connections, replication, system)
- Prometheus alerts for critical issues (pagerduty, slack)
- Monitoring runbooks (what alerts mean, how to respond)
- Performance baseline documentation (before optimization metrics)
- Operational runbooks (routine maintenance, incident response)
- Capacity planning report (growth projections, scaling recommendations)
- Post-optimization performance report (improvements achieved)
- Knowledge transfer documentation (how to interpret metrics, tune database)

### Phase 6: Security Assessment & Hardening (1.5-2 hours)
**Lead:** `security-audit-specialist`, **Supporting:** `postgresql-expert`

Authentication & Access Control:
- Review authentication mechanisms (password policies, MFA, certificate authentication)
- Audit user accounts, roles, and privilege assignments (principle of least privilege)
- Identify overprivileged accounts (users with SUPERUSER, DBA, root access)
- Validate network security (firewall rules, VPC isolation, private subnets)
- Review connection encryption (SSL/TLS enforcement, certificate validation)

Data Protection:
- Assess encryption at rest (transparent data encryption, encrypted volumes)
- Validate backup encryption and secure storage
- Review data masking for non-production environments
- Assess SQL injection vulnerability surface (prepared statements, input validation)
- Audit logging configuration and retention policies

Compliance & Governance:
- Review compliance requirements (PCI DSS, HIPAA, GDPR, SOC 2)
- Validate audit trail implementation
- Assess data retention and deletion policies
- Review access control matrix
- Document security policies and procedures

**Deliverables:**
- User privilege audit report identifying overprivileged accounts
- Security vulnerability findings with CVSS scores and remediation steps
- Access control matrix showing who can access what data
- Encryption status report (in-transit, at-rest, backup encryption)
- Compliance gap analysis against required standards
- Security hardening checklist with implementation priorities

### Phase 7: Schema Quality & Data Integrity (1.5-2 hours)
**Lead:** `data-engineer`, **Supporting:** `postgresql-expert`

Schema Design Assessment:
- Assess normalization levels and identify denormalization trade-offs
- Review data type choices for efficiency and correctness
- Validate constraint usage (primary keys, foreign keys, unique, check)
- Evaluate naming conventions and schema organization consistency
- Identify missing foreign key relationships
- Review temporal data handling (timestamps, soft deletes, audit trails)
- Identify schema anti-patterns (EAV, over-normalization, polymorphic associations)

Data Quality Validation:
- Validate referential integrity (orphaned records, dangling foreign keys)
- Identify NULL values in critical columns without NOT NULL constraints
- Assess data consistency across related tables
- Review data validation rules and check constraints
- Identify duplicate records and data quality issues
- Evaluate data lineage and transformation documentation
- Assess data governance policies

**Deliverables:**
- Schema quality scorecard with normalization assessment
- Data type optimization recommendations
- Missing constraint recommendations
- Data integrity violation report
- Data quality monitoring queries
- Schema refactoring recommendations for identified anti-patterns

## Expected Outcomes

### Performance Improvements
- **Query latency**: 50-90% reduction in p95 latency for slow queries
- **Throughput**: 2-5x increase in queries per second
- **Cache hit ratio**: >95% buffer cache hit rate (from 70-80% untuned)
- **Connection efficiency**: 50-70% reduction in active connections via pooling
- **Index efficiency**: >95% of queries using indexes (reduce sequential scans)
- **Replication lag**: <1s for synchronous, <5s for asynchronous replicas
- **Bloat reduction**: <20% table/index bloat (from 50%+ untuned)

### Security & Compliance
- **Access control**: Zero overprivileged accounts, principle of least privilege
- **Encryption**: 100% data encrypted at rest and in transit
- **Vulnerability remediation**: All critical vulnerabilities patched
- **Compliance**: GDPR, HIPAA, PCI DSS, SOC 2 requirements met
- **Audit trails**: Complete audit logging for compliance
- **SQL injection protection**: 100% prepared statements

### Data Quality
- **Referential integrity**: Zero orphaned records
- **Data consistency**: 100% constraint enforcement
- **Schema quality**: Properly normalized (3NF) or justified denormalization
- **Naming conventions**: Consistent across all database objects
- **Data validation**: Check constraints for business rules
- **Documentation**: Complete schema and data lineage documentation

### Operational Excellence
- **Monitoring**: Real-time dashboards for all key metrics
- **Alerting**: Proactive alerts before user-facing issues
- **High availability**: Automatic failover with <30s downtime
- **Backup and recovery**: Tested restore procedures, PITR capability
- **Capacity planning**: Growth projections and scaling recommendations
- **Runbooks**: Documented procedures for common issues
- **Knowledge transfer**: Team trained on optimization and troubleshooting

### Business Value
- **Faster application**: Users experience 50-90% faster page loads
- **Higher capacity**: Support 2-5x more concurrent users
- **Reduced costs**: Smaller database instances (better resource utilization)
- **Better reliability**: 99.95%+ uptime with automatic failover
- **Easier scaling**: Read replicas handle growth
- **Compliance ready**: Meet regulatory requirements
- **Reduced risk**: Security vulnerabilities eliminated
- **Faster development**: Clean schema, optimized queries

## Usage

```bash
# Full database quality review and optimization (all phases)
/database-optimization --comprehensive=true

# Performance-focused optimization only
/database-optimization --focus=performance

# Security and compliance review
/database-optimization --focus=security --compliance=hipaa,gdpr

# Schema quality and data integrity assessment
/database-optimization --focus=schema-quality

# Optimize PostgreSQL database with slow queries
/database-optimization --database=postgresql --issue=slow-queries

# Setup replication and high availability
/database-optimization --database=postgresql --setup=replication

# Optimize for read-heavy workload
/database-optimization --workload=read-heavy --replicas=3

# Pre-production readiness assessment
/database-optimization --assessment=production-readiness
```

## Prerequisites

- [ ] Database access (superuser or rds_superuser for AWS RDS)
- [ ] PostgreSQL version identified (9.6+, 12+ recommended)
- [ ] Current performance metrics collected (baseline)
- [ ] Slow query logs enabled (pg_stat_statements extension)
- [ ] Maintenance window scheduled (for some operations)
- [ ] Backup tested and verified (before making changes)
- [ ] Monitoring infrastructure available (Prometheus, Grafana)
- [ ] Replica servers available (for replication setup)

## Success Criteria

### Performance Optimization
- [ ] Top 20 slow queries optimized (50%+ latency reduction)
- [ ] Missing indexes created (>95% index usage)
- [ ] Unused indexes removed (reduce bloat, improve write performance)
- [ ] Configuration tuned (postgresql.conf optimized)
- [ ] Connection pooling implemented (50%+ connection reduction)
- [ ] Cache hit ratio >95% (buffer cache, index cache)
- [ ] Autovacuum tuned (bloat <20%)
- [ ] Query performance regression tests passing

### High Availability
- [ ] Read replicas configured (1-3 replicas)
- [ ] Replication lag <1s (synchronous) or <5s (asynchronous)
- [ ] Load balancing configured (HAProxy, pgpool-II, DNS)
- [ ] Automatic failover tested (Patroni, repmgr)
- [ ] Backup and restore tested (PITR, pg_basebackup)
- [ ] Disaster recovery runbook documented
- [ ] Failover testing completed (manual failover successful)

### Security & Compliance
- [ ] User privileges audited and minimized
- [ ] Encryption enabled (at-rest, in-transit, backups)
- [ ] Critical vulnerabilities remediated
- [ ] SQL injection protection verified
- [ ] Compliance requirements validated (GDPR, HIPAA, etc.)
- [ ] Audit logging configured and tested
- [ ] Access control matrix documented

### Schema & Data Quality
- [ ] Schema normalization validated (3NF or justified denormalization)
- [ ] Data types optimized for storage and performance
- [ ] Referential integrity enforced (foreign keys, constraints)
- [ ] Orphaned records identified and cleaned
- [ ] Naming conventions standardized
- [ ] Data validation rules implemented
- [ ] Schema documentation generated

### Monitoring & Operations
- [ ] Grafana dashboards deployed (query, connections, replication, system)
- [ ] Prometheus alerts configured (lag, connections, bloat, disk)
- [ ] Slow query logging operational (pg_stat_statements)
- [ ] Baseline metrics documented (before optimization)
- [ ] Performance targets defined (SLAs, p95 latency)
- [ ] Runbooks created (maintenance, incident response)
- [ ] Team trained (database optimization, troubleshooting)

## Real-World Examples

### Example 1: E-commerce Platform (PostgreSQL 14)
**Optimization Time:** 8 hours

**Starting State:**
- 150K queries/day, p95 latency 2.5s
- 50% cache hit ratio (excessive disk I/O)
- 200 connections (80% saturation, frequent timeouts)
- No replication (single point of failure)
- 65% table bloat (autovacuum overwhelmed)

**Optimizations Applied:**

**Phase 1: Audit** (1.5 hours)
- Identified 15 N+1 query patterns in checkout flow
- Found 12 missing indexes on foreign keys
- Discovered 8 unused indexes (never used in 30 days)
- Identified autovacuum not keeping up (vacuum running 24/7)

**Phase 2: Query Optimization** (2 hours)
- Rewrote 15 N+1 queries with JOINs (95% latency reduction)
- Created 12 missing indexes (order_items(order_id), products(category_id), etc.)
- Removed 8 unused indexes (5% write performance improvement)
- Created materialized view for sales dashboard (refresh hourly)
- Implemented covering index for order summary queries (index-only scans)

**Phase 3: Configuration Tuning** (1.5 hours)
- Increased shared_buffers: 256MB → 4GB
- Tuned work_mem: 4MB → 32MB (32 connections × 32MB = 1GB max)
- Configured PgBouncer (transaction mode, 25 pool size)
- Tuned autovacuum: scale_factor 0.2 → 0.05, max_workers 3 → 6
- Increased max_wal_size: 1GB → 4GB (fewer checkpoints)

**Phase 4: Replication** (2 hours)
- Setup 2 read replicas (read queries → replicas, writes → primary)
- Configured HAProxy for read query load balancing
- Setup Patroni for automatic failover (VIP switchover)
- Configured WAL archiving to S3 (PITR capability)
- Tested failover (successful, 15s downtime)

**Phase 5: Monitoring** (1 hour)
- Deployed Grafana dashboards (query, connections, replication, bloat)
- Configured alerts (lag >5s, connections >80%, cache hit <90%)
- Setup pg_stat_statements monitoring (weekly slow query review)

**Impact:**
- **Query latency**: p95 2.5s → 180ms (93% reduction)
- **Throughput**: 150K → 600K queries/day (4x increase)
- **Cache hit ratio**: 50% → 98% (48% improvement)
- **Connections**: 200 → 30 active (PgBouncer pooling, 85% reduction)
- **Bloat**: 65% → 15% (autovacuum keeping up)
- **Availability**: Single instance → HA with automatic failover (99.95% uptime)
- **Black Friday**: Handled 10x traffic with no downtime (read replicas scaled)
- **Cost savings**: Delayed vertical scaling by 12 months ($8K/month savings)

### Example 2: SaaS Multi-Tenant Database (PostgreSQL 15)
**Optimization Time:** 7 hours

**Starting State:**
- 5,000 tenants, 500GB database
- Slow dashboard queries (10-30s p95)
- Frequent lock contention (tenant analytics blocking writes)
- No partitioning (single 200GB table)
- Backup taking 4 hours (impacting performance)

**Optimizations Applied:**

**Query Optimization:**
- Rewrote dashboard queries with CTEs and window functions (80% faster)
- Created composite indexes on (workspace_id, created_at) for tenant queries
- Implemented partial indexes for active records (WHERE deleted_at IS NULL)
- Created materialized views for per-tenant dashboards (refresh every 5 minutes)

**Partitioning:**
- Partitioned large events table by month (declarative partitioning)
- Created 24 partitions (2 years of monthly partitions)
- Configured auto-partition creation (pg_partman extension)
- Pruned old partitions (drop partitions older than 2 years)

**Configuration:**
- Implemented statement timeout (30s) to prevent runaway queries
- Configured row-level security (RLS) for tenant isolation
- Tuned autovacuum per table (events table: aggressive, users table: less frequent)
- Increased maintenance_work_mem to 2GB (faster CREATE INDEX)

**Replication & Backup:**
- Setup 3 read replicas in different AZs (geographic distribution)
- Routed analytics queries to dedicated replica (isolated from prod load)
- Switched to pg_basebackup with WAL streaming (30min backups vs 4 hours)
- Implemented pgBackRest for incremental backups (daily full, hourly incremental)

**Impact:**
- **Dashboard latency**: p95 30s → 1.2s (96% reduction)
- **Lock contention**: Eliminated (analytics on read replica)
- **Partitioning**: Queries 10x faster (partition pruning)
- **Backup time**: 4 hours → 30 minutes (pg_basebackup, no performance impact)
- **Scalability**: Supports 10K tenants (2x growth)
- **Compliance**: GDPR-compliant tenant data deletion (drop partition vs DELETE)

### Example 3: Time-Series IoT Database (PostgreSQL + TimescaleDB)
**Optimization Time:** 6.5 hours

**Starting State:**
- 100K data points/second ingest
- 2TB of raw telemetry data (growing 500GB/month)
- Slow aggregation queries (1-2 minutes for hourly rollups)
- Retention policy manual (DBA deleting old data monthly)

**Optimizations Applied:**

**TimescaleDB Hypertables:**
- Converted raw_telemetry table to hypertable (automatic time partitioning)
- Created continuous aggregates for 1min, 1hour, 1day rollups (real-time materialized views)
- Configured refresh policies (1min: real-time, 1hour: every 10min, 1day: hourly)

**Compression:**
- Enabled compression on chunks older than 7 days (95% compression ratio)
- Configured compression policy (automatic after 7 days)
- Compressed historical data (2TB → 100GB, $900/month storage savings)

**Retention:**
- Configured retention policies (raw: 90 days, 1min: 1 year, 1hour: 2 years, 1day: forever)
- Automated chunk dropping (no manual data deletion)

**Indexing:**
- Created composite indexes on (device_id, time DESC) for device queries
- Implemented BRIN indexes on time column (minimal index size for time-series)

**Replication:**
- Setup 2 read replicas for analytics workloads
- Configured connection pooling (PgBouncer: 500 ingest connections → 25 database connections)

**Impact:**
- **Ingest performance**: 100K → 200K data points/second (compression async)
- **Aggregation queries**: 1-2min → 50-200ms (continuous aggregates)
- **Storage**: 2TB → 100GB (95% compression)
- **Storage cost**: $1K/month → $100/month (90% savings)
- **Retention**: Manual → automatic (retention policies)
- **Query performance**: 10x faster (hypertable partitioning + compression)

## Related Commands

- `/database-design` - Design new database schema from scratch
- `/api-design` - Optimize API data access patterns
- `/quality:performance-audit` - Application-level performance review
- `/quality:security-audit` - Application security assessment
- `/quality:production-readiness` - Pre-deployment checklist

## Notes

**When to Optimize:**
- p95 query latency >200ms (user-facing performance issues)
- Cache hit ratio <90% (excessive disk I/O)
- Connection saturation >80% (timeouts, slow connections)
- Table/index bloat >50% (autovacuum not keeping up)
- Replication lag >5s (stale data on replicas)
- Frequent lock contention (blocking queries, deadlocks)
- Database size growth concerns (storage costs, backup time)

**Performance Targets:**
- **Query latency**: p95 <100ms (OLTP), p95 <5s (analytics)
- **Cache hit ratio**: >95% (buffer cache)
- **Connection utilization**: 50-70% (not saturated, not under-utilized)
- **Index usage**: >95% of queries use indexes
- **Bloat**: <20% for tables and indexes
- **Replication lag**: <1s (synchronous), <5s (asynchronous)
- **Backup time**: <1 hour for full backup

**Common Bottlenecks:**

**1. Missing Indexes:**
- Sequential scans on large tables
- Solution: CREATE INDEX on WHERE/JOIN columns

**2. Unused Indexes:**
- Slow writes, bloat, wasted space
- Solution: DROP INDEX for unused indexes

**3. N+1 Queries:**
- Application queries in loops (10 queries → 1000 queries)
- Solution: Eager loading, JOINs, or batch queries

**4. Poor Connection Management:**
- Too many connections, connection churn
- Solution: Connection pooling (PgBouncer, pgpool-II)

**5. Autovacuum Not Keeping Up:**
- Table/index bloat, slow queries
- Solution: Tune autovacuum settings, manual VACUUM

**6. Inefficient Queries:**
- Suboptimal execution plans
- Solution: Rewrite queries, update statistics, tune planner

**7. Configuration Defaults:**
- PostgreSQL defaults are conservative (small shared_buffers)
- Solution: Tune for production workloads

**8. No Replication:**
- Single point of failure, read scalability limits
- Solution: Setup read replicas, automatic failover

**When to Use This vs `/database-design`:**
- **Use `/database-design`**: When creating a NEW database schema from scratch
- **Use `/database-optimization`**: For EXISTING databases that need performance tuning, security hardening, quality assessment, or operational improvements

This workflow ensures databases are optimized, secure, reliable, and operationally excellent for production workloads.
