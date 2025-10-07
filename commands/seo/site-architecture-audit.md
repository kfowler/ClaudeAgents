# SEO Site Architecture Audit

**Command:** `/seo-site-architecture-audit`
**Agents:** `seo-structure-architect`, `seo-technical-auditor`, `seo-keyword-strategist`
**Complexity:** High
**Duration:** 6-10 hours (depending on site size)

## Overview

Performs comprehensive site architecture audit analyzing URL structure, internal linking, content silos, crawl efficiency, and link equity distribution to optimize site-wide SEO performance.

## What This Command Does

This command orchestrates a complete site architecture audit across three specialized agents:

1. **Architecture Analysis** (`seo-structure-architect`)
   - URL structure and hierarchy analysis
   - Navigation and site structure evaluation
   - Internal linking analysis and link equity distribution
   - Content silo identification
   - Crawl depth and efficiency analysis
   - Orphan page detection

2. **Technical Validation** (`seo-technical-auditor`)
   - Crawlability and indexability verification
   - XML sitemap architecture review
   - Robots.txt and meta robots analysis
   - Canonical URL strategy validation
   - Duplicate content detection

3. **Keyword Alignment** (`seo-keyword-strategist`)
   - Keyword-to-URL mapping analysis
   - Topic cluster validation
   - Search intent alignment with site structure
   - Content gap identification

## Usage

```bash
# Full site architecture audit
/seo-site-architecture-audit https://example.com

# Focus on specific issues
/seo-site-architecture-audit https://example.com --focus=orphans,internal-linking

# Crawl depth limit (for large sites)
/seo-site-architecture-audit https://example.com --crawl-limit=10000

# Compare with competitors
/seo-site-architecture-audit https://example.com --compare=competitor.com
```

## Execution Workflow

### Phase 1: Site Crawl & Discovery (60-90 min)

**seo-structure-architect** performs comprehensive site crawl:

**Crawl Analysis:**
- Total pages crawled
- Crawl depth distribution
- Page types (content, category, product, etc.)
- Response codes (200, 301, 404, etc.)
- Page load times
- File size distribution

**Example Output:**
```
Site Crawl Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total URLs Crawled: 8,342
Indexable URLs: 6,210 (74%)
Non-Indexable: 2,132 (26%)

Crawl Depth Distribution:
- Depth 0 (Homepage): 1 page
- Depth 1: 12 pages (main navigation)
- Depth 2: 145 pages (category/pillar pages)
- Depth 3: 1,420 pages (subcategories/cluster pages)
- Depth 4: 3,215 pages (articles/products)
- Depth 5: 1,200 pages (deep content)
- Depth 6+: 349 pages (very deep - crawl waste)

Average Crawl Depth: 3.8 clicks from homepage
Max Crawl Depth: 9 clicks (too deep)

Response Codes:
- 200 OK: 6,210 (74%)
- 301 Redirect: 1,120 (13%)
- 404 Not Found: 845 (10%)
- 403/500 Errors: 167 (2%)

Page Types:
- Blog posts: 3,420 (41%)
- Product pages: 1,850 (22%)
- Category pages: 420 (5%)
- Landing pages: 320 (4%)
- Other: 2,332 (28%)
```

### Phase 2: URL Structure Analysis (45-60 min)

**seo-structure-architect** analyzes URL patterns:

**URL Analysis:**
1. **Structure Patterns:**
   - Hierarchical vs. flat structure
   - URL length (optimal: <60 chars)
   - Semantic keywords in URLs
   - Subdirectory depth
   - Parameter usage

2. **URL Issues:**
   - Long URLs (>100 chars)
   - Non-semantic URLs (IDs, dates, UUIDs)
   - Duplicate content via URL parameters
   - Mixed HTTP/HTTPS
   - Trailing slash inconsistency

3. **URL Best Practices:**
   - Descriptive slugs
   - Keyword inclusion
   - Proper hierarchy
   - Clean structure (no parameters)

