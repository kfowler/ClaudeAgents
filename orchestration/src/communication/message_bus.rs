use std::sync::Arc;
use std::collections::HashMap;
use std::time::Duration;
use tokio::sync::{RwLock, Mutex, broadcast, mpsc};
use tokio::time::{timeout, sleep};
use tracing::{info, warn, error, debug};
use dashmap::DashMap;
use redis::aio::MultiplexedConnection;
use lapin::{Connection, Channel as RabbitChannel, Queue};
use uuid::Uuid;

use crate::config::{MessageQueueConfig, RedisConfig};
use crate::error::{Result, OrchestrationError};
use super::{
    Message, MessageId, AgentId, Channel, MessageAck, AckStatus,
    MessagePriority, DeliveryOptions, QueueStats, CircuitBreakerStats,
    CircuitBreakerState
};

/// High-performance message bus for inter-agent communication
pub struct MessageBus {
    config: MessageQueueConfig,
    redis_config: RedisConfig,
    
    // Redis connection pool
    redis_pool: Arc<RwLock<Vec<MultiplexedConnection>>>,
    
    // RabbitMQ connection and channels
    rabbit_connection: Option<Connection>,
    rabbit_channels: Arc<DashMap<String, RabbitChannel>>,
    
    // In-memory message routing
    subscribers: Arc<DashMap<Channel, Vec<MessageSubscriber>>>,
    message_handlers: Arc<DashMap<AgentId, mpsc::UnboundedSender<Message>>>,
    
    // Message tracking and acknowledgments
    pending_messages: Arc<DashMap<MessageId, PendingMessage>>,
    acknowledgments: Arc<DashMap<MessageId, MessageAck>>,
    
    // Circuit breakers for fault tolerance
    circuit_breakers: Arc<DashMap<String, CircuitBreaker>>,
    
    // Performance metrics
    queue_stats: Arc<DashMap<String, QueueStats>>,
    
    // Background task handles
    cleanup_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
    stats_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
    
    // Shutdown coordination
    shutdown_tx: Arc<Mutex<Option<broadcast::Sender<()>>>>,
}

#[derive(Debug, Clone)]
struct MessageSubscriber {
    agent_id: AgentId,
    sender: mpsc::UnboundedSender<Message>,
    filter: Option<MessageFilter>,
}

#[derive(Debug, Clone)]
struct MessageFilter {
    message_types: Option<Vec<String>>,
    priority_threshold: Option<MessagePriority>,
    metadata_filters: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone)]
struct PendingMessage {
    message: Message,
    retry_count: u32,
    next_retry_at: chrono::DateTime<chrono::Utc>,
    created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone)]
struct CircuitBreaker {
    state: CircuitBreakerState,
    failure_count: u32,
    success_count: u32,
    last_failure: Option<chrono::DateTime<chrono::Utc>>,
    threshold: f32,
    timeout_ms: u64,
}

impl MessageBus {
    pub async fn new(
        mq_config: &MessageQueueConfig,
        redis_config: &RedisConfig,
    ) -> Result<Self> {
        info!("Initializing message bus");
        
        // Initialize Redis connection pool
        let redis_pool = Self::init_redis_pool(redis_config).await?;
        
        // Initialize RabbitMQ connection
        let rabbit_connection = if let Some(url) = &mq_config.rabbitmq_url {
            Some(Connection::connect(url, lapin::ConnectionProperties::default()).await?)
        } else {
            None
        };
        
        let (shutdown_tx, _) = broadcast::channel(1);
        
        Ok(MessageBus {
            config: mq_config.clone(),
            redis_config: redis_config.clone(),
            redis_pool: Arc::new(RwLock::new(redis_pool)),
            rabbit_connection,
            rabbit_channels: Arc::new(DashMap::new()),
            subscribers: Arc::new(DashMap::new()),
            message_handlers: Arc::new(DashMap::new()),
            pending_messages: Arc::new(DashMap::new()),
            acknowledgments: Arc::new(DashMap::new()),
            circuit_breakers: Arc::new(DashMap::new()),
            queue_stats: Arc::new(DashMap::new()),
            cleanup_handle: Arc::new(Mutex::new(None)),
            stats_handle: Arc::new(Mutex::new(None)),
            shutdown_tx: Arc::new(Mutex::new(Some(shutdown_tx))),
        })
    }
    
