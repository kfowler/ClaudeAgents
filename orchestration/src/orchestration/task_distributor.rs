use std::sync::Arc;
use std::collections::HashMap;
use std::time::Duration;
use tokio::sync::{RwLock, Mutex, broadcast};
use tokio::time::Instant;
use tracing::{info, warn, error, debug};
use dashmap::DashMap;
use uuid::Uuid;
use serde::{Deserialize, Serialize};

use crate::config::Config;
use crate::error::{Result, OrchestrationError};
use crate::agents::AgentRegistry;
use crate::communication::{MessageBus, Message, MessageType, MessagePayload, MessageRecipient, Channel};
use super::{
    Task, Agent, TaskId, AgentId, TaskStatus, AgentStatus, TaskRequirements,
    LoadBalancingStrategy, ResourceManager
};

/// Intelligent task distribution and load balancing engine
pub struct TaskDistributor {
    config: Arc<Config>,
    agent_registry: Arc<AgentRegistry>,
    resource_manager: Arc<ResourceManager>,
    message_bus: Arc<MessageBus>,
    
    // Task assignment tracking
    task_assignments: Arc<DashMap<TaskId, TaskAssignment>>,
    agent_workloads: Arc<DashMap<AgentId, AgentWorkload>>,
    
    // Load balancing algorithms
    load_balancers: Arc<DashMap<String, Box<dyn LoadBalancer + Send + Sync>>>,
    
    // Assignment strategies and policies
    assignment_policies: Arc<RwLock<Vec<AssignmentPolicy>>>,
    capability_matcher: Arc<CapabilityMatcher>,
    
    // Performance tracking
    assignment_metrics: Arc<RwLock<AssignmentMetrics>>,
    historical_performance: Arc<DashMap<AgentId, PerformanceHistory>>,
    
    // Background optimization
    optimization_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
    rebalance_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
    
    // Shutdown coordination
    shutdown_tx: Arc<Mutex<Option<broadcast::Sender<()>>>>,
}

#[derive(Debug, Clone)]
struct TaskAssignment {
    task_id: TaskId,
    assigned_agents: Vec<AgentId>,
    assignment_strategy: AssignmentStrategy,
    assigned_at: chrono::DateTime<chrono::Utc>,
    started_at: Option<chrono::DateTime<chrono::Utc>>,
    estimated_completion: Option<chrono::DateTime<chrono::Utc>>,
    actual_completion: Option<chrono::DateTime<chrono::Utc>>,
    assignment_score: f32,
    retries: u32,
}

