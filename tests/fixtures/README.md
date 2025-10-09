# AIL Test Fixtures

Test fixtures for Archaeological Intelligence Layer (AIL) testing.

## Overview

These fixtures provide controlled test environments for measuring agent quality improvement with AIL context. Each fixture contains:

1. **Known Code Issues**: Deliberately planted issues for agents to find
2. **Historical Context**: Git history explaining design decisions
3. **Ground Truth**: Documentation of what agents should find
4. **Complexity Levels**: Easy, medium, hard test cases

## Fixture Categories

### 1. Code Review Fixtures

**Purpose**: Test code-architect agent's ability to identify architectural issues

**Fixtures**:
- `code_review_simple.py` - Basic architectural issues (5 known findings)
- `code_review_complex.py` - Advanced design patterns (10 known findings)
- `code_review_historical.py` - Issues requiring historical context (8 findings)

**Expected Improvement**:
- Without AIL: Finds surface-level issues (40-50% recall)
- With AIL: Finds historical context issues (85-90% recall)

### 2. Security Audit Fixtures

**Purpose**: Test security-audit-specialist's ability to distinguish real issues from documented workarounds

**Fixtures**:
- `security_basic.py` - Common vulnerabilities (3 real, 0 false positives)
- `security_workarounds.py` - Legitimate security exceptions (2 real, 2 documented exceptions)
- `security_false_positives.py` - Tricky cases (1 real, 4 false positives without context)

**Expected Improvement**:
- Without AIL: High false positive rate (40-50%)
- With AIL: Low false positive rate (<10%)

### 3. Refactoring Fixtures

**Purpose**: Test refactoring-specialist's ability to suggest safe refactorings

**Fixtures**:
- `refactoring_safe.py` - Safe refactoring opportunities (5 low-risk)
- `refactoring_constrained.py` - Code with historical constraints (3 risky without context)
- `refactoring_evolution.py` - Code that evolved for specific reasons (historical constraints)

**Expected Improvement**:
- Without AIL: Suggests risky refactorings (60% high-risk)
- With AIL: Suggests safe refactorings (90% low-risk)

## Usage

### Running Tests with Fixtures

```python
# Run all fixture tests
pytest tests/test_ail_quality_metrics.py -v

# Run specific fixture category
pytest tests/test_ail_quality_metrics.py::TestCodeReviewQualityMetrics -v

# Generate quality report
pytest tests/test_ail_quality_metrics.py::TestOverallQualityImprovement -v
```

### Creating New Fixtures

1. Create file in appropriate category directory
2. Add ground truth documentation
3. Create git history explaining decisions
4. Add test case in quality metrics

## Fixture Structure

Each fixture follows this structure:

```
fixtures/
├── code_review/
│   ├── simple.py           # Test code
│   ├── simple_ground_truth.json  # Expected findings
│   └── simple_history.md   # Historical context
├── security/
│   ├── workarounds.py
│   ├── workarounds_ground_truth.json
│   └── workarounds_history.md
└── refactoring/
    ├── constrained.py
    ├── constrained_ground_truth.json
    └── constrained_history.md
```

## Ground Truth Format

```json
{
  "fixture_name": "security_workarounds",
  "expected_findings": [
    {
      "id": "SEC-001",
      "type": "real_vulnerability",
      "severity": "high",
      "description": "SQL injection in user input",
      "location": "line 45"
    },
    {
      "id": "SEC-002",
      "type": "documented_exception",
      "severity": "low",
      "description": "Hardcoded API key (test environment only)",
      "location": "line 78",
      "historical_context": "Commit abc123: Test API key for CI/CD"
    }
  ],
  "quality_baseline": {
    "without_ail": {
      "true_positives": 1,
      "false_positives": 2,
      "precision": 0.33
    },
    "with_ail": {
      "true_positives": 1,
      "false_positives": 0,
      "precision": 1.0
    }
  }
}
```

## Historical Context Format

Each fixture should have git history that provides context:

```markdown
# Fixture: Security Workarounds

## Commit History

### 2024-01-15: Add test API key
**Commit**: abc123
**Author**: dev@example.com
**Message**: Add hardcoded API key for CI/CD testing

This API key is intentionally hardcoded for test environments.
It has rate limits and cannot be used in production.
See: SECURITY.md for production key management.

### 2024-01-20: Document security exception
**Commit**: def456
**Author**: security@example.com
**Message**: Security review: Approved test API key exception

Security team reviewed and approved the hardcoded test API key.
Exception documented in security audit log.
```

## Quality Metrics

Fixtures should demonstrate these improvements:

| Metric | Without AIL | With AIL | Improvement |
|--------|-------------|----------|-------------|
| Code Review Thoroughness | 50% | 85% | +70% |
| Security False Positives | 40% | 10% | -75% |
| Refactoring Safety | 40% | 90% | +125% |
| **Overall Quality** | **43%** | **88%** | **+105%** |

Target: **40%+ weighted improvement** across all metrics
