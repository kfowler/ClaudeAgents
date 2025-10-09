---
name: growth:metrics-setup
description: North Star metric identification and comprehensive analytics implementation plan combining product strategy, data engineering, and measurement framework design for data-driven growth
category: growth
---

# Growth Command: Metrics Setup

## Overview

This command orchestrates the design and implementation of a comprehensive growth metrics framework by identifying your North Star metric, designing supporting analytics infrastructure, creating actionable dashboards, and establishing a data-driven decision-making culture. Proper metrics foundation enables all other growth initiatives to be measured, optimized, and scaled.

**What this accomplishes:**
- North Star metric identification aligned with business objectives
- Complete analytics infrastructure design and implementation plan
- Growth metrics dashboard with leading and lagging indicators
- Data governance framework and team enablement
- Experimentation measurement framework

**When to use:**
- Early-stage product before scaling growth efforts
- Existing product with incomplete or fragmented analytics
- Planning to invest in growth initiatives requiring measurement
- Transitioning from opinion-based to data-driven decisions
- Preparing for fundraising or board reporting

**Expected execution time:** 20-30 minutes

## Prerequisites

- Clear understanding of business model and revenue drivers
- Product with at least basic user tracking capability
- Technical capability to implement analytics infrastructure
- Stakeholder alignment on importance of data-driven decisions
- Budget for analytics tools (if not using open-source)

## Multi-Agent Orchestration Strategy

### **Phase 1: North Star Metric & Growth Model**
Deploy `product-strategist` to:
- Identify North Star metric that predicts long-term business success
- Design growth model connecting North Star to revenue/business value
- Define supporting input metrics that drive North Star
- Create growth equation and lever identification
- Benchmark metrics against industry standards
- Align metrics with business stage (early growth, scale, maturity)
- Design metric ownership and accountability framework
- Establish guardrail metrics to prevent gaming

**Why this agent:** North Star metric selection requires deep understanding of business models, user psychology, and long-term value creation. Product strategists align metrics with strategic objectives.

**Deliverable:** North Star metric definition with rationale, growth model diagram, input metrics hierarchy, benchmark comparison, and ownership framework.

### **Phase 2: Analytics Infrastructure Design**
Engage `data-engineer` to:
- Design analytics tech stack (tracking, storage, processing, visualization)
- Create event taxonomy and data schema for growth metrics
- Plan data pipeline architecture for real-time and batch processing
- Design data warehouse schema for growth analytics
- Specify instrumentation requirements for product analytics
- Plan data quality monitoring and validation systems
- Create scalability plan for growing data volumes
- Establish data governance and privacy compliance framework

**Why this agent:** Analytics infrastructure requires expertise in data pipelines, warehouse design, and scalable systems. Data engineers build reliable, performant analytics foundations.

**Deliverable:** Analytics infrastructure architecture with tech stack recommendations, event schema, data pipeline design, warehouse schema, instrumentation guide, and implementation estimate.

### **Phase 3: Measurement Framework & Dashboards**
Use `product-manager` to:
- Design growth metrics dashboard hierarchy (executive, team, individual)
- Create North Star tracking dashboard with decomposition
- Define funnel analytics and conversion tracking
- Design cohort analysis framework for retention measurement
- Create A/B testing metrics and statistical significance framework
- Specify user segmentation dimensions for analysis
- Design alert system for metric anomalies and regression
- Establish reporting cadence and stakeholder communication

**Why this agent:** Product managers excel at defining actionable metrics, creating clear dashboards, and establishing measurement processes that drive decision-making.

**Deliverable:** Dashboard specifications with wireframes, metric definitions, visualization requirements, segmentation framework, alerting logic, and reporting templates.

### **Phase 4: Implementation Roadmap & Enablement**
Deploy `product-strategist` to:
- Create phased implementation plan (foundational → advanced analytics)
- Prioritize analytics instrumentation by business impact
- Design team training and enablement program
- Establish data-driven decision-making processes and rituals
- Create documentation and self-service analytics guide
- Plan regular metric reviews and optimization cycles
- Define success criteria for analytics maturity
- Design feedback loop for continuous improvement