#[derive(Debug, Clone)]
struct AgentWorkload {
    agent_id: AgentId,
    active_tasks: Vec<TaskId>,
    pending_tasks: Vec<TaskId>,
    current_load: f32,
    capacity: f32,
    specialization_scores: HashMap<String, f32>,
    last_updated: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum AssignmentStrategy {
    SingleAgent,
    MultiAgent { coordination_mode: CoordinationMode },
    Pipeline { stages: Vec<AgentId> },
    Redundant { redundancy_factor: usize },
    Adaptive,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
enum CoordinationMode {
    Independent,
    Collaborative,
    LeaderFollower,
    Consensus,
}

#[derive(Debug, Clone)]
struct AssignmentPolicy {
    policy_id: String,
    priority: i32,
    conditions: Vec<AssignmentCondition>,
    action: AssignmentAction,
    enabled: bool,
}

#[derive(Debug, Clone)]
enum AssignmentCondition {
    RequiredCapability(String),
    PreferredAgent(AgentId),
    ExcludedAgent(AgentId),
    LoadThreshold(f32),
    PerformanceThreshold(f32),
    ResourceRequirement(String, f32),
    Custom(String),
}

#[derive(Debug, Clone)]
enum AssignmentAction {
    Assign(AssignmentStrategy),
    Reject(String),
    Defer(Duration),
    Escalate(String),
    Custom(String),
}

trait LoadBalancer {
    fn select_agents(
        &self,
        task: &Task,
        available_agents: &[Agent],
        workloads: &HashMap<AgentId, AgentWorkload>,
    ) -> Result<Vec<AgentId>>;
    
    fn calculate_score(
        &self,
        task: &Task,
        agent: &Agent,
        workload: &AgentWorkload,
    ) -> f32;
}

struct RoundRobinBalancer {
    next_agent_index: Arc<Mutex<usize>>,
}

struct LeastConnectionsBalancer;
struct WeightedRoundRobinBalancer;
struct ConsistentHashBalancer;
struct AdaptiveLoadBalancer {
    performance_history: Arc<DashMap<AgentId, PerformanceHistory>>,
}

#[derive(Debug)]
struct CapabilityMatcher {
    capability_weights: HashMap<String, f32>,
    similarity_threshold: f32,
}

#[derive(Debug, Default)]
struct AssignmentMetrics {
    total_assignments: u64,
    successful_assignments: u64,
    failed_assignments: u64,
    avg_assignment_time_ms: f64,
    avg_task_completion_time_ms: f64,
    load_balance_efficiency: f32,
    agent_utilization: HashMap<AgentId, f32>,
    capability_match_accuracy: f32,
}

#[derive(Debug, Clone, Default)]
struct PerformanceHistory {
    agent_id: AgentId,
    completed_tasks: u64,
    failed_tasks: u64,
    avg_completion_time_ms: f64,
    success_rate: f32,
    capability_performance: HashMap<String, f32>,
    load_handling: f32,
    reliability_score: f32,
    last_updated: chrono::DateTime<chrono::Utc>,
}

impl TaskDistributor {
    pub async fn new(
        config: Arc<Config>,
        agent_registry: Arc<AgentRegistry>,
        resource_manager: Arc<ResourceManager>,
        message_bus: Arc<MessageBus>,
    ) -> Result<Self> {
        info!("Initializing task distributor");
        
        let capability_matcher = Arc::new(CapabilityMatcher::new());
        let (shutdown_tx, _) = broadcast::channel(1);
        
        let mut distributor = TaskDistributor {
            config: config.clone(),
            agent_registry,
            resource_manager,
            message_bus,
            task_assignments: Arc::new(DashMap::new()),
            agent_workloads: Arc::new(DashMap::new()),
            load_balancers: Arc::new(DashMap::new()),
            assignment_policies: Arc::new(RwLock::new(Vec::new())),
            capability_matcher,
            assignment_metrics: Arc::new(RwLock::new(AssignmentMetrics::default())),
            historical_performance: Arc::new(DashMap::new()),
            optimization_handle: Arc::new(Mutex::new(None)),
            rebalance_handle: Arc::new(Mutex::new(None)),
            shutdown_tx: Arc::new(Mutex::new(Some(shutdown_tx))),
        };
        
        // Initialize load balancers
        distributor.init_load_balancers().await?;
        
        // Initialize assignment policies
        distributor.init_assignment_policies().await?;
        
        info!("Task distributor initialized successfully");
        Ok(distributor)
    }
    
    pub async fn start(&self) -> Result<()> {
        info!("Starting task distributor");
        
        // Start performance optimization task
        self.start_optimization_task().await;
        
        // Start load rebalancing task
        self.start_rebalancing_task().await;
        
        info!("Task distributor started successfully");
        Ok(())
    }
    
    pub async fn shutdown(&self) -> Result<()> {
        info!("Shutting down task distributor");
        
        // Signal shutdown
        if let Some(tx) = self.shutdown_tx.lock().await.take() {
            let _ = tx.send(());
        }
        
        // Stop background tasks
        if let Some(handle) = self.optimization_handle.lock().await.take() {
            handle.abort();
        }
        
        if let Some(handle) = self.rebalance_handle.lock().await.take() {
            handle.abort();
        }
        
        info!("Task distributor shut down successfully");
        Ok(())
    }
    
    /// Assign a task to appropriate agents
    pub async fn assign_task(&self, task: &Task) -> Result<Vec<AgentId>> {
        let assignment_start = Instant::now();
        
        debug!("Assigning task: {} ({})", task.name, task.id);
        
        // Get available agents
        let available_agents = self.get_available_agents(&task.requirements).await?;
        
        if available_agents.is_empty() {
            return Err(OrchestrationError::Agent(
                "No available agents for task requirements".to_string()
            ));
        }
        
        // Apply assignment policies
        let policy_result = self.apply_assignment_policies(task, &available_agents).await?;
        
        match policy_result {
            PolicyResult::Assign(strategy) => {
                let selected_agents = self.select_agents_for_task(task, &available_agents, &strategy).await?;
                
                // Create task assignment record
                let assignment = TaskAssignment {
                    task_id: task.id,
                    assigned_agents: selected_agents.clone(),
                    assignment_strategy: strategy,
                    assigned_at: chrono::Utc::now(),
                    started_at: None,
                    estimated_completion: self.estimate_completion_time(task, &selected_agents).await,
                    actual_completion: None,
                    assignment_score: self.calculate_assignment_score(task, &selected_agents).await,
                    retries: 0,
                };
                
                self.task_assignments.insert(task.id, assignment);
                
                // Update agent workloads
                self.update_agent_workloads(&selected_agents, task).await;
                
                // Send assignment messages
                self.send_assignment_messages(task, &selected_agents).await?;
                
                // Update metrics
                self.update_assignment_metrics(assignment_start, true).await;
                
                info!("Task {} assigned to {} agents: {:?}", 
                     task.id, selected_agents.len(), selected_agents);
                
                Ok(selected_agents)
            }
            PolicyResult::Reject(reason) => {
                self.update_assignment_metrics(assignment_start, false).await;
                Err(OrchestrationError::Task(format!("Task rejected: {}", reason)))
            }
            PolicyResult::Defer(duration) => {
                warn!("Task {} deferred for {:?}", task.id, duration);
                tokio::time::sleep(duration).await;
                self.assign_task(task).await
            }
            PolicyResult::Escalate(reason) => {
                warn!("Task {} escalated: {}", task.id, reason);
                self.escalate_task_assignment(task, reason).await
            }
        }
    }
    
    /// Reassign a failed task
    pub async fn reassign_task(&self, task_id: TaskId, failure_reason: String) -> Result<Vec<AgentId>> {
        info!("Reassigning task {} due to: {}", task_id, failure_reason);
        
        // Update assignment record
        if let Some(mut assignment) = self.task_assignments.get_mut(&task_id) {
            assignment.retries += 1;
            
            // Remove from previous agents' workloads
            for agent_id in &assignment.assigned_agents {
                if let Some(mut workload) = self.agent_workloads.get_mut(agent_id) {
                    workload.active_tasks.retain(|id| *id != task_id);
                    workload.current_load = self.calculate_agent_load(&workload.active_tasks).await;
                    workload.last_updated = chrono::Utc::now();
                }
            }
        }
        
        // Get the task (would typically come from task manager)
        // For now, return an error if we can't get the task
        Err(OrchestrationError::Task(
            "Task reassignment not fully implemented".to_string()
        ))
    }
    
    /// Update task progress and workload tracking
    pub async fn update_task_progress(&self, task_id: TaskId, agent_id: &AgentId, progress: f32) -> Result<()> {
        debug!("Task {} progress update from {}: {}%", task_id, agent_id, progress * 100.0);
        
        // Update assignment record
        if let Some(mut assignment) = self.task_assignments.get_mut(&task_id) {
            if assignment.started_at.is_none() && progress > 0.0 {
                assignment.started_at = Some(chrono::Utc::now());
            }
        }
        
        // Update agent workload if task is complete
        if progress >= 1.0 {
            if let Some(mut workload) = self.agent_workloads.get_mut(agent_id) {
                workload.active_tasks.retain(|id| *id != task_id);
                workload.current_load = self.calculate_agent_load(&workload.active_tasks).await;
                workload.last_updated = chrono::Utc::now();
            }
            
            // Update performance history
            self.update_performance_history(task_id, agent_id, true).await;
        }
        
        Ok(())
    }
    
    /// Get current load balancing statistics
    pub async fn get_load_balance_stats(&self) -> Result<LoadBalanceStats> {
        let mut agent_loads = HashMap::new();
        let mut total_load = 0.0;
        let mut agent_count = 0;
        
        for entry in self.agent_workloads.iter() {
            let workload = entry.value();
            agent_loads.insert(workload.agent_id.clone(), workload.current_load);
            total_load += workload.current_load;
            agent_count += 1;
        }
        
        let avg_load = if agent_count > 0 { total_load / agent_count as f32 } else { 0.0 };
        
        // Calculate load variance
        let variance = if agent_count > 0 {
            agent_loads.values()
                .map(|load| (load - avg_load).powi(2))
                .sum::<f32>() / agent_count as f32
        } else {
            0.0
        };
        
        let metrics = self.assignment_metrics.read().await;
        
        Ok(LoadBalanceStats {
            total_agents: agent_count,
            average_load: avg_load,
            load_variance: variance,
            efficiency_score: metrics.load_balance_efficiency,
            agent_loads,
            active_assignments: self.task_assignments.len(),
        })
    }
    
    // Private implementation methods
    
    async fn init_load_balancers(&self) -> Result<()> {
        // Initialize different load balancing algorithms
        self.load_balancers.insert(
            "round_robin".to_string(),
            Box::new(RoundRobinBalancer {
                next_agent_index: Arc::new(Mutex::new(0)),
            })
        );
        
        self.load_balancers.insert(
            "least_connections".to_string(),
            Box::new(LeastConnectionsBalancer)
        );
        
        self.load_balancers.insert(
            "weighted_round_robin".to_string(),
            Box::new(WeightedRoundRobinBalancer)
        );
        
        self.load_balancers.insert(
            "consistent_hash".to_string(),
            Box::new(ConsistentHashBalancer)
        );
        
        self.load_balancers.insert(
            "adaptive_load".to_string(),
            Box::new(AdaptiveLoadBalancer {
                performance_history: self.historical_performance.clone(),
            })
        );
        
        Ok(())
    }
    
    async fn init_assignment_policies(&self) -> Result<()> {
        let mut policies = self.assignment_policies.write().await;
        
        // High priority: Resource constraints
        policies.push(AssignmentPolicy {
            policy_id: "resource_constraints".to_string(),
            priority: 100,
            conditions: vec![
                AssignmentCondition::ResourceRequirement("memory".to_string(), 1000.0),
                AssignmentCondition::ResourceRequirement("cpu".to_string(), 2.0),
            ],
            action: AssignmentAction::Assign(AssignmentStrategy::SingleAgent),
            enabled: true,
        });
        
        // Medium priority: Capability matching
        policies.push(AssignmentPolicy {
            policy_id: "capability_matching".to_string(),
            priority: 50,
            conditions: vec![],
            action: AssignmentAction::Assign(AssignmentStrategy::Adaptive),
            enabled: true,
        });
        
        // Low priority: Load balancing
        policies.push(AssignmentPolicy {
            policy_id: "load_balancing".to_string(),
            priority: 10,
            conditions: vec![AssignmentCondition::LoadThreshold(0.8)],
            action: AssignmentAction::Defer(Duration::from_secs(30)),
            enabled: true,
        });
        
        Ok(())
    }
    
    async fn get_available_agents(&self, requirements: &TaskRequirements) -> Result<Vec<Agent>> {
        let all_agents = self.agent_registry.get_all_agents().await?;
        
        let available_agents: Vec<Agent> = all_agents
            .into_iter()
            .filter(|agent| {
                // Check agent status
                if !matches!(agent.status, AgentStatus::Available | AgentStatus::Busy) {
                    return false;
                }
                
                // Check capability requirements
                if !requirements.required_capabilities.is_empty() {
                    let has_all_capabilities = requirements.required_capabilities
                        .iter()
                        .all(|cap| agent.capabilities.contains(cap));
                    
                    if !has_all_capabilities {
                        return false;
                    }
                }
                
                // Check exclusion list
                if requirements.excluded_agents.contains(&agent.id) {
                    return false;
                }
                
                // Check current load
                if let Some(workload) = self.agent_workloads.get(&agent.id) {
                    if workload.current_load > 0.95 {
                        return false;
                    }
                }
                
                true
            })
            .collect();
        
        Ok(available_agents)
    }
    
    async fn apply_assignment_policies(
        &self,
        task: &Task,
        available_agents: &[Agent],
    ) -> Result<PolicyResult> {
        let policies = self.assignment_policies.read().await;
        
        // Sort policies by priority
        let mut sorted_policies: Vec<&AssignmentPolicy> = policies
            .iter()
            .filter(|p| p.enabled)
            .collect();
        
        sorted_policies.sort_by(|a, b| b.priority.cmp(&a.priority));
        
        // Apply policies in priority order
        for policy in sorted_policies {
            if self.policy_matches(policy, task, available_agents).await {
                match &policy.action {
                    AssignmentAction::Assign(strategy) => {
                        return Ok(PolicyResult::Assign(strategy.clone()));
                    }
                    AssignmentAction::Reject(reason) => {
                        return Ok(PolicyResult::Reject(reason.clone()));
                    }
                    AssignmentAction::Defer(duration) => {
                        return Ok(PolicyResult::Defer(*duration));
                    }
                    AssignmentAction::Escalate(reason) => {
                        return Ok(PolicyResult::Escalate(reason.clone()));
                    }
                    AssignmentAction::Custom(_) => {
                        // Handle custom actions
                        continue;
                    }
                }
            }
        }
        
        // Default policy: assign with adaptive strategy
        Ok(PolicyResult::Assign(AssignmentStrategy::Adaptive))
    }
    
    async fn policy_matches(
        &self,
        policy: &AssignmentPolicy,
        task: &Task,
        available_agents: &[Agent],
    ) -> bool {
        for condition in &policy.conditions {
            match condition {
                AssignmentCondition::RequiredCapability(cap) => {
                    if !task.requirements.required_capabilities.contains(cap) {
                        return false;
                    }
                }
                AssignmentCondition::LoadThreshold(threshold) => {
                    let avg_load = self.calculate_average_load().await;
                    if avg_load < *threshold {
                        return false;
                    }
                }
                AssignmentCondition::ResourceRequirement(resource, amount) => {
                    // Check if resource requirement can be met
                    if !self.resource_manager.can_allocate(resource, *amount).await.unwrap_or(false) {
                        return false;
                    }
                }
                _ => {
                    // Handle other conditions
                    continue;
                }
            }
        }
        
        true
    }
    
    async fn select_agents_for_task(
        &self,
        task: &Task,
        available_agents: &[Agent],
        strategy: &AssignmentStrategy,
    ) -> Result<Vec<AgentId>> {
        match strategy {
            AssignmentStrategy::SingleAgent => {
                self.select_single_agent(task, available_agents).await
            }
            AssignmentStrategy::MultiAgent { coordination_mode: _ } => {
                self.select_multi_agents(task, available_agents).await
            }
            AssignmentStrategy::Adaptive => {
                self.select_agents_adaptive(task, available_agents).await
            }
            _ => {
                // Fallback to single agent
                self.select_single_agent(task, available_agents).await
            }
        }
    }
    
    async fn select_single_agent(&self, task: &Task, available_agents: &[Agent]) -> Result<Vec<AgentId>> {
        let load_balancer = self.get_load_balancer().await;
        
        // Get current workloads
        let workloads: HashMap<AgentId, AgentWorkload> = self.agent_workloads
            .iter()
            .map(|entry| (entry.key().clone(), entry.value().clone()))
            .collect();
        
        let selected_agents = load_balancer.select_agents(task, available_agents, &workloads)?;
        
        if selected_agents.is_empty() {
            return Err(OrchestrationError::Agent("No agents selected".to_string()));
        }
        
        // Return only the first agent for single agent strategy
        Ok(vec![selected_agents[0].clone()])
    }
    
    async fn select_multi_agents(&self, task: &Task, available_agents: &[Agent]) -> Result<Vec<AgentId>> {
        let min_agents = task.requirements.min_agents.max(2);
        let max_agents = task.requirements.max_agents.min(available_agents.len());
        
        let load_balancer = self.get_load_balancer().await;
        let workloads: HashMap<AgentId, AgentWorkload> = self.agent_workloads
            .iter()
            .map(|entry| (entry.key().clone(), entry.value().clone()))
            .collect();
        
        let mut selected_agents = load_balancer.select_agents(task, available_agents, &workloads)?;
        
        // Ensure we have the right number of agents
        if selected_agents.len() < min_agents {
            return Err(OrchestrationError::Agent(
                format!("Not enough agents available: {} < {}", selected_agents.len(), min_agents)
            ));
        }
        
        selected_agents.truncate(max_agents);
        Ok(selected_agents)
    }
    
    async fn select_agents_adaptive(&self, task: &Task, available_agents: &[Agent]) -> Result<Vec<AgentId>> {
        // Use heuristics to decide between single and multi-agent assignment
        let complexity_score = self.calculate_task_complexity(task).await;
        
        if complexity_score > 0.7 || task.requirements.min_agents > 1 {
            self.select_multi_agents(task, available_agents).await
        } else {
            self.select_single_agent(task, available_agents).await
        }
    }
    
    async fn get_load_balancer(&self) -> Arc<dyn LoadBalancer + Send + Sync> {
        let strategy = &self.config.orchestration.load_balancing_strategy;
        
        let balancer_key = match strategy {
            crate::config::LoadBalancingStrategy::RoundRobin => "round_robin",
            crate::config::LoadBalancingStrategy::LeastConnections => "least_connections",
            crate::config::LoadBalancingStrategy::WeightedRoundRobin => "weighted_round_robin",
            crate::config::LoadBalancingStrategy::ConsistentHashing => "consistent_hash",
            crate::config::LoadBalancingStrategy::AdaptiveLoad => "adaptive_load",
        };
        
        self.load_balancers.get(balancer_key)
            .map(|entry| entry.value().clone())
            .unwrap_or_else(|| {
                // Fallback to least connections
                self.load_balancers.get("least_connections")
                    .map(|entry| entry.value().clone())
                    .unwrap()
            })
    }
    
    async fn calculate_task_complexity(&self, task: &Task) -> f32 {
        let mut complexity = 0.0;
        
        // Factor in requirements complexity
        complexity += task.requirements.required_capabilities.len() as f32 * 0.1;
        complexity += task.requirements.min_agents as f32 * 0.2;
        
        // Factor in resource requirements
        if let Some(memory) = task.requirements.required_resources.memory_mb {
            complexity += (memory as f32 / 1000.0) * 0.1;
        }
        
        if let Some(time) = task.requirements.required_resources.execution_time_estimate_ms {
            complexity += (time as f32 / 60000.0) * 0.1; // Minutes
        }
        
        // Factor in dependencies
        complexity += task.dependencies.len() as f32 * 0.15;
        
        complexity.min(1.0)
    }
    
    async fn update_agent_workloads(&self, agent_ids: &[AgentId], task: &Task) {
        for agent_id in agent_ids {
            let mut workload = self.agent_workloads
                .entry(agent_id.clone())
                .or_insert_with(|| AgentWorkload {
                    agent_id: agent_id.clone(),
                    active_tasks: Vec::new(),
                    pending_tasks: Vec::new(),
                    current_load: 0.0,
                    capacity: 1.0,
                    specialization_scores: HashMap::new(),
                    last_updated: chrono::Utc::now(),
                });
            
            workload.active_tasks.push(task.id);
            workload.current_load = self.calculate_agent_load(&workload.active_tasks).await;
            workload.last_updated = chrono::Utc::now();
        }
    }
    
    async fn calculate_agent_load(&self, active_tasks: &[TaskId]) -> f32 {
        // Simple load calculation based on number of tasks
        // In a real implementation, this would consider task complexity, resource usage, etc.
        (active_tasks.len() as f32 * 0.2).min(1.0)
    }
    
    async fn calculate_average_load(&self) -> f32 {
        let mut total_load = 0.0;
        let mut count = 0;
        
        for entry in self.agent_workloads.iter() {
            total_load += entry.value().current_load;
            count += 1;
        }
        
        if count > 0 {
            total_load / count as f32
        } else {
            0.0
        }
    }
    
    async fn send_assignment_messages(&self, task: &Task, agent_ids: &[AgentId]) -> Result<()> {
        for agent_id in agent_ids {
            let message = Message::new(
                "task_distributor".to_string(),
                MessageRecipient::Agent(agent_id.clone()),
                Channel::TaskExecution,
                MessageType::TaskAssigned,
                MessagePayload::TaskAssignment {
                    task_id: task.id,
                    task_data: serde_json::to_value(task)?,
                    requirements: serde_json::to_value(&task.requirements)?,
                    deadline: task.deadline,
                },
            );
            
            self.message_bus.publish(message).await?;
        }
        
        Ok(())
    }
    
    async fn estimate_completion_time(&self, task: &Task, agent_ids: &[AgentId]) -> Option<chrono::DateTime<chrono::Utc>> {
        // Get performance history for assigned agents
        let mut estimated_time_ms = 0.0;
        let mut valid_estimates = 0;
        
        for agent_id in agent_ids {
            if let Some(history) = self.historical_performance.get(agent_id) {
                estimated_time_ms += history.avg_completion_time_ms;
                valid_estimates += 1;
            }
        }
        
        if valid_estimates > 0 {
            estimated_time_ms /= valid_estimates as f64;
            
            // Add task-specific factors
            if let Some(estimate) = task.requirements.required_resources.execution_time_estimate_ms {
                estimated_time_ms = estimated_time_ms.max(estimate as f64);
            }
            
            let duration = chrono::Duration::milliseconds(estimated_time_ms as i64);
            Some(chrono::Utc::now() + duration)
        } else {
            None
        }
    }
    
    async fn calculate_assignment_score(&self, task: &Task, agent_ids: &[AgentId]) -> f32 {
        let mut total_score = 0.0;
        
        for agent_id in agent_ids {
            let capability_score = self.capability_matcher
                .calculate_capability_match(&task.requirements.required_capabilities, agent_id).await;
            
            let load_score = if let Some(workload) = self.agent_workloads.get(agent_id) {
                1.0 - workload.current_load
            } else {
                1.0
            };
            
            let performance_score = if let Some(history) = self.historical_performance.get(agent_id) {
                history.reliability_score
            } else {
                0.5
            };
            
            let agent_score = (capability_score * 0.4) + (load_score * 0.3) + (performance_score * 0.3);
            total_score += agent_score;
        }
        
        total_score / agent_ids.len() as f32
    }
    
    async fn update_assignment_metrics(&self, assignment_start: Instant, success: bool) {
        let mut metrics = self.assignment_metrics.write().await;
        
        metrics.total_assignments += 1;
        
        if success {
            metrics.successful_assignments += 1;
        } else {
            metrics.failed_assignments += 1;
        }
        
        let assignment_time_ms = assignment_start.elapsed().as_millis() as f64;
        metrics.avg_assignment_time_ms = 
            (metrics.avg_assignment_time_ms * (metrics.total_assignments - 1) as f64 + assignment_time_ms) 
            / metrics.total_assignments as f64;
    }
    
    async fn update_performance_history(&self, task_id: TaskId, agent_id: &AgentId, success: bool) {
        let mut history = self.historical_performance
            .entry(agent_id.clone())
            .or_insert_with(|| PerformanceHistory {
                agent_id: agent_id.clone(),
                ..Default::default()
            });
        
        if success {
            history.completed_tasks += 1;
        } else {
            history.failed_tasks += 1;
        }
        
        let total_tasks = history.completed_tasks + history.failed_tasks;
        history.success_rate = history.completed_tasks as f32 / total_tasks as f32;
        
        // Update reliability score (exponential moving average)
        let new_reliability = if success { 1.0 } else { 0.0 };
        history.reliability_score = 0.9 * history.reliability_score + 0.1 * new_reliability;
        
        history.last_updated = chrono::Utc::now();
    }
    
    async fn escalate_task_assignment(&self, task: &Task, reason: String) -> Result<Vec<AgentId>> {
        warn!("Escalating task assignment for {}: {}", task.id, reason);
        
        // Send escalation message
        let message = Message::new(
            "task_distributor".to_string(),
            MessageRecipient::Coordinator,
            Channel::TaskExecution,
            MessageType::SystemAlert,
            MessagePayload::SystemData {
                system_type: "task_assignment_escalation".to_string(),
                data: serde_json::json!({
                    "task_id": task.id,
                    "reason": reason,
                    "task": task
                }),
                severity: "high".to_string(),
                action_required: true,
            },
        );
        
        self.message_bus.publish(message).await?;
        
        Err(OrchestrationError::Task(format!("Task assignment escalated: {}", reason)))
    }
    
    async fn start_optimization_task(&self) {
        let assignment_metrics = self.assignment_metrics.clone();
        let historical_performance = self.historical_performance.clone();
        let capability_matcher = self.capability_matcher.clone();
        
        let shutdown_rx = {
            let tx = self.shutdown_tx.lock().await;
            tx.as_ref().unwrap().subscribe()
        };
        
        let handle = tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(300)); // 5 minutes
            let mut shutdown_rx = shutdown_rx;
            
            loop {
                tokio::select! {
                    _ = interval.tick() => {
                        Self::optimize_assignment_strategies(
                            &assignment_metrics,
                            &historical_performance,
                            &capability_matcher
                        ).await;
                    }
                    _ = shutdown_rx.recv() => break,
                }
            }
        });
        
