# Death Certificate: edge-computing-specialist

**Agent Name:** edge-computing-specialist
**Date of Creation:** 2024 (mid-year)
**Date of Death:** 2025-10-10
**Lifespan:** ~6-9 months
**Tier:** Extended
**Cause of Death:** Narrow focus, functional overlap, better served by generalists

## Detailed Autopsy

**Symptoms Leading to Death:**
- Narrow specialization: edge computing, CDN optimization, edge deployment
- Significant overlap with devops-engineer (deployment, infrastructure automation)
- Significant overlap with cloud-architect (multi-region architecture, latency optimization)
- Low adoption: edge computing is emerging but not yet mainstream for most users
- No command usage, minimal documentation references
- Better served by combining devops-engineer + cloud-architect expertise

**Root Causes:**
- **Premature Specialization**: Created agent for emerging technology before widespread demand
- **Unclear Boundaries**: Where does "edge computing" end and "cloud infrastructure" begin?
- **Better Generalist Coverage**: devops-engineer handles deployment (including edge platforms), cloud-architect handles multi-region architecture
- **Technology Still Evolving**: Edge computing patterns not yet stable enough for dedicated specialist

## Lessons Learned

1. **Validate Demand Before Specializing:** Edge computing is important but not yet common enough to justify dedicated agent. Most users solve edge problems with devops-engineer + cloud-architect.

2. **Emerging Tech Needs Stable Patterns:** Edge computing still evolving (Cloudflare Workers, AWS Lambda@Edge, Vercel Edge Functions, Deno Deploy all different). Wait for pattern stabilization before creating specialist.

3. **Generalists Can Handle Emerging Domains:** devops-engineer and cloud-architect already understand edge computing concepts (latency, geographic distribution, caching). They can handle edge cases without dedicated agent.

## Migration Path

**For users who might have used edge-computing-specialist:**

**Use Case 1: CDN deployment, edge caching, static asset optimization**
→ **Replacement:** `devops-engineer`
→ **Why:** CDN configuration (CloudFront, Cloudflare, Fastly) is infrastructure automation. devops-engineer handles deployment, caching strategies, and cache invalidation.

**Use Case 2: Edge functions (Cloudflare Workers, Lambda@Edge, Vercel Edge)**
→ **Replacement:** `full-stack-architect`
→ **Why:** Edge functions are JavaScript/TypeScript code running on edge nodes. full-stack-architect understands serverless patterns, API routing, and edge runtime constraints.

**Use Case 3: Multi-region architecture, geographic distribution, latency optimization**
→ **Replacement:** `cloud-architect`
→ **Why:** Multi-region deployment is cloud architecture discipline. cloud-architect designs for geographic distribution, failover, data residency, and latency optimization.

**Use Case 4: Edge storage, distributed databases (Cloudflare KV, Durable Objects)**
→ **Replacement:** `data-engineer` or `database-administrator`
→ **Why:** Distributed data systems require database expertise. data-engineer designs data pipelines, database-administrator handles replication and consistency.

**Use Case 5: Edge security, DDoS protection, WAF configuration**
→ **Replacement:** `security-audit-specialist` + `devops-engineer`
→ **Why:** Edge security combines security expertise (threat modeling, WAF rules) with infrastructure (CDN configuration). Two specialists in coordination.

**Use Case 6: Performance optimization at the edge (image optimization, compression)**
→ **Replacement:** `frontend-performance-specialist`
→ **Why:** Image optimization, compression, format selection (WebP, AVIF) are frontend performance concerns. Edge deployment is delivery mechanism.

**Search Keyword Redirects:**
- "CDN", "edge caching", "CloudFront", "Cloudflare", "Fastly" → `devops-engineer`
- "edge functions", "Cloudflare Workers", "Lambda@Edge", "Vercel Edge" → `full-stack-architect`
- "multi-region", "geographic distribution", "latency optimization" → `cloud-architect`
- "edge storage", "distributed database", "Cloudflare KV" → `data-engineer`
- "edge security", "DDoS", "WAF" → `security-audit-specialist` + `devops-engineer`
- "edge performance", "image optimization at edge" → `frontend-performance-specialist`

## Final Notes

The death of edge-computing-specialist reflects market reality: edge computing is growing but not yet mainstream enough for dedicated agent.

**Market Maturity Assessment:**
- **Cloud Computing (2015-2025)**: Mature, stable patterns → cloud-architect justified
- **Edge Computing (2020-2025)**: Emerging, evolving patterns → premature for dedicated agent
- **Prediction**: Edge computing will mature by 2027-2028. Revisit specialist then if demand warrants.

**Current State (2025):**
- Most edge use cases solved by generalists:
  - CDN deployment → devops-engineer
  - Edge functions → full-stack-architect
  - Multi-region architecture → cloud-architect
  - Edge performance → frontend-performance-specialist

**Future State (2027+):**
- If edge computing becomes dominant paradigm (edge-first architecture)
- If edge patterns stabilize (consensus on edge function patterns, edge database patterns)
- If user demand increases significantly (10+ requests for edge specialist)
- Then: Resurrect edge-computing-specialist with proven patterns

**Platform gains:**
- **Current Demand Met**: Generalists handle today's edge use cases effectively
- **Avoid Premature Specialization**: Wait for stable patterns before creating specialist
- **Future-Ready**: Can create edge specialist later when market demands it

**Users gain:**
- **Proven Expertise**: Generalists (devops, cloud-architect, full-stack) have battle-tested edge experience
- **No Confusion**: Clear agent selection (CDN → devops, edge functions → full-stack)
- **Better Today**: Generalists solve current edge problems; specialist would add minimal value now

This deprecation validates: **Create specialists when patterns stabilize and demand proves itself, not speculatively.**

---

**Death Certificate prepared by:** product-manager, cloud-architect, devops-engineer
**Date:** 2025-10-10
