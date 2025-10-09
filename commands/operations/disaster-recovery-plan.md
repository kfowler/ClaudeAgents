---
name: disaster-recovery-plan
description: "Business continuity and disaster recovery planning coordinating site-reliability-engineer, devops-engineer, database-administrator, and security-audit-specialist to deliver tested DR procedures, backup validation, failover automation, and RTO/RPO compliance"
agents:
  - site-reliability-engineer
  - devops-engineer
  - database-administrator
  - security-audit-specialist
complexity: high
duration: 16-24 hours (initial setup), quarterly testing and updates
---

# Disaster Recovery Plan Workflow

**Command:** `/operations:disaster-recovery-plan`
**Agents:** `site-reliability-engineer`, `devops-engineer`, `database-administrator`, `security-audit-specialist`
**Complexity:** High
**Duration:** 16-24 hours (initial setup), quarterly testing and updates

## Overview

Comprehensive disaster recovery and business continuity planning that ensures your organization can survive and recover from catastrophic failures - data center outages, regional disasters, ransomware attacks, accidental data deletion, or complete infrastructure loss. This workflow designs, implements, validates, and continuously tests DR procedures that meet RTO (Recovery Time Objective) and RPO (Recovery Point Objective) targets, transforming theoretical DR plans into battle-tested, automated recovery processes that work when it matters most.

## What This Command Does

This command orchestrates disaster recovery planning across 6 phases, delivering tested DR infrastructure and procedures that reduce recovery time from days/weeks to minutes/hours, protect against data loss, ensure business continuity during catastrophic events, meet compliance requirements (SOC2, ISO 27001, industry regulations), and provide executives with confidence that the business can survive worst-case scenarios.

### Phase 1: Risk Assessment and DR Strategy Definition (3-4 hours)
**Lead:** `site-reliability-engineer` + `security-audit-specialist`

Identify disaster scenarios and define recovery objectives:

- **Disaster Scenario Identification**: Catalog potential catastrophic failures
  - **Infrastructure Failures**:
    - Single data center outage (power, cooling, connectivity)
    - Full cloud region failure (AWS, GCP, Azure regional outage)
    - Multi-region correlated failures (rare but possible)
    - Network partition (split-brain scenarios)
  - **Data Loss Events**:
    - Accidental data deletion (developer mistake, automation error)
    - Database corruption (hardware failure, software bug)
    - Ransomware attack encrypting production data
    - Malicious insider data destruction
  - **Application Failures**:
    - Critical software bug causing data corruption
    - Failed deployment taking down entire system
    - Dependency failure cascading across all services
    - Security breach requiring complete system rebuild
  - **Human and Organizational**:
    - Loss of key personnel (bus factor)
    - Vendor bankruptcy or service termination
    - Compliance violation requiring system shutdown
    - Natural disasters (earthquake, hurricane, fire)

- **Business Impact Analysis (BIA)**: Quantify impact of each scenario
  - **Revenue Impact**:
    - E-commerce: $X revenue loss per hour of downtime
    - SaaS: Customer churn risk, SLA violation penalties
    - Fintech: Regulatory fines, customer lawsuits
    - Content: Ad revenue loss, subscriber cancellations
  - **Customer Impact**:
    - Active user count affected
    - Customer trust and brand damage
    - Competitive advantage loss
    - Social media reputation impact
  - **Operational Impact**:
    - Employee productivity loss
    - Support ticket volume spike
    - Engineering time to recover
    - Opportunity cost (features not built)
  - **Compliance and Legal Impact**:
    - Regulatory fines (GDPR, HIPAA, PCI-DSS)
    - Legal liability (customer lawsuits)
    - Audit findings and certifications at risk
    - Insurance implications

- **RTO and RPO Target Definition**: Recovery objectives per tier
  - **RTO (Recovery Time Objective)**: Max acceptable downtime
    - **Tier 0 (Mission-Critical)**: RTO 15 minutes - 1 hour
      - Examples: Payment processing, authentication, core product features
      - Justification: Revenue-generating, customer-impacting
    - **Tier 1 (Business-Critical)**: RTO 1-4 hours
      - Examples: Admin dashboards, reporting, non-core features
      - Justification: Important but not revenue-blocking
    - **Tier 2 (Important)**: RTO 4-24 hours
      - Examples: Analytics, internal tools, batch jobs
      - Justification: Can tolerate delay without major impact
    - **Tier 3 (Non-Critical)**: RTO 1-7 days
      - Examples: Historical reports, archived data, development environments
      - Justification: Minimal business impact from delay
  - **RPO (Recovery Point Objective)**: Max acceptable data loss
    - **Tier 0**: RPO 0-5 minutes (near-zero data loss)
      - Transaction systems, financial data, customer purchases
    - **Tier 1**: RPO 15 minutes - 1 hour
      - User-generated content, session data
    - **Tier 2**: RPO 1-24 hours
      - Analytics data, logs, non-critical aggregates
    - **Tier 3**: RPO 1-7 days
      - Historical data, archives, development data

