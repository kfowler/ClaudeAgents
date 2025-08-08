use std::sync::Arc;
use crate::config::Config;
use crate::error::Result;
use crate::persistence::StateStore;

/// Handles conflict resolution between agents
pub struct ConflictResolver {
    config: Arc<Config>,
    state_store: Arc<StateStore>,
}

impl ConflictResolver {
    pub fn new(config: Arc<Config>, state_store: Arc<StateStore>) -> Result<Self> {
        Ok(ConflictResolver {
            config,
            state_store,
        })
    }
}