# System Health Check Runbook

## Overview

This runbook provides comprehensive procedures for checking the overall health of the Claude Agents platform. These checks should be performed during regular maintenance windows, incident response, and post-deployment verification.

## Quick Health Assessment (5 minutes)

### 1. Service Status Check

```bash
# Check all pods in the claude-agents namespace
kubectl get pods -n claude-agents

# Expected output: All pods should be "Running" or "Completed"
# Look for: CrashLoopBackOff, Error, Pending, ImagePullBackOff

# Check service endpoints
kubectl get endpoints -n claude-agents

# Verify ingress status
kubectl get ingress -n claude-agents
```

### 2. Core Services Health Endpoints

```bash
# Test all health endpoints
services=(
  "orchestrator:8080"
  "agent-recommender:8000"
  "learning-system:8000"
  "semantic-agent:8000"
  "analytics:8000"
  "workflows:8000"
)

for service in "${services[@]}"; do
  echo "Checking $service..."
  kubectl exec -n claude-agents deployment/test-pod -- curl -f "http://$service/health" || echo "❌ $service health check failed"
done
```

### 3. Database Connectivity

```bash
# PostgreSQL connection test
kubectl exec -n claude-agents deployment/orchestrator -- psql $DATABASE_URL -c "SELECT 1;" || echo "❌ PostgreSQL connection failed"

# Redis connection test
kubectl exec -n claude-agents deployment/orchestrator -- redis-cli -h redis ping || echo "❌ Redis connection failed"

# Qdrant connection test
kubectl exec -n claude-agents deployment/semantic-agent -- curl -f "http://qdrant:6333/health" || echo "❌ Qdrant health check failed"
```

## Detailed Health Assessment (15 minutes)

### 1. Resource Utilization Check

```bash
# Check CPU and memory usage across all pods
kubectl top pods -n claude-agents --sort-by=cpu
kubectl top pods -n claude-agents --sort-by=memory

# Check node resources
kubectl top nodes

# Look for:
# - Pods using >80% of allocated memory
# - Pods using >70% of allocated CPU
# - Nodes with high resource utilization
```

### 2. Database Performance Check

```bash
# PostgreSQL performance metrics
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
  datname,
  numbackends as connections,
  xact_commit as commits,
  xact_rollback as rollbacks,
  blks_read + blks_hit as total_reads,
  temp_files,
  temp_bytes
FROM pg_stat_database 
WHERE datname = 'claude_agents';
"

# Check for long-running queries
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
  pid,
  now() - pg_stat_activity.query_start AS duration,
  query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Redis performance metrics
kubectl exec -n claude-agents deployment/redis -- redis-cli info stats
kubectl exec -n claude-agents deployment/redis -- redis-cli info memory
```

### 3. Application Performance Metrics

```bash
# Check recent error rates from logs
kubectl logs -n claude-agents deployment/orchestrator --tail=1000 | grep -i "error\|exception\|panic" | tail -10

# Check response time patterns (if metrics are available)
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(http_request_duration_seconds_bucket{job=~\"claude-agents-.*\"}[5m]))by(le))"

# Check for recent alerts
curl -s "http://alertmanager:9093/api/v1/alerts" | jq '.data[] | select(.status.state == "firing")'
```

### 4. Security Health Check

```bash
# Check for failed authentication attempts
kubectl logs -n claude-agents -l app=orchestrator --tail=1000 | grep -i "auth.*fail\|unauthorized\|forbidden"

# Verify TLS certificates
kubectl get secret -n claude-agents tls-secret -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -dates

# Check network policies
kubectl get networkpolicy -n claude-agents
```

## Critical System Dependencies

### 1. Kubernetes Cluster Health

```bash
# Check cluster nodes
kubectl get nodes -o wide

# Check cluster-critical pods
kubectl get pods -n kube-system | grep -E "(coredns|kube-proxy|aws-node|ebs-csi)"

# Check cluster resource allocation
kubectl describe nodes | grep -E "(Allocated resources|CPU Requests|Memory Requests)"
```

