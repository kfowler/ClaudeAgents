# Cognitive Code Archaeology - Analytics Integration

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Privacy:** Local-only, opt-in

---

## Overview

CCA Analytics provides comprehensive tracking and insights into how Cognitive Code Archaeology is used, helping users understand the value delivered and platform maintainers optimize the system.

### Key Features

- **Privacy-first design**: All data stays local, never transmitted
- **Opt-in**: Follows global telemetry settings
- **Comprehensive tracking**: Usage patterns, performance, quality, value delivered
- **Actionable insights**: ROI calculations, satisfaction metrics, performance benchmarks
- **Zero overhead**: Minimal performance impact when enabled

---

## What Is Tracked

### Analysis Events

When you analyze a repository, CCA tracks:

- **Analysis start/completion** - Timestamp, duration
- **Commits analyzed** - Total count
- **GitHub enrichment** - Whether GitHub data was included
- **Analysis performance** - Time to analyze, index size

**Privacy guarantee**: No repository names, file paths, or code content stored.

### Query Events

When you execute a query, CCA tracks:

- **Query category** - Architecture, technical debt, onboarding, etc. (no query text!)
- **Response time** - How long the query took
- **Answer quality** - Confidence score, credibility score
- **Citations** - Number of citations provided
- **Estimated time saved** - Conservative estimate vs manual investigation

**Privacy guarantee**: Only query category stored, never the actual question text.

### User Feedback

When you provide feedback, CCA tracks:

- **Satisfaction** - Thumbs up/down
- **Query category** - What type of query you rated (optional)

### Export Events

When you export results, CCA tracks:

- **Export format** - markdown, HTML, JSON
- **Query count** - Number of queries in export

---

## Query Categories

CCA automatically categorizes queries (without storing query text) into:

| Category | Description | Example | Est. Time Saved |
|----------|-------------|---------|-----------------|
| **Architecture Decision** | "Why did we choose X?" | "Why did we choose PostgreSQL?" | 120 min |
| **Technical Debt** | Workarounds, hacks, TODOs | "Why was this workaround implemented?" | 90 min |
| **Feature Evolution** | How features changed over time | "How did authentication evolve?" | 60 min |
| **Code Context** | Understanding specific changes | "What was the context for this change?" | 30 min |
| **Team Knowledge** | Who made decisions | "Who decided to refactor auth?" | 45 min |
| **Bug Investigation** | Why bugs occurred | "Why did this bug occur?" | 90 min |
| **Onboarding** | General understanding | "What is the architecture overview?" | 120 min |
| **Other** | Uncategorized queries | - | 30 min |

**Note**: Time saved estimates are conservative, based on case study data.

---

## Viewing Your Analytics

### Quick Summary

```bash
# View comprehensive analytics
python3 tools/code_archaeology/analytics.py summary
```

**Output includes:**

```
===============================================================
COGNITIVE CODE ARCHAEOLOGY ANALYTICS
===============================================================

📊 Overview:
  • Total events: 47
  • Analyses run: 3
  • Queries executed: 28
  • Exports generated: 2
  • Period: 2025-10-01 to 2025-10-08

🔍 Analysis Performance:
  • Total commits analyzed: 1,245
  • Avg analysis time: 18.3s
  • GitHub enrichment rate: 67.0%

❓ Query Patterns:
  • Architecture Decision: 12 queries
  • Technical Debt: 8 queries
  • Onboarding: 5 queries
  • Feature Evolution: 3 queries
  • Avg response time: 1.8s

⭐ Quality Metrics:
  • Avg confidence: 83.5%
  • Avg credibility: 88.2%
  • Avg quality score: 85.9%
  • Avg citations per answer: 4.2
  • High-confidence queries (>80%): 18
  • Well-cited queries (3+ citations): 22

💰 Value Delivered:
  • Total time saved: 52.5 hours (3,150 minutes)
  • Avg time saved per query: 112.5 minutes
  • Estimated ROI: 18.3x

😊 User Satisfaction:
  • Feedback received: 15
  • Satisfied: 13
  • Satisfaction rate: 86.7%

📤 Exports:
  • Total exports: 2
    • markdown: 2
```

