# Business Requirements Analysis

**Command:** `/requirements-analysis`
**Agents:** `business-analyst`, `product-manager`, `technical-writer`
**Complexity:** Medium
**Duration:** 4-6 hours (depending on project scope)

## Overview

Performs comprehensive business requirements analysis, gathering stakeholder needs, documenting business requirements, creating user stories, and producing a complete Business Requirements Document (BRD) ready for development.

## What This Command Does

This command orchestrates a complete requirements analysis workflow across three specialized agents:

1. **Requirements Gathering** (`business-analyst`)
   - Stakeholder interviews and analysis
   - Business problem identification
   - Current state vs. desired state analysis
   - Functional and non-functional requirements
   - Process flow documentation (BPMN, flowcharts)
   - Use case development

2. **User Story Creation** (`product-manager`)
   - Epic and user story breakdown
   - Acceptance criteria definition
   - Story prioritization (MoSCoW, RICE)
   - Story point estimation
   - Sprint planning alignment

3. **Documentation** (`technical-writer`)
   - Business Requirements Document (BRD)
   - Stakeholder communication materials
   - Requirements traceability matrix
   - Glossary and terminology

## Usage

```bash
# New feature requirements
/requirements-analysis --project="Customer Portal Redesign"

# From stakeholder interviews
/requirements-analysis --interviews=interviews.md --stakeholders="Product,Engineering,Sales"

# Existing system enhancement
/requirements-analysis --system="CRM" --enhancement="Email automation workflow"

# With existing documentation
/requirements-analysis --docs=current-spec.md --output=brd.md
```

## Execution Workflow

### Phase 1: Stakeholder Discovery (60-90 min)

**business-analyst** conducts stakeholder analysis:

**Stakeholder Identification:**
1. **Key Stakeholders:**
   - Executive sponsors
   - Product owners
   - End users
   - Technical teams
   - External partners

2. **Stakeholder Analysis (RACI):**
   - Responsible: Who does the work
   - Accountable: Final decision authority
   - Consulted: Subject matter experts
   - Informed: Keep updated

3. **Power/Interest Matrix:**
   - High Power, High Interest: Manage Closely
   - High Power, Low Interest: Keep Satisfied
   - Low Power, High Interest: Keep Informed
   - Low Power, Low Interest: Monitor

**Example Output:**
```
Stakeholder Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Stakeholders Identified: 12

Executive Sponsors (2):
- Sarah Chen, VP Product (High Power, High Interest)
- Michael Rodriguez, CTO (High Power, High Interest)

Product Team (3):
- Jennifer Kim, Product Manager (Accountable)
- Alex Thompson, Product Owner (Responsible)
- User Research Team (Consulted)

Engineering Team (4):
- David Park, Engineering Manager (Responsible)
- Frontend Team Lead (Responsible)
- Backend Team Lead (Responsible)
- QA Lead (Consulted)

End Users (3):
- Sales Team Representatives (High Interest)
- Customer Success Team (High Interest)
- External Customers (High Interest)

RACI Matrix:
                        Sarah  Michael  Jennifer  Alex  David  Frontend  Backend  QA
Business Requirements     A      C         R       C     I       I         I       I
Technical Architecture    I      A         C       I     R       C         C       C
User Stories             C      I         A       R     C       I         I       I
Implementation           I      C         C       I     A       R         R       C
Testing & QA             I      I         C       I     C       I         I       A
```

### Phase 2: Business Problem Definition (45-60 min)

**business-analyst** defines the business problem:

**Problem Statement:**
1. **Current State:**
   - What's the current situation?
   - What pain points exist?
   - What's the business impact?

2. **Desired State:**
   - What's the ideal outcome?
   - What success looks like?
   - What value will be delivered?

3. **Gap Analysis:**
   - Current vs. desired state gaps
   - Root cause analysis
   - Constraints and dependencies

