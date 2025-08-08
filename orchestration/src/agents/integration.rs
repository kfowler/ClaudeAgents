use std::sync::Arc;
use crate::error::Result;
use super::ClaudeAgentAdapter;

/// Integration layer for Claude agent system
pub struct ClaudeAgentIntegration {
    adapter: Arc<ClaudeAgentAdapter>,
}

impl ClaudeAgentIntegration {
    pub fn new(agents_directory: String) -> Self {
        ClaudeAgentIntegration {
            adapter: Arc::new(ClaudeAgentAdapter::new(agents_directory)),
        }
    }
    
    pub async fn initialize(&self) -> Result<()> {
        self.adapter.load_agents().await?;
        Ok(())
    }
}