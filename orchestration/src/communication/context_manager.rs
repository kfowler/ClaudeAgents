use std::sync::Arc;
use std::collections::HashMap;
use std::time::Duration;
use tokio::sync::{RwLock, Mutex, broadcast};
use tokio::time::{timeout, Instant};
use tracing::{info, warn, error, debug};
use dashmap::DashMap;
use uuid::Uuid;
use serde_json::Value;

use crate::error::{Result, OrchestrationError};
use crate::persistence::StateStore;
use crate::orchestration::{AgentId, SessionId, SharedContext, ContextUpdate, ContextOperation};
use super::{MessageBus, Message, MessageType, MessagePayload, MessageRecipient, Channel, EventType, RealtimeEvent};

/// Manages shared context for multi-agent coordination with conflict resolution
pub struct ContextManager {
    state_store: Arc<StateStore>,
    message_bus: Arc<MessageBus>,
    
    // In-memory context cache with versioning
    contexts: Arc<DashMap<Uuid, Arc<RwLock<SharedContext>>>>,
    
    // Context locks for concurrent access control
    locks: Arc<DashMap<Uuid, ContextLock>>,
    
    // Context subscriptions for real-time updates
    subscriptions: Arc<DashMap<Uuid, Vec<AgentSubscription>>>,
    
    // Change tracking and conflict detection
    pending_changes: Arc<DashMap<Uuid, Vec<PendingChange>>>,
    conflict_detector: Arc<ConflictDetector>,
    
    // Performance optimization
    access_patterns: Arc<DashMap<Uuid, AccessPattern>>,
    cache_stats: Arc<RwLock<CacheStats>>,
    
    // Background task handles
    sync_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
    cleanup_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
    
    // Shutdown coordination
    shutdown_tx: Arc<Mutex<Option<broadcast::Sender<()>>>>,
}

#[derive(Debug, Clone)]
struct ContextLock {
    locked_by: AgentId,
    locked_at: chrono::DateTime<chrono::Utc>,
    expires_at: chrono::DateTime<chrono::Utc>,
    lock_type: LockType,
}

#[derive(Debug, Clone)]
enum LockType {
    Read,
    Write,
    Exclusive,
}

#[derive(Debug, Clone)]
struct AgentSubscription {
    agent_id: AgentId,
    filter: SubscriptionFilter,
    created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone)]
struct SubscriptionFilter {
    keys: Option<Vec<String>>,
    operations: Option<Vec<ContextOperation>>,
    agents: Option<Vec<AgentId>>,
}

#[derive(Debug, Clone)]
struct PendingChange {
    change_id: Uuid,
    context_id: Uuid,
    agent_id: AgentId,
    operation: ContextOperation,
    key: String,
    value: Option<Value>,
    timestamp: chrono::DateTime<chrono::Utc>,
    dependencies: Vec<Uuid>,
}

#[derive(Debug)]
struct ConflictDetector {
    conflict_rules: Vec<ConflictRule>,
    resolution_strategies: HashMap<String, ResolutionStrategy>,
}

#[derive(Debug, Clone)]
struct ConflictRule {
    rule_id: String,
    pattern: ConflictPattern,
    severity: ConflictSeverity,
    auto_resolve: bool,
}

#[derive(Debug, Clone)]
enum ConflictPattern {
    ConcurrentWrite { key_pattern: String },
    VersionMismatch { threshold: u64 },
    AgentConflict { excluded_pairs: Vec<(AgentId, AgentId)> },
    ValueConflict { key_pattern: String, value_type: String },
    Custom(String),
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
enum ConflictSeverity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone)]
enum ResolutionStrategy {
    LastWriteWins,
    FirstWriteWins,
    Merge,
    AgentPriority(Vec<AgentId>),
    Manual,
    Custom(String),
}

#[derive(Debug, Clone)]
struct AccessPattern {
    context_id: Uuid,
    read_count: u64,
    write_count: u64,
    last_accessed: chrono::DateTime<chrono::Utc>,
    frequent_keys: HashMap<String, u64>,
    accessing_agents: Vec<AgentId>,
}

