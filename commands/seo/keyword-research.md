# SEO Keyword Research & Strategy

**Command:** `/seo-keyword-research`
**Agents:** `seo-keyword-strategist`, `seo-technical-auditor`, `seo-structure-architect`
**Complexity:** Medium-High
**Duration:** 4-8 hours (depending on scope)

## Overview

Performs comprehensive keyword research and strategy development, identifying high-opportunity keywords, analyzing search intent, creating keyword clusters, and mapping keywords to content strategy and site architecture.

## What This Command Does

This command orchestrates a complete keyword research workflow across three specialized agents:

1. **Keyword Research & Strategy** (`seo-keyword-strategist`)
   - Seed keyword expansion and discovery
   - Search volume and competition analysis
   - Search intent classification
   - Keyword clustering and topic modeling
   - Competitive keyword gap analysis
   - Opportunity scoring and prioritization

2. **Technical Validation** (`seo-technical-auditor`)
   - Ensure target keywords are indexable
   - Validate existing keyword rankings
   - Identify cannibalization issues
   - Check Search Console query data

3. **Site Architecture Mapping** (`seo-structure-architect`)
   - Map keyword clusters to site structure
   - Plan content silos and topic clusters
   - Design URL structure for new content
   - Plan internal linking strategy

## Usage

```bash
# Industry/topic keyword research
/seo-keyword-research --topic="project management"

# Competitor-based keyword research
/seo-keyword-research --competitor=https://competitor.com

# Product/service keyword research
/seo-keyword-research --product="CRM software" --intent=commercial

# Local keyword research
/seo-keyword-research --business="coffee shop" --location="San Francisco"

# Batch keyword analysis
/seo-keyword-research --keywords=keyword-list.csv
```

## Execution Workflow

### Phase 1: Seed Keyword Discovery (30-60 min)

**seo-keyword-strategist** identifies seed keywords:

**Methods:**
1. **Business Understanding:**
   - Products/services offered
   - Target audience and personas
   - Industry and niche
   - Unique value propositions

2. **Brainstorming:**
   - 10-20 core seed keywords
   - Product/service names
   - Problem-based keywords (pain points)
   - Solution-based keywords (benefits)

3. **Competitor Analysis:**
   - Extract keywords from 3-5 top competitors
   - Identify their top-ranking keywords
   - Find gaps in their keyword coverage

4. **Search Console Data:**
   - Existing keyword rankings (if available)
   - Queries driving traffic
   - Underperforming opportunities

**Example Output:**
```
Seed Keywords (15 total):
- project management software
- project management tools
- task management software
- project tracking app
- team collaboration software
- agile project management
- project planning tool
- workflow management
- resource management software
- project portfolio management
- kanban board software
- gantt chart software
- project management for teams
- online project management
- best project management software
```

### Phase 2: Keyword Expansion (60-90 min)

**seo-keyword-strategist** expands seed keywords:

**Expansion Techniques:**
1. **Tool-Based Expansion:**
   - Google Keyword Planner: Related keywords, search volume
   - Ahrefs/SEMrush: Keyword variations, related terms
   - Answer the Public: Question-based keywords
   - AlsoAsked: People Also Ask questions
   - Google Trends: Trending variations, related queries

2. **Modifiers:**
   - Best, top, review, comparison (commercial)
   - How to, what is, guide, tutorial (informational)
   - Buy, pricing, cost, free trial (transactional)
   - vs, alternative, comparison (comparison)
   - Near me, in [location] (local)
   - 2024, 2025 (time-based)

3. **Long-Tail Discovery:**
   - 3-5 word keyword phrases
   - Question-based keywords
   - Specific use case keywords
   - Industry-specific terminology

