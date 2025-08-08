use std::sync::Arc;
use tokio::sync::{RwLock, Mutex};
use tokio::time::{interval, Duration};
use tracing::{info, warn, error, debug};
use dashmap::DashMap;
use uuid::Uuid;

use crate::config::Config;
use crate::error::{Result, OrchestrationError};
use crate::communication::MessageBus;
use crate::persistence::StateStore;
use crate::agents::AgentRegistry;
use crate::monitoring::MetricsCollector;
use super::{
    Coordinator, TaskDistributor, ConflictResolver, ResourceManager,
    Task, Agent, OrchestrationSession, SessionId, TaskId, AgentId,
    TaskStatus, SessionStatus, AgentStatus
};

/// Main orchestration engine that coordinates all components
pub struct OrchestrationEngine {
    config: Arc<Config>,
    coordinator: Arc<Coordinator>,
    task_distributor: Arc<TaskDistributor>,
    conflict_resolver: Arc<ConflictResolver>,
    resource_manager: Arc<ResourceManager>,
    message_bus: Arc<MessageBus>,
    state_store: Arc<StateStore>,
    agent_registry: Arc<AgentRegistry>,
    metrics: Arc<MetricsCollector>,
    
    // Runtime state
    sessions: Arc<DashMap<SessionId, Arc<RwLock<OrchestrationSession>>>>,
    tasks: Arc<DashMap<TaskId, Arc<RwLock<Task>>>>,
    agents: Arc<DashMap<AgentId, Arc<RwLock<Agent>>>>,
    
    // Control channels
    shutdown_tx: Arc<Mutex<Option<tokio::sync::broadcast::Sender<()>>>>,
}

impl OrchestrationEngine {
    /// Create a new orchestration engine
    pub async fn new(config: Arc<Config>) -> Result<Self> {
        info!("Initializing orchestration engine");
        
        // Initialize core components
        let state_store = Arc::new(StateStore::new(&config.database).await?);
        let message_bus = Arc::new(MessageBus::new(&config.message_queue, &config.redis).await?);
        let agent_registry = Arc::new(AgentRegistry::new(config.clone()).await?);
        let metrics = Arc::new(MetricsCollector::new(&config.monitoring)?);
        
        // Initialize orchestration components
        let resource_manager = Arc::new(ResourceManager::new(
            config.clone(),
            state_store.clone(),
            metrics.clone(),
        ).await?);
        
        let conflict_resolver = Arc::new(ConflictResolver::new(
            config.clone(),
            state_store.clone(),
        )?);
        
        let task_distributor = Arc::new(TaskDistributor::new(
            config.clone(),
            agent_registry.clone(),
            resource_manager.clone(),
            message_bus.clone(),
        ).await?);
        
        let coordinator = Arc::new(Coordinator::new(
            config.clone(),
            task_distributor.clone(),
            conflict_resolver.clone(),
            message_bus.clone(),
            state_store.clone(),
        ).await?);
        
        // Initialize runtime collections
        let sessions = Arc::new(DashMap::new());
        let tasks = Arc::new(DashMap::new());
        let agents = Arc::new(DashMap::new());
        
        let (shutdown_tx, _) = tokio::sync::broadcast::channel(1);
        let shutdown_tx = Arc::new(Mutex::new(Some(shutdown_tx)));
        
        let engine = OrchestrationEngine {
            config,
            coordinator,
            task_distributor,
            conflict_resolver,
            resource_manager,
            message_bus,
            state_store,
            agent_registry,
            metrics,
            sessions,
            tasks,
            agents,
            shutdown_tx,
        };
        
        info!("Orchestration engine initialized successfully");
        Ok(engine)
    }
    
    /// Start the orchestration engine
    pub async fn start(&self) -> Result<()> {
        info!("Starting orchestration engine");
        
        // Start core components
        self.message_bus.start().await?;
        self.agent_registry.start().await?;
        self.metrics.start().await?;
        
        // Load existing state from persistence
        self.load_state().await?;
        
        // Start background tasks
        self.start_background_tasks().await?;
        
        info!("Orchestration engine started successfully");
        Ok(())
    }
    
    /// Gracefully shutdown the orchestration engine
    pub async fn shutdown(&self) -> Result<()> {
        info!("Shutting down orchestration engine");
        
        // Signal shutdown to all background tasks
        if let Some(tx) = self.shutdown_tx.lock().await.take() {
            let _ = tx.send(());
        }
        
        // Cancel all active tasks gracefully
        self.cancel_all_tasks().await?;
        
        // Stop core components
        self.agent_registry.shutdown().await?;
        self.message_bus.shutdown().await?;
        self.metrics.shutdown().await?;
        
        // Persist final state
        self.persist_state().await?;
        
        info!("Orchestration engine shut down successfully");
        Ok(())
    }
    
