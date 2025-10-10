# Growth Commands - Validation Experiment

## Overview

This directory contains 5 growth-focused commands designed as a **demand validation experiment** before investing in a dedicated growth agent. These commands orchestrate existing agents to deliver growth value while measuring actual usage to inform future development priorities.

## Validation Hypothesis

**Question:** Is there sufficient demand for growth-specific functionality to justify building a dedicated growth-engineer agent?

**Approach:** Build 5 high-value commands (1-2 hours each) that solve real growth problems using existing agents. Track usage for 60-90 days to validate demand.

**Success Criteria:**
- **Strong Demand**: 20+ invocations across 10+ unique users → Build dedicated growth agent
- **Moderate Demand**: 10-20 invocations → Iterate on command design, extend validation
- **Low Demand**: <10 invocations → Deprioritize growth features, focus on other domains

## Commands

### 1. `/growth:conversion-audit`
**Purpose:** Landing page and funnel optimization to maximize conversion rates

**Value Proposition:** Identifies technical performance issues, UX friction, and A/B testing opportunities that typically deliver 15-30% conversion improvements.

**Orchestration:**
- `frontend-performance-specialist`: Technical performance audit
- `product-manager`: Funnel analysis and experimentation design
- `product-strategist`: Implementation roadmap and ROI projection

**Expected Usage:** Product teams launching new features, marketing teams optimizing campaigns, early-stage startups improving activation rates.

---

### 2. `/growth:viral-loop`
**Purpose:** Referral program design and viral growth mechanics

**Value Proposition:** Designs complete viral loop systems that reduce customer acquisition cost by 50-80% through organic word-of-mouth growth.

**Orchestration:**
- `product-strategist`: Viral mechanics and incentive design
- `backend-api-engineer`: Referral tracking and reward system architecture
- `product-manager`: Growth modeling and experimentation framework

**Expected Usage:** Products with natural sharing triggers, high CAC problems, or network effect potential.

---

### 3. `/growth:retention-playbook`
**Purpose:** User retention and engagement optimization

**Value Proposition:** Improving retention by 10 percentage points can double or triple customer lifetime value. Designs onboarding, engagement loops, and churn prevention systems.

**Orchestration:**
- `product-manager`: Retention analysis and engagement loop design
- `product-strategist`: Onboarding flow optimization
- `data-engineer`: Churn prediction and analytics infrastructure

**Expected Usage:** Products with retention challenges, high churn rates, or preparing to scale acquisition.

---

### 4. `/growth:metrics-setup`
**Purpose:** North Star metric identification and analytics infrastructure

**Value Proposition:** Establishes data-driven decision-making foundation. Proper metrics setup enables all other growth initiatives to be measured and optimized.

**Orchestration:**
- `product-strategist`: North Star metric and growth model design
- `data-engineer`: Analytics infrastructure architecture
- `product-manager`: Dashboard design and measurement framework

**Expected Usage:** Early-stage products before scaling, teams transitioning to data-driven growth, pre-fundraising analytics setup.

---

### 5. `/growth:experiment-design`
**Purpose:** A/B testing strategy and experiment prioritization

**Value Proposition:** Systematic experimentation typically delivers 2-5x ROI vs ad-hoc optimization. Creates prioritized experiment backlog with statistical rigor.

**Orchestration:**
- `product-manager`: Hypothesis generation and prioritization
- `product-strategist`: Strategic alignment and roadmap
- `data-engineer`: Statistical design and significance calculation
- `backend-api-engineer`: A/B testing infrastructure

**Expected Usage:** Products with sufficient traffic (1K+ weekly active users) ready to optimize growth through experimentation.

## Usage Tracking & Privacy

### What We Track

All commands log **privacy-preserving telemetry** to validate demand:

```json
{
  "timestamp": "2025-10-09T00:45:00Z",
  "command": "growth:conversion-audit",
  "session_id": "sha256_hash",
  "status": "completed|failed|partial",
  "execution_time_minutes": 24,
  "phases_completed": 4
}
```

**Privacy Guarantees:**
- ✅ Command invocation counts and timestamps
- ✅ Session ID (SHA-256 hashed, non-reversible)
- ✅ Completion status and execution time
- ❌ NO user identity, email, or personal information
- ❌ NO command arguments (URLs, product names, etc.)
- ❌ NO command outputs or analysis results
- ❌ NO business metrics or sensitive data

### Data Storage

