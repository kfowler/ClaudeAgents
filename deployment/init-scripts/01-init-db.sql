-- Initialize Claude Agents Database
-- This script sets up the initial database structure and users

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS agents;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS workflows;
CREATE SCHEMA IF NOT EXISTS learning;
CREATE SCHEMA IF NOT EXISTS semantic;

-- Create application user with limited privileges
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'app_user') THEN
        CREATE USER app_user WITH PASSWORD 'app_user_password';
    END IF;
END
$$;

-- Grant permissions to schemas
GRANT USAGE ON SCHEMA agents TO app_user;
GRANT USAGE ON SCHEMA analytics TO app_user;
GRANT USAGE ON SCHEMA workflows TO app_user;
GRANT USAGE ON SCHEMA learning TO app_user;
GRANT USAGE ON SCHEMA semantic TO app_user;

GRANT CREATE ON SCHEMA agents TO app_user;
GRANT CREATE ON SCHEMA analytics TO app_user;
GRANT CREATE ON SCHEMA workflows TO app_user;
GRANT CREATE ON SCHEMA learning TO app_user;
GRANT CREATE ON SCHEMA semantic TO app_user;

-- Create read-only user for monitoring
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'monitor_user') THEN
        CREATE USER monitor_user WITH PASSWORD 'monitor_password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE claude_agents TO monitor_user;
GRANT USAGE ON SCHEMA public, agents, analytics, workflows, learning, semantic TO monitor_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public, agents, analytics, workflows, learning, semantic TO monitor_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA agents GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA workflows GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA learning GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA semantic GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA agents GRANT SELECT ON TABLES TO monitor_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO monitor_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA workflows GRANT SELECT ON TABLES TO monitor_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA learning GRANT SELECT ON TABLES TO monitor_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA semantic GRANT SELECT ON TABLES TO monitor_user;

-- Create system health table
CREATE TABLE IF NOT EXISTS public.system_health (
    id SERIAL PRIMARY KEY,
    component VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'healthy',
    last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_health_component ON public.system_health(component);
CREATE INDEX IF NOT EXISTS idx_system_health_last_check ON public.system_health(last_check);

-- Create audit log table
CREATE TABLE IF NOT EXISTS public.audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON public.audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON public.audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON public.audit_log(action);

-- Function to update modified timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Insert initial system health records
INSERT INTO public.system_health (component, status, details) VALUES
    ('database', 'healthy', '{"version": "15", "initialized": true}'),
    ('orchestrator', 'initializing', '{"status": "pending_startup"}'),
    ('agent_recommender', 'initializing', '{"status": "pending_startup"}'),
    ('learning_system', 'initializing', '{"status": "pending_startup"}'),
    ('semantic_agent', 'initializing', '{"status": "pending_startup"}'),
    ('analytics', 'initializing', '{"status": "pending_startup"}'),
    ('workflows', 'initializing', '{"status": "pending_startup"}')
ON CONFLICT (component) DO UPDATE SET
    last_check = NOW(),
    details = EXCLUDED.details;