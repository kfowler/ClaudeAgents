# ClaudeAgents Telemetry Guide

**Version:** 1.0
**Last Updated:** 2025-10-07

---

## Overview

ClaudeAgents includes an **optional, privacy-first telemetry system** to help improve agent quality through usage data. This guide explains what's collected, how to enable/disable it, and how to view your data.

### Key Principles

✅ **Privacy-First**
- No personally identifiable information (PII)
- No code snippets or project details
- Aggregate metrics only

✅ **Opt-In**
- Disabled by default
- You must explicitly enable telemetry
- Can be disabled at any time

✅ **Transparent**
- Clear documentation of what's collected
- Plain JSON files you can inspect
- No external servers - all data stays local

✅ **Local-First**
- Data stored in `~/.claude-telemetry/`
- Plain JSON files, no databases
- You have full control

---

## What We Collect

### Events Tracked

1. **Agent Invocations**
   - Which agent was used
   - When it was invoked
   - Success/failure outcome
   - Duration (time to complete)

2. **Command Usage**
   - Which commands are used
   - Frequency of invocation

3. **User Satisfaction**
   - Post-task Y/N feedback
   - Optional per-agent satisfaction

### What We DON'T Collect

❌ Code snippets or file contents
❌ Project names or directory paths
❌ Personal information
❌ Error messages with sensitive data
❌ IP addresses or network data

### Data Example

Here's what a typical telemetry event looks like:

```json
{
  "timestamp": 1696675200.0,
  "event_type": "agent_completed",
  "agent_name": "full-stack-architect",
  "outcome": "success",
  "duration_seconds": 45.3
}
```

---

## How to Enable Telemetry

### Option 1: Command Line

```bash
python3 tools/telemetry.py enable
```

Output:
```
✅ Telemetry enabled. Data stored in: /Users/you/.claude-telemetry
```

### Option 2: Manual Configuration

Edit `~/.claude-telemetry/config.json`:

```json
{
  "enabled": true,
  "version": "1.0",
  "created_at": "2025-10-07T10:00:00"
}
```

---

## How to Disable Telemetry

### Command Line

```bash
python3 tools/telemetry.py disable
```

### Delete All Data

```bash
rm -rf ~/.claude-telemetry
```

This permanently deletes all telemetry data.

---

## Viewing Your Data

### Check Telemetry Status

```bash
python3 tools/telemetry.py status
```

Output:
```
Telemetry: ✅ Enabled
Data directory: /Users/you/.claude-telemetry
```

### View Summary Statistics

```bash
python3 tools/telemetry.py summary
```

Example output:
```
============================================================
CLAUDEAGENTS TELEMETRY SUMMARY
============================================================

📊 Overview:
  • Total events: 234
  • Period: 2025-10-01T09:00:00 to 2025-10-07T16:30:00

🤖 Top 10 Most-Used Agents:
  1. full-stack-architect
     Invocations: 45, Success: 93.3%, Avg Duration: 67.2s
  2. security-audit-specialist
     Invocations: 23, Success: 100.0%, Avg Duration: 120.5s
  3. devops-engineer
     Invocations: 18, Success: 88.9%, Avg Duration: 55.1s

📋 Commands Used:
  • /code-review: 12 times
  • /security-audit: 8 times
  • /deploy-prep: 5 times

😊 User Satisfaction:
  • Feedback received: 34
  • Satisfied: 31
  • Satisfaction rate: 91.2%
```

### Inspect Raw Data

All events stored in `~/.claude-telemetry/events/`:

```bash
# View today's events
cat ~/.claude-telemetry/events/2025-10-07.jsonl

# Count total events
wc -l ~/.claude-telemetry/events/*.jsonl

# View summary
cat ~/.claude-telemetry/summary.json
```

---

## Data Storage Structure

```
~/.claude-telemetry/
├── events/
│   ├── 2025-10-01.jsonl  # Daily event logs (JSONL format)
│   ├── 2025-10-02.jsonl
│   └── 2025-10-07.jsonl
├── config.json            # Your telemetry preferences
└── summary.json           # Aggregated statistics
```

### Event File Format

Events are stored as **JSON Lines (JSONL)** - one JSON object per line:

```jsonl
{"timestamp": 1696675200.0, "event_type": "agent_invoked", "agent_name": "full-stack-architect"}
{"timestamp": 1696675245.3, "event_type": "agent_completed", "agent_name": "full-stack-architect", "outcome": "success", "duration_seconds": 45.3}
{"timestamp": 1696675300.0, "event_type": "user_feedback", "user_satisfied": true, "agent_name": "full-stack-architect"}
```

---

## Using Telemetry Data

### For Individual Users

1. **Identify Your Most-Used Agents**
   - See which agents you rely on most
   - Understand your workflow patterns

2. **Track Success Rates**
   - Which agents work well for you?
   - Which ones need improvement?

3. **Improve Your Efficiency**
   - See average durations
   - Optimize your agent selection

### For Contributors

1. **Data-Driven Agent Improvements**
   - See which agents get used most
   - Identify agents with low success rates
   - Prioritize improvements based on usage

2. **Validate New Agents**
   - Does the new agent get used?
   - Is it successful?
   - Should it be promoted to Core tier?

---

## Privacy & Security

### Data Retention

- Events are stored indefinitely (unless you delete them)
- You can manually delete old event files:

```bash
# Delete events older than 30 days
find ~/.claude-telemetry/events/ -name "*.jsonl" -mtime +30 -delete
```

### Sharing Data (Optional)

If you want to contribute anonymized data to improve ClaudeAgents:

1. Run summary generation:
   ```bash
   python3 tools/telemetry.py summary > my-summary.txt
   ```

2. Review `my-summary.txt` for any sensitive information

3. Share the summary (not raw events) via GitHub issue or discussion

**Note:** We never automatically upload data. Sharing is 100% manual and optional.

---

## Integration with Agents

### For Agent Developers

To add telemetry to a custom agent or command:

```python
from tools.telemetry import TelemetryCollector, Outcome

# Initialize collector
collector = TelemetryCollector()

# Record agent invocation
collector.agent_invoked("my-custom-agent")

# Start timer
import time
start_time = time.time()

try:
    # ... agent logic ...

    # Record success
    duration = time.time() - start_time
    collector.agent_completed(
        "my-custom-agent",
        Outcome.SUCCESS,
        duration
    )
except Exception as e:
    # Record failure
    duration = time.time() - start_time
    collector.agent_completed(
        "my-custom-agent",
        Outcome.FAILURE,
        duration,
        error_category=type(e).__name__
    )
```

### For Command Developers

```python
# Record command usage
collector.command_invoked("/my-command")
```

### User Feedback Collection

After task completion, prompt for feedback:

```python
# Simple Y/N prompt
satisfied = input("Was this helpful? (y/n): ").lower() == 'y'
collector.user_feedback(satisfied, agent_name="full-stack-architect")
```

---

## Roadmap

Future enhancements planned:

- **Web Dashboard** (Phase 2): Visual analytics for your telemetry data
- **Agent Recommendations** (Phase 2): AI-powered agent suggestions based on your patterns
- **Comparative Analytics** (Phase 3): Compare your usage vs community averages (opt-in)
- **Export Formats** (Phase 3): CSV, Excel, Grafana integration

---

## FAQ

### Q: Is telemetry required to use ClaudeAgents?

**A:** No. Telemetry is completely optional and disabled by default.

### Q: Can I see what data is being collected?

**A:** Yes! All data is stored in plain JSON files at `~/.claude-telemetry/`. Inspect them anytime.

### Q: Does telemetry slow down agents?

**A:** No. Event recording is asynchronous and adds <1ms overhead per event.

### Q: Can I export my data?

**A:** Yes. Copy the `~/.claude-telemetry/` directory or use `summary.json` for aggregated stats.

### Q: What if I accidentally enabled telemetry?

**A:** Run `python3 tools/telemetry.py disable` or delete `~/.claude-telemetry/`.

### Q: Will this data be uploaded anywhere?

**A:** No. All data stays on your local machine. We never automatically upload anything.

### Q: Can I contribute my data to help improve ClaudeAgents?

**A:** Yes! Share your `summary.json` (not raw events) via GitHub. Review it first to ensure no sensitive info.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/anthropics/claude-code/issues)
- **Discussions:** [GitHub Discussions](https://github.com/anthropics/claude-code/discussions)
- **Documentation:** [docs/](.)

---

**Maintained By:** ClaudeAgents Core Team
**License:** MIT
**Last Updated:** 2025-10-07
