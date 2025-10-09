---
name: growth:viral-loop
description: Referral program design and viral growth strategy combining behavioral psychology, technical implementation planning, and measurement framework to achieve organic user acquisition through word-of-mouth
category: growth
---

# Growth Command: Viral Loop Design

## Overview

This command orchestrates the design and implementation planning of a viral growth system that turns existing users into acquisition channels through referral programs, social sharing mechanics, and viral loops. Combines behavioral psychology, incentive design, technical architecture, and measurement frameworks to create sustainable viral growth.

**What this accomplishes:**
- Complete viral loop strategy with mechanics and incentive design
- Technical implementation roadmap for referral tracking and rewards
- Viral coefficient calculation and growth modeling
- Launch plan with fraud prevention and optimization framework

**When to use:**
- Building new product with viral growth potential
- Existing product ready to add referral/sharing features
- Customer acquisition cost (CAC) is too high for unit economics
- Product has natural sharing triggers or network effects
- Seeking sustainable organic growth channel

**Expected execution time:** 25-35 minutes

## Prerequisites

- Product with established product-market fit (PMV minimum)
- User base of at least 100-1000+ active users (for testing)
- Understanding of target user motivations and behaviors
- Budget for incentive costs (if monetary rewards used)
- Technical capability to implement tracking and attribution

## Multi-Agent Orchestration Strategy

### **Phase 1: Viral Mechanics Strategy**
Deploy `product-strategist` to:
- Analyze product for natural viral potential and sharing triggers
- Design viral loop mechanics aligned with user psychology
- Create incentive structure (monetary, product credits, status/gamification)
- Map viral loops: referrer journey, referee journey, activation triggers
- Benchmark against successful viral programs (Dropbox, Airbnb, Uber)
- Calculate target viral coefficient (K-factor) for exponential growth
- Design fraud prevention strategy and abuse scenarios
- Define success metrics and viral loop health indicators

**Why this agent:** Viral growth requires deep understanding of user psychology, market dynamics, and strategic incentive design. Product strategists excel at designing systems that align user incentives with business growth objectives.

**Deliverable:** Complete viral loop strategy document with mechanics, incentive structure, user journey maps, K-factor targets, and fraud prevention approach.

### **Phase 2: Technical Implementation Architecture**
Engage `backend-api-engineer` to:
- Design referral tracking and attribution system architecture
- Create referral code generation and management system
- Design reward fulfillment and ledger system
- Plan analytics and fraud detection infrastructure
- Specify API endpoints for referral actions and tracking
- Design database schema for referrals, rewards, and attribution
- Create technical integration points for frontend sharing UI
- Plan scalability for viral growth scenarios (10x, 100x user growth)

**Why this agent:** Referral systems require robust backend infrastructure for accurate attribution, reward tracking, and fraud prevention. Backend engineers design scalable, reliable systems that handle viral growth loads.

**Deliverable:** Technical architecture document with database schema, API specifications, referral tracking system design, and implementation estimate (story points/hours).

### **Phase 3: Growth Modeling & Experimentation**
Use `product-manager` to:
- Build viral growth model with conversion rates and time cycles
- Calculate viral coefficient (K = invites sent × conversion rate)
- Model growth scenarios (K=0.5, K=1.0, K=1.5+) over 90 days
- Design A/B testing framework for incentive optimization
- Define measurement framework and key metrics dashboard
- Create experiment backlog for optimizing viral loops
- Establish success criteria and iteration triggers
- Plan cohort analysis for viral vs non-viral user retention

**Why this agent:** Product managers excel at metrics modeling, experimentation design, and data-driven optimization. They create frameworks that turn viral loops into measurable, improvable systems.

**Deliverable:** Viral growth model with projections, A/B test specifications, measurement dashboard requirements, and optimization playbook.

### **Phase 4: Launch Strategy & Rollout Plan**
Deploy `product-strategist` to:
- Create phased rollout plan (beta testing → gradual rollout → full launch)
- Design communication strategy for announcing referral program
- Plan user education and sharing trigger placement
- Establish monitoring and rapid response framework for issues
- Define budget allocation for incentives and target ROI
- Create stakeholder reporting and success communication plan
- Design ongoing optimization process and ownership model
- Plan competitive response and differentiation strategy

**Why this agent:** Successful viral launch requires strategic timing, communication, and risk management. Product strategists orchestrate complex launches that maximize initial momentum while managing risks.

**Deliverable:** 30-60-90 day launch roadmap with rollout phases, budget allocation, communication plan, success metrics, and risk mitigation strategies.

## Execution Flow

```
Phase 1: product-strategist
  ↓ (Viral mechanics + incentive design)
Phase 2: backend-api-engineer
  ↓ (Technical architecture)
Phase 3: product-manager
  ↓ (Growth modeling + experimentation framework)
Phase 4: product-strategist
  ↓ (Launch strategy + rollout plan)
Final Deliverables
```

## Expected Deliverables

- **Viral Loop Strategy**: Complete mechanics design, incentive structure, user journey maps, K-factor targets, fraud prevention approach
- **Technical Architecture**: Database schema, API specifications, referral tracking system, implementation roadmap
- **Growth Model**: Viral coefficient calculations, 90-day growth projections, scenario modeling (K=0.5 to K=1.5+)
- **Measurement Framework**: Key metrics dashboard, A/B testing backlog, success criteria, cohort analysis plan
- **Launch Roadmap**: Phased rollout plan, budget allocation, communication strategy, monitoring framework

