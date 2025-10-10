# Growth Hacker Agent: Decision Framework

## Build Now If:

1. **User research validates specific need**
   - Conduct 10+ interviews with technical founders in next 2 weeks
   - Document failed attempts to solve growth problems with existing agents
   - Identify 3+ use cases that existing agents can't handle well

2. **Clear scope boundary established**
   - Define MVP as: "Product-led growth instrumentation and experimentation"
   - Exclude: paid acquisition, content marketing, SEO, viral mechanics (v2+)
   - Create differentiation matrix vs product-manager and data-engineer

3. **Resourcing doesn't delay Sprint 2**
   - Complete after current sprint commitments
   - OR: Explicitly deprioritize one existing roadmap item

## Build Later If:

1. **Demand signals emerge organically**
   - Users explicitly request "growth automation" features
   - Existing agents consistently fail at growth-related tasks
   - Community/market shows momentum for AI growth tools

2. **Scope can be proven minimal**
   - Prototype as commands (e.g., /growth-experiment-design) first
   - If commands get high usage → promote to agent
   - If commands see low adoption → kill the idea

3. **After core infrastructure stabilizes**
   - Sprint 2 complete, AIL ecosystem mature
   - Agent maintenance burden is manageable
   - Team has capacity for "nice to have" additions

## Don't Build If:

1. **No differentiation from existing agents**
   - User research shows prompting existing agents works fine
   - Growth tactics can be handled by product-manager + data-engineer combo
   - No unique methodology or framework that requires specialization

2. **"Growth hacker" can't be meaningfully scoped**
   - Scope keeps expanding in planning discussions
   - No agreement on what's in vs out for MVP
   - Domain expertise is too fragmented to codify

3. **Strategic misalignment**
   - Delays higher-priority infrastructure work
   - Doesn't fit the "professional development ecosystem" positioning
   - Better solved by templates/playbooks than agent intelligence

## Recommended Path Forward

**Option A: Validate First (RECOMMENDED)**
1. Create `/growth` command directory with 3-5 workflow commands:
   - `/growth:experiment-design` - A/B test implementation generator
   - `/growth:funnel-analysis` - Conversion funnel diagnostic
   - `/growth:instrumentation-setup` - Analytics tracking code generation
   - `/growth:activation-optimize` - Onboarding flow improvements
   - `/growth:referral-system` - Viral loop implementation

2. Use existing agents (product-manager, data-engineer, full-stack-architect)

3. Track usage for 4-6 weeks

4. If commands show high engagement → Build dedicated agent
   If commands see low usage → Kill with data

**Option B: Enhanced Product-Manager (ALTERNATIVE)**
Instead of new agent, extend product-manager with growth-specific capabilities:
- Add growth experimentation patterns
- Include activation/retention optimization prompts
- Enhance with statistical analysis for A/B tests
- Lower maintenance burden, clearer boundaries

**Option C: Build Now (NOT RECOMMENDED)**
Without user validation, this is speculative feature development. Risk:
- Agent gets built but not used (sunk cost)
- Overlaps with existing agents (confusion)
- Maintenance burden without proven value

## Success Metrics (If We Build)

**Leading Indicators:**
- Agent invocation frequency (target: 100+ uses in first month)
- User satisfaction ratings (target: 4.5+ / 5)
- Task completion rate (target: 85%+)

**Lagging Indicators:**
- User retention (do people come back for growth advice?)
- Growth tactic implementation rate (do people ship the suggestions?)
- Comparison: growth-hacker vs product-manager for growth tasks

**Kill Criteria:**
- < 50 uses in first month
- < 4.0 satisfaction rating
- Users consistently prefer other agents for growth tasks

## Next Steps Based on Decision

**If GO:**
1. User research: 10 founder interviews (2 weeks)
2. Scope definition: Write detailed agent spec (1 week)
3. Build MVP agent (3-4 weeks)
4. Beta test with 20 users (2 weeks)
5. Iterate based on feedback (ongoing)

**If WAIT:**
1. Implement Option A: growth commands (1 week)
2. Track usage data (4-6 weeks)
3. Revisit decision with data

**If NO-GO:**
1. Document decision and reasoning
2. Create growth-related templates for existing agents
3. Monitor for demand signals that might change decision