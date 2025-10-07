# Comprehensive SEO Audit

**Command:** `/comprehensive-seo-audit`
**Agents:** `seo-technical-auditor`, `seo-meta-optimizer`, `seo-performance-specialist`
**Complexity:** High
**Duration:** 45-90 minutes (depending on site size)

## Overview

Performs a complete technical SEO audit coordinating three specialized agents to identify and prioritize all SEO issues blocking search visibility, rankings, and organic traffic.

## What This Command Does

This command orchestrates a comprehensive SEO audit across three critical dimensions:

1. **Technical SEO Infrastructure** (`seo-technical-auditor`)
   - Crawlability and indexability analysis
   - XML sitemap validation
   - Structured data implementation
   - Mobile-friendliness and HTTPS
   - Canonical tags and hreflang
   - Duplicate content detection
   - JavaScript rendering issues

2. **Metadata Optimization** (`seo-meta-optimizer`)
   - Meta title and description analysis
   - Open Graph and Twitter Card implementation
   - Structured data (JSON-LD) validation
   - Canonical URL strategy
   - Character count optimization
   - CTR improvement opportunities

3. **Performance for Rankings** (`seo-performance-specialist`)
   - Core Web Vitals assessment (LCP, INP, CLS)
   - Mobile-first performance analysis
   - TTFB and server response optimization
   - Image optimization opportunities
   - Third-party script impact
   - Field data vs lab data comparison

## Usage

```bash
# Basic audit
/comprehensive-seo-audit

# With specific URL or sitemap
/comprehensive-seo-audit https://example.com

# Focus on specific issues
/comprehensive-seo-audit --focus=mobile,performance
```

## Execution Workflow

### Phase 1: Discovery & Data Collection (5-10 min)

**seo-technical-auditor** performs initial crawl:
- Crawl up to 10,000 URLs (or sitemap limit)
- Analyze robots.txt and meta robots directives
- Extract all metadata, structured data, canonicals
- Identify indexability issues
- Check Search Console integration

**seo-meta-optimizer** analyzes metadata:
- Extract all meta titles and descriptions
- Validate character counts
- Analyze keyword placement
- Review structured data implementation
- Check social media tags

**seo-performance-specialist** gathers performance data:
- Fetch Core Web Vitals from Search Console
- Run PageSpeed Insights for key pages
- Analyze CrUX field data
- Identify render-blocking resources
- Check mobile vs desktop performance gaps

### Phase 2: Issue Identification (10-15 min)

Each agent identifies domain-specific issues with severity ratings:

**Critical Issues** (block indexing or rankings):
- Pages blocked by robots.txt
- Noindex tags on important pages
- Broken canonical chains
- Missing or invalid hreflang
- Core Web Vitals failing (>75th percentile poor)
- Mobile usability errors
- HTTPS/SSL issues

**High Priority Issues** (significant ranking impact):
- Missing or poor meta descriptions
- Duplicate title tags
- Structured data errors
- Missing XML sitemap
- Slow TTFB (>600ms)
- Poor LCP (>2.5s on mobile)
- Orphaned pages with no internal links

**Medium Priority Issues** (optimization opportunities):
- Suboptimal meta title lengths
- Missing Open Graph tags
- Thin internal linking
- Image optimization opportunities
- Third-party script overhead
- Moderate CLS issues

**Low Priority Issues** (minor improvements):
- Minor structured data warnings
- Character count tweaks
- Cache optimization
- Minor mobile usability warnings

### Phase 3: Prioritization & Roadmap (5-10 min)

**project-orchestrator** synthesizes findings:
- Cross-reference issues across agents
- Calculate total potential impact
- Create prioritized fix list
- Estimate implementation effort
- Identify quick wins vs long-term projects

### Phase 4: Deliverable Generation (5-10 min)

Generate comprehensive SEO audit report:

```markdown
# SEO Audit Report - [Site Name]
**Date:** [Date]
**Audited URLs:** [Count]
**Critical Issues:** [Count]
**Overall SEO Health Score:** [Score/100]

## Executive Summary
- **Top 3 Critical Issues:** [List]
- **Estimated Traffic Impact:** [Percentage]
- **Quick Wins (< 1 week):** [List]
- **Long-term Projects (1-3 months):** [List]

## Technical SEO Findings
[seo-technical-auditor detailed report]
- Crawlability: [Score/100] - [Issues count]
- Indexability: [Score/100] - [Issues count]
- Mobile-Friendliness: [Score/100] - [Issues count]
- HTTPS: [Score/100] - [Issues count]
- [Additional categories...]

## Metadata Optimization
[seo-meta-optimizer detailed report]
- Meta Titles: [Score/100] - [Issues count]
- Meta Descriptions: [Score/100] - [Issues count]
- Structured Data: [Score/100] - [Issues count]
- Social Tags: [Score/100] - [Issues count]
- [Additional categories...]

## Performance for SEO
[seo-performance-specialist detailed report]
- Core Web Vitals: [Pass/Fail] - [URLs passing %]
- LCP: [Median] - [Good/Needs Improvement/Poor breakdown]
- INP: [Median] - [Good/Needs Improvement/Poor breakdown]
- CLS: [Median] - [Good/Needs Improvement/Poor breakdown]
- TTFB: [Median] - [Assessment]
- [Additional categories...]

## Prioritized Action Plan

### Immediate (Week 1)
1. [Critical Issue 1] - Estimated impact: [X% traffic]
   - Implementation: [Brief description]
   - Effort: [Hours/days]
   - Owner: [Agent]

2. [Critical Issue 2] - Estimated impact: [X% traffic]
   [...]

### Short-term (Weeks 2-4)
[High priority issues...]

### Medium-term (Months 2-3)
[Medium priority issues...]

### Long-term Optimization (Month 3+)
[Low priority and ongoing optimization...]

## Estimated Impact
- **Total potential traffic increase:** [X-Y%]
- **Ranking improvement:** [Positions]
- **Core Web Vitals:** [Current %] → [Target %] passing
- **Indexability:** [Current URLs] → [Target URLs] indexed

## Implementation Resources
- Required agents: [List with links]
- Estimated total effort: [Hours/weeks]
- External tools needed: [List]
- Budget considerations: [CDN, tools, etc.]
```

## Success Metrics

Track audit effectiveness through:
- **Audit Coverage**: % of site URLs analyzed
- **Issue Detection**: Number and severity of issues found
- **Fix Implementation**: % of recommendations implemented
- **Traffic Impact**: Organic traffic increase post-fixes
- **Ranking Improvement**: Keyword position changes
- **Core Web Vitals**: % URLs achieving "Good" ratings
- **Indexability**: Coverage increase in Search Console

## Common Use Cases

### New Site Launch
Run comprehensive audit before launch to catch all technical issues:
```bash
/comprehensive-seo-audit --pre-launch https://staging.example.com
```

### Traffic Drop Investigation
Identify issues causing organic traffic decline:
```bash
/comprehensive-seo-audit --compare-baseline 2024-09-01
```

### Competitive Analysis Integration
Combine with competitive analysis to benchmark:
```bash
/comprehensive-seo-audit --benchmark https://competitor.com
```

### Regular Quarterly Audits
Ongoing SEO health monitoring:
```bash
/comprehensive-seo-audit --quarterly-report Q3-2024
```

## Integration with Other Commands

This command works well with:
- `/security-audit` - Identify security issues affecting SEO (HTTPS, headers)
- `/performance-audit` - Deep dive into Core Web Vitals technical implementation
- `/accessibility-audit` - Accessibility issues often overlap with SEO (headings, alt text)
- `/code-review` - Review SEO implementation in codebase

## Prerequisites

### Required Access
- Google Search Console property verification
- Analytics access (for traffic correlation)
- Hosting/server access (for technical fixes)
- CMS/codebase access (for metadata updates)

### Recommended Tools
- Google Search Console
- PageSpeed Insights API access
- Screaming Frog SEO Spider (for large sites >10k URLs)
- Access to sitemap.xml and robots.txt

