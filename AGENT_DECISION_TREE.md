# Agent Selection Decision Tree

This guide helps Claude Code automatically select the optimal agents based on user requests and project context.

## 🎯 PRIMARY DECISION FLOW

### **Step 1: Identify Intent Category**

**🚀 NEW PROJECT/PRODUCT**
→ Start with `product-strategist` for market validation
→ Then `project-orchestrator` for execution planning

**🔧 EXISTING PROJECT ENHANCEMENT**
→ Analyze specific requirements (see Step 2)

**🐛 BUG FIXES/DEBUGGING**
→ `code-architect` for structural issues
→ `systems-engineer` for performance problems
→ `security-audit-specialist` for security vulnerabilities

**📊 ANALYSIS/REVIEW REQUEST**
→ `the-critic` for decision analysis
→ `code-reviewer` for code quality
→ `security-audit-specialist` for security audit

### **Step 2: Technology Stack Detection**

**WEB APPLICATION KEYWORDS:**
`React`, `Next.js`, `Svelte`, `SvelteKit`, `Vue`, `frontend`, `backend`, `API`, `web app`
→ **`full-stack-architect`**

**MOBILE APPLICATION KEYWORDS:**
`iOS`, `Android`, `Swift`, `Kotlin`, `React Native`, `Flutter`, `mobile app`, `app store`
→ **`mobile-developer`**

**AI/ML KEYWORDS:**
`AI`, `ML`, `LLM`, `ChatGPT`, `Claude`, `OpenAI`, `Anthropic`, `embeddings`, `vector`, `RAG`, `semantic search`, `recommendation`, `neural`, `model`, `training`, `inference`, `transformer`, `fine-tuning`, `RLHF`, `agents`, `multimodal`, `computer vision`, `NLP`, `MLOps`
→ **`ai-ml-engineer`**

**DATABASE/DATA KEYWORDS:**
`database`, `PostgreSQL`, `MongoDB`, `data pipeline`, `analytics`, `ETL`, `data warehouse`
→ **`data-engineer`**

**INFRASTRUCTURE KEYWORDS:**
`deploy`, `CI/CD`, `Docker`, `AWS`, `cloud`, `infrastructure`, `DevOps`, `monitoring`
→ **`devops-engineer`**

**SYSTEMS PROGRAMMING KEYWORDS:**
`Rust`, `C++`, `Go`, `performance`, `optimization`, `concurrent`, `memory`, `systems`, `unsafe`, `zero-copy`, `embedded`, `kernel`, `async`, `threading`
→ **`systems-engineer`**

**LEGACY/MIGRATION KEYWORDS:**
`Objective-C`, `legacy`, `migration`, `modernize`, `refactor`, `compatibility`
→ **`legacy-specialist`**

### **Step 3: Quality/Security Requirements**

**ALWAYS INCLUDE IF:**
- Production deployment mentioned → `security-audit-specialist` + `qa-test-engineer`
- Accessibility/compliance needed → `accessibility-expert`
- Code quality concerns → `code-architect`
- Architecture decisions → `the-critic` (for evaluation)
- Financial/payment systems → `security-audit-specialist` (mandatory)
- Health/medical data → `security-audit-specialist` + compliance review
- Educational/government systems → `accessibility-expert` (mandatory)
- Multi-tenant systems → `security-audit-specialist` + `systems-engineer`
- Real-time systems → `systems-engineer` + `qa-test-engineer`

## 🔄 MULTI-AGENT ORCHESTRATION PATTERNS

### **Pattern 1: New Product Development**
```
1. product-strategist (market research)
2. project-orchestrator (planning)
3. [primary development agent] (implementation)
4. security-audit-specialist (security review)
5. accessibility-expert (inclusion review)
6. qa-test-engineer (testing)
7. devops-engineer (deployment)
```

### **Pattern 2: Feature Addition**
```
1. [domain-specific agent] (implementation)
2. code-architect (integration review)
3. qa-test-engineer (testing)
4. security-audit-specialist (if security-relevant)
```

### **Pattern 3: Technical Decision**
```
1. the-critic (option analysis)
2. [relevant specialists] (feasibility assessment)
3. project-orchestrator (implementation planning)
```

### **Pattern 4: Code Quality Improvement**
```
1. code-architect (assessment)
2. [language-specific specialist] (optimization)
3. qa-test-engineer (testing strategy)
```

## 🎯 KEYWORD-TO-AGENT MAPPING

