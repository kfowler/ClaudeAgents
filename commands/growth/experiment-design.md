---
name: growth:experiment-design
description: A/B testing strategy and experiment prioritization combining hypothesis generation, statistical design, implementation planning, and learning frameworks to maximize growth velocity through rapid experimentation
category: growth
---

# Growth Command: Experiment Design

## Overview

This command orchestrates the design of a comprehensive experimentation program by generating high-impact growth hypotheses, prioritizing experiments using rigorous frameworks, designing statistically valid A/B tests, planning technical implementation, and establishing learning systems that compound velocity over time.

**What this accomplishes:**
- Prioritized growth experiment backlog (30-50 hypotheses)
- Top 10 A/B test specifications with detailed implementation plans
- Statistical design ensuring valid, actionable results
- Experimentation infrastructure and measurement framework
- Learning system to capture and apply insights

**When to use:**
- Sufficient traffic for A/B testing (typically 1,000+ weekly active users)
- Ready to systematically optimize growth metrics
- Need to validate growth initiatives before full investment
- Building culture of experimentation and data-driven decisions
- Plateaued growth seeking new optimization levers

**Expected execution time:** 25-35 minutes

## Prerequisites

- Product with measurable conversion or engagement metrics
- Sufficient traffic volume for statistical significance (1K+ WAU minimum)
- Analytics infrastructure to measure experiment results
- Technical capability to implement A/B testing framework
- Organizational commitment to data-driven decision-making

## Multi-Agent Orchestration Strategy

### **Phase 1: Hypothesis Generation & Analysis**
Deploy `product-manager` to:
- Analyze growth funnel to identify optimization opportunities
- Generate 30-50 experiment hypotheses across AARRR framework
- Map hypotheses to growth model and North Star metric
- Identify quick wins vs long-term strategic bets
- Research successful experiments from similar products
- Apply psychological principles (urgency, social proof, friction reduction)
- Create hypothesis canvas for each experiment
- Categorize by growth lever (acquisition, activation, retention, referral, revenue)

**Why this agent:** Product managers excel at identifying growth opportunities through data analysis, competitive research, and understanding user psychology. They generate diverse, high-quality hypotheses.

**Deliverable:** Hypothesis backlog (30-50 experiments) with expected impact, confidence level, implementation effort, and categorization by growth lever.

### **Phase 2: Experiment Prioritization Framework**
Engage `product-strategist` to:
- Apply ICE scoring framework (Impact × Confidence × Ease)
- Validate hypotheses against user research and qualitative feedback
- Assess technical feasibility and implementation complexity
- Evaluate strategic alignment with product vision
- Consider sequencing dependencies and experiment order
- Balance quick wins with long-term strategic experiments
- Create quarterly experiment roadmap with themes
- Define success criteria and decision-making thresholds

**Why this agent:** Strategic prioritization requires balancing short-term wins with long-term value, understanding organizational constraints, and aligning experiments with business strategy.

**Deliverable:** Prioritized experiment backlog with ICE scores, quarterly roadmap, strategic rationale, and clear success criteria for each experiment.

### **Phase 3: Statistical Design & Methodology**
Use `data-engineer` to:
- Design statistical framework for experiment validity
- Calculate required sample sizes for statistical power (80%+)
- Define primary and secondary metrics for each experiment
- Establish statistical significance thresholds (typically p < 0.05)
- Plan for multiple testing correction if running concurrent experiments
- Design guardrail metrics to prevent harmful optimizations
- Create analysis plan including segmentation analysis
- Specify experiment duration and early stopping criteria

**Why this agent:** Rigorous statistical design prevents false positives, underpowered experiments, and misleading results. Data engineers ensure experiments produce valid, actionable insights.

**Deliverable:** Statistical design specifications including sample size calculations, significance thresholds, primary/secondary metrics, guardrails, and analysis methodology.

### **Phase 4: Technical Implementation Architecture**
Deploy `backend-api-engineer` to:
- Design A/B testing infrastructure (feature flags, variant assignment)
- Plan user bucketing and randomization strategy
- Create experiment tracking and data collection system
- Design analytics integration for metric calculation
- Plan technical implementation for top 10 experiments
- Specify API contracts and frontend integration points
- Design experiment management dashboard
- Create quality assurance and validation procedures

**Why this agent:** A/B testing infrastructure requires careful technical design for accurate variant assignment, consistent user experience, and reliable data collection. Backend engineers build robust experimentation systems.

