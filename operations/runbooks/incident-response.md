# Incident Response Runbook

## Overview

This runbook provides comprehensive procedures for responding to incidents in the Claude Agents platform. It covers incident classification, response procedures, communication protocols, and post-incident activities.

## Incident Classification

### Severity Levels

#### P0 - Critical (Production Down)
- **Impact**: Complete service outage, data loss, security breach
- **Response Time**: Immediate (within 5 minutes)
- **Examples**: 
  - All services unreachable
  - Database corruption or data loss
  - Security breach with data exposure
  - Complete cluster failure

#### P1 - High (Major Degradation)
- **Impact**: Significant functionality impacted, some users affected
- **Response Time**: 15 minutes
- **Examples**:
  - Core service unavailable (orchestrator down)
  - High error rates (>5%)
  - Performance severely degraded
  - Authentication failures

#### P2 - Medium (Minor Degradation)
- **Impact**: Limited functionality affected, workarounds available
- **Response Time**: 1 hour
- **Examples**:
  - Single service experiencing issues
  - Moderate performance degradation
  - Non-critical features unavailable
  - Resource constraints

#### P3 - Low (Minor Issues)
- **Impact**: Minimal user impact, cosmetic issues
- **Response Time**: Next business day
- **Examples**:
  - UI inconsistencies
  - Non-functional requirements not met
  - Enhancement requests
  - Documentation issues

## Immediate Response Procedures

### Step 1: Incident Detection and Assessment (0-5 minutes)

```bash
# Quick system overview
kubectl get pods -n claude-agents
kubectl get nodes
kubectl get ingress -n claude-agents

# Check recent deployments
kubectl rollout history deployment -n claude-agents

# Identify the scope of impact
# - Which services are affected?
# - How many users are impacted?
# - When did the issue start?
```

### Step 2: Initial Triage (5-10 minutes)

#### Determine Severity
```bash
# Check error rates
curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{code!~\"2..\"}[5m]))/sum(rate(http_requests_total[5m]))" | jq '.data.result[0].value[1]'

# Check service availability
services=(orchestrator agent-recommender learning-system semantic-agent)
for service in "${services[@]}"; do
  kubectl exec -n claude-agents deployment/test-pod -- curl -f "http://$service:8000/health" || echo "$service DOWN"
done

# Check infrastructure health
kubectl top nodes
kubectl describe nodes | grep -E "(OutOfDisk|MemoryPressure|DiskPressure|PIDPressure)"
```

#### Quick Mitigation Attempts
```bash
# If recent deployment caused the issue
kubectl rollout undo deployment/<affected-deployment> -n claude-agents

# If resource exhaustion
kubectl scale deployment -n claude-agents <deployment> --replicas=<higher-number>

# If single pod issues
kubectl delete pod -n claude-agents <problematic-pod>
```

### Step 3: Communication (Within 10 minutes)

#### Internal Notification
```bash
# Slack notification template
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-type: application/json' \
  --data '{
    "channel": "#incidents",
    "username": "Incident Bot",
    "icon_emoji": ":fire:",
    "text": "🚨 P0 INCIDENT: <describe issue>\nResponse Lead: @<engineer>\nStatus: Investigating\nStarted: <timestamp>"
  }'
```

#### Customer Communication (P0/P1 only)
- Update status page within 15 minutes
- Notify customer success team
- Prepare customer communication template

## Detailed Investigation Procedures

### Service-Specific Troubleshooting

#### Orchestrator Issues
```bash
# Check orchestrator logs
kubectl logs -n claude-agents deployment/orchestrator --tail=100 -f

# Check database connections
kubectl exec -n claude-agents deployment/orchestrator -- \
  psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis connectivity
kubectl exec -n claude-agents deployment/orchestrator -- \
  redis-cli -h redis ping

# Verify configuration
kubectl describe configmap -n claude-agents orchestrator-config
```

#### Database Issues
```bash
# PostgreSQL health check
kubectl exec -n claude-agents deployment/postgres -- pg_isready
kubectl exec -n claude-agents deployment/postgres -- \
  psql -c "SELECT version(), current_database(), current_user;"

# Check for blocking queries
kubectl exec -n claude-agents deployment/postgres -- psql -c "
SELECT 
  blocked_locks.pid AS blocked_pid,
  blocked_activity.usename AS blocked_user,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.usename AS blocking_user,
  blocked_activity.query AS blocked_statement,
  blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
"

# Check disk space
kubectl exec -n claude-agents deployment/postgres -- df -h
```