        *self.optimization_handle.lock().await = Some(handle);
    }
    
    async fn start_rebalancing_task(&self) {
        let agent_workloads = self.agent_workloads.clone();
        let task_assignments = self.task_assignments.clone();
        
        let shutdown_rx = {
            let tx = self.shutdown_tx.lock().await;
            tx.as_ref().unwrap().subscribe()
        };
        
        let handle = tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(120)); // 2 minutes
            let mut shutdown_rx = shutdown_rx;
            
            loop {
                tokio::select! {
                    _ = interval.tick() => {
                        Self::rebalance_workloads(&agent_workloads, &task_assignments).await;
                    }
                    _ = shutdown_rx.recv() => break,
                }
            }
        });
        
        *self.rebalance_handle.lock().await = Some(handle);
    }
    
    async fn optimize_assignment_strategies(
        _assignment_metrics: &RwLock<AssignmentMetrics>,
        _historical_performance: &DashMap<AgentId, PerformanceHistory>,
        _capability_matcher: &CapabilityMatcher,
    ) {
        // Implement optimization logic
        debug!("Running assignment strategy optimization");
        
        // Analyze performance patterns
        // Adjust capability matching weights
        // Update load balancing parameters
        // Fine-tune assignment policies
    }
    
    async fn rebalance_workloads(
        _agent_workloads: &DashMap<AgentId, AgentWorkload>,
        _task_assignments: &DashMap<TaskId, TaskAssignment>,
    ) {
        // Implement workload rebalancing logic
        debug!("Running workload rebalancing");
        
        // Identify overloaded agents
        // Find underutilized agents  
        // Suggest task migrations
        // Update load distribution
    }
}