### 2. Networking Health

```bash
# Test DNS resolution
kubectl exec -n claude-agents deployment/orchestrator -- nslookup kubernetes.default

# Test service-to-service communication
kubectl exec -n claude-agents deployment/orchestrator -- curl -f http://agent-recommender:8000/health

# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=50
```

### 3. Storage Health

```bash
# Check persistent volumes
kubectl get pv
kubectl get pvc -n claude-agents

# Check storage class
kubectl get storageclass

# Verify backup status (if using automated backups)
kubectl get cronjobs -n claude-agents
```

## Performance Benchmarks

### Expected Response Times

| Service | Endpoint | Expected p95 | Action if Exceeded |
|---------|----------|--------------|-------------------|
| Orchestrator | /api/orchestrate | <1000ms | Check resource allocation, database connections |
| Agent Recommender | /api/recommend | <500ms | Check model loading, cache hit rate |
| Learning System | /api/learn | <2000ms | Check ML model performance, data pipeline |
| Semantic Agent | /api/semantic | <750ms | Check vector database performance |

### Resource Usage Baselines

| Service | CPU (Normal) | Memory (Normal) | Action Threshold |
|---------|-------------|----------------|------------------|
| Orchestrator | 10-30% | 256-512MB | >70% CPU, >1GB memory |
| PostgreSQL | 5-20% | 512MB-1GB | >50% CPU, >2GB memory |
| Redis | 5-15% | 128-256MB | >40% CPU, >512MB memory |
| Learning System | 20-50% | 1-2GB | >80% CPU, >4GB memory |

## Troubleshooting Common Issues

### High CPU Usage

```bash
# Identify high CPU pods
kubectl top pods -n claude-agents --sort-by=cpu

# Check pod logs for errors
kubectl logs -n claude-agents <high-cpu-pod> --tail=100

# Scale horizontally if needed
kubectl scale deployment -n claude-agents <deployment-name> --replicas=<new-count>
```

### High Memory Usage

```bash
# Check memory usage patterns
kubectl describe pod -n claude-agents <pod-name>

# Look for memory leaks in logs
kubectl logs -n claude-agents <pod-name> | grep -i "memory\|oom\|gc"

# Restart pod if memory leak suspected
kubectl delete pod -n claude-agents <pod-name>
```

### Database Connection Issues

```bash
# Check connection pool status
kubectl exec -n claude-agents deployment/postgres -- psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check for deadlocks
kubectl exec -n claude-agents deployment/postgres -- psql -c "SELECT * FROM pg_stat_activity WHERE wait_event IS NOT NULL;"

# Restart connections if needed
kubectl rollout restart deployment -n claude-agents orchestrator
```

### Service Discovery Issues

```bash
# Check service endpoints
kubectl get endpoints -n claude-agents <service-name>

# Verify labels and selectors
kubectl describe service -n claude-agents <service-name>
kubectl get pods -n claude-agents --show-labels

# Test internal DNS
kubectl exec -n claude-agents deployment/orchestrator -- nslookup <service-name>
```

## Emergency Procedures

### Complete Service Restart

```bash
# Graceful restart of all services (use only when necessary)
kubectl rollout restart deployment -n claude-agents

# Wait for rollout to complete
kubectl rollout status deployment -n claude-agents --timeout=300s
```

### Scale to Zero (Emergency Stop)

```bash
# Emergency scale down (preserve data)
kubectl scale deployment -n claude-agents --all --replicas=0

# To restart
kubectl scale deployment -n claude-agents orchestrator --replicas=3
kubectl scale deployment -n claude-agents agent-recommender --replicas=2
# ... continue for all services
```

### Database Emergency Recovery