**Deliverable:** A/B testing infrastructure design with variant assignment logic, tracking specification, implementation guides for top 10 experiments, and QA procedures.

### **Phase 5: Learning System & Velocity Optimization**
Use `product-manager` to:
- Design experiment review and learning capture process
- Create experiment documentation template and repository
- Establish velocity metrics (experiments shipped per quarter)
- Plan team rituals (weekly experiment reviews, monthly retrospectives)
- Design decision-making framework (ship, iterate, kill, scale)
- Create knowledge sharing system for cross-team learning
- Define experiment success patterns and failure modes
- Plan for increasing experiment velocity over time

**Why this agent:** Experimentation value compounds through organizational learning. Product managers design processes that capture insights, share knowledge, and accelerate velocity.

**Deliverable:** Learning system design with documentation templates, review processes, velocity metrics, team rituals, and knowledge management framework.

## Execution Flow

```
Phase 1: product-manager
  ↓ (Hypothesis generation)
Phase 2: product-strategist
  ↓ (Prioritization + roadmap)
Phase 3: data-engineer
  ↓ (Statistical design)
Phase 4: backend-api-engineer
  ↓ (Technical implementation)
Phase 5: product-manager
  ↓ (Learning system)
Final Deliverables
```

## Expected Deliverables

- **Hypothesis Backlog**: 30-50 experiments with impact/confidence/ease scores, expected results, and categorization
- **Prioritized Roadmap**: Top 10 experiments with quarterly themes, strategic rationale, and success criteria
- **Statistical Design**: Sample size calculations, significance thresholds, metric definitions, analysis plans
- **Technical Specifications**: A/B testing infrastructure design, implementation guides, tracking system
- **Learning Framework**: Documentation templates, review processes, velocity metrics, knowledge sharing system

## Success Criteria

- [ ] 30+ experiment hypotheses generated across AARRR framework
- [ ] All hypotheses scored using ICE framework (Impact × Confidence × Ease)
- [ ] Top 10 experiments prioritized with clear success criteria
- [ ] Statistical design ensures 80%+ power and valid significance testing
- [ ] Sample size requirements calculated for each experiment
- [ ] A/B testing infrastructure designed with variant assignment logic
- [ ] Implementation guides created for top 5 experiments
- [ ] Learning system designed with documentation and review processes
- [ ] Experiment velocity target set (e.g., 2-4 experiments per month)

## Usage Analytics

**Privacy-Preserving Telemetry:**
- Command invocations logged to `.claude-telemetry/growth/experiment-design.log`
- Tracked data: timestamp, session_id (hashed), completion_status, execution_time
- NO user data, experiment details, or command outputs are stored
- Data used solely for validation demand assessment

**Log Format:**
```json
{
  "timestamp": "2025-10-09T00:40:15Z",
  "command": "growth:experiment-design",
  "session_id": "sha256_hash",
  "status": "completed",
  "execution_time_minutes": 29,
  "phases_completed": 5
}
```

## Common Issues and Solutions

**Issue:** Insufficient traffic for statistical significance
**Solution:** Agent will recommend higher-impact changes (larger effect sizes), longer experiment durations, or sequential testing approach. May suggest focusing on qualitative user research until traffic scales.
**Prevention:** Minimum 1,000 weekly conversions recommended for standard A/B testing. Use traffic volume to determine experiment scope.

**Issue:** Multiple concurrent experiments causing metric interference
**Solution:** Phase 3 includes statistical correction methods (Bonferroni, False Discovery Rate control). Agent will recommend isolation strategies or sequential testing order.
**Prevention:** Limit concurrent experiments to different parts of the user journey or use orthogonal test designs.

**Issue:** Team lacks A/B testing infrastructure
**Solution:** Phase 4 provides complete implementation plan. Can start with simple cookie-based bucketing and manual variant assignment before building sophisticated infrastructure.
**Prevention:** Implement basic feature flag system early (e.g., LaunchDarkly, Unleash, or custom). Start simple, iterate toward sophistication.

**Issue:** Organizational resistance to data-driven decisions
**Solution:** Phase 5 focuses on change management through quick wins, stakeholder communication, and gradual process adoption. Start with low-risk experiments to build confidence.
**Prevention:** Involve stakeholders in hypothesis generation. Frame experiments as risk reduction, not decision abdication.

## Related Commands

