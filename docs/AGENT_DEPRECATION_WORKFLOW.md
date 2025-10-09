# Agent Deprecation Workflow

**Version:** 1.0
**Last Updated:** 2025-10-09
**Owner:** Product Management Team

## Overview

This document defines the end-to-end process for deprecating agents in the ClaudeAgents ecosystem. Our approach prioritizes radical transparency through Agent Death Certificates - public postmortems that document why agents fail and what we learned.

**Philosophy:** Every deprecation is a learning opportunity. We document failures as openly as successes to build community trust and advance the field of AI agent design.

---

## 1. Deprecation Trigger Criteria

### Quantitative Triggers (Data-Driven)

An agent becomes a **deprecation candidate** when ANY of these conditions persist:

| Trigger | Threshold | Measurement Period | Data Source |
|---------|-----------|-------------------|-------------|
| **Low Usage** | <10 invocations/month | 3 consecutive months | Analytics telemetry |
| **Poor Satisfaction** | <3.0/5.0 average rating | 6+ weeks | User feedback surveys |
| **High Error Rate** | >15% task failure rate | 4+ weeks | Error tracking logs |
| **Zero Adoption** | 0 new users | 8+ weeks | User analytics |
| **Support Burden** | >20 tickets/month | 2+ months | Support ticket system |

### Qualitative Triggers (Strategic Assessment)

Deprecation consideration triggered by:

1. **Supersession**: New agent demonstrably better (A/B test shows >30% improvement in task completion)
2. **Strategic Misalignment**: Agent doesn't align with platform roadmap (validated through product strategy review)
3. **Technical Debt Crisis**: Would require >80% rewrite to maintain, no clear ROI
4. **Regulatory/Legal Risk**: Compliance issues with no viable mitigation path
5. **Community Consensus**: Multiple users request deprecation or report fundamental design flaws

### False Positive Prevention

**Do NOT deprecate if:**
- Agent serves niche use case with small but highly satisfied user base (>4.5/5.0 rating, even if low volume)
- Usage is seasonal or cyclical (e.g., tax-season agent)
- Recent launch (<6 months) with expected slow adoption curve
- Strategic importance despite metrics (e.g., accessibility-expert for compliance)

---

## 2. Deprecation Decision Process

### Phase 1: Identification (Week 0)

**Owner:** Product Manager

1. **Automated Monitoring**: Weekly dashboard review flags agents meeting trigger criteria
2. **Manual Review**: PM validates data accuracy, checks for false positives
3. **Preliminary Assessment**:
   ```markdown
   Agent: [agent-name]
   Trigger: [specific criteria met]
   Usage Data: [last 3 months stats]
   User Feedback: [recent sentiment analysis]
   Strategic Context: [business justification]
   Recommendation: [investigate | deprecate | improve]
   ```

### Phase 2: Investigation (Week 1-2)

**Owner:** Cross-Functional Team (PM, Eng Lead, Product Strategist)

**Investigation Checklist:**
- [ ] Analyze root causes: Why is the agent underperforming?
- [ ] Review user feedback: What do users say? (interviews with 3-5 affected users)
- [ ] Assess alternatives: Can existing agents cover this use case?
- [ ] Cost-benefit analysis: Fix vs deprecate? (effort estimate vs expected impact)
- [ ] Competitive analysis: Do competitors offer similar agents? Is deprecation a strategic risk?

**Decision Framework:**

| Scenario | Decision |
|----------|----------|
| Fixable within 1 sprint + positive ROI | **FIX IT** - Schedule improvements |
| Superseded agent exists with clear migration | **DEPRECATE** - Proceed to Phase 3 |
| Niche value but low usage | **MAINTAIN** - Reduce support, keep active |
| High cost to fix + no strategic value | **DEPRECATE** - Proceed to Phase 3 |
| Unclear value proposition | **SUNSET TRIAL** - Mark as beta, re-evaluate in 3 months |

### Phase 3: Go/No-Go Decision (End of Week 2)

**Decision Makers:** Product Manager (final authority), Engineering Lead (feasibility), Product Strategist (strategic alignment)

**Go/No-Go Meeting Agenda:**
1. Present investigation findings (15 min)
2. Discuss migration path and user impact (10 min)
3. Review death certificate draft outline (5 min)
4. Decision: Proceed with deprecation? (5 min)
5. If GO: Assign death certificate authoring team (5 min)

**Documentation Required:**
```markdown
# Deprecation Decision Record

**Agent:** [agent-name]
**Decision Date:** [YYYY-MM-DD]
**Decision:** DEPRECATE

## Rationale
[2-3 paragraphs explaining why deprecation is the right choice]

## User Impact
- Affected Users: [count]
- Migration Path: [specific alternative agent(s)]
- Support Plan: [how we'll help users transition]

## Timeline
- Notification: [date]
- Death Certificate Draft: [date]
- Final Deprecation: [date]

## Approvals
- Product Manager: [name] ✓
- Engineering Lead: [name] ✓
- Product Strategist: [name] ✓
```

---

## 3. Deprecation Communication Plan

### 30-Day Timeline (Transparency-First Approach)

```
Day 0          Day 7          Day 14         Day 21         Day 30
  |              |              |              |              |
Decision      Notify         Draft          Final        Official
  Made         Users       Certificate    Certificate   Deprecation
  |              |              |              |              |
  v              v              v              v              v
Internal    Email +       Publish for     Lock & Link   Move to
 Start      Notice        Feedback       Migration    deprecated/
```

### Day 0: Internal Decision

**Actions:**
- [ ] Go/No-Go decision documented
- [ ] Deprecation issue created in project tracker
- [ ] Death certificate authoring team assigned
- [ ] Internal Slack announcement in #product-updates

