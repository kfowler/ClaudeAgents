# FinTech Compliance - Complete Financial Services Development Workflow

**Category:** Vertical Workflow Package
**Target Market:** Financial services, payment processors, banking apps, investment platforms
**Estimated Duration:** 12-16 hours (multi-phase workflow)
**Agents Involved:** 8-10 specialized agents
**Complexity:** Very High (compliance-critical)

---

## Overview

End-to-end workflow for building compliant financial services applications with security, regulatory compliance, and audit requirements built in from day one. This vertical package orchestrates security, backend, business, and compliance specialists to deliver production-ready FinTech solutions.

**What You Get:**
- SOC 2 Type II compliance framework
- PCI DSS Level 1 compliance (payment processing)
- GDPR/CCPA data privacy compliance
- Bank-grade security architecture
- Regulatory reporting system
- Audit trail and logging
- Incident response plan
- Technical documentation for auditors

---

## When to Use This Command

Use `/fintech-compliance` when you need to:
- Build payment processing systems
- Launch a digital banking app
- Create investment/trading platforms
- Develop lending/credit applications
- Build cryptocurrency exchanges
- Implement financial data aggregation

**Prerequisites:**
- Business entity registered (LLC, Corp)
- Legal counsel familiar with FinTech regulations
- Compliance officer identified (can be external consultant)
- Target jurisdiction(s) defined (US, EU, UK, etc.)
- Payment processor account (Stripe, Plaid, etc.)

**Regulatory Scope:**
- **US:** PCI DSS, SOC 2, BSA/AML, GLBA, State licensing
- **EU:** GDPR, PSD2, MiFID II (if applicable)
- **Global:** ISO 27001, SWIFT CSP (if applicable)

---

## Workflow Phases

### Phase 1: Compliance Architecture (3-4 hours)

**Agents:**
- `business-analyst` - Regulatory requirements analysis
- `security-audit-specialist` - Security framework design
- `backend-api-engineer` - Compliance-ready architecture
- `technical-writer` - Compliance documentation

**Deliverables:**

1. **Regulatory Requirements Matrix**
   - Applicable regulations by jurisdiction
   - Compliance obligations timeline
   - Certification requirements (SOC 2, PCI DSS)
   - Licensing needs (money transmitter, etc.)

2. **Security Architecture**
   - Zero-trust network architecture
   - Encryption at rest and in transit (AES-256, TLS 1.3)
   - Multi-factor authentication (MFA) mandatory
   - Role-based access control (RBAC)
   - Secrets management (HSM, Vault)
   - DDoS protection and WAF

3. **Data Classification System**
   - PII (Personally Identifiable Information)
   - FTI (Federal Tax Information)
   - CHD (Cardholder Data) - PCI DSS scope
   - Financial records (retention requirements)
   - Audit logs (immutable, 7-year retention)

4. **Compliance Documentation**
   - System Security Plan (SSP)
   - Data Flow Diagrams
   - Risk Assessment and Treatment Plan
   - Business Continuity Plan (BCP)
   - Disaster Recovery Plan (DRP)

**Success Criteria:**
- ✅ All applicable regulations identified
- ✅ Security architecture reviewed by CISO/consultant
- ✅ Data classification policy documented
- ✅ Compliance framework established

---

### Phase 2: Secure Development (4-5 hours)

**Agents:**
- `backend-api-engineer` - API development with security
- `database-administrator` - Encrypted database setup
- `security-audit-specialist` - Secure coding review
- `qa-test-engineer` - Security testing

**Implementation Areas:**

1. **Authentication & Authorization**
   - OAuth 2.0 / OpenID Connect
   - Multi-factor authentication (TOTP, SMS, biometric)
   - Session management (secure tokens, expiration)
   - Password policy enforcement (NIST 800-63B)
   - Account lockout and rate limiting
   - Privileged access management (PAM)

