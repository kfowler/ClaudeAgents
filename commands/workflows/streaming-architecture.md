---
name: streaming-architecture
description: "Real-time data streaming architecture workflow coordinating Kafka expert, data engineer, backend API engineer, and DevOps for event-driven systems with Apache Kafka"
agents:
  - kafka-expert
  - data-engineer
  - backend-api-engineer
  - devops-engineer
  - project-orchestrator
complexity: high
duration: 8-12 hours
---

# Streaming Architecture Workflow

**Command:** `/streaming-architecture`
**Agents:** `project-orchestrator`, `kafka-expert`, `data-engineer`, `backend-api-engineer`, `devops-engineer`
**Complexity:** High
**Duration:** 8-12 hours

## Overview

Comprehensive real-time data streaming architecture workflow that coordinates Kafka specialists, data engineers, backend engineers, and DevOps to design and implement event-driven systems with Apache Kafka for high-throughput, low-latency data pipelines.

## What This Command Does

This command orchestrates streaming architecture design across 5 phases:

### Phase 1: Architecture Design & Use Case Analysis (2-2.5 hours)
**Lead:** `project-orchestrator`, **Supporting:** `kafka-expert`, `data-engineer`

Use Case Identification:
- Analyze streaming requirements (real-time analytics, event sourcing, CDC, microservices communication)
- Define data sources (databases, APIs, IoT devices, application events)
- Identify data consumers (analytics dashboards, data warehouses, microservices, ML models)
- Determine latency requirements (sub-second, seconds, minutes)
- Define throughput requirements (events/second, data volume)
- Plan data retention policies (hours, days, weeks, months)
- Identify data transformations needed (enrichment, aggregation, filtering)
- Define exactly-once vs at-least-once delivery semantics

Architecture Patterns:
- **Event-Driven Microservices**: Asynchronous communication between services
- **Event Sourcing**: Store all state changes as events (audit trail, replay)
- **CQRS**: Separate read and write models (command/query responsibility segregation)
- **Change Data Capture (CDC)**: Stream database changes (Debezium, Maxwell)
- **Stream Processing**: Real-time ETL, aggregations, joins (Kafka Streams, Flink)
- **Log Aggregation**: Centralized logging (application logs, system logs)
- **Metrics & Monitoring**: Real-time metrics aggregation (Prometheus, Datadog)
- **Real-Time Analytics**: Live dashboards, anomaly detection

Technology Stack:
- **Message Broker**: Apache Kafka (distributed, durable, high-throughput)
- **Schema Registry**: Confluent Schema Registry, AWS Glue Schema Registry (Avro, Protobuf, JSON Schema)
- **Stream Processing**: Kafka Streams, Apache Flink, Apache Spark Streaming
- **CDC**: Debezium, Maxwell's Daemon, AWS DMS
- **Connectors**: Kafka Connect (source and sink connectors)
- **Monitoring**: Prometheus, Grafana, Kafka Manager, Confluent Control Center

**Deliverables:**
- Streaming architecture diagram (data sources, Kafka, consumers, sinks)
- Use case documentation (what streams exist, why, who consumes)
- Technology stack selection with rationale
- Latency and throughput requirements per stream
- Data retention policies per topic
- Architecture pattern selection (event sourcing, CQRS, CDC, etc.)
- Risk assessment (data loss, ordering, duplicates)

### Phase 2: Kafka Cluster Design & Topic Planning (2-2.5 hours)
**Lead:** `kafka-expert`, **Supporting:** `devops-engineer`

Kafka Cluster Design:
- Design cluster size (3-node minimum for HA, 5-7 nodes for production)
- Plan broker configuration (num.network.threads, num.io.threads, socket buffer sizes)
- Configure replication factor (3 for production, 2 for dev/staging)
- Set min.insync.replicas (2 for durability, 1 for performance)
- Design partition distribution (even distribution across brokers)
- Plan for horizontal scaling (add brokers, rebalance partitions)
- Configure rack awareness (distribute replicas across availability zones)
- Design ZooKeeper ensemble (3 or 5 nodes) or KRaft mode (Kafka 3.3+)

