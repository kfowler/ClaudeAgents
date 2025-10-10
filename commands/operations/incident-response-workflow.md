---
name: incident-response-workflow
description: "Production incident management workflow coordinating site-reliability-engineer, devops-engineer, and technical-writer to deliver structured incident detection, triage, resolution, communication, and blameless postmortems"
agents:
  - site-reliability-engineer
  - devops-engineer
  - technical-writer
complexity: high
duration: 2-4 hours (initial setup), continuous operation during incidents
---

# Incident Response Workflow

**Command:** `/operations:incident-response-workflow`
**Agents:** `site-reliability-engineer`, `devops-engineer`, `technical-writer`
**Complexity:** High
**Duration:** 2-4 hours (initial setup), continuous operation during incidents

## Overview

Comprehensive production incident management framework that transforms chaotic war rooms into structured, efficient incident response. This workflow coordinates detection, triage, communication, resolution, and learning across the complete incident lifecycle - from initial alert to blameless postmortem - reducing MTTR by 50-70%, improving stakeholder communication by 80%+, and building organizational resilience through systematic learning.

## What This Command Does

This command orchestrates structured incident response across 6 phases, delivering consistent, efficient incident management that minimizes customer impact, reduces engineering stress, maintains stakeholder trust, and transforms every incident into a learning opportunity that prevents recurrence.

### Phase 1: Incident Detection and Initial Response (Immediate, <5 minutes)
**Lead:** `site-reliability-engineer`

Detect incidents quickly and initiate structured response:

- **Incident Detection Mechanisms**: Multiple detection paths
  - **Automated Monitoring Alerts**: Prometheus, Datadog, CloudWatch, New Relic alerts
    - SLO breach detection (error budget burn rate exceeding threshold)
    - Availability monitoring (service health checks failing)
    - Performance degradation (latency p95/p99 exceeding SLO)
    - Error rate spikes (5xx errors, exception rates)
    - Infrastructure alerts (CPU, memory, disk saturation)
  - **External Monitoring**: Pingdom, UptimeRobot, Catchpoint synthetic checks
    - User-facing endpoint availability from multiple regions
    - SSL certificate expiration warnings
    - DNS resolution failures
  - **Customer Reports**: Support tickets, social media, direct customer feedback
    - Support ticket volume spikes (auto-detection via Zendesk/Intercom)
    - Social media monitoring (Twitter, Reddit, forums)
    - Customer-facing error tracking (Sentry, Bugsnag user reports)
  - **Security Alerts**: Intrusion detection, anomaly detection, security tool alerts
    - WAF blocks (unusual traffic patterns)
    - Authentication failures (brute force attempts)
    - Data exfiltration detection
  - **Business Metric Anomalies**: Revenue, conversion, user activity drops
    - Revenue drop >10% in 15-minute window
    - Conversion funnel drop-off anomalies
    - Active user count sudden decreases

- **Incident Declaration Criteria**: When to declare an incident
  - **Automatic Incident Creation**:
    - P0: Customer-impacting outage (availability <99% over 5min window)
    - P0: Critical security breach or data exposure
    - P0: Revenue-impacting system failure (payment processing down)
    - P1: Significant service degradation (latency 3x normal)
    - P1: Multiple customer reports of same issue
  - **Manual Incident Declaration**:
    - On-call engineer assessment of situation
    - Support team escalation for widespread customer impact
    - Security team identification of potential breach
    - Executive escalation for business-critical issues

- **Initial Alert Response Procedure**: First 5 minutes
  - **Acknowledge Alert** (within 1 minute):
    - PagerDuty/Opsgenie acknowledgment to stop escalation
    - Post in incident Slack channel: "Alert acknowledged, investigating"
    - Claim incident ownership in incident management tool
  - **Assess Severity** (within 3 minutes):
    - Check monitoring dashboards for scope of impact
    - Query metrics for affected user percentage (1%, 10%, 100%?)
    - Estimate business impact (revenue loss rate, user count)
    - Determine if this is a new incident or related to existing incident
  - **Declare Incident or Resolve False Positive** (within 5 minutes):
    - If real incident: Create incident ticket, set severity, start war room
    - If false positive: Document reasoning, suppress alert, tune threshold
    - If related to existing incident: Link to parent incident, do NOT create duplicate