    pub async fn start(&self) -> Result<()> {
        info!("Starting message bus");
        
        // Start background cleanup task
        self.start_cleanup_task().await;
        
        // Start statistics collection task
        self.start_stats_task().await;
        
        // Initialize message queues
        self.init_queues().await?;
        
        info!("Message bus started successfully");
        Ok(())
    }
    
    pub async fn shutdown(&self) -> Result<()> {
        info!("Shutting down message bus");
        
        // Signal shutdown to background tasks
        if let Some(tx) = self.shutdown_tx.lock().await.take() {
            let _ = tx.send(());
        }
        
        // Wait for background tasks to complete
        if let Some(handle) = self.cleanup_handle.lock().await.take() {
            handle.abort();
        }
        
        if let Some(handle) = self.stats_handle.lock().await.take() {
            handle.abort();
        }
        
        // Close RabbitMQ connection
        if let Some(connection) = &self.rabbit_connection {
            connection.close(0, "Shutting down").await?;
        }
        
        info!("Message bus shut down successfully");
        Ok(())
    }
    
    /// Publish a message to the specified channel
    pub async fn publish(&self, message: Message) -> Result<()> {
        let channel_key = message.channel.clone();
        let routing_key = message.routing_key();
        
        // Check circuit breaker
        if !self.check_circuit_breaker(&routing_key).await {
            return Err(OrchestrationError::Communication(
                format!("Circuit breaker open for route: {}", routing_key)
            ));
        }
        
        // Handle different delivery options
        match message.delivery_options.guaranteed_delivery {
            true => self.publish_reliable(message).await,
            false => self.publish_best_effort(message).await,
        }
    }
    
    /// Subscribe to messages on a specific channel
    pub async fn subscribe(
        &self,
        agent_id: AgentId,
        channel: Channel,
        filter: Option<MessageFilter>,
    ) -> Result<mpsc::UnboundedReceiver<Message>> {
        let (tx, rx) = mpsc::unbounded_channel();
        
        let subscriber = MessageSubscriber {
            agent_id: agent_id.clone(),
            sender: tx.clone(),
            filter,
        };
        
        // Add to channel subscribers
        self.subscribers
            .entry(channel.clone())
            .or_insert_with(Vec::new)
            .push(subscriber);
        
        // Store handler for direct messaging
        self.message_handlers.insert(agent_id.clone(), tx);
        
        debug!("Agent {} subscribed to channel {:?}", agent_id, channel);
        Ok(rx)
    }
    
    /// Unsubscribe from a channel
    pub async fn unsubscribe(&self, agent_id: &AgentId, channel: &Channel) -> Result<()> {
        if let Some(mut subscribers) = self.subscribers.get_mut(channel) {
            subscribers.retain(|s| s.agent_id != *agent_id);
        }
        
        debug!("Agent {} unsubscribed from channel {:?}", agent_id, channel);
        Ok(())
    }
    
    /// Send acknowledgment for a message
    pub async fn acknowledge(&self, message_id: MessageId, agent_id: AgentId, status: AckStatus) -> Result<()> {
        let ack = MessageAck {
            message_id,
            recipient: agent_id.clone(),
            status: status.clone(),
            timestamp: chrono::Utc::now(),
            response_data: None,
            error_message: None,
        };
        
        self.acknowledgments.insert(message_id, ack);
        
        // Remove from pending if successfully processed
        if matches!(status, AckStatus::Processed) {
            self.pending_messages.remove(&message_id);
            self.record_success(&format!("ack.{}", agent_id)).await;
        } else if matches!(status, AckStatus::Failed) {
            self.record_failure(&format!("ack.{}", agent_id)).await;
        }
        
        debug!("Message {} acknowledged by {} with status {:?}", message_id, agent_id, status);
        Ok(())
    }
    
    /// Get message statistics
    pub async fn get_stats(&self) -> HashMap<String, QueueStats> {
        self.queue_stats
            .iter()
            .map(|entry| (entry.key().clone(), entry.value().clone()))
            .collect()
    }
    