Topic Design:
- Design topic naming conventions (domain.entity.event, e.g., orders.created, users.updated)
- Determine partition count per topic (start with 3-6, scale to 30-100 for high throughput)
- Configure replication factor per topic (3 for critical, 2 for non-critical)
- Set retention policies (time-based: 7 days, size-based: 100GB, compact for CDC)
- Configure log compaction for keyed topics (retain latest per key, e.g., user state)
- Design partition key strategy (user_id, order_id, null for round-robin)
- Plan for topic evolution (adding fields, deprecating topics)
- Configure cleanup policy (delete for time-series, compact for state)

Message Schema Design:
- Choose schema format (Avro for efficient serialization, Protobuf for compatibility, JSON for flexibility)
- Design message schemas with backward/forward compatibility
- Configure Schema Registry (subject naming strategy, compatibility mode)
- Design event envelope (metadata: timestamp, event_id, source, version)
- Plan schema evolution strategy (add fields with defaults, never remove required fields)
- Design dead letter topics (invalid messages, deserialization errors)
- Implement schema versioning (v1, v2 subjects)

Kafka Configuration:
- Configure log.retention.hours (168 hours = 7 days default)
- Set log.segment.bytes (1GB default, tune for retention policy)
- Configure compression.type (lz4 for performance, gzip for size)
- Set batch.size and linger.ms (batching for throughput)
- Configure acks (all for durability, 1 for performance)
- Set max.in.flight.requests.per.connection (5 for throughput, 1 for ordering)
- Configure transaction.timeout.ms (for exactly-once semantics)

**Deliverables:**
- Kafka cluster architecture diagram (brokers, ZooKeeper/KRaft, partitions)
- Topic catalog (topic names, partitions, replication, retention)
- Message schema definitions (Avro schemas, Protobuf definitions)
- Kafka broker configuration (server.properties)
- Schema Registry configuration (compatibility modes, subjects)
- Partition key strategy documentation
- Topic creation scripts (kafka-topics.sh commands)
- Capacity planning (storage, network, throughput projections)

### Phase 3: Producer & Consumer Implementation (2-3 hours)
**Lead:** `backend-api-engineer`, **Supporting:** `kafka-expert`

Producer Implementation:
- Design producer applications (microservices, CDC connectors, log shippers)
- Configure producer settings (acks, retries, batch.size, linger.ms)
- Implement idempotent producers (enable.idempotence=true)
- Design message keys (partition by user_id, order_id, or null for round-robin)
- Implement serialization (Avro, Protobuf, JSON with schema validation)
- Handle producer errors (retriable vs fatal, dead letter topics)
- Implement producer metrics (send latency, failure rate, record count)
- Design backpressure handling (queue limits, circuit breakers)
- Implement exactly-once semantics with transactions (if needed)

Kafka Connect Source Connectors:
- Configure JDBC source connector (CDC from databases)
- Setup Debezium connectors (PostgreSQL, MySQL, MongoDB CDC)
- Configure file source connector (log files, CSV files)
- Setup S3 source connector (batch file ingestion)
- Configure custom source connectors (REST APIs, FTP, etc.)
- Implement SMTs (Single Message Transforms) for data enrichment
- Configure connector error handling (tolerance, dead letter queues)

Consumer Implementation:
- Design consumer applications (microservices, analytics engines, data sinks)
- Configure consumer groups (group.id, partition assignment strategy)
- Set auto.offset.reset (earliest for new consumers, latest for existing)
- Configure max.poll.records (batch size for processing)
- Implement offset management (auto-commit vs manual commit)
- Handle deserialization errors (schema mismatches, dead letter topics)
- Implement idempotent consumers (deduplicate by event_id, database constraints)
- Design retry and error handling (exponential backoff, max retries)
- Implement consumer lag monitoring (consumer group lag alerts)
- Design graceful shutdown (commit offsets, close connections)

