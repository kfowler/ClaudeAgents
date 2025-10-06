---
name: command-name
description: Brief description of what this command accomplishes and when to use it
---

# Command Name

## Overview

Clear explanation of:
- What this command accomplishes
- When to use this command
- Expected outcomes and deliverables
- Estimated execution time (if applicable)

## Prerequisites

Optional section listing:
- Required setup or configuration
- Access permissions needed
- Dependencies or tools required
- Recommended project state

## Multi-Agent Orchestration Strategy

### **Phase 1: [Phase Name]**
Deploy `agent-name` to:
- Specific responsibility or task
- Expected deliverable or outcome
- Quality criteria or success metrics
- Integration points with next phase

**Why this agent:** Brief explanation of why this specific agent is appropriate for this phase.

### **Phase 2: [Next Phase Name]**
Engage `another-agent` to:
- Follow-up tasks building on Phase 1
- Additional analysis or implementation
- Quality verification or testing
- Documentation or reporting

**Why this agent:** Rationale for agent selection.

### **Phase 3: [Subsequent Phase]**
Use `third-agent` to:
- Advanced features or optimization
- Integration with external systems
- Performance tuning or scaling
- Final verification and validation

**Why this agent:** Justification for using this agent.

## Execution Flow

Optional visual representation of the workflow:

```
Phase 1 (agent-name)
    ↓
Phase 2 (another-agent)
    ↓
Phase 3 (third-agent)
    ↓
Deliverables
```

Or for parallel execution:

```
Phase 1a (agent-1)  ┐
Phase 1b (agent-2)  ├→ Integration → Phase 2 (orchestrator) → Final Output
Phase 1c (agent-3)  ┘
```

## Expected Deliverables

Clear list of what this command produces:
- **[Deliverable 1]**: Description and format
- **[Deliverable 2]**: Location and structure
- **[Deliverable 3]**: Quality standards met

## Success Criteria

How to verify the command completed successfully:
- [ ] Specific measurable outcome 1
- [ ] Specific measurable outcome 2
- [ ] Specific measurable outcome 3
- [ ] All tests passing
- [ ] Documentation updated

## Common Issues and Solutions

Optional section for known challenges:

**Issue:** Description of potential problem
**Solution:** How to resolve it
**Prevention:** How to avoid it in the future

**Issue:** Another common problem
**Solution:** Resolution steps
**Prevention:** Proactive measures

## Related Commands

Optional references to complementary or alternative commands:
- **`related-command-1`**: When to use this instead or in addition
- **`related-command-2`**: Follow-up command for next steps
- **`related-command-3`**: Alternative approach for different contexts

## Notes

Optional additional context:
- Best practices specific to this command
- Performance considerations
- Scaling implications
- Security considerations
- Cost implications (if applicable)

---

## Template Usage Instructions

### Required Sections
- Overview
- Multi-Agent Orchestration Strategy (at least 2 phases)
- Expected Deliverables

### Optional Sections
- Prerequisites
- Execution Flow
- Success Criteria
- Common Issues and Solutions
- Related Commands
- Notes

### Agent References
- Use backticks for agent names: `agent-name`
- Ensure all referenced agents exist in `agents/` directory
- Provide rationale for agent selection

### Phase Structure
- Each phase should have a clear purpose
- Explain why specific agents are chosen
- Define handoffs between phases
- Include quality criteria

### Testing Your Command
After creating a command, verify:
1. All agent references are valid (run tests)
2. Phase descriptions are clear and actionable
3. Deliverables are well-defined
4. Success criteria are measurable

### Naming Conventions
- Use kebab-case for command names
- Choose descriptive, action-oriented names
- Place in appropriate subdirectory:
  - `development/`: Code-focused workflows
  - `quality/`: Testing, security, performance
  - `deployment/`: Infrastructure, deployment
  - `specialized/`: Language/framework-specific
  - `workflows/`: Multi-agent orchestration

### Example Command Names
- ✅ `security-audit` (clear, action-oriented)
- ✅ `deploy-prep` (concise, descriptive)
- ✅ `python-web-api` (specific domain)
- ❌ `do-stuff` (vague)
- ❌ `command1` (non-descriptive)

---

**Remember:** Commands orchestrate agents. Keep the focus on the workflow and agent coordination, not implementation details (that's the agent's job).
