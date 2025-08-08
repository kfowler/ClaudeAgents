use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{Duration, Instant, SystemTime};
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Unique identifier for tasks
pub type TaskId = Uuid;

/// Unique identifier for agents
pub type AgentId = String;

/// Unique identifier for orchestration sessions
pub type SessionId = Uuid;

/// Represents the current state of a task
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TaskStatus {
    Pending,
    Assigned,
    InProgress,
    Completed,
    Failed,
    Cancelled,
    Timeout,
}

/// Priority levels for task execution
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum TaskPriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Critical = 3,
    Emergency = 4,
}

/// Represents the current state of an agent
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AgentStatus {
    Available,
    Busy,
    Unavailable,
    Error,
    Maintenance,
}

/// Task definition with requirements and constraints
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: TaskId,
    pub session_id: SessionId,
    pub name: String,
    pub description: String,
    pub priority: TaskPriority,
    pub requirements: TaskRequirements,
    pub dependencies: Vec<TaskId>,
    pub input: TaskInput,
    pub constraints: TaskConstraints,
    pub metadata: HashMap<String, serde_json::Value>,
    pub created_at: DateTime<Utc>,
    pub deadline: Option<DateTime<Utc>>,
    pub status: TaskStatus,
    pub assigned_agents: Vec<AgentId>,
    pub result: Option<TaskResult>,
    pub error: Option<String>,
    pub retries: u32,
    pub max_retries: u32,
}

/// Requirements for task execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskRequirements {
    pub required_capabilities: Vec<String>,
    pub preferred_agents: Vec<AgentId>,
    pub excluded_agents: Vec<AgentId>,
    pub min_agents: usize,
    pub max_agents: usize,
    pub required_resources: ResourceRequirements,
}

/// Resource requirements for tasks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceRequirements {
    pub cpu_cores: Option<f32>,
    pub memory_mb: Option<u64>,
    pub tokens_per_minute: Option<u64>,
    pub context_size_mb: Option<u64>,
    pub execution_time_estimate_ms: Option<u64>,
}

/// Task execution constraints
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskConstraints {
    pub timeout_ms: Option<u64>,
    pub retry_policy: Option<RetryPolicy>,
    pub isolation_level: IsolationLevel,
    pub consistency_requirements: ConsistencyLevel,
    pub coordination_mode: CoordinationMode,
}

/// Retry policy for failed tasks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RetryPolicy {
    pub max_attempts: u32,
    pub initial_delay_ms: u64,
    pub backoff_multiplier: f64,
    pub max_delay_ms: u64,
    pub retry_on_failures: Vec<String>,
}

/// Isolation levels for task execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IsolationLevel {
    None,
    Process,
    Container,
    Sandbox,
}

/// Consistency requirements for distributed execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConsistencyLevel {
    Eventual,
    Strong,
    Sequential,
    Linearizable,
}

/// Coordination modes between agents
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CoordinationMode {
    Independent,
    Collaborative,
    Hierarchical,
    Consensus,
}

/// Input data for task execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskInput {
    pub data: serde_json::Value,
    pub context: Option<SharedContext>,
    pub files: Vec<FileReference>,
    pub parameters: HashMap<String, serde_json::Value>,
}

/// Result of task execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskResult {
    pub output: serde_json::Value,
    pub artifacts: Vec<Artifact>,
    pub metrics: ExecutionMetrics,
    pub context_updates: Vec<ContextUpdate>,
    pub recommendations: Vec<Recommendation>,
    pub completed_at: DateTime<Utc>,
}

/// Execution metrics for performance tracking
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionMetrics {
    pub execution_time_ms: u64,
    pub tokens_used: u64,
    pub memory_peak_mb: u64,
    pub cpu_usage_percent: f32,
    pub network_bytes_sent: u64,
    pub network_bytes_received: u64,
    pub cache_hits: u64,
    pub cache_misses: u64,
}