2. **API Security**
   - API key rotation and management
   - Request signing (HMAC-SHA256)
   - Rate limiting (prevent abuse)
   - Input validation (prevent injection)
   - CORS policy (strict origin control)
   - API versioning and deprecation

3. **Payment Processing**
   - PCI DSS scoping (minimize CHD exposure)
   - Tokenization (never store card numbers)
   - 3D Secure (SCA for EU)
   - Fraud detection integration
   - Payment reconciliation
   - Refund and chargeback handling

4. **Transaction Security**
   - Idempotency keys (prevent double-charging)
   - Transaction signing (non-repudiation)
   - Atomic operations (ACID compliance)
   - Distributed transaction handling
   - Reconciliation processes
   - Settlement reporting

5. **Data Encryption**
   - Field-level encryption (sensitive data)
   - Database encryption at rest (TDE)
   - Encryption key management (HSM/KMS)
   - Secure key rotation procedures
   - Backup encryption
   - Data masking (non-production environments)

6. **Audit Logging**
   - Immutable audit trails (append-only)
   - User activity logging
   - Transaction logging (all financial operations)
   - Admin action logging
   - Security event logging
   - Log retention (7 years for financial records)

**Success Criteria:**
- ✅ Authentication passes penetration testing
- ✅ Payment flow PCI DSS compliant
- ✅ All sensitive data encrypted
- ✅ Audit logs comprehensive and immutable

---

### Phase 3: Compliance Controls (3-4 hours)

**Agents:**
- `security-audit-specialist` - Control implementation
- `business-analyst` - Policy documentation
- `technical-writer` - Procedure documentation
- `devops-engineer` - Infrastructure hardening

**Control Implementation:**

1. **Access Controls**
   - Principle of least privilege
   - Separation of duties
   - Privileged user monitoring
   - Access review procedures (quarterly)
   - Offboarding procedures
   - Emergency access (break-glass)

2. **Change Management**
   - Code review requirements (2+ reviewers)
   - Approval workflows for production
   - Rollback procedures
   - Change advisory board (CAB)
   - Emergency change procedures
   - Change success metrics

3. **Vulnerability Management**
   - Automated vulnerability scanning
   - Penetration testing (annual minimum)
   - Patch management SLA (critical: 72 hours)
   - Dependency monitoring (Snyk, Dependabot)
   - Security advisory tracking
   - Remediation tracking

4. **Incident Response**
   - Security incident classification
   - Incident response team (IRT)
   - Escalation procedures
   - Breach notification plan (72-hour rule)
   - Forensics preservation
   - Post-incident review

5. **Business Continuity**
   - Recovery time objective (RTO): 4 hours
   - Recovery point objective (RPO): 1 hour
   - Backup testing (monthly)
   - Disaster recovery drills (quarterly)
   - Alternative site arrangements
   - Crisis communication plan

6. **Vendor Management**
   - Third-party risk assessment
   - Vendor security questionnaires
   - SOC 2 report collection
   - Contract security requirements
   - Vendor monitoring
   - Exit procedures

**Success Criteria:**
- ✅ SOC 2 controls documented and implemented
- ✅ Incident response plan tested
- ✅ Business continuity validated
- ✅ Third-party risks assessed

---

### Phase 4: Regulatory Compliance (3-4 hours)

**Agents:**
- `business-analyst` - Regulatory mapping
- `backend-api-engineer` - Compliance features
- `technical-writer` - Regulatory documentation
- `data-engineer` - Reporting infrastructure

**Compliance Features:**

1. **Know Your Customer (KYC)**
   - Identity verification (IDV)
   - Document verification (passport, license)
   - Liveness detection (prevent fraud)
   - Watchlist screening (OFAC, sanctions)
   - Politically Exposed Person (PEP) screening
   - Ongoing monitoring

2. **Anti-Money Laundering (AML)**
   - Transaction monitoring rules
   - Suspicious activity detection
   - SAR filing procedures (FinCEN 314)
   - Currency Transaction Report (CTR) threshold
   - Enhanced due diligence (EDD)
   - AML training program