**Why this agent:** Successful analytics adoption requires organizational change management, training, and process design. Product strategists drive cultural transformation toward data-driven decisions.

**Deliverable:** 30-60-90 day implementation roadmap with priorities, team enablement plan, process documentation, success criteria, and maturity assessment framework.

## Execution Flow

```
Phase 1: product-strategist
  ↓ (North Star metric + growth model)
Phase 2: data-engineer
  ↓ (Analytics infrastructure design)
Phase 3: product-manager
  ↓ (Dashboards + measurement framework)
Phase 4: product-strategist
  ↓ (Implementation roadmap + enablement)
Final Deliverables
```

## Expected Deliverables

- **North Star Framework**: Metric definition, growth model, input metrics, benchmarks, ownership model
- **Analytics Architecture**: Tech stack design, event schema, data pipeline, warehouse design, instrumentation guide
- **Dashboard Specifications**: Executive dashboard, team dashboards, metric definitions, visualization wireframes, alert configuration
- **Measurement Framework**: Funnel analytics, cohort analysis, A/B testing framework, segmentation dimensions
- **Implementation Roadmap**: Phased plan with priorities, enablement program, process documentation, success criteria

## Success Criteria

- [ ] North Star metric identified with clear business value connection
- [ ] Growth model created showing how inputs drive North Star
- [ ] Analytics tech stack selected and architecture designed
- [ ] Event taxonomy documented with 20-50 core events defined
- [ ] Data warehouse schema designed for growth analytics
- [ ] Dashboard wireframes created for executive and team views
- [ ] A/B testing statistical framework specified
- [ ] 30-60-90 day implementation roadmap with clear priorities
- [ ] Team enablement plan includes training and documentation

## Usage Analytics

**Privacy-Preserving Telemetry:**
- Command invocations logged to `.claude-telemetry/growth/metrics-setup.log`
- Tracked data: timestamp, session_id (hashed), completion_status, execution_time
- NO user data, business metrics, or command outputs are stored
- Data used solely for validation demand assessment

**Log Format:**
```json
{
  "timestamp": "2025-10-09T00:35:20Z",
  "command": "growth:metrics-setup",
  "session_id": "sha256_hash",
  "status": "completed",
  "execution_time_minutes": 26,
  "phases_completed": 4
}
```

## Common Issues and Solutions

**Issue:** Stakeholders disagree on North Star metric
**Solution:** Agent facilitates decision framework based on predictive validity (correlation with revenue/retention), actionability (team can influence), and alignment (all teams contribute). Present data supporting each candidate metric.
**Prevention:** Involve key stakeholders early. North Star should unite teams, not divide them.

**Issue:** Product lacks basic analytics instrumentation
**Solution:** Phase 2 includes comprehensive instrumentation plan. Prioritize foundational tracking (user identity, core actions, conversion events) before advanced analytics.
**Prevention:** Implement basic analytics from day one of product development. Retrofitting is costly and loses historical data.

**Issue:** Budget constraints for analytics tools (Amplitude, Mixpanel, Heap)
**Solution:** Agent will recommend open-source alternatives (PostHog, Metabase, Plausible) or DIY stack (PostgreSQL + Metabase + custom event tracking).
**Prevention:** Clarify budget upfront. Quality analytics can be built with $0-500/month budget for early-stage products.

**Issue:** Analytics complexity overwhelming for team
**Solution:** Phase 4 focuses on simple dashboards and gradual enablement. Start with 3-5 key metrics, expand as team gains analytics fluency.
**Prevention:** Prioritize simplicity over comprehensiveness. Most teams only need 10-15 metrics to be data-driven.

## Related Commands

- **`growth:conversion-audit`**: Requires metrics setup for funnel tracking and optimization measurement
- **`growth:retention-playbook`**: Depends on cohort analytics and retention metric tracking
- **`growth:viral-loop`**: Needs referral attribution and viral coefficient measurement
- **`growth:experiment-design`**: Requires A/B testing framework and statistical significance calculation
- **`development:database-design`**: Data warehouse schema design for analytics storage

