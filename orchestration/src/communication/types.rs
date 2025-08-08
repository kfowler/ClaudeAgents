use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;
use chrono::{DateTime, Utc};
use crate::orchestration::{TaskId, AgentId, SessionId};

/// Unique identifier for messages
pub type MessageId = Uuid;

/// Communication channels for different message types
#[derive(Debug, Clone, Serialize, Deserialize, Hash, PartialEq, Eq)]
pub enum Channel {
    TaskExecution,
    AgentCoordination,
    ContextSync,
    ConflictResolution,
    ResourceManagement,
    HealthCheck,
    Broadcast,
    Direct(AgentId),
    Session(SessionId),
}

/// Message types for inter-agent communication
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub id: MessageId,
    pub sender: AgentId,
    pub recipient: MessageRecipient,
    pub channel: Channel,
    pub message_type: MessageType,
    pub payload: MessagePayload,
    pub priority: MessagePriority,
    pub timestamp: DateTime<Utc>,
    pub correlation_id: Option<MessageId>,
    pub expires_at: Option<DateTime<Utc>>,
    pub delivery_options: DeliveryOptions,
    pub metadata: HashMap<String, serde_json::Value>,
}

/// Message recipients
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessageRecipient {
    Agent(AgentId),
    Agents(Vec<AgentId>),
    Session(SessionId),
    All,
    Coordinator,
}

/// Types of messages in the system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessageType {
    // Task management
    TaskAssigned,
    TaskStarted,
    TaskProgress,
    TaskCompleted,
    TaskFailed,
    TaskCancelled,
    
    // Agent coordination
    AgentHeartbeat,
    AgentStatusUpdate,
    AgentCapabilityUpdate,
    AgentJoinSession,
    AgentLeaveSession,
    
    // Context synchronization
    ContextUpdate,
    ContextRequest,
    ContextResponse,
    ContextLock,
    ContextUnlock,
    ContextConflict,
    
    // Conflict resolution
    ConflictDetected,
    ConflictProposal,
    ConflictVote,
    ConflictResolved,
    
    // Resource management
    ResourceRequest,
    ResourceGrant,
    ResourceRelease,
    ResourceExhausted,
    
    // Real-time coordination
    CoordinationRequest,
    CoordinationResponse,
    SynchronizationPoint,
    BarrierWait,
    BarrierRelease,
    
    // System messages
    SystemAlert,
    SystemHealth,
    SystemShutdown,
    
    // Custom message
    Custom(String),
}

/// Message priority levels
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum MessagePriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Critical = 3,
    Emergency = 4,
}

/// Message payload containing actual data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessagePayload {
    TaskAssignment {
        task_id: TaskId,
        task_data: serde_json::Value,
        requirements: serde_json::Value,
        deadline: Option<DateTime<Utc>>,
    },
    TaskProgress {
        task_id: TaskId,
        progress_percent: f32,
        status_message: String,
        intermediate_results: Option<serde_json::Value>,
        metrics: Option<serde_json::Value>,
    },
    TaskResult {
        task_id: TaskId,
        result: serde_json::Value,
        success: bool,
        error_message: Option<String>,
        artifacts: Vec<String>,
        metrics: serde_json::Value,
    },
    AgentStatus {
        agent_id: AgentId,
        status: String,
        load_percent: f32,
        active_tasks: Vec<TaskId>,
        capabilities: Vec<String>,
        health_metrics: serde_json::Value,
    },
    ContextOperation {
        context_id: Uuid,
        operation: ContextOperationType,
        key: String,
        value: Option<serde_json::Value>,
        version: u64,
    },
    ConflictData {
        conflict_id: Uuid,
        conflict_type: ConflictType,
        involved_agents: Vec<AgentId>,
        data: serde_json::Value,
        proposed_resolution: Option<serde_json::Value>,
    },
    ResourceData {
        resource_type: String,
        amount: f32,
        duration_ms: Option<u64>,
        justification: String,
        alternatives: Vec<String>,
    },
    CoordinationData {
        coordination_id: Uuid,
        coordination_type: CoordinationType,
        participants: Vec<AgentId>,
        data: serde_json::Value,
        timeout_ms: Option<u64>,
    },
    SystemData {
        system_type: String,
        data: serde_json::Value,
        severity: String,
        action_required: bool,
    },
    Raw(serde_json::Value),
}

