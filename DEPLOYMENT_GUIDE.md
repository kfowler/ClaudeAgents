# Claude Code 2.0 Enhanced Agent System - Deployment Guide

This guide provides comprehensive instructions for deploying the Claude Code 2.0 enhancements using our phased rollout approach.

## Overview

The Claude Code 2.0 deployment uses a sophisticated 4-phase rollout strategy designed to minimize risk while ensuring comprehensive validation at each step:

- **Phase 1: Alpha Deployment** - Internal testing environment
- **Phase 2: Beta Deployment** - Limited external users with canary strategy
- **Phase 3: Gradual Production Rollout** - Incremental traffic scaling (10% → 100%)
- **Phase 4: Full Production** - Complete deployment with optimization

## Quick Start

### Prerequisites

Ensure you have the following tools installed:
- `kubectl` (v1.28+)
- `helm` (v3.12+)
- `docker` (v24.0+)
- `python3` (v3.11+)
- `istioctl` (v1.19+) - for advanced traffic management
- `curl`, `jq`, `bc` - for monitoring and validation

### Basic Deployment

```bash
# Full deployment with all phases
./deploy-claude-2.0.sh deploy

# Deploy specific phase
./deploy-claude-2.0.sh phase1
./deploy-claude-2.0.sh phase2
./deploy-claude-2.0.sh phase3
./deploy-claude-2.0.sh phase4

# Check deployment status
./deploy-claude-2.0.sh status

# Start monitoring dashboard
./deploy-claude-2.0.sh monitor
```

## Detailed Phase Descriptions

### Phase 1: Alpha Deployment (Internal Testing)

**Objective**: Deploy to development environment for internal validation

**Infrastructure**:
- Single Kubernetes namespace (`claude-agents-alpha`)
- Minimal resource allocation (1 replica per service)
- Basic monitoring and logging
- SQLite or single PostgreSQL instance

**Validation Criteria**:
- All services start successfully
- Basic API endpoints respond
- Smoke tests pass (>90% success rate)
- System health score >80%

**Duration**: ~15-30 minutes

**Command**:
```bash
# Execute Phase 1 only
./deployment/scripts/phase1-alpha-deploy.sh

# Or via master script
./deploy-claude-2.0.sh phase1
```

**Access**:
```bash
kubectl port-forward -n claude-agents-alpha service/orchestrator 8080:8080
# Visit http://localhost:8080
```

### Phase 2: Beta Deployment (Limited External Users)

**Objective**: Production-like environment with external user testing

**Infrastructure**:
- Dedicated namespace (`claude-agents-beta`)
- Multiple replicas with auto-scaling
- Production-grade PostgreSQL with read replicas
- Load balancing and canary deployment capabilities
- Comprehensive monitoring with Prometheus/Grafana

**Key Features**:
- Canary deployment strategy (25% initial traffic)
- Production-like load testing
- User feedback collection
- Advanced monitoring and alerting

**Validation Criteria**:
- System availability >99.9%
- p95 response time <750ms under peak load
- Error rate <1%
- User satisfaction score >8/10
- Successful handling of 2x traffic spikes

**Duration**: ~45-60 minutes

**Command**:
```bash
# Execute Phase 2 only
./deployment/scripts/phase2-beta-deploy.sh

# Or via master script
./deploy-claude-2.0.sh phase2
```

**Access**:
```bash
# Via ingress (if configured)
https://beta.claude-agents.local

# Or port-forward
kubectl port-forward -n claude-agents-beta service/orchestrator 8080:8080
```

### Phase 3: Gradual Production Rollout

**Objective**: Deploy to production with incremental traffic scaling

**Infrastructure**:
- Production namespace (`claude-agents-prod`)
- High-availability setup with multiple zones
- Advanced traffic management with Istio
- Horizontal Pod Autoscaling (HPA)
- Production-grade security policies

**Traffic Scaling Steps**:
1. **10% Traffic** (15 minutes monitoring)
2. **25% Traffic** (30 minutes monitoring)
3. **50% Traffic** (30 minutes monitoring)
4. **75% Traffic** (60 minutes monitoring)
5. **100% Traffic** (30 minutes final validation)

