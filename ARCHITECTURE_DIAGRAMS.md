# ClaudeAgents Architecture Diagrams

**Visual Guide to Current State and Proposed Architecture**

---

## Current Architecture (Before Enhancements)

### System Overview - Current State

```
┌─────────────────────────────────────────────────────────────┐
│                    ClaudeAgents System                      │
│                     (Current State)                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ Natural language request
       ▼
┌──────────────────────────────────────────────────────────┐
│              Claude Code Interface                       │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│           Agent Selection & Invocation                   │
│                                                          │
│  ┌────────────────────────────────────────┐            │
│  │  Manual Selection or                   │            │
│  │  project-orchestrator (basic)          │            │
│  └────────────────────────────────────────┘            │
│                                                          │
│  Agent Library (43 agents)                              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                  │
│  │Agent1│ │Agent2│ │Agent3│ │ ...  │                  │
│  └──────┘ └──────┘ └──────┘ └──────┘                  │
└──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│         Claude Code Native Tools                         │
│  (Bash, Read, Write, Edit, Grep, etc.)                  │
└──────────────────────────────────────────────────────────┘
       │
       ▼ Temporary session only
┌──────────────────────────────────────────────────────────┐
│             No Persistent State                          │
│     Context discarded after execution                    │
└──────────────────────────────────────────────────────────┘
```

**Limitations:**
- ❌ No MCP protocol support
- ❌ No persistent memory/context
- ❌ Basic agent coordination
- ❌ No workflow automation
- ❌ Limited GitHub integration (bash git commands only)
- ❌ Manual agent selection only

---

## Proposed Architecture (After Enhancements)

### System Overview - Future State

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      ClaudeAgents System                                 │
│                    (Enhanced Architecture)                               │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│    User     │
└──────┬──────┘
       │ Natural language request
       ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    Claude Code Interface                              │
