# Specialized AI Agents for Claude Code

This directory contains 20 specialized AI agent definitions optimized for comprehensive software development projects. Each agent is an expert in their domain and works autonomously to deliver production-ready solutions.

## How Agents Work

Agents are intelligent, autonomous specialists that:
- Analyze requirements and create realistic execution plans
- Perform complex multi-step tasks with appropriate trade-off awareness
- Utilize all available tools while acknowledging limitations
- Coordinate with other agents through clear handoffs
- Deliver maintainable solutions with documentation

## 🎯 AGENT SELECTION GUIDE

### **📊 FOR PRODUCT STRATEGY & PLANNING**
- **`product-strategist`** - Market research, competitive analysis, product ideation, go-to-market strategy
- **`project-orchestrator`** - Complex project coordination, task breakdown, agent delegation

### **🏗️ FOR CORE DEVELOPMENT**
- **`full-stack-architect`** - Complete web applications (React/Next.js, Svelte/SvelteKit + backend APIs)
- **`mobile-developer`** - iOS/Android apps (native Swift/Kotlin or React Native/Flutter)
- **`data-engineer`** - Database design, data pipelines, analytics, ML data infrastructure
- **`devops-engineer`** - Infrastructure, CI/CD, deployment, cost optimization

### **🔒 FOR QUALITY & SECURITY**
- **`security-audit-specialist`** - Security reviews, vulnerability assessment, compliance
- **`qa-test-engineer`** - Testing strategies, test implementation, quality assurance
- **`accessibility-expert`** - WCAG compliance, inclusive design, assistive technology
- **`code-architect`** - Code review, architecture improvements, maintainability

### **💻 FOR SPECIALIZED PROGRAMMING**
- **`systems-engineer`** - Rust, C++, Go, performance-critical, concurrent systems
- **`functional-programmer`** - Haskell, Clojure, F#, advanced type systems, category theory
- **`metaprogramming-specialist`** - Lisp, macros, DSLs, code generation, language extension
- **`legacy-specialist`** - Legacy code migration, Objective-C, deprecated technology bridging

### **🎨 FOR MODERN CAPABILITIES**
- **`ai-ml-engineer`** - LLM integration, RAG systems, ML pipelines, vector databases
- **`platform-integrator`** - Native platform development (macOS/Windows/Linux APIs)
- **`artist`** - Digital assets, UI graphics, visual design, multimedia content

### **⚖️ FOR DECISION SUPPORT**
- **`the-critic`** - Technical decision analysis, trade-off evaluation, architectural critique
- **`merge-meister`** - Conflict resolution, code integration, branch management
- **`code-reviewer`** - Code quality assessment, best practices enforcement

## 🚀 USAGE PATTERNS

### **🎯 Start Here for Different Project Types:**

**Building a Web Application:**
1. `product-strategist` → Market validation & feature definition
2. `full-stack-architect` → Complete web app implementation
3. `security-audit-specialist` → Security review
4. `qa-test-engineer` → Testing implementation

**Mobile App Development:**
1. `product-strategist` → Market research & user personas
2. `mobile-developer` → iOS/Android implementation
3. `accessibility-expert` → Inclusive design review
4. `devops-engineer` → App store deployment

**Adding AI Features:**
1. `ai-ml-engineer` → LLM/RAG implementation
2. `data-engineer` → Vector database & data pipelines
3. `security-audit-specialist` → AI security review
4. `devops-engineer` → ML infrastructure deployment

**Legacy System Modernization:**
1. `legacy-specialist` → Migration strategy & compatibility
2. `code-architect` → Architecture assessment & refactoring
3. `systems-engineer` → Performance optimization
4. `qa-test-engineer` → Comprehensive testing strategy

### **🔄 Agent Coordination Patterns:**

**Sequential Execution:**
```
product-strategist → project-orchestrator → [development agents] → qa-test-engineer
```

**Parallel Execution:**
```
full-stack-architect + security-audit-specialist + accessibility-expert
```

**Iterative Refinement:**
```
code-architect → systems-engineer → the-critic → [refinement cycle]
```

## 📋 AGENT INVOCATION

### **Automatic Selection (Recommended):**
Claude Code analyzes your request and selects optimal agents automatically based on:
- Task complexity and domain requirements
- Technology stack and platform targets
- Quality and security considerations
- Project phase and deliverable needs

### **Explicit Agent Requests:**
```
"Use the product-strategist to research the productivity software market"
"Have the ai-ml-engineer implement semantic search with RAG"
"Get the security-audit-specialist to review my authentication system"
"Ask the-critic to evaluate these architecture options"
```

### **Multi-Agent Orchestration:**
```
"Use the project-orchestrator to plan a task management app with:
- React frontend and Node.js backend
- Real-time collaboration features
- Mobile companion app
- AI-powered task suggestions"
```

## 🎯 OPTIMAL USAGE TIPS

### **✅ DO:**
- Start with `product-strategist` for new product ideas
- Use `project-orchestrator` for complex multi-domain projects
- Combine complementary agents (e.g., `full-stack-architect` + `accessibility-expert`)
- Leverage `the-critic` for important architectural decisions
- Include `security-audit-specialist` and `qa-test-engineer` in production code

### **❌ AVOID:**
- Using multiple agents with overlapping capabilities simultaneously
- Skipping security and accessibility reviews for production applications
- Implementing AI features without involving `ai-ml-engineer`
- Starting complex projects without product strategy validation
- Ignoring `code-architect` feedback on maintainability concerns

## 🔍 AGENT CAPABILITIES MATRIX

| Agent | Web Dev | Mobile | AI/ML | Security | Performance | Legacy |
|-------|---------|--------|-------|----------|-------------|--------|
| full-stack-architect | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| mobile-developer | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| ai-ml-engineer | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| systems-engineer | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| security-audit-specialist | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| legacy-specialist | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

⭐⭐⭐ = Primary expertise, ⭐⭐ = Secondary capability, ⭐ = Basic support

## 🏆 SUCCESS METRICS

Track agent effectiveness through:
- **Feature Completion Rate**: Delivered features working as specified
- **Code Quality Scores**: Maintainability, security, performance metrics
- **Integration Success**: Seamless agent handoffs and coordination
- **User Satisfaction**: End-user acceptance of agent-delivered solutions
- **Development Velocity**: Time from concept to production deployment

Each agent is designed to deliver production-ready solutions with appropriate documentation, testing strategies, and deployment guidance for their domain.