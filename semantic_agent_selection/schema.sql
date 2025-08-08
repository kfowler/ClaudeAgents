-- Semantic Agent Selection Database Schema
-- PostgreSQL with pgvector extension for vector similarity search

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Agent capability embeddings table
CREATE TABLE agent_embeddings (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    capability_vector VECTOR(384), -- Sentence Transformer embedding dimension
    metadata JSONB NOT NULL DEFAULT '{}',
    content_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(agent_name, embedding_model)
);

-- Indexes for agent embeddings
CREATE INDEX idx_agent_embeddings_name ON agent_embeddings(agent_name);
CREATE INDEX idx_agent_embeddings_model ON agent_embeddings(embedding_model);
CREATE INDEX idx_agent_embeddings_vector ON agent_embeddings USING ivfflat (capability_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_agent_embeddings_metadata ON agent_embeddings USING GIN (metadata);

-- Request analysis table
CREATE TABLE request_analysis (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL DEFAULT uuid_generate_v4(),
    request_text TEXT NOT NULL,
    request_embedding VECTOR(384),
    extracted_context JSONB,
    complexity_score FLOAT,
    risk_level VARCHAR(20),
    intent_classification VARCHAR(50),
    technical_keywords TEXT[],
    domain_keywords TEXT[],
    confidence_score FLOAT,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (complexity_score >= 0 AND complexity_score <= 4),
    CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for request analysis
CREATE INDEX idx_request_analysis_session ON request_analysis(session_id);
CREATE INDEX idx_request_analysis_intent ON request_analysis(intent_classification);
CREATE INDEX idx_request_analysis_risk ON request_analysis(risk_level);
CREATE INDEX idx_request_analysis_embedding ON request_analysis USING ivfflat (request_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_request_analysis_created_at ON request_analysis(created_at);

-- Convert to hypertable for time-series data
SELECT create_hypertable('request_analysis', 'created_at', chunk_time_interval => INTERVAL '1 month');

-- Semantic matching results table
CREATE TABLE semantic_matches (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES request_analysis(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    similarity_score FLOAT NOT NULL,
    context_score FLOAT,
    success_probability FLOAT,
    confidence_score FLOAT,
    explanation_factors JSONB,
    ranking INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (similarity_score >= 0 AND similarity_score <= 1),
    CHECK (context_score >= 0 AND context_score <= 1),
    CHECK (success_probability >= 0 AND success_probability <= 1),
    CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for semantic matches
CREATE INDEX idx_semantic_matches_request ON semantic_matches(request_id);
CREATE INDEX idx_semantic_matches_agent ON semantic_matches(agent_name);
CREATE INDEX idx_semantic_matches_similarity ON semantic_matches(similarity_score DESC);
CREATE INDEX idx_semantic_matches_success ON semantic_matches(success_probability DESC);

-- Agent combination patterns table
CREATE TABLE agent_combinations (
    id SERIAL PRIMARY KEY,
    combination_hash VARCHAR(64) UNIQUE NOT NULL, -- Hash of sorted agent names
    agents TEXT[] NOT NULL, -- Array of agent names
    success_rate FLOAT NOT NULL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 1,
    context_patterns JSONB NOT NULL DEFAULT '{}',
    average_duration INTERVAL,
    confidence_score FLOAT,
    last_used TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (success_rate >= 0 AND success_rate <= 1),
    CHECK (usage_count >= 0),
    CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for agent combinations
CREATE INDEX idx_agent_combinations_hash ON agent_combinations(combination_hash);
CREATE INDEX idx_agent_combinations_success ON agent_combinations(success_rate DESC);
CREATE INDEX idx_agent_combinations_usage ON agent_combinations(usage_count DESC);
CREATE INDEX idx_agent_combinations_last_used ON agent_combinations(last_used DESC);
CREATE INDEX idx_agent_combinations_context ON agent_combinations USING GIN (context_patterns);

-- Selection feedback table
CREATE TABLE selection_feedback (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    request_id INTEGER REFERENCES request_analysis(id) ON DELETE SET NULL,
    recommended_agents TEXT[] NOT NULL,
    selected_agents TEXT[],
    user_satisfaction_score INTEGER,
    task_success BOOLEAN,
    feedback_text TEXT,
    implicit_signals JSONB DEFAULT '{}',
    selection_strategy VARCHAR(50),
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (user_satisfaction_score >= 1 AND user_satisfaction_score <= 5)
);

-- Indexes for selection feedback
CREATE INDEX idx_selection_feedback_session ON selection_feedback(session_id);
CREATE INDEX idx_selection_feedback_request ON selection_feedback(request_id);
CREATE INDEX idx_selection_feedback_satisfaction ON selection_feedback(user_satisfaction_score);
CREATE INDEX idx_selection_feedback_success ON selection_feedback(task_success);
CREATE INDEX idx_selection_feedback_strategy ON selection_feedback(selection_strategy);
CREATE INDEX idx_selection_feedback_created_at ON selection_feedback(created_at);

-- Convert to hypertable
SELECT create_hypertable('selection_feedback', 'created_at', chunk_time_interval => INTERVAL '1 month');

-- Agent performance metrics table
CREATE TABLE agent_performance_semantic (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    context_type VARCHAR(50),
    semantic_score_range VARCHAR(20), -- e.g., "0.8-0.9"
    success_rate FLOAT NOT NULL,
    avg_user_satisfaction FLOAT,
    avg_confidence_score FLOAT,
    sample_size INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (success_rate >= 0 AND success_rate <= 1),
    CHECK (avg_user_satisfaction >= 1 AND avg_user_satisfaction <= 5),
    CHECK (avg_confidence_score >= 0 AND avg_confidence_score <= 1),
    CHECK (sample_size >= 0),
    
    -- Unique constraint
    UNIQUE(agent_name, context_type, semantic_score_range)
);

-- Indexes for agent performance
CREATE INDEX idx_agent_performance_name ON agent_performance_semantic(agent_name);
CREATE INDEX idx_agent_performance_context ON agent_performance_semantic(context_type);
CREATE INDEX idx_agent_performance_success ON agent_performance_semantic(success_rate DESC);
CREATE INDEX idx_agent_performance_satisfaction ON agent_performance_semantic(avg_user_satisfaction DESC);

-- ML model performance tracking table
CREATE TABLE model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    performance_metrics JSONB NOT NULL,
    training_samples INTEGER,
    validation_accuracy FLOAT,
    feature_importance JSONB,
    training_date TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (validation_accuracy >= 0 AND validation_accuracy <= 1)
);

-- Indexes for model performance
CREATE INDEX idx_model_performance_name ON model_performance(model_name);
CREATE INDEX idx_model_performance_version ON model_performance(model_version);
CREATE INDEX idx_model_performance_accuracy ON model_performance(validation_accuracy DESC);
CREATE INDEX idx_model_performance_date ON model_performance(training_date DESC);

-- Agent invocations tracking (for ML training data)
CREATE TABLE agent_invocations (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    request_id INTEGER REFERENCES request_analysis(id) ON DELETE SET NULL,
    agent_name VARCHAR(100) NOT NULL,
    invocation_type VARCHAR(50), -- 'primary', 'supporting', 'validator'
    start_time TIMESTAMP DEFAULT NOW(),
    completion_time TIMESTAMP,
    success BOOLEAN,
    user_satisfaction_score INTEGER,
    output_quality_score FLOAT,
    processing_metrics JSONB DEFAULT '{}',
    
    -- Constraints
    CHECK (user_satisfaction_score >= 1 AND user_satisfaction_score <= 5),
    CHECK (output_quality_score >= 0 AND output_quality_score <= 1)
);

-- Indexes for agent invocations
CREATE INDEX idx_agent_invocations_session ON agent_invocations(session_id);
CREATE INDEX idx_agent_invocations_request ON agent_invocations(request_id);
CREATE INDEX idx_agent_invocations_agent ON agent_invocations(agent_name);
CREATE INDEX idx_agent_invocations_success ON agent_invocations(success);
CREATE INDEX idx_agent_invocations_start_time ON agent_invocations(start_time);

-- Convert to hypertable
SELECT create_hypertable('agent_invocations', 'start_time', chunk_time_interval => INTERVAL '1 month');

-- Project context cache table
CREATE TABLE project_context_cache (
    id SERIAL PRIMARY KEY,
    project_path_hash VARCHAR(64) UNIQUE NOT NULL,
    project_path TEXT NOT NULL,
    context_data JSONB NOT NULL,
    technologies TEXT[],
    frameworks TEXT[],
    languages TEXT[],
    last_analyzed TIMESTAMP DEFAULT NOW(),
    cache_expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours'),
    
    -- Index on expiration for cleanup
    CHECK (cache_expires_at > last_analyzed)
);

-- Indexes for project context cache
CREATE INDEX idx_project_context_hash ON project_context_cache(project_path_hash);
CREATE INDEX idx_project_context_expires ON project_context_cache(cache_expires_at);
CREATE INDEX idx_project_context_technologies ON project_context_cache USING GIN (technologies);
CREATE INDEX idx_project_context_frameworks ON project_context_cache USING GIN (frameworks);

-- System metrics table for monitoring
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Index for system metrics
CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- Convert to hypertable
SELECT create_hypertable('system_metrics', 'timestamp', chunk_time_interval => INTERVAL '1 hour');

-- Materialized views for performance
CREATE MATERIALIZED VIEW agent_effectiveness_summary AS
SELECT 
    agent_name,
    COUNT(*) as total_invocations,
    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
    AVG(user_satisfaction_score) as avg_satisfaction,
    AVG(output_quality_score) as avg_quality,
    AVG(EXTRACT(EPOCH FROM (completion_time - start_time))) as avg_duration_seconds,
    COUNT(DISTINCT session_id) as unique_sessions
FROM agent_invocations 
WHERE completion_time IS NOT NULL 
    AND start_time >= NOW() - INTERVAL '30 days'
GROUP BY agent_name;

-- Index on materialized view
CREATE INDEX idx_agent_effectiveness_success_rate ON agent_effectiveness_summary(success_rate DESC);
CREATE INDEX idx_agent_effectiveness_satisfaction ON agent_effectiveness_summary(avg_satisfaction DESC);

-- Materialized view for user satisfaction trends
CREATE MATERIALIZED VIEW user_satisfaction_trends AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    selection_strategy,
    AVG(user_satisfaction_score) as avg_satisfaction,
    COUNT(*) as total_responses,
    AVG(CASE WHEN task_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM selection_feedback 
WHERE created_at >= NOW() - INTERVAL '90 days'
    AND user_satisfaction_score IS NOT NULL
GROUP BY DATE_TRUNC('day', created_at), selection_strategy
ORDER BY date DESC;

-- Materialized view for optimal agent combinations
CREATE MATERIALIZED VIEW optimal_agent_combinations AS
SELECT 
    agents,
    success_rate,
    usage_count,
    confidence_score,
    context_patterns,
    EXTRACT(EPOCH FROM average_duration) as avg_duration_seconds,
    last_used
FROM agent_combinations 
WHERE usage_count >= 5 
    AND success_rate >= 0.7
ORDER BY success_rate DESC, usage_count DESC;

-- Functions for analytics
CREATE OR REPLACE FUNCTION calculate_agent_performance(
    p_agent_name VARCHAR(100),
    p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE(
    success_rate FLOAT,
    avg_satisfaction FLOAT,
    total_invocations BIGINT,
    avg_duration_seconds FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(CASE WHEN ai.success THEN 1.0 ELSE 0.0 END)::FLOAT as success_rate,
        AVG(ai.user_satisfaction_score)::FLOAT as avg_satisfaction,
        COUNT(*)::BIGINT as total_invocations,
        AVG(EXTRACT(EPOCH FROM (ai.completion_time - ai.start_time)))::FLOAT as avg_duration_seconds
    FROM agent_invocations ai
    WHERE ai.agent_name = p_agent_name
        AND ai.start_time >= NOW() - (p_days_back || ' days')::INTERVAL
        AND ai.completion_time IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to get similar requests
CREATE OR REPLACE FUNCTION find_similar_requests(
    p_embedding VECTOR(384),
    p_threshold FLOAT DEFAULT 0.7,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE(
    id INTEGER,
    request_text TEXT,
    similarity FLOAT,
    intent_classification VARCHAR(50),
    complexity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ra.id,
        ra.request_text,
        (1 - (ra.request_embedding <=> p_embedding))::FLOAT as similarity,
        ra.intent_classification,
        ra.complexity_score
    FROM request_analysis ra
    WHERE ra.request_embedding IS NOT NULL
        AND (1 - (ra.request_embedding <=> p_embedding)) >= p_threshold
    ORDER BY ra.request_embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to update agent combination patterns
CREATE OR REPLACE FUNCTION update_agent_combination(
    p_agents TEXT[],
    p_success BOOLEAN,
    p_duration INTERVAL DEFAULT NULL,
    p_context JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
DECLARE
    v_sorted_agents TEXT[];
    v_hash VARCHAR(64);
BEGIN
    -- Sort agents for consistent hashing
    SELECT array_agg(agent ORDER BY agent) INTO v_sorted_agents
    FROM unnest(p_agents) AS agent;
    
    -- Create hash
    v_hash := encode(digest(array_to_string(v_sorted_agents, ','), 'sha256'), 'hex');
    
    -- Insert or update
    INSERT INTO agent_combinations (combination_hash, agents, success_rate, usage_count, context_patterns, average_duration, last_used)
    VALUES (v_hash, v_sorted_agents, CASE WHEN p_success THEN 1.0 ELSE 0.0 END, 1, p_context, p_duration, NOW())
    ON CONFLICT (combination_hash)
    DO UPDATE SET
        success_rate = (
            (agent_combinations.success_rate * agent_combinations.usage_count + 
             CASE WHEN p_success THEN 1.0 ELSE 0.0 END) / 
            (agent_combinations.usage_count + 1)
        ),
        usage_count = agent_combinations.usage_count + 1,
        average_duration = CASE 
            WHEN p_duration IS NOT NULL THEN (
                (COALESCE(agent_combinations.average_duration, INTERVAL '0') * agent_combinations.usage_count + p_duration) /
                (agent_combinations.usage_count + 1)
            )
            ELSE agent_combinations.average_duration
        END,
        context_patterns = agent_combinations.context_patterns || p_context,
        last_used = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW agent_effectiveness_summary;
    REFRESH MATERIALIZED VIEW user_satisfaction_trends;
    REFRESH MATERIALIZED VIEW optimal_agent_combinations;
END;
$$ LANGUAGE plpgsql;

-- Data retention policies
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS VOID AS $$
BEGIN
    -- Clean up old request analysis (keep 6 months)
    DELETE FROM request_analysis 
    WHERE created_at < NOW() - INTERVAL '6 months';
    
    -- Clean up old agent invocations (keep 6 months)
    DELETE FROM agent_invocations 
    WHERE start_time < NOW() - INTERVAL '6 months';
    
    -- Clean up old selection feedback (keep 1 year)
    DELETE FROM selection_feedback 
    WHERE created_at < NOW() - INTERVAL '1 year';
    
    -- Clean up expired project context cache
    DELETE FROM project_context_cache 
    WHERE cache_expires_at < NOW();
    
    -- Clean up old system metrics (keep 3 months)
    DELETE FROM system_metrics 
    WHERE timestamp < NOW() - INTERVAL '3 months';
    
    -- Update usage count and success rate for low-usage combinations
    DELETE FROM agent_combinations 
    WHERE usage_count < 3 
        AND last_used < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic updates
CREATE OR REPLACE FUNCTION update_agent_embedding_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER agent_embeddings_update_trigger
    BEFORE UPDATE ON agent_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_embedding_timestamp();

-- Scheduled jobs (using pg_cron if available)
-- SELECT cron.schedule('refresh-analytics', '*/30 * * * *', 'SELECT refresh_analytics_views()');
-- SELECT cron.schedule('cleanup-data', '0 2 * * *', 'SELECT cleanup_old_data()');

-- Insert some initial system configuration
INSERT INTO system_metrics (metric_name, metric_value, metric_unit, tags) VALUES
('system_initialized', 1, 'boolean', '{"version": "1.0", "schema_version": "1.0"}'),
('embedding_dimension', 384, 'dimensions', '{"model": "all-MiniLM-L6-v2"}'),
('default_similarity_threshold', 0.7, 'score', '{"type": "cosine_similarity"}');

-- Create default agent tier mappings (if needed for quick lookups)
CREATE TABLE agent_tier_mapping (
    agent_name VARCHAR(100) PRIMARY KEY,
    tier INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),
    category VARCHAR(50),
    description TEXT
);

INSERT INTO agent_tier_mapping (agent_name, tier, category, description) VALUES
-- Tier 1 (Core agents)
('full-stack-architect', 1, 'development', 'Modern web applications'),
('mobile-developer', 1, 'development', 'iOS/Android development'),
('project-orchestrator', 1, 'coordination', 'Complex project coordination'),
('security-audit-specialist', 1, 'quality', 'Security reviews'),
('qa-test-engineer', 1, 'quality', 'Testing and QA'),

-- Tier 2 (Specialized agents)
('ai-ml-engineer', 2, 'specialized', 'AI/ML integration'),
('data-engineer', 2, 'specialized', 'Data pipelines and analytics'),
('devops-engineer', 2, 'specialized', 'Infrastructure and deployment'),
('systems-engineer', 2, 'specialized', 'Performance and systems'),
('code-architect', 2, 'quality', 'Code architecture and review'),
('accessibility-expert', 2, 'quality', 'Accessibility compliance'),
('the-critic', 2, 'analysis', 'Technical decision analysis'),
('product-strategist', 2, 'strategy', 'Product planning and validation'),
('legacy-specialist', 2, 'specialized', 'Legacy system modernization'),
('platform-integrator', 2, 'specialized', 'Third-party integrations'),

-- Tier 3 (Niche/creative agents)
('functional-programmer', 3, 'niche', 'Functional programming'),
('metaprogramming-specialist', 3, 'niche', 'Metaprogramming and DSLs'),
('elisp-specialist', 3, 'niche', 'Emacs Lisp development'),
('artist', 3, 'creative', 'Visual design and art'),
('writer', 3, 'creative', 'Content and documentation'),
('ava-the-director', 3, 'creative', 'Video and multimedia'),
('iris-the-modeler', 3, 'creative', '3D modeling and visualization'),
('milo-the-comic', 3, 'creative', 'Comics and illustration'),
('echo-the-audio-engineer', 3, 'creative', 'Audio and sound');

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO semantic_agent_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO semantic_agent_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO semantic_agent_user;

-- Final schema validation
DO $$
BEGIN
    -- Verify vector extension
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'pgvector extension not found. Install with: CREATE EXTENSION vector;';
    END IF;
    
    -- Verify TimescaleDB (optional)
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        RAISE NOTICE 'TimescaleDB detected - using hypertables for time-series data';
    ELSE
        RAISE NOTICE 'TimescaleDB not detected - using regular tables';
    END IF;
    
    RAISE NOTICE 'Semantic agent selection schema created successfully';
END $$;