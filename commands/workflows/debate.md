# Debate - Agent Conflict Theater for Technical Decisions

**Category:** Workflow Command
**Purpose:** Surface hidden tradeoffs through structured agent disagreement
**Duration:** 45-90 minutes
**Agents Involved:** 2-3 opposing specialists + the-critic (moderator)
**Complexity:** High

---

## Overview

The `/debate` command orchestrates a structured argument between 2-3 agents with fundamentally different philosophies or priorities. Instead of providing a single answer, it surfaces hidden tradeoffs, assumptions, and perspectives that consensus obscures.

**Core Insight:** The REAL value isn't in the agents' answers—it's in surfacing what they disagree about.

---

## Philosophy

### Why Disagreement Matters

**Traditional Approach:**
- Agent provides recommendation
- User accepts or rejects
- Hidden assumptions unchallenged
- Blind spots remain invisible

**Debate Theater Approach:**
- Multiple agents argue opposing positions
- Assumptions made explicit through conflict
- Tradeoffs surface through disagreement
- User makes informed decision

**Example:**
- **Question:** "Should we use PostgreSQL or MongoDB?"
- **Traditional:** Single agent recommends one
- **Debate:** data-engineer (PostgreSQL) vs ai-ml-engineer (MongoDB vector search) vs the-skeptic ("neither, use managed service")

### When Disagreement Adds Value

✅ **Use debate for:**
- Architectural decisions with long-term consequences
- Technology stack selection
- Build vs buy decisions
- Optimization tradeoffs (performance vs simplicity)
- Strategic direction setting

❌ **Don't use debate for:**
- Factual questions with right answers
- Emergency situations requiring quick action
- Already-committed decisions (post-debate validation)
- Low-stakes, reversible choices

---

## Debate Formats

### Format 1: Technology Showdown

**Structure:** 2 agents advocate for different technology choices

**Example Topics:**
- "PostgreSQL vs MongoDB for our use case"
- "React vs Svelte for this project"
- "Microservices vs Monolith architecture"
- "REST vs GraphQL API design"

**Debaters:**
- **Agent A:** Advocates for option 1 (e.g., PostgreSQL)
- **Agent B:** Advocates for option 2 (e.g., MongoDB)
- **Moderator:** the-critic (synthesizes, identifies tradeoffs)

**Deliverable:**
- Side-by-side comparison
- Tradeoff analysis
- Recommendation with context

---

### Format 2: Philosophy Clash

**Structure:** 2 agents with opposing engineering philosophies debate approach

**Example Topics:**
- "Optimize for performance vs optimize for simplicity"
- "Build custom vs use off-the-shelf"
- "Move fast and break things vs measure twice cut once"
- "Premature optimization vs technical debt"

**Debaters:**
- **Agent A:** Performance-focused (e.g., systems-engineer)
- **Agent B:** Simplicity-focused (e.g., the-skeptic)
- **Moderator:** the-critic

**Deliverable:**
- Philosophical positions clarified
- Context where each applies
- Recommendations for this specific case

---

### Format 3: Stakeholder Perspectives

**Structure:** 2-3 agents represent different stakeholder concerns

**Example Topics:**
- "Security vs usability for authentication"
- "Feature velocity vs code quality"
- "User needs vs business constraints"
- "Innovation vs reliability"

**Debaters:**
- **Agent A:** Security perspective (security-audit-specialist)
- **Agent B:** UX perspective (accessibility-expert)
- **Agent C:** Business perspective (product-manager)
- **Moderator:** project-orchestrator

**Deliverable:**
- Multi-stakeholder tradeoff matrix
- Compromise solutions
- Prioritization framework

---

### Format 4: The Gauntlet (Advanced)

**Structure:** One proposed solution vs 3 challenging agents

**Example:**
- **Proposal:** "Let's use serverless architecture"
- **Challenger 1:** devops-engineer (operational complexity)
- **Challenger 2:** the-skeptic (cost overruns)
- **Challenger 3:** systems-engineer (performance unpredictability)
- **Moderator:** the-critic

