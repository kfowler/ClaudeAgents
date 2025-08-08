# Agent Usage Analytics Framework

A comprehensive analytics system for tracking agent effectiveness, optimizing recommendations, and improving user experience in the Claude Code agent ecosystem.

## Overview

This framework provides:

- **Data Collection**: Non-intrusive tracking of agent usage patterns
- **Performance Analytics**: Comprehensive metrics on agent effectiveness and user satisfaction
- **Feedback Systems**: Smart collection of explicit and implicit user feedback
- **Recommendation Engine**: Data-driven agent selection optimization
- **Dashboard Analytics**: Visual insights and reporting capabilities

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent System Integration                     │
├─────────────────────────────────────────────────────────────────┤
│  collector.py          │  feedback.py          │  metrics.py    │
│  Data Collection       │  Feedback Collection   │  Analytics     │
│  ┌─────────────────┐  │  ┌─────────────────┐   │  ┌──────────┐  │
│  │ Session Tracking│  │  │ Smart Prompts   │   │  │ KPI Calc │  │
│  │ Invocation Data │  │  │ Implicit Signals│   │  │ Insights │  │
│  │ Context Analysis│  │  │ User Preferences│   │  │ Trends   │  │
│  └─────────────────┘  │  └─────────────────┘   │  └──────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                     Storage & Processing                         │
│  PostgreSQL + TimescaleDB     │      Redis Cache                │
│  ┌─────────────────────────┐  │  ┌─────────────────────────────┐ │
│  │ • Session Data          │  │  │ • Session Cache             │ │
│  │ • Invocation Metrics    │  │  │ • User Preferences          │ │
│  │ • User Feedback         │  │  │ • Recommendation Cache      │ │
│  │ • Performance Stats     │  │  │ • Real-time Aggregates      │ │
│  └─────────────────────────┘  │  └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                     Analytics & Reporting                        │
│  dashboard.py                              integration_example.py │
│  ┌─────────────────────────────────────┐  ┌────────────────────┐ │
│  │ • Multi-tab Dashboard Configuration │  │ • Easy Integration │ │
│  │ • Real-time Charts & Metrics       │  │ • Context Managers │ │
│  │ • Grafana Export                   │  │ • Production Ready │ │
│  │ • Custom Visualizations           │  │ • Error Handling   │ │
│  └─────────────────────────────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Database Setup

```sql
-- Run the schema creation
psql -d your_database -f analytics/schema.sql
```

### 2. Basic Integration

```python
from analytics.integration_example import AgentAnalyticsManager, AnalyticsContext

# Initialize analytics
analytics = AgentAnalyticsManager(
    db_url="postgresql://user:pass@localhost/db",
    enable_feedback=True
)
await analytics.initialize()

# Use context manager for sessions
async with AnalyticsContext(analytics, "user123", "./project") as session_id:
    # Track agent usage
    inv_id = await analytics.track_agent_invocation(
        session_id, "full-stack-architect", "Build React component"
    )
    
    # Your agent work here...
    
    # Complete tracking
    await analytics.complete_agent_invocation(inv_id, success=True)
```

### 3. Dashboard Setup

```python
from analytics.dashboard import DashboardBuilder, generate_dashboard_config

# Generate dashboard configuration
config = generate_dashboard_config()

# Export for Grafana
with open('grafana_dashboard.json', 'w') as f:
    f.write(config['grafana'])
```

## Core Components

### Data Collection (`collector.py`)

**Features:**
- Session-based tracking with project context detection
- Automatic tech stack identification
- Performance metrics (tokens, duration, quality scores)
- Graceful degradation (local storage fallback)
- Configurable buffering and batch processing

**Key Classes:**
- `AnalyticsCollector`: Main data collection interface
- `ProjectContext`: Automatic project analysis
- `UserRequest`: Standardized request classification

### Feedback Collection (`feedback.py`)

**Features:**
- Non-intrusive feedback prompts with smart timing
- Implicit behavior signal tracking
- User preference learning and adaptation
- Multiple feedback types (ratings, text, choices)
- Pattern detection (corrections, abandonment, success)

**Key Classes:**
- `FeedbackCollector`: Smart feedback orchestration
- `ImplicitTracker`: Behavioral pattern detection
- `FeedbackPrompt`: Configurable feedback strategies

### Analytics Engine (`metrics.py`)

**Features:**
- Agent effectiveness scoring with multiple factors
- User satisfaction trend analysis
- Optimization opportunity detection
- Recommendation engine accuracy metrics
- Comprehensive reporting and insights

**Key Classes:**
- `AnalyticsEngine`: Core metrics calculation
- `RecommendationInsight`: Actionable optimization insights
- Export functions for various report formats

### Dashboard System (`dashboard.py`)

**Features:**
- Multi-tab dashboard with 5 comprehensive views
- Real-time chart configurations
- Grafana export compatibility
- Configurable refresh intervals and filters
- Performance-optimized data providers

**Dashboard Tabs:**
1. **Overview**: High-level KPIs and usage trends
2. **Performance**: Agent effectiveness and duration metrics
3. **Satisfaction**: User feedback and correction patterns
4. **Combinations**: Multi-agent workflow analysis
5. **Issues**: Error analysis and troubleshooting

## Data Schema

The PostgreSQL schema includes:

### Core Tables
- `agent_sessions`: User sessions with project context
- `agent_invocations`: Individual agent usage events
- `user_feedback`: Explicit and implicit feedback
- `agent_combinations`: Multi-agent workflow tracking