#[derive(Debug, Default)]
struct CacheStats {
    cache_hits: u64,
    cache_misses: u64,
    evictions: u64,
    conflicts_detected: u64,
    conflicts_resolved: u64,
    sync_operations: u64,
    lock_contentions: u64,
}

impl ContextManager {
    pub async fn new(
        state_store: Arc<StateStore>,
        message_bus: Arc<MessageBus>,
    ) -> Result<Self> {
        info!("Initializing context manager");
        
        let conflict_detector = Arc::new(ConflictDetector::new());
        let (shutdown_tx, _) = broadcast::channel(1);
        
        Ok(ContextManager {
            state_store,
            message_bus,
            contexts: Arc::new(DashMap::new()),
            locks: Arc::new(DashMap::new()),
            subscriptions: Arc::new(DashMap::new()),
            pending_changes: Arc::new(DashMap::new()),
            conflict_detector,
            access_patterns: Arc::new(DashMap::new()),
            cache_stats: Arc::new(RwLock::new(CacheStats::default())),
            sync_handle: Arc::new(Mutex::new(None)),
            cleanup_handle: Arc::new(Mutex::new(None)),
            shutdown_tx: Arc::new(Mutex::new(Some(shutdown_tx))),
        })
    }
    
    pub async fn start(&self) -> Result<()> {
        info!("Starting context manager");
        
        // Load existing contexts from storage
        self.load_contexts().await?;
        
        // Start background synchronization
        self.start_sync_task().await;
        
        // Start cleanup task
        self.start_cleanup_task().await;
        
        info!("Context manager started successfully");
        Ok(())
    }
    
    pub async fn shutdown(&self) -> Result<()> {
        info!("Shutting down context manager");
        
        // Signal shutdown
        if let Some(tx) = self.shutdown_tx.lock().await.take() {
            let _ = tx.send(());
        }
        
        // Stop background tasks
        if let Some(handle) = self.sync_handle.lock().await.take() {
            handle.abort();
        }
        
        if let Some(handle) = self.cleanup_handle.lock().await.take() {
            handle.abort();
        }
        
        // Persist all contexts
        self.persist_all_contexts().await?;
        
        info!("Context manager shut down successfully");
        Ok(())
    }
    
    /// Create a new shared context
    pub async fn create_context(
        &self,
        session_id: SessionId,
        name: String,
        initial_data: HashMap<String, Value>,
        permissions: Vec<AgentId>,
    ) -> Result<Uuid> {
        let context_id = Uuid::new_v4();
        let now = chrono::Utc::now();
        
        let context = SharedContext {
            id: context_id,
            session_id,
            name: name.clone(),
            data: initial_data,
            version: 1,
            created_at: now,
            updated_at: now,
            access_permissions: permissions,
            locked_by: None,
            lock_expires_at: None,
        };
        
        // Store in cache
        self.contexts.insert(context_id, Arc::new(RwLock::new(context.clone())));
        
        // Persist to storage
        self.state_store.save_context(&context).await?;
        
        // Initialize access pattern tracking
        self.access_patterns.insert(context_id, AccessPattern {
            context_id,
            read_count: 0,
            write_count: 0,
            last_accessed: now,
            frequent_keys: HashMap::new(),
            accessing_agents: Vec::new(),
        });
        
        info!("Created context: {} ({})", name, context_id);
        Ok(context_id)
    }
    
    /// Read a value from shared context
    pub async fn read_context(
        &self,
        context_id: Uuid,
        agent_id: &AgentId,
        key: &str,
    ) -> Result<Option<Value>> {
        // Check permissions and get context
        let context = self.get_context_with_permission(context_id, agent_id, false).await?;
        let context_guard = context.read().await;
        
        // Track access pattern
        self.track_access(context_id, agent_id, key, false).await;
        
        // Update cache stats
        {
            let mut stats = self.cache_stats.write().await;
            stats.cache_hits += 1;
        }
        
        Ok(context_guard.data.get(key).cloned())
    }
    