### Check Status

```bash
# Check if analytics is enabled
python3 tools/code_archaeology/analytics.py status
```

---

## Analytics Data Storage

Analytics data is stored locally in `~/.claude-telemetry/cca/`:

```
~/.claude-telemetry/
  └── cca/
      ├── events.jsonl      # All CCA events (append-only)
      └── summary.json      # Latest summary statistics
```

### Event Format

Events are stored as JSON Lines (one event per line):

```json
{"timestamp": 1728404823.5, "event_type": "query_executed", "query_category": "architecture_decision", "query_response_time": 1.8, "answer_confidence": 0.85, "answer_credibility": 0.90, "citation_count": 5, "estimated_time_saved_minutes": 120}
```

### Inspecting Raw Data

```bash
# View all events
cat ~/.claude-telemetry/cca/events.jsonl | jq

# Count queries by category
cat ~/.claude-telemetry/cca/events.jsonl | jq -r 'select(.event_type=="query_executed") | .query_category' | sort | uniq -c

# View latest summary
cat ~/.claude-telemetry/cca/summary.json | jq
```

---

## Privacy & Security

### What We Track

✅ **Anonymous usage metrics**:
- Event types (analysis, query, export)
- Query categories (NOT query text)
- Performance metrics (duration, response time)
- Quality scores (confidence, credibility)
- User satisfaction (thumbs up/down)

### What We DON'T Track

❌ **Never collected**:
- Query text or content
- Repository names or URLs
- File paths or code snippets
- Commit messages or diffs
- Author names or emails
- IP addresses or network data
- Any personally identifiable information

### Privacy Guarantees

1. **Local-only**: All data stored in `~/.claude-telemetry/` on your machine
2. **Opt-in**: Follows global telemetry setting (disabled by default)
3. **Transparent**: Open-source code, inspect `tools/code_archaeology/analytics.py`
4. **Privacy-preserving categorization**: Only patterns detected, never text stored
5. **Easy opt-out**: `python3 tools/telemetry.py disable`

---

## Value Metrics Explained

### Time Saved Calculation

CCA estimates time saved by comparing:

**Traditional approach** (manual investigation):
- Reading commit history: 30-60 min
- Searching codebase: 30-90 min
- Interviewing team members: 60-120 min
- Experimental testing: 60-180 min
- **Total**: 3-8 hours per question

**CCA approach**:
- Analysis (one-time): 10-30 seconds
- Query execution: 1-3 seconds
- **Total**: <1 minute per question

**Time saved** = Traditional time - CCA time (conservative estimates)

### ROI Multiplier

ROI = Total time saved / Total time spent using CCA

Example:
- 28 queries × 112.5 min avg = 3,150 min saved
- Analysis time: 3 × 18.3s = 55s ≈ 1 min
- Query time: 28 × 1.8s = 50s ≈ 1 min
- Total time spent: 2 min
- **ROI = 3,150 / 2 = 1,575x** (actual results vary)

---

## Integration with Global Telemetry

CCA analytics integrates with the global ClaudeAgents telemetry system:

### Enabling Telemetry

```bash
# Enable telemetry (enables both global + CCA analytics)
python3 tools/telemetry.py enable
```

### Viewing All Telemetry

```bash
# View global telemetry summary (includes CCA events)
python3 tools/telemetry.py summary
```

CCA events appear in global telemetry with `cca_` prefix:
- `cca_analysis_started`
- `cca_query_executed`
- `cca_user_feedback`
- `cca_export_generated`

---

## Use Cases

### Personal Productivity Tracking

Track your own productivity gains:

```bash
# After a week of using CCA
python3 tools/code_archaeology/analytics.py summary
```

See how much time you've saved and which query types are most valuable to you.

### Team Performance Analysis

Aggregate metrics across team (requires opt-in from all members):

```bash
# Each team member shares their summary.json
# Combine and analyze trends

# Most common query types
# Avg time saved per developer
# ROI for adopting CCA
```

### Product Improvement

Platform maintainers use analytics to:
- Identify most valuable query categories
- Optimize slow query types
- Improve answer quality for low-confidence queries
- Prioritize features based on usage patterns

