# Death Certificate: incident-coordinator

**Agent Name:** incident-coordinator
**Date of Creation:** 2024 (mid-year)
**Date of Death:** 2025-10-10
**Lifespan:** ~6-9 months
**Tier:** Extended
**Cause of Death:** Functional overlap with site-reliability-engineer

## Detailed Autopsy

**Symptoms Leading to Death:**
- Created as specialized incident response agent
- site-reliability-engineer already handles incident management (SRE core competency)
- Significant overlap: both agents handle war rooms, post-mortems, on-call processes
- Unclear differentiation: when to use incident-coordinator vs site-reliability-engineer?
- Low adoption despite operational focus (SRE agent preferred)
- Incident response is a subset of SRE, not a separate discipline

**Root Causes:**
- **Insufficient Differentiation**: incident-coordinator and site-reliability-engineer have 80%+ overlap in incident management
- **SRE Includes Incident Response**: Google's SRE methodology (which site-reliability-engineer follows) explicitly includes incident management as core competency
- **Premature Specialization**: Split incident response from SRE before validating need for separate agent
- **Better Holistic Approach**: SREs manage entire incident lifecycle (prevention, response, learning) better than coordinator focused only on response

## Lessons Learned

1. **Understand Discipline Scope Before Splitting:** SRE methodology inherently includes incident management. Splitting "incident coordination" from SRE fractures coherent discipline.

2. **Lifecycle > Single Phase:** site-reliability-engineer handles incident prevention (SLO engineering), response (coordination), and learning (post-mortems). incident-coordinator only handles response phase—worse user experience.

3. **Industry Standards Matter:** Google's SRE framework is industry standard. Following established methodologies (SRE includes incident management) beats custom role fragmentation.

## Migration Path

**For users who might have used incident-coordinator:**

**Use Case 1: Production incident response, war room coordination**
→ **Replacement:** `site-reliability-engineer`
→ **Why:** SRE methodology explicitly includes incident response as core competency. Google SRE book devotes entire chapters to incident management, on-call, and post-mortems.

**Use Case 2: Post-mortem analysis, blameless retrospectives**
→ **Replacement:** `site-reliability-engineer`
→ **Why:** SREs own the full incident lifecycle: prevention (SLO engineering) → detection (monitoring) → response (war rooms) → learning (post-mortems). Post-mortems inform SLO improvements.

**Use Case 3: On-call runbooks, incident playbooks**
→ **Replacement:** `site-reliability-engineer`
→ **Why:** Runbook creation is SRE discipline. SREs understand operational patterns, common failures, and recovery procedures.

**Use Case 4: Incident metrics, MTTR tracking, incident trends**
→ **Replacement:** `site-reliability-engineer`
→ **Why:** SLO/SLI framework tracks incident impact, error budgets, and reliability trends. MTTR, MTTD, MTTF are SRE metrics.

**Use Case 5: Incident communication, stakeholder updates**
→ **Replacement:** `site-reliability-engineer`
→ **Why:** SREs coordinate cross-team communication during incidents. Incident commander role (from SRE methodology) handles stakeholder updates.

**Use Case 6: Chaos engineering, failure injection testing**
→ **Replacement:** `site-reliability-engineer`
→ **Why:** SREs use chaos engineering to proactively find weaknesses before incidents. Gamedays, failure injection, and resilience testing are SRE practices.

**Search Keyword Redirects:**
- "incident response", "war room", "production incident" → `site-reliability-engineer`
- "post-mortem", "incident retrospective", "blameless culture" → `site-reliability-engineer`
- "on-call", "runbook", "incident playbook" → `site-reliability-engineer`
- "MTTR", "incident metrics", "reliability tracking" → `site-reliability-engineer`
- "chaos engineering", "failure injection", "gameday" → `site-reliability-engineer`

## Final Notes

The death of incident-coordinator is not a failure—it's a consolidation based on industry best practices.

**SRE Incident Lifecycle (from Google SRE book):**
1. **Prevention**: SLO engineering, error budgets, reliability design
2. **Detection**: Monitoring, alerting, symptom-based alerts
3. **Response**: Incident command, war rooms, mitigation
4. **Learning**: Post-mortems, action items, SLO refinement

incident-coordinator only handled #3 (Response). site-reliability-engineer handles the full lifecycle—better for users:

**Users gain:**
- **Complete Incident Lifecycle**: One agent handles prevention, response, AND learning
- **Coherent Methodology**: SRE framework provides proven incident management patterns
- **Better Context**: SRE understands system reliability holistically, not just incident response
- **Industry-Standard Practices**: Google SRE methodology is battle-tested at scale

**Platform gains:**
- **Reduced Overlap**: Eliminate 80% functional duplication between two agents
- **Clearer Selection**: "Incident response" → site-reliability-engineer (obvious)
- **Methodology Alignment**: Follow industry-standard SRE practices, not custom role fragmentation

This deprecation validates: **Follow established industry methodologies. SRE includes incident management; don't fragment coherent disciplines.**

---

**Death Certificate prepared by:** site-reliability-engineer, code-architect, product-manager
**Date:** 2025-10-10
