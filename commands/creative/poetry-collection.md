---
name: poetry-collection
description: Complete poetry collection development workflow coordinating poet, the-critic, and technical-writer for professional manuscript submission and publication
---

# Poetry Collection

## Overview

This command orchestrates the development of a professional poetry collection from individual poems to publication-ready manuscript. It coordinates creative writing, critical evaluation, and manuscript formatting to produce a cohesive collection suitable for book contests, publisher submissions, or self-publication.

**What this accomplishes:**
- 40-80 poems with thematic or narrative coherence forming complete collection
- Critical analysis identifying strongest work and structural weaknesses
- Publication-ready manuscript formatted to industry standards
- Submission materials (cover letter, bio, synopsis) for contests and publishers

**When to use:**
- Chapbook development (20-30 pages)
- Full-length collection preparation (50-80 pages)
- Book contest submissions (Nationnicholl, Yale Series, etc.)
- Publisher solicitations or self-publication projects

**Expected outcomes:**
- Cohesive poetry collection with clear through-line
- Professionally formatted manuscript ready for submission
- Strategic submission plan targeting appropriate venues

**Estimated execution time:** 3-6 months for full collection development and revision

## Multi-Agent Orchestration Strategy

### **Phase 1: Poem Generation & Revision**
Deploy `poet` to:
- Write 50-100 individual poems exploring thematic territory for collection
- Revise poems through multiple drafts focusing on craft (imagery, sound, line breaks, form)
- Experiment with diverse forms (sonnets, free verse, prose poetry) and voices
- Develop signature style and recurring motifs connecting poems
- Workshop poems with feedback integration and ruthless self-editing

**Why this agent:** Poet specializes in verse composition with attention to craft, form, and literary quality across traditional and contemporary poetry.

### **Phase 2: Critical Analysis & Selection**
Engage `the-critic` to:
- Evaluate entire body of work identifying strongest 40-60 poems for collection
- Analyze thematic coherence and identify through-line or narrative arc
- Identify weak craft moments (clichés, sentimentality, unclear imagery, ineffective line breaks)
- Recommend poems for cutting, revision priorities, and structural organization
- Provide honest assessment of publication readiness and target audience fit

**Why this agent:** The-critic provides objective evaluation identifying weaknesses poet may overlook due to attachment. Ensures only strongest work included in final manuscript.

**Handoff:** Poet provides complete poem portfolio. Critic evaluates craft quality, thematic coherence, and collection potential, returning curated selection with revision notes.

### **Phase 3: Collection Architecture**
Return to `poet` to:
- Organize selected poems into sections with intentional arc (chronological, thematic, tonal progression)
- Write section titles or epigraphs if appropriate for collection structure
- Determine opening poem (strong, inviting) and closing poem (resonant, memorable)
- Create transitions between sections through poem placement and thematic bridges
- Final polish on individual poems informed by collection context

**Why this agent:** Poet makes final artistic decisions on structure, order, and polish ensuring collection reads as unified work.

**Handoff:** Critic's curation informs selection. Poet arranges poems architecturally, creating reading experience greater than sum of individual poems.

### **Phase 4: Manuscript Formatting & Submission Materials**
Use `technical-writer` to:
- Format manuscript to contest/publisher specifications (font, margins, spacing, page numbers)
- Create table of contents with poem titles and page numbers
- Write cover letter introducing collection, explaining themes, and highlighting credentials
- Draft author bio (50-100 words) with publication credits and relevant background
- Prepare collection synopsis (1-page) for submissions requiring project description
- Research and compile target submission venues (contests, publishers, literary journals for chapbook series)

**Why this agent:** Technical-writer ensures professional formatting and submission materials meeting industry standards. Frees poet to focus on creative work.

**Handoff:** Finalized poems and collection structure provided. Technical-writer produces submission-ready package with all required materials.

## Execution Flow

```
Phase 1: Poem Generation & Revision (poet)
    ↓ [50-100 revised poems]
Phase 2: Critical Analysis & Selection (the-critic)
    ↓ [40-60 poems selected, revision notes]
Phase 3: Collection Architecture (poet)
    ↓ [Poems organized into cohesive collection]
Phase 4: Manuscript Formatting & Submission (technical-writer)
    ↓
[Publication-ready manuscript with submission materials]
```

## Expected Deliverables

