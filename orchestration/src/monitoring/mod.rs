mod metrics_collector;

pub use metrics_collector::MetricsCollector;

use crate::error::Result;
use crate::orchestration::SessionId;

/// Trait for metrics collection and monitoring
#[async_trait::async_trait]
pub trait Monitoring: Send + Sync {
    async fn record_session_created(&self, session_id: SessionId);
    async fn record_task_completed(&self, task_id: uuid::Uuid, duration_ms: u64);
    async fn record_agent_activity(&self, agent_id: String, activity: String);
}