    /// Create a new orchestration session
    pub async fn create_session(&self, name: String, description: String) -> Result<SessionId> {
        let session_id = Uuid::new_v4();
        let session = OrchestrationSession {
            id: session_id,
            name: name.clone(),
            description,
            tasks: Vec::new(),
            agents: Vec::new(),
            shared_contexts: Vec::new(),
            status: SessionStatus::Active,
            created_at: chrono::Utc::now(),
            completed_at: None,
            configuration: self.get_default_session_config(),
            metrics: Default::default(),
        };
        
        let session = Arc::new(RwLock::new(session));
        self.sessions.insert(session_id, session.clone());
        
        // Persist to storage
        self.state_store.save_session(&*session.read().await).await?;
        
        // Record metrics
        self.metrics.record_session_created(session_id).await;
        
        info!("Created orchestration session: {} ({})", name, session_id);
        Ok(session_id)
    }
    
    /// Submit a task for execution
    pub async fn submit_task(&self, session_id: SessionId, mut task: Task) -> Result<TaskId> {
        // Validate session exists
        let session = self.sessions.get(&session_id)
            .ok_or_else(|| OrchestrationError::Task(format!("Session not found: {}", session_id)))?;
        
        task.session_id = session_id;
        let task_id = task.id;
        
        // Store task
        let task = Arc::new(RwLock::new(task));
        self.tasks.insert(task_id, task.clone());
        
        // Add to session
        session.write().await.tasks.push(task_id);
        
        // Submit to coordinator
        self.coordinator.submit_task(task_id).await?;
        
        // Persist state
        self.state_store.save_task(&*task.read().await).await?;
        
        info!("Submitted task {} to session {}", task_id, session_id);
        Ok(task_id)
    }
    
    /// Get task status
    pub async fn get_task_status(&self, task_id: TaskId) -> Result<TaskStatus> {
        let task = self.tasks.get(&task_id)
            .ok_or_else(|| OrchestrationError::Task(format!("Task not found: {}", task_id)))?;
        
        Ok(task.read().await.status.clone())
    }
    
    /// Get session status
    pub async fn get_session_status(&self, session_id: SessionId) -> Result<SessionStatus> {
        let session = self.sessions.get(&session_id)
            .ok_or_else(|| OrchestrationError::Task(format!("Session not found: {}", session_id)))?;
        
        Ok(session.read().await.status.clone())
    }
    
    /// Cancel a task
    pub async fn cancel_task(&self, task_id: TaskId) -> Result<()> {
        let task = self.tasks.get(&task_id)
            .ok_or_else(|| OrchestrationError::Task(format!("Task not found: {}", task_id)))?;
        
        let mut task_guard = task.write().await;
        if !task_guard.is_completed() {
            task_guard.status = TaskStatus::Cancelled;
            self.coordinator.cancel_task(task_id).await?;
            self.state_store.save_task(&*task_guard).await?;
            
            info!("Cancelled task: {}", task_id);
        }
        
        Ok(())
    }
    
    /// Register a new agent
    pub async fn register_agent(&self, agent: Agent) -> Result<()> {
        let agent_id = agent.id.clone();
        let agent = Arc::new(RwLock::new(agent));
        
        self.agents.insert(agent_id.clone(), agent.clone());
        self.agent_registry.register_agent(agent_id.clone(), agent).await?;
        
        info!("Registered agent: {}", agent_id);
        Ok(())
    }
    
    /// Unregister an agent
    pub async fn unregister_agent(&self, agent_id: &AgentId) -> Result<()> {
        self.agents.remove(agent_id);
        self.agent_registry.unregister_agent(agent_id).await?;
        
        info!("Unregistered agent: {}", agent_id);
        Ok(())
    }
    
    /// Get engine health status
    pub async fn health_check(&self) -> Result<EngineHealth> {
        let active_sessions = self.sessions.len();
        let active_tasks = self.tasks.iter()
            .filter(|entry| {
                let task = entry.value();
                if let Ok(task_guard) = task.try_read() {
                    matches!(task_guard.status, TaskStatus::InProgress | TaskStatus::Assigned)
                } else {
                    false
                }
            })
            .count();
        
        let active_agents = self.agents.iter()
            .filter(|entry| {
                let agent = entry.value();
                if let Ok(agent_guard) = agent.try_read() {
                    agent_guard.status == AgentStatus::Available || agent_guard.status == AgentStatus::Busy
                } else {
                    false
                }
            })
            .count();
        
        let health = EngineHealth {
            is_healthy: true,
            active_sessions,
            active_tasks,
            active_agents,
            message_bus_healthy: self.message_bus.is_healthy().await,
            state_store_healthy: self.state_store.is_healthy().await,
            resource_utilization: self.resource_manager.get_utilization().await?,
        };
        
        Ok(health)
    }
    
