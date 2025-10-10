# Creative Triad System

## Overview

The **Creative Triad** is a coordinated system of four specialized agents that transform creative ideation from art into science through structured divergence, synthesis, and experimental validation. Inspired by research in creativity science and falsifiability principles, this system guarantees diversity, measurability, and rigorous thinking.

### The Four Agents

1. **creative-catalyst** - Divergent ideation with oblique strategies and constraint generation
2. **the-inventor** - Divergent ideation with guaranteed diversity across multiple dimensions
3. **the-synthesist** - Convergent synthesis organizing ideas into coherent strategic frames
4. **the-architect-of-experiments** - Falsifiable experiment design with 100% kill condition coverage

### When to Use the Creative Triad

**Use the creative triad when you need:**
- Novel solutions to complex problems that resist conventional approaches
- Diverse idea generation across mechanism, experience, and market dimensions
- Strategic frameworks that synthesize multiple ideas into coherent implementation paths
- Rigorous experimental validation before committing significant resources

**Don't use the creative triad for:**
- Simple implementation tasks with known solutions
- Tactical decisions with clear best practices
- Situations requiring immediate action without exploration time
- Problems with established patterns that work well

## Quick Start Guide

### Scenario 1: New Product Ideation

**Problem:** Design a new mobile app feature to increase retention

```bash
# Step 1: Generate diverse ideas (creative-catalyst mode)
"Generate 10 diverse ideas for mobile app retention features.
Use oblique strategies and maximize novelty distribution."

# Step 2: Synthesize into strategic frames (the-synthesist)
"Synthesize the 10 retention ideas into 3 coherent strategic frames.
Ensure 100% idea coverage and identify false tradeoffs."

# Step 3: Design experiments (the-architect-of-experiments)
"Design falsifiable experiments to validate each strategic frame.
Require 100% kill condition coverage and 48-120 hour duration windows."
```

### Scenario 2: System Architecture Exploration

**Problem:** Evaluate different approaches to scaling a backend system

```bash
# Use the-inventor for technical diversity
"Generate 7-12 architecturally diverse approaches for scaling our API backend.
Ensure diversity across mechanism (how it works), experience (developer UX),
and data_approach (how data flows)."

# Then synthesize and validate
"Synthesize these approaches into 3-5 coherent architecture strategies."
"Design experiments to validate each architecture's performance claims."
```

### Scenario 3: Business Model Innovation

**Problem:** Explore new revenue models for SaaS product

```bash
# Use creative-catalyst for breakthrough thinking
"Apply oblique strategies to generate 8-10 unconventional revenue models.
Challenge assumptions about subscription pricing. Generate creative constraints."

# Synthesize practical frames
"Organize these revenue model ideas into 2-3 implementable business strategies.
Identify which ideas complement each other and which represent false tradeoffs."

# Design validation experiments
"Design A/B tests or market validation experiments for each revenue strategy.
Each experiment must have clear kill conditions and quantitative success metrics."
```

## Agent Selection Guide

### creative-catalyst vs. the-inventor

Both agents generate ideas, but differ in approach:

| Aspect | creative-catalyst | the-inventor |
|--------|-------------------|--------------|
| **Method** | Oblique strategies, lateral thinking | Systematic diversity guarantees |
| **Output** | 5-50 ideas, novelty-focused | 7-12 ideas, diversity-focused |
| **Best for** | Breaking assumptions, creative breakthroughs | Comprehensive exploration, rigorous diversity |
| **Novelty** | Emphasizes high-novelty ideas (0.7-1.0) | Balanced distribution (conventional to breakthrough) |
| **Dimensions** | Flexible dimensions | Required: mechanism, experience, market, data (optional) |

**When to use creative-catalyst:**
- You need to challenge assumptions and break mental models
- Novelty and unexpectedness are primary goals
- You want oblique constraints and provocations
- Problem feels stuck in conventional thinking

**When to use the-inventor:**
- You need comprehensive coverage of solution space
- Diversity metrics matter for decision-making
- You want balanced novelty distribution
- Problem benefits from systematic exploration

### the-synthesist: Convergent Synthesis

Use **the-synthesist** after ideation to:
- Organize scattered ideas into coherent strategic frames
- Ensure 100% of generated ideas are considered (no cherry-picking)
- Identify false tradeoffs that create artificial constraints
- Create implementation paths with phases, effort estimates, and risks

**Key capabilities:**
- Frame coherence validation
- Cross-frame synergy identification
- Dominant axis articulation (what unifies each frame)
- Implementation path planning

### the-architect-of-experiments: Falsifiable Validation

Use **the-architect-of-experiments** to:
- Design rigorous experiments with clear success/failure criteria
- Ensure 100% kill condition coverage (every experiment can fail)
- Define quantitative success metrics (no vague criteria)
- Sequence experiments for optimal learning and risk management

**Quality guarantees:**
- Every experiment has falsifiable kill condition
- All success metrics are quantitatively measurable
- Duration constrained to 48-120 hours for rapid iteration
- Resource requirements explicitly stated

## Integration with Contrarian Triad

The Creative Triad works beautifully with the Contrarian Triad for decision validation:

```bash
# Creative workflow
creative-catalyst → the-synthesist → the-architect-of-experiments

# Then validate with contrarian analysis
the-pragmatist: "Evaluate implementation feasibility of top frame"
the-skeptic: "Challenge core assumptions in experiment design"
the-critic: "Make final recommendation on which experiment to run first"
```