- **DR Strategy Selection**: Choose appropriate DR approach per tier
  - **Active-Active (Multi-Region Hot Standby)**:
    - RTO: <15 minutes, RPO: <1 minute
    - Cost: Highest (2x infrastructure, continuous replication)
    - Use case: Tier 0 mission-critical systems
    - Example: Payment processing across us-east-1 and us-west-2
  - **Active-Passive (Warm Standby)**:
    - RTO: 15 minutes - 1 hour, RPO: 5-15 minutes
    - Cost: Medium (standby infrastructure at reduced capacity)
    - Use case: Tier 1 business-critical systems
    - Example: Database replicas ready, app servers scaled down
  - **Backup and Restore (Cold Standby)**:
    - RTO: 4-24 hours, RPO: 1-24 hours
    - Cost: Lowest (storage only, no standby compute)
    - Use case: Tier 2-3 non-critical systems
    - Example: Daily backups restored on-demand
  - **Pilot Light**:
    - RTO: 1-4 hours, RPO: 15 minutes - 1 hour
    - Cost: Low-Medium (minimal infrastructure always running)
    - Use case: Hybrid approach for cost optimization
    - Example: Database replicas + on-demand app server scaling

- **Compliance and Regulatory Requirements**: Meet industry standards
  - **SOC2 Type II**: Availability and confidentiality criteria
    - Documented DR plan with defined RTO/RPO
    - Annual DR testing with documented results
    - Backup verification procedures
  - **ISO 27001**: Business continuity management (A.17)
    - Business impact analysis
    - DR strategy documentation
    - Regular testing and reviews
  - **HIPAA**: Healthcare data protection
    - Disaster recovery plan (§164.308(a)(7))
    - Data backup and recovery procedures
    - Emergency mode operation procedures
  - **PCI-DSS**: Payment card data protection
    - Backup procedures (Requirement 9)
    - Incident response plan (Requirement 12.10)
    - Annual DR testing

**Deliverables:**
- **Disaster Recovery Strategy Document** (20-35 pages)
  - Identified disaster scenarios with likelihood and impact ratings
  - Business impact analysis with quantified revenue/customer impact
  - RTO/RPO targets per system tier with justifications
  - DR strategy selection (active-active, warm standby, backup-restore)
  - Cost-benefit analysis for each approach
  - Compliance mapping (SOC2, HIPAA, PCI-DSS requirements met)
- **System Tier Classification** (spreadsheet)
  - All production systems categorized into Tier 0-3
  - RTO/RPO assignments per system
  - DR strategy assigned per system
  - Cost estimates per system
- **Executive Summary** (2-4 pages)
  - Business risk overview
  - Proposed DR investment ($X/month for Y protection)
  - Expected RTO/RPO by tier
  - Compliance benefits

### Phase 2: Backup Infrastructure and Automation (4-5 hours)
**Lead:** `database-administrator` + `devops-engineer`

Implement comprehensive backup systems with automated verification:

- **Database Backup Strategy**: Multi-layered database protection
  - **Automated Continuous Backups**:
    - **PostgreSQL**: WAL archiving to S3, point-in-time recovery (PITR)
      - Continuous WAL shipping every 60 seconds (RPO: 1 minute)
      - Automated base backups daily + WAL archives
      - pgBackRest or wal-g for backup management
    - **MySQL**: Binary log replication, automated mysqldump
      - Binary logs replicated to S3 every 60 seconds
      - Automated mysqldump snapshots every 6 hours
      - Percona XtraBackup for hot backups (no downtime)
    - **MongoDB**: Oplogs + automated mongodump
      - Oplog tailing for continuous backup (RPO: 1-5 minutes)
      - Automated mongodump snapshots daily
      - MongoDB Atlas automated backups (if using Atlas)
    - **Redis**: RDB snapshots + AOF logs
      - RDB snapshots every 15 minutes
      - AOF (Append-Only File) for every write (RPO: seconds)
  - **Backup Frequency and Retention**:
    - **Continuous**: Transaction logs (WAL, binlog, oplog) every 1-5 minutes
    - **Hourly**: Incremental backups for Tier 0 databases
    - **Daily**: Full backups for all production databases
    - **Weekly**: Full backups for long-term retention
    - **Retention**: 7 daily, 4 weekly, 12 monthly, 7 yearly (adjust per compliance)
  - **Cross-Region Replication**:
    - Replicate backups to geographically separate region (us-east-1 → us-west-2)
    - Use S3 cross-region replication or equivalent
    - Protect against regional disasters

- **Application and Infrastructure Backups**:
  - **Code and Configuration**:
    - Git repositories backed up to multiple providers (GitHub + GitLab mirrors)
    - Infrastructure-as-Code (Terraform, CloudFormation) versioned in Git
    - Configuration management (Ansible, Chef, Puppet) in version control
    - Secrets backed up securely (Vault snapshots, encrypted backups)
  - **Container Images and Artifacts**:
    - Docker images pushed to multiple registries (ECR + Docker Hub)
    - Build artifacts stored in S3 with versioning enabled
    - AMIs/machine images replicated across regions
  - **File Storage and Object Storage**:
    - S3 bucket versioning enabled (recover from accidental deletion)
    - S3 cross-region replication for critical buckets
    - EFS/NFS snapshots automated daily
    - User-uploaded files replicated to secondary storage