## Notes

**North Star Metric Examples by Business Model:**
- **SaaS**: Weekly Active Users (WAU), Feature Adoption Rate, Customer Health Score
- **E-commerce**: Purchases per Month, Customer Lifetime Value (LTV)
- **Marketplace**: Gross Merchandise Volume (GMV), Successful Transactions
- **Social Network**: Daily Active Users (DAU), Content Created per User
- **Content/Media**: Time Spent, Content Consumption, Engaged Readers
- **Freemium**: Paid Conversion Rate, Revenue per User

**Growth Model Framework (Example - SaaS):**
```
North Star: Weekly Active Companies

Input Metrics:
1. Acquisition: New Signups per Week
2. Activation: % Completing Onboarding
3. Engagement: Features Used per Session
4. Retention: % Active Week-over-Week
5. Referral: Invites Sent per User

Growth Equation:
WAC = (New Signups × Activation Rate × Retention Rate) + (Referrals × Activation × Retention)
```

**Analytics Tech Stack Tiers:**

**Tier 1 - Enterprise ($10K+/year):**
- Product Analytics: Amplitude, Mixpanel, Heap
- Data Warehouse: Snowflake, BigQuery, Redshift
- Visualization: Looker, Tableau, Mode

**Tier 2 - Growth Stage ($1K-5K/year):**
- Product Analytics: PostHog, Pendo, Matomo
- Data Warehouse: PostgreSQL, ClickHouse
- Visualization: Metabase, Redash, Superset

**Tier 3 - Bootstrap ($0-500/year):**
- Product Analytics: Plausible, Umami, Custom Events
- Data Warehouse: PostgreSQL, SQLite
- Visualization: Metabase (self-hosted), Grafana

**Event Taxonomy Best Practices:**
1. **Naming Convention**: verb_noun format (e.g., `clicked_signup_button`, `completed_onboarding`)
2. **Event Properties**: Include context (user_id, timestamp, source, device, A/B test variant)
3. **Categorization**: Group events by domain (authentication, content, payment, social)
4. **Versioning**: Include schema version for backward compatibility
5. **Validation**: Enforce required properties and data types

**Dashboard Hierarchy:**

**Executive Dashboard (Weekly Review):**
- North Star metric with trend
- Growth rate (week-over-week, month-over-month)
- Key input metrics summary
- Guardrail metrics status
- Top wins and risks

**Team Dashboard (Daily/Weekly):**
- Team-specific input metrics
- Funnel conversion rates
- Feature adoption metrics
- A/B test results
- User segments performance

**Individual Dashboard (Self-Service):**
- Custom queries and analysis
- Cohort retention curves
- User behavior flows
- Segmentation deep-dives

**Critical Metrics by Growth Stage:**

**Early Stage (PMF Validation):**
- Retention curves (D1, D7, D30)
- Activation rate (% reaching "aha moment")
- Usage frequency (sessions per user)
- Qualitative feedback sentiment

**Growth Stage (Scaling):**
- North Star metric growth rate
- Customer acquisition cost (CAC)
- Conversion funnel metrics
- Viral coefficient (K-factor)
- Monthly recurring revenue (MRR)

**Mature Stage (Optimization):**
- Customer lifetime value (LTV)
- LTV:CAC ratio (target > 3:1)
- Net revenue retention (NRR)
- Payback period (target < 12 months)
- Market share metrics

**Quick Wins for Metrics Setup:**
1. Implement user identity tracking across all platforms (Day 1)
2. Track 5 core conversion events (signup, activation, key features)
3. Create simple weekly metrics email for leadership
4. Set up basic cohort retention dashboard
5. Document all tracking in shared event dictionary

**Cost Consideration:**
Investing 10-15% of engineering time in analytics infrastructure typically returns 2-5x through better decision-making, faster experiment velocity, and reduced waste on low-impact initiatives. Metrics debt compounds like technical debt - address early.