**Internal Announcement Template:**
```markdown
:warning: Agent Deprecation Decision: `[agent-name]`

We've decided to deprecate the `[agent-name]` agent effective [date].

**Why:** [1-sentence reason]
**Affected Users:** [count or "none identified"]
**Migration Path:** Users should use `[alternative-agent]` instead
**Death Certificate:** Draft in progress, will be published Day 14

**Next Steps:**
- Day 7: User notification email sent
- Day 14: Public death certificate draft published
- Day 30: Agent moved to deprecated/ directory

Questions? Reply in thread or DM @product-manager
```

### Day 7: User Notification

**Actions:**
- [ ] Email sent to all affected users (see template below)
- [ ] Public deprecation notice posted to:
  - Project README.md (deprecation section)
  - GitHub Discussions (if applicable)
  - Community forum announcement
- [ ] Social media post (optional, for high-profile agents)

**Email Template: User Notification**

**Subject:** Action Required: `[agent-name]` Agent Deprecation Notice

```
Hi [User Name],

We're writing to inform you that the `[agent-name]` agent will be deprecated on [DATE] (23 days from now).

WHY WE'RE DEPRECATING
[2-3 sentences explaining the reason in plain language, no corporate jargon]

WHAT THIS MEANS FOR YOU
- The agent will continue working until [DATE]
- After [DATE], you'll need to use `[alternative-agent]` instead
- We've prepared a migration guide to help you transition: [link]

YOUR MIGRATION PATH
Recommended alternative: `[alternative-agent]`
- [Key benefit 1 of alternative]
- [Key benefit 2 of alternative]
- [Migration effort estimate: "5 minutes" or "minimal changes needed"]

Migration guide: [link to docs]

QUESTIONS OR CONCERNS?
- Reply to this email for 1:1 support
- Join our office hours on [date/time] for live Q&A
- Review our death certificate (publishing [DATE]): [link when available]

We're committed to transparency about why this agent didn't work out. On [DATE], we'll publish a detailed "Agent Death Certificate" explaining what we learned and how we'll do better.

Thank you for being part of our community.

[Product Manager Name]
[Email/Calendar Link for Office Hours]
```

**Public Deprecation Notice (README.md Section):**
```markdown
## Deprecation Notices

### `[agent-name]` - Deprecating [DATE]

**Reason:** [1-sentence explanation]
**Alternative:** Use `[alternative-agent]` instead
**Migration Guide:** [link]
**Death Certificate:** Publishing [DATE] - [link when available]

**Timeline:**
- :calendar: Day 7 (today): Notification sent to affected users
- :memo: Day 14: Death certificate draft published for community feedback
- :white_check_mark: Day 21: Final death certificate published
- :coffin: Day 30: Agent officially deprecated
```

### Day 14: Death Certificate Draft Published

**Actions:**
- [ ] Death certificate markdown file created in `death_certificates/drafts/`
- [ ] Draft published for community feedback
- [ ] Announcement in GitHub Discussions / forum: "Help us learn from this"
- [ ] Feedback collection form linked (Google Form or GitHub Discussions thread)

**Draft Announcement Template:**
```markdown
# Death Certificate Draft: `[agent-name]` - Community Feedback Requested

We've drafted the death certificate for the `[agent-name]` agent (deprecating [DATE]).

**Read the draft:** [link to death_certificates/drafts/AGENT-NAME-YYYY-MM-DD.md]

**We want your input:**
- Did we accurately describe the failure?
- Are we missing important context?
- Do you have suggestions for how we could have done better?

**Feedback deadline:** [Day 20] - We'll incorporate your feedback into the final version.

This is an experiment in radical transparency. Thank you for helping us learn.
```

### Day 21: Final Death Certificate Published

**Actions:**
- [ ] Incorporate community feedback into final certificate
- [ ] Move certificate from `drafts/` to `death_certificates/`
- [ ] Update deprecation notice with final certificate link
- [ ] Migration guide finalized and linked
- [ ] Final announcement: "Death certificate published, 9 days until deprecation"

### Day 30: Official Deprecation

**Actions:**
- [ ] Move agent from `agents/` to `agents/deprecated/`
- [ ] Add deprecation warning to agent frontmatter
- [ ] Update CLAUDE.md to remove agent from active roster
- [ ] Add redirect in docs to death certificate
- [ ] Run validation: `python3 tools/validate_agents.py`
- [ ] Commit changes with message: `Deprecate [agent-name] - Death Certificate: [link]`
- [ ] Update death certificates gallery: Add entry to `death_certificates/README.md`
- [ ] Final email to affected users: "Deprecation complete, here's your migration path"
- [ ] Close deprecation issue in project tracker

**Git Commit Template:**
```
Deprecate agent: [agent-name]

Moved to agents/deprecated/ following 30-day deprecation process.

Reason: [1-sentence summary]
Death Certificate: death_certificates/AGENT-NAME-YYYY-MM-DD.md
Migration Path: Use [alternative-agent] instead

Affected users notified on Day 7, community feedback collected on
draft certificate Day 14-20, final certificate published Day 21.

Closes #[deprecation-issue-number]
```

---

## 4. Death Certificate Authoring Process

### Death Certificate Structure

Every death certificate follows this markdown template:

```markdown
# Agent Death Certificate: [Agent Name]

**Agent ID:** [agent-file-name]
**Date of Birth:** [YYYY-MM-DD] (first commit)
**Date of Death:** [YYYY-MM-DD] (deprecation date)
**Lifespan:** [X months]
**Cause of Death:** [Primary reason category]

---

## Executive Summary

[2-3 paragraph honest summary of what happened. No corporate jargon. What did we try to build? Why did it fail? What did we learn?]

---

## What We Tried to Build

**Vision:** [What was the agent supposed to do?]

**Target Users:** [Who was this for?]

**Key Capabilities:**
- [Capability 1]
- [Capability 2]
- [Capability 3]

**Success Criteria:** [What would success have looked like?]

---

## Usage Statistics

| Metric | Value | Context |
|--------|-------|---------|
| Total Invocations | [count] | [over X months] |
| Monthly Active Users | [count] | [peak vs final month] |
| Average Satisfaction | [X.X/5.0] | [sample size] |
| Task Success Rate | [X%] | [vs platform avg Y%] |
| Support Tickets | [count] | [% of total support volume] |

**Usage Trend:** [Graph or description of adoption curve - did usage grow then decline? Never take off? Spike then crash?]

---

## What Happened (The Honest Story)

[3-5 paragraphs telling the real story. This section should be written like a postmortem - honest, detailed, technical where appropriate.]

**Initial Hypothesis:**
[What did we believe when we built this?]

**Reality:**
[What actually happened when users tried to use it?]

**Key Turning Points:**
1. [Event 1: e.g., "Week 4: First user complained about X"]
2. [Event 2: e.g., "Month 2: Realized fundamental design flaw"]
3. [Event 3: e.g., "Month 5: Team decided to deprecate vs rewrite"]

**Root Causes:**
- **Primary:** [The main reason this failed]
- **Secondary:** [Contributing factors]
- **Missed Assumptions:** [What did we get wrong in our initial assumptions?]

---

## User Feedback (Unfiltered)

[Include actual user quotes - both positive and negative. This builds credibility.]

**What Users Liked:**
> "[User quote 1]"
> "[User quote 2]"

**What Users Disliked:**
> "[User quote about problems]"
> "[User quote about frustrations]"

**Most Common Complaint:** [Specific issue that came up repeatedly]

---

## What We Learned

### Technical Lessons
- [Lesson 1: e.g., "Multi-agent coordination requires explicit handoff protocols"]
- [Lesson 2: e.g., "Domain specificity is more valuable than generalization"]
- [Lesson 3]

### Product Lessons
- [Lesson 1: e.g., "Users need migration guides before deprecation, not after"]
- [Lesson 2: e.g., "Low usage isn't always a failure signal - check satisfaction"]
- [Lesson 3]

### Process Lessons
- [Lesson 1: e.g., "Should have run user interviews before building"]
- [Lesson 2: e.g., "Beta testing with 5 users would have caught this"]
- [Lesson 3]

---

## Migration Path

**Recommended Alternative:** [`alternative-agent`](../agents/alternative-agent.md)

**Why This Alternative is Better:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Migration Guide:**

| Old Agent Task | New Approach |
|----------------|--------------|
| [Task 1] | Use `[alternative-agent]` with [specific instructions] |
| [Task 2] | Use `[alternative-agent]` with [specific instructions] |
| [Task 3] | Use `[alternative-agent]` with [specific instructions] |

**Effort Estimate:** [X minutes/hours to migrate typical usage]

**Migration Support:**
- Documentation: [link]
- Support email: [email]
- Community forum: [link]

---

## What We'd Do Differently

[Bullet list of specific, actionable things we'd change if we could start over]

1. **[Area 1]:** [Specific change]
2. **[Area 2]:** [Specific change]
3. **[Area 3]:** [Specific change]

---

## Memorial: What This Agent Taught Us

[1-2 paragraphs reflecting on the positive impact, even if the agent failed. What questions did it help us answer? What future agents benefited from these lessons?]

---

## Appendix: Technical Details

**Commit History:** [Link to Git history]
**Deprecation Issue:** [Link to issue tracker]
**Community Feedback:** [Link to discussion thread]
**Related Death Certificates:** [Links to similar failures]

---

**Death Certificate Author:** [Product Manager Name]
**Contributors:** [Engineering Lead, Product Strategist, User Researcher, etc.]
**Community Reviewers:** [Users who provided feedback on draft]
**Published:** [YYYY-MM-DD]
**Status:** Final

---

*This death certificate is part of our commitment to radical transparency. Every failure teaches us how to build better agents. Thank you to everyone who used, tested, and provided feedback on this agent.*
```

### Authoring Team & Responsibilities

| Role | Responsibility | Deliverable |
|------|----------------|-------------|
| **Product Manager** | Overall authoring, usage statistics, executive summary | Sections: Executive Summary, Usage Statistics, Migration Path |
| **Technical Writer** | Interview team, write "What Happened" narrative | Section: What Happened (The Honest Story) |
| **Engineering Lead** | Root cause analysis, technical lessons | Sections: Root Causes, Technical Lessons, Technical Details |
| **Product Strategist** | Strategic context, alternatives, future direction | Sections: What We'd Do Differently, Memorial |
| **User Researcher** | Compile user feedback, quotes, satisfaction data | Section: User Feedback (Unfiltered) |
| **The-Critic (Agent)** | Review for honesty, call out corporate speak, ensure transparency | Quality review pass on full draft |

### Authoring Timeline (Days 7-21)

**Days 7-10: Individual Drafting**
- Each team member drafts their assigned sections independently
- Product Manager creates shared Google Doc or markdown draft
- Sections completed: 60%

**Days 11-13: Integration & Review**
- Product Manager integrates sections into cohesive narrative
- Engineering Lead reviews for technical accuracy
- Product Strategist reviews for strategic clarity
- Sections completed: 85%

**Day 14: Publish Draft for Community Feedback**
- The-Critic agent reviews draft for honesty (no corporate jargon filter)
- Draft published to `death_certificates/drafts/`
- Community announcement posted

**Days 15-20: Community Feedback Period**
- Monitor feedback channels (GitHub Discussions, email, forum)
- Product Manager compiles feedback into document
- Team reviews feedback, prioritizes changes

**Day 21: Finalize & Publish**
- Incorporate top feedback (focus on accuracy and clarity)
- Final The-Critic review
- Move from `drafts/` to `death_certificates/`
- Publish announcement

### Honesty Checklist (The-Critic Review)

Before publishing, The-Critic agent (or designated human reviewer) checks:

- [ ] **No corporate jargon:** Replace "strategic pivot" with "we failed", "learnings" with "mistakes"
- [ ] **Specific, not vague:** "Usage dropped from 50 to 8/month" not "usage declined"
- [ ] **Real user quotes:** Include actual feedback, not sanitized versions
- [ ] **Admits mistakes:** Clearly states what the team got wrong
- [ ] **Actionable lessons:** "What We'd Do Differently" has concrete, testable recommendations
- [ ] **No blame-shifting:** Takes responsibility, doesn't blame users or external factors
- [ ] **Balanced:** Includes what worked as well as what didn't
- [ ] **Useful to others:** Someone building a similar agent would find this valuable

**Red Flags (Require Rewrite):**
- Passive voice: "Mistakes were made" → "We misunderstood user needs"
- Vague metrics: "Low usage" → "8 invocations/month, 95% below target"
- Missing root cause: Must explain WHY it failed, not just THAT it failed
- No user voice: Must include real user feedback, not team interpretation
- Corporate euphemisms: "Sunset", "strategic realignment", "optimizing portfolio"

---

## 5. Technical Deprecation Steps

### Pre-Deprecation Validation

Before making code changes, validate:

```bash
# 1. Verify agent exists and is documented
ls -la agents/[agent-name].md
grep -r "[agent-name]" docs/

# 2. Check for dependencies (other agents referencing this one)
grep -r "agent-name" agents/
grep -r "agent-name" commands/

# 3. Run full validation suite
python3 tools/validate_agents.py
python3 -m pytest tests/
```

### Code Changes Checklist

**Step 1: Update Agent File**

```bash
# Move agent to deprecated directory
mkdir -p agents/deprecated
git mv agents/[agent-name].md agents/deprecated/[agent-name].md
```

**Step 2: Add Deprecation Frontmatter**

Edit `agents/deprecated/[agent-name].md` YAML frontmatter:

```yaml
---
name: "[Agent Name]"
description: "[Original description]"
color: "gray"  # Change to gray to indicate deprecation
deprecated: true
deprecation_date: "YYYY-MM-DD"
death_certificate: "death_certificates/AGENT-NAME-YYYY-MM-DD.md"
migration_path: "[alternative-agent]"
---

# DEPRECATED: [Agent Name]

**This agent was deprecated on [DATE].**

**Reason:** [1-sentence summary]

**Use this instead:** [`alternative-agent`](../agents/alternative-agent.md)

**Full story:** See our [Death Certificate](../death_certificates/AGENT-NAME-YYYY-MM-DD.md) for complete details on what happened and lessons learned.

---

[Original agent content below for historical reference]

[... rest of original agent markdown ...]
```

**Step 3: Update CLAUDE.md**

Remove agent from active roster:

```markdown
<!-- BEFORE -->
### Business Operations Agents
- **Requirements**: `business-analyst`
- **Documentation**: `technical-writer`
- **Product Management**: `product-manager`
- **[OLD AGENT]**: `old-agent-name`  <-- REMOVE THIS LINE

<!-- AFTER -->
### Business Operations Agents
- **Requirements**: `business-analyst`
- **Documentation**: `technical-writer`
- **Product Management**: `product-manager`
```