- **Incident Severity Classification**: P0 through P3
  - **P0 - Critical (All hands on deck)**:
    - Complete outage of customer-facing service
    - Data loss or corruption affecting customers
    - Security breach with confirmed data exposure
    - Revenue-generating system completely down
    - **Response SLA**: Acknowledge <1min, engage <5min, all hands <15min
    - **Stakeholder Notification**: Immediate (executives, customers, support)
  - **P1 - High (Urgent response required)**:
    - Significant service degradation (>20% of requests affected)
    - Partial outage affecting subset of customers
    - Payment processing delays or failures
    - Performance degradation exceeding SLO by 3x
    - **Response SLA**: Acknowledge <5min, engage <15min, escalate <30min
    - **Stakeholder Notification**: Within 30min (executives, support)
  - **P2 - Medium (Scheduled response)**:
    - Minor degradation affecting <5% of requests
    - Non-critical feature unavailable
    - Elevated error rates not yet impacting users
    - **Response SLA**: Acknowledge <15min, engage during business hours
    - **Stakeholder Notification**: Daily summary, no immediate notification
  - **P3 - Low (Monitor and plan)**:
    - Cosmetic issues, minor bugs
    - Monitoring alerts for trending issues
    - Capacity warnings (not yet critical)
    - **Response SLA**: Acknowledge <1 hour, fix when convenient
    - **Stakeholder Notification**: Weekly summary

**Deliverables:**
- **Incident Ticket** (created in <5 minutes)
  - Title: Clear, concise description of user-facing impact
  - Severity: P0/P1/P2/P3 classification
  - Detection method: How was this discovered?
  - Initial impact assessment: Users affected, business impact
  - Assigned incident commander (IC) and responders
- **War Room** (Slack channel or video call)
  - P0/P1: Dedicated Slack channel `#incident-YYYY-MM-DD-description`
  - P0: Zoom/Meet video call for synchronous coordination
  - P2/P3: Updates in general incident channel
- **Initial Status Update** (posted within 10 minutes)
  - "We are investigating [issue]. Estimated impact: [X% of users/transactions]"

### Phase 2: Incident Triage and War Room Coordination (5-30 minutes)
**Lead:** `site-reliability-engineer`

Establish structured incident command and coordinate response:

- **Incident Commander (IC) Role Assignment**: Single point of coordination
  - **IC Responsibilities**:
    - Own incident resolution end-to-end
    - Coordinate all responders (who does what)
    - Make critical decisions (rollback, failover, scale up)
    - Manage communication (internal, customer, executive)
    - Ensure documentation and timeline tracking
    - Declare incident resolved when appropriate
  - **IC Selection**:
    - Default: On-call SRE or most senior responder
    - P0 incidents: May require engineering manager or director as IC
    - IC can delegate tasks but owns overall coordination

- **War Room Setup and Norms**: Structured communication
  - **Slack War Room Channel**:
    - Naming: `#incident-2025-10-08-checkout-failure`
    - Pin incident ticket, runbook, dashboard links
    - Set topic with severity and current status
    - Post updates every 15-30 minutes (P0), every hour (P1)
  - **Video Call (P0 only)**:
    - Zoom/Meet link shared in Slack channel
    - IC runs the call, mutes non-speakers
    - Screen share dashboards, logs, metrics
  - **Communication Norms**:
    - IC posts questions, responders answer in thread
    - Use status emoji (👀 investigating, 🔧 fixing, ✅ resolved)
    - Minimize noise - only incident-related messages
    - Save casual discussion for after incident resolution

- **Responder Roles and Responsibilities**: Define who does what
  - **Incident Commander (IC)**: Coordination, decision-making, communication
  - **Resolver/SME (Subject Matter Expert)**: Technical investigation and fixes
    - Debug the issue using logs, metrics, traces
    - Implement fixes (rollback, config change, restart services)
    - Validate fix effectiveness
  - **Communication Lead**: Stakeholder updates (IC can delegate)
    - Draft customer status page updates
    - Notify executives with impact summaries
    - Update support team with customer communication guidance
  - **Scribe**: Timeline documentation (IC can delegate)
    - Log all actions taken with timestamps
    - Record key findings and decisions
    - Track responders and their contributions
    - Note customer impact changes over time

- **Situation Assessment and Hypotheses**: Structured investigation
  - **Gather Context** (first 10 minutes):
    - Recent changes: Deployments, config changes, infrastructure changes
    - Monitoring data: Metrics, logs, traces showing abnormal behavior
    - Blast radius: Which services, regions, customer segments affected?
    - Similar past incidents: Has this happened before? What fixed it?
  - **Form Hypotheses** (actionable guesses):
    - "Hypothesis: Recent deployment introduced N+1 query causing DB overload"
    - "Hypothesis: Traffic spike from bot traffic exceeding capacity"
    - "Hypothesis: External API timeout cascading to our services"
  - **Prioritize Investigation**:
    - Test most likely hypothesis first (recent deployment)
    - Test quickest to validate hypotheses (check logs vs. deep code analysis)
    - Parallel investigation when multiple strong hypotheses