Kafka Connect Sink Connectors:
- Configure JDBC sink connector (stream to databases)
- Setup S3 sink connector (data lake ingestion, Parquet format)
- Configure Elasticsearch sink connector (search indexing)
- Setup HDFS sink connector (big data analytics)
- Configure custom sink connectors (HTTP, FTP, etc.)
- Implement SMTs (transforms, filtering, routing)
- Configure exactly-once delivery (idempotent writes, transactions)

**Deliverables:**
- Producer application code (Kafka producer libraries integrated)
- Consumer application code (Kafka consumer libraries integrated)
- Kafka Connect configurations (source and sink connectors)
- Message serialization/deserialization code (Avro, Protobuf)
- Producer metrics and monitoring (send rate, error rate, latency)
- Consumer metrics and monitoring (lag, throughput, processing time)
- Error handling implementation (retries, dead letter topics)
- Integration tests (producer to consumer end-to-end)

### Phase 4: Stream Processing & Transformations (2-3 hours)
**Lead:** `data-engineer`, **Supporting:** `kafka-expert`

Kafka Streams Applications:
- Design stream processing topology (sources, processors, sinks)
- Implement stateless transformations (map, filter, flatMap)
- Implement stateful transformations (aggregations, joins, windowing)
- Design state stores (RocksDB, in-memory, changelog topics)
- Implement windowed aggregations (tumbling, hopping, session windows)
- Implement stream-stream joins (inner, left, outer joins with time windows)
- Implement stream-table joins (enrich streams with reference data)
- Configure exactly-once processing (processing.guarantee=exactly_once_v2)
- Design repartitioning strategy (co-partitioning for joins)
- Implement interactive queries (query state stores via REST API)

Apache Flink Applications:
- Design Flink job topology (sources, operators, sinks)
- Implement event time processing (watermarks, late data handling)
- Configure checkpointing for fault tolerance (interval, timeout)
- Implement windowed computations (time windows, count windows, session windows)
- Implement complex event processing (pattern detection with CEP)
- Design broadcast state for global configuration updates
- Implement side outputs for multi-stream processing
- Configure savepoints for versioning and recovery
- Implement backpressure handling
- Design Flink cluster deployment (JobManager, TaskManagers)

Real-Time Analytics:
- Implement aggregations (count, sum, avg, min, max per window)
- Design materialized views (KSQL, Kafka Streams state stores)
- Implement anomaly detection (statistical thresholds, ML models)
- Design sessionization (user sessions from clickstream events)
- Implement funnel analysis (conversion rates, drop-offs)
- Design real-time dashboards (Grafana, Kibana, custom dashboards)
- Implement alerting (trigger alerts on thresholds, anomalies)

Data Enrichment:
- Implement stream-table joins (enrich events with user data, product data)
- Design reference data loading (compact topics, global stores)
- Implement geocoding (enrich with location data)
- Design fraud detection (enrich with risk scores, blacklists)
- Implement data normalization (standardize formats, units)

**Deliverables:**
- Kafka Streams application code (Java, Scala)
- Apache Flink job code (Java, Scala, Python)
- Stream processing topology diagrams
- State store design (local stores, changelog topics)
- Windowing strategy documentation
- Join implementation (co-partitioning, windowing)
- Real-time analytics queries (KSQL, Kafka Streams)
- Performance benchmarks (throughput, latency, state size)

### Phase 5: Operations, Monitoring & Deployment (2-3 hours)
**Lead:** `devops-engineer`, **Supporting:** `kafka-expert`