    /// Check if message bus is healthy
    pub async fn is_healthy(&self) -> bool {
        // Check Redis connectivity
        let redis_healthy = self.check_redis_health().await;
        
        // Check RabbitMQ connectivity
        let rabbit_healthy = if self.rabbit_connection.is_some() {
            self.check_rabbit_health().await
        } else {
            true // No RabbitMQ configured
        };
        
        // Check circuit breaker states
        let circuit_breakers_healthy = self.circuit_breakers
            .iter()
            .all(|entry| !matches!(entry.value().state, CircuitBreakerState::Open));
        
        redis_healthy && rabbit_healthy && circuit_breakers_healthy
    }
    
    // Private implementation methods
    
    async fn publish_reliable(&self, message: Message) -> Result<()> {
        let message_id = message.id;
        let routing_key = message.routing_key();
        
        // Store as pending message
        let pending = PendingMessage {
            message: message.clone(),
            retry_count: 0,
            next_retry_at: chrono::Utc::now(),
            created_at: chrono::Utc::now(),
        };
        self.pending_messages.insert(message_id, pending);
        
        // Attempt delivery
        match self.deliver_message(message).await {
            Ok(_) => {
                self.record_success(&routing_key).await;
                Ok(())
            }
            Err(e) => {
                self.record_failure(&routing_key).await;
                Err(e)
            }
        }
    }
    
    async fn publish_best_effort(&self, message: Message) -> Result<()> {
        let routing_key = message.routing_key();
        
        match self.deliver_message(message).await {
            Ok(_) => {
                self.record_success(&routing_key).await;
                Ok(())
            }
            Err(e) => {
                self.record_failure(&routing_key).await;
                warn!("Best-effort message delivery failed: {}", e);
                Ok(()) // Don't propagate error for best-effort
            }
        }
    }
    
    async fn deliver_message(&self, message: Message) -> Result<()> {
        // Try in-memory delivery first (fastest)
        if self.deliver_in_memory(&message).await {
            return Ok(());
        }
        
        // Try Redis pub/sub (medium latency)
        if self.deliver_via_redis(&message).await? {
            return Ok(());
        }
        
        // Fall back to RabbitMQ (reliable but higher latency)
        if self.rabbit_connection.is_some() {
            self.deliver_via_rabbitmq(&message).await?;
            return Ok(());
        }
        
        Err(OrchestrationError::Communication(
            "No available delivery method".to_string()
        ))
    }
    
    async fn deliver_in_memory(&self, message: &Message) -> bool {
        let mut delivered = false;
        
        // Direct messaging to specific agent
        if let super::MessageRecipient::Agent(agent_id) = &message.recipient {
            if let Some(handler) = self.message_handlers.get(agent_id) {
                if handler.send(message.clone()).is_ok() {
                    delivered = true;
                }
            }
        }
        
        // Channel-based delivery
        if let Some(subscribers) = self.subscribers.get(&message.channel) {
            for subscriber in subscribers.iter() {
                if self.matches_filter(&subscriber.filter, message) {
                    if subscriber.sender.send(message.clone()).is_ok() {
                        delivered = true;
                    }
                }
            }
        }
        
        delivered
    }
    
    async fn deliver_via_redis(&self, message: &Message) -> Result<bool> {
        let serialized = serde_json::to_string(message)?;
        let routing_key = message.routing_key();
        
        let redis_pool = self.redis_pool.read().await;
        if let Some(mut conn) = redis_pool.first().cloned() {
            drop(redis_pool); // Release lock early
            
            match redis::cmd("PUBLISH")
                .arg(&routing_key)
                .arg(&serialized)
                .query_async::<_, i32>(&mut conn)
                .await
            {
                Ok(subscriber_count) => Ok(subscriber_count > 0),
                Err(e) => {
                    warn!("Redis publish failed: {}", e);
                    Ok(false)
                }
            }
        } else {
            Ok(false)
        }
    }
    
    async fn deliver_via_rabbitmq(&self, message: &Message) -> Result<()> {
        if let Some(connection) = &self.rabbit_connection {
            let channel = connection.create_channel().await?;
            let routing_key = message.routing_key();
            let serialized = serde_json::to_vec(message)?;
            
            // Declare exchange if not exists
            channel.exchange_declare(
                "orchestration",
                lapin::ExchangeKind::Topic,
                lapin::options::ExchangeDeclareOptions::default(),
                lapin::types::FieldTable::default(),
            ).await?;
            
            // Publish message
            channel.basic_publish(
                "orchestration",
                &routing_key,
                lapin::options::BasicPublishOptions::default(),
                &serialized,
                lapin::BasicProperties::default()
                    .with_priority(message.priority as u8)
                    .with_correlation_id(
                        message.correlation_id
                            .map(|id| id.to_string().into())
                            .unwrap_or_else(|| message.id.to_string().into())
                    ),
            ).await?;
            
            Ok(())
        } else {
            Err(OrchestrationError::Communication(
                "RabbitMQ connection not available".to_string()
            ))
        }
    }
    