**Example Output:**
```
Business Problem Definition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current State:
Sales team uses manual spreadsheets to track leads and opportunities.
This results in:
- Data inconsistency across team members
- No real-time visibility into pipeline
- Manual data entry consuming 8-10 hours/week per rep
- Lost opportunities due to delayed follow-ups
- Inability to forecast revenue accurately

Business Impact:
- Lost revenue: Est. $500K/year from missed opportunities
- Productivity loss: 320 hours/month across 8 sales reps
- Data quality: 60% accuracy in manual spreadsheets
- Customer experience: 24-48 hour response time (vs. 2-4 hour target)

Desired State:
Automated CRM system that:
- Centralizes all customer data in single source of truth
- Provides real-time pipeline visibility to entire team
- Automates lead capture and routing
- Enables <2 hour response time with automated workflows
- Generates accurate revenue forecasts

Expected Business Value:
- Revenue increase: +$750K/year (recovered + new opportunities)
- Productivity gain: 240 hours/month (75% reduction in manual work)
- Data accuracy: >95% (automated data validation)
- Customer satisfaction: 2-4 hour response time achieved

Gap Analysis:
1. Technology Gap: Spreadsheets → CRM platform
2. Process Gap: Manual → Automated workflows
3. Data Gap: Siloed → Centralized database
4. Skills Gap: Basic Excel → CRM platform training required
5. Integration Gap: Standalone → Integrated with email, calendar, support

Root Causes:
- Legacy process established 10 years ago
- No budget allocated for CRM in previous years
- Team resistance to change ("spreadsheets work fine")
- Lack of technical expertise on CRM platforms
- Previous failed CRM implementation 3 years ago

Constraints:
- Budget: $50K implementation, $10K/year ongoing
- Timeline: Must launch before Q4 sales cycle (6 months)
- Resources: 1 FTE dedicated project manager, 0.5 FTE developer
- Training: Maximum 2 days per sales rep
- Integration: Must work with existing email (Gmail) and calendar
```

### Phase 3: Requirements Elicitation (90-120 min)

**business-analyst** gathers detailed requirements:

**Requirement Types:**
1. **Functional Requirements:**
   - What the system must do
   - User capabilities and features
   - Business rules and logic

2. **Non-Functional Requirements:**
   - Performance (response time, throughput)
   - Security (authentication, authorization, data protection)
   - Usability (ease of use, accessibility)
   - Scalability (user growth, data volume)
   - Reliability (uptime, disaster recovery)

3. **Business Rules:**
   - Policies and regulations
   - Calculation formulas
   - Validation rules
   - Workflow rules

**Example Output:**
```
Requirements Specification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Functional Requirements (25 total):

FR-1: Lead Capture
- System SHALL automatically capture leads from website forms
- System SHALL import leads from CSV files
- System SHALL validate required fields (name, email, company)
- System SHALL assign leads based on territory rules
- System SHALL send notification to assigned sales rep within 5 minutes

FR-2: Contact Management
- System SHALL store contact information (name, email, phone, company, role)
- System SHALL track communication history (calls, emails, meetings)
- System SHALL link contacts to accounts and opportunities
- System SHALL prevent duplicate contacts (match on email)
- System SHALL support custom fields (up to 20 per object)

FR-3: Opportunity Pipeline
- System SHALL support 5 pipeline stages (Lead, Qualified, Proposal, Negotiation, Closed)
- System SHALL calculate probability by stage (20%, 40%, 60%, 80%, 100%)
- System SHALL track opportunity value and close date
- System SHALL generate weighted forecast (value × probability)
- System SHALL allow manual stage override with reason

[22 more functional requirements...]

Non-Functional Requirements (15 total):

NFR-1: Performance
- System SHALL load dashboard in <2 seconds
- System SHALL support 100 concurrent users
- System SHALL sync email in <30 seconds
- System SHALL generate reports in <10 seconds

NFR-2: Security
- System SHALL use OAuth 2.0 for authentication
- System SHALL enforce role-based access control (RBAC)
- System SHALL encrypt data at rest (AES-256)
- System SHALL encrypt data in transit (TLS 1.3)
- System SHALL log all data access and changes
- System SHALL support MFA for admin users

NFR-3: Usability
- System SHALL be accessible (WCAG 2.1 AA compliant)
- System SHALL work on desktop and mobile (responsive design)
- System SHALL provide contextual help and tooltips
- System SHALL support keyboard navigation
- System SHALL provide undo for destructive actions

[12 more non-functional requirements...]

Business Rules (20 total):

BR-1: Lead Assignment
- Leads with company size >500 employees → Enterprise team
- Leads with company size 50-500 employees → Mid-market team
- Leads with company size <50 employees → SMB team
- Leads outside territories → Round-robin assignment

BR-2: Opportunity Forecasting
- Forecast = Sum(Opportunity Value × Probability)
- Probability by stage: Lead 20%, Qualified 40%, Proposal 60%, Negotiation 80%, Closed Won 100%
- Opportunities >90 days in same stage → Flag for review

BR-3: Data Validation
- Email addresses MUST match regex pattern
- Phone numbers MUST be 10-15 digits
- Company names MUST be unique
- Opportunity close dates MUST be future dates
- Opportunity values MUST be >$0

[17 more business rules...]
```

