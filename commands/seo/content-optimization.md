# SEO Content Optimization

**Command:** `/seo-content-optimization`
**Agents:** `seo-keyword-strategist`, `seo-content-optimizer`, `seo-meta-optimizer`
**Complexity:** Medium
**Duration:** 2-4 hours per page

## Overview

Performs comprehensive content optimization for individual pages or articles, coordinating keyword strategy, on-page optimization, and metadata implementation to maximize search rankings and user engagement.

## What This Command Does

This command orchestrates a complete content optimization workflow across three specialized agents:

1. **Keyword Strategy** (`seo-keyword-strategist`)
   - Target keyword validation and intent analysis
   - Related keyword opportunities
   - Competitive content analysis
   - Keyword-to-content mapping

2. **Content Optimization** (`seo-content-optimizer`)
   - On-page keyword implementation
   - Content structure and heading hierarchy
   - Readability optimization (Flesch-Kincaid 60-70)
   - E-E-A-T enhancement (Experience, Expertise, Authoritativeness, Trustworthiness)
   - Internal linking strategy
   - Image optimization (alt text, file names)
   - Featured snippet optimization

3. **Metadata Implementation** (`seo-meta-optimizer`)
   - Meta title optimization (50-60 chars)
   - Meta description optimization (150-160 chars)
   - Open Graph tags for social sharing
   - Structured data (JSON-LD)
   - Canonical URL optimization

## Usage

```bash
# Optimize existing content
/seo-content-optimization https://example.com/article

# Optimize with specific target keyword
/seo-content-optimization https://example.com/product --keyword="project management software"

# Optimize new content from brief
/seo-content-optimization --brief=content-brief.md --keyword="best crm tools"

# Batch optimize multiple pages
/seo-content-optimization --urls=urls.txt
```

## Execution Workflow

### Phase 1: Keyword Strategy & Analysis (30-45 min)

**seo-keyword-strategist** performs keyword research:
- Validate target keyword (search volume, difficulty, intent)
- Analyze top 10 SERP results for target keyword
- Identify related keywords and LSI terms
- Determine optimal content length based on competition
- Map keyword clusters to content sections
- Identify featured snippet opportunities

**Deliverables:**
- Primary keyword: "project management software" (5,400 volume, 67 difficulty, Commercial)
- Secondary keywords: "project management tools", "project tracking software" (15 total)
- LSI keywords: "task management", "team collaboration", "workflow automation"
- Recommended length: 2,500-3,000 words (based on top 10 avg: 2,847 words)
- SERP features: Featured snippet (definition), People Also Ask (4 questions)

### Phase 2: Content Optimization (60-90 min)

**seo-content-optimizer** optimizes the content:

**Content Structure:**
- H1 optimization: Include primary keyword naturally
- H2-H6 hierarchy: Semantic heading structure with keyword variations
- Introduction: Hook + keyword in first 100 words
- Body: Comprehensive topic coverage with keyword density 0.5-2.5%
- Conclusion: Summary + CTA

**Readability:**
- Flesch Reading Ease: Target 60-70 (Grade Level 8-10)
- Sentence length: 15-20 words average
- Paragraph length: 3-5 sentences
- Transition words: 30%+ of sentences
- Active voice: 80%+ of sentences

**E-E-A-T Optimization:**
- Author credentials: Add author bio with expertise signals
- Citations: 3-5 authoritative sources (industry reports, studies)
- Original research: Include unique data, case studies, or examples
- Expert quotes: 1-2 industry expert quotes
- Updated date: Include last updated timestamp

**Image Optimization:**
- Descriptive alt text: "Screenshot of [Product Name] project board with task cards"
- File names: "project-management-software-dashboard.jpg"
- Captions: Descriptive captions with keywords
- Compress: All images <100KB, WebP format

**Internal Linking:**
- 2-5 contextual internal links per 1,000 words
- Link to related pillar content, product pages, resources
- Descriptive anchor text (not "click here")
- Mix of topical relevance and PageRank distribution

**Featured Snippet Optimization:**
- Definition snippet: Clear 40-60 word definition in first paragraph
- List snippet: Bullet/numbered lists for "top", "best", "how to" queries
- Table snippet: Comparison tables for "vs" and comparison queries

