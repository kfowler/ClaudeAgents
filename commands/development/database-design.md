---
name: database-design
description: "Comprehensive database schema design workflow coordinating data-engineer and full-stack-architect for production-ready database architecture with migrations, indexing, and performance optimization"
agents:
  - data-engineer
  - full-stack-architect
complexity: medium-high
duration: 4-6 hours
---

# Database Design Workflow

**Command:** `/database-design`
**Agents:** `data-engineer`, `full-stack-architect`
**Complexity:** Medium-High
**Duration:** 4-6 hours

## Overview

Comprehensive database schema design workflow that coordinates database engineering and backend architecture to create production-ready database schemas with proper normalization, indexing, migrations, and performance optimization.

## What This Command Does

This command orchestrates complete database design across 6 phases:

### Phase 1: Requirements & Data Modeling (45-60 min)
**Lead:** `data-engineer`

- Analyze application requirements and data access patterns
- Identify entities, relationships, and constraints
- Choose database type (SQL vs NoSQL vs hybrid)
- Define data integrity and consistency requirements
- Plan for scalability and performance needs
- Identify compliance and security requirements (GDPR, HIPAA, etc.)

**Deliverables:**
- Data requirements document
- Database technology selection (PostgreSQL, MySQL, MongoDB, etc.)
- Entity list with attributes
- Relationship mapping (one-to-one, one-to-many, many-to-many)
- Data access pattern analysis

### Phase 2: Schema Design & Normalization (1-1.5 hours)
**Lead:** `data-engineer`

- Create entity-relationship diagrams (ERD)
- Design tables, columns, data types, constraints
- Apply normalization (1NF, 2NF, 3NF) or denormalization strategy
- Define primary keys, foreign keys, unique constraints
- Design composite keys and surrogate keys
- Plan for soft deletes and audit trails (created_at, updated_at, deleted_at)
- Design data validation rules and check constraints

**Deliverables:**
- ERD diagram (Mermaid, dbdiagram.io, or similar)
- Normalized schema design (or justified denormalization)
- Table definitions with all columns and types
- Constraint definitions (PK, FK, unique, check)
- Data type selection rationale

### Phase 3: Indexing Strategy & Performance (1-1.5 hours)
**Lead:** `data-engineer`, **Supporting:** `full-stack-architect`

- Analyze query patterns from application design
- Design single-column indexes for frequently queried fields
- Create composite indexes for multi-column queries
- Plan partial indexes for filtered queries
- Design full-text search indexes (PostgreSQL: GIN, MySQL: FULLTEXT)
- Plan covering indexes for index-only scans
- Design indexes for foreign keys and join columns
- Plan index maintenance strategy (REINDEX, ANALYZE)

**Deliverables:**
- Index design document with query patterns
- Composite index strategy (column order optimization)
- Partial index conditions
- Full-text search configuration
- Index bloat monitoring plan
- Query execution plan examples (EXPLAIN ANALYZE)

### Phase 4: Migrations & Version Control (45-60 min)
**Lead:** `data-engineer`

- Choose migration framework (Flyway, Liquibase, Alembic, Prisma Migrate, etc.)
- Create initial schema migration (V1__initial_schema.sql)
- Design migration rollback strategy
- Plan for zero-downtime migrations (expand-contract pattern)
- Create seed data migrations for initial setup
- Design migration testing strategy
- Plan for production migration execution

**Deliverables:**
- Migration files (up and down migrations)
- Migration execution plan with rollback procedures
- Seed data scripts
- Zero-downtime migration strategy (if needed)
- Migration testing checklist

### Phase 5: Advanced Features & Optimization (1-1.5 hours)
**Lead:** `data-engineer`, **Supporting:** `full-stack-architect`

Advanced Database Features:
- Design materialized views for complex queries and reporting
- Plan partitioning strategy for large tables (range, list, hash)
- Design database triggers for business logic (audit logs, cascades)
- Plan stored procedures for complex operations
- Design database functions for reusable logic
- Plan database-level security (row-level security, column encryption)
- Design replication and backup strategy

Performance Optimization:
- Configure connection pooling (PgBouncer, pgpool, MySQL Proxy)
- Plan read replica strategy for read-heavy workloads
- Design caching strategy at database level
- Plan query optimization and slow query monitoring
- Design database vacuum and maintenance schedules
- Plan for database scaling (vertical, horizontal, sharding)

