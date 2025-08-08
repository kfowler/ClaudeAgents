use thiserror::Error;

#[derive(Error, Debug)]
pub enum OrchestrationError {
    #[error("Configuration error: {0}")]
    Config(#[from] config::ConfigError),
    
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    
    #[error("Redis error: {0}")]
    Redis(#[from] redis::RedisError),
    
    #[error("Message queue error: {0}")]
    MessageQueue(#[from] lapin::Error),
    
    #[error("Agent error: {0}")]
    Agent(String),
    
    #[error("Task error: {0}")]
    Task(String),
    
    #[error("Communication error: {0}")]
    Communication(String),
    
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    
    #[error("Network error: {0}")]
    Network(#[from] reqwest::Error),
    
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Validation error: {0}")]
    Validation(#[from] validator::ValidationErrors),
    
    #[error("Timeout error: {message}")]
    Timeout { message: String },
    
    #[error("Resource exhausted: {resource}")]
    ResourceExhausted { resource: String },
    
    #[error("Conflict resolution failed: {reason}")]
    ConflictResolution { reason: String },
    
    #[error("Agent unavailable: {agent_id}")]
    AgentUnavailable { agent_id: String },
    
    #[error("Internal error: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, OrchestrationError>;

impl OrchestrationError {
    pub fn is_retryable(&self) -> bool {
        match self {
            OrchestrationError::Network(_) |
            OrchestrationError::Database(_) |
            OrchestrationError::Redis(_) |
            OrchestrationError::MessageQueue(_) |
            OrchestrationError::Timeout { .. } |
            OrchestrationError::AgentUnavailable { .. } => true,
            _ => false,
        }
    }
    
    pub fn severity(&self) -> ErrorSeverity {
        match self {
            OrchestrationError::Config(_) |
            OrchestrationError::Validation(_) => ErrorSeverity::Critical,
            
            OrchestrationError::Database(_) |
            OrchestrationError::Redis(_) |
            OrchestrationError::MessageQueue(_) => ErrorSeverity::High,
            
            OrchestrationError::Agent(_) |
            OrchestrationError::Task(_) |
            OrchestrationError::AgentUnavailable { .. } => ErrorSeverity::Medium,
            
            OrchestrationError::Communication(_) |
            OrchestrationError::Network(_) |
            OrchestrationError::Timeout { .. } => ErrorSeverity::Low,
            
            _ => ErrorSeverity::Medium,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorSeverity {
    Low,
    Medium, 
    High,
    Critical,
}

impl ErrorSeverity {
    pub fn as_str(&self) -> &'static str {
        match self {
            ErrorSeverity::Low => "low",
            ErrorSeverity::Medium => "medium", 
            ErrorSeverity::High => "high",
            ErrorSeverity::Critical => "critical",
        }
    }
}