// Implementation of load balancing algorithms

impl LoadBalancer for RoundRobinBalancer {
    fn select_agents(
        &self,
        _task: &Task,
        available_agents: &[Agent],
        _workloads: &HashMap<AgentId, AgentWorkload>,
    ) -> Result<Vec<AgentId>> {
        if available_agents.is_empty() {
            return Ok(Vec::new());
        }
        
        let index = {
            let mut next_index = self.next_agent_index.blocking_lock();
            let current = *next_index % available_agents.len();
            *next_index = (*next_index + 1) % available_agents.len();
            current
        };
        
        Ok(vec![available_agents[index].id.clone()])
    }
    
    fn calculate_score(&self, _task: &Task, _agent: &Agent, _workload: &AgentWorkload) -> f32 {
        1.0 // All agents have equal score in round robin
    }
}

impl LoadBalancer for LeastConnectionsBalancer {
    fn select_agents(
        &self,
        _task: &Task,
        available_agents: &[Agent],
        workloads: &HashMap<AgentId, AgentWorkload>,
    ) -> Result<Vec<AgentId>> {
        if available_agents.is_empty() {
            return Ok(Vec::new());
        }
        
        let best_agent = available_agents
            .iter()
            .min_by_key(|agent| {
                workloads.get(&agent.id)
                    .map(|w| w.active_tasks.len())
                    .unwrap_or(0)
            })
            .unwrap();
        
        Ok(vec![best_agent.id.clone()])
    }
    