**Deliverables:**
- Optimized content: 2,847 words (target: 2,500-3,000 ✓)
- Readability score: Flesch 68 (target: 60-70 ✓)
- Keyword density: 1.8% (target: 0.5-2.5% ✓)
- Heading structure: H1(1) → H2(6) → H3(14) ✓
- E-E-A-T signals: Author bio, 4 citations, 2 expert quotes ✓
- Images: 8 optimized images, all <100KB, descriptive alt text ✓
- Internal links: 6 contextual links ✓
- Featured snippet format: Definition + comparison table ✓

### Phase 3: Metadata Implementation (15-30 min)

**seo-meta-optimizer** implements optimized metadata:

**Meta Title:**
- Length: 50-60 characters
- Primary keyword placement: Beginning or near beginning
- Brand name: End of title (if space allows)
- CTR optimization: Numbers, power words, emotional triggers
- Example: "10 Best Project Management Software Tools (2024 Guide)"

**Meta Description:**
- Length: 150-160 characters
- Include primary and 1-2 secondary keywords
- Compelling value proposition
- Clear call-to-action
- Example: "Compare the top 10 project management software tools for teams. Features, pricing, pros & cons. Find the perfect tool to streamline your workflow in 2024."

**Open Graph Tags:**
- og:title: Optimized for social sharing (may differ from meta title)
- og:description: Compelling social description
- og:image: High-quality featured image (1200x630px)
- og:type: article
- article:published_time, article:modified_time, article:author

**Structured Data (JSON-LD):**
- Article schema: headline, description, image, author, publisher, datePublished, dateModified
- BreadcrumbList: Site hierarchy for breadcrumb navigation
- FAQPage (if applicable): Q&A pairs for PAA optimization
- HowTo (if applicable): Step-by-step instructions

**Canonical URL:**
- Self-referencing canonical: https://example.com/article
- Ensure consistency across all pages

**Deliverables:**
- Meta title: 57 chars (target: 50-60 ✓), includes primary keyword ✓
- Meta description: 156 chars (target: 150-160 ✓), includes 3 keywords ✓
- Open Graph: Complete og:title, og:description, og:image ✓
- Structured data: Article + BreadcrumbList schemas ✓
- Canonical: Self-referencing canonical URL ✓

### Phase 4: Quality Assurance & Reporting (15-30 min)

**Final checklist validation:**
- ✓ Target keyword: "project management software" (validated, 5,400 volume)
- ✓ Content length: 2,847 words (competitive with top 10)
- ✓ Readability: Flesch 68 (Grade Level 9)
- ✓ Keyword density: 1.8% (natural, not stuffed)
- ✓ Heading structure: Valid H1→H2→H3 hierarchy
- ✓ E-E-A-T signals: Author credentials, 4 citations, expertise demonstrated
- ✓ Image optimization: 8 images, all optimized, descriptive alt text
- ✓ Internal linking: 6 contextual links to related content
- ✓ Featured snippet: Definition + comparison table formats
- ✓ Meta title: 57 chars, keyword-optimized, CTR-focused
- ✓ Meta description: 156 chars, compelling, action-oriented
- ✓ Structured data: Article + BreadcrumbList implemented
- ✓ Canonical URL: Self-referencing canonical set

**Generate optimization report:**