    /// Write a value to shared context
    pub async fn write_context(
        &self,
        context_id: Uuid,
        agent_id: &AgentId,
        key: String,
        value: Value,
    ) -> Result<()> {
        // Check permissions and get context
        let context = self.get_context_with_permission(context_id, agent_id, true).await?;
        
        // Acquire write lock if needed
        self.acquire_lock(context_id, agent_id, LockType::Write, Duration::from_secs(30)).await?;
        
        // Check for conflicts
        let change = PendingChange {
            change_id: Uuid::new_v4(),
            context_id,
            agent_id: agent_id.clone(),
            operation: ContextOperation::Write,
            key: key.clone(),
            value: Some(value.clone()),
            timestamp: chrono::Utc::now(),
            dependencies: Vec::new(),
        };
        
        if let Some(conflict) = self.detect_conflict(&change).await? {
            return self.handle_conflict(conflict).await;
        }
        
        // Apply the change
        {
            let mut context_guard = context.write().await;
            context_guard.data.insert(key.clone(), value.clone());
            context_guard.version += 1;
            context_guard.updated_at = chrono::Utc::now();
        }
        
        // Track access pattern
        self.track_access(context_id, agent_id, &key, true).await;
        
        // Persist to storage
        let context_guard = context.read().await;
        self.state_store.save_context(&*context_guard).await?;
        
        // Notify subscribers
        self.notify_subscribers(context_id, &change).await?;
        
        // Release lock
        self.release_lock(context_id, agent_id).await?;
        
        debug!("Updated context {} key '{}' by agent {}", context_id, key, agent_id);
        Ok(())
    }
    
    /// Subscribe to context changes
    pub async fn subscribe_to_context(
        &self,
        context_id: Uuid,
        agent_id: AgentId,
        filter: SubscriptionFilter,
    ) -> Result<()> {
        // Check permissions
        let context = self.get_context_with_permission(context_id, &agent_id, false).await?;
        
        let subscription = AgentSubscription {
            agent_id: agent_id.clone(),
            filter,
            created_at: chrono::Utc::now(),
        };
        
        self.subscriptions
            .entry(context_id)
            .or_insert_with(Vec::new)
            .push(subscription);
        
        debug!("Agent {} subscribed to context {}", agent_id, context_id);
        Ok(())
    }
    
    /// Unsubscribe from context changes
    pub async fn unsubscribe_from_context(
        &self,
        context_id: Uuid,
        agent_id: &AgentId,
    ) -> Result<()> {
        if let Some(mut subscriptions) = self.subscriptions.get_mut(&context_id) {
            subscriptions.retain(|s| s.agent_id != *agent_id);
        }
        
        debug!("Agent {} unsubscribed from context {}", agent_id, context_id);
        Ok(())
    }
    
    /// Acquire a lock on a context
    pub async fn acquire_lock(
        &self,
        context_id: Uuid,
        agent_id: &AgentId,
        lock_type: LockType,
        duration: Duration,
    ) -> Result<()> {
        let now = chrono::Utc::now();
        let expires_at = now + chrono::Duration::from_std(duration).unwrap();
        
        // Check if context is already locked
        if let Some(existing_lock) = self.locks.get(&context_id) {
            if existing_lock.expires_at > now && existing_lock.locked_by != *agent_id {
                // Update contention stats
                {
                    let mut stats = self.cache_stats.write().await;
                    stats.lock_contentions += 1;
                }
                
                return Err(OrchestrationError::Communication(
                    format!("Context {} is locked by {}", context_id, existing_lock.locked_by)
                ));
            }
        }
        
        // Acquire the lock
        let lock = ContextLock {
            locked_by: agent_id.clone(),
            locked_at: now,
            expires_at,
            lock_type,
        };
        
        self.locks.insert(context_id, lock);
        
        debug!("Lock acquired on context {} by agent {}", context_id, agent_id);
        Ok(())
    }
    
    /// Release a lock on a context
    pub async fn release_lock(
        &self,
        context_id: Uuid,
        agent_id: &AgentId,
    ) -> Result<()> {
        if let Some((_, lock)) = self.locks.remove(&context_id) {
            if lock.locked_by != *agent_id {
                // Put the lock back if it's not owned by this agent
                self.locks.insert(context_id, lock);
                return Err(OrchestrationError::Communication(
                    format!("Context {} is not locked by agent {}", context_id, agent_id)
                ));
            }
        }
        
        debug!("Lock released on context {} by agent {}", context_id, agent_id);
        Ok(())
    }
    
