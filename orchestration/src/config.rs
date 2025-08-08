use serde::{Deserialize, Serialize};
use std::time::Duration;
use crate::error::Result;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub redis: RedisConfig,
    pub message_queue: MessageQueueConfig,
    pub orchestration: OrchestrationConfig,
    pub monitoring: MonitoringConfig,
    pub security: SecurityConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub worker_threads: Option<usize>,
    pub max_connections: usize,
    pub request_timeout_ms: u64,
    pub keepalive_timeout_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub min_connections: u32,
    pub acquire_timeout_ms: u64,
    pub idle_timeout_ms: u64,
    pub max_lifetime_ms: Option<u64>,
    pub migrate_on_startup: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RedisConfig {
    pub urls: Vec<String>,
    pub pool_size: u32,
    pub timeout_ms: u64,
    pub retry_attempts: u32,
    pub cluster_mode: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageQueueConfig {
    pub rabbitmq_url: Option<String>,
    pub kafka_brokers: Option<Vec<String>>,
    pub default_queue: String,
    pub prefetch_count: u16,
    pub ack_timeout_ms: u64,
    pub retry_policy: RetryPolicy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RetryPolicy {
    pub max_attempts: u32,
    pub initial_delay_ms: u64,
    pub backoff_multiplier: f64,
    pub max_delay_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrchestrationConfig {
    pub max_concurrent_tasks: usize,
    pub task_timeout_ms: u64,
    pub agent_startup_timeout_ms: u64,
    pub heartbeat_interval_ms: u64,
    pub load_balancing_strategy: LoadBalancingStrategy,
    pub conflict_resolution_strategy: ConflictResolutionStrategy,
    pub resource_limits: ResourceLimits,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum LoadBalancingStrategy {
    RoundRobin,
    LeastConnections,
    WeightedRoundRobin,
    ConsistentHashing,
    AdaptiveLoad,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConflictResolutionStrategy {
    FirstWins,
    LastWins,
    Majority,
    WeightedVoting,
    ExpertPriority,
    ConsensusRequired,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceLimits {
    pub max_memory_mb: Option<u64>,
    pub max_cpu_cores: Option<f32>,
    pub max_tokens_per_minute: u64,
    pub max_agents_per_task: usize,
    pub max_context_size_mb: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringConfig {
    pub prometheus_endpoint: String,
    pub jaeger_endpoint: Option<String>,
    pub log_level: String,
    pub metrics_interval_ms: u64,
    pub health_check_interval_ms: u64,
    pub performance_profiling: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub jwt_secret: String,
    pub jwt_expiry_hours: u64,
    pub rate_limiting: RateLimitConfig,
    pub cors_origins: Vec<String>,
    pub tls_enabled: bool,
    pub cert_path: Option<String>,
    pub key_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RateLimitConfig {
    pub requests_per_minute: u64,
    pub burst_size: u64,
    pub per_ip_limit: u64,
    pub per_user_limit: u64,
}

impl Config {
    pub async fn from_file(path: &str) -> Result<Self> {
        let content = tokio::fs::read_to_string(path).await?;
        let config: Config = toml::from_str(&content)?;
        Ok(config)
    }
    
    pub fn default() -> Self {
        Config {
            server: ServerConfig {
                host: "0.0.0.0".to_string(),
                port: 8080,
                worker_threads: None,
                max_connections: 10000,
                request_timeout_ms: 30000,
                keepalive_timeout_ms: 5000,
            },
            database: DatabaseConfig {
                url: "postgresql://localhost:5432/orchestration".to_string(),
                max_connections: 100,
                min_connections: 5,
                acquire_timeout_ms: 5000,
                idle_timeout_ms: 300000,
                max_lifetime_ms: Some(1800000),
                migrate_on_startup: true,
            },
            redis: RedisConfig {
                urls: vec!["redis://localhost:6379".to_string()],
                pool_size: 50,
                timeout_ms: 5000,
                retry_attempts: 3,
                cluster_mode: false,
            },
            message_queue: MessageQueueConfig {
                rabbitmq_url: Some("amqp://localhost:5672".to_string()),
                kafka_brokers: None,
                default_queue: "orchestration".to_string(),
                prefetch_count: 10,
                ack_timeout_ms: 30000,
                retry_policy: RetryPolicy {
                    max_attempts: 3,
                    initial_delay_ms: 1000,
                    backoff_multiplier: 2.0,
                    max_delay_ms: 30000,
                },
            },
            orchestration: OrchestrationConfig {
                max_concurrent_tasks: 1000,
                task_timeout_ms: 300000,
                agent_startup_timeout_ms: 10000,
                heartbeat_interval_ms: 5000,
                load_balancing_strategy: LoadBalancingStrategy::AdaptiveLoad,
                conflict_resolution_strategy: ConflictResolutionStrategy::WeightedVoting,
                resource_limits: ResourceLimits {
                    max_memory_mb: None,
                    max_cpu_cores: None,
                    max_tokens_per_minute: 100000,
                    max_agents_per_task: 10,
                    max_context_size_mb: 100,
                },
            },
            monitoring: MonitoringConfig {
                prometheus_endpoint: "0.0.0.0:9090".to_string(),
                jaeger_endpoint: None,
                log_level: "info".to_string(),
                metrics_interval_ms: 10000,
                health_check_interval_ms: 30000,
                performance_profiling: false,
            },
            security: SecurityConfig {
                jwt_secret: "change-this-secret-key".to_string(),
                jwt_expiry_hours: 24,
                rate_limiting: RateLimitConfig {
                    requests_per_minute: 1000,
                    burst_size: 100,
                    per_ip_limit: 100,
                    per_user_limit: 1000,
                },
                cors_origins: vec!["*".to_string()],
                tls_enabled: false,
                cert_path: None,
                key_path: None,
            },
        }
    }
    
    pub fn request_timeout(&self) -> Duration {
        Duration::from_millis(self.server.request_timeout_ms)
    }
    
    pub fn task_timeout(&self) -> Duration {
        Duration::from_millis(self.orchestration.task_timeout_ms)
    }
    
    pub fn heartbeat_interval(&self) -> Duration {
        Duration::from_millis(self.orchestration.heartbeat_interval_ms)
    }
}