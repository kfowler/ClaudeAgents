# Agent Tier System - Quality-Based Organization

**Version:** 1.0
**Last Updated:** 2025-10-07
**Purpose:** Organize agents by quality, usage, and validation status

---

## Overview

The ClaudeAgents ecosystem uses a three-tier system to organize agents based on their proven value, usage patterns, and validation status. This helps users quickly identify the most reliable agents while allowing for innovation through experimental agents.

**Tier Structure:**
- **Core Tier** (10-15 agents): Battle-tested, highest quality, most-used
- **Extended Tier** (25-30 agents): Validated, domain-specific, proven value
- **Experimental Tier** (10-15 agents): Emerging, innovative, community-driven

---

## Core Tier (10-15 agents)

### Selection Criteria

✅ **Usage Metrics:**
- Top 15 most-invoked agents (via telemetry)
- Used in 50+ documented workflows
- Invoked in 30%+ of all agent requests

✅ **Quality Metrics:**
- >90% user satisfaction score
- <5% failure rate
- <10% unresolved issues/bugs

✅ **Validation:**
- Proven across 10+ real-world projects
- Documented success stories
- Community endorsement

### Core Tier Agents (Provisional List)

**Note:** Final list determined by telemetry data collection (Phase 2)

**Development (Provisional):**
1. **project-orchestrator** - Multi-agent coordination, complex projects
2. **full-stack-architect** - Web applications, React/Next.js, backend APIs
3. **backend-api-engineer** - RESTful/GraphQL APIs, server-side logic
4. **mobile-developer** - iOS/Android, React Native, Flutter

**Quality & Security:**
5. **security-audit-specialist** - Vulnerability assessment, compliance
6. **qa-test-engineer** - Testing strategies, automation
7. **code-architect** - Architecture review, code quality

**Infrastructure:**
8. **devops-engineer** - CI/CD, Docker, Kubernetes, cloud deployment
9. **data-engineer** - Data pipelines, analytics, databases

**Decision Support:**
10. **the-critic** - Technical decision analysis
11. **the-realist** - Business and market contrarian analysis

**Business:**
12. **product-strategist** - Market validation, competitive analysis

**Potential Additions (Pending Data):**
- frontend-performance-specialist (if high usage)
- llm-integration-architect, rag-systems-engineer (if high usage in AI projects)
- database-administrator (if operational DB needs common)

### Core Tier Benefits

**For Users:**
- ⚡ Fastest selection by orchestrator
- 📊 Highest confidence in recommendations
- 📚 Most comprehensive documentation
- 🎯 Proven workflows and examples

**For Agents:**
- 🏆 Featured in README and documentation
- 📈 Priority for improvements and updates
- 🔄 Regular validation and testing
- 💬 Active community support

### Core Tier Responsibilities

**Quality Standards:**
- Maintain >90% satisfaction
- Response time <24 hours for critical issues
- Comprehensive documentation
- Regular updates and improvements

**Support Commitments:**
- Quick bug fixes (critical: 24h, medium: 1 week)
- Backward compatibility maintained
- Clear deprecation notices (6 months minimum)
- Active community engagement

---

## Extended Tier (25-30 agents)

### Selection Criteria

✅ **Domain Expertise:**
- Specialized skills for specific use cases
- Validated through 10+ successful uses
- Fills important capability gaps

✅ **Quality Metrics:**
- >75% user satisfaction score
- <10% failure rate
- Documented use cases

✅ **Validation:**
- Proven in 5+ real-world projects
- Domain expert endorsement
- Community adoption

### Extended Tier Agents (Provisional List)