/// Agent definition with capabilities and status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Agent {
    pub id: AgentId,
    pub name: String,
    pub description: String,
    pub capabilities: Vec<String>,
    pub specializations: Vec<String>,
    pub status: AgentStatus,
    pub current_load: f32,
    pub max_concurrent_tasks: usize,
    pub active_tasks: Vec<TaskId>,
    pub performance_metrics: AgentMetrics,
    pub health: HealthStatus,
    pub configuration: HashMap<String, serde_json::Value>,
    pub last_heartbeat: DateTime<Utc>,
    pub version: String,
}

/// Performance metrics for agents
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentMetrics {
    pub tasks_completed: u64,
    pub tasks_failed: u64,
    pub average_execution_time_ms: f64,
    pub success_rate: f32,
    pub tokens_processed: u64,
    pub uptime_hours: f64,
    pub error_rate: f32,
    pub quality_score: f32,
}

/// Health status of agents
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthStatus {
    pub is_healthy: bool,
    pub last_check: DateTime<Utc>,
    pub response_time_ms: Option<u64>,
    pub error_count: u32,
    pub warnings: Vec<String>,
    pub details: HashMap<String, serde_json::Value>,
}

/// Shared context for multi-agent coordination
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SharedContext {
    pub id: Uuid,
    pub session_id: SessionId,
    pub name: String,
    pub data: HashMap<String, serde_json::Value>,
    pub version: u64,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub access_permissions: Vec<AgentId>,
    pub locked_by: Option<AgentId>,
    pub lock_expires_at: Option<DateTime<Utc>>,
}

/// Updates to shared context
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextUpdate {
    pub context_id: Uuid,
    pub key: String,
    pub value: serde_json::Value,
    pub operation: ContextOperation,
    pub agent_id: AgentId,
    pub timestamp: DateTime<Utc>,
}

/// Operations on shared context
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ContextOperation {
    Set,
    Update,
    Delete,
    Append,
    Increment,
}

/// File references for task input/output
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileReference {
    pub path: String,
    pub size: u64,
    pub checksum: String,
    pub mime_type: String,
    pub encoding: Option<String>,
}

/// Output artifacts from task execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Artifact {
    pub name: String,
    pub artifact_type: ArtifactType,
    pub data: serde_json::Value,
    pub size: u64,
    pub created_at: DateTime<Utc>,
    pub metadata: HashMap<String, serde_json::Value>,
}

/// Types of artifacts
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ArtifactType {
    Code,
    Documentation,
    Data,
    Model,
    Configuration,
    Log,
    Report,
    Image,
    Other,
}

/// Recommendations from agents
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recommendation {
    pub agent_id: AgentId,
    pub recommendation_type: RecommendationType,
    pub title: String,
    pub description: String,
    pub confidence: f32,
    pub priority: TaskPriority,
    pub suggested_actions: Vec<String>,
    pub metadata: HashMap<String, serde_json::Value>,
}

/// Types of recommendations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RecommendationType {
    Optimization,
    Security,
    BestPractice,
    Performance,
    Maintenance,
    Alternative,
    Warning,
}

/// Orchestration session tracking multiple related tasks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrchestrationSession {
    pub id: SessionId,
    pub name: String,
    pub description: String,
    pub tasks: Vec<TaskId>,
    pub agents: Vec<AgentId>,
    pub shared_contexts: Vec<Uuid>,
    pub status: SessionStatus,
    pub created_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
    pub configuration: SessionConfiguration,
    pub metrics: SessionMetrics,
}

/// Status of orchestration sessions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SessionStatus {
    Active,
    Paused,
    Completed,
    Failed,
    Cancelled,
}

/// Configuration for orchestration sessions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionConfiguration {
    pub coordination_strategy: CoordinationMode,
    pub conflict_resolution: ConflictResolutionStrategy,
    pub load_balancing: LoadBalancingStrategy,
    pub fault_tolerance: FaultToleranceConfig,
    pub monitoring: MonitoringConfig,
}

/// Strategies for conflict resolution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConflictResolutionStrategy {
    FirstWins,
    LastWins,
    Majority,
    WeightedVoting,
    ExpertPriority,
    ConsensusRequired,
}