## Success Criteria

- [ ] Viral mechanics designed with clear referrer and referee value propositions
- [ ] Incentive structure validated against budget constraints and unit economics
- [ ] Technical architecture supports accurate attribution and fraud prevention
- [ ] Growth model shows path to K-factor > 1.0 (exponential growth)
- [ ] A/B testing framework designed with at least 5 optimization experiments
- [ ] Launch plan includes beta testing phase with success criteria
- [ ] Fraud prevention strategy addresses common abuse scenarios
- [ ] Budget ROI positive within 90 days (referral CAC < organic CAC)

## Usage Analytics

**Privacy-Preserving Telemetry:**
- Command invocations logged to `.claude-telemetry/growth/viral-loop.log`
- Tracked data: timestamp, session_id (hashed), completion_status, execution_time
- NO user data, incentive amounts, or command outputs are stored
- Data used solely for validation demand assessment

**Log Format:**
```json
{
  "timestamp": "2025-10-09T00:25:30Z",
  "command": "growth:viral-loop",
  "session_id": "sha256_hash",
  "status": "completed",
  "execution_time_minutes": 28,
  "phases_completed": 4
}
```

## Common Issues and Solutions

**Issue:** Product doesn't have obvious viral sharing triggers
**Solution:** Agent will identify "manufactured virality" opportunities (e.g., collaborative features, social proof, content creation tools). May recommend building viral features into product roadmap.
**Prevention:** Assess viral potential before running command. Products with network effects, content creation, or social components are best candidates.

**Issue:** Budget constraints prevent meaningful incentives
**Solution:** Focus on non-monetary incentives (product credits, status/gamification, exclusive features, recognition). Design intrinsic viral loops based on product value.
**Prevention:** Define budget constraints upfront. Many successful viral loops use non-cash incentives (Dropbox storage, LinkedIn visibility).

**Issue:** Concerns about referral fraud and abuse
**Solution:** Phase 2 includes comprehensive fraud prevention strategy (verification requirements, velocity limits, manual review triggers, ML-based fraud detection).
**Prevention:** Expect 5-15% fraud/abuse rate. Budget accordingly and prioritize fraud detection in technical architecture.

**Issue:** Viral coefficient below 1.0 (sub-exponential growth)
**Solution:** Even K=0.5-0.8 provides significant CAC reduction. Agent will design optimization experiments to increase K through incentive testing, sharing UI improvements, and conversion optimization.
**Prevention:** Set realistic K-factor goals. Most successful programs achieve K=0.4-0.8, not K>1.0.

## Related Commands

- **`growth:retention-playbook`**: Viral users must be retained to achieve compounding growth; optimize retention alongside acquisition
- **`growth:experiment-design`**: Deep-dive A/B testing for optimizing referral conversion rates and incentive structures
- **`growth:metrics-setup`**: Establish comprehensive analytics for tracking viral loops before launch
- **`development:api-design`**: Detailed API implementation for referral tracking system
- **`quality:security-audit`**: Security review of referral system to prevent fraud and abuse

## Notes

**Viral Coefficient Formula:**
```
K = (invites sent per user) × (conversion rate of invites)
```

**Viral Growth Benchmarks:**
- K < 0.5: Weak viral effect (modest CAC reduction)
- K = 0.5-0.8: Strong viral effect (significant CAC reduction)
- K = 0.8-1.0: Very strong viral effect (approaching exponential growth)
- K > 1.0: Exponential growth (rare, typically temporary)

**Successful Referral Program Examples:**
- **Dropbox**: 500MB storage (referrer) + 500MB (referee) = 60% signup boost, 35% K-factor
- **Airbnb**: $25 travel credit (referrer) + $25 (referee) = 300% growth in user base
- **Uber**: Free ride credits both sides = 50% of rides from referrals at peak
- **PayPal**: $10-20 cash both sides = 7-10% daily growth in early days
- **Tesla**: $1000 discount both sides = 25% of sales from referrals

**Incentive Structure Patterns:**
1. **Two-sided incentives**: Both referrer and referee receive rewards (highest conversion)
2. **Product credits**: Lower cost than cash, higher perceived value
3. **Tiered rewards**: Escalating incentives for multiple referrals
4. **Time-limited offers**: Create urgency and sharing spikes
5. **Non-monetary**: Status, exclusive features, recognition (lowest cost)

**Viral Loop Time Cycles:**
- **Immediate loops**: Sharing during onboarding or activation (fastest growth)
- **Usage-triggered loops**: Sharing during product use (most sustainable)
- **Periodic campaigns**: Time-limited referral bonuses (controllable bursts)

**Critical Success Factors:**
1. **Easy sharing**: 1-click sharing to multiple channels
2. **Clear value**: Obvious benefit for both referrer and referee
3. **Immediate gratification**: Rewards granted quickly, not delayed
4. **Social proof**: Show existing referral success to encourage sharing
5. **Product quality**: Viral loops amplify product experience (good or bad)

**Cost Consideration:**
Referral CAC typically 20-50% of organic CAC, with referred users showing 15-25% higher LTV due to better onboarding and social validation. Budget 10-30% of customer LTV for incentive costs.