---

## API Usage (Programmatic)

### Basic Usage

```python
from tools.code_archaeology.analytics import CCAAnalytics, QueryCategory

# Create analytics instance
analytics = CCAAnalytics()

# Check if enabled
if analytics.is_enabled():
    # Track analysis
    analytics.analysis_started(commits_count=200, github_enriched=True)
    # ... perform analysis ...
    analytics.analysis_completed(commits_count=200, github_enriched=True)

    # Track query
    analytics.query_executed(
        category=QueryCategory.ARCHITECTURE_DECISION,
        response_time_seconds=2.1,
        confidence=0.88,
        credibility=0.92,
        citation_count=5,
        estimated_time_saved_minutes=120
    )

    # Track feedback
    analytics.user_feedback(
        satisfied=True,
        query_category=QueryCategory.ARCHITECTURE_DECISION
    )
```

### Getting Summary Data

```python
# Generate summary
summary = analytics.generate_summary()

# Access metrics
print(f"Total queries: {summary['overview']['total_queries']}")
print(f"Avg confidence: {summary['queries']['avg_confidence']:.1%}")
print(f"Time saved: {summary['value']['total_time_saved_hours']:.1f} hours")
print(f"ROI: {summary['value']['estimated_roi_multiplier']:.1f}x")
```

---

## Troubleshooting

### Analytics Not Recording Events

**Problem**: Events not appearing in `~/.claude-telemetry/cca/events.jsonl`

**Solution**:

1. Check telemetry is enabled:
   ```bash
   python3 tools/telemetry.py status
   ```

2. Enable if disabled:
   ```bash
   python3 tools/telemetry.py enable
   ```

3. Verify config:
   ```bash
   cat ~/.claude-telemetry/config.json
   # Should show "enabled": true
   ```

### Summary Shows Zero Events

**Problem**: `summary.json` shows no data

**Solution**:

1. Check events file exists:
   ```bash
   ls -la ~/.claude-telemetry/cca/events.jsonl
   ```

2. Regenerate summary:
   ```bash
   python3 tools/code_archaeology/analytics.py summary
   ```

### Permission Errors

**Problem**: Cannot write to `~/.claude-telemetry/`

**Solution**:

```bash
# Fix permissions
chmod -R 755 ~/.claude-telemetry/

# Or use different directory
export CCA_ANALYTICS_DIR="/tmp/cca-analytics"
```

---

## Future Enhancements

Planned features for future releases:

- [ ] **Dashboard visualization**: Web-based analytics dashboard
- [ ] **Team aggregation**: Combine metrics across team members
- [ ] **Trend analysis**: Track metrics over time
- [ ] **Query recommendations**: Suggest queries based on patterns
- [ ] **Export to CSV/Excel**: For custom analysis
- [ ] **Integration with JIRA/Linear**: Track time savings in tickets

---

## FAQ

### Q: Does enabling analytics slow down CCA?

**A**: No. Analytics adds <1ms overhead per query. Analysis time is unaffected.

### Q: Can I delete my analytics data?

**A**: Yes. Simply delete `~/.claude-telemetry/cca/`:
```bash
rm -rf ~/.claude-telemetry/cca/
```

### Q: Is my query text stored?

**A**: No. Only query categories are stored (architecture, technical debt, etc.), never the actual query text.

### Q: How accurate are time saved estimates?

**A**: Conservative estimates based on case study data. Actual time saved varies by query complexity and team context.

### Q: Can I export analytics data?

**A**: Yes. Data is stored in JSON format at `~/.claude-telemetry/cca/`. Use `jq` or any JSON tool to analyze.

### Q: Does disabling telemetry delete my data?

**A**: No. Disabling stops new data collection but doesn't delete existing data. Delete manually if desired.

---

## Related Documentation

- [Telemetry Privacy Policy](TELEMETRY_PRIVACY.md)
- [CCA Case Studies](CCA_CASE_STUDIES.md)
- [CCA User Guide](../tools/code_archaeology/README.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

Last updated: 2025-10-08
Version: 1.0.0
Maintainers: ClaudeAgents Platform Team