**Example Output:**
```
Expanded Keywords: 487 total keywords

Top Keywords by Volume:
1. project management software - 5,400 volume, 67 difficulty, Commercial
2. project management tools - 3,200 volume, 65 difficulty, Commercial
3. best project management software - 2,900 volume, 72 difficulty, Commercial
4. free project management software - 2,100 volume, 58 difficulty, Commercial
5. project management app - 1,800 volume, 61 difficulty, Commercial

Long-Tail Opportunities (50+ keywords):
- project management software for small teams - 320 volume, 45 difficulty
- project management tools for remote teams - 280 volume, 42 difficulty
- best free project management software for startups - 210 volume, 38 difficulty
- agile project management software for developers - 190 volume, 41 difficulty

Question Keywords (30+ keywords):
- what is project management software - 890 volume, 35 difficulty
- how to choose project management software - 420 volume, 40 difficulty
- why use project management software - 310 volume, 32 difficulty
```

### Phase 3: Search Intent Analysis (45-60 min)

**seo-keyword-strategist** classifies search intent:

**Intent Types:**
1. **Informational (40-50% of keywords):**
   - User seeks information/knowledge
   - Content: Blog posts, guides, tutorials, how-tos
   - Examples: "what is project management", "how to plan a project"

2. **Navigational (10-15% of keywords):**
   - User seeks specific brand/website
   - Content: Brand pages, product pages
   - Examples: "asana login", "monday.com pricing"

3. **Commercial (30-40% of keywords):**
   - User researching before purchase
   - Content: Comparisons, reviews, "best" lists, buying guides
   - Examples: "best project management software", "asana vs monday"

4. **Transactional (10-20% of keywords):**
   - User ready to purchase/sign up
   - Content: Product pages, pricing pages, signup flows
   - Examples: "buy project management software", "project management free trial"

**Example Output:**
```
Intent Classification (487 keywords):

Informational (215 keywords, 44%):
- what is project management software (890 volume)
- project management best practices (720 volume)
- how to manage a project (650 volume)

Commercial (187 keywords, 38%):
- best project management software (2,900 volume)
- project management software comparison (810 volume)
- asana vs monday (680 volume)

Transactional (62 keywords, 13%):
- project management software free trial (540 volume)
- buy project management software (290 volume)

Navigational (23 keywords, 5%):
- asana project management (1,200 volume)
- trello login (890 volume)
```

### Phase 4: Keyword Clustering (60-90 min)

**seo-keyword-strategist** groups keywords into clusters:

**Clustering Methods:**
1. **Topic-Based Clustering:**
   - Group semantically similar keywords
   - Create topic clusters around pillar content
   - Map clusters to content types

2. **Search Intent Clustering:**
   - Group by search intent (informational, commercial, etc.)
   - Align clusters with funnel stages (awareness, consideration, decision)

3. **Algorithmic Clustering:**
   - Use keyword similarity algorithms
   - SERP overlap analysis (keywords with similar top 10 results)
   - Semantic relationship analysis

**Example Output:**
```
Keyword Clusters: 12 clusters identified

Cluster 1: Core Product (Pillar Content)
- Pillar keyword: "project management software" (5,400 volume)
- Cluster keywords (45 total): "project management tools", "task management software", "project tracking app"
- Recommended content: Comprehensive pillar page (3,000+ words)
- Cluster pages: 6-8 supporting articles

Cluster 2: Best/Comparison (Commercial)
- Pillar keyword: "best project management software" (2,900 volume)
- Cluster keywords (32 total): "top project management tools", "project management software comparison"
- Recommended content: Comparison guide with detailed reviews
- Cluster pages: Individual product reviews (10-15 pages)

Cluster 3: Use Cases (Informational/Commercial)
- Pillar keyword: "project management for teams" (1,100 volume)
- Cluster keywords (28 total): "project management for remote teams", "project management for small business"
- Recommended content: Use case guides
- Cluster pages: 8-10 specific use case articles

Cluster 4: Features (Informational)
- Pillar keyword: "project management features" (680 volume)
- Cluster keywords (25 total): "kanban board software", "gantt chart software", "time tracking software"
- Recommended content: Feature deep-dives
- Cluster pages: 5-7 feature explainer articles

[8 more clusters...]
```

### Phase 5: Competitive Gap Analysis (60-90 min)

**seo-keyword-strategist** identifies competitor keyword gaps:

**Analysis:**
1. **Competitor Keyword Extraction:**
   - Identify 3-5 top competitors
   - Extract their ranking keywords (top 100)
   - Analyze their keyword strengths