/// Load balancing strategies
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum LoadBalancingStrategy {
    RoundRobin,
    LeastConnections,
    WeightedRoundRobin,
    ConsistentHashing,
    AdaptiveLoad,
}

/// Fault tolerance configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FaultToleranceConfig {
    pub enable_circuit_breaker: bool,
    pub circuit_breaker_threshold: f32,
    pub enable_automatic_recovery: bool,
    pub backup_agents: Vec<AgentId>,
    pub graceful_degradation: bool,
}

/// Monitoring configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringConfig {
    pub enable_real_time_tracking: bool,
    pub metrics_collection_interval_ms: u64,
    pub enable_performance_profiling: bool,
    pub alert_thresholds: AlertThresholds,
}

/// Alert thresholds for monitoring
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertThresholds {
    pub max_execution_time_ms: u64,
    pub max_memory_usage_mb: u64,
    pub min_success_rate: f32,
    pub max_error_rate: f32,
    pub max_response_time_ms: u64,
}

/// Session-level metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionMetrics {
    pub total_tasks: u64,
    pub completed_tasks: u64,
    pub failed_tasks: u64,
    pub total_execution_time_ms: u64,
    pub total_tokens_used: u64,
    pub agents_used: u64,
    pub conflicts_resolved: u64,
    pub context_updates: u64,
}

impl Task {
    pub fn new(session_id: SessionId, name: String, description: String) -> Self {
        Task {
            id: Uuid::new_v4(),
            session_id,
            name,
            description,
            priority: TaskPriority::Normal,
            requirements: TaskRequirements::default(),
            dependencies: Vec::new(),
            input: TaskInput::default(),
            constraints: TaskConstraints::default(),
            metadata: HashMap::new(),
            created_at: Utc::now(),
            deadline: None,
            status: TaskStatus::Pending,
            assigned_agents: Vec::new(),
            result: None,
            error: None,
            retries: 0,
            max_retries: 3,
        }
    }
    
    pub fn is_ready_to_execute(&self) -> bool {
        self.status == TaskStatus::Pending && self.dependencies.is_empty()
    }
    
    pub fn is_completed(&self) -> bool {
        matches!(self.status, TaskStatus::Completed | TaskStatus::Failed | TaskStatus::Cancelled)
    }
    
    pub fn is_timeout(&self) -> bool {
        if let Some(deadline) = self.deadline {
            Utc::now() > deadline
        } else {
            false
        }
    }
}

impl Default for TaskRequirements {
    fn default() -> Self {
        TaskRequirements {
            required_capabilities: Vec::new(),
            preferred_agents: Vec::new(),
            excluded_agents: Vec::new(),
            min_agents: 1,
            max_agents: 1,
            required_resources: ResourceRequirements::default(),
        }
    }
}

impl Default for ResourceRequirements {
    fn default() -> Self {
        ResourceRequirements {
            cpu_cores: None,
            memory_mb: None,
            tokens_per_minute: None,
            context_size_mb: None,
            execution_time_estimate_ms: None,
        }
    }
}

impl Default for TaskConstraints {
    fn default() -> Self {
        TaskConstraints {
            timeout_ms: Some(300_000), // 5 minutes default
            retry_policy: Some(RetryPolicy::default()),
            isolation_level: IsolationLevel::Process,
            consistency_requirements: ConsistencyLevel::Eventual,
            coordination_mode: CoordinationMode::Independent,
        }
    }
}

impl Default for TaskInput {
    fn default() -> Self {
        TaskInput {
            data: serde_json::Value::Null,
            context: None,
            files: Vec::new(),
            parameters: HashMap::new(),
        }
    }
}

impl Default for RetryPolicy {
    fn default() -> Self {
        RetryPolicy {
            max_attempts: 3,
            initial_delay_ms: 1000,
            backoff_multiplier: 2.0,
            max_delay_ms: 30000,
            retry_on_failures: vec!["timeout".to_string(), "network_error".to_string()],
        }
    }
}