#### Performance Issues
```bash
# Resource utilization
kubectl top pods -n claude-agents --sort-by=cpu
kubectl top pods -n claude-agents --sort-by=memory

# Application metrics
curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[5m])"
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))"

# Check for memory leaks
kubectl exec -n claude-agents deployment/<service> -- ps aux
```

### Network and Infrastructure Issues
```bash
# DNS resolution
kubectl exec -n claude-agents deployment/orchestrator -- nslookup kubernetes.default
kubectl exec -n claude-agents deployment/orchestrator -- nslookup google.com

# Service connectivity
kubectl exec -n claude-agents deployment/orchestrator -- nc -zv agent-recommender 8000

# Ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=100

# Check network policies
kubectl get networkpolicy -n claude-agents
kubectl describe networkpolicy -n claude-agents
```

## Recovery Procedures

### Service Recovery

#### Rolling Restart
```bash
# Graceful restart of specific service
kubectl rollout restart deployment -n claude-agents <service-name>
kubectl rollout status deployment -n claude-agents <service-name> --timeout=300s
```

#### Rollback to Previous Version
```bash
# Check rollout history
kubectl rollout history deployment -n claude-agents <service-name>

# Rollback to previous version
kubectl rollout undo deployment -n claude-agents <service-name>

# Rollback to specific revision
kubectl rollout undo deployment -n claude-agents <service-name> --to-revision=<revision-number>
```

#### Scale Out for Load Issues
```bash
# Horizontal scaling
kubectl scale deployment -n claude-agents <service-name> --replicas=<new-count>

# Check HPA status
kubectl get hpa -n claude-agents
kubectl describe hpa -n claude-agents <hpa-name>
```

### Database Recovery

#### Connection Pool Reset
```bash
# Restart services to reset connection pools
kubectl rollout restart deployment -n claude-agents orchestrator
kubectl rollout restart deployment -n claude-agents agent-recommender
```

#### Point-in-Time Recovery
```bash
# Stop all application pods
kubectl scale deployment -n claude-agents --all --replicas=0

# Restore database from backup
kubectl exec -n claude-agents deployment/postgres -- \
  pg_restore -C -d postgres /backups/claude_agents_$(date +%Y%m%d).sql

# Verify data integrity
kubectl exec -n claude-agents deployment/postgres -- \
  psql claude_agents -c "SELECT COUNT(*) FROM agents;"

# Restart application services
kubectl scale deployment -n claude-agents orchestrator --replicas=3
```

### Infrastructure Recovery

#### Node Issues
```bash
# Drain problematic node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Check node status
kubectl describe node <node-name>

# If node is unrecoverable, cordon and replace
kubectl cordon <node-name>
# Follow cloud provider procedures to replace node
```

#### Cluster Recovery
```bash
# Check cluster health
kubectl get componentstatuses
kubectl cluster-info

# If control plane issues, escalate to infrastructure team
# If etcd issues, restore from etcd backup (critical - get expert help)
```

## Communication Templates

### Status Page Updates

#### Initial Incident Report
```
We are currently investigating reports of service disruption affecting the Claude Agents platform. 
Users may experience difficulty accessing certain features. We are actively working to resolve 
this issue and will provide updates as more information becomes available.

Time started: [TIME]
Services affected: [LIST]
Impact: [DESCRIPTION]
Status: Investigating
```

#### Progress Update
```
We have identified the root cause of the service disruption as [CAUSE]. Our team is implementing 
a fix and we expect services to be fully restored within [TIMEFRAME].

Current status: Implementing fix
ETA for resolution: [TIME]
Workaround: [IF AVAILABLE]
```

#### Resolution Notice
```
The service disruption affecting the Claude Agents platform has been resolved. All services 
are now operating normally. We apologize for any inconvenience this may have caused.

Resolution time: [TIME]
Duration: [TOTAL TIME]
Root cause: [BRIEF DESCRIPTION]
```

### Internal Communication

#### Slack Updates (Every 30 minutes during P0/P1)
```
🚨 INCIDENT UPDATE - P[X] - [BRIEF DESCRIPTION]
Status: [Investigating/Mitigating/Resolved]
Lead: @[engineer]
Duration: [time]
Impact: [description]
Next update: [time]

Actions taken:
- [action 1]
- [action 2]

Next steps:
- [next action]

Need help with: [if applicable]
```

### Customer Communication