### Phase 4: Use Case Development (60-90 min)

**business-analyst** creates detailed use cases:

**Use Case Template:**
1. **Use Case Name:** Descriptive title
2. **Actor:** Who performs the action
3. **Preconditions:** What must be true before
4. **Main Flow:** Step-by-step happy path
5. **Alternative Flows:** Variations and exceptions
6. **Postconditions:** What's true after success
7. **Business Rules:** Applicable rules
8. **Non-Functional Requirements:** Performance, security, etc.

**Example Output:**
```
Use Case: Capture and Assign Web Lead
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UC-01: Capture and Assign Web Lead

Primary Actor: Sales Representative
Secondary Actor: System (automated)

Preconditions:
- Website contact form is configured and live
- Lead assignment rules are defined
- Sales reps have active user accounts

Main Flow:
1. Prospect submits contact form on website
2. System validates required fields (name, email, company)
3. System checks for duplicate lead (match on email)
4. System creates new lead record
5. System evaluates lead assignment rules
   a. Company size >500 → Enterprise team
   b. Company size 50-500 → Mid-market team
   c. Company size <50 → SMB team
6. System assigns lead to available rep (round-robin within team)
7. System sends email notification to assigned rep
8. System sends auto-response email to prospect
9. System logs lead source as "Website"
10. Use case ends successfully

Alternative Flow 1: Duplicate Lead
3a. System finds existing lead with same email
3b. System updates existing lead record (append note)
3c. System notifies original assigned rep
3d. Resume at step 9

Alternative Flow 2: No Available Rep
6a. No reps available in assigned team
6b. System assigns to team queue
6c. System sends notification to team manager
6d. Resume at step 8

Alternative Flow 3: Invalid Data
2a. Required field missing or invalid format
2b. System displays validation error to prospect
2c. Prospect corrects and resubmits
2d. Resume at step 2

Exception Flow: System Unavailable
*. System is down or unresponsive
*1. System buffers form submission
*2. System processes once available (within 5 minutes SLA)
*3. If >5 minutes, escalate to on-call engineer

Postconditions (Success):
- Lead record created in CRM
- Lead assigned to sales rep
- Rep notified via email
- Prospect receives auto-response
- Lead source tracked

Business Rules Applied:
- BR-1: Lead Assignment (territory rules)
- BR-3: Data Validation (email, required fields)

Non-Functional Requirements:
- NFR-1: Lead captured within 30 seconds
- NFR-2: Rep notified within 5 minutes
- NFR-2: Data encrypted at rest and in transit
```

### Phase 5: User Story Creation (60-90 min)

**product-manager** breaks down requirements into user stories:

**User Story Format:**
```
As a [user role]
I want to [capability]
So that [business value]

Acceptance Criteria:
- Given [context]
- When [action]
- Then [outcome]

Story Points: [1, 2, 3, 5, 8, 13, 21]
Priority: [Must Have, Should Have, Could Have, Won't Have]
```

