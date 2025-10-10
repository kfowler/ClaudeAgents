# AIL Production Deployment Guide

**Complete guide for deploying Archaeological Intelligence Layer (AIL) to production environments**

**Version**: 2.0.0 (Sprint 2)
**Updated**: 2025-10-09
**Target Audience**: DevOps Engineers, System Administrators, Production Deployments

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [FAISS Activation](#faiss-activation)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Rollout Strategy](#rollout-strategy)
9. [Rollback Procedures](#rollback-procedures)
10. [Security Considerations](#security-considerations)
11. [Common Issues](#common-issues)
12. [Maintenance](#maintenance)

---

## System Requirements

### Minimum Requirements (Sprint 1 Only)

**For basic AIL without FAISS**:
- **OS**: Linux, macOS, or Windows
- **Python**: 3.9+
- **RAM**: 512MB available
- **Storage**: 100MB available
- **CPU**: 1 core
- **Network**: Optional (for GitHub integration)

**Expected Performance**:
- 50 queries/second
- p95 latency: ~800ms (cold), ~5ms (cached)
- Cache hit rate: 30-50%

### Recommended Requirements (Sprint 2 with FAISS)

**For full AIL with semantic search**:
- **OS**: Linux (Ubuntu 20.04+, RHEL 8+) or macOS
- **Python**: 3.9, 3.10, or 3.11 (3.12 not yet tested)
- **RAM**: 4GB available (2GB minimum)
- **Storage**: 1GB SSD (500MB minimum)
- **CPU**: 4+ cores (2+ minimum)
- **Network**: Optional (for GitHub integration)

**Expected Performance**:
- 110+ queries/second
- p95 latency: ~450ms (cold), ~2ms (L1 cached), ~35ms (L2 cached)
- Cache hit rate: 50-60%

### High-Throughput Requirements

**For production systems with 1000+ queries/hour**:
- **OS**: Linux (Ubuntu 22.04+ recommended)
- **Python**: 3.10 or 3.11
- **RAM**: 8GB+ available
- **Storage**: 2GB+ NVMe SSD
- **CPU**: 8+ cores
- **GPU**: Optional (NVIDIA with CUDA for 10x embedding speedup)
- **Network**: 100 Mbps+ (for GitHub integration)

**Expected Performance**:
- 200+ queries/second
- p95 latency: ~300ms (cold), ~1ms (L1 cached), ~25ms (L2 cached)
- Cache hit rate: 60-70%

### Hardware Sizing Guide

| Workload | Queries/Hour | RAM | Storage | CPU Cores | GPU |
|----------|-------------|-----|---------|-----------|-----|
| **Development** | <100 | 2GB | 500MB | 2 | No |
| **Small Production** | 100-1000 | 4GB | 1GB | 4 | No |
| **Medium Production** | 1000-10000 | 8GB | 2GB | 8 | Optional |
| **Large Production** | 10000+ | 16GB | 5GB | 16+ | Yes |

---

## Pre-Deployment Checklist

### Code Review

- [ ] Review [Sprint 2 Complete Summary](AIL_SPRINT_2_COMPLETE.md)
- [ ] Understand [Architecture](AIL_ARCHITECTURE.md)
- [ ] Review [Performance Benchmarks](AIL_SPRINT_2_PERFORMANCE_BENCHMARKS.md)
- [ ] Read [Security Considerations](#security-considerations)

### Infrastructure

- [ ] Verify system requirements met
- [ ] Provision adequate RAM (4GB+ recommended)
- [ ] Ensure SSD storage available (1GB+)
- [ ] Configure network access (if using GitHub)
- [ ] Set up monitoring infrastructure
- [ ] Configure log aggregation
- [ ] Set up alerting system

### Dependencies

- [ ] Python 3.9+ installed and verified
- [ ] Git installed and configured
- [ ] Access to repository (local or remote)
- [ ] GitHub token (optional, for enhanced context)
- [ ] FAISS installation tested (optional, for Sprint 2 features)

### Testing

- [ ] Run validation scripts successfully
- [ ] Execute test suite (100% pass rate required)
- [ ] Perform load testing with expected query volume
- [ ] Verify cache performance
- [ ] Test rollback procedures

### Documentation

- [ ] Document deployment configuration
- [ ] Create runbook for common operations
- [ ] Document monitoring and alerting
- [ ] Create incident response procedures
- [ ] Document rollback procedures

---

## Installation

### Step 1: Environment Setup

```bash
# Create dedicated user (recommended)
sudo useradd -m -s /bin/bash ail
sudo su - ail

# Create directory structure
mkdir -p ~/ail/{logs,data,cache,config}
cd ~/ail

# Clone repository (if not already present)
git clone https://github.com/your-org/ClaudeAgents.git
cd ClaudeAgents
```

### Step 2: Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install numpy>=1.21.0 requests>=2.28.0

# Verify core installation
python3 -c "from tools.ail import ArchaeologyContextProvider; print('✅ Core AIL installed')"
```

### Step 3: Optional Dependencies (Sprint 2)

```bash
# Install FAISS (CPU version for most deployments)
pip install faiss-cpu>=1.7.4

# For GPU deployments (10x speedup for embeddings)
# pip install faiss-gpu>=1.7.4

# Install sentence transformers
pip install sentence-transformers>=2.2.0

# Verify FAISS installation
python3 tools/ail/validate_faiss.py .
```

**Expected Output**:
```
✅ FAISS Installation Validation
====================================
✅ faiss-cpu installed (version 1.7.4)
✅ sentence-transformers installed (version 2.2.0)
✅ Embedding model loaded (all-MiniLM-L6-v2)
✅ FAISS index created successfully
✅ Search functionality working
✅ All FAISS features operational

Summary: FAISS is ready for production use
```

### Step 4: Testing Dependencies

```bash
# Install testing framework (optional, for validation)
pip install pytest>=7.0.0 pytest-asyncio>=0.21.0

# Run full test suite
python3 -m pytest tests/test_ail/ -v

# Expected: 57+ tests passing
```

### Step 5: Freeze Dependencies

```bash
# Save exact versions for reproducibility
pip freeze > requirements-production.txt

# For future deployments, use:
# pip install -r requirements-production.txt
```

---

## Configuration

### Environment Variables

Create `/etc/ail/config.env`:

```bash
# Core Configuration
AIL_REPO_PATH=/path/to/your/repository
AIL_CACHE_SIZE=2000              # L1 cache entries (default: 1000)
AIL_MAX_QUERY_TIME_S=5.0         # Query timeout (default: 2.0)

# FAISS Configuration (Sprint 2)
AIL_FAISS_ENABLED=true           # Enable FAISS semantic search
FAISS_ROLLOUT=100                # Percentage of traffic (0-100)
FAISS_SIMILARITY_THRESHOLD=0.85  # Semantic similarity threshold (0.0-1.0)
FAISS_CACHE_SIZE=200             # L2 cache entries (default: 100)

# GitHub Integration (Optional)
GITHUB_OWNER=your-org            # GitHub organization
GITHUB_REPO=your-repo            # GitHub repository
GITHUB_TOKEN=ghp_your_token      # GitHub personal access token

# Logging
AIL_LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
AIL_LOG_FILE=/var/log/ail/ail.log

# Performance Tuning
AIL_BATCH_SIZE=32                # Embedding batch size (default: 32)
AIL_MAX_WORKERS=4                # Concurrent workers (default: CPU count)
```

Load configuration:

```bash
# In your application startup
source /etc/ail/config.env

# Or in Python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/etc/ail/config.env')
```

### Application Configuration

Create `config/ail_production.py`:

```python
import os
from tools.ail import ArchaeologyContextProvider

class AILConfig:
    """Production AIL configuration."""

    # Repository
    REPO_PATH = os.environ.get('AIL_REPO_PATH', '.')

    # Cache Configuration
    CACHE_SIZE = int(os.environ.get('AIL_CACHE_SIZE', '2000'))
    MAX_QUERY_TIME_S = float(os.environ.get('AIL_MAX_QUERY_TIME_S', '5.0'))

    # FAISS Configuration
    FAISS_ENABLED = os.environ.get('AIL_FAISS_ENABLED', 'true').lower() == 'true'
    FAISS_ROLLOUT = int(os.environ.get('FAISS_ROLLOUT', '100'))
    FAISS_SIMILARITY_THRESHOLD = float(os.environ.get('FAISS_SIMILARITY_THRESHOLD', '0.85'))

    # GitHub Configuration
    GITHUB_OWNER = os.environ.get('GITHUB_OWNER')
    GITHUB_REPO = os.environ.get('GITHUB_REPO')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

    # Logging
    LOG_LEVEL = os.environ.get('AIL_LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('AIL_LOG_FILE', '/var/log/ail/ail.log')

    @classmethod
    def create_provider(cls) -> ArchaeologyContextProvider:
        """Create configured provider instance."""
        return ArchaeologyContextProvider(
            repo_path=cls.REPO_PATH,
            cache_size=cls.CACHE_SIZE,
            max_query_time_s=cls.MAX_QUERY_TIME_S,
            github_owner=cls.GITHUB_OWNER,
            github_repo=cls.GITHUB_REPO,
            github_token=cls.GITHUB_TOKEN,
        )

# Usage
provider = AILConfig.create_provider()
```

### Logging Configuration

Create `config/logging_config.py`:

```python
import logging
import logging.handlers
import os

def setup_logging():
    """Configure production logging."""
    log_level = os.environ.get('AIL_LOG_LEVEL', 'INFO')
    log_file = os.environ.get('AIL_LOG_FILE', '/var/log/ail/ail.log')

    # Create logger
    logger = logging.getLogger('tools.ail')
    logger.setLevel(getattr(logging, log_level))

    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Usage
setup_logging()
```

---

## FAISS Activation

### Verification

Before activating FAISS in production:

```bash
# Validate FAISS installation
python3 tools/ail/validate_faiss.py $AIL_REPO_PATH

# Validate semantic cache
python3 tools/ail/validate_semantic_cache.py $AIL_REPO_PATH

# Run performance benchmarks
python3 -m pytest tests/test_ail/test_sprint2_performance.py -v
```

### Gradual Rollout (Recommended)

#### Phase 1: Dark Launch (Day 1)

Deploy with FAISS disabled:

```bash
# In /etc/ail/config.env
AIL_FAISS_ENABLED=false
FAISS_ROLLOUT=0
```

Build indices in background:

```bash
# Build FAISS indices without serving traffic
python3 -c "
from tools.ail import ArchaeologyContextProvider
provider = ArchaeologyContextProvider('$AIL_REPO_PATH')
print('✅ Indices built successfully')
"
```

Monitor logs for any errors or warnings.

#### Phase 2: 10% Rollout (Day 2)

Enable FAISS for 10% of traffic:

```bash
# In /etc/ail/config.env
AIL_FAISS_ENABLED=true
FAISS_ROLLOUT=10  # 10% of queries use FAISS
```

Restart application:

```bash
sudo systemctl restart ail-service
```

Monitor metrics (see [Monitoring & Alerts](#monitoring--alerts)):
- Latency (p50, p95, p99)
- Memory usage
- Cache hit rates (L1 vs L2)
- Error rates

If metrics are good after 24 hours, proceed to next phase.

#### Phase 3: 25% → 50% Rollout (Day 3)

Increase rollout percentage gradually:

```bash
# 25% rollout
FAISS_ROLLOUT=25
sudo systemctl restart ail-service

# Monitor for 12 hours, then:
FAISS_ROLLOUT=50
sudo systemctl restart ail-service
```

#### Phase 4: 100% Rollout (Day 4+)

Full production rollout:

```bash
# 100% rollout
FAISS_ROLLOUT=100
sudo systemctl restart ail-service
```

Continue monitoring for 7 days to ensure stability.

### Instant Rollback

If issues are detected:

```bash
# Instant rollback (no restart required)
export AIL_FAISS_ENABLED=false

# Or set in config and restart
FAISS_ROLLOUT=0
sudo systemctl restart ail-service
```

System automatically falls back to L1 cache only.

---

## Performance Tuning

### Cache Optimization

#### L1 Cache Sizing

```python
# Calculate optimal L1 cache size
# Rule: 1000 entries per 1000 queries/hour
queries_per_hour = 5000
cache_size = queries_per_hour * 1.0  # 5000 entries

provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=int(cache_size)
)
```

**Memory Impact**: ~10KB per cache entry
- 1000 entries: ~10MB
- 5000 entries: ~50MB
- 10000 entries: ~100MB

#### L2 Cache Tuning

```bash
# In /etc/ail/config.env
FAISS_CACHE_SIZE=200              # Semantic cache entries (default: 100)
FAISS_SIMILARITY_THRESHOLD=0.85   # Lower = more cache hits, less precision
```

**Tuning Guidelines**:
- **High precision**: `FAISS_SIMILARITY_THRESHOLD=0.90` (fewer hits, higher quality)
- **Balanced**: `FAISS_SIMILARITY_THRESHOLD=0.85` (default, recommended)
- **High recall**: `FAISS_SIMILARITY_THRESHOLD=0.80` (more hits, lower quality)

### Memory Optimization

#### Reduce Memory Footprint

```python
# For memory-constrained environments
provider = ArchaeologyContextProvider(
    repo_path=".",
    cache_size=500,  # Smaller L1 cache
)

# Set smaller L2 cache
os.environ['FAISS_CACHE_SIZE'] = '50'
```

#### Monitor Memory Usage

```python
import psutil
import os

def monitor_memory():
    """Monitor AIL memory usage."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()

    print(f"RSS: {mem_info.rss / 1024 / 1024:.0f}MB")
    print(f"VMS: {mem_info.vms / 1024 / 1024:.0f}MB")

    # Alert if over 500MB
    if mem_info.rss > 500 * 1024 * 1024:
        print("⚠️  High memory usage detected")

monitor_memory()
```

### Latency Optimization

#### Reduce Query Timeout

```python
# For fast queries only
provider = ArchaeologyContextProvider(
    repo_path=".",
    max_query_time_s=1.0  # Strict 1s timeout
)
```

#### Pre-warm Cache

```python
# Pre-warm cache at startup
common_queries = [
    ("README.md", "What is this project?"),
    ("src/main.py", "What is the entry point?"),
    # ... top 20-50 most common queries
]

for file_path, question in common_queries:
    provider.get_context_sync(file_path, question)
```

### Throughput Optimization

#### Increase Batch Size

```bash
# In /etc/ail/config.env
AIL_BATCH_SIZE=64  # Default: 32 (larger = faster for batch operations)
```

#### Concurrent Workers

```bash
# In /etc/ail/config.env
AIL_MAX_WORKERS=8  # Default: CPU count (adjust based on workload)
```

#### GPU Acceleration (Optional)

```bash
# Install GPU version
pip install faiss-gpu>=1.7.4

# Verify GPU availability
python3 -c "import faiss; print(f'GPU available: {faiss.get_num_gpus()}')"
```

**Performance Gain**: 10x faster embedding generation with GPU

---

## Monitoring & Alerts

### Key Metrics

#### Latency Metrics

```python
from prometheus_client import Histogram

# Define metrics
query_latency = Histogram(
    'ail_query_latency_seconds',
    'AIL query latency',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Instrument queries
with query_latency.time():
    context = provider.get_context_sync("file.py", "question")
```

**Alert Thresholds**:
- **Warning**: p95 latency > 600ms
- **Critical**: p95 latency > 1000ms

#### Cache Metrics

```python
from prometheus_client import Gauge, Counter

# Cache hit rates
cache_hits = Counter('ail_cache_hits_total', 'Cache hits', ['tier'])
cache_misses = Counter('ail_cache_misses_total', 'Cache misses', ['tier'])
cache_size = Gauge('ail_cache_size_entries', 'Cache size', ['tier'])

# Track hits/misses
stats = provider.get_cache_stats()
cache_hits.labels(tier='l1').inc(stats.l1_hits)
cache_hits.labels(tier='l2').inc(stats.l2_hits)
cache_misses.labels(tier='l1').inc(stats.l1_misses)
```

**Alert Thresholds**:
- **Warning**: Combined hit rate < 40%
- **Critical**: Combined hit rate < 30%

#### Memory Metrics

```python
from prometheus_client import Gauge

memory_usage = Gauge('ail_memory_usage_bytes', 'Memory usage')

# Update periodically
process = psutil.Process(os.getpid())
memory_usage.set(process.memory_info().rss)
```

**Alert Thresholds**:
- **Warning**: Memory > 400MB
- **Critical**: Memory > 600MB

#### Error Metrics

```python
from prometheus_client import Counter

errors = Counter('ail_errors_total', 'Errors', ['type'])

# Track errors
try:
    context = provider.get_context_sync("file.py", "question")
except TimeoutError:
    errors.labels(type='timeout').inc()
except Exception as e:
    errors.labels(type='other').inc()
```

**Alert Thresholds**:
- **Warning**: Error rate > 1%
- **Critical**: Error rate > 5%

### Health Checks

#### Liveness Probe

```python
def liveness_check() -> bool:
    """Check if AIL is alive."""
    return provider.is_initialized()

# HTTP endpoint
@app.get('/health/live')
def health_live():
    if liveness_check():
        return {'status': 'ok'}
    return {'status': 'error'}, 503
```

#### Readiness Probe

```python
def readiness_check() -> bool:
    """Check if AIL is ready to serve traffic."""
    if not provider.is_initialized():
        return False

    # Quick test query
    try:
        context = provider.get_context_sync(
            "README.md",
            "test",
            timeout=1.0
        )
        return True
    except:
        return False

# HTTP endpoint
@app.get('/health/ready')
def health_ready():
    if readiness_check():
        return {'status': 'ready'}
    return {'status': 'not_ready'}, 503
```

### Dashboards

#### Grafana Dashboard Example

```json
{
  "dashboard": {
    "title": "AIL Production Metrics",
    "panels": [
      {
        "title": "Query Latency (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(ail_query_latency_seconds_bucket[5m]))"
        }],
        "thresholds": [
          {"value": 0.6, "color": "yellow"},
          {"value": 1.0, "color": "red"}
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [{
          "expr": "rate(ail_cache_hits_total[5m]) / (rate(ail_cache_hits_total[5m]) + rate(ail_cache_misses_total[5m]))"
        }],
        "thresholds": [
          {"value": 0.4, "color": "red"},
          {"value": 0.5, "color": "yellow"},
          {"value": 0.6, "color": "green"}
        ]
      },
      {
        "title": "Memory Usage",
        "targets": [{
          "expr": "ail_memory_usage_bytes / 1024 / 1024"
        }],
        "thresholds": [
          {"value": 400, "color": "yellow"},
          {"value": 600, "color": "red"}
        ]
      }
    ]
  }
}
```

---

## Rollout Strategy

See [FAISS Activation](#faiss-activation) for detailed rollout procedure.

**Summary**:
1. **Day 1**: Dark launch (FAISS disabled, build indices)
2. **Day 2**: 10% rollout (monitor metrics)
3. **Day 3**: 25% → 50% rollout (gradual increase)
4. **Day 4+**: 100% rollout (full production)

---

## Rollback Procedures

### Immediate Rollback (No Downtime)

```bash
# Method 1: Environment variable (instant, no restart)
export AIL_FAISS_ENABLED=false

# Method 2: Configuration file (requires restart)
# Edit /etc/ail/config.env
AIL_FAISS_ENABLED=false
sudo systemctl restart ail-service

# Method 3: Gradual rollback
FAISS_ROLLOUT=50  # Reduce to 50%
FAISS_ROLLOUT=10  # Reduce to 10%
FAISS_ROLLOUT=0   # Full rollback
```

### Rollback Verification

```bash
# Verify rollback
python3 -c "
import os
os.environ['AIL_FAISS_ENABLED'] = 'false'
from tools.ail import ArchaeologyContextProvider
provider = ArchaeologyContextProvider('.')
stats = provider.get_cache_stats()
print(f'L2 hits: {stats.l2_hits}')  # Should be 0 after rollback
print('✅ Rollback verified')
"
```

### Rollback Scenarios

| Scenario | Action | Expected Impact |
|----------|--------|-----------------|
| **High Latency** | Set `FAISS_ROLLOUT=0` | Immediate latency reduction |
| **High Memory** | Set `FAISS_ROLLOUT=0` | Memory drops ~90MB |
| **High Errors** | Set `AIL_FAISS_ENABLED=false` | Instant fallback to L1 cache |
| **Index Corruption** | Delete index files, restart | Rebuilds indices on startup |

---

## Security Considerations

### GitHub Token Security

```bash
# Store GitHub token securely
# Option 1: Environment variable (not in code)
export GITHUB_TOKEN=$(cat /secure/path/github_token)

# Option 2: Secrets management (Vault, AWS Secrets Manager)
export GITHUB_TOKEN=$(vault kv get -field=token secret/github)

# Option 3: Kubernetes secret
kubectl create secret generic ail-github-token \
  --from-literal=token=ghp_your_token_here
```

### File System Security

```bash
# Secure configuration directory
sudo chown -R ail:ail /etc/ail
sudo chmod 700 /etc/ail
sudo chmod 600 /etc/ail/config.env

# Secure log directory
sudo chown -R ail:ail /var/log/ail
sudo chmod 750 /var/log/ail

# Secure data directory
sudo chown -R ail:ail /var/lib/ail
sudo chmod 700 /var/lib/ail
```

### Network Security

```bash
# Firewall rules (if exposing HTTP endpoints)
sudo ufw allow from 10.0.0.0/8 to any port 8080 proto tcp  # Internal only
sudo ufw deny from any to any port 8080 proto tcp          # Block external

# TLS/SSL (if serving over network)
# Use reverse proxy (nginx, traefik) with TLS termination
```

### Data Privacy

**No Sensitive Data in Logs**:
```python
# ✅ Good: Don't log sensitive data
logger.info(f"Query completed in {query_time_ms}ms")

# ❌ Bad: Don't log full queries or responses
# logger.info(f"Query: {question}, Answer: {answer}")
```

**No Sensitive Data in Cache**:
- AIL caches only query results, not credentials
- Cache keys are SHA256 hashes (not reversible)
- Cached data stored in memory only (not persisted to disk by default)

### Compliance

**GDPR Considerations**:
- AIL processes git history (public commit data)
- No personal data stored beyond git author information
- Cache can be cleared on demand: `provider.clear_cache()`
- Logs can be anonymized/redacted

**SOC 2 Considerations**:
- Enable comprehensive logging (`LOG_LEVEL=DEBUG`)
- Set up audit trails (track all queries)
- Implement access controls (authentication/authorization)
- Regular security updates (dependency scanning)

---

## Common Issues

### Issue: FAISS Installation Fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement faiss-cpu
```

**Solutions**:
```bash
# Option 1: Use conda (recommended for difficult installations)
conda install -c conda-forge faiss-cpu

# Option 2: Try different FAISS version
pip install faiss-cpu==1.7.3

# Option 3: Build from source (last resort)
git clone https://github.com/facebookresearch/faiss.git
cd faiss
cmake -B build .
make -C build -j8
cd build/faiss/python
pip install .

# Option 4: Deploy without FAISS (fallback)
# AIL works without FAISS (Sprint 1 features only)
```

### Issue: High Memory Usage

**Symptoms**: Memory > 500MB

**Diagnosis**:
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.0f}MB")

# Check cache sizes
stats = provider.get_cache_stats()
print(f"L1 cache: {stats.l1_size} entries")
print(f"L2 cache: {stats.l2_size} entries")
```

**Solutions**:
```python
# 1. Reduce L1 cache size
provider = ArchaeologyContextProvider(repo_path=".", cache_size=500)

# 2. Reduce L2 cache size
os.environ['FAISS_CACHE_SIZE'] = '50'

# 3. Clear cache periodically
provider.clear_cache()

# 4. Disable FAISS if needed
os.environ['AIL_FAISS_ENABLED'] = 'false'
```

### Issue: Slow Queries

**Symptoms**: Queries consistently > 1s

**Diagnosis**:
```python
stats = provider.get_cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Avg query time: {stats.avg_query_time_ms:.0f}ms")

# If hit rate < 30%, cache not working well
# If avg query time > 500ms, performance issue
```

**Solutions**:
```python
# 1. Increase cache size
provider = ArchaeologyContextProvider(repo_path=".", cache_size=5000)

# 2. Pre-warm cache
for query in common_queries:
    provider.get_context_sync(*query)

# 3. Reduce query timeout
provider = ArchaeologyContextProvider(repo_path=".", max_query_time_s=1.0)

# 4. Check repository size (>10k commits may be slow)
```

### Issue: Low Confidence Scores

**Symptoms**: Confidence consistently < 20%

**Solutions**:
1. **More specific questions**: Ask detailed questions
2. **Better commit messages**: Ensure repository has descriptive commits
3. **Use files with history**: New files have limited context
4. **Enable GitHub integration**: Add GitHub token for PR/issue context

---

## Maintenance

### Regular Maintenance Tasks

#### Daily

- [ ] Monitor dashboard metrics
- [ ] Check error logs for anomalies
- [ ] Verify backup completion

#### Weekly

- [ ] Review cache hit rates (optimize if < 40%)
- [ ] Check memory usage trends
- [ ] Review slow query logs
- [ ] Update dependencies (security patches)

#### Monthly

- [ ] Performance benchmarking
- [ ] Capacity planning review
- [ ] Security audit
- [ ] Documentation updates

#### Quarterly

- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Architecture review
- [ ] Upgrade planning

### Backup & Recovery

#### Cache Backup (Optional)

```bash
# Backup cache (if persistence enabled)
tar -czf ail-cache-$(date +%Y%m%d).tar.gz /var/lib/ail/cache/

# Restore cache
tar -xzf ail-cache-20251009.tar.gz -C /var/lib/ail/
```

#### Configuration Backup

```bash
# Backup configuration
cp /etc/ail/config.env /backups/ail-config-$(date +%Y%m%d).env

# Backup indices
tar -czf ail-indices-$(date +%Y%m%d).tar.gz /var/lib/ail/indices/
```

### Upgrades

#### Minor Version Upgrade (2.0.x → 2.0.y)

```bash
# 1. Backup current version
pip freeze > requirements-before-upgrade.txt

# 2. Upgrade dependencies
pip install --upgrade numpy requests faiss-cpu sentence-transformers

# 3. Run tests
python3 -m pytest tests/test_ail/ -v

# 4. Restart service
sudo systemctl restart ail-service

# 5. Monitor for issues
# Check metrics for 24 hours
```

#### Major Version Upgrade (2.0.x → 3.0.0)

```bash
# 1. Review CHANGELOG.md for breaking changes
cat tools/ail/CHANGELOG.md

# 2. Backup everything
./scripts/backup-ail.sh

# 3. Test in staging environment first
# Deploy to staging, run full test suite

# 4. Deploy to production (during maintenance window)
# Follow rollout strategy (10% → 25% → 50% → 100%)

# 5. Monitor closely for 7 days
```

### Health Checks

#### Automated Health Check Script

```bash
#!/bin/bash
# /usr/local/bin/ail-health-check.sh

set -e

echo "Running AIL health check..."

# 1. Check service status
if ! systemctl is-active --quiet ail-service; then
    echo "❌ Service not running"
    exit 1
fi

# 2. Check memory usage
MEM_USAGE=$(ps aux | grep ail | awk '{sum+=$6} END {print sum/1024}')
if (( $(echo "$MEM_USAGE > 500" | bc -l) )); then
    echo "⚠️  High memory usage: ${MEM_USAGE}MB"
fi

# 3. Check cache hit rate
HIT_RATE=$(python3 -c "
from tools.ail import ArchaeologyContextProvider
provider = ArchaeologyContextProvider('.')
stats = provider.get_cache_stats()
print(f'{stats.hit_rate:.2f}')
")

if (( $(echo "$HIT_RATE < 0.3" | bc -l) )); then
    echo "⚠️  Low cache hit rate: ${HIT_RATE}"
fi

# 4. Test query
python3 -c "
from tools.ail import ArchaeologyContextProvider
provider = ArchaeologyContextProvider('.')
context = provider.get_context_sync('README.md', 'test')
assert context is not None
print('✅ Query test passed')
"

echo "✅ Health check passed"
```

Run periodically:

```bash
# Add to crontab
crontab -e
*/5 * * * * /usr/local/bin/ail-health-check.sh >> /var/log/ail/health-check.log 2>&1
```

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying AIL to production environments. Follow the checklist, monitor metrics closely, and use the rollback procedures if issues arise.

### Key Takeaways

1. **Start Small**: Begin with Sprint 1 (no FAISS), then gradually enable Sprint 2 features
2. **Monitor Everything**: Set up comprehensive monitoring before production deployment
3. **Test Thoroughly**: Run validation scripts and test suite before deploying
4. **Roll Out Gradually**: Use 10% → 25% → 50% → 100% rollout strategy
5. **Have Rollback Ready**: Instant rollback capability with `AIL_FAISS_ENABLED=false`

### Support

- **Documentation**: [AIL User Guide](AIL_USER_GUIDE.md), [API Reference](AIL_API.md)
- **Getting Started**: [Getting Started Guide](AIL_GETTING_STARTED.md)
- **Troubleshooting**: This guide's [Common Issues](#common-issues) section
- **Community**: Check project repository for issues and discussions

---

**Production Deployment Checklist**: Before going live, ensure all items in [Pre-Deployment Checklist](#pre-deployment-checklist) are complete.

---

*For detailed technical specifications, see [AIL Sprint 2 Complete Summary](AIL_SPRINT_2_COMPLETE.md).*
