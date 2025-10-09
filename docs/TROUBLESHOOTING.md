# Troubleshooting Guide

Common issues and solutions for ClaudeAgents platform.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Import Errors](#import-errors)
- [Agent Validation Errors](#agent-validation-errors)
- [Workflow Execution Issues](#workflow-execution-issues)
- [Code Archaeology Issues](#code-archaeology-issues)
- [Testing Issues](#testing-issues)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### Issue: `pip install` fails with dependency conflicts

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement numpy>=1.21.0
```

**Solution**:
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install dependencies
pip install -r tools/requirements.txt

# If still failing, try without version constraints
pip install numpy requests pytest
```

### Issue: Permission denied when installing

**Symptoms**:
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Use --user flag
pip install --user -r tools/requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r tools/requirements.txt
```

---

## Import Errors

### Issue: `ModuleNotFoundError: No module named 'tools'`

**Symptoms**:
```python
ModuleNotFoundError: No module named 'tools.code_archaeology'
```

**Solution**:
```bash
# Ensure you're in the correct directory
cd /path/to/ClaudeAgents

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with python -m
python -m tools.archaeology
```

### Issue: Import errors in archaeology tools

**Symptoms**:
```
ImportError: attempted relative import with no known parent package
```

**Solution**:
```bash
# Use the provided executable
python3 tools/archaeology --query "your question"

# Or install as package (development mode)
pip install -e .
```

---

## Agent Validation Errors

### Issue: Agent validation fails

**Symptoms**:
```
ERROR: Invalid agent definition in agents/my-agent.md
```

**Solution**:
1. Check YAML frontmatter format:
```yaml
---
name: agent-name
model: sonnet
computational_complexity: medium
color: blue
description: "Brief description"
---
```

2. Ensure required fields are present:
   - `name`: Must match filename (without `.md`)
   - `description`: Must be 50-500 characters
   - `model`: Must be `haiku`, `sonnet`, or `opus`

3. Run validation:
```bash
python3 tools/validate_agents.py
```

### Issue: Duplicate agent names

**Symptoms**:
```
ERROR: Duplicate agent name found: my-agent
```

**Solution**:
```bash
# Find duplicates
grep -r "name: my-agent" agents/

# Rename one of them
mv agents/my-agent.md agents/my-agent-v2.md
```

---

## Workflow Execution Issues

### Issue: Workflow command not found

**Symptoms**:
```
ERROR: Workflow '/my-workflow' not found
```

**Solution**:
1. Check command exists:
```bash
ls commands/*/*/*.md | grep my-workflow
```

2. Use correct path format:
```bash
# Correct
/quality:testing-strategy

# Incorrect
/testing-strategy
/quality/testing-strategy
```

3. Check available commands:
```bash
# See all commands
ls commands/*/*/*.md

# Search by keyword
grep -l "testing" commands/*/*.md
```

---

## Code Archaeology Issues

### Issue: "Not a git repository" error

**Symptoms**:
```
ValueError: Not a git repository: /path/to/dir
```

**Solution**:
```bash
# Ensure directory is a git repository
cd /path/to/dir
git status

# If not initialized
git init
```

### Issue: Dimension mismatch in embeddings

**Symptoms**:
```
ValueError: shapes (5,) and (512,) not aligned
```

**Solution**:
This is fixed in v1.0.0. Update to latest version:
```bash
git pull
```

### Issue: GitHub enrichment fails

**Symptoms**:
```
GitHub API rate limit exceeded or forbidden
```

**Solution**:
```bash
# Set GitHub token
export GITHUB_TOKEN="your_token_here"

# Verify token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Run without GitHub enrichment
python3 tools/archaeology --query "your question"
# (Don't use --github flag)
```

### Issue: FAISS not available warning

**Symptoms**:
```
Warning: FAISS not available, using simple search
```

**Solution**:
```bash
# Install FAISS (optional, for better performance)
pip install faiss-cpu

# Or ignore - simple search works fine for <1000 commits
```

### Issue: Rich formatting not working

**Symptoms**:
Plain text output instead of colored formatting

**Solution**:
```bash
# Install rich
pip install rich

# Or use NO_COLOR environment variable
NO_COLOR=1 python3 tools/archaeology
```

---

## Testing Issues

### Issue: pytest not found

**Symptoms**:
```
bash: pytest: command not found
```

**Solution**:
```bash
# Install pytest
pip install pytest pytest-cov

# Run with python -m
python3 -m pytest tests/
```

### Issue: Integration tests failing

**Symptoms**:
```
FAILED tests/test_integration_archaeology.py::test_github_enrichment
```

**Solution**:
```bash
# Skip integration tests (require git repo)
pytest tests/ -v -m "not integration"

# Run only unit tests
pytest tests/test_git_analyzer.py tests/test_github_integrator.py
```

### Issue: Unknown pytest marker warning

**Symptoms**:
```
PytestUnknownMarkWarning: Unknown pytest.mark.integration
```

**Solution**:
This is just a warning. Fixed by `pytest.ini`. If still seeing it:
```bash
# Add pytest.ini to project root
# (Should already be there in v1.0.0+)
```

---

## Performance Issues

### Issue: Analysis is very slow

**Symptoms**:
Analyzing 1000+ commits takes several minutes

**Solution**:
```bash
# Limit analysis
python3 tools/archaeology --query "question" --limit 100

# Install FAISS for faster search
pip install faiss-cpu

# Use more efficient embedding provider
# (Already default in v1.0.0)
```

### Issue: High memory usage

**Symptoms**:
Python process using >2GB RAM

**Solution**:
```bash
# Limit commits analyzed
python3 -c "
from tools.code_archaeology import GitArchaeologist
arch = GitArchaeologist('.')
history = arch.analyze_repo(limit=100)  # Limit to 100 commits
"

# Or analyze in chunks
# (Future feature)
```

---

## Getting Help

Still stuck? Here's how to get help:

1. **Check existing issues**: [GitHub Issues](https://github.com/anthropics/claude-code/issues)

2. **Create a new issue** with:
   - Error message (full traceback)
   - Python version: `python3 --version`
   - OS: `uname -a` (Linux/Mac) or `ver` (Windows)
   - Installation method
   - Minimal reproduction steps

3. **Community support**:
   - Discord: [claude.ai/discord](https://claude.ai/discord)
   - Forum: [community.anthropic.com](https://community.anthropic.com)

---

## Debug Mode

Enable debug logging for more information:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with verbose output
python3 tools/archaeology --query "question" -v
```

---

## Common Error Patterns

### Pattern: "File not found"
- **Cause**: Incorrect path or working directory
- **Fix**: Use absolute paths or verify `pwd`

### Pattern: "Permission denied"
- **Cause**: Insufficient file permissions
- **Fix**: Check file ownership with `ls -la`

### Pattern: "Import error"
- **Cause**: Missing dependencies or wrong PYTHONPATH
- **Fix**: Reinstall requirements, check PYTHONPATH

### Pattern: "Rate limit exceeded"
- **Cause**: Too many GitHub API calls
- **Fix**: Set GITHUB_TOKEN or reduce requests

---

Last updated: 2025-10-08
Version: 1.0.0