    async fn check_circuit_breaker(&self, route: &str) -> bool {
        if let Some(breaker) = self.circuit_breakers.get(route) {
            match breaker.state {
                CircuitBreakerState::Closed => true,
                CircuitBreakerState::Open => {
                    // Check if timeout has passed
                    if let Some(last_failure) = breaker.last_failure {
                        let timeout = chrono::Duration::milliseconds(breaker.timeout_ms as i64);
                        if chrono::Utc::now() - last_failure > timeout {
                            // Transition to half-open
                            drop(breaker);
                            if let Some(mut breaker) = self.circuit_breakers.get_mut(route) {
                                breaker.state = CircuitBreakerState::HalfOpen;
                            }
                            true
                        } else {
                            false
                        }
                    } else {
                        false
                    }
                }
                CircuitBreakerState::HalfOpen => true,
            }
        } else {
            // Initialize circuit breaker
            let breaker = CircuitBreaker {
                state: CircuitBreakerState::Closed,
                failure_count: 0,
                success_count: 0,
                last_failure: None,
                threshold: 0.5, // 50% failure rate threshold
                timeout_ms: 30000, // 30 seconds
            };
            self.circuit_breakers.insert(route.to_string(), breaker);
            true
        }
    }
    
    async fn record_success(&self, route: &str) {
        if let Some(mut breaker) = self.circuit_breakers.get_mut(route) {
            breaker.success_count += 1;
            
            // Reset circuit breaker if enough successes in half-open state
            if matches!(breaker.state, CircuitBreakerState::HalfOpen) && breaker.success_count >= 5 {
                breaker.state = CircuitBreakerState::Closed;
                breaker.failure_count = 0;
                breaker.success_count = 0;
            }
        }
    }
    
    async fn record_failure(&self, route: &str) {
        if let Some(mut breaker) = self.circuit_breakers.get_mut(route) {
            breaker.failure_count += 1;
            breaker.last_failure = Some(chrono::Utc::now());
            
            // Check if should open circuit breaker
            let total_requests = breaker.failure_count + breaker.success_count;
            if total_requests >= 10 {
                let failure_rate = breaker.failure_count as f32 / total_requests as f32;
                if failure_rate >= breaker.threshold {
                    breaker.state = CircuitBreakerState::Open;
                }
            }
        }
    }
    
    fn matches_filter(&self, filter: &Option<MessageFilter>, message: &Message) -> bool {
        if let Some(filter) = filter {
            // Check message type filter
            if let Some(types) = &filter.message_types {
                let message_type = format!("{:?}", message.message_type);
                if !types.contains(&message_type) {
                    return false;
                }
            }
            
            // Check priority filter
            if let Some(threshold) = &filter.priority_threshold {
                if message.priority < *threshold {
                    return false;
                }
            }
            
            // Check metadata filters
            for (key, expected_value) in &filter.metadata_filters {
                if let Some(actual_value) = message.metadata.get(key) {
                    if actual_value != expected_value {
                        return false;
                    }
                } else {
                    return false;
                }
            }
        }
        
        true
    }
    
    async fn init_redis_pool(config: &RedisConfig) -> Result<Vec<MultiplexedConnection>> {
        let mut connections = Vec::new();
        
        for url in &config.urls {
            let client = redis::Client::open(url.as_str())?;
            let conn = client.get_multiplexed_tokio_connection().await?;
            connections.push(conn);
        }
        
        Ok(connections)
    }
    