```bash
# Check database status
kubectl exec -n claude-agents deployment/postgres -- pg_isready

# If database is corrupted, restore from backup
kubectl exec -n claude-agents deployment/postgres -- pg_restore -d claude_agents /backups/latest.sql

# Verify data integrity after restoration
kubectl exec -n claude-agents deployment/postgres -- psql -c "SELECT COUNT(*) FROM agents;"
```

## Health Check Automation

### Automated Health Check Script

```bash
#!/bin/bash
# health-check.sh - Automated system health verification

set -e

NAMESPACE="claude-agents"
FAILED_CHECKS=()

check_pods() {
    echo "=== Checking Pod Status ==="
    if kubectl get pods -n $NAMESPACE | grep -E "(Error|CrashLoopBackOff|ImagePullBackOff|Pending)"; then
        FAILED_CHECKS+=("Pod status check failed")
    else
        echo "✅ All pods healthy"
    fi
}

check_services() {
    echo "=== Checking Service Health ==="
    services=("orchestrator:8080" "agent-recommender:8000" "learning-system:8000")
    
    for service in "${services[@]}"; do
        if ! kubectl exec -n $NAMESPACE deployment/test-pod -- curl -f -s "http://$service/health" > /dev/null; then
            FAILED_CHECKS+=("$service health check failed")
        else
            echo "✅ $service healthy"
        fi
    done
}

check_resources() {
    echo "=== Checking Resource Usage ==="
    high_cpu=$(kubectl top pods -n $NAMESPACE --no-headers | awk '$3 > 80 {print $1}')
    if [[ -n "$high_cpu" ]]; then
        FAILED_CHECKS+=("High CPU usage detected: $high_cpu")
    else
        echo "✅ CPU usage normal"
    fi
}

check_database() {
    echo "=== Checking Database ==="
    if ! kubectl exec -n $NAMESPACE deployment/postgres -- pg_isready > /dev/null; then
        FAILED_CHECKS+=("PostgreSQL not ready")
    else
        echo "✅ PostgreSQL healthy"
    fi
    
    if ! kubectl exec -n $NAMESPACE deployment/redis -- redis-cli ping > /dev/null; then
        FAILED_CHECKS+=("Redis not responding")
    else
        echo "✅ Redis healthy"
    fi
}

# Run all checks
check_pods
check_services
check_resources
check_database

# Report results
if [[ ${#FAILED_CHECKS[@]} -eq 0 ]]; then
    echo "🎉 All health checks passed!"
    exit 0
else
    echo "❌ Health check failures:"
    printf '%s\n' "${FAILED_CHECKS[@]}"
    exit 1
fi
```

## Monitoring Integration

### Grafana Dashboards

- **System Overview**: `/d/claude-agents-overview` - High-level system health
- **Service Details**: `/d/claude-agents-services` - Individual service metrics
- **Infrastructure**: `/d/claude-agents-infra` - Node and cluster health

### Prometheus Queries for Health Checks

```promql
# Service availability
up{job=~"claude-agents-.*"} == 0

# High error rate
sum(rate(http_requests_total{job=~"claude-agents-.*", code!~"2.."}[5m])) by (job) / sum(rate(http_requests_total{job=~"claude-agents-.*"}[5m])) by (job) > 0.01

# High memory usage
container_memory_working_set_bytes{pod=~"claude-agents-.*"} / container_spec_memory_limit_bytes{pod=~"claude-agents-.*"} > 0.8

# Database connection issues
pg_stat_database_numbackends / pg_settings_max_connections > 0.8
```

## Escalation Procedures

### Level 1: Automated Response
- Automatic scaling triggers
- Circuit breaker activation
- Alert notifications

### Level 2: On-call Engineer
- Manual intervention required
- Complex troubleshooting
- Configuration changes

### Level 3: Subject Matter Expert
- Deep system knowledge needed
- Architecture decisions
- Code changes required

### Level 4: Emergency Response
- Multiple system failures
- Data integrity issues
- Security incidents

---

**Last Updated**: 2024-01-XX  
**Version**: 1.0  
**Owner**: Platform Operations Team  
**Review Schedule**: Monthly