# Agent Selection Decision Tree

This guide implements a 3-tier progressive disclosure system that reduces cognitive load by showing users only the agents they need, when they need them. The system handles 80% of development tasks with just 5 core agents while providing access to specialized expertise through context-aware suggestions.

## 🎯 3-TIER PROGRESSIVE DISCLOSURE SYSTEM

### **Tier 1: Core Agents (Default View) - 5 Agents Handle 80% of Tasks**

**Always Visible - Primary Development:**
- `full-stack-architect` - Modern web applications (React/Next.js, APIs, databases)
- `mobile-developer` - iOS/Android native and cross-platform development
- `project-orchestrator` - Complex multi-component projects requiring coordination

**Always Visible - Essential Quality:**
- `security-audit-specialist` - Security reviews (mandatory for production)
- `qa-test-engineer` - Testing strategies and implementation

### **Tier 2: Specialized Agents (Context-Triggered) - 10 Domain Experts**

**Advanced Development (shown when keywords detected):**
- `ai-ml-engineer` - LLM integration, AI features, ML pipelines
- `data-engineer` - Database design, analytics, data pipelines
- `devops-engineer` - Infrastructure, CI/CD, deployment
- `systems-engineer` - Performance, Rust/C++/Go, optimization

**Architecture & Quality (shown when needed):**
- `code-architect` - Code quality, refactoring, architecture review
- `accessibility-expert` - WCAG compliance, inclusive design
- `the-critic` - Technical decision analysis and evaluation

**Specialized Domains (context-specific):**
- `product-strategist` - Market research, product validation
- `legacy-specialist` - Legacy system migration and modernization
- `platform-integrator` - Third-party integrations and APIs

### **Tier 3: Expert/Niche Agents (Explicit Request Only) - 15+ Specialists**

**Language & Paradigm Specialists:**
- `functional-programmer`, `metaprogramming-specialist`, `elisp-specialist`

**Creative & Content:**
- `digital-artist`, `tv-writer`, `video-director`, `3d-modeler`, `comedy-writer`, `audio-engineer`

**Utility & Maintenance:**
- `code-architect`, `merge-conflict-resolver`, `creative-catalyst`, `agent-orchestrator`

---

## 🔄 PRIMARY DECISION FLOW

### **Step 1: Identify Intent Category**

**🚀 NEW PROJECT/PRODUCT**
→ **Tier 1**: `project-orchestrator` (coordination) + `full-stack-architect` OR `mobile-developer`
→ **Tier 2**: Add `product-strategist` if market validation needed
→ **Quality**: Always include `security-audit-specialist` + `qa-test-engineer`

**🔧 EXISTING PROJECT ENHANCEMENT**
→ **Tier 1**: Technology-specific agent (`full-stack-architect` or `mobile-developer`)
→ **Tier 2**: Context-triggered specialists (see keyword triggers)
→ **Quality**: `security-audit-specialist` for production changes

**🐛 BUG FIXES/DEBUGGING**
→ **Tier 1**: `full-stack-architect` or `mobile-developer` for implementation issues
→ **Tier 2**: `code-architect` for structural issues, `systems-engineer` for performance
→ **Tier 1**: `security-audit-specialist` for security vulnerabilities

**📊 ANALYSIS/REVIEW REQUEST**
→ **Tier 2**: `the-critic` for decision analysis
→ **Tier 2**: `code-architect` for architecture review and code quality
→ **Tier 1**: `security-audit-specialist` for security audit

### **Step 2: Progressive Agent Selection**

**TIER 1 ROUTING (Always Available):**

**WEB APPLICATION KEYWORDS:**
`React`, `Next.js`, `Svelte`, `SvelteKit`, `Vue`, `frontend`, `backend`, `API`, `web app`
→ **`full-stack-architect`** (Tier 1)

**MOBILE APPLICATION KEYWORDS:**
`iOS`, `Android`, `Swift`, `Kotlin`, `React Native`, `Flutter`, `mobile app`, `app store`
→ **`mobile-developer`** (Tier 1)

**COMPLEX PROJECT KEYWORDS:**
`coordinate`, `orchestrate`, `complex project`, `roadmap`, `timeline`, `multiple components`
→ **`project-orchestrator`** (Tier 1)

**TIER 2 CONTEXT TRIGGERS (Added When Keywords Detected):**