└───────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────────────┐
│              Workflow & Orchestration Layer                           │
│                                                                       │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐   │
│  │ Workflow Engine  │    │ Hooks System     │    │ Event Bus    │   │
│  │ - Templates      │    │ - Lifecycle      │    │ - Pub/Sub    │   │
│  │ - Automation     │    │ - Integration    │    │ - Req/Resp   │   │
│  └──────────────────┘    └──────────────────┘    └──────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │        Agent Coordination Protocol                          │    │
│  │  - State Machine                                            │    │
│  │  - Handoff Management                                       │    │
│  │  - Communication Bus                                        │    │
│  └─────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────────────┐
│                 Quality-Certified Agent Library                       │
│                                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │               │
│  │  (Gold)  │ │ (Silver) │ │ (Silver) │ │  (Gold)  │               │
│  │ Score:95 │ │ Score:82 │ │ Score:78 │ │ Score:92 │               │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │
│                                                                       │
│  43+ Certified Agents (expandable to 75-100)                         │
└───────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      Tool Integration Layer                           │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │              MCP Protocol Client                           │     │
│  │  - Tool Discovery                                          │     │
│  │  - Request/Response Handling                               │     │
│  │  - Security Sandbox                                        │     │
│  └────────────────────────────────────────────────────────────┘     │
│       │                    │                    │                    │
│       ▼                    ▼                    ▼                    │
│  ┌─────────┐         ┌─────────┐         ┌─────────┐               │
│  │  MCP    │         │  MCP    │         │  MCP    │               │
│  │ Server  │         │ Server  │         │ Server  │               │
│  │Database │         │FileSystem│        │  API    │               │
│  └─────────┘         └─────────┘         └─────────┘               │
│                                                                       │
│  + Claude Code Native Tools (Bash, Read, Write, etc.)               │
└───────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    Persistent State Layer                             │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │              Context Store (SQLite)                        │     │
│  │  - Session History                                         │     │
│  │  - Agent State                                             │     │
│  │  - Workflow State                                          │     │
│  │  - 90-day Retention                                        │     │
│  └────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    External Integrations                              │
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   GitHub     │    │  Databases   │    │  Custom APIs │          │
│  │   - Issues   │    │  - Query     │    │  - HTTP      │          │
│  │   - PRs      │    │  - Execute   │    │  - GraphQL   │          │
│  │   - Actions  │    │  - Schema    │    │  - Webhooks  │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
└───────────────────────────────────────────────────────────────────────┘
```

**Enhancements:**
- ✅ MCP protocol support (infinite tool extensibility)
- ✅ Persistent memory/context (session continuity)
- ✅ Advanced agent coordination (state machine + handoffs)
- ✅ Workflow automation (templates + hooks)
- ✅ Native GitHub integration (issues, PRs, releases)
- ✅ Quality certification (objective metrics)

---

## MCP Protocol Architecture (Detailed)

```
┌──────────────────────────────────────────────────────────────────┐
│                   MCP Integration Architecture                   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Agent Layer                              │
│                                                                 │
│  Agent Prompt with MCP Tool Awareness:                          │
│  "You have access to the following MCP tools:                   │
│   - database_query: Query PostgreSQL databases                  │
│   - file_search: Advanced file system search                    │
│   - http_request: Make HTTP API calls                           │
│                                                                 │
│   To invoke: MCP_INVOKE: tool_name(arg1=val1, arg2=val2)"      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Protocol Client                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │  Tool Discovery                                    │        │
│  │  - Enumerate available tools from servers          │        │
│  │  - Cache tool metadata                             │        │
│  │  - Update on server changes                        │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │  Request Handler                                   │        │
│  │  - Parse agent tool invocations                    │        │
│  │  - Validate arguments                              │        │
│  │  - Route to appropriate server                     │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │  Response Handler                                  │        │
│  │  - Process server responses                        │        │
│  │  - Format for agent consumption                    │        │
│  │  - Handle errors gracefully                        │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │  Security Layer                                    │        │
│  │  - Sandbox tool execution                          │        │
│  │  - Validate inputs                                 │        │
│  │  - Rate limiting                                   │        │
│  │  - Audit logging                                   │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ MCP Server 1 │  │ MCP Server 2 │  │ MCP Server N │
│  (Database)  │  │ (Filesystem) │  │   (Custom)   │
└──────────────┘  └──────────────┘  └──────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────────────────────────────────────────┐
│        External Resources & Services             │
│  - PostgreSQL Database                           │
│  - Local Filesystem                              │
│  - Third-party APIs                              │
│  - Custom Integrations                           │
└──────────────────────────────────────────────────┘
```

**MCP Tool Invocation Flow:**

```
1. Agent generates tool request:
   "MCP_INVOKE: database_query(query='SELECT * FROM users', limit=10)"

2. MCP Client parses request:
   {
     "tool": "database_query",
     "arguments": {
       "query": "SELECT * FROM users",
       "limit": 10
     }
   }

3. Client routes to Database MCP Server

4. Server executes query and returns:
   {
     "status": "success",
     "data": [
       {"id": 1, "name": "Alice"},
       {"id": 2, "name": "Bob"}
     ],
     "rows_returned": 2
   }

5. Client formats response for agent:
   "Query executed successfully. Retrieved 2 users: Alice, Bob"