    /// Get context statistics
    pub async fn get_context_stats(&self, context_id: Uuid) -> Result<ContextStats> {
        let access_pattern = self.access_patterns.get(&context_id)
            .ok_or_else(|| OrchestrationError::Communication(
                format!("Context not found: {}", context_id)
            ))?;
        
        let context = self.contexts.get(&context_id)
            .ok_or_else(|| OrchestrationError::Communication(
                format!("Context not found: {}", context_id)
            ))?;
        
        let context_guard = context.read().await;
        
        Ok(ContextStats {
            context_id,
            version: context_guard.version,
            size_bytes: serde_json::to_vec(&context_guard.data)?.len() as u64,
            read_count: access_pattern.read_count,
            write_count: access_pattern.write_count,
            last_accessed: access_pattern.last_accessed,
            subscribers: self.subscriptions.get(&context_id)
                .map(|s| s.len())
                .unwrap_or(0),
            is_locked: self.locks.contains_key(&context_id),
        })
    }
    
    // Private implementation methods
    
    async fn get_context_with_permission(
        &self,
        context_id: Uuid,
        agent_id: &AgentId,
        write_access: bool,
    ) -> Result<Arc<RwLock<SharedContext>>> {
        let context = self.contexts.get(&context_id)
            .ok_or_else(|| {
                // Try loading from storage
                self.load_context_from_storage(context_id)
            })?;
        
        // Check permissions
        let context_guard = context.read().await;
        if !context_guard.access_permissions.contains(agent_id) &&
           !context_guard.access_permissions.is_empty() {
            return Err(OrchestrationError::Communication(
                format!("Agent {} does not have access to context {}", agent_id, context_id)
            ));
        }
        
        drop(context_guard);
        Ok(context.clone())
    }
    
    fn load_context_from_storage(&self, context_id: Uuid) -> OrchestrationError {
        // This would typically load from storage asynchronously
        // For now, return an error
        OrchestrationError::Communication(
            format!("Context not found: {}", context_id)
        )
    }
    
    async fn load_contexts(&self) -> Result<()> {
        let contexts = self.state_store.load_contexts().await?;
        
        for context in contexts {
            let context_id = context.id;
            self.contexts.insert(context_id, Arc::new(RwLock::new(context)));
            
            // Initialize access pattern
            self.access_patterns.insert(context_id, AccessPattern {
                context_id,
                read_count: 0,
                write_count: 0,
                last_accessed: chrono::Utc::now(),
                frequent_keys: HashMap::new(),
                accessing_agents: Vec::new(),
            });
        }
        
        info!("Loaded {} contexts from storage", self.contexts.len());
        Ok(())
    }
    
    async fn persist_all_contexts(&self) -> Result<()> {
        for entry in self.contexts.iter() {
            let context = entry.value().read().await;
            self.state_store.save_context(&*context).await?;
        }
        
        info!("Persisted {} contexts to storage", self.contexts.len());
        Ok(())
    }
    
    async fn track_access(&self, context_id: Uuid, agent_id: &AgentId, key: &str, is_write: bool) {
        if let Some(mut pattern) = self.access_patterns.get_mut(&context_id) {
            if is_write {
                pattern.write_count += 1;
            } else {
                pattern.read_count += 1;
            }
            
            pattern.last_accessed = chrono::Utc::now();
            
            // Track frequent keys
            *pattern.frequent_keys.entry(key.to_string()).or_insert(0) += 1;
            
            // Track accessing agents
            if !pattern.accessing_agents.contains(agent_id) {
                pattern.accessing_agents.push(agent_id.clone());
            }
        }
    }
    