**Validation Criteria**:
- System availability >99.99%
- p95 response time <1s under normal load
- Error rate <0.1%
- No performance degradation between steps
- Successful automated rollback capabilities

**Duration**: ~3-4 hours

**Command**:
```bash
# Execute Phase 3 only
./deployment/scripts/phase3-gradual-production.sh

# Or via master script
./deploy-claude-2.0.sh phase3
```

**Monitoring**:
```bash
# Real-time traffic monitoring
kubectl port-forward -n claude-agents-prod service/grafana 3000:3000
# Visit http://localhost:3000

# Istio traffic dashboard
istioctl dashboard kiali
```

### Phase 4: Full Production & Optimization

**Objective**: Enable all features and implement ongoing optimization

**Infrastructure**:
- Full production capacity (10+ replicas per service)
- All features enabled via configuration
- Advanced monitoring and observability
- Cost optimization with VerticalPodAutoscaler
- Backup and disaster recovery systems
- Security hardening and compliance

**Key Features Enabled**:
- Advanced learning and semantic search
- Multi-agent workflow orchestration
- Real-time analytics and insights
- A/B testing framework
- Performance profiling and optimization
- Chaos engineering for resilience testing

**Optimization Systems**:
- ML-based resource optimization
- Automated cost reporting
- Predictive scaling
- Continuous security scanning
- Automated backup procedures

**Duration**: ~60-90 minutes

**Command**:
```bash
# Execute Phase 4 only
./deployment/scripts/phase4-full-production.sh

# Or via master script
./deploy-claude-2.0.sh phase4
```

## Advanced Usage

### Environment Variables

```bash
# Set custom version
export VERSION=v2.1.0

# Skip validation (not recommended for production)
export SKIP_VALIDATION=true

# Enable auto-proceed mode
export AUTO_PROCEED=true

# Enable dry-run mode
export DRY_RUN=true
```

### Custom Deployment Options

```bash
# Deploy with custom version
./deploy-claude-2.0.sh --version=v2.1.0 deploy

# Skip validation steps
./deploy-claude-2.0.sh --skip-validation deploy

# Dry run to see what would be deployed
./deploy-claude-2.0.sh --dry-run deploy

# Auto-proceed without manual confirmations
./deploy-claude-2.0.sh --auto-proceed deploy

# Start from specific phase
./deploy-claude-2.0.sh --phase=beta deploy
```

### Rollback Procedures

```bash
# Execute comprehensive rollback
./deploy-claude-2.0.sh rollback

# Phase-specific rollback
./deployment/scripts/phase1-alpha-deploy.sh rollback
./deployment/scripts/phase2-beta-deploy.sh rollback
./deployment/scripts/phase3-gradual-production.sh rollback

# Manual rollback via rollback manager
python3 rollback/rollback_manager.py --execute --type full
```

## Monitoring and Observability

### Monitoring Dashboard

Access the comprehensive rollout monitoring dashboard:

```bash
# Start port-forward to Grafana
kubectl port-forward -n claude-agents-prod service/grafana 3000:3000

# Visit http://localhost:3000
# Default credentials: admin/admin
```

### Key Metrics to Monitor

**Golden Signals**:
- **Latency**: p50, p95, p99 response times
- **Traffic**: Requests per second, user sessions
- **Errors**: Error rate, exception counts
- **Saturation**: CPU, memory, disk usage

**SLI/SLO Targets**:
- **Availability**: 99.95% uptime
- **Response Time**: p95 < 1s
- **Error Rate**: < 0.1%
- **Recovery Time**: < 5 minutes

### Alerting

Critical alerts are configured for:
- Service downtime
- High error rates (>5%)
- Performance degradation (>50% increase in latency)
- Resource exhaustion (>90% utilization)
- Security incidents

## Troubleshooting

### Common Issues

**1. Pod Startup Failures**
```bash
# Check pod logs
kubectl logs -n <namespace> deployment/<service-name>

# Check events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Check resource constraints
kubectl describe pod -n <namespace> <pod-name>
```