    fn calculate_score(&self, _task: &Task, agent: &Agent, workload: &AgentWorkload) -> f32 {
        1.0 - (workload.active_tasks.len() as f32 * 0.1)
    }
}

impl LoadBalancer for WeightedRoundRobinBalancer {
    fn select_agents(
        &self,
        task: &Task,
        available_agents: &[Agent],
        workloads: &HashMap<AgentId, AgentWorkload>,
    ) -> Result<Vec<AgentId>> {
        if available_agents.is_empty() {
            return Ok(Vec::new());
        }
        
        // Calculate weighted scores for each agent
        let mut agent_scores: Vec<(AgentId, f32)> = available_agents
            .iter()
            .map(|agent| {
                let score = self.calculate_score(task, agent, 
                    workloads.get(&agent.id).unwrap_or(&AgentWorkload {
                        agent_id: agent.id.clone(),
                        active_tasks: Vec::new(),
                        pending_tasks: Vec::new(),
                        current_load: 0.0,
                        capacity: 1.0,
                        specialization_scores: HashMap::new(),
                        last_updated: chrono::Utc::now(),
                    }));
                (agent.id.clone(), score)
            })
            .collect();
        
        // Sort by score (descending)
        agent_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        
        Ok(vec![agent_scores[0].0.clone()])
    }
    