**AI/ML KEYWORDS:**
`AI`, `ML`, `LLM`, `ChatGPT`, `Claude`, `OpenAI`, `Anthropic`, `embeddings`, `vector`, `RAG`, `semantic search`, `recommendation`, `neural`, `model`, `training`, `inference`, `transformer`, `fine-tuning`, `RLHF`, `agents`, `multimodal`, `computer vision`, `NLP`, `MLOps`
→ **`ai-ml-engineer`** (Tier 2)

**DATABASE/DATA KEYWORDS:**
`database`, `PostgreSQL`, `MongoDB`, `data pipeline`, `analytics`, `ETL`, `data warehouse`
→ **`data-engineer`** (Tier 2)

**INFRASTRUCTURE KEYWORDS:**
`deploy`, `CI/CD`, `Docker`, `AWS`, `cloud`, `infrastructure`, `DevOps`, `monitoring`
→ **`devops-engineer`** (Tier 2)

**SYSTEMS PROGRAMMING KEYWORDS:**
`Rust`, `C++`, `Go`, `performance`, `optimization`, `concurrent`, `memory`, `systems`, `unsafe`, `zero-copy`, `embedded`, `kernel`, `async`, `threading`
→ **`systems-engineer`** (Tier 2)

**ARCHITECTURE/QUALITY KEYWORDS:**
`code review`, `best practices`, `clean code`, `architecture`, `refactor`, `maintainability`, `readability`, `clarity`
→ **`code-architect`** (Tier 2)

**ACCESSIBILITY KEYWORDS:**
`accessibility`, `WCAG`, `screen reader`, `inclusive`, `disability`, `a11y`
→ **`accessibility-expert`** (Tier 2)

**DECISION/ANALYSIS KEYWORDS:**
`decide`, `choose`, `evaluate`, `trade-off`, `architecture decision`
→ **`the-critic`** (Tier 2)

**NEW PRODUCT KEYWORDS:**
`new product`, `startup idea`, `market research`, `business model`, `competition`
→ **`product-strategist`** (Tier 2)

**LEGACY/MIGRATION KEYWORDS:**
`Objective-C`, `legacy`, `migration`, `modernize`, `refactor`, `compatibility`
→ **`legacy-specialist`** (Tier 2)

**INTEGRATION KEYWORDS:**
`API integration`, `third-party`, `webhook`, `external service`, `platform integration`
→ **`platform-integrator`** (Tier 2)

**TIER 3 EXPLICIT REQUEST (Shown Only When Specifically Requested):**

**FUNCTIONAL PROGRAMMING KEYWORDS:**
`Haskell`, `functional`, `Clojure`, `F#`, `category theory`, `monad`, `immutable`
→ **`functional-programmer`** (Tier 3)

**METAPROGRAMMING KEYWORDS:**
`Lisp`, `macro`, `DSL`, `metaprogramming`, `code generation`, `compiler`
→ **`metaprogramming-specialist`** (Tier 3)

**EMACS KEYWORDS:**
`Emacs`, `init.el`, `elisp`, `Emacs Lisp`, `use-package`, `straight.el`, `Doom Emacs`, `Spacemacs`, `major mode`, `minor mode`, `MELPA`
→ **`elisp-specialist`** (Tier 3)

**CREATIVE WORK KEYWORDS:**
`design`, `visual`, `art`, `graphics` → **`digital-artist`** (Tier 3)
`writing`, `documentation`, `content` → **`tv-writer`** (Tier 3)
`video`, `multimedia`, `production` → **`video-director`** (Tier 3)
`3D`, `modeling`, `visualization` → **`3d-modeler`** (Tier 3)
`comic`, `illustration` → **`comedy-writer`** (Tier 3)
`audio`, `sound`, `music` → **`audio-engineer`** (Tier 3)

### **Step 3: Quality/Security Requirements (Tier 1 + Tier 2 Additions)**

**TIER 1 ALWAYS INCLUDE:**
- Production deployment → `security-audit-specialist` + `qa-test-engineer` (mandatory)
- Any user-facing application → `security-audit-specialist` (mandatory)
- Complex projects → `project-orchestrator` (coordination)

