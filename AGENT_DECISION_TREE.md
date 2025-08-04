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
`AI`, `ML`, `LLM`, `ChatGPT`, `Claude`, `embeddings`, `vector`, `RAG`, `semantic search`, `recommendation`
→ **`ai-ml-engineer`**

**DATABASE/DATA KEYWORDS:**
`database`, `PostgreSQL`, `MongoDB`, `data pipeline`, `analytics`, `ETL`, `data warehouse`
→ **`data-engineer`**

**INFRASTRUCTURE KEYWORDS:**
`deploy`, `CI/CD`, `Docker`, `AWS`, `cloud`, `infrastructure`, `DevOps`, `monitoring`
→ **`devops-engineer`**

**SYSTEMS PROGRAMMING KEYWORDS:**
`Rust`, `C++`, `Go`, `performance`, `optimization`, `concurrent`, `memory`, `systems`
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
- `"new product"`, `"startup idea"`, `"market research"` → **product-strategist**
- `"coordinate"`, `"orchestrate"`, `"complex project"` → **project-orchestrator** 
- `"security audit"`, `"vulnerability"`, `"penetration test"` → **security-audit-specialist**
- `"accessibility"`, `"WCAG"`, `"screen reader"` → **accessibility-expert**
- `"AI integration"`, `"add LLM"`, `"chatbot"` → **ai-ml-engineer**

### **Technology Stack Triggers**
- `"React"`, `"Next.js"`, `"web app"`, `"full-stack"` → **full-stack-architect**
- `"iOS"`, `"Android"`, `"mobile"`, `"Swift"`, `"Kotlin"` → **mobile-developer**
- `"database"`, `"PostgreSQL"`, `"data pipeline"` → **data-engineer**
- `"deploy"`, `"CI/CD"`, `"infrastructure"` → **devops-engineer**
- `"Rust"`, `"performance"`, `"optimization"` → **systems-engineer**

### **Quality/Review Triggers**
- `"code review"`, `"best practices"`, `"clean code"` → **code-architect** or **code-reviewer**
- `"test"`, `"testing"`, `"QA"`, `"quality assurance"` → **qa-test-engineer**
- `"decide"`, `"choose"`, `"evaluate options"` → **the-critic**
- `"merge conflict"`, `"git conflict"` → **merge-meister**

## 📋 CONTEXTUAL DECISION FACTORS

### **Project Phase Detection**
- **Planning Phase**: `product-strategist` → `project-orchestrator`
- **Development Phase**: Technology-specific agents
- **Review Phase**: `code-architect`, `security-audit-specialist`, `qa-test-engineer`
- **Deployment Phase**: `devops-engineer`
- **Maintenance Phase**: `legacy-specialist`, `code-architect`

### **Complexity Assessment**
- **Simple Task**: Single specialist agent
- **Medium Complexity**: 2-3 complementary agents
- **High Complexity**: `project-orchestrator` + multiple specialists
- **Enterprise/Production**: Always include security, accessibility, and testing agents

### **Risk Level Indicators**
- **High Risk**: Production systems, user data, payments → mandatory security audit
- **Medium Risk**: Internal tools, non-critical features → recommended security review  
- **Low Risk**: Prototypes, experiments → optional security consideration

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

### **Sequential Dependencies:**
- Product strategy → Project planning → Implementation
- Backend API → Frontend integration
- Core implementation → Security review → Testing → Deployment

### **Feedback Loops:**
- `the-critic` → Implementation agents → `code-architect` → Refinement
- User research → `product-strategist` → Feature implementation → User testing

This decision tree ensures optimal agent selection while avoiding redundancy and ensuring comprehensive coverage of all project needs.