**Deliverable:**
- Strengthened proposal (survives challenges)
- Abandoned proposal (challenges won)
- Modified proposal (compromise)

---

## Debate Structure

### Phase 1: Opening Statements (15 minutes)

Each agent presents their position:

**Agent A:**
- Why their approach is superior
- Key benefits and advantages
- Ideal use cases

**Agent B:**
- Why the alternative is better
- Limitations of Agent A's approach
- Counter-examples

**Agent C (if present):**
- Third option or middle ground
- Critiques of both positions

### Phase 2: Rebuttal (20 minutes)

Agents challenge each other's assumptions:

**Agent A Response:**
- Addresses Agent B's critiques
- Questions Agent B's assumptions
- Highlights Agent B's blindspots

**Agent B Response:**
- Counters Agent A's defense
- Provides evidence for position
- Identifies Agent A's biases

### Phase 3: Tradeoff Analysis (15 minutes)

**Moderator (the-critic) Synthesizes:**
- Areas of agreement (common ground)
- Core disagreements (fundamental tradeoffs)
- Context-dependent factors (when each is right)
- Hidden assumptions (what both agents assume)

### Phase 4: Recommendations (15 minutes)

**Moderator Delivers:**
- **Option A Wins If:** [Context where Agent A is right]
- **Option B Wins If:** [Context where Agent B is right]
- **Compromise If:** [Hybrid approaches]
- **Neither If:** [When to reject both]

**Decision Framework:**
- Questions to ask yourself
- Data you need to collect
- Experiments to run
- Reversibility assessment

---

## Example Debates

### Debate 1: PostgreSQL vs MongoDB

**Topic:** Database selection for SaaS analytics platform

**Agent A: data-engineer (PostgreSQL)**

**Opening Statement:**
> "PostgreSQL wins for analytics workloads. Strong ACID guarantees, mature query optimizer, time-series extensions (TimescaleDB), excellent JOIN performance for relational analytics. MongoDB's flexibility is irrelevant when your schema is stable. PostgreSQL's JSON support gives you flexibility where needed without sacrificing consistency."

**Key Arguments:**
- Transactional integrity critical for financial data
- Complex aggregations need SQL's expressiveness
- Mature ecosystem (pgAdmin, pg_stat_statements, etc.)
- Horizontal scaling via Citus extension

**Agent B: ai-ml-engineer (MongoDB)**

**Opening Statement:**
> "MongoDB excels for evolving data models and vector search. Your analytics platform will grow—PostgreSQL migrations break things. MongoDB's flexible schema lets you iterate fast. Native vector search (Atlas Vector Search) for AI-powered insights without external service. Aggregation pipeline more intuitive than SQL for data scientists."

**Key Arguments:**
- Schema evolution without migrations
- Vector embeddings for semantic search
- Document model matches JSON APIs
- Horizontal sharding built-in

**Moderator: the-critic**

**Tradeoff Analysis:**
> **Core Disagreement:** Consistency vs Flexibility
>
> **Both assume:** You'll scale beyond single server (may not be true)
>
> **PostgreSQL Wins If:**
> - Data integrity non-negotiable (financial/compliance)
> - Relational queries dominate (JOINs, aggregations)
> - Team knows SQL better than NoSQL
> - Mature tooling ecosystem needed
>
> **MongoDB Wins If:**
> - Schema will evolve frequently
> - Vector search is core requirement
> - Document-centric data model
> - Team prefers JavaScript/Python over SQL
>
> **Compromise: PostgreSQL + pgvector**
> - Use PostgreSQL for transactional data
> - Add pgvector extension for vector search
> - Get best of both worlds

**Recommendation:**
> Start with PostgreSQL + pgvector. You get:
> - ACID guarantees (financial data needs this)
> - Vector search (pgvector extension)
> - JSON fields for flexibility (JSONB)
> - Mature analytics ecosystem
>
> Revisit if: Schema changes 10+ times (signals MongoDB might be better)