```markdown
# Content Optimization Report
**URL:** https://example.com/project-management-software
**Target Keyword:** project management software
**Date:** 2024-10-08

## Summary
- **Content Length:** 2,847 words (↑ from 1,200 words)
- **Readability:** Flesch 68 (↑ from 52)
- **Keyword Optimization:** 1.8% density (↑ from 0.3%)
- **Estimated Impact:** 25-40% organic traffic increase within 3-6 months

## Optimizations Applied

### Content
- ✓ Expanded from 1,200 → 2,847 words (comprehensive coverage)
- ✓ Improved heading structure: H1(1) → H2(6) → H3(14)
- ✓ Enhanced readability: Flesch 52 → 68
- ✓ Added E-E-A-T signals: author bio, 4 citations, 2 expert quotes
- ✓ Optimized 8 images with descriptive alt text
- ✓ Added 6 contextual internal links
- ✓ Formatted for featured snippet (definition + table)

### Metadata
- ✓ Meta title: Generic → "10 Best Project Management Software Tools (2024 Guide)"
- ✓ Meta description: Missing → Compelling 156-char description with keywords
- ✓ Added Open Graph tags for social sharing
- ✓ Implemented Article + BreadcrumbList structured data
- ✓ Set canonical URL

## Competitive Comparison
| Metric | Before | After | Top 10 Avg |
|--------|--------|-------|-----------|
| Word Count | 1,200 | 2,847 | 2,650 |
| Readability | 52 | 68 | 65 |
| Keyword Density | 0.3% | 1.8% | 1.5% |
| Internal Links | 1 | 6 | 5 |
| Images | 2 | 8 | 7 |
| E-E-A-T Signals | 0 | 7 | 5 |

## Next Steps
1. Publish optimized content
2. Submit to Search Console for re-crawl
3. Monitor rankings for target keyword (weekly for first month)
4. Track organic traffic (30-day baseline)
5. A/B test meta description variations (if CTR <5%)
6. Update content quarterly to maintain freshness

## Expected Outcomes
- **Ranking Improvement:** Position 15 → Position 5-8 (3-6 months)
- **Organic Traffic:** +25-40% increase within 6 months
- **CTR:** 3.2% → 5.5% (improved meta title/description)
- **Time on Page:** 1:15 → 2:30 (better content quality)
- **Bounce Rate:** 68% → 55% (improved engagement)
- **Featured Snippet:** 15-25% probability (optimized formats)
```

## Success Metrics

Track content performance through:
- **Rankings**: Target keyword position (track weekly)
- **Organic Traffic**: Visitors from search (30-day comparison)
- **CTR**: Click-through rate from SERPs (Search Console)
- **Engagement**: Time on page, bounce rate, scroll depth
- **Conversions**: Goal completions from organic traffic
- **Featured Snippets**: Snippet wins for target queries

## Common Use Cases

### New Content Creation
Optimize content before publication for maximum impact:
```bash
/seo-content-optimization --brief=content-brief.md --keyword="customer retention strategies"
```

### Existing Content Refresh
Update and optimize underperforming content:
```bash
/seo-content-optimization https://example.com/old-article --keyword="email marketing best practices"
```

### Competitive Content
Create content to outrank competitors:
```bash
/seo-content-optimization --competitor=https://competitor.com/article --keyword="sales funnel optimization"
```

### Product/Service Pages
Optimize commercial pages for transactional keywords:
```bash
/seo-content-optimization https://example.com/product --keyword="buy project management software"
```

## Integration with Other Commands

This command works well with:
- `/comprehensive-seo-audit` - Identify content optimization opportunities site-wide
- `/seo-technical-audit` - Ensure optimized content is crawlable/indexable
- `/performance-audit` - Optimize page speed for SEO and UX
- `/accessibility-audit` - Ensure content is accessible (overlaps with SEO)

## Prerequisites

### Required Access
- Content management system (CMS) access for content updates
- Google Search Console (for keyword/performance data)
- Analytics access (for traffic/engagement baselines)

### Recommended Tools
- Keyword research tool (Ahrefs, SEMrush, Moz)
- Readability analyzer (Hemingway, Yoast, Grammarly)
- SEO content tool (Clearscope, MarketMuse, Surfer SEO)
- SERP analysis tool

### Content Requirements
- Existing content URL OR content brief with target keyword
- Target keyword (or keyword research will be performed)
- Access to competitor content for analysis

## Limitations

- **Time per Page**: 2-4 hours per page (comprehensive optimization)
- **Keyword Research**: Requires access to keyword research tools
- **Content Length**: Optimal for 500-5,000 word content (not landing pages)
- **Language**: English-optimized (other languages may need adjustments)
- **Content Type**: Best for blog posts, articles, guides, product pages

## Advanced Options

### Content Type Optimization
```bash
# Blog post
/seo-content-optimization --type=blog-post --keyword="react hooks tutorial"

# Product page
/seo-content-optimization --type=product --keyword="best crm for small business"

# Comparison/review
/seo-content-optimization --type=comparison --keyword="asana vs monday"

# How-to guide
/seo-content-optimization --type=how-to --keyword="how to build a sales funnel"
```