3. **Data Privacy (GDPR/CCPA)**
   - Consent management
   - Right to access (data export)
   - Right to erasure ("right to be forgotten")
   - Data portability
   - Privacy policy and notices
   - Data breach notification (72 hours)

4. **Financial Reporting**
   - General ledger integration
   - Transaction reconciliation
   - Regulatory reporting (Call Reports, etc.)
   - Tax reporting (1099-K, etc.)
   - Audit-ready records
   - Escheatment tracking (unclaimed funds)

5. **Record Retention**
   - Document retention schedule
   - Automated archival
   - Legal hold procedures
   - Secure deletion after retention
   - eDiscovery readiness
   - Archive restoration testing

**Success Criteria:**
- ✅ KYC/AML procedures operational
- ✅ Privacy rights automated (GDPR/CCPA)
- ✅ Regulatory reporting tested
- ✅ Record retention policy enforced

---

### Phase 5: Security Testing & Audit (2-3 hours)

**Agents:**
- `security-audit-specialist` - Comprehensive security audit
- `qa-test-engineer` - Compliance testing
- `incident-coordinator` - Incident simulation
- `the-skeptic` - Risk assessment

**Testing & Validation:**

1. **Penetration Testing**
   - External penetration test
   - Internal penetration test
   - API security testing
   - Social engineering test
   - Physical security test (if on-premise)
   - Remediation validation

2. **Compliance Audit**
   - PCI DSS self-assessment (SAQ)
   - SOC 2 Type II audit preparation
   - GDPR compliance review
   - Gap analysis against regulations
   - Control effectiveness testing
   - Evidence collection

3. **Disaster Recovery Test**
   - Full system restore test
   - Database recovery test
   - Backup validation
   - RTO/RPO verification
   - Communication plan test
   - Post-test report

4. **Incident Response Drill**
   - Simulated security breach
   - Incident detection time
   - Response time measurement
   - Escalation procedure validation
   - Communication effectiveness
   - Lessons learned documentation

5. **Risk Assessment**
   - Threat modeling
   - Vulnerability assessment
   - Impact analysis
   - Risk prioritization
   - Mitigation recommendations
   - Residual risk acceptance

**Success Criteria:**
- ✅ Penetration test passed (no critical findings)
- ✅ Audit readiness confirmed
- ✅ DR test successful (met RTO/RPO)
- ✅ Incident response effective

---

### Phase 6: Deployment & Operations (2-3 hours)

**Agents:**
- `devops-engineer` - Secure deployment
- `observability-engineer` - Security monitoring
- `incident-coordinator` - Runbooks and playbooks
- `technical-writer` - Operations documentation

**Production Readiness:**

1. **Infrastructure Security**
   - Network segmentation (VLANs, VPCs)
   - Firewall rules (deny-all default)
   - Intrusion detection (IDS/IPS)
   - DDoS protection (CloudFlare, AWS Shield)
   - WAF rules (OWASP Top 10)
   - Security groups and NACLs

2. **Monitoring & Alerting**
   - Security Information and Event Management (SIEM)
   - Anomaly detection (ML-based)
   - Failed login monitoring
   - Privilege escalation alerts
   - Data exfiltration detection
   - Compliance violation alerts

3. **Operational Procedures**
   - Deployment runbooks
   - Rollback procedures
   - Scaling procedures
   - Backup and restore
   - Incident response playbooks
   - Maintenance windows

4. **Compliance Operations**
   - Daily reconciliation
   - Weekly security reviews
   - Monthly access reviews
   - Quarterly DR tests
   - Annual penetration tests
   - Continuous compliance monitoring

**Success Criteria:**
- ✅ Production environment hardened
- ✅ Monitoring covering all security events
- ✅ Runbooks validated through drills
- ✅ Compliance dashboard operational