**Example Output:**
```
User Stories - CRM Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Epic 1: Lead Management (13 stories, 55 story points)

Story 1.1: Capture Web Leads
As a sales representative
I want web form submissions to automatically create leads in the CRM
So that I can follow up quickly without manual data entry

Acceptance Criteria:
- Given a prospect submits the website contact form
- When the form is submitted with valid data
- Then a lead is created in CRM within 30 seconds
- And I receive an email notification within 5 minutes
- And the lead source is tagged as "Website"

Story Points: 5
Priority: Must Have
Dependencies: None
Sprint: 1

Story 1.2: Assign Leads Based on Territory
As a sales manager
I want leads automatically assigned based on company size and territory
So that the right rep handles each opportunity

Acceptance Criteria:
- Given a new lead is created
- When company size is >500 employees
- Then lead is assigned to Enterprise team
- And round-robin within team members
- When company size is 50-500 employees
- Then lead is assigned to Mid-market team
- When company size is <50 employees
- Then lead is assigned to SMB team

Story Points: 8
Priority: Must Have
Dependencies: Story 1.1
Sprint: 1

Story 1.3: Prevent Duplicate Leads
As a sales representative
I want the system to detect duplicate leads by email
So that I don't waste time on contacts we already have

Acceptance Criteria:
- Given a lead with email "john@example.com" exists
- When a new lead with same email is submitted
- Then system appends note to existing lead
- And notifies the originally assigned rep
- And does not create duplicate record

Story Points: 3
Priority: Should Have
Dependencies: Story 1.1
Sprint: 2

[10 more lead management stories...]

Epic 2: Contact & Account Management (8 stories, 34 story points)
Epic 3: Opportunity Pipeline (10 stories, 42 story points)
Epic 4: Reporting & Forecasting (6 stories, 28 story points)
Epic 5: Mobile Access (5 stories, 21 story points)

Total: 42 user stories, 180 story points
Estimated Duration: 6 sprints (12 weeks, 2-week sprints)

Story Prioritization (MoSCoW):
- Must Have: 18 stories (43%) - Core functionality
- Should Have: 15 stories (36%) - Important but not critical
- Could Have: 7 stories (17%) - Nice to have
- Won't Have: 2 stories (5%) - Deferred to Phase 2
```

### Phase 6: Process Flow Documentation (45-60 min)

**business-analyst** creates process flow diagrams:

**Process Flows:**
1. **Current State (As-Is):**
   - Document existing manual process
   - Identify inefficiencies and pain points

2. **Future State (To-Be):**
   - Design optimized automated process
   - Show system interactions

3. **Swim Lane Diagrams:**
   - Show responsibilities across roles
   - Handoff points between teams

**Example Output:**
```
Lead-to-Opportunity Process Flow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current State (As-Is):
┌────────────┐     ┌───────────┐     ┌──────────┐
│ Prospect   │────▶│ Manual    │────▶│ Sales    │
│ Submits    │     │ Spreadsheet│     │ Rep      │
│ Web Form   │     │ Entry     │     │ Follow-up│
└────────────┘     └───────────┘     └──────────┘
                         ▼
                   ┌───────────┐
                   │ Data      │
                   │ Quality   │
                   │ Issues    │
                   └───────────┘

Issues:
- 24-48 hour delay from submission to follow-up
- Manual data entry errors (40% error rate)
- Leads lost in spreadsheet chaos
- No automated routing

Future State (To-Be):
┌────────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│ Prospect   │────▶│ CRM Auto  │────▶│ Auto     │────▶│ Sales    │
│ Submits    │     │ Capture   │     │ Assignment│     │ Rep      │
│ Web Form   │     │ (30 sec)  │     │ (5 min)  │     │ Notified │
└────────────┘     └───────────┘     └──────────┘     └──────────┘
                         │
                         ▼
                   ┌───────────┐
                   │ Data      │
                   │ Validation│
                   │ (Auto)    │
                   └───────────┘

Benefits:
- <5 minute response time
- 95%+ data accuracy (automated validation)
- Zero lost leads
- Intelligent routing based on rules

Swim Lane Diagram (To-Be):

Prospect        │  ══════════►  Submit Form
                │
CRM System      │               Validate Data ══► Create Lead ══► Assign Lead
                │                                                      │
Sales Rep       │                                               Receive Notification ══► Contact Lead
                │
Manager         │                                               View Dashboard
```

### Phase 7: Documentation Generation (60-90 min)

**technical-writer** creates Business Requirements Document:

**BRD Structure:**
1. Executive Summary
2. Business Problem & Objectives
3. Stakeholder Analysis
4. Scope (In-Scope / Out-of-Scope)
5. Functional Requirements
6. Non-Functional Requirements
7. Business Rules
8. Use Cases
9. User Stories (Epics)
10. Process Flows
11. Assumptions & Constraints
12. Risks & Mitigation
13. Success Criteria
14. Appendices

**Example Output:**
```markdown
# Business Requirements Document
## CRM Implementation Project

**Document Version:** 1.0
**Date:** 2024-10-08
**Author:** Business Analyst Team
**Status:** Draft for Review

---

## 1. Executive Summary

### 1.1 Purpose
This document defines the business requirements for implementing a Customer Relationship Management (CRM) system to replace manual spreadsheet-based lead and opportunity tracking.

### 1.2 Business Problem
The sales team currently manages leads and opportunities using manual spreadsheets, resulting in:
- $500K/year in lost revenue from missed opportunities
- 320 hours/month in productivity loss across 8 sales reps
- 60% data accuracy due to manual entry errors
- 24-48 hour response time vs. 2-4 hour target

### 1.3 Proposed Solution
Implement automated CRM system providing:
- Automated lead capture from website (<30 seconds)
- Intelligent lead routing based on territory rules (<5 minutes)
- Centralized customer database (95%+ data accuracy)
- Real-time pipeline visibility and forecasting
- <2 hour response time with automated workflows

### 1.4 Expected Business Value
- Revenue increase: +$750K/year (150% ROI year 1)
- Productivity gain: 240 hours/month (75% reduction)
- Data accuracy: >95% (vs. current 60%)
- Customer satisfaction: 2-4 hour response time achieved

### 1.5 Project Scope
**In-Scope:**
- Lead capture and routing automation
- Contact and account management
- Opportunity pipeline tracking
- Sales forecasting and reporting
- Mobile access (iOS, Android)
- Email integration (Gmail)
- Calendar integration (Google Calendar)

**Out-of-Scope (Phase 2):**
- Marketing automation
- Customer support ticketing
- Advanced analytics and AI
- Third-party data enrichment
- Custom mobile app

### 1.6 Success Criteria
- 100% of sales reps actively using CRM daily (by Week 8)
- >90% leads followed up within 4 hours (by Week 12)
- >95% data accuracy maintained (ongoing)
- $500K+ revenue recovered in first year
- Sales rep satisfaction >4/5 (survey after 3 months)

---

## 2. Stakeholder Analysis

[Full stakeholder RACI matrix from Phase 1...]

---

## 3. Business Problem & Objectives

[Full business problem definition from Phase 2...]

---

## 4. Functional Requirements

[All 25 functional requirements from Phase 3...]

---

## 5. Non-Functional Requirements

[All 15 non-functional requirements from Phase 3...]

---

## 6. Business Rules

[All 20 business rules from Phase 3...]

---

## 7. Use Cases

[All 15 use cases from Phase 4...]

---

## 8. User Stories

[All 42 user stories organized by epic from Phase 5...]

---

## 9. Process Flows

[BPMN diagrams and swim lanes from Phase 6...]

---

## 10. Assumptions & Constraints

### 10.1 Assumptions
- Sales team has stable internet connectivity
- Gmail and Google Calendar will remain primary tools
- Team will complete CRM training within 2 weeks
- Legacy spreadsheet data can be migrated (<1% data loss)

### 10.2 Constraints
- Budget: $50K implementation, $10K/year ongoing
- Timeline: 6-month implementation before Q4
- Resources: 1 FTE PM, 0.5 FTE developer
- Training: Maximum 2 days per sales rep

---

## 11. Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| User adoption resistance | High | High | Early stakeholder engagement, comprehensive training, exec sponsorship |
| Data migration issues | Medium | High | Phased migration, data validation, parallel run period |
| Integration failures | Medium | Medium | Proof of concept, vendor support SLA, fallback plan |
| Budget overrun | Low | Medium | Detailed estimate, contingency buffer, phased implementation |
| Timeline delays | Medium | Medium | Agile sprints, MVP approach, dedicated PM |

---

## 12. Requirements Traceability Matrix

| Req ID | Requirement | Use Case | User Story | Test Case | Status |
|--------|------------|----------|------------|-----------|--------|
| FR-1 | Lead Capture | UC-01 | Story 1.1 | TC-001 | Draft |
| FR-2 | Contact Mgmt | UC-02 | Story 2.1 | TC-010 | Draft |
| NFR-1 | Performance | All | All | TC-100 | Draft |
| ... | ... | ... | ... | ... | ... |

---

## 13. Glossary

**CRM:** Customer Relationship Management
**Lead:** Potential customer who has expressed interest
**Opportunity:** Qualified lead with defined sales potential
**Pipeline:** Collection of opportunities in various stages
**Forecast:** Projected revenue based on pipeline × probability
**MoSCoW:** Must have, Should have, Could have, Won't have
**RACI:** Responsible, Accountable, Consulted, Informed

---

## 14. Appendices

### Appendix A: Stakeholder Interview Notes
### Appendix B: Current Spreadsheet Templates
### Appendix C: Competitive CRM Analysis
### Appendix D: Vendor Evaluation Criteria
### Appendix E: Change Management Plan

---

**Document Approval:**

| Name | Role | Signature | Date |
|------|------|-----------|------|
| Sarah Chen | VP Product (Sponsor) | _________ | _____ |
| Michael Rodriguez | CTO (Sponsor) | _________ | _____ |
| Jennifer Kim | Product Manager | _________ | _____ |
| David Park | Engineering Manager | _________ | _____ |
```