6. Agent continues with result
```

---

## Agent Coordination Architecture (Detailed)

```
┌─────────────────────────────────────────────────────────────────┐
│              Agent Coordination & Workflow System               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Workflow Engine                              │
│                                                                 │
│  Workflow Template:                                             │
│  ┌────────────────────────────────────────────────┐            │
│  │ name: full_stack_web_app                       │            │
│  │ phases:                                        │            │
│  │   - architecture (sequential)                  │            │
│  │   - implementation (parallel)                  │            │
│  │   - quality_assurance (parallel)               │            │
│  │   - deployment (sequential)                    │            │
│  └────────────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   State Machine                                 │
│                                                                 │
│  States:                                                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐ │
│  │  INIT    │ →  │  RUNNING │ →  │ COMPLETE │ →  │ SUCCESS │ │
│  └──────────┘    └──────────┘    └──────────┘    └─────────┘ │
│       │               │               │                        │
│       └───────────────┴───────────────┴────→ ┌─────────┐      │
│                                              │  ERROR  │      │
│                                              └─────────┘      │
│                                                                 │
│  Transitions:                                                   │
│  - Validate preconditions                                       │
│  - Execute phase actions                                        │
│  - Verify postconditions                                        │
│  - Update state                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Agent Communication Bus                            │
│                                                                 │
│  ┌────────────────────────────────────────────────┐            │
│  │  Message Types:                                │            │
│  │                                                │            │
│  │  1. Request/Response (synchronous)             │            │
│  │     Agent A → Request → Agent B                │            │
│  │     Agent B → Response → Agent A               │            │
│  │                                                │            │
│  │  2. Publish/Subscribe (asynchronous)           │            │
│  │     Agent A → Event → [All Subscribers]        │            │
│  │                                                │            │
│  │  3. Queue (background jobs)                    │            │
│  │     Agent A → Job → Queue → Agent B (later)    │            │
│  └────────────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Handoff Protocol                               │
│                                                                 │
│  Handoff Message:                                               │
│  {                                                              │
│    "from_agent": "full-stack-architect",                        │
│    "to_agent": "qa-test-engineer",                              │
│    "context": {                                                 │
│      "component": "authentication_service",                     │
│      "implementation": "auth_service.py",                       │
│      "tests_needed": ["login", "logout", "token_refresh"]       │
│    },                                                           │
│    "deliverables": [                                            │
│      "auth_service.py",                                         │
│      "auth_api.yaml"                                            │
│    ],                                                           │
│    "success_criteria": [                                        │
│      "All authentication flows work",                           │
│      "JWT tokens properly generated",                           │
│      "OAuth integration functional"                             │
│    ],                                                           │
│    "verification": "Run integration tests"                      │
│  }                                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Example Multi-Agent Workflow:**

