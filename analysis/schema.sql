-- Project Context Analysis Database Schema
-- Supports caching and performance optimization for project analysis

-- Main project analysis cache table
CREATE TABLE IF NOT EXISTS project_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL UNIQUE,
    path_hash TEXT NOT NULL,
    analysis_data TEXT NOT NULL,  -- JSON serialized ProjectContext
    timestamp TEXT NOT NULL,
    analysis_version TEXT NOT NULL DEFAULT '1.0.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_project_path ON project_analysis (project_path);
CREATE INDEX IF NOT EXISTS idx_path_hash ON project_analysis (path_hash);
CREATE INDEX IF NOT EXISTS idx_timestamp ON project_analysis (timestamp);
CREATE INDEX IF NOT EXISTS idx_updated_at ON project_analysis (updated_at);

-- Agent recommendations cache table
CREATE TABLE IF NOT EXISTS agent_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_analysis_id INTEGER NOT NULL,
    user_request TEXT,  -- Optional user request that influenced recommendations
    user_request_hash TEXT,  -- Hash of user request for cache invalidation
    recommendation_data TEXT NOT NULL,  -- JSON serialized AgentRecommendation
    risk_level TEXT NOT NULL,
    estimated_complexity TEXT NOT NULL,
    orchestration_pattern TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_analysis_id) REFERENCES project_analysis (id) ON DELETE CASCADE
);

-- Index for agent recommendations lookups
CREATE INDEX IF NOT EXISTS idx_recommendations_project ON agent_recommendations (project_analysis_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_request_hash ON agent_recommendations (user_request_hash);
CREATE INDEX IF NOT EXISTS idx_recommendations_timestamp ON agent_recommendations (timestamp);

-- Technology stack detection patterns cache
-- Stores commonly detected patterns for faster future analysis
CREATE TABLE IF NOT EXISTS tech_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,  -- 'language', 'framework', 'database', etc.
    pattern_name TEXT NOT NULL,
    file_patterns TEXT NOT NULL,  -- JSON array of file patterns
    content_patterns TEXT,  -- JSON array of content regex patterns
    confidence_weight REAL DEFAULT 1.0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for tech patterns
CREATE INDEX IF NOT EXISTS idx_tech_patterns_type ON tech_patterns (pattern_type);
CREATE INDEX IF NOT EXISTS idx_tech_patterns_name ON tech_patterns (pattern_name);

-- Agent scoring rules cache
-- Stores agent scoring rules for consistent recommendations
CREATE TABLE IF NOT EXISTS agent_scoring_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    tier INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),
    rule_type TEXT NOT NULL,  -- 'keyword', 'technology', 'architecture', etc.
    rule_pattern TEXT NOT NULL,
    score_weight REAL NOT NULL DEFAULT 1.0,
    is_required_condition BOOLEAN DEFAULT FALSE,
    description TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for agent scoring rules
CREATE INDEX IF NOT EXISTS idx_agent_rules_name ON agent_scoring_rules (agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_rules_tier ON agent_scoring_rules (tier);
CREATE INDEX IF NOT EXISTS idx_agent_rules_type ON agent_scoring_rules (rule_type);

-- Performance analytics table
-- Tracks analysis performance and accuracy metrics
CREATE TABLE IF NOT EXISTS performance_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL,
    analysis_duration_ms INTEGER NOT NULL,
    cache_hit BOOLEAN DEFAULT FALSE,
    file_count INTEGER,
    line_count INTEGER,
    tech_stack_accuracy REAL,  -- User feedback on accuracy (0-1)
    recommendation_accuracy REAL,  -- User feedback on recommendations (0-1)
    user_feedback TEXT,  -- Optional user feedback
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance analytics
CREATE INDEX IF NOT EXISTS idx_perf_project_path ON performance_analytics (project_path);
CREATE INDEX IF NOT EXISTS idx_perf_created_at ON performance_analytics (created_at);
CREATE INDEX IF NOT EXISTS idx_perf_cache_hit ON performance_analytics (cache_hit);

-- User preferences table
-- Stores user preferences for agent recommendations
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,  -- Optional user identifier
    project_pattern TEXT,  -- Project path pattern or glob
    preferred_agents TEXT,  -- JSON array of preferred agent names
    excluded_agents TEXT,  -- JSON array of excluded agent names
    default_tier_visibility INTEGER DEFAULT 2,  -- Show Tier 1 and 2 by default
    risk_tolerance TEXT DEFAULT 'medium',  -- low, medium, high, critical
    complexity_preference TEXT DEFAULT 'auto',  -- simple, medium, high, auto
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for user preferences
CREATE INDEX IF NOT EXISTS idx_user_prefs_user_id ON user_preferences (user_id);
CREATE INDEX IF NOT EXISTS idx_user_prefs_project_pattern ON user_preferences (project_pattern);

-- File type analysis cache
-- Caches file type detection results for performance
CREATE TABLE IF NOT EXISTS file_type_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_extension TEXT NOT NULL,
    file_name TEXT,  -- For specific filename patterns
    detected_language TEXT,
    detected_framework TEXT,
    confidence_score REAL NOT NULL,
    pattern_source TEXT,  -- Source of the detection pattern
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for file type cache
CREATE INDEX IF NOT EXISTS idx_file_type_ext ON file_type_cache (file_extension);
CREATE INDEX IF NOT EXISTS idx_file_type_name ON file_type_cache (file_name);

-- Analysis history table
-- Tracks changes in project analysis over time
CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL,
    analysis_data TEXT NOT NULL,  -- JSON diff or snapshot
    change_summary TEXT,  -- Human readable summary of changes
    previous_analysis_id INTEGER,  -- Reference to previous analysis
    timestamp TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (previous_analysis_id) REFERENCES project_analysis (id)
);