### Analytics Tables
- `agent_performance_metrics`: Pre-calculated performance data
- `project_patterns`: Context-based recommendation patterns
- `selection_optimization`: Recommendation engine learning

### Views
- `agent_effectiveness_summary`: Quick performance overview
- `user_satisfaction_trends`: Satisfaction over time
- `optimal_agent_combinations`: Best workflow patterns

## Configuration Options

### Production Setup
```python
config = create_production_config(
    db_url="postgresql://user:pass@host:5432/analytics",
    redis_url="redis://host:6379/1"
)
analytics = AgentAnalyticsManager(**config)
```

### Development Setup
```python
config = create_development_config()  # Uses local storage
analytics = AgentAnalyticsManager(**config)
```

### Minimal Setup
```python
config = create_minimal_config()  # Minimal resources
analytics = AgentAnalyticsManager(**config)
```

## Key Metrics Tracked

### Agent Effectiveness
- Success rate (completed vs failed tasks)
- Quality score (code quality, user satisfaction)
- Context match accuracy (right agent for the task)
- Performance efficiency (time, token usage)

### User Satisfaction
- Explicit ratings (1-5 scale)
- Implicit signals (corrections, abandonment, rapid completion)
- Feedback volume and sentiment
- User preference patterns

### System Performance
- Recommendation engine accuracy
- Agent selection patterns
- Error rates and types
- Usage trends and patterns

## Integration Patterns

### Session Tracking
```python
# Start session with context
session_id = await analytics.start_agent_session(user_id, project_path)

# Track agent work
inv_id = await analytics.track_agent_invocation(session_id, agent_name, request)

# Complete with metrics
await analytics.complete_agent_invocation(inv_id, success, metrics)

# End session
await analytics.end_agent_session(session_id, outcome)
```

### Feedback Collection
```python
# Explicit feedback
await analytics.record_user_feedback(session_id, rating=4, text="Good job")

# Implicit tracking
analytics.track_code_modification(session_id, agent, time_to_modify, extent)
analytics.track_agent_override(session_id, recommended, selected, reason)
```

### Analytics Queries
```python
# Get agent recommendations
recommendations = await analytics.get_agent_recommendations(user_id, request, context)

# Generate insights report
report = await analytics.generate_insights_report()

# Get dashboard data
chart_data = await analytics.get_dashboard_data(chart_id, filters)
```

## Performance Considerations

### Database Optimization
- TimescaleDB for time-series data
- Proper indexing on query patterns
- Materialized views for expensive calculations
- Automated data retention policies

### Caching Strategy
- Redis for session and preference caching
- Query result caching with TTL
- Pre-calculated metric tables
- Intelligent cache invalidation

### Scalability Features
- Asynchronous data collection
- Batch processing and buffering
- Horizontal scaling with read replicas
- Graceful degradation to local storage

## Monitoring and Alerting

### Health Checks
- Database connection monitoring
- Analytics pipeline health
- Feedback collection rates
- Dashboard performance

### Key Alerts
- High error rates by agent
- Declining user satisfaction scores
- Recommendation engine accuracy drops
- Database performance issues

## Deployment

### Database Migration
```bash
# Create database and extensions
createdb claude_analytics
psql -d claude_analytics -c "CREATE EXTENSION timescaledb;"

# Run schema migration
psql -d claude_analytics -f analytics/schema.sql
```

### Application Integration
```python
# In your main application initialization
analytics = AgentAnalyticsManager(
    db_url=os.getenv('ANALYTICS_DB_URL'),
    enable_feedback=True
)
await analytics.initialize()

# Register cleanup
atexit.register(lambda: asyncio.run(analytics.shutdown()))
```

### Dashboard Deployment
```bash
# Export Grafana dashboard
python -c "
from analytics.dashboard import generate_dashboard_config
import json
config = generate_dashboard_config()
print(config['grafana'])
" > grafana_dashboard.json

# Import to Grafana via API
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana_dashboard.json
```

## Privacy and Compliance

### Data Minimization
- Only collect necessary analytics data
- Configurable data retention periods
- Automatic PII scrubbing in requests
- User consent management

### Security
- Encrypted data in transit and at rest
- Role-based access to analytics
- Audit logging for sensitive operations
- GDPR compliance features

## Extending the Framework

### Custom Metrics
```python
# Add custom analytics
class CustomAnalyticsEngine(AnalyticsEngine):
    async def calculate_custom_metric(self):
        # Your custom analytics logic
        pass
```

### Custom Feedback
```python
# Add domain-specific feedback prompts
collector.add_custom_prompt(FeedbackPrompt(
    trigger=FeedbackTrigger.TASK_COMPLETION,
    feedback_type=FeedbackType.CHOICE,
    prompt_text="How was the security analysis?",
    options=["Comprehensive", "Adequate", "Insufficient"],
    context_requirements={'agent_name': 'security-audit-specialist'}
))
```

### Custom Dashboard Charts
```python
# Add custom visualizations
custom_chart = ChartConfiguration(
    id="custom_metric",
    title="My Custom Metric",
    chart_type=ChartType.LINE,
    query="SELECT date, value FROM my_custom_metrics WHERE date >= NOW() - INTERVAL '{{time_range}}'",
    refresh_interval=60
)
```

This analytics framework provides a solid foundation for understanding and optimizing agent performance while maintaining user privacy and system performance.