- **Poetry Portfolio**: 50-100 revised poems in various stages (draft to polished)
- **Critical Evaluation**: Analysis identifying strongest poems, revision priorities, thematic assessment (5-10 page report)
- **Final Collection**: 40-60 poems organized into 2-4 sections with intentional arc (50-80 manuscript pages)
- **Formatted Manuscript**: Industry-standard formatting (12pt Times, 1-inch margins, header with last name/title) (PDF + DOCX)
- **Cover Letter**: Personalized template for contest/publisher submissions (1 page, adaptable)
- **Author Bio**: Short (50 words) and long (150 words) versions with publication credits
- **Collection Synopsis**: 1-page overview of themes, structure, and poetic approach
- **Submission Target List**: 15-30 appropriate contests, publishers, or presses with deadlines and guidelines

## Success Criteria

- [ ] Collection has clear thematic through-line connecting poems
- [ ] Opening and closing poems are strong, memorable, and frame collection effectively
- [ ] Individual poems demonstrate craft excellence (imagery, sound, form, originality)
- [ ] Manuscript formatting meets professional standards for target venues
- [ ] Cover letter is personalized, professional, and highlights collection strengths
- [ ] Submission materials are error-free with accurate contact information
- [ ] Target venue list is realistic for poet's publication history and collection quality
- [ ] Collection length appropriate for target (chapbook 20-30 pages, full-length 50-80 pages)
- [ ] All poems have been revised through multiple drafts with workshop feedback

## Common Issues and Solutions

**Issue:** Collection lacks coherence, reads like random assortment of poems
**Solution:** Poet identifies thematic clusters, cuts outlier poems, writes bridging pieces if needed
**Prevention:** Define collection concept early, write with unifying theme in mind

**Issue:** Strongest poems are scattered, weak poems dilute impact
**Solution:** Critic curates aggressively, poet accepts that favorite poems may not fit collection
**Prevention:** Separate attachment from quality assessment, trust outside evaluation

**Issue:** Collection opens weakly, readers don't engage with first poems
**Solution:** Poet reorders placing most accessible, powerful poem first
**Prevention:** Test opening poems with readers, prioritize immediate engagement

**Issue:** Manuscript formatting doesn't meet contest/publisher specifications
**Solution:** Technical-writer adjusts formatting to specific guidelines for each submission
**Prevention:** Research guidelines before formatting, create adaptable master template

**Issue:** Cover letter is generic, doesn't highlight collection uniqueness
**Solution:** Technical-writer customizes for each venue, mentions specific editors or publications
**Prevention:** Research venues thoroughly, personalize each submission

**Issue:** Poet receives repeated rejections, loses motivation
**Solution:** Expand submission list, target emerging venues, build publication credits with journal placements first
**Prevention:** Set realistic expectations (95%+ rejection rate normal), celebrate small victories

## Related Commands

- **`/creative:poetry-workshop`**: Focus on individual poem craft without collection development
- **`/quality:manuscript-review`**: Deep critical analysis of completed manuscript
- **`/creative:literary-submission-strategy`**: Submission planning without manuscript development

## Notes

**Collection Types:**
- **Chapbook (20-30 pages)**: Focused theme, single section or minimal sections, accessible entry point
- **Full-Length (50-80 pages)**: Multiple sections, broader thematic range, sustained vision
- **Concept Album**: Unified narrative or theme, poems interdependent, read as complete work
- **Selected Poems**: Career retrospective, greatest hits, typically for established poets

**Publication Paths:**
- **Book Contests**: Yale Series, National Poetry Series, Akron Prize ($1500-$5000 prize + publication)
- **Publisher Solicitation**: Submit to presses accepting unsolicited manuscripts (Copper Canyon, Graywolf, smaller indie presses)
- **Chapbook Series**: Literary journal chapbook contests (Ploughshares, Cincinnati Review)
- **Self-Publication**: Print-on-demand (Lulu, IngramSpark), full creative control, marketing responsibility

**Building Toward Collection:**
- Place individual poems in literary journals first (builds credentials)
- Win or place in poetry contests (signals quality to publishers)
- Develop social media/website presence (demonstrates audience)
- Attend conferences, meet editors, network (relationships matter)
- MFA not required but helpful for connections and craft development

**Timeline Estimates:**
- **Chapbook**: 6-12 months (if poems already written), 1-2 years from scratch
- **Full-Length**: 2-5 years for first collection (including journal publication building)
- **Submission Cycle**: Submit to 20-30 venues, expect 3-12 month response times

**Submission Strategy:**
- **Tiered Approach**: Submit to dream venues, realistic fits, and safety options simultaneously
- **Timing**: Many contests have fall/winter deadlines, plan accordingly
- **Fees**: Contest entry fees $20-$30 typical, budget $300-$600 for submission season
- **Persistence**: Finalists often receive encouraging rejections, resubmit to same venues annually

This workflow ensures professional poetry collection development through coordinated specialist expertise from individual poems to publication-ready manuscript.