**Example Output:**
```
URL Structure Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Structure Type: Hierarchical (good)
- example.com/category/subcategory/article
- Average depth: 3.2 levels

URL Length Distribution:
- <50 chars: 2,420 (29%) ✓
- 50-75 chars: 3,210 (38%) ✓
- 75-100 chars: 1,850 (22%) ⚠️
- >100 chars: 862 (10%) ❌ (too long)

URL Issues Found:
❌ Long URLs (862 pages): URLs >100 characters
   Example: /blog/2024/10/08/how-to-choose-the-best-project-management-software-for-your-remote-team-in-2024
   Recommendation: Shorten to /blog/best-project-management-software-remote-teams

❌ Non-Semantic URLs (420 pages): URLs with IDs instead of keywords
   Example: /product?id=12345
   Recommendation: Use /products/project-management-software

❌ Parameter Pollution (320 pages): Faceted navigation creating duplicate URLs
   Example: /products?color=blue&size=large&sort=price
   Recommendation: Canonicalize to /products, use hash fragments, or noindex

⚠️ Trailing Slash Inconsistency (1,200 pages): Mixed with/without trailing slash
   Example: /blog/article vs. /blog/article/
   Recommendation: Standardize (with or without, consistently)

✓ HTTPS (100%): All pages use HTTPS
✓ Keyword Usage (85%): Most URLs include target keywords
```

### Phase 3: Internal Linking Analysis (90-120 min)

**seo-structure-architect** analyzes internal link distribution:

**Internal Linking Metrics:**
1. **Link Distribution:**
   - Total internal links
   - Links per page (average, min, max)
   - Link depth (clicks from homepage)
   - Orphan pages (no internal links)

2. **Link Equity Flow:**
   - PageRank distribution
   - Authority page identification
   - Link equity concentration
   - Siloed link patterns

3. **Anchor Text Analysis:**
   - Descriptive anchor text usage
   - Over-optimization detection
   - Branded vs. keyword anchors
   - Generic anchors ("click here")

**Example Output:**
```
Internal Linking Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Internal Links: 124,500
Links per Page (avg): 15.2 links

Link Distribution:
- 0-5 links: 1,240 pages (15%) ❌ (under-linked)
- 6-15 links: 4,210 pages (50%) ✓ (good)
- 16-30 links: 2,120 pages (25%) ✓ (good)
- 31+ links: 640 pages (8%) ⚠️ (over-linked, possible link dilution)

Orphan Pages: 342 pages (4%) ❌
- No internal links pointing to these pages
- Only accessible via sitemap or direct URL
- Examples:
  * /blog/old-article-2019
  * /hidden-landing-page
  * /product-archive/discontinued-product

Link Equity Distribution:
Top 10 Most Linked Pages (high authority):
1. Homepage: 8,420 internal links
2. /blog: 2,420 links
3. /products: 1,850 links
4. /pricing: 1,420 links
5. /features: 1,120 links

Priority Pages Under-Linked (opportunity):
1. /best-project-management-software: 12 links (should have 50+)
2. /project-management-for-remote-teams: 8 links (should have 30+)
3. /asana-vs-monday: 5 links (should have 25+)

Anchor Text Distribution:
- Descriptive (keyword-rich): 45% ✓
- Branded: 25% ✓
- Generic ("click here", "read more"): 20% ⚠️ (reduce)
- Over-optimized (exact match spam): 10% ❌ (diversify)

Recommendations:
1. Link to 342 orphan pages from related content
2. Increase internal links to under-linked priority pages
3. Reduce generic anchor text usage (20% → 10%)
4. Diversify over-optimized exact match anchors
```

### Phase 4: Content Silo Analysis (60-90 min)

**seo-structure-architect** evaluates topic clustering:

**Silo Analysis:**
1. **Topic Clusters:**
   - Pillar content identification
   - Cluster content grouping
   - Silo boundaries and isolation
   - Cross-silo linking

2. **Topical Authority:**
   - Topic coverage depth
   - Comprehensive vs. thin silos
   - Keyword cluster alignment
   - Content gaps within silos

