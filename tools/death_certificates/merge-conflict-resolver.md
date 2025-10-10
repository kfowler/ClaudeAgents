# Death Certificate: merge-conflict-resolver

**Agent Name:** merge-conflict-resolver
**Date of Creation:** 2024 (early agent)
**Date of Death:** 2025-10-10
**Lifespan:** ~12-18 months
**Tier:** Experimental
**Cause of Death:** Single-purpose tool, better handled by general agents

## Detailed Autopsy

**Symptoms Leading to Death:**
- Hyper-specific scope: only handles git merge conflicts
- Single-purpose tool better suited for general-purpose agents
- Merge conflicts are tactical, not strategic—don't justify dedicated agent
- No command usage, no documented examples
- Users already solving merge conflicts with full-stack-architect, code-architect, or domain specialists
- Git has native conflict resolution tools (mergetool, diff3)—agent adds minimal value

**Root Causes:**
- **Tool-Level Specialization**: Created agent for task-level problem (merge conflicts) rather than domain-level expertise
- **No Strategic Complexity**: Merge conflict resolution is mechanical: understand both sides, choose correct code, test
- **Better Alternatives Exist**: Domain specialists (full-stack-architect, backend-api-engineer) resolve conflicts in context better than generic conflict resolver
- **Git Native Tools**: git mergetool, diff3, semantic merge tools already handle most conflicts

## Lessons Learned

1. **Task-Level != Agent-Level:** Agents should embody domain expertise, not task automation. Merge conflicts are a task; software architecture is a domain.

2. **Context Matters in Conflict Resolution:** Resolving merge conflicts requires understanding the codebase, architecture, and intent. Domain specialists (who understand context) outperform generic conflict resolvers.

3. **Tool-Appropriate Granularity:** Some problems are better solved by tools (git mergetool, IDE conflict resolution) than AI agents. Agents add value when judgment and expertise are required.

## Migration Path

**For users who might have used merge-conflict-resolver:**

**Use Case 1: Frontend merge conflicts (React, Next.js, JavaScript)**
→ **Replacement:** `full-stack-architect`
→ **Why:** Understands component architecture, state management, styling patterns. Can resolve conflicts while maintaining architectural consistency.

**Use Case 2: Backend merge conflicts (API routes, database schemas)**
→ **Replacement:** `backend-api-engineer` or `data-engineer`
→ **Why:** Domain expertise in API design, database normalization, business logic. Resolves conflicts with architectural context.

**Use Case 3: Infrastructure/config merge conflicts (Kubernetes, Terraform)**
→ **Replacement:** `devops-engineer` or `infrastructure-as-code-specialist`
→ **Why:** Deep knowledge of infrastructure patterns, deployment configurations, environment management.

**Use Case 4: Documentation merge conflicts (README, docs)**
→ **Replacement:** `technical-writer`
→ **Why:** Expertise in documentation structure, clarity, consistency. Merges conflicting docs while improving overall quality.

**Use Case 5: Complex architectural conflicts (major refactors)**
→ **Replacement:** `code-architect`
→ **Why:** Holistic view of system architecture. Can assess which conflicting approach better serves long-term maintainability and scalability.

**Use Case 6: Test merge conflicts (unit tests, integration tests)**
→ **Replacement:** `qa-test-engineer`
→ **Why:** Understands test coverage, test design patterns, assertion strategies. Merges tests while improving coverage.

**General Approach:**
1. Identify conflict domain (frontend, backend, infrastructure, docs, tests)
2. Engage domain specialist for that area
3. Specialist resolves conflict with full architectural context
4. Run tests to validate resolution

**Search Keyword Redirects:**
- "merge conflict", "git conflict", "resolve conflict" + "frontend" → `full-stack-architect`
- "merge conflict" + "backend" → `backend-api-engineer`
- "merge conflict" + "infrastructure", "config" → `devops-engineer`
- "merge conflict" + "docs", "README" → `technical-writer`
- "merge conflict" + "complex", "architecture" → `code-architect`

## Final Notes

The death of merge-conflict-resolver demonstrates an important principle: **Agents should embody expertise, not automate tasks.**

Merge conflicts are symptoms of deeper issues:
- **Parallel development** → coordination problem (project-orchestrator)
- **Architectural divergence** → design problem (code-architect)
- **Unclear ownership** → organizational problem (product-manager)

Resolving the conflict is tactical; preventing conflicts is strategic. Domain specialists (full-stack-architect, backend-api-engineer) provide both:
1. **Tactical**: Resolve this specific conflict correctly
2. **Strategic**: Improve architecture to reduce future conflicts

**Platform gains:**
- **Context-Aware Resolution**: Domain specialists understand why code exists, not just syntax
- **Architectural Improvement**: Specialists use conflicts as opportunities to improve design
- **Reduced Agents**: One fewer task-level agent; domain specialists handle conflicts in context

**Users gain:**
- **Better Resolutions**: Conflicts resolved by specialists who understand the domain
- **Architectural Guidance**: Specialists explain why one approach beats another
- **Learning Opportunity**: Domain experts teach conflict resolution patterns

This deprecation validates: **General-purpose domain experts > single-purpose task automators.**

---

**Death Certificate prepared by:** code-architect, product-manager
**Date:** 2025-10-10