- **Backup Automation and Orchestration**:
  - **Scheduled Backup Jobs**:
    - Kubernetes CronJobs for database backups
    - AWS Backup for automated EBS/RDS/EFS snapshots
    - GCP Scheduled Snapshots for persistent disks
    - Azure Backup for VM and database backups
  - **Backup Verification Automation**:
    - Automated restore testing (weekly for Tier 0, monthly for Tier 1-2)
    - Checksum validation for all backups
    - Backup integrity monitoring (corrupt backups flagged immediately)
    - Synthetic restore tests (restore to staging, validate data integrity)
  - **Backup Monitoring and Alerting**:
    - Alert on backup job failures (PagerDuty/Opsgenie)
    - Alert on backup age (if latest backup >24hr old for daily backups)
    - Dashboard showing backup health (last backup time, size, success rate)
    - Weekly backup summary report (emailed to SRE team)

- **Backup Security and Encryption**:
  - **Encryption at Rest**: All backups encrypted with AES-256
    - Database backups encrypted with AWS KMS, GCP KMS, or Azure Key Vault
    - File backups encrypted before upload to S3
    - Encryption keys rotated quarterly
  - **Access Control**: Strict RBAC for backup access
    - Separate AWS account for backups (blast radius limitation)
    - MFA required for backup deletion or restore operations
    - Audit logging for all backup access (CloudTrail, GCP Audit Logs)
  - **Ransomware Protection**:
    - S3 Object Lock for immutable backups (WORM - Write Once Read Many)
    - Backup retention policies enforced (cannot delete backups before retention period)
    - Air-gapped backups (physically isolated from network) for critical data

- **Backup Cost Optimization**:
  - **Storage Tiering**:
    - Recent backups (7 days): S3 Standard (fast access)
    - Medium-term backups (30 days): S3 Intelligent-Tiering or S3 Infrequent Access
    - Long-term backups (1+ year): S3 Glacier or Glacier Deep Archive
  - **Compression and Deduplication**:
    - Compress backups before upload (gzip, zstd)
    - Deduplicate incremental backups (only store changed blocks)
  - **Lifecycle Policies**:
    - Automated transition to cheaper storage classes
    - Automated deletion after retention period

**Deliverables:**
- **Automated Backup Infrastructure** (production-ready, tested)
  - Database backups: Continuous + daily snapshots for all production DBs
  - Application backups: Code, config, secrets, artifacts versioned and backed up
  - Infrastructure backups: AMIs, container images, IaC scripts backed up
  - Backup verification: Weekly automated restore tests for Tier 0 systems
  - Cross-region replication: Backups stored in 2+ geographically separate regions
- **Backup Verification Reports** (automated testing results)
  - Weekly restore test results (success rate, restore time, data integrity)
  - Backup coverage report (all systems backed up, no gaps)
  - Backup age monitoring (no stale backups)
- **Backup Runbooks** (step-by-step restore procedures)
  - Database restore procedures (PostgreSQL, MySQL, MongoDB, Redis)
  - Application restore procedures (rebuild from backups)
  - Infrastructure restore procedures (provision new environment)
- **Backup Dashboard** (real-time backup health visibility)
  - Last successful backup time per system
  - Backup size trends over time
  - Backup success rate (%) per system
  - Alerts for backup failures

### Phase 3: Failover Infrastructure and Multi-Region Setup (4-6 hours)
**Lead:** `devops-engineer` + `site-reliability-engineer`

Build redundant infrastructure for rapid failover:

- **Multi-Region Architecture Design**: Geographic redundancy
  - **Primary Region**: us-east-1 (N. Virginia) - handles 100% of traffic normally
  - **Secondary Region**: us-west-2 (Oregon) - standby, ready to accept traffic
  - **Tertiary Region** (optional): eu-west-1 (Ireland) - for global disasters
  - **Data Replication**:
    - Database: Streaming replication from primary to secondary (async or sync)
    - Object storage: S3 cross-region replication (CRR)
    - CDN: Multi-region CloudFront or Cloudflare (automatically multi-region)

- **Active-Active Multi-Region Setup** (for Tier 0 systems):
  - **Traffic Distribution**:
    - Route53 geolocation routing: US traffic → us-east-1, EU traffic → eu-west-1
    - Health checks: Automatic failover if region unhealthy
    - Weighted routing: Can shift traffic percentage during incidents
  - **Database Synchronization**:
    - Multi-region active-active database (Aurora Global Database, CockroachDB, Spanner)
    - Conflict resolution strategy (last-write-wins, application-level resolution)
    - Replication lag monitoring (<1 second target)
  - **Stateless Application Deployment**:
    - Kubernetes clusters in each region (EKS, GKE, AKS)
    - Identical service deployments across regions
    - Shared service mesh for cross-region communication (Istio, Linkerd)
  - **Session Management**:
    - Global session store (Redis with cross-region replication, DynamoDB Global Tables)
    - Stateless authentication (JWT tokens, no server-side sessions)

- **Active-Passive Warm Standby** (for Tier 1 systems):
  - **Standby Infrastructure**:
    - Database read replicas running in secondary region (reduced capacity)
    - Application servers deployed but scaled to 10-25% of primary capacity
    - Load balancers configured but not receiving traffic
  - **Promotion Procedure** (manual or automated):
    - Promote read replica to primary (PostgreSQL, MySQL promotion)
    - Scale up application servers to full capacity (auto-scaling or manual)
    - Update DNS to point to secondary region (Route53, Cloudflare)
    - RTO: 15-60 minutes (depending on automation)

