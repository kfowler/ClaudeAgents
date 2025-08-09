# Development Crisis Management

Handle development emergencies and critical issues across your entire stack:

**Incident Response Coordination:**
- Assess severity and impact of issues across services
- Coordinate response across team members via multiple channels
- Establish incident command structure for major outages
- Document timeline and response actions for post-mortems

**Multi-Service Triage:**
- Check health of services running on pi via dokku
- Verify database connectivity and performance in OrbStack
- Test API endpoints and service dependencies
- Monitor system resources and identify bottlenecks

**Emergency Communication:**
- Send immediate alerts via SMS/iMessage for critical issues
- Update team channels with status and resolution progress  
- Communicate with stakeholders via email for longer outages
- Coordinate with external vendors or service providers

**Rapid Diagnostics:**
- SSH into pi to check logs and system status
- Query PostgreSQL for data consistency and performance issues
- Check OrbStack container health and resource usage
- Analyze nginx logs for traffic patterns and errors

**Emergency Fixes:**
- Deploy hotfixes via dokku with minimal downtime
- Implement temporary workarounds while permanent fixes develop
- Coordinate rollbacks if deployments cause additional issues
- Scale resources or restart services as emergency measures

**Documentation & Learning:**
- Create incident reports with timeline and root cause analysis
- Update runbooks and emergency procedures based on lessons learned
- Share knowledge with team to prevent similar issues
- Establish preventive measures and monitoring improvements

**Recovery Verification:**
- Test all critical paths after emergency resolution
- Verify data consistency and no corruption occurred
- Monitor for cascading effects or delayed symptoms
- Communicate all-clear status to stakeholders

Crisis Type/Service: $ARGUMENTS