**Deliverables:**
- Materialized view definitions
- Partitioning strategy and implementation
- Trigger and stored procedure design
- Connection pooling configuration
- Read replica architecture
- Database maintenance schedule
- Scaling strategy and sharding plan (if applicable)

### Phase 6: Documentation & Monitoring (30-45 min)
**Lead:** `data-engineer`

- Create database schema documentation (auto-generated from schema)
- Document all tables, columns, relationships, constraints
- Create query performance guidelines
- Design database monitoring strategy (pg_stat_statements, slow query log)
- Plan alerting for database health (connection saturation, disk space, replication lag)
- Create database access control documentation (roles, permissions)
- Design database disaster recovery plan

**Deliverables:**
- Database schema documentation (SchemaSpy, dbdocs, etc.)
- Query performance guidelines
- Monitoring dashboard specification (Grafana, Datadog, etc.)
- Alert thresholds and escalation policy
- Access control matrix (who can access what)
- Disaster recovery runbook (backup, restore, failover)

## Expected Outcomes

### Database Design Artifacts
- **ERD diagram** with all entities, relationships, and cardinality
- **Migration files** ready to execute (up and down migrations)
- **Index strategy** optimized for application query patterns
- **Performance configuration** (connection pooling, read replicas)
- **Monitoring and alerting** setup for database health
- **Disaster recovery plan** with backup and restore procedures

### Design Quality
- **Normalized schema** (3NF) or justified denormalization for performance
- **Referential integrity** enforced through foreign keys and constraints
- **Optimized indexes** matching query patterns (80%+ queries use indexes)
- **Scalable architecture** supporting horizontal and vertical scaling
- **Well-documented** schema with clear naming conventions
- **Security by design** (row-level security, encryption, access control)
- **Performance targets** met (query p95 <100ms, connection pool <70% utilization)

### Business Value
- **Faster queries** with optimized indexes (50-80% improvement)
- **Data integrity** through constraints and validation
- **Easier maintenance** with clear migrations and documentation
- **Scalability** for future growth (10x traffic capacity)
- **Reduced downtime** through zero-downtime migrations
- **Compliance** with data regulations (GDPR, HIPAA, SOC 2)

## Usage

```bash
# Design PostgreSQL database for e-commerce
/database-design --database=postgresql --domain=ecommerce

# Design MongoDB schema for social network
/database-design --database=mongodb --domain=social

# Design MySQL database with read replicas
/database-design --database=mysql --replicas=true

# Design time-series database for IoT platform
/database-design --database=timescaledb --domain=iot
```

## Prerequisites

- [ ] Application requirements defined (features, data needs)
- [ ] Database technology selected (PostgreSQL, MySQL, MongoDB, etc.)
- [ ] Data access patterns understood (queries, frequency, volume)
- [ ] Performance requirements known (SLA, concurrent connections)
- [ ] Compliance requirements identified (GDPR, HIPAA, etc.)
- [ ] Scalability needs defined (expected growth, traffic patterns)

## Success Criteria

### Schema Design
- [ ] ERD diagram complete with all entities and relationships
- [ ] All tables designed with appropriate data types
- [ ] Primary and foreign keys defined
- [ ] Constraints implemented (unique, check, not null)
- [ ] Normalization applied (3NF) or denormalization justified
- [ ] Audit trails designed (created_at, updated_at, deleted_at)

### Performance Optimization
- [ ] Indexes designed for all frequently queried columns
- [ ] Composite indexes for multi-column queries
- [ ] Query patterns analyzed with execution plans
- [ ] Connection pooling configured
- [ ] Read replicas planned for read-heavy workloads
- [ ] Materialized views for complex aggregations
- [ ] Partitioning strategy for large tables (if needed)

### Migrations & Version Control
- [ ] Migration framework selected and configured
- [ ] Initial schema migration created (V1)
- [ ] Rollback migrations designed
- [ ] Zero-downtime migration strategy (if needed)
- [ ] Seed data migrations created
- [ ] Migration testing checklist complete

### Monitoring & Operations
- [ ] Database monitoring configured (metrics, logs)
- [ ] Alerts defined (connections, disk, replication lag)
- [ ] Backup and restore procedures documented
- [ ] Disaster recovery plan created
- [ ] Access control matrix documented
- [ ] Performance guidelines established