    async fn detect_conflict(&self, change: &PendingChange) -> Result<Option<DetectedConflict>> {
        // Check pending changes for conflicts
        if let Some(pending) = self.pending_changes.get(&change.context_id) {
            for existing_change in pending.iter() {
                if existing_change.key == change.key &&
                   existing_change.agent_id != change.agent_id &&
                   matches!(existing_change.operation, ContextOperation::Write) {
                    
                    let conflict = DetectedConflict {
                        conflict_id: Uuid::new_v4(),
                        context_id: change.context_id,
                        conflicting_changes: vec![existing_change.clone(), change.clone()],
                        conflict_type: super::ConflictType::ContextUpdate,
                        severity: ConflictSeverity::Medium,
                        detected_at: chrono::Utc::now(),
                    };
                    
                    // Update stats
                    {
                        let mut stats = self.cache_stats.write().await;
                        stats.conflicts_detected += 1;
                    }
                    
                    return Ok(Some(conflict));
                }
            }
        }
        
        Ok(None)
    }
    
    async fn handle_conflict(&self, conflict: DetectedConflict) -> Result<()> {
        warn!("Conflict detected in context {}: {:?}", conflict.context_id, conflict.conflict_type);
        
        // Try to resolve automatically based on severity and rules
        match conflict.severity {
            ConflictSeverity::Low | ConflictSeverity::Medium => {
                // Use last-write-wins strategy for now
                self.resolve_conflict_auto(&conflict).await?;
            }
            ConflictSeverity::High | ConflictSeverity::Critical => {
                // Require manual resolution
                self.escalate_conflict(&conflict).await?;
            }
        }
        
        // Update stats
        {
            let mut stats = self.cache_stats.write().await;
            stats.conflicts_resolved += 1;
        }
        
        Ok(())
    }
    
    async fn resolve_conflict_auto(&self, conflict: &DetectedConflict) -> Result<()> {
        debug!("Auto-resolving conflict {}", conflict.conflict_id);
        
        // For now, implement last-write-wins
        if let Some(latest_change) = conflict.conflicting_changes
            .iter()
            .max_by_key(|c| c.timestamp) {
            
            // Apply the latest change
            if let Some(context) = self.contexts.get(&conflict.context_id) {
                let mut context_guard = context.write().await;
                
                if let Some(value) = &latest_change.value {
                    context_guard.data.insert(latest_change.key.clone(), value.clone());
                    context_guard.version += 1;
                    context_guard.updated_at = chrono::Utc::now();
                }
            }
        }
        
        Ok(())
    }
    
    async fn escalate_conflict(&self, conflict: &DetectedConflict) -> Result<()> {
        warn!("Escalating conflict {} for manual resolution", conflict.conflict_id);
        
        // Send conflict message to coordination channel
        let message = Message::new(
            "context_manager".to_string(),
            MessageRecipient::All,
            Channel::ConflictResolution,
            MessageType::ConflictDetected,
            MessagePayload::ConflictData {
                conflict_id: conflict.conflict_id,
                conflict_type: conflict.conflict_type.clone(),
                involved_agents: conflict.conflicting_changes
                    .iter()
                    .map(|c| c.agent_id.clone())
                    .collect(),
                data: serde_json::to_value(conflict)?,
                proposed_resolution: None,
            },
        );
        
        self.message_bus.publish(message).await?;
        Ok(())
    }
    
    async fn notify_subscribers(&self, context_id: Uuid, change: &PendingChange) -> Result<()> {
        if let Some(subscriptions) = self.subscriptions.get(&context_id) {
            for subscription in subscriptions.iter() {
                if self.matches_subscription_filter(&subscription.filter, change) {
                    let event = RealtimeEvent::new(
                        EventType::Custom("context_update".to_string()),
                        serde_json::to_value(change)?,
                    );
                    
                    // Send via message bus
                    let message = Message::new(
                        "context_manager".to_string(),
                        MessageRecipient::Agent(subscription.agent_id.clone()),
                        Channel::ContextSync,
                        MessageType::ContextUpdate,
                        MessagePayload::ContextOperation {
                            context_id: change.context_id,
                            operation: change.operation.clone(),
                            key: change.key.clone(),
                            value: change.value.clone(),
                            version: 0, // Will be updated with actual version
                        },
                    );
                    
                    self.message_bus.publish(message).await?;
                }
            }
        }
        
        Ok(())
    }
    