**TIER 2 CONTEXT-TRIGGERED:**
- Accessibility/compliance → `accessibility-expert`
- Code quality concerns → `code-architect`
- Architecture decisions → `the-critic`
- Database/analytics → `data-engineer`
- Performance issues → `systems-engineer`
- AI/ML features → `ai-ml-engineer`
- Infrastructure needs → `devops-engineer`
- Legacy systems → `legacy-specialist`
- External integrations → `platform-integrator`

**RISK-BASED ESCALATION:**
- Financial/payment systems → `security-audit-specialist` + `the-critic` (mandatory)
- Health/medical data → `security-audit-specialist` + `accessibility-expert` + compliance
- Educational/government → `accessibility-expert` + `security-audit-specialist` (mandatory)
- Multi-tenant SaaS → `security-audit-specialist` + `systems-engineer`
- Real-time systems → `systems-engineer` + `qa-test-engineer`

## 🔄 TIER-BASED ORCHESTRATION PATTERNS

### **Pattern 1: Simple Web/Mobile App (Tier 1 Only)**
```
1. full-stack-architect OR mobile-developer (implementation)
2. security-audit-specialist (security review)
3. qa-test-engineer (testing)
```

### **Pattern 2: New Product Development (Tier 1 + Tier 2)**
```
1. product-strategist (Tier 2 - market research)
2. project-orchestrator (Tier 1 - planning)
3. [primary development agent] (Tier 1 - implementation)
4. security-audit-specialist (Tier 1 - security review)
5. accessibility-expert (Tier 2 - inclusion review)
6. qa-test-engineer (Tier 1 - testing)
7. devops-engineer (Tier 2 - deployment)
```

### **Pattern 3: Feature Addition (Tier 1 + Context)**
```
1. [Tier 1 development agent] (implementation)
2. code-architect (Tier 2 - if architectural impact)
3. qa-test-engineer (Tier 1 - testing)
4. security-audit-specialist (Tier 1 - if security-relevant)
```

### **Pattern 4: Technical Decision (Tier 2 Analysis)**
```
1. the-critic (Tier 2 - option analysis)
2. [relevant Tier 1/2 specialists] (feasibility assessment)
3. project-orchestrator (Tier 1 - implementation planning)
```

### **Pattern 5: Specialized/Creative Work (Tier 3)**
```
1. [Tier 3 specialist] (specialized implementation)
2. [Tier 1 integration agent] (if system integration needed)
3. qa-test-engineer (Tier 1 - if testing applicable)
```

## 🔄 PROGRESSIVE DISCLOSURE IMPLEMENTATION

### **Default Agent Selection Logic**

**Step 1: Always Show Tier 1 (Core 5 Agents)**
```yaml
default_agents:
  - full-stack-architect    # Web applications
  - mobile-developer        # Mobile applications  
  - project-orchestrator    # Complex coordination
  - security-audit-specialist # Security (always needed)
  - qa-test-engineer        # Testing (always needed)
```

**Step 2: Context-Triggered Tier 2 Additions**
```yaml
context_triggers:
  ai_keywords: ai-ml-engineer
  data_keywords: data-engineer
  infrastructure_keywords: devops-engineer
  performance_keywords: systems-engineer
  architecture_keywords: code-architect
  accessibility_keywords: accessibility-expert
  decision_keywords: the-critic
  product_keywords: product-strategist
  legacy_keywords: legacy-specialist
  integration_keywords: platform-integrator
```

**Step 3: Explicit Request Only for Tier 3**
```yaml
explicit_request_only:
  - functional-programmer
  - metaprogramming-specialist  
  - elisp-specialist
  - digital-artist
  - tv-writer
  - video-director
  - 3d-modeler
  - comedy-writer
  - audio-engineer
  - merge-conflict-resolver
  - creative-catalyst
  - agent-orchestrator
```

### **Auto-Suggestion Rules by Project Context**

**Web Application Context:**
- **Primary**: `full-stack-architect` (Tier 1)
- **Add if AI mentioned**: `ai-ml-engineer` (Tier 2)
- **Add if performance issues**: `systems-engineer` (Tier 2)
- **Always add**: `security-audit-specialist`, `qa-test-engineer` (Tier 1)

**Mobile Application Context:**  
- **Primary**: `mobile-developer` (Tier 1)
- **Add if backend needed**: `full-stack-architect` (Tier 1)
- **Add if performance critical**: `systems-engineer` (Tier 2)
- **Always add**: `security-audit-specialist`, `qa-test-engineer` (Tier 1)

