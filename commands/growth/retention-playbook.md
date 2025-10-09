---
name: growth:retention-playbook
description: User retention and engagement optimization through onboarding design, habit formation, churn prediction, and win-back strategies to maximize customer lifetime value
category: growth
---

# Growth Command: Retention Playbook

## Overview

This command orchestrates a comprehensive user retention strategy by analyzing user behavior, designing effective onboarding experiences, creating habit-forming engagement loops, predicting churn, and building win-back systems. Retention is the foundation of sustainable growth - improving retention from 80% to 90% can triple customer lifetime value.

**What this accomplishes:**
- Complete onboarding flow optimization with activation milestones
- Engagement loop design with habit formation triggers
- Churn prediction model and early warning system
- Win-back campaign strategy for at-risk and churned users
- Retention metrics framework and optimization roadmap

**When to use:**
- New product with low user retention (< 40% D7, < 20% D30)
- Existing product with high churn rate impacting growth
- After achieving product-market fit, before scaling acquisition
- When customer acquisition cost (CAC) exceeds customer lifetime value (LTV)
- Building engagement features or redesigning onboarding

**Expected execution time:** 25-35 minutes

## Prerequisites

- User behavior data or ability to implement basic analytics
- Current retention rates (D1, D7, D30) or cohort data if available
- Understanding of core product value and "aha moment"
- List of key product features and user actions
- User feedback or qualitative insights (if available)

## Multi-Agent Orchestration Strategy

### **Phase 1: Retention Analysis & Diagnosis**
Deploy `product-manager` to:
- Analyze current retention curves and cohort behavior
- Identify retention benchmarks for industry/product type
- Diagnose retention issues (onboarding, activation, engagement, value delivery)
- Map user journey from signup to habit formation
- Identify critical activation milestones and "aha moments"
- Analyze feature adoption correlation with retention
- Calculate customer lifetime value (LTV) and retention impact
- Benchmark against industry standards (SaaS, consumer, marketplace)

**Why this agent:** Product managers excel at metrics analysis, user behavior diagnosis, and identifying root causes of retention issues through data-driven investigation.

**Deliverable:** Retention analysis report with current performance, benchmark comparison, issue diagnosis, activation milestone identification, and LTV calculations.

### **Phase 2: Onboarding Flow Optimization**
Engage `product-strategist` to:
- Design optimal onboarding flow to fastest "aha moment"
- Create activation milestone checklist (signup → value realization)
- Design progressive disclosure strategy to prevent overwhelm
- Plan personalization and segmentation for different user types
- Create onboarding gamification and progress indicators
- Design empty state experiences and first-use magic moments
- Map email/notification triggers for onboarding engagement
- Establish success metrics for onboarding optimization

**Why this agent:** Strategic onboarding design requires understanding user psychology, behavior change principles, and product positioning. Product strategists design experiences that align user goals with product value.

**Deliverable:** Comprehensive onboarding redesign with user flow diagrams, activation milestones, personalization strategy, communication plan, and success metrics.

### **Phase 3: Engagement Loop Design**
Use `product-manager` to:
- Design habit-forming engagement loops (trigger → action → reward → investment)
- Create notification strategy for re-engagement without annoyance
- Plan feature introduction sequence for progressive engagement
- Design social/collaborative features to increase switching costs
- Create content/data value accumulation over time (investment)
- Build engagement scoring model to identify power users
- Design weekly/monthly engagement goals and celebrations
- Establish A/B testing framework for engagement optimization

**Why this agent:** Building sustainable engagement requires understanding behavioral psychology, retention metrics, and experimentation frameworks. Product managers create data-driven engagement systems.

**Deliverable:** Engagement playbook with habit loops, notification strategy, engagement scoring model, A/B test backlog, and measurement framework.

### **Phase 4: Churn Prediction & Win-Back Strategy**
Deploy `data-engineer` to:
- Design churn prediction model based on behavioral signals
- Create early warning system for at-risk user identification
- Build user segmentation for personalized interventions
- Design automated win-back campaigns for churned users
- Plan analytics infrastructure for retention monitoring
- Create retention dashboard with leading indicators
- Design feedback loops for continuous improvement
- Establish data pipeline for retention cohort analysis

**Why this agent:** Churn prediction requires data modeling, pipeline design, and analytics infrastructure. Data engineers build scalable systems that identify at-risk users and enable intervention.

**Deliverable:** Churn prediction system specification with behavioral signals, risk scoring model, win-back campaign design, analytics dashboard, and implementation roadmap.

### **Phase 5: Implementation Roadmap**
Use `product-strategist` to:
- Prioritize retention initiatives by impact and effort (ICE framework)
- Create 30-60-90 day implementation roadmap
- Calculate projected retention improvements and LTV impact
- Design measurement framework and success criteria
- Plan resource allocation and team ownership
- Create stakeholder communication and reporting plan
- Establish ongoing optimization process
- Define retention-focused product culture principles

**Why this agent:** Retention optimization requires strategic prioritization, resource planning, and organizational alignment. Product strategists create executable roadmaps with clear business impact.

**Deliverable:** Phased implementation roadmap with prioritized initiatives, projected retention improvements, LTV impact calculations, and measurement framework.

## Execution Flow

```
Phase 1: product-manager
  ↓ (Retention analysis + diagnosis)
Phase 2: product-strategist
  ↓ (Onboarding optimization)
Phase 3: product-manager
  ↓ (Engagement loop design)
Phase 4: data-engineer
  ↓ (Churn prediction + win-back)
Phase 5: product-strategist
  ↓ (Implementation roadmap)
Final Deliverables
```

## Expected Deliverables

