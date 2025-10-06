# Deployment Preparation

Comprehensive deployment preparation orchestrating multiple specialized agents for production-ready releases.

## Orchestration Flow

This command coordinates multiple agents to ensure bulletproof deployments:

1. **qa-test-engineer**: Validates test coverage and quality gates
2. **security-audit-specialist**: Performs security assessment and vulnerability scanning
3. **devops-engineer**: Prepares infrastructure and deployment pipelines
4. **systems-engineer**: Optimizes performance and resource utilization
5. **accessibility-expert**: Ensures compliance with accessibility standards

## Pre-Deployment Phase

### Quality Validation
**Agent: qa-test-engineer**
- Execute comprehensive test suite (unit, integration, E2E)
- Validate test coverage meets thresholds (>80% for critical paths)
- Run performance benchmarks against SLAs
- Execute chaos engineering tests for resilience
- Verify backward compatibility for APIs

### Security Assessment
**Agent: security-audit-specialist**
- Scan for known vulnerabilities (OWASP Top 10)
- Validate secrets management and encryption
- Check dependency vulnerabilities with CVE scanning
- Perform penetration testing on staging environment
- Verify compliance requirements (SOC 2, GDPR, HIPAA)

### Infrastructure Preparation
**Agent: devops-engineer**
- Validate infrastructure as code configurations
- Test auto-scaling policies under load
- Verify backup and disaster recovery procedures
- Configure monitoring, logging, and alerting
- Prepare rollback strategies and feature flags

## Build & Optimization Phase

### Performance Optimization
**Agent: systems-engineer**
- Profile application for memory leaks and bottlenecks
- Optimize database queries and connection pooling
- Minimize bundle sizes and asset optimization
- Configure CDN and caching strategies
- Validate resource limits and scaling parameters

### Accessibility Compliance
**Agent: accessibility-expert**
- Validate WCAG 2.1 AA compliance
- Test with screen readers and assistive technologies
- Verify keyboard navigation and focus management
- Check color contrast and visual accessibility
- Ensure mobile accessibility standards

## Deployment Execution

### Progressive Rollout Strategy
**Agent: devops-engineer**
- **Canary Deployment**: 5% traffic for 30 minutes
- **Blue-Green Staging**: 50% traffic for 2 hours
- **Full Production**: 100% after validation
- **Feature Flags**: Gradual feature enablement
- **Geographic Rollout**: Region-by-region deployment

### Monitoring & Validation
- Real-time metrics dashboard
- Error rate monitoring (<0.1% threshold)
- Performance metrics (p50, p95, p99 latencies)
- User experience monitoring (Core Web Vitals)
- Business metrics validation

## Post-Deployment Phase

### Health Verification
**Automated Checks:**
- API endpoint health checks
- Database connection validation
- External service integration tests
- SSL certificate validation
- DNS propagation verification

### Documentation & Knowledge Transfer
**Agent: code-architect**
- Update deployment runbooks
- Document configuration changes
- Create incident response procedures
- Update architecture diagrams
- Record lessons learned

## Rollback Procedures

### Automated Rollback Triggers
- Error rate exceeds 1%
- Response time degrades >50%
- Memory/CPU usage exceeds limits
- Critical business metrics drop
- Security breach detected

### Rollback Strategy
1. **Immediate**: Revert to previous version
2. **Data Migration**: Handle schema changes
3. **Cache Invalidation**: Clear CDN and caches
4. **Communication**: Notify stakeholders
5. **Post-Mortem**: Analyze failure causes

## Command Parameters

```
Deployment Environment: $ENVIRONMENT (staging|production)
Target Version: $VERSION
Rollout Strategy: $STRATEGY (canary|blue-green|rolling|immediate)
Risk Level: $RISK (low|medium|high|critical)
Compliance Requirements: $COMPLIANCE (none|sox|gdpr|hipaa|pci)
```

## Success Criteria

✅ All tests passing (100% critical path coverage)
✅ Zero critical security vulnerabilities
✅ Performance within SLA boundaries
✅ Accessibility compliance validated
✅ Rollback tested and verified
✅ Monitoring and alerting active
✅ Documentation updated
✅ Team notified and ready

## Emergency Contacts

- **On-Call Engineer**: Via PagerDuty
- **Security Team**: Via security escalation
- **Product Owner**: Via stakeholder list
- **Customer Success**: For user communications

This comprehensive deployment preparation ensures production readiness through multi-agent collaboration and rigorous validation processes.