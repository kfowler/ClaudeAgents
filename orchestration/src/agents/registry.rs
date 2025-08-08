use std::sync::Arc;
use std::collections::HashMap;
use tokio::sync::RwLock;
use tracing::{info, warn};

use crate::config::Config;
use crate::error::{Result, OrchestrationError};
use crate::orchestration::{Agent, AgentId};
use super::ClaudeAgentAdapter;

/// Registry for managing available agents
pub struct AgentRegistry {
    config: Arc<Config>,
    claude_adapter: ClaudeAgentAdapter,
    agents: Arc<RwLock<HashMap<AgentId, Arc<RwLock<Agent>>>>>,
}

impl AgentRegistry {
    pub async fn new(config: Arc<Config>) -> Result<Self> {
        info!("Initializing agent registry");
        
        // Initialize Claude agent adapter
        let agents_directory = std::env::var("CLAUDE_AGENTS_DIR")
            .unwrap_or_else(|_| "../agents".to_string());
        
        let claude_adapter = ClaudeAgentAdapter::new(agents_directory);
        
        Ok(AgentRegistry {
            config,
            claude_adapter,
            agents: Arc::new(RwLock::new(HashMap::new())),
        })
    }
    
    pub async fn start(&self) -> Result<()> {
        info!("Starting agent registry");
        
        // Load Claude agents
        match self.claude_adapter.load_agents().await {
            Ok(claude_agents) => {
                let mut agents = self.agents.write().await;
                for agent in claude_agents {
                    agents.insert(agent.id.clone(), Arc::new(RwLock::new(agent)));
                }
                info!("Loaded {} Claude agents", agents.len());
            }
            Err(e) => {
                warn!("Failed to load Claude agents: {}", e);
            }
        }
        
        Ok(())
    }
    
    pub async fn shutdown(&self) -> Result<()> {
        info!("Shutting down agent registry");
        Ok(())
    }
    
    pub async fn register_agent(&self, agent_id: AgentId, agent: Arc<RwLock<Agent>>) -> Result<()> {
        let mut agents = self.agents.write().await;
        agents.insert(agent_id, agent);
        Ok(())
    }
    
    pub async fn unregister_agent(&self, agent_id: &AgentId) -> Result<()> {
        let mut agents = self.agents.write().await;
        agents.remove(agent_id);
        Ok(())
    }
    
    pub async fn get_agent(&self, agent_id: &AgentId) -> Result<Option<Arc<RwLock<Agent>>>> {
        let agents = self.agents.read().await;
        Ok(agents.get(agent_id).cloned())
    }
    
    pub async fn get_all_agents(&self) -> Result<Vec<Agent>> {
        let agents = self.agents.read().await;
        let mut result = Vec::new();
        
        for agent_ref in agents.values() {
            if let Ok(agent) = agent_ref.try_read() {
                result.push(agent.clone());
            }
        }
        
        Ok(result)
    }
}