Kafka Cluster Deployment:
- Deploy Kafka brokers (Kubernetes, Docker, VMs, cloud-managed)
- Configure broker storage (SSD for low latency, HDD for cost)
- Setup ZooKeeper ensemble (3 or 5 nodes) or KRaft mode
- Configure broker networking (listeners, advertised.listeners)
- Implement TLS encryption (SSL for data in transit)
- Configure SASL authentication (SCRAM-SHA-512, OAuth)
- Implement ACLs for authorization (topic-level, consumer group-level)
- Configure log directories (RAID for redundancy, separate disks for ZooKeeper)

Monitoring & Observability:
- Deploy Kafka exporter (JMX metrics to Prometheus)
- Configure Grafana dashboards (broker metrics, topic metrics, consumer lag)
- Monitor broker health (under-replicated partitions, offline partitions)
- Track producer/consumer metrics (throughput, latency, error rate)
- Monitor consumer lag (critical metric for stream processing health)
- Configure alerting (high lag, broker down, under-replication)
- Monitor Kafka Connect (connector status, task failures)
- Track JVM metrics (heap usage, GC pauses, threads)
- Monitor disk usage (log retention, compaction progress)
- Implement distributed tracing (OpenTelemetry, Jaeger)

Performance Tuning:
- Tune producer batching (batch.size, linger.ms for throughput)
- Configure consumer fetch settings (fetch.min.bytes, fetch.max.wait.ms)
- Optimize broker performance (num.network.threads, num.io.threads)
- Configure OS-level tuning (vm.swappiness, file descriptors, TCP settings)
- Implement tiered storage (move old data to S3, EBS)
- Configure quota management (per-client quotas, throttling)
- Optimize partition count (balance parallelism vs overhead)
- Tune replication (acks=1 for performance, acks=all for durability)

Disaster Recovery & High Availability:
- Configure multi-datacenter replication (MirrorMaker 2.0, Confluent Replicator)
- Implement automated broker failover (ZooKeeper or KRaft leader election)
- Setup backup and restore (Kafka topic backups, state store backups)
- Design disaster recovery runbook (broker failure, ZooKeeper failure, network partition)
- Configure rack awareness (distribute replicas across availability zones)
- Implement cluster rolling upgrades (zero-downtime broker upgrades)
- Plan for partition reassignment (rebalancing load across brokers)
- Configure unclean leader election (disabled for data integrity)

CI/CD & GitOps:
- Implement infrastructure as code (Terraform, Helm charts)
- Configure automated topic creation (CI/CD pipelines, topic management tools)
- Setup Kafka Connect deployment automation (connector configurations in Git)
- Implement Kafka Streams deployment (Docker images, Kubernetes deployments)
- Configure blue-green deployments for stream processing apps
- Implement canary deployments (gradual rollout, monitor errors)
- Design rollback procedures (revert to previous version, replay from offset)

**Deliverables:**
- Kafka cluster deployed (3+ brokers, ZooKeeper/KRaft, HA configuration)
- Monitoring dashboards (Grafana with Kafka metrics)
- Alerting rules (Prometheus alerts for critical issues)
- Security configuration (TLS, SASL, ACLs)
- Disaster recovery runbook (failover procedures, backup/restore)
- Performance tuning documentation (broker config, producer/consumer settings)
- Infrastructure as code (Terraform, Helm charts)
- CI/CD pipelines (automated deployment, testing, rollback)
- Operational runbooks (common tasks, troubleshooting)

## Expected Outcomes

### Streaming Infrastructure
- **Kafka cluster**: 3-7 brokers with HA (99.95%+ uptime)
- **Topics**: 10-100 topics with appropriate partitioning (3-100 partitions per topic)
- **Throughput**: 100K-1M+ messages/second (depends on cluster size, message size)
- **Latency**: p95 <100ms end-to-end (producer to consumer)
- **Retention**: 7-30 days (configurable per topic)
- **Schema Registry**: Versioned schemas with backward/forward compatibility