---

## Execution Command

```bash
# Full FinTech compliance workflow
/fintech-compliance

# Or invoke specific phases:
/fintech-compliance --phase=architecture
/fintech-compliance --phase=development
/fintech-compliance --phase=controls
/fintech-compliance --phase=regulatory
/fintech-compliance --phase=testing
/fintech-compliance --phase=deployment
```

---

## Example: Building a Digital Wallet App

**User Request:**
> "Build a digital wallet app for peer-to-peer payments. Users can link bank accounts, send money, request payments. Need PCI DSS and SOC 2 compliance. Target US market initially."

**Orchestrated Workflow:**

### Phase 1: Architecture (business-analyst, security-audit-specialist)
- **Regulatory Requirements:**
  - State money transmitter licenses (varies by state)
  - PCI DSS Level 1 (processing >6M transactions/year)
  - SOC 2 Type II (for enterprise customers)
  - GLBA (financial privacy)
  - BSA/AML (Bank Secrecy Act, Anti-Money Laundering)

- **Security Architecture:**
  - Zero-trust network (AWS VPC with private subnets)
  - End-to-end encryption (TLS 1.3, AES-256)
  - Hardware Security Module (HSM) for key management
  - MFA mandatory for all users
  - Biometric authentication (Face ID, Touch ID)

- **Tech Stack:**
  - Backend: Node.js + PostgreSQL (encrypted)
  - Payment: Stripe Connect (handles PCI compliance)
  - KYC/AML: Plaid Identity + Persona
  - Infrastructure: AWS (SOC 2, PCI DSS certified)

### Phase 2: Development (backend-api-engineer, database-administrator)
- **Core Features:**
  - Account linking (Plaid for bank connections)
  - P2P transfers (instant via Stripe)
  - Transaction history (encrypted at rest)
  - Split payments and requests
  - Recurring payments
  - In-app notifications

- **Security Implementation:**
  - OAuth 2.0 + MFA (TOTP via Authy)
  - API signing (HMAC-SHA256)
  - Rate limiting (100 req/min per user)
  - Tokenization (Stripe tokens, no CHD stored)
  - Field-level encryption (SSN, account numbers)
  - Audit logging (all financial transactions)

### Phase 3: Compliance Controls (security-audit-specialist, business-analyst)
- **Controls Implemented:**
  - Access control matrix (least privilege)
  - Code review (2+ engineers, security scan)
  - Vulnerability scanning (daily automated)
  - Incident response plan (breach <72 hours)
  - Business continuity (RTO: 4h, RPO: 1h)
  - Vendor assessments (Stripe, Plaid, AWS)

### Phase 4: Regulatory (business-analyst, data-engineer)
- **KYC/AML:**
  - Identity verification (Persona IDV)
  - Document upload (passport, license)
  - Liveness check (selfie verification)
  - OFAC screening (automated)
  - Transaction monitoring ($10K threshold alerts)
  - SAR filing procedure (manual review)

- **Privacy Compliance:**
  - GDPR consent (EU users)
  - CCPA opt-out (California users)
  - Data export (JSON format)
  - Account deletion (30-day grace period)
  - Privacy policy (attorney-reviewed)

### Phase 5: Testing (security-audit-specialist, qa-test-engineer)
- **Penetration Test:**
  - External test (no critical vulnerabilities)
  - API security test (auth bypass attempts failed)
  - Social engineering test (staff trained)

- **Audits:**
  - PCI DSS SAQ D (merchant level 1)
  - SOC 2 Type II (6-month observation)
  - Gap analysis (100% controls implemented)

### Phase 6: Deployment (devops-engineer, observability-engineer)
- **Infrastructure:**
  - Multi-region deployment (US-East, US-West)
  - Auto-scaling (2-10 instances)
  - CDN (CloudFlare for DDoS protection)
  - WAF (OWASP rule set)
  - Monitoring (Datadog APM + SIEM)

