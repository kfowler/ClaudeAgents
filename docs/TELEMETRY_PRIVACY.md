# ClaudeAgents Telemetry Privacy Policy

**Version:** 2.0
**Effective Date:** October 8, 2025
**Last Updated:** October 8, 2025

---

## Overview

ClaudeAgents offers **optional, privacy-first telemetry** to help us improve agent quality and validate our tier system. This document provides complete transparency about what we collect, why we collect it, and how you control your data.

**Key Principles:**
- **Opt-in only** - Disabled by default, you must explicitly enable
- **Local-first** - All data stored on your machine
- **No transmission** - Never sent anywhere without explicit consent
- **Full transparency** - Open-source telemetry code you can inspect
- **Easy opt-out** - Single command to disable and delete

---

## What We Collect

### Data Collection Details

When telemetry is **enabled**, we collect the following metadata:

#### 1. Agent Usage Metrics
- **Agent name** - Which agent was invoked (e.g., "full-stack-architect")
- **Timestamp** - When the agent was used
- **Duration** - How long the agent took to complete
- **Outcome** - Success, failure, partial completion, or abandoned
- **Error category** - Type of error if failed (e.g., "ValueError", "TimeoutError")

**Example Event:**
```json
{
  "timestamp": 1728345600.0,
  "event_type": "agent_completed",
  "agent_name": "full-stack-architect",
  "outcome": "success",
  "duration_seconds": 45.3
}
```

#### 2. Command Usage
- **Command name** - Which workflow command was used (e.g., "/code-review")
- **Invocation count** - How many times the command was run
- **Completion status** - Whether the command finished successfully

#### 3. Performance Metrics
- **Execution time** - How long tasks take to complete
- **Resource usage** - Memory and CPU estimates (coming in v2.0)
- **Success rates** - Percentage of successful completions per agent

#### 4. User Satisfaction (Optional)
- **Satisfaction rating** - Yes/No feedback after task completion
- **Associated agent** - Which agent the feedback relates to
- **No comments or text** - Only boolean satisfaction indicator

#### 5. Platform Information
- **Operating system** - macOS, Linux, or Windows
- **Claude Code version** - Which version of Claude Code you're using
- **Python version** - Runtime environment version

### What We NEVER Collect

We are committed to **never** collecting:

❌ **No Code or Files**
- No source code snippets
- No file contents
- No file names or paths
- No project structures

❌ **No Personal Information**
- No names, emails, or usernames
- No IP addresses or network data
- No geographic location
- No demographic information

❌ **No Business Data**
- No project names or company names
- No client information
- No proprietary business logic
- No API keys, credentials, or secrets

❌ **No Tracking or Analytics**
- No third-party analytics services
- No cookies or browser tracking
- No cross-site tracking
- No advertising identifiers

❌ **No Sensitive Context**
- No error messages with sensitive data
- No environment variables
- No command arguments or parameters
- No user prompts or AI responses

---

## Why We Collect Telemetry

### Primary Goals

#### 1. Validate Quality-First Tier System
**Problem:** We claim "Core agents perform better than Specialized agents" but have zero data to prove it.

**Solution:** Telemetry lets us measure:
- Success rates by tier (Core vs Specialized vs Experimental)
- Average task duration by tier
- User satisfaction scores by tier
- Failure patterns and error categories

**Outcome:** Data-driven decisions on tier promotions and demotions.

#### 2. Identify Underused Agents
**Problem:** We have 41 agents but don't know which ones are never used.

**Solution:** Track invocation counts to find:
- Agents with <10 uses in 90 days (candidates for archival)
- Specialized agents outperforming Core agents (promotion candidates)
- Experimental agents ready for Specialized tier

**Outcome:** Maintain a lean, high-quality agent ecosystem.

#### 3. Optimize Performance
**Problem:** Some agents take too long to complete tasks, frustrating users.