```
User Request: "Build a web application with authentication"

Workflow: full_stack_web_app

┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Architecture (Sequential)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  project-orchestrator                                       │
│         ↓                                                   │
│  full-stack-architect (design system)                       │
│         ↓                                                   │
│  the-critic (review design)                                 │
│         ↓                                                   │
│  [Handoff: Design approved] → Next Phase                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Implementation (Parallel)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────┐        ┌──────────────────┐         │
│  │full-stack-architect│        │  data-engineer   │         │
│  │  (frontend + API) │        │  (database)      │         │
│  └────────┬──────────┘        └────────┬─────────┘         │
│           │                            │                    │
│           └────────────┬───────────────┘                    │
│                        ↓                                    │
│             Integration Point                               │
│         (Both complete before proceeding)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Quality Assurance (Parallel)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌─────────────────────────────┐    │
│  │qa-test-engineer  │  │security-audit-specialist    │    │
│  │  (test suite)    │  │  (security scan)            │    │
│  └────────┬─────────┘  └────────┬────────────────────┘    │
│           │                     │                          │
│           └──────────┬──────────┘                          │
│                      ↓                                     │
│         [Both Pass] → Next Phase                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Deployment (Sequential)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  devops-engineer                                            │
│         ↓                                                   │
│  Deploy to staging                                          │
│         ↓                                                   │
│  Verify deployment                                          │
│         ↓                                                   │
│  [Success] → Workflow Complete                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Persistent Context Architecture (Detailed)

```
┌─────────────────────────────────────────────────────────────────┐
│                  Context Management System                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Agent Execution                            │
│                                                                 │
│  Agent invoked → Check for existing context                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Context Repository                           │
│                                                                 │
│  Interface:                                                     │
│  - get_context(session_id, agent_id) → Context                  │
│  - save_context(context)                                        │
│  - search_contexts(query) → List[Context]                       │
│  - delete_expired_contexts()                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Storage Backend (SQLite)                      │
│                                                                 │
│  Schema:                                                        │
│  ┌────────────────────────────────────────────────┐            │
│  │ TABLE contexts                                 │            │
│  ├────────────────────────────────────────────────┤            │
│  │ id            TEXT PRIMARY KEY                 │            │
│  │ session_id    TEXT NOT NULL                    │            │
│  │ agent_id      TEXT NOT NULL                    │            │
│  │ state         JSON NOT NULL                    │            │
│  │ created_at    TIMESTAMP                        │            │
│  │ updated_at    TIMESTAMP                        │            │
│  │ expires_at    TIMESTAMP                        │            │
│  └────────────────────────────────────────────────┘            │
│                                                                 │
│  ┌────────────────────────────────────────────────┐            │
│  │ TABLE interactions                             │            │
│  ├────────────────────────────────────────────────┤            │
│  │ id            TEXT PRIMARY KEY                 │            │
│  │ context_id    TEXT FOREIGN KEY                 │            │
│  │ timestamp     TIMESTAMP                        │            │
│  │ input         TEXT                             │            │
│  │ output        TEXT                             │            │
│  │ tokens_used   INTEGER                          │            │
│  └────────────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Lifecycle Management                           │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │  Creation:                               │                  │
│  │  - First agent invocation                │                  │
│  │  - Generate session_id                   │                  │
│  │  - Set expiration (90 days)              │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │  Updates:                                │                  │
│  │  - After each interaction                │                  │
│  │  - Update state                          │                  │
│  │  - Extend expiration                     │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │  Retrieval:                              │                  │
│  │  - On subsequent invocations             │                  │
│  │  - Lazy loading for performance          │                  │
│  │  - Cache in memory during session        │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  ┌──────────────────────────────────────────┐                  │
│  │  Cleanup:                                │                  │
│  │  - Background job (daily)                │                  │
│  │  - Delete expired contexts               │                  │
│  │  - Vacuum database                       │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Context Usage Flow:**

```
Session 1 (Initial):
User → Agent invocation
Agent → No context found → Create new context
Agent → Process request → Save state
Agent → Return result

Session 2 (Return User):
User → Agent invocation (same agent)
Agent → Context found → Load previous state
Agent → "I remember we were working on X..."
Agent → Continue from last state → Update context
Agent → Return result

Session 3 (After 90 days):
User → Agent invocation
Agent → Context expired → Start fresh
Agent → "This appears to be a new session..."
```

---

## Quality Certification System (Detailed)