- **Launch:**
  - Beta: 100 users (1 month testing)
  - Public: Phased rollout (1K, 10K, 100K users)
  - Compliance: SOC 2 report obtained
  - Licensing: Filed in 10 states (ongoing)

**Timeline:** 12 weeks (includes audit waiting periods)
**Outcome:**
- Month 1: 5K users, $200K transaction volume
- Month 3: 25K users, $2M transaction volume
- Month 6: SOC 2 Type II certified, 50K users

**Compliance Status:**
- ✅ PCI DSS Level 1 compliant (via Stripe)
- ✅ SOC 2 Type II certified
- ✅ GDPR/CCPA compliant
- ⏳ State licenses (10/50 states approved)

---

## Cost & Timeline Estimates

### Development & Compliance Costs

**With ClaudeAgents:**
- Development: 12-16 hours of focused work
- Compliance consulting: $10K-$20K (external auditor)
- Audit fees: $15K-$30K (SOC 2 Type II)
- Legal fees: $5K-$15K (attorney review)
- **Total: $30K-$65K, 3-4 months**

**Traditional Development:**
- Development: 6-12 months, 3-5 engineers ($300K-$600K)
- Compliance: $50K-$100K (consultant + audit)
- Legal: $20K-$50K
- **Total: $370K-$750K, 9-18 months**

**Time Savings:** 75-85%
**Cost Savings:** 90-92%

### Ongoing Compliance Costs

- **Annual SOC 2 audit:** $15K-$25K
- **Penetration testing:** $10K-$20K
- **Compliance monitoring:** $5K-$10K/month (tools + staff)
- **Legal updates:** $5K-$10K/year
- **Insurance (E&O, cyber):** $10K-$30K/year

---

## Success Metrics

### Technical Metrics
- **Uptime:** >99.95% (financial-grade SLA)
- **API latency:** <200ms (p95)
- **Error rate:** <0.01%
- **Security incidents:** Zero critical (target)

### Compliance Metrics
- **Audit findings:** Zero critical, <5 medium
- **Control effectiveness:** >95%
- **Incident response time:** <1 hour (detection to containment)
- **Backup success rate:** 100%
- **DR test success:** Meets RTO/RPO

### Business Metrics
- **Regulatory compliance:** 100% (all applicable regs)
- **Audit pass rate:** 100% (SOC 2, PCI DSS)
- **Customer trust:** >4.5/5 security rating
- **Churn due to security:** <0.5%

---

## Regulatory Reference Guide

### United States

**PCI DSS (Payment Card Industry Data Security Standard)**
- **Scope:** All entities handling credit/debit cards
- **Levels:** Based on transaction volume
- **Requirements:** 12 high-level requirements, 78 base requirements
- **Attestation:** Self-Assessment Questionnaire (SAQ) or audit

**SOC 2 Type II**
- **Scope:** Service organizations handling customer data
- **Trust Criteria:** Security, Availability, Confidentiality, Processing Integrity, Privacy
- **Observation Period:** Minimum 6 months
- **Auditor:** CPA firm

**Bank Secrecy Act (BSA) / Anti-Money Laundering (AML)**
- **Scope:** Money transmitters, banks, financial institutions
- **Requirements:** KYC, transaction monitoring, SAR/CTR filing
- **Regulator:** FinCEN (Financial Crimes Enforcement Network)

**Gramm-Leach-Bliley Act (GLBA)**
- **Scope:** Financial institutions
- **Requirements:** Privacy notices, safeguards, information sharing disclosures
- **Regulator:** FTC, OCC, FDIC (depends on entity)

**State Money Transmitter Licenses**
- **Scope:** Varies by state (48 states + DC require licenses)
- **Requirements:** Surety bonds, net worth minimums, compliance officer
- **Timeline:** 6-18 months per state

### European Union