## Success Metrics

Track requirements analysis effectiveness through:
- **Stakeholder Approval:** >90% stakeholder sign-off on BRD
- **Requirement Completeness:** Zero critical gaps discovered during development
- **Change Request Rate:** <10% requirements changed after approval
- **User Story Velocity:** Team completes estimated story points per sprint
- **Traceability:** 100% requirements mapped to user stories and test cases

## Common Use Cases

### New Product Feature
```bash
/requirements-analysis --project="User Dashboard v2.0" --stakeholders="Product,UX,Engineering"
```

### System Integration
```bash
/requirements-analysis --integration="CRM-to-Marketing Automation" --systems="Salesforce,HubSpot"
```

### Process Automation
```bash
/requirements-analysis --process="Expense Approval Workflow" --current-state=manual-process.md
```

### Regulatory Compliance
```bash
/requirements-analysis --compliance="GDPR Data Privacy" --regulations=gdpr-requirements.pdf
```

## Integration with Other Commands

This command works well with:
- `/product-roadmap` - Convert BRD into product roadmap with timelines
- `/documentation-generation` - Generate technical specifications from BRD
- `/architecture-review` - Validate technical feasibility of requirements
- `/test-coverage` - Create test plans from requirements

## Prerequisites

### Required Access
- Stakeholder availability for interviews (4-8 hours total)
- Access to current systems/processes (for as-is analysis)
- Business context and strategy documents

### Recommended Preparation
- Schedule stakeholder interviews in advance
- Gather existing documentation (process flows, specs)
- Define project scope and constraints
- Identify business objectives and KPIs

## Limitations

- **Time Required:** 4-6 hours for comprehensive analysis
- **Stakeholder Availability:** Depends on stakeholder schedules
- **Scope Creep:** Requires strong facilitation to maintain focus
- **Technical Details:** Business requirements only (not technical design)

## Best Practices

1. **Start with Why:** Understand business value before diving into features
2. **Engage Stakeholders Early:** Get buy-in from day one
3. **Use Visual Aids:** Process flows, diagrams clarify complex requirements
4. **Prioritize Ruthlessly:** Not everything can be "Must Have"
5. **Validate Assumptions:** Document and verify all assumptions
6. **Think in User Stories:** Frame requirements from user perspective
7. **Define Success Criteria:** Measurable outcomes, not just deliverables
8. **Plan for Change:** Requirements evolve; use version control

---

**Pro Tip**: Conduct requirements workshops with cross-functional teams (Product, Engineering, UX) to surface hidden requirements and build shared understanding early. This reduces costly late-stage changes.