**Example Output:**
```
Content Silo Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Identified Silos: 8 topic silos

Silo 1: Project Management Software (Strong)
- Pillar: /project-management-software (3,200 words, 45 internal links)
- Cluster pages: 32 pages
- Keywords covered: 145 keywords
- Internal linking: 95% of cluster pages link to pillar ✓
- Coverage: Comprehensive (strong topical authority)

Silo 2: Team Collaboration (Moderate)
- Pillar: /team-collaboration-tools (1,800 words, 18 internal links)
- Cluster pages: 12 pages
- Keywords covered: 48 keywords
- Internal linking: 75% link to pillar ⚠️ (improve)
- Coverage: Moderate (missing subtopics)

Silo 3: Agile Methodology (Weak)
- Pillar: None identified ❌
- Cluster pages: 8 orphaned pages
- Keywords covered: 22 keywords
- Internal linking: Fragmented, no clear hub
- Coverage: Thin (needs pillar content + structure)

Issues Found:
❌ Missing Pillars (3 silos): No clear pillar page for Agile, Kanban, Remote Work silos
❌ Orphaned Clusters (45 pages): Cluster content not linked to pillar
❌ Cross-Silo Leakage (120 links): Too many links between silos (dilutes authority)
❌ Thin Silos (2 silos): <10 pages, insufficient topical coverage

Recommendations:
1. Create pillar pages for 3 weak silos
2. Link 45 orphaned cluster pages to respective pillars
3. Reduce cross-silo links (120 → 40), keep silos isolated
4. Expand thin silos with 10-15 additional cluster pages each
```

### Phase 5: Crawl Efficiency Analysis (45-60 min)

**seo-technical-auditor** evaluates crawl efficiency:

**Crawl Metrics:**
1. **Crawl Waste:**
   - Non-indexable pages being crawled
   - Duplicate content
   - Low-value pages
   - Redirect chains

2. **Crawl Budget Optimization:**
   - Page importance vs. crawl depth
   - High-value pages deep in structure
   - Low-value pages shallow
   - Crawl priority misalignment

**Example Output:**
```
Crawl Efficiency Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Crawl Budget: ~8,000 pages/day (estimated)
Pages Crawled: 8,342

Crawl Waste: 2,420 pages (29%) ❌

Waste Breakdown:
- Noindexed pages: 1,200 (14%) - crawled but not indexed
- 404 pages: 845 (10%) - broken links being crawled
- Redirect chains: 375 (4%) - 3+ redirects consuming crawl

Crawl Priority Misalignment:
❌ High-Value Pages Too Deep (120 pages):
   - /best-project-management-software (depth 5, should be depth 2-3)
   - /asana-vs-monday (depth 6, should be depth 2-3)
   - /project-management-remote-teams (depth 5, should be depth 2-3)

❌ Low-Value Pages Too Shallow (340 pages):
   - /author/john-doe (depth 2, low search demand)
   - /tag/misc (depth 2, thin content)
   - /archive/2018 (depth 3, outdated)

Recommendations:
1. Noindex low-value pages (1,200 pages) to save crawl budget
2. Fix 845 broken links (404s)
3. Reduce redirect chains (consolidate 375 → direct links)
4. Move high-value pages shallower (depth 5-6 → depth 2-3)
5. Push low-value pages deeper or noindex
6. Estimated crawl waste reduction: 29% → 10%
```

### Phase 6: Link Equity Flow Analysis (60-90 min)

**seo-structure-architect** analyzes PageRank distribution:

**PageRank Analysis:**
1. **Link Equity Distribution:**
   - PageRank concentration (homepage, key pages)
   - Link equity leakage (external links, low-value pages)
   - Priority page authority
   - Link equity flow efficiency

2. **Strategic Link Placement:**
   - Homepage links to priority pages
   - Navigation links
   - Footer links
   - Sidebar links
   - Contextual links

**Example Output:**
```
Link Equity Flow Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PageRank Distribution (simulated):
Homepage: 1.00 (baseline)
Top Pages:
- /blog: 0.45 (45% of homepage authority)
- /products: 0.38
- /pricing: 0.32
- /features: 0.28

Priority Commercial Pages (should be high):
- /best-project-management-software: 0.08 ❌ (too low, should be 0.25+)
- /project-management-software: 0.12 ⚠️ (should be 0.30+)
- /asana-vs-monday: 0.05 ❌ (too low, should be 0.15+)

Link Equity Leakage:
❌ Footer Links (85 links): Excessive footer navigation diluting link equity
❌ Sidebar Links (42 links): Sidebar promoting low-value pages
❌ Author Pages (420 pages): Link equity flowing to author bios (low value)

Recommendations:
1. Add homepage links to priority commercial pages (3-5 strategic links)
2. Reduce footer links (85 → 30, only essential pages)
3. Remove sidebar links to low-value pages
4. Nofollow author page links (preserve equity for content)
5. Add contextual links from high-authority pages to commercial pages
6. Estimated priority page authority increase: 2-3x
```

### Phase 7: XML Sitemap Architecture (30-45 min)

**seo-technical-auditor** audits sitemap structure:

**Sitemap Analysis:**
1. **Sitemap Coverage:**
   - Pages in sitemap vs. actual pages
   - Missing important pages
   - Unnecessary pages included
   - Sitemap segmentation

2. **Sitemap Quality:**
   - Priority tags usage
   - Changefreq accuracy
   - Lastmod timestamps
   - Image/video sitemap inclusion

**Example Output:**
```
XML Sitemap Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sitemap URL: /sitemap.xml
Total URLs in Sitemap: 5,420

Coverage Analysis:
- Indexable pages: 6,210
- Pages in sitemap: 5,420
- Missing from sitemap: 790 pages ❌

Missing Important Pages (120 pages):
- /best-project-management-software (high priority, missing)
- /project-management-for-remote-teams (missing)
- 118 other commercial/blog pages

Pages That Shouldn't Be in Sitemap (340 pages):
- Noindexed pages: 120 (remove from sitemap)
- 404 pages: 85 (remove)
- Redirect pages: 135 (remove, use final destination)

Sitemap Segmentation:
✓ Using sitemap index: /sitemap.xml
✓ Segmented by type:
  - /sitemap-posts.xml (3,420 URLs)
  - /sitemap-products.xml (1,850 URLs)
  - /sitemap-pages.xml (150 URLs)

Priority Tag Usage:
⚠️ All pages have priority 0.5 (not strategic)
   Recommendation: Priority 1.0 for homepage, 0.8 for key pages, 0.5 for content

Recommendations:
1. Add 790 missing pages to sitemap
2. Remove 340 pages that shouldn't be included
3. Implement strategic priority tags
4. Update lastmod timestamps dynamically
5. Add image sitemap for 3,200+ images
```

### Phase 8: Canonical Strategy Analysis (30-45 min)

**seo-technical-auditor** reviews canonical URLs:

**Canonical Analysis:**
1. **Self-Referencing Canonicals:**
   - All indexable pages should have self-referencing canonical
   - Missing canonicals
   - Incorrect canonical targets

2. **Duplicate Content Handling:**
   - Parameter-based duplicates
   - WWW vs. non-WWW
   - HTTP vs. HTTPS
   - Trailing slash variations

**Example Output:**
```
Canonical Strategy Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Canonical Tag Coverage: 72% (4,470 / 6,210 pages)

Missing Canonicals: 1,740 pages ❌
- Should have self-referencing canonical

Incorrect Canonicals: 420 pages ❌
- Canonical points to different URL (consolidation intended?)
- Example: /blog/article → /blog/article?utm_source=email (wrong direction)

Canonical Chains: 85 pages ⚠️
- Page A canonicals to B, B canonicals to C (should A → C directly)

Duplicate Content Issues:
❌ Parameter Variations (320 pages):
   - /products, /products?sort=price, /products?filter=new
   - Recommendation: Canonical all variations to /products

❌ WWW Variation (6,210 pages accessible on both):
   - www.example.com and example.com both resolve
   - Recommendation: 301 redirect one to the other + canonical

✓ HTTPS Canonical: All canonicals use HTTPS (correct)

Recommendations:
1. Add self-referencing canonical to 1,740 pages
2. Fix 420 incorrect canonical directions
3. Resolve 85 canonical chains (A → C directly)
4. Canonical all parameter variations to clean URL
5. Enforce www vs. non-www consistency (pick one, redirect other)
```

### Phase 9: Architecture Recommendations (45-60 min)

**Final deliverable - comprehensive architecture report:**

