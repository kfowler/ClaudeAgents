---
name: growth:conversion-audit
description: Landing page and funnel optimization combining performance analysis, conversion rate optimization, and A/B testing strategy to maximize visitor-to-customer conversion rates
category: growth
---

# Growth Command: Conversion Audit

## Overview

This command orchestrates a comprehensive conversion rate optimization (CRO) audit of your landing pages and user funnels by analyzing technical performance, user experience friction points, and designing data-driven experiments to increase conversion rates. Ideal for product launches, marketing campaigns, or existing products with conversion rate challenges.

**What this accomplishes:**
- Complete landing page performance and UX audit
- Funnel analysis identifying drop-off points and friction
- Prioritized conversion optimization experiments
- Implementation-ready A/B test specifications

**When to use:**
- Launching new product landing pages or marketing campaigns
- Low conversion rates on existing funnels (below industry benchmarks)
- Post-traffic acquisition to maximize ROI from paid/organic traffic
- Pre-campaign optimization to ensure maximum conversion efficiency

**Expected execution time:** 20-30 minutes

## Prerequisites

- Live or staging URL of landing page(s) to audit
- Access to analytics data (Google Analytics, Mixpanel, etc.) if available
- Current conversion rate baseline (if known)
- Target audience and conversion goals defined

## Multi-Agent Orchestration Strategy

### **Phase 1: Technical Performance Analysis**
Deploy `frontend-performance-specialist` to:
- Audit Core Web Vitals (LCP, FID, CLS) impact on conversion
- Analyze page load performance and rendering bottlenecks
- Identify mobile responsiveness and cross-device issues
- Evaluate JavaScript bundle size and loading strategy
- Assess image optimization and asset delivery performance
- Validate accessibility barriers that reduce conversion
- Generate performance optimization priority list

**Why this agent:** Page speed is directly correlated with conversion rates (1-second delay = 7% reduction in conversions). Technical performance issues must be identified first as they compound all other optimization efforts.

**Deliverable:** Technical performance report with prioritized fixes and estimated conversion impact (e.g., "Fix LCP from 4.2s to 2.5s = estimated +8-12% conversion lift").

### **Phase 2: Conversion Funnel Analysis**
Engage `product-manager` to:
- Map complete user journey from landing to conversion
- Identify friction points, drop-off stages, and user confusion
- Analyze form fields, CTAs, value proposition clarity
- Evaluate trust signals, social proof, and credibility elements
- Assess mobile vs desktop conversion rate disparities
- Benchmark against industry conversion rate standards
- Create funnel optimization hypothesis backlog

**Why this agent:** Product managers specialize in user journey optimization, metrics analysis, and understanding user psychology. They identify behavioral barriers that prevent conversion beyond technical issues.

**Deliverable:** Conversion funnel map with drop-off analysis, friction point heatmap, and prioritized UX improvement recommendations with expected impact.

### **Phase 3: A/B Testing Strategy**
Use `product-manager` to:
- Design high-impact A/B test experiments based on Phase 1-2 findings
- Prioritize tests using ICE framework (Impact × Confidence × Ease)
- Define success metrics, sample size, and test duration requirements
- Create detailed test specifications with variants
- Establish statistical significance thresholds
- Design rollout and measurement plan
- Document learnings capture and iteration framework

**Why this agent:** Rigorous experimentation design prevents false positives and ensures optimization decisions are data-driven with measurable business impact.

**Deliverable:** Top 5 prioritized A/B test specifications with implementation details, expected impact, success metrics, and execution timeline.

### **Phase 4: Implementation Roadmap**
Deploy `product-strategist` to:
- Create phased implementation roadmap (quick wins first)
- Estimate conversion rate improvement potential (conservative, expected, optimistic)
- Calculate ROI for optimization efforts vs traffic acquisition
- Define measurement framework and success criteria
- Create stakeholder communication plan for optimization results
- Establish ongoing optimization process and team ownership

**Why this agent:** Strategic planning ensures optimization efforts align with business objectives, resources are allocated efficiently, and results are tracked against clear success metrics.

**Deliverable:** 30-60-90 day conversion optimization roadmap with projected conversion rate improvements, resource requirements, and measurement framework.

## Execution Flow