### Data Pipelines
- **Producers**: Microservices, CDC connectors, log shippers
- **Consumers**: Analytics engines, microservices, data warehouses
- **Stream processing**: Real-time aggregations, enrichment, transformations
- **Exactly-once delivery**: For critical workloads (financial, orders)
- **Monitoring**: Consumer lag <1s, alerting on lag >10s

### Business Value
- **Real-time insights**: Analytics dashboards updated in real-time (<1s)
- **Event-driven architecture**: Decoupled microservices, faster feature development
- **Data integration**: Unified event backbone (replace point-to-point integrations)
- **Scalability**: Handle 10x traffic spikes (Black Friday, product launches)
- **Fault tolerance**: Automatic failover, no data loss (replication factor 3)
- **Audit trail**: Event sourcing provides complete audit history

## Usage

```bash
# Design event-driven microservices architecture
/streaming-architecture --use-case=event-driven-microservices --events=100K/sec

# Setup CDC pipeline from PostgreSQL to data warehouse
/streaming-architecture --use-case=cdc --source=postgresql --sink=snowflake

# Build real-time analytics platform
/streaming-architecture --use-case=real-time-analytics --latency=sub-second

# Implement event sourcing with CQRS
/streaming-architecture --pattern=event-sourcing --cqrs=true

# Setup log aggregation pipeline
/streaming-architecture --use-case=log-aggregation --sources=microservices
```

## Prerequisites

- [ ] Use case defined (microservices, CDC, analytics, event sourcing)
- [ ] Data sources identified (databases, APIs, applications)
- [ ] Data consumers identified (services, dashboards, warehouses)
- [ ] Throughput requirements (events/second, data volume)
- [ ] Latency requirements (sub-second, seconds, minutes)
- [ ] Infrastructure budget (cloud provider, cluster size)
- [ ] Team expertise (Kafka experience, stream processing)
- [ ] Development environment (Kafka cluster for testing)

## Success Criteria

### Kafka Cluster
- [ ] Kafka cluster deployed (3+ brokers, HA configuration)
- [ ] ZooKeeper or KRaft operational (3 or 5 nodes)
- [ ] Topics created with appropriate partitioning (3-100 partitions)
- [ ] Replication factor 3 for production topics
- [ ] TLS encryption enabled (data in transit)
- [ ] SASL authentication configured (security)
- [ ] ACLs implemented (topic-level authorization)

### Data Pipelines
- [ ] Producers implemented (microservices, CDC connectors)
- [ ] Consumers implemented (analytics, microservices, sinks)
- [ ] Schema Registry operational (Avro/Protobuf schemas)
- [ ] Stream processing deployed (Kafka Streams, Flink)
- [ ] Exactly-once semantics (for critical workloads)
- [ ] Error handling (retries, dead letter topics)
- [ ] Integration tests passing (end-to-end data flow)

### Performance
- [ ] Throughput meets requirements (100K-1M+ messages/second)
- [ ] Latency meets requirements (p95 <100ms end-to-end)
- [ ] Consumer lag <1s under normal load
- [ ] No data loss (replication, acks=all for critical topics)
- [ ] No message duplication (idempotent producers/consumers)

### Operations
- [ ] Monitoring dashboards (Grafana with Kafka metrics)
- [ ] Alerting configured (lag, broker down, under-replication)
- [ ] Disaster recovery tested (broker failover, data recovery)
- [ ] CI/CD pipelines (automated deployment, rollback)
- [ ] Runbooks documented (operations, troubleshooting)
- [ ] Team trained (Kafka operations, stream processing)

## Real-World Examples

### Example 1: E-commerce Event-Driven Microservices
**Implementation Time:** 10 hours

**Use Case:**
- Decouple order processing microservices (order, payment, inventory, shipping, notification)
- Replace synchronous REST APIs with asynchronous events
- Implement event sourcing for orders (audit trail, state replay)

**Architecture:**