2. **Gap Identification:**
   - Keywords competitors rank for, you don't
   - Keywords with ranking opportunity (you rank 11-30, they rank top 10)
   - High-volume keywords you're not targeting

3. **Opportunity Scoring:**
   - Search volume (traffic potential)
   - Keyword difficulty (ranking feasibility)
   - Relevance (business alignment)
   - Competition (current rankings)

**Example Output:**
```
Competitive Gap Analysis

Competitor 1: asana.com
- Total ranking keywords: 12,400
- Top 10 rankings: 3,200
- Keywords we don't target: 1,850

Competitor 2: monday.com
- Total ranking keywords: 11,800
- Top 10 rankings: 2,950
- Keywords we don't target: 1,620

Competitor 3: clickup.com
- Total ranking keywords: 9,200
- Top 10 rankings: 2,100
- Keywords we don't target: 1,420

High-Opportunity Gap Keywords (100 total):
1. "project management templates" - 1,200 volume, 48 difficulty (all 3 competitors rank top 5)
2. "project management certification" - 890 volume, 52 difficulty (2 competitors rank top 10)
3. "agile vs waterfall" - 780 volume, 45 difficulty (all 3 competitors rank top 10)
4. "project management methodologies" - 720 volume, 50 difficulty (2 competitors rank top 5)

Medium-Opportunity Gap Keywords (200 total):
[...]

Total Opportunity: 1,200+ keywords not currently targeted
Estimated traffic potential: 45,000-60,000 monthly visits
```

### Phase 6: Keyword Prioritization (30-45 min)

**seo-keyword-strategist** prioritizes keywords:

**Prioritization Framework:**
1. **Opportunity Score:**
   - Search volume: Weight 40%
   - Keyword difficulty: Weight 30%
   - Relevance: Weight 20%
   - Competition: Weight 10%

2. **Effort Estimation:**
   - Content length required
   - Competition strength
   - Domain authority needed
   - Link building effort

3. **Opportunity vs. Effort Matrix:**
   - Quick wins: High opportunity, low effort
   - Strategic targets: High opportunity, high effort
   - Fill-ins: Low opportunity, low effort
   - Avoid: Low opportunity, high effort

**Example Output:**
```
Keyword Prioritization Matrix

Quick Wins (25 keywords):
- High opportunity, low difficulty (sweet spot)
- Can rank within 3-6 months with quality content

1. "project management software for small teams" - Opportunity: 85/100, Effort: 35/100
2. "free project management tools for startups" - Opportunity: 78/100, Effort: 30/100
3. "project management templates free" - Opportunity: 82/100, Effort: 25/100

Strategic Targets (40 keywords):
- High opportunity, high difficulty (long-term investment)
- Requires comprehensive content + link building

1. "best project management software" - Opportunity: 95/100, Effort: 85/100
2. "project management software" - Opportunity: 98/100, Effort: 90/100
3. "project management tools" - Opportunity: 92/100, Effort: 88/100

Fill-ins (30 keywords):
- Low opportunity, low difficulty (content gaps)
- Easy to rank, moderate traffic

1. "project management tips for beginners" - Opportunity: 45/100, Effort: 20/100
2. "how to create a project timeline" - Opportunity: 50/100, Effort: 25/100
```

### Phase 7: Site Architecture Mapping (45-60 min)

**seo-structure-architect** maps keywords to site structure:

**Architecture Design:**
1. **URL Structure:**
   - Plan URL hierarchy for keyword clusters
   - Design SEO-friendly URL slugs
   - Map keywords to URL paths

2. **Content Silos:**
   - Organize keyword clusters into topic silos
   - Design pillar-cluster architecture
   - Plan internal linking strategy

3. **Navigation Hierarchy:**
   - Map keyword clusters to main navigation
   - Design category structure
   - Plan breadcrumb hierarchy