**Deliverables:**
- **Incident Command Structure** (clear roles and ownership)
  - IC assigned and coordinating response
  - Responders assigned to investigation and remediation
  - Communication lead drafting stakeholder updates
  - Scribe documenting timeline
- **War Room Active** (Slack + video call if needed)
  - All responders present and coordinating
  - Clear communication norms established
  - IC posting regular status updates
- **Initial Investigation Summary** (within 30 minutes)
  - Current hypotheses and investigation status
  - Actions taken so far (rollbacks attempted, logs checked)
  - Next steps and expected timeline
  - Updated impact assessment (user count, revenue impact)

### Phase 3: Diagnosis and Root Cause Identification (15 minutes - 2 hours)
**Lead:** `site-reliability-engineer` + `devops-engineer`

Identify root cause using observability data and system knowledge:

- **Observability-Driven Diagnosis**: Use logs, metrics, traces
  - **Start with Monitoring Dashboards**:
    - Service health dashboard (which services are red?)
    - Golden signals dashboard (latency, traffic, errors, saturation)
    - Infrastructure dashboard (CPU, memory, disk, network)
    - Business metrics dashboard (revenue, conversions, active users)
  - **Drill into Metrics**:
    - Identify anomalies (spikes, drops, patterns)
    - Correlate metrics across services (API errors → database slow queries)
    - Check time alignment (did error rate spike at same time as deployment?)
  - **Analyze Distributed Traces**:
    - Sample slow requests to identify bottlenecks
    - Identify failing service in microservices chain
    - Trace database queries, external API calls causing delays
  - **Search Logs**:
    - Filter by time window and severity (ERROR, FATAL)
    - Search for exception stack traces
    - Look for patterns in error messages
    - Correlate log events with metric spikes

- **Common Root Cause Patterns**: What to look for
  - **Recent Deployment Issues** (50% of incidents):
    - Code bug introduced in recent release
    - Database migration causing slow queries
    - Configuration error in new deployment
    - Missing environment variable or secret
  - **Capacity and Scaling Issues** (20% of incidents):
    - Traffic spike exceeding auto-scaling limits
    - Database connection pool exhaustion
    - Memory leaks causing OOM crashes
    - Disk space exhaustion
  - **External Dependency Failures** (15% of incidents):
    - Third-party API timeouts or errors
    - DNS resolution failures
    - Cloud provider outages (AWS, GCP, Azure)
    - CDN or external service degradation
  - **Infrastructure Issues** (10% of incidents):
    - Kubernetes node failures
    - Load balancer misconfigurations
    - Network partitions or latency spikes
    - Certificate expirations
  - **Data Issues** (5% of incidents):
    - Database replication lag
    - Cache invalidation issues
    - Data corruption or schema mismatches

- **Hypothesis Testing and Validation**: Confirm root cause
  - **Test Hypothesis**:
    - "If deployment is the issue, rollback should fix it"
    - "If database is overloaded, scaling read replicas should reduce latency"
    - "If external API is failing, circuit breaker should prevent cascading failures"
  - **Validation Criteria**:
    - Metrics return to normal after mitigation
    - Error rate drops to <0.1%
    - User-facing symptoms resolved
    - Monitoring confirms stability for 15+ minutes

- **Runbook Usage**: Follow documented procedures
  - **Runbook Structure**:
    - Symptoms: Error messages, metric patterns, user-reported issues
    - Diagnosis steps: What to check, in what order
    - Mitigation: Quick fixes to reduce customer impact
    - Resolution: Permanent fixes to address root cause
  - **Common Runbooks**:
    - "Database Connection Pool Exhaustion" → increase pool size, restart services
    - "Payment Gateway Timeout" → enable circuit breaker, retry with backoff
    - "Memory Leak in Service X" → restart pods, deploy memory fix
    - "Certificate Expiration" → renew certificate, update load balancer

**Deliverables:**
- **Root Cause Identification** (with supporting evidence)
  - Clear statement: "Root cause is [X] because [evidence Y and Z]"
  - Supporting metrics, logs, traces showing the issue
  - Timeline of events leading to incident
  - Confirmation through hypothesis testing
- **Impact Assessment** (quantified customer impact)
  - Total users affected: X% of active users
  - Duration of impact: Y minutes of degradation
  - Revenue impact: Estimated $Z lost or delayed
  - SLO impact: X minutes of error budget consumed

### Phase 4: Mitigation and Resolution (Immediate - 4 hours)
**Lead:** `devops-engineer` + `site-reliability-engineer`

Restore service and resolve root cause:

- **Mitigation vs. Resolution Strategy**: Stop the bleeding first
  - **Mitigation (first)**: Reduce customer impact immediately
    - Rollback recent deployment
    - Restart failing services
    - Scale up infrastructure
    - Enable circuit breakers or rate limiting
    - Redirect traffic to healthy region
  - **Resolution (second)**: Fix root cause permanently
    - Deploy proper code fix
    - Optimize database queries
    - Increase capacity limits
    - Fix configuration errors
    - Update runbooks and alerts

