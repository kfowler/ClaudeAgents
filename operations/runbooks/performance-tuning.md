# Performance Tuning Runbook

## Overview

This runbook provides comprehensive procedures for identifying, diagnosing, and resolving performance issues in the Claude Agents platform. It covers both reactive troubleshooting and proactive optimization strategies.

## Performance Monitoring Baseline

### Key Performance Indicators (KPIs)

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **Response Time (p95)** | <500ms | >1s | >2s |
| **Error Rate** | <0.1% | >1% | >5% |
| **Throughput** | >100 RPS | <50 RPS | <10 RPS |
| **CPU Usage** | <50% | >70% | >90% |
| **Memory Usage** | <70% | >85% | >95% |
| **Database Response** | <100ms | >500ms | >1s |

### Performance Monitoring Queries

```bash
# Response time monitoring
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(http_request_duration_seconds_bucket{job=~\"claude-agents-.*\"}[5m]))by(le))"

# Error rate monitoring
curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{job=~\"claude-agents-.*\",code!~\"2..\"}[5m]))/sum(rate(http_requests_total{job=~\"claude-agents-.*\"}[5m]))"

# Throughput monitoring
curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{job=~\"claude-agents-.*\"}[5m]))"

# Resource utilization
kubectl top pods -n claude-agents --sort-by=cpu
kubectl top pods -n claude-agents --sort-by=memory
```

## Performance Issue Diagnosis

### Step 1: Identify the Problem Scope

```bash
# Check which services are experiencing issues
services=(orchestrator agent-recommender learning-system semantic-agent analytics workflows)
for service in "${services[@]}"; do
    echo "=== Checking $service ==="
    kubectl logs -n claude-agents deployment/$service --tail=50 | grep -E "(slow|timeout|error|exception)"
    kubectl top pod -n claude-agents -l app=$service
done

# Identify the timeframe when issues started
kubectl get events -n claude-agents --sort-by='.lastTimestamp' | tail -20
```

### Step 2: Resource Analysis

#### CPU Performance Issues
```bash
# Identify CPU-intensive pods
kubectl top pods -n claude-agents --sort-by=cpu | head -10

# Check CPU throttling
kubectl exec -n claude-agents deployment/orchestrator -- cat /sys/fs/cgroup/cpu/cpu.stat | grep throttled

# Profile CPU usage (if profiling endpoint available)
kubectl exec -n claude-agents deployment/orchestrator -- curl http://localhost:8080/debug/pprof/profile?seconds=30 > cpu-profile.pprof
```

#### Memory Performance Issues
```bash
# Identify memory-intensive pods
kubectl top pods -n claude-agents --sort-by=memory | head -10

# Check for memory pressure
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check for memory leaks
for pod in $(kubectl get pods -n claude-agents -o name); do
    echo "=== $pod ==="
    kubectl exec -n claude-agents $pod -- ps aux | head -5
done

# Analyze garbage collection (for JVM/Python services)
kubectl logs -n claude-agents deployment/learning-system | grep -i "gc\|garbage"
```

### Step 3: Database Performance Analysis

#### PostgreSQL Performance
```bash
# Check active connections and queries
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
    count(*) as total_connections,
    count(*) filter (where state = 'active') as active_connections,
    count(*) filter (where state = 'idle') as idle_connections,
    count(*) filter (where state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity;
"

# Identify slow queries
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check for blocking queries
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.query AS blocked_statement,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
"

# Analyze buffer cache hit ratio
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;
"
```

#### Redis Performance
```bash
# Redis performance metrics
kubectl exec -n claude-agents deployment/redis -- redis-cli info stats
kubectl exec -n claude-agents deployment/redis -- redis-cli info memory
kubectl exec -n claude-agents deployment/redis -- redis-cli info clients

# Check slow queries
kubectl exec -n claude-agents deployment/redis -- redis-cli slowlog get 10

# Check memory usage patterns
kubectl exec -n claude-agents deployment/redis -- redis-cli --bigkeys
```

### Step 4: Network Performance Analysis

```bash
# Check service-to-service latency
kubectl exec -n claude-agents deployment/orchestrator -- time curl http://agent-recommender:8000/health

# Check DNS resolution time
kubectl exec -n claude-agents deployment/orchestrator -- time nslookup agent-recommender

# Network connectivity test
kubectl exec -n claude-agents deployment/orchestrator -- nc -zv postgres 5432
kubectl exec -n claude-agents deployment/orchestrator -- nc -zv redis 6379

# Check ingress controller performance
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller | grep -E "(upstream_response_time|request_time)"
```