    // Private helper methods
    
    async fn load_state(&self) -> Result<()> {
        debug!("Loading state from persistence");
        
        // Load sessions
        let sessions = self.state_store.load_active_sessions().await?;
        for session in sessions {
            let session_id = session.id;
            self.sessions.insert(session_id, Arc::new(RwLock::new(session)));
        }
        
        // Load tasks
        let tasks = self.state_store.load_active_tasks().await?;
        for task in tasks {
            let task_id = task.id;
            self.tasks.insert(task_id, Arc::new(RwLock::new(task)));
        }
        
        // Load agents
        let agents = self.state_store.load_registered_agents().await?;
        for agent in agents {
            let agent_id = agent.id.clone();
            self.agents.insert(agent_id, Arc::new(RwLock::new(agent)));
        }
        
        debug!("State loaded successfully");
        Ok(())
    }
    
    async fn persist_state(&self) -> Result<()> {
        debug!("Persisting state");
        
        // Persist all sessions
        for entry in self.sessions.iter() {
            let session = entry.value().read().await;
            self.state_store.save_session(&*session).await?;
        }
        
        // Persist all tasks
        for entry in self.tasks.iter() {
            let task = entry.value().read().await;
            self.state_store.save_task(&*task).await?;
        }
        
        debug!("State persisted successfully");
        Ok(())
    }
    
    async fn start_background_tasks(&self) -> Result<()> {
        let shutdown_rx = {
            let tx = self.shutdown_tx.lock().await;
            tx.as_ref().unwrap().subscribe()
        };
        
        // Start periodic state persistence
        {
            let engine = self.clone();
            let mut shutdown_rx = shutdown_rx.resubscribe();
            tokio::spawn(async move {
                let mut interval = interval(Duration::from_secs(30));
                loop {
                    tokio::select! {
                        _ = interval.tick() => {
                            if let Err(e) = engine.persist_state().await {
                                warn!("Failed to persist state: {}", e);
                            }
                        }
                        _ = shutdown_rx.recv() => break,
                    }
                }
            });
        }
        
        // Start task timeout monitoring
        {
            let engine = self.clone();
            let mut shutdown_rx = shutdown_rx.resubscribe();
            tokio::spawn(async move {
                let mut interval = interval(Duration::from_secs(10));
                loop {
                    tokio::select! {
                        _ = interval.tick() => {
                            engine.check_task_timeouts().await;
                        }
                        _ = shutdown_rx.recv() => break,
                    }
                }
            });
        }
        
        // Start agent health monitoring
        {
            let engine = self.clone();
            let mut shutdown_rx = shutdown_rx.resubscribe();
            tokio::spawn(async move {
                let mut interval = interval(engine.config.heartbeat_interval());
                loop {
                    tokio::select! {
                        _ = interval.tick() => {
                            engine.monitor_agent_health().await;
                        }
                        _ = shutdown_rx.recv() => break,
                    }
                }
            });
        }
        
        Ok(())
    }
    
