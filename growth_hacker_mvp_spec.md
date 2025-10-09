# Growth Commands: Validation MVP Spec

## Purpose
Test demand for growth-focused capabilities WITHOUT building a dedicated agent.
Timeline: 1 week to build, 6 weeks to validate usage.

## Commands to Build

### 1. /growth:experiment-design
**What it does**: Generates complete A/B test implementation
**Agents used**: product-manager (hypothesis), full-stack-architect (code), data-engineer (analytics)
**Input**: Feature to test (e.g., "pricing page CTA button color")
**Output**:
- Statistical hypothesis and sample size calculation
- Feature flag implementation code
- Tracking instrumentation
- Analysis SQL queries
- Success criteria dashboard

### 2. /growth:funnel-analysis
**What it does**: Diagnoses conversion funnel drop-offs
**Agents used**: data-engineer (queries), product-manager (interpretation)
**Input**: Funnel events and current metrics
**Output**:
- SQL queries to analyze each funnel step
- Drop-off identification and quantification
- Hypothesis for why users drop off
- Ranked improvement suggestions with impact estimates

### 3. /growth:instrumentation-setup
**What it does**: Generates complete analytics tracking implementation
**Agents used**: full-stack-architect (frontend), backend-api-engineer (backend), data-engineer (schema)
**Input**: Events to track (signups, feature usage, etc.)
**Output**:
- Event schema definitions
- Frontend tracking code (Segment/Amplitude/Mixpanel)
- Backend event emission code
- Data warehouse table schemas
- Example analysis queries

### 4. /growth:activation-optimize
**What it does**: Improves user onboarding/activation flow
**Agents used**: product-manager (strategy), full-stack-architect (implementation)
**Input**: Current activation rate and onboarding flow
**Output**:
- Activation funnel analysis
- Friction point identification
- Specific UI/UX improvements (code)
- Progressive disclosure strategy
- A/B test plan for improvements

### 5. /growth:referral-system
**What it does**: Implements viral/referral mechanics
**Agents used**: full-stack-architect (fullstack), security-audit-specialist (fraud prevention)
**Input**: Product description and target viral coefficient
**Output**:
- Referral link generation system
- Unique code/invite implementation
- Reward/incentive tracking database schema
- Fraud detection patterns
- Attribution logic
- Sharing UI components

## Implementation Plan

### Week 1: Build Commands
- Create `/commands/growth/` directory
- Write 5 command markdown files
- Test each command with sample inputs
- Document in README

### Weeks 2-7: Validation Period
- Track usage via command logs
- Collect user feedback after each command execution
- Monitor completion rates (did user accept generated code?)
- Interview 5 users who tried commands

### Week 8: Decision Point
**If strong validation:**
- Average 20+ uses/week across all commands
- 4.0+ satisfaction rating
- Users request additional growth commands
- **→ Proceed to build growth-hacker agent**

**If weak validation:**
- < 10 uses/week total
- Mixed or negative feedback
- Users prefer existing agents
- **→ Kill growth agent idea, keep commands**

**If partial validation:**
- Some commands popular, others ignored
- **→ Promote popular commands to agent, deprecate unpopular**

## Success Metrics Dashboard

Track weekly:
- Total command invocations (by command type)
- Unique users invoking growth commands
- Average satisfaction rating (post-command survey)
- Code acceptance rate (% of generated code actually used)
- Follow-up questions (indicates command was incomplete)

Kill criteria:
- < 30 total invocations across all 5 commands in first month
- < 3.5 average satisfaction rating
- < 50% code acceptance rate

## Why This Approach Wins

1. **Evidence-based**: Validates demand before agent investment
2. **Low risk**: 1 week to build vs 4 weeks for full agent
3. **Reversible**: Easy to kill if validation fails
4. **Reusable**: If agent gets built, commands become examples
5. **User-centric**: Tests actual usage, not hypothetical need

## If Validation Succeeds: Agent Spec

Only write full agent spec after validation proves demand.

Preliminary scope (pending validation):
- **Domain**: Product-led growth (activation, retention, experimentation)
- **Target User**: Technical founders, growth PMs, eng leads
- **Core Capabilities**: Experiment design, funnel optimization, instrumentation, viral mechanics
- **Excluded**: Paid acquisition, content marketing, SEO (separate agents)
- **Differentiation**: Generates production-ready code, not just strategy
- **Integration**: Works with product-manager (why), full-stack-architect (how), data-engineer (measure)

## Conclusion

The debate forced a critical realization: **We're solving for excitement, not evidence.**

This MVP spec solves for evidence first. If users want growth automation, they'll use these commands. If they don't, we save 4 weeks of wasted development.

**Recommendation**: Build the commands, not the agent. Let usage data make the decision.