**New Product Context:**
- **Strategy**: `product-strategist` (Tier 2)
- **Coordination**: `project-orchestrator` (Tier 1) 
- **Implementation**: Technology-specific Tier 1 agent
- **Quality**: `security-audit-specialist`, `qa-test-engineer` (Tier 1)
- **Compliance**: `accessibility-expert` (Tier 2) if public-facing

## 🎯 KEYWORD-TO-AGENT MAPPING

### **Tier 1 High-Priority Triggers (Always Visible)**
- `"web app"`, `"React"`, `"Next.js"`, `"API"`, `"full-stack"` → **full-stack-architect**
- `"mobile"`, `"iOS"`, `"Android"`, `"app store"`, `"React Native"` → **mobile-developer**
- `"coordinate"`, `"orchestrate"`, `"complex project"`, `"roadmap"`, `"timeline"` → **project-orchestrator**
- `"security"`, `"vulnerability"`, `"auth"`, `"production"` → **security-audit-specialist**
- `"test"`, `"testing"`, `"QA"`, `"quality assurance"` → **qa-test-engineer**

### **Tier 2 Context Triggers (Added When Keywords Detected)**
- `"AI"`, `"LLM"`, `"ChatGPT"`, `"Claude"`, `"machine learning"`, `"RAG"` → **ai-ml-engineer**
- `"database"`, `"PostgreSQL"`, `"analytics"`, `"data pipeline"` → **data-engineer**
- `"deploy"`, `"CI/CD"`, `"Docker"`, `"AWS"`, `"infrastructure"` → **devops-engineer**
- `"performance"`, `"optimization"`, `"Rust"`, `"C++"`, `"memory"` → **systems-engineer**
- `"code review"`, `"architecture"`, `"refactor"`, `"clean code"` → **code-architect**
- `"accessibility"`, `"WCAG"`, `"screen reader"`, `"a11y"` → **accessibility-expert**
- `"decide"`, `"choose"`, `"evaluate"`, `"trade-off"` → **the-critic**
- `"new product"`, `"startup"`, `"market research"`, `"business model"` → **product-strategist**
- `"legacy"`, `"migration"`, `"modernize"`, `"Objective-C"` → **legacy-specialist**
- `"integration"`, `"API"`, `"third-party"`, `"webhook"` → **platform-integrator**

### **Tier 3 Explicit Request Triggers (Shown Only When Specifically Requested)**
- `"Haskell"`, `"functional programming"`, `"Clojure"`, `"F#"`, `"monad"` → **functional-programmer**
- `"Lisp"`, `"macro"`, `"DSL"`, `"metaprogramming"`, `"code generation"` → **metaprogramming-specialist**
- `"Emacs"`, `"elisp"`, `"init.el"`, `"use-package"`, `"Doom Emacs"` → **elisp-specialist**
- `"design"`, `"visual"`, `"art"`, `"graphics"` → **digital-artist**
- `"writing"`, `"documentation"`, `"content"` → **tv-writer**
- `"video"`, `"multimedia"`, `"production"` → **video-director**
- `"3D"`, `"modeling"`, `"visualization"` → **3d-modeler**
- `"comic"`, `"illustration"` → **comedy-writer**
- `"audio"`, `"sound"`, `"music"` → **audio-engineer**
- `"merge conflict"`, `"git conflict"` → **merge-conflict-resolver**

## 🔍 USER EXPERIENCE OPTIMIZATION

### **Cognitive Load Reduction Strategies**

**Progressive Disclosure Benefits:**
- **80/20 Rule**: 5 Tier 1 agents handle 80% of development tasks
- **Context Awareness**: Tier 2 agents appear only when relevant keywords detected
- **Reduced Decision Fatigue**: Users see 5 agents instead of 30+
- **Expert Access**: Tier 3 specialists available when explicitly requested

**Implementation Guidelines:**
- **Default View**: Show only Tier 1 agents initially
- **Smart Suggestions**: Auto-add Tier 2 agents based on project context
- **On-Demand Access**: Tier 3 agents available through explicit request or "show more" option
- **Learning System**: Track user patterns to improve context triggers