/// Context operation types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ContextOperationType {
    Read,
    Write,
    Update,
    Delete,
    Lock,
    Unlock,
    Subscribe,
    Unsubscribe,
}

/// Types of conflicts that can occur
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConflictType {
    ContextUpdate,
    ResourceContention,
    TaskAssignment,
    DecisionDisagreement,
    ProtocolViolation,
    Custom(String),
}

/// Coordination types for multi-agent synchronization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CoordinationType {
    Barrier,
    Consensus,
    Election,
    Synchronization,
    Handoff,
    Custom(String),
}

/// Delivery options for messages
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeliveryOptions {
    pub guaranteed_delivery: bool,
    pub max_retries: u32,
    pub retry_delay_ms: u64,
    pub require_acknowledgment: bool,
    pub duplicate_detection: bool,
    pub ordering_required: bool,
}

/// Message acknowledgment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageAck {
    pub message_id: MessageId,
    pub recipient: AgentId,
    pub status: AckStatus,
    pub timestamp: DateTime<Utc>,
    pub response_data: Option<serde_json::Value>,
    pub error_message: Option<String>,
}

/// Acknowledgment status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AckStatus {
    Received,
    Processed,
    Failed,
    Rejected,
}

/// Real-time event for WebSocket clients
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RealtimeEvent {
    pub event_id: Uuid,
    pub event_type: EventType,
    pub session_id: Option<SessionId>,
    pub agent_id: Option<AgentId>,
    pub task_id: Option<TaskId>,
    pub data: serde_json::Value,
    pub timestamp: DateTime<Utc>,
}

/// Types of real-time events
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EventType {
    TaskCreated,
    TaskStarted,
    TaskProgress,
    TaskCompleted,
    TaskFailed,
    AgentJoined,
    AgentLeft,
    AgentStatusChanged,
    ConflictDetected,
    ConflictResolved,
    ResourceAlert,
    SystemAlert,
    Custom(String),
}

/// Connection information for WebSocket clients
#[derive(Debug, Clone)]
pub struct ClientConnection {
    pub connection_id: Uuid,
    pub client_type: ClientType,
    pub subscriptions: Vec<Subscription>,
    pub authenticated: bool,
    pub user_id: Option<String>,
    pub connected_at: DateTime<Utc>,
    pub last_activity: DateTime<Utc>,
}

/// Types of WebSocket clients
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ClientType {
    Dashboard,
    Agent,
    Monitor,
    Developer,
    Integration,
}

/// Subscription filters for real-time events
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subscription {
    pub id: Uuid,
    pub event_types: Vec<EventType>,
    pub session_filter: Option<SessionId>,
    pub agent_filter: Option<AgentId>,
    pub task_filter: Option<TaskId>,
    pub custom_filters: HashMap<String, serde_json::Value>,
}

/// Message routing information
#[derive(Debug, Clone)]
pub struct MessageRoute {
    pub source: AgentId,
    pub destinations: Vec<AgentId>,
    pub channel: Channel,
    pub routing_strategy: RoutingStrategy,
    pub load_balancing: bool,
    pub failover_agents: Vec<AgentId>,
}

/// Strategies for message routing
#[derive(Debug, Clone)]
pub enum RoutingStrategy {
    Direct,
    Broadcast,
    Multicast,
    LoadBalanced,
    Failover,
    Custom(String),
}

/// Message queue statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueueStats {
    pub queue_name: String,
    pub message_count: u64,
    pub consumer_count: u32,
    pub published_rate: f64,
    pub consumed_rate: f64,
    pub average_latency_ms: f64,
    pub error_rate: f64,
    pub last_updated: DateTime<Utc>,
}