---

### Debate 2: Optimize Now vs Later

**Topic:** Should we optimize performance before launch?

**Agent A: systems-engineer (Optimize Now)**

**Opening Statement:**
> "Premature optimization is a myth used by lazy engineers. You're building a product for 10K+ users but testing with 10. Performance issues compound—what's 100ms at 10 users is 10s at 10K users. Refactoring live production is 10x harder than building it right. Optimize now or pay with interest later."

**Key Arguments:**
- Performance bugs harder to fix in production
- User expectations set by initial experience
- Technical debt accumulates exponentially
- "We'll optimize later" rarely happens

**Agent B: the-skeptic (Optimize Later)**

**Opening Statement:**
> "You don't have 10K users. You have 0 users. Premature optimization is procrastination disguised as engineering. You're guessing at bottlenecks. 90% of your optimizations will target the wrong thing. Ship, measure, optimize what actually matters. Every hour optimizing is an hour not validating product-market fit."

**Key Arguments:**
- Don't know where bottlenecks are until real usage
- Optimization without measurement wastes time
- Shipping sooner validates assumptions faster
- Can always optimize top 20% that causes 80% of issues

**Moderator: the-critic**

**Tradeoff Analysis:**
> **Core Disagreement:** Risk tolerance (slow launch vs slow product)
>
> **Both assume:** You'll get to 10K users (optimistic!)
>
> **Optimize Now If:**
> - Hard performance requirements (medical, financial, gaming)
> - Known bottlenecks from similar products
> - Can't iterate post-launch (embedded systems)
> - Downtime unacceptable (infrastructure)
>
> **Optimize Later If:**
> - Uncertain product-market fit
> - Need to ship fast to learn
> - Can iterate post-launch easily
> - Cost of slowness < cost of delay
>
> **Hybrid Approach:**
> - Avoid obvious stupidity (N+1 queries, huge bundle sizes)
> - Don't prematurely optimize (complex caching, micro-optimizations)
> - Instrument everything (know where to optimize when needed)
> - Set performance budget (no slower than this, no faster needed)