**2. Service Discovery Issues**
```bash
# Check service endpoints
kubectl get endpoints -n <namespace>

# Test DNS resolution
kubectl exec -it <pod-name> -n <namespace> -- nslookup <service-name>
```

**3. Database Connection Issues**
```bash
# Check PostgreSQL status
kubectl exec -it deployment/postgres -n <namespace> -- psql -U claude -d claude_agents -c "SELECT 1;"

# Check Redis connectivity
kubectl exec -it deployment/redis -n <namespace> -- redis-cli ping
```

**4. Traffic Routing Issues**
```bash
# Check Istio configuration
kubectl get virtualservice,destinationrule -n <namespace>

# Validate Istio proxy configuration
istioctl proxy-config cluster <pod-name>.<namespace>
```

### Log Locations

All deployment logs are stored in:
- `deployment/logs/` - Deployment script logs
- `validation_reports/` - Validation framework results
- Kubernetes logs: `kubectl logs -n <namespace> <pod-name>`

### Recovery Procedures

**Emergency Rollback**:
```bash
# Immediate traffic redirection (production)
kubectl patch virtualservice claude-agents-routing -n claude-agents-prod --type='merge' -p='{"spec":{"http":[{"route":[{"destination":{"host":"orchestrator","subset":"stable"},"weight":100}]}]}}'

# Scale down new version
kubectl scale deployment orchestrator-new --replicas=0 -n claude-agents-prod
```

**Health Check Validation**:
```bash
# Quick health check
curl -f http://localhost:8080/health

# Comprehensive validation
python3 rollout_validation.py --phase post-deployment
```

## Security Considerations

### Network Policies

All deployments include:
- Namespace isolation
- Ingress/egress traffic controls
- Service mesh security (mTLS)

### Secrets Management

- Kubernetes secrets for database credentials
- JWT token rotation
- TLS certificate management
- API key protection

### Compliance

- Regular security scans (daily)
- Vulnerability assessments
- Configuration compliance checks
- Audit logging enabled

## Performance Tuning

### Resource Optimization

The deployment includes:
- Vertical Pod Autoscaler (VPA) recommendations
- Horizontal Pod Autoscaler (HPA) configuration
- Resource quotas and limits
- Cost optimization reporting

### Scaling Configuration

```yaml
# Example HPA configuration
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 60
  targetMemoryUtilizationPercentage: 70
```

## Cost Optimization

### FinOps Features

- Automated cost reporting
- Resource utilization optimization
- Spot instance recommendations
- Idle resource detection

### Cost Monitoring

```bash
# Daily cost reports
kubectl logs job/cost-optimization-report -n claude-agents-prod

# VPA recommendations
kubectl get vpa -n claude-agents-prod -o yaml
```

## Backup and Disaster Recovery

### Automated Backups

- PostgreSQL: Daily backups with 7-day retention
- Redis: Daily RDB snapshots
- Configuration: GitOps-based versioning

### Recovery Procedures

```bash
# Restore from backup
kubectl create job --from=cronjob/postgres-backup postgres-restore -n claude-agents-prod

# Verify data integrity
kubectl exec -it deployment/postgres -n claude-agents-prod -- psql -U claude_prod -d claude_agents_prod -c "SELECT count(*) FROM agents;"
```

## Support and Maintenance

### Documentation

- Deployment logs: `deployment/logs/`
- Runbooks: `operations/runbooks/`
- API documentation: Available in deployed services

### Contact Information

- **Operations Team**: Available 24/7 via on-call rotation
- **Engineering Team**: Regular business hours support
- **Emergency Escalation**: Automated via monitoring alerts

### Regular Maintenance

- **Daily**: Automated backups and security scans
- **Weekly**: Performance optimization cycles
- **Monthly**: Disaster recovery testing
- **Quarterly**: Comprehensive security audits

---

## Conclusion

The Claude Code 2.0 deployment system provides a robust, scalable, and secure foundation for rolling out AI agent enhancements. The phased approach ensures reliability while the comprehensive monitoring and validation frameworks provide confidence in production deployments.

For additional support or questions, refer to the operational runbooks or contact the engineering team.