- **Location**: `.claude-telemetry/growth/` (gitignored)
- **Format**: Append-only JSON logs, one file per command
- **Retention**: 90 days (auto-deleted afterward)
- **Access**: Local only, never transmitted externally
- **Purpose**: Validation experiment only, deleted after decision

### Telemetry Implementation

Each command includes standardized telemetry logging:

```bash
# At command start
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"command\":\"growth:conversion-audit\",\"session_id\":\"$(echo $USER-$$ | sha256sum | cut -d' ' -f1)\",\"status\":\"started\"}" >> .claude-telemetry/growth/conversion-audit.log

# At command completion
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"command\":\"growth:conversion-audit\",\"session_id\":\"$(echo $USER-$$ | sha256sum | cut -d' ' -f1)\",\"status\":\"completed\",\"execution_time_minutes\":24,\"phases_completed\":4}" >> .claude-telemetry/growth/conversion-audit.log
```

## Validation Timeline

### Phase 1: Launch (Weeks 1-2)
- Announce growth commands to user base
- Share use cases and value propositions
- Monitor initial adoption and gather feedback

### Phase 2: Iteration (Weeks 3-8)
- Analyze usage patterns and completion rates
- Gather qualitative feedback from users
- Iterate on command design based on learnings
- Add additional commands if specific patterns emerge

### Phase 3: Decision (Weeks 9-12)
- Review usage data against success criteria
- Analyze completion rates and phase drop-offs
- Survey users who tried commands
- Make build/no-build decision on growth agent

### Expected Outcomes

**Build Growth Agent If:**
- 20+ total command invocations
- 10+ unique users
- 70%+ completion rate (not abandoned mid-execution)
- Strong qualitative feedback requesting more growth features
- Clear usage patterns showing unmet needs

**Iterate Commands If:**
- 10-20 invocations but low completion rate → UX/complexity issues
- Usage concentrated in 1-2 commands → Focus on those, deprecate others
- Feedback indicates missing functionality → Add targeted commands

**Deprioritize If:**
- <10 invocations after 90 days
- High abandonment rate suggesting wrong problem/solution fit
- Users prefer general-purpose agents over specialized commands
- Feedback indicates value misalignment

## Competitive Advantages of Command Approach

### Why Commands Before Agent?

1. **Lower Investment**: 8-10 hours total vs 40+ hours for full agent
2. **Faster Validation**: Ship in 1 week vs 4-6 weeks for agent development
3. **Lower Risk**: Easy to deprecate if demand doesn't materialize
4. **Clearer Signal**: Usage data shows *which* growth problems users care about
5. **Iterative**: Can adjust scope based on real usage patterns

### What We Learn

Command-level tracking reveals:
- **Which growth levers matter most** (conversion, retention, viral, metrics, experiments)
- **Which agent combinations provide value** (validates orchestration patterns)
- **Completion rates by phase** (identifies complexity/value drop-off points)
- **Usage frequency** (one-time setup vs recurring optimization)
- **User segments** (early-stage, growth-stage, enterprise)

This data informs **what a growth agent should focus on** if we build one.

## Integration with Existing Agents

These commands leverage existing agents' expertise:

- **`product-strategist`**: Strategic planning, market positioning, viral mechanics
- **`product-manager`**: Metrics, experimentation, funnel analysis, retention
- **`data-engineer`**: Analytics infrastructure, data modeling, statistical design
- **`frontend-performance-specialist`**: Conversion optimization through performance
- **`backend-api-engineer`**: Referral systems, A/B testing infrastructure

**Key Insight:** If growth commands show strong usage, it validates need for a **growth-specialized orchestrator** that knows how to combine these agents for growth outcomes.

## Future Growth Agent Scope (If Validated)

Based on validation results, a dedicated growth-engineer agent would:

### Core Capabilities
- Growth model design and metric selection
- Funnel analysis and conversion rate optimization
- Retention and engagement strategy
- Viral loop and referral program design
- Experimentation framework and A/B testing
- Analytics infrastructure for growth measurement

### Differentiators from Existing Agents
- **vs product-manager**: Growth-specific frameworks (AARRR, viral loops, retention curves)
- **vs product-strategist**: Tactical growth execution, not just high-level strategy
- **vs data-engineer**: Growth analytics focus (cohorts, funnels, experiments) vs data pipelines
- **vs frontend-performance-specialist**: Conversion psychology and behavioral optimization