```markdown
# Site Architecture Audit Report
**Site:** example.com
**Date:** 2024-10-08
**Pages Audited:** 8,342

## Executive Summary

**Overall Architecture Health:** 65/100 (Needs Improvement)

**Critical Issues (11):**
1. 342 orphan pages (4% of site) - no internal links
2. 862 URLs too long (>100 chars)
3. 1,740 pages missing canonical tags
4. 790 important pages missing from sitemap
5. 120 high-value pages too deep (depth 5-6, should be 2-3)
6. 2,420 pages wasting crawl budget (29%)
7. Priority commercial pages under-linked (8-12 links, need 30-50)
8. 3 silos missing pillar content
9. 420 pages with incorrect canonical direction
10. Link equity leaking to low-value pages (footer, sidebar)
11. Over-optimized anchor text (10% exact match spam)

**High-Priority Recommendations (6):**
1. Fix orphan pages: Link 342 pages from related content
2. Optimize URL structure: Shorten 862 long URLs
3. Add canonicals: Implement 1,740 missing self-referencing canonicals
4. Update sitemap: Add 790 missing pages, remove 340 unnecessary
5. Shallow high-value pages: Move 120 priority pages from depth 5-6 to 2-3
6. Reduce crawl waste: Noindex low-value pages, fix 404s (29% → 10%)

**Expected Impact:**
- **Crawl Efficiency:** +40% (waste 29% → 10%)
- **Link Equity to Priority Pages:** +200-300% (via strategic internal linking)
- **Indexation:** +12% (1,740 pages with proper canonicals)
- **Organic Traffic:** +25-35% within 6-12 months (better architecture)

## Detailed Findings

### URL Structure (Score: 58/100)

**Issues:**
- 862 URLs >100 chars (10%) ❌
- 420 non-semantic URLs with IDs ❌
- 320 parameter pollution pages ❌
- 1,200 trailing slash inconsistency ⚠️

**Recommendations:**
1. Shorten URLs: Reduce 862 long URLs to <75 chars
   - Before: /blog/2024/10/08/how-to-choose-the-best-project-management-software-for-your-remote-team-in-2024
   - After: /blog/best-project-management-software-remote-teams
2. Semantic URLs: Convert 420 ID-based URLs to keyword-rich slugs
3. Canonicalize parameters: 320 faceted nav pages → clean URL canonical
4. Standardize trailing slashes: Pick with or without, 301 redirect inconsistencies

### Internal Linking (Score: 62/100)

**Issues:**
- 342 orphan pages (4%) ❌
- Priority pages under-linked (8-12 links, need 30-50) ❌
- 640 pages over-linked (31+ links) ⚠️
- Generic anchor text (20%) ⚠️

**Recommendations:**
1. Link orphans: Add 2-5 contextual links to each orphan from related pages
2. Boost priority pages: Homepage + hub pages link to commercial pages
   - /best-project-management-software: 12 → 50 links
   - /asana-vs-monday: 5 → 25 links
3. Reduce link dilution: Trim 640 over-linked pages (31+ → 20-25 links)
4. Improve anchors: Reduce generic "click here" (20% → 10%)

### Content Silos (Score: 70/100)

**Issues:**
- 3 silos missing pillar content ❌
- 45 orphaned cluster pages ❌
- 120 cross-silo links (too much) ⚠️
- 2 thin silos (<10 pages) ⚠️

**Recommendations:**
1. Create pillars: Write 3 comprehensive pillar pages for weak silos
2. Link clusters: Connect 45 orphaned cluster pages to pillars
3. Reduce cross-silo links: 120 → 40 (preserve silo isolation)
4. Expand thin silos: Add 10-15 pages to each thin silo

### Crawl Efficiency (Score: 55/100)

**Issues:**
- 29% crawl waste (2,420 pages) ❌
- 120 priority pages too deep ❌
- 845 broken links (404s) ❌
- 375 redirect chains ⚠️

**Recommendations:**
1. Noindex low-value: 1,200 pages (author bios, tags, archives)
2. Flatten priority pages: Move 120 commercial pages shallower (depth 5-6 → 2-3)
3. Fix broken links: 845 404s wasting crawl budget
4. Eliminate redirect chains: 375 pages with 3+ redirects
5. Estimated waste reduction: 29% → 10%

### Link Equity Distribution (Score: 60/100)

**Issues:**
- Priority pages under-powered (PageRank 0.05-0.12, need 0.20-0.35) ❌
- Footer link dilution (85 links) ❌
- Link equity to low-value pages (author bios) ⚠️

**Recommendations:**
1. Homepage links: Add 3-5 strategic links to commercial pages
2. Reduce footer: 85 → 30 links (only essential)
3. Nofollow low-value: Author bios, tags (preserve equity)
4. Hub-and-spoke: High-authority blog posts link to commercial pages
5. Estimated priority page authority: +200-300%

### XML Sitemap (Score: 75/100)

**Issues:**
- 790 pages missing from sitemap ❌
- 340 pages shouldn't be in sitemap ❌
- Priority tags not strategic ⚠️

**Recommendations:**
1. Add missing pages: 790 important pages
2. Remove unnecessary: 340 noindexed/404/redirect pages
3. Strategic priority: Homepage 1.0, key pages 0.8, content 0.5
4. Dynamic lastmod: Auto-update on content change
5. Add image sitemap: 3,200+ images

### Canonical Strategy (Score: 68/100)

**Issues:**
- 1,740 missing canonicals ❌
- 420 incorrect canonical direction ❌
- 85 canonical chains ⚠️

**Recommendations:**
1. Self-referencing canonicals: Add to 1,740 pages
2. Fix direction: 420 incorrect canonicals
3. Resolve chains: 85 pages, canonical A → C directly
4. Parameter handling: Canonical all variations to clean URL
5. WWW consistency: Pick one, 301 redirect other

## Implementation Roadmap

### Month 1 (Critical Fixes)
1. Add 1,740 self-referencing canonicals
2. Fix 342 orphan pages (link from related content)
3. Update sitemap (+790 pages, -340 pages)
4. Add homepage links to 5 priority commercial pages
5. Noindex 1,200 low-value pages (save crawl budget)

### Month 2 (Structure Improvements)
1. Shorten 862 long URLs (implement 301 redirects)
2. Move 120 priority pages shallower (depth 5-6 → 2-3)
3. Fix 845 broken links (404s)
4. Create 3 missing pillar pages
5. Link 45 orphaned cluster pages to pillars

### Month 3 (Link Equity Optimization)
1. Reduce footer links (85 → 30)
2. Add 2-5 contextual internal links to priority pages
3. Nofollow author/tag links
4. Reduce over-linked pages (640 pages from 31+ → 20-25 links)
5. Improve anchor text (reduce generic 20% → 10%)

### Month 4 (Polish & Validation)
1. Fix 420 incorrect canonicals
2. Eliminate 375 redirect chains
3. Reduce cross-silo links (120 → 40)
4. Expand 2 thin silos (+10-15 pages each)
5. Validate all fixes, run follow-up audit

## Success Metrics

**Month 1:**
- Crawl waste: 29% → 20%
- Indexed pages: +12% (canonical fixes)
- Orphan pages: 342 → 0

**Month 3:**
- Crawl waste: 20% → 10%
- Priority page authority: +100-150%
- Link equity to commercial pages: +2x

**Month 6:**
- Organic traffic: +15-20%
- Priority page rankings: +5-10 positions avg
- Crawl efficiency: +40%

**Month 12:**
- Organic traffic: +25-35%
- Priority page rankings: Top 10 for 50% of targets
- Site architecture score: 65 → 85/100
```