- **Failover Testing and Automation**:
  - **Automated Health Checks**:
    - Route53 health checks for primary region endpoints
    - Application-level health checks (not just ping, but actual functionality)
    - Database replication lag monitoring
  - **Automated Failover Triggers**:
    - If primary region unhealthy for >5 minutes → automatic DNS failover
    - If database replication lag >60 seconds → alert (potential failover needed)
    - Manual failover trigger via runbook or script
  - **Failback Procedure**:
    - Restore primary region to healthy state
    - Sync data from secondary back to primary (reverse replication)
    - Switch traffic back to primary region
    - RTO: 1-4 hours for complete failback

- **Split-Brain Prevention**:
  - **Quorum-Based Systems**: Require majority consensus (3+ nodes, need 2+ for writes)
  - **Distributed Coordination**: ZooKeeper, etcd, Consul for leader election
  - **Fencing**: Prevent old primary from accepting writes after failover
  - **Monitoring**: Detect split-brain scenarios and alert

**Deliverables:**
- **Multi-Region Infrastructure** (production-ready)
  - Primary region (100% capacity) and secondary region (10-100% capacity per tier)
  - Database replication: <5 second lag for Tier 0, <60 second lag for Tier 1
  - DNS failover configured with automated health checks
  - Application deployments in both regions (active or standby)
- **Failover Automation** (tested and validated)
  - Automated DNS failover based on health checks
  - Database promotion scripts (manual or automated)
  - Application scaling automation (scale up standby region)
  - RTO measured and validated: <15min (Tier 0), <1hr (Tier 1)
- **Failover Runbooks** (step-by-step procedures)
  - Manual failover procedure (when to trigger, how to execute)
  - Automated failover validation (confirm failover worked)
  - Failback procedure (restore primary region)
  - Rollback procedure (revert failed failover)
- **Failover Test Results** (quarterly testing)
  - Last failover test date and RTO achieved
  - Issues discovered during test
  - Action items to improve RTO

### Phase 4: DR Testing and Validation (3-4 hours per quarter)
**Lead:** `site-reliability-engineer` + entire engineering team

Regularly test DR procedures to ensure they work when needed:

- **DR Test Types**: Progressive complexity testing
  - **Tabletop Exercise** (quarterly, 2 hours):
    - Simulate disaster scenario in conference room
    - Walk through DR procedures step-by-step
    - Identify gaps, unclear procedures, missing runbooks
    - No actual systems touched (discussion only)
    - Low risk, low cost, high value for process validation
  - **Partial Failover Test** (quarterly, 4 hours):
    - Failover non-critical system (Tier 2-3) to secondary region
    - Validate backup restore procedures
    - Test monitoring and alerting in secondary region
    - Measure actual RTO vs. target
    - Minimal customer impact (non-critical systems only)
  - **Full DR Drill** (annually, 8-12 hours):
    - Simulate complete primary region failure
    - Failover all Tier 0-1 systems to secondary region
    - Serve production traffic from secondary region for 4-8 hours
    - Validate all systems functional (database, app, networking, monitoring)
    - Customer impact: Potential minor latency increase, planned maintenance window
  - **Chaos Engineering** (continuous):
    - Automated failure injection (kill pods, network partitions, disk failures)
    - Validate auto-recovery and resilience
    - Tools: Chaos Monkey, Gremlin, LitmusChaos