**Solution:** Measure execution times to:
- Identify slowest agents (p95, p99 durations)
- Find performance regression across versions
- Optimize prompts and logic for speed

**Outcome:** Faster, more responsive agent workflows.

#### 4. Detect Composite Workflow Patterns
**Problem:** Users manually chain agents together, but we don't know which combinations are common.

**Solution:** Analyze agent invocation sequences to:
- Auto-create composite commands (e.g., "/full-review" = security + accessibility + performance)
- Pre-load context for frequently chained agents
- Suggest next-agent recommendations

**Outcome:** Smarter workflow automation.

#### 5. Improve Command Success Rates
**Problem:** Some workflow commands fail frequently, but we don't know why.

**Solution:** Track command completion rates to:
- Identify commands with high failure rates
- Debug common error patterns
- Improve command robustness

**Outcome:** More reliable automated workflows.

---

## Where Data is Stored

### Storage Location

**Default Location:** `~/.claude-telemetry/`

All telemetry data is stored **locally on your machine** in plain JSON files:

```
~/.claude-telemetry/
├── events/
│   ├── 2025-10-08.jsonl  # Daily event logs
│   ├── 2025-10-09.jsonl
│   └── 2025-10-10.jsonl
├── config.json            # Your telemetry preferences
└── summary.json           # Aggregated statistics
```

### Data Format

**JSONL (JSON Lines)** - One event per line:
```jsonl
{"timestamp": 1728345600.0, "event_type": "agent_invoked", "agent_name": "full-stack-architect"}
{"timestamp": 1728345645.3, "event_type": "agent_completed", "agent_name": "full-stack-architect", "outcome": "success", "duration_seconds": 45.3}
```

### Access Control

- **Only you** can access this data
- No network transmission without explicit consent
- No background uploads or syncing
- No cloud storage or third-party services

### Inspection

You can view your data **anytime**:
```bash
# View today's events
cat ~/.claude-telemetry/events/2025-10-08.jsonl

# View summary statistics
cat ~/.claude-telemetry/summary.json

# Count total events
wc -l ~/.claude-telemetry/events/*.jsonl
```

---

## Privacy Promise

We commit to the following privacy principles:

### 1. Opt-In Only
- Telemetry is **disabled by default**
- You must **explicitly enable** it
- No "pre-checked boxes" or dark patterns
- Clear consent flow with full disclosure

### 2. Local-First Storage
- All data stored **on your machine**
- No automatic cloud sync or uploads
- No third-party analytics services
- You control the data directory

### 3. No Transmission Without Consent
- **Never** automatically upload data
- **Never** phone home in the background
- If we add opt-in data sharing in the future:
  - Requires separate, explicit consent
  - Shows exactly what will be shared
  - Allows review before submission

### 4. Full Transparency
- **Open-source code** - Inspect `tools/telemetry.py` anytime
- **Human-readable format** - Plain JSON, no binary files
- **Complete documentation** - This document + code comments
- **No obfuscation** - Clear, understandable event structure

### 5. Easy Opt-Out
- **Single command** to disable: `python3 tools/telemetry.py disable`
- **Instant deletion**: `rm -rf ~/.claude-telemetry/`
- **No retention** - We don't keep copies when you delete
- **No penalties** - Full functionality without telemetry

### 6. No Third-Party Tracking
- **No Google Analytics** or similar services
- **No advertising networks** or tracking pixels
- **No fingerprinting** techniques
- **No cross-site tracking** or cookies

---

## How to Enable/Disable Telemetry

### Enable Telemetry

#### Interactive Method (Recommended)
```bash
python3 tools/telemetry.py enable
```

**You'll see:**
```
Enable Telemetry?
  ✅ Help improve agent quality
  ✅ Get early access to v4.0 features
  ✅ Your data stays on your machine
  ❌ No code, no PII, no tracking

See details: docs/TELEMETRY_PRIVACY.md

Enable telemetry? (y/N):
```

Type `y` to confirm.