#### High-Touch Customers (P0/P1)
```
Subject: Claude Agents Service Disruption - [INCIDENT ID]

Dear [Customer],

We are writing to inform you of a service disruption currently affecting the Claude Agents 
platform. We identified the issue at [TIME] and are working urgently to restore full service.

Impact: [Specific impact to customer]
Current Status: [Status]
Expected Resolution: [ETA]
Workaround: [If available]

We will continue to provide updates every [FREQUENCY] until the issue is resolved. You can 
also monitor our status page at [URL] for real-time updates.

We sincerely apologize for any inconvenience this may cause and appreciate your patience 
as we work to resolve this matter.

Best regards,
Claude Agents Support Team
```

## Post-Incident Activities

### Immediate Post-Resolution (Within 2 hours)

#### Verify Full Recovery
```bash
# Run comprehensive health checks
./scripts/health-check.sh

# Verify metrics return to baseline
curl -s "http://prometheus:9090/api/v1/query?query=up{job=~\"claude-agents-.*\"}"

# Check error rates
curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{code!~\"2..\"}[5m]))"
```

#### Customer Follow-up
- Update status page with resolution
- Send resolution notice to affected customers
- Monitor support channels for related issues

### Post-Incident Review (Within 24 hours)

#### Data Collection
```bash
# Collect logs from incident timeframe
kubectl logs -n claude-agents deployment/orchestrator \
  --since-time="2024-01-01T10:00:00Z" \
  --until-time="2024-01-01T12:00:00Z" > incident-logs-orchestrator.log

# Export metrics data
curl -s "http://prometheus:9090/api/v1/query_range?query=up&start=2024-01-01T10:00:00Z&end=2024-01-01T12:00:00Z&step=60s" > incident-metrics.json

# Document timeline
# - When was the incident first detected?
# - When did it actually start?
# - What actions were taken and when?
# - When was it resolved?
```

#### Root Cause Analysis Template
```markdown
# Post-Incident Review: [INCIDENT ID]

## Summary
- **Date**: [DATE]
- **Duration**: [TOTAL TIME]
- **Severity**: P[X]
- **Impact**: [USER IMPACT]
- **Root Cause**: [ONE SENTENCE]

## Timeline
- [TIME] - Incident starts (root cause event)
- [TIME] - First alert fired
- [TIME] - Incident detected by team
- [TIME] - Investigation began
- [TIME] - Root cause identified
- [TIME] - Mitigation applied
- [TIME] - Service restored
- [TIME] - All clear given

## Root Cause
[Detailed explanation of what went wrong and why]

## Contributing Factors
- [Factor 1]
- [Factor 2]

## What Went Well
- [Positive aspect 1]
- [Positive aspect 2]

## What Could Be Improved
- [Improvement 1]
- [Improvement 2]

## Action Items
- [ ] [Action item 1] - Owner: [NAME] - Due: [DATE]
- [ ] [Action item 2] - Owner: [NAME] - Due: [DATE]
```

### Long-term Improvements (Within 1 week)

#### System Improvements
- Implement additional monitoring
- Improve alerting rules
- Add circuit breakers or failsafes
- Update runbooks based on lessons learned

#### Process Improvements
- Update incident response procedures
- Conduct team training if needed
- Improve communication templates
- Review escalation procedures

## Escalation Matrix

### Technical Escalation
1. **On-call Engineer** (0-15 minutes)
2. **Senior Engineer** (15-30 minutes)
3. **Engineering Manager** (30-60 minutes)
4. **Principal Engineer/Architect** (1+ hours)

### Business Escalation
1. **Engineering Manager** (P0 immediately, P1 within 30 minutes)
2. **Director of Engineering** (P0 within 30 minutes)
3. **CTO** (P0 affecting major customers)
4. **CEO** (Major security breach or extended P0)

### External Escalation
- **Cloud Provider Support** (Infrastructure issues)
- **Security Team** (Security incidents)
- **Legal Team** (Data breach or compliance issues)
- **Customer Success** (High-touch customer impact)

## Tools and Resources

### Monitoring and Alerting
- **Grafana**: http://grafana.internal/dashboards
- **Prometheus**: http://prometheus.internal
- **AlertManager**: http://alertmanager.internal
- **Status Page**: https://status.claude-agents.com

### Communication
- **Slack Channels**: #incidents, #on-call, #engineering
- **PagerDuty**: https://claude-agents.pagerduty.com
- **Zoom Bridge**: [EMERGENCY BRIDGE NUMBER]

### Documentation
- **Runbooks**: Internal wiki /runbooks
- **Architecture Docs**: Internal wiki /architecture
- **API Documentation**: Internal wiki /api-docs
- **Deployment Guides**: Internal wiki /deployment

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-XX  
**Owner**: Platform Operations Team  
**Review Schedule**: After each P0/P1 incident and quarterly