### Agent Boundaries
A growth agent would **orchestrate** specialists but have deep expertise in:
- Growth frameworks (AARRR, ICE scoring, North Star metrics)
- Behavioral psychology and conversion optimization
- Viral mechanics and network effects
- Retention science and habit formation
- Statistical experimentation and learning systems

## Command Design Principles

Each growth command follows these principles:

### 1. Quick to Build (1-2 hours each)
- Leverage existing agents (no new agent development)
- Focus on orchestration, not custom logic
- Reuse proven agent capabilities

### 2. Real Value Delivery (<30 min execution)
- Solve complete problems, not partial ones
- Deliver actionable outputs (specs, roadmaps, analyses)
- Provide clear next steps for implementation

### 3. Measurable Outcomes
- Privacy-preserving usage tracking
- Completion rate monitoring
- Phase-level drop-off analysis

### 4. Clear Use Cases
- Specific problem statements
- Target user personas
- Prerequisites and constraints

### 5. Professional Quality
- Comprehensive documentation
- Industry benchmarks and best practices
- Real-world examples and templates

## Success Stories We're Looking For

Post-validation, we want to hear:

- "Conversion audit identified 3 quick wins that improved signup conversion by 22%"
- "Viral loop design helped us reduce CAC from $45 to $12 through referrals"
- "Retention playbook increased D30 retention from 18% to 31% in 6 weeks"
- "Metrics setup gave us clarity on our North Star metric and 10x'd experiment velocity"
- "Experiment design prioritized our backlog and helped us ship 12 validated tests"

These outcomes validate that growth commands solve real problems worth investing in.

## Feedback & Iteration

### How to Provide Feedback

If you use these commands, we'd love to hear:
- Which command did you use and why?
- What value did you get from it?
- What was missing or could be improved?
- Would you use a dedicated growth agent if available?

### Known Limitations

These commands are **intentionally scoped** for validation:
- No custom growth agent (use existing agents only)
- No implementation automation (analysis and planning only)
- No real-time dashboards (specs for implementation)
- No ongoing optimization (point-in-time analysis)

If demand validates, a dedicated growth agent would address these limitations.

## Timeline to Decision

**Target Decision Date**: 90 days from launch

**Decision Framework:**
```
IF usage >= 20 invocations AND unique_users >= 10 AND completion_rate >= 70%:
    BUILD dedicated growth-engineer agent
ELSE IF usage >= 10 invocations:
    ITERATE on command design, extend validation 30 days
ELSE:
    DEPRECATE growth commands, focus on other priorities
```

## Analytics Review Process

**Weekly** (During validation period):
- Monitor usage counts and trends
- Review completion rates by command and phase
- Identify common drop-off points
- Collect qualitative feedback from users

**Monthly** (During validation period):
- Analyze usage patterns and user segments
- Compare actual vs expected usage
- Identify iteration opportunities
- Update success criteria if needed

**End of Validation** (Day 90):
- Comprehensive usage analysis
- User surveys and interviews
- Build/no-build recommendation
- If build: Scope definition for growth agent based on learnings

---

## Appendix: Validation Data Schema

### Command Invocation Log
```json
{
  "timestamp": "ISO-8601",
  "command": "growth:command-name",
  "session_id": "sha256_hash",
  "status": "started|completed|failed|partial",
  "execution_time_minutes": 0,
  "phases_completed": 0,
  "error_message": "optional"
}
```

### Aggregated Metrics (Weekly)
```json
{
  "week": "2025-W41",
  "total_invocations": 0,
  "unique_sessions": 0,
  "completion_rate": 0.0,
  "avg_execution_time_minutes": 0.0,
  "by_command": {
    "growth:conversion-audit": {
      "invocations": 0,
      "completions": 0,
      "avg_phases": 0.0
    }
  }
}
```

### Decision Criteria Matrix
| Metric | Strong Demand | Moderate Demand | Low Demand |
|--------|---------------|-----------------|------------|
| Total Invocations (90 days) | 20+ | 10-19 | <10 |
| Unique Users | 10+ | 5-9 | <5 |
| Completion Rate | 70%+ | 50-69% | <50% |
| Qualitative Feedback | Enthusiastic | Neutral | Critical |
| **Decision** | **BUILD** | **ITERATE** | **DEPRECATE** |

---

**Last Updated**: 2025-10-09
**Status**: Active Validation (Day 0)
**Next Review**: 2025-10-16 (Week 1)
**Decision Target**: 2026-01-07 (Day 90)