## Real-World Examples

### Example 1: E-commerce Database (PostgreSQL)
**Design Time:** 5 hours

Schema Designed:
- 15 tables: users, products, orders, cart_items, payments, inventory, etc.
- 42 indexes: composite for (user_id, created_at), partial for active products
- 8 foreign keys with cascading deletes
- Row-level security for multi-tenant isolation
- Materialized view for sales analytics (refreshed hourly)

Delivered:
- ERD with all relationships
- 12 migration files (initial + enhancements)
- Connection pool: PgBouncer (100 connections, transaction mode)
- Read replicas: 2 replicas for reporting queries
- Partitioning: orders table by month (12 partitions)

Impact:
- Query performance: p95 45ms (vs 520ms before indexing)
- Zero downtime deployments with expand-contract pattern
- 99.95% uptime with automated failover
- Supports 10K concurrent users

### Example 2: SaaS Multi-Tenant Database (PostgreSQL)
**Design Time:** 6 hours

Schema Designed:
- 18 tables with workspace_id for tenant isolation
- Row-level security (RLS) policies per tenant
- Composite indexes on (workspace_id, <query_column>)
- Materialized views for per-tenant analytics
- Soft deletes with deleted_at timestamps

Delivered:
- RLS policies enforcing tenant isolation at database level
- Connection pooling with tenant-aware routing
- Automated daily backups with 30-day retention
- Replication to EU region for GDPR compliance
- Query monitoring with pg_stat_statements

Impact:
- 100% tenant data isolation (RLS enforced)
- Sub-100ms queries across all tenants
- GDPR compliant with data residency
- Scaled to 5,000 tenants without redesign

### Example 3: Time-Series IoT Database (TimescaleDB)
**Design Time:** 5.5 hours

Schema Designed:
- Hypertables for telemetry data (auto-partitioned by time)
- Continuous aggregates for 1min, 1hour, 1day rollups
- Compression policies (7 days uncompressed, then compress)
- Retention policies (90 days hot, 2 years cold, then delete)
- Indexes on device_id and sensor_type

Delivered:
- 3 hypertables: raw_telemetry, device_events, alerts
- 6 continuous aggregates (real-time rollups)
- Compression: 95% storage savings after 7 days
- Retention: Automated data lifecycle management
- Read replicas for analytics workloads

Impact:
- Ingestion: 100K data points/second sustained
- Query latency: <100ms for 1 year of data
- Storage: 95% reduction through compression
- Cost savings: $8K/month on storage

## Related Commands

- `/api-design` - API design (integrates with database schema)
- `/quality:performance-audit` - Database performance review
- `/security-audit` - Database security assessment
- `/data-migration` - Data migration planning and execution

## Notes

**Database Technology Choice:**
- **PostgreSQL**: Best for complex queries, ACID compliance, JSON support, extensions
- **MySQL**: Best for read-heavy workloads, simple queries, wide hosting support
- **MongoDB**: Best for flexible schema, nested documents, horizontal scaling
- **TimescaleDB**: Best for time-series data, IoT, real-time analytics

**Normalization vs Denormalization:**
- **Normalize (3NF)** for: OLTP systems, data integrity, avoiding update anomalies
- **Denormalize** for: Read-heavy systems, performance optimization, reducing JOINs
- **Hybrid**: Normalize for writes, denormalize for reads (materialized views, caching)

**Indexing Best Practices:**
- Index foreign keys (for JOINs)
- Index frequently filtered columns (WHERE clauses)
- Use composite indexes for multi-column queries (most selective column first)
- Avoid over-indexing (indexes slow down writes)
- Monitor index usage and remove unused indexes

**Migration Strategies:**
- **Blue-Green**: Deploy new schema, switch traffic (requires double resources)
- **Expand-Contract**: Add new columns, migrate data, remove old columns (zero downtime)
- **Read Replicas**: Migrate replica, promote to primary (minimal downtime)

**Performance Targets:**
- Query execution: p95 <100ms, p99 <300ms
- Connection pool utilization: 50-70% (not saturated)
- Index hit rate: >95% (most queries use indexes)
- Buffer cache hit rate: >95% (data in memory)
- Replication lag: <500ms for read replicas

This workflow ensures databases are well-designed, performant, scalable, and maintainable from day one.