    fn calculate_score(&self, task: &Task, agent: &Agent, workload: &AgentWorkload) -> f32 {
        let mut score = 1.0 - workload.current_load;
        
        // Bonus for capability match
        let capability_match = task.requirements.required_capabilities
            .iter()
            .filter(|cap| agent.capabilities.contains(cap))
            .count() as f32 / task.requirements.required_capabilities.len().max(1) as f32;
        
        score += capability_match * 0.5;
        
        // Bonus for preferred agents
        if task.requirements.preferred_agents.contains(&agent.id) {
            score += 0.3;
        }
        
        score
    }
}

impl LoadBalancer for ConsistentHashBalancer {
    fn select_agents(
        &self,
        task: &Task,
        available_agents: &[Agent],
        _workloads: &HashMap<AgentId, AgentWorkload>,
    ) -> Result<Vec<AgentId>> {
        if available_agents.is_empty() {
            return Ok(Vec::new());
        }
        
        // Simple hash-based selection
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        task.id.hash(&mut hasher);
        let hash = hasher.finish();
        
        let index = (hash % available_agents.len() as u64) as usize;
        Ok(vec![available_agents[index].id.clone()])
    }
    
    fn calculate_score(&self, _task: &Task, _agent: &Agent, _workload: &AgentWorkload) -> f32 {
        1.0 // Hash-based selection doesn't use scores
    }
}

