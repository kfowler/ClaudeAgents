# Mobile Engagement Golden Example

## Problem Statement

**Current State:** Mobile productivity app with 30% D1 retention rate
**Target:** Increase to 50% D1 retention while improving user satisfaction
**Challenge:** Users report feeling overwhelmed and manipulated by standard engagement tactics (streaks, notifications, social proof)

## Constraints

- **Ethical:** No dark patterns or manipulative tactics allowed
- **Privacy:** Privacy-first approach with minimal data collection
- **Technical:** Must work offline-first for low-connectivity users
- **UX:** Maximum 3 notification categories to avoid overwhelm

## Creative Triad Workflow

### Phase 1: Divergent Ideation (creative-catalyst)

**Agent:** `creative-catalyst`
**Mode:** Oblique strategies
**Output:** 10 ideas with 0.88 overall diversity score

**Key Ideas Generated:**
1. **Reverse Onboarding** - Hide features until users express need (novelty: 0.75)
2. **Social Vulnerability** - Ephemeral authentic sharing spaces (novelty: 0.82)
3. **Anti-Metrics** - Replace quantitative metrics with qualitative impact (novelty: 0.88)
4. **Scheduled Unavailability** - Intentional downtime with reflection gates (novelty: 0.90)
5. **Collaborative Content** - All content co-created by multiple users (novelty: 0.80)
6. And 5 more across mechanism, experience, and market dimensions

**Novelty Distribution:**
- Conventional: 0 ideas
- Moderate: 4 ideas (40%)
- Breakthrough: 6 ideas (60%)

**Diversity Metrics:**
- Mechanism diversity: 0.92
- Experience diversity: 0.89
- Market diversity: 0.84
- Overall: **0.88** (exceeds 0.75 threshold)

### Phase 2: Convergent Synthesis (the-synthesist)

**Agent:** `the-synthesist`
**Input:** 10 creative-catalyst ideas
**Output:** 3 strategic frames with 100% idea coverage

**Frame 1: Authentic Connection Over Performative Engagement**
- **Ideas clustered:** Anti-metrics, social vulnerability, failure celebration, collaborative content
- **Unifying principle:** Build retention through genuine human connection and authenticity rather than gamified metrics
- **Implementation:** 4 phases over quarters (remove metrics → vulnerability spaces → collaborative creation → failure celebration)
- **Frame strength:** 0.85

**Frame 2: Contextual Intelligence and Adaptive Experiences**
- **Ideas clustered:** Reverse onboarding, curiosity loops, time-based transformation, offline-first
- **Unifying principle:** Intelligent adaptation to user context, energy, and readiness
- **Implementation:** 4 phases over quarters (behavioral analytics → progressive disclosure → chronotype adaptation → offline architecture)
- **Frame strength:** 0.82

**Frame 3: Intentional Boundaries and Respectful Engagement**
- **Ideas clustered:** Earned notifications, scheduled unavailability
- **Unifying principle:** Respect user boundaries and treat attention as sacred resource
- **Implementation:** 4 phases over months (earned notifications → accountability dashboard → scheduled downtime → personalized boundaries)
- **Frame strength:** 0.78

**False Tradeoff Identified:**
> "Engagement vs. User Wellbeing" - Traditional thinking assumes you must choose between high engagement and user health. These frames prove you can build sustainable long-term retention by explicitly prioritizing wellbeing, boundaries, and authentic connection.

**Cross-Frame Synergies:**
- Authentic connection + Intentional boundaries: Vulnerability requires safety that includes downtime
- Contextual intelligence + Intentional boundaries: Smart systems power better boundary recommendations
- Authentic connection + Contextual intelligence: Progressive disclosure ensures users discover vulnerability features when ready

### Phase 3: Experimental Validation (the-architect-of-experiments)

**Agent:** `the-architect-of-experiments`
**Input:** 3 strategic frames
**Output:** 3 falsifiable experiments with 100% kill condition coverage

**Experiment 1: Earned Notifications (Frame 3)**
- **Hypothesis:** Zero-notification default with opt-in will decrease volume 60% while maintaining D7 retention within 5%
- **Method:** A/B test, 2500 users, 72 hours
- **Kill condition:** D3 retention drop ≥8% OR user frustration ≥50% at 48h
- **Success metrics:**
  - Notification volume reduction: ≥60%
  - Notification engagement rate increase: ≥3x
  - D7 retention parity: within 5% of control