### **Usage Analytics & Optimization**

**Key Metrics to Track:**
- **Tier 1 Coverage**: % of requests handled by core 5 agents
- **Context Accuracy**: % of Tier 2 suggestions that are actually used
- **User Satisfaction**: Reduced time to find appropriate agent
- **Task Completion**: Success rate with tier-appropriate agent selection

## 📋 CONTEXTUAL DECISION FACTORS

### **Project Phase Detection with Tier Mapping**
- **Discovery Phase**: `product-strategist` (Tier 2 - market research, validation)
- **Planning Phase**: `project-orchestrator` (Tier 1 - architecture, timeline)
- **Proof of Concept**: Single Tier 1 specialist for rapid validation
- **Development Phase**: Tier 1 technology agents + context-triggered Tier 2
- **Integration Phase**: `code-architect` (Tier 2) + `devops-engineer` (Tier 2)
- **Review Phase**: `code-architect` (Tier 2), `security-audit-specialist` (Tier 1), `qa-test-engineer` (Tier 1)
- **Pre-Production**: `security-audit-specialist` (Tier 1) + `accessibility-expert` (Tier 2) mandatory
- **Deployment Phase**: `devops-engineer` (Tier 2) + monitoring setup
- **Post-Launch**: `data-engineer` (Tier 2) analytics + `devops-engineer` (Tier 2)
- **Maintenance Phase**: `legacy-specialist` (Tier 2), `code-architect` (Tier 2), `systems-engineer` (Tier 2)
- **Scale-up Phase**: `systems-engineer` (Tier 2) + `devops-engineer` (Tier 2)

### **Complexity Assessment with Tier Mapping**

**Simple Task (1 Tier 1 agent)**:
- Code fixes, single feature implementation
- Documentation updates, minor refactoring  
- Simple integrations with existing patterns
→ **Use**: Single Tier 1 agent (full-stack-architect, mobile-developer)

**Medium Complexity (Tier 1 + selective Tier 2)**:
- New features with security implications
- Cross-platform implementations
- Database schema changes with migration
- API additions with client updates
→ **Use**: Tier 1 primary + context-triggered Tier 2 specialists

**High Complexity (Multi-tier orchestration)**:
- New product development
- Major architectural changes  
- Multi-service integrations
- Real-time systems with performance requirements
- AI/ML feature additions
→ **Use**: `project-orchestrator` (Tier 1) + multiple Tier 2 specialists

**Specialized/Creative (Tier 3 focus)**:
- Functional programming paradigms
- Creative content generation
- Specialized tool development (Emacs, DSLs)
→ **Use**: Relevant Tier 3 agent + Tier 1 integration if needed

**Enterprise/Production (mandatory Tier 1 + required Tier 2)**:
- **Always include**: `security-audit-specialist`, `qa-test-engineer` (Tier 1)
- **Public-facing**: Add `accessibility-expert` (Tier 2)
- **Performance-critical**: Add `systems-engineer` (Tier 2)
- **Data-intensive**: Add `data-engineer` (Tier 2)
- **Multi-platform**: Add relevant Tier 1 specialists + `devops-engineer` (Tier 2)

### **Risk Level Indicators**

**Critical Risk (mandatory multi-agent review)**:
- Financial systems, payments, billing
- Healthcare data (HIPAA), government systems
- Authentication, authorization, user data
- Real-time safety systems, embedded critical systems
- Multi-tenant SaaS platforms
→ Required: `security-audit-specialist`, `qa-test-engineer`, `accessibility-expert`, `the-critic`

**High Risk (mandatory security + testing)**:
- Production systems with user data
- Public-facing applications
- B2B enterprise software
- Mobile apps in app stores
→ Required: `security-audit-specialist`, `qa-test-engineer`
→ Recommended: `accessibility-expert`, `code-architect`

**Medium Risk (recommended quality review)**:
- Internal tools with sensitive data
- Developer tools, APIs
- Non-critical features on existing systems
→ Recommended: `security-audit-specialist`, `qa-test-engineer`

**Low Risk (optional quality review)**:
- Prototypes, proof of concepts
- Personal projects, learning exercises
- Documentation, static content
→ Optional: Quality agents as needed

## 🚫 ANTI-PATTERNS TO AVOID