### Environment Setup
```bash
# Set Search Console property ID
export SEARCH_CONSOLE_PROPERTY="https://example.com"

# Optional: Configure crawl limits
export SEO_CRAWL_LIMIT=10000
export SEO_CRAWL_DEPTH=5
```

## Limitations

- **Site Size**: Full crawls limited to 10,000 URLs (use Screaming Frog for larger sites)
- **Historical Data**: Requires 28 days of CrUX data for accurate Core Web Vitals
- **Search Console**: Requires verified property access
- **JavaScript Sites**: May require rendering service for full JavaScript audit
- **International Sites**: Hreflang validation requires all language versions accessible

## Advanced Options

### Focus Areas
```bash
# Technical SEO only
/comprehensive-seo-audit --technical-only

# Performance focus
/comprehensive-seo-audit --focus=performance,mobile

# Metadata optimization
/comprehensive-seo-audit --metadata-only
```

### Output Formats
```bash
# JSON output for automation
/comprehensive-seo-audit --format=json

# CSV for spreadsheet import
/comprehensive-seo-audit --format=csv --output=seo-issues.csv

# Interactive HTML report
/comprehensive-seo-audit --format=html --output=report.html
```

### Comparison & Trending
```bash
# Compare against previous audit
/comprehensive-seo-audit --compare=audit-2024-09-01.json

# Track metrics over time
/comprehensive-seo-audit --track-trends --baseline=2024-01-01
```

## Troubleshooting

### "Crawl incomplete" error
- Check robots.txt isn't blocking crawler
- Verify site is accessible from audit environment
- Increase timeout limits for slow sites

### "No Search Console data" warning
- Verify Search Console property ownership
- Wait 28 days after site launch for CrUX data
- Check API permissions and quotas

### "Structured data validation failed"
- Ensure JSON-LD is valid JSON
- Check schema.org types are correctly specified
- Validate URLs are absolute, not relative

## Example Output

```
🔍 Comprehensive SEO Audit Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Discovery & Data Collection
✓ Crawled 8,342 URLs
✓ Analyzed 8,342 meta titles
✓ Fetched Core Web Vitals for 847 URLs with traffic

Phase 2: Issue Identification
🔴 Critical Issues: 12
🟠 High Priority Issues: 34
🟡 Medium Priority Issues: 127
🟢 Low Priority Issues: 56

Phase 3: Prioritization
📊 Total Potential Impact: 25-35% traffic increase
⚡ Quick Wins (<1 week): 8 issues, 12-15% impact
🎯 Strategic Fixes (1-3 months): 18 issues, 15-20% impact

Phase 4: Report Generation
📝 Generated comprehensive audit report: seo-audit-2024-10-06.md
📊 Exported issue tracker: seo-issues.csv
📈 Created action plan: seo-roadmap.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ SEO Audit Complete

Next Steps:
1. Review audit report: seo-audit-2024-10-06.md
2. Prioritize quick wins in action plan
3. Schedule implementation with development team
4. Re-audit in 30 days to measure impact
```

## Best Practices

1. **Run Regularly**: Quarterly audits catch issues early
2. **Track Changes**: Compare audit results over time to measure improvement
3. **Prioritize by Impact**: Focus on high-traffic pages first
4. **Validate Fixes**: Re-run focused audits after implementing fixes
5. **Document Decisions**: Record why certain issues weren't fixed (trade-offs)
6. **Cross-Functional**: Share reports with development, marketing, and product teams
7. **Benchmark Competitors**: Compare audit metrics with top-ranking competitors
8. **Mobile-First**: Always prioritize mobile issues given mobile-first indexing

## Related Commands

- `/seo-keyword-research` - Keyword strategy (Phase 2 agents)
- `/seo-content-optimization` - Content quality (Phase 2 agents)
- `/seo-backlink-audit` - Off-page SEO (future)
- `/local-seo-audit` - Local search optimization (future)

---

**Pro Tip**: Schedule this audit to run automatically monthly via CI/CD to catch SEO regressions before they impact traffic. Export results to dashboard for executive visibility.