```
Phase 1: frontend-performance-specialist
  ↓ (Technical performance audit)
Phase 2: product-manager
  ↓ (Funnel analysis + friction identification)
Phase 3: product-manager
  ↓ (A/B testing strategy design)
Phase 4: product-strategist
  ↓ (Implementation roadmap + ROI projection)
Final Deliverables
```

## Expected Deliverables

- **Technical Performance Report**: Core Web Vitals analysis, optimization priority list, estimated conversion impact of fixes
- **Conversion Funnel Analysis**: Complete user journey map, drop-off analysis, friction point identification, benchmark comparison
- **A/B Test Portfolio**: Top 5 prioritized experiments with detailed specifications, success metrics, and implementation requirements
- **Implementation Roadmap**: 30-60-90 day execution plan with projected conversion improvements, resource allocation, and measurement framework
- **Conversion Metrics Dashboard**: Recommended tracking setup and KPIs for ongoing optimization

## Success Criteria

- [ ] All Core Web Vitals in "Good" range (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] Conversion funnel mapped with drop-off rates quantified at each stage
- [ ] At least 5 high-confidence A/B test experiments designed
- [ ] 30-60-90 day roadmap with clear ownership and success metrics
- [ ] Conservative conversion rate improvement projection > 15%
- [ ] Quick wins identified that can be implemented within 1 week

## Usage Analytics

**Privacy-Preserving Telemetry:**
- Command invocations logged to `.claude-telemetry/growth/conversion-audit.log`
- Tracked data: timestamp, session_id (hashed), completion_status, execution_time
- NO user data, URLs, or command outputs are stored
- Data used solely for validation demand assessment

**Log Format:**
```json
{
  "timestamp": "2025-10-09T00:20:15Z",
  "command": "growth:conversion-audit",
  "session_id": "sha256_hash",
  "status": "completed",
  "execution_time_minutes": 24,
  "phases_completed": 4
}
```

## Common Issues and Solutions

**Issue:** No analytics data available for funnel analysis
**Solution:** Agent will use heuristic analysis based on industry benchmarks and best practices. Recommend implementing analytics before A/B testing.
**Prevention:** Set up basic analytics (Google Analytics, Plausible, or similar) before running audit.

**Issue:** Landing page is part of larger application with shared components
**Solution:** Focus audit on conversion-critical pages and isolated funnel paths. Provide implementation guidance that respects shared component architecture.
**Prevention:** Clearly define audit scope and page URLs upfront.

**Issue:** Conversion rate already high (>10% for B2B, >5% for e-commerce)
**Solution:** Shift focus to micro-conversions, user engagement quality, and customer lifetime value optimization rather than top-of-funnel conversion.
**Prevention:** Provide current conversion rate and business context when invoking command.

## Related Commands

- **`growth:retention-playbook`**: Follow-up after conversion optimization to improve user engagement and reduce churn
- **`growth:metrics-setup`**: Establish comprehensive analytics before running conversion audit for better data-driven insights
- **`growth:experiment-design`**: Deep-dive on specific A/B test implementation after identifying opportunities
- **`quality:performance-optimization`**: Technical implementation of performance improvements identified in Phase 1
- **`quality:production-readiness`**: Validate optimizations before deployment to production

## Notes

**Industry Conversion Rate Benchmarks:**
- SaaS Landing Pages: 2-5% (visitor to trial signup)
- E-commerce Product Pages: 2-4% (visitor to purchase)
- B2B Lead Generation: 1-3% (visitor to qualified lead)
- Mobile App Landing Pages: 0.5-2% (visitor to install)

**Performance Impact Studies:**
- 1-second page load delay = 7% reduction in conversions (Akamai)
- 53% of mobile users abandon pages that take >3 seconds to load (Google)
- Pages loading in 0-2 seconds have highest conversion rates (Portent)

**Quick Wins to Prioritize:**
1. Above-the-fold load time optimization
2. Mobile responsiveness fixes
3. CTA button clarity and visibility
4. Form field reduction (each field removed = +10% conversion)
5. Trust signal addition (testimonials, security badges, guarantees)

**Cost Consideration:**
Conversion rate optimization typically delivers 5-10x ROI compared to increasing traffic volume, making it the most cost-effective growth lever for existing traffic sources.