```
┌─────────────────────────────────────────────────────────────────┐
│              Agent Quality Certification Pipeline               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Stage 1: Metadata Validation (20 points)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Check:                                                         │
│  ✓ Frontmatter complete                 (5 points)              │
│  ✓ Version information present          (3 points)              │
│  ✓ Description clear and concise        (5 points)              │
│  ✓ Color and model appropriate          (3 points)              │
│  ✓ Complexity rating accurate           (4 points)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 2: Documentation Quality (20 points)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Check:                                                         │
│  ✓ Clear purpose statement              (5 points)              │
│  ✓ Usage examples provided              (5 points)              │
│  ✓ Related agents documented            (3 points)              │
│  ✓ Anti-patterns listed                 (4 points)              │
│  ✓ Integration guidance present         (3 points)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 3: Prompt Engineering Quality (30 points)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Check:                                                         │
│  ✓ Clear role definition                (8 points)              │
│  ✓ Specific expertise areas             (7 points)              │
│  ✓ Boundary conditions defined          (5 points)              │
│  ✓ Success criteria explicit            (5 points)              │
│  ✓ Anti-mock enforcement present        (5 points)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 4: Integration Quality (15 points)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Check:                                                         │
│  ✓ Orchestration compatible             (5 points)              │
│  ✓ Clear handoff protocols              (4 points)              │
│  ✓ Context requirements specified       (3 points)              │
│  ✓ Dependencies documented              (3 points)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 5: Benchmark Performance (15 points)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Measure:                                                       │
│  ✓ Task completion rate                 (5 points)              │
│  ✓ Quality of outputs                   (5 points)              │
│  ✓ Efficiency metrics                   (3 points)              │
│  ✓ User satisfaction proxy              (2 points)              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Final Certification                            │
│                                                                 │
│  Total Score: Sum of all stages (0-100)                         │
│                                                                 │
│  Tier Assignment:                                               │
│  ┌──────────────────────────────────────────┐                  │
│  │ 90-100: 🏆 Gold Certified                │                  │
│  │         Production-ready, exemplary       │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ 75-89:  🥈 Silver Certified               │                  │
│  │         Production-ready, excellent       │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ 60-74:  🥉 Bronze Certified               │                  │
│  │         Functional, good quality          │                  │
│  ├──────────────────────────────────────────┤                  │
│  │ <60:    ⚠️  Needs Improvement            │                  │
│  │         Not recommended for production    │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
│  Certification Badge:                                           │
│  - Added to agent frontmatter                                   │
│  - Visible in documentation                                     │
│  - Tracked in metrics dashboard                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**CI/CD Integration:**

```
GitHub PR → Automated Checks
              │
              ├→ Validation (schema, references)
              ├→ Certification Scoring
              ├→ Benchmark Testing
              │
              ▼
         Pass/Fail Status
              │
              ├→ Pass (Score ≥ 60) → Merge allowed
              │
              └→ Fail (Score < 60) → Changes requested
                                     with specific feedback
```

---

## Data Flow Diagrams

### Current State Data Flow

```
User Request
     ↓
Agent Selection (manual/basic)
     ↓
Agent Execution
     ↓
Claude Code Tools
     ↓
Temporary Results
     ↓
Response to User
     ↓
[Context Lost]
```

### Future State Data Flow

```
User Request
     ↓
Workflow Engine
     ├→ Load Previous Context (if exists)
     ├→ Select Workflow Template
     ├→ Initialize State Machine
     ↓
Agent Coordination
     ├→ Sequential Execution
     ├→ Parallel Execution
     ├→ Handoff Management
     ↓
Tool Invocation
     ├→ Claude Code Native Tools
     ├→ MCP Tools (database, API, custom)
     ├→ GitHub Integration
     ↓
State Updates
     ├→ Save Context
     ├→ Update Workflow State
     ├→ Trigger Hooks
     ↓
Results Aggregation
     ↓
Response to User
     ↓
[Context Persisted for 90 days]
```

---

## GitHub Integration Flow

```
┌──────────────────────────────────────────────────────┐
│           GitHub Event Triggers                      │
└──────────────────────────────────────────────────────┘
              │
              ├→ Issue Created
              ├→ PR Opened
              ├→ Push to Branch
              └→ Release Created
              │
              ▼
┌──────────────────────────────────────────────────────┐
│              Webhook Handler                         │
│  - Receives GitHub events                            │
│  - Validates payload                                 │
│  - Triggers appropriate workflow                     │
└──────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────┐
│           Workflow Automation                        │
│                                                      │
│  Issue Created → debugging-specialist                │
│                 ↓                                    │
│                Analyze issue                         │
│                Add labels                            │
│                Assign if clear                       │
│                                                      │
│  PR Opened → code-architect                          │
│             qa-test-engineer                         │
│             security-audit-specialist                │
│                 ↓                                    │
│                Review code                           │
│                Run tests                             │
│                Check security                        │
│                Add comments                          │
│                                                      │
│  Release → technical-writer                          │
│           devops-engineer                            │
│                 ↓                                    │
│                Generate changelog                    │
│                Deploy release                        │
│                                                      │
└──────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────┐
│         GitHub API Client                            │
│  - Create/update issues                              │
│  - Add PR comments                                   │
│  - Update labels                                     │
│  - Trigger workflows                                 │
│  - Create releases                                   │
└──────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Current Deployment