**Kafka Cluster:**
- 5 brokers (AWS MSK m5.large instances)
- 15 topics: orders.created, orders.paid, inventory.reserved, etc.
- Replication factor 3, min.insync.replicas=2
- Avro schemas for all events

**Producers:**
- Order service: Publishes orders.created, orders.cancelled
- Payment service: Publishes orders.paid, orders.payment_failed
- Inventory service: Publishes inventory.reserved, inventory.released
- Shipping service: Publishes orders.shipped, orders.delivered

**Consumers:**
- Payment service: Consumes orders.created → process payment
- Inventory service: Consumes orders.paid → reserve inventory
- Shipping service: Consumes inventory.reserved → schedule shipment
- Notification service: Consumes all events → send emails/SMS
- Analytics service: Consumes all events → real-time dashboards

**Stream Processing:**
- Kafka Streams: Aggregate order metrics (orders/minute, revenue/minute)
- Kafka Streams: Sessionization (user sessions from clickstream)
- Fraud detection: Real-time anomaly detection on payment events

**Delivered:**
- 15 Kafka topics with 6 partitions each (90 partitions total)
- 5 producer services, 6 consumer services
- 2 Kafka Streams applications (metrics, fraud detection)
- Schema Registry with 15 Avro schemas
- 99.98% uptime (automatic broker failover)

**Impact:**
- **Decoupling**: Services deployed independently (10 deploys/day vs 2/week)
- **Scalability**: Handled 10x traffic on Black Friday (Kafka auto-rebalance)
- **Reliability**: Payment failure doesn't block order creation (async retry)
- **Audit trail**: Complete order history (event sourcing)
- **Performance**: p95 latency 45ms (vs 250ms synchronous REST)
- **Development velocity**: New consumers added in hours (no producer changes)

### Example 2: PostgreSQL CDC to Snowflake Data Warehouse
**Implementation Time:** 9 hours

**Use Case:**
- Stream database changes from PostgreSQL to Snowflake in real-time
- Replace nightly batch ETL (12-hour staleness → <1 second)
- Enable real-time analytics dashboards

**Architecture:**

**Kafka Cluster:**
- 3 brokers (Confluent Cloud, Standard tier)
- 20 topics (one per database table)
- Log compaction enabled (retain latest per primary key)
- Protobuf schemas

**CDC Pipeline:**
- Debezium PostgreSQL connector (streams inserts, updates, deletes)
- Kafka topics: db.public.users, db.public.orders, db.public.products, etc.
- 20 PostgreSQL tables streamed (100GB total, 50K changes/day)

**Stream Processing:**
- Apache Flink: Denormalize events (join user, order, product streams)
- Flink: Aggregate metrics (orders per hour, revenue per product)
- Flink: Implement slowly changing dimensions (SCD Type 2)

**Data Sink:**
- Snowflake sink connector (streams to Snowflake tables)
- Micro-batch ingestion (every 60 seconds)
- Schema evolution (auto-create columns on schema changes)

**Delivered:**
- 20 Kafka topics with log compaction
- Debezium connector (PostgreSQL CDC)
- Apache Flink jobs (denormalization, aggregation)
- Snowflake sink connector (real-time data warehouse sync)
- Real-time dashboards (Looker, updated every 60 seconds)

**Impact:**
- **Latency**: 12 hours → <1 second (real-time dashboards)
- **Data quality**: 100% accurate (no batch ETL failures)
- **Development velocity**: New analytics in hours (no ETL changes)
- **Cost savings**: Eliminated nightly batch jobs ($5K/month savings)
- **Business value**: Real-time inventory visibility (prevent stockouts)

### Example 3: IoT Sensor Data Streaming
**Implementation Time:** 11 hours

**Use Case:**
- Ingest 1M sensor readings/second from 100K IoT devices
- Real-time anomaly detection (device failures, temperature spikes)
- Store time-series data for analytics (7 days hot, 90 days cold)

**Architecture:**