- **Common Mitigation Actions**: Fast customer impact reduction
  - **Rollback Deployment** (fastest, safest for deployment issues):
    - Roll back to last known good version
    - Validate rollback success with metrics
    - Communicate rollback to team
  - **Service Restart** (for memory leaks, connection pool exhaustion):
    - Rolling restart to avoid downtime
    - Monitor metrics during restart
    - Validate health checks pass
  - **Infrastructure Scaling** (for capacity issues):
    - Scale up instances/pods
    - Increase database connection pool size
    - Add read replicas for database
    - Increase resource limits (CPU, memory)
  - **Traffic Management** (for partial failures):
    - Drain traffic from unhealthy instances
    - Redirect to backup region
    - Enable maintenance mode for affected features
  - **Circuit Breakers and Fallbacks** (for external dependency failures):
    - Enable circuit breaker to fail fast
    - Serve cached/stale data
    - Degrade gracefully (disable non-critical features)

- **Change Management During Incidents**: Safe changes under pressure
  - **Approval Requirements**:
    - P0: IC approves all changes (can be verbal/Slack)
    - P1: IC + one other engineer approval
    - P2/P3: Standard change management process
  - **Change Communication**:
    - Announce change in war room before executing
    - Post change confirmation after execution
    - Roll back if change makes situation worse
  - **Change Validation**:
    - Monitor metrics for 5-15 minutes after change
    - Confirm error rate decreases
    - Validate user-facing symptoms improve
    - Check for secondary impacts

- **Resolution Validation and Monitoring**: Confirm stability
  - **Validation Criteria**:
    - Error rate <0.1% for 15+ minutes
    - Latency p95/p99 within SLO targets
    - All health checks passing
    - Customer reports of issues stopped
    - Monitoring dashboards green
  - **Soak Period**: Monitor for stability
    - P0: 30-60 minutes stable before declaring resolved
    - P1: 15-30 minutes stable
    - P2/P3: 5-15 minutes stable
  - **Secondary Impact Check**:
    - Did the fix cause issues elsewhere?
    - Are downstream services healthy?
    - Database replication lag normal?

**Deliverables:**
- **Service Restored** (customer-facing impact eliminated)
  - Metrics returned to normal levels
  - Error rate <0.1%
  - Latency within SLO
  - User reports of issues stopped
- **Root Cause Resolved** (permanent fix deployed or planned)
  - Immediate fix deployed (rollback, restart, scale)
  - Permanent fix in progress (code fix, architecture change)
  - Follow-up tasks created for long-term prevention
- **Stability Confirmed** (monitoring shows sustained health)
  - 30+ minutes of stable metrics (P0)
  - No secondary incidents triggered
  - All systems green

### Phase 5: Communication and Stakeholder Updates (Throughout incident)
**Lead:** `site-reliability-engineer` + `technical-writer`

Maintain clear, timely communication with all stakeholders:

- **Internal Communication**: Keep team informed
  - **War Room Updates** (every 15-30 minutes):
    - Status: Investigating / Mitigating / Resolved
    - Current hypothesis and actions in progress
    - Next steps and estimated timeline
    - Impact update (users affected, duration)
  - **Engineering-Wide Updates** (hourly for P0, as needed for P1):
    - Post in general engineering Slack channel
    - Summary of situation and current status
    - Expected resolution time
    - How engineers can help (or stay out of the way)
  - **On-Call Handoff** (if incident spans shifts):
    - Comprehensive handoff document
    - Current status and actions taken
    - Outstanding hypotheses and next steps
    - Key people and escalation contacts

- **Executive Communication**: Business impact focus
  - **Initial Notification** (P0: <15min, P1: <30min):
    - Subject: "[P0 INCIDENT] Checkout system down, 100% of users affected"
    - Impact: "Customers cannot complete purchases. Estimated revenue loss: $5K/minute"
    - Status: "Team investigating. Rollback in progress."
    - Next update: "Update in 30 minutes or when resolved"
  - **Progress Updates** (every 30-60 minutes):
    - Current status and actions taken
    - Updated impact estimate
    - Expected resolution time
    - Business implications (revenue loss, customer impact)
  - **Resolution Notification**:
    - "Incident resolved at [time]. Total duration: X minutes"
    - "Total customer impact: Y% of users for Z minutes"
    - "Estimated revenue impact: $X"
    - "Root cause: [brief explanation]"
    - "Follow-up actions: [prevention work planned]"