## Performance Optimization Strategies

### Application-Level Optimization

#### 1. Connection Pool Tuning

**Database Connections**:
```yaml
# Update connection pool settings in orchestrator config
database:
  max_connections: 20
  min_connections: 5
  connection_timeout: 30s
  idle_timeout: 300s
  max_lifetime: 3600s
```

**Redis Connections**:
```yaml
redis:
  pool_size: 10
  max_retries: 3
  retry_delay: 100ms
  read_timeout: 1s
  write_timeout: 1s
```

#### 2. Caching Strategies

**Application-Level Caching**:
```bash
# Enable Redis caching for agent recommendations
kubectl patch configmap -n claude-agents agent-recommender-config --patch '
data:
  cache_enabled: "true"
  cache_ttl: "3600"
  cache_size: "1000"
'

# Restart service to apply changes
kubectl rollout restart deployment -n claude-agents agent-recommender
```

**Database Query Caching**:
```sql
-- Enable query caching in PostgreSQL
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET log_min_duration_statement = 1000;
```

#### 3. Async Processing

```bash
# Enable async processing for learning system
kubectl patch configmap -n claude-agents learning-system-config --patch '
data:
  async_enabled: "true"
  worker_count: "4"
  queue_size: "1000"
'
```

### Infrastructure-Level Optimization

#### 1. Horizontal Pod Autoscaling (HPA)

```yaml
# Configure HPA for orchestrator
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orchestrator-hpa
  namespace: claude-agents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orchestrator
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Reduced from 70%
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70  # Reduced from 80%
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

#### 2. Vertical Pod Autoscaling (VPA)

```yaml
# Enable VPA for learning system (compute-intensive)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: learning-system-vpa
  namespace: claude-agents
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: learning-system
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: learning-system
      minAllowed:
        memory: 512Mi
        cpu: 250m
      maxAllowed:
        memory: 8Gi
        cpu: 2000m
```

#### 3. Resource Requests and Limits Tuning

```bash
# Update resource allocations based on actual usage
kubectl patch deployment -n claude-agents orchestrator --patch '
spec:
  template:
    spec:
      containers:
      - name: orchestrator
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
'

# Update learning system for ML workloads
kubectl patch deployment -n claude-agents learning-system --patch '
spec:
  template:
    spec:
      containers:
      - name: learning-system
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
'
```

### Database Optimization

#### PostgreSQL Tuning

```bash
# Update PostgreSQL configuration for better performance
kubectl exec -n claude-agents deployment/postgres -- psql -c "
-- Connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- WAL settings
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_writer_delay = '200ms';

-- Query planning
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

SELECT pg_reload_conf();
"

# Restart PostgreSQL to apply configuration changes
kubectl rollout restart statefulset -n claude-agents postgres
```

#### Database Index Optimization

```sql
-- Analyze query patterns and add indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Create indexes for common query patterns
CREATE INDEX CONCURRENTLY idx_agents_type_created ON agents(type, created_at);
CREATE INDEX CONCURRENTLY idx_workflows_status_updated ON workflows(status, updated_at);
CREATE INDEX CONCURRENTLY idx_analytics_timestamp ON analytics_events(timestamp);

-- Update table statistics
ANALYZE;
```

#### Redis Optimization

```bash
# Update Redis configuration
kubectl patch configmap -n claude-agents redis-config --patch '
data:
  redis.conf: |
    # Memory optimization
    maxmemory 1gb
    maxmemory-policy allkeys-lru
    
    # Performance settings
    tcp-keepalive 300
    timeout 300
    save 900 1
    save 300 10
    save 60 10000
    
    # Network optimization
    tcp-backlog 511
    
    # Advanced configuration
    hash-max-ziplist-entries 512
    hash-max-ziplist-value 64
    list-max-ziplist-size -2
    set-max-intset-entries 512
    zset-max-ziplist-entries 128
    zset-max-ziplist-value 64
'

# Restart Redis to apply changes
kubectl rollout restart deployment -n claude-agents redis
```

## Advanced Performance Tuning

### JVM Tuning (for JVM-based services)

```bash
# Update JVM flags for better performance
kubectl patch deployment -n claude-agents analytics --patch '
spec:
  template:
    spec:
      containers:
      - name: analytics
        env:
        - name: JVM_OPTS
          value: "-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+PrintGC -XX:+PrintGCDetails"
