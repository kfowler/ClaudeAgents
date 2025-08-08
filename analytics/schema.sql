-- Agent Usage Analytics Database Schema
-- PostgreSQL 16+ with extensions for analytics and JSON processing

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Core tracking tables
CREATE TABLE agent_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    project_context JSONB NOT NULL, -- tech stack, files, complexity
    session_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_end TIMESTAMPTZ,
    total_duration_seconds INTEGER,
    final_outcome VARCHAR(50), -- completed, abandoned, error, timeout
    user_satisfaction_score INTEGER CHECK (user_satisfaction_score BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('agent_sessions', 'created_at', if_not_exists => true);

CREATE TABLE agent_invocations (
    invocation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    invocation_reason VARCHAR(50), -- automatic, user_selected, recommended, fallback
    user_request TEXT NOT NULL,
    context_match_score REAL CHECK (context_match_score BETWEEN 0 AND 1),
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    tokens_used INTEGER,
    success_status VARCHAR(20), -- success, partial, failed, cancelled
    error_type VARCHAR(50),
    error_message TEXT,
    files_modified INTEGER DEFAULT 0,
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    quality_score REAL CHECK (quality_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('agent_invocations', 'created_at', if_not_exists => true);

-- Index for efficient queries
CREATE INDEX idx_agent_invocations_session_agent ON agent_invocations(session_id, agent_name);
CREATE INDEX idx_agent_invocations_agent_time ON agent_invocations(agent_name, created_at);
CREATE INDEX idx_agent_invocations_success ON agent_invocations(agent_name, success_status);

CREATE TABLE agent_combinations (
    combination_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    primary_agent VARCHAR(100) NOT NULL,
    secondary_agents TEXT[], -- array of agent names
    combination_pattern VARCHAR(200), -- sequential, parallel, handoff, review
    combination_success BOOLEAN,
    synergy_score REAL CHECK (synergy_score BETWEEN 0 AND 1),
    total_duration_seconds INTEGER,
    user_intervention_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_combinations_pattern ON agent_combinations(combination_pattern, combination_success);
CREATE INDEX idx_agent_combinations_primary ON agent_combinations(primary_agent, created_at);

CREATE TABLE task_classifications (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invocation_id UUID NOT NULL REFERENCES agent_invocations(invocation_id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL, -- implementation, review, debugging, optimization, etc.
    complexity_level VARCHAR(20), -- simple, medium, complex, enterprise
    domain VARCHAR(50), -- web, mobile, ai_ml, security, devops, data
    tech_stack TEXT[], -- array of technologies detected
    risk_level VARCHAR(20), -- low, medium, high, critical
    business_impact VARCHAR(20), -- prototype, internal, production, customer_facing
    success_metrics JSONB, -- custom metrics per task type
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_task_classifications_type_domain ON task_classifications(task_type, domain);
CREATE INDEX idx_task_classifications_complexity ON task_classifications(complexity_level, risk_level);

-- User feedback and preferences
CREATE TABLE user_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES agent_sessions(session_id) ON DELETE CASCADE,
    invocation_id UUID REFERENCES agent_invocations(invocation_id) ON DELETE CASCADE,
    feedback_type VARCHAR(50), -- explicit_rating, implicit_behavior, correction, suggestion
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    suggested_agent VARCHAR(100),
    user_correction JSONB, -- what the user changed/fixed
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_feedback_type_time ON user_feedback(feedback_type, timestamp);

CREATE TABLE user_preferences (
    user_id VARCHAR(255) PRIMARY KEY,
    preferred_agents TEXT[], -- agents user explicitly prefers
    avoided_agents TEXT[], -- agents user tends to reject
    workflow_preferences JSONB, -- progressive, all_at_once, manual_selection
    risk_tolerance VARCHAR(20), -- conservative, balanced, aggressive
    expertise_level VARCHAR(20), -- beginner, intermediate, expert
    notification_preferences JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent performance metrics (materialized for fast access)
CREATE TABLE agent_performance_metrics (
    agent_name VARCHAR(100) NOT NULL,
    time_period VARCHAR(20) NOT NULL, -- daily, weekly, monthly
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Usage metrics
    total_invocations INTEGER NOT NULL DEFAULT 0,
    successful_invocations INTEGER NOT NULL DEFAULT 0,
    failed_invocations INTEGER NOT NULL DEFAULT 0,
    average_duration_seconds REAL,
    median_duration_seconds REAL,
    
    -- Quality metrics
    average_quality_score REAL,
    average_user_satisfaction REAL,
    code_quality_improvement REAL,
    defect_introduction_rate REAL,
    
    -- Context metrics
    context_match_accuracy REAL,
    recommendation_acceptance_rate REAL,
    user_correction_frequency REAL,
    
    -- Efficiency metrics
    lines_per_hour REAL,
    tokens_efficiency REAL,
    task_completion_rate REAL,
    
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (agent_name, time_period, period_start)
);

CREATE INDEX idx_agent_performance_time ON agent_performance_metrics(time_period, period_start);

-- Project context patterns for recommendation engine
CREATE TABLE project_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tech_stack_signature TEXT NOT NULL, -- hash of sorted tech stack
    project_characteristics JSONB NOT NULL, -- size, complexity, domain
    successful_agent_combinations JSONB NOT NULL, -- [{"agents": [], "success_rate": 0.95}]
    common_failure_modes JSONB,
    recommendation_confidence REAL CHECK (recommendation_confidence BETWEEN 0 AND 1),
    sample_size INTEGER NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_project_patterns_stack ON project_patterns(tech_stack_signature);

-- Real-time agent selection optimization
CREATE TABLE selection_optimization (
    optimization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    selection_context JSONB NOT NULL, -- user request, project context
    recommended_agents TEXT[] NOT NULL,
    actual_selection TEXT[] NOT NULL,
    selection_rationale JSONB,
    outcome_success BOOLEAN,
    learning_weight REAL DEFAULT 1.0, -- higher weight for more recent/reliable data
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_selection_optimization_time ON selection_optimization(created_at);
CREATE INDEX idx_selection_optimization_success ON selection_optimization(outcome_success, learning_weight);

-- Triggers for automatic metric computation
CREATE OR REPLACE FUNCTION update_agent_performance_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update daily metrics when an invocation completes
    INSERT INTO agent_performance_metrics (
        agent_name, 
        time_period, 
        period_start, 
        period_end,
        total_invocations,
        successful_invocations,
        failed_invocations,
        average_duration_seconds,
        average_quality_score
    )
    SELECT 
        NEW.agent_name,
        'daily',
        date_trunc('day', NEW.created_at),
        date_trunc('day', NEW.created_at) + interval '1 day',
        COUNT(*),
        SUM(CASE WHEN success_status = 'success' THEN 1 ELSE 0 END),
        SUM(CASE WHEN success_status = 'failed' THEN 1 ELSE 0 END),
        AVG(duration_seconds),
        AVG(quality_score)
    FROM agent_invocations 
    WHERE agent_name = NEW.agent_name 
    AND created_at >= date_trunc('day', NEW.created_at)
    AND created_at < date_trunc('day', NEW.created_at) + interval '1 day'
    GROUP BY agent_name
    ON CONFLICT (agent_name, time_period, period_start) 
    DO UPDATE SET
        total_invocations = EXCLUDED.total_invocations,
        successful_invocations = EXCLUDED.successful_invocations,
        failed_invocations = EXCLUDED.failed_invocations,
        average_duration_seconds = EXCLUDED.average_duration_seconds,
        average_quality_score = EXCLUDED.average_quality_score,
        computed_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER agent_invocation_metrics_update
    AFTER UPDATE OF end_time ON agent_invocations
    FOR EACH ROW
    WHEN (NEW.end_time IS NOT NULL AND OLD.end_time IS NULL)
    EXECUTE FUNCTION update_agent_performance_metrics();

-- Views for common analytics queries
CREATE VIEW agent_effectiveness_summary AS
SELECT 
    agent_name,
    COUNT(*) as total_uses,
    AVG(CASE WHEN success_status = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(duration_seconds) as avg_duration,
    AVG(quality_score) as avg_quality,
    AVG(context_match_score) as avg_context_match,
    COUNT(DISTINCT session_id) as unique_sessions,
    MAX(created_at) as last_used
FROM agent_invocations 
WHERE created_at >= NOW() - interval '30 days'
GROUP BY agent_name
ORDER BY success_rate DESC, total_uses DESC;

CREATE VIEW user_satisfaction_trends AS
SELECT 
    date_trunc('day', uf.timestamp) as day,
    ai.agent_name,
    AVG(uf.rating) as avg_rating,
    COUNT(*) as feedback_count,
    AVG(CASE WHEN uf.user_correction IS NOT NULL THEN 1.0 ELSE 0.0 END) as correction_rate
FROM user_feedback uf
JOIN agent_invocations ai ON uf.invocation_id = ai.invocation_id
WHERE uf.timestamp >= NOW() - interval '90 days'
GROUP BY date_trunc('day', uf.timestamp), ai.agent_name
ORDER BY day DESC, avg_rating DESC;

CREATE VIEW optimal_agent_combinations AS
SELECT 
    primary_agent,
    secondary_agents,
    combination_pattern,
    COUNT(*) as usage_count,
    AVG(CASE WHEN combination_success THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(synergy_score) as avg_synergy,
    AVG(total_duration_seconds) as avg_duration
FROM agent_combinations
WHERE created_at >= NOW() - interval '60 days'
GROUP BY primary_agent, secondary_agents, combination_pattern
HAVING COUNT(*) >= 3
ORDER BY success_rate DESC, avg_synergy DESC;