- **Customer Communication**: Maintain trust and transparency
  - **Status Page Updates** (StatusPage.io, Atlassian Statuspage):
    - **Investigating** (within 15 minutes of P0 detection):
      - "We are investigating reports of issues with [service]. Customers may experience [symptom]."
    - **Identified** (once root cause known):
      - "We have identified the issue as [brief explanation]. We are working on a fix."
    - **Monitoring** (after mitigation):
      - "A fix has been implemented and we are monitoring the results."
    - **Resolved**:
      - "This incident has been resolved. Service is fully operational."
  - **Support Team Updates**:
    - Provide support team with customer-facing talking points
    - Update FAQ with common customer questions
    - Notify when to stop creating incident-related tickets
  - **Proactive Customer Emails** (for major P0 incidents):
    - Post-incident summary to affected customers
    - Apology, explanation, prevention commitments
    - Compensation if appropriate (credits, refunds)

- **Communication Templates**: Pre-drafted for speed
  - **Slack Status Update Template**:
    ```
    [Timestamp] INCIDENT UPDATE - P0 - Checkout Failure

    STATUS: Mitigating
    IMPACT: 100% of checkout attempts failing since 2:15pm EST
    ROOT CAUSE: Database connection pool exhausted due to slow query introduced in v2.34 deployment
    ACTIONS TAKEN:
    - Rolled back deployment to v2.33 at 2:30pm
    - Restarted database connection pools at 2:32pm
    - Monitoring error rate (currently 12%, down from 98%)
    NEXT STEPS:
    - Continue monitoring for 30 minutes
    - Prepare hotfix for slow query issue
    ETA: Service fully restored by 3:00pm EST
    REVENUE IMPACT: Estimated $15K lost (45min outage)
    ```
  - **Status Page Template**:
    ```
    Investigating - We are investigating reports of checkout failures.
    Customers may experience errors when attempting to complete purchases.
    We apologize for the inconvenience and are working to resolve this as quickly as possible.
    ```
  - **Executive Update Template**:
    ```
    Subject: [P0 INCIDENT - RESOLVED] Checkout System Outage

    SUMMARY: Checkout system experienced a 45-minute outage affecting 100% of purchase attempts.

    TIMELINE:
    - 2:15pm EST: Incident detected via monitoring alerts
    - 2:18pm EST: Incident declared, war room started
    - 2:30pm EST: Root cause identified (slow DB query in v2.34)
    - 2:32pm EST: Rollback to v2.33 completed
    - 2:45pm EST: Service fully restored and stable

    IMPACT:
    - Duration: 45 minutes
    - Users affected: 100% of checkout attempts
    - Revenue impact: Estimated $15K lost
    - Customer complaints: 47 support tickets

    ROOT CAUSE: Database query introduced in v2.34 deployment caused connection pool exhaustion.

    PREVENTION:
    - Implement query performance testing in CI pipeline
    - Add connection pool monitoring alerts
    - Conduct post-mortem and share learnings

    Next update: Post-mortem document by end of week.
    ```

**Deliverables:**
- **Communication Log** (all stakeholder updates documented)
  - Timestamps of all internal and external communications
  - Content of status page updates
  - Executive email trail
  - Support team notifications
- **Status Page Updates** (customer-facing transparency)
  - Investigating → Identified → Monitoring → Resolved progression
  - Clear, non-technical language
  - Regular updates (every 30-60 minutes for P0)

### Phase 6: Post-Incident Review and Learning (Within 5 business days)
**Lead:** `technical-writer` + `site-reliability-engineer`

Conduct blameless postmortem and extract learnings:

- **Postmortem Document Structure**: Comprehensive incident analysis
  - **Executive Summary**:
    - What happened (1-2 sentences)
    - Customer impact (duration, users affected, revenue loss)
    - Root cause (brief technical explanation)
    - Prevention actions (top 3-5 action items)
  - **Timeline** (detailed chronology):
    - Detection: When and how incident was discovered
    - Investigation: Key findings and hypothesis testing
    - Mitigation: Actions taken to reduce customer impact
    - Resolution: Permanent fix and validation
    - Communication: Stakeholder updates sent
  - **Root Cause Analysis**:
    - Immediate cause (what broke)
    - Contributing factors (what made it worse)
    - Why our defenses failed (why didn't we catch it earlier)
    - Systemic issues (organizational, process, technical)
  - **Impact Assessment**:
    - Duration of customer impact
    - Percentage of users/requests affected
    - Revenue impact (lost sales, credits issued)
    - SLO impact (error budget consumed)
    - Engineering time spent (incident response + follow-up)
  - **Five Whys Analysis**:
    - Why did the incident happen? → Slow query introduced
    - Why was slow query introduced? → No performance testing for queries
    - Why no performance testing? → Not part of CI pipeline
    - Why not in CI pipeline? → Team prioritized features over testing infrastructure
    - Why prioritization issue? → No clear ownership of testing infrastructure
  - **Action Items** (specific, assigned, time-bound):
    - SHORT-TERM (this week): Immediate fixes and prevention
      - [John] Add query performance regression test by Friday
      - [Sarah] Deploy connection pool monitoring by Wednesday
      - [Team] Review all queries in codebase for similar issues by Friday
    - MEDIUM-TERM (this month): Deeper prevention
      - [DevOps] Integrate query performance testing in CI pipeline by month-end
      - [SRE] Implement automated rollback on error rate spike within 2 weeks
      - [Eng Manager] Define testing infrastructure ownership and OKRs
    - LONG-TERM (this quarter): Systemic improvements
      - [Architecture] Evaluate read replica architecture for database by Q4
      - [Leadership] Allocate 20% engineering time to reliability work

- **Blameless Culture Principles**: Focus on learning, not blame
  - **Assume Good Intentions**: People did the best they could with information available
  - **Systems Thinking**: Incidents are caused by systemic issues, not individual mistakes
  - **Focus on How, Not Who**: "How did this happen?" not "Who broke it?"
  - **Celebrate Learning**: Incidents are opportunities to improve systems
  - **No Punishment**: Fear of blame leads to hiding issues and reduced learning
  - **Psychological Safety**: Safe to admit mistakes, ask for help, surface concerns

- **Postmortem Meeting Facilitation**: Live discussion (1-2 hours)
  - **Attendees**: Incident responders, service owners, engineering leadership
  - **Agenda**:
    - IC presents timeline and root cause (15min)
    - Open discussion: What went well? What could be better? (30min)
    - Brainstorm action items (15min)
    - Prioritize and assign action items (15min)
    - Identify sharing opportunities (how to prevent similar issues in other teams)
  - **Ground Rules**:
    - Blameless - focus on systems and processes
    - Respectful - assume good intentions
    - Specific - actionable suggestions, not vague complaints
    - Time-boxed - stay on schedule

- **Knowledge Sharing and Prevention**: Spread learnings
  - **Share Postmortem**: Distribute to engineering org
  - **Update Runbooks**: Improve incident response procedures
  - **Enhance Monitoring**: Add alerts to catch similar issues earlier
  - **Update Documentation**: Improve architecture docs, operational guides
  - **Training**: Incorporate learnings into onboarding, chaos engineering exercises

**Deliverables:**
- **Postmortem Document** (comprehensive, published within 5 business days)
  - 5-15 pages documenting incident end-to-end
  - Blameless tone focusing on systems and learning
  - Specific, time-bound action items with owners
  - Executive summary for leadership
  - Technical deep-dive for engineers
- **Action Item Tracking** (follow-through on commitments)
  - Jira tickets created for all action items
  - Owners assigned and committed to timelines
  - Progress tracked in weekly engineering meetings
  - 80%+ completion rate within committed timelines
- **Knowledge Base Updates** (captured learnings)
  - Runbooks updated with new procedures
  - Monitoring alerts tuned based on learnings
  - Documentation improved
  - Similar issues prevented in future

## Expected Outcomes

### Incident Response Efficiency
- **50-70% reduction in MTTR**: Structured process accelerates resolution
  - Before: 2-4 hours to resolve typical P1 incident
  - After: 30-60 minutes with clear roles and runbooks
- **60-80% faster incident detection**: Proactive monitoring vs. customer reports
  - Before: Customers report issue after 30-60 minutes
  - After: Alerts detect issue in <1 minute
- **40-60% reduction in incident escalations**: Better initial triage and runbooks
- **80%+ of incidents resolved using runbooks**: Documented procedures accelerate fixes
- **90%+ incident communication satisfaction**: Stakeholders feel informed and confident

### Organizational Learning
- **95%+ postmortem completion rate**: Every P0/P1 gets thorough analysis
- **70-85% action item completion**: Prevention work actually gets done
- **50-75% reduction in incident recurrence**: Learnings prevent similar issues
- **60-80% improvement in new engineer incident response**: Clear procedures enable junior responders
- **Blameless culture index 8+/10**: Psychological safety and learning focus

### Customer and Business Impact
- **40-60% reduction in customer-impacting incidents**: Better prevention
- **30-50% reduction in total customer impact minutes**: Faster detection and resolution
- **80%+ customer satisfaction with incident communication**: Transparent status updates
- **25-45% reduction in support ticket volume during incidents**: Proactive communication
- **70-90% improvement in executive confidence**: Clear communication and prevention follow-through

### Cost Savings and ROI
- **$200K-$800K annual value from reduced downtime**
  - Example: 50% MTTR reduction × 100 incidents × 2hr avg × $2K/hr = $200K
- **$100K-$350K annual value from faster response**
  - Example: 60% faster detection × 100 incidents × 30min × $1K/hr = $100K
- **$80K-$250K annual value from reduced recurrence**
  - Example: 50% recurrence reduction × 40 incidents × 2hr × $1.5K/hr = $120K
- **9-16x ROI in first year** (typical: 12x)
- **$380K-$1.4M+ total annual impact**

## Usage

```bash
# Initialize incident response framework (setup)
/operations:incident-response-workflow --setup

# Declare new incident (creates ticket, starts war room)
/operations:incident-response-workflow --declare --severity=P0 --title="Checkout system down"

# Update incident status (posts structured update)
/operations:incident-response-workflow --update --status=mitigating --eta="15 minutes"

# Resolve incident (transitions to postmortem phase)
/operations:incident-response-workflow --resolve

# Generate postmortem template (pre-filled with incident data)
/operations:incident-response-workflow --postmortem

# Track action items from postmortem
/operations:incident-response-workflow --track-actions

# Generate incident metrics report (MTTR trends, incident count)
/operations:incident-response-workflow --report=monthly
```

## Prerequisites

- [ ] Incident management tool (PagerDuty, Opsgenie, or Jira/GitHub for tracking)
- [ ] Communication platform (Slack/Teams for war room, Zoom/Meet for video)
- [ ] Status page tool (StatusPage.io, Atlassian Statuspage, or custom)
- [ ] Monitoring and observability infrastructure (alerts, dashboards, runbooks)
- [ ] On-call rotation defined (who responds to incidents)
- [ ] Escalation paths documented (when to page manager, executive)
- [ ] Incident response training for on-call engineers
- [ ] Blameless culture commitment from leadership

## Success Criteria

### Process Metrics
- [ ] 100% of P0/P1 incidents have incident tickets created
- [ ] 95%+ acknowledgment within SLA (P0: 1min, P1: 5min)
- [ ] 90%+ incidents have assigned Incident Commander
- [ ] 80%+ incidents follow structured war room process
- [ ] 100% of P0 incidents have status page updates
- [ ] 95%+ P0/P1 incidents have completed postmortems within 5 days
- [ ] 70%+ action item completion rate

### Performance Metrics
- [ ] MTTR reduced by 50%+ vs. pre-framework baseline
- [ ] MTTD reduced by 60%+ (faster detection)
- [ ] Incident recurrence rate <15% (same root cause within 90 days)
- [ ] Executive communication satisfaction >8/10
- [ ] Customer communication satisfaction >8/10
- [ ] Support team incident communication satisfaction >8/10

### Cultural Metrics
- [ ] Blameless culture score >8/10 (anonymous survey)
- [ ] Psychological safety index >8/10
- [ ] On-call engineer confidence >7/10
- [ ] New engineer incident readiness within 2 weeks of training
- [ ] 80%+ of engineers participate in postmortem discussions
- [ ] Leadership attends >50% of major incident postmortems

## Real-World Impact Examples

### SaaS Platform (Scale: 25K customers, 80 engineers, 24/7 operations)
- **Before:** 45min MTTR, 2hr MTTD, chaotic war rooms, 60% postmortem completion, blame culture
- **After:** 18min MTTR (-60%), 5min MTTD (-96%), structured process, 98% postmortems, blameless
- **Impact:** $920K annual savings, 13x ROI, improved team morale and retention

**Specific Improvements:**
- Structured IC role reduced decision paralysis (3 people debating → IC decides in 30 seconds)
- Runbooks enabled junior engineers to resolve 70% of incidents without escalation
- Blameless postmortems surfaced systemic issues (testing gaps, monitoring blind spots)
- Action item tracking prevented 32 incident recurrences in first year

### E-Commerce Platform (Scale: $500M GMV, 120 engineers, Black Friday critical)
- **Before:** 90min MTTR, poor executive communication, customer trust issues, repeat incidents
- **After:** 22min MTTR (-76%), real-time executive updates, transparent status pages, prevention culture
- **Impact:** $1.6M annual value (prevented downtime + faster resolution), 15x ROI

**Specific Improvements:**
- Black Friday incident (P0) resolved in 18 minutes using incident framework (previous year: 3 hours)
- Executive confidence improved dramatically (real-time Slack updates vs. "we'll get back to you")
- Customer communication during incidents became a competitive advantage (competitors went silent)
- Postmortem action items reduced payment gateway incidents from 12/year to 2/year

### Fintech Startup (Scale: $50M AUM, 35 engineers, regulatory scrutiny)
- **Before:** Incidents poorly documented, no postmortems, regulatory concerns, repeat security issues
- **After:** Comprehensive incident documentation, 100% postmortem compliance, regulatory approval
- **Impact:** $480K annual value + passed SOC2 audit + improved investor confidence

**Specific Improvements:**
- SOC2 audit cited incident management framework as exemplary control
- Security incident response time: 3 hours → 20 minutes (prevented data breach escalation)
- Regulatory documentation automatically generated from incident tickets and postmortems
- Investor confidence increased due to transparent incident communication and learning culture

## Common Challenges and Solutions

### Challenge: Incident Commander Role Confusion
**Problem:** Multiple people trying to coordinate, decisions delayed, chaos in war room
**Solution:**
- Explicitly assign IC at incident start, post in Slack: "@john is IC for this incident"
- IC wears "IC hat" - only IC makes decisions, others provide input
- IC can delegate tasks but retains decision authority
- Train all on-call engineers on IC responsibilities

### Challenge: Over-Communication Fatigue
**Problem:** Too many Slack messages, video calls, status updates - responders can't focus on fixing
**Solution:**
- Use threaded replies in Slack (questions in threads, updates in main channel)
- Time-box updates (every 30min for P0, not every 5min)
- Mute non-essential participants in video calls
- Delegate communication lead role so IC can focus on coordination

### Challenge: Blame Culture and Fear of Postmortems
**Problem:** Engineers fear postmortems, hide mistakes, don't surface issues early
**Solution:**
- Leadership commitment to blameless culture (explicitly stated, modeled in behavior)
- Rename "postmortem" to "learning review" (less morbid)
- Facilitate postmortems carefully (redirect blame language to systems language)
- Celebrate learning (share great postmortems company-wide, recognize contributors)
- Never punish people for mistakes (punish only willful negligence or malice)

### Challenge: Low Action Item Completion Rate
**Problem:** Great postmortems, many action items, 20% completion rate, incidents recur
**Solution:**
- Prioritize ruthlessly (3-5 action items max, not 20)
- Make action items SMART (Specific, Measurable, Assigned, Realistic, Time-bound)
- Track in regular engineering meetings (weekly review of outstanding action items)
- Allocate dedicated time (20% reliability work, not "squeeze it in")
- Hold accountable (gently) - ask "what's blocking you?" not "why isn't this done?"

### Challenge: Incident Fatigue and Burnout
**Problem:** Too many incidents, on-call burden high, engineers burning out
**Solution:**
- This is a symptom of deeper issues - use postmortems to identify systemic problems
- Invest in prevention (action items from postmortems reduce future incidents)
- Improve monitoring (reduce false positives, better alerting)
- Load balancing (spread on-call across more engineers, reduce rotation frequency)
- Provide recovery time (comp time after major incidents, mental health support)

## Related Commands

- `/operations:monitoring-stack-setup` - Implement observability for incident detection
- `/operations:production-learning-loop` - Extract patterns from incidents for prevention
- `/operations:disaster-recovery-plan` - Business continuity and DR procedures
- `/quality:production-readiness` - Pre-deployment validation to prevent incidents
- `/development:chaos-engineering` - Proactive resilience testing (future command)

## Notes

**Incident Commander is Critical:** Single point of coordination prevents chaos. IC doesn't need to be technical expert - they coordinate experts and make decisions. Clear IC assignment within first 5 minutes is #1 success factor.

**Blameless Culture Takes Time:** You can't decree blameless culture - it's built through consistent leadership behavior, facilitation of respectful postmortems, and celebrating learning. Expect 6-12 months to shift culture.

**Communication is Half the Battle:** Technical fix might take 30 minutes, but poor communication can damage customer trust for months. Invest heavily in stakeholder communication templates and training.

**Runbooks are Force Multipliers:** Junior engineers can resolve 70%+ of incidents with good runbooks. Every postmortem should update or create runbooks. Runbook quality correlates directly with MTTR.

**Prevention Work Requires Discipline:** It's easy to close postmortem and move on. Action item completion is where real learning happens. Allocate time, track progress, hold accountable.

**Status Pages Build Trust:** Customers forgive incidents if you communicate well. Transparent, frequent status updates turn angry customers into understanding partners. Don't go silent.

**Severity Discipline Matters:** Not everything is P0. Save P0 for customer-impacting outages. Overuse of P0 creates alert fatigue and burnout. Be disciplined about severity classification.

**War Room Norms Prevent Chaos:** Establish communication norms early (threads, emoji, update frequency). Without norms, war room becomes noisy and unhelpful.

**Postmortems are Investments:** Comprehensive postmortems take 4-8 hours to write but prevent hundreds of hours of future incidents. Don't skimp on postmortem quality.

**Incident Response is a Team Sport:** Best incident response teams train together (chaos engineering, tabletop exercises), rotate IC role, share learnings across teams. Invest in team cohesion and practice.