'
```

### Python/Gunicorn Tuning

```bash
# Update Gunicorn configuration for Python services
kubectl patch deployment -n claude-agents agent-recommender --patch '
spec:
  template:
    spec:
      containers:
      - name: agent-recommender
        env:
        - name: GUNICORN_WORKERS
          value: "4"
        - name: GUNICORN_WORKER_CLASS
          value: "uvicorn.workers.UvicornWorker"
        - name: GUNICORN_MAX_REQUESTS
          value: "1000"
        - name: GUNICORN_MAX_REQUESTS_JITTER
          value: "100"
        - name: GUNICORN_PRELOAD
          value: "true"
'
```

### Rust Performance Tuning

```bash
# Update Rust service configuration
kubectl patch deployment -n claude-agents orchestrator --patch '
spec:
  template:
    spec:
      containers:
      - name: orchestrator
        env:
        - name: RUST_LOG
          value: "info"
        - name: TOKIO_WORKER_THREADS
          value: "4"
        - name: SERVER_WORKERS
          value: "4"
        - name: CONNECTION_POOL_SIZE
          value: "20"
'
```

## Load Testing and Benchmarking

### Load Testing Setup

```bash
# Install load testing tool
kubectl create ns load-testing
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: load-test
  namespace: load-testing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: load-test
  template:
    metadata:
      labels:
        app: load-test
    spec:
      containers:
      - name: k6
        image: grafana/k6:latest
        command: ["/bin/sh"]
        args: ["-c", "while true; do sleep 3600; done"]
        volumeMounts:
        - name: scripts
          mountPath: /scripts
      volumes:
      - name: scripts
        configMap:
          name: load-test-scripts
EOF
```

### Load Test Scripts

```javascript
// k6 load test script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests under 1s
    http_req_failed: ['rate<0.01'], // Error rate under 1%
  },
};

export default function() {
  // Test orchestrator endpoint
  let response = http.post('http://claude-agents-orchestrator:8080/api/orchestrate', {
    task: 'recommend_agent',
    context: 'web development project',
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  
  // Test agent recommendation
  response = http.get('http://claude-agents-agent-recommender:8000/api/recommend?query=react+components');
  
  check(response, {
    'recommendation status is 200': (r) => r.status === 200,
    'recommendation response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

### Running Load Tests

```bash
# Run load test
kubectl exec -n load-testing deployment/load-test -- k6 run /scripts/load-test.js

# Monitor during load test
watch -n 5 'kubectl top pods -n claude-agents'
watch -n 5 'curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[1m])"'
```

## Performance Monitoring and Alerting

### Custom Performance Metrics

```bash
# Create custom performance dashboard
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: performance-dashboard
  namespace: claude-agents
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Claude Agents Performance",
        "panels": [
          {
            "title": "Response Time Distribution",
            "type": "heatmap",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
              }
            ]
          },
          {
            "title": "Error Rate by Service",
            "type": "timeseries",
            "targets": [
              {
                "expr": "sum(rate(http_requests_total{code!~\"2..\"}[5m])) by (job) / sum(rate(http_requests_total[5m])) by (job)"
              }
            ]
          }
        ]
      }
    }
EOF
```

### Performance Alerting Rules

```yaml
# performance-alerts.yml
groups:
- name: performance.rules
  rules:
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1
    for: 2m
    labels:
      severity: warning
      team: performance
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s"

  - alert: HighThroughput
    expr: sum(rate(http_requests_total[5m])) > 1000
    for: 1m
    labels:
      severity: info
      team: performance
    annotations:
      summary: "High traffic detected"
      description: "Request rate is {{ $value }} requests/second"

  - alert: DatabaseSlowQueries
    expr: pg_stat_activity_max_tx_duration > 60
    for: 1m
    labels:
      severity: warning
      team: database
    annotations:
      summary: "Slow database queries detected"
      description: "Query running for {{ $value }} seconds"
```

## Performance Optimization Checklist

### Before Optimization
- [ ] Establish baseline performance metrics
- [ ] Identify specific performance bottlenecks
- [ ] Document current resource utilization
- [ ] Set up comprehensive monitoring
- [ ] Plan rollback strategy

### During Optimization
- [ ] Make one change at a time
- [ ] Monitor impact of each change
- [ ] Document all modifications
- [ ] Test under load conditions
- [ ] Verify no regressions introduced

### After Optimization
- [ ] Measure performance improvements
- [ ] Update monitoring thresholds
- [ ] Document optimal configurations
- [ ] Update runbooks with lessons learned
- [ ] Schedule regular performance reviews

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-XX  
**Owner**: Performance Engineering Team  
**Review Schedule**: Monthly or after performance incidents