```
┌─────────────────────────────────────┐
│    User's Local Machine             │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  ClaudeAgents Repository      │  │
│  │  - Markdown files only        │  │
│  │  - No runtime components      │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Claude Code                  │  │
│  │  - Reads agent definitions    │  │
│  │  - Executes prompts           │  │
│  └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### Future Deployment (with MCP and Context)

```
┌─────────────────────────────────────────────────────┐
│           User's Local Machine                      │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  ClaudeAgents Repository                      │  │
│  │  - Agent definitions (markdown)               │  │
│  │  - Python tools (validation, certification)   │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  Claude Code                                  │  │
│  │  - Reads agent definitions                    │  │
│  │  - Executes prompts                           │  │
│  │  - Invokes MCP client                         │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  MCP Infrastructure                           │  │
│  │  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ MCP Client   │  │ Context DB   │          │  │
│  │  │ (Python)     │  │ (SQLite)     │          │  │
│  │  └──────────────┘  └──────────────┘          │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│          MCP Servers (Local or Remote)              │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Database    │  │  Filesystem  │  │  Custom  │  │
│  │  Server      │  │  Server      │  │  Servers │  │
│  │  (Port 8001) │  │  (Port 8002) │  │  (8003+) │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Installation Steps (Future):**

```bash
# 1. Clone repository
git clone https://github.com/user/ClaudeAgents.git
cd ClaudeAgents

# 2. Install Python dependencies
pip install -r tools/requirements.txt

# 3. Initialize context database
python tools/init_context_db.py

# 4. Start MCP servers (optional)
python tools/start_mcp_servers.py

# 5. Use with Claude Code
# (No additional steps - agents now MCP-enabled)
```

---

## Performance & Scalability Considerations

### Current Performance

```
Agent Invocation: <100ms (markdown parsing)
Tool Usage: Variable (depends on Claude Code tools)
Memory: Minimal (no persistence)
Scalability: Unlimited (stateless)
```

### Future Performance Targets

```
┌──────────────────────────────────────────────────┐
│  Performance Targets                             │
├──────────────────────────────────────────────────┤
│  Agent Invocation:     <100ms (no change)        │
│  Context Retrieval:    <100ms (SQLite query)     │
│  MCP Tool Invocation:  <500ms (depends on tool)  │
│  Workflow Execution:   Variable (multi-agent)    │
│  Context Save:         <50ms (async)             │
│                                                  │
│  Scalability:                                    │
│  - Contexts: 100k+ sessions                      │
│  - MCP Tools: Unlimited (distributed servers)    │
│  - Agents: 75-100 certified                      │
│  - Concurrent Workflows: 10+ (resource limited)  │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│              Security Layers                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Layer 1: Agent Execution Sandbox                   │
│  - No direct system access                          │
│  - Tool invocation only through MCP                 │
│  - Validated inputs                                 │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│  Layer 2: MCP Security                              │
│  - Tool permission system                           │
│  - Rate limiting per tool                           │
│  - Input sanitization                               │
│  - Audit logging                                    │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│  Layer 3: Context Storage Security                  │
│  - No PII storage (configurable)                    │
│  - Encrypted at rest (optional)                     │
│  - Expiration enforcement                           │
│  - Access control (future)                          │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│  Layer 4: External Integration Security             │
│  - GitHub token management                          │
│  - API key storage (secure)                         │
│  - HTTPS only for MCP servers                       │
│  - Webhook signature validation                     │
└─────────────────────────────────────────────────────┘
```

---

**For detailed implementation plans, see ARCHITECTURAL_ASSESSMENT.md**
**For quick reference, see TECHNICAL_ROADMAP_SUMMARY.md**