This creates a complete creative → critical → decisive workflow.

## Structured Output Format

All Creative Triad agents produce **IDEATION_REPORT** structured output:

```json
{
  "agent_id": "the-inventor",
  "version": "v1.0",
  "report_type": "ideation",
  "content": {
    "ideas": [...],
    "diversity_metrics": {
      "overall_diversity_score": 0.85,
      "mechanism_diversity": 0.90,
      "experience_diversity": 0.88,
      "market_diversity": 0.78
    }
  }
}
```

See `schemas/creative/IDEATION_REPORT_v1.json` for complete specification.

## Validation and Quality Assurance

Validate Creative Triad outputs:

```bash
# Schema validation
python tools/validate_creative.py path/to/report.json

# Quality scorecard
python tools/scorecard_creative.py path/to/reports/

# Agent discovery (find right agent for task)
python tools/agent_discovery.py "generate diverse mobile engagement ideas"
```

## Golden Examples

Study these complete workflows:

1. **SaaS Onboarding Optimization** - `tests/seed_templates/creative-catalyst.golden.json`
   - Problem: Reduce 40% drop-off rate
   - Approach: Oblique strategies → synthesis → experiments
   - Result: 10 ideas (0.87 diversity) → 3 frames → validation plan

2. **Mobile Engagement Improvement** - `tests/seed_templates/examples/mobile_engagement/`
   - Problem: Increase D1 retention from 30% to 50%
   - Approach: creative-catalyst (oblique) → synthesist (frames) → architect (experiments)
   - Result: 10 breakthrough ideas → 3 strategic frames → 3 falsifiable experiments

## Frequently Asked Questions

### When should I use creative-catalyst vs. the-inventor?

Use **creative-catalyst** when you need breakthrough thinking and are willing to challenge core assumptions. Use **the-inventor** when you need systematic diversity guarantees and comprehensive coverage.

### Can I skip the-synthesist and go straight to experiments?

Not recommended. the-synthesist ensures 100% idea coverage, identifies false tradeoffs, and creates coherent implementation paths. Skipping synthesis often leads to cherry-picking favorite ideas while missing valuable combinations.

### What if my experiment doesn't fit the 48-120 hour window?

The 48-120 hour constraint forces rapid iteration and learning. If you truly need longer validation, break the experiment into phases with intermediate checkpoints. Each phase should still have falsifiable outcomes within the time window.

### How many ideas should I generate?

- **creative-catalyst:** 5-50 ideas (typically 8-12 for focused exploration)
- **the-inventor:** 7-12 ideas (required range for diversity guarantees)

More isn't always better - focus on diversity and novelty over quantity.

### Can I use only one agent from the triad?

Yes! Each agent provides standalone value:
- **creative-catalyst/the-inventor:** Ideation for brainstorming sessions
- **the-synthesist:** Organizing existing scattered ideas
- **the-architect-of-experiments:** Designing rigorous A/B tests or validation plans

However, the full triad workflow provides maximum value for complex problems.

### How do I know if my diversity score is good enough?

**the-inventor** requires ≥0.7 overall diversity score. Scores interpretation:
- **0.9-1.0:** Exceptional diversity, highly orthogonal ideas
- **0.7-0.9:** Good diversity, sufficient exploration
- **0.5-0.7:** Moderate diversity, may have clustering
- **<0.5:** Low diversity, ideas too similar

### What makes a kill condition falsifiable?

A good kill condition:
1. Is **measurable** (quantitative threshold, not vague)
2. Is **observable** (can actually detect when met)
3. **Would** kill the experiment (not just a warning signal)
4. Has **clear timeline** (when to evaluate)

**Good:** "If D1 retention drops ≥10% within first 24 hours, kill experiment"
**Bad:** "If users seem unhappy, reconsider approach"

### How do I identify false tradeoffs?

the-synthesist identifies false tradeoffs by finding ideas that seem contradictory but can coexist:

- "Engagement vs. User Wellbeing" - FALSE: You can build retention through respect
- "Speed vs. Accuracy" - SOMETIMES FALSE: Better algorithms can improve both
- "Cost vs. Quality" - CONTEXT-DEPENDENT: Automation can reduce cost while improving quality

### Can I modify the structured output schema?

The schema is versioned (v1.0). For custom needs:
1. Extend metadata fields (allowed)
2. Add optional fields to ideas/frames/experiments (allowed)
3. Modify required fields - create new schema version

See `schemas/creative/IDEATION_REPORT_v1.json` for extension points.

## Next Steps

- **Learn more:** See `docs/creative-triad/CREATIVE_TRIAD_GUIDE.md` for detailed usage patterns
- **Discover agents:** Use `python tools/agent_discovery.py` to find the right agent for your task
- **Validate outputs:** Run `python tools/validate_creative.py` to check report quality
- **Study examples:** Examine `tests/seed_templates/examples/` for complete workflows

## Related Documentation

- [Agent Discovery Guide](../AGENT_DISCOVERY_GUIDE.md) - How to use the discovery system
- [Ideation Report Schema](../../schemas/creative/IDEATION_REPORT_v1.json) - Structured output specification
- [System Architecture](../architecture.md) - Overall agent ecosystem design
- [Professional Standards](../PROFESSIONAL_STANDARDS.md) - Quality expectations for all agents
