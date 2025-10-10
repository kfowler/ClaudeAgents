# Death Certificate: the-skeptic

**Agent Name:** the-skeptic
**Date of Creation:** 2024 (early agent)
**Date of Death:** 2025-10-10
**Lifespan:** ~12-18 months
**Tier:** Experimental
**Cause of Death:** Superseded by specialized contrarian triad

## Detailed Autopsy

**Symptoms Leading to Death:**
- Originally designed as general-purpose contrarian for all decision types
- Vague scope: "risk assessment, devil's advocate analysis" covered technical, business, and execution decisions
- Users couldn't tell when to use the-skeptic vs the-critic
- Sprint 17 introduced specialized contrarians (the-realist for business, the-pragmatist for execution) with clear boundaries
- the-skeptic became redundant: technical contrarian → the-critic, business contrarian → the-realist, execution contrarian → the-pragmatist

**Root Causes:**
- **Monolithic Contrarian Design**: One agent trying to challenge all decision types (technical, business, execution)
- **Overlapping with the-critic**: Both agents did "contrarian analysis" but unclear which to use when
- **No Clear Trigger**: Users didn't know: "Should I use the-skeptic or the-critic for this architecture decision?"
- **Sprint 17 Clarity**: Introduction of the-realist (business contrarian) and the-pragmatist (execution contrarian) made the-skeptic's role obsolete

## Lessons Learned

1. **Decision Type Determines Contrarian:** Technical decisions need technical contrarians (the-critic), business decisions need business contrarians (the-realist), execution decisions need execution contrarians (the-pragmatist). General-purpose contrarians create ambiguity.

2. **Vague Scope → Low Adoption:** the-skeptic was underutilized (7 total command references) because users couldn't articulate when to use it vs alternatives.

3. **Specialized Contrarians > General Contrarian:** the-critic (technical), the-realist (business), the-pragmatist (execution) provide clearer selection criteria and deeper domain expertise.

## Migration Path

**For users who might have used the-skeptic:**

**Use Case 1: Challenging technical/architectural decisions**
→ **Replacement:** `the-critic`
→ **Why:** Deep technical expertise in architecture, code quality, scalability, security. Produces structured DECISION_REPORT with dominant_axis, alternatives, false_tradeoffs, required_proofs.

**Use Case 2: Challenging business/market assumptions**
→ **Replacement:** `the-realist` (Sprint 17)
→ **Why:** Specialized in market sizing validation (TAM/SAM/SOM), revenue model reality checks, competitive dynamics, ROI analysis. Challenges optimistic projections with bottoms-up math.

**Use Case 3: Challenging execution/shipping timelines**
→ **Replacement:** `the-pragmatist` (Sprint 17)
→ **Why:** Focused on MVP scope validation, deadline feasibility, build vs buy assessment, resource allocation reality. Prevents scope creep and unrealistic commitments.

**Use Case 4: Automation decisions (should we automate this?)**
→ **Replacement:** `the-critic` with automation focus
→ **Why:** the-skeptic had AUTOMATION_ASSESSMENT output for "should we automate?" decisions. This capability moved to the-critic (structured DECISION_REPORT covers automation tradeoffs).

**Use Case 5: Multi-domain decisions (technical + business + execution)**
→ **Replacement:** `project-orchestrator` coordinates the-critic + the-realist + the-pragmatist
→ **Why:** Complex decisions spanning multiple domains (e.g., product launch) benefit from sequential or parallel contrarian analysis across all three specialists.

**Search Keyword Redirects:**
- "challenge assumptions", "devil's advocate", "risk assessment" (technical context) → `the-critic`
- "market validation", "ROI reality check", "business case challenge" → `the-realist`
- "deadline feasibility", "scope validation", "shipping challenge" → `the-pragmatist`
- "should we automate", "automation ROI" → `the-critic` (automation-focused DECISION_REPORT)

## Final Notes

the-skeptic served its purpose as the first contrarian agent, but DECISION-005 (Contrarian Agent Diversification, Sprint 17) demonstrated that decision type determines optimal contrarian:

- **Technical decisions** → the-critic (architecture, code quality, scalability)
- **Business decisions** → the-realist (market sizing, competitive analysis, ROI)
- **Execution decisions** → the-pragmatist (MVP scope, deadlines, build vs buy)

This specialization provides:
- **Clearer Selection**: Users know exactly which contrarian to engage
- **Deeper Expertise**: Domain-specific contrarians have 10x depth
- **Structured Outputs**: All three contrarians produce machine-readable JSON (DECISION_REPORT, DELIVERABILITY_ASSESSMENT)
- **Better Orchestration**: project-orchestrator can coordinate multi-contrarian debates for complex decisions

The death of the-skeptic validates: **Specialized contrarians with clear domains beat general-purpose skepticism.**

---

**Death Certificate prepared by:** code-architect, product-manager
**Date:** 2025-10-10
**Related Decision:** DECISION-005 (Contrarian Agent Diversification, Sprint 17)