- **Sequencing:** Run FIRST (fastest, lowest risk, 1 sprint implementation)

**Experiment 2: Contextual Disclosure (Frame 2)**
- **Hypothesis:** Progressive disclosure will increase feature discovery 40% and reduce abandonment 25%
- **Method:** A/B test, 1500 new users, 96 hours
- **Kill condition:** Feature discovery drop ≥30% OR early drop-off increase ≥20% at 48h
- **Success metrics:**
  - Feature discovery rate increase: ≥40pp
  - Feature abandonment decrease: ≥25pp
  - Celebration moment effectiveness: ≥70%
- **Sequencing:** Run SECOND (moderate risk, more complex implementation)

**Experiment 3: Anti-Metrics MVP (Frame 1)**
- **Hypothesis:** Removing visible metrics will increase D7 retention 15% and satisfaction 20%
- **Method:** A/B test, 2000 users, 72 hours
- **Kill condition:** D1 retention drop ≥10% OR session frequency drop ≥15% in first 24h
- **Success metrics:**
  - D7 retention increase: ≥15pp
  - User satisfaction increase: ≥2 points (1-10 scale)
  - Qualitative feedback engagement: ≥60%
- **Sequencing:** Run THIRD (highest risk but highest potential impact)

**Falsifiability Coverage:** 3/3 experiments (100%) have defined kill conditions

## Key Insights

### Strategic Positioning
This approach represents a coherent **counter-narrative to standard mobile engagement playbooks**. Instead of maximizing time-in-app through addictive mechanics, it builds retention through:
- Respect for user boundaries
- Intelligent contextual adaptation
- Authentic human connection

### Risk-Reward Profile
- **Highest Risk:** Experiment 3 (Anti-Metrics) - removes familiar validation signals
- **Highest Reward:** Experiment 3 - could create distinctive market positioning
- **Best ROI:** Experiment 1 (Earned Notifications) - quick win, builds confidence

### Implementation Path
**Recommended sequence:**
1. **Weeks 1-2:** Run Experiment 1 (Earned Notifications) - validate boundaries approach
2. **Weeks 3-4:** Analyze results, begin Experiment 2 (Contextual Disclosure) development
3. **Weeks 5-6:** Run Experiment 2 - validate intelligence approach
4. **Weeks 7-8:** If Exp 1 & 2 successful, run Experiment 3 (Anti-Metrics) - validate authenticity approach

**Decision gates:**
- If Experiment 1 fails (hits kill condition): Re-evaluate Frame 3, may need gentler boundaries
- If Experiment 2 fails: Simplify progressive disclosure, may be too aggressive on feature hiding
- If Experiment 3 fails: Consider hybrid approach (reduce metrics visibility rather than eliminate)

### Success Criteria

**Individual Experiment Success:**
- All quantitative metrics hit targets
- No kill conditions triggered
- Qualitative feedback positive

**Strategic Success (if all 3 experiments succeed):**
- D1 retention: 30% → 40%+ (toward 50% target)
- User satisfaction: 20%+ improvement
- Distinctive positioning: "The app that respects you"

## Files in This Example

1. **creative-catalyst-output.golden.json** - Divergent ideation with oblique strategies
2. **synthesist-output.golden.json** - Convergent synthesis into 3 frames
3. **architect-output.golden.json** - Falsifiable experiment designs
4. **README.md** - This walkthrough

## Validation

All outputs validate against:
- `schemas/creative/IDEATION_REPORT_v1.json`
- Diversity thresholds (≥0.6 overall score)
- Falsifiability requirements (100% kill condition coverage)
- Duration constraints (48-120 hours per experiment)

Run validation:
```bash
python tools/validate_creative.py tests/seed_templates/examples/mobile_engagement/creative-catalyst-output.golden.json
python tools/validate_creative.py tests/seed_templates/examples/mobile_engagement/synthesist-output.golden.json
python tools/validate_creative.py tests/seed_templates/examples/mobile_engagement/architect-output.golden.json
```

Generate scorecard:
```bash
python tools/scorecard_creative.py tests/seed_templates/examples/mobile_engagement/
```