- **`growth:metrics-setup`**: Prerequisite for measuring experiment results accurately
- **`growth:conversion-audit`**: Generates specific optimization opportunities for testing
- **`growth:retention-playbook`**: Provides retention-focused experiment ideas
- **`growth:viral-loop`**: Requires experimentation to optimize viral mechanics
- **`development:api-design`**: Technical implementation of experimentation infrastructure

## Notes

**ICE Prioritization Framework:**
```
Score = (Impact × Confidence × Ease) / 3

Impact (1-10): Expected improvement to North Star metric
Confidence (1-10): Likelihood hypothesis is correct
Ease (1-10): Implementation simplicity (inverse of effort)

Example:
- Hypothesis: Reduce signup form from 8 to 4 fields
- Impact: 8 (form friction major barrier)
- Confidence: 9 (proven pattern, user feedback)
- Ease: 10 (simple change)
- ICE Score: (8 × 9 × 10) / 3 = 240 (HIGH PRIORITY)
```

**Statistical Significance Requirements:**
```
For 80% statistical power and 5% significance level:

Minimum Detectable Effect (MDE) based on sample size:
- 1,000 users per variant: 8-10% relative improvement
- 5,000 users per variant: 4-5% relative improvement
- 10,000 users per variant: 2-3% relative improvement
- 50,000 users per variant: 1-2% relative improvement

Rule of thumb: Need ~16,000 users per variant to detect 2% improvement
```

**Experiment Categories (AARRR Framework):**

1. **Acquisition**: Landing page optimization, ad copy testing, referral source tracking
2. **Activation**: Onboarding flow, feature discovery, time-to-value reduction
3. **Retention**: Engagement triggers, notification optimization, habit formation
4. **Referral**: Sharing mechanics, incentive testing, viral loop optimization
5. **Revenue**: Pricing tests, upsell flows, payment optimization

**High-Confidence Experiment Patterns:**

**Friction Reduction:**
- Remove form fields (each field removed = ~10% conversion increase)
- Reduce signup steps (3-step max ideal)
- Offer guest checkout (can increase conversion 20-40%)

**Social Proof:**
- Add testimonials (typically 5-15% lift)
- Display usage statistics ("Join 100,000+ users")
- Show recent activity ("Sarah just signed up")

**Urgency & Scarcity:**
- Limited-time offers (10-30% lift, use ethically)
- Stock indicators ("Only 3 left")
- Countdown timers (controversial, test carefully)

**Value Proposition:**
- Headline testing (can double conversion rates)
- Benefit-focused vs feature-focused copy
- Specificity in claims ("Increase revenue by 23%" vs "Grow revenue")

**Visual Hierarchy:**
- CTA button color, size, positioning (5-20% typical lift)
- Above-the-fold content optimization
- Image vs text emphasis

**Experiment Velocity Benchmarks:**
- **Startups**: 2-4 experiments per month (limited resources)
- **Growth-stage**: 4-8 experiments per month (dedicated growth team)
- **Enterprise**: 10-30+ concurrent experiments (sophisticated infrastructure)

**Learning Compound Effect:**
```
Year 1: 24 experiments × 15% win rate × 5% avg lift = 18% cumulative improvement
Year 2: 36 experiments × 25% win rate × 6% avg lift = 54% improvement (learning compounds)
Year 3: 48 experiments × 35% win rate × 7% avg lift = 117% improvement

Key insight: Experiment velocity and win rate improve with organizational learning
```

**Common Experiment Mistakes:**
1. **Stopping early**: Reaching significance early often regresses to mean
2. **P-hacking**: Running experiments until reaching significance
3. **Ignoring guardrails**: Optimizing conversion while harming retention
4. **Confounding factors**: Seasonality, marketing campaigns, external events
5. **Sample ratio mismatch**: Variant assignment bias indicating implementation bugs

**Quick Wins for Experimentation:**
1. Start with high-traffic, low-risk experiments (CTA button tests)
2. Use qualitative research to generate high-confidence hypotheses
3. Implement 80/20 A/B testing infrastructure (simple before sophisticated)
4. Document all experiments, even failures (learning value)
5. Share wins broadly to build experimentation culture

**Cost Consideration:**
Building experimentation culture typically requires 1-2 engineers + 1 product manager for infrastructure and process. Returns 2-5x through higher growth rates and reduced waste on unvalidated initiatives. Best investment for products with product-market fit ready to scale.