-- Index for analysis history
CREATE INDEX IF NOT EXISTS idx_history_project_path ON analysis_history (project_path);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON analysis_history (timestamp);

-- Views for common queries

-- Current project analysis with latest recommendations
CREATE VIEW IF NOT EXISTS current_project_state AS
SELECT 
    pa.project_path,
    pa.analysis_data,
    pa.timestamp as analysis_timestamp,
    ar.recommendation_data,
    ar.risk_level,
    ar.estimated_complexity,
    ar.orchestration_pattern,
    ar.timestamp as recommendation_timestamp
FROM project_analysis pa
LEFT JOIN agent_recommendations ar ON pa.id = ar.project_analysis_id
WHERE ar.id = (
    SELECT MAX(id) FROM agent_recommendations ar2 
    WHERE ar2.project_analysis_id = pa.id
) OR ar.id IS NULL;

-- Agent usage statistics
CREATE VIEW IF NOT EXISTS agent_usage_stats AS
SELECT 
    json_extract(value, '$') as agent_name,
    COUNT(*) as recommendation_count,
    AVG(json_extract(value, '$.score')) as avg_score,
    MAX(json_extract(value, '$.score')) as max_score,
    COUNT(CASE WHEN json_extract(value, '$.required') = 1 THEN 1 END) as required_count
FROM agent_recommendations ar,
     json_each(json_extract(ar.recommendation_data, '$.primary_agents')) 
WHERE json_valid(ar.recommendation_data)
GROUP BY json_extract(value, '$')
UNION ALL
SELECT 
    json_extract(value, '$') as agent_name,
    COUNT(*) as recommendation_count,
    AVG(json_extract(value, '$.score')) as avg_score,
    MAX(json_extract(value, '$.score')) as max_score,
    0 as required_count
FROM agent_recommendations ar,
     json_each(json_extract(ar.recommendation_data, '$.context_agents'))
WHERE json_valid(ar.recommendation_data)
GROUP BY json_extract(value, '$');

-- Technology stack trends
CREATE VIEW IF NOT EXISTS tech_stack_trends AS
SELECT 
    json_extract(lang.value, '$') as technology,
    'language' as tech_type,
    COUNT(*) as usage_count,
    AVG(CAST(json_extract(lang.value, '$') as REAL)) as avg_confidence,
    DATE(pa.created_at) as analysis_date
FROM project_analysis pa,
     json_each(json_extract(pa.analysis_data, '$.tech_stack.languages')) lang
WHERE json_valid(pa.analysis_data)
GROUP BY json_extract(lang.value, '$'), DATE(pa.created_at)
UNION ALL
SELECT 
    json_extract(fw.value, '$') as technology,
    'framework' as tech_type,
    COUNT(*) as usage_count,
    AVG(CAST(json_extract(fw.value, '$') as REAL)) as avg_confidence,
    DATE(pa.created_at) as analysis_date
FROM project_analysis pa,
     json_each(json_extract(pa.analysis_data, '$.tech_stack.frameworks')) fw
WHERE json_valid(pa.analysis_data)
GROUP BY json_extract(fw.value, '$'), DATE(pa.created_at);

-- Cache cleanup procedures (implemented as comments for reference)
-- These would be implemented in Python as maintenance procedures

/*
-- Cleanup old cache entries (older than 30 days)
DELETE FROM project_analysis 
WHERE datetime(created_at) < datetime('now', '-30 days');

-- Cleanup orphaned agent recommendations
DELETE FROM agent_recommendations 
WHERE project_analysis_id NOT IN (SELECT id FROM project_analysis);

-- Cleanup old performance analytics (older than 90 days)
DELETE FROM performance_analytics 
WHERE datetime(created_at) < datetime('now', '-90 days');

-- Update analysis cache hit statistics
UPDATE performance_analytics 
SET cache_hit = TRUE 
WHERE id IN (
    SELECT pa_id FROM (
        SELECT 
            perf.id as pa_id,
            COUNT(*) as analysis_count
        FROM performance_analytics perf
        JOIN project_analysis pa ON perf.project_path = pa.project_path
        WHERE perf.created_at > pa.updated_at
        GROUP BY perf.project_path
        HAVING analysis_count > 1
    )
);
*/

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_analysis_data_json ON project_analysis (json_extract(analysis_data, '$.tech_stack.languages'));
CREATE INDEX IF NOT EXISTS idx_recommendation_data_json ON agent_recommendations (json_extract(recommendation_data, '$.risk_level'));

-- Trigger to update timestamps
CREATE TRIGGER IF NOT EXISTS update_project_analysis_timestamp
    AFTER UPDATE ON project_analysis
BEGIN
    UPDATE project_analysis 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger to cleanup old cache entries when new ones are added
CREATE TRIGGER IF NOT EXISTS cleanup_old_cache_entries
    AFTER INSERT ON project_analysis
BEGIN
    DELETE FROM project_analysis 
    WHERE project_path = NEW.project_path 
    AND id != NEW.id 
    AND datetime(created_at) < datetime('now', '-7 days');
END;