    async fn cancel_all_tasks(&self) -> Result<()> {
        let task_ids: Vec<TaskId> = self.tasks.iter()
            .filter_map(|entry| {
                let task = entry.value();
                if let Ok(task_guard) = task.try_read() {
                    if !task_guard.is_completed() {
                        Some(task_guard.id)
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .collect();
        
        for task_id in task_ids {
            if let Err(e) = self.cancel_task(task_id).await {
                warn!("Failed to cancel task {}: {}", task_id, e);
            }
        }
        
        Ok(())
    }
    
    async fn check_task_timeouts(&self) {
        let now = chrono::Utc::now();
        let timeout_tasks: Vec<TaskId> = self.tasks.iter()
            .filter_map(|entry| {
                let task = entry.value();
                if let Ok(task_guard) = task.try_read() {
                    if task_guard.is_timeout() && !task_guard.is_completed() {
                        Some(task_guard.id)
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .collect();
        
        for task_id in timeout_tasks {
            if let Some(task) = self.tasks.get(&task_id) {
                let mut task_guard = task.write().await;
                task_guard.status = TaskStatus::Timeout;
                
                if let Err(e) = self.state_store.save_task(&*task_guard).await {
                    warn!("Failed to save timeout task {}: {}", task_id, e);
                }
                
                warn!("Task {} timed out", task_id);
            }
        }
    }
    
    async fn monitor_agent_health(&self) {
        let unhealthy_agents: Vec<AgentId> = self.agents.iter()
            .filter_map(|entry| {
                let agent = entry.value();
                if let Ok(agent_guard) = agent.try_read() {
                    let last_heartbeat = agent_guard.last_heartbeat;
                    let heartbeat_threshold = chrono::Utc::now() - chrono::Duration::seconds(30);
                    
                    if last_heartbeat < heartbeat_threshold {
                        Some(agent_guard.id.clone())
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .collect();
        
        for agent_id in unhealthy_agents {
            if let Some(agent) = self.agents.get(&agent_id) {
                let mut agent_guard = agent.write().await;
                agent_guard.status = AgentStatus::Unavailable;
                warn!("Agent {} marked as unavailable due to missed heartbeat", agent_id);
            }
        }
    }
    
    fn get_default_session_config(&self) -> super::SessionConfiguration {
        super::SessionConfiguration {
            coordination_strategy: super::CoordinationMode::Collaborative,
            conflict_resolution: self.config.orchestration.conflict_resolution_strategy.clone().into(),
            load_balancing: self.config.orchestration.load_balancing_strategy.clone().into(),
            fault_tolerance: super::FaultToleranceConfig {
                enable_circuit_breaker: true,
                circuit_breaker_threshold: 0.5,
                enable_automatic_recovery: true,
                backup_agents: Vec::new(),
                graceful_degradation: true,
            },
            monitoring: super::MonitoringConfig {
                enable_real_time_tracking: true,
                metrics_collection_interval_ms: self.config.monitoring.metrics_interval_ms,
                enable_performance_profiling: self.config.monitoring.performance_profiling,
                alert_thresholds: super::AlertThresholds {
                    max_execution_time_ms: self.config.orchestration.task_timeout_ms,
                    max_memory_usage_mb: 1000,
                    min_success_rate: 0.95,
                    max_error_rate: 0.05,
                    max_response_time_ms: 5000,
                },
            },
        }
    }
}

impl Clone for OrchestrationEngine {
    fn clone(&self) -> Self {
        OrchestrationEngine {
            config: self.config.clone(),
            coordinator: self.coordinator.clone(),
            task_distributor: self.task_distributor.clone(),
            conflict_resolver: self.conflict_resolver.clone(),
            resource_manager: self.resource_manager.clone(),
            message_bus: self.message_bus.clone(),
            state_store: self.state_store.clone(),
            agent_registry: self.agent_registry.clone(),
            metrics: self.metrics.clone(),
            sessions: self.sessions.clone(),
            tasks: self.tasks.clone(),
            agents: self.agents.clone(),
            shutdown_tx: self.shutdown_tx.clone(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct EngineHealth {
    pub is_healthy: bool,
    pub active_sessions: usize,
    pub active_tasks: usize,
    pub active_agents: usize,
    pub message_bus_healthy: bool,
    pub state_store_healthy: bool,
    pub resource_utilization: f32,
}

// Conversion traits for config enums
impl From<crate::config::ConflictResolutionStrategy> for super::ConflictResolutionStrategy {
    fn from(strategy: crate::config::ConflictResolutionStrategy) -> Self {
        match strategy {
            crate::config::ConflictResolutionStrategy::FirstWins => Self::FirstWins,
            crate::config::ConflictResolutionStrategy::LastWins => Self::LastWins,
            crate::config::ConflictResolutionStrategy::Majority => Self::Majority,
            crate::config::ConflictResolutionStrategy::WeightedVoting => Self::WeightedVoting,
            crate::config::ConflictResolutionStrategy::ExpertPriority => Self::ExpertPriority,
            crate::config::ConflictResolutionStrategy::ConsensusRequired => Self::ConsensusRequired,
        }
    }
}

impl From<crate::config::LoadBalancingStrategy> for super::LoadBalancingStrategy {
    fn from(strategy: crate::config::LoadBalancingStrategy) -> Self {
        match strategy {
            crate::config::LoadBalancingStrategy::RoundRobin => Self::RoundRobin,
            crate::config::LoadBalancingStrategy::LeastConnections => Self::LeastConnections,
            crate::config::LoadBalancingStrategy::WeightedRoundRobin => Self::WeightedRoundRobin,
            crate::config::LoadBalancingStrategy::ConsistentHashing => Self::ConsistentHashing,
            crate::config::LoadBalancingStrategy::AdaptiveLoad => Self::AdaptiveLoad,
        }
    }
}

impl Default for super::SessionMetrics {
    fn default() -> Self {
        Self {
            total_tasks: 0,
            completed_tasks: 0,
            failed_tasks: 0,
            total_execution_time_ms: 0,
            total_tokens_used: 0,
            agents_used: 0,
            conflicts_resolved: 0,
            context_updates: 0,
        }
    }
}