impl LoadBalancer for AdaptiveLoadBalancer {
    fn select_agents(
        &self,
        task: &Task,
        available_agents: &[Agent],
        workloads: &HashMap<AgentId, AgentWorkload>,
    ) -> Result<Vec<AgentId>> {
        if available_agents.is_empty() {
            return Ok(Vec::new());
        }
        
        let mut agent_scores: Vec<(AgentId, f32)> = available_agents
            .iter()
            .map(|agent| {
                let score = self.calculate_score(task, agent, 
                    workloads.get(&agent.id).unwrap_or(&AgentWorkload {
                        agent_id: agent.id.clone(),
                        active_tasks: Vec::new(),
                        pending_tasks: Vec::new(),
                        current_load: 0.0,
                        capacity: 1.0,
                        specialization_scores: HashMap::new(),
                        last_updated: chrono::Utc::now(),
                    }));
                (agent.id.clone(), score)
            })
            .collect();
        
        agent_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        
        // Return top N agents based on task requirements
        let num_agents = task.requirements.min_agents.max(1).min(available_agents.len());
        Ok(agent_scores.into_iter().take(num_agents).map(|(id, _)| id).collect())
    }
    
    fn calculate_score(&self, task: &Task, agent: &Agent, workload: &AgentWorkload) -> f32 {
        let mut score = 0.0;
        
        // Load factor (30%)
        let load_score = 1.0 - workload.current_load;
        score += load_score * 0.3;
        
        // Capability match (40%)
        let capability_score = if task.requirements.required_capabilities.is_empty() {
            1.0
        } else {
            task.requirements.required_capabilities
                .iter()
                .filter(|cap| agent.capabilities.contains(cap))
                .count() as f32 / task.requirements.required_capabilities.len() as f32
        };
        score += capability_score * 0.4;
        
        // Performance history (30%)
        let performance_score = if let Some(history) = self.performance_history.get(&agent.id) {
            (history.success_rate + history.reliability_score) / 2.0
        } else {
            0.5 // Default score for new agents
        };
        score += performance_score * 0.3;
        
        score
    }
}

impl CapabilityMatcher {
    fn new() -> Self {
        CapabilityMatcher {
            capability_weights: HashMap::new(),
            similarity_threshold: 0.7,
        }
    }
    
    async fn calculate_capability_match(&self, required_capabilities: &[String], agent_id: &AgentId) -> f32 {
        // This would typically use more sophisticated matching logic
        // For now, return a simple match score
        if required_capabilities.is_empty() {
            return 1.0;
        }
        
        // Simplified capability matching
        0.8 // Placeholder score
    }
}

#[derive(Debug)]
enum PolicyResult {
    Assign(AssignmentStrategy),
    Reject(String),
    Defer(Duration),
    Escalate(String),
}

#[derive(Debug, Clone)]
pub struct LoadBalanceStats {
    pub total_agents: usize,
    pub average_load: f32,
    pub load_variance: f32,
    pub efficiency_score: f32,
    pub agent_loads: HashMap<AgentId, f32>,
    pub active_assignments: usize,
}