### **High-Priority Triggers**
- `"new product"`, `"startup idea"`, `"market research"`, `"business model"`, `"competition"` → **product-strategist**
- `"coordinate"`, `"orchestrate"`, `"complex project"`, `"roadmap"`, `"timeline"` → **project-orchestrator** 
- `"security audit"`, `"vulnerability"`, `"penetration test"`, `"compliance"`, `"GDPR"`, `"HIPAA"`, `"auth"` → **security-audit-specialist**
- `"accessibility"`, `"WCAG"`, `"screen reader"`, `"inclusive"`, `"disability"`, `"a11y"` → **accessibility-expert**
- `"AI integration"`, `"add LLM"`, `"chatbot"`, `"machine learning"`, `"neural network"`, `"GPT"`, `"Claude"` → **ai-ml-engineer**
- `"performance"`, `"optimization"`, `"slow"`, `"memory"`, `"cpu"`, `"latency"`, `"bottleneck"` → **systems-engineer**
- `"decide"`, `"choose"`, `"evaluate"`, `"trade-off"`, `"architecture decision"` → **the-critic**

### **Technology Stack Triggers**
- `"React"`, `"Next.js"`, `"web app"`, `"full-stack"`, `"TypeScript"`, `"Node.js"`, `"API"` → **full-stack-architect**
- `"iOS"`, `"Android"`, `"mobile"`, `"Swift"`, `"Kotlin"`, `"React Native"`, `"Flutter"`, `"app store"` → **mobile-developer**
- `"database"`, `"PostgreSQL"`, `"data pipeline"`, `"SQL"`, `"analytics"`, `"ETL"`, `"warehouse"` → **data-engineer**
- `"deploy"`, `"CI/CD"`, `"infrastructure"`, `"Docker"`, `"Kubernetes"`, `"AWS"`, `"cloud"` → **devops-engineer**
- `"Rust"`, `"performance"`, `"optimization"`, `"C++"`, `"Go"`, `"systems"`, `"concurrent"`, `"memory"` → **systems-engineer**
- `"Haskell"`, `"functional"`, `"Clojure"`, `"F#"`, `"category theory"`, `"monad"`, `"immutable"` → **functional-programmer**
- `"Lisp"`, `"macro"`, `"DSL"`, `"metaprogramming"`, `"code generation"`, `"compiler"` → **metaprogramming-specialist**
- `"Emacs"`, `"init.el"`, `"elisp"`, `"Emacs Lisp"`, `"use-package"`, `"straight.el"`, `"Doom Emacs"`, `"Spacemacs"`, `"major mode"`, `"minor mode"`, `"MELPA"` → **elisp-specialist**
- `"legacy"`, `"migration"`, `"Objective-C"`, `"COBOL"`, `"modernize"`, `"refactor"` → **legacy-specialist**

### **Quality/Review Triggers**
- `"code review"`, `"best practices"`, `"clean code"` → **code-architect** or **code-reviewer**
- `"test"`, `"testing"`, `"QA"`, `"quality assurance"` → **qa-test-engineer**
- `"decide"`, `"choose"`, `"evaluate options"` → **the-critic**
- `"merge conflict"`, `"git conflict"` → **merge-meister**

## 📋 CONTEXTUAL DECISION FACTORS

### **Project Phase Detection**
- **Discovery Phase**: `product-strategist` (market research, validation)
- **Planning Phase**: `project-orchestrator` (architecture, timeline)
- **Proof of Concept**: Single specialist agent for rapid validation
- **Development Phase**: Technology-specific agents + quality agents
- **Integration Phase**: `code-architect` + `devops-engineer`
- **Review Phase**: `code-architect`, `security-audit-specialist`, `qa-test-engineer`
- **Pre-Production**: `security-audit-specialist` + `accessibility-expert` (mandatory)
- **Deployment Phase**: `devops-engineer` + monitoring setup
- **Post-Launch**: `data-engineer` (analytics) + `devops-engineer`
- **Maintenance Phase**: `legacy-specialist`, `code-architect`, `systems-engineer`
- **Scale-up Phase**: `systems-engineer` + `devops-engineer`

### **Complexity Assessment**

**Single Task (1 agent)**:
- Code fixes, single feature implementation
- Documentation updates, minor refactoring
- Simple integrations with existing patterns

**Medium Complexity (2-3 agents)**:
- New features with security implications
- Cross-platform implementations
- Database schema changes with migration
- API additions with client updates

**High Complexity (4+ agents with orchestration)**:
- New product development
- Major architectural changes
- Multi-service integrations
- Real-time systems with performance requirements
- AI/ML feature additions

**Enterprise/Production (mandatory quality agents)**:
- Always include: `security-audit-specialist`, `qa-test-engineer`
- Public-facing: Add `accessibility-expert`
- Performance-critical: Add `systems-engineer`
- Data-intensive: Add `data-engineer`
- Multi-platform: Add platform-specific specialists

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
- ❌ `code-architect` + `code-reviewer` simultaneously  
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