### Optimization Level
```bash
# Light optimization (metadata + basic on-page)
/seo-content-optimization --level=light --url=https://example.com/article

# Standard optimization (full workflow, default)
/seo-content-optimization --level=standard --url=https://example.com/article

# Deep optimization (extensive research, comprehensive rewrite)
/seo-content-optimization --level=deep --url=https://example.com/article
```

### Output Formats
```bash
# Markdown report (default)
/seo-content-optimization --url=https://example.com/article --output=report.md

# JSON for automation
/seo-content-optimization --url=https://example.com/article --format=json

# HTML preview
/seo-content-optimization --url=https://example.com/article --format=html --output=preview.html
```

## Troubleshooting

### "Keyword too competitive" warning
- Choose long-tail variation with lower difficulty
- Focus on subtopics with less competition
- Build topical authority with cluster content first

### "Content length insufficient" error
- Expand content to match or exceed top 10 average
- Add comprehensive sections covering all search intent aspects
- Include examples, case studies, expert quotes for depth

### "Readability score too low" warning
- Simplify complex sentences (aim for 15-20 words avg)
- Use transition words (30%+ of sentences)
- Break long paragraphs into 3-5 sentence blocks
- Use bullet points and numbered lists for scannability

## Example Output

```
🔍 SEO Content Optimization Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Keyword Strategy & Analysis
✓ Target keyword validated: "project management software" (5,400 volume, 67 difficulty)
✓ Analyzed top 10 SERP results (avg length: 2,650 words)
✓ Identified 15 secondary keywords
✓ Featured snippet opportunity: Definition + comparison table

Phase 2: Content Optimization
✓ Optimized content: 2,847 words (↑ from 1,200)
✓ Readability: Flesch 68 (↑ from 52)
✓ Keyword density: 1.8% (natural implementation)
✓ E-E-A-T signals: Author bio, 4 citations, 2 expert quotes
✓ Optimized 8 images with descriptive alt text
✓ Added 6 contextual internal links
✓ Featured snippet format: Definition + comparison table

Phase 3: Metadata Implementation
✓ Meta title: 57 chars, keyword-optimized
✓ Meta description: 156 chars, compelling CTA
✓ Open Graph tags: Complete social sharing optimization
✓ Structured data: Article + BreadcrumbList schemas
✓ Canonical URL: Self-referencing canonical set

Phase 4: Quality Assurance
✓ All quality checks passed (15/15)
✓ Generated optimization report: seo-content-optimization-report.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Content Optimization Complete

Estimated Impact: 25-40% organic traffic increase within 3-6 months

Next Steps:
1. Publish optimized content
2. Submit to Search Console for re-crawl
3. Monitor rankings weekly
4. Track organic traffic (30-day baseline)
```

## Best Practices

1. **Target One Primary Keyword**: Don't dilute focus with multiple unrelated keywords
2. **Match Search Intent**: Informational, navigational, transactional, or commercial intent
3. **Exceed Competition**: Content length, depth, and quality should match or exceed top 10
4. **Natural Keyword Use**: 0.5-2.5% density, natural placement, avoid keyword stuffing
5. **E-E-A-T is Critical**: Demonstrate expertise, authoritativeness, trustworthiness
6. **Optimize for Snippets**: Format content for featured snippets (definition, list, table)
7. **Internal Linking**: 2-5 contextual links per 1,000 words to related content
8. **Keep Content Fresh**: Update quarterly with new data, examples, insights
9. **Mobile-First**: Ensure content is readable and engaging on mobile devices
10. **Monitor & Iterate**: Track rankings weekly, refine based on performance data

## Related Commands

- `/comprehensive-seo-audit` - Full site SEO audit (identify optimization opportunities)
- `/seo-keyword-research` - Keyword research and strategy (Phase 2 command)
- `/seo-technical-audit` - Technical SEO infrastructure (ensure content is indexable)
- `/seo-site-architecture` - Site architecture and internal linking (Phase 2 command)
- `/performance-audit` - Page speed optimization (fast pages rank better)

---

**Pro Tip**: For maximum impact, optimize pillar content first (high-traffic, high-authority pages), then cascade improvements to cluster content. This establishes topical authority and distributes link equity effectively.
