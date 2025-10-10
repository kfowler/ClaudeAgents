# Death Certificate: platform-integrator

**Agent Name:** platform-integrator
**Date of Creation:** 2024 (early agent)
**Date of Death:** 2025-10-10
**Lifespan:** ~12-18 months
**Tier:** Experimental
**Cause of Death:** Vague scope, functional overlap, low adoption

## Detailed Autopsy

**Symptoms Leading to Death:**
- Unclear scope: "Cross-platform integration" is too vague
- What platforms? (Operating systems? Cloud providers? SaaS tools? APIs?)
- Overlaps with devops-engineer (CI/CD integration, deployment platforms)
- Overlaps with platform-engineering-specialist (internal platforms, developer tooling)
- Overlaps with full-stack-architect (API integration, third-party services)
- Low adoption: minimal command usage, no clear selection criteria
- Users didn't know when to choose platform-integrator vs alternatives

**Root Causes:**
- **Vague Naming**: "Platform" is ambiguous (OS platforms? Cloud platforms? Integration platforms? Internal platforms?)
- **No Clear Domain**: platform-integrator tried to cover too many integration types (cloud, API, OS, SaaS)
- **Better Specialists Exist**: devops-engineer (cloud/CI/CD), platform-engineering-specialist (internal platforms), full-stack-architect (API integration)
- **Premature Generalization**: Created before understanding which "platform integration" problems were common

## Lessons Learned

1. **Vague Names → Low Adoption:** Agents need crystal-clear scope. "Platform integration" could mean 10+ different things—users defaulted to clearer alternatives.

2. **Validate Problem Before Creating Agent:** platform-integrator was created speculatively. Should have waited for recurring user requests for specific integration patterns.

3. **Favor Specific over Generic:** "Kubernetes integration" (devops-engineer), "Stripe API integration" (full-stack-architect), "Internal developer platform" (platform-engineering-specialist) are clearer than "platform integration."

## Migration Path

**For users who might have used platform-integrator:**

**Use Case 1: CI/CD integration, deployment automation**
→ **Replacement:** `devops-engineer`
→ **Why:** Deep expertise in Jenkins, GitHub Actions, CircleCI, cloud deployment, container orchestration. "CI/CD platform integration" is core devops-engineer responsibility.

**Use Case 2: Internal developer platforms, tooling, self-service**
→ **Replacement:** `platform-engineering-specialist`
→ **Why:** Specializes in building internal platforms (golden paths, self-service tools, developer portals). This is the modern "platform team" focus.

**Use Case 3: Third-party API integration (Stripe, Twilio, SendGrid)**
→ **Replacement:** `full-stack-architect`
→ **Why:** API integration is core full-stack development. OAuth, webhooks, rate limiting, error handling—all full-stack-architect expertise.

**Use Case 4: Cloud platform integration (AWS, Azure, GCP)**
→ **Replacement:** `cloud-architect`
→ **Why:** Multi-cloud strategy, cost optimization, cloud-native architecture. Cloud platform expertise is cloud-architect's domain.

**Use Case 5: SaaS platform integration (Salesforce, Workday, ServiceNow)**
→ **Replacement:** `backend-api-engineer`
→ **Why:** Enterprise SaaS integration requires API design expertise, authentication patterns, data synchronization—backend-api-engineer handles this.

**Use Case 6: Operating system platform integration (Windows, macOS, Linux)**
→ **Replacement:** `macos-specialist`, `windows-specialist`, or `linux-sysadmin`
→ **Why:** OS-specific integration requires platform-specific expertise. No generalist can match specialists.

**Search Keyword Redirects:**
- "CI/CD integration", "deployment platform" → `devops-engineer`
- "internal platform", "developer portal", "self-service tooling" → `platform-engineering-specialist`
- "API integration", "third-party API", "OAuth", "webhooks" → `full-stack-architect`
- "cloud integration", "AWS", "Azure", "GCP" → `cloud-architect`
- "enterprise SaaS integration", "Salesforce API", "ServiceNow" → `backend-api-engineer`
- "OS integration", "macOS", "Windows", "Linux" → OS-specific specialist

## Final Notes

The death of platform-integrator demonstrates a critical principle: **Vague scope kills adoption.**

"Platform integration" could mean:
1. CI/CD platforms → devops-engineer
2. Internal platforms → platform-engineering-specialist
3. API platforms → full-stack-architect
4. Cloud platforms → cloud-architect
5. SaaS platforms → backend-api-engineer
6. OS platforms → macos-specialist/windows-specialist/linux-sysadmin

Users faced with this ambiguity chose clearer alternatives. The platform gains from this deprecation:

- **Clearer Selection**: Users know exactly which agent handles their integration type
- **Deeper Expertise**: Specialized agents have 10x depth in their domain
- **No Ambiguity**: "Stripe integration" → full-stack-architect (not "platform-integrator?")

This deprecation validates: **Agents must have clear, unambiguous scope. Generic names create confusion.**

---

**Death Certificate prepared by:** product-manager, code-architect
**Date:** 2025-10-10