    async fn init_queues(&self) -> Result<()> {
        if let Some(connection) = &self.rabbit_connection {
            let channel = connection.create_channel().await?;
            
            // Declare main orchestration exchange
            channel.exchange_declare(
                "orchestration",
                lapin::ExchangeKind::Topic,
                lapin::options::ExchangeDeclareOptions::default(),
                lapin::types::FieldTable::default(),
            ).await?;
            
            // Declare queues for different message types
            let queues = vec![
                "task.execution",
                "agent.coordination",
                "context.sync",
                "conflict.resolution",
                "resource.management",
                "health.check",
            ];
            
            for queue_name in queues {
                channel.queue_declare(
                    queue_name,
                    lapin::options::QueueDeclareOptions {
                        durable: true,
                        ..Default::default()
                    },
                    lapin::types::FieldTable::default(),
                ).await?;
                
                // Bind queue to exchange
                channel.queue_bind(
                    queue_name,
                    "orchestration",
                    queue_name,
                    lapin::options::QueueBindOptions::default(),
                    lapin::types::FieldTable::default(),
                ).await?;
            }
        }
        
        Ok(())
    }
    
    async fn start_cleanup_task(&self) {
        let pending_messages = self.pending_messages.clone();
        let acknowledgments = self.acknowledgments.clone();
        let config = self.config.clone();
        
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
                        Self::cleanup_expired_messages(&pending_messages, &acknowledgments, &config).await;
                    }
                    _ = shutdown_rx.recv() => break,
                }
            }
        });
        
        *self.cleanup_handle.lock().await = Some(handle);
    }
    
    async fn start_stats_task(&self) {
        let queue_stats = self.queue_stats.clone();
        let rabbit_connection = self.rabbit_connection.clone();
        
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
                        if let Some(connection) = &rabbit_connection {
                            Self::collect_queue_stats(&queue_stats, connection).await;
                        }
                    }
                    _ = shutdown_rx.recv() => break,
                }
            }
        });
        
        *self.stats_handle.lock().await = Some(handle);
    }
    
    async fn cleanup_expired_messages(
        pending_messages: &DashMap<MessageId, PendingMessage>,
        acknowledgments: &DashMap<MessageId, MessageAck>,
        config: &MessageQueueConfig,
    ) {
        let now = chrono::Utc::now();
        let max_age = chrono::Duration::seconds(3600); // 1 hour
        
        // Clean up old acknowledgments
        acknowledgments.retain(|_, ack| {
            now.signed_duration_since(ack.timestamp) < max_age
        });
        
        // Clean up expired pending messages
        pending_messages.retain(|_, pending| {
            let age = now.signed_duration_since(pending.created_at);
            let expired = age > max_age;
            let max_retries_exceeded = pending.retry_count >= config.retry_policy.max_attempts;
            
            !(expired || max_retries_exceeded)
        });
    }
    
    async fn collect_queue_stats(
        queue_stats: &DashMap<String, QueueStats>,
        connection: &Connection,
    ) {
        if let Ok(channel) = connection.create_channel().await {
            let queues = vec![
                "task.execution",
                "agent.coordination", 
                "context.sync",
                "conflict.resolution",
                "resource.management",
                "health.check",
            ];
            
            for queue_name in queues {
                if let Ok(queue) = channel.queue_declare(
                    queue_name,
                    lapin::options::QueueDeclareOptions::default(),
                    lapin::types::FieldTable::default(),
                ).await {
                    let stats = QueueStats {
                        queue_name: queue_name.to_string(),
                        message_count: queue.message_count() as u64,
                        consumer_count: queue.consumer_count(),
                        published_rate: 0.0, // Would need more complex tracking
                        consumed_rate: 0.0, // Would need more complex tracking
                        average_latency_ms: 0.0, // Would need message timing
                        error_rate: 0.0, // Would need error tracking
                        last_updated: chrono::Utc::now(),
                    };
                    
                    queue_stats.insert(queue_name.to_string(), stats);
                }
            }
        }
    }
    
    async fn check_redis_health(&self) -> bool {
        let redis_pool = self.redis_pool.read().await;
        if let Some(mut conn) = redis_pool.first().cloned() {
            drop(redis_pool);
            
            match timeout(
                Duration::from_millis(5000),
                redis::cmd("PING").query_async::<_, String>(&mut conn)
            ).await {
                Ok(Ok(response)) => response == "PONG",
                _ => false,
            }
        } else {
            false
        }
    }
    
    async fn check_rabbit_health(&self) -> bool {
        if let Some(connection) = &self.rabbit_connection {
            connection.status().connected()
        } else {
            true // No RabbitMQ configured
        }
    }
}