**Development Specialists:**
- systems-engineer (Rust, C++, Go, performance)
- functional-programmer (Haskell, Clojure, F#)
- game-development-engineer (Unity, Unreal Engine)
- blockchain-web3-engineer (Solidity, DeFi, NFTs)
- [DEPRECATED] embedded-iot-developer → systems-engineer

**Quality Specialists:**
- frontend-performance-specialist (Core Web Vitals)
- accessibility-expert (WCAG compliance)
- debugging-specialist (Advanced debugging)
- test-automation-engineer (Playwright, Cypress)

**Infrastructure Specialists:**
- cloud-architect (Multi-cloud strategy)
- infrastructure-as-code-specialist (Terraform, Pulumi)
- platform-engineering-specialist (Backstage, IDPs)
- [DEPRECATED] edge-computing-specialist → devops-engineer, cloud-architect
- observability-engineer (Distributed tracing, SLOs)
- [DEPRECATED] incident-coordinator → site-reliability-engineer
- database-administrator (Production DB operations)
- linux-sysadmin (System administration, OS hardening)

**SEO Specialists:**
- seo-meta-optimizer (Meta tags, Open Graph)
- seo-technical-auditor (Crawlability, indexability)
- seo-performance-specialist (Core Web Vitals for SEO)
- seo-keyword-strategist (Keyword research)
- seo-content-optimizer (On-page optimization)
- seo-structure-architect (Site architecture)

**Business & Operations:**
- business-analyst (Requirements, BRD, user stories)
- product-manager (Roadmap, feature prioritization)
- technical-writer (API docs, user guides)

**Specialized:**
- [DEPRECATED] platform-integrator → domain-specific specialists
- legacy-specialist (Legacy code migration)
- [DEPRECATED] merge-conflict-resolver → domain specialists

### Extended Tier Benefits

**For Users:**
- ⭐ Reliable for domain-specific tasks
- 📖 Good documentation coverage
- 🎯 Proven in specialized scenarios
- 🔍 Easy to discover via registry

**For Agents:**
- 📚 Listed in main documentation
- 🔄 Regular validation
- 💬 Community support available
- 📈 Path to Core Tier promotion

### Extended Tier Responsibilities

**Quality Standards:**
- Maintain >75% satisfaction
- Response time <1 week for issues
- Domain-specific documentation
- Quarterly validation reviews

**Support Commitments:**
- Bug fixes (critical: 1 week, medium: 1 month)
- Backward compatibility preferred
- Deprecation notices (3 months minimum)
- Community engagement encouraged

---

## Experimental Tier (10-15 agents)

### Selection Criteria

✅ **Innovation:**
- New capabilities not in Core/Extended
- Emerging technologies or approaches
- Community-requested functionality

✅ **Validation Status:**
- <5 real-world uses (early stage)
- Early adopter feedback
- Proof-of-concept validated

✅ **Emergence:**
- Emerged from usage pattern tracking
- Composite of existing agents
- Experimental new agent types

### Experimental Tier Agents

**Creative & Specialized:**
- creative-catalyst (Lateral thinking, Oblique Strategies)
- digital-artist (UI/UX graphics, game assets)
- video-director (Video production, editing)
- audio-engineer (Logic Pro, CoreAudio)
- 3d-modeler (Blender workflows)
- comedy-writer (Stand-up comedy, humor)
- tv-writer (Television scripts, procedurals)

**Niche Development:**
- [DEPRECATED] elisp-specialist → metaprogramming-specialist
- metaprogramming-specialist (Lisp, macros, DSLs)

**Emerging Composites** (Example placeholders):
- mobile-security-specialist (mobile-developer + security-audit-specialist)
- performance-accessibility-specialist (frontend-performance + accessibility-expert)
- data-ml-engineer (data-engineer + llm-integration-architect)

### Experimental Tier Characteristics

**For Users:**
- ⚠️ Use with caution (unproven at scale)
- 🧪 Experimental status clearly marked
- 💡 Innovative capabilities
- 📝 Feedback strongly encouraged

**For Agents:**
- 🚀 Rapid iteration allowed
- 🔄 No backward compatibility guarantees
- 💬 Direct user feedback integration
- 📊 Usage tracking for promotion

### Experimental Tier Lifecycle

**Promotion Path:**
1. **Created** - Initial agent definition
2. **Validated** - 5+ successful uses
3. **Refined** - Based on user feedback
4. **Promoted to Extended** - Meets Extended criteria
5. **Eventually Core** - If becomes widely used

**Deprecation Path:**
1. **Low adoption** - <5 uses in 6 months
2. **Community vote** - Is this agent valuable?
3. **Archive** - Move to `agents/archived/`
4. **Documentation** - Lessons learned preserved

---

## Tier Movement

### Promotion Process

**Experimental → Extended:**
- ✅ 5+ documented successful uses
- ✅ >75% satisfaction from early adopters
- ✅ No critical bugs outstanding
- ✅ Community endorsement

**Extended → Core:**
- ✅ Top 15 most-used agents
- ✅ >90% satisfaction score
- ✅ 50+ documented workflows
- ✅ Proven across 10+ projects

### Demotion Process

**Core → Extended:**
- ❌ Drops out of top 15 usage
- ❌ Satisfaction <85% for 3+ months
- ❌ Superseded by better agent
- ❌ Technology/approach obsolete

**Extended → Experimental:**
- ❌ <10 uses in 6 months
- ❌ Satisfaction <70%
- ❌ Multiple unresolved critical issues
- ❌ Community concerns

**Experimental → Archived:**
- ❌ <5 uses in 6 months
- ❌ No positive feedback
- ❌ Approach proven ineffective
- ❌ Community vote to archive

### Review Cadence

- **Core Tier:** Quarterly review
- **Extended Tier:** Semi-annual review
- **Experimental Tier:** Monthly review (first 3 months), then quarterly

---

## Using the Tier System

### For Users

**Choosing Agents:**
```python
# Orchestrator automatically prioritizes by tier
# Core agents selected first, then Extended, then Experimental

# Manual selection examples:
"Use core agents only" → orchestrator filters to Core tier
"Try experimental agents" → orchestrator considers Experimental
"Mobile development" → mobile-developer (Core) preferred over emerging composites
```

**Trust Levels:**
- **Core:** Use with confidence for production
- **Extended:** Reliable for domain-specific needs
- **Experimental:** Evaluate before production use

### For Contributors

**Creating New Agents:**
1. Start in Experimental tier
2. Gather 5+ successful uses
3. Document use cases and satisfaction
4. Apply for Extended tier promotion
5. Continue gathering data for Core consideration

**Improving Existing Agents:**
- Focus on Core tier (highest impact)
- Extended tier when domain expertise needed
- Experimental tier for innovation

---

## Tier Visualization

```
┌─────────────────────────────────────────────┐
│  CORE TIER (10-15 agents)                   │
│  ★★★★★ Battle-tested, highest quality       │
│  • project-orchestrator                     │
│  • full-stack-architect                     │
│  • security-audit-specialist                │
│  • ...                                      │
└─────────────────────────────────────────────┘
                    ▲
                    │ Promotion (top 15 usage, >90% sat)
                    │
┌─────────────────────────────────────────────┐
│  EXTENDED TIER (25-30 agents)               │
│  ★★★★ Validated, domain-specific           │
│  • frontend-performance-specialist          │
│  • seo-meta-optimizer                      │
│  • blockchain-web3-engineer                │
│  • ...                                      │
└─────────────────────────────────────────────┘
                    ▲
                    │ Promotion (5+ uses, >75% sat)
                    │
┌─────────────────────────────────────────────┐
│  EXPERIMENTAL TIER (10-15 agents)           │
│  ★★ Emerging, innovative, unproven         │
│  • creative-catalyst                        │
│  • mobile-security-specialist (composite)   │
│  • data-ml-engineer (composite)            │
│  • ...                                      │
└─────────────────────────────────────────────┘
```

---

## Success Metrics by Tier

### Core Tier Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Satisfaction | >90% | Post-task feedback |
| Failure Rate | <5% | Errors / Total invocations |
| Usage Frequency | Top 15 | Telemetry ranking |
| Response Time | <24h | Issue resolution time |
| Documentation | 100% | Completeness score |

### Extended Tier Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Satisfaction | >75% | Post-task feedback |
| Failure Rate | <10% | Errors / Total invocations |
| Domain Validation | 10+ uses | Successful completions |
| Response Time | <1 week | Issue resolution time |
| Documentation | >80% | Completeness score |

### Experimental Tier Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Early Adoption | 5+ uses | First 6 months |
| Positive Feedback | >50% | Early adopter satisfaction |
| Critical Bugs | 0 | Blocking issues |
| Innovation Value | Qualitative | Community assessment |

---

## Frequently Asked Questions

### Q: Can an agent be in multiple tiers?

**A:** No. Each agent belongs to exactly one tier at any time. However, agents can move between tiers based on performance.

### Q: How often are tier assignments reviewed?

**A:** Core (quarterly), Extended (semi-annual), Experimental (monthly initially, then quarterly).

### Q: What happens to deprecated agents?

**A:** Deprecated agents move to `agents/archived/` with documentation explaining why and suggesting alternatives.

### Q: Can users request tier changes?

**A:** Yes! Community feedback drives tier assignments. Submit evidence (usage data, satisfaction scores) via GitHub issues.

### Q: Do Experimental agents get less support?

**A:** Experimental agents get rapid iteration support but no backward compatibility guarantees. Core/Extended have formal support commitments.

### Q: How are composite agents (emergent) assigned tiers?

**A:** All new composite agents start in Experimental, regardless of their component agents' tiers.

---

## Implementation Timeline

**Phase 1 (Complete):**
- ✅ Tier system designed
- ✅ Criteria defined
- ✅ Documentation created

**Phase 2 (Weeks 1-4):**
- ⏳ Enable telemetry collection
- ⏳ Gather 50+ agent invocations
- ⏳ Calculate initial tier assignments

**Phase 3 (Weeks 5-8):**
- ⏳ Publish official tier assignments
- ⏳ Update README with tier badges
- ⏳ Implement tier filtering in orchestrator

**Phase 4 (Ongoing):**
- ⏳ Quarterly Core tier reviews
- ⏳ Semi-annual Extended tier reviews
- ⏳ Monthly Experimental reviews (first quarter)
- ⏳ Community-driven tier proposals

---

## Related Documentation

- [Agent Registry](../tools/agent_registry.py) - Semantic agent search
- [Emergence Tracking](../tools/agent_emergence.py) - Composite agent identification
- [Telemetry Guide](telemetry-guide.md) - Usage data collection
- [Strategic Roadmap](ROADMAP.md) - Long-term vision

---

**Maintained By:** project-orchestrator
**Status:** Phase 3 implementation
**Next Review:** After telemetry data collection (30 days)
**License:** MIT