/// Circuit breaker state for fault tolerance
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CircuitBreakerState {
    Closed,
    Open,
    HalfOpen,
}

/// Circuit breaker statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CircuitBreakerStats {
    pub state: CircuitBreakerState,
    pub failure_count: u32,
    pub success_count: u32,
    pub failure_rate: f32,
    pub last_failure: Option<DateTime<Utc>>,
    pub next_attempt_at: Option<DateTime<Utc>>,
}

impl Message {
    pub fn new(
        sender: AgentId,
        recipient: MessageRecipient,
        channel: Channel,
        message_type: MessageType,
        payload: MessagePayload,
    ) -> Self {
        Message {
            id: Uuid::new_v4(),
            sender,
            recipient,
            channel,
            message_type,
            payload,
            priority: MessagePriority::Normal,
            timestamp: Utc::now(),
            correlation_id: None,
            expires_at: None,
            delivery_options: DeliveryOptions::default(),
            metadata: HashMap::new(),
        }
    }
    
    pub fn with_priority(mut self, priority: MessagePriority) -> Self {
        self.priority = priority;
        self
    }
    
    pub fn with_correlation_id(mut self, correlation_id: MessageId) -> Self {
        self.correlation_id = Some(correlation_id);
        self
    }
    
    pub fn with_expiry(mut self, expires_at: DateTime<Utc>) -> Self {
        self.expires_at = Some(expires_at);
        self
    }
    
    pub fn with_delivery_options(mut self, options: DeliveryOptions) -> Self {
        self.delivery_options = options;
        self
    }
    
    pub fn is_expired(&self) -> bool {
        if let Some(expires_at) = self.expires_at {
            Utc::now() > expires_at
        } else {
            false
        }
    }
    
    pub fn routing_key(&self) -> String {
        match &self.channel {
            Channel::TaskExecution => "task.execution".to_string(),
            Channel::AgentCoordination => "agent.coordination".to_string(),
            Channel::ContextSync => "context.sync".to_string(),
            Channel::ConflictResolution => "conflict.resolution".to_string(),
            Channel::ResourceManagement => "resource.management".to_string(),
            Channel::HealthCheck => "health.check".to_string(),
            Channel::Broadcast => "broadcast".to_string(),
            Channel::Direct(agent_id) => format!("direct.{}", agent_id),
            Channel::Session(session_id) => format!("session.{}", session_id),
        }
    }
}

impl Default for DeliveryOptions {
    fn default() -> Self {
        DeliveryOptions {
            guaranteed_delivery: false,
            max_retries: 3,
            retry_delay_ms: 1000,
            require_acknowledgment: false,
            duplicate_detection: true,
            ordering_required: false,
        }
    }
}

impl DeliveryOptions {
    pub fn reliable() -> Self {
        DeliveryOptions {
            guaranteed_delivery: true,
            max_retries: 5,
            retry_delay_ms: 2000,
            require_acknowledgment: true,
            duplicate_detection: true,
            ordering_required: true,
        }
    }
    
    pub fn best_effort() -> Self {
        DeliveryOptions {
            guaranteed_delivery: false,
            max_retries: 0,
            retry_delay_ms: 0,
            require_acknowledgment: false,
            duplicate_detection: false,
            ordering_required: false,
        }
    }
}

impl RealtimeEvent {
    pub fn new(
        event_type: EventType,
        data: serde_json::Value,
    ) -> Self {
        RealtimeEvent {
            event_id: Uuid::new_v4(),
            event_type,
            session_id: None,
            agent_id: None,
            task_id: None,
            data,
            timestamp: Utc::now(),
        }
    }
    
    pub fn with_session(mut self, session_id: SessionId) -> Self {
        self.session_id = Some(session_id);
        self
    }
    
    pub fn with_agent(mut self, agent_id: AgentId) -> Self {
        self.agent_id = Some(agent_id);
        self
    }
    
    pub fn with_task(mut self, task_id: TaskId) -> Self {
        self.task_id = Some(task_id);
        self
    }
}