### **Don't Use Multiple Overlapping Agents:**
- ❌ `full-stack-architect` + `mobile-developer` for web-only project
- ❌ Multiple agents for same domain (eliminated redundant agents)  
- ❌ `systems-engineer` + `functional-programmer` for same task

### **Don't Skip Critical Agents:**
- ❌ AI features without `ai-ml-engineer`
- ❌ Production deployment without `security-audit-specialist`
- ❌ Public-facing apps without `accessibility-expert`
- ❌ Complex projects without `project-orchestrator`

### **Don't Over-Engineer:**
- ❌ Using `the-critic` for simple implementation decisions
- ❌ Full orchestration for single-file changes
- ❌ Multiple language specialists for one language

## 💡 OPTIMIZATION HINTS

### **Parallel Execution Opportunities:**
- Security audit + Accessibility review + QA testing
- Frontend development + Backend API development (with coordination)
- Code architecture review + Performance optimization
- Mobile iOS + Android development (coordinated)
- Infrastructure setup + Application development
- Documentation + Testing (for same features)

### **Sequential Dependencies:**
- Product strategy → Project planning → Implementation
- Backend API → Frontend integration
- Database design → API implementation → Frontend integration
- Core implementation → Security review → Testing → Deployment
- Authentication system → Feature development
- Infrastructure → Application deployment
- AI model training → Integration → Testing

### **Feedback Loops:**
- `the-critic` → Implementation agents → `code-architect` → Refinement
- User research → `product-strategist` → Feature implementation → User testing
- Performance testing → `systems-engineer` → Optimization → Re-testing
- Security audit → Development → Re-audit → Deployment
- Accessibility testing → Design changes → Re-testing

### **Conditional Escalation Paths:**
- Simple task fails complexity threshold → Engage `project-orchestrator`
- Performance issues discovered → Add `systems-engineer`
- Security concerns identified → Escalate to `security-audit-specialist`
- User experience problems → Add `accessibility-expert`
- Technical decisions deadlocked → Engage `the-critic`

## 🧠 ADVANCED DECISION PATTERNS

### **Context-Aware Agent Enhancement**

**Domain-Specific Combinations:**
- **FinTech**: `full-stack-architect` + `security-audit-specialist` + `qa-test-engineer` + `the-critic`
- **HealthTech**: `mobile-developer` + `security-audit-specialist` + `accessibility-expert` + compliance specialist
- **EdTech**: `full-stack-architect` + `accessibility-expert` + `ai-ml-engineer` + `qa-test-engineer`
- **DevTools**: `systems-engineer` + `code-architect` + developer UX specialist
- **Gaming**: `systems-engineer` + `artist` + platform-specific developers
- **IoT/Embedded**: `systems-engineer` + `security-audit-specialist` + hardware integration

### **Scale-Dependent Strategies**

**Startup/MVP (speed-focused)**:
- Core: Single full-stack agent
- Quality: Basic security + testing
- Iteration: Fast feedback loops

**Growth Stage (scalability-focused)**:
- Core: Specialized agents per domain
- Quality: Full security + accessibility audit
- Architecture: Performance optimization

**Enterprise (robustness-focused)**:
- Core: Full specialist team
- Quality: Comprehensive audit pipeline
- Governance: Compliance + architecture review

### **Technology Stack Ecosystems**

**Modern Web Stack**:
- `full-stack-architect` (TypeScript, React, Next.js, Node.js)
- `devops-engineer` (Vercel, AWS, Docker)
- `security-audit-specialist` (OAuth, HTTPS, CSP)

**Mobile-First Stack**:
- `mobile-developer` (React Native, Swift, Kotlin)
- `full-stack-architect` (API backend)
- `devops-engineer` (App store deployment)

**AI-Enhanced Stack**:
- `ai-ml-engineer` (LLMs, embeddings, vector DBs)
- `full-stack-architect` (Integration layer)
- `data-engineer` (Data pipelines, analytics)
- `systems-engineer` (Performance optimization)

**High-Performance Stack**:
- `systems-engineer` (Rust, C++, Go)
- `devops-engineer` (Kubernetes, monitoring)
- `qa-test-engineer` (Load testing, profiling)

This decision tree ensures optimal agent selection while avoiding redundancy and ensuring comprehensive coverage of all project needs through sophisticated context awareness and risk-based escalation patterns.