- **Retention Analysis**: Current performance metrics, benchmark comparison, issue diagnosis, activation milestones, LTV calculations
- **Onboarding Redesign**: User flow diagrams, activation checklist, personalization strategy, communication plan
- **Engagement Playbook**: Habit loops, notification strategy, engagement scoring, A/B test backlog
- **Churn Prevention System**: Prediction model, early warning system, win-back campaigns, analytics infrastructure
- **Implementation Roadmap**: 30-60-90 day plan with projected retention improvements, priorities, and measurement framework

## Success Criteria

- [ ] Current retention rates quantified (D1, D7, D30, D90)
- [ ] Activation milestones identified with target completion rates
- [ ] Onboarding flow redesigned to reduce time-to-value by 30%+
- [ ] Engagement loops designed with clear trigger-action-reward-investment cycles
- [ ] Churn prediction model specified with behavioral signals and risk scoring
- [ ] Win-back campaigns designed for at-risk and churned user segments
- [ ] 30-60-90 day roadmap with conservative retention improvement > 10 percentage points
- [ ] Measurement framework established with leading indicators

## Usage Analytics

**Privacy-Preserving Telemetry:**
- Command invocations logged to `.claude-telemetry/growth/retention-playbook.log`
- Tracked data: timestamp, session_id (hashed), completion_status, execution_time
- NO user data, retention rates, or command outputs are stored
- Data used solely for validation demand assessment

**Log Format:**
```json
{
  "timestamp": "2025-10-09T00:30:45Z",
  "command": "growth:retention-playbook",
  "session_id": "sha256_hash",
  "status": "completed",
  "execution_time_minutes": 31,
  "phases_completed": 5
}
```

## Common Issues and Solutions

**Issue:** Limited or no user behavior data available
**Solution:** Agent will use industry benchmarks and heuristic analysis. Will prioritize implementing analytics infrastructure in Phase 4 for future optimization.
**Prevention:** Implement basic analytics (user actions, feature usage, session tracking) before running command for data-driven insights.

**Issue:** Product has inherent usage frequency limitations (e.g., tax software used annually)
**Solution:** Focus on annual retention, secondary use cases, value-add features between primary use periods, and building anticipation for next usage cycle.
**Prevention:** Clarify natural usage frequency when invoking command. Retention strategies differ for daily-use vs periodic-use products.

**Issue:** Retention already strong (> 60% D30) with limited improvement opportunities
**Solution:** Shift focus to power user engagement, feature adoption depth, viral loops, and customer expansion (upsell/cross-sell) rather than basic retention.
**Prevention:** Provide current retention metrics upfront. High-retention products may benefit more from other growth commands.

**Issue:** Onboarding redesign conflicts with existing user base expectations
**Solution:** Design separate onboarding flows for new users while preserving existing user experience. Use feature flags for gradual rollout and A/B testing.
**Prevention:** Consider existing user impact. Plan phased rollout with monitoring for existing user disruption.

## Related Commands

- **`growth:metrics-setup`**: Establish retention analytics before running playbook for data-driven optimization
- **`growth:conversion-audit`**: Optimize activation conversion within onboarding flow
- **`growth:experiment-design`**: A/B test onboarding and engagement features
- **`growth:viral-loop`**: Retained users are essential for sustainable viral growth
- **`development:database-design`**: Design data models for engagement tracking and churn prediction

## Notes

**Retention Benchmarks by Product Type:**
- **SaaS (B2B)**: D1 70-80%, D7 50-60%, D30 40-50%, Annual 80-90%
- **SaaS (B2C)**: D1 40-60%, D7 25-35%, D30 15-25%, Annual 40-60%
- **Consumer Social**: D1 60-70%, D7 40-50%, D30 25-35%
- **E-commerce**: D30 30-40%, Annual 60-70%
- **Mobile Games**: D1 40-60%, D7 20-30%, D30 10-15%

**Retention Improvement Impact on LTV:**
```
If retention increases from 80% to 90% monthly:
- LTV = ARPU / churn rate
- Before: $100 / 0.20 = $500 LTV
- After: $100 / 0.10 = $1,000 LTV
- Result: 100% increase in LTV from 10-point retention improvement
```

**Critical Activation Milestones (Examples):**
- **Slack**: Team sends 2,000 messages (correlates with 93% retention)
- **Facebook**: 7 friends in 10 days (early retention predictor)
- **Dropbox**: 1 file in 1 folder on 1 device
- **Twitter**: Follow 30 accounts (drives feed engagement)
- **LinkedIn**: 5 connections and complete profile

**Engagement Loop Framework (Hook Model):**
1. **Trigger**: External (notification, email) or Internal (emotion, routine)
2. **Action**: Simplest behavior to receive reward
3. **Variable Reward**: Unpredictable positive reinforcement
4. **Investment**: User adds value that increases future engagement

**Win-Back Campaign Timing:**
- **At-Risk Users**: 7-14 days of inactivity (early intervention)
- **Recently Churned**: 30-60 days after last activity (highest recovery rate)
- **Long-Term Churned**: 90+ days (lowest recovery, but cheap re-acquisition)

**Notification Best Practices:**
- Limit to 1-2 notifications per week to avoid annoyance
- Personalize based on user behavior and preferences
- Provide immediate opt-out to build trust
- Focus on value delivery, not engagement manipulation
- Test send time optimization for different user segments

**Quick Wins for Retention:**
1. Reduce onboarding steps to reach "aha moment" (< 5 minutes ideal)
2. Send 2-3 onboarding emails in first week (not daily)
3. Add progress indicators to show onboarding completion
4. Celebrate first success moments with positive reinforcement
5. Implement simple engagement scoring to identify at-risk users

**Cost Consideration:**
Improving retention is 5-25x more cost-effective than acquiring new users. A 10-percentage-point retention improvement can reduce growth budget needs by 30-50% while achieving same revenue targets.