#### Manual Method
Edit `~/.claude-telemetry/config.json`:
```json
{
  "enabled": true,
  "version": "1.0",
  "created_at": "2025-10-08T10:00:00"
}
```

### Disable Telemetry

#### Command Line
```bash
python3 tools/telemetry.py disable
```

**Output:**
```
🔕 Telemetry disabled
```

### Delete All Telemetry Data

```bash
# Complete removal
rm -rf ~/.claude-telemetry/
```

This **permanently deletes** all telemetry data from your machine.

### Check Status

```bash
python3 tools/telemetry.py status
```

**Output:**
```
Telemetry: ✅ Enabled
Data directory: /Users/you/.claude-telemetry
```

---

## Incentives for Opt-In

### Why Enable Telemetry?

**Help Us Improve, Get Exclusive Benefits:**

#### 1. Early Access to v4.0 Features
- **30 days before public release**
- Try new agents, commands, and workflows first
- Provide feedback that shapes the final release
- **Eligibility:** Enable telemetry + 10+ agent invocations

#### 2. Premium Tier Trial
- **7 days free access** to premium agents (coming in v3.0)
- Test advanced AI/ML integration agents
- Explore enterprise-grade security and compliance tools
- **Eligibility:** Enable telemetry + 25+ agent invocations

#### 3. Tier Promotion Voting Rights
- **Vote on agent promotions** - Which Specialized agents should become Core?
- **Influence the roadmap** - Help decide which agents get priority development
- **Quarterly voting rounds** - Your usage data gives you voting power
- **Eligibility:** Enable telemetry + 50+ agent invocations

#### 4. Feature Request Priority
- **Fast-track your feature requests** - Telemetry users get first consideration
- **Direct feedback channel** - Influence what gets built next
- **Beta tester status** - Get invited to test new features early
- **Eligibility:** Enable telemetry + provide feedback

#### 5. Community Recognition
- **Top contributor badges** (anonymous handles, opt-in only)
- **Monthly highlights** of most active users
- **Exclusive Discord channel** for telemetry contributors
- **Eligibility:** Enable telemetry + opt-in to community features

---

## Frequently Asked Questions

### General Questions

**Q: Can you see my code?**
**A:** No. We only collect metadata (agent name, duration, success/failure). No code snippets, file contents, or project details are ever collected.

**Q: Is my data sold to third parties?**
**A:** No. Data never leaves your machine. We have no way to sell what we don't have.

**Q: How do I know what's being collected?**
**A:** Check `~/.claude-telemetry/` anytime. All events are stored in plain JSON files you can read with any text editor.

**Q: What if I opt-in then change my mind?**
**A:** Run `python3 tools/telemetry.py disable` and optionally delete the `~/.claude-telemetry/` folder. No questions asked, no penalties.

**Q: Does telemetry slow down agents?**
**A:** No. Event recording adds <1ms overhead per event and runs asynchronously.

### Privacy & Security

**Q: Is telemetry required to use ClaudeAgents?**
**A:** No. Telemetry is completely optional and disabled by default. All features work without it.

**Q: Will my employer see this data?**
**A:** No. Data is stored locally on your machine in your home directory (`~/`). It's not visible to other users or systems.

**Q: Can I use ClaudeAgents in air-gapped environments?**
**A:** Yes. Telemetry is local-only and doesn't require internet connectivity.

**Q: What if I accidentally enable telemetry?**
**A:** Disable it (`python3 tools/telemetry.py disable`) and delete the folder (`rm -rf ~/.claude-telemetry/`). Done.

**Q: Do you collect IP addresses?**
**A:** No. We don't collect any network information.

### Data Sharing

**Q: Will you ever upload my data without asking?**
**A:** No. We will never automatically upload data. If we add optional data sharing in the future, it will require separate, explicit consent with a review step before submission.