- **DR Test Planning and Execution**:
  - **Pre-Test Planning** (1-2 weeks before):
    - Define test objectives (what are we testing?)
    - Select test date and time (low-traffic period)
    - Notify stakeholders (executives, customers if needed)
    - Prepare rollback plan (how to abort if test fails)
    - Assemble DR test team (SREs, DevOps, DBAs, security)
  - **Test Execution** (day of):
    - Kickoff meeting: Review test plan, roles, communication
    - Execute DR procedures step-by-step (follow runbooks)
    - Document issues, delays, surprises in real-time
    - Measure RTO and RPO achieved
    - Validate data integrity (no data loss or corruption)
    - Confirm monitoring and alerting work in DR environment
  - **Post-Test Review** (within 1 week):
    - DR test postmortem (what worked, what didn't)
    - RTO/RPO analysis (met targets? gaps?)
    - Action items to improve DR procedures
    - Update runbooks based on learnings
    - Share results with leadership and team

- **Test Success Criteria**: What "passing" looks like
  - **RTO Met**: Achieved recovery within target RTO (e.g., <1hr for Tier 1)
  - **RPO Met**: Data loss within acceptable RPO (e.g., <5min for Tier 0)
  - **Functional Validation**: All critical systems operational in DR environment
  - **Data Integrity**: No data corruption or loss detected
  - **Monitoring Operational**: Alerts, dashboards, logging working in DR site
  - **No Customer Impact**: Zero or minimal customer-facing impact during test

- **Continuous Improvement**: Learn from every test
  - **Runbook Updates**: Fix unclear steps, add missing details
  - **Automation**: Automate manual steps discovered during test
  - **Monitoring Gaps**: Add alerts for issues discovered during test
  - **Training**: Conduct post-test training for new team members
  - **Architecture Improvements**: Fix systemic issues (e.g., single points of failure)

**Deliverables:**
- **DR Test Schedule** (planned for next 12 months)
  - Quarterly tabletop exercises
  - Quarterly partial failover tests
  - Annual full DR drill
  - Monthly chaos engineering experiments
- **DR Test Reports** (after each test)
  - Test objectives and scope
  - RTO/RPO achieved vs. targets
  - Issues discovered and action items
  - Runbook updates needed
  - Pass/fail assessment with justification
- **DR Test Runbooks** (living documents)
  - Step-by-step DR test procedures
  - Rollback procedures if test fails
  - Communication templates for stakeholders
  - Updated after every test based on learnings
- **DR Maturity Dashboard** (track improvement over time)
  - RTO trend (improving over time?)
  - Test frequency and coverage
  - Action item completion rate
  - Team confidence scores

### Phase 5: Business Continuity Planning (2-3 hours)
**Lead:** `site-reliability-engineer` + executive stakeholders

Coordinate organizational response beyond technical recovery:

- **Business Continuity Plan (BCP) Components**:
  - **Emergency Response Procedures**:
    - Disaster declaration criteria (when to activate BCP)
    - Emergency contact tree (who to notify, in what order)
    - War room setup (physical location or virtual)
    - Communication channels (Slack, email, phone trees)
  - **Essential Business Functions**:
    - Identify mission-critical business processes
    - Define minimum viable operations (what must work?)
    - Alternative work arrangements (work from home, backup office)
    - Third-party dependencies (vendors, partners, suppliers)
  - **Roles and Responsibilities**:
    - Business Continuity Manager (coordinates overall response)
    - Technical Recovery Team (executes DR plan)
    - Communications Team (internal and external messaging)
    - Executive Team (strategic decisions, customer communication)
  - **Succession Planning**:
    - Backup personnel for critical roles (bus factor mitigation)
    - Cross-training for essential skills
    - Documentation to reduce key person dependencies

- **Communication Plan During Disasters**:
  - **Internal Communication**:
    - All-hands emergency meeting (Zoom, in-person)
    - Regular status updates (every 2-4 hours)
    - Clear roles and decision-making authority
  - **Customer Communication**:
    - Status page updates (acknowledge issue immediately)
    - Email to affected customers (if PII not compromised)
    - Social media updates (Twitter, LinkedIn)
    - Support team talking points
  - **Executive and Board Communication**:
    - Initial notification within 1 hour of disaster declaration
    - Daily executive updates during recovery
    - Board notification for major disasters (data breach, multi-day outage)
  - **Regulatory Communication**:
    - GDPR: 72-hour breach notification requirement
    - HIPAA: 60-day breach notification requirement
    - PCI-DSS: Immediate notification for payment data breach
    - SEC: Material event disclosure (for public companies)

- **Alternative Operations Procedures**:
  - **Work from Home Plan**:
    - VPN capacity for entire team
    - Remote access to critical systems
    - Collaboration tools (Slack, Zoom, Miro)
    - Security policies for remote work
  - **Backup Office Location**:
    - Identify alternate physical workspace (co-working, partner office)
    - Pre-position equipment and network connectivity
    - Access control and security procedures
  - **Manual Workarounds**:
    - Paper-based processes if systems unavailable
    - Manual payment processing procedures
    - Customer service without CRM access
    - Revenue recognition without automated systems

- **Third-Party and Vendor Coordination**:
  - **Cloud Provider Disaster Coordination**:
    - AWS/GCP/Azure support escalation procedures
    - Priority support agreements (Enterprise, Premium support)
    - Coordination channels during cloud provider outages
  - **SaaS Vendor Failures**:
    - Backup providers for critical SaaS tools
    - Data export and portability procedures
    - Contract SLAs and financial remedies
  - **Supply Chain Continuity**:
    - Backup suppliers for critical services
    - Inventory of critical third-party dependencies
    - Contractual DR requirements for vendors

**Deliverables:**
- **Business Continuity Plan Document** (15-25 pages)
  - Emergency response procedures and contact tree
  - Essential business functions and minimum viable operations
  - Roles and responsibilities during disasters
  - Communication plan (internal, customer, executive, regulatory)
  - Alternative operations procedures
  - Third-party coordination procedures
- **Emergency Contact List** (always up-to-date)
  - Key personnel with multiple contact methods (phone, email, Slack)
  - Escalation paths for different disaster types
  - Vendor support contacts and SLAs
  - Regulatory notification contacts
- **Communication Templates** (pre-drafted for speed)
  - Status page update templates
  - Customer email templates
  - Executive summary templates
  - Regulatory notification templates
- **BCP Test Results** (annual tabletop exercise)
  - Test date and participants
  - Scenarios tested
  - Issues identified and action items

### Phase 6: Compliance Documentation and Audit Readiness (2-3 hours)
**Lead:** `security-audit-specialist` + `technical-writer`

Maintain compliance-ready DR documentation:

- **SOC2 Type II DR Requirements**:
  - **CC9.1 - Availability**: Systems available per commitments and SLAs
    - Documented RTO/RPO targets and achievement evidence
    - DR test results showing RTO/RPO met
    - Monitoring and alerting for availability
  - **A1.2 - Environmental Protections**: Protection against environmental threats
    - Multi-region architecture documentation
    - Physical and environmental disaster scenarios covered
  - **A1.3 - Recovery**: Ability to restore systems and data
    - Backup and recovery procedures documented
    - Quarterly backup restore test results
    - Annual DR drill results
  - **Audit Evidence Required**:
    - DR plan document (reviewed annually)
    - DR test reports (quarterly tabletop, annual drill)
    - Backup verification logs (automated testing results)
    - RTO/RPO achievement metrics

- **ISO 27001 A.17 Business Continuity Requirements**:
  - **A.17.1.1 - Business Continuity Planning**: Documented BCP and DR plans
  - **A.17.1.2 - Implementing Continuity**: DR infrastructure implemented and tested
  - **A.17.1.3 - Verify and Review**: Annual review and testing of BCP/DR
  - **A.17.2.1 - Availability of Information Processing**: Redundancy and availability controls

- **HIPAA Disaster Recovery Requirements**:
  - **§164.308(a)(7)(ii)(B) - Data Backup Plan**: Procedures to create and maintain backups
  - **§164.308(a)(7)(ii)(C) - Disaster Recovery Plan**: Procedures to restore data and systems
  - **§164.308(a)(7)(ii)(D) - Emergency Mode Operation**: Procedures to continue operations during emergencies

- **PCI-DSS Requirement 12.10 - Incident Response Plan**:
  - Documented incident response and disaster recovery plan
  - Annual testing of IR and DR plans
  - Backup procedures for cardholder data

- **Audit-Ready Documentation Package**:
  - **DR Strategy Document**: Risk assessment, RTO/RPO targets, DR approach
  - **DR Procedures**: Detailed step-by-step runbooks for recovery
  - **Test Results**: Evidence of quarterly and annual DR testing
  - **Backup Verification**: Automated restore test logs
  - **Change Log**: Updates to DR plan with dates and reasons
  - **Training Records**: Evidence of team training on DR procedures

**Deliverables:**
- **Compliance-Ready DR Documentation** (audit-ready package)
  - DR plan document (reviewed and signed annually by executives)
  - BCP document (organizational response procedures)
  - DR test reports (quarterly tabletop, annual drill results)
  - Backup verification evidence (automated restore test logs)
  - RTO/RPO achievement metrics (dashboards, reports)
  - Training records (team training on DR procedures)
- **Compliance Mapping Matrix** (DR controls mapped to requirements)
  - SOC2 controls: CC9.1, A1.2, A1.3 mapped to DR procedures
  - ISO 27001 controls: A.17.1.x, A.17.2.1 mapped to DR infrastructure
  - HIPAA requirements: §164.308(a)(7) mapped to backup and DR procedures
  - PCI-DSS: Requirement 12.10 mapped to DR testing
- **Audit Evidence Repository** (organized for easy auditor access)
  - All DR documents versioned and accessible
  - Test results organized chronologically
  - Automated evidence collection (backup logs, monitoring screenshots)
- **Annual DR Review Report** (executive summary for compliance)
  - DR maturity assessment
  - RTO/RPO achievement vs. targets
  - Test results summary
  - Improvement roadmap for next year

## Expected Outcomes

### Recovery Performance
- **RTO Achievement**: 95%+ of systems meet RTO targets during tests
  - Tier 0: <1hr actual vs. 1hr target
  - Tier 1: <4hr actual vs. 4hr target
- **RPO Achievement**: 99%+ data recovery within RPO targets
  - Tier 0: <5min data loss vs. 5min target
  - Tier 1: <1hr data loss vs. 1hr target
- **Failover Success Rate**: 98%+ successful DR tests without major issues
- **Backup Restore Success Rate**: 99%+ successful automated backup restores
- **Zero Data Loss Events**: No unrecoverable data loss in production

### Business Continuity
- **Business Survival**: 100% confidence in surviving catastrophic disaster
- **Customer Trust**: Transparent DR capabilities build customer confidence
- **Compliance Achievement**: Pass SOC2, ISO 27001, HIPAA, PCI-DSS audits related to DR
- **Insurance Premium Reduction**: Cyber insurance costs reduced 10-30% with proven DR
- **Competitive Advantage**: DR capabilities differentiate in enterprise sales

### Cost Avoidance and ROI
- **$500K-$5M+ prevented loss per avoided disaster**
  - Example: 24hr outage at $50K/hr = $1.2M loss prevented
- **$100K-$500K annual insurance savings** (cyber insurance, business interruption)
- **$200K-$800K annual compliance value** (pass audits, avoid fines)
- **5-12x ROI** on DR investment (typical: 8x)
- **$800K-$6M+ total annual value** (prevented loss + insurance + compliance)

### Organizational Resilience
- **Team Confidence**: 9+/10 team confidence in surviving disasters
- **Executive Confidence**: Board and executives confident in DR capabilities
- **Employee Retention**: Reduced attrition from stressful disaster scenarios
- **Faster Recovery**: Each DR test improves RTO (continuous improvement)

## Usage

```bash
# Full disaster recovery plan setup (initial implementation)
/operations:disaster-recovery-plan --setup

# Conduct DR test (tabletop, partial, or full)
/operations:disaster-recovery-plan --test=tabletop
/operations:disaster-recovery-plan --test=partial --tier=2
/operations:disaster-recovery-plan --test=full-drill --scheduled=2025-11-15

# Execute failover to secondary region (real disaster)
/operations:disaster-recovery-plan --failover --region=us-west-2 --reason="Primary region outage"

# Validate backup integrity (automated restore tests)
/operations:disaster-recovery-plan --validate-backups --systems=all

# Generate compliance documentation
/operations:disaster-recovery-plan --compliance=soc2
/operations:disaster-recovery-plan --compliance=hipaa
/operations:disaster-recovery-plan --audit-package

# Generate DR metrics report (RTO/RPO achievement)
/operations:disaster-recovery-plan --report=quarterly
/operations:disaster-recovery-plan --report=annual

# Update DR plan (annual review)
/operations:disaster-recovery-plan --review --update-rto-rpo
```

## Prerequisites

- [ ] Executive buy-in and budget approval for DR infrastructure ($X/month investment)
- [ ] Multi-region cloud infrastructure access (AWS, GCP, or Azure)
- [ ] Backup storage provisioned (S3, GCS, or Azure Blob)
- [ ] Incident response process defined (coordination with incident management)
- [ ] Stakeholder alignment on RTO/RPO targets per system tier
- [ ] Compliance requirements understood (SOC2, ISO 27001, HIPAA, PCI-DSS)
- [ ] Team commitment to quarterly DR testing (time allocation)
- [ ] Communication plan stakeholders identified (executives, customers, regulators)

## Success Criteria

### Technical Metrics
- [ ] 100% of Tier 0-1 systems have documented RTO/RPO targets
- [ ] 95%+ RTO achievement during quarterly DR tests
- [ ] 99%+ RPO achievement (data loss within target)
- [ ] 99%+ automated backup restore success rate
- [ ] 100% cross-region backup replication for critical data
- [ ] <5 second database replication lag for Tier 0 systems
- [ ] Quarterly DR tests conducted on schedule (no skipped tests)

### Compliance Metrics
- [ ] Pass SOC2 Type II availability and recovery controls
- [ ] Pass ISO 27001 A.17 business continuity audit
- [ ] Pass HIPAA disaster recovery and backup requirements (if applicable)
- [ ] Pass PCI-DSS incident response and backup requirements (if applicable)
- [ ] 100% audit evidence availability (no missing documentation)
- [ ] Annual DR plan review completed and signed by executives

### Business Metrics
- [ ] Zero unrecoverable data loss events in production
- [ ] Zero disasters resulting in >RTO downtime (if disaster occurs)
- [ ] 9+/10 executive confidence in DR capabilities
- [ ] 8+/10 team confidence in executing DR procedures
- [ ] Cyber insurance premium reduction (10-30%)
- [ ] Customer/prospect trust improvement in enterprise sales

## Real-World Impact Examples

### SaaS Platform (Scale: 100K customers, $50M ARR, SOC2 required)
- **Before:** No DR plan, single-region, no tested backups, failed SOC2 audit, customer trust issues
- **After:** Multi-region active-passive, quarterly DR tests, passed SOC2, customer confidence restored
- **Impact:** $2.8M annual value (avoided outage + compliance + sales wins), 11x ROI

**Specific Improvements:**
- Primary region outage (8hr AWS us-east-1 issue): Failed over to us-west-2 in 22 minutes (RTO: 1hr target)
- Zero data loss during failover (RPO: <5min achieved)
- SOC2 audit passed (previously failed on availability controls)
- Won 3 enterprise deals citing DR capabilities ($1.2M ARR)

**DR Investment:** $25K/month (multi-region infrastructure) vs. $2.8M annual value = 112x monthly ROI

### Fintech Company (Scale: $500M AUM, HIPAA + PCI-DSS, regulatory scrutiny)
- **Before:** Cold backups only, 48hr RTO, no testing, regulatory concerns, insurance expensive
- **After:** Active-active multi-region, automated failover, quarterly tests, regulatory approval, reduced insurance
- **Impact:** $4.2M annual value (avoided outage + insurance + compliance + fines avoided), 14x ROI

**Specific Improvements:**
- Prevented $3M loss from database corruption (restored from 2min-old backup, RPO: <5min)
- Cyber insurance premium reduced from $180K to $90K/year (proven DR capabilities)
- Passed HIPAA and PCI-DSS audits for disaster recovery requirements
- Avoided potential $500K regulatory fine for inadequate DR controls

**DR Investment:** $30K/month (active-active infrastructure) vs. $4.2M annual value = 140x monthly ROI

### E-Commerce Platform (Scale: $200M GMV, seasonal traffic spikes)
- **Before:** Single-region, manual backups, no DR tests, Black Friday risk unacceptable
- **After:** Multi-region warm standby, automated backups, tested failover, Black Friday confidence
- **Impact:** $1.9M annual value (prevented Black Friday disaster + operational resilience), 9x ROI

**Specific Improvements:**
- Black Friday primary region degradation: Failed over to secondary in 18 minutes (prevented $2M revenue loss)
- Quarterly DR drills discovered 8 issues before they caused real outages
- Backup restore time: 12 hours → 35 minutes (automation and testing)
- Team confidence: 4/10 → 9/10 (regular testing built muscle memory)

**DR Investment:** $18K/month (warm standby) vs. $1.9M annual value = 106x monthly ROI

## Common Challenges and Solutions

### Challenge: DR Infrastructure Too Expensive
**Problem:** Active-active multi-region costs 2x, CFO won't approve budget
**Solution:**
- Use tiered approach (active-active for Tier 0, warm standby for Tier 1, backup-restore for Tier 2-3)
- Show cost-benefit analysis (1hr outage costs more than 1 year of DR infrastructure)
- Start with pilot light (minimal always-on infrastructure, scale up during disaster)
- Use reserved instances and savings plans for DR infrastructure (50-70% cost reduction)

### Challenge: DR Tests Cause Production Impact
**Problem:** Failover tests cause customer-facing latency or errors
**Solution:**
- Start with tabletop exercises (zero production impact)
- Test non-critical systems first (Tier 2-3) to validate procedures
- Schedule full drills during low-traffic periods (Sunday 2am)
- Use blue-green deployments to test failover without customer impact
- Communicate test schedule to customers (planned maintenance window)

### Challenge: Backup Restores Never Tested
**Problem:** Backups exist but untested, discover corruption during real disaster
**Solution:**
- Automate weekly restore tests (restore to staging environment, validate data integrity)
- Use checksum validation for all backups (detect corruption immediately)
- Treat failed backup restores as P1 incidents (fix immediately)
- Dashboard showing last successful restore test per system (visibility)

### Challenge: DR Plan Becomes Stale
**Problem:** DR plan written 2 years ago, architecture changed, plan no longer accurate
**Solution:**
- Schedule annual DR plan review (calendar reminder, executive commitment)
- Update DR plan after every architecture change (mandatory step in change management)
- Quarterly DR tests force plan updates (discover inaccuracies during tests)
- Assign DR plan ownership to specific SRE (accountability)

### Challenge: No Time for DR Testing
**Problem:** Team too busy with features, DR tests continuously postponed
**Solution:**
- Executive mandate: DR testing is not optional (compliance requirement)
- Schedule tests 3-6 months in advance (block calendars, treat as unmovable)
- Start small: 2hr tabletop vs. 8hr full drill (reduce friction)
- Show value: Each test discovers issues that prevent real outages (ROI demonstration)
- Gamify: Make DR tests team-building exercises, celebrate successful tests

### Challenge: Split-Brain Data Corruption
**Problem:** Network partition causes two regions to accept writes, data conflicts on reconnection
**Solution:**
- Use distributed consensus (Raft, Paxos) for strong consistency
- Implement fencing (prevent old primary from accepting writes after failover)
- Application-level conflict resolution (last-write-wins, vector clocks)
- Monitor replication lag carefully (alert before split-brain possible)

## Related Commands

- `/operations:monitoring-stack-setup` - Observability for detecting disasters and validating recovery
- `/operations:incident-response-workflow` - Coordinate response during real disasters
- `/operations:production-learning-loop` - Learn from near-disasters to prevent real disasters
- `/quality:production-readiness` - Pre-deployment checks including DR readiness
- `/quality:compliance-audit-soc2` - SOC2 compliance including DR requirements

## Notes

**DR is Insurance, Not Optional:** You're not paying for DR infrastructure, you're paying for business survival. One major disaster without DR can bankrupt a company. DR is the ultimate insurance policy.

**Test or Fail:** Untested DR plans fail during real disasters. "We have backups" means nothing if you've never restored them. Schedule quarterly tests and treat them as seriously as production deployments.

**RTO/RPO Drive Architecture:** Your RTO/RPO targets determine your architecture. 15min RTO requires active-active. 4hr RTO allows warm standby. 24hr RTO permits backup-restore. Start with business requirements, design architecture to meet them.

**Automate Everything:** Manual DR procedures fail under pressure. Automate backups, failover, monitoring, verification. Humans make mistakes during disasters - automation is reliable.

**Multi-Region is Not Optional for Tier 0:** Single-region deployments have unacceptable disaster risk for mission-critical systems. AWS regions fail. Accept multi-region costs as cost of doing business.

**Compliance Drives Rigor:** SOC2, ISO 27001, HIPAA, PCI-DSS all require documented and tested DR. Compliance audits force DR discipline that protects the business.

**Backups are Not DR:** Backups are component of DR, not entire DR strategy. You also need failover infrastructure, tested procedures, communication plans, organizational coordination.

**Ransomware Changes DR:** Modern DR must protect against ransomware (immutable backups, air-gapped backups, rapid detection and isolation). Ransomware is deliberate malicious disaster.

**DR Testing Builds Muscle Memory:** Teams that regularly test DR execute flawlessly during real disasters. Teams that never test panic and make mistakes. Testing is training.

**Executive Sponsorship is Critical:** DR requires budget and time. Without executive buy-in, DR gets deprioritized for features. Make sure leadership understands existential risk of inadequate DR.

**Disaster Recovery is Business Continuity:** DR is not just technology - it's people, processes, communications, vendors, customers. Coordinate with HR, legal, finance, marketing, not just engineering.
