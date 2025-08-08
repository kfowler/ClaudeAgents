mod state_store;
mod migrations;
mod repositories;

pub use state_store::StateStore;
pub use repositories::*;

use crate::error::Result;
use crate::orchestration::{Task, Agent, OrchestrationSession, SharedContext};

/// Trait for persistent storage operations
#[async_trait::async_trait]
pub trait PersistentStorage: Send + Sync {
    async fn save_task(&self, task: &Task) -> Result<()>;
    async fn load_task(&self, task_id: uuid::Uuid) -> Result<Option<Task>>;
    async fn load_active_tasks(&self) -> Result<Vec<Task>>;
    
    async fn save_agent(&self, agent: &Agent) -> Result<()>;
    async fn load_agent(&self, agent_id: &str) -> Result<Option<Agent>>;
    async fn load_registered_agents(&self) -> Result<Vec<Agent>>;
    
    async fn save_session(&self, session: &OrchestrationSession) -> Result<()>;
    async fn load_session(&self, session_id: uuid::Uuid) -> Result<Option<OrchestrationSession>>;
    async fn load_active_sessions(&self) -> Result<Vec<OrchestrationSession>>;
    
    async fn save_context(&self, context: &SharedContext) -> Result<()>;
    async fn load_context(&self, context_id: uuid::Uuid) -> Result<Option<SharedContext>>;
    async fn load_contexts(&self) -> Result<Vec<SharedContext>>;
    
    async fn is_healthy(&self) -> bool;
}