**General Data Protection Regulation (GDPR)**
- **Scope:** All entities processing EU citizen data
- **Requirements:** Consent, right to access, right to erasure, breach notification (72h)
- **Penalties:** Up to €20M or 4% of global revenue

**Payment Services Directive 2 (PSD2)**
- **Scope:** Payment service providers in EU
- **Requirements:** Strong Customer Authentication (SCA), open banking APIs
- **Regulator:** National competent authorities

### Global Standards

**ISO 27001 (Information Security Management)**
- **Scope:** Any organization handling sensitive data
- **Requirements:** 114 controls across 14 domains
- **Certification:** External audit by accredited body

**SWIFT Customer Security Programme (CSP)**
- **Scope:** SWIFT members (banks)
- **Requirements:** 16 mandatory controls, 11 advisory
- **Attestation:** Annual self-attestation

---

## Related Workflows

- `/saas-mvp` - SaaS product development
- `/ecommerce-platform` - E-commerce with payment processing
- `/security-audit` - Comprehensive security review
- `/production-readiness` - Pre-deployment checklist

---

## Customization Options

### Industry Verticals

**Digital Payments:**
- P2P transfers (Venmo, Cash App)
- Bill payment platforms
- Remittance services
- Cryptocurrency wallets

**Lending & Credit:**
- Personal loans
- Buy-now-pay-later (BNPL)
- Credit scoring platforms
- Debt collection

**Investment & Trading:**
- Robo-advisors
- Stock trading apps
- Cryptocurrency exchanges
- Real estate crowdfunding

**Banking:**
- Neobanks (digital-only banks)
- Business banking
- Expense management
- Treasury management

### Compliance Variations

**Startup (Pre-Revenue):**
- Minimal compliance (SOC 2 Type I)
- Payment processor handles PCI DSS
- Focus on security fundamentals
- Audit readiness, not certification

**Growth Stage (Revenue, Customers):**
- SOC 2 Type II (enterprise sales)
- PCI DSS if processing cards directly
- State licenses (as needed)
- Full compliance program

**Enterprise (Regulated Entity):**
- Full regulatory compliance
- Multiple audits (SOC 2, PCI, ISO 27001)
- Dedicated compliance team
- Continuous monitoring and reporting

---

## Risk Warnings

### High-Risk Items

🚨 **Regulatory Non-Compliance**
- Fines: $100K-$1M+ per violation
- License revocation
- Legal liability
- Reputation damage

🚨 **Security Breach**
- Data breach notification costs: $50K-$500K
- Legal settlements: $1M-$100M+
- Customer churn: 20-30%
- Brand damage: Irreversible

🚨 **Operational Failure**
- Downtime cost: $5K-$50K per hour
- Lost transactions: Revenue + trust
- SLA penalties (if enterprise)

### Mitigation Strategies

✅ **Hire Compliance Expertise**
- Fractional CISO (first 6-12 months)
- Compliance consultant (audit prep)
- Legal counsel (regulatory)

✅ **Use Certified Infrastructure**
- AWS/GCP/Azure (SOC 2, PCI DSS)
- Stripe/Plaid (payment, banking)
- Auth0/Okta (authentication)

✅ **Insurance Coverage**
- Cyber liability insurance
- Errors & Omissions (E&O)
- Directors & Officers (D&O)

✅ **Phased Approach**
- Start with minimal compliance
- Add certifications as needed
- Continuous improvement mindset

---

## Version History

- **v1.0** (2025-10-07): Initial FinTech compliance workflow

**Coming Soon:**
- Insurance & HealthTech compliance variants
- International expansion guides
- Cryptocurrency-specific compliance

---

**Maintained By:** business-analyst, security-audit-specialist, backend-api-engineer
**Last Updated:** 2025-10-07
**License:** MIT

**⚠️ DISCLAIMER:** This workflow provides technical implementation guidance. Consult qualified legal counsel and compliance experts for regulatory advice. Regulations vary by jurisdiction and change frequently.