    fn matches_subscription_filter(&self, filter: &SubscriptionFilter, change: &PendingChange) -> bool {
        // Check key filter
        if let Some(keys) = &filter.keys {
            if !keys.contains(&change.key) {
                return false;
            }
        }
        
        // Check operation filter
        if let Some(operations) = &filter.operations {
            if !operations.contains(&change.operation) {
                return false;
            }
        }
        
        // Check agent filter
        if let Some(agents) = &filter.agents {
            if !agents.contains(&change.agent_id) {
                return false;
            }
        }
        
        true
    }
    
    async fn start_sync_task(&self) {
        let contexts = self.contexts.clone();
        let state_store = self.state_store.clone();
        let cache_stats = self.cache_stats.clone();
        
        let shutdown_rx = {
            let tx = self.shutdown_tx.lock().await;
            tx.as_ref().unwrap().subscribe()
        };
        
        let handle = tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(60));
            let mut shutdown_rx = shutdown_rx;
            
            loop {
                tokio::select! {
                    _ = interval.tick() => {
                        Self::sync_contexts(&contexts, &state_store, &cache_stats).await;
                    }
                    _ = shutdown_rx.recv() => break,
                }
            }
        });
        
        *self.sync_handle.lock().await = Some(handle);
    }
    
    async fn start_cleanup_task(&self) {
        let locks = self.locks.clone();
        let pending_changes = self.pending_changes.clone();
        
        let shutdown_rx = {
            let tx = self.shutdown_tx.lock().await;
            tx.as_ref().unwrap().subscribe()
        };
        
        let handle = tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(30));
            let mut shutdown_rx = shutdown_rx;
            
            loop {
                tokio::select! {
                    _ = interval.tick() => {
                        Self::cleanup_expired_locks(&locks).await;
                        Self::cleanup_old_pending_changes(&pending_changes).await;
                    }
                    _ = shutdown_rx.recv() => break,
                }
            }
        });
        
        *self.cleanup_handle.lock().await = Some(handle);
    }
    
    async fn sync_contexts(
        contexts: &DashMap<Uuid, Arc<RwLock<SharedContext>>>,
        state_store: &StateStore,
        cache_stats: &RwLock<CacheStats>,
    ) {
        let mut synced = 0;
        
        for entry in contexts.iter() {
            if let Ok(context) = entry.value().try_read() {
                if let Err(e) = state_store.save_context(&*context).await {
                    warn!("Failed to sync context {}: {}", entry.key(), e);
                } else {
                    synced += 1;
                }
            }
        }
        
        // Update stats
        {
            let mut stats = cache_stats.write().await;
            stats.sync_operations += synced;
        }
        
        if synced > 0 {
            debug!("Synced {} contexts to storage", synced);
        }
    }
    
    async fn cleanup_expired_locks(locks: &DashMap<Uuid, ContextLock>) {
        let now = chrono::Utc::now();
        let mut expired = Vec::new();
        
        for entry in locks.iter() {
            if entry.value().expires_at < now {
                expired.push(*entry.key());
            }
        }
        
        for context_id in expired {
            locks.remove(&context_id);
            debug!("Cleaned up expired lock for context {}", context_id);
        }
    }
    
    async fn cleanup_old_pending_changes(pending_changes: &DashMap<Uuid, Vec<PendingChange>>) {
        let now = chrono::Utc::now();
        let max_age = chrono::Duration::minutes(10);
        
        for mut entry in pending_changes.iter_mut() {
            entry.retain(|change| {
                now.signed_duration_since(change.timestamp) < max_age
            });
        }
        
        // Remove empty entries
        pending_changes.retain(|_, changes| !changes.is_empty());
    }
}

impl ConflictDetector {
    fn new() -> Self {
        ConflictDetector {
            conflict_rules: Vec::new(),
            resolution_strategies: HashMap::new(),
        }
    }
}

#[derive(Debug, Clone)]
struct DetectedConflict {
    conflict_id: Uuid,
    context_id: Uuid,
    conflicting_changes: Vec<PendingChange>,
    conflict_type: super::ConflictType,
    severity: ConflictSeverity,
    detected_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone)]
pub struct ContextStats {
    pub context_id: Uuid,
    pub version: u64,
    pub size_bytes: u64,
    pub read_count: u64,
    pub write_count: u64,
    pub last_accessed: chrono::DateTime<chrono::Utc>,
    pub subscribers: usize,
    pub is_locked: bool,
}