**Example Output:**
```
Site Architecture Plan

Pillar Content (12 pillar pages):
/project-management-software (Cluster 1 - 45 keywords)
  ├── /features
  │   ├── /kanban-boards (Cluster 4 - 25 keywords)
  │   ├── /gantt-charts
  │   └── /time-tracking
  ├── /use-cases
  │   ├── /for-remote-teams (Cluster 3 - 28 keywords)
  │   ├── /for-small-business
  │   └── /for-agencies
  └── /comparisons
      ├── /asana-vs-monday (Cluster 2 - 32 keywords)
      ├── /best-project-management-software
      └── /project-management-software-reviews

/blog
  ├── /guides
  │   ├── /what-is-project-management
  │   ├── /how-to-manage-a-project
  │   └── /project-management-best-practices
  ├── /templates
  │   ├── /project-plan-template
  │   └── /project-timeline-template
  └── /tips
      └── /project-management-tips

Internal Linking Strategy:
- Pillar pages link to all cluster pages
- Cluster pages link back to pillar
- Cross-silo linking for related topics
- 2-5 contextual links per 1,000 words
```

### Phase 8: Technical Validation (30-45 min)

**seo-technical-auditor** validates keyword targets:

**Validation Checks:**
1. **Indexability:**
   - Ensure target pages are crawlable
   - Check robots.txt isn't blocking
   - Validate meta robots tags

2. **Cannibalization:**
   - Identify multiple pages targeting same keyword
   - Recommend consolidation or differentiation
   - Plan canonical strategy

3. **Current Rankings:**
   - Check existing rankings for target keywords
   - Identify pages already ranking (optimize vs. create new)
   - Find ranking opportunities (position 11-30)

**Example Output:**
```
Technical Validation Report

Indexability Check: ✓ PASSED
- All planned URLs are crawlable
- No robots.txt conflicts
- Site architecture supports keyword strategy

Cannibalization Issues: 3 found
- "project management software" targeted by 3 pages (consolidate)
- "best project management tools" targeted by 2 pages (differentiate)
- "project tracking app" targeted by 2 pages (canonical to primary)

Current Rankings (from Search Console):
- 45 keywords already ranking (optimize existing content)
- 120 keywords position 11-30 (quick win opportunities)
- 322 keywords not ranking (create new content)

Recommendations:
1. Consolidate 3 cannibalized pages → 1 comprehensive page
2. Optimize 45 existing ranking pages (low-hanging fruit)
3. Create 322 new pages for unranked target keywords
4. Set canonical URLs for duplicate content
```

### Phase 9: Content Roadmap (30-45 min)

**Final deliverable - comprehensive keyword strategy:**

**Content Roadmap:**
```markdown
# Keyword Research & Content Roadmap
**Date:** 2024-10-08
**Total Keywords:** 487 analyzed

## Executive Summary
- **Total Opportunity:** 487 keywords, 85,000+ monthly search volume
- **Quick Wins:** 25 keywords (rank within 3-6 months)
- **Strategic Targets:** 40 keywords (12-18 months)
- **Content Required:** 12 pillar pages, 80-100 cluster pages
- **Estimated Traffic Potential:** 45,000-60,000 monthly organic visits (12-18 months)

## Keyword Clusters

### Cluster 1: Core Product (Priority: HIGH)
- **Pillar Keyword:** "project management software" (5,400 volume, 67 difficulty)
- **Cluster Size:** 45 keywords
- **Intent:** Commercial
- **Content:** Comprehensive pillar page (3,000+ words) + 6-8 cluster pages
- **Timeline:** Month 1-2
- **Estimated Traffic:** 8,000-12,000 monthly visits

### Cluster 2: Best/Comparison (Priority: HIGH)
- **Pillar Keyword:** "best project management software" (2,900 volume, 72 difficulty)
- **Cluster Size:** 32 keywords
- **Intent:** Commercial
- **Content:** Comparison guide + 10-15 product review pages
- **Timeline:** Month 2-3
- **Estimated Traffic:** 6,000-9,000 monthly visits

[10 more clusters...]

## Content Production Plan

### Month 1 (10 pieces):
1. Pillar: "Project Management Software - Complete Guide" (Cluster 1)
2-6. Cluster pages: Use case articles (remote teams, small business, agencies, etc.)
7-10. Quick wins: Long-tail low-difficulty keywords

### Month 2 (12 pieces):
1. Pillar: "Best Project Management Software 2024" (Cluster 2)
2-7. Product reviews: Top 6 tools in-depth
8-12. Quick wins: Comparison articles

### Month 3 (15 pieces):
1. Pillar: "Project Management Features Explained" (Cluster 4)
2-10. Feature deep-dives: Kanban, Gantt, time tracking, etc.
11-15. Fill-ins: Tips and how-tos

[Months 4-12...]

## Success Metrics
- **Month 3:** 500-1,000 organic visits/month (quick wins ranking)
- **Month 6:** 5,000-8,000 organic visits/month (strategic targets starting to rank)
- **Month 12:** 25,000-35,000 organic visits/month (comprehensive coverage)
- **Month 18:** 45,000-60,000 organic visits/month (competitive positioning)

## Next Steps
1. Review and approve keyword clusters
2. Prioritize content production order
3. Assign writers/content creators
4. Begin content creation (Month 1 plan)
5. Track rankings weekly for target keywords
6. Refine strategy based on performance data
```