## Success Metrics

Track architecture improvements through:
- **Crawl Efficiency:** Crawl waste reduction (target: <15%)
- **Link Equity:** PageRank to priority pages (2-3x increase)
- **Indexation:** % of site indexed (target: >85%)
- **Orphan Pages:** Zero orphan pages
- **Crawl Depth:** Priority pages at depth 2-3 (target: 90%+)
- **Organic Traffic:** Overall organic traffic increase (12-month baseline)

## Common Use Cases

### E-commerce Site Architecture
```bash
/seo-site-architecture-audit https://shop.example.com --focus=products,categories
```

### Blog/Content Site Architecture
```bash
/seo-site-architecture-audit https://blog.example.com --focus=silos,internal-linking
```

### Large Site (>10k pages)
```bash
/seo-site-architecture-audit https://large-site.com --crawl-limit=20000 --priority=critical
```

## Integration with Other Commands

This command works well with:
- `/comprehensive-seo-audit` - Complete SEO health check
- `/seo-technical-audit` - Technical crawlability issues
- `/seo-keyword-research` - Map keyword clusters to architecture
- `/seo-content-optimization` - Optimize pages within improved structure

## Prerequisites

### Required Tools
- Screaming Frog SEO Spider (for crawling >500 pages)
- Google Search Console access
- Site access for technical implementation

### Site Requirements
- Sitemap accessible
- Robots.txt accessible
- No login walls (or credentials provided)

## Limitations

- **Crawl Limit:** 10,000 pages default (adjust with --crawl-limit)
- **JavaScript Sites:** May require rendering service
- **Time Required:** 6-10 hours for comprehensive audit
- **Large Sites:** >50k pages may need segmented audits

---

**Pro Tip**: Fix crawl waste first (noindex low-value pages, fix 404s) to free up crawl budget for search engines to discover your important content faster. Architecture improvements take 3-6 months to show full impact in rankings.