Add to deprecated agents section (create if doesn't exist):

```markdown
## Deprecated Agents

The following agents have been deprecated. See their death certificates for full details.

- **[Agent Name]** (`old-agent-name`) - Deprecated YYYY-MM-DD
  - Reason: [1-sentence]
  - Alternative: `alternative-agent`
  - Death Certificate: [link](death_certificates/AGENT-NAME-YYYY-MM-DD.md)
```

**Step 4: Update Commands**

Search for references in command files:

```bash
grep -r "old-agent-name" commands/
```

For each reference, either:
- **Option A:** Update to use alternative agent
- **Option B:** Add deprecation notice if command itself should be deprecated

**Step 5: Add Documentation Redirects**

Create redirect in relevant docs:

```markdown
<!-- In docs/architecture.md or other places where agent was documented -->

## ~~[Old Agent Name]~~ (DEPRECATED)

**This agent was deprecated on [DATE].** Use [`alternative-agent`](../agents/alternative-agent.md) instead.

**Why was it deprecated?** See [Death Certificate](../death_certificates/AGENT-NAME-YYYY-MM-DD.md)
```

**Step 6: Update Death Certificates Gallery**

Add entry to `death_certificates/README.md` (see Section 6 for format).

**Step 7: Run Validation**

```bash
# Validate agents still parse correctly
python3 tools/validate_agents.py

# Run tests
python3 -m pytest tests/

# Check for broken links (if tool exists)
# markdown-link-check death_certificates/*.md
```

**Step 8: Commit Changes**

```bash
git add agents/deprecated/[agent-name].md
git add CLAUDE.md
git add death_certificates/[AGENT-NAME]-[DATE].md
git add death_certificates/README.md
git add docs/  # Any documentation updates

git commit -m "Deprecate agent: [agent-name]

Moved to agents/deprecated/ following 30-day deprecation process.

Reason: [1-sentence summary]
Death Certificate: death_certificates/AGENT-NAME-YYYY-MM-DD.md
Migration Path: Use [alternative-agent] instead

Timeline:
- Day 7: User notification sent
- Day 14: Draft death certificate published
- Day 21: Final death certificate published
- Day 30: Agent officially deprecated (today)

Closes #[deprecation-issue-number]"

git push origin master  # Or feature branch if following git flow
```

### Post-Deprecation Monitoring

**Week 1-4 After Deprecation:**
- [ ] Monitor support tickets for migration issues
- [ ] Track usage of alternative agent (should see uptick if migration successful)
- [ ] Watch for community discussion of deprecation
- [ ] Respond to feedback on death certificate

**Month 2-3 After Deprecation:**
- [ ] Review migration success: Did affected users successfully transition?
- [ ] Collect testimonials from users who migrated successfully
- [ ] Update death certificate with "3-month retrospective" section if major learnings emerge

---

## 6. Public Death Certificates Gallery

### Gallery Structure

Create `death_certificates/README.md` as the public-facing gallery:

```markdown
# Agent Death Certificates Gallery

**Welcome to our Agent Graveyard.** This is where we document our failures with radical transparency.

Every agent that gets deprecated receives a death certificate explaining what happened, what we learned, and how we'll do better. This is our commitment to learning in public.

**Why publish failures?** Because honest postmortems advance the entire field of AI agent design. If we can help others avoid our mistakes, our failures become valuable.

---

## Browse by Cause of Death

### Low Adoption / Product-Market Fit Failures
- **[Agent Name](AGENT-NAME-YYYY-MM-DD.md)** - Deprecated YYYY-MM-DD
  - *Lesson:* [1-sentence key lesson]
  - *Migration:* [`alternative-agent`](../agents/alternative-agent.md)

### Technical Design Flaws
- **[Agent Name](AGENT-NAME-YYYY-MM-DD.md)** - Deprecated YYYY-MM-DD
  - *Lesson:* [1-sentence key lesson]
  - *Migration:* [`alternative-agent`](../agents/alternative-agent.md)

### Superseded by Better Alternatives
- **[Agent Name](AGENT-NAME-YYYY-MM-DD.md)** - Deprecated YYYY-MM-DD
  - *Lesson:* [1-sentence key lesson]
  - *Migration:* [`alternative-agent`](../agents/alternative-agent.md)

### Strategic Misalignment
- **[Agent Name](AGENT-NAME-YYYY-MM-DD.md)** - Deprecated YYYY-MM-DD
  - *Lesson:* [1-sentence key lesson]
  - *Migration:* [`alternative-agent`](../agents/alternative-agent.md)

### Unsustainable Technical Debt
- **[Agent Name](AGENT-NAME-YYYY-MM-DD.md)** - Deprecated YYYY-MM-DD
  - *Lesson:* [1-sentence key lesson]
  - *Migration:* [`alternative-agent`](../agents/alternative-agent.md)

---

## Lessons Learned Index

Browse by lesson category:

### Multi-Agent Coordination Lessons
- [Agent 1 Death Certificate](LINK) - Learned: [lesson]
- [Agent 2 Death Certificate](LINK) - Learned: [lesson]

### User Experience Lessons
- [Agent 3 Death Certificate](LINK) - Learned: [lesson]
- [Agent 4 Death Certificate](LINK) - Learned: [lesson]

### Product Strategy Lessons
- [Agent 5 Death Certificate](LINK) - Learned: [lesson]

### Technical Architecture Lessons
- [Agent 6 Death Certificate](LINK) - Learned: [lesson]

---

## Wall of Failure (Badge of Honor)

**Total Agents Deprecated:** [count]
**Total Lessons Documented:** [count]
**Community Contributors:** [count of people who gave feedback on drafts]

**Most Valuable Death Certificate** (by community votes):
- [Agent Name](LINK) - [vote count] votes - [1-sentence why it's valuable]

**Most Controversial Deprecation** (by discussion volume):
- [Agent Name](LINK) - [comment count] comments - [1-sentence summary of debate]

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Agents Built | [count] |
| Total Agents Deprecated | [count] |
| Deprecation Rate | [X%] |
| Average Agent Lifespan | [X months] |
| Fastest Deprecation | [Agent Name] - [X weeks] |
| Longest-Lived Deprecated Agent | [Agent Name] - [X months] |

**Deprecation Trend:**
```
[ASCII art graph or link to visual]
Q1 2025: 2 deprecations
Q2 2025: 1 deprecation
Q3 2025: 3 deprecations
Q4 2025: 0 deprecations
```

---

## How to Read a Death Certificate

New to death certificates? Here's what each section tells you:

1. **Executive Summary:** The TL;DR - what failed and why
2. **Usage Statistics:** Hard data on adoption and satisfaction
3. **What Happened:** The full story - our hypothesis vs reality
4. **User Feedback:** Real quotes from users (unfiltered)
5. **What We Learned:** Actionable lessons for future agent design
6. **Migration Path:** Practical guide to switch to better alternative
7. **What We'd Do Differently:** Specific changes we'd make if starting over

---

## Contributing

**Found an error in a death certificate?** Open an issue or PR - we want these to be accurate.

**Have additional context to add?** If you were a user of a deprecated agent, we'd love to hear your perspective. Add a comment to the death certificate's discussion thread.

**Want to reference these in your own work?** Please do! Citation format:

```
ClaudeAgents Project. (YYYY). Agent Death Certificate: [Agent Name].
Retrieved from https://github.com/[repo]/death_certificates/AGENT-NAME-YYYY-MM-DD.md
```

---

## External Recognition

**Has our transparency inspired you?** We'd love to hear about it:

- **[Company/Project Name]** adopted death certificates for their feature deprecations
- **[Blog Post Title]** referenced our approach as best practice
- **[Conference Talk]** featured our gallery as case study in product transparency

[Submit a PR to add your reference!]

---

**Why This Matters**

In a field moving as fast as AI agents, we need to learn from failures as much as successes. By documenting what doesn't work, we collectively advance faster.

Every death certificate here represents:
- **Users** who trusted us with their workflows
- **Team members** who poured effort into building
- **Lessons** that make future agents better
- **Transparency** that builds community trust

Thank you for reading. Let's learn together.

---

*Gallery Last Updated: [YYYY-MM-DD]*
*Total Death Certificates: [count]*
*Community Contributors: [count]*
```

### Gallery Maintenance

**Quarterly Review (Every 3 Months):**
- [ ] Update statistics section with latest numbers
- [ ] Review "Most Valuable" rankings based on community votes
- [ ] Add any external references or recognition received
- [ ] Check all links are still valid
- [ ] Archive extremely old certificates to `archive/` if no longer relevant (>2 years)

**Annual Retrospective (Every 12 Months):**
- [ ] Publish blog post: "Year in Review: What Our Failures Taught Us"
- [ ] Aggregate top 10 lessons learned across all certificates
- [ ] Update product strategy based on deprecation patterns
- [ ] Present findings at team offsite or company all-hands

---

## 7. Success Metrics Dashboard

### Deprecation Process Health Metrics

**Operational Excellence:**

| Metric | Target | Measurement | Current |
|--------|--------|-------------|---------|
| **Timeline Adherence** | 100% of deprecations follow 30-day process | % on schedule | [TBD] |
| **User Notification** | 100% of affected users notified Day 7 | Email delivery confirmation | [TBD] |
| **Certificate Completeness** | 100% have all required sections | Checklist validation | [TBD] |
| **Migration Success** | 80% of affected users migrate to alternative | Alternative agent usage tracking | [TBD] |
| **Support Burden** | <10 support tickets per deprecation | Ticket tagging | [TBD] |

### Transparency Impact Metrics

**Community Trust:**

| Metric | Target | Measurement Method | Data Source |
|--------|--------|-------------------|-------------|
| **NPS Before/After** | <5 point drop, ideally +5 | Survey affected users pre/post deprecation | User surveys |
| **Death Certificate Engagement** | 100+ views per certificate in first 30 days | Analytics on death_certificates/ pages | GitHub traffic, web analytics |
| **Community Feedback** | 5+ substantive comments per draft | Count GitHub Discussion replies | GitHub API |
| **Positive Sentiment** | 70%+ positive or neutral reactions | Sentiment analysis of feedback | NLP analysis or manual coding |

**External Recognition:**

| Metric | Target | Measurement Method | Current |
|--------|--------|-------------------|---------|
| **Inbound Links** | 10+ external references per year | Backlink tracking | [Use Ahrefs or similar] |
| **Social Shares** | 50+ shares per certificate | Social media monitoring | [Twitter/LinkedIn analytics] |
| **Media Coverage** | 2+ articles mentioning approach | Media monitoring | [Google Alerts, PR tracking] |
| **Adoption by Others** | 3+ orgs adopt death certificate approach | Direct outreach + social listening | [Manual tracking] |

**Business Impact:**

| Metric | Target | Measurement Method | Insight |
|--------|--------|-------------------|---------|
| **Reduced Churn** | <5% user churn due to deprecation | Compare churn rate of affected users vs baseline | Proves good migration path |
| **Alternative Adoption** | 80% of deprecated agent users adopt alternative | Track alternative agent usage by previous users | Validates migration strategy |
| **Support Efficiency** | 30% fewer "why did you deprecate" tickets | Compare support volume with/without death certificates | Proves proactive communication works |
| **Trust Indicators** | 10% increase in new user signups citing transparency | Survey new users on why they chose platform | Proves transparency is competitive advantage |

### Dashboard Implementation

**Tool:** Google Data Studio / Looker / Custom Dashboard

**Page 1: Operational Health**
- Timeline adherence gauge (green if 100%, yellow if 90-99%, red if <90%)
- Table of active deprecations with status indicators
- Support ticket volume trend line
- Migration success rate by agent

**Page 2: Community Impact**
- NPS before/after deprecation (line chart over time)
- Death certificate engagement metrics (views, time on page, comments)
- Sentiment analysis breakdown (pie chart: positive/neutral/negative)
- Top 5 most-viewed death certificates

**Page 3: External Recognition**
- Inbound links over time (line chart)
- Social shares by certificate (bar chart)
- Media mentions timeline
- Organizations that adopted approach (list with links)

**Page 4: Lessons Learned**
- Word cloud of most common lessons across all certificates
- Deprecation causes breakdown (pie chart)
- Average agent lifespan before deprecation (histogram)
- Correlation analysis: Which initial characteristics predict deprecation?

### Reporting Cadence

**Weekly (Internal):**
- Product Manager reviews active deprecations dashboard
- Check for timeline slippage or support spikes
- Update stakeholders on any issues

**Monthly (Team):**
- Present deprecation metrics at product team meeting
- Discuss any patterns emerging
- Celebrate successful migrations

**Quarterly (Executives + Community):**
- Executive summary of deprecation activity
- Community blog post: "What We Learned This Quarter"
- Update death certificates gallery with stats
- Strategic review: Are we deprecating too much/too little?

**Annual (Public):**
- Publish comprehensive "Year in Failures" report
- Aggregate lessons learned across all certificates
- Share externally: Blog post, conference talk, GitHub Discussions
- Use insights to inform product strategy for next year

---

## 8. Email Templates

### Template A: Day 7 User Notification (Detailed)

**Subject:** Action Required: `[agent-name]` Agent Deprecation Notice (23 Days)

```
Hi [First Name],

We're writing to inform you that the `[agent-name]` agent will be deprecated on [DATE - 23 days from now].

WHY WE'RE DEPRECATING
[2-3 sentences in plain language. Be honest but not alarmist. Example:]

After 6 months of operation, we've found that the `[agent-name]` agent has a 15% task failure rate - significantly higher than our platform average of 4%. User satisfaction scores (2.8/5.0) indicate fundamental design issues that would require a complete rewrite to fix. Rather than maintain a subpar experience, we're deprecating this agent in favor of `[alternative-agent]`, which achieves the same goals with a 94% success rate and 4.5/5.0 satisfaction.

WHAT THIS MEANS FOR YOU
- The agent will continue working normally until [DATE]
- After [DATE], invoking `[agent-name]` will return an error with migration instructions
- Your existing workflows will need to be updated to use `[alternative-agent]`
- We estimate migration will take approximately [X minutes/hours] for typical usage

YOUR MIGRATION PATH
Recommended alternative: `[alternative-agent]`

Why it's better:
- [Key benefit 1: e.g., "94% task success rate vs 85% for old agent"]
- [Key benefit 2: e.g., "Native integration with [tool] - no manual exports needed"]
- [Key benefit 3: e.g., "Faster execution: 2 minutes vs 8 minutes average"]

Migration effort: [Realistic estimate: "5 minutes to update your prompts" or "30 minutes to restructure your workflow"]

Detailed migration guide: [link to documentation]

SUPPORT RESOURCES
We're here to help you transition:

1. **Migration Guide:** Step-by-step instructions at [link]
2. **Office Hours:** Join our live Q&A on [date] at [time] - [calendar link]
3. **1:1 Support:** Reply to this email to schedule a personal walkthrough
4. **Community Forum:** Ask questions and see others' migration experiences: [link]

UNDERSTANDING WHAT HAPPENED
On [DATE - Day 14], we'll publish a detailed "Agent Death Certificate" explaining exactly what went wrong and what we learned. This is our commitment to transparency - we document our failures as openly as our successes.

Preview the draft and provide feedback: [link when available on Day 14]

TIMELINE
- Today (Day 7): This notification
- [DATE - Day 14]: Death certificate draft published for community feedback
- [DATE - Day 21]: Final death certificate published
- [DATE - Day 30]: Agent officially deprecated

QUESTIONS?
- Reply to this email for 1:1 support
- Post in our forum: [link]
- Join office hours: [calendar link]

We know deprecations are disruptive. Thank you for your patience and for being part of our community as we learn and improve.

Best regards,
[Product Manager Name]
[Title]
[Email] | [Calendar Link]

P.S. If you prefer to continue using `[agent-name]` despite the deprecation, you can fork the agent definition from our GitHub repo and maintain it independently. We'll provide instructions in the death certificate.
```

### Template B: Day 21 Final Notice (Short)

**Subject:** Reminder: `[agent-name]` Agent Deprecation in 9 Days

```
Hi [First Name],

Quick reminder: The `[agent-name]` agent will be deprecated in 9 days on [DATE].

FINAL DEATH CERTIFICATE PUBLISHED
We've published the final death certificate documenting what happened and what we learned:
[link to death_certificates/AGENT-NAME-YYYY-MM-DD.md]

MIGRATION GUIDE READY
Step-by-step instructions to migrate to `[alternative-agent]`:
[link to migration guide]

NEED HELP?
- Reply to this email
- Office hours: [remaining dates/times]
- Forum: [link]

Thank you,
[Product Manager Name]
```

### Template C: Day 30 Deprecation Complete

**Subject:** `[agent-name]` Agent Deprecation Complete - Migration Path

```
Hi [First Name],

As of today, the `[agent-name]` agent has been officially deprecated.

WHAT'S CHANGED
- Invoking `[agent-name]` now returns: "This agent was deprecated on [DATE]. Use `[alternative-agent]` instead. Migration guide: [link]"
- The agent definition has been moved to our deprecated agents archive
- All documentation has been updated with migration instructions

YOUR NEXT STEPS
1. Update any saved prompts/workflows to use `[alternative-agent]`
2. Review the migration guide: [link]
3. Test your updated workflows

STILL NEED HELP?
We're still here to support your migration:
- Reply to this email
- Community forum: [link]
- Review the death certificate for full context: [link]

Thank you for your understanding as we work to maintain high-quality agents.

Best regards,
[Product Manager Name]

---

FEEDBACK REQUESTED
How did this deprecation process go for you? We'd love your input to improve future deprecations:
[link to 2-minute survey]
```

### Template D: Internal Announcement (Day 0)

**Subject:** [INTERNAL] Agent Deprecation Decision: `[agent-name]`

**Slack Message for #product-updates:**

```markdown
:warning: **Agent Deprecation Decision: `[agent-name]`**

We've decided to deprecate the `[agent-name]` agent effective [DATE - 30 days from now].

**Why:** [1-2 sentence honest summary - this is internal, be direct]

**Data:**
- Usage: [X invocations/month] (down from [Y] at peak)
- Satisfaction: [X.X/5.0]
- Affected users: [count]

**Migration Path:** Users will transition to `[alternative-agent]`

**Death Certificate:** Authoring team assigned, draft due Day 14

**Next Steps & Timeline:**
- Day 7: User notification emails sent
- Day 14: Draft death certificate published for community feedback
- Day 21: Final certificate published
- Day 30: Agent moved to `agents/deprecated/`

**Responsible Team:**
- PM: [name] - overall coordination
- Eng: [name] - technical deprecation
- Support: [name] - user migration assistance
- Docs: [name] - death certificate authoring

**Questions?** Reply in thread or DM @[product-manager]

**Deprecation Issue:** [link to project tracker]
```

---

## 9. Death Certificate Authoring Checklist

Use this checklist to ensure every death certificate meets quality standards before publishing:

### Pre-Draft (Day 7-10)

**Data Collection:**
- [ ] Usage statistics exported (invocations, MAU, satisfaction, success rate)
- [ ] User feedback compiled (support tickets, survey responses, interviews)
- [ ] Timeline of key events documented (launch, major updates, complaints, decision)
- [ ] Root cause analysis completed (engineering postmortem)
- [ ] Alternative agent identified and validated
- [ ] Migration guide drafted

**Team Assignments:**
- [ ] Product Manager assigned as primary author
- [ ] Technical Writer assigned for narrative sections
- [ ] Engineering Lead assigned for root cause analysis
- [ ] User Researcher assigned for feedback compilation
- [ ] Product Strategist assigned for lessons learned
- [ ] The-Critic assigned for honesty review

### Draft (Day 11-13)

**Content Completeness:**
- [ ] Executive Summary written (2-3 paragraphs, no jargon)
- [ ] "What We Tried to Build" section complete (vision, users, capabilities)
- [ ] Usage Statistics table filled with real data
- [ ] "What Happened" narrative written (honest story, not sanitized)
- [ ] Root causes identified (primary + secondary + missed assumptions)
- [ ] User Feedback section includes 3+ real quotes (positive + negative)
- [ ] "What We Learned" lists 5+ specific, actionable lessons
- [ ] Migration Path section provides clear alternative + guide
- [ ] "What We'd Do Differently" lists 3+ concrete changes
- [ ] Memorial section written (positive reflection)
- [ ] Technical appendix complete (links, references)

**Quality Standards:**
- [ ] All statistics are specific numbers, not vague ("8/month" not "low usage")
- [ ] User quotes are real, with attribution or anonymized properly
- [ ] No corporate jargon ("failed" not "strategic pivot", "sunset", "optimized")
- [ ] Root cause explains WHY it failed, not just WHAT happened
- [ ] Lessons are actionable (someone could apply them to their own agent)
- [ ] Tone is honest but not defensive or blame-shifting
- [ ] Migration path tested with at least 1 user

### Pre-Publish Review (Day 14)

**The-Critic Honesty Review:**
- [ ] No passive voice ("We failed" not "Mistakes were made")
- [ ] No euphemisms ("deprecated" is fine, but explain clearly why)
- [ ] No missing context (reader should understand full story)
- [ ] No blame-shifting (takes responsibility, doesn't blame users)
- [ ] Balanced (includes what worked, not just failures)
- [ ] Specific (uses real examples, not generalizations)

**Legal/Compliance Review:**
- [ ] No personally identifiable information in user quotes (anonymize if needed)
- [ ] No confidential business information disclosed
- [ ] No disparagement of competitors (factual comparisons OK)
- [ ] Complies with company transparency guidelines

**Final Checklist:**
- [ ] Proofread for typos, grammar, formatting
- [ ] All links work (use relative paths for internal links)
- [ ] Markdown renders correctly in preview
- [ ] Death certificate follows template structure exactly
- [ ] Authoring team reviewed and approved
- [ ] Product Manager signs off

### Post-Publish (Day 14-20)

**Community Feedback:**
- [ ] Draft published to `death_certificates/drafts/`
- [ ] Announcement posted in GitHub Discussions / forum
- [ ] Feedback form linked
- [ ] Team monitoring feedback channels daily
- [ ] Feedback compiled into document by Day 20

**Feedback Incorporation (Day 21):**
- [ ] Top 3-5 feedback items addressed (prioritize accuracy and clarity)
- [ ] Changes reviewed by original authoring team
- [ ] Final The-Critic review after changes
- [ ] Moved from `drafts/` to `death_certificates/`
- [ ] Gallery (`death_certificates/README.md`) updated with new entry
- [ ] Final announcement posted

---

## 10. Continuous Improvement

### Quarterly Deprecation Process Review

**Every 3 months, Product Manager conducts retrospective:**

**Agenda:**
1. Review all deprecations in past quarter (5 min)
2. Metrics review: Did we hit targets? (10 min)
3. User feedback themes: What did users say? (10 min)
4. Process issues: What went wrong? (10 min)
5. Improvements: What should we change? (10 min)
6. Update this document with learnings (5 min)

**Output:** Document improvements to deprecation workflow

### Annual Deprecation Strategy Review

**Every 12 months, Product Leadership reviews:**

1. **Deprecation Rate:** Are we deprecating too many/too few agents?
2. **Cause Patterns:** What types of failures are most common?
3. **Business Impact:** How does deprecation affect user trust, NPS, retention?
4. **External Recognition:** Is our transparency approach resonating?
5. **Strategic Adjustments:** Should we change how we build agents to reduce deprecations?

**Output:** Updated product strategy based on failure patterns

### Version History of This Document

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-09 | Initial version | Product Manager |
| [future] | [date] | [changes] | [author] |

---

## Appendix: FAQ

**Q: Do we have to deprecate agents that have low usage but high satisfaction?**
A: No. Low usage with high satisfaction (>4.0/5.0) indicates a valuable niche agent. Consider "maintenance mode" (no new features, but keep it working).

**Q: What if users strongly object to deprecation?**
A: Listen carefully. If 10+ users make a compelling case in the Day 14 feedback period, consider delaying deprecation to re-evaluate. Document this in the death certificate.

**Q: Can we deprecate faster than 30 days for critical security issues?**
A: Yes. For security or legal risks, follow expedited process:
- Day 0: Immediate disable (feature flag off)
- Day 1: Emergency notification to users
- Day 7: Death certificate published
- 30-day timeline not required for safety-critical deprecations

**Q: What if there's no good alternative agent?**
A: Don't deprecate until there is one. Either build the alternative first, or document manual workarounds in the death certificate. Never leave users stranded.

**Q: Who has final authority to approve deprecation?**
A: Product Manager, with Engineering Lead sign-off for technical feasibility and Product Strategist sign-off for strategic alignment. In case of disagreement, escalate to VP Product.

**Q: Do we need a death certificate for agents deprecated in first 30 days (failed beta)?**
A: Optional. For very short-lived agents (<90 days), a simplified "Lessons Learned" doc may suffice. Full death certificate recommended for any agent with >5 active users.

**Q: How do we handle users who refuse to migrate?**
A: Provide path to fork and self-host the deprecated agent. Include instructions in death certificate. We support the right to fork.

**Q: Can we un-deprecate an agent?**
A: Rarely, but yes. If post-deprecation we discover the alternative isn't adequate, we can un-deprecate. Document this in an addendum to the death certificate explaining what changed.

---

**End of Document**

*This workflow is a living document. If you see ways to improve it, open a PR or discuss with the Product Manager.*

*Version 1.0 - Published 2025-10-09*