## Success Metrics

Track keyword research effectiveness through:
- **Keyword Coverage:** % of target keywords with content
- **Ranking Progress:** Average position for target keywords
- **Organic Traffic:** Monthly visits from target keywords
- **Quick Win Success:** % of quick-win keywords ranking top 10
- **Strategic Target Progress:** Position improvements for high-difficulty keywords
- **Content ROI:** Traffic per content piece published

## Common Use Cases

### New Website Keyword Strategy
```bash
/seo-keyword-research --topic="SaaS project management" --intent=all --output=comprehensive
```

### Competitive Keyword Targeting
```bash
/seo-keyword-research --competitors=asana.com,monday.com,clickup.com --gaps-only
```

### Local Business Keyword Research
```bash
/seo-keyword-research --business="dental practice" --location="Austin, TX" --radius=25mi
```

### E-commerce Product Keywords
```bash
/seo-keyword-research --products=products.csv --intent=commercial,transactional
```

## Integration with Other Commands

This command works well with:
- `/seo-content-optimization` - Optimize content for researched keywords
- `/comprehensive-seo-audit` - Validate keyword strategy against current site
- `/seo-site-architecture` - Implement keyword-driven site structure
- `/seo-technical-audit` - Ensure keywords are indexable

## Prerequisites

### Required Access
- Keyword research tool (Ahrefs, SEMrush, Moz, or Google Keyword Planner)
- Google Search Console (for existing rankings, if available)
- Competitor URLs (for gap analysis)

### Recommended Tools
- Ahrefs or SEMrush (comprehensive keyword data)
- Answer the Public (question keywords)
- AlsoAsked (People Also Ask questions)
- Google Trends (trending variations)

## Limitations

- **Time Required:** 4-8 hours for comprehensive research
- **Tool Access:** Requires paid keyword research tool for best results
- **Language:** Optimized for English (other languages may need adjustments)
- **Industry:** B2B and B2C supported (local requires location data)

## Best Practices

1. **Start Broad, Narrow Down:** Begin with 10-20 seed keywords, expand to 500+, prioritize to 100-150 targets
2. **Match Search Intent:** Ensure content type matches keyword intent (informational → blog, commercial → comparison, etc.)
3. **Target Keyword Clusters, Not Individual Keywords:** Build comprehensive topic coverage
4. **Balance Quick Wins and Strategic Targets:** Mix low-difficulty and high-opportunity keywords
5. **Update Quarterly:** Keyword trends change; refresh research every 3-6 months
6. **Track Competitors:** Monitor competitor keyword rankings; adapt strategy
7. **Validate with Search Console:** Use existing ranking data to inform strategy
8. **Map to Site Architecture:** Plan site structure around keyword clusters before content creation

---

**Pro Tip**: Focus 70% of effort on commercial intent keywords (comparisons, reviews, "best" lists) for faster ROI, and 30% on informational content for long-term topical authority and backlink acquisition.