**Recommendation:**
> Follow the "80% rule":
> - Spend 80% on features, 20% on performance
> - Avoid obvious anti-patterns (that's not premature optimization)
> - Add monitoring/profiling (know what's slow)
> - Optimize top 3 bottlenecks after launch (data-driven)
>
> Re-debate if: Performance becomes #1 user complaint

---

### Debate 3: Accessibility vs Velocity

**Topic:** Spend extra 30% time on accessibility or ship faster?

**Agent A: accessibility-expert (Accessibility First)**

**Opening Statement:**
> "Accessibility isn't optional. 15% of users have disabilities. WCAG compliance is law in many jurisdictions. Retrofitting accessibility is 3-5x more expensive than building it in. Every day you ship without accessibility, you're excluding millions and accruing legal risk."

**Key Arguments:**
- Legal compliance (ADA, WCAG requirements)
- 15% market expansion (disabled users)
- Better UX for everyone (captions help in noisy environments)
- Cheaper to build in than retrofit

**Agent B: product-manager (Ship Fast, Iterate)**

**Opening Statement:**
> "Perfect accessibility on a product nobody uses is worthless. Ship fast, validate demand, then invest in accessibility properly. 30% slower time-to-market could mean competitors win. Start with 80% accessibility (semantic HTML, keyboard nav), perfect it when you have users and revenue."

**Key Arguments:**
- Time-to-market is competitive advantage
- No revenue = no resources to invest in accessibility
- Can prioritize post-validation
- 80% accessibility covers 95% of users

**Moderator: the-critic**

**Tradeoff Analysis:**
> **Core Disagreement:** Risk prioritization (legal/ethical vs market)
>
> **Both assume:** Resources are constrained (might not be true)
>
> **Accessibility First If:**
> - Government/enterprise customers (require WCAG AA)
> - High legal risk industry
> - Brand values center on inclusion
> - Long development cycle (time to do it right)
>
> **Ship Fast If:**
> - B2C consumer app (lower legal risk)
> - Tight competition (seconds matter)
> - Pre-PMF (validating core concept)
> - Can iterate quickly post-launch
>
> **Compromise: Accessibility MVP**
> - Semantic HTML (costs nothing, huge benefit)
> - Keyboard navigation (adds 10%, not 30%)
> - Alt text (quick wins)
> - Defer: Screen reader perfection, ARIA complexity, color contrast edge cases

**Recommendation:**
> Implement "Accessibility MVP":
> - Week 1-2: Semantic HTML, keyboard nav, alt text (10% time)
> - Post-Launch: Full WCAG AA audit (when you have revenue)
> - Months 3-6: Perfect screen reader support, advanced ARIA
>
> Re-debate if: Enterprise/gov sales opportunity, lawsuit risk, or brand positioning on inclusion

---

## Debate Moderation Best Practices

### The Moderator's Role (the-critic)

**DO:**
- ✅ Identify core disagreements (not surface differences)
- ✅ Surface hidden assumptions (what both agents assume)
- ✅ Highlight context dependencies (when each is right)
- ✅ Challenge weak arguments (keep debate rigorous)
- ✅ Synthesize recommendations (actionable guidance)

**DON'T:**
- ❌ Take sides (moderator stays neutral)
- ❌ Let it devolve into name-calling (keep professional)
- ❌ Allow strawmen arguments (challenge misrepresentations)
- ❌ Provide vague synthesis ("it depends" without specifics)

### Keeping Debates Productive

**Red Flags:**
- Agents repeating same points (time to move on)
- Arguing semantics instead of substance (refocus)
- Personal attacks (re-establish ground rules)
- Talking past each other (clarify disagreement)

**Green Flags:**
- New insights emerging (extended debate valuable)
- Assumptions being questioned (core value of debate)
- Compromise solutions proposed (productive dialogue)
- User understanding deepening (goal achieved)

---

## Usage Examples

### Invoke via Command

```bash
# Basic debate
/debate "PostgreSQL vs MongoDB for analytics platform"

# Specify agents
/debate "performance vs simplicity" --agents=systems-engineer,the-skeptic

# Multi-agent debate
/debate "authentication approach" --agents=security-audit-specialist,accessibility-expert,product-manager
```

### Expected Workflow

1. **User submits question** with 2-3 alternatives
2. **System selects agents** with opposing views (or user specifies)
3. **Agents present opening statements** (15 min each)
4. **Agents rebut each other** (20 min)
5. **Moderator synthesizes** (15 min)
6. **Recommendations delivered** with decision framework

---

## Success Metrics

**Debate succeeds when:**

1. **Hidden Tradeoffs Surfaced**
   - User discovers considerations they hadn't thought of
   - Assumptions made explicit
   - Blindspots revealed

2. **Better Decision Made**
   - User feels more confident in decision
   - Decision accounts for tradeoffs
   - Fallback plans identified

3. **Learning Occurred**
   - User understands both perspectives
   - Can articulate tradeoffs to others
   - Knows what data they need to collect

**Debate fails when:**
- User more confused after than before
- Debate devolves into technical jargon
- No actionable recommendations emerge
- Obvious winner, debate was unnecessary

---

## Related Commands

- `/architecture-review` - Comprehensive architecture assessment
- `/code-quality-review` - Code quality and maintainability review
- `/production-readiness` - Pre-deployment checklist

---

## Related Agents

- **the-critic** - Default moderator for debates
- **the-skeptic** - Questions all automation assumptions
- **project-orchestrator** - Coordinates multi-agent workflows

---

## Version History

- **v1.0** (2025-10-07): Initial debate command implementation

---

**Maintained By:** project-orchestrator, the-critic
**Last Updated:** 2025-10-07
**License:** MIT