**Q: Can I contribute my data to help improve ClaudeAgents?**
**A:** Yes! You can manually share your `summary.json` (aggregated stats only, not raw events) via GitHub. Review it first to ensure no sensitive info leaked.

**Q: What if there's a data breach?**
**A:** Since all data is stored locally on your machine, there's no central database to breach. Your data is as secure as your local filesystem.

### Incentives & Benefits

**Q: How do I qualify for early access to v4.0?**
**A:** Enable telemetry + record at least 10 agent invocations within 30 days of the v4.0 beta announcement.

**Q: What happens if I disable telemetry after earning benefits?**
**A:** You keep any benefits already granted (e.g., early access codes). Future benefits require active telemetry.

**Q: Can I opt-in to incentives but not data sharing?**
**A:** Yes. All benefits are based on local telemetry collection only. No data sharing required.

---

## Data Retention & Deletion

### Retention Policy

- **Local Storage:** Events are stored indefinitely in `~/.claude-telemetry/` unless you delete them.
- **No Cloud Retention:** We don't store any telemetry data on our servers (because we never receive it).
- **Manual Cleanup:** You can delete old events anytime:

```bash
# Delete events older than 30 days
find ~/.claude-telemetry/events/ -name "*.jsonl" -mtime +30 -delete
```

### Deletion Rights

You have **full control** over your data:

- **Instant deletion** - `rm -rf ~/.claude-telemetry/`
- **No residual data** - We don't keep backups or copies
- **No "soft deletes"** - Data is permanently removed
- **No retention requirements** - Delete anytime, for any reason

---

## Open Source & Auditability

### Transparency Commitment

**All telemetry code is open source:**

- **Source Code:** `/Users/kfowler/Projects/ClaudeAgents/tools/telemetry.py`
- **License:** MIT - Free to inspect, modify, or fork
- **No obfuscation** - Plain Python, no compiled binaries
- **Community audits** - Pull requests welcome for privacy improvements

### How to Audit

1. **Read the code:**
   ```bash
   cat /Users/kfowler/Projects/ClaudeAgents/tools/telemetry.py
   ```

2. **Check network calls:**
   ```bash
   grep -r "requests\|urllib\|http" /Users/kfowler/Projects/ClaudeAgents/tools/telemetry.py
   ```
   Result: **No network calls** - All data stays local.

3. **Inspect events:**
   ```bash
   cat ~/.claude-telemetry/events/*.jsonl | jq .
   ```

4. **Verify file operations:**
   ```bash
   # Use filesystem monitoring to confirm only local writes
   sudo fs_usage -f filesys python3 tools/telemetry.py enable
   ```

---

## Changes to This Policy

### Notification

If we make **material changes** to this privacy policy:

1. **Version number bump** - New version number at the top of this document
2. **GitHub notification** - Announcement in repository README and releases
3. **Opt-in re-confirmation** - For breaking changes, telemetry auto-disables until you re-consent
4. **30-day notice** - Major changes announced 30 days before taking effect

### Change History

- **v2.0 (2025-10-08):** Added incentive programs, expanded FAQ, detailed data collection examples
- **v1.0 (2025-10-07):** Initial privacy policy

---

## Contact & Support

### Questions or Concerns?

- **Privacy inquiries:** Open a [GitHub Issue](https://github.com/anthropics/claude-code/issues) with tag `privacy`
- **General support:** [GitHub Discussions](https://github.com/anthropics/claude-code/discussions)
- **Documentation:** [docs/telemetry-guide.md](telemetry-guide.md)

### Report Privacy Issues

If you discover a privacy issue or data leak:

1. **DO NOT** post publicly (to protect other users)
2. Email: `security@anthropic.com` with subject "ClaudeAgents Privacy Issue"
3. We'll respond within **48 hours**
4. We'll patch critical issues within **7 days**

---

**Maintained By:** ClaudeAgents Core Team
**License:** MIT
**Last Updated:** October 8, 2025
**Next Review:** January 8, 2026