**Kafka Cluster:**
- 7 brokers (c5.2xlarge, NVMe SSD storage)
- 1 topic: iot.sensor.readings (100 partitions for parallelism)
- Replication factor 3
- Compression: lz4 (80% compression ratio)
- Retention: 7 days (300GB/day × 7 = 2.1TB)

**Producers:**
- 100K IoT devices (MQTT → Kafka bridge)
- Protobuf serialization (efficient for sensor data)

**Stream Processing:**
- Kafka Streams: Tumbling window aggregations (1-minute, 1-hour rollups)
- Kafka Streams: Anomaly detection (statistical thresholds, ML model)
- Kafka Streams: Alert generation (temperature >80C, device offline >5 min)

**Data Sinks:**
- S3 sink connector (Parquet format, partitioned by date)
- TimescaleDB sink connector (real-time queries on 7 days of data)
- Alert service (consumes alert events → PagerDuty, email)

**Delivered:**
- Kafka cluster handling 1M events/second (100MB/sec)
- Kafka Streams applications (aggregations, anomaly detection)
- S3 data lake (90 days retention, Parquet format)
- TimescaleDB (7 days hot storage, real-time queries)
- Real-time dashboards (Grafana, device health, anomalies)

**Impact:**
- **Throughput**: 1M events/second sustained (10x previous system)
- **Latency**: p95 85ms end-to-end (device → alert)
- **Cost**: $8K/month (vs $25K/month previous batch system)
- **Reliability**: 99.97% uptime (automatic failover)
- **Business value**: Reduced device downtime by 60% (proactive alerts)

## Related Commands

- `/microservices-architecture` - Event-driven microservices design
- `/database-design` - Design event store for event sourcing
- `/api-design` - Design REST APIs for event producers
- `/quality:performance-optimization` - Optimize stream processing performance

## Notes

**When to Use Kafka:**
- High-throughput event streaming (100K+ events/second)
- Event-driven microservices (decouple services)
- Real-time data pipelines (CDC, log aggregation, IoT)
- Event sourcing and CQRS (audit trail, state replay)
- Stream processing (aggregations, joins, enrichment)

**When NOT to Use Kafka:**
- Low-volume events (<1K events/second, simpler solutions exist)
- Request-response patterns (use REST, gRPC instead)
- Small teams (operational overhead of Kafka)
- Simple pub/sub (RabbitMQ, Redis Pub/Sub may be simpler)

**Kafka Best Practices:**

**1. Topic Design:**
- Use semantic naming (domain.entity.event)
- Start with fewer partitions, increase as needed (3-6 initially)
- Replication factor 3 for production (durability)
- Log compaction for state (retain latest per key)

**2. Producer Best Practices:**
- Enable idempotence (enable.idempotence=true)
- Set acks=all for critical data (durability)
- Batch messages for throughput (batch.size, linger.ms)
- Use compression (lz4 for performance, gzip for size)
- Implement proper error handling (retriable vs fatal)

**3. Consumer Best Practices:**
- Use consumer groups (parallelism, automatic failover)
- Commit offsets after processing (at-least-once, manual commit)
- Implement idempotent consumers (deduplicate messages)
- Monitor consumer lag (critical metric)
- Design graceful shutdown (commit offsets, close connections)

**4. Stream Processing Best Practices:**
- Use event time (not processing time)
- Configure watermarks for late data
- Implement exactly-once processing (processing.guarantee)
- Design repartitioning strategy (co-partitioning for joins)
- Monitor state store size (can grow large)

**5. Operations Best Practices:**
- Monitor consumer lag (most important metric)
- Alert on under-replicated partitions (data loss risk)
- Configure rack awareness (distribute replicas across AZs)
- Implement automated failover (ZooKeeper, KRaft)
- Plan for capacity (storage, network, broker count)
- Test disaster recovery (broker failure, network partition)

This workflow ensures streaming architectures are scalable, reliable